"""
Supplier matching service for RFQ processing platform.

This module provides functions to match suppliers with RFQ requirements
based on various criteria including price, quality, and delivery time.
"""

from typing import List, Dict, Any, Optional, Tuple
import re
from datetime import datetime

from ..models.schemas import ExtractedRequirement, Supplier, Product, SupplierMatch, MatchDetails
from ..models.db_storage import storage

def parse_delivery_time(delivery_time: str) -> float:
    """Parse delivery time string to get average days"""
    pattern = r'(\d+)-(\d+)'
    match = re.search(pattern, delivery_time)
    if match:
        min_days = int(match.group(1))
        max_days = int(match.group(2))
        return (min_days + max_days) / 2
    return 30  # Default to 30 days if no pattern is found

def compare_processors(requirement: str, spec: str) -> float:
    """Compare processor specifications and return a score between 0 and 1"""
    # Extract processor family and generation if possible
    requirement = requirement.lower()
    spec = spec.lower()
    
    # Check for exact match
    if requirement == spec:
        return 1.0
    
    # Check for processor family match (i.e., Intel Core i7, AMD Ryzen 7)
    req_family = re.search(r'(i\d|ryzen \d)', requirement)
    spec_family = re.search(r'(i\d|ryzen \d)', spec)
    
    if req_family and spec_family and req_family.group() == spec_family.group():
        return 0.8
    
    # More general match
    if 'i7' in requirement and 'i7' in spec:
        return 0.7
    if 'i5' in requirement and 'i5' in spec:
        return 0.7
    if 'i3' in requirement and 'i3' in spec:
        return 0.7
    if 'ryzen 7' in requirement and 'ryzen 7' in spec:
        return 0.7
    if 'ryzen 5' in requirement and 'ryzen 5' in spec:
        return 0.7
    
    # Check for generation
    req_gen = re.search(r'(\d{4,5}[a-zA-Z]*)', requirement)
    spec_gen = re.search(r'(\d{4,5}[a-zA-Z]*)', spec)
    
    if req_gen and spec_gen:
        req_gen_num = req_gen.group()
        spec_gen_num = spec_gen.group()
        if req_gen_num == spec_gen_num:
            return 0.6
    
    # Basic processor type match
    processor_types = ['intel', 'amd', 'core', 'ryzen', 'snapdragon']
    for p_type in processor_types:
        if p_type in requirement and p_type in spec:
            return 0.5
    
    return 0.3  # Low match

def compare_memory(requirement: str, spec: str) -> float:
    """Compare memory specifications and return a score between 0 and 1"""
    # Extract memory capacity
    req_gb = re.search(r'(\d+)\s*gb', requirement.lower())
    spec_gb = re.search(r'(\d+)\s*gb', spec.lower())
    
    if req_gb and spec_gb:
        req_amount = int(req_gb.group(1))
        spec_amount = int(spec_gb.group(1))
        
        # Exact match
        if req_amount == spec_amount:
            return 1.0
        
        # Product has more memory than required
        if spec_amount > req_amount:
            # Calculate a score based on how much more memory the product has
            # Max score for 2x required memory, diminishing returns beyond that
            ratio = min(spec_amount / req_amount, 2.0)
            return 0.7 + (0.3 * (ratio - 1))
        
        # Product has less memory than required
        # Score drops quickly if memory is less than required
        ratio = spec_amount / req_amount
        return max(0.2, ratio * 0.7)
    
    # If we can't parse the memory amounts, check for type match (DDR4, DDR5)
    ddr_type_req = re.search(r'(ddr\d)', requirement.lower())
    ddr_type_spec = re.search(r'(ddr\d)', spec.lower())
    
    if ddr_type_req and ddr_type_spec and ddr_type_req.group() == ddr_type_spec.group():
        return 0.5
    
    return 0.3  # Low match

