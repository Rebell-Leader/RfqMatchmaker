
"""
AI service for processing RFQ documents and extracting requirements.
"""

import json
import logging
import os
from typing import Dict, Any, Optional
from openai import OpenAI
from ..models.schemas import ExtractedRequirement

# Configure logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client
def get_openai_client():
    """Get OpenAI client with proper API key handling"""
    api_key = os.getenv("FEATHERLESS_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("No API key found. Please set FEATHERLESS_API_KEY or OPENAI_API_KEY environment variable.")
    
    # Use Featherless AI endpoint if using their key
    if api_key.startswith("rc_"):
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.featherless.ai/v1"
        )
        logger.info("Using Featherless AI for requirement extraction")
    else:
        client = OpenAI(api_key=api_key)
        logger.info("Using OpenAI for requirement extraction")
    
    return client

async def extract_requirements_from_rfq(content: str) -> ExtractedRequirement:
    """Extract structured requirements from RFQ content using AI."""
    
    if not content or len(content.strip()) < 10:
        logger.warning("Content too short or empty, using fallback requirements")
        return _get_fallback_requirements()
    
    try:
        client = get_openai_client()
        
        system_prompt = """
        You are an expert procurement analyst specializing in extracting structured requirements from RFQ documents.
        
        Analyze the provided RFQ content and extract key information in JSON format.
        
        Focus on these areas:
        - title: Brief descriptive title
        - description: Summary of what's being procured  
        - categories: Types of equipment/services needed
        - quantity: Number of units
        - technical_specifications: Detailed requirements
        - criteria: Evaluation criteria with weights (price, quality, delivery)
        - timeline: Delivery or project timeline
        
        For AI hardware RFQs, also extract:
        - compute_requirements: Performance needs (FLOPS, memory, etc.)
        - frameworks: Required ML/AI frameworks
        - compliance: Export control or regulatory requirements
        
        Return ONLY valid JSON with no additional text.
        """
        
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-32B-Instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extract requirements from this RFQ:\n\n{content}"}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        
        extracted_content = response.choices[0].message.content
        logger.info(f"AI extracted content: {extracted_content}")
        
        # Parse JSON response
        try:
            extracted_data = json.loads(extracted_content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            return _get_fallback_requirements()
        
        # Convert to ExtractedRequirement object
        return ExtractedRequirement(**extracted_data)
        
    except Exception as e:
        logger.error(f"Error in AI requirement extraction: {str(e)}")
        return _get_fallback_requirements()

def _get_fallback_requirements() -> ExtractedRequirement:
    """Return fallback requirements when AI extraction fails"""
    return ExtractedRequirement(
        title="General Equipment Procurement",
        description="Equipment procurement requirements",
        categories=["General Equipment"],
        quantity=1,
        technical_specifications="Standard specifications as per requirements",
        criteria={
            "price": {"weight": 40},
            "quality": {"weight": 40},
            "delivery": {"weight": 20}
        }
    )

async def generate_email_proposal(rfq_data: Dict[str, Any], product_data: Dict[str, Any], supplier_data: Dict[str, Any]) -> Dict[str, str]:
    """Generate professional email proposal for supplier"""
    
    try:
        client = get_openai_client()
        
        system_prompt = """
        Generate a professional email proposal for a supplier responding to an RFQ.
        The email should be formal, detailed, and persuasive.
        
        Include:
        - Professional greeting and introduction
        - Reference to the RFQ and understanding of requirements
        - Product/service highlights that match the requirements
        - Competitive advantages and value proposition
        - Next steps and contact information
        
        Return JSON with: {"subject": "...", "body": "..."}
        """
        
        user_content = f"""
        RFQ Details:
        Title: {rfq_data.get('title', 'N/A')}
        Description: {rfq_data.get('description', 'N/A')}
        
        Product Details:
        Name: {product_data.get('name', 'N/A')}
        Price: ${product_data.get('price', 'N/A')}
        
        Supplier Details:
        Name: {supplier_data.get('name', 'N/A')}
        Contact: {supplier_data.get('contactEmail', 'N/A')}
        """
        
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-32B-Instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        logger.error(f"Error generating email proposal: {str(e)}")
        return {
            "subject": f"Proposal for {rfq_data.get('title', 'Your RFQ')}",
            "body": f"Dear Procurement Team,\n\nWe are pleased to submit our proposal for your recent RFQ.\n\nBest regards,\n{supplier_data.get('name', 'Supplier Team')}"
        }
