from typing import Dict, List, Optional, Any
import json
import re
import openai
import os
from datetime import datetime
from ..models.schemas import (
    ExtractedRequirement, LaptopRequirements, MonitorRequirements, 
    AwardCriteria, EmailTemplate
)

# In a real implementation, this would use the OpenAI API key from environment variables
# openai.api_key = os.environ.get("OPENAI_API_KEY")

async def extract_requirements_from_rfq(content: str) -> ExtractedRequirement:
    """
    Extract structured requirements from RFQ document using Featherless AI.
    
    This is a mock implementation for the MVP that simulates AI extraction.
    In a real implementation, this would use OpenAI's API to extract requirements.
    """
    # For the MVP, we'll parse the sample content and return pre-determined structured data
    # In a real implementation, this would use AI to extract requirements
    
    # Default values
    title = "High School Computer Class Equipment"
    description = "Supply and delivery of laptops and monitors for high school computer lab"
    categories = ["Laptops", "Monitors"]
    
    # Initialize requirements
    laptops = None
    monitors = None
    
    # Extract laptops requirements if present in content
    if "laptop" in content.lower():
        laptops = LaptopRequirements(
            quantity=30,
            os="Windows 11 Pro or Education",
            processor="Intel Core i5 11th gen or equivalent",
            memory="16GB DDR4",
            storage="512GB SSD",
            display="14-inch FHD (1920 x 1080)",
            battery="8+ hours battery life",
            durability="MIL-STD-810H tested",
            connectivity="Wi-Fi 6, Bluetooth 5.0",
            warranty="3 years onsite"
        )
    
    # Extract monitors requirements if present in content
    if "monitor" in content.lower():
        monitors = MonitorRequirements(
            quantity=30,
            screenSize="27 inches",
            resolution="2K QHD (2560 x 1440)",
            panelTech="IPS",
            brightness="300 cd/m² or higher",
            contrastRatio="1000:1 or higher",
            connectivity="HDMI, DisplayPort, USB-C",
            adjustability="Height, tilt, swivel adjustable",
            warranty="3 years standard"
        )
    
    # Extract award criteria
    criteria = AwardCriteria(
        price={"weight": 50},
        quality={"weight": 30},
        delivery={"weight": 20}
    )
    
    # If title is in the content, try to extract it
    title_match = re.search(r"Title:?\s*([^\n]+)", content)
    if title_match:
        title = title_match.group(1).strip()
    
    # Create ExtractedRequirement object
    requirement = ExtractedRequirement(
        title=title,
        description=description,
        categories=categories,
        laptops=laptops,
        monitors=monitors,
        criteria=criteria
    )
    
    return requirement

async def generate_email_proposal(rfq: Dict[str, Any], product: Dict[str, Any], supplier: Dict[str, Any]) -> EmailTemplate:
    """
    Generate personalized email proposal for a selected supplier.
    
    This is a mock implementation for the MVP that simulates AI email generation.
    In a real implementation, this would use OpenAI's API to generate the email.
    """
    # Extract relevant information
    supplier_name = supplier.get("name", "Supplier")
    product_name = product.get("name", "Product")
    product_category = product.get("category", "")
    product_price = product.get("price", 0)
    warranty = product.get("warranty", "")
    
    if "title" in rfq:
        rfq_title = rfq.get("title", "RFQ")
    elif "extractedRequirements" in rfq and "title" in rfq["extractedRequirements"]:
        rfq_title = rfq["extractedRequirements"]["title"]
    else:
        rfq_title = "RFQ"
    
    # Calculate total price
    quantity = 0
    if product_category.lower() == "laptops" and "extractedRequirements" in rfq and "laptops" in rfq["extractedRequirements"]:
        quantity = rfq["extractedRequirements"]["laptops"]["quantity"]
    elif product_category.lower() == "monitors" and "extractedRequirements" in rfq and "monitors" in rfq["extractedRequirements"]:
        quantity = rfq["extractedRequirements"]["monitors"]["quantity"]
    
    total_price = product_price * quantity
    
    # Generate email subject
    subject = f"Proposal for {rfq_title}: {product_name}"
    
    # Format total price with commas and two decimal places
    formatted_price = "${:,.2f}".format(total_price)
    
    # Generate email body
    body = f"""Dear {supplier_name} Team,

We are pleased to invite you to submit a formal quotation for our {rfq_title} project. After careful evaluation of available options, we have identified your {product_name} as a potential match for our requirements.

Project Details:
- Project: {rfq_title}
- Product: {product_name}
- Quantity: {quantity} units
- Estimated Total: {formatted_price}

We are particularly interested in the following specifications and features:
- {", ".join([f"{k.capitalize()}: {v}" for k, v in product.get("specifications", {}).items()][:5])}
- Warranty: {warranty}

Please provide a formal quotation including:
1. Confirmed unit and total pricing
2. Delivery timeline
3. Warranty terms and conditions
4. Any educational discounts available
5. Technical support options

We look forward to your response and potentially working with {supplier_name} on this project. Please submit your quotation by [DATE] to be considered.

If you have any questions or need additional information, please don't hesitate to contact us.

Best regards,
Procurement Team
[YOUR ORGANIZATION]
[CONTACT INFORMATION]
"""
    
    # Create EmailTemplate object
    email_template = EmailTemplate(
        to=supplier.get("contactEmail", "contact@example.com"),
        subject=subject,
        body=body
    )
    
    return email_template