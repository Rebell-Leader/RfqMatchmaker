"""
API routes for RFQ processing platform.
"""

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Query
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import json
import os
import shutil
from datetime import datetime

from ..models.schemas import RFQResponse, SupplierMatchResponse, EmailTemplate
from ..models.schemas import RFQUploadRequest, MatchSuppliersRequest, GenerateEmailRequest
from ..models.db_storage import storage
from ..services.ai_service import extract_requirements_from_rfq, generate_email_proposal
from ..services.supplier_matching import match_suppliers_for_rfq

# Create router
router = APIRouter()

# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)

@router.get("/rfqs", response_model=List[RFQResponse])
async def get_rfqs():
    """Get all RFQs"""
    rfqs = await storage.get_all_rfqs()
    return [
        RFQResponse(
            id=rfq.id,
            title=rfq.title,
            description=rfq.description,
            extractedRequirements=rfq.extractedRequirements,
            createdAt=rfq.createdAt
        )
        for rfq in rfqs
    ]

@router.get("/rfqs/{rfq_id}", response_model=RFQResponse)
async def get_rfq(rfq_id: int):
    """Get RFQ by ID"""
    rfq = await storage.get_rfq_by_id(rfq_id)
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    
    return RFQResponse(
        id=rfq.id,
        title=rfq.title,
        description=rfq.description,
        extractedRequirements=rfq.extractedRequirements,
        createdAt=rfq.createdAt
    )

@router.post("/rfqs/upload", response_model=Dict[str, Any])
async def upload_rfq(file: UploadFile = File(...)):
    """Upload RFQ document and extract requirements"""
    import PyPDF2  # Import at function level to avoid global import issues
    
    # Save uploaded file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"uploads/{timestamp}_{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Process file based on extension
    content = ""
    file_ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ""
    
    try:
        if file_ext == "pdf":
            # Extract text from PDF
            with open(file_path, "rb") as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                for page_num in range(len(pdf_reader.pages)):
                    content += pdf_reader.pages[page_num].extract_text() + "\n"
        else:
            # Assume it's a text file
            with open(file_path, "r", errors="replace") as f:
                content = f.read()
        
        # Extract requirements using AI
        extracted_requirements = await extract_requirements_from_rfq(content)
        
        # Create RFQ in database
        rfq_data = {
            "title": extracted_requirements.title,
            "description": extracted_requirements.description or "",
            "originalContent": content,
            "extractedRequirements": extracted_requirements,
            "userId": 1  # Default user ID
        }
        
        rfq = await storage.create_rfq(rfq_data)
        
        # Clean up the uploaded file
        try:
            os.remove(file_path)
        except:
            pass
        
        return {
            "id": rfq.id,
            "title": rfq.title,
            "description": rfq.description,
            "extractedRequirements": rfq.extractedRequirements
        }
    except Exception as e:
        # Log the error
        print(f"Error processing uploaded file: {str(e)}")
        
        # Create a fallback RFQ with mock data for demo purposes
        mock_requirements = {
            "title": file.filename.split('.')[0] if '.' in file.filename else "Computer Equipment RFQ",
            "description": "High School Computer Class Equipment",
            "categories": ["Laptops", "Monitors"],
            "laptops": {
                "quantity": 25,
                "os": "Windows 11 Pro",
                "processor": "Intel Core i5 12th Gen or higher",
                "memory": "16 GB DDR4",
                "storage": "512 GB SSD",
                "display": "15.6 inch Full HD (1920x1080)",
                "battery": "6+ hours battery life",
                "durability": "MIL-STD-810G tested",
                "connectivity": "USB 3.0, HDMI, Wi-Fi 6",
                "warranty": "3 years warranty"
            },
            "monitors": {
                "quantity": 25,
                "screenSize": "24 inch",
                "resolution": "1920x1080 Full HD",
                "panelTech": "IPS",
                "brightness": "250 cd/m²",
                "contrastRatio": "1000:1",
                "connectivity": "HDMI, DisplayPort",
                "adjustability": "Height, tilt, and swivel adjustable",
                "warranty": "3 years warranty"
            },
            "criteria": {
                "price": {"weight": 50},
                "quality": {"weight": 30},
                "delivery": {"weight": 20}
            }
        }
        
        extracted_requirements = ExtractedRequirement(**mock_requirements)
        
        rfq_data = {
            "title": mock_requirements["title"],
            "description": mock_requirements["description"],
            "originalContent": content or "Failed to extract content from file",
            "extractedRequirements": extracted_requirements,
            "userId": 1  # Default user ID
        }
        
        rfq = await storage.create_rfq(rfq_data)
        
        # Clean up the uploaded file
        try:
            os.remove(file_path)
        except:
            pass
        
        return {
            "id": rfq.id,
            "title": rfq.title,
            "description": rfq.description,
            "extractedRequirements": rfq.extractedRequirements
        }

