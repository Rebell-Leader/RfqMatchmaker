from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union

# Equipment requirements schemas
class LaptopRequirements(BaseModel):
    quantity: int = 1
    os: Optional[str] = None
    processor: Optional[str] = None
    memory: Optional[str] = None
    storage: Optional[str] = None
    display: Optional[str] = None
    battery: Optional[str] = None
    durability: Optional[str] = None
    connectivity: Optional[str] = None
    warranty: Optional[str] = None

class MonitorRequirements(BaseModel):
    quantity: int = 1
    screenSize: Optional[str] = None
    resolution: Optional[str] = None
    panelTech: Optional[str] = None
    brightness: Optional[str] = None
    contrastRatio: Optional[str] = None
    connectivity: Optional[str] = None
    adjustability: Optional[str] = None
    warranty: Optional[str] = None

class AwardCriteria(BaseModel):
    price: Dict[str, int] = Field(default={"weight": 50})
    quality: Dict[str, int] = Field(default={"weight": 30})
    delivery: Dict[str, int] = Field(default={"weight": 20})

class ExtractedRequirement(BaseModel):
    title: str
    description: Optional[str] = None
    categories: List[str]
    laptops: Optional[LaptopRequirements] = None
    monitors: Optional[MonitorRequirements] = None
    criteria: AwardCriteria

# Database models
class User(BaseModel):
    id: int
    username: str
    email: str
    fullName: Optional[str] = None
    company: Optional[str] = None

class RFQ(BaseModel):
    id: int
    title: str
    description: str = ""
    originalContent: str
    extractedRequirements: ExtractedRequirement
    userId: int
    createdAt: datetime = Field(default_factory=datetime.now)

class Supplier(BaseModel):
    id: int
    name: str
    logoUrl: str
    website: str
    country: str
    description: str
    contactEmail: str
    contactPhone: str
    deliveryTime: str  # e.g., "15-30 days"
    isVerified: bool = False

class Product(BaseModel):
    id: int
    supplierId: int
    name: str
    category: str  # e.g., "Laptops", "Monitors"
    description: str
    price: float
    specifications: Dict[str, Any]
    warranty: str

class MatchDetails(BaseModel):
    price: float
    quality: float
    delivery: float

class SupplierMatch(BaseModel):
    supplier: Supplier
    product: Product
    matchScore: float
    matchDetails: MatchDetails
    totalPrice: float

class Proposal(BaseModel):
    id: int
    rfqId: int
    productId: int
    score: float
    priceScore: float
    qualityScore: float
    deliveryScore: float
    emailContent: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.now)

# API request/response schemas
class EmailTemplate(BaseModel):
    to: str
    cc: Optional[str] = None
    subject: str
    body: str

class RFQUploadRequest(BaseModel):
    title: str
    description: Optional[str] = None
    specifications: str

class MatchSuppliersRequest(BaseModel):
    rfqId: int

class GenerateEmailRequest(BaseModel):
    proposalId: int

class RFQResponse(BaseModel):
    id: int
    title: str
    description: str
    extractedRequirements: ExtractedRequirement
    createdAt: datetime

class SupplierMatchResponse(BaseModel):
    rfqId: int
    matches: List[SupplierMatch]