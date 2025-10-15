"""Embedding generation for vector store."""

from typing import List

import openai

from src.config import settings


class Embedder:
    """Abstract embedder interface for generating text embeddings."""

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        raise NotImplementedError


class OpenAIEmbedder(Embedder):
    """OpenAI embeddings using their API."""

    def __init__(self, model: str = None):
        """Initialize OpenAI embedder.

        Args:
            model: OpenAI embedding model name
        """
        self.model = model or settings.openai_embedding_model
        self.client = openai.OpenAI(api_key=settings.openai_api_key)

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI API.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        # OpenAI API has a batch limit, process in chunks if needed
        embeddings = []
        chunk_size = 100

        for i in range(0, len(texts), chunk_size):
            chunk = texts[i : i + chunk_size]
            response = self.client.embeddings.create(input=chunk, model=self.model)
            embeddings.extend([item.embedding for item in response.data])

        return embeddings


class SentenceTransformerEmbedder(Embedder):
    """Local embeddings using sentence-transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize sentence-transformer embedder.

        Args:
            model_name: HuggingFace model name
        """
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using sentence-transformers.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()


def get_embedder(provider: str = None) -> Embedder:
    """Factory function to get appropriate embedder.

    Args:
        provider: Embedding provider (openai, sentence-transformers)

    Returns:
        Embedder instance
    """
    provider = provider or settings.llm_provider

    if provider == "openai":
        return OpenAIEmbedder()
    else:
        # Default to sentence-transformers for local/offline use
        return SentenceTransformerEmbedder()
