"""
Document chunking for RAG system.
"""

import tiktoken
from typing import List, Dict
from pathlib import Path


class DocumentChunker:
    """Chunks documents into smaller pieces for embedding."""

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        min_chunk_size: int = 50,
    ):
        """
        Initialize chunker.

        Args:
            chunk_size: Maximum tokens per chunk
            chunk_overlap: Token overlap between chunks
            min_chunk_size: Minimum chunk size in tokens
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        # Use cl100k_base encoding (used by GPT models)
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))

    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Chunk text into smaller pieces.

        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk

        Returns:
            List of chunk dictionaries with text and metadata
        """
        if not text or not text.strip():
            return []

        # Split by paragraphs first (preserve structure)
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = []
        current_tokens = 0

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            para_tokens = self.count_tokens(paragraph)

            # If paragraph is too large, split by sentences
            if para_tokens > self.chunk_size:
                # Flush current chunk if exists
                if current_chunk:
                    chunk_text = "\n\n".join(current_chunk)
                    if self.count_tokens(chunk_text) >= self.min_chunk_size:
                        chunks.append(self._create_chunk(chunk_text, metadata))
                    current_chunk = []
                    current_tokens = 0

                # Split large paragraph by sentences
                sentences = paragraph.split(". ")
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                    sentence_tokens = self.count_tokens(sentence)

                    if current_tokens + sentence_tokens > self.chunk_size:
                        if current_chunk:
                            chunk_text = ". ".join(current_chunk)
                            if self.count_tokens(chunk_text) >= self.min_chunk_size:
                                chunks.append(
                                    self._create_chunk(chunk_text, metadata)
                                )
                        current_chunk = [sentence]
                        current_tokens = sentence_tokens
                    else:
                        current_chunk.append(sentence)
                        current_tokens += sentence_tokens
            else:
                # Check if adding this paragraph would exceed chunk size
                if current_tokens + para_tokens > self.chunk_size:
                    if current_chunk:
                        chunk_text = "\n\n".join(current_chunk)
                        if self.count_tokens(chunk_text) >= self.min_chunk_size:
                            chunks.append(self._create_chunk(chunk_text, metadata))
                    # Start new chunk with overlap
                    if chunks and self.chunk_overlap > 0:
                        # Get last chunk and use its end as overlap
                        last_chunk = chunks[-1]["text"]
                        overlap_text = self._get_overlap_text(
                            last_chunk, self.chunk_overlap
                        )
                        current_chunk = [overlap_text, paragraph]
                        current_tokens = self.count_tokens("\n\n".join(current_chunk))
                    else:
                        current_chunk = [paragraph]
                        current_tokens = para_tokens
                else:
                    current_chunk.append(paragraph)
                    current_tokens += para_tokens

        # Add final chunk
        if current_chunk:
            chunk_text = "\n\n".join(current_chunk)
            if self.count_tokens(chunk_text) >= self.min_chunk_size:
                chunks.append(self._create_chunk(chunk_text, metadata))

        return chunks

    def _get_overlap_text(self, text: str, overlap_tokens: int) -> str:
        """Get the last N tokens of text for overlap."""
        tokens = self.encoding.encode(text)
        if len(tokens) <= overlap_tokens:
            return text
        overlap_tokens_list = tokens[-overlap_tokens:]
        return self.encoding.decode(overlap_tokens_list)

    def _create_chunk(self, text: str, metadata: Dict = None) -> Dict:
        """Create a chunk dictionary."""
        chunk = {
            "text": text.strip(),
            "token_count": self.count_tokens(text),
        }
        if metadata:
            chunk["metadata"] = metadata.copy()
        return chunk

    def chunk_file(self, file_path: Path, metadata: Dict = None) -> List[Dict]:
        """
        Chunk a markdown file.

        Args:
            file_path: Path to markdown file
            metadata: Metadata to attach to chunks

        Returns:
            List of chunk dictionaries
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Add file-specific metadata
            file_metadata = {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "source": file_path.stem,
            }
            if metadata:
                file_metadata.update(metadata)

            return self.chunk_text(content, file_metadata)
        except Exception as e:
            print(f"Error chunking file {file_path}: {e}")
            return []

