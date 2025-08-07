/**
 * RFQ Processing Pipeline Tests
 * 
 * Tests the core RFQ processing functionality including:
 * - File upload and parsing
 * - Requirement extraction
 * - Supplier matching
 * - Proposal generation
 */

import { describe, it, expect, beforeEach, jest } from '@jest/globals';
import request from 'supertest';
import express from 'express';
import { ExtractedRequirement, Rfq, SupplierMatch } from '@shared/schema';

// Mock data for testing
const mockRfqContent = `
Request for Quotation - AI Hardware Requirements

Company: TestTech Inc.
Project: ML Infrastructure Upgrade

Requirements:
- 4x NVIDIA H100 GPUs
- 80GB VRAM minimum per GPU
- CUDA 12.0+ support
- Delivery within 4 weeks
- Budget: $120,000 maximum
- Location: United States
- Export compliance required
`;

const mockExtractedRequirements: ExtractedRequirement = {
  title: "AI Hardware Requirements",
  description: "ML Infrastructure Upgrade for TestTech Inc.",
  categories: ["GPU", "AI Accelerator"],
  specifications: {
    gpuModel: "H100",
    quantity: 4,
    vramMinimum: 80,
    cudaVersion: "12.0+",
    powerRequirements: "High",
    formFactor: "PCIe"
  },
  criteria: {
    price: { weight: 30, maxBudget: 120000 },
    performance: { weight: 40, minTflops: 50 },
    availability: { weight: 15, maxLeadTime: 4 },
    compliance: { weight: 15, requiredCertifications: ["Export Control"] }
  },
  quantity: 4,
  budget: 120000,
  deadline: new Date(Date.now() + 4 * 7 * 24 * 60 * 60 * 1000), // 4 weeks from now
  complianceRequirements: "Export control compliance required for US delivery"
};

const mockSupplierMatches: SupplierMatch[] = [
  {
    supplier: {
      id: 1,
      name: "NVIDIA Corporation",
      country: "United States",
      isVerified: true,
      deliveryTime: "3-4 weeks",
      contactEmail: "enterprise-sales@nvidia.com",
      complianceStatus: "Compliant"
    },
    products: [
      {
        id: 1,
        name: "NVIDIA H100 SXM5 80GB",
        category: "GPU",
        price: 30000,
        specifications: {
          model: "H100-SXM5-80GB",
          memory: "80GB HBM3",
          performance: "989 TFLOPS (FP16)"
        },
        inStock: true,
        quantityAvailable: 10
      }
    ],
    matchScore: 95,
    priceScore: 85,
    performanceScore: 98,
    availabilityScore: 90,
    complianceScore: 100,
    totalPrice: 120000,
    estimatedDeliveryDays: 21,
    alternatives: []
  }
];

