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
        self.openai_client = None
        self.use_openai = False
        
        # Properly check for OpenAI API key (not Featherless AI key)
        # The OPENAI_API_KEY is separate from FEATHERLESS_API_KEY
        if self.openai_api_key:
            try:
                # Check if we're using the Featherless AI key by mistake
                if self.openai_api_key.startswith("rc_"):
                    logger.warning("Invalid OpenAI API key format detected (starts with 'rc_'). This appears to be a Featherless AI key.")
                    logger.warning("Please set a separate OPENAI_API_KEY environment variable for vector embeddings.")
                    self.use_openai = False
                else:
                    # Only initialize OpenAI client if we have a proper key
                    self.openai_client = OpenAI(api_key=self.openai_api_key)
                    
                    # Test the connection by making a small request
                    try:
                        _ = self.openai_client.embeddings.create(
                            model="text-embedding-ada-002",
                            input="Test connection"
                        )
                        logger.info("OpenAI client initialized and tested successfully")
                        self.use_openai = True
                    except Exception as e:
                        # More detailed error reporting
                        error_msg = str(e)
                        if hasattr(e, 'response'):
                            try:
                                error_data = e.response.json()
                                error_msg = f"Error code: {e.response.status_code} - {error_data}"
                            except:
                                error_msg = f"Error code: {e.response.status_code} - {error_msg}"

                        logger.error(f"OpenAI API connection test failed: {error_msg}")
                        self.use_openai = False
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")
                self.use_openai = False
        else:
            logger.warning("No OpenAI API key found, using fallback embedding method")
            self.use_openai = False
            
        # Suggest adding an API key if not available
        if not self.use_openai:
            logger.warning("For better semantic search accuracy, consider adding an OPENAI_API_KEY")
            
        # Use in-memory Qdrant for development if URL not provided
        qdrant_url = os.environ.get("QDRANT_URL")
        self.qdrant_client = None
        
        if qdrant_url:
            try:
                self.qdrant_client = QdrantClient(url=qdrant_url)
                # Test connection
                _ = self.qdrant_client.get_collections()
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
        if not self.qdrant_client:
            logger.error("Qdrant client is not initialized")
            return
            
        try:
            collections = self.qdrant_client.get_collections().collections
            collection_names = [collection.name for collection in collections]
            
            if COLLECTION_NAME not in collection_names:
                self.qdrant_client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE)
                )
                logger.info(f"Created Qdrant collection: {COLLECTION_NAME}")
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            # Recreate client if needed
            if not self.qdrant_client:
                self.qdrant_client = QdrantClient(":memory:")
                logger.info("Recreated in-memory Qdrant client")
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embeddings for the given text using OpenAI or fallback method."""
        # Check if OpenAI is available and initialized
        if self.use_openai and self.openai_client:
            try:
                response = self.openai_client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=text
                )
                return response.data[0].embedding
            except Exception as e:
                logger.error(f"Error creating embedding with OpenAI: {str(e)}")
                # If we get API errors, temporarily disable OpenAI to avoid further attempts
                if "API" in str(e):
                    logger.warning("Temporarily disabling OpenAI due to API errors")
                    self.use_openai = False
                # Fall back to the basic embedding method
        
        # Fallback embedding method: TF-IDF style simple embedding
        # This is a very simplified version that creates deterministic embeddings
        # based on word frequencies - not as good as real embeddings but works for demo
        return self.create_simple_embedding(text)
    
    def create_simple_embedding(self, text: str) -> List[float]:
        """
        Create a simple deterministic embedding based on word frequencies.
        This is a fallback method when OpenAI API is not available.
        
        Args:
            text: Input text to embed
            
        Returns:
            List[float]: A vector of fixed dimension that represents the text
        """
        try:
            # Handle empty or None input
            if not text or not isinstance(text, str):
                logger.warning(f"Invalid input for embedding: {type(text)}")
                # Return a zero vector with a small random seed to avoid identical embeddings
                import random
                random.seed(0 if not text else hash(str(text)))
                embedding = [0.0] * EMBEDDING_DIM
                # Set a few random dimensions to small values to differentiate
                for _ in range(10):
                    idx = random.randint(0, EMBEDDING_DIM-1)
                    embedding[idx] = random.random() * 0.1
                return embedding
            
            # Convert to lowercase and remove punctuation
            text = text.lower()
            for char in ',.!?;:()[]{}"\'+-*/=<>@#$%^&*_~`|\\':
                text = text.replace(char, ' ')
            
            # Split into words and remove stopwords
            words = text.split()
            stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 
                        'be', 'been', 'being', 'in', 'on', 'at', 'to', 'for', 'with', 
                        'by', 'about', 'as', 'of', 'this', 'that', 'these', 'those'}
            words = [word for word in words if word not in stopwords and len(word) > 1]
            
            # Calculate word frequencies
            word_freq = {}
            for word in words:
                if word not in word_freq:
                    word_freq[word] = 0
                word_freq[word] += 1
            
            # Generate a hash for each word and create a sparse embedding
            # We'll use a deterministic hash function to assign each word to a dimension
            embedding = [0.0] * EMBEDDING_DIM
            
            # Include n-grams (pairs of consecutive words) for better semantic capture
            if len(words) > 1:
                bigrams = [f"{words[i]}_{words[i+1]}" for i in range(len(words)-1)]
                for bigram in bigrams:
                    if bigram not in word_freq:
                        word_freq[bigram] = 0
                    word_freq[bigram] += 0.5  # Lower weight for bigrams
            
            for word, freq in word_freq.items():
                # Create multiple dimensions per word to reduce collisions
                for i in range(3):  # Use 3 dimensions per word
                    # Simple hash function to map words to dimensions
                    dimension = abs(hash(word + str(i))) % EMBEDDING_DIM
                    # Use square root of frequency as the value (common in TF-IDF)
                    embedding[dimension] += (freq ** 0.5)
            
            # Normalize the embedding to have unit length (cosine similarity)
            magnitude = sum(x**2 for x in embedding) ** 0.5
            if magnitude > 0:
                embedding = [x/magnitude for x in embedding]
                
            return embedding
            
        except Exception as e:
            logger.error(f"Error in create_simple_embedding: {str(e)}")
            # Fallback to zeros with a random seed
            import random
            random.seed(hash(str(text)) if text else 0)
            return [random.random() * 0.01 for _ in range(EMBEDDING_DIM)]
    
    def index_product(self, product_id: int, product_data: Dict[str, Any]) -> bool:
        """
        Index a product in the vector database.
        
        Args:
            product_id: Unique ID of the product
            product_data: Product data including name, description, specifications
            
        Returns:
            bool: True if successfully indexed
        """
        if not self.qdrant_client:
            logger.error("Qdrant client is not initialized, cannot index product")
            return False
            
        try:
            # Ensure product_data has required fields
            required_fields = ["name", "category", "description", "specifications", "supplierId", "price"]
            for field in required_fields:
                if field not in product_data:
                    logger.error(f"Missing required field '{field}' in product data")
                    return False
            
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
            try:
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
                logger.error(f"Error in Qdrant upsert operation: {str(e)}")
                # Try to recreate collection if needed
                try:
                    self._create_collection_if_not_exists()
                    # Retry upsert
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
                    logger.info(f"Successfully indexed product {product_id} after recreating collection")
                    return True
                except Exception as retry_error:
                    logger.error(f"Retry failed: {str(retry_error)}")
                    return False
            
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
        if not self.qdrant_client:
            logger.error("Qdrant client is not initialized, cannot perform search")
            return []
            
        # Validate input
        if not query_text or not isinstance(query_text, str):
            logger.error(f"Invalid search query: {type(query_text)}")
            return []
            
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
            try:
                # Search without filter parameter, Qdrant client may have compatibility issues
                # If filtering is needed, we'll do it manually post-search
                search_results = self.qdrant_client.search(
                    collection_name=COLLECTION_NAME,
                    query_vector=query_embedding,
                    limit=limit * 3 if category else limit  # Get more results if we need to filter
                )
                
                # Format results
                results = []
                for result in search_results:
                    product_data = result.payload
                    product_data["score"] = result.score
                    results.append(product_data)
                
                # Manual filtering by category if needed
                if category:
                    filtered_results = []
                    for product in results:
                        if product.get("category", "").lower() == category.lower():
                            filtered_results.append(product)
                    
                    # Only return filtered results if we found any
                    if filtered_results:
                        logger.info(f"Filtered results by category {category}: {len(filtered_results)} of {len(results)}")
                        return filtered_results[:limit]  # Limit to requested number
                
                return results[:limit]  # Limit to requested number
            except Exception as e:
                logger.error(f"Error performing Qdrant search: {str(e)}")
                # Try to recreate collection if needed
                try:
                    self._create_collection_if_not_exists()
                    # Retry search with safely handling the filter
                    if filter_param:
                        try:
                            search_results = self.qdrant_client.search(
                                collection_name=COLLECTION_NAME,
                                query_vector=query_embedding,
                                limit=limit,
                                filter=filter_param
                            )
                        except TypeError:
                            search_results = self.qdrant_client.search(
                                collection_name=COLLECTION_NAME,
                                query_vector=query_embedding,
                                limit=limit
                            )
                    else:
                        search_results = self.qdrant_client.search(
                            collection_name=COLLECTION_NAME,
                            query_vector=query_embedding,
                            limit=limit
                        )
                    
                    # Format results
                    results = []
                    for result in search_results:
                        product_data = result.payload
                        product_data["score"] = result.score
                        results.append(product_data)
                        
                    logger.info("Search successful after recreating collection")
                    return results
                except Exception as retry_error:
                    logger.error(f"Retry failed: {str(retry_error)}")
                    return []
            
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
        if not self.qdrant_client:
            logger.error("Qdrant client is not initialized, cannot search RFQ requirements")
            return []
            
        # Validate inputs
        if not category:
            logger.error("Category is required for searching RFQ requirements")
            return []
            
        if not requirements:
            logger.warning("Empty requirements provided, using generic search")
            search_query = f"{category} product specifications quality features"
            return self.search_similar_products(search_query, category, limit)
        
        # Initialize search query
        search_query = ""
        
        try:
            # Ensure requirements is a dict
            if not isinstance(requirements, dict):
                if hasattr(requirements, "dict"):
                    try:
                        requirements = requirements.dict()
                    except Exception as e:
                        logger.warning(f"Failed to convert to dict using .dict(): {str(e)}")
                elif hasattr(requirements, "__dict__"):
                    try:
                        requirements = requirements.__dict__
                    except Exception as e:
                        logger.warning(f"Failed to convert to dict using .__dict__: {str(e)}")
                else:
                    logger.warning(f"Could not convert requirements to dict, type: {type(requirements)}")
                    requirements = {}
            
            # Build search query from requirements
            # Add title and description
            if "title" in requirements and requirements["title"]:
                search_query += f"{requirements['title']} "
            if "description" in requirements and requirements["description"]:
                search_query += f"{requirements['description']} "
            
            # Add specific requirements based on category
            if category.lower() == "laptops" and "laptops" in requirements:
                laptop_reqs = requirements["laptops"]
                
                # Handle both dict and object formats
                if not isinstance(laptop_reqs, dict) and hasattr(laptop_reqs, "__dict__"):
                    try:
                        laptop_reqs = laptop_reqs.__dict__
                    except Exception as e:
                        logger.warning(f"Failed to convert laptop requirements to dict: {str(e)}")
                
                # Safely extract attributes with fallbacks
                processor = laptop_reqs.get('processor', '') if isinstance(laptop_reqs, dict) else getattr(laptop_reqs, 'processor', '')
                memory = laptop_reqs.get('memory', '') if isinstance(laptop_reqs, dict) else getattr(laptop_reqs, 'memory', '')
                storage = laptop_reqs.get('storage', '') if isinstance(laptop_reqs, dict) else getattr(laptop_reqs, 'storage', '')
                display = laptop_reqs.get('display', '') if isinstance(laptop_reqs, dict) else getattr(laptop_reqs, 'display', '')
                battery = laptop_reqs.get('battery', '') if isinstance(laptop_reqs, dict) else getattr(laptop_reqs, 'battery', '')
                connectivity = laptop_reqs.get('connectivity', '') if isinstance(laptop_reqs, dict) else getattr(laptop_reqs, 'connectivity', '')
                warranty = laptop_reqs.get('warranty', '') if isinstance(laptop_reqs, dict) else getattr(laptop_reqs, 'warranty', '')
                
                search_query += f"processor: {processor} "
                search_query += f"memory: {memory} "
                search_query += f"storage: {storage} "
                search_query += f"display: {display} "
                search_query += f"battery: {battery} "
                search_query += f"connectivity: {connectivity} "
                search_query += f"warranty: {warranty} "
                
                logger.info(f"Built search query for laptop requirements: {search_query[:100]}...")
            
            elif category.lower() == "monitors" and "monitors" in requirements:
                monitor_reqs = requirements["monitors"]
                
                # Handle both dict and object formats
                if not isinstance(monitor_reqs, dict) and hasattr(monitor_reqs, "__dict__"):
                    try:
                        monitor_reqs = monitor_reqs.__dict__
                    except Exception as e:
                        logger.warning(f"Failed to convert monitor requirements to dict: {str(e)}")
                
                # Safely extract attributes with fallbacks
                screen_size = monitor_reqs.get('screenSize', '') if isinstance(monitor_reqs, dict) else getattr(monitor_reqs, 'screenSize', '')
                resolution = monitor_reqs.get('resolution', '') if isinstance(monitor_reqs, dict) else getattr(monitor_reqs, 'resolution', '')
                panel_tech = monitor_reqs.get('panelTech', '') if isinstance(monitor_reqs, dict) else getattr(monitor_reqs, 'panelTech', '')
                brightness = monitor_reqs.get('brightness', '') if isinstance(monitor_reqs, dict) else getattr(monitor_reqs, 'brightness', '')
                contrast_ratio = monitor_reqs.get('contrastRatio', '') if isinstance(monitor_reqs, dict) else getattr(monitor_reqs, 'contrastRatio', '')
                connectivity = monitor_reqs.get('connectivity', '') if isinstance(monitor_reqs, dict) else getattr(monitor_reqs, 'connectivity', '')
                warranty = monitor_reqs.get('warranty', '') if isinstance(monitor_reqs, dict) else getattr(monitor_reqs, 'warranty', '')
                
                search_query += f"screen size: {screen_size} "
                search_query += f"resolution: {resolution} "
                search_query += f"panel technology: {panel_tech} "
                search_query += f"brightness: {brightness} "
                search_query += f"contrast ratio: {contrast_ratio} "
                search_query += f"connectivity: {connectivity} "
                search_query += f"warranty: {warranty} "
                
                logger.info(f"Built search query for monitor requirements: {search_query[:100]}...")
                
            # If we couldn't extract category-specific requirements, add generic product terms
            if not search_query or len(search_query.strip()) < 10:
                search_query = f"{category} product specifications quality features"
                logger.info(f"Using generic search query: {search_query}")
                
        except Exception as e:
            logger.error(f"Error building search query from requirements: {str(e)}")
            # Fallback query
            search_query = f"{category} product specifications quality features"
            logger.info(f"Using fallback search query due to error: {search_query}")
        
        # Perform semantic search
        return self.search_similar_products(search_query, category, limit)

# Create singleton instance
vector_service = VectorService()