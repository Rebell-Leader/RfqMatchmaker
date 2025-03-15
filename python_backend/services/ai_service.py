import os
import json
from typing import Dict, Any
import openai
from ..models.schemas import ExtractedRequirement, EmailTemplate

# Initialize Featherless AI client
openai.api_base = "https://api.featherless.ai/v1"
openai.api_key = os.environ.get("FEATHERLESS_API_KEY", "rc_f8cf96bf43de3fde06f99a693f4d11e32d0c68a3bf3b7cdcaf851efec169d0b8")


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
        
        response = await openai.ChatCompletion.acreate(
            model="Qwen/Qwen2.5-32B-Instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ],
            temperature=0.2
        )
        
        extracted_content = response.choices[0].message.content
        
        try:
            parsed_data = json.loads(extracted_content)
            return ExtractedRequirement(**parsed_data)
        except Exception as e:
            print(f"Error parsing AI response as JSON: {e}")
            # Return fallback structure
            return ExtractedRequirement(
                title="Failed to parse RFQ",
                description="Could not extract structured data from the RFQ document",
                categories=[],
                criteria={
                    "price": {"weight": 50}, 
                    "quality": {"weight": 30}, 
                    "delivery": {"weight": 20}
                }
            )
    
    except Exception as e:
        print(f"Error extracting requirements from RFQ: {e}")
        # Return fallback structure
        return ExtractedRequirement(
            title="Error Processing RFQ",
            description="An error occurred while processing the RFQ document",
            categories=[],
            criteria={
                "price": {"weight": 50}, 
                "quality": {"weight": 30}, 
                "delivery": {"weight": 20}
            }
        )


async def generate_email_proposal(rfq: Dict[str, Any], product: Dict[str, Any], supplier: Dict[str, Any]) -> EmailTemplate:
    """
    Generate personalized email proposal for a selected supplier.
    """
    try:
        system_prompt = f"""
            You are a professional procurement specialist generating a purchase proposal email to send to a supplier.
            
            The email should:
            1. Be formal yet friendly
            2. Reference the RFQ clearly
            3. Show interest in the specific product
            4. Request a formal quotation and timeline
            5. End with a clear call to action
            
            Format the response as a JSON object with the following fields:
            {{
                "to": email address of supplier,
                "cc": email for cc (optional),
                "subject": professional email subject,
                "body": complete email body with proper formatting
            }}
            
            Return ONLY the JSON response.
        """
        
        requirements = rfq.get("extractedRequirements", {})
        rfq_title = requirements.get("title", "Product Request")
        
        user_prompt = f"""
            RFQ Details:
            - Title: {rfq_title}
            - Description: {requirements.get("description", "")}
            
            Selected Supplier:
            - Name: {supplier.get("name")}
            - Contact Email: {supplier.get("contactEmail")}
            
            Product:
            - Name: {product.get("name")}
            - Price: ${product.get("price")}
            - Specifications: {json.dumps(product.get("specifications", {}))}
            
            Generate an email proposal to this supplier.
        """
        
        response = await openai.ChatCompletion.acreate(
            model="Qwen/Qwen2.5-32B-Instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4
        )
        
        email_content = response.choices[0].message.content
        
        try:
            email_data = json.loads(email_content)
            return EmailTemplate(**email_data)
        except Exception as e:
            print(f"Error parsing AI response as JSON for email: {e}")
            # Return fallback email template
            return EmailTemplate(
                to=supplier.get("contactEmail", "supplier@example.com"),
                subject=f"RFQ: {rfq_title}",
                body=f"""Dear {supplier.get('name')} Team,

We are interested in your {product.get('name')} for our {rfq_title} project. 
Please provide a formal quotation for {requirements.get('laptops', {}).get('quantity', 0) or requirements.get('monitors', {}).get('quantity', 0)} units.

Best regards,
Procurement Team"""
            )
    
    except Exception as e:
        print(f"Error generating email proposal: {e}")
        # Return fallback email template
        return EmailTemplate(
            to=supplier.get("contactEmail", "supplier@example.com"),
            subject=f"RFQ: {rfq_title}",
            body=f"""Dear {supplier.get('name')} Team,

We are interested in your {product.get('name')} for our project. 
Please provide a formal quotation.

Best regards,
Procurement Team"""
        )