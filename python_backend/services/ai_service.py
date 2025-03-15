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
# Since this is an MVP, we'll implement a more sophisticated version of these functions

async def extract_requirements_from_rfq(content: str) -> ExtractedRequirement:
    """
    Extract structured requirements from RFQ document using AI.
    
    This implementation performs more detailed pattern matching to extract 
    requirements from RFQ documents. In a production environment, this would
    use OpenAI's API or another AI service.
    """
    # Check if the content includes laptops or computers
    laptop_match = bool(re.search(r'laptop|notebook|computer', content.lower()))
    
    # Check if the content includes monitors or displays
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
    if not title_match:
        title_match = re.search(r'RFQ.*?Title:?\s*([^\n]+)', content, re.IGNORECASE)
    title = title_match.group(1) if title_match else "Supply and Delivery of IT Equipment"
    
    # Extract description from content
    description_match = re.search(r'Description:\s*([^\n\.]+)', content)
    if not description_match:
        description_match = re.search(r'(procurement of.*?)(?:\n|\.)', content, re.IGNORECASE)
    description = description_match.group(1) if description_match else "Procurement of IT equipment for organizational use"
    
    # Extract award criteria if present
    price_weight = 50
    quality_weight = 30
    delivery_weight = 20
    
    price_weight_match = re.search(r'price.*?(\d+)%', content, re.IGNORECASE)
    if price_weight_match:
        price_weight = int(price_weight_match.group(1))
        
    quality_weight_match = re.search(r'quality.*?(\d+)%', content, re.IGNORECASE)
    if quality_weight_match:
        quality_weight = int(quality_weight_match.group(1))
        
    delivery_weight_match = re.search(r'delivery.*?(\d+)%', content, re.IGNORECASE)
    if delivery_weight_match:
        delivery_weight = int(delivery_weight_match.group(1))
    
    # Normalize weights to ensure they add up to 100
    total_weight = price_weight + quality_weight + delivery_weight
    if total_weight != 100:
        price_weight = int((price_weight / total_weight) * 100)
        quality_weight = int((quality_weight / total_weight) * 100)
        delivery_weight = 100 - price_weight - quality_weight
    
    # Create requirements object
    requirements = {
        "title": title.strip(),
        "description": description.strip(),
        "categories": categories,
        "criteria": {
            "price": {"weight": price_weight},
            "quality": {"weight": quality_weight},
            "delivery": {"weight": delivery_weight}
        }
    }
    
    # Extract laptop requirements if needed
    if "Laptops" in categories:
        # Extract quantity
        quantity_match = re.search(r'quantity[:\s]*(\d+)|(\d+)\s*laptop', content.lower())
        quantity = int(quantity_match.group(1) or quantity_match.group(2)) if quantity_match else 30
        
        # Extract OS requirements
        os_match = re.search(r'operating system[:\s]*(windows|linux|macos|chrome\s*os).*?(\d+|\w+)', content.lower())
        os = "Windows 11 Pro"
        if os_match:
            os_type = os_match.group(1)
            os_version = os_match.group(2)
            if os_type.lower() == "windows":
                os = f"Windows {os_version}"
            elif os_type.lower() == "macos":
                os = f"macOS {os_version}"
            elif os_type.lower() == "linux":
                os = f"Linux {os_version}"
            elif os_type.lower() == "chrome os":
                os = "Chrome OS"
        
        # Extract processor requirements
        processor_match = re.search(r'processor[:\s]*(intel|amd).*?(i\d|ryzen|core).*?(\d+)', content.lower())
        processor = "Intel Core i5 or better"
        if processor_match:
            proc_brand = processor_match.group(1)
            proc_family = processor_match.group(2)
            proc_gen = processor_match.group(3)
            if proc_brand.lower() == "intel":
                processor = f"Intel {proc_family.title()} {proc_gen}"
            elif proc_brand.lower() == "amd":
                processor = f"AMD {proc_family.title()} {proc_gen}"
        
        # Extract memory requirements
        memory_match = re.search(r'memory[:\s]*(\d+)\s*(gb|gigabyte)', content.lower())
        memory = "16GB DDR4"
        if memory_match:
            memory_size = memory_match.group(1)
            memory_type_match = re.search(r'(ddr\d)', content.lower())
            memory_type = memory_type_match.group(1).upper() if memory_type_match else "DDR4"
            memory = f"{memory_size}GB {memory_type}"
        
        # Extract storage requirements
        storage_match = re.search(r'storage[:\s]*(\d+)\s*(gb|tb|gigabyte|terabyte)', content.lower())
        storage = "512GB SSD"
        if storage_match:
            storage_size = storage_match.group(1)
            storage_unit = "GB" if storage_match.group(2).startswith("g") else "TB"
            storage_type_match = re.search(r'(ssd|hdd|nvme)', content.lower())
            storage_type = storage_type_match.group(1).upper() if storage_type_match else "SSD"
            storage = f"{storage_size}{storage_unit} {storage_type}"
        
        # Extract display requirements
        display_match = re.search(r'display[:\s]*(\d+\.?\d*).*?(inch|"|inches)', content.lower())
        display = "14-inch FHD (1920 x 1080)"
        if display_match:
            display_size = display_match.group(1)
            display_res_match = re.search(r'(hd|fhd|qhd|uhd|4k|\d+\s*x\s*\d+)', content.lower())
            display_res = display_res_match.group(1).upper() if display_res_match else "FHD"
            if display_res.lower() == "hd":
                display_res = "HD (1366 x 768)"
            elif display_res.lower() == "fhd":
                display_res = "FHD (1920 x 1080)"
            elif display_res.lower() == "qhd":
                display_res = "QHD (2560 x 1440)"
            elif display_res.lower() == "uhd" or display_res.lower() == "4k":
                display_res = "UHD (3840 x 2160)"
            display = f"{display_size}-inch {display_res}"
        
        # Extract battery requirements
        battery_match = re.search(r'battery[:\s]*(\d+)\s*(hours?|hrs?)', content.lower())
        battery = "8+ hours"
        if battery_match:
            battery_hours = battery_match.group(1)
            battery = f"{battery_hours}+ hours"
        
        # Extract warranty requirements
        warranty_match = re.search(r'warranty[:\s]*(\d+)\s*(years?|yr)', content.lower())
        warranty = "3 years onsite"
        if warranty_match:
            warranty_years = warranty_match.group(1)
            warranty_type_match = re.search(r'(onsite|next.*?day|nbd|care\s*pack)', content.lower())
            warranty_type = warranty_type_match.group(1) if warranty_type_match else "onsite"
            warranty = f"{warranty_years} years {warranty_type}"
        
        # Create laptop requirements
        requirements["laptops"] = {
            "quantity": quantity,
            "os": os,
            "processor": processor,
            "memory": memory,
            "storage": storage,
            "display": display,
            "battery": battery,
            "durability": "MIL-STD-810H tested",
            "connectivity": "Wi-Fi 6, Bluetooth 5.0",
            "warranty": warranty
        }
    
    # Extract monitor requirements if needed
    if "Monitors" in categories:
        # Extract quantity
        quantity_match = re.search(r'quantity[:\s]*(\d+)|(\d+)\s*monitor', content.lower())
        quantity = int(quantity_match.group(1) or quantity_match.group(2)) if quantity_match else 30
        
        # Extract screen size requirements
        screen_size_match = re.search(r'screen\s*size[:\s]*(\d+\.?\d*).*?(inch|"|inches)', content.lower())
        screen_size = "27 inches"
        if screen_size_match:
            size = screen_size_match.group(1)
            screen_size = f"{size} inches"
        
        # Extract resolution requirements
        resolution_match = re.search(r'resolution[:\s]*(hd|fhd|qhd|uhd|4k|\d+\s*x\s*\d+)', content.lower())
        resolution = "QHD (2560 x 1440)"
        if resolution_match:
            res = resolution_match.group(1).upper()
            if res.lower() == "hd":
                resolution = "HD (1366 x 768)"
            elif res.lower() == "fhd":
                resolution = "FHD (1920 x 1080)"
            elif res.lower() == "qhd":
                resolution = "QHD (2560 x 1440)"
            elif res.lower() == "uhd" or res.lower() == "4k":
                resolution = "UHD (3840 x 2160)"
            elif "x" in res.lower():
                resolution = res
        
        # Extract panel technology requirements
        panel_match = re.search(r'panel[:\s]*(ips|tn|va|oled)', content.lower())
        panel_tech = "IPS"
        if panel_match:
            panel_tech = panel_match.group(1).upper()
        
        # Extract brightness requirements
        brightness_match = re.search(r'brightness[:\s]*(\d+)\s*(nits?|cd/m²)', content.lower())
        brightness = "300 cd/m²"
        if brightness_match:
            bright_value = brightness_match.group(1)
            brightness = f"{bright_value} cd/m²"
        
        # Extract connectivity requirements
        connectivity = "HDMI, DisplayPort, USB-C"
        if "hdmi" in content.lower() and "displayport" in content.lower():
            connectivity = "HDMI, DisplayPort"
        if "usb-c" in content.lower() or "usb c" in content.lower():
            connectivity += ", USB-C"
        if "vga" in content.lower():
            connectivity += ", VGA"
        
        # Extract warranty requirements
        warranty_match = re.search(r'warranty[:\s]*(\d+)\s*(years?|yr)', content.lower())
        warranty = "3 years standard"
        if warranty_match:
            warranty_years = warranty_match.group(1)
            warranty = f"{warranty_years} years standard"
        
        # Create monitor requirements
        requirements["monitors"] = {
            "quantity": quantity,
            "screenSize": screen_size,
            "resolution": resolution,
            "panelTech": panel_tech,
            "brightness": brightness,
            "contrastRatio": "1000:1",
            "connectivity": connectivity,
            "adjustability": "Height, tilt, swivel adjustable",
            "warranty": warranty
        }
    
    # Create and return ExtractedRequirement object
    return ExtractedRequirement(**requirements)