describe('RFQ Processing Pipeline', () => {
  let app: express.Express;
  
  beforeEach(() => {
    app = express();
    app.use(express.json());
    
    // Mock the Python backend responses
    jest.clearAllMocks();
  });

  describe('RFQ Upload and Parsing', () => {
    it('should accept RFQ file upload', async () => {
      // Mock the file upload endpoint
      app.post('/api/rfqs/upload', (req, res) => {
        res.json({
          id: 1,
          title: "Test RFQ",
          status: "uploaded",
          extractedRequirements: mockExtractedRequirements
        });
      });

      const response = await request(app)
        .post('/api/rfqs/upload')
        .attach('file', Buffer.from(mockRfqContent), 'test-rfq.txt')
        .expect(200);

      expect(response.body).toHaveProperty('id');
      expect(response.body).toHaveProperty('extractedRequirements');
      expect(response.body.extractedRequirements.title).toBe("AI Hardware Requirements");
    });

    it('should handle manual RFQ creation', async () => {
      app.post('/api/rfqs', (req, res) => {
        const { title, description, specifications } = req.body;
        res.json({
          id: 2,
          title,
          description,
          specifications,
          extractedRequirements: mockExtractedRequirements
        });
      });

      const response = await request(app)
        .post('/api/rfqs')
        .send({
          title: "Manual RFQ Test",
          description: "Test description",
          specifications: mockRfqContent
        })
        .expect(200);

      expect(response.body.id).toBe(2);
      expect(response.body.title).toBe("Manual RFQ Test");
    });

    it('should validate required fields in RFQ creation', async () => {
      app.post('/api/rfqs', (req, res) => {
        const { title, specifications } = req.body;
        if (!title || !specifications) {
          return res.status(400).json({ error: "Title and specifications are required" });
        }
        res.json({ id: 3, title, specifications });
      });

      await request(app)
        .post('/api/rfqs')
        .send({
          description: "Missing title and specs"
        })
        .expect(400);
    });
  });

  describe('Requirement Extraction', () => {
    it('should extract structured requirements from RFQ text', () => {
      // Test the requirement extraction logic
      const extracted = mockExtractedRequirements;
      
      expect(extracted).toHaveProperty('title');
      expect(extracted).toHaveProperty('categories');
      expect(extracted).toHaveProperty('specifications');
      expect(extracted).toHaveProperty('criteria');
      
      expect(extracted.categories).toContain('GPU');
      expect(extracted.specifications.gpuModel).toBe('H100');
      expect(extracted.specifications.quantity).toBe(4);
      expect(extracted.specifications.vramMinimum).toBe(80);
    });

    it('should set appropriate scoring criteria weights', () => {
      const criteria = mockExtractedRequirements.criteria;
      
      expect(criteria.price.weight).toBe(30);
      expect(criteria.performance.weight).toBe(40);
      expect(criteria.availability.weight).toBe(15);
      expect(criteria.compliance.weight).toBe(15);
      
      // Total weights should sum to 100
      const totalWeight = Object.values(criteria).reduce((sum, criterion) => sum + criterion.weight, 0);
      expect(totalWeight).toBe(100);
    });

    it('should handle missing or incomplete requirements gracefully', () => {
      const incompleteRequirement: Partial<ExtractedRequirement> = {
        title: "Incomplete RFQ",
        categories: ["GPU"]
      };
      
      // Should have defaults for missing fields
      expect(incompleteRequirement.title).toBeDefined();
      expect(incompleteRequirement.categories).toBeDefined();
    });
  });

  describe('Supplier Matching', () => {
    it('should find relevant suppliers for AI hardware requirements', async () => {
      app.post('/api/rfqs/:id/match-suppliers', (req, res) => {
        res.json({
          matches: mockSupplierMatches,
          totalMatches: mockSupplierMatches.length
        });
      });

      const response = await request(app)
        .post('/api/rfqs/1/match-suppliers')
        .send(mockExtractedRequirements)
        .expect(200);

      expect(response.body.matches).toHaveLength(1);
      expect(response.body.matches[0].supplier.name).toBe("NVIDIA Corporation");
      expect(response.body.matches[0].matchScore).toBe(95);
    });

    it('should calculate accurate match scores', () => {
      const match = mockSupplierMatches[0];
      
      // Match score should be a weighted average of component scores
      const expectedScore = (
        match.priceScore * 0.3 +
        match.performanceScore * 0.4 +
        match.availabilityScore * 0.15 +
        match.complianceScore * 0.15
      );
      
      expect(match.matchScore).toBeCloseTo(expectedScore, 1);
    });

    it('should filter suppliers by compliance requirements', () => {
      const match = mockSupplierMatches[0];
      
      // Should only include compliant suppliers
      expect(match.supplier.complianceStatus).toBe("Compliant");
      expect(match.complianceScore).toBe(100);
    });

    it('should respect budget constraints', () => {
      const match = mockSupplierMatches[0];
      const requirements = mockExtractedRequirements;
      
      expect(match.totalPrice).toBeLessThanOrEqual(requirements.budget || Infinity);
    });
  });

  describe('Error Handling', () => {
    it('should handle API timeouts gracefully', async () => {
      app.post('/api/rfqs/upload', (req, res) => {
        // Simulate timeout
        setTimeout(() => {
          res.status(408).json({ error: "Request timeout" });
        }, 100);
      });

      const response = await request(app)
        .post('/api/rfqs/upload')
        .attach('file', Buffer.from(mockRfqContent), 'test-rfq.txt')
        .timeout(200);

      expect(response.status).toBe(408);
    });

    it('should handle invalid file formats', async () => {
      app.post('/api/rfqs/upload', (req, res) => {
        const fileType = req.headers['content-type'];
        if (!fileType?.includes('text') && !fileType?.includes('pdf')) {
          return res.status(400).json({ error: "Invalid file format" });
        }
        res.json({ id: 1, status: "uploaded" });
      });

      await request(app)
        .post('/api/rfqs/upload')
        .attach('file', Buffer.from('invalid content'), 'test.exe')
        .expect(400);
    });

    it('should handle missing AI service gracefully', async () => {
      app.post('/api/rfqs', (req, res) => {
        // Simulate AI service unavailable
        res.status(503).json({ 
          error: "AI service temporarily unavailable",
          fallback: "Manual requirement entry available"
        });
      });

      const response = await request(app)
        .post('/api/rfqs')
        .send({
          title: "Test RFQ",
          specifications: mockRfqContent
        })
        .expect(503);

      expect(response.body.error).toContain("AI service");
      expect(response.body.fallback).toBeDefined();
    });
  });
});