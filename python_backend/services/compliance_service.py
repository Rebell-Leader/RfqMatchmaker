"""
Compliance service for AI hardware procurement platform.

This module provides functionality to check compliance with export regulations
and other regulatory requirements for AI hardware procurement.
"""

import os
import json
import logging
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

# Geopolitical restrictions - major countries and their restrictions
COUNTRY_RESTRICTIONS = {
    "United States": {
        "restricted_countries": [
            "Russia", "Belarus", "Iran", "Syria", "North Korea", "Cuba", "Crimea"
        ],
        "partially_restricted": [
            "China", "Venezuela", "Myanmar", "Afghanistan"
        ],
        "restricted_products": [
            "High-performance GPUs", "AI accelerators with >32GB memory", 
            "Products with >800 GB/s memory bandwidth"
        ]
    },
    "China": {
        "restricted_countries": [
            "Taiwan"
        ],
        "partially_restricted": [],
        "restricted_products": []
    },
    "European Union": {
        "restricted_countries": [
            "Russia", "Belarus", "Iran", "Syria", "North Korea"
        ],
        "partially_restricted": [],
        "restricted_products": [
            "Dual-use technologies including high-performance computing"
        ]
    }
}

# Product restriction thresholds
GPU_RESTRICTION_THRESHOLDS = {
    "memory_capacity": 32,  # GB
    "memory_bandwidth": 800,  # GB/s
    "fp32_performance": 50,  # TFLOPS
    "int8_performance": 400  # TOPS
}

