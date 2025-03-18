"""
AI Hardware Matching service for GPU/accelerator procurement platform.

This module provides specialized functions to match suppliers with AI hardware RFQ requirements
based on various criteria including performance metrics, memory specifications, supported frameworks,
and compliance with export regulations.
"""

import re
import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional, Set, Union

from ..models.db_storage import DatabaseStorage
from ..models.schemas import SupplierMatch, Product, Supplier, ExtractedRequirement
from .vector_service import vector_service
from .compliance_service import ComplianceService, check_product_shipping_restrictions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database storage and compliance service
db_storage = DatabaseStorage()
compliance_service = ComplianceService()

# Thresholds for AI hardware comparison
PERFORMANCE_THRESHOLDS = {
    "fp32_tflops": {
        "entry": 5,       # Entry level
        "mid": 20,        # Mid-range
        "high": 50,       # High performance
        "ultra": 100      # Ultra high performance
    },
    "fp16_tflops": {
        "entry": 10,
        "mid": 40,
        "high": 100,
        "ultra": 200
    },
    "memory_size_gb": {
        "entry": 8,
        "mid": 24,
        "high": 48,
        "ultra": 80
    },
    "memory_bandwidth_gbs": {
        "entry": 300,
        "mid": 750,
        "high": 1500,
        "ultra": 2500
    }
}

def ensure_extracted_requirement(requirements: Any) -> ExtractedRequirement:
    """
    Ensure that requirements are in the correct ExtractedRequirement format.
    Convert dictionary to ExtractedRequirement object if needed.
    
    Args:
        requirements: The requirements object or dictionary
        
    Returns:
        ExtractedRequirement object
    """
    if isinstance(requirements, ExtractedRequirement):
        return requirements
        
    if isinstance(requirements, dict):
        try:
            # Create default criteria if missing
            if "criteria" not in requirements:
                requirements["criteria"] = {
                    "price": {"weight": 30},
                    "performance": {"weight": 40},
                    "availability": {"weight": 15},
                    "compliance": {"weight": 15}
                }
                
            return ExtractedRequirement(**requirements)
        except Exception as e:
            logger.error(f"Error converting dict to ExtractedRequirement: {str(e)}")
            
    # If we can't convert, create a minimal valid instance
    return ExtractedRequirement(
        title="Default AI Hardware Requirements",
        categories=["GPU", "AI Accelerator"],
        criteria={
            "price": {"weight": 30},
            "performance": {"weight": 40},
            "availability": {"weight": 15},
            "compliance": {"weight": 15}
        }
    )

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

