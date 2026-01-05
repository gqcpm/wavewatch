"""
Configuration for RAG system.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class RAGConfig:
    """Configuration for RAG system."""

    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
    KNOWLEDGE_BASE_PATH = PROJECT_ROOT / "data" / "knowledge_base"
    BEACHES_PATH = KNOWLEDGE_BASE_PATH / "beaches"
    GENERAL_PATH = KNOWLEDGE_BASE_PATH / "general"
    METADATA_PATH = KNOWLEDGE_BASE_PATH / "metadata"

    # API Keys
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    PINECONE_API_KEY: Optional[str] = os.getenv("PINECONE_API_KEY")
    
    # Pinecone Cloud Configuration
    PINECONE_CLOUD: Optional[str] = os.getenv("PINECONE_CLOUD", "aws")  # aws, gcp, or azure
    PINECONE_REGION: Optional[str] = os.getenv("PINECONE_REGION", "us-west-2")  # e.g., us-east-1, us-west-2

    # Embedding Configuration
    EMBEDDING_MODEL = "gemini-embedding-001"  # Gemini embedding model
    EMBEDDING_DIMENSION = 768  # Gemini embedding dimension (768, 1536, or 3072)

    # Chunking Configuration
    CHUNK_SIZE = 500  # tokens per chunk
    CHUNK_OVERLAP = 100  # token overlap between chunks
    MIN_CHUNK_SIZE = 50  # minimum chunk size in tokens

    # Pinecone Configuration
    PINECONE_INDEX_NAME = "wavewatch-knowledge-base"
    PINECONE_METRIC = "cosine"  # similarity metric

    # Retrieval Configuration
    DEFAULT_TOP_K = 5  # default number of results to retrieve
    MAX_TOP_K = 20  # maximum number of results

    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration is present."""
        missing = []
        if not cls.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        if not cls.PINECONE_API_KEY:
            missing.append("PINECONE_API_KEY")

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )
        return True

