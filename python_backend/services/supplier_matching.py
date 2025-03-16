"""
Supplier matching service for RFQ processing platform.

This module provides functions to match suppliers with RFQ requirements
based on various criteria including price, quality, and delivery time.
It now includes semantic search capabilities using vector embeddings.
"""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional
import json

from ..models.db_storage import DatabaseStorage
from ..models.schemas import SupplierMatch, Product, Supplier, ExtractedRequirement
from .vector_service import vector_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database storage
db_storage = DatabaseStorage()

def parse_delivery_time(delivery_time: str) -> float:
    """Parse delivery time string to get average days"""
    if not delivery_time:
        return 30.0
    
    # Try to extract numbers from the delivery time string
    numbers = re.findall(r'\d+', delivery_time)
    if not numbers:
        return 30.0
    
    # If there's a range (e.g., "15-30 days"), take the average
    if len(numbers) >= 2:
        return (float(numbers[0]) + float(numbers[1])) / 2
    
    # If there's just one number, use that
    return float(numbers[0])

def compare_processors(requirement: str, spec: str) -> float:
    """Compare processor specifications and return a score between 0 and 1"""
    if not requirement or not spec:
        return 0.5
    
    req_lower = requirement.lower()
    spec_lower = spec.lower()
    
    # Check for exact match
    if req_lower == spec_lower:
        return 1.0
    
    # Extract processor generation and model information
    req_gen = re.search(r'i(\d+)', req_lower)
    spec_gen = re.search(r'i(\d+)', spec_lower)
    
    # Compare Intel Core i-series processors
    if req_gen and spec_gen:
        req_i = int(req_gen.group(1))
        spec_i = int(spec_gen.group(1))
        
        # Higher generation is better
        if spec_i > req_i:
            return 1.0
        elif spec_i == req_i:
            return 0.9
        else:
            return max(0.5, 1.0 - (req_i - spec_i) * 0.2)  # Deduct 20% per generation below
    
    # Compare AMD Ryzen processors
    req_ryzen = re.search(r'ryzen\s*(\d+)', req_lower)
    spec_ryzen = re.search(r'ryzen\s*(\d+)', spec_lower)
    
    if req_ryzen and spec_ryzen:
        req_r = int(req_ryzen.group(1))
        spec_r = int(spec_ryzen.group(1))
        
        # Higher series is better
        if spec_r > req_r:
            return 1.0
        elif spec_r == req_r:
            return 0.9
        else:
            return max(0.5, 1.0 - (req_r - spec_r) * 0.2)  # Deduct 20% per series below
    
    # If types don't match, give a moderate score if the spec seems high-end
    if 'i7' in spec_lower or 'i9' in spec_lower or 'ryzen 7' in spec_lower or 'ryzen 9' in spec_lower:
        return 0.8
    elif 'i5' in spec_lower or 'ryzen 5' in spec_lower:
        return 0.7
    
    # Default score for other cases
    return 0.6

def compare_memory(requirement: str, spec: str) -> float:
    """Compare memory specifications and return a score between 0 and 1"""
    if not requirement or not spec:
        return 0.5
    
    # Extract memory size in GB
    req_size = re.search(r'(\d+)\s*gb', requirement.lower())
    spec_size = re.search(r'(\d+)\s*gb', spec.lower())
    
    if req_size and spec_size:
        req_gb = int(req_size.group(1))
        spec_gb = int(spec_size.group(1))
        
        # More memory is better
        if spec_gb >= req_gb:
            # Exactly matching or exceeding gets full score
            return 1.0
        else:
            # Deduct 20% for each 4GB less than required
            return max(0.5, 1.0 - ((req_gb - spec_gb) / 4) * 0.2)
    
    # Check for DDR type
    req_ddr = re.search(r'ddr(\d)', requirement.lower())
    spec_ddr = re.search(r'ddr(\d)', spec.lower())
    
    if req_ddr and spec_ddr:
        req_ver = int(req_ddr.group(1))
        spec_ver = int(spec_ddr.group(1))
        
        # Higher DDR version is better
        if spec_ver > req_ver:
            return 0.9  # Bonus for better DDR
        elif spec_ver == req_ver:
            return 0.8
        else:
            return max(0.5, 0.8 - (req_ver - spec_ver) * 0.1)  # Deduct 10% per DDR version below
    
    # Default score for other cases
    return 0.6

