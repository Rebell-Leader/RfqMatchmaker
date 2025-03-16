"""
Sample data generator for the RFQ processing platform.
This module creates sample suppliers and products for testing.
"""

import json
import logging
from sqlalchemy.exc import SQLAlchemyError
from .database import SessionLocal, User, Supplier, Product

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_data():
    """Create sample suppliers and products for testing"""
    db = SessionLocal()
    try:
        # Check if we already have sample data
        existing_suppliers = db.query(Supplier).count()
        if existing_suppliers > 0:
            logger.info(f"Database already contains {existing_suppliers} suppliers - skipping sample data creation")
            return
        
        # Create a default user if one doesn't exist
        default_user = db.query(User).filter(User.username == "admin").first()
        if not default_user:
            default_user = User(
                username="admin",
                email="admin@example.com",
                full_name="Admin User",
                company="MatchPoint"
            )
            db.add(default_user)
            db.commit()
            logger.info("Created default admin user")
        
        # Create sample suppliers
        suppliers = [
            {
                "name": "Dell Technologies",
                "logo_url": "https://logo.clearbit.com/dell.com",
                "website": "https://www.dell.com",
                "country": "United States",
                "description": "Dell Technologies is an American multinational technology company that develops, sells, repairs, and supports computers and related products and services.",
                "contact_email": "sales@dell.com",
                "contact_phone": "+1-800-624-9897",
                "delivery_time": "10-15 days",
                "is_verified": True
            },
            {
                "name": "HP Inc.",
                "logo_url": "https://logo.clearbit.com/hp.com",
                "website": "https://www.hp.com",
                "country": "United States",
                "description": "HP Inc. is an American multinational information technology company that develops personal computers, printers and related supplies.",
                "contact_email": "sales@hp.com",
                "contact_phone": "+1-800-474-6836",
                "delivery_time": "7-14 days",
                "is_verified": True
            },
            {
                "name": "Lenovo",
                "logo_url": "https://logo.clearbit.com/lenovo.com",
                "website": "https://www.lenovo.com",
                "country": "China",
                "description": "Lenovo Group Limited is a Chinese multinational technology company that designs, develops, manufactures, and sells personal computers, tablets, smartphones, workstations, servers, electronic storage devices, IT management software, and smart televisions.",
                "contact_email": "sales@lenovo.com",
                "contact_phone": "+1-855-253-6686",
                "delivery_time": "14-21 days",
                "is_verified": True
            },
            {
                "name": "Samsung Electronics",
                "logo_url": "https://logo.clearbit.com/samsung.com",
                "website": "https://www.samsung.com",
                "country": "South Korea",
                "description": "Samsung Electronics Co., Ltd. is a South Korean multinational electronics company that specializes in consumer electronics, IT & mobile communications, and device solutions.",
                "contact_email": "sales@samsung.com",
                "contact_phone": "+1-800-726-7864",
                "delivery_time": "10-20 days",
                "is_verified": True
            },
            {
                "name": "LG Electronics",
                "logo_url": "https://logo.clearbit.com/lg.com",
                "website": "https://www.lg.com",
                "country": "South Korea",
                "description": "LG Electronics Inc. is a South Korean multinational electronics company that manufactures electronics, appliances, and mobile devices.",
                "contact_email": "sales@lg.com",
                "contact_phone": "+1-800-243-0000",
                "delivery_time": "14-21 days",
                "is_verified": True
            },
            {
                "name": "ASUS",
                "logo_url": "https://logo.clearbit.com/asus.com",
                "website": "https://www.asus.com",
                "country": "Taiwan",
                "description": "ASUSTeK Computer Inc. is a Taiwanese multinational computer and phone hardware and electronics company that develops and manufactures products such as desktops, laptops, netbooks, mobile phones, and computer hardware.",
                "contact_email": "sales@asus.com",
                "contact_phone": "+1-888-678-3688",
                "delivery_time": "15-25 days",
                "is_verified": True
            }
        ]
        
        # Create sample laptop products
        laptop_products = [
            {
                "supplier_name": "Dell Technologies",
                "name": "Dell Latitude 5520",
                "category": "Laptops",
                "description": "Business laptop with excellent durability and performance",
                "price": 999.99,
                "specifications": {
                    "processor": "Intel Core i5-1135G7",
                    "memory": "16 GB DDR4",
                    "storage": "512 GB SSD",
                    "display": "15.6-inch FHD (1920 x 1080)",
                    "battery": "Up to 10 hours",
                    "durability": "MIL-STD-810H tested",
                    "connectivity": "USB-C, USB-A, HDMI, RJ-45",
                    "os": "Windows 11 Pro"
                },
                "warranty": "3 years ProSupport"
            },
            {
                "supplier_name": "Dell Technologies",
                "name": "Dell XPS 13",
                "category": "Laptops",
                "description": "Premium ultrabook with InfinityEdge display",
                "price": 1299.99,
                "specifications": {
                    "processor": "Intel Core i7-1165G7",
                    "memory": "16 GB LPDDR4x",
                    "storage": "1 TB PCIe NVMe SSD",
                    "display": "13.4-inch FHD+ (1920 x 1200)",
                    "battery": "Up to 12 hours",
                    "durability": "Aluminum chassis",
                    "connectivity": "Thunderbolt 4, USB-C",
                    "os": "Windows 11 Pro"
                },
                "warranty": "1 year Premium Support"
            },
            {
                "supplier_name": "HP Inc.",
                "name": "HP EliteBook 840 G8",
                "category": "Laptops",
                "description": "Enterprise-grade laptop with security features",
                "price": 1199.99,
                "specifications": {
                    "processor": "Intel Core i5-1145G7",
                    "memory": "16 GB DDR4",
                    "storage": "512 GB SSD",
                    "display": "14-inch FHD (1920 x 1080)",
                    "battery": "Up to 10 hours",
                    "durability": "MIL-STD-810H tested",
                    "connectivity": "USB-C, USB-A, HDMI, Dock connector",
                    "os": "Windows 11 Pro"
                },
                "warranty": "3 years HP Care Pack"
            },
            {
                "supplier_name": "HP Inc.",
                "name": "HP Spectre x360",
                "category": "Laptops",
                "description": "Premium convertible laptop with touch display",
                "price": 1399.99,
                "specifications": {
                    "processor": "Intel Core i7-1165G7",
                    "memory": "16 GB LPDDR4x",
                    "storage": "1 TB PCIe NVMe SSD",
                    "display": "13.3-inch FHD (1920 x 1080) touch",
                    "battery": "Up to 12 hours",
                    "durability": "CNC aluminum chassis",
                    "connectivity": "Thunderbolt 4, USB-C, USB-A",
                    "os": "Windows 11 Home"
                },
                "warranty": "1 year limited warranty"
            },
            {
                "supplier_name": "Lenovo",
                "name": "Lenovo ThinkPad X1 Carbon Gen 9",
                "category": "Laptops",
                "description": "Premium business ultrabook with durability",
                "price": 1499.99,
                "specifications": {
                    "processor": "Intel Core i7-1165G7",
                    "memory": "16 GB LPDDR4x",
                    "storage": "1 TB PCIe SSD",
                    "display": "14-inch FHD+ (1920 x 1200)",
                    "battery": "Up to 16 hours",
                    "durability": "MIL-STD-810H tested, carbon fiber chassis",
                    "connectivity": "Thunderbolt 4, USB-A, HDMI",
                    "os": "Windows 11 Pro"
                },
                "warranty": "3 years ThinkPad warranty"
            },
            {
                "supplier_name": "Lenovo",
                "name": "Lenovo IdeaPad 5",
                "category": "Laptops",
                "description": "Mid-range laptop with good performance",
                "price": 699.99,
                "specifications": {
                    "processor": "AMD Ryzen 5 5500U",
                    "memory": "8 GB DDR4",
                    "storage": "512 GB SSD",
                    "display": "15.6-inch FHD (1920 x 1080)",
                    "battery": "Up to 12 hours",
                    "durability": "Aluminum top cover",
                    "connectivity": "USB-C, USB-A, HDMI, SD card reader",
                    "os": "Windows 11 Home"
                },
                "warranty": "1 year limited warranty"
            },
            {
                "supplier_name": "ASUS",
                "name": "ASUS ZenBook 14",
                "category": "Laptops",
                "description": "Compact and lightweight ultrabook",
                "price": 899.99,
                "specifications": {
                    "processor": "AMD Ryzen 7 5800H",
                    "memory": "16 GB LPDDR4X",
                    "storage": "512 GB PCIe SSD",
                    "display": "14-inch FHD (1920 x 1080)",
                    "battery": "Up to 10 hours",
                    "durability": "Military-grade durability",
                    "connectivity": "Thunderbolt 4, USB-A, HDMI",
                    "os": "Windows 11 Home"
                },
                "warranty": "1 year ASUS global warranty"
            }
        ]
        
        # Create sample monitor products
        monitor_products = [
            {
                "supplier_name": "Dell Technologies",
                "name": "Dell UltraSharp U2720Q",
                "category": "Monitors",
                "description": "27-inch 4K USB-C Monitor",
                "price": 549.99,
                "specifications": {
                    "screenSize": "27 inches",
                    "resolution": "3840 x 2160 (4K UHD)",
                    "panelTech": "IPS",
                    "brightness": "350 nits",
                    "contrastRatio": "1300:1",
                    "connectivity": "HDMI, DisplayPort, USB-C with 90W power delivery",
                    "adjustability": "Height, tilt, swivel, pivot",
                    "refreshRate": "60 Hz"
                },
                "warranty": "3 years Advanced Exchange Service"
            },
            {
                "supplier_name": "Dell Technologies",
                "name": "Dell P2419H",
                "category": "Monitors",
                "description": "24-inch FHD Monitor for Business",
                "price": 199.99,
                "specifications": {
                    "screenSize": "24 inches",
                    "resolution": "1920 x 1080 (Full HD)",
                    "panelTech": "IPS",
                    "brightness": "250 nits",
                    "contrastRatio": "1000:1",
                    "connectivity": "HDMI, DisplayPort, VGA",
                    "adjustability": "Height, tilt, swivel, pivot",
                    "refreshRate": "60 Hz"
                },
                "warranty": "3 years Advanced Exchange Service"
            },
            {
                "supplier_name": "HP Inc.",
                "name": "HP E27u G4",
                "category": "Monitors",
                "description": "27-inch QHD USB-C Monitor",
                "price": 379.99,
                "specifications": {
                    "screenSize": "27 inches",
                    "resolution": "2560 x 1440 (QHD)",
                    "panelTech": "IPS",
                    "brightness": "300 nits",
                    "contrastRatio": "1000:1",
                    "connectivity": "HDMI, DisplayPort, USB-C",
                    "adjustability": "Height, tilt, swivel, pivot",
                    "refreshRate": "60 Hz"
                },
                "warranty": "3 years HP standard warranty"
            },
            {
                "supplier_name": "HP Inc.",
                "name": "HP P24h G4",
                "category": "Monitors",
                "description": "24-inch FHD Monitor",
                "price": 209.99,
                "specifications": {
                    "screenSize": "23.8 inches",
                    "resolution": "1920 x 1080 (Full HD)",
                    "panelTech": "IPS",
                    "brightness": "250 nits",
                    "contrastRatio": "1000:1",
                    "connectivity": "HDMI, DisplayPort, VGA",
                    "adjustability": "Height, tilt",
                    "refreshRate": "60 Hz"
                },
                "warranty": "3 years HP standard warranty"
            },
            {
                "supplier_name": "Samsung Electronics",
                "name": "Samsung S27R650",
                "category": "Monitors",
                "description": "27-inch FHD Monitor with USB-C",
                "price": 259.99,
                "specifications": {
                    "screenSize": "27 inches",
                    "resolution": "1920 x 1080 (Full HD)",
                    "panelTech": "IPS",
                    "brightness": "250 nits",
                    "contrastRatio": "1000:1",
                    "connectivity": "HDMI, DisplayPort, USB-C",
                    "adjustability": "Height, tilt, swivel, pivot",
                    "refreshRate": "60 Hz"
                },
                "warranty": "3 years Samsung warranty"
            },
            {
                "supplier_name": "Samsung Electronics",
                "name": "Samsung S32A600U",
                "category": "Monitors",
                "description": "32-inch UHD Monitor",
                "price": 399.99,
                "specifications": {
                    "screenSize": "32 inches",
                    "resolution": "3840 x 2160 (4K UHD)",
                    "panelTech": "VA",
                    "brightness": "300 nits",
                    "contrastRatio": "2500:1",
                    "connectivity": "HDMI, DisplayPort",
                    "adjustability": "Height, tilt",
                    "refreshRate": "60 Hz"
                },
                "warranty": "3 years Samsung warranty"
            },
            {
                "supplier_name": "LG Electronics",
                "name": "LG 27QN880-B",
                "category": "Monitors",
                "description": "27-inch QHD Monitor with Ergo Stand",
                "price": 349.99,
                "specifications": {
                    "screenSize": "27 inches",
                    "resolution": "2560 x 1440 (QHD)",
                    "panelTech": "IPS",
                    "brightness": "350 nits",
                    "contrastRatio": "1000:1",
                    "connectivity": "HDMI, DisplayPort, USB-C",
                    "adjustability": "Ergo stand with clamp (extend, retract, swivel, height, pivot)",
                    "refreshRate": "75 Hz"
                },
                "warranty": "1 year LG limited warranty"
            },
            {
                "supplier_name": "LG Electronics",
                "name": "LG 24MP400",
                "category": "Monitors",
                "description": "24-inch FHD IPS Monitor",
                "price": 149.99,
                "specifications": {
                    "screenSize": "24 inches",
                    "resolution": "1920 x 1080 (Full HD)",
                    "panelTech": "IPS",
                    "brightness": "250 nits",
                    "contrastRatio": "1000:1",
                    "connectivity": "HDMI, VGA",
                    "adjustability": "Tilt only",
                    "refreshRate": "75 Hz"
                },
                "warranty": "1 year LG limited warranty"
            }
        ]
        
        # Add suppliers to the database
        db_suppliers = {}
        for supplier_data in suppliers:
            supplier = Supplier(**supplier_data)
            db.add(supplier)
            db.flush()  # Flush to get supplier ID
            db_suppliers[supplier.name] = supplier
            logger.info(f"Added supplier: {supplier.name}")
        
        # Add laptop products
        for product_data in laptop_products:
            supplier_name = product_data.pop("supplier_name")
            supplier = db_suppliers.get(supplier_name)
            if supplier:
                product_data["supplier_id"] = supplier.id
                product_data["specifications"] = json.dumps(product_data["specifications"])
                product = Product(**product_data)
                db.add(product)
                logger.info(f"Added laptop product: {product.name} from {supplier_name}")
        
        # Add monitor products
        for product_data in monitor_products:
            supplier_name = product_data.pop("supplier_name")
            supplier = db_suppliers.get(supplier_name)
            if supplier:
                product_data["supplier_id"] = supplier.id
                product_data["specifications"] = json.dumps(product_data["specifications"])
                product = Product(**product_data)
                db.add(product)
                logger.info(f"Added monitor product: {product.name} from {supplier_name}")
        
        # Commit all changes
        db.commit()
        logger.info(f"Successfully added {len(suppliers)} suppliers and {len(laptop_products) + len(monitor_products)} products")
        
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
    except Exception as e:
        logger.error(f"Error creating sample data: {str(e)}")
        db.rollback()
    finally:
        db.close()

# Run the sample data creation automatically on import
if __name__ == "__main__":
    create_sample_data()