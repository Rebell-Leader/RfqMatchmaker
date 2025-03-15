from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List, Optional, Dict, Any
import os
import json

from models.schemas import (
    User, RFQ, Supplier, Product, Proposal, EmailTemplate,
    RFQUploadRequest, MatchSuppliersRequest, GenerateEmailRequest,
    RFQResponse, SupplierMatchResponse, ExtractedRequirement
)
from models.storage import MemStorage
from services.ai_service import extract_requirements_from_rfq, generate_email_proposal

# Initialize router
router = APIRouter()

# Initialize storage
storage = MemStorage()
storage.initialize_sample_data()

# RFQ routes
@router.get("/rfqs", response_model=List[RFQResponse])
async def get_rfqs():
    """Get all RFQs"""
    return await storage.get_all_rfqs()

@router.get("/rfqs/{rfq_id}", response_model=RFQResponse)
async def get_rfq(rfq_id: int):
    """Get RFQ by ID"""
    rfq = await storage.get_rfq_by_id(rfq_id)
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    return rfq

@router.post("/rfqs/upload", response_model=Dict[str, Any])
async def upload_rfq(file: UploadFile = File(...)):
    """Upload RFQ document and extract requirements"""
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    
    # Save uploaded file
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Read file content
    with open(file_path, "r") as f:
        content = f.read()
    
    # Extract requirements using AI service
    requirements = await extract_requirements_from_rfq(content)
    
    # Create RFQ in storage
    rfq_data = {
        "title": requirements.title,
        "description": requirements.description if requirements.description else "",
        "originalContent": content,
        "extractedRequirements": requirements.dict(),
        "userId": 1  # Default user ID for MVP
    }
    
    rfq = await storage.create_rfq(rfq_data)
    
    return {"id": rfq.id, "message": "RFQ processed successfully"}

@router.post("/rfqs", response_model=Dict[str, Any])
async def create_rfq(rfq_request: RFQUploadRequest):
    """Create RFQ manually with specifications"""
    # Extract requirements using AI service
    requirements = await extract_requirements_from_rfq(rfq_request.specifications)
    
    # Create RFQ in storage
    rfq_data = {
        "title": rfq_request.title,
        "description": rfq_request.description if rfq_request.description else "",
        "originalContent": rfq_request.specifications,
        "extractedRequirements": requirements.dict(),
        "userId": 1  # Default user ID for MVP
    }
    
    rfq = await storage.create_rfq(rfq_data)
    
    return {"id": rfq.id, "message": "RFQ created successfully"}

# Supplier routes
@router.get("/suppliers", response_model=List[Supplier])
async def get_suppliers():
    """Get all suppliers"""
    return await storage.get_all_suppliers()

# Product routes
@router.get("/products", response_model=List[Product])
async def get_products(category: Optional[str] = None):
    """Get products, optionally filtered by category"""
    if category:
        return await storage.get_products_by_category(category)
    else:
        # Get all products from all suppliers
        suppliers = await storage.get_all_suppliers()
        products = []
        for supplier in suppliers:
            supplier_products = await storage.get_products_by_supplier(supplier.id)
            products.extend(supplier_products)
        return products

# Matching routes
@router.post("/rfqs/{rfq_id}/match-suppliers", response_model=SupplierMatchResponse)
async def match_suppliers(rfq_id: int):
    """Match suppliers based on RFQ requirements"""
    rfq = await storage.get_rfq_by_id(rfq_id)
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    
    # Get requirements
    requirements = rfq.extractedRequirements
    
    # Get all products
    suppliers = await storage.get_all_suppliers()
    all_products = []
    for supplier in suppliers:
        supplier_products = await storage.get_products_by_supplier(supplier.id)
        all_products.extend([(product, supplier) for product in supplier_products])
    
    # Match products to requirements
    matches = []
    
    for product, supplier in all_products:
        for category in requirements.categories:
            if product.category.lower() == category.lower():
                # Calculate match score
                match_score, match_details = calculate_match_score(product, supplier, requirements, category)
                
                # Calculate total price based on quantity
                quantity = 0
                if category.lower() == "laptops" and requirements.laptops:
                    quantity = requirements.laptops.quantity
                elif category.lower() == "monitors" and requirements.monitors:
                    quantity = requirements.monitors.quantity
                
                total_price = product.price * quantity
                
                matches.append({
                    "supplier": supplier,
                    "product": product,
                    "matchScore": match_score,
                    "matchDetails": match_details,
                    "totalPrice": total_price
                })
                
                # Store proposal in database
                proposal_data = {
                    "rfqId": rfq_id,
                    "productId": product.id,
                    "score": match_score,
                    "priceScore": match_details["price"],
                    "qualityScore": match_details["quality"],
                    "deliveryScore": match_details["delivery"]
                }
                
                await storage.create_proposal(proposal_data)
    
    return {"rfqId": rfq_id, "matches": matches}

