"""
Product Scraper for AI hardware procurement platform.

This module provides functionality to scrape product information from
various manufacturer and supplier websites, focusing on GPUs and AI accelerators.
"""

import os
import json
import logging
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base URLs for different manufacturers
NVIDIA_BASE_URL = "https://www.nvidia.com"
NVIDIA_PRODUCTS_URL = f"{NVIDIA_BASE_URL}/en-us/data-center/products//"
AMD_BASE_URL = "https://www.amd.com"
AMD_PRODUCTS_URL = f"{AMD_BASE_URL}/en/products/graphics/server-accelerators"

# Headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

class ProductScraper:
    """Base class for product scrapers."""
    
    def __init__(self):
        """Initialize the scraper."""
        self.products = []
        self.errors = []
    
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch a web page and return its BeautifulSoup object.
        
        Args:
            url: The URL to fetch
            
        Returns:
            BeautifulSoup object if successful, None otherwise
        """
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            self.errors.append(f"Failed to fetch {url}: {str(e)}")
            return None
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: The text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove special characters
        text = re.sub(r'[^\w\s.,-]', '', text)
        return text.strip()
    
    def extract_number(self, text: str) -> Optional[float]:
        """
        Extract a number from a string.
        
        Args:
            text: String containing a number
            
        Returns:
            Extracted number as float, or None if not found
        """
        if not text:
            return None
            
        match = re.search(r'(\d+\.?\d*)', text)
        if match:
            return float(match.group(1))
        return None
    
    def save_products(self, filename: str) -> None:
        """
        Save scraped products to a JSON file.
        
        Args:
            filename: The name of the file to save to
        """
        if not self.products:
            logger.warning("No products to save")
            return
            
        try:
            output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
            os.makedirs(output_dir, exist_ok=True)
            
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w') as f:
                json.dump({
                    'products': self.products,
                    'errors': self.errors,
                    'scraped_at': datetime.now().isoformat()
                }, f, indent=2)
            
            logger.info(f"Saved {len(self.products)} products to {filepath}")
        except Exception as e:
            logger.error(f"Error saving products: {str(e)}")


class NvidiaProductScraper(ProductScraper):
    """Scraper for NVIDIA GPU products."""
    
    def __init__(self):
        """Initialize the NVIDIA scraper."""
        super().__init__()
        self.product_urls = []
    
    def get_all_product_urls(self) -> List[str]:
        """
        Get URLs for all NVIDIA data center GPU products.
        
        Returns:
            List of product URLs
        """
        soup = self.get_page(NVIDIA_PRODUCTS_URL)
        if not soup:
            return []
        
        product_urls = []
        
        # For each product card/link on the page
        for link in soup.select('a[href*="/data-center/products/"]'):
            url = link.get('href')
            if url and 'gpu' in url.lower() and url != NVIDIA_PRODUCTS_URL:
                # Ensure it's an absolute URL
                if not url.startswith('http'):
                    url = NVIDIA_BASE_URL + url
                product_urls.append(url)
        
        # Remove duplicates while preserving order
        seen = set()
        self.product_urls = [url for url in product_urls if not (url in seen or seen.add(url))]
        
        logger.info(f"Found {len(self.product_urls)} NVIDIA product URLs")
        return self.product_urls
    
    def extract_product_info(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract product information from a product page.
        
        Args:
            url: The URL of the product page
            
        Returns:
            Dictionary containing product information
        """
        soup = self.get_page(url)
        if not soup:
            return None
        
        # Initialize product data with default values
        product = {
            "name": "",
            "manufacturer": "NVIDIA",
            "category": "GPU",
            "type": "GPU",
            "description": "",
            "specifications": {},
            "price": 0,  # Price typically not available on manufacturer sites
            "warranty": "Standard manufacturer warranty",
            "dataSourceUrl": url,
            "lastPriceUpdate": datetime.now().isoformat(),
            "computeSpecs": {},
            "memorySpecs": {},
            "powerConsumption": {},
            "supportedFrameworks": [],
            "architecture": "",
            "complianceInfo": {},
            "inStock": True,  # Default, actual availability would come from suppliers
            "model": ""
        }
        
        # Extract product name
        try:
            name_elem = soup.select_one('h1')
            if name_elem:
                product["name"] = self.clean_text(name_elem.text)
                # Extract model number from name
                if "NVIDIA" in product["name"]:
                    model_match = re.search(r'NVIDIA\s+([A-Z0-9-]+)', product["name"])
                    if model_match:
                        product["model"] = model_match.group(1)
        except Exception as e:
            logger.error(f"Error extracting product name from {url}: {str(e)}")
        
        # Extract product description
        try:
            desc_elem = soup.select_one('meta[name="description"]')
            if desc_elem:
                product["description"] = self.clean_text(desc_elem.get('content', ''))
        except Exception as e:
            logger.error(f"Error extracting product description from {url}: {str(e)}")
        
        # Extract specifications
        try:
            spec_tables = soup.select('table.specs-table')
            for table in spec_tables:
                rows = table.select('tr')
                for row in rows:
                    cells = row.select('td')
                    if len(cells) >= 2:
                        key = self.clean_text(cells[0].text)
                        value = self.clean_text(cells[1].text)
                        if key and value:
                            product["specifications"][key] = value
                            
                            # Extract architecture
                            if 'architecture' in key.lower():
                                product["architecture"] = value
                            
                            # Extract compute performance
                            elif 'cuda cores' in key.lower():
                                product["computeSpecs"]["cudaCores"] = self.extract_number(value)
                            elif 'tensor cores' in key.lower():
                                product["computeSpecs"]["tensorCores"] = self.extract_number(value)
                            elif 'fp32' in key.lower() and 'performance' in key.lower():
                                product["computeSpecs"]["fp32Performance"] = self.extract_number(value)
                            elif 'fp16' in key.lower() and 'performance' in key.lower():
                                product["computeSpecs"]["fp16Performance"] = self.extract_number(value)
                            elif 'int8' in key.lower() and 'performance' in key.lower():
                                product["computeSpecs"]["int8Performance"] = self.extract_number(value)
                            elif 'clock' in key.lower():
                                product["computeSpecs"]["clockSpeed"] = self.extract_number(value)
                            
                            # Extract memory specifications
                            elif 'memory' in key.lower() and 'size' in key.lower():
                                memory_size = self.extract_number(value)
                                if memory_size:
                                    product["memorySpecs"]["capacity"] = memory_size
                            elif 'memory' in key.lower() and 'bandwidth' in key.lower():
                                bandwidth = self.extract_number(value)
                                if bandwidth:
                                    product["memorySpecs"]["bandwidth"] = bandwidth
                            elif 'memory' in key.lower() and 'type' in key.lower():
                                product["memorySpecs"]["type"] = value
                            elif 'memory' in key.lower() and 'bus' in key.lower():
                                bus_width = self.extract_number(value)
                                if bus_width:
                                    product["memorySpecs"]["busWidth"] = bus_width
                            elif 'ecc' in key.lower():
                                product["memorySpecs"]["eccSupport"] = 'yes' in value.lower()
                            
                            # Extract power consumption
                            elif 'tdp' in key.lower() or 'power' in key.lower():
                                tdp = self.extract_number(value)
                                if tdp:
                                    product["powerConsumption"]["tdp"] = tdp
        except Exception as e:
            logger.error(f"Error extracting specifications from {url}: {str(e)}")
        
        # Extract supported frameworks
        try:
            frameworks = []
            frameworks_section = soup.select_one('section:contains("frameworks")')
            if frameworks_section:
                framework_items = frameworks_section.select('li')
                for item in framework_items:
                    framework = self.clean_text(item.text)
                    if framework:
                        frameworks.append(framework)
            
            if frameworks:
                product["supportedFrameworks"] = frameworks
            else:
                # Default frameworks supported by NVIDIA
                product["supportedFrameworks"] = [
                    "TensorFlow", "PyTorch", "CUDA", "RAPIDS", "TensorRT"
                ]
        except Exception as e:
            logger.error(f"Error extracting frameworks from {url}: {str(e)}")
        
        # Set defaults for required fields if not found
        if not product["memorySpecs"]:
            product["memorySpecs"] = {
                "capacity": 0,
                "bandwidth": 0,
                "type": "Unknown",
                "busWidth": 0
            }
            
        if not product["powerConsumption"]:
            product["powerConsumption"] = {
                "tdp": 0
            }
            
        return product
    
    def scrape_products(self) -> List[Dict[str, Any]]:
        """
        Scrape all NVIDIA GPU products.
        
        Returns:
            List of product dictionaries
        """
        if not self.product_urls:
            self.get_all_product_urls()
        
        for url in self.product_urls:
            logger.info(f"Scraping product from {url}")
            product_info = self.extract_product_info(url)
            if product_info:
                self.products.append(product_info)
        
        return self.products


