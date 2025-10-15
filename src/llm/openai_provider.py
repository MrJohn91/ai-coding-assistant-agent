"""OpenAI LLM provider implementation."""

import json
import logging
from typing import Dict, List

import openai

from src.config import settings
from src.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI GPT-4/3.5 provider."""

    def __init__(self, model: str = None, api_key: str = None):
        """Initialize OpenAI provider.

        Args:
            model: OpenAI model name (defaults to settings)
            api_key: OpenAI API key (defaults to settings)
        """
        self.model = model or settings.openai_model
        self.client = openai.AsyncOpenAI(api_key=api_key or settings.openai_api_key)

    async def generate(
        self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 500
    ) -> str:
        """Generate text using OpenAI API.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text

        Raises:
            openai.APIError: If API call fails
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content

        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def generate_json(
        self, messages: List[Dict[str, str]], temperature: float = 0.7
    ) -> Dict:
        """Generate structured JSON response using OpenAI.

        Args:
            messages: List of message dicts
            temperature: Sampling temperature

        Returns:
            Parsed JSON response

        Raises:
            openai.APIError: If API call fails
            json.JSONDecodeError: If response is not valid JSON
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            return json.loads(content)

        except (openai.APIError, json.JSONDecodeError) as e:
            logger.error(f"OpenAI JSON generation error: {e}")
            raise