# Proposal routes
@router.get("/rfqs/{rfq_id}/proposals", response_model=List[Proposal])
async def get_proposals_by_rfq(rfq_id: int):
    """Get all proposals for an RFQ"""
    return await storage.get_proposals_by_rfq(rfq_id)

@router.post("/proposals/{proposal_id}/generate-email", response_model=EmailTemplate)
async def generate_proposal_email(proposal_id: int):
    """Generate email proposal for a specific supplier match"""
    proposal = await storage.get_proposal_by_id(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    rfq = await storage.get_rfq_by_id(proposal.rfqId)
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    
    product = await storage.get_product_by_id(proposal.productId)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    supplier = await storage.get_supplier_by_id(product.supplierId)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    # Generate email using AI service
    email_template = await generate_email_proposal(rfq.dict(), product.dict(), supplier.dict())
    
    # Update proposal with email content
    proposal.emailContent = email_template.body
    
    return email_template

def calculate_match_score(product: Product, supplier: Supplier, requirements: ExtractedRequirement, category: str):
    """Calculate match score between product and RFQ requirements"""
    # Get criteria weights
    price_weight = requirements.criteria.price["weight"] / 100
    quality_weight = requirements.criteria.quality["weight"] / 100
    delivery_weight = requirements.criteria.delivery["weight"] / 100
    
    # Initialize scores
    price_score = 0
    quality_score = 0
    delivery_score = 0
    
    # Calculate price score (lower price is better)
    # This is a simple calculation - in a real app, it would be more sophisticated
    price_score = min(100, 100 * (1 - (product.price / 2000)))  # Assuming $2000 is max price
    
    # Calculate quality score based on specs match
    if category.lower() == "laptops" and requirements.laptops:
        laptop_reqs = requirements.laptops
        specs = product.specifications
        
        # Count matching specs
        matches = 0
        total_specs = 8  # Total number of specs to check
        
        if specs.get("os", "").lower() in laptop_reqs.os.lower():
            matches += 1
        if specs.get("processor", "").lower() in laptop_reqs.processor.lower():
            matches += 1
        if specs.get("memory", "").lower() in laptop_reqs.memory.lower():
            matches += 1
        if specs.get("storage", "").lower() in laptop_reqs.storage.lower():
            matches += 1
        if specs.get("display", "").lower() in laptop_reqs.display.lower():
            matches += 1
        if specs.get("battery", "").lower() in laptop_reqs.battery.lower():
            matches += 1
        if specs.get("connectivity", "").lower() in laptop_reqs.connectivity.lower():
            matches += 1
        if specs.get("warranty", "").lower() in laptop_reqs.warranty.lower():
            matches += 1
        
        quality_score = (matches / total_specs) * 100
    
    elif category.lower() == "monitors" and requirements.monitors:
        monitor_reqs = requirements.monitors
        specs = product.specifications
        
        # Count matching specs
        matches = 0
        total_specs = 7  # Total number of specs to check
        
        if specs.get("screenSize", "").lower() in monitor_reqs.screenSize.lower():
            matches += 1
        if specs.get("resolution", "").lower() in monitor_reqs.resolution.lower():
            matches += 1
        if specs.get("panelTech", "").lower() in monitor_reqs.panelTech.lower():
            matches += 1
        if specs.get("brightness", "").lower() in monitor_reqs.brightness.lower():
            matches += 1
        if specs.get("contrastRatio", "").lower() in monitor_reqs.contrastRatio.lower():
            matches += 1
        if specs.get("connectivity", "").lower() in monitor_reqs.connectivity.lower():
            matches += 1
        if specs.get("warranty", "").lower() in monitor_reqs.warranty.lower():
            matches += 1
        
        quality_score = (matches / total_specs) * 100
    
    else:
        # Default quality score for other categories
        quality_score = 70  # Arbitrary default
    
    # Calculate delivery score
    # Extract numeric value from delivery time (e.g., "15-30 days" -> 22.5)
    delivery_text = supplier.deliveryTime
    if "-" in delivery_text:
        parts = delivery_text.split("-")
        try:
            min_days = int(parts[0].strip())
            max_days = int(parts[1].split(" ")[0].strip())
            avg_days = (min_days + max_days) / 2
        except:
            avg_days = 30  # Default
    else:
        try:
            avg_days = int(delivery_text.split(" ")[0].strip())
        except:
            avg_days = 30  # Default
    
    # Lower days is better
    delivery_score = max(0, 100 - (avg_days * 2))  # 0 days -> 100%, 50 days -> 0%
    
    # Calculate weighted score
    match_score = (
        price_score * price_weight +
        quality_score * quality_weight +
        delivery_score * delivery_weight
    )
    
    match_details = {
        "price": price_score,
        "quality": quality_score,
        "delivery": delivery_score
    }
    
    return match_score, match_details