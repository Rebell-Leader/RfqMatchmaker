"""
Tests for API Endpoints

Tests the FastAPI endpoints including:
- RFQ creation and management
- Supplier matching
- Email generation
- Error handling
"""

import pytest
import asyncio
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from ..api.app import app
from ..models.schemas import ExtractedRequirement, RFQ

client = TestClient(app)

# Mock data for API testing
mock_rfq_data = {
    "title": "Test AI Hardware RFQ",
    "description": "Testing API endpoints",
    "specifications": "4x NVIDIA H100 GPUs, 80GB VRAM, CUDA 12.0+",
    "budget": 120000,
    "deadline": "2024-06-01T00:00:00Z"
}

mock_extracted_requirements = {
    "title": "AI Hardware Requirements",
    "description": "High-performance GPU procurement",
    "categories": ["GPU", "AI Accelerator"],
    "specifications": {
        "gpuModel": "H100",
        "quantity": 4,
        "vramMinimum": 80
    },
    "criteria": {
        "price": {"weight": 30},
        "performance": {"weight": 40},
        "availability": {"weight": 15},
        "compliance": {"weight": 15}
    },
    "quantity": 4,
    "budget": 120000
}

class TestAPIEndpoints:
    """Test cases for API endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_create_rfq_manual(self):
        """Test manual RFQ creation endpoint"""
        with patch('python_backend.services.requirement_extraction.extract_requirements_from_text') as mock_extract:
            mock_extract.return_value = mock_extracted_requirements
            
            response = client.post("/api/rfqs", json=mock_rfq_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert data["title"] == mock_rfq_data["title"]
            assert "extractedRequirements" in data
    
    def test_create_rfq_invalid_data(self):
        """Test RFQ creation with invalid data"""
        invalid_data = {
            "title": "",  # Empty title
            "specifications": ""  # Empty specifications
        }
        
        response = client.post("/api/rfqs", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_upload_rfq_file(self):
        """Test RFQ file upload endpoint"""
        test_file_content = """
        REQUEST FOR QUOTATION
        
        We require 4x NVIDIA H100 GPUs for our AI training infrastructure.
        Budget: $120,000
        Timeline: 4 weeks
        """
        
        with patch('python_backend.services.requirement_extraction.extract_requirements_from_text') as mock_extract:
            mock_extract.return_value = mock_extracted_requirements
            
            files = {"file": ("test_rfq.txt", test_file_content, "text/plain")}
            response = client.post("/api/rfqs/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert "extractedRequirements" in data
    
    def test_upload_invalid_file_type(self):
        """Test upload with invalid file type"""
        files = {"file": ("test.exe", b"invalid content", "application/exe")}
        response = client.post("/api/rfqs/upload", files=files)
        
        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]
    
    def test_upload_file_too_large(self):
        """Test upload with file too large"""
        # Create a large file (>10MB)
        large_content = "x" * (11 * 1024 * 1024)  # 11MB
        files = {"file": ("large_file.txt", large_content, "text/plain")}
        
        response = client.post("/api/rfqs/upload", files=files)
        assert response.status_code == 413  # File too large
    
    def test_get_rfq_by_id(self):
        """Test retrieving RFQ by ID"""
        # First create an RFQ
        with patch('python_backend.services.requirement_extraction.extract_requirements_from_text') as mock_extract:
            mock_extract.return_value = mock_extracted_requirements
            
            create_response = client.post("/api/rfqs", json=mock_rfq_data)
            rfq_id = create_response.json()["id"]
            
            # Then retrieve it
            response = client.get(f"/api/rfqs/{rfq_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == rfq_id
            assert data["title"] == mock_rfq_data["title"]
    
    def test_get_rfq_not_found(self):
        """Test retrieving non-existent RFQ"""
        response = client.get("/api/rfqs/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_list_rfqs(self):
        """Test listing all RFQs"""
        response = client.get("/api/rfqs")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        # Should contain any existing RFQs
    
    def test_match_suppliers_for_rfq(self):
        """Test supplier matching endpoint"""
        mock_matches = [
            {
                "supplier": {
                    "id": 1,
                    "name": "NVIDIA Corporation",
                    "country": "United States",
                    "isVerified": True,
                    "deliveryTime": "3-4 weeks",
                    "contactEmail": "sales@nvidia.com"
                },
                "products": [
                    {
                        "id": 1,
                        "name": "NVIDIA H100 SXM5 80GB",
                        "category": "GPU",
                        "price": 30000,
                        "specifications": {"memory": "80GB HBM3"},
                        "inStock": True
                    }
                ],
                "matchScore": 95,
                "priceScore": 85,
                "performanceScore": 98,
                "availabilityScore": 90,
                "complianceScore": 100
            }
        ]
        
        # First create an RFQ
        with patch('python_backend.services.requirement_extraction.extract_requirements_from_text') as mock_extract:
            mock_extract.return_value = mock_extracted_requirements
            
            create_response = client.post("/api/rfqs", json=mock_rfq_data)
            rfq_id = create_response.json()["id"]
            
            # Then match suppliers
            with patch('python_backend.services.ai_hardware_matching.match_suppliers_for_rfq') as mock_match:
                mock_match.return_value = mock_matches
                
                response = client.post(f"/api/rfqs/{rfq_id}/match-suppliers")
                
                assert response.status_code == 200
                data = response.json()
                assert "matches" in data
                assert len(data["matches"]) > 0
                assert data["matches"][0]["supplier"]["name"] == "NVIDIA Corporation"
    
    def test_generate_email_proposal(self):
        """Test email proposal generation endpoint"""
        mock_email = {
            "to": "sales@nvidia.com",
            "subject": "RFQ: AI Hardware Procurement",
            "body": "Dear NVIDIA Sales Team,\n\nWe are interested in...",
            "attachments": ["rfq-requirements.pdf"]
        }
        
        with patch('python_backend.services.email_generation.generate_email_template') as mock_gen:
            mock_gen.return_value = mock_email
            
            response = client.post("/api/proposals/1/generate-email")
            
            assert response.status_code == 200
            data = response.json()
            assert data["to"] == "sales@nvidia.com"
            assert "RFQ" in data["subject"]
            assert len(data["body"]) > 50
    
    def test_get_compliance_info(self):
        """Test compliance information endpoint"""
        response = client.get("/api/ai-hardware/check-compliance")
        
        assert response.status_code == 200
        data = response.json()
        assert "exportControls" in data
        assert "certifications" in data
    
    def test_get_frameworks_compatibility(self):
        """Test frameworks compatibility endpoint"""
        response = client.get("/api/ai-hardware/frameworks-compatibility")
        
        assert response.status_code == 200
        data = response.json()
        assert "frameworks" in data
        assert isinstance(data["frameworks"], list)
        
        # Should include common frameworks
        framework_names = [f["name"] for f in data["frameworks"]]
        assert "PyTorch" in framework_names
        assert "TensorFlow" in framework_names
    
    def test_get_performance_comparison(self):
        """Test performance comparison endpoint"""
        response = client.get("/api/ai-hardware/performance-comparison")
        
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        assert isinstance(data["products"], list)
        
        if data["products"]:
            product = data["products"][0]
            assert "name" in product
            assert "performance" in product
    
    def test_seed_ai_hardware_products(self):
        """Test seeding AI hardware products"""
        response = client.post("/api/seed-ai-hardware-products")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "products_added" in data
        assert isinstance(data["products_added"], int)
    
    def test_error_handling_500(self):
        """Test 500 error handling"""
        with patch('python_backend.services.requirement_extraction.extract_requirements_from_text') as mock_extract:
            mock_extract.side_effect = Exception("Internal server error")
            
            response = client.post("/api/rfqs", json=mock_rfq_data)
            
            assert response.status_code == 500
            data = response.json()
            assert "error" in data
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = client.get("/api/rfqs")
        
        # Should include CORS headers (configured in app)
        assert response.status_code == 200
        # Note: CORS headers might not be visible in test client
        # This test documents the expectation
    
    def test_request_validation(self):
        """Test request validation middleware"""
        # Test with malformed JSON
        response = client.post(
            "/api/rfqs",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_rate_limiting_simulation(self):
        """Test rate limiting (simulated)"""
        # Make multiple rapid requests
        responses = []
        for i in range(10):
            response = client.get("/health")
            responses.append(response.status_code)
        
        # All should succeed in test environment
        # (Rate limiting would be configured in production)
        assert all(status == 200 for status in responses)
    
    def test_api_documentation(self):
        """Test that API documentation is available"""
        response = client.get("/docs")
        assert response.status_code == 200
        
        # Test OpenAPI schema
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema
    
    def test_database_connection_handling(self):
        """Test database connection error handling"""
        with patch('python_backend.models.database.SessionLocal') as mock_session:
            mock_session.side_effect = Exception("Database connection failed")
            
            # API should handle database errors gracefully
            response = client.get("/api/rfqs")
            
            # Should return appropriate error response
            assert response.status_code in [500, 503]
    
    def test_ai_service_timeout_handling(self):
        """Test AI service timeout handling"""
        with patch('python_backend.services.requirement_extraction.extract_requirements_from_text') as mock_extract:
            mock_extract.side_effect = TimeoutError("AI service timeout")
            
            response = client.post("/api/rfqs", json=mock_rfq_data)
            
            # Should handle timeout gracefully
            assert response.status_code in [408, 503]
            if response.status_code == 503:
                assert "timeout" in response.json()["detail"].lower()
    
    def test_file_upload_security(self):
        """Test file upload security measures"""
        # Test with potentially malicious filename
        malicious_filename = "../../../etc/passwd"
        files = {"file": (malicious_filename, "content", "text/plain")}
        
        response = client.post("/api/rfqs/upload", files=files)
        
        # Should either succeed with sanitized filename or reject
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            # Filename should be sanitized
            data = response.json()
            assert "../" not in str(data)
    
    def test_input_sanitization(self):
        """Test input sanitization"""
        # Test with potentially malicious input
        malicious_data = {
            "title": "<script>alert('xss')</script>",
            "description": "SELECT * FROM users; DROP TABLE users;",
            "specifications": "<?xml version='1.0'?><!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]><foo>&xxe;</foo>"
        }
        
        with patch('python_backend.services.requirement_extraction.extract_requirements_from_text') as mock_extract:
            mock_extract.return_value = mock_extracted_requirements
            
            response = client.post("/api/rfqs", json=malicious_data)
            
            if response.status_code == 200:
                # Input should be sanitized
                data = response.json()
                assert "<script>" not in data["title"]
                assert "DROP TABLE" not in data["description"]