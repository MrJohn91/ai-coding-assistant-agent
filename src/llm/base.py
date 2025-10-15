"""Base LLM provider interface."""

from abc import ABC, abstractmethod
from typing import Dict, List


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(
        self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 500
    ) -> str:
        """Generate text from messages.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response
        """
        pass

    @abstractmethod
    async def generate_json(
        self, messages: List[Dict[str, str]], temperature: float = 0.7
    ) -> Dict:
        """Generate structured JSON response.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)

        Returns:
            Parsed JSON response as dictionary
        """
        pass