def compare_storage(requirement: str, spec: str) -> float:
    """Compare storage specifications and return a score between 0 and 1"""
    if not requirement or not spec:
        return 0.5
    
    req_lower = requirement.lower()
    spec_lower = spec.lower()
    
    # Convert TB to GB for comparison
    req_tb = re.search(r'(\d+(\.\d+)?)\s*tb', req_lower)
    spec_tb = re.search(r'(\d+(\.\d+)?)\s*tb', spec_lower)
    
    # Extract GB values
    req_gb = re.search(r'(\d+)\s*gb', req_lower)
    spec_gb = re.search(r'(\d+)\s*gb', spec_lower)
    
    # Calculate storage sizes in GB
    req_size_gb = 0
    spec_size_gb = 0
    
    if req_tb:
        req_size_gb = float(req_tb.group(1)) * 1024
    elif req_gb:
        req_size_gb = float(req_gb.group(1))
        
    if spec_tb:
        spec_size_gb = float(spec_tb.group(1)) * 1024
    elif spec_gb:
        spec_size_gb = float(spec_gb.group(1))
    
    # Compare storage types (SSD is better than HDD)
    req_type_score = 0.8 if 'ssd' in req_lower else 0.5
    spec_type_score = 0.8 if 'ssd' in spec_lower else 0.5
    
    # NVMe is better than regular SSD
    if 'nvme' in spec_lower:
        spec_type_score = 1.0
    
    # Compare storage size
    size_score = 0.7
    if req_size_gb > 0 and spec_size_gb > 0:
        if spec_size_gb >= req_size_gb:
            size_score = 1.0
        else:
            # Deduct 10% for each 256GB less than required
            size_score = max(0.5, 1.0 - ((req_size_gb - spec_size_gb) / 256) * 0.1)
    
    # Combine scores (size is more important than type)
    return size_score * 0.7 + spec_type_score * 0.3

def compare_display(requirement: str, spec: str) -> float:
    """Compare display specifications and return a score between 0 and 1"""
    if not requirement or not spec:
        return 0.5
    
    req_lower = requirement.lower()
    spec_lower = spec.lower()
    
    # Extract display size
    req_size = re.search(r'(\d+(\.\d+)?)["\'-]?\s*(inch|in)?', req_lower)
    spec_size = re.search(r'(\d+(\.\d+)?)["\'-]?\s*(inch|in)?', spec_lower)
    
    # Extract resolution
    res_scores = {
        'hd': 0.6,
        '1366': 0.6,
        '768': 0.6,
        'fhd': 0.8,
        '1080': 0.8,
        '1920': 0.8,
        'qhd': 0.9,
        '1440': 0.9,
        '2560': 0.9,
        '4k': 1.0,
        'uhd': 1.0,
        '2160': 1.0,
        '3840': 1.0
    }
    
    # Calculate size score
    size_score = 0.7
    if req_size and spec_size:
        req_inches = float(req_size.group(1))
        spec_inches = float(spec_size.group(1))
        
        if abs(spec_inches - req_inches) <= 1:
            # Within 1 inch is good enough
            size_score = 1.0
        else:
            # Deduct 10% for each inch difference, but not below 0.5
            size_score = max(0.5, 1.0 - abs(spec_inches - req_inches) * 0.1)
    
    # Calculate resolution score
    res_score = 0.7  # Default
    for key, score in res_scores.items():
        if key in req_lower and key in spec_lower:
            res_score = score
            break
        elif key in spec_lower and key not in req_lower:
            # Higher resolution than required is good
            for req_key, req_score in res_scores.items():
                if req_key in req_lower and res_scores[key] > req_score:
                    res_score = min(1.0, req_score + 0.1)  # Slight bonus for better resolution
                    break
    
    # Combine scores (resolution is more important than exact size)
    return size_score * 0.4 + res_score * 0.6

