from typing import List, Dict, Optional, Any
from datetime import datetime
import json

from .schemas import User, RFQ, Supplier, Product, Proposal

class MemStorage:
    def __init__(self):
        """Initialize in-memory storage with empty collections"""
        self.users = {}
        self.rfqs = {}
        self.suppliers = {}
        self.products = {}
        self.proposals = {}
        
        # Counters for generating IDs
        self.user_id_counter = 1
        self.rfq_id_counter = 1
        self.supplier_id_counter = 1
        self.product_id_counter = 1
        self.proposal_id_counter = 1
    
    async def get_user(self, id: int) -> Optional[User]:
        """Get a user by ID"""
        return self.users.get(id)
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username"""
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    async def create_user(self, user_data: dict) -> User:
        """Create a new user"""
        id = self.user_id_counter
        self.user_id_counter += 1
        
        user = User(id=id, **user_data)
        self.users[id] = user
        return user
    
    async def create_rfq(self, rfq_data: dict) -> RFQ:
        """Create a new RFQ"""
        id = self.rfq_id_counter
        self.rfq_id_counter += 1
        
        rfq = RFQ(id=id, **rfq_data)
        self.rfqs[id] = rfq
        return rfq
    
    async def get_rfq_by_id(self, id: int) -> Optional[RFQ]:
        """Get an RFQ by ID"""
        return self.rfqs.get(id)
    
    async def get_all_rfqs(self) -> List[RFQ]:
        """Get all RFQs"""
        return list(self.rfqs.values())
    
    async def create_supplier(self, supplier_data: dict) -> Supplier:
        """Create a new supplier"""
        id = self.supplier_id_counter
        self.supplier_id_counter += 1
        
        supplier = Supplier(id=id, **supplier_data)
        self.suppliers[id] = supplier
        return supplier
    
    async def get_supplier_by_id(self, id: int) -> Optional[Supplier]:
        """Get a supplier by ID"""
        return self.suppliers.get(id)
    
    async def get_all_suppliers(self) -> List[Supplier]:
        """Get all suppliers"""
        return list(self.suppliers.values())
    
    async def create_product(self, product_data: dict) -> Product:
        """Create a new product"""
        id = self.product_id_counter
        self.product_id_counter += 1
        
        product = Product(id=id, **product_data)
        self.products[id] = product
        return product
    
    async def get_product_by_id(self, id: int) -> Optional[Product]:
        """Get a product by ID"""
        return self.products.get(id)
    
    async def get_products_by_supplier(self, supplier_id: int) -> List[Product]:
        """Get all products for a supplier"""
        return [p for p in self.products.values() if p.supplierId == supplier_id]
    
    async def get_products_by_category(self, category: str) -> List[Product]:
        """Get all products by category"""
        return [p for p in self.products.values() if p.category.lower() == category.lower()]
    
    async def create_proposal(self, proposal_data: dict) -> Proposal:
        """Create a new proposal"""
        id = self.proposal_id_counter
        self.proposal_id_counter += 1
        
        proposal = Proposal(id=id, **proposal_data)
        self.proposals[id] = proposal
        return proposal
    
    async def get_proposal_by_id(self, id: int) -> Optional[Proposal]:
        """Get a proposal by ID"""
        return self.proposals.get(id)
    
    async def get_proposals_by_rfq(self, rfq_id: int) -> List[Proposal]:
        """Get all proposals for an RFQ"""
        return [p for p in self.proposals.values() if p.rfqId == rfq_id]
    
    def initialize_sample_data(self):
        """Initialize the storage with sample data for testing"""
        # Create test user
        self.create_user_sync({
            "username": "testuser",
            "email": "test@example.com",
            "fullName": "Test User",
            "company": "Test Company"
        })
        
        # Create suppliers
        dell_supplier = self.create_supplier_sync({
            "name": "Dell Technologies",
            "logoUrl": "https://logo.clearbit.com/dell.com",
            "website": "https://www.dell.com",
            "country": "USA",
            "description": "Dell is a multinational technology company that develops, sells, repairs, and supports computers and related products and services.",
            "contactEmail": "sales@dell.com",
            "contactPhone": "+1-800-624-9897",
            "deliveryTime": "15-30 days",
            "isVerified": True
        })
        
        hp_supplier = self.create_supplier_sync({
            "name": "HP Inc.",
            "logoUrl": "https://logo.clearbit.com/hp.com",
            "website": "https://www.hp.com",
            "country": "USA",
            "description": "HP Inc. is an American multinational information technology company that develops personal computers, printers and related supplies.",
            "contactEmail": "sales@hp.com",
            "contactPhone": "+1-800-474-6836",
            "deliveryTime": "10-20 days",
            "isVerified": True
        })
        
        lenovo_supplier = self.create_supplier_sync({
            "name": "Lenovo",
            "logoUrl": "https://logo.clearbit.com/lenovo.com",
            "website": "https://www.lenovo.com",
            "country": "China",
            "description": "Lenovo is a Chinese multinational technology company that designs, develops, manufactures and sells personal computers, tablets, smartphones, workstations, servers, electronic storage, IT management software, and smart TVs.",
            "contactEmail": "sales@lenovo.com",
            "contactPhone": "+1-855-253-6686",
            "deliveryTime": "20-40 days",
            "isVerified": True
        })
        
        # Create laptop products
        # Dell laptop
        self.create_product_sync({
            "supplierId": dell_supplier.id,
            "name": "Dell Latitude 7430",
            "category": "Laptops",
            "description": "Enterprise-grade business laptop with excellent performance and security features.",
            "price": 1499.99,
            "specifications": {
                "os": "Windows 11 Pro",
                "processor": "Intel Core i7-1265U",
                "memory": "16GB DDR4",
                "storage": "512GB SSD",
                "display": "14-inch FHD (1920 x 1080)",
                "battery": "12 hours",
                "durability": "MIL-STD-810H tested",
                "connectivity": "Wi-Fi 6E, Bluetooth 5.2"
            },
            "warranty": "3 years ProSupport"
        })
        
        # HP laptop
        self.create_product_sync({
            "supplierId": hp_supplier.id,
            "name": "HP EliteBook 840 G9",
            "category": "Laptops",
            "description": "Premium business laptop designed for professionals with advanced security features.",
            "price": 1399.99,
            "specifications": {
                "os": "Windows 11 Pro",
                "processor": "Intel Core i5-1245U",
                "memory": "16GB DDR5",
                "storage": "512GB NVMe SSD",
                "display": "14-inch FHD (1920 x 1080)",
                "battery": "10 hours",
                "durability": "MIL-STD-810H tested",
                "connectivity": "Wi-Fi 6E, Bluetooth 5.2"
            },
            "warranty": "3 years HP Care Pack"
        })
        
        # Lenovo laptop
        self.create_product_sync({
            "supplierId": lenovo_supplier.id,
            "name": "Lenovo ThinkPad X1 Carbon Gen 10",
            "category": "Laptops",
            "description": "Ultra-lightweight premium business laptop with exceptional build quality.",
            "price": 1699.99,
            "specifications": {
                "os": "Windows 11 Pro",
                "processor": "Intel Core i7-1260P",
                "memory": "16GB LPDDR5",
                "storage": "1TB SSD",
                "display": "14-inch WUXGA (1920 x 1200)",
                "battery": "14 hours",
                "durability": "MIL-STD-810H tested",
                "connectivity": "Wi-Fi 6E, Bluetooth 5.2"
            },
            "warranty": "3 years Lenovo Premier Support"
        })
        
        # Create monitor products
        # Dell monitor
        self.create_product_sync({
            "supplierId": dell_supplier.id,
            "name": "Dell UltraSharp U2723QE",
            "category": "Monitors",
            "description": "Professional 4K USB-C Hub Monitor with excellent color accuracy.",
            "price": 599.99,
            "specifications": {
                "screenSize": "27 inches",
                "resolution": "4K UHD (3840 x 2160)",
                "panelTech": "IPS",
                "brightness": "400 cd/m²",
                "contrastRatio": "2000:1",
                "connectivity": "HDMI, DisplayPort, USB-C",
                "adjustability": "Height, tilt, swivel, pivot adjustable"
            },
            "warranty": "3 years Advanced Exchange Service"
        })
        
        # HP monitor
        self.create_product_sync({
            "supplierId": hp_supplier.id,
            "name": "HP E27u G4",
            "category": "Monitors",
            "description": "Business-class QHD monitor with USB-C and ergonomic stand.",
            "price": 399.99,
            "specifications": {
                "screenSize": "27 inches",
                "resolution": "QHD (2560 x 1440)",
                "panelTech": "IPS",
                "brightness": "300 cd/m²",
                "contrastRatio": "1000:1",
                "connectivity": "HDMI, DisplayPort, USB-C",
                "adjustability": "Height, tilt, swivel adjustable"
            },
            "warranty": "3 years standard"
        })
        
        # Lenovo monitor
        self.create_product_sync({
            "supplierId": lenovo_supplier.id,
            "name": "Lenovo ThinkVision P27h-20",
            "category": "Monitors",
            "description": "Professional QHD monitor with USB-C docking and factory calibration.",
            "price": 499.99,
            "specifications": {
                "screenSize": "27 inches",
                "resolution": "QHD (2560 x 1440)",
                "panelTech": "IPS",
                "brightness": "350 cd/m²",
                "contrastRatio": "1000:1",
                "connectivity": "HDMI, DisplayPort, USB-C",
                "adjustability": "Height, tilt, swivel, pivot adjustable"
            },
            "warranty": "3 years Lenovo Premier Support"
        })
    
    def create_user_sync(self, user_data: dict) -> User:
        """Create a new user (sync version for initialization)"""
        id = self.user_id_counter
        self.user_id_counter += 1
        
        user = User(id=id, **user_data)
        self.users[id] = user
        return user
    
    def create_supplier_sync(self, supplier_data: dict) -> Supplier:
        """Create a new supplier (sync version for initialization)"""
        id = self.supplier_id_counter
        self.supplier_id_counter += 1
        
        supplier = Supplier(id=id, **supplier_data)
        self.suppliers[id] = supplier
        return supplier
    
    def create_product_sync(self, product_data: dict) -> Product:
        """Create a new product (sync version for initialization)"""
        id = self.product_id_counter
        self.product_id_counter += 1
        
        product = Product(id=id, **product_data)
        self.products[id] = product
        return product