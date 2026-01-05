"""
Knowledge base utilities for RAG system.
"""

from pathlib import Path
from typing import Optional
from .config import RAGConfig


def beach_has_knowledge_base(beach_name: str) -> bool:
    """
    Check if a knowledge base exists for a given beach.

    Args:
        beach_name: Name of the beach (e.g., "Pleasure Point", "pleasure_point")

    Returns:
        True if knowledge base folder exists, False otherwise
    """
    # Normalize beach name
    normalized_name = beach_name.lower().replace(" ", "_").replace("-", "_")
    
    # Check if beach folder exists
    beach_path = RAGConfig.BEACHES_PATH / normalized_name
    
    if not beach_path.exists() or not beach_path.is_dir():
        return False
    
    # Check if there are any markdown files
    md_files = list(beach_path.glob("*.md"))
    return len(md_files) > 0


def get_beach_knowledge_base_path(beach_name: str) -> Optional[Path]:
    """
    Get the path to a beach's knowledge base folder if it exists.

    Args:
        beach_name: Name of the beach

    Returns:
        Path to knowledge base folder, or None if it doesn't exist
    """
    normalized_name = beach_name.lower().replace(" ", "_").replace("-", "_")
    beach_path = RAGConfig.BEACHES_PATH / normalized_name
    
    if beach_path.exists() and beach_path.is_dir():
        return beach_path
    
    return None