def compare_warranty(requirement: str, spec: str) -> float:
    """Compare warranty specifications and return a score between 0 and 1"""
    if not requirement or not spec:
        return 0.5
    
    # Extract warranty duration in years
    req_years = re.search(r'(\d+)\s*(year|yr)', requirement.lower())
    spec_years = re.search(r'(\d+)\s*(year|yr)', spec.lower())
    
    # Calculate warranty period score
    if req_years and spec_years:
        req_period = int(req_years.group(1))
        spec_period = int(spec_years.group(1))
        
        if spec_period >= req_period:
            return 1.0  # Meeting or exceeding required warranty
        else:
            # Deduct 25% for each year less than required
            return max(0.5, 1.0 - (req_period - spec_period) * 0.25)
    
    # Check warranty type (onsite is better than return-to-base)
    warranty_type_score = 0.6  # Default
    
    if 'onsite' in spec.lower():
        warranty_type_score = 0.9
    if 'next day' in spec.lower() or 'nbd' in spec.lower():
        warranty_type_score = 1.0
    
    return warranty_type_score

def calculate_match_score(product: Product, supplier: Supplier, requirements: ExtractedRequirement, category: str) -> Tuple[float, Dict[str, float]]:
    """Calculate match score between product and RFQ requirements"""
    # Get category-specific requirements
    category_req = None
    specs = product.specifications if isinstance(product.specifications, dict) else {}
    
    if category.lower() == "laptops" and hasattr(requirements, "laptops") and requirements.laptops:
        category_req = requirements.laptops
    elif category.lower() == "monitors" and hasattr(requirements, "monitors") and requirements.monitors:
        category_req = requirements.monitors
    
    if not category_req:
        return 50.0, {"price": 50.0, "quality": 50.0, "delivery": 50.0}
    
    # Get criteria weights
    price_weight = requirements.criteria.price.get("weight", 50) if hasattr(requirements, "criteria") else 50
    quality_weight = requirements.criteria.quality.get("weight", 30) if hasattr(requirements, "criteria") else 30
    delivery_weight = requirements.criteria.delivery.get("weight", 20) if hasattr(requirements, "criteria") else 20
    
    # Calculate price score (lower price is better)
    price_score = 50.0  # Default mid-range score
    
    # For more sophisticated price scoring, we would need to know the price range for the category
    # Here we use a simple formula based on price point
    if product.price <= 500:
        price_score = 90.0  # Budget option, good for price-sensitive RFQs
    elif product.price <= 1000:
        price_score = 75.0  # Mid-range option
    elif product.price <= 1500:
        price_score = 60.0  # Higher-end option
    else:
        price_score = 40.0  # Premium option, not as good for price-sensitive RFQs
    
    # Calculate quality score
    quality_score = 50.0  # Default mid-range score
    quality_factors = []
    
    if category.lower() == "laptops":
        # Processor comparison
        if hasattr(category_req, "processor") and "processor" in specs:
            proc_score = compare_processors(category_req.processor, specs["processor"]) * 100
            quality_factors.append(("processor", proc_score))
        
        # Memory comparison
        if hasattr(category_req, "memory") and "memory" in specs:
            mem_score = compare_memory(category_req.memory, specs["memory"]) * 100
            quality_factors.append(("memory", mem_score))
        
        # Storage comparison
        if hasattr(category_req, "storage") and "storage" in specs:
            storage_score = compare_storage(category_req.storage, specs["storage"]) * 100
            quality_factors.append(("storage", storage_score))
        
        # Display comparison
        if hasattr(category_req, "display") and "display" in specs:
            display_score = compare_display(category_req.display, specs["display"]) * 100
            quality_factors.append(("display", display_score))
        
        # Warranty comparison
        if hasattr(category_req, "warranty") and hasattr(product, "warranty"):
            warranty_score = compare_warranty(category_req.warranty, product.warranty) * 100
            quality_factors.append(("warranty", warranty_score))
    
    elif category.lower() == "monitors":
        # Screen size and resolution comparisons
        if hasattr(category_req, "screenSize") and "screenSize" in specs:
            screen_score = compare_display(category_req.screenSize, specs["screenSize"]) * 100
            quality_factors.append(("screenSize", screen_score))
        
        if hasattr(category_req, "resolution") and "resolution" in specs:
            res_score = compare_display(category_req.resolution, specs["resolution"]) * 100
            quality_factors.append(("resolution", res_score))
        
        # Panel technology comparison
        if hasattr(category_req, "panelTech") and "panelTech" in specs:
            panel_score = 70.0  # Default
            if specs["panelTech"].lower() == category_req.panelTech.lower():
                panel_score = 100.0
            elif "ips" in specs["panelTech"].lower() and not "ips" in category_req.panelTech.lower():
                panel_score = 90.0  # IPS is generally better than other panels
            quality_factors.append(("panelTech", panel_score))
        
        # Warranty comparison
        if hasattr(category_req, "warranty") and hasattr(product, "warranty"):
            warranty_score = compare_warranty(category_req.warranty, product.warranty) * 100
            quality_factors.append(("warranty", warranty_score))
    
    # Calculate average quality score from all factors
    if quality_factors:
        quality_score = sum(score for _, score in quality_factors) / len(quality_factors)
    
    # Calculate delivery score
    delivery_score = 50.0  # Default mid-range score
    
    # Parse delivery time and calculate score
    delivery_days = parse_delivery_time(supplier.deliveryTime)
    
    # For most business equipment, faster delivery is better
    if delivery_days <= 7:
        delivery_score = 100.0  # Excellent delivery time
    elif delivery_days <= 14:
        delivery_score = 90.0  # Very good delivery time
    elif delivery_days <= 21:
        delivery_score = 80.0  # Good delivery time
    elif delivery_days <= 30:
        delivery_score = 70.0  # Acceptable delivery time
    elif delivery_days <= 45:
        delivery_score = 60.0  # Below average delivery time
    else:
        delivery_score = 50.0  # Poor delivery time
    
    # Apply weights to individual scores
    weighted_price_score = price_score * (price_weight / 100)
    weighted_quality_score = quality_score * (quality_weight / 100)
    weighted_delivery_score = delivery_score * (delivery_weight / 100)
    
    # Calculate total score
    total_score = weighted_price_score + weighted_quality_score + weighted_delivery_score
    
    return total_score, {
        "price": price_score,
        "quality": quality_score,
        "delivery": delivery_score
    }

