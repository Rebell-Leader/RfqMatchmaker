from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router

def create_app():
    """Create and configure the FastAPI application"""
    # Create FastAPI app
    app = FastAPI(
        title="RFQ Processor API",
        description="API for processing RFQs, matching suppliers, and generating proposals",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For development; restrict in production
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
            "message": "Welcome to the RFQ Processor API", 
            "docs_url": "/docs"
        }
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "ok"}
    
    return app