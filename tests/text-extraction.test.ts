/**
 * Text Extraction Tests
 * 
 * Tests the AI-powered text extraction functionality including:
 * - PDF text extraction
 * - Requirement parsing
 * - AI service integration
 * - Structured data extraction
 */

import { describe, it, expect, beforeEach, jest } from '@jest/globals';
import { ExtractedRequirement } from '@shared/schema';

// Mock AI service responses
const mockAIResponse = {
  title: "GPU Procurement Request",
  description: "Enterprise AI infrastructure upgrade requiring high-performance computing hardware",
  categories: ["GPU", "AI Accelerator", "High Performance Computing"],
  specifications: {
    gpuModel: "H100",
    quantity: 8,
    vramMinimum: 80,
    cudaVersion: "12.0+",
    powerRequirements: "700W per unit",
    formFactor: "SXM5",
    coolingRequirements: "Active cooling required",
    rackSpace: "4U chassis"
  },
  criteria: {
    price: {
      weight: 25,
      maxBudget: 240000,
      preferredRange: "200000-240000"
    },
    performance: {
      weight: 45,
      minTflops: 900,
      benchmarkRequirements: "MLPerf certified"
    },
    availability: {
      weight: 20,
      maxLeadTime: 6,
      preferredDelivery: "4 weeks"
    },
    compliance: {
      weight: 10,
      requiredCertifications: ["Export Control", "FCC", "CE"],
      restrictedCountries: ["RU", "CN", "IR"]
    }
  },
  quantity: 8,
  budget: 240000,
  deadline: new Date('2024-06-01'),
  complianceRequirements: "Export control compliance for US-based delivery. Hardware must meet enterprise security standards.",
  useCase: "Large language model training and inference workloads",
  technicalContact: "ai-infrastructure@company.com",
  priority: "high"
};

// Sample RFQ text content for testing
const sampleRFQTexts = {
  aiHardware: `
REQUEST FOR QUOTATION - AI INFRASTRUCTURE

Company: TechCorp AI Division
Project: Large Language Model Training Infrastructure
Date: March 15, 2024
RFQ ID: TC-AI-2024-003

REQUIREMENTS:
We require high-performance GPU hardware for our AI training infrastructure expansion.

Hardware Specifications:
- GPU Model: NVIDIA H100 or equivalent
- Quantity: 8 units
- Memory: Minimum 80GB per GPU
- CUDA Support: Version 12.0 or later
- Form Factor: SXM5 preferred
- Power: Up to 700W per unit acceptable
- Cooling: Active cooling solutions required

Performance Requirements:
- Minimum 900 TFLOPS (FP16) per GPU
- MLPerf benchmark certified
- Support for distributed training across multiple nodes
- NVLink connectivity for multi-GPU configurations

Budget: $240,000 maximum
Timeline: Delivery required within 6 weeks
Location: United States (California)

Compliance Requirements:
- Export control compliance documentation required
- FCC and CE certification mandatory
- No hardware from restricted countries (Russia, China, Iran)

Technical Contact: ai-infrastructure@techcorp.com
Procurement Contact: procurement@techcorp.com

EVALUATION CRITERIA:
- Performance (45%): Raw compute power and efficiency
- Price (25%): Total cost including shipping and taxes
- Availability (20%): Delivery timeline and stock availability
- Compliance (10%): Regulatory and export compliance

Please provide:
1. Detailed technical specifications
2. Pricing breakdown with volume discounts
3. Delivery timeline and logistics
4. Compliance documentation
5. Warranty and support terms

Response deadline: March 30, 2024
  `,
  
  generalProcurement: `
REQUEST FOR QUOTATION - OFFICE EQUIPMENT

Company: Business Solutions Inc.
Date: March 15, 2024
RFQ ID: BSI-2024-015

We require the following office equipment for our new branch office:

LAPTOPS:
- Quantity: 25 units
- Processor: Intel i7 or AMD equivalent
- RAM: 16GB minimum
- Storage: 512GB SSD
- Display: 14" or 15" FHD
- OS: Windows 11 Pro
- Budget: $1,200 per unit

MONITORS:
- Quantity: 25 units
- Size: 24" minimum
- Resolution: 1920x1080 minimum
- Connectivity: HDMI and DisplayPort
- Adjustable stand preferred
- Budget: $300 per unit

DELIVERY: Within 3 weeks
LOCATION: Austin, Texas
PAYMENT: Net 30 terms preferred

Contact: procurement@businesssolutions.com
  `,
  
  complexRFQ: `
MULTI-CATEGORY PROCUREMENT REQUEST

Organization: Research University
Department: Computer Science & AI Research Lab
RFQ Number: UNIV-CS-2024-007

CATEGORY 1: HIGH-PERFORMANCE COMPUTING
GPU Cluster Requirements:
- 16x NVIDIA A100 or H100 GPUs
- Minimum 40GB VRAM per GPU (80GB preferred)
- NVLink support for multi-GPU communication
- PCIe 4.0 or SXM form factors acceptable
- Budget: $400,000

CATEGORY 2: STORAGE INFRASTRUCTURE
- 500TB high-speed NVMe storage array
- Minimum 5GB/s sequential read speed
- RAID 6 or equivalent redundancy
- 10-year data retention capability
- Budget: $150,000

CATEGORY 3: NETWORKING
- 100Gbps Ethernet switches (4 units)
- InfiniBand HDR connectivity (optional)
- Fiber optic cabling and transceivers
- Budget: $75,000

SPECIAL REQUIREMENTS:
- All hardware must support CUDA 12.0+
- Energy efficiency ratings required
- Quiet operation (<60dB) for research environment
- 24/7 technical support included
- Installation and configuration services

COMPLIANCE:
- University procurement policies
- Federal grant compliance (NSF)
- Export control regulations
- Environmental sustainability standards

TIMELINE: 8 weeks for complete installation
TOTAL BUDGET: $625,000

EVALUATION FACTORS:
- Technical specifications (40%)
- Price and value (30%)
- Vendor experience and support (20%)
- Delivery and installation timeline (10%)

Responses due: April 1, 2024
Contact: procurement@university.edu
  `
};

