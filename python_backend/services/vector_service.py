"""
Vector database service for RFQ processing platform.

This module provides functionality for semantic search and embeddings 
using Qdrant vector database and OpenAI embeddings.
"""

import os
import json
from typing import List, Dict, Any, Optional, Tuple
import logging

from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.models import Distance, VectorParams, PointStruct

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
COLLECTION_NAME = "supplier_products"
EMBEDDING_DIM = 1536  # OpenAI embedding dimension

class VectorService:
    """Service for vector embeddings and semantic search."""
    
    def __init__(self):
        """Initialize the vector service with Qdrant client and OpenAI client."""
        # Check if OpenAI API key is available
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        if self.openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=self.openai_api_key)
                logger.info("OpenAI client initialized successfully")
                self.use_openai = True
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")
                self.use_openai = False
        else:
            logger.warning("No OpenAI API key found, using fallback embedding method")
            self.use_openai = False
            
        # Use in-memory Qdrant for development if URL not provided
        qdrant_url = os.environ.get("QDRANT_URL")
        if qdrant_url:
            try:
                self.qdrant_client = QdrantClient(url=qdrant_url)
                logger.info(f"Connected to Qdrant at {qdrant_url}")
            except Exception as e:
                logger.error(f"Failed to connect to Qdrant at {qdrant_url}: {str(e)}")
                logger.info("Falling back to in-memory Qdrant database")
                self.qdrant_client = QdrantClient(":memory:")
        else:
            self.qdrant_client = QdrantClient(":memory:")
            logger.info("Using in-memory Qdrant database")
        
        # Create collection if it doesn't exist
        self._create_collection_if_not_exists()
    
    def _create_collection_if_not_exists(self):
        """Create the vector collection if it doesn't exist."""
        collections = self.qdrant_client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if COLLECTION_NAME not in collection_names:
            self.qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE)
            )
            logger.info(f"Created Qdrant collection: {COLLECTION_NAME}")
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embeddings for the given text using OpenAI or fallback method."""
        # Check if OpenAI is available
        if self.use_openai:
            try:
                response = self.openai_client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=text
                )
                return response.data[0].embedding
            except Exception as e:
                logger.error(f"Error creating embedding with OpenAI: {str(e)}")
                # Fall back to the basic embedding method
        
        # Fallback embedding method: TF-IDF style simple embedding
        # This is a very simplified version that creates deterministic embeddings
        # based on word frequencies - not as good as real embeddings but works for demo
        return self.create_simple_embedding(text)
    
    def create_simple_embedding(self, text: str) -> List[float]:
        """
        Create a simple deterministic embedding based on word frequencies.
        This is a fallback method when OpenAI API is not available.
        """
        # Convert to lowercase and remove punctuation
        text = text.lower()
        for char in ',.!?;:()[]{}"\'':
            text = text.replace(char, ' ')
        
        # Split into words
        words = text.split()
        
        # Calculate word frequencies
        word_freq = {}
        for word in words:
            if word not in word_freq:
                word_freq[word] = 0
            word_freq[word] += 1
        
        # Generate a hash for each word and create a sparse embedding
        # We'll use a deterministic hash function to assign each word to a dimension
        embedding = [0.0] * EMBEDDING_DIM
        
        for word, freq in word_freq.items():
            # Simple hash function to map words to dimensions
            dimension = hash(word) % EMBEDDING_DIM
            # Use square root of frequency as the value (common in TF-IDF)
            embedding[dimension] += (freq ** 0.5)
        
        # Normalize the embedding to have unit length (cosine similarity)
        magnitude = sum(x**2 for x in embedding) ** 0.5
        if magnitude > 0:
            embedding = [x/magnitude for x in embedding]
        
        return embedding
    
    def index_product(self, product_id: int, product_data: Dict[str, Any]) -> bool:
        """
        Index a product in the vector database.
        
        Args:
            product_id: Unique ID of the product
            product_data: Product data including name, description, specifications
            
        Returns:
            bool: True if successfully indexed
        """
        try:
            # Prepare text for embedding
            text_to_embed = f"{product_data['name']} {product_data['description']} "
            
            # Add specifications to text
            specs = product_data.get('specifications', {})
            if specs:
                for key, value in specs.items():
                    text_to_embed += f"{key}: {value} "
            
            # Get embedding
            embedding = self.get_embedding(text_to_embed)
            
            # Create payload with all product data
            payload = {
                "product_id": product_id,
                "name": product_data["name"],
                "category": product_data["category"],
                "supplier_id": product_data["supplierId"],
                "price": product_data["price"],
                "description": product_data["description"],
                "specifications": product_data["specifications"],
                "warranty": product_data.get("warranty", "")
            }
            
            # Index in Qdrant
            self.qdrant_client.upsert(
                collection_name=COLLECTION_NAME,
                points=[
                    PointStruct(
                        id=product_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            
            logger.info(f"Successfully indexed product {product_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error indexing product {product_id}: {str(e)}")
            return False
    
    def index_all_products(self, products: List[Dict[str, Any]]) -> int:
        """
        Index all products in the vector database.
        
        Args:
            products: List of products to index
            
        Returns:
            int: Number of successfully indexed products
        """
        success_count = 0
        for product in products:
            if self.index_product(product["id"], product):
                success_count += 1
                
        logger.info(f"Indexed {success_count} out of {len(products)} products")
        return success_count
    
    def search_similar_products(
        self, 
        query_text: str, 
        category: Optional[str] = None, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for semantically similar products.
        
        Args:
            query_text: Text to search for
            category: Optional category to filter by
            limit: Maximum number of results
            
        Returns:
            List of products sorted by relevance
        """
        try:
            # Get embedding for the query
            query_embedding = self.get_embedding(query_text)
            
            # Prepare filter
            filter_param = None
            if category:
                filter_param = models.Filter(
                    must=[
                        models.FieldCondition(
                            key="category",
                            match=models.MatchValue(value=category)
                        )
                    ]
                )
            
            # Search
            search_results = self.qdrant_client.search(
                collection_name=COLLECTION_NAME,
                query_vector=query_embedding,
                limit=limit,
                filter=filter_param
            )
            
            # Format results
            results = []
            for result in search_results:
                product_data = result.payload
                product_data["score"] = result.score
                results.append(product_data)
                
            return results
            
        except Exception as e:
            logger.error(f"Error searching products: {str(e)}")
            return []
    
    def search_rfq_requirements(
        self, 
        requirements: Dict[str, Any],
        category: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for products matching RFQ requirements.
        
        Args:
            requirements: Extracted requirements from RFQ
            category: Product category to search in
            limit: Maximum number of results
            
        Returns:
            List of products sorted by relevance
        """
        # Build search query from requirements
        search_query = ""
        
        # Add title and description
        if "title" in requirements:
            search_query += f"{requirements['title']} "
        if "description" in requirements:
            search_query += f"{requirements['description']} "
        
        # Add specific requirements based on category
        if category.lower() == "laptops" and "laptops" in requirements:
            laptop_reqs = requirements["laptops"]
            search_query += f"processor: {laptop_reqs.get('processor', '')} "
            search_query += f"memory: {laptop_reqs.get('memory', '')} "
            search_query += f"storage: {laptop_reqs.get('storage', '')} "
            search_query += f"display: {laptop_reqs.get('display', '')} "
            search_query += f"battery: {laptop_reqs.get('battery', '')} "
            search_query += f"connectivity: {laptop_reqs.get('connectivity', '')} "
            search_query += f"warranty: {laptop_reqs.get('warranty', '')} "
        
        elif category.lower() == "monitors" and "monitors" in requirements:
            monitor_reqs = requirements["monitors"]
            search_query += f"screen size: {monitor_reqs.get('screenSize', '')} "
            search_query += f"resolution: {monitor_reqs.get('resolution', '')} "
            search_query += f"panel technology: {monitor_reqs.get('panelTech', '')} "
            search_query += f"brightness: {monitor_reqs.get('brightness', '')} "
            search_query += f"contrast ratio: {monitor_reqs.get('contrastRatio', '')} "
            search_query += f"connectivity: {monitor_reqs.get('connectivity', '')} "
            search_query += f"warranty: {monitor_reqs.get('warranty', '')} "
        
        # Perform semantic search
        return self.search_similar_products(search_query, category, limit)

# Create singleton instance
vector_service = VectorService()