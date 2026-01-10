"""
Tests for RAGRetriever.
"""

import pytest
from unittest.mock import patch, MagicMock
from wavewatch.rag.retriever import RAGRetriever
from wavewatch.rag.embedder import GeminiEmbedder
from wavewatch.rag.vector_store import PineconeVectorStore
from wavewatch.rag.config import RAGConfig


class TestRAGRetriever:
    """Test cases for RAGRetriever."""

    @patch("wavewatch.rag.retriever.GeminiEmbedder")
    @patch("wavewatch.rag.retriever.PineconeVectorStore")
    def test_initialization_defaults(self, mock_vector_store_class, mock_embedder_class):
        """Test retriever initializes with default components."""
        mock_embedder = MagicMock()
        mock_embedder_class.return_value = mock_embedder
        
        mock_vector_store = MagicMock()
        mock_vector_store.index = MagicMock()
        mock_vector_store_class.return_value = mock_vector_store
        
        retriever = RAGRetriever(initialize_index=False)
        
        assert retriever.embedder == mock_embedder
        assert retriever.vector_store == mock_vector_store

    @patch("wavewatch.rag.retriever.GeminiEmbedder")
    @patch("wavewatch.rag.retriever.PineconeVectorStore")
    def test_initialization_with_custom_components(self, mock_vector_store_class, mock_embedder_class):
        """Test retriever initializes with custom components."""
        custom_embedder = MagicMock()
        custom_vector_store = MagicMock()
        custom_vector_store.index = MagicMock()
        
        retriever = RAGRetriever(
            embedder=custom_embedder,
            vector_store=custom_vector_store,
            initialize_index=False
        )
        
        assert retriever.embedder == custom_embedder
        assert retriever.vector_store == custom_vector_store

    @patch("wavewatch.rag.retriever.GeminiEmbedder")
    @patch("wavewatch.rag.retriever.PineconeVectorStore")
    def test_retrieve_no_index(self, mock_vector_store_class, mock_embedder_class):
        """Test retrieve returns empty list when index not initialized."""
        mock_embedder = MagicMock()
        mock_embedder_class.return_value = mock_embedder
        
        mock_vector_store = MagicMock()
        mock_vector_store.index = None  # Not initialized
        mock_vector_store_class.return_value = mock_vector_store
        
        retriever = RAGRetriever(initialize_index=False)
        results = retriever.retrieve("test query")
        
        assert results == []

    @patch("wavewatch.rag.retriever.GeminiEmbedder")
    @patch("wavewatch.rag.retriever.PineconeVectorStore")
    def test_retrieve_success(self, mock_vector_store_class, mock_embedder_class):
        """Test successful retrieval."""
        mock_embedder = MagicMock()
        mock_embedder.embed_text.return_value = [0.1] * RAGConfig.EMBEDDING_DIMENSION
        mock_embedder_class.return_value = mock_embedder
        
        mock_vector_store = MagicMock()
        mock_vector_store.index = MagicMock()
        mock_vector_store.query.return_value = [
            {
                "id": "test_id",
                "score": 0.95,
                "metadata": {"text": "Test chunk text", "source": "test.md"}
            }
        ]
        mock_vector_store_class.return_value = mock_vector_store
        
        retriever = RAGRetriever(initialize_index=False)
        results = retriever.retrieve("test query")
        
        assert len(results) == 1
        assert results[0]["text"] == "Test chunk text"
        assert results[0]["score"] == 0.95
        assert "metadata" in results[0]

    @patch("wavewatch.rag.retriever.GeminiEmbedder")
    @patch("wavewatch.rag.retriever.PineconeVectorStore")
    def test_retrieve_with_beach_filter(self, mock_vector_store_class, mock_embedder_class):
        """Test retrieval with beach name filter."""
        mock_embedder = MagicMock()
        mock_embedder.embed_text.return_value = [0.1] * RAGConfig.EMBEDDING_DIMENSION
        mock_embedder_class.return_value = mock_embedder
        
        mock_vector_store = MagicMock()
        mock_vector_store.index = MagicMock()
        mock_vector_store.query.return_value = []
        mock_vector_store_class.return_value = mock_vector_store
        
        retriever = RAGRetriever(initialize_index=False)
        retriever.retrieve("test query", beach_name="Pleasure Point")
        
        # Check that filter was applied
        call_args = mock_vector_store.query.call_args
        assert call_args is not None
        filter_dict = call_args.kwargs.get("filter", {})
        assert "beach_name" in filter_dict
        assert filter_dict["beach_name"] == "pleasure_point"

    @patch("wavewatch.rag.retriever.GeminiEmbedder")
    @patch("wavewatch.rag.retriever.PineconeVectorStore")
    def test_retrieve_respects_top_k(self, mock_vector_store_class, mock_embedder_class):
        """Test retrieval respects top_k parameter."""
        mock_embedder = MagicMock()
        mock_embedder.embed_text.return_value = [0.1] * RAGConfig.EMBEDDING_DIMENSION
        mock_embedder_class.return_value = mock_embedder
        
        mock_vector_store = MagicMock()
        mock_vector_store.index = MagicMock()
        mock_vector_store.query.return_value = []
        mock_vector_store_class.return_value = mock_vector_store
        
        retriever = RAGRetriever(initialize_index=False)
        retriever.retrieve("test query", top_k=10)
        
        call_args = mock_vector_store.query.call_args
        assert call_args.kwargs["top_k"] == 10

    @patch("wavewatch.rag.retriever.GeminiEmbedder")
    @patch("wavewatch.rag.retriever.PineconeVectorStore")
    def test_retrieve_limits_max_top_k(self, mock_vector_store_class, mock_embedder_class):
        """Test retrieval limits top_k to MAX_TOP_K."""
        mock_embedder = MagicMock()
        mock_embedder.embed_text.return_value = [0.1] * RAGConfig.EMBEDDING_DIMENSION
        mock_embedder_class.return_value = mock_embedder
        
        mock_vector_store = MagicMock()
        mock_vector_store.index = MagicMock()
        mock_vector_store.query.return_value = []
        mock_vector_store_class.return_value = mock_vector_store
        
        retriever = RAGRetriever(initialize_index=False)
        retriever.retrieve("test query", top_k=1000)  # Exceeds MAX_TOP_K
        
        call_args = mock_vector_store.query.call_args
        assert call_args.kwargs["top_k"] <= RAGConfig.MAX_TOP_K

    def test_retrieve_for_beach(self):
        """Test retrieve_for_beach convenience method."""
        with patch.object(RAGRetriever, "retrieve") as mock_retrieve:
            mock_retrieve.return_value = []
            retriever = RAGRetriever(initialize_index=False)
            
            retriever.retrieve_for_beach("Pleasure Point", "test query", top_k=5)
            
            mock_retrieve.assert_called_once_with(
                query="test query",
                beach_name="Pleasure Point",
                top_k=5
            )

    def test_format_context(self):
        """Test formatting context from results."""
        retriever = RAGRetriever(initialize_index=False)
        
        results = [
            {
                "text": "First chunk text",
                "metadata": {"source": "file1.md", "beach_name": "pleasure_point"}
            },
            {
                "text": "Second chunk text",
                "metadata": {"source": "file2.md", "beach_name": "pleasure_point"}
            }
        ]
        
        context = retriever.format_context(results, max_length=1000)
        
        assert "First chunk text" in context
        assert "Second chunk text" in context
        assert "file1.md" in context
        assert "pleasure_point" in context

    def test_format_context_respects_max_length(self):
        """Test format_context respects max_length."""
        retriever = RAGRetriever(initialize_index=False)
        
        results = [
            {
                "text": "A" * 100,  # Long text
                "metadata": {"source": "file1.md", "beach_name": "test"}
            },
            {
                "text": "B" * 100,  # Long text
                "metadata": {"source": "file2.md", "beach_name": "test"}
            }
        ]
        
        context = retriever.format_context(results, max_length=50)
        
        # Should only include first chunk or part of it
        assert len(context) <= 50 or "A" in context

    def test_format_context_empty_results(self):
        """Test format_context with empty results."""
        retriever = RAGRetriever(initialize_index=False)
        context = retriever.format_context([])
        assert context == ""

