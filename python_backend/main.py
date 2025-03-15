"""
Main entry point for the RFQ processing platform.
"""

import os
import uvicorn
from python_backend.api.app import create_app

# Create FastAPI application
app = create_app()

# Run the API server if executed directly
if __name__ == "__main__":
    # Use environment variable for port if available, otherwise default to 8000
    port = int(os.environ.get("PORT", 8000))
    
    # Run the server
    uvicorn.run(
        "python_backend.main:app",
        host="0.0.0.0",  # Bind to all interfaces
        port=port,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )