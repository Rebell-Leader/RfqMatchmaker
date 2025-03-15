from typing import Dict, List, Optional, Any
from datetime import datetime
from .schemas import User, RFQ, Supplier, Product, Proposal, ExtractedRequirement, AwardCriteria

class MemStorage:
    def __init__(self):
        """Initialize in-memory storage with empty collections"""
        self.users: Dict[int, User] = {}
        self.rfqs: Dict[int, RFQ] = {}
        self.suppliers: Dict[int, Supplier] = {}
        self.products: Dict[int, Product] = {}
        self.proposals: Dict[int, Proposal] = {}
        
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
        
        # Create RFQ object
        rfq = RFQ(
            id=id,
            title=rfq_data["title"],
            description=rfq_data.get("description", ""),
            originalContent=rfq_data["originalContent"],
            extractedRequirements=rfq_data["extractedRequirements"],
            userId=rfq_data.get("userId", 1),
            createdAt=datetime.now()
        )
        
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
        
        # Create Supplier object
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
        
        # Create Product object
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
        
        # Create Proposal object
        proposal = Proposal(
            id=id,
            rfqId=proposal_data["rfqId"],
            productId=proposal_data["productId"],
            score=proposal_data["score"],
            priceScore=proposal_data["priceScore"],
            qualityScore=proposal_data["qualityScore"],
            deliveryScore=proposal_data["deliveryScore"],
            emailContent=proposal_data.get("emailContent"),
            createdAt=datetime.now()
        )
        
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
        # Create sample users
        self.create_user_sync({
            "username": "testuser",
            "email": "test@example.com",
            "fullName": "Test User",
            "company": "Test Company"
        })
        
        # Create sample suppliers
        dell_supplier = self.create_supplier_sync({
            "name": "Dell Technologies",
            "logoUrl": "https://logo.clearbit.com/dell.com",
            "website": "https://www.dell.com",
            "country": "United States",
            "description": "Global computer technology company that develops, sells, repairs, and supports computers and related products and services.",
            "contactEmail": "sales@dell.com",
            "contactPhone": "+1-800-999-3355",
            "deliveryTime": "15-30 days"
        })
        
        hp_supplier = self.create_supplier_sync({
            "name": "HP Inc.",
            "logoUrl": "https://logo.clearbit.com/hp.com",
            "website": "https://www.hp.com",
            "country": "United States",
            "description": "American multinational information technology company that develops computers, printers, and related supplies.",
            "contactEmail": "sales@hp.com",
            "contactPhone": "+1-800-474-6836",
            "deliveryTime": "10-20 days"
        })
        
        lenovo_supplier = self.create_supplier_sync({
            "name": "Lenovo",
            "logoUrl": "https://logo.clearbit.com/lenovo.com",
            "website": "https://www.lenovo.com",
            "country": "China",
            "description": "Chinese multinational technology company that designs, develops, manufactures, and sells personal computers, tablets, smartphones, and more.",
            "contactEmail": "sales@lenovo.com",
            "contactPhone": "+1-855-253-6686",
            "deliveryTime": "20-35 days"
        })
        
        asus_supplier = self.create_supplier_sync({
            "name": "ASUS",
            "logoUrl": "https://logo.clearbit.com/asus.com",
            "website": "https://www.asus.com",
            "country": "Taiwan",
            "description": "Taiwanese multinational computer and phone hardware and electronics company.",
            "contactEmail": "sales@asus.com",
            "contactPhone": "+1-888-678-3688",
            "deliveryTime": "15-25 days"
        })
        
        acer_supplier = self.create_supplier_sync({
            "name": "Acer",
            "logoUrl": "https://logo.clearbit.com/acer.com",
            "website": "https://www.acer.com",
            "country": "Taiwan",
            "description": "Taiwanese multinational hardware and electronics corporation specializing in computers and related products.",
            "contactEmail": "sales@acer.com",
            "contactPhone": "+1-866-695-2237",
            "deliveryTime": "15-30 days"
        })
        
        # Create sample products for each supplier
        
        # Dell Laptops
        self.create_product_sync({
            "supplierId": dell_supplier.id,
            "name": "Dell Latitude 5420",
            "category": "Laptops",
            "description": "Business laptop with enhanced security features and long battery life",
            "price": 999.99,
            "specifications": {
                "os": "Windows 11 Pro",
                "processor": "Intel Core i5-1135G7",
                "memory": "16GB DDR4",
                "storage": "512GB SSD",
                "display": "14-inch FHD (1920 x 1080)",
                "battery": "Up to 10 hours",
                "durability": "MIL-STD-810H tested",
                "connectivity": "Wi-Fi 6, Bluetooth 5.1",
                "warranty": "3 year ProSupport"
            },
            "warranty": "3 years ProSupport"
        })
        
        self.create_product_sync({
            "supplierId": dell_supplier.id,
            "name": "Dell Precision 7560",
            "category": "Laptops",
            "description": "Powerful mobile workstation for professional applications",
            "price": 1899.99,
            "specifications": {
                "os": "Windows 11 Pro",
                "processor": "Intel Core i7-11850H",
                "memory": "32GB DDR4",
                "storage": "1TB SSD",
                "display": "15.6-inch UHD (3840 x 2160)",
                "battery": "Up to 8 hours",
                "durability": "MIL-STD-810H tested",
                "connectivity": "Wi-Fi 6, Bluetooth 5.2",
                "warranty": "3 year ProSupport"
            },
            "warranty": "3 years ProSupport"
        })
        
        # Dell Monitors
        self.create_product_sync({
            "supplierId": dell_supplier.id,
            "name": "Dell UltraSharp U2720Q",
            "category": "Monitors",
            "description": "27-inch 4K UHD monitor with USB-C connectivity",
            "price": 599.99,
            "specifications": {
                "screenSize": "27 inches",
                "resolution": "4K UHD (3840 x 2160)",
                "panelTech": "IPS",
                "brightness": "350 cd/m²",
                "contrastRatio": "1300:1",
                "connectivity": "HDMI, DisplayPort, USB-C",
                "adjustability": "Height, tilt, swivel, pivot",
                "warranty": "3 years Advanced Exchange"
            },
            "warranty": "3 years Advanced Exchange"
        })
        
        # HP Laptops
        self.create_product_sync({
            "supplierId": hp_supplier.id,
            "name": "HP ProBook 450 G8",
            "category": "Laptops",
            "description": "Reliable business laptop with comprehensive security features",
            "price": 889.99,
            "specifications": {
                "os": "Windows 11 Pro",
                "processor": "Intel Core i5-1135G7",
                "memory": "8GB DDR4",
                "storage": "256GB SSD",
                "display": "15.6-inch FHD (1920 x 1080)",
                "battery": "Up to 9 hours",
                "durability": "Spill-resistant keyboard",
                "connectivity": "Wi-Fi 6, Bluetooth 5.0",
                "warranty": "1 year standard"
            },
            "warranty": "1 year standard"
        })
        
        # HP Monitors
        self.create_product_sync({
            "supplierId": hp_supplier.id,
            "name": "HP E27u G4",
            "category": "Monitors",
            "description": "27-inch QHD monitor with USB-C",
            "price": 379.99,
            "specifications": {
                "screenSize": "27 inches",
                "resolution": "QHD (2560 x 1440)",
                "panelTech": "IPS",
                "brightness": "300 cd/m²",
                "contrastRatio": "1000:1",
                "connectivity": "HDMI, DisplayPort, USB-C",
                "adjustability": "Height, tilt, swivel, pivot",
                "warranty": "3 years"
            },
            "warranty": "3 years"
        })
        
        # Lenovo Laptops
        self.create_product_sync({
            "supplierId": lenovo_supplier.id,
            "name": "Lenovo ThinkPad L14",
            "category": "Laptops",
            "description": "Durable business laptop with advanced security features",
            "price": 849.99,
            "specifications": {
                "os": "Windows 11 Pro",
                "processor": "Intel Core i5-1135G7",
                "memory": "8GB DDR4",
                "storage": "256GB SSD",
                "display": "14-inch FHD (1920 x 1080)",
                "battery": "Up to 10 hours",
                "durability": "MIL-STD-810H tested",
                "connectivity": "Wi-Fi 6, Bluetooth 5.1",
                "warranty": "1 year depot"
            },
            "warranty": "1 year depot"
        })
        
        # Lenovo Monitors
        self.create_product_sync({
            "supplierId": lenovo_supplier.id,
            "name": "Lenovo ThinkVision P27h-20",
            "category": "Monitors",
            "description": "27-inch QHD monitor with USB-C docking",
            "price": 449.99,
            "specifications": {
                "screenSize": "27 inches",
                "resolution": "QHD (2560 x 1440)",
                "panelTech": "IPS",
                "brightness": "350 cd/m²",
                "contrastRatio": "1000:1",
                "connectivity": "HDMI, DisplayPort, USB-C",
                "adjustability": "Height, tilt, swivel, pivot",
                "warranty": "3 years"
            },
            "warranty": "3 years"
        })
    
    # Synchronous versions for sample data initialization
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