from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router

def create_app():
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="RFQ Supplier Matching API",
        description="API for matching suppliers to RFQs using AI",
        version="1.0.0"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, restrict this to specific domains
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(router, prefix="/api")
    
    @app.get("/")
    async def root():
        return {"message": "Welcome to the RFQ Supplier Matching API"}
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    return app