def compare_compute_performance(required: Dict[str, Any], product: Dict[str, Any]) -> float:
    """
    Compare compute performance between requirements and product specs.
    
    Args:
        required: Required compute performance specifications
        product: Product compute performance specifications
        
    Returns:
        Score between 0 and 1 representing how well the product meets requirements
    """
    if not required or not product:
        return 0.5
    
    # Extract compute specs
    compute_specs = product.get("computeSpecs", {})
    if not compute_specs and "specifications" in product:
        # Try to extract from specifications
        compute_specs = product.get("specifications", {})
    
    if not compute_specs:
        return 0.5
    
    # Initialize scores for different metrics
    fp32_score = tensor_cores_score = cuda_cores_score = int8_score = fp16_score = 0.5
    
    # Check FP32 performance
    if "fp32Performance" in compute_specs and "minComputePower" in required:
        req_fp32 = float(required["minComputePower"])
        prod_fp32 = float(compute_specs["fp32Performance"])
        
        if prod_fp32 >= req_fp32 * 1.5:
            fp32_score = 1.0  # Exceeds by 50%
        elif prod_fp32 >= req_fp32:
            fp32_score = 0.9  # Meets requirements
        elif prod_fp32 >= req_fp32 * 0.8:
            fp32_score = 0.7  # Close to meeting requirements
        elif prod_fp32 >= req_fp32 * 0.6:
            fp32_score = 0.5  # Significantly below requirements
        else:
            fp32_score = 0.3  # Far below requirements
    
    # Check tensor cores
    if "tensorCores" in compute_specs and "minTensorCores" in required:
        req_cores = int(required["minTensorCores"])
        prod_cores = int(compute_specs["tensorCores"])
        
        if prod_cores >= req_cores:
            tensor_cores_score = 1.0
        else:
            # Score reduces by 0.1 for every 10% below requirement
            tensor_cores_score = max(0.5, 1.0 - (req_cores - prod_cores) / req_cores)
    
    # Check CUDA cores
    if "cudaCores" in compute_specs and "minCudaCores" in required:
        req_cuda = int(required["minCudaCores"])
        prod_cuda = int(compute_specs["cudaCores"])
        
        if prod_cuda >= req_cuda:
            cuda_cores_score = 1.0
        else:
            # Score reduces by 0.1 for every 10% below requirement
            cuda_cores_score = max(0.5, 1.0 - (req_cuda - prod_cuda) / req_cuda)
    
    # Check INT8 performance
    if "int8Performance" in compute_specs and "minInt8Performance" in required:
        req_int8 = float(required["minInt8Performance"])
        prod_int8 = float(compute_specs["int8Performance"])
        
        if prod_int8 >= req_int8:
            int8_score = 1.0
        else:
            # Score reduces by 0.1 for every 10% below requirement
            int8_score = max(0.5, 1.0 - (req_int8 - prod_int8) / req_int8)
    
    # Check FP16 performance
    if "fp16Performance" in compute_specs and "minFp16Performance" in required:
        req_fp16 = float(required["minFp16Performance"])
        prod_fp16 = float(compute_specs["fp16Performance"])
        
        if prod_fp16 >= req_fp16:
            fp16_score = 1.0
        else:
            # Score reduces by 0.1 for every 10% below requirement
            fp16_score = max(0.5, 1.0 - (req_fp16 - prod_fp16) / req_fp16)
    
    # Calculate overall performance score
    scores = []
    if fp32_score != 0.5:
        scores.append(("fp32", fp32_score, 0.4))  # FP32 is very important
    if tensor_cores_score != 0.5:
        scores.append(("tensor_cores", tensor_cores_score, 0.15))
    if cuda_cores_score != 0.5:
        scores.append(("cuda_cores", cuda_cores_score, 0.15))
    if int8_score != 0.5:
        scores.append(("int8", int8_score, 0.15))
    if fp16_score != 0.5:
        scores.append(("fp16", fp16_score, 0.15))
    
    if not scores:
        return 0.5
    
    # Weighted average of available scores
    total_weight = sum(weight for _, _, weight in scores)
    weighted_sum = sum(score * weight for _, score, weight in scores)
    
    return weighted_sum / total_weight

