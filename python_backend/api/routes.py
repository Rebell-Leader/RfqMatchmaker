from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import json
import os
from datetime import datetime

from ..models.schemas import (
    RFQUploadRequest,
    MatchSuppliersRequest,
    GenerateEmailRequest,
    RFQResponse,
    SupplierMatchResponse,
    ExtractedRequirement,
    SupplierMatch,
    EmailTemplate
)
from ..services.ai_service import extract_requirements_from_rfq, generate_email_proposal
from ..models.storage import MemStorage

# Create router
router = APIRouter()

# Create in-memory storage instance
storage = MemStorage()
storage.initialize_sample_data()

# RFQ endpoints
@router.get("/rfqs", response_model=List[RFQResponse])
async def get_rfqs():
    """Get all RFQs"""
    rfqs = await storage.get_all_rfqs()
    return rfqs

@router.get("/rfqs/{rfq_id}", response_model=Dict[str, Any])
async def get_rfq(rfq_id: int):
    """Get RFQ by ID"""
    rfq = await storage.get_rfq_by_id(rfq_id)
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    return rfq

@router.post("/rfqs/upload", status_code=201)
async def upload_rfq(file: UploadFile = File(...)):
    """Upload RFQ document and extract requirements"""
    try:
        # Read file content
        content = await file.read()
        content_text = content.decode("utf-8")
        
        # Save file to uploads directory for reference
        os.makedirs("uploads", exist_ok=True)
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Extract requirements using AI
        requirements = await extract_requirements_from_rfq(content_text)
        
        # Create RFQ in storage
        rfq_data = {
            "title": requirements.title,
            "description": requirements.description or "",
            "originalContent": content_text,
            "extractedRequirements": requirements.dict(),
            "userId": 1  # Mock user ID for the MVP
        }
        
        rfq = await storage.create_rfq(rfq_data)
        
        return {
            "id": rfq.id,
            "message": "RFQ uploaded and processed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing RFQ: {str(e)}")

@router.post("/rfqs", status_code=201)
async def create_rfq(rfq_request: RFQUploadRequest):
    """Create RFQ manually with specifications"""
    try:
        # Extract requirements using AI
        requirements = await extract_requirements_from_rfq(rfq_request.specifications)
        
        # Override title and description if provided
        requirements.title = rfq_request.title
        if rfq_request.description:
            requirements.description = rfq_request.description
        
        # Create RFQ in storage
        rfq_data = {
            "title": requirements.title,
            "description": requirements.description or "",
            "originalContent": rfq_request.specifications,
            "extractedRequirements": requirements.dict(),
            "userId": 1  # Mock user ID for the MVP
        }
        
        rfq = await storage.create_rfq(rfq_data)
        
        return {
            "id": rfq.id,
            "message": "RFQ created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating RFQ: {str(e)}")

# Supplier endpoints
@router.get("/suppliers")
async def get_suppliers():
    """Get all suppliers"""
    suppliers = await storage.get_all_suppliers()
    return suppliers

# Product endpoints
@router.get("/products")
async def get_products(category: Optional[str] = None):
    """Get products, optionally filtered by category"""
    if category:
        products = await storage.get_products_by_category(category)
    else:
        # Get all products (this is a simplified approach for the MVP)
        all_suppliers = await storage.get_all_suppliers()
        products = []
        for supplier in all_suppliers:
            supplier_products = await storage.get_products_by_supplier(supplier.id)
            products.extend(supplier_products)
    
    return products

# Matching endpoints
@router.post("/rfqs/{rfq_id}/match-suppliers", response_model=Dict[str, Any])
async def match_suppliers(rfq_id: int):
    """Match suppliers based on RFQ requirements"""
    # Get RFQ
    rfq = await storage.get_rfq_by_id(rfq_id)
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    
    # Extract requirements
    requirements = rfq.extractedRequirements
    
    # Get relevant products based on categories
    products = []
    for category in requirements.get("categories", []):
        category_products = await storage.get_products_by_category(category)
        products.extend(category_products)
    
    # Match products with requirements
    matches = []
    for product in products:
        # Get supplier for this product
        supplier = await storage.get_supplier_by_id(product.supplierId)
        if not supplier:
            continue
        
        # Calculate match score
        match_score = calculate_match_score(product, supplier, requirements, product.category)
        
        # Create supplier match object
        supplier_match = {
            "supplier": supplier,
            "product": product,
            "matchScore": match_score["totalScore"],
            "matchDetails": {
                "price": match_score["priceScore"],
                "quality": match_score["qualityScore"],
                "delivery": match_score["deliveryScore"]
            },
            "totalPrice": product.price * get_quantity_for_category(requirements, product.category)
        }
        
        matches.append(supplier_match)
    
    # Sort matches by score (descending)
    matches = sorted(matches, key=lambda x: x["matchScore"], reverse=True)
    
    # Save proposals in storage (in a real app)
    for match in matches:
        proposal_data = {
            "rfqId": rfq_id,
            "productId": match["product"].id,
            "score": match["matchScore"],
            "priceScore": match["matchDetails"]["price"],
            "qualityScore": match["matchDetails"]["quality"],
            "deliveryScore": match["matchDetails"]["delivery"]
        }
        await storage.create_proposal(proposal_data)
    
    return {
        "rfqId": rfq_id,
        "matches": matches
    }