def compare_storage(requirement: str, spec: str) -> float:
    """Compare storage specifications and return a score between 0 and 1"""
    # Extract storage capacity
    req_capacity = re.search(r'(\d+)\s*(gb|tb)', requirement.lower())
    spec_capacity = re.search(r'(\d+)\s*(gb|tb)', spec.lower())
    
    if req_capacity and spec_capacity:
        req_amount = int(req_capacity.group(1))
        req_unit = req_capacity.group(2)
        
        spec_amount = int(spec_capacity.group(1))
        spec_unit = spec_capacity.group(2)
        
        # Convert to GB for comparison
        if req_unit == 'tb':
            req_amount *= 1024
        if spec_unit == 'tb':
            spec_amount *= 1024
        
        # Exact match
        if req_amount == spec_amount:
            return 1.0
        
        # Product has more storage than required
        if spec_amount > req_amount:
            # Calculate a score based on how much more storage the product has
            # Max score for 2x required storage, diminishing returns beyond that
            ratio = min(spec_amount / req_amount, 2.0)
            return 0.7 + (0.3 * (ratio - 1))
        
        # Product has less storage than required
        # Score drops quickly if storage is less than required
        ratio = spec_amount / req_amount
        return max(0.2, ratio * 0.7)
    
    # Check for storage type match (SSD, HDD, NVMe)
    storage_types = ['ssd', 'hdd', 'nvme', 'pcie']
    for s_type in storage_types:
        if s_type in requirement.lower() and s_type in spec.lower():
            return 0.5
    
    return 0.3  # Low match

def compare_display(requirement: str, spec: str) -> float:
    """Compare display specifications and return a score between 0 and 1"""
    # Check for resolution match
    resolutions = ['hd', 'fhd', '1080p', '4k', 'uhd', 'qhd', '1440p', '2160p']
    for res in resolutions:
        if res in requirement.lower() and res in spec.lower():
            return 0.8
    
    # Check for exact resolution spec
    res_patterns = [r'(\d+)\s*x\s*(\d+)', r'(\d+)p']
    for pattern in res_patterns:
        req_match = re.search(pattern, requirement.lower())
        spec_match = re.search(pattern, spec.lower())
        if req_match and spec_match and req_match.group() == spec_match.group():
            return 1.0
    
    # Check for panel technology match
    panel_techs = ['ips', 'tn', 'va', 'oled', 'amoled', 'retina']
    for tech in panel_techs:
        if tech in requirement.lower() and tech in spec.lower():
            return 0.7
    
    # Check for brightness
    req_nits = re.search(r'(\d+)\s*nits', requirement.lower())
    spec_nits = re.search(r'(\d+)\s*nits', spec.lower())
    
    if req_nits and spec_nits:
        req_brightness = int(req_nits.group(1))
        spec_brightness = int(spec_nits.group(1))
        
        if spec_brightness >= req_brightness:
            return 0.9
        else:
            # Score based on how close to required brightness
            ratio = spec_brightness / req_brightness
            return max(0.3, ratio * 0.9)
    
    # Screen size match
    req_size = re.search(r'(\d+\.?\d*)\s*inches?', requirement.lower())
    spec_size = re.search(r'(\d+\.?\d*)\s*inches?', spec.lower())
    
    if req_size and spec_size:
        req_inches = float(req_size.group(1))
        spec_inches = float(spec_size.group(1))
        
        # Within 1 inch difference
        if abs(req_inches - spec_inches) <= 1:
            return 0.8
        # Within 2 inches difference
        elif abs(req_inches - spec_inches) <= 2:
            return 0.6
    
    return 0.4  # Moderate match if some display specs mentioned