def compare_memory_specs(required: Dict[str, Any], product: Dict[str, Any]) -> float:
    """
    Compare memory specifications between requirements and product specs.
    
    Args:
        required: Required memory specifications
        product: Product memory specifications
        
    Returns:
        Score between 0 and 1 representing how well the product meets requirements
    """
    if not required or not product:
        return 0.5
    
    # Extract memory specs
    memory_specs = product.get("memorySpecs", {})
    if not memory_specs and "specifications" in product:
        # Try to extract from specifications
        memory_specs = product.get("specifications", {})
    
    if not memory_specs:
        return 0.5
    
    # Initialize scores for different metrics
    capacity_score = bandwidth_score = type_score = 0.5
    
    # Check memory capacity
    if "capacity" in memory_specs and "minMemory" in required:
        req_capacity = float(required["minMemory"])
        prod_capacity = float(memory_specs["capacity"])
        
        if prod_capacity >= req_capacity * 1.5:
            capacity_score = 1.0  # Exceeds by 50%
        elif prod_capacity >= req_capacity:
            capacity_score = 0.9  # Meets requirements
        elif prod_capacity >= req_capacity * 0.8:
            capacity_score = 0.7  # Close to meeting requirements
        elif prod_capacity >= req_capacity * 0.6:
            capacity_score = 0.5  # Significantly below requirements
        else:
            capacity_score = 0.3  # Far below requirements
    
    # Check memory bandwidth
    if "bandwidth" in memory_specs and "minMemoryBandwidth" in required:
        req_bandwidth = float(required["minMemoryBandwidth"])
        prod_bandwidth = float(memory_specs["bandwidth"])
        
        if prod_bandwidth >= req_bandwidth * 1.3:
            bandwidth_score = 1.0  # Exceeds by 30%
        elif prod_bandwidth >= req_bandwidth:
            bandwidth_score = 0.9  # Meets requirements
        elif prod_bandwidth >= req_bandwidth * 0.8:
            bandwidth_score = 0.7  # Close to meeting requirements
        else:
            bandwidth_score = 0.5  # Below requirements
    
    # Check memory type
    if "type" in memory_specs and "memoryType" in required:
        req_type = required["memoryType"].lower()
        prod_type = memory_specs["type"].lower()
        
        # HBM3 > HBM2e > HBM2 > GDDR6X > GDDR6 > GDDR5X > GDDR5
        memory_types_ranked = ["gddr5", "gddr5x", "gddr6", "gddr6x", "hbm2", "hbm2e", "hbm3"]
        
        if req_type == prod_type:
            type_score = 1.0  # Exact match
        else:
            try:
                req_index = memory_types_ranked.index(req_type)
                prod_index = memory_types_ranked.index(prod_type)
                
                if prod_index > req_index:
                    type_score = 1.0  # Better than required
                else:
                    # Score reduces by 0.15 for each step down
                    type_score = max(0.5, 1.0 - (req_index - prod_index) * 0.15)
            except ValueError:
                # Type not in our ranking, use default score
                type_score = 0.6
    
    # Calculate overall memory score
    scores = []
    if capacity_score != 0.5:
        scores.append(("capacity", capacity_score, 0.5))  # Capacity is very important
    if bandwidth_score != 0.5:
        scores.append(("bandwidth", bandwidth_score, 0.3))
    if type_score != 0.5:
        scores.append(("type", type_score, 0.2))
    
    if not scores:
        return 0.5
    
    # Weighted average of available scores
    total_weight = sum(weight for _, _, weight in scores)
    weighted_sum = sum(score * weight for _, score, weight in scores)
    
    return weighted_sum / total_weight

def compare_power_specs(required: Dict[str, Any], product: Dict[str, Any]) -> float:
    """
    Compare power specifications between requirements and product specs.
    
    Args:
        required: Required power specifications
        product: Product power specifications
        
    Returns:
        Score between 0 and 1 representing how well the product meets requirements
    """
    if not required or not product:
        return 0.5
    
    # Extract power specs
    power_specs = product.get("powerConsumption", {})
    if not power_specs and "specifications" in product:
        # Try to extract from specifications
        power_specs = product.get("specifications", {})
    
    if not power_specs:
        return 0.5
    
    # Check TDP against power constraints
    if "tdp" in power_specs and "powerConstraints" in required:
        max_tdp = float(required["powerConstraints"])
        product_tdp = float(power_specs["tdp"])
        
        if product_tdp <= max_tdp * 0.8:
            return 1.0  # Significantly under power constraint
        elif product_tdp <= max_tdp:
            return 0.9  # Under power constraint
        elif product_tdp <= max_tdp * 1.1:
            return 0.7  # Slightly over power constraint
        elif product_tdp <= max_tdp * 1.2:
            return 0.5  # Moderately over power constraint
        else:
            return 0.3  # Significantly over power constraint
    
    return 0.5  # Default score

def compare_framework_support(required: Dict[str, Any], product: Dict[str, Any]) -> float:
    """
    Compare framework support between requirements and product specs.
    
    Args:
        required: Required frameworks
        product: Product specifications
        
    Returns:
        Score between 0 and 1 representing how well the product meets requirements
    """
    if not required or not product:
        return 0.5
    
    # Extract supported frameworks
    frameworks = product.get("supportedFrameworks", [])
    if not frameworks and "specifications" in product:
        # Try to extract from specifications
        specs = product.get("specifications", {})
        if "supportedFrameworks" in specs:
            frameworks = specs["supportedFrameworks"]
    
    if not frameworks or "frameworks" not in required:
        return 0.5
    
    required_frameworks = required["frameworks"]
    if not required_frameworks:
        return 0.5
    
    # Count how many required frameworks are supported
    supported_count = 0
    for req_framework in required_frameworks:
        req_lower = req_framework.lower()
        for framework in frameworks:
            if req_lower in framework.lower():
                supported_count += 1
                break
    
    # Calculate score based on percentage of required frameworks supported
    if not required_frameworks:
        return 0.5
    
    support_ratio = supported_count / len(required_frameworks)
    
    if support_ratio == 1.0:
        return 1.0  # All required frameworks supported
    elif support_ratio >= 0.8:
        return 0.9  # Most required frameworks supported
    elif support_ratio >= 0.6:
        return 0.8  # Many required frameworks supported
    elif support_ratio >= 0.4:
        return 0.7  # Some required frameworks supported
    elif support_ratio > 0:
        return 0.6  # Few required frameworks supported
    else:
        return 0.4  # No required frameworks supported

