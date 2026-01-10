"""
Tests for RAGConfig.
"""

import pytest
import os
from unittest.mock import patch
from wavewatch.rag.config import RAGConfig


class TestRAGConfig:
    """Test cases for RAGConfig."""

    def test_paths_exist(self):
        """Test that configuration paths are defined."""
        assert hasattr(RAGConfig, "PROJECT_ROOT")
        assert hasattr(RAGConfig, "KNOWLEDGE_BASE_PATH")
        assert hasattr(RAGConfig, "BEACHES_PATH")
        assert hasattr(RAGConfig, "GENERAL_PATH")
        assert hasattr(RAGConfig, "METADATA_PATH")

    def test_paths_are_path_objects(self):
        """Test that paths are Path objects."""
        from pathlib import Path
        assert isinstance(RAGConfig.PROJECT_ROOT, Path)
        assert isinstance(RAGConfig.KNOWLEDGE_BASE_PATH, Path)
        assert isinstance(RAGConfig.BEACHES_PATH, Path)

    def test_chunking_config(self):
        """Test chunking configuration values."""
        assert isinstance(RAGConfig.CHUNK_SIZE, int)
        assert RAGConfig.CHUNK_SIZE > 0
        assert isinstance(RAGConfig.CHUNK_OVERLAP, int)
        assert RAGConfig.CHUNK_OVERLAP >= 0
        assert isinstance(RAGConfig.MIN_CHUNK_SIZE, int)
        assert RAGConfig.MIN_CHUNK_SIZE > 0

    def test_embedding_config(self):
        """Test embedding configuration."""
        assert isinstance(RAGConfig.EMBEDDING_MODEL, str)
        assert len(RAGConfig.EMBEDDING_MODEL) > 0
        assert isinstance(RAGConfig.EMBEDDING_DIMENSION, int)
        assert RAGConfig.EMBEDDING_DIMENSION > 0

    def test_pinecone_config(self):
        """Test Pinecone configuration."""
        assert isinstance(RAGConfig.PINECONE_INDEX_NAME, str)
        assert len(RAGConfig.PINECONE_INDEX_NAME) > 0
        assert isinstance(RAGConfig.PINECONE_METRIC, str)
        assert RAGConfig.PINECONE_METRIC in ["cosine", "euclidean", "dotproduct"]

    def test_retrieval_config(self):
        """Test retrieval configuration."""
        assert isinstance(RAGConfig.DEFAULT_TOP_K, int)
        assert RAGConfig.DEFAULT_TOP_K > 0
        assert isinstance(RAGConfig.MAX_TOP_K, int)
        assert RAGConfig.MAX_TOP_K >= RAGConfig.DEFAULT_TOP_K

    def test_validate_with_missing_keys(self):
        """Test validation fails when API keys are missing."""
        # Temporarily clear the API keys
        original_gemini = RAGConfig.GEMINI_API_KEY
        original_pinecone = RAGConfig.PINECONE_API_KEY
        
        try:
            RAGConfig.GEMINI_API_KEY = None
            RAGConfig.PINECONE_API_KEY = None
            
            with pytest.raises(ValueError) as exc_info:
                RAGConfig.validate()
            assert "GEMINI_API_KEY" in str(exc_info.value) or "PINECONE_API_KEY" in str(exc_info.value)
        finally:
            # Restore original values
            RAGConfig.GEMINI_API_KEY = original_gemini
            RAGConfig.PINECONE_API_KEY = original_pinecone

    def test_validate_with_keys(self):
        """Test validation passes when API keys are present."""
        with patch.dict(os.environ, {
            "GEMINI_API_KEY": "test_key",
            "PINECONE_API_KEY": "test_key"
        }):
            import importlib
            import wavewatch.rag.config
            importlib.reload(wavewatch.rag.config)
            
            result = wavewatch.rag.config.RAGConfig.validate()
            assert result is True

