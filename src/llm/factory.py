"""LLM provider factory."""

from src.config import settings
from src.llm.base import LLMProvider
from src.llm.local_provider import LocalLLMProvider
from src.llm.openai_provider import OpenAIProvider


def get_llm_provider(provider_name: str = None) -> LLMProvider:
    """Get LLM provider based on configuration.

    Args:
        provider_name: Provider name (openai, local) or None to use settings

    Returns:
        LLMProvider instance

    Raises:
        ValueError: If provider name is invalid
    """
    provider_name = provider_name or settings.llm_provider

    if provider_name == "openai":
        return OpenAIProvider()
    elif provider_name == "local":
        return LocalLLMProvider()
    else:
        raise ValueError(
            f"Unknown LLM provider: {provider_name}. Use 'openai' or 'local'."
        )
