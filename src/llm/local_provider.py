"""Local LLM provider (Ollama) implementation."""

import json
import logging
from typing import Dict, List

import httpx

from src.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class LocalLLMProvider(LLMProvider):
    """Local LLM provider using Ollama."""

    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434"):
        """Initialize local LLM provider.

        Args:
            model: Model name (e.g., llama2, mistral)
            base_url: Ollama API base URL
        """
        self.model = model
        self.base_url = base_url

    async def generate(
        self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 500
    ) -> str:
        """Generate text using Ollama.

        Args:
            messages: List of message dicts
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text

        Raises:
            httpx.HTTPError: If API call fails
        """
        # Convert messages to Ollama format
        prompt = self._messages_to_prompt(messages)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "temperature": temperature,
                        "stream": False,
                    },
                    timeout=60.0,
                )
                response.raise_for_status()

                result = response.json()
                return result.get("response", "")

            except httpx.HTTPError as e:
                logger.error(f"Ollama API error: {e}")
                raise

    async def generate_json(
        self, messages: List[Dict[str, str]], temperature: float = 0.7
    ) -> Dict:
        """Generate JSON response using Ollama.

        Note: This adds explicit JSON formatting instructions to the prompt.

        Args:
            messages: List of message dicts
            temperature: Sampling temperature

        Returns:
            Parsed JSON response
        """
        # Add JSON formatting instruction
        messages = messages.copy()
        messages.append({
            "role": "system",
            "content": "Respond with valid JSON only. No additional text."
        })

        response = await self.generate(messages, temperature=temperature)

        try:
            # Extract JSON from response (sometimes wrapped in code blocks)
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]

            return json.loads(response.strip())

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from local LLM: {e}")
            logger.error(f"Response: {response}")
            raise

    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to a single prompt string.

        Args:
            messages: List of message dicts

        Returns:
            Formatted prompt string
        """
        prompt_parts = []

        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")

        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)
