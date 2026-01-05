"""
RAG (Retrieval-Augmented Generation) module for WaveWatch.

This module handles knowledge base management, embedding generation,
and vector search for surf forecasting.
"""

from .config import RAGConfig
from .embedder import GeminiEmbedder
from .chunker import DocumentChunker
from .vector_store import PineconeVectorStore
from .retriever import RAGRetriever
from .knowledge_base import beach_has_knowledge_base, get_beach_knowledge_base_path

__all__ = [
    "RAGConfig",
    "GeminiEmbedder",
    "DocumentChunker",
    "PineconeVectorStore",
    "RAGRetriever",
    "beach_has_knowledge_base",
    "get_beach_knowledge_base_path",
]

