"""
AI service for RFQ processing platform.

This module provides AI-powered functions for extracting requirements from RFQ documents
and generating personalized email proposals based on matched suppliers.
"""

import json
import os
from typing import Dict, Any, Optional
from openai import OpenAI

from ..models.schemas import ExtractedRequirement, EmailTemplate

# Get API key from environment variable, fall back to a default for development only
API_KEY = os.environ.get("FEATHERLESS_API_KEY", "rc_f8cf96bf43de3fde06f99a693f4d11e32d0c68a3bf3b7cdcaf851efec169d0b8")

# Initialize Featherless AI client
client = OpenAI(
    base_url="https://api.featherless.ai/v1",
    api_key=API_KEY,
)

async def extract_requirements_from_rfq(content: str) -> ExtractedRequirement:
    """
    Extract structured requirements from RFQ document using Featherless AI.
    """
    try:
        system_prompt = """
        You are an AI assistant that extracts structured information from Request for Quotations (RFQs).
        Given an RFQ document, extract the following information in JSON format:
        - title: The title of the RFQ
        - description: A brief description of the RFQ purpose
        - categories: Array of product categories (e.g., "Laptops", "Monitors")
        - laptops: If present, extract details about laptop requirements including:
          - quantity: Number of units
          - os: Operating system requirements
          - processor: Processor specifications
          - memory: RAM specifications
          - storage: Storage specifications
          - display: Display specifications
          - battery: Battery life requirements
          - durability: Durability certifications needed
          - connectivity: Required ports and wireless connectivity
          - warranty: Warranty requirements
        - monitors: If present, extract details about monitor requirements including:
          - quantity: Number of units
          - screenSize: Screen size specifications
          - resolution: Resolution requirements
          - panelTech: Panel technology requirements
          - brightness: Brightness specifications
          - contrastRatio: Contrast ratio requirements
          - connectivity: Required ports
          - adjustability: Adjustability features required
          - warranty: Warranty requirements
        - criteria: Award criteria with weights for:
          - price: {weight: number from 0-100}
          - quality: {weight: number from 0-100}
          - delivery: {weight: number from 0-100}
        
        Return ONLY the JSON response with no other text or explanation.
        """
        
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-32B-Instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ],
            temperature=0.2,
        )
        
        extracted_content = response.model_dump()['choices'][0]['message']['content']
        
        try:
            parsed_content = json.loads(extracted_content)
            return ExtractedRequirement(**parsed_content)
        except json.JSONDecodeError:
            print(f"Error parsing AI response as JSON: {extracted_content}")
            # Create default requirements
            return ExtractedRequirement(
                title="Failed to parse RFQ",
                description="Could not extract structured data from the RFQ document",
                categories=["Laptops"],
                criteria={
                    "price": {"weight": 50},
                    "quality": {"weight": 30},
                    "delivery": {"weight": 20}
                }
            )
    except Exception as e:
        print(f"Error extracting requirements from RFQ: {str(e)}")
        # Create default requirements
        return ExtractedRequirement(
            title="Error Processing RFQ",
            description="An error occurred while processing the RFQ document",
            categories=["Laptops"],
            criteria={
                "price": {"weight": 50},
                "quality": {"weight": 30},
                "delivery": {"weight": 20}
            }
        )

async def generate_email_proposal(rfq: Dict[str, Any], product: Dict[str, Any], supplier: Dict[str, Any]) -> EmailTemplate:
    """
    Generate personalized email proposal for a selected supplier using Featherless AI.
    """
    try:
        # Format the prompt with the required information
        system_prompt = """
        You are an AI assistant that helps procurement professionals create personalized email proposals to suppliers.
        Please generate a professional and persuasive email proposal based on the provided information.
        
        The email should follow this structure:
        1. Professional greeting
        2. Brief introduction to the proposal
        3. Description of the selected product and its suitability for the requirements
        4. Detailed pricing information including any volume discounts
        5. Technical specifications and how they meet or exceed the requirements
        6. Terms and conditions including delivery, warranty, and payment terms
        7. Call to action and next steps
        8. Professional closing
        
        Make the email personal, professional, and persuasive, highlighting how the selected product provides value and meets the requirements.
        """
        
        # Create user prompt with all necessary information
        user_prompt = f"""
        Generate an email proposal for this RFQ:
        
        RFQ Information:
        Title: {rfq.get("title", "IT Equipment Procurement")}
        Description: {rfq.get("description", "Procurement of IT equipment")}
        ID: {rfq.get("id", "RFQ-2023-001")}
        Categories: {rfq.get("extractedRequirements", {}).get("categories", ["IT Equipment"])}
        
        Selected Supplier:
        Name: {supplier.get("name", "Supplier")}
        Country: {supplier.get("country", "Unknown")}
        Contact Email: {supplier.get("contactEmail", "supplier@example.com")}
        Delivery Time: {supplier.get("deliveryTime", "30 days")}
        
        Selected Product:
        Name: {product.get("name", "Product")}
        Category: {product.get("category", "IT Equipment")}
        Price: ${product.get("price", 0)}
        Description: {product.get("description", "")}
        Warranty: {product.get("warranty", "1 year")}
        Specifications: {json.dumps(product.get("specifications", {}))}
        
        Requirements:
        {json.dumps(rfq.get("extractedRequirements", {}))}
        
        Generate ONLY the email content with Subject and Body.
        """
        
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-32B-Instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
        )
        
        generated_content = response.model_dump()['choices'][0]['message']['content']
        
        # Extract subject and body from the response
        subject_match = None
        if "Subject:" in generated_content:
            parts = generated_content.split("Subject:", 1)
            if len(parts) > 1:
                subject_body = parts[1].split("\n", 1)
                subject_match = subject_body[0].strip()
                body = subject_body[1].strip() if len(subject_body) > 1 else ""
        
        if not subject_match:
            subject = f"Proposal for {rfq.get('title', 'IT Equipment Procurement')}: {supplier.get('name', 'Supplier')} Solution"
            body = generated_content
        else:
            subject = subject_match
            body = body if 'body' in locals() else generated_content
        
        # Create email template
        email_template = EmailTemplate(
            to=supplier.get("contactEmail", "supplier@example.com"),
            subject=subject,
            body=body
        )
        
        return email_template
    
    except Exception as e:
        print(f"Error generating email proposal: {str(e)}")
        # Create a default email template
        return EmailTemplate(
            to=supplier.get("contactEmail", "supplier@example.com"),
            subject=f"Proposal for {rfq.get('title', 'IT Equipment')}",
            body=f"""Dear {supplier.get('name', 'Supplier')},

Thank you for the opportunity to submit a proposal for {rfq.get('title', 'IT Equipment')}. We believe our {product.get('name', 'product')} is an excellent fit for your requirements.

The total price for {product.get('quantity', 1)} units is ${product.get('price', 0) * product.get('quantity', 1):.2f}.

We look forward to your favorable consideration.

Best regards,
Procurement Team
"""
        )