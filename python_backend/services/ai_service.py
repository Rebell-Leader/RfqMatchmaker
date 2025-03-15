"""
AI service for RFQ processing platform.

This module provides AI-powered functions for extracting requirements from RFQ documents
and generating personalized email proposals based on matched suppliers.
"""

import json
import re
from typing import Dict, Any, List, Optional

from ..models.schemas import ExtractedRequirement, LaptopRequirements, MonitorRequirements, AwardCriteria, EmailTemplate

# For a real implementation, we would use OpenAI's API or another AI service
# Since this is an MVP, we'll implement mock versions of these functions

async def extract_requirements_from_rfq(content: str) -> ExtractedRequirement:
    """
    Extract structured requirements from RFQ document using Featherless AI.
    
    This is a mock implementation for the MVP that simulates AI extraction.
    In a real implementation, this would use OpenAI's API to extract requirements.
    """
    # Check if the content includes laptops
    laptop_match = bool(re.search(r'laptop|notebook|computer', content.lower()))
    
    # Check if the content includes monitors
    monitor_match = bool(re.search(r'monitor|display|screen', content.lower()))
    
    # Determine categories based on content
    categories = []
    if laptop_match:
        categories.append("Laptops")
    if monitor_match:
        categories.append("Monitors")
    
    # If no categories detected, default to laptops (for demo purposes)
    if not categories:
        categories = ["Laptops"]
    
    # Extract title from content
    title_match = re.search(r'Title:\s*([^\n]+)', content)
    title = title_match.group(1) if title_match else "Supply and Delivery of IT Equipment"
    
    # Extract description from content
    description_match = re.search(r'Description:\s*([^\n]+)', content)
    description = description_match.group(1) if description_match else "Procurement of IT equipment for organizational use"
    
    # Create requirements object
    requirements = {
        "title": title,
        "description": description,
        "categories": categories,
        "criteria": {
            "price": {"weight": 50},
            "quality": {"weight": 30},
            "delivery": {"weight": 20}
        }
    }
    
    # Extract laptop requirements if needed
    if "Laptops" in categories:
        # Try to extract quantity
        quantity_match = re.search(r'quantity[:\s]*(\d+)', content.lower())
        quantity = int(quantity_match.group(1)) if quantity_match else 30
        
        # Create laptop requirements
        requirements["laptops"] = {
            "quantity": quantity,
            "os": "Windows 11 Pro",
            "processor": "Intel Core i5 or better",
            "memory": "16GB DDR4",
            "storage": "512GB SSD",
            "display": "14-inch FHD (1920 x 1080)",
            "battery": "8+ hours",
            "durability": "MIL-STD-810H tested",
            "connectivity": "Wi-Fi 6, Bluetooth 5.0",
            "warranty": "3 years onsite"
        }
    
    # Extract monitor requirements if needed
    if "Monitors" in categories:
        # Try to extract quantity
        quantity_match = re.search(r'quantity[:\s]*(\d+)', content.lower())
        quantity = int(quantity_match.group(1)) if quantity_match else 30
        
        # Create monitor requirements
        requirements["monitors"] = {
            "quantity": quantity,
            "screenSize": "27 inches",
            "resolution": "QHD (2560 x 1440)",
            "panelTech": "IPS",
            "brightness": "300 cd/m² or higher",
            "contrastRatio": "1000:1 or higher",
            "connectivity": "HDMI, DisplayPort, USB-C",
            "adjustability": "Height, tilt, swivel adjustable",
            "warranty": "3 years standard"
        }
    
    # Create and return ExtractedRequirement object
    return ExtractedRequirement(**requirements)

async def generate_email_proposal(rfq: Dict[str, Any], product: Dict[str, Any], supplier: Dict[str, Any]) -> EmailTemplate:
    """
    Generate personalized email proposal for a selected supplier.
    
    This is a mock implementation for the MVP that simulates AI email generation.
    In a real implementation, this would use OpenAI's API to generate the email.
    """
    # Extract key information
    rfq_title = rfq.get("title", "IT Equipment Procurement")
    supplier_name = supplier.get("name", "Supplier")
    product_name = product.get("name", "Product")
    product_category = product.get("category", "IT Equipment")
    product_price = product.get("price", 0)
    quantity = 30  # Default quantity
    
    # Try to get actual quantity from requirements
    requirements = rfq.get("extractedRequirements", {})
    if product_category == "Laptops" and requirements.get("laptops"):
        quantity = requirements["laptops"].get("quantity", 30)
    elif product_category == "Monitors" and requirements.get("monitors"):
        quantity = requirements["monitors"].get("quantity", 30)
    
    # Calculate total price
    total_price = product_price * quantity
    
    # Generate subject line
    subject = f"RFQ Proposal: {rfq_title} - {supplier_name}"
    
    # Generate email body
    body = f"""Dear Procurement Team,

I hope this email finds you well. We are pleased to submit our proposal in response to your Request for Quotation (RFQ) for {rfq_title}.

After careful review of your requirements, we recommend the following product:

Product: {product_name}
Category: {product_category}
Unit Price: ${product_price:.2f}
Quantity: {quantity}
Total Price: ${total_price:.2f}

Key Features:
"""

    # Add product-specific features
    if product_category == "Laptops":
        specs = product.get("specifications", {})
        body += f"""- Operating System: {specs.get('os', 'Windows 11 Pro')}
- Processor: {specs.get('processor', 'Intel Core i7')}
- Memory: {specs.get('memory', '16GB')}
- Storage: {specs.get('storage', '512GB SSD')}
- Display: {specs.get('display', '14-inch FHD')}
- Battery Life: {specs.get('battery', '8+ hours')}
- Warranty: {product.get('warranty', '3 years')}
"""
    elif product_category == "Monitors":
        specs = product.get("specifications", {})
        body += f"""- Screen Size: {specs.get('screenSize', '27 inches')}
- Resolution: {specs.get('resolution', 'QHD (2560 x 1440)')}
- Panel Technology: {specs.get('panelTech', 'IPS')}
- Brightness: {specs.get('brightness', '300 cd/m²')}
- Connectivity: {specs.get('connectivity', 'HDMI, DisplayPort, USB-C')}
- Adjustability: {specs.get('adjustability', 'Height, tilt, swivel adjustable')}
- Warranty: {product.get('warranty', '3 years')}
"""

    # Complete the email with delivery information and closing
    body += f"""
Delivery Information:
- Estimated Delivery Time: {supplier.get('deliveryTime', '15-30 days')}
- Shipping Method: Express Courier
- Shipping Fee: Included in the total price

We believe that {product_name} is the ideal solution for your requirements, offering excellent performance, reliability, and value for money. {supplier_name} is committed to providing high-quality products and exceptional service.

Should you have any questions or require additional information, please don't hesitate to contact us at {supplier.get('contactEmail', 'sales@example.com')} or {supplier.get('contactPhone', '+1-555-123-4567')}.

We look forward to the opportunity of working with you.

Best regards,
Sales Team
{supplier_name}
{supplier.get('website', 'www.example.com')}
"""

    # Create and return EmailTemplate object
    return EmailTemplate(
        to=f"procurement@example.com",
        cc=f"sales@{supplier.get('website', 'example.com').replace('https://www.', '').replace('http://www.', '')}",
        subject=subject,
        body=body
    )