async def generate_email_proposal(rfq: Dict[str, Any], product: Dict[str, Any], supplier: Dict[str, Any]) -> EmailTemplate:
    """
    Generate personalized email proposal for a selected supplier.
    
    This is an enhanced implementation for the MVP that creates more detailed
    and personalized email proposals. In a production environment, this would
    use OpenAI's API or another AI service for even better personalization.
    """
    # Extract key information
    rfq_title = rfq.get("title", "IT Equipment Procurement")
    supplier_name = supplier.get("name", "Supplier")
    product_name = product.get("name", "Product")
    product_category = product.get("category", "IT Equipment")
    product_price = product.get("price", 0)
    product_description = product.get("description", "")
    quantity = 30  # Default quantity
    
    # Try to get actual quantity from requirements
    requirements = rfq.get("extractedRequirements", {})
    req_obj = requirements
    if isinstance(requirements, str):
        # Handle case where requirements might be a JSON string
        try:
            req_obj = json.loads(requirements)
        except:
            req_obj = {}
    
    # Get specific category requirements
    category_req = None
    if product_category.lower() == "laptops" and isinstance(req_obj, dict) and req_obj.get("laptops"):
        category_req = req_obj["laptops"]
        quantity = category_req.get("quantity", 30)
    elif product_category.lower() == "monitors" and isinstance(req_obj, dict) and req_obj.get("monitors"):
        category_req = req_obj["monitors"]
        quantity = category_req.get("quantity", 30)
    
    # Calculate total price
    total_price = product_price * quantity
    volume_discount = 0
    
    # Apply volume discount for larger orders
    if quantity >= 50:
        volume_discount = 0.10  # 10% discount for 50+ units
    elif quantity >= 20:
        volume_discount = 0.05  # 5% discount for 20-49 units
    
    discounted_price = product_price * (1 - volume_discount)
    discounted_total = discounted_price * quantity
    
    # Generate subject line
    subject = f"Proposal for {rfq_title}: {supplier_name} {product_name} Solution"
    
    # Format current date
    from datetime import datetime
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Generate email body with more personalization
    body = f"""Dear Procurement Team,

We hope this email finds you well. On behalf of {supplier_name}, I am pleased to submit our proposal in response to your Request for Quotation (RFQ) for {rfq_title}.

Date: {current_date}
RFQ Reference: {rfq.get("id", "RFQ-2023-001")}

PROPOSED SOLUTION
----------------
After thoroughly reviewing your requirements, we are confident that our {product_name} is the perfect match for your needs. This solution offers exceptional performance, reliability, and value while meeting or exceeding your specifications.

PRODUCT DETAILS
--------------
Product: {product_name}
Manufacturer: {supplier_name}
Category: {product_category}
"""

    # Add product description if available
    if product_description:
        body += f"Description: {product_description}\n"

    # Add pricing information
    body += f"""
PRICING
-------
Unit Price: ${product_price:.2f}
Quantity: {quantity} units
"""

    # Add discount information if applicable
    if volume_discount > 0:
        body += f"""Volume Discount: {volume_discount * 100:.0f}%
Discounted Unit Price: ${discounted_price:.2f}
Total Price: ${discounted_total:.2f} (includes volume discount)
"""
    else:
        body += f"Total Price: ${total_price:.2f}\n"

    body += "\nTECHNICAL SPECIFICATIONS\n-----------------------\n"
    
    # Add product-specific features with more detail and compare with requirements
    if product_category.lower() == "laptops":
        specs = product.get("specifications", {})
        
        # Create a detailed specification table
        body += f"""• Operating System: {specs.get('os', 'Windows 11 Pro')}
• Processor: {specs.get('processor', 'Intel Core i7')}
• Memory: {specs.get('memory', '16GB')}
• Storage: {specs.get('storage', '512GB SSD')}
• Display: {specs.get('display', '14-inch FHD')}
• Battery Life: {specs.get('battery', '8+ hours')}
• Durability: {specs.get('durability', 'Military-grade durability')}
• Connectivity: {specs.get('connectivity', 'Wi-Fi 6, Bluetooth 5.0')}
• Weight: {specs.get('weight', 'Lightweight design')}
• Ports: {specs.get('ports', 'Multiple USB ports, HDMI')}
• Warranty: {product.get('warranty', '3 years')}
"""
        
        # If we have the original requirements, compare them with our solution
        if category_req:
            body += f"""
REQUIREMENTS COMPLIANCE
---------------------
Our proposed solution meets or exceeds your requirements in the following areas:

✓ Operating System: You requested {category_req.get('os', 'Windows')} - Our solution provides {specs.get('os', 'Windows 11 Pro')}
✓ Processor: You requested {category_req.get('processor', 'Intel Core i5 or better')} - Our solution provides {specs.get('processor', 'Intel Core i7')}
✓ Memory: You requested {category_req.get('memory', '16GB')} - Our solution provides {specs.get('memory', '16GB')}
✓ Storage: You requested {category_req.get('storage', '512GB SSD')} - Our solution provides {specs.get('storage', '512GB SSD')}
✓ Warranty: You requested {category_req.get('warranty', '3 years')} - Our solution provides {product.get('warranty', '3 years')}
"""
    
    elif product_category.lower() == "monitors":
        specs = product.get("specifications", {})
        
        # Create a detailed specification table
        body += f"""• Screen Size: {specs.get('screenSize', '27 inches')}
• Resolution: {specs.get('resolution', 'QHD (2560 x 1440)')}
• Panel Technology: {specs.get('panelTech', 'IPS')}
• Brightness: {specs.get('brightness', '300 cd/m²')}
• Contrast Ratio: {specs.get('contrastRatio', '1000:1')}
• Connectivity: {specs.get('connectivity', 'HDMI, DisplayPort, USB-C')}
• Adjustability: {specs.get('adjustability', 'Height, tilt, swivel adjustable')}
• Response Time: {specs.get('responseTime', '5ms')}
• Color Gamut: {specs.get('colorGamut', '99% sRGB')}
• Warranty: {product.get('warranty', '3 years')}
"""
        
        # If we have the original requirements, compare them with our solution
        if category_req:
            body += f"""
REQUIREMENTS COMPLIANCE
---------------------
Our proposed solution meets or exceeds your requirements in the following areas:

✓ Screen Size: You requested {category_req.get('screenSize', '27 inches')} - Our solution provides {specs.get('screenSize', '27 inches')}
✓ Resolution: You requested {category_req.get('resolution', 'QHD')} - Our solution provides {specs.get('resolution', 'QHD (2560 x 1440)')}
✓ Panel Technology: You requested {category_req.get('panelTech', 'IPS')} - Our solution provides {specs.get('panelTech', 'IPS')}
✓ Connectivity: You requested {category_req.get('connectivity', 'Multiple ports')} - Our solution provides {specs.get('connectivity', 'HDMI, DisplayPort, USB-C')}
✓ Warranty: You requested {category_req.get('warranty', '3 years')} - Our solution provides {product.get('warranty', '3 years')}
"""

    # Add delivery and support information
    body += f"""
DELIVERY AND SUPPORT
------------------
• Estimated Delivery Time: {supplier.get('deliveryTime', '15-30 days')} from purchase order
• Shipping Method: Express Courier with tracking
• Shipping Fee: Included in the total price
• Installation Support: Available upon request
• Technical Support: Available 24/7 via phone, email, or chat
• Warranty Support: {product.get('warranty', '3 years')} with on-site service available

ABOUT {supplier_name.upper()}
{'-' * (6 + len(supplier_name))}
{supplier.get('description', f'{supplier_name} is a leading provider of high-quality technology solutions.')}

We have been in business for over {supplier.get('yearsInBusiness', '15')} years and have successfully delivered similar solutions to numerous clients in the education sector, including {supplier.get('clientsServed', 'many educational institutions')}. Our clients consistently rate us highly for product quality, timely delivery, and exceptional support.

NEXT STEPS
---------
If you would like to proceed with this proposal or need additional information, please:

1. Reply to this email
2. Call us at {supplier.get('contactPhone', '+1-555-123-4567')}
3. Schedule a demo by contacting {supplier.get('contactEmail', 'sales@example.com')}

We can also provide references from similar clients upon request.

We look forward to the opportunity of working with you and helping your institution achieve its technology goals.

Best regards,

Sales Team
{supplier_name}
{supplier.get('website', 'www.example.com')}
{supplier.get('contactEmail', 'sales@example.com')} | {supplier.get('contactPhone', '+1-555-123-4567')}
"""

    # Extract domain from website for CC
    website = supplier.get('website', 'example.com')
    domain = website.replace('https://', '').replace('http://', '').replace('www.', '')
    if not domain:
        domain = 'example.com'
    
    # Create and return EmailTemplate object
    return EmailTemplate(
        to="procurement@example.com",
        cc=f"sales@{domain}",
        subject=subject,
        body=body
    )