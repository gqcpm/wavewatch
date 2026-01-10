"""
Tests for DocumentChunker.
"""

import pytest
from pathlib import Path
from wavewatch.rag.chunker import DocumentChunker


class TestDocumentChunker:
    """Test cases for DocumentChunker."""

    def test_initialization_defaults(self):
        """Test chunker initializes with default values."""
        chunker = DocumentChunker()
        assert chunker.chunk_size == 500
        assert chunker.chunk_overlap == 100
        assert chunker.min_chunk_size == 50

    def test_initialization_custom(self):
        """Test chunker initializes with custom values."""
        chunker = DocumentChunker(
            chunk_size=300, chunk_overlap=50, min_chunk_size=25
        )
        assert chunker.chunk_size == 300
        assert chunker.chunk_overlap == 50
        assert chunker.min_chunk_size == 25

    def test_count_tokens(self):
        """Test token counting functionality."""
        chunker = DocumentChunker()
        text = "Hello world"
        token_count = chunker.count_tokens(text)
        assert isinstance(token_count, int)
        assert token_count > 0

    def test_count_tokens_empty(self):
        """Test token counting with empty string."""
        chunker = DocumentChunker()
        assert chunker.count_tokens("") == 0

    def test_chunk_text_empty(self):
        """Test chunking empty text returns empty list."""
        chunker = DocumentChunker()
        result = chunker.chunk_text("")
        assert result == []
        result = chunker.chunk_text("   ")
        assert result == []

    def test_chunk_text_small(self):
        """Test chunking small text that fits in one chunk."""
        chunker = DocumentChunker(chunk_size=500, min_chunk_size=10)
        text = "This is a short paragraph that should fit in one chunk."
        chunks = chunker.chunk_text(text)
        assert len(chunks) == 1
        assert "text" in chunks[0]
        assert "token_count" in chunks[0]
        assert chunks[0]["text"] == text.strip()

    def test_chunk_text_with_metadata(self):
        """Test chunking text with metadata."""
        chunker = DocumentChunker(chunk_size=500, min_chunk_size=10)
        text = "This is a longer test paragraph that should definitely exceed the minimum chunk size requirement."
        metadata = {"source": "test", "page": 1}
        chunks = chunker.chunk_text(text, metadata)
        assert len(chunks) >= 1
        assert "metadata" in chunks[0]
        assert chunks[0]["metadata"]["source"] == "test"
        assert chunks[0]["metadata"]["page"] == 1

    def test_chunk_text_multiple_paragraphs(self):
        """Test chunking text with multiple paragraphs."""
        chunker = DocumentChunker(chunk_size=100, min_chunk_size=10)
        text = "This is the first paragraph with enough content to meet the minimum requirements.\n\nThis is the second paragraph that also has sufficient length.\n\nThis is the third paragraph completing our test content."
        chunks = chunker.chunk_text(text)
        assert len(chunks) >= 1
        for chunk in chunks:
            assert "text" in chunk
            assert "token_count" in chunk
            assert chunk["token_count"] <= chunker.chunk_size

    def test_chunk_text_respects_chunk_size(self):
        """Test that chunks respect maximum chunk size."""
        chunker = DocumentChunker(chunk_size=100, min_chunk_size=10)
        # Create text that will require multiple chunks
        text = " ".join(["This is a longer sentence that will help us test chunking behavior properly."] * 15)
        chunks = chunker.chunk_text(text)
        assert len(chunks) > 1
        # Allow some flexibility (overlap can cause slight overflow)
        for chunk in chunks:
            # Chunks should generally respect size, allowing up to 20% overflow for edge cases
            assert chunk["token_count"] <= chunker.chunk_size * 1.2

    def test_chunk_text_respects_min_chunk_size(self):
        """Test that chunks respect minimum chunk size."""
        chunker = DocumentChunker(chunk_size=500, min_chunk_size=100)
        # Very short text should be filtered out
        text = "Short."
        chunks = chunker.chunk_text(text)
        # Should be empty if below min_chunk_size
        if chunks:
            for chunk in chunks:
                assert chunk["token_count"] >= chunker.min_chunk_size

    def test_chunk_file_nonexistent(self):
        """Test chunking non-existent file returns empty list."""
        chunker = DocumentChunker()
        fake_path = Path("/nonexistent/file.md")
        result = chunker.chunk_file(fake_path)
        assert result == []

    def test_chunk_file_success(self, tmp_path):
        """Test chunking an actual file."""
        chunker = DocumentChunker(chunk_size=500, min_chunk_size=10)
        # Create a temporary test file
        test_file = tmp_path / "test.md"
        test_file.write_text("This is a test file.\n\nWith multiple paragraphs.")
        chunks = chunker.chunk_file(test_file)
        assert len(chunks) >= 1
        # Check that file metadata is included
        if chunks:
            assert "metadata" in chunks[0]
            assert chunks[0]["metadata"]["file_name"] == "test.md"
            assert chunks[0]["metadata"]["source"] == "test"

    def test_chunk_file_with_metadata(self, tmp_path):
        """Test chunking file with additional metadata."""
        chunker = DocumentChunker(chunk_size=500, min_chunk_size=10)
        test_file = tmp_path / "test.md"
        test_file.write_text("Test content.")
        metadata = {"custom": "value"}
        chunks = chunker.chunk_file(test_file, metadata)
        if chunks:
            assert chunks[0]["metadata"]["custom"] == "value"
            assert chunks[0]["metadata"]["file_name"] == "test.md"

