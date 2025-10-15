"""Configuration management for Sales Bike Agent."""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Configuration
    llm_provider: str = "openai"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    openai_embedding_model: str = "text-embedding-3-small"

    # CRM API Configuration
    crm_api_url: str = "https://api.example.com"
    crm_api_key: Optional[str] = None

    # Mem0 Configuration (for conversation memory)
    # Based on Mem0 initialization pattern from docs
    # Reference: Mem0 Four Lines of Code (page_id: e15ed917-c80f-4a1a-bdd5-63c1016e7ab9)
    mem0_api_key: Optional[str] = None

    # Application Configuration
    log_level: str = "INFO"
    session_ttl_minutes: int = 30
    max_conversation_turns: int = 20

    # Vector Store Configuration
    faiss_index_path: Path = Path("data/indices")

    # Data Paths
    product_catalog_path: Path = Path("Data/product_catalog.json")
    faq_path: Path = Path("Data/faq.txt")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
