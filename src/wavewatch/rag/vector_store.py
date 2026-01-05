"""
Pinecone vector store integration for RAG system.
"""

import os
from typing import List, Dict, Optional
from pinecone import (
    Pinecone,
    ServerlessSpec,
    CloudProvider,
    AwsRegion,
    GcpRegion,
    AzureRegion,
    Metric,
)
from .config import RAGConfig


class PineconeVectorStore:
    """Manages vector storage in Pinecone."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        cloud: Optional[str] = None,
        region: Optional[str] = None,
        index_name: Optional[str] = None,
    ):
        """
        Initialize Pinecone vector store.

        Args:
            api_key: Pinecone API key. If None, uses RAGConfig.
            cloud: Cloud provider (aws, gcp, azure). If None, uses RAGConfig.
            region: Region (e.g., us-east-1). If None, uses RAGConfig.
            index_name: Index name. If None, uses RAGConfig.
        """
        self.api_key = api_key or RAGConfig.PINECONE_API_KEY
        self.cloud = cloud or RAGConfig.PINECONE_CLOUD
        self.region = region or RAGConfig.PINECONE_REGION
        self.index_name = index_name or RAGConfig.PINECONE_INDEX_NAME

        if not self.api_key:
            raise ValueError(
                "Pinecone API key is required. Set PINECONE_API_KEY environment variable."
            )

        # Initialize Pinecone client
        self.client = Pinecone(api_key=self.api_key)
        self.index = None

    def initialize_index(self, dimension: int = None, recreate: bool = False):
        """
        Initialize or connect to Pinecone index.

        Args:
            dimension: Embedding dimension. If None, uses RAGConfig.
            recreate: If True, delete and recreate index if it exists.
        """
        dimension = dimension or RAGConfig.EMBEDDING_DIMENSION

        # Check if index exists
        existing_indexes = [idx.name for idx in self.client.list_indexes()]

        if self.index_name in existing_indexes:
            if recreate:
                print(f"Deleting existing index: {self.index_name}")
                self.client.delete_index(self.index_name)
                self._create_index(dimension)
            else:
                print(f"Connecting to existing index: {self.index_name}")
                self.index = self.client.Index(self.index_name)
        else:
            print(f"Creating new index: {self.index_name}")
            self._create_index(dimension)

    def _create_index(self, dimension: int):
        """Create a new Pinecone index."""
        # Map cloud string to CloudProvider enum
        cloud_map = {
            "aws": CloudProvider.AWS,
            "gcp": CloudProvider.GCP,
            "azure": CloudProvider.AZURE,
        }
        cloud_provider = cloud_map.get(self.cloud.lower(), CloudProvider.AWS)
        
        # Map metric string to Metric enum
        metric_map = {
            "cosine": Metric.COSINE,
            "euclidean": Metric.EUCLIDEAN,
            "dotproduct": Metric.DOTPRODUCT,
        }
        metric = metric_map.get(RAGConfig.PINECONE_METRIC.lower(), Metric.COSINE)
        
        # Map region string to appropriate region enum based on cloud provider
        # For simplicity, we'll use string regions which Pinecone also accepts
        # But we can map common regions to enums if needed
        region = self._get_region_enum(cloud_provider, self.region)
        
        self.client.create_index(
            name=self.index_name,
            dimension=dimension,
            metric=metric,
            spec=ServerlessSpec(
                cloud=cloud_provider,
                region=region,
            ),
        )
        # Wait for index to be ready
        import time

        while self.index_name not in [idx.name for idx in self.client.list_indexes()]:
            time.sleep(1)
        self.index = self.client.Index(self.index_name)
    
    def _get_region_enum(self, cloud_provider: CloudProvider, region_str: str):
        """
        Get region enum or string based on cloud provider.
        
        Pinecone accepts both enum and string formats, but enums provide
        better type safety. We'll try to map common regions to enums.
        """
        region_str = region_str.upper().replace("-", "_")
        
        if cloud_provider == CloudProvider.AWS:
            # Map common AWS regions
            aws_region_map = {
                "US_EAST_1": AwsRegion.US_EAST_1,
                "US_WEST_2": AwsRegion.US_WEST_2,
            }
            return aws_region_map.get(region_str, region_str.lower().replace("_", "-"))
        
        elif cloud_provider == CloudProvider.GCP:
            # Map common GCP regions
            gcp_region_map = {
                "US_CENTRAL1": GcpRegion.US_CENTRAL1,
                "US_EAST1": GcpRegion.US_EAST1,
                "US_WEST1": GcpRegion.US_WEST1,
                "EUROPE_WEST1": GcpRegion.EUROPE_WEST1,
            }
            return gcp_region_map.get(region_str, region_str.lower().replace("_", "-"))
        
        elif cloud_provider == CloudProvider.AZURE:
            # Map common Azure regions
            azure_region_map = {
                "EASTUS2": AzureRegion.EASTUS2,
                "WESTUS2": AzureRegion.WESTUS2,
                "WESTEUROPE": AzureRegion.WESTEUROPE,
            }
            return azure_region_map.get(region_str, region_str.lower().replace("_", "-"))
        
        # Fallback to string format
        return region_str.lower().replace("_", "-")

    def upsert_vectors(
        self,
        vectors: List[Dict],
        namespace: Optional[str] = None,
    ):
        """
        Upsert vectors into Pinecone.

        Args:
            vectors: List of dicts with 'id', 'values', and 'metadata'
            namespace: Optional namespace for organization
        """
        if not self.index:
            raise ValueError("Index not initialized. Call initialize_index() first.")

        try:
            # Pinecone expects vectors in format: [(id, values, metadata), ...]
            # But we're using dict format, so convert
            formatted_vectors = []
            for vec in vectors:
                formatted_vectors.append(
                    {
                        "id": vec["id"],
                        "values": vec["values"],
                        "metadata": vec.get("metadata", {}),
                    }
                )

            self.index.upsert(vectors=formatted_vectors, namespace=namespace)
            print(f"Upserted {len(formatted_vectors)} vectors to Pinecone")
        except Exception as e:
            print(f"Error upserting vectors: {e}")
            raise

    def query(
        self,
        query_vector: List[float],
        top_k: int = 5,
        namespace: Optional[str] = None,
        filter: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        Query Pinecone for similar vectors.

        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            namespace: Optional namespace
            filter: Optional metadata filter

        Returns:
            List of results with 'id', 'score', and 'metadata'
        """
        if not self.index:
            raise ValueError("Index not initialized. Call initialize_index() first.")

        try:
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                namespace=namespace,
                filter=filter,
                include_metadata=True,
            )

            # Format results
            formatted_results = []
            for match in results.matches:
                formatted_results.append(
                    {
                        "id": match.id,
                        "score": match.score,
                        "metadata": match.metadata or {},
                    }
                )

            return formatted_results
        except Exception as e:
            print(f"Error querying Pinecone: {e}")
            raise

    def delete_vectors(
        self,
        ids: List[str],
        namespace: Optional[str] = None,
    ):
        """
        Delete vectors from Pinecone.

        Args:
            ids: List of vector IDs to delete
            namespace: Optional namespace
        """
        if not self.index:
            raise ValueError("Index not initialized. Call initialize_index() first.")

        try:
            self.index.delete(ids=ids, namespace=namespace)
            print(f"Deleted {len(ids)} vectors from Pinecone")
        except Exception as e:
            print(f"Error deleting vectors: {e}")
            raise

    def get_stats(self) -> Dict:
        """Get index statistics."""
        if not self.index:
            raise ValueError("Index not initialized. Call initialize_index() first.")

        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}

