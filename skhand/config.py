"""Configuration loaded from .env via Pydantic settings."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Anthropic
    anthropic_api_key: str = ""

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "skhand2026"

    # ChromaDB
    chroma_persist_dir: str = "./data/chromadb"

    # Models
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    claude_model: str = "claude-sonnet-4-5-20250929"
    claude_fast_model: str = "claude-haiku-4-5-20251001"

    # Paths
    project_root: Path = Path(__file__).parent.parent
    sanskrit_data_dir: Path = Path(__file__).parent.parent / "data" / "sanskrit"
    papers_data_dir: Path = Path(__file__).parent.parent / "data" / "papers"
    db_path: Path = Path(__file__).parent.parent / "data" / "skhand.db"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
