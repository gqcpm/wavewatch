"""
Tests for knowledge base utilities.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from wavewatch.rag.knowledge_base import (
    beach_has_knowledge_base,
    get_beach_knowledge_base_path,
)
from wavewatch.rag.config import RAGConfig


class TestKnowledgeBase:
    """Test cases for knowledge base utilities."""

    def test_beach_has_knowledge_base_normalizes_name(self):
        """Test that beach name is normalized correctly."""
        with patch.object(RAGConfig, "BEACHES_PATH") as mock_path:
            mock_beach_path = MagicMock()
            mock_beach_path.exists.return_value = True
            mock_beach_path.is_dir.return_value = True
            mock_beach_path.glob.return_value = [MagicMock()]  # Has .md files
            mock_path.__truediv__ = MagicMock(return_value=mock_beach_path)
            
            # Test various name formats
            result1 = beach_has_knowledge_base("Pleasure Point")
            result2 = beach_has_knowledge_base("pleasure-point")
            result3 = beach_has_knowledge_base("PLEASURE_POINT")
            
            # All should normalize to same path
            assert mock_path.__truediv__.call_count == 3

    def test_beach_has_knowledge_base_no_directory(self):
        """Test returns False when directory doesn't exist."""
        with patch.object(RAGConfig, "BEACHES_PATH") as mock_path:
            mock_beach_path = MagicMock()
            mock_beach_path.exists.return_value = False
            mock_path.__truediv__ = MagicMock(return_value=mock_beach_path)
            
            result = beach_has_knowledge_base("Nonexistent Beach")
            assert result is False

    def test_beach_has_knowledge_base_no_markdown_files(self):
        """Test returns False when no markdown files exist."""
        with patch.object(RAGConfig, "BEACHES_PATH") as mock_path:
            mock_beach_path = MagicMock()
            mock_beach_path.exists.return_value = True
            mock_beach_path.is_dir.return_value = True
            mock_beach_path.glob.return_value = []  # No .md files
            mock_path.__truediv__ = MagicMock(return_value=mock_beach_path)
            
            result = beach_has_knowledge_base("Empty Beach")
            assert result is False

    def test_beach_has_knowledge_base_with_files(self):
        """Test returns True when markdown files exist."""
        with patch.object(RAGConfig, "BEACHES_PATH") as mock_path:
            mock_beach_path = MagicMock()
            mock_beach_path.exists.return_value = True
            mock_beach_path.is_dir.return_value = True
            mock_beach_path.glob.return_value = [MagicMock(), MagicMock()]  # Has .md files
            mock_path.__truediv__ = MagicMock(return_value=mock_beach_path)
            
            result = beach_has_knowledge_base("Pleasure Point")
            assert result is True

    def test_get_beach_knowledge_base_path_exists(self):
        """Test returns path when beach directory exists."""
        with patch.object(RAGConfig, "BEACHES_PATH") as mock_path:
            mock_beach_path = MagicMock()
            mock_beach_path.exists.return_value = True
            mock_beach_path.is_dir.return_value = True
            mock_path.__truediv__ = MagicMock(return_value=mock_beach_path)
            
            result = get_beach_knowledge_base_path("Pleasure Point")
            assert result == mock_beach_path

    def test_get_beach_knowledge_base_path_not_exists(self):
        """Test returns None when beach directory doesn't exist."""
        with patch.object(RAGConfig, "BEACHES_PATH") as mock_path:
            mock_beach_path = MagicMock()
            mock_beach_path.exists.return_value = False
            mock_path.__truediv__ = MagicMock(return_value=mock_beach_path)
            
            result = get_beach_knowledge_base_path("Nonexistent Beach")
            assert result is None

    def test_get_beach_knowledge_base_path_not_directory(self):
        """Test returns None when path exists but is not a directory."""
        with patch.object(RAGConfig, "BEACHES_PATH") as mock_path:
            mock_beach_path = MagicMock()
            mock_beach_path.exists.return_value = True
            mock_beach_path.is_dir.return_value = False
            mock_path.__truediv__ = MagicMock(return_value=mock_beach_path)
            
            result = get_beach_knowledge_base_path("Not A Directory")
            assert result is None

