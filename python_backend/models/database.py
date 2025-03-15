import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text, JSON, ForeignKey, DateTime, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import json
from datetime import datetime

# Get database connection string from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# Create SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
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