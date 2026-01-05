"""
RAG retriever for surf knowledge base.
"""

from typing import List, Dict, Optional
from .embedder import GeminiEmbedder
from .vector_store import PineconeVectorStore
from .config import RAGConfig


class RAGRetriever:
    """Retrieves relevant knowledge base chunks using vector search."""

    def __init__(
        self,
        embedder: Optional[GeminiEmbedder] = None,
        vector_store: Optional[PineconeVectorStore] = None,
        initialize_index: bool = True,
    ):
        """
        Initialize RAG retriever.

        Args:
            embedder: GeminiEmbedder instance. If None, creates new one.
            vector_store: PineconeVectorStore instance. If None, creates new one.
            initialize_index: Whether to initialize the Pinecone index. Set False if index might not exist.
        """
        self.embedder = embedder or GeminiEmbedder()
        self.vector_store = vector_store or PineconeVectorStore()
        if initialize_index:
            try:
                self.vector_store.initialize_index()
            except Exception as e:
                print(f"Warning: Could not initialize Pinecone index: {e}")
                print("RAG retrieval will not be available.")

    def retrieve(
        self,
        query: str,
        beach_name: Optional[str] = None,
        top_k: int = None,
        filter_metadata: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: Search query
            beach_name: Optional beach name to filter results
            top_k: Number of results to return
            filter_metadata: Additional metadata filters

        Returns:
            List of relevant chunks with text, score, and metadata.
            Returns empty list if retrieval fails or no results found.
        """
        # Check if vector store is initialized
        if not self.vector_store.index:
            print("Warning: Pinecone index not initialized. Cannot retrieve.")
            return []

        top_k = top_k or RAGConfig.DEFAULT_TOP_K
        top_k = min(top_k, RAGConfig.MAX_TOP_K)

        try:
            # Generate query embedding
            query_embedding = self.embedder.embed_text(query)

            # Build filter
            filter_dict = {}
            if beach_name:
                # Normalize beach name for filtering
                normalized_beach = beach_name.lower().replace(" ", "_").replace("-", "_")
                filter_dict["beach_name"] = normalized_beach
            if filter_metadata:
                filter_dict.update(filter_metadata)

            # Query Pinecone
            results = self.vector_store.query(
                query_vector=query_embedding,
                top_k=top_k,
                filter=filter_dict if filter_dict else None,
            )

            # Format results with text retrieval
            formatted_results = []
            for result in results:
                # Get text from metadata or fetch from source
                text = result.get("metadata", {}).get("text", "")
                if not text:
                    # If text not in metadata, we'd need to fetch from source
                    # For now, skip this result
                    continue

                formatted_results.append(
                    {
                        "text": text,
                        "score": result["score"],
                        "metadata": result.get("metadata", {}),
                        "id": result.get("id"),
                    }
                )

            return formatted_results
        except Exception as e:
            print(f"Error during RAG retrieval: {e}")
            return []

    def retrieve_for_beach(
        self,
        beach_name: str,
        query: str,
        top_k: int = None,
    ) -> List[Dict]:
        """
        Retrieve relevant chunks for a specific beach.

        Args:
            beach_name: Beach name
            query: Search query
            top_k: Number of results to return

        Returns:
            List of relevant chunks
        """
        return self.retrieve(
            query=query,
            beach_name=beach_name,
            top_k=top_k,
        )

    def format_context(self, results: List[Dict], max_length: int = 2000) -> str:
        """
        Format retrieval results into context string for LLM.

        Args:
            results: List of retrieval results
            max_length: Maximum length of context in characters

        Returns:
            Formatted context string
        """
        context_parts = []
        current_length = 0

        for i, result in enumerate(results, 1):
            text = result.get("text", "")
            metadata = result.get("metadata", {})
            source = metadata.get("source", "unknown")
            beach = metadata.get("beach_name", "unknown")

            # Format chunk
            chunk_text = f"[Source: {source}, Beach: {beach}]\n{text}\n"
            chunk_length = len(chunk_text)

            if current_length + chunk_length > max_length:
                break

            context_parts.append(chunk_text)
            current_length += chunk_length

        return "\n---\n".join(context_parts)

