"""
FastAPI application for RFQ processing platform.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .routes import router
from ..models.database import create_tables
from ..models.db_storage import storage

def create_app():
    """Create and configure the FastAPI application"""
    # Create database tables
    create_tables()
    
    # Initialize sample data
    storage.initialize_sample_data()
    
    # Create FastAPI app
    app = FastAPI(
        title="RFQ Processing Platform API",
        description="API for the RFQ processing platform",
        version="1.0.0"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(router, prefix="/api")
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Welcome to the RFQ Processing Platform API",
            "docs_url": "/docs",
            "redoc_url": "/redoc"
        }
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    return app