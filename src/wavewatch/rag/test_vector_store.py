"""
Tests for PineconeVectorStore.
"""

import pytest
from unittest.mock import patch, MagicMock
from wavewatch.rag.vector_store import PineconeVectorStore
from wavewatch.rag.config import RAGConfig


class TestPineconeVectorStore:
    """Test cases for PineconeVectorStore."""

    def test_initialization_with_api_key(self):
        """Test vector store initializes with provided API key."""
        with patch("wavewatch.rag.vector_store.Pinecone") as mock_pinecone:
            mock_client = MagicMock()
            mock_pinecone.return_value = mock_client
            
            store = PineconeVectorStore(api_key="test_key")
            
            assert store.api_key == "test_key"
            assert store.index is None
            mock_pinecone.assert_called_once_with(api_key="test_key")

    def test_initialization_without_api_key(self):
        """Test vector store initializes with config API key."""
        with patch("wavewatch.rag.vector_store.Pinecone"), \
             patch.object(RAGConfig, "PINECONE_API_KEY", "config_key"):
            store = PineconeVectorStore()
            assert store.api_key == "config_key"

    def test_initialization_no_api_key_raises_error(self):
        """Test vector store raises error when no API key available."""
        with patch.object(RAGConfig, "PINECONE_API_KEY", None):
            with pytest.raises(ValueError) as exc_info:
                PineconeVectorStore()
            assert "API key" in str(exc_info.value)

    @patch("wavewatch.rag.vector_store.Pinecone")
    def test_initialization_with_custom_config(self, mock_pinecone):
        """Test vector store initializes with custom configuration."""
        mock_client = MagicMock()
        mock_pinecone.return_value = mock_client
        
        store = PineconeVectorStore(
            api_key="test_key",
            cloud="gcp",
            region="us-central1",
            index_name="custom-index"
        )
        
        assert store.cloud == "gcp"
        assert store.region == "us-central1"
        assert store.index_name == "custom-index"

    @patch("wavewatch.rag.vector_store.Pinecone")
    @patch("time.sleep")
    def test_initialize_index_creates_new(self, mock_sleep, mock_pinecone):
        """Test initialize_index creates new index when it doesn't exist."""
        mock_client = MagicMock()
        mock_index = MagicMock()
        mock_client.Index.return_value = mock_index
        
        # Mock index object that will be returned after creation
        mock_index_obj = MagicMock()
        mock_index_obj.name = RAGConfig.PINECONE_INDEX_NAME
        
        # Track calls to simulate index appearing after creation
        call_count = [0]
        def list_indexes_side_effect():
            call_count[0] += 1
            if call_count[0] == 1:
                return []  # First call - no indexes
            else:
                return [mock_index_obj]  # Subsequent calls - index exists
        
        mock_client.list_indexes.side_effect = list_indexes_side_effect
        mock_pinecone.return_value = mock_client
        
        store = PineconeVectorStore(api_key="test_key")
        store.initialize_index(dimension=768, recreate=False)
        
        # Should call create_index
        assert mock_client.create_index.called
        # Should eventually connect to the index
        assert store.index == mock_index

    @patch("wavewatch.rag.vector_store.Pinecone")
    def test_initialize_index_connects_existing(self, mock_pinecone):
        """Test initialize_index connects to existing index."""
        mock_client = MagicMock()
        mock_index = MagicMock()
        mock_client.Index.return_value = mock_index
        
        # Mock existing index
        mock_index_obj = MagicMock()
        mock_index_obj.name = RAGConfig.PINECONE_INDEX_NAME
        mock_client.list_indexes.return_value = [mock_index_obj]
        
        mock_pinecone.return_value = mock_client
        
        store = PineconeVectorStore(api_key="test_key")
        store.initialize_index(dimension=768, recreate=False)
        
        # Should connect to existing index
        assert store.index == mock_index

    @patch("wavewatch.rag.vector_store.Pinecone")
    def test_upsert_vectors_success(self, mock_pinecone):
        """Test successful vector upsert."""
        mock_client = MagicMock()
        mock_index = MagicMock()
        mock_client.Index.return_value = mock_index
        mock_pinecone.return_value = mock_client
        
        store = PineconeVectorStore(api_key="test_key")
        store.index = mock_index
        
        vectors = [
            {
                "id": "vec1",
                "values": [0.1, 0.2, 0.3],
                "metadata": {"text": "test"}
            }
        ]
        
        store.upsert_vectors(vectors)
        
        mock_index.upsert.assert_called_once()

    @patch("wavewatch.rag.vector_store.Pinecone")
    def test_upsert_vectors_no_index_raises_error(self, mock_pinecone):
        """Test upsert_vectors raises error when index not initialized."""
        mock_client = MagicMock()
        mock_pinecone.return_value = mock_client
        
        store = PineconeVectorStore(api_key="test_key")
        # index is None
        
        with pytest.raises(ValueError) as exc_info:
            store.upsert_vectors([{"id": "test", "values": [0.1]}])
        assert "not initialized" in str(exc_info.value)

    @patch("wavewatch.rag.vector_store.Pinecone")
    def test_query_success(self, mock_pinecone):
        """Test successful query."""
        mock_client = MagicMock()
        mock_index = MagicMock()
        mock_client.Index.return_value = mock_index
        mock_pinecone.return_value = mock_client
        
        # Mock query response
        mock_match = MagicMock()
        mock_match.id = "test_id"
        mock_match.score = 0.95
        mock_match.metadata = {"text": "test"}
        mock_response = MagicMock()
        mock_response.matches = [mock_match]
        mock_index.query.return_value = mock_response
        
        store = PineconeVectorStore(api_key="test_key")
        store.index = mock_index
        
        results = store.query([0.1] * RAGConfig.EMBEDDING_DIMENSION, top_k=5)
        
        assert len(results) == 1
        assert results[0]["id"] == "test_id"
        assert results[0]["score"] == 0.95
        assert "metadata" in results[0]

    @patch("wavewatch.rag.vector_store.Pinecone")
    def test_query_with_filter(self, mock_pinecone):
        """Test query with metadata filter."""
        mock_client = MagicMock()
        mock_index = MagicMock()
        mock_client.Index.return_value = mock_index
        mock_pinecone.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.matches = []
        mock_index.query.return_value = mock_response
        
        store = PineconeVectorStore(api_key="test_key")
        store.index = mock_index
        
        filter_dict = {"beach_name": "pleasure_point"}
        store.query([0.1] * RAGConfig.EMBEDDING_DIMENSION, filter=filter_dict)
        
        call_args = mock_index.query.call_args
        assert call_args.kwargs["filter"] == filter_dict

    @patch("wavewatch.rag.vector_store.Pinecone")
    def test_delete_vectors_success(self, mock_pinecone):
        """Test successful vector deletion."""
        mock_client = MagicMock()
        mock_index = MagicMock()
        mock_client.Index.return_value = mock_index
        mock_pinecone.return_value = mock_client
        
        store = PineconeVectorStore(api_key="test_key")
        store.index = mock_index
        
        store.delete_vectors(["id1", "id2"])
        
        mock_index.delete.assert_called_once_with(ids=["id1", "id2"], namespace=None)

    @patch("wavewatch.rag.vector_store.Pinecone")
    def test_get_stats_success(self, mock_pinecone):
        """Test getting index statistics."""
        mock_client = MagicMock()
        mock_index = MagicMock()
        mock_client.Index.return_value = mock_index
        mock_pinecone.return_value = mock_client
        
        # Mock stats response
        mock_stats = MagicMock()
        mock_stats.total_vector_count = 100
        mock_stats.dimension = 768
        mock_stats.index_fullness = 0.5
        mock_index.describe_index_stats.return_value = mock_stats
        
        store = PineconeVectorStore(api_key="test_key")
        store.index = mock_index
        
        stats = store.get_stats()
        
        assert stats["total_vectors"] == 100
        assert stats["dimension"] == 768
        assert stats["index_fullness"] == 0.5

    @patch("wavewatch.rag.vector_store.Pinecone")
    def test_get_stats_no_index_raises_error(self, mock_pinecone):
        """Test get_stats raises error when index not initialized."""
        mock_client = MagicMock()
        mock_pinecone.return_value = mock_client
        
        store = PineconeVectorStore(api_key="test_key")
        # index is None
        
        with pytest.raises(ValueError) as exc_info:
            store.get_stats()
        assert "not initialized" in str(exc_info.value)

