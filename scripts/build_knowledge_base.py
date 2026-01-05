#!/usr/bin/env python3
"""
Script to process markdown files and build Pinecone vector database.

Usage:
    python scripts/build_knowledge_base.py [--beach BEACH_NAME] [--recreate]
"""

import sys
import os
from pathlib import Path
from typing import List, Dict
import argparse
from uuid import uuid4

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from wavewatch.rag.config import RAGConfig
from wavewatch.rag.chunker import DocumentChunker
from wavewatch.rag.embedder import GeminiEmbedder
from wavewatch.rag.vector_store import PineconeVectorStore


def get_markdown_files(beach_name: str = None) -> List[Path]:
    """
    Get all markdown files from knowledge base.

    Args:
        beach_name: Optional beach name to filter

    Returns:
        List of markdown file paths
    """
    files = []

    if beach_name:
        # Get files for specific beach
        beach_path = RAGConfig.BEACHES_PATH / beach_name.lower().replace(" ", "_")
        if beach_path.exists():
            files.extend(list(beach_path.glob("*.md")))
    else:
        # Get all beach files
        for beach_dir in RAGConfig.BEACHES_PATH.iterdir():
            if beach_dir.is_dir():
                files.extend(list(beach_dir.glob("*.md")))

        # Get general knowledge files
        if RAGConfig.GENERAL_PATH.exists():
            files.extend(list(RAGConfig.GENERAL_PATH.rglob("*.md")))

    return files


def process_file(
    file_path: Path,
    chunker: DocumentChunker,
    embedder: GeminiEmbedder,
    beach_name: str = None,
) -> List[Dict]:
    """
    Process a markdown file into chunks with embeddings.

    Args:
        file_path: Path to markdown file
        chunker: DocumentChunker instance
        embedder: GeminiEmbedder instance
        beach_name: Optional beach name

    Returns:
        List of vectors ready for Pinecone
    """
    print(f"Processing: {file_path}")

    # Extract beach name from path if not provided
    if not beach_name and "beaches" in str(file_path):
        beach_name = file_path.parent.name

    # Create metadata
    metadata = {
        "source": file_path.stem,
        "file_name": file_path.name,
        "file_path": str(file_path.relative_to(RAGConfig.KNOWLEDGE_BASE_PATH)),
    }
    if beach_name:
        metadata["beach_name"] = beach_name.lower().replace(" ", "_")

    # Chunk document
    chunks = chunker.chunk_file(file_path, metadata=metadata)
    print(f"  Created {len(chunks)} chunks")

    if not chunks:
        return []

    # Generate embeddings
    texts = [chunk["text"] for chunk in chunks]
    print(f"  Generating embeddings...")
    embeddings = embedder.embed_batch(texts, batch_size=50)

    # Create vectors for Pinecone
    vectors = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        # Store text in metadata for retrieval
        chunk_metadata = chunk.get("metadata", {}).copy()
        chunk_metadata["text"] = chunk["text"]
        chunk_metadata["chunk_index"] = i
        chunk_metadata["token_count"] = chunk.get("token_count", 0)

        vector_id = f"{file_path.stem}_{i}_{uuid4().hex[:8]}"

        vectors.append(
            {
                "id": vector_id,
                "values": embedding,
                "metadata": chunk_metadata,
            }
        )

    print(f"  Created {len(vectors)} vectors")
    return vectors


def main():
    """Main function to build knowledge base."""
    parser = argparse.ArgumentParser(description="Build Pinecone knowledge base")
    parser.add_argument(
        "--beach",
        type=str,
        help="Process only specific beach (e.g., 'pleasure_point')",
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Recreate Pinecone index (deletes existing)",
    )
    args = parser.parse_args()

    # Validate configuration
    try:
        RAGConfig.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        return 1

    # Initialize components
    print("Initializing components...")
    chunker = DocumentChunker(
        chunk_size=RAGConfig.CHUNK_SIZE,
        chunk_overlap=RAGConfig.CHUNK_OVERLAP,
        min_chunk_size=RAGConfig.MIN_CHUNK_SIZE,
    )
    embedder = GeminiEmbedder()
    vector_store = PineconeVectorStore()

    # Initialize Pinecone index
    print("Initializing Pinecone index...")
    vector_store.initialize_index(recreate=args.recreate)

    # Get markdown files
    print("Finding markdown files...")
    files = get_markdown_files(beach_name=args.beach)
    print(f"Found {len(files)} markdown files")

    if not files:
        print("No markdown files found!")
        return 1

    # Process files
    all_vectors = []
    for file_path in files:
        try:
            vectors = process_file(file_path, chunker, embedder)
            all_vectors.extend(vectors)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue

    if not all_vectors:
        print("No vectors created!")
        return 1

    # Upsert to Pinecone in batches
    print(f"\nUpserting {len(all_vectors)} vectors to Pinecone...")
    batch_size = 100
    for i in range(0, len(all_vectors), batch_size):
        batch = all_vectors[i : i + batch_size]
        try:
            vector_store.upsert_vectors(batch)
            print(f"  Batch {i//batch_size + 1}/{(len(all_vectors)-1)//batch_size + 1}")
        except Exception as e:
            print(f"Error upserting batch {i//batch_size + 1}: {e}")

    # Get stats
    stats = vector_store.get_stats()
    print(f"\n✅ Knowledge base built successfully!")
    print(f"Total vectors: {stats.get('total_vectors', 'unknown')}")
    print(f"Dimension: {stats.get('dimension', 'unknown')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