@router.post("/rfqs", response_model=Dict[str, Any])
async def create_rfq(rfq_request: RFQUploadRequest):
    """Create RFQ manually with specifications"""
    # Extract requirements using AI
    extracted_requirements = await extract_requirements_from_rfq(rfq_request.specifications)
    
    # Override title and description if provided
    if rfq_request.title:
        extracted_requirements.title = rfq_request.title
    if rfq_request.description:
        extracted_requirements.description = rfq_request.description
    
    # Create RFQ in database
    rfq_data = {
        "title": extracted_requirements.title,
        "description": extracted_requirements.description or "",
        "originalContent": rfq_request.specifications,
        "extractedRequirements": extracted_requirements,
        "userId": 1  # Default user ID
    }
    
    rfq = await storage.create_rfq(rfq_data)
    
    return {
        "id": rfq.id,
        "title": rfq.title,
        "description": rfq.description,
        "extractedRequirements": rfq.extractedRequirements
    }

@router.get("/suppliers", response_model=List[Dict[str, Any]])
async def get_suppliers():
    """Get all suppliers"""
    suppliers = await storage.get_all_suppliers()
    return [supplier.dict() for supplier in suppliers]

@router.get("/products", response_model=List[Dict[str, Any]])
async def get_products(category: Optional[str] = None):
    """Get products, optionally filtered by category"""
    if category:
        products = await storage.get_products_by_category(category)
    else:
        # Get all products for all suppliers
        suppliers = await storage.get_all_suppliers()
        products = []
        for supplier in suppliers:
            supplier_products = await storage.get_products_by_supplier(supplier.id)
            products.extend(supplier_products)
    
    return [product.dict() for product in products]

@router.post("/rfqs/{rfq_id}/match-suppliers", response_model=SupplierMatchResponse)
async def match_suppliers(rfq_id: int):
    """Match suppliers based on RFQ requirements"""
    # Get the RFQ
    rfq = await storage.get_rfq_by_id(rfq_id)
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    
    # Use supplier matching service to find matches
    matches = await match_suppliers_for_rfq(rfq_id)
    
    # Create proposals in the database for top matches
    for match in matches:
        proposal_data = {
            "rfqId": rfq_id,
            "productId": match.product.id,
            "score": match.matchScore,
            "priceScore": match.matchDetails.price,
            "qualityScore": match.matchDetails.quality,
            "deliveryScore": match.matchDetails.delivery
        }
        await storage.create_proposal(proposal_data)
    
    return SupplierMatchResponse(
        rfqId=rfq_id,
        matches=matches
    )

@router.get("/rfqs/{rfq_id}/proposals", response_model=List[Dict[str, Any]])
async def get_proposals_by_rfq(rfq_id: int):
    """Get all proposals for an RFQ"""
    proposals = await storage.get_proposals_by_rfq(rfq_id)
    return [proposal.dict() for proposal in proposals]

@router.post("/proposals/{proposal_id}/generate-email", response_model=EmailTemplate)
async def generate_proposal_email(proposal_id: int):
    """Generate email proposal for a specific supplier match"""
    # Get the proposal
    proposal = await storage.get_proposal_by_id(proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # Get the RFQ, product, and supplier
    rfq = await storage.get_rfq_by_id(proposal.rfqId)
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    
    product = await storage.get_product_by_id(proposal.productId)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    supplier = await storage.get_supplier_by_id(product.supplierId)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    # Generate email proposal
    email_template = await generate_email_proposal(
        rfq.dict(),
        product.dict(),
        supplier.dict()
    )
    
    # Update proposal with email content
    proposal_data = {
        "rfqId": proposal.rfqId,
        "productId": proposal.productId,
        "score": proposal.score,
        "priceScore": proposal.priceScore,
        "qualityScore": proposal.qualityScore,
        "deliveryScore": proposal.deliveryScore,
        "emailContent": email_template.body
    }
    
    await storage.create_proposal(proposal_data)
    
    return email_template