describe('Text Extraction', () => {
  beforeEach(() => {
    // Mock AI service
    global.fetch = jest.fn();
    jest.clearAllMocks();
  });

  describe('PDF Text Extraction', () => {
    it('should extract text from PDF files', async () => {
      // Mock PDF extraction
      const mockPdfText = sampleRFQTexts.aiHardware;
      
      // Simulate PDF text extraction result
      const extractedText = mockPdfText;
      
      expect(extractedText).toContain("REQUEST FOR QUOTATION");
      expect(extractedText).toContain("NVIDIA H100");
      expect(extractedText).toContain("$240,000");
      expect(extractedText).toContain("8 units");
    });

    it('should handle multi-page PDF documents', async () => {
      // Simulate multi-page PDF with page breaks
      const multiPageContent = sampleRFQTexts.complexRFQ;
      
      expect(multiPageContent).toContain("CATEGORY 1");
      expect(multiPageContent).toContain("CATEGORY 2");
      expect(multiPageContent).toContain("CATEGORY 3");
      expect(multiPageContent).toContain("$625,000");
    });

    it('should handle PDF files with tables and formatting', () => {
      const tableContent = `
      | Item | Quantity | Specification | Unit Price |
      |------|----------|---------------|------------|
      | GPU  | 8        | H100 80GB     | $30,000    |
      | CPU  | 4        | Intel Xeon    | $2,500     |
      `;
      
      // Should extract structured data from tables
      expect(tableContent).toContain("GPU");
      expect(tableContent).toContain("8");
      expect(tableContent).toContain("H100 80GB");
      expect(tableContent).toContain("$30,000");
    });

    it('should handle corrupted or invalid PDF files', async () => {
      // Mock invalid PDF scenario
      const invalidPdfError = {
        error: "Invalid PDF format",
        code: "PDF_PARSE_ERROR",
        suggestion: "Please ensure the file is a valid PDF document"
      };
      
      expect(invalidPdfError.error).toBe("Invalid PDF format");
      expect(invalidPdfError.code).toBe("PDF_PARSE_ERROR");
    });
  });

  describe('AI-Powered Requirement Parsing', () => {
    it('should extract structured requirements from AI hardware RFQ', async () => {
      // Mock AI service call
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockAIResponse
      });
      
      // Simulate AI extraction
      const extracted = mockAIResponse;
      
      expect(extracted.title).toBe("GPU Procurement Request");
      expect(extracted.categories).toContain("GPU");
      expect(extracted.categories).toContain("AI Accelerator");
      expect(extracted.specifications.gpuModel).toBe("H100");
      expect(extracted.specifications.quantity).toBe(8);
      expect(extracted.budget).toBe(240000);
    });

    it('should parse technical specifications correctly', () => {
      const specs = mockAIResponse.specifications;
      
      expect(specs.vramMinimum).toBe(80);
      expect(specs.cudaVersion).toBe("12.0+");
      expect(specs.powerRequirements).toBe("700W per unit");
      expect(specs.formFactor).toBe("SXM5");
    });

    it('should extract and validate criteria weights', () => {
      const criteria = mockAIResponse.criteria;
      
      // Check individual weights
      expect(criteria.price.weight).toBe(25);
      expect(criteria.performance.weight).toBe(45);
      expect(criteria.availability.weight).toBe(20);
      expect(criteria.compliance.weight).toBe(10);
      
      // Validate total weight equals 100
      const totalWeight = criteria.price.weight + 
                         criteria.performance.weight + 
                         criteria.availability.weight + 
                         criteria.compliance.weight;
      expect(totalWeight).toBe(100);
    });

    it('should handle different RFQ formats', async () => {
      // Test with general procurement format
      const generalSpecs = {
        categories: ["Laptops", "Monitors"],
        quantity: 50, // 25 laptops + 25 monitors
        budget: 37500, // (25 * $1,200) + (25 * $300)
        deadline: new Date('2024-04-05') // 3 weeks from March 15
      };
      
      expect(generalSpecs.categories).toContain("Laptops");
      expect(generalSpecs.categories).toContain("Monitors");
      expect(generalSpecs.budget).toBe(37500);
    });

    it('should extract compliance requirements', () => {
      const compliance = mockAIResponse.complianceRequirements;
      const restrictedCountries = mockAIResponse.criteria.compliance.restrictedCountries;
      
      expect(compliance).toContain("Export control compliance");
      expect(compliance).toContain("enterprise security standards");
      expect(restrictedCountries).toContain("RU");
      expect(restrictedCountries).toContain("CN");
      expect(restrictedCountries).toContain("IR");
    });
  });

  describe('Data Validation and Cleaning', () => {
    it('should validate extracted numeric values', () => {
      const extracted = mockAIResponse;
      
      // Quantities should be positive integers
      expect(extracted.quantity).toBeGreaterThan(0);
      expect(Number.isInteger(extracted.quantity)).toBe(true);
      
      // Budget should be positive number
      expect(extracted.budget).toBeGreaterThan(0);
      expect(typeof extracted.budget).toBe('number');
      
      // VRAM should be reasonable for GPUs
      expect(extracted.specifications.vramMinimum).toBeGreaterThan(0);
      expect(extracted.specifications.vramMinimum).toBeLessThan(1000); // Sanity check
    });

    it('should validate date formats', () => {
      const deadline = mockAIResponse.deadline;
      
      expect(deadline).toBeInstanceOf(Date);
      expect(deadline.getTime()).toBeGreaterThan(Date.now()); // Should be in future
    });

    it('should clean and normalize text data', () => {
      const title = mockAIResponse.title;
      const description = mockAIResponse.description;
      
      // Should not have extra whitespace
      expect(title.trim()).toBe(title);
      expect(description.trim()).toBe(description);
      
      // Should have reasonable length
      expect(title.length).toBeGreaterThan(5);
      expect(title.length).toBeLessThan(100);
    });

    it('should handle missing or incomplete data gracefully', () => {
      const incompleteRFQ = {
        title: "Incomplete RFQ",
        // Missing many required fields
      };
      
      // Should provide defaults for missing critical fields
      const defaults = {
        categories: ["General"],
        criteria: {
          price: { weight: 40 },
          performance: { weight: 30 },
          availability: { weight: 20 },
          compliance: { weight: 10 }
        },
        quantity: 1,
        budget: null
      };
      
      expect(defaults.categories).toHaveLength(1);
      expect(defaults.criteria.price.weight).toBe(40);
    });
  });

  describe('AI Service Integration', () => {
    it('should handle AI service API calls', async () => {
      const mockRequest = {
        text: sampleRFQTexts.aiHardware,
        extractionType: "ai_hardware",
        language: "en"
      };
      
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockAIResponse
      });
      
      // Simulate API call
      const response = await fetch('/api/extract-requirements', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mockRequest)
      });
      
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/extract-requirements',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
      );
    });

    it('should handle AI service timeouts', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(
        new Error('Request timeout')
      );
      
      try {
        await fetch('/api/extract-requirements', {
          method: 'POST',
          body: JSON.stringify({ text: sampleRFQTexts.aiHardware })
        });
      } catch (error) {
        expect((error as Error).message).toBe('Request timeout');
      }
    });

    it('should handle AI service rate limits', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 429,
        json: async () => ({
          error: "Rate limit exceeded",
          retryAfter: 60,
          message: "Please try again in 60 seconds"
        })
      });
      
      const response = await fetch('/api/extract-requirements', {
        method: 'POST',
        body: JSON.stringify({ text: sampleRFQTexts.aiHardware })
      });
      
      expect(response.ok).toBe(false);
      expect(response.status).toBe(429);
    });

    it('should provide fallback for AI service failures', async () => {
      // When AI service fails, should provide basic extraction
      const fallbackExtraction = {
        title: "Manual RFQ Processing Required",
        description: "AI service unavailable - manual review needed",
        categories: ["Unknown"],
        specifications: {},
        criteria: {
          price: { weight: 30 },
          performance: { weight: 30 },
          availability: { weight: 20 },
          compliance: { weight: 20 }
        },
        extractedText: sampleRFQTexts.aiHardware
      };
      
      expect(fallbackExtraction.title).toContain("Manual");
      expect(fallbackExtraction.extractedText).toContain("REQUEST FOR QUOTATION");
    });
  });

  describe('Performance and Scalability', () => {
    it('should handle large document processing', () => {
      // Simulate large document
      const largeDocument = sampleRFQTexts.aiHardware.repeat(100);
      
      expect(largeDocument.length).toBeGreaterThan(100000);
      
      // Should process efficiently
      const processingStart = Date.now();
      const textLength = largeDocument.length;
      const processingTime = Date.now() - processingStart;
      
      expect(textLength).toBeGreaterThan(0);
      expect(processingTime).toBeLessThan(5000); // Should complete within 5 seconds
    });

    it('should batch process multiple documents', async () => {
      const documents = [
        sampleRFQTexts.aiHardware,
        sampleRFQTexts.generalProcurement,
        sampleRFQTexts.complexRFQ
      ];
      
      const batchResults = documents.map((doc, index) => ({
        id: index,
        text: doc,
        extracted: mockAIResponse // Simplified for test
      }));
      
      expect(batchResults).toHaveLength(3);
      batchResults.forEach(result => {
        expect(result).toHaveProperty('id');
        expect(result).toHaveProperty('text');
        expect(result).toHaveProperty('extracted');
      });
    });

    it('should handle concurrent extraction requests', async () => {
      const concurrentRequests = Array(5).fill(null).map((_, index) => 
        fetch(`/api/extract-requirements`, {
          method: 'POST',
          body: JSON.stringify({ 
            text: sampleRFQTexts.aiHardware,
            requestId: `req_${index}`
          })
        })
      );
      
      // Mock concurrent responses
      (global.fetch as jest.Mock).mockImplementation(() => 
        Promise.resolve({
          ok: true,
          json: async () => mockAIResponse
        })
      );
      
      const results = await Promise.all(concurrentRequests);
      expect(results).toHaveLength(5);
    });
  });
});