async def get_quantity_for_category(requirements: ExtractedRequirement, category: str) -> int:
    """Get quantity from requirements for a specific category"""
    if category.lower() == "laptops" and hasattr(requirements, "laptops") and requirements.laptops:
        return requirements.laptops.quantity
    elif category.lower() == "monitors" and hasattr(requirements, "monitors") and requirements.monitors:
        return requirements.monitors.quantity
    return 1  # Default quantity

async def calculate_price_score(product: Product, all_products: List[Product], criteria: Dict[str, Dict[str, int]]) -> float:
    """Calculate price score compared to other products in the same category"""
    if not all_products:
        return 50.0
    
    # Get price range for this category
    prices = [p.price for p in all_products if p.category == product.category]
    if not prices:
        return 50.0
    
    min_price = min(prices)
    max_price = max(prices)
    price_range = max_price - min_price
    
    # Avoid division by zero
    if price_range == 0:
        return 80.0
    
    # Calculate relative position in price range (lower is better)
    relative_position = (product.price - min_price) / price_range
    
    # Invert score (lower price = higher score)
    price_score = 100 - (relative_position * 100)
    
    # Ensure score is within 0-100 range
    return max(0, min(100, price_score))

async def match_suppliers_for_rfq(rfq_id: int) -> List[SupplierMatch]:
    """Match suppliers based on RFQ requirements with semantic search capabilities"""
    try:
        # Get RFQ data
        rfq = await db_storage.get_rfq_by_id(rfq_id)
        if not rfq:
            logger.error(f"RFQ with ID {rfq_id} not found")
            return []
        
        requirements = rfq.extractedRequirements
        if not requirements:
            logger.error(f"No requirements found for RFQ {rfq_id}")
            return []
        
        # Convert requirements to object if stored as JSON string
        if isinstance(requirements, str):
            try:
                requirements = json.loads(requirements)
            except:
                logger.error(f"Failed to parse requirements for RFQ {rfq_id}")
                return []
        
        # Get categories from requirements
        categories = requirements.get("categories", []) if isinstance(requirements, dict) else requirements.categories
        if not categories:
            logger.error(f"No categories found for RFQ {rfq_id}")
            return []
        
        match_results = []
        use_vector_search = True  # Flag to control whether to use vector search
        
        for category in categories:
            # Step 1: Index all products in vector database for semantic search
            all_products = await db_storage.get_products_by_category(category)
            
            if not all_products:
                logger.warning(f"No products found for category {category}")
                continue
            
            # Convert products to dict format for vector indexing
            products_for_indexing = []
            for product in all_products:
                if hasattr(product, "to_dict"):
                    product_dict = product.to_dict()
                else:
                    # Create dictionary manually
                    product_dict = {
                        "id": product.id,
                        "name": product.name,
                        "category": product.category,
                        "supplierId": product.supplierId,
                        "description": product.description,
                        "price": product.price,
                        "specifications": product.specifications,
                        "warranty": getattr(product, "warranty", "")
                    }
                products_for_indexing.append(product_dict)
            
            # Index products in vector database
            if use_vector_search:
                try:
                    indexed_count = vector_service.index_all_products(products_for_indexing)
                    logger.info(f"Indexed {indexed_count} products for category {category}")
                    
                    # Step 2: Use semantic search to find relevant products
                    semantic_results = vector_service.search_rfq_requirements(
                        requirements if isinstance(requirements, dict) else requirements.dict(),
                        category,
                        limit=20  # Get top 20 matches from semantic search
                    )
                    
                    if semantic_results:
                        logger.info(f"Found {len(semantic_results)} semantic matches for category {category}")
                        
                        # Step 3: Process semantic search results
                        for result in semantic_results:
                            # Get product and supplier details from database
                            product_id = result.get("product_id")
                            if product_id is None:
                                logger.warning("Missing product_id in search result")
                                continue
                                
                            try:
                                # Convert to int if not already
                                if not isinstance(product_id, int):
                                    product_id = int(product_id)
                                
                                product = await db_storage.get_product_by_id(product_id)
                                if not product:
                                    logger.warning(f"Product not found for id {product_id}")
                                    continue
                                    
                                supplier = await db_storage.get_supplier_by_id(product.supplierId)
                                if not supplier:
                                    logger.warning(f"Supplier not found for id {product.supplierId}")
                                    continue
                                
                                # Get semantic similarity score
                                semantic_score = result.get("score", 0.5) * 100
                                
                                # Create ExtractedRequirement instance if needed
                                req_for_scoring = requirements
                                if isinstance(requirements, dict) and not isinstance(requirements, ExtractedRequirement):
                                    from ..models.schemas import ExtractedRequirement
                                    # Create a compatible object for scoring
                                    req_for_scoring = ExtractedRequirement(**requirements)
                                
                                # Calculate additional match details using traditional approach
                                match_score, match_details = calculate_match_score(product, supplier, req_for_scoring, category)
                            except (ValueError, TypeError) as e:
                                logger.error(f"Error processing search result: {str(e)}")
                                continue
                            
                            # Blend semantic score with traditional score
                            # Give semantic score 30% weight
                            blended_score = (match_score * 0.7) + (semantic_score * 0.3)
                            
                            # Calculate total price based on quantity
                            try:
                                quantity = await get_quantity_for_category(req_for_scoring, category)
                                total_price = product.price * quantity
                            except Exception as e:
                                logger.error(f"Error calculating semantic match quantity: {str(e)}")
                                quantity = 1
                                total_price = product.price
                            
                            # Create a supplier match object with blended score
                            supplier_match = SupplierMatch(
                                supplier=supplier,
                                product=product,
                                matchScore=blended_score,
                                matchDetails={
                                    "price": match_details["price"],
                                    "quality": match_details["quality"],
                                    "delivery": match_details["delivery"],
                                    "semantic": semantic_score
                                },
                                totalPrice=total_price
                            )
                            
                            match_results.append(supplier_match)
                            
                            # Create a proposal in storage
                            await db_storage.create_proposal({
                                "rfqId": rfq_id,
                                "productId": product.id,
                                "score": blended_score,
                                "priceScore": match_details["price"],
                                "qualityScore": match_details["quality"],
                                "deliveryScore": match_details["delivery"],
                                "emailContent": None
                            })
                        
                        # If we got semantic results, skip traditional matching for this category
                        continue
                        
                except Exception as e:
                    logger.error(f"Error in vector search for category {category}: {str(e)}")
                    # Fall back to traditional matching if vector search fails
                    logger.info("Falling back to traditional matching")
            
            # Traditional matching approach (used as fallback or if vector search is disabled)
            logger.info(f"Using traditional matching for category {category}")
            for product in all_products:
                # Get supplier details
                supplier = await db_storage.get_supplier_by_id(product.supplierId)
                
                if supplier:
                    try:
                        # Create ExtractedRequirement instance if needed
                        req_for_scoring = requirements
                        if isinstance(requirements, dict) and not isinstance(requirements, ExtractedRequirement):
                            from ..models.schemas import ExtractedRequirement
                            # Create a compatible object for scoring
                            req_for_scoring = ExtractedRequirement(**requirements)
                        
                        # Calculate match score based on RFQ criteria
                        match_score, match_details = calculate_match_score(product, supplier, req_for_scoring, category)
                        
                        # Calculate total price based on quantity
                        quantity = await get_quantity_for_category(req_for_scoring, category)
                        total_price = product.price * quantity
                    except Exception as e:
                        logger.error(f"Error in traditional matching: {str(e)}")
                        # Use default values if calculation fails
                        match_score = 50.0
                        match_details = {"price": 50.0, "quality": 50.0, "delivery": 50.0}
                        quantity = 1
                        total_price = product.price
                    
                    # Create a supplier match object
                    supplier_match = SupplierMatch(
                        supplier=supplier,
                        product=product,
                        matchScore=match_score,
                        matchDetails={
                            "price": match_details["price"],
                            "quality": match_details["quality"],
                            "delivery": match_details["delivery"]
                        },
                        totalPrice=total_price
                    )
                    
                    match_results.append(supplier_match)
                    
                    # Create a proposal in storage
                    await db_storage.create_proposal({
                        "rfqId": rfq_id,
                        "productId": product.id,
                        "score": match_score,
                        "priceScore": match_details["price"],
                        "qualityScore": match_details["quality"],
                        "deliveryScore": match_details["delivery"],
                        "emailContent": None
                    })
        
        # Sort match results by match score (descending)
        match_results.sort(key=lambda x: x.matchScore, reverse=True)
        
        logger.info(f"Total supplier matches for RFQ {rfq_id}: {len(match_results)}")
        return match_results
    
    except Exception as e:
        logger.error(f"Error matching suppliers for RFQ {rfq_id}: {str(e)}")
        return []