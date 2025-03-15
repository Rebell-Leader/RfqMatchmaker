from typing import Dict, List, Optional, Union
from datetime import datetime
from .schemas import User, RFQ, Supplier, Product, Proposal, ExtractedRequirement

# In-memory storage implementation
class MemStorage:
    def __init__(self):
        self.users: Dict[int, User] = {}
        self.rfqs: Dict[int, RFQ] = {}
        self.suppliers: Dict[int, Supplier] = {}
        self.products: Dict[int, Product] = {}
        self.proposals: Dict[int, Proposal] = {}
        
        # ID counters
        self.user_id: int = 1
        self.rfq_id: int = 1
        self.supplier_id: int = 1
        self.product_id: int = 1
        self.proposal_id: int = 1
        
        # Initialize with sample data
        self.initialize_sample_data()
    
    # User methods
    async def get_user(self, id: int) -> Optional[User]:
        return self.users.get(id)
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    async def create_user(self, user_data: dict) -> User:
        id = self.user_id
        self.user_id += 1
        
        user = User(id=id, **user_data)
        self.users[id] = user
        return user
    
    # RFQ methods
    async def create_rfq(self, rfq_data: dict) -> RFQ:
        id = self.rfq_id
        self.rfq_id += 1
        
        rfq = RFQ(id=id, createdAt=datetime.now(), **rfq_data)
        self.rfqs[id] = rfq
        return rfq
    
    async def get_rfq_by_id(self, id: int) -> Optional[RFQ]:
        return self.rfqs.get(id)
    
    async def get_all_rfqs(self) -> List[RFQ]:
        return list(self.rfqs.values())
    
    # Supplier methods
    async def create_supplier(self, supplier_data: dict) -> Supplier:
        id = self.supplier_id
        self.supplier_id += 1
        
        supplier = Supplier(id=id, **supplier_data)
        self.suppliers[id] = supplier
        return supplier
    
    async def get_supplier_by_id(self, id: int) -> Optional[Supplier]:
        return self.suppliers.get(id)
    
    async def get_all_suppliers(self) -> List[Supplier]:
        return list(self.suppliers.values())
    
    # Product methods
    async def create_product(self, product_data: dict) -> Product:
        id = self.product_id
        self.product_id += 1
        
        product = Product(id=id, **product_data)
        self.products[id] = product
        return product
    
    async def get_product_by_id(self, id: int) -> Optional[Product]:
        return self.products.get(id)
    
    async def get_products_by_supplier(self, supplier_id: int) -> List[Product]:
        return [product for product in self.products.values() if product.supplierId == supplier_id]
    
    async def get_products_by_category(self, category: str) -> List[Product]:
        return [product for product in self.products.values() if product.category == category]
    
    # Proposal methods
    async def create_proposal(self, proposal_data: dict) -> Proposal:
        id = self.proposal_id
        self.proposal_id += 1
        
        proposal = Proposal(id=id, createdAt=datetime.now(), **proposal_data)
        self.proposals[id] = proposal
        return proposal
    
    async def get_proposal_by_id(self, id: int) -> Optional[Proposal]:
        return self.proposals.get(id)
    
    async def get_proposals_by_rfq(self, rfq_id: int) -> List[Proposal]:
        return [proposal for proposal in self.proposals.values() if proposal.rfqId == rfq_id]
    
    # Sample data initialization
    def initialize_sample_data(self):
        # Create sample user
        self.users[1] = User(
            id=1,
            username="demo_user",
            email="demo@example.com",
            fullName="Demo User",
            company="Demo Company"
        )
        
        # Create sample suppliers
        dell_supplier = Supplier(
            id=1,
            name="Dell Technologies",
            logoUrl="https://logo.clearbit.com/dell.com",
            website="https://www.dell.com",
            country="United States",
            description="Global computer technology company",
            contactEmail="sales@dell.com",
            contactPhone="+1-800-999-3355",
            deliveryTime="15-20 days"
        )
        
        hp_supplier = Supplier(
            id=2,
            name="HP Inc.",
            logoUrl="https://logo.clearbit.com/hp.com",
            website="https://www.hp.com",
            country="United States",
            description="Information technology company",
            contactEmail="sales@hp.com",
            contactPhone="+1-800-474-6836",
            deliveryTime="20-30 days"
        )
        
        lenovo_supplier = Supplier(
            id=3,
            name="Lenovo",
            logoUrl="https://logo.clearbit.com/lenovo.com",
            website="https://www.lenovo.com",
            country="China",
            description="Multinational technology company",
            contactEmail="sales@lenovo.com",
            contactPhone="+1-855-253-6686",
            deliveryTime="25-35 days"
        )
        
        self.suppliers[1] = dell_supplier
        self.suppliers[2] = hp_supplier
        self.suppliers[3] = lenovo_supplier
        
        # Create sample products
        # Dell Laptop
        self.products[1] = Product(
            id=1,
            supplierId=1,
            name="Dell Latitude 5350",
            category="Laptops",
            description="Business laptop with Intel Core i5 processor",
            price=899.99,
            specifications={
                "processor": "Intel Core i5-125U (12 cores, up to 4.3 GHz)",
                "memory": "16 GB LPDDR5x RAM",
                "storage": "256 GB PCIe Gen4 NVMe SSD",
                "display": "FHD (1920x1080), IPS, non-touch, 250 nits",
                "battery": "9 hours",
                "durability": "MIL-STD 810G certified",
                "connectivity": "Wi-Fi 6, Bluetooth, HDMI, USB-C",
                "os": "Windows 11 Pro"
            },
            warranty="1 year basic onsite service"
        )
        
        # HP Laptop
        self.products[2] = Product(
            id=2,
            supplierId=2,
            name="HP Fortis Pro",
            category="Laptops",
            description="Durable educational laptop with Intel Core i5 processor",
            price=1199.99,
            specifications={
                "processor": "Intel Core i5-1235U (10 cores, up to 4.4 GHz)",
                "memory": "32 GB LPDDR5 RAM",
                "storage": "512 GB PCIe NVMe SSD",
                "display": "FHD (1920x1080), IPS, non-touch, 300 nits",
                "battery": "10 hours",
                "durability": "MIL-STD 810H certified",
                "connectivity": "Wi-Fi 6E, Bluetooth 5.2, HDMI, USB-C, Thunderbolt 4",
                "os": "Windows 11 Pro for Education"
            },
            warranty="3 years onsite service"
        )
        
        # Lenovo Laptop
        self.products[3] = Product(
            id=3,
            supplierId=3,
            name="Lenovo ThinkPad L14",
            category="Laptops",
            description="Business laptop with AMD Ryzen processor",
            price=999.99,
            specifications={
                "processor": "AMD Ryzen 5 PRO 5675U (6 cores, up to 4.3 GHz)",
                "memory": "16 GB DDR4 RAM",
                "storage": "256 GB PCIe NVMe SSD",
                "display": "FHD (1920x1080), IPS, anti-glare, 250 nits",
                "battery": "8 hours",
                "durability": "MIL-STD 810H certified",
                "connectivity": "Wi-Fi 6, Bluetooth 5.1, HDMI, USB-C",
                "os": "Windows 11 Pro"
            },
            warranty="2 years onsite service"
        )
        
        # Dell Monitor
        self.products[4] = Product(
            id=4,
            supplierId=1,
            name="Dell E2420H",
            category="Monitors",
            description="24-inch full HD monitor",
            price=199.99,
            specifications={
                "screenSize": "24 inches",
                "resolution": "FHD (1920x1080)",
                "panelTech": "IPS with anti-glare coating",
                "brightness": "250 nits",
                "contrastRatio": "1000:1",
                "connectivity": "VGA, DisplayPort",
                "adjustability": "Tilt adjustment"
            },
            warranty="3 years advanced exchange service"
        )
        
        # HP Monitor
        self.products[5] = Product(
            id=5,
            supplierId=2,
            name="HP P24v G5",
            category="Monitors",
            description="23.8-inch full HD monitor",
            price=179.99,
            specifications={
                "screenSize": "23.8 inches",
                "resolution": "FHD (1920x1080)",
                "panelTech": "IPS with anti-glare coating",
                "brightness": "250 nits",
                "contrastRatio": "1000:1",
                "connectivity": "HDMI, VGA",
                "adjustability": "Tilt adjustment"
            },
            warranty="1 year standard exchange"
        )
        
        # Lenovo Monitor
        self.products[6] = Product(
            id=6,
            supplierId=3,
            name="Lenovo ThinkVision T24m-20",
            category="Monitors",
            description="23.8-inch full HD monitor with USB-C",
            price=249.99,
            specifications={
                "screenSize": "23.8 inches",
                "resolution": "FHD (1920x1080)",
                "panelTech": "IPS with anti-glare coating",
                "brightness": "250 nits",
                "contrastRatio": "1000:1",
                "connectivity": "HDMI, DisplayPort, USB-C",
                "adjustability": "Tilt, height, pivot, and swivel adjustment"
            },
            warranty="3 years advanced exchange service"
        )

# Create a singleton instance of MemStorage
storage = MemStorage()