def check_compliance_match(buyer_country: str, product: Dict[str, Any], supplier: Dict[str, Any]) -> Tuple[float, str]:
    """
    Check compliance match between buyer, product, and supplier.
    
    Args:
        buyer_country: Country of the buyer
        product: Product specifications
        supplier: Supplier specifications
        
    Returns:
        Tuple of (score between 0 and 1, compliance notes)
    """
    if not buyer_country or not product or not supplier:
        return 0.5, "Insufficient data for compliance check"
    
    # Extract compliance info
    compliance_info = product.get("complianceInfo", {})
    
    # Check country restrictions
    restricted_countries = compliance_info.get("restrictedCountries", [])
    if buyer_country in restricted_countries:
        return 0.0, f"Export to {buyer_country} is restricted for this product"
    
    # Check supplier country restrictions
    supplier_country = supplier.get("country", "Unknown")
    
    # Basic geopolitical checks
    if buyer_country == "Russia" and supplier_country == "United States":
        return 0.1, "US suppliers are heavily restricted for Russian buyers"
    elif buyer_country == "China" and supplier_country == "United States":
        return 0.3, "Some US AI hardware exports to China are restricted"
    elif buyer_country == "Iran" and (supplier_country == "United States" or supplier_country == "European Union"):
        return 0.0, f"Exports from {supplier_country} to Iran are prohibited"
    
    # Check memory size restrictions (many countries restrict high-memory GPUs)
    memory_specs = product.get("memorySpecs", {})
    if memory_specs and "capacity" in memory_specs:
        memory_capacity = float(memory_specs["capacity"])
        if memory_capacity >= 32:
            if buyer_country in ["China", "Russia", "Iran", "North Korea", "Syria"]:
                return 0.2, f"High-memory GPU (>{memory_capacity}GB) exports to {buyer_country} likely require special licensing"
    
    # If no specific restrictions, check general export compliance
    shipping_restrictions = check_product_shipping_restrictions(product, buyer_country)
    if not shipping_restrictions["can_ship"]:
        return 0.0, "; ".join(shipping_restrictions["restrictions"])
    elif shipping_restrictions["requires_license"]:
        return 0.4, f"Export license required for shipping to {buyer_country}"
    
    # If local supplier, high compliance score
    if supplier_country == buyer_country:
        return 1.0, "Local supplier, no export restrictions"
    
    # Default score for non-restricted international shipping
    return 0.8, "Standard international shipping rules apply"

