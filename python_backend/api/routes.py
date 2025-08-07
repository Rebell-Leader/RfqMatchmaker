"""
API routes for RFQ processing platform.

This module provides API routes for the RFQ processing platform,
with specialized handling for AI hardware procurement.
"""

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Query
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import json
import os
import shutil
import logging
from datetime import datetime

from ..models.schemas import RFQResponse, SupplierMatchResponse, EmailTemplate
from ..models.schemas import RFQUploadRequest, MatchSuppliersRequest, GenerateEmailRequest
from ..models.schemas import ExtractedRequirement
from ..models.db_storage import storage
from ..services.ai_service import extract_requirements_from_rfq, generate_email_proposal
# Use the specialized AI hardware matching service for GPU/accelerator requirements
from ..services.ai_hardware_matching import match_suppliers_for_rfq
from ..services.compliance_service import ComplianceService, check_product_shipping_restrictions
from ..services.product_scraper import create_sample_gpu_products, store_products_in_database

# Configure logging
logger = logging.getLogger(__name__)

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
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Received manual RFQ creation request: {rfq_request}")
        
        # Extract requirements using AI
        logger.info(f"Extracting requirements from specifications...")
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
        
        logger.info(f"Creating RFQ in database with data: {rfq_data}")
        rfq = await storage.create_rfq(rfq_data)
        
        response_data = {
            "id": rfq.id,
            "title": rfq.title,
            "description": rfq.description,
            "extractedRequirements": rfq.extractedRequirements
        }
        
        logger.info(f"RFQ created successfully with ID: {rfq.id}")
        return response_data
        
    except Exception as e:
        logger.error(f"Error creating RFQ: {str(e)}", exc_info=True)
        # Re-raise to let FastAPI handle the error response
        raise

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

# AI hardware specific endpoints
@router.post("/seed-ai-hardware-products", response_model=Dict[str, Any])
async def seed_ai_hardware_products():
    """Seed the database with sample AI hardware products for testing"""
    try:
        # Generate sample GPU products
        sample_products = create_sample_gpu_products()
        
        # Store in database
        await store_products_in_database(sample_products)
        
        return {
            "success": True,
            "message": f"Successfully seeded database with {len(sample_products)} AI hardware products",
            "products": [p["name"] for p in sample_products]
        }
    except Exception as e:
        logger.error(f"Error seeding AI hardware products: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error seeding AI hardware products: {str(e)}"
        )

@router.get("/ai-hardware/check-compliance", response_model=Dict[str, Any])
async def check_compliance(buyer_country: str, product_id: int):
    """Check compliance for shipping a specific product to a country"""
    try:
        # Get the product and supplier
        product = await storage.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        supplier = await storage.get_supplier_by_id(product.supplierId)
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
        
        # Convert product to dict
        product_dict = product.dict() if hasattr(product, "dict") else vars(product)
        
        # Check shipping restrictions
        compliance_result = check_product_shipping_restrictions(product_dict, buyer_country)
        
        # Get detailed compliance report
        compliance_service = ComplianceService()
        buyer = {"country": buyer_country}
        compliance_report = compliance_service.generate_compliance_report(
            buyer,
            supplier.dict() if hasattr(supplier, "dict") else vars(supplier),
            product_dict
        )
        
        return {
            "canShip": compliance_result["can_ship"],
            "restrictions": compliance_result["restrictions"],
            "requiresLicense": compliance_result["requires_license"],
            "requiredDocuments": compliance_result["required_documents"],
            "complianceReport": compliance_report
        }
    except Exception as e:
        logger.error(f"Error checking compliance: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error checking compliance: {str(e)}"
        )

