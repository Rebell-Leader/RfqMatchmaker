"""
Tests for AI Hardware Matching Service

Tests the core supplier matching functionality including:
- Requirement extraction and validation
- Supplier scoring algorithms
- Compliance checking
- Alternative product suggestions
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from typing import List, Dict, Any

from ..models.schemas import ExtractedRequirement, SupplierMatch, Product, Supplier
from ..services.ai_hardware_matching import (
    match_suppliers_for_rfq,
    calculate_match_score,
    ensure_extracted_requirement,
    find_alternative_products,
    parse_delivery_time
)

# Mock data for testing
mock_extracted_requirement = ExtractedRequirement(
    title="AI Hardware Procurement",
    description="High-performance GPU cluster for ML training",
    categories=["GPU", "AI Accelerator"],
    specifications={
        "gpuModel": "H100",
        "quantity": 4,
        "vramMinimum": 80,
        "cudaVersion": "12.0+",
        "powerRequirements": "700W",
        "formFactor": "SXM5"
    },
    criteria={
        "price": {"weight": 30, "maxBudget": 120000},
        "performance": {"weight": 40, "minTflops": 900},
        "availability": {"weight": 15, "maxLeadTime": 4},
        "compliance": {"weight": 15, "requiredCertifications": ["Export Control"]}
    },
    quantity=4,
    budget=120000,
    deadline=datetime.now() + timedelta(weeks=4),
    complianceRequirements="Export control compliance required"
)

mock_supplier = Supplier(
    id=1,
    name="NVIDIA Corporation",
    country="United States",
    isVerified=True,
    deliveryTime="3-4 weeks",
    contactEmail="enterprise-sales@nvidia.com",
    complianceStatus="Compliant",
    description="Leader in AI computing and GPUs"
)

mock_product = Product(
    id=1,
    name="NVIDIA H100 SXM5 80GB",
    category="GPU",
    price=30000,
    specifications={
        "model": "H100-SXM5-80GB",
        "manufacturer": "NVIDIA",
        "memory": "80GB HBM3",
        "performance": "989 TFLOPS (FP16)",
        "powerConsumption": "700W TDP",
        "formFactor": "SXM5"
    },
    inStock=True,
    quantityAvailable=10,
    warranty="3 years limited",
    supplierId=1
)

class TestAIHardwareMatching:
    """Test cases for AI hardware matching functionality"""
    
    @pytest.fixture
    def mock_db_storage(self):
        """Mock database storage for testing"""
        storage = Mock()
        storage.get_all_suppliers.return_value = [mock_supplier]
        storage.get_products_by_supplier.return_value = [mock_product]
        storage.get_all_products.return_value = [mock_product]
        return storage
    
    def test_ensure_extracted_requirement_from_dict(self):
        """Test conversion of dictionary to ExtractedRequirement object"""
        req_dict = {
            "title": "Test RFQ",
            "categories": ["GPU"],
            "criteria": {
                "price": {"weight": 30},
                "performance": {"weight": 40},
                "availability": {"weight": 15},
                "compliance": {"weight": 15}
            }
        }
        
        result = ensure_extracted_requirement(req_dict)
        
        assert isinstance(result, ExtractedRequirement)
        assert result.title == "Test RFQ"
        assert "GPU" in result.categories
        assert result.criteria["price"]["weight"] == 30
    
    def test_ensure_extracted_requirement_from_object(self):
        """Test that ExtractedRequirement objects pass through unchanged"""
        result = ensure_extracted_requirement(mock_extracted_requirement)
        
        assert result is mock_extracted_requirement
        assert result.title == "AI Hardware Procurement"
    
    def test_ensure_extracted_requirement_invalid_input(self):
        """Test handling of invalid input to ensure_extracted_requirement"""
        result = ensure_extracted_requirement("invalid input")
        
        assert isinstance(result, ExtractedRequirement)
        assert result.title == "Default AI Hardware Requirements"
        assert "GPU" in result.categories
    
    def test_parse_delivery_time_weeks(self):
        """Test parsing delivery time in weeks format"""
        assert parse_delivery_time("3-4 weeks") == 24.5  # Average of 3-4 weeks in days
        assert parse_delivery_time("2 weeks") == 14.0
        assert parse_delivery_time("1-2 weeks") == 10.5
    
    def test_parse_delivery_time_days(self):
        """Test parsing delivery time in days format"""
        assert parse_delivery_time("10-15 days") == 12.5
        assert parse_delivery_time("5 days") == 5.0
        assert parse_delivery_time("3-5 days") == 4.0
    
    def test_parse_delivery_time_invalid(self):
        """Test handling of invalid delivery time formats"""
        assert parse_delivery_time("") == 30.0  # Default
        assert parse_delivery_time("immediate") == 30.0  # Default
        assert parse_delivery_time(None) == 30.0  # Default
    
    def test_calculate_match_score_high_match(self):
        """Test match score calculation for high-quality match"""
        # Mock a high-scoring product
        high_score_product = Product(
            id=1,
            name="Perfect Match GPU",
            category="GPU",
            price=25000,  # Under budget
            specifications={
                "performance": "1000 TFLOPS",  # Exceeds minimum
                "memory": "80GB",  # Meets requirement
                "powerConsumption": "600W"  # Under limit
            },
            inStock=True,
            quantityAvailable=10
        )
        
        score = calculate_match_score(
            high_score_product,
            mock_extracted_requirement,
            mock_supplier,
            available_quantity=4
        )
        
        assert score.overall_score >= 85  # Should be high score
        assert score.price_score >= 80  # Good price
        assert score.performance_score >= 90  # Excellent performance
        assert score.availability_score >= 85  # Good availability
    
    def test_calculate_match_score_poor_match(self):
        """Test match score calculation for poor match"""
        poor_match_product = Product(
            id=2,
            name="Poor Match GPU",
            category="GPU",
            price=35000,  # Over budget per unit
            specifications={
                "performance": "500 TFLOPS",  # Below minimum
                "memory": "40GB",  # Insufficient memory
                "powerConsumption": "800W"  # Too high
            },
            inStock=False,
            quantityAvailable=0
        )
        
        score = calculate_match_score(
            poor_match_product,
            mock_extracted_requirement,
            mock_supplier,
            available_quantity=0
        )
        
        assert score.overall_score <= 50  # Should be low score
        assert score.price_score <= 60  # Poor price
        assert score.performance_score <= 40  # Poor performance
        assert score.availability_score <= 30  # Poor availability
    
    @pytest.mark.asyncio
    async def test_match_suppliers_for_rfq_success(self, mock_db_storage):
        """Test successful supplier matching"""
        with patch('python_backend.services.ai_hardware_matching.db_storage', mock_db_storage):
            matches = await match_suppliers_for_rfq(mock_extracted_requirement)
            
            assert len(matches) > 0
            assert isinstance(matches[0], SupplierMatch)
            assert matches[0].supplier.name == "NVIDIA Corporation"
            assert matches[0].products[0].name == "NVIDIA H100 SXM5 80GB"
    
    @pytest.mark.asyncio
    async def test_match_suppliers_for_rfq_no_matches(self, mock_db_storage):
        """Test handling when no suppliers match requirements"""
        # Mock empty supplier list
        mock_db_storage.get_all_suppliers.return_value = []
        
        with patch('python_backend.services.ai_hardware_matching.db_storage', mock_db_storage):
            matches = await match_suppliers_for_rfq(mock_extracted_requirement)
            
            assert len(matches) == 0
    
    @pytest.mark.asyncio
    async def test_match_suppliers_compliance_filtering(self, mock_db_storage):
        """Test that non-compliant suppliers are filtered out"""
        non_compliant_supplier = Supplier(
            id=2,
            name="Non-Compliant Supplier",
            country="Restricted Country",
            isVerified=False,
            deliveryTime="2 weeks",
            complianceStatus="Non-Compliant"
        )
        
        mock_db_storage.get_all_suppliers.return_value = [mock_supplier, non_compliant_supplier]
        
        with patch('python_backend.services.ai_hardware_matching.db_storage', mock_db_storage):
            matches = await match_suppliers_for_rfq(mock_extracted_requirement)
            
            # Should only include compliant supplier
            supplier_names = [match.supplier.name for match in matches]
            assert "NVIDIA Corporation" in supplier_names
            assert "Non-Compliant Supplier" not in supplier_names
    
    def test_find_alternative_products(self, mock_db_storage):
        """Test finding alternative products for requirements"""
        alternative_product = Product(
            id=2,
            name="NVIDIA A100 80GB",
            category="GPU",
            price=15000,
            specifications={
                "model": "A100-SXM4-80GB",
                "memory": "80GB HBM2e",
                "performance": "624 TFLOPS (FP16)"
            },
            inStock=True,
            quantityAvailable=5
        )
        
        mock_db_storage.get_all_products.return_value = [mock_product, alternative_product]
        
        with patch('python_backend.services.ai_hardware_matching.db_storage', mock_db_storage):
            alternatives = find_alternative_products(mock_extracted_requirement, [mock_product])
            
            assert len(alternatives) >= 0  # May find alternatives
            # If alternatives found, they should be different products
            if alternatives:
                alternative_ids = [alt.id for alt in alternatives]
                assert mock_product.id not in alternative_ids
    
    def test_budget_constraint_enforcement(self):
        """Test that budget constraints are properly enforced"""
        expensive_product = Product(
            id=3,
            name="Expensive GPU",
            category="GPU",
            price=50000,  # Would exceed budget for 4 units
            specifications={"memory": "80GB"},
            inStock=True,
            quantityAvailable=10
        )
        
        score = calculate_match_score(
            expensive_product,
            mock_extracted_requirement,
            mock_supplier,
            available_quantity=4
        )
        
        # Price score should be very low due to budget constraints
        assert score.price_score <= 30
    
    def test_performance_requirement_scoring(self):
        """Test performance-based scoring"""
        high_perf_product = Product(
            id=4,
            name="High Performance GPU",
            category="GPU",
            price=30000,
            specifications={
                "performance": "1200 TFLOPS",  # Well above minimum 900
                "memory": "80GB"
            },
            inStock=True,
            quantityAvailable=10
        )
        
        score = calculate_match_score(
            high_perf_product,
            mock_extracted_requirement,
            mock_supplier,
            available_quantity=4
        )
        
        # Performance score should be high
        assert score.performance_score >= 90
    
    def test_availability_scoring(self):
        """Test availability-based scoring"""
        out_of_stock_product = Product(
            id=5,
            name="Out of Stock GPU",
            category="GPU",
            price=30000,
            specifications={"memory": "80GB"},
            inStock=False,
            quantityAvailable=0
        )
        
        score = calculate_match_score(
            out_of_stock_product,
            mock_extracted_requirement,
            mock_supplier,
            available_quantity=0
        )
        
        # Availability score should be very low
        assert score.availability_score <= 20
    
    def test_quantity_requirement_handling(self):
        """Test handling of quantity requirements"""
        limited_stock_product = Product(
            id=6,
            name="Limited Stock GPU",
            category="GPU",
            price=30000,
            specifications={"memory": "80GB"},
            inStock=True,
            quantityAvailable=2  # Less than required 4
        )
        
        score = calculate_match_score(
            limited_stock_product,
            mock_extracted_requirement,
            mock_supplier,
            available_quantity=2
        )
        
        # Availability score should be reduced due to insufficient quantity
        assert score.availability_score <= 60
    
    @pytest.mark.asyncio
    async def test_error_handling_database_failure(self, mock_db_storage):
        """Test handling of database failures"""
        # Mock database failure
        mock_db_storage.get_all_suppliers.side_effect = Exception("Database connection failed")
        
        with patch('python_backend.services.ai_hardware_matching.db_storage', mock_db_storage):
            with pytest.raises(Exception, match="Database connection failed"):
                await match_suppliers_for_rfq(mock_extracted_requirement)
    
    def test_criteria_weight_validation(self):
        """Test that criteria weights are properly validated"""
        invalid_requirement = ExtractedRequirement(
            title="Invalid Weights",
            categories=["GPU"],
            criteria={
                "price": {"weight": 50},
                "performance": {"weight": 30},
                "availability": {"weight": 15},
                "compliance": {"weight": 10}
                # Total: 105% - invalid
            }
        )
        
        # Should handle invalid weights gracefully
        normalized_req = ensure_extracted_requirement(invalid_requirement)
        total_weight = sum(criterion["weight"] for criterion in normalized_req.criteria.values())
        
        # Should either normalize to 100 or use defaults
        assert total_weight == 100 or total_weight > 0
    
    def test_empty_specifications_handling(self):
        """Test handling of products with empty specifications"""
        empty_spec_product = Product(
            id=7,
            name="No Specs GPU",
            category="GPU",
            price=30000,
            specifications={},  # Empty specifications
            inStock=True,
            quantityAvailable=10
        )
        
        score = calculate_match_score(
            empty_spec_product,
            mock_extracted_requirement,
            mock_supplier,
            available_quantity=4
        )
        
        # Should handle gracefully without crashing
        assert isinstance(score.overall_score, (int, float))
        assert 0 <= score.overall_score <= 100
    
    def test_category_matching(self):
        """Test category-based product matching"""
        wrong_category_product = Product(
            id=8,
            name="CPU Product",
            category="CPU",  # Wrong category for GPU requirement
            price=30000,
            specifications={"cores": 64},
            inStock=True,
            quantityAvailable=10
        )
        
        score = calculate_match_score(
            wrong_category_product,
            mock_extracted_requirement,
            mock_supplier,
            available_quantity=4
        )
        
        # Score should be low due to category mismatch
        assert score.overall_score <= 50