def calculate_match_score(
    product: Dict[str, Any], 
    supplier: Dict[str, Any], 
    requirements: Dict[str, Any], 
    buyer_country: str
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate comprehensive match score between AI hardware product and RFQ requirements
    
    Args:
        product: Product specifications
        supplier: Supplier information
        requirements: Extracted requirements from RFQ
        buyer_country: Country of the buyer
        
    Returns:
        Tuple of (overall score, detailed score breakdown)
    """
    # Initialize score components
    performance_score = 0.5
    compatibility_score = 0.5
    price_score = 0.5
    availability_score = 0.5
    compliance_score = 0.5
    compliance_notes = ""
    
    # Extract AI hardware requirements
    ai_hw_reqs = requirements.get("aiHardware", {})
    gpu_reqs = requirements.get("gpuRequirements", {})
    
    # Combine requirements for easier access
    hw_requirements = {**ai_hw_reqs, **gpu_reqs}
    
    # Calculate performance score based on compute capabilities
    performance_score = compare_compute_performance(hw_requirements, product)
    
    # Calculate memory and framework compatibility scores
    memory_score = compare_memory_specs(hw_requirements, product)
    framework_score = compare_framework_support(hw_requirements, product)
    power_score = compare_power_specs(hw_requirements, product)
    
    # Combine into overall compatibility score
    compatibility_score = (memory_score * 0.4) + (framework_score * 0.3) + (power_score * 0.3)
    
    # Calculate price score
    # For sophisticated pricing, we'd compare against similar products
    # Here we use a simple heuristic based on price
    if "price" in product:
        price = float(product["price"])
        if price < 1000:
            price_score = 0.9  # Budget option
        elif price < 5000:
            price_score = 0.8  # Mid-range option
        elif price < 10000:
            price_score = 0.7  # High-end option
        elif price < 20000:
            price_score = 0.6  # Premium option
        else:
            price_score = 0.5  # Ultra-premium option
    
    # Calculate availability score
    if supplier.get("leadTime"):
        lead_time = int(supplier["leadTime"])
        if lead_time <= 7:
            availability_score = 1.0  # Immediate availability
        elif lead_time <= 14:
            availability_score = 0.9  # Fast availability
        elif lead_time <= 30:
            availability_score = 0.8  # Standard availability
        elif lead_time <= 60:
            availability_score = 0.6  # Long lead time
        else:
            availability_score = 0.4  # Very long lead time
    elif supplier.get("deliveryTime"):
        delivery_days = parse_delivery_time(supplier["deliveryTime"])
        if delivery_days <= 7:
            availability_score = 1.0
        elif delivery_days <= 14:
            availability_score = 0.9
        elif delivery_days <= 30:
            availability_score = 0.8
        elif delivery_days <= 60:
            availability_score = 0.6
        else:
            availability_score = 0.4
    else:
        # Default if no lead time information
        in_stock = product.get("inStock", True)
        availability_score = 0.8 if in_stock else 0.4
    
    # Calculate compliance score
    compliance_score, compliance_notes = check_compliance_match(buyer_country, product, supplier)
    
    # Calculate overall match score
    # Get criteria weights from requirements
    criteria = requirements.get("criteria", {})
    price_weight = criteria.get("price", {}).get("weight", 25) / 100
    performance_weight = criteria.get("performance", {}).get("weight", 40) / 100
    compatibility_weight = criteria.get("compatibility", {}).get("weight", 15) / 100
    availability_weight = criteria.get("availability", {}).get("weight", 10) / 100
    compliance_weight = criteria.get("compliance", {}).get("weight", 10) / 100
    
    # Ensure weights sum to 1
    total_weight = price_weight + performance_weight + compatibility_weight + availability_weight + compliance_weight
    if total_weight != 1:
        price_weight /= total_weight
        performance_weight /= total_weight
        compatibility_weight /= total_weight
        availability_weight /= total_weight
        compliance_weight /= total_weight
    
    # Calculate weighted overall score
    overall_score = (
        price_score * price_weight +
        performance_score * performance_weight +
        compatibility_score * compatibility_weight +
        availability_score * availability_weight +
        compliance_score * compliance_weight
    ) * 100  # Convert to 0-100 scale
    
    # Prepare detailed score breakdown
    score_details = {
        "price": price_score * 100,
        "performance": performance_score * 100,
        "compatibility": compatibility_score * 100,
        "availability": availability_score * 100,
        "compliance": compliance_score * 100,
        "compliance_notes": compliance_notes
    }
    
    return overall_score, score_details

async def get_quantity_for_category(requirements: Any, category: str) -> int:
    """
    Get quantity from requirements for a specific category
    
    Args:
        requirements: Extracted requirements
        category: Product category
        
    Returns:
        Quantity as integer
    """
    try:
        # Handle different ways to access the data based on type
        if isinstance(requirements, dict):
            # Dictionary access
            if category.lower() in ["gpu", "accelerator", "ai accelerator"]:
                if "aiHardware" in requirements and "quantity" in requirements["aiHardware"]:
                    return int(requirements["aiHardware"]["quantity"])
                elif "gpuRequirements" in requirements and "quantity" in requirements["gpuRequirements"]:
                    return int(requirements["gpuRequirements"]["quantity"])
                elif "GPUs" in requirements and "quantity" in requirements["GPUs"]:
                    return int(requirements["GPUs"]["quantity"])
        else:
            # Object attribute access
            if category.lower() in ["gpu", "accelerator", "ai accelerator"]:
                if hasattr(requirements, "aiHardware") and requirements.aiHardware and hasattr(requirements.aiHardware, "quantity"):
                    return int(requirements.aiHardware.quantity)
                elif hasattr(requirements, "gpuRequirements") and requirements.gpuRequirements and hasattr(requirements.gpuRequirements, "quantity"):
                    return int(requirements.gpuRequirements.quantity)
                elif hasattr(requirements, "GPUs") and requirements.GPUs and hasattr(requirements.GPUs, "quantity"):
                    return int(requirements.GPUs.quantity)
    except Exception as e:
        logger.error(f"Error determining quantity: {str(e)}")
    
    # If we can't determine quantity, default to 1
    return 1

async def calculate_price_score(product: Product, all_products: List[Product], criteria: Dict[str, Dict[str, int]]) -> float:
    """
    Calculate price score compared to other products in the same category
    
    Args:
        product: The product to score
        all_products: List of all products for comparison
        criteria: Award criteria weights
        
    Returns:
        Price score (0-100)
    """
    # Extract price weight from criteria (default to 25%)
    price_weight = criteria.get("price", {}).get("weight", 25)
    
    # Filter to same category products
    same_category = [p for p in all_products if p.category == product.category]
    if not same_category:
        return 75.0  # Default if no comparison available
    
    # Extract prices
    prices = [p.price for p in same_category if hasattr(p, "price")]
    if not prices:
        return 75.0  # Default if no prices available
    
    # Calculate price percentile
    prices.sort()
    try:
        index = prices.index(product.price)
        percentile = index / len(prices)
        
        # Convert to score (lower price = higher score)
        score = 100.0 - (percentile * 100.0)
        
        # Adjust based on price sensitivity (from criteria)
        if price_weight >= 40:
            # Price-sensitive RFQ, enhance score differences
            score = 100.0 - (percentile * 120.0)
        elif price_weight <= 15:
            # Price-insensitive RFQ, reduce score differences
            score = 100.0 - (percentile * 70.0)
        
        # Ensure score is between 40 and 100
        return max(40.0, min(100.0, score))
    except ValueError:
        return 75.0  # Default if price not found

async def find_alternative_products(
    product: Product,
    all_products: List[Product],
    supplier_matches: List[SupplierMatch]
) -> Dict[str, int]:
    """
    Find alternative products that may be of interest
    
    Args:
        product: The main product
        all_products: List of all available products
        supplier_matches: List of supplier matches already found
        
    Returns:
        Dictionary mapping alternative type to product ID
    """
    alternatives = {
        "similarPerformance": [],
        "lowerCost": [],
        "fasterDelivery": [],
        "betterCompliance": []
    }
    
    # Only consider products of same category but not the product itself
    candidates = [p for p in all_products if p.category == product.category and p.id != product.id]
    
    if not candidates:
        return alternatives
    
    # Extract product key metrics
    try:
        prod_price = product.price
        
        # Get compute performance
        compute_specs = getattr(product, "computeSpecs", {})
        if isinstance(compute_specs, str):
            compute_specs = json.loads(compute_specs)
        
        fp32_perf = compute_specs.get("fp32Performance", 0)
        memory_specs = getattr(product, "memorySpecs", {})
        if isinstance(memory_specs, str):
            memory_specs = json.loads(memory_specs)
        
        memory_capacity = memory_specs.get("capacity", 0)
        
        # Similar performance alternatives
        similar_perf = []
        for p in candidates:
            p_specs = getattr(p, "computeSpecs", {})
            if isinstance(p_specs, str):
                p_specs = json.loads(p_specs)
            
            p_fp32 = p_specs.get("fp32Performance", 0)
            
            # Similar performance = within 20% of main product
            if abs(p_fp32 - fp32_perf) / (fp32_perf or 1) <= 0.2:
                similar_perf.append((p.id, abs(p_fp32 - fp32_perf)))
        
        # Sort by closest performance
        similar_perf.sort(key=lambda x: x[1])
        alternatives["similarPerformance"] = [p_id for p_id, _ in similar_perf[:3]]
        
        # Lower cost alternatives
        lower_cost = []
        for p in candidates:
            p_price = p.price
            p_specs = getattr(p, "computeSpecs", {})
            if isinstance(p_specs, str):
                p_specs = json.loads(p_specs)
            
            p_fp32 = p_specs.get("fp32Performance", 0)
            
            # Lower cost but still decent performance (at least 70% of original)
            if p_price < prod_price * 0.9 and p_fp32 >= fp32_perf * 0.7:
                lower_cost.append((p.id, prod_price - p_price))
        
        # Sort by biggest price saving
        lower_cost.sort(key=lambda x: x[1], reverse=True)
        alternatives["lowerCost"] = [p_id for p_id, _ in lower_cost[:3]]
        
        # Faster delivery alternatives
        faster_delivery = []
        for sm in supplier_matches:
            if sm.product.id != product.id:
                try:
                    # Check if this match has better availability
                    current_score = next((m for m in supplier_matches if m.product.id == product.id), None)
                    if current_score and sm.matchDetails["availability"] > current_score.matchDetails["availability"]:
                        faster_delivery.append((sm.product.id, sm.matchDetails["availability"]))
                except Exception as e:
                    logger.error(f"Error comparing availability: {str(e)}")
        
        # Sort by availability score
        faster_delivery.sort(key=lambda x: x[1], reverse=True)
        alternatives["fasterDelivery"] = [p_id for p_id, _ in faster_delivery[:3]]
        
        # Better compliance alternatives
        better_compliance = []
        for sm in supplier_matches:
            if sm.product.id != product.id:
                try:
                    # Check if this match has better compliance
                    current_score = next((m for m in supplier_matches if m.product.id == product.id), None)
                    if current_score and sm.matchDetails["compliance"] > current_score.matchDetails["compliance"]:
                        better_compliance.append((sm.product.id, sm.matchDetails["compliance"]))
                except Exception as e:
                    logger.error(f"Error comparing compliance: {str(e)}")
        
        # Sort by compliance score
        better_compliance.sort(key=lambda x: x[1], reverse=True)
        alternatives["betterCompliance"] = [p_id for p_id, _ in better_compliance[:3]]
    
    except Exception as e:
        logger.error(f"Error finding alternative products: {str(e)}")
    
    return alternatives

async def match_suppliers_for_rfq(rfq_id: int) -> List[SupplierMatch]:
    """
    Match suppliers based on RFQ requirements with specialized AI hardware matching
    
    Args:
        rfq_id: ID of the RFQ to match
        
    Returns:
        List of supplier matches sorted by match score
    """
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
        
        # Get buyer information
        buyer_country = "United States"  # Default
        if rfq.userId:
            user = await db_storage.get_user(rfq.userId)
            if user and hasattr(user, "country") and user.country:
                buyer_country = user.country
        
        # Extract AI hardware specific categories from requirements
        # Handle both object access and dictionary access
        if hasattr(requirements, "categories"):
            categories = requirements.categories
        elif isinstance(requirements, dict) and "categories" in requirements:
            categories = requirements["categories"]
        else:
            # Default to GPU if no categories specified
            categories = ["GPU", "AI Accelerator"]
        
        # Ensure categories is a list
        if not isinstance(categories, list):
            categories = [categories] if categories else []
        
        # Filter categories to AI hardware specific ones
        ai_hw_categories = [c for c in categories if c.lower() in [
            "gpu", "ai accelerator", "ml accelerator", "tpu", "vpu", "fpga", "asic"
        ]]
        
        if not ai_hw_categories:
            logger.warning(f"No AI hardware categories found in RFQ {rfq_id}")
            ai_hw_categories = ["GPU"]  # Default to GPU
        
        match_results = []
        
        for category in ai_hw_categories:
            # Get all products in this category
            all_products = await db_storage.get_products_by_category(category)
            
            if not all_products:
                logger.warning(f"No products found for category {category}")
                continue
            
            logger.info(f"Found {len(all_products)} products for category {category}")
            
            # Process each product
            for product in all_products:
                try:
                    # Get supplier information
                    supplier = await db_storage.get_supplier_by_id(product.supplierId)
                    if not supplier:
                        logger.warning(f"Supplier not found for product {product.id}")
                        continue
                    
                    # Convert product to dict format
                    product_dict = {}
                    for key, value in vars(product).items():
                        if not key.startswith("_"):
                            product_dict[key] = value
                    
                    # Convert supplier to dict format
                    supplier_dict = {}
                    for key, value in vars(supplier).items():
                        if not key.startswith("_"):
                            supplier_dict[key] = value
                    
                    # Calculate match score
                    match_score, match_details = calculate_match_score(
                        product_dict, 
                        supplier_dict, 
                        requirements, 
                        buyer_country
                    )
                    
                    # Calculate total price based on quantity
                    try:
                        quantity = await get_quantity_for_category(requirements, category)
                        total_price = product.price * quantity
                    except Exception as e:
                        logger.error(f"Error calculating quantity: {str(e)}")
                        quantity = 1
                        total_price = product.price
                    
                    # Calculate estimated delivery date
                    delivery_days = 30  # Default
                    if hasattr(supplier, "leadTime") and supplier.leadTime:
                        delivery_days = int(supplier.leadTime)
                    elif hasattr(supplier, "deliveryTime") and supplier.deliveryTime:
                        delivery_days = int(parse_delivery_time(supplier.deliveryTime))
                    
                    estimated_delivery = datetime.now().strftime("%Y-%m-%d")
                    try:
                        from datetime import timedelta
                        estimated_delivery = (datetime.now() + timedelta(days=delivery_days)).strftime("%Y-%m-%d")
                    except Exception as e:
                        logger.error(f"Error calculating estimated delivery: {str(e)}")
                    
                    # Create a supplier match object
                    supplier_match = SupplierMatch(
                        supplier=supplier,
                        product=product,
                        matchScore=match_score,
                        matchDetails={
                            "price": match_details["price"],
                            "performance": match_details["performance"],
                            "compatibility": match_details["compatibility"],
                            "availability": match_details["availability"],
                            "compliance": match_details["compliance"]
                        },
                        totalPrice=total_price,
                        estimatedDelivery=estimated_delivery,
                        complianceNotes=match_details.get("compliance_notes", "")
                    )
                    
                    match_results.append(supplier_match)
                except Exception as e:
                    logger.error(f"Error processing product {product.id}: {str(e)}")
            
        # Sort results by match score (descending)
        match_results.sort(key=lambda x: x.matchScore, reverse=True)
        
        # Find alternatives for top matches
        try:
            if match_results:
                # Find alternatives only for top matches
                top_matches = match_results[:min(5, len(match_results))]
                for match in top_matches:
                    alternatives = await find_alternative_products(match.product, all_products, match_results)
                    if alternatives:
                        # Update match object with alternatives if found
                        match.alternatives = alternatives
        except Exception as e:
            logger.error(f"Error finding alternatives: {str(e)}")
        
        return match_results
    
    except Exception as e:
        logger.error(f"Error matching suppliers for RFQ {rfq_id}: {str(e)}")
        return []


if __name__ == "__main__":
    # For testing purposes
    import asyncio
    
    async def test_matching():
        # Create sample requirements
        sample_requirements = {
            "categories": ["GPU"],
            "aiHardware": {
                "type": "GPU",
                "quantity": 2,
                "minMemory": 24,
                "minComputePower": 20,
                "powerConstraints": 350,
                "frameworks": ["TensorFlow", "PyTorch"]
            },
            "criteria": {
                "price": {"weight": 30},
                "performance": {"weight": 40},
                "availability": {"weight": 15},
                "compliance": {"weight": 15}
            }
        }
        
        # Create sample product
        sample_product = {
            "name": "NVIDIA A100 40GB PCIe",
            "category": "GPU",
            "price": 10000,
            "computeSpecs": {
                "fp32Performance": 19.5,
                "tensorCores": 432
            },
            "memorySpecs": {
                "capacity": 40,
                "bandwidth": 1555
            },
            "supportedFrameworks": ["TensorFlow", "PyTorch", "CUDA"],
            "complianceInfo": {
                "restrictedCountries": ["Iran", "North Korea"]
            }
        }
        
        # Create sample supplier
        sample_supplier = {
            "name": "NVIDIA Direct",
            "country": "United States",
            "leadTime": 14
        }
        
        # Test calculate_match_score
        score, details = calculate_match_score(
            sample_product,
            sample_supplier,
            sample_requirements,
            "United Kingdom"
        )
        
        print(f"Match score: {score:.2f}")
        print("Score details:")
        for key, value in details.items():
            print(f"  {key}: {value:.2f}" if isinstance(value, float) else f"  {key}: {value}")
    
    asyncio.run(test_matching())