from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
import json

from ..models.storage import storage
from ..models.schemas import (
    SupplierMatch, RFQ, Product, Supplier, Proposal, 
    ExtractedRequirement, EmailTemplate, RFQUploadRequest
)
from ..services.ai_service import extract_requirements_from_rfq, generate_email_proposal

router = APIRouter()


@router.get("/rfqs", response_model=List[RFQ])
async def get_rfqs():
    """Get all RFQs"""
    return await storage.get_all_rfqs()


@router.get("/rfqs/{rfq_id}", response_model=RFQ)
async def get_rfq(rfq_id: int):
    """Get RFQ by ID"""
    rfq = await storage.get_rfq_by_id(rfq_id)
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    return rfq


@router.post("/rfqs/upload")
async def upload_rfq(file: UploadFile = File(...)):
    """Upload RFQ document and extract requirements"""
    try:
        content = await file.read()
        # Decode assuming UTF-8
        rfq_content = content.decode("utf-8")
        
        # Extract requirements using AI
        requirements = await extract_requirements_from_rfq(rfq_content)
        
        # Create new RFQ in storage
        rfq_data = {
            "title": requirements.title,
            "description": requirements.description or "",
            "originalContent": rfq_content,
            "extractedRequirements": requirements,
            "userId": 1  # Demo user
        }
        
        rfq = await storage.create_rfq(rfq_data)
        return {"id": rfq.id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing RFQ: {str(e)}")


@router.post("/rfqs")
async def create_rfq(rfq_request: RFQUploadRequest):
    """Create RFQ manually with specifications"""
    try:
        # Extract requirements using AI from the specifications text
        requirements = await extract_requirements_from_rfq(rfq_request.specifications)
        
        # Create new RFQ in storage
        rfq_data = {
            "title": rfq_request.title,
            "description": rfq_request.description or "",
            "originalContent": rfq_request.specifications,
            "extractedRequirements": requirements,
            "userId": 1  # Demo user
        }
        
        rfq = await storage.create_rfq(rfq_data)
        return {"id": rfq.id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating RFQ: {str(e)}")


@router.get("/suppliers", response_model=List[Supplier])
async def get_suppliers():
    """Get all suppliers"""
    return await storage.get_all_suppliers()


@router.get("/products", response_model=List[Product])
async def get_products(category: Optional[str] = None):
    """Get products, optionally filtered by category"""
    if category:
        return await storage.get_products_by_category(category)
    
    # Collect all products
    all_products = []
    for supplier_id in range(1, 4):  # We have suppliers with IDs 1-3
        products = await storage.get_products_by_supplier(supplier_id)
        all_products.extend(products)
    
    return all_products


@router.post("/rfqs/{rfq_id}/match-suppliers", response_model=Dict[str, Any])
async def match_suppliers(rfq_id: int):
    """Match suppliers based on RFQ requirements"""
    rfq = await storage.get_rfq_by_id(rfq_id)
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    
    try:
        requirements = rfq.extractedRequirements
        
        # Get all relevant products based on categories
        matches = []
        
        for category in requirements.categories:
            products = await storage.get_products_by_category(category)
            
            for product in products:
                supplier = await storage.get_supplier_by_id(product.supplierId)
                
                if not supplier:
                    continue
                
                # Calculate match score
                match_score, match_details = calculate_match_score(product, supplier, requirements, category)
                
                # Calculate total price
                quantity = 0
                if category.lower() == "laptops" and requirements.laptops:
                    quantity = requirements.laptops.quantity
                elif category.lower() == "monitors" and requirements.monitors:
                    quantity = requirements.monitors.quantity
                
                total_price = product.price * quantity
                
                # Create supplier match
                supplier_match = SupplierMatch(
                    supplier=supplier,
                    product=product,
                    matchScore=match_score,
                    matchDetails=match_details,
                    totalPrice=total_price
                )
                
                matches.append(supplier_match)
                
                # Create proposal record
                proposal_data = {
                    "rfqId": rfq_id,
                    "productId": product.id,
                    "score": match_score,
                    "priceScore": match_details.price,
                    "qualityScore": match_details.quality,
                    "deliveryScore": match_details.delivery
                }
                
                await storage.create_proposal(proposal_data)
        
        # Sort matches by score in descending order
        matches.sort(key=lambda x: x.matchScore, reverse=True)
        
        return {"rfqId": rfq_id, "matches": matches}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error matching suppliers: {str(e)}")


@router.post("/proposals/{proposal_id}/generate-email", response_model=EmailTemplate)
async def generate_proposal_email(proposal_id: int):
    """Generate email proposal for a specific supplier match"""
    proposal = await storage.get_proposal_by_id(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    rfq = await storage.get_rfq_by_id(proposal.rfqId)
    product = await storage.get_product_by_id(proposal.productId)
    supplier = await storage.get_supplier_by_id(product.supplierId)
    
    try:
        email_template = await generate_email_proposal(
            rfq.dict(),
            product.dict(),
            supplier.dict()
        )
        
        # Update proposal with email content
        proposal.emailContent = email_template.body
        
        return email_template
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating email: {str(e)}")


def calculate_match_score(product: Product, supplier: Supplier, requirements: ExtractedRequirement, category: str):
    """Calculate match score between product and RFQ requirements"""
    price_score = 0.0
    quality_score = 0.0
    delivery_score = 0.0
    
    if category.lower() == "laptops" and requirements.laptops:
        laptop_specs = product.specifications
        laptop_reqs = requirements.laptops
        
        # Price score (lower price = higher score, simplified for demo)
        price_ceiling = 1500  # Arbitrary ceiling for demo
        price_score = min(100, max(0, 100 - (product.price / price_ceiling) * 100))
        
        # Quality score based on specs matching
        quality_points = 0
        total_points = 0
        
        # OS match
        if laptop_reqs.os and "os" in laptop_specs:
            total_points += 10
            if laptop_reqs.os.lower() in laptop_specs["os"].lower():
                quality_points += 10
        
        # Processor match
        if laptop_reqs.processor and "processor" in laptop_specs:
            total_points += 15
            if any(term in laptop_specs["processor"].lower() for term in laptop_reqs.processor.lower().split()):
                quality_points += 15
        
        # Memory match
        if laptop_reqs.memory and "memory" in laptop_specs:
            total_points += 10
            if any(term in laptop_specs["memory"].lower() for term in laptop_reqs.memory.lower().split()):
                quality_points += 10
        
        # Storage match
        if laptop_reqs.storage and "storage" in laptop_specs:
            total_points += 10
            if any(term in laptop_specs["storage"].lower() for term in laptop_reqs.storage.lower().split()):
                quality_points += 10
        
        # Display match
        if laptop_reqs.display and "display" in laptop_specs:
            total_points += 10
            if any(term in laptop_specs["display"].lower() for term in laptop_reqs.display.lower().split()):
                quality_points += 10
        
        # Battery match
        if laptop_reqs.battery and "battery" in laptop_specs:
            total_points += 10
            if any(term in laptop_specs["battery"].lower() for term in laptop_reqs.battery.lower().split()):
                quality_points += 10
        
        # Durability match
        if laptop_reqs.durability and "durability" in laptop_specs:
            total_points += 10
            if any(term in laptop_specs["durability"].lower() for term in laptop_reqs.durability.lower().split()):
                quality_points += 10
        
        # Connectivity match
        if laptop_reqs.connectivity and "connectivity" in laptop_specs:
            total_points += 10
            if any(term in laptop_specs["connectivity"].lower() for term in laptop_reqs.connectivity.lower().split()):
                quality_points += 10
        
        # Warranty match
        if laptop_reqs.warranty and "warranty" in product.warranty:
            total_points += 15
            num_years_req = next((int(s) for s in laptop_reqs.warranty.split() if s.isdigit()), 0)
            num_years_prod = next((int(s) for s in product.warranty.split() if s.isdigit()), 0)
            
            if num_years_prod >= num_years_req:
                quality_points += 15
            elif num_years_prod > 0:
                quality_points += 5  # Partial match
        
        # Calculate quality score as percentage
        quality_score = (quality_points / total_points * 100) if total_points > 0 else 50
    
    elif category.lower() == "monitors" and requirements.monitors:
        monitor_specs = product.specifications
        monitor_reqs = requirements.monitors
        
        # Price score (lower price = higher score, simplified for demo)
        price_ceiling = 500  # Arbitrary ceiling for demo
        price_score = min(100, max(0, 100 - (product.price / price_ceiling) * 100))
        
        # Quality score based on specs matching
        quality_points = 0
        total_points = 0
        
        # Screen size match
        if monitor_reqs.screenSize and "screenSize" in monitor_specs:
            total_points += 15
            if any(term in monitor_specs["screenSize"].lower() for term in monitor_reqs.screenSize.lower().split()):
                quality_points += 15
        
        # Resolution match
        if monitor_reqs.resolution and "resolution" in monitor_specs:
            total_points += 15
            if any(term in monitor_specs["resolution"].lower() for term in monitor_reqs.resolution.lower().split()):
                quality_points += 15
        
        # Panel technology match
        if monitor_reqs.panelTech and "panelTech" in monitor_specs:
            total_points += 10
            if any(term in monitor_specs["panelTech"].lower() for term in monitor_reqs.panelTech.lower().split()):
                quality_points += 10
        
        # Brightness match
        if monitor_reqs.brightness and "brightness" in monitor_specs:
            total_points += 10
            if any(term in monitor_specs["brightness"].lower() for term in monitor_reqs.brightness.lower().split()):
                quality_points += 10
        
        # Contrast ratio match
        if monitor_reqs.contrastRatio and "contrastRatio" in monitor_specs:
            total_points += 10
            if any(term in monitor_specs["contrastRatio"].lower() for term in monitor_reqs.contrastRatio.lower().split()):
                quality_points += 10
        
        # Connectivity match
        if monitor_reqs.connectivity and "connectivity" in monitor_specs:
            total_points += 10
            if any(term in monitor_specs["connectivity"].lower() for term in monitor_reqs.connectivity.lower().split()):
                quality_points += 10
        
        # Adjustability match
        if monitor_reqs.adjustability and "adjustability" in monitor_specs:
            total_points += 15
            if any(term in monitor_specs["adjustability"].lower() for term in monitor_reqs.adjustability.lower().split()):
                quality_points += 15
        
        # Warranty match
        if monitor_reqs.warranty and product.warranty:
            total_points += 15
            num_years_req = next((int(s) for s in monitor_reqs.warranty.split() if s.isdigit()), 0)
            num_years_prod = next((int(s) for s in product.warranty.split() if s.isdigit()), 0)
            
            if num_years_prod >= num_years_req:
                quality_points += 15
            elif num_years_prod > 0:
                quality_points += 5  # Partial match
        
        # Calculate quality score as percentage
        quality_score = (quality_points / total_points * 100) if total_points > 0 else 50
    
    else:
        # Default scores if category doesn't match requirements
        price_score = 50
        quality_score = 50
    
    # Delivery score (lower delivery time = higher score)
    # Extract number of days from delivery time (e.g., "15-30 days" -> 22.5)
    delivery_days = 0
    if "-" in supplier.deliveryTime:
        parts = supplier.deliveryTime.split("-")
        if len(parts) >= 2:
            try:
                min_days = float(parts[0].strip())
                max_days = float(parts[1].split()[0].strip())
                delivery_days = (min_days + max_days) / 2
            except (ValueError, IndexError):
                delivery_days = 30  # Default if parsing fails
    
    # Scale delivery score (assuming 15 days is excellent and 60+ days is poor)
    if delivery_days <= 15:
        delivery_score = 100
    elif delivery_days >= 60:
        delivery_score = 0
    else:
        delivery_score = 100 - ((delivery_days - 15) / 45 * 100)
    
    # Apply weights from RFQ criteria
    price_weight = requirements.criteria.price.get("weight", 50) / 100
    quality_weight = requirements.criteria.quality.get("weight", 30) / 100
    delivery_weight = requirements.criteria.delivery.get("weight", 20) / 100
    
    # Calculate weighted score
    weighted_score = (
        price_score * price_weight +
        quality_score * quality_weight +
        delivery_score * delivery_weight
    )
    
    # Create match details
    from ..models.schemas import MatchDetails
    match_details = MatchDetails(
        price=price_score,
        quality=quality_score,
        delivery=delivery_score
    )
    
    return weighted_score, match_details