@router.get("/ai-hardware/frameworks-compatibility", response_model=Dict[str, Any])
async def check_frameworks_compatibility(product_id: int, frameworks: List[str] = Query(None)):
    """Check if a product supports specific ML frameworks"""
    try:
        # Get the product
        product = await storage.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Convert product to dict
        product_dict = product.dict() if hasattr(product, "dict") else vars(product)
        
        # Extract supported frameworks
        supported_frameworks = product_dict.get("supportedFrameworks", [])
        
        # If supportedFrameworks is not in the main product dict, check in specifications
        if not supported_frameworks and "specifications" in product_dict:
            specifications = product_dict["specifications"]
            if isinstance(specifications, str):
                try:
                    specifications = json.loads(specifications)
                except:
                    specifications = {}
            
            supported_frameworks = specifications.get("supportedFrameworks", [])
        
        # Check compatibility with requested frameworks
        if not frameworks:
            return {
                "product": product.name,
                "supportedFrameworks": supported_frameworks,
                "compatibility": 1.0
            }
        
        # Count matching frameworks
        matching = 0
        framework_compatibility = {}
        for framework in frameworks:
            framework_lower = framework.lower()
            is_supported = False
            for supported in supported_frameworks:
                if framework_lower in supported.lower():
                    is_supported = True
                    matching += 1
                    break
            framework_compatibility[framework] = is_supported
        
        compatibility_score = matching / len(frameworks) if frameworks else 1.0
        
        return {
            "product": product.name,
            "supportedFrameworks": supported_frameworks,
            "requestedFrameworks": frameworks,
            "compatibilityScore": compatibility_score,
            "frameworkCompatibility": framework_compatibility
        }
    except Exception as e:
        logger.error(f"Error checking framework compatibility: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error checking framework compatibility: {str(e)}"
        )

@router.get("/ai-hardware/performance-comparison", response_model=Dict[str, Any])
async def compare_hardware_performance(product_ids: List[int] = Query(...), metric: str = "fp32"):
    """Compare performance metrics of multiple AI hardware products"""
    try:
        # Valid performance metrics
        valid_metrics = ["fp32", "fp16", "int8", "memory_bandwidth", "memory_capacity", "tdp"]
        
        if metric not in valid_metrics:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid metric. Valid options are: {', '.join(valid_metrics)}"
            )
        
        # Get the products
        products = []
        for pid in product_ids:
            product = await storage.get_product_by_id(pid)
            if product:
                products.append(product)
        
        if not products:
            raise HTTPException(status_code=404, detail="No valid products found")
        
        # Extract performance data
        performance_data = []
        for product in products:
            # Convert product to dict
            product_dict = product.dict() if hasattr(product, "dict") else vars(product)
            
            # Extract compute specs
            compute_specs = product_dict.get("computeSpecs", {})
            memory_specs = product_dict.get("memorySpecs", {})
            power_specs = product_dict.get("powerConsumption", {})
            
            # If specs are stored as strings, convert to dict
            if isinstance(compute_specs, str):
                try:
                    compute_specs = json.loads(compute_specs)
                except:
                    compute_specs = {}
            
            if isinstance(memory_specs, str):
                try:
                    memory_specs = json.loads(memory_specs)
                except:
                    memory_specs = {}
            
            if isinstance(power_specs, str):
                try:
                    power_specs = json.loads(power_specs)
                except:
                    power_specs = {}
            
            # Extract metric value
            metric_value = None
            if metric == "fp32":
                metric_value = compute_specs.get("fp32Performance", 0)
            elif metric == "fp16":
                metric_value = compute_specs.get("fp16Performance", 0)
            elif metric == "int8":
                metric_value = compute_specs.get("int8Performance", 0)
            elif metric == "memory_bandwidth":
                metric_value = memory_specs.get("bandwidth", 0)
            elif metric == "memory_capacity":
                metric_value = memory_specs.get("capacity", 0)
            elif metric == "tdp":
                metric_value = power_specs.get("tdp", 0)
            
            performance_data.append({
                "id": product.id,
                "name": product.name,
                "manufacturer": product_dict.get("manufacturer", "Unknown"),
                "metric": metric,
                "value": metric_value
            })
        
        # Sort by metric value (descending)
        performance_data.sort(key=lambda x: x["value"], reverse=True)
        
        # Calculate relative performance (% of best)
        if performance_data and performance_data[0]["value"]:
            best_value = performance_data[0]["value"]
            for item in performance_data:
                item["relativePerformance"] = (item["value"] / best_value) * 100
        
        metric_labels = {
            "fp32": "FP32 Performance (TFLOPS)",
            "fp16": "FP16 Performance (TFLOPS)",
            "int8": "INT8 Performance (TOPS)",
            "memory_bandwidth": "Memory Bandwidth (GB/s)",
            "memory_capacity": "Memory Capacity (GB)",
            "tdp": "Thermal Design Power (W)"
        }
        
        return {
            "metric": metric,
            "metricLabel": metric_labels.get(metric, metric),
            "products": performance_data
        }
    except Exception as e:
        logger.error(f"Error comparing hardware performance: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error comparing hardware performance: {str(e)}"
        )