# Email proposal endpoints
@router.post("/proposals/{proposal_id}/generate-email", response_model=EmailTemplate)
async def generate_proposal_email(proposal_id: int):
    """Generate email proposal for a specific supplier match"""
    # In a real app, get the proposal from storage
    # For this MVP, we'll mock it since we don't have actual proposal IDs
    
    # Extract product_id and supplier_id from the proposal_id (simplified approach)
    supplier_id = int(str(proposal_id)[0])
    product_id = int(str(proposal_id)[1:])
    
    # Get supplier and product
    supplier = await storage.get_supplier_by_id(supplier_id)
    product = await storage.get_product_by_id(product_id)
    
    if not supplier or not product:
        raise HTTPException(status_code=404, detail="Supplier or product not found")
    
    # Get the RFQ (simplified approach - just get the first RFQ)
    rfqs = await storage.get_all_rfqs()
    if not rfqs:
        raise HTTPException(status_code=404, detail="No RFQs found")
    
    rfq = rfqs[0]
    
    # Generate email proposal
    email_template = await generate_email_proposal(rfq, product, supplier)
    
    # Update proposal in storage (in a real app)
    # await storage.update_proposal(proposal_id, {"emailContent": email_template.body})
    
    return email_template

# Proposal endpoints
@router.get("/rfqs/{rfq_id}/proposals")
async def get_proposals_by_rfq(rfq_id: int):
    """Get all proposals for an RFQ"""
    proposals = await storage.get_proposals_by_rfq(rfq_id)
    return proposals

# Utility functions
def calculate_match_score(product: Any, supplier: Any, requirements: Dict[str, Any], category: str) -> Dict[str, float]:
    """Calculate match score between product and RFQ requirements"""
    # Get criteria weights
    criteria = requirements.get("criteria", {})
    price_weight = criteria.get("price", {}).get("weight", 50) / 100
    quality_weight = criteria.get("quality", {}).get("weight", 30) / 100
    delivery_weight = criteria.get("delivery", {}).get("weight", 20) / 100
    
    # Calculate price score (lower price = higher score)
    # For simplicity, we'll use a reference price
    reference_price = 1500 if category == "Laptops" else 400  # Reference price for laptops/monitors
    price_score = min(100, max(0, (reference_price / max(product.price, 1)) * 100))
    
    # Calculate quality score (this would be more sophisticated in a real app)
    # Here we'll use a combination of specs matching and supplier verification
    quality_score = 0
    
    if category == "Laptops" and requirements.get("laptops"):
        laptop_reqs = requirements["laptops"]
        specs = product.specifications
        
        # Match processor
        if "processor" in specs and specs["processor"].lower() in laptop_reqs["processor"].lower():
            quality_score += 20
        
        # Match memory
        if "memory" in specs and specs["memory"].lower() in laptop_reqs["memory"].lower():
            quality_score += 15
        
        # Match storage
        if "storage" in specs and specs["storage"].lower() in laptop_reqs["storage"].lower():
            quality_score += 15
        
        # Match OS
        if "os" in specs and specs["os"].lower() in laptop_reqs["os"].lower():
            quality_score += 10
        
        # Match display
        if "display" in specs and specs["display"].lower() in laptop_reqs["display"].lower():
            quality_score += 10
        
        # Match warranty
        if product.warranty and product.warranty.lower() in laptop_reqs["warranty"].lower():
            quality_score += 10
    
    elif category == "Monitors" and requirements.get("monitors"):
        monitor_reqs = requirements["monitors"]
        specs = product.specifications
        
        # Match screen size
        if "screenSize" in specs and specs["screenSize"].lower() in monitor_reqs["screenSize"].lower():
            quality_score += 25
        
        # Match resolution
        if "resolution" in specs and specs["resolution"].lower() in monitor_reqs["resolution"].lower():
            quality_score += 25
        
        # Match panel tech
        if "panelTech" in specs and specs["panelTech"].lower() in monitor_reqs["panelTech"].lower():
            quality_score += 20
        
        # Match warranty
        if product.warranty and product.warranty.lower() in monitor_reqs["warranty"].lower():
            quality_score += 10
    
    # Add supplier verification bonus
    if getattr(supplier, "isVerified", False):
        quality_score += 20
    
    # Cap quality score at 100
    quality_score = min(100, quality_score)
    
    # Calculate delivery score
    delivery_score = 0
    
    # Parse delivery time (e.g., "15-30 days" -> average of 22.5 days)
    delivery_time = parse_delivery_time(supplier.deliveryTime)
    
    # Score based on delivery time (faster = higher score)
    if delivery_time <= 7:
        delivery_score = 100
    elif delivery_time <= 14:
        delivery_score = 90
    elif delivery_time <= 21:
        delivery_score = 80
    elif delivery_time <= 30:
        delivery_score = 70
    elif delivery_time <= 45:
        delivery_score = 50
    else:
        delivery_score = 30
    
    # Calculate total score
    total_score = (
        price_score * price_weight +
        quality_score * quality_weight +
        delivery_score * delivery_weight
    )
    
    return {
        "totalScore": total_score,
        "priceScore": price_score,
        "qualityScore": quality_score,
        "deliveryScore": delivery_score
    }

def parse_delivery_time(delivery_time: str) -> float:
    """Parse delivery time string to get average days"""
    try:
        # Handle formats like "15-30 days"
        if "-" in delivery_time:
            parts = delivery_time.split("-")
            min_days = float(parts[0].strip())
            max_days = float(parts[1].split(" ")[0].strip())
            return (min_days + max_days) / 2
        
        # Handle formats like "15 days"
        else:
            return float(delivery_time.split(" ")[0].strip())
    except:
        # Default to 30 days if parsing fails
        return 30.0

def get_quantity_for_category(requirements: Dict[str, Any], category: str) -> int:
    """Get quantity from requirements for a specific category"""
    if category == "Laptops" and requirements.get("laptops"):
        return requirements["laptops"]["quantity"]
    elif category == "Monitors" and requirements.get("monitors"):
        return requirements["monitors"]["quantity"]
    else:
        return 1  # Default quantity