def compare_warranty(requirement: str, spec: str) -> float:
    """Compare warranty specifications and return a score between 0 and 1"""
    # Extract warranty duration
    req_years = re.search(r'(\d+)\s*years?', requirement.lower())
    spec_years = re.search(r'(\d+)\s*years?', spec.lower())
    
    if req_years and spec_years:
        req_duration = int(req_years.group(1))
        spec_duration = int(spec_years.group(1))
        
        if spec_duration >= req_duration:
            # Extra warranty years provide diminishing returns
            extra_years = min(spec_duration - req_duration, 3)  # Cap at 3 years extra
            return 0.7 + (extra_years * 0.1)
        else:
            # Score drops if warranty is shorter than required
            ratio = spec_duration / req_duration
            return max(0.2, ratio * 0.7)
    
    # Check for warranty type match
    warranty_types = ['onsite', 'next business day', 'pro support', 'premium', 'care pack', 'exchange']
    for w_type in warranty_types:
        if w_type in requirement.lower() and w_type in spec.lower():
            return 0.8
    
    # If warranty is mentioned but can't parse duration
    if 'warranty' in requirement.lower() and 'warranty' in spec.lower():
        return 0.5
    
    return 0.3  # Low match

def calculate_match_score(product: Product, supplier: Supplier, requirements: ExtractedRequirement, category: str) -> Tuple[float, Dict[str, float]]:
    """Calculate match score between product and RFQ requirements"""
    total_score = 0.0
    max_possible_score = 0.0
    match_details = {}
    
    # Get category-specific requirements
    if category.lower() == "laptops" and requirements.laptops:
        category_req = requirements.laptops
        specs = product.specifications
        
        # Processor match
        if "processor" in specs and hasattr(category_req, "processor"):
            processor_score = compare_processors(category_req.processor, specs["processor"])
            total_score += processor_score * 15
            max_possible_score += 15
        
        # Memory match
        if "memory" in specs and hasattr(category_req, "memory"):
            memory_score = compare_memory(category_req.memory, specs["memory"])
            total_score += memory_score * 15
            max_possible_score += 15
        
        # Storage match
        if "storage" in specs and hasattr(category_req, "storage"):
            storage_score = compare_storage(category_req.storage, specs["storage"])
            total_score += storage_score * 15
            max_possible_score += 15
        
        # Display match
        if "display" in specs and hasattr(category_req, "display"):
            display_score = compare_display(category_req.display, specs["display"])
            total_score += display_score * 10
            max_possible_score += 10
        
        # OS match
        if "os" in specs and hasattr(category_req, "os"):
            os_score = 1.0 if category_req.os.lower() in specs["os"].lower() else 0.3
            total_score += os_score * 10
            max_possible_score += 10
        
        # Battery match
        if "battery" in specs and hasattr(category_req, "battery"):
            req_hours = re.search(r'(\d+)\s*hours?', category_req.battery)
            spec_hours = re.search(r'(\d+)\s*hours?', specs["battery"])
            
            if req_hours and spec_hours:
                req_time = int(req_hours.group(1))
                spec_time = int(spec_hours.group(1))
                
                if spec_time >= req_time:
                    # Extra battery life provides diminishing returns
                    battery_score = 0.7 + min((spec_time - req_time) / 10, 0.3)
                else:
                    # Score drops if battery life is shorter
                    battery_score = max(0.2, (spec_time / req_time) * 0.7)
                
                total_score += battery_score * 10
                max_possible_score += 10
        
        # Warranty match
        if "warranty" in product.warranty and hasattr(category_req, "warranty"):
            warranty_score = compare_warranty(category_req.warranty, product.warranty)
            total_score += warranty_score * 10
            max_possible_score += 10
            
    elif category.lower() == "monitors" and requirements.monitors:
        category_req = requirements.monitors
        specs = product.specifications
        
        # Screen size match
        if "screenSize" in specs and hasattr(category_req, "screenSize"):
            req_size = re.search(r'(\d+\.?\d*)\s*inches?', category_req.screenSize)
            spec_size = re.search(r'(\d+\.?\d*)\s*inches?', specs["screenSize"])
            
            if req_size and spec_size:
                req_inches = float(req_size.group(1))
                spec_inches = float(spec_size.group(1))
                
                # Calculate score based on how close the sizes are
                size_diff = abs(req_inches - spec_inches)
                size_score = max(0.0, 1.0 - (size_diff / req_inches))
                
                total_score += size_score * 20
                max_possible_score += 20
        
        # Resolution match
        if "resolution" in specs and hasattr(category_req, "resolution"):
            # Check for exact match
            resolution_score = 1.0 if category_req.resolution.lower() in specs["resolution"].lower() else 0.0
            
            # If no exact match, check for resolution level
            if resolution_score == 0.0:
                res_levels = {
                    "hd": 1,
                    "fhd": 2,
                    "qhd": 3,
                    "uhd": 4,
                    "4k": 4
                }
                
                req_level = 0
                spec_level = 0
                
                for level_name, level_value in res_levels.items():
                    if level_name in category_req.resolution.lower():
                        req_level = level_value
                    if level_name in specs["resolution"].lower():
                        spec_level = level_value
                
                if req_level > 0 and spec_level > 0:
                    if spec_level >= req_level:
                        resolution_score = 0.7 + min((spec_level - req_level) * 0.1, 0.3)
                    else:
                        resolution_score = max(0.2, (spec_level / req_level) * 0.7)
            
            total_score += resolution_score * 20
            max_possible_score += 20
        
        # Panel technology match
        if "panelTech" in specs and hasattr(category_req, "panelTech"):
            panel_score = 1.0 if category_req.panelTech.lower() in specs["panelTech"].lower() else 0.3
            total_score += panel_score * 15
            max_possible_score += 15
        
        # Brightness match
        if "brightness" in specs and hasattr(category_req, "brightness"):
            req_nits = re.search(r'(\d+)', category_req.brightness)
            spec_nits = re.search(r'(\d+)', specs["brightness"])
            
            if req_nits and spec_nits:
                req_value = int(req_nits.group(1))
                spec_value = int(spec_nits.group(1))
                
                if spec_value >= req_value:
                    brightness_score = 0.7 + min((spec_value - req_value) / (req_value * 2), 0.3)
                else:
                    brightness_score = max(0.2, (spec_value / req_value) * 0.7)
                
                total_score += brightness_score * 10
                max_possible_score += 10
        
        # Connectivity match
        if "connectivity" in specs and hasattr(category_req, "connectivity"):
            connectivity_types = ["hdmi", "displayport", "vga", "usb-c", "thunderbolt"]
            req_types = [t for t in connectivity_types if t in category_req.connectivity.lower()]
            spec_types = [t for t in connectivity_types if t in specs["connectivity"].lower()]
            
            common_types = set(req_types).intersection(set(spec_types))
            if req_types:
                connectivity_score = len(common_types) / len(req_types)
            else:
                connectivity_score = 0.5  # Default if no specific types mentioned
            
            total_score += connectivity_score * 10
            max_possible_score += 10
            
        # Adjustability match
        if "adjustability" in specs and hasattr(category_req, "adjustability"):
            adjustability_features = ["height", "tilt", "swivel", "pivot"]
            req_features = [f for f in adjustability_features if f in category_req.adjustability.lower()]
            spec_features = [f for f in adjustability_features if f in specs["adjustability"].lower()]
            
            common_features = set(req_features).intersection(set(spec_features))
            if req_features:
                adjustability_score = len(common_features) / len(req_features)
            else:
                adjustability_score = 0.5  # Default if no specific features mentioned
            
            total_score += adjustability_score * 10
            max_possible_score += 10
            
        # Warranty match
        if hasattr(category_req, "warranty"):
            warranty_score = compare_warranty(category_req.warranty, product.warranty)
            total_score += warranty_score * 10
            max_possible_score += 10
    
    # Calculate price score (lower price = higher score)
    # For calculating price score, we need to know other products in same category
    # This will be handled separately
    
    # Calculate delivery score
    avg_delivery_days = parse_delivery_time(supplier.deliveryTime)
    # Arbitrary formula: score decreases as delivery days increase
    delivery_score = max(0.1, 1.0 - (avg_delivery_days / 60))  # Max 60 days
    total_score += delivery_score * 5
    max_possible_score += 5
    
    # Calculate final percentage score
    normalized_score = (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0
    
    # Prepare match details - we'll calculate price score separately
    match_details = {
        "quality": normalized_score,  # Using overall match as quality score for now
        "delivery": delivery_score * 100  # Convert to percentage
    }
    
    return (normalized_score, match_details)

async def get_quantity_for_category(requirements: ExtractedRequirement, category: str) -> int:
    """Get quantity from requirements for a specific category"""
    if category.lower() == "laptops" and requirements.laptops:
        return requirements.laptops.quantity
    elif category.lower() == "monitors" and requirements.monitors:
        return requirements.monitors.quantity
    return 1  # Default to 1 if not specified

async def calculate_price_score(product: Product, all_products: List[Product], criteria: Dict[str, Dict[str, int]]) -> float:
    """Calculate price score compared to other products in the same category"""
    category_products = [p for p in all_products if p.category.lower() == product.category.lower()]
    
    if not category_products:
        return 0.0
    
    # Get min and max prices in category
    prices = [p.price for p in category_products]
    min_price = min(prices)
    max_price = max(prices)
    
    # If all products have the same price
    if min_price == max_price:
        return 100.0
    
    # Calculate score: 100 for lowest price, 0 for highest price
    price_range = max_price - min_price
    relative_position = (max_price - product.price) / price_range
    
    return relative_position * 100

async def match_suppliers_for_rfq(rfq_id: int) -> List[SupplierMatch]:
    """Match suppliers based on RFQ requirements"""
    # Get the RFQ
    rfq = await storage.get_rfq_by_id(rfq_id)
    if not rfq:
        return []
    
    # Get all suppliers and products
    suppliers = await storage.get_all_suppliers()
    all_products = []
    
    # Collect all products for all suppliers
    for supplier in suppliers:
        products = await storage.get_products_by_supplier(supplier.id)
        all_products.extend(products)
    
    # Get categories from RFQ
    categories = rfq.extractedRequirements.categories
    
    # Store matches for all categories
    all_matches = []
    
    # Process each category
    for category in categories:
        # Get products for this category
        category_products = [p for p in all_products if p.category.lower() == category.lower()]
        
        # Process each product
        for product in category_products:
            # Find the supplier for this product
            supplier = next((s for s in suppliers if s.id == product.supplierId), None)
            if not supplier:
                continue
            
            # Calculate match score
            raw_score, match_details = calculate_match_score(product, supplier, rfq.extractedRequirements, category)
            
            # Calculate price score
            price_score = await calculate_price_score(product, all_products, rfq.extractedRequirements.criteria.dict())
            match_details["price"] = price_score
            
            # Calculate quantity for category
            quantity = await get_quantity_for_category(rfq.extractedRequirements, category)
            
            # Calculate total price
            total_price = product.price * quantity
            
            # Calculate final weighted score based on criteria
            criteria = rfq.extractedRequirements.criteria.dict()
            final_score = (
                (price_score * criteria["price"]["weight"] / 100) +
                (match_details["quality"] * criteria["quality"]["weight"] / 100) +
                (match_details["delivery"] * criteria["delivery"]["weight"] / 100)
            )
            
            # Create supplier match object
            match = SupplierMatch(
                supplier=supplier,
                product=product,
                matchScore=final_score,
                matchDetails=MatchDetails(
                    price=price_score,
                    quality=match_details["quality"],
                    delivery=match_details["delivery"]
                ),
                totalPrice=total_price
            )
            
            all_matches.append(match)
    
    # Sort matches by score (highest first)
    sorted_matches = sorted(all_matches, key=lambda m: m.matchScore, reverse=True)
    
    return sorted_matches