class ComplianceService:
    """Service for checking compliance with export regulations."""
    
    def __init__(self):
        """Initialize the compliance service."""
        self.country_domain_map = self._load_country_domain_map()
        self.sanctions_lists = self._load_sanctions_lists()
    
    def _load_country_domain_map(self) -> Dict[str, str]:
        """
        Load mapping of country codes to domain extensions.
        
        Returns:
            Dictionary mapping country codes to domain extensions
        """
        # Basic mapping of some common country codes to country names
        return {
            "ru": "Russia",
            "cn": "China",
            "us": "United States",
            "uk": "United Kingdom",
            "de": "Germany",
            "fr": "France",
            "it": "Italy",
            "jp": "Japan",
            "kr": "South Korea",
            "in": "India",
            "br": "Brazil",
            "za": "South Africa",
            "au": "Australia",
            "ca": "Canada",
            "eu": "European Union"
        }
    
    def _load_sanctions_lists(self) -> Dict[str, List[str]]:
        """
        Load sanctions lists for different jurisdictions.
        
        Returns:
            Dictionary mapping jurisdiction to list of sanctioned entities
        """
        # This would ideally load from official sources or APIs
        # For the MVP, using a simple hardcoded list of examples
        return {
            "US": [
                "Huawei Technologies Co., Ltd.",
                "Semiconductor Manufacturing International Corporation",
                "SenseTime Group Limited"
            ],
            "EU": [
                "Tianjin Phytium Information Technology",
                "Hangzhou Hikvision Digital Technology Co., Ltd."
            ],
            "UK": [
                "Moscow Center of SPARC Technologies",
                "Central Research Institute of Machine Building"
            ]
        }
    
    def detect_country_from_website(self, website_url: str) -> Optional[str]:
        """
        Detect the country of a company based on its website domain.
        
        Args:
            website_url: URL of the company website
            
        Returns:
            Country name if detected, None otherwise
        """
        try:
            # Extract domain and TLD
            domain_parts = website_url.lower().split('/')[-1].split('.')
            if len(domain_parts) >= 2:
                tld = domain_parts[-1]
                
                # Check if TLD is a country code
                if tld in self.country_domain_map:
                    return self.country_domain_map[tld]
                
                # For .com, .org, etc., try to extract country information from the website content
                if tld in ['com', 'org', 'net', 'info']:
                    return self._extract_country_from_content(website_url)
            
            return None
        except Exception as e:
            logger.error(f"Error detecting country from website {website_url}: {str(e)}")
            return None
    
    def _extract_country_from_content(self, website_url: str) -> Optional[str]:
        """
        Extract country information from website content.
        
        Args:
            website_url: URL of the company website
            
        Returns:
            Country name if found, None otherwise
        """
        try:
            response = requests.get(website_url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for country mentions in common locations
            # 1. Check meta tags
            meta_tags = soup.find_all('meta')
            for tag in meta_tags:
                content = tag.get('content', '').lower()
                for country_code, country_name in self.country_domain_map.items():
                    if country_name.lower() in content:
                        return country_name
            
            # 2. Check footer text (common location for addresses)
            footer = soup.find('footer')
            if footer:
                footer_text = footer.get_text().lower()
                for country_code, country_name in self.country_domain_map.items():
                    if country_name.lower() in footer_text:
                        return country_name
            
            # 3. Check contact/about page links
            contact_links = soup.find_all('a', href=re.compile(r'contact|about|location', re.I))
            for link in contact_links:
                href = link.get('href', '')
                if href and not href.startswith(('http', 'www')):
                    # Construct absolute URL
                    if not href.startswith('/'):
                        href = '/' + href
                    contact_url = website_url.rstrip('/') + href
                    
                    # Try to extract country from contact page
                    try:
                        contact_response = requests.get(contact_url, headers=HEADERS, timeout=10)
                        contact_soup = BeautifulSoup(contact_response.text, 'html.parser')
                        contact_text = contact_soup.get_text().lower()
                        
                        for country_code, country_name in self.country_domain_map.items():
                            if country_name.lower() in contact_text:
                                return country_name
                    except:
                        # Skip if contact page access fails
                        pass
            
            return None
        except Exception as e:
            logger.error(f"Error extracting country from website content {website_url}: {str(e)}")
            return None
    
    def check_sanctions_list(self, company_name: str) -> List[str]:
        """
        Check if a company is on any sanctions list.
        
        Args:
            company_name: Name of the company to check
            
        Returns:
            List of jurisdictions where the company is sanctioned
        """
        sanctioned_by = []
        company_name_lower = company_name.lower()
        
        for jurisdiction, sanctioned_entities in self.sanctions_lists.items():
            for entity in sanctioned_entities:
                if entity.lower() in company_name_lower or company_name_lower in entity.lower():
                    sanctioned_by.append(jurisdiction)
                    break
        
        return sanctioned_by
    
    def check_export_compliance(
        self, 
        buyer_country: str, 
        supplier_country: str, 
        product_specs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check export compliance for a specific buyer-supplier-product combination.
        
        Args:
            buyer_country: Country of the buyer
            supplier_country: Country of the supplier
            product_specs: Specifications of the product
            
        Returns:
            Dictionary with compliance information
        """
        result = {
            "is_compliant": True,
            "restrictions": [],
            "warnings": [],
            "alternative_sources": []
        }
        
        # Check country-level restrictions
        for regulator, restrictions in COUNTRY_RESTRICTIONS.items():
            # Check if supplier is from a restricted country for the buyer
            if supplier_country in restrictions["restricted_countries"]:
                result["is_compliant"] = False
                result["restrictions"].append(
                    f"Supplier from {supplier_country} is restricted for buyers in {buyer_country} under {regulator} regulations"
                )
            
            # Check if supplier is from a partially restricted country
            if supplier_country in restrictions["partially_restricted"]:
                result["warnings"].append(
                    f"Supplier from {supplier_country} is partially restricted for buyers in {buyer_country} under {regulator} regulations. Additional licensing may be required."
                )
        
        # Check product-specific restrictions
        compute_specs = product_specs.get("computeSpecs", {})
        memory_specs = product_specs.get("memorySpecs", {})
        
        # Check memory capacity restrictions
        if memory_specs.get("capacity", 0) >= GPU_RESTRICTION_THRESHOLDS["memory_capacity"]:
            result["warnings"].append(
                f"Product has {memory_specs.get('capacity')}GB memory, which exceeds the {GPU_RESTRICTION_THRESHOLDS['memory_capacity']}GB threshold for unrestricted export"
            )
        
        # Check memory bandwidth restrictions
        if memory_specs.get("bandwidth", 0) >= GPU_RESTRICTION_THRESHOLDS["memory_bandwidth"]:
            result["warnings"].append(
                f"Product has {memory_specs.get('bandwidth')}GB/s memory bandwidth, which exceeds the {GPU_RESTRICTION_THRESHOLDS['memory_bandwidth']}GB/s threshold for unrestricted export"
            )
        
        # Check computational performance restrictions
        if compute_specs.get("fp32Performance", 0) >= GPU_RESTRICTION_THRESHOLDS["fp32_performance"]:
            result["warnings"].append(
                f"Product has {compute_specs.get('fp32Performance')}TFLOPS FP32 performance, which exceeds the {GPU_RESTRICTION_THRESHOLDS['fp32_performance']}TFLOPS threshold for unrestricted export"
            )
        
        # Check INT8 performance restrictions
        if compute_specs.get("int8Performance", 0) >= GPU_RESTRICTION_THRESHOLDS["int8_performance"]:
            result["warnings"].append(
                f"Product has {compute_specs.get('int8Performance')}TOPS INT8 performance, which exceeds the {GPU_RESTRICTION_THRESHOLDS['int8_performance']}TOPS threshold for unrestricted export"
            )
        
        # Suggest alternative sources if there are compliance issues
        if not result["is_compliant"] or result["warnings"]:
            # Suggest alternatives based on the current compliance issues
            if "United States" in supplier_country and "China" in buyer_country:
                result["alternative_sources"].append("Local Chinese vendors like Huawei, Alibaba, or Baidu")
            elif "China" in supplier_country and "United States" in buyer_country:
                result["alternative_sources"].append("US-based vendors like NVIDIA, AMD, or Intel")
            
            # If high-performance GPUs are restricted, suggest alternatives
            if any("performance" in warning for warning in result["warnings"]):
                result["alternative_sources"].append("Consider cloud-based AI services instead of hardware purchase")
                result["alternative_sources"].append("Split workload across multiple lower-spec devices")
        
        return result
    
    def generate_compliance_report(
        self, 
        buyer: Dict[str, Any], 
        supplier: Dict[str, Any], 
        product: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive compliance report for a transaction.
        
        Args:
            buyer: Buyer information including country
            supplier: Supplier information including country
            product: Product information including specifications
            
        Returns:
            Dictionary with detailed compliance report
        """
        buyer_country = buyer.get("country", "Unknown")
        supplier_country = supplier.get("country", "Unknown")
        
        # If supplier country is unknown, try to detect from website
        if supplier_country == "Unknown" and supplier.get("website"):
            detected_country = self.detect_country_from_website(supplier["website"])
            if detected_country:
                supplier_country = detected_country
        
        # Check sanctions lists
        sanctions = self.check_sanctions_list(supplier.get("name", ""))
        
        # Check export compliance
        compliance_info = self.check_export_compliance(
            buyer_country,
            supplier_country,
            product
        )
        
        # Build the report
        report = {
            "transaction_date": datetime.now().isoformat(),
            "buyer": {
                "name": buyer.get("company", "Unknown"),
                "country": buyer_country
            },
            "supplier": {
                "name": supplier.get("name", "Unknown"),
                "country": supplier_country,
                "sanctions": sanctions
            },
            "product": {
                "name": product.get("name", "Unknown"),
                "category": product.get("category", "Unknown"),
                "type": product.get("type", "Unknown"),
                "high_performance": self._is_high_performance_product(product)
            },
            "compliance_result": compliance_info,
            "overall_risk_level": self._calculate_risk_level(compliance_info, sanctions),
            "required_actions": self._determine_required_actions(compliance_info, sanctions)
        }
        
        return report
    
    def _is_high_performance_product(self, product: Dict[str, Any]) -> bool:
        """
        Determine if a product is considered high-performance under export regulations.
        
        Args:
            product: Product information including specifications
            
        Returns:
            Boolean indicating if the product is high-performance
        """
        compute_specs = product.get("computeSpecs", {})
        memory_specs = product.get("memorySpecs", {})
        
        # Check against thresholds
        if (memory_specs.get("capacity", 0) >= GPU_RESTRICTION_THRESHOLDS["memory_capacity"] or
            memory_specs.get("bandwidth", 0) >= GPU_RESTRICTION_THRESHOLDS["memory_bandwidth"] or
            compute_specs.get("fp32Performance", 0) >= GPU_RESTRICTION_THRESHOLDS["fp32_performance"] or
            compute_specs.get("int8Performance", 0) >= GPU_RESTRICTION_THRESHOLDS["int8_performance"]):
            return True
        
        return False
    
    def _calculate_risk_level(self, compliance_info: Dict[str, Any], sanctions: List[str]) -> str:
        """
        Calculate overall risk level for a transaction.
        
        Args:
            compliance_info: Compliance check results
            sanctions: List of jurisdictions where supplier is sanctioned
            
        Returns:
            Risk level as string (Low, Medium, High, Critical)
        """
        if not compliance_info["is_compliant"]:
            return "Critical"
        
        if sanctions:
            return "High"
        
        if compliance_info["warnings"]:
            return "Medium"
        
        return "Low"
    
    def _determine_required_actions(self, compliance_info: Dict[str, Any], sanctions: List[str]) -> List[str]:
        """
        Determine required actions based on compliance results.
        
        Args:
            compliance_info: Compliance check results
            sanctions: List of jurisdictions where supplier is sanctioned
            
        Returns:
            List of required actions
        """
        actions = []
        
        if not compliance_info["is_compliant"]:
            actions.append("Transaction cannot proceed due to compliance restrictions")
            actions.append("Consider alternative suppliers from allowed countries")
        
        if sanctions:
            actions.append(f"Supplier is on sanctions lists for the following jurisdictions: {', '.join(sanctions)}")
            actions.append("Conduct enhanced due diligence before proceeding")
        
        if compliance_info["warnings"]:
            actions.append("Obtain export license before proceeding")
            actions.append("Consult with legal counsel specializing in export controls")
        
        if not actions:
            actions.append("No compliance issues detected, transaction can proceed normally")
        
        return actions
    
    def check_buyer_compliance(self, buyer_website: str) -> Dict[str, Any]:
        """
        Check compliance status of a potential buyer based on their website.
        
        Args:
            buyer_website: Website URL of the buyer
            
        Returns:
            Dictionary with buyer compliance information
        """
        result = {
            "country": "Unknown",
            "sanctions": [],
            "risk_level": "Medium",  # Default to medium if we can't determine
            "is_compliant": True,
            "notes": []
        }
        
        # Detect country from website
        country = self.detect_country_from_website(buyer_website)
        if country:
            result["country"] = country
            result["notes"].append(f"Detected buyer country: {country}")
        else:
            result["notes"].append("Could not detect buyer country from website")
        
        # Extract company name from website
        company_name = self._extract_company_name(buyer_website)
        if company_name:
            result["company_name"] = company_name
            
            # Check sanctions
            sanctions = self.check_sanctions_list(company_name)
            if sanctions:
                result["sanctions"] = sanctions
                result["is_compliant"] = False
                result["risk_level"] = "High"
                result["notes"].append(f"Company appears on {', '.join(sanctions)} sanctions lists")
        
        # Check if the country is under broad restrictions
        if result["country"] in ["Russia", "Belarus", "Iran", "Syria", "North Korea", "Cuba", "Crimea"]:
            result["is_compliant"] = False
            result["risk_level"] = "Critical"
            result["notes"].append(f"Buyer country ({result['country']}) is under broad export restrictions")
        
        # Set final risk level
        if result["risk_level"] != "Critical" and result["is_compliant"]:
            if result["country"] == "Unknown":
                result["risk_level"] = "Medium"
                result["notes"].append("Unable to fully verify compliance due to limited information")
            else:
                result["risk_level"] = "Low"
                result["notes"].append("No compliance issues detected")
        
        return result
    
    def _extract_company_name(self, website_url: str) -> Optional[str]:
        """
        Extract company name from website.
        
        Args:
            website_url: URL of the company website
            
        Returns:
            Company name if found, None otherwise
        """
        try:
            response = requests.get(website_url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try different approaches to extract company name
            
            # 1. Look for title tag
            title = soup.title.string if soup.title else None
            if title:
                # Remove common title suffixes like "- Home", "| Official Website"
                cleaned_title = re.sub(r'\s*[-|]\s*.*$', '', title.strip())
                if cleaned_title:
                    return cleaned_title
            
            # 2. Look for logo alt text
            logo = soup.find('img', alt=True)
            if logo and logo.get('alt') and len(logo.get('alt')) > 1:
                return logo.get('alt')
            
            # 3. Look for company name in meta tags
            meta_tags = soup.find_all('meta')
            for tag in meta_tags:
                if tag.get('property') in ['og:site_name', 'og:title']:
                    return tag.get('content')
            
            # 4. Extract from domain name
            domain = website_url.lower().split('//')[-1].split('/')[0]
            domain_parts = domain.split('.')
            if len(domain_parts) >= 2:
                # Remove common TLDs and www
                if domain_parts[0] == 'www':
                    domain_parts.pop(0)
                if domain_parts[-1] in ['com', 'org', 'net', 'io', 'co']:
                    domain_parts.pop()
                return domain_parts[0].capitalize()
            
            return None
        except Exception as e:
            logger.error(f"Error extracting company name from website {website_url}: {str(e)}")
            return None


def check_product_shipping_restrictions(product_specs: Dict[str, Any], destination_country: str) -> Dict[str, Any]:
    """
    Check shipping restrictions for a specific product to a destination country.
    
    Args:
        product_specs: Product specifications
        destination_country: Destination country for shipping
        
    Returns:
        Dictionary with shipping restriction information
    """
    result = {
        "can_ship": True,
        "restrictions": [],
        "requires_license": False,
        "required_documents": []
    }
    
    # Product compliance info
    compliance_info = product_specs.get("complianceInfo", {})
    restricted_countries = compliance_info.get("restrictedCountries", [])
    
    # Check if destination is in restricted countries list
    if destination_country in restricted_countries:
        result["can_ship"] = False
        result["restrictions"].append(f"Product cannot be shipped to {destination_country} due to manufacturer restrictions")
    
    # Check for export restrictions
    export_restrictions = compliance_info.get("exportRestrictions", [])
    if export_restrictions:
        # If there are export restrictions and destination is a sensitive country
        sensitive_countries = [
            "China", "Russia", "Iran", "Belarus", "North Korea", 
            "Syria", "Venezuela", "Cuba", "Myanmar", "Afghanistan"
        ]
        
        if destination_country in sensitive_countries:
            result["requires_license"] = True
            result["required_documents"].append("Export license from origin country")
            result["required_documents"].append("End-user certificate")
            result["required_documents"].append("Statement of end use")
            
            if not result["restrictions"]:
                result["restrictions"].append(
                    f"Product requires export license for shipping to {destination_country}"
                )
    
    # Check if product is high-performance
    is_high_performance = False
    compute_specs = product_specs.get("computeSpecs", {})
    memory_specs = product_specs.get("memorySpecs", {})
    
    if (memory_specs.get("capacity", 0) >= GPU_RESTRICTION_THRESHOLDS["memory_capacity"] or
        memory_specs.get("bandwidth", 0) >= GPU_RESTRICTION_THRESHOLDS["memory_bandwidth"] or
        compute_specs.get("fp32Performance", 0) >= GPU_RESTRICTION_THRESHOLDS["fp32_performance"] or
        compute_specs.get("int8Performance", 0) >= GPU_RESTRICTION_THRESHOLDS["int8_performance"]):
        is_high_performance = True
    
    if is_high_performance:
        # High-performance products have additional restrictions
        if not result["requires_license"]:
            result["requires_license"] = True
            result["required_documents"].append("Export license from origin country")
            result["required_documents"].append("End-user certificate")
        
        if destination_country in ["China", "Russia", "Iran", "Belarus", "North Korea", "Syria"]:
            result["can_ship"] = False
            result["restrictions"].append(
                f"High-performance AI hardware cannot be shipped to {destination_country} under current regulations"
            )
    
    return result


if __name__ == "__main__":
    # For testing purposes
    service = ComplianceService()
    print(service.check_buyer_compliance("https://www.example.com"))
    
    # Test product shipping restrictions
    sample_product = {
        "name": "NVIDIA A100 80GB PCIe",
        "manufacturer": "NVIDIA",
        "computeSpecs": {
            "fp32Performance": 19.5,
            "tensorCores": 432
        },
        "memorySpecs": {
            "capacity": 80,
            "bandwidth": 2039
        },
        "complianceInfo": {
            "exportRestrictions": ["Restricted under US export regulations"],
            "restrictedCountries": ["Russia", "Iran", "North Korea", "Cuba", "Syria"]
        }
    }
    
    print(check_product_shipping_restrictions(sample_product, "China"))
    print(check_product_shipping_restrictions(sample_product, "Russia"))