class AmdProductScraper(ProductScraper):
    """Scraper for AMD GPU products."""
    
    def __init__(self):
        """Initialize the AMD scraper."""
        super().__init__()
        self.product_urls = []
    
    def get_all_product_urls(self) -> List[str]:
        """
        Get URLs for all AMD data center GPU products.
        
        Returns:
            List of product URLs
        """
        soup = self.get_page(AMD_PRODUCTS_URL)
        if not soup:
            return []
        
        product_urls = []
        
        # This is a placeholder - actual implementation would need to be
        # customized to AMD's website structure
        for link in soup.select('a[href*="/products/graphics/"]'):
            url = link.get('href')
            if url and ('server' in url.lower() or 'data-center' in url.lower()):
                # Ensure it's an absolute URL
                if not url.startswith('http'):
                    url = AMD_BASE_URL + url
                product_urls.append(url)
        
        # Remove duplicates while preserving order
        seen = set()
        self.product_urls = [url for url in product_urls if not (url in seen or seen.add(url))]
        
        logger.info(f"Found {len(self.product_urls)} AMD product URLs")
        return self.product_urls
    
    def extract_product_info(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract product information from a product page.
        
        Args:
            url: The URL of the product page
            
        Returns:
            Dictionary containing product information
        """
        # This is a placeholder - actual implementation would need to be
        # customized to AMD's website structure
        soup = self.get_page(url)
        if not soup:
            return None
        
        # Initialize product data with default values
        product = {
            "name": "",
            "manufacturer": "AMD",
            "category": "GPU",
            "type": "GPU",
            "description": "",
            "specifications": {},
            "price": 0,
            "warranty": "Standard manufacturer warranty",
            "dataSourceUrl": url,
            "lastPriceUpdate": datetime.now().isoformat(),
            "computeSpecs": {},
            "memorySpecs": {},
            "powerConsumption": {},
            "supportedFrameworks": [],
            "architecture": "",
            "complianceInfo": {},
            "inStock": True,
            "model": ""
        }
        
        # Implementation would extract data from AMD's website
        # This is just a placeholder
        
        return product
    
    def scrape_products(self) -> List[Dict[str, Any]]:
        """
        Scrape all AMD GPU products.
        
        Returns:
            List of product dictionaries
        """
        if not self.product_urls:
            self.get_all_product_urls()
        
        for url in self.product_urls:
            logger.info(f"Scraping product from {url}")
            product_info = self.extract_product_info(url)
            if product_info:
                self.products.append(product_info)
        
        return self.products


def scrape_all_products() -> Dict[str, List[Dict[str, Any]]]:
    """
    Scrape products from all supported manufacturers.
    
    Returns:
        Dictionary with manufacturer names as keys and lists of products as values
    """
    all_products = {}
    
    # NVIDIA products
    try:
        nvidia_scraper = NvidiaProductScraper()
        nvidia_products = nvidia_scraper.scrape_products()
        nvidia_scraper.save_products("nvidia_products.json")
        all_products["NVIDIA"] = nvidia_products
    except Exception as e:
        logger.error(f"Error scraping NVIDIA products: {str(e)}")
        all_products["NVIDIA"] = []
    
    # AMD products
    try:
        amd_scraper = AmdProductScraper()
        amd_products = amd_scraper.scrape_products()
        amd_scraper.save_products("amd_products.json")
        all_products["AMD"] = amd_products
    except Exception as e:
        logger.error(f"Error scraping AMD products: {str(e)}")
        all_products["AMD"] = []
    
    # Save combined products
    try:
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, "all_products.json")
        with open(filepath, 'w') as f:
            json.dump({
                'products': [p for mfg_products in all_products.values() for p in mfg_products],
                'scraped_at': datetime.now().isoformat()
            }, f, indent=2)
        
        total_products = sum(len(products) for products in all_products.values())
        logger.info(f"Saved {total_products} products to {filepath}")
    except Exception as e:
        logger.error(f"Error saving combined products: {str(e)}")
    
    return all_products


# Function to manually add sample GPU products when scraping isn't possible
def create_sample_gpu_products() -> List[Dict[str, Any]]:
    """
    Create sample GPU product data for testing.
    
    Returns:
        List of sample GPU product dictionaries
    """
    current_time = datetime.now().isoformat()
    
    return [
        {
            "name": "NVIDIA A100 80GB PCIe",
            "manufacturer": "NVIDIA",
            "category": "GPU",
            "type": "GPU",
            "model": "A100",
            "description": "The NVIDIA A100 Tensor Core GPU delivers unprecedented acceleration at every scale for AI, data analytics, and high-performance computing.",
            "specifications": {
                "CUDA Cores": "6912",
                "Tensor Cores": "432",
                "Memory Size": "80 GB HBM2e",
                "Memory Bandwidth": "2039 GB/s",
                "TDP": "300 W"
            },
            "price": 10000.00,  # Estimated price
            "warranty": "3 years",
            "dataSourceUrl": "https://www.nvidia.com/en-us/data-center/a100/",
            "lastPriceUpdate": current_time,
            "computeSpecs": {
                "cudaCores": 6912,
                "tensorCores": 432,
                "fp32Performance": 19.5,  # TFLOPS
                "fp16Performance": 312,   # TFLOPS with sparsity
                "int8Performance": 624    # TOPS with sparsity
            },
            "memorySpecs": {
                "capacity": 80,
                "type": "HBM2e",
                "bandwidth": 2039,
                "busWidth": 5120,
                "eccSupport": True
            },
            "powerConsumption": {
                "tdp": 300,
                "requiredPsu": 800
            },
            "architecture": "Ampere",
            "supportedFrameworks": [
                "TensorFlow", "PyTorch", "CUDA", "TensorRT", "RAPIDS"
            ],
            "complianceInfo": {
                "exportRestrictions": ["Restricted under US export regulations"],
                "certifications": ["PCI Express 4.0", "NVLink"],
                "restrictedCountries": ["Russia", "Iran", "North Korea", "Cuba", "Syria"]
            },
            "benchmarks": {
                "mlTraining": {
                    "ResNet-50": 1.0,
                    "BERT": 1.0
                },
                "llmInference": {
                    "GPT-3": 180  # tokens/sec
                }
            },
            "inStock": True,
            "leadTime": 14,
            "quantityAvailable": 10
        },
        {
            "name": "NVIDIA H100 80GB SXM5",
            "manufacturer": "NVIDIA",
            "category": "GPU",
            "type": "GPU",
            "model": "H100",
            "description": "The NVIDIA H100 GPU is the most advanced accelerator ever built. Powered by the NVIDIA Hopper architecture, it delivers an order of magnitude leap for accelerated computing.",
            "specifications": {
                "CUDA Cores": "16896",
                "Tensor Cores": "528",
                "Memory Size": "80 GB HBM3",
                "Memory Bandwidth": "3.35 TB/s",
                "TDP": "700 W"
            },
            "price": 30000.00,  # Estimated price
            "warranty": "3 years",
            "dataSourceUrl": "https://www.nvidia.com/en-us/data-center/h100/",
            "lastPriceUpdate": current_time,
            "computeSpecs": {
                "cudaCores": 16896,
                "tensorCores": 528,
                "fp32Performance": 60,    # TFLOPS
                "fp16Performance": 1000,  # TFLOPS with sparsity
                "int8Performance": 2000   # TOPS with sparsity
            },
            "memorySpecs": {
                "capacity": 80,
                "type": "HBM3",
                "bandwidth": 3350,
                "busWidth": 5120,
                "eccSupport": True
            },
            "powerConsumption": {
                "tdp": 700,
                "requiredPsu": 1600
            },
            "architecture": "Hopper",
            "supportedFrameworks": [
                "TensorFlow", "PyTorch", "CUDA", "TensorRT", "RAPIDS", "JAX"
            ],
            "complianceInfo": {
                "exportRestrictions": ["Restricted under US export regulations"],
                "certifications": ["NVLink4", "PCIe Gen5"],
                "restrictedCountries": ["Russia", "Iran", "North Korea", "Cuba", "Syria"]
            },
            "benchmarks": {
                "mlTraining": {
                    "ResNet-50": 4.5,
                    "BERT": 4.0
                },
                "llmInference": {
                    "GPT-3": 500  # tokens/sec
                }
            },
            "inStock": False,
            "leadTime": 90,
            "quantityAvailable": 0
        },
        {
            "name": "AMD Instinct MI250X",
            "manufacturer": "AMD",
            "category": "GPU",
            "type": "GPU",
            "model": "MI250X",
            "description": "The AMD Instinct MI250X accelerator delivers exceptional performance for HPC and AI workloads with a multi-die GPU design.",
            "specifications": {
                "Stream Processors": "14080",
                "Matrix Cores": "220",
                "Memory Size": "128 GB HBM2e",
                "Memory Bandwidth": "3.2 TB/s",
                "TDP": "500 W"
            },
            "price": 12000.00,  # Estimated price
            "warranty": "3 years",
            "dataSourceUrl": "https://www.amd.com/en/products/server-accelerators/instinct-mi250x",
            "lastPriceUpdate": current_time,
            "computeSpecs": {
                "streamProcessors": 14080,
                "matrixCores": 220,
                "fp32Performance": 47.9,  # TFLOPS
                "fp16Performance": 383,   # TFLOPS
                "int8Performance": 383    # TOPS
            },
            "memorySpecs": {
                "capacity": 128,
                "type": "HBM2e",
                "bandwidth": 3200,
                "busWidth": 8192,
                "eccSupport": True
            },
            "powerConsumption": {
                "tdp": 500,
                "requiredPsu": 1200
            },
            "architecture": "CDNA 2",
            "supportedFrameworks": [
                "TensorFlow", "PyTorch", "ROCm", "OpenMP", "OpenCL"
            ],
            "complianceInfo": {
                "exportRestrictions": ["May be subject to export controls"],
                "certifications": ["PCIe Gen4", "Infinity Fabric"],
                "restrictedCountries": []
            },
            "benchmarks": {
                "mlTraining": {
                    "ResNet-50": 3.2,
                    "BERT": 2.8
                },
                "llmInference": {
                    "GPT-3": 320  # tokens/sec
                }
            },
            "inStock": True,
            "leadTime": 30,
            "quantityAvailable": 5
        },
        {
            "name": "Huawei Ascend 910B",
            "manufacturer": "Huawei",
            "category": "AI Accelerator",
            "type": "NPU",
            "model": "Ascend 910B",
            "description": "The Huawei Ascend 910B is a dedicated AI processor designed for training and inference of deep neural networks.",
            "specifications": {
                "Computing Power": "256 TFLOPS",
                "Memory Size": "32 GB HBM",
                "Memory Bandwidth": "1.2 TB/s",
                "TDP": "310 W"
            },
            "price": 8000.00,  # Estimated price
            "warranty": "2 years",
            "dataSourceUrl": "https://e.huawei.com/en/products/compute/ascend",
            "lastPriceUpdate": current_time,
            "computeSpecs": {
                "fp32Performance": 32,   # TFLOPS
                "fp16Performance": 256,  # TFLOPS
                "int8Performance": 512   # TOPS
            },
            "memorySpecs": {
                "capacity": 32,
                "type": "HBM",
                "bandwidth": 1200,
                "busWidth": 2048
            },
            "powerConsumption": {
                "tdp": 310
            },
            "architecture": "Da Vinci",
            "supportedFrameworks": [
                "TensorFlow", "PyTorch", "MindSpore", "CANN"
            ],
            "complianceInfo": {
                "exportRestrictions": ["Not subject to US export controls"],
                "restrictedCountries": []
            },
            "benchmarks": {
                "mlTraining": {
                    "ResNet-50": 2.8,
                    "BERT": 2.5
                }
            },
            "inStock": True,
            "leadTime": 45,
            "quantityAvailable": 20
        },
        {
            "name": "Cerebras CS-2",
            "manufacturer": "Cerebras",
            "category": "Wafer-Scale Engine",
            "type": "AI Accelerator",
            "model": "CS-2",
            "description": "The Cerebras CS-2 is the world's largest and fastest AI processor, featuring a wafer-scale engine with 850,000 cores.",
            "specifications": {
                "Cores": "850,000",
                "Memory Size": "40 GB on-chip + 1.2 TB off-chip",
                "Memory Bandwidth": "20 PB/s on-chip",
                "TDP": "15 kW"
            },
            "price": 2000000.00,  # Estimated price
            "warranty": "3 years with support contract",
            "dataSourceUrl": "https://cerebras.net/products/cs-2/",
            "lastPriceUpdate": current_time,
            "computeSpecs": {
                "cores": 850000,
                "fp32Performance": 1000,   # Approximate TFLOPS
                "fp16Performance": 2000    # Approximate TFLOPS
            },
            "memorySpecs": {
                "capacity": 40,
                "type": "SRAM (on-chip) + DRAM (off-chip)",
                "bandwidth": 20000000      # PB/s converted to GB/s
            },
            "powerConsumption": {
                "tdp": 15000,              # 15 kW
                "requiredPsu": 20000
            },
            "architecture": "Wafer-Scale Engine 2",
            "supportedFrameworks": [
                "TensorFlow", "PyTorch", "Cerebras Software Platform"
            ],
            "complianceInfo": {
                "exportRestrictions": ["Subject to US export regulations"],
                "certifications": ["Only available through direct sales"],
                "restrictedCountries": ["Russia", "Iran", "North Korea", "Cuba", "Syria"]
            },
            "benchmarks": {
                "mlTraining": {
                    "ResNet-50": 12.0,
                    "BERT": 15.0
                }
            },
            "inStock": False,
            "leadTime": 180,
            "quantityAvailable": 0
        }
    ]


# Additional helper function to store sample data in the database
async def store_products_in_database(products: List[Dict[str, Any]]) -> None:
    """
    Store products in the database.
    
    Args:
        products: List of product dictionaries to store
    """
    try:
        from python_backend.models.database import Product, Supplier, get_db
        
        db = next(get_db())
        
        # For each product, create or update the supplier and the product
        for product_data in products:
            # Check if supplier exists, create if not
            supplier = db.query(Supplier).filter(
                Supplier.name == product_data["manufacturer"]
            ).first()
            
            if not supplier:
                supplier = Supplier(
                    name=product_data["manufacturer"],
                    country="United States",  # Default, should be updated with actual data
                    description=f"Manufacturer of {product_data['category']} products",
                    website=f"https://www.{product_data['manufacturer'].lower()}.com",
                    logoUrl=f"/images/suppliers/{product_data['manufacturer'].lower()}.png",
                    contactEmail=f"info@{product_data['manufacturer'].lower()}.com",
                    contactPhone="+1-555-555-5555",
                    deliveryTime="4-6 weeks",
                    isVerified=True,
                    complianceStatus="Compliant",
                    stockAvailability="Limited",
                    leadTime=product_data.get("leadTime", 30)
                )
                db.add(supplier)
                db.commit()
                db.refresh(supplier)
            
            # Check if product exists, create if not, update if it does
            existing_product = db.query(Product).filter(
                Product.name == product_data["name"],
                Product.supplier_id == supplier.id
            ).first()
            
            if existing_product:
                # Update existing product
                for key, value in product_data.items():
                    if hasattr(existing_product, key) and key != 'id':
                        setattr(existing_product, key, value)
                
                db.commit()
                logger.info(f"Updated product: {product_data['name']}")
            else:
                # Create new product
                new_product = Product(
                    supplier_id=supplier.id,
                    name=product_data["name"],
                    category=product_data["category"],
                    description=product_data["description"],
                    specifications=product_data["specifications"],
                    price=product_data["price"],
                    warranty=product_data["warranty"],
                    type=product_data.get("type", ""),
                    manufacturer=product_data["manufacturer"],
                    model=product_data.get("model", ""),
                    architecture=product_data.get("architecture", ""),
                    compute_specs=product_data.get("computeSpecs", {}),
                    memory_specs=product_data.get("memorySpecs", {}),
                    power_consumption=product_data.get("powerConsumption", {}),
                    supported_frameworks=product_data.get("supportedFrameworks", []),
                    compliance_info=product_data.get("complianceInfo", {}),
                    benchmarks=product_data.get("benchmarks", {}),
                    in_stock=product_data.get("inStock", True),
                    lead_time=product_data.get("leadTime", 0),
                    quantity_available=product_data.get("quantityAvailable", 0),
                    data_source_url=product_data.get("dataSourceUrl", "")
                )
                db.add(new_product)
                db.commit()
                logger.info(f"Created product: {product_data['name']}")
        
    except Exception as e:
        logger.error(f"Error storing products in database: {str(e)}")
        raise


if __name__ == "__main__":
    # For testing purposes
    products = create_sample_gpu_products()
    print(f"Created {len(products)} sample products")
    
    # Save sample products to file
    output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
    os.makedirs(output_dir, exist_ok=True)
    
    filepath = os.path.join(output_dir, "sample_products.json")
    with open(filepath, 'w') as f:
        json.dump({
            'products': products,
            'scraped_at': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"Saved sample products to {filepath}")