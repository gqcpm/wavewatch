"""
Tests for GeminiEmbedder.
"""

import pytest
from unittest.mock import patch, MagicMock
from wavewatch.rag.embedder import GeminiEmbedder
from wavewatch.rag.config import RAGConfig


class TestGeminiEmbedder:
    """Test cases for GeminiEmbedder."""

    def test_initialization_with_api_key(self):
        """Test embedder initializes with provided API key."""
        with patch("wavewatch.rag.embedder.genai.Client") as mock_client:
            embedder = GeminiEmbedder(api_key="test_key")
            assert embedder.api_key == "test_key"
            assert embedder.model == RAGConfig.EMBEDDING_MODEL
            mock_client.assert_called_once_with(api_key="test_key")

    def test_initialization_without_api_key(self):
        """Test embedder initializes with config API key."""
        with patch("wavewatch.rag.embedder.genai.Client"), \
             patch.object(RAGConfig, "GEMINI_API_KEY", "config_key"):
            embedder = GeminiEmbedder()
            assert embedder.api_key == "config_key"

    def test_initialization_no_api_key_raises_error(self):
        """Test embedder raises error when no API key available."""
        with patch.object(RAGConfig, "GEMINI_API_KEY", None):
            with pytest.raises(ValueError) as exc_info:
                GeminiEmbedder()
            assert "API key" in str(exc_info.value)

    def test_get_embedding_dimension(self):
        """Test getting embedding dimension."""
        with patch("wavewatch.rag.embedder.genai.Client"):
            embedder = GeminiEmbedder(api_key="test_key")
            dimension = embedder.get_embedding_dimension()
            assert dimension == RAGConfig.EMBEDDING_DIMENSION
            assert isinstance(dimension, int)

    @patch("wavewatch.rag.embedder.genai.Client")
    def test_embed_text_success(self, mock_client_class):
        """Test successful text embedding."""
        # Mock the client and response
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock embedding response
        mock_embedding = MagicMock()
        mock_embedding.values = [0.1, 0.2, 0.3] * (RAGConfig.EMBEDDING_DIMENSION // 3)
        mock_response = MagicMock()
        mock_response.embeddings = [mock_embedding]
        mock_client.models.embed_content.return_value = mock_response
        
        embedder = GeminiEmbedder(api_key="test_key")
        result = embedder.embed_text("test text")
        
        assert isinstance(result, list)
        assert len(result) == RAGConfig.EMBEDDING_DIMENSION
        assert all(isinstance(x, float) for x in result)

    @patch("wavewatch.rag.embedder.genai.Client")
    def test_embed_text_empty(self, mock_client_class):
        """Test embedding empty text."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_embedding = MagicMock()
        mock_embedding.values = [0.0] * RAGConfig.EMBEDDING_DIMENSION
        mock_response = MagicMock()
        mock_response.embeddings = [mock_embedding]
        mock_client.models.embed_content.return_value = mock_response
        
        embedder = GeminiEmbedder(api_key="test_key")
        result = embedder.embed_text("")
        
        assert len(result) == RAGConfig.EMBEDDING_DIMENSION

    @patch("wavewatch.rag.embedder.genai.Client")
    def test_embed_batch_success(self, mock_client_class):
        """Test successful batch embedding."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock batch response - first batch (2 texts), then second batch (1 text)
        def mock_embed_side_effect(*args, **kwargs):
            contents = kwargs.get("contents", args[1] if len(args) > 1 else [])
            if isinstance(contents, list):
                batch_size = len(contents)
            else:
                batch_size = 1
            
            mock_embeddings = []
            for i in range(batch_size):
                mock_emb = MagicMock()
                mock_emb.values = [float(i)] * RAGConfig.EMBEDDING_DIMENSION
                mock_embeddings.append(mock_emb)
            
            mock_response = MagicMock()
            mock_response.embeddings = mock_embeddings
            return mock_response
        
        mock_client.models.embed_content.side_effect = mock_embed_side_effect
        
        embedder = GeminiEmbedder(api_key="test_key")
        texts = ["text1", "text2", "text3"]
        results = embedder.embed_batch(texts, batch_size=3)  # Use batch_size=3 so all in one batch
        
        assert len(results) == 3
        assert all(len(emb) == RAGConfig.EMBEDDING_DIMENSION for emb in results)

    @patch("wavewatch.rag.embedder.genai.Client")
    def test_embed_batch_empty_list(self, mock_client_class):
        """Test batch embedding with empty list."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        embedder = GeminiEmbedder(api_key="test_key")
        results = embedder.embed_batch([])
        
        assert results == []

    @patch("wavewatch.rag.embedder.genai.Client")
    def test_embed_batch_respects_batch_size(self, mock_client_class):
        """Test batch embedding respects batch size."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_embedding = MagicMock()
        mock_embedding.values = [0.1] * RAGConfig.EMBEDDING_DIMENSION
        mock_response = MagicMock()
        mock_response.embeddings = [mock_embedding]
        mock_client.models.embed_content.return_value = mock_response
        
        embedder = GeminiEmbedder(api_key="test_key")
        texts = ["text"] * 5
        embedder.embed_batch(texts, batch_size=2)
        
        # Should be called multiple times due to batch size
        assert mock_client.models.embed_content.call_count >= 2

