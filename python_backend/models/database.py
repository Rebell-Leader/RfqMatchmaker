import os
import logging
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text, JSON, ForeignKey, DateTime, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import QueuePool
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database connection string from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable not set - using SQLite for testing")
    DATABASE_URL = "sqlite:///./test.db"

try:
    # Create SQLAlchemy engine with proper connection pooling and timeout settings
    # Add connect_args only for PostgreSQL
    connect_args = {}
    if DATABASE_URL.startswith('postgresql'):
        connect_args = {"connect_timeout": 10}  # PostgreSQL connection timeout
    
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,  # Recycle connections after 30 minutes
        connect_args=connect_args
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info(f"Database connection established successfully")
except Exception as e:
    logger.error(f"Database connection error: {str(e)}")
    # Fallback to SQLite for testing if PostgreSQL fails
    DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.warning(f"Using SQLite fallback database at {DATABASE_URL}")

Base = declarative_base()

# Define database models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, index=True)
    full_name = Column(String, nullable=True)
    company = Column(String, nullable=True)
    
    rfqs = relationship("RFQ", back_populates="user")

class RFQ(Base):
    __tablename__ = "rfqs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    original_content = Column(Text)
    extracted_requirements = Column(JSON)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User", back_populates="rfqs")
    proposals = relationship("Proposal", back_populates="rfq")

class Supplier(Base):
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    logo_url = Column(String, nullable=True)
    website = Column(String, nullable=True)
    country = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    delivery_time = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    
    products = relationship("Product", back_populates="supplier")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    name = Column(String, index=True)
    category = Column(String, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float)
    specifications = Column(JSON)
    warranty = Column(String, nullable=True)
    
    supplier = relationship("Supplier", back_populates="products")
    proposals = relationship("Proposal", back_populates="product")

class Proposal(Base):
    __tablename__ = "proposals"
    
    id = Column(Integer, primary_key=True, index=True)
    rfq_id = Column(Integer, ForeignKey("rfqs.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    score = Column(Float)
    price_score = Column(Float)
    quality_score = Column(Float)
    delivery_score = Column(Float)
    email_content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    rfq = relationship("RFQ", back_populates="proposals")
    product = relationship("Product", back_populates="proposals")

# Create all tables in the database
def create_tables():
    Base.metadata.create_all(bind=engine)

# Get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()