from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
import json
from datetime import datetime

from .database import User as DBUser, RFQ as DBRFQ, Supplier as DBSupplier
from .database import Product as DBProduct, Proposal as DBProposal
from .database import get_db
from .schemas import User, RFQ, Supplier, Product, Proposal, ExtractedRequirement

class DatabaseStorage:
    """Database storage implementation using PostgreSQL and SQLAlchemy"""
    
    async def get_user(self, id: int) -> Optional[User]:
        """Get a user by ID"""
        db = next(get_db())
        db_user = db.query(DBUser).filter(DBUser.id == id).first()
        if not db_user:
            return None
        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            fullName=db_user.full_name,
            company=db_user.company
        )
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username"""
        db = next(get_db())
        db_user = db.query(DBUser).filter(DBUser.username == username).first()
        if not db_user:
            return None
        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            fullName=db_user.full_name,
            company=db_user.company
        )
    
    async def create_user(self, user_data: dict) -> User:
        """Create a new user"""
        db = next(get_db())
        db_user = DBUser(
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data.get("fullName"),
            company=user_data.get("company")
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            fullName=db_user.full_name,
            company=db_user.company
        )
    
    async def create_rfq(self, rfq_data: dict) -> RFQ:
        """Create a new RFQ"""
        db = next(get_db())
        db_rfq = DBRFQ(
            title=rfq_data["title"],
            description=rfq_data.get("description", ""),
            original_content=rfq_data["originalContent"],
            extracted_requirements=rfq_data["extractedRequirements"].dict(),
            user_id=rfq_data.get("userId", 1)  # Default to user 1 if not specified
        )
        db.add(db_rfq)
        db.commit()
        db.refresh(db_rfq)
        
        return RFQ(
            id=db_rfq.id,
            title=db_rfq.title,
            description=db_rfq.description,
            originalContent=db_rfq.original_content,
            extractedRequirements=ExtractedRequirement.parse_obj(db_rfq.extracted_requirements),
            userId=db_rfq.user_id,
            createdAt=db_rfq.created_at
        )
    
    async def get_rfq_by_id(self, id: int) -> Optional[RFQ]:
        """Get an RFQ by ID"""
        db = next(get_db())
        db_rfq = db.query(DBRFQ).filter(DBRFQ.id == id).first()
        if not db_rfq:
            return None
        
        return RFQ(
            id=db_rfq.id,
            title=db_rfq.title,
            description=db_rfq.description,
            originalContent=db_rfq.original_content,
            extractedRequirements=ExtractedRequirement.parse_obj(db_rfq.extracted_requirements),
            userId=db_rfq.user_id,
            createdAt=db_rfq.created_at
        )
    
    async def get_all_rfqs(self) -> List[RFQ]:
        """Get all RFQs"""
        db = next(get_db())
        db_rfqs = db.query(DBRFQ).all()
        
        return [
            RFQ(
                id=db_rfq.id,
                title=db_rfq.title,
                description=db_rfq.description,
                originalContent=db_rfq.original_content,
                extractedRequirements=ExtractedRequirement.parse_obj(db_rfq.extracted_requirements),
                userId=db_rfq.user_id,
                createdAt=db_rfq.created_at
            )
            for db_rfq in db_rfqs
        ]
    
    async def create_supplier(self, supplier_data: dict) -> Supplier:
        """Create a new supplier"""
        db = next(get_db())
        db_supplier = DBSupplier(
            name=supplier_data["name"],
            logo_url=supplier_data.get("logoUrl"),
            website=supplier_data.get("website"),
            country=supplier_data.get("country"),
            description=supplier_data.get("description", ""),
            contact_email=supplier_data.get("contactEmail"),
            contact_phone=supplier_data.get("contactPhone"),
            delivery_time=supplier_data.get("deliveryTime"),
            is_verified=supplier_data.get("isVerified", False)
        )
        db.add(db_supplier)
        db.commit()
        db.refresh(db_supplier)
        
        return Supplier(
            id=db_supplier.id,
            name=db_supplier.name,
            logoUrl=db_supplier.logo_url or "",
            website=db_supplier.website or "",
            country=db_supplier.country or "",
            description=db_supplier.description or "",
            contactEmail=db_supplier.contact_email or "",
            contactPhone=db_supplier.contact_phone or "",
            deliveryTime=db_supplier.delivery_time or "",
            isVerified=db_supplier.is_verified
        )
    
    async def get_supplier_by_id(self, id: int) -> Optional[Supplier]:
        """Get a supplier by ID"""
        db = next(get_db())
        db_supplier = db.query(DBSupplier).filter(DBSupplier.id == id).first()
        if not db_supplier:
            return None
        
        return Supplier(
            id=db_supplier.id,
            name=db_supplier.name,
            logoUrl=db_supplier.logo_url or "",
            website=db_supplier.website or "",
            country=db_supplier.country or "",
            description=db_supplier.description or "",
            contactEmail=db_supplier.contact_email or "",
            contactPhone=db_supplier.contact_phone or "",
            deliveryTime=db_supplier.delivery_time or "",
            isVerified=db_supplier.is_verified
        )
    
    async def get_all_suppliers(self) -> List[Supplier]:
        """Get all suppliers"""
        db = next(get_db())
        db_suppliers = db.query(DBSupplier).all()
        
        return [
            Supplier(
                id=db_supplier.id,
                name=db_supplier.name,
                logoUrl=db_supplier.logo_url or "",
                website=db_supplier.website or "",
                country=db_supplier.country or "",
                description=db_supplier.description or "",
                contactEmail=db_supplier.contact_email or "",
                contactPhone=db_supplier.contact_phone or "",
                deliveryTime=db_supplier.delivery_time or "",
                isVerified=db_supplier.is_verified
            )
            for db_supplier in db_suppliers
        ]
    
    async def create_product(self, product_data: dict) -> Product:
        """Create a new product"""
        db = next(get_db())
        db_product = DBProduct(
            supplier_id=product_data["supplierId"],
            name=product_data["name"],
            category=product_data["category"],
            description=product_data.get("description", ""),
            price=product_data["price"],
            specifications=product_data["specifications"],
            warranty=product_data.get("warranty", "")
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        
        return Product(
            id=db_product.id,
            supplierId=db_product.supplier_id,
            name=db_product.name,
            category=db_product.category,
            description=db_product.description or "",
            price=db_product.price,
            specifications=db_product.specifications,
            warranty=db_product.warranty or ""
        )
    
    async def get_product_by_id(self, id: int) -> Optional[Product]:
        """Get a product by ID"""
        db = next(get_db())
        db_product = db.query(DBProduct).filter(DBProduct.id == id).first()
        if not db_product:
            return None
        
        return Product(
            id=db_product.id,
            supplierId=db_product.supplier_id,
            name=db_product.name,
            category=db_product.category,
            description=db_product.description or "",
            price=db_product.price,
            specifications=db_product.specifications,
            warranty=db_product.warranty or ""
        )
    
    async def get_products_by_supplier(self, supplier_id: int) -> List[Product]:
        """Get all products for a supplier"""
        db = next(get_db())
        db_products = db.query(DBProduct).filter(DBProduct.supplier_id == supplier_id).all()
        
        return [
            Product(
                id=db_product.id,
                supplierId=db_product.supplier_id,
                name=db_product.name,
                category=db_product.category,
                description=db_product.description or "",
                price=db_product.price,
                specifications=db_product.specifications,
                warranty=db_product.warranty or ""
            )
            for db_product in db_products
        ]
    
    async def get_products_by_category(self, category: str) -> List[Product]:
        """Get all products by category"""
        db = next(get_db())
        db_products = db.query(DBProduct).filter(DBProduct.category.ilike(f"%{category}%")).all()
        
        return [
            Product(
                id=db_product.id,
                supplierId=db_product.supplier_id,
                name=db_product.name,
                category=db_product.category,
                description=db_product.description or "",
                price=db_product.price,
                specifications=db_product.specifications,
                warranty=db_product.warranty or ""
            )
            for db_product in db_products
        ]
    
    async def create_proposal(self, proposal_data: dict) -> Proposal:
        """Create a new proposal"""
        db = next(get_db())
        db_proposal = DBProposal(
            rfq_id=proposal_data["rfqId"],
            product_id=proposal_data["productId"],
            score=proposal_data["score"],
            price_score=proposal_data["priceScore"],
            quality_score=proposal_data["qualityScore"],
            delivery_score=proposal_data["deliveryScore"],
            email_content=proposal_data.get("emailContent")
        )
        db.add(db_proposal)
        db.commit()
        db.refresh(db_proposal)
        
        return Proposal(
            id=db_proposal.id,
            rfqId=db_proposal.rfq_id,
            productId=db_proposal.product_id,
            score=db_proposal.score,
            priceScore=db_proposal.price_score,
            qualityScore=db_proposal.quality_score,
            deliveryScore=db_proposal.delivery_score,
            emailContent=db_proposal.email_content,
            createdAt=db_proposal.created_at
        )
    
    async def get_proposal_by_id(self, id: int) -> Optional[Proposal]:
        """Get a proposal by ID"""
        db = next(get_db())
        db_proposal = db.query(DBProposal).filter(DBProposal.id == id).first()
        if not db_proposal:
            return None
        
        return Proposal(
            id=db_proposal.id,
            rfqId=db_proposal.rfq_id,
            productId=db_proposal.product_id,
            score=db_proposal.score,
            priceScore=db_proposal.price_score,
            qualityScore=db_proposal.quality_score,
            deliveryScore=db_proposal.delivery_score,
            emailContent=db_proposal.email_content,
            createdAt=db_proposal.created_at
        )
    
    async def get_proposals_by_rfq(self, rfq_id: int) -> List[Proposal]:
        """Get all proposals for an RFQ"""
        db = next(get_db())
        db_proposals = db.query(DBProposal).filter(DBProposal.rfq_id == rfq_id).all()
        
        return [
            Proposal(
                id=db_proposal.id,
                rfqId=db_proposal.rfq_id,
                productId=db_proposal.product_id,
                score=db_proposal.score,
                priceScore=db_proposal.price_score,
                qualityScore=db_proposal.quality_score,
                deliveryScore=db_proposal.delivery_score,
                emailContent=db_proposal.email_content,
                createdAt=db_proposal.created_at
            )
            for db_proposal in db_proposals
        ]
    
    # Method to seed the database with sample data
    def initialize_sample_data(self):
        """Initialize the database with sample data"""
        db = next(get_db())
        
        # Only proceed if the database is empty
        if db.query(DBUser).count() == 0:
            # Create test user
            test_user = DBUser(
                username="testuser",
                email="test@example.com",
                full_name="Test User",
                company="Test Company"
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            # Create suppliers
            dell_supplier = DBSupplier(
                name="Dell Technologies",
                logo_url="https://logo.clearbit.com/dell.com",
                website="https://www.dell.com",
                country="USA",
                description="Dell is a multinational technology company that develops, sells, repairs, and supports computers and related products and services.",
                contact_email="sales@dell.com",
                contact_phone="+1-800-624-9897",
                delivery_time="15-30 days",
                is_verified=True
            )
            
            hp_supplier = DBSupplier(
                name="HP Inc.",
                logo_url="https://logo.clearbit.com/hp.com",
                website="https://www.hp.com",
                country="USA",
                description="HP Inc. is an American multinational information technology company that develops personal computers, printers and related supplies.",
                contact_email="sales@hp.com",
                contact_phone="+1-800-474-6836",
                delivery_time="10-20 days",
                is_verified=True
            )
            
            lenovo_supplier = DBSupplier(
                name="Lenovo",
                logo_url="https://logo.clearbit.com/lenovo.com",
                website="https://www.lenovo.com",
                country="China",
                description="Lenovo is a Chinese multinational technology company that designs, develops, manufactures and sells personal computers, tablets, smartphones, workstations, servers, electronic storage, IT management software, and smart TVs.",
                contact_email="sales@lenovo.com",
                contact_phone="+1-855-253-6686",
                delivery_time="20-40 days",
                is_verified=True
            )
            
            db.add_all([dell_supplier, hp_supplier, lenovo_supplier])
            db.commit()
            db.refresh(dell_supplier)
            db.refresh(hp_supplier)
            db.refresh(lenovo_supplier)
            
            # Create products
            # Dell laptop
            dell_laptop = DBProduct(
                supplier_id=dell_supplier.id,
                name="Dell Latitude 7430",
                category="Laptops",
                description="Enterprise-grade business laptop with excellent performance and security features.",
                price=1499.99,
                specifications={
                    "os": "Windows 11 Pro",
                    "processor": "Intel Core i7-1265U",
                    "memory": "16GB DDR4",
                    "storage": "512GB SSD",
                    "display": "14-inch FHD (1920 x 1080)",
                    "battery": "12 hours",
                    "durability": "MIL-STD-810H tested",
                    "connectivity": "Wi-Fi 6E, Bluetooth 5.2"
                },
                warranty="3 years ProSupport"
            )
            
            # HP laptop
            hp_laptop = DBProduct(
                supplier_id=hp_supplier.id,
                name="HP EliteBook 840 G9",
                category="Laptops",
                description="Premium business laptop designed for professionals with advanced security features.",
                price=1399.99,
                specifications={
                    "os": "Windows 11 Pro",
                    "processor": "Intel Core i5-1245U",
                    "memory": "16GB DDR5",
                    "storage": "512GB NVMe SSD",
                    "display": "14-inch FHD (1920 x 1080)",
                    "battery": "10 hours",
                    "durability": "MIL-STD-810H tested",
                    "connectivity": "Wi-Fi 6E, Bluetooth 5.2"
                },
                warranty="3 years HP Care Pack"
            )
            
            # Lenovo laptop
            lenovo_laptop = DBProduct(
                supplier_id=lenovo_supplier.id,
                name="Lenovo ThinkPad X1 Carbon Gen 10",
                category="Laptops",
                description="Ultra-lightweight premium business laptop with exceptional build quality.",
                price=1699.99,
                specifications={
                    "os": "Windows 11 Pro",
                    "processor": "Intel Core i7-1260P",
                    "memory": "16GB LPDDR5",
                    "storage": "1TB SSD",
                    "display": "14-inch WUXGA (1920 x 1200)",
                    "battery": "14 hours",
                    "durability": "MIL-STD-810H tested",
                    "connectivity": "Wi-Fi 6E, Bluetooth 5.2"
                },
                warranty="3 years Lenovo Premier Support"
            )
            
            # Dell monitor
            dell_monitor = DBProduct(
                supplier_id=dell_supplier.id,
                name="Dell UltraSharp U2723QE",
                category="Monitors",
                description="Professional 4K USB-C Hub Monitor with excellent color accuracy.",
                price=599.99,
                specifications={
                    "screenSize": "27 inches",
                    "resolution": "4K UHD (3840 x 2160)",
                    "panelTech": "IPS",
                    "brightness": "400 cd/m²",
                    "contrastRatio": "2000:1",
                    "connectivity": "HDMI, DisplayPort, USB-C",
                    "adjustability": "Height, tilt, swivel, pivot adjustable"
                },
                warranty="3 years Advanced Exchange Service"
            )
            
            # HP monitor
            hp_monitor = DBProduct(
                supplier_id=hp_supplier.id,
                name="HP E27u G4",
                category="Monitors",
                description="Business-class QHD monitor with USB-C and ergonomic stand.",
                price=399.99,
                specifications={
                    "screenSize": "27 inches",
                    "resolution": "QHD (2560 x 1440)",
                    "panelTech": "IPS",
                    "brightness": "300 cd/m²",
                    "contrastRatio": "1000:1",
                    "connectivity": "HDMI, DisplayPort, USB-C",
                    "adjustability": "Height, tilt, swivel adjustable"
                },
                warranty="3 years standard"
            )
            
            # Lenovo monitor
            lenovo_monitor = DBProduct(
                supplier_id=lenovo_supplier.id,
                name="Lenovo ThinkVision P27h-20",
                category="Monitors",
                description="Professional QHD monitor with USB-C docking and factory calibration.",
                price=499.99,
                specifications={
                    "screenSize": "27 inches",
                    "resolution": "QHD (2560 x 1440)",
                    "panelTech": "IPS",
                    "brightness": "350 cd/m²",
                    "contrastRatio": "1000:1",
                    "connectivity": "HDMI, DisplayPort, USB-C",
                    "adjustability": "Height, tilt, swivel, pivot adjustable"
                },
                warranty="3 years Lenovo Premier Support"
            )
            
            db.add_all([dell_laptop, hp_laptop, lenovo_laptop, dell_monitor, hp_monitor, lenovo_monitor])
            db.commit()

# Create an instance of the database storage
storage = DatabaseStorage()