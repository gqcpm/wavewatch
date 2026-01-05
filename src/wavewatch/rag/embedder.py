"""
Gemini embedding generation for RAG system.
"""

import os
from typing import List, Optional
from google import genai
from google.genai import types
from .config import RAGConfig


class GeminiEmbedder:
    """Generate embeddings using Google Gemini."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini embedder.

        Args:
            api_key: Google Gemini API key. If None, uses RAGConfig.
        """
        self.api_key = api_key or RAGConfig.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError(
                "Gemini API key is required. Set GEMINI_API_KEY environment variable."
            )

        self.client = genai.Client(api_key=self.api_key)
        self.model = RAGConfig.EMBEDDING_MODEL

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text using gemini-embedding-001.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        try:
            result = self.client.models.embed_content(
                model=self.model,
                contents=text,
                config=types.EmbedContentConfig(
                    output_dimensionality=RAGConfig.EMBEDDING_DIMENSION
                ),
            )
            # Access embedding values from the result
            # The response structure: result.embeddings[0].values
            if hasattr(result, "embeddings") and isinstance(result.embeddings, list) and len(result.embeddings) > 0:
                embedding_obj = result.embeddings[0]
                if hasattr(embedding_obj, "values"):
                    embedding_values = embedding_obj.values
                else:
                    raise ValueError("Embedding object does not have 'values' attribute")
            else:
                raise ValueError("Response does not contain embeddings list")
            
            # Ensure we return a list of floats
            if not isinstance(embedding_values, list):
                raise ValueError(f"Embedding values are not a list: {type(embedding_values)}")
            
            # Ensure all values are floats
            return [float(x) for x in embedding_values]
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise

    def embed_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.

        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process per batch

        Returns:
            List of embedding vectors
        """
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            try:
                # Gemini supports batch embedding - pass list of texts
                results = self.client.models.embed_content(
                    model=self.model,
                    contents=batch,
                    config=types.EmbedContentConfig(
                        output_dimensionality=RAGConfig.EMBEDDING_DIMENSION
                    ),
                )
                # Handle batch response - results should contain multiple embeddings
                # Response structure: results.embeddings (list) where each has .values
                if hasattr(results, "embeddings") and isinstance(results.embeddings, list):
                    # Multiple embeddings in one response
                    for emb_obj in results.embeddings:
                        if hasattr(emb_obj, "values"):
                            emb_values = emb_obj.values
                            # Ensure all values are floats
                            if isinstance(emb_values, list):
                                embeddings.append([float(x) for x in emb_values])
                            else:
                                raise ValueError(f"Embedding values are not a list: {type(emb_values)}")
                        else:
                            raise ValueError("Embedding object does not have 'values' attribute")
                else:
                    raise ValueError("Response does not contain embeddings list")
            except Exception as e:
                print(f"Error in batch embedding (batch {i//batch_size + 1}): {e}")
                # Fallback to individual embedding
                for text in batch:
                    try:
                        embeddings.append(self.embed_text(text))
                    except Exception as e2:
                        print(f"Error embedding individual text: {e2}")
                        # Return zero vector as fallback
                        embeddings.append([0.0] * RAGConfig.EMBEDDING_DIMENSION)

        return embeddings

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings."""
        return RAGConfig.EMBEDDING_DIMENSION

