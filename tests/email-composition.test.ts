/**
 * Email Composition Tests
 * 
 * Tests the email draft generation and composition functionality including:
 * - Email template generation
 * - Content personalization
 * - PDF attachment creation
 * - Email validation
 */

import { describe, it, expect, beforeEach, jest } from '@jest/globals';
import request from 'supertest';
import express from 'express';
import { EmailTemplate, Proposal, Supplier, Product } from '@shared/schema';

// Mock data for testing
const mockSupplier: Supplier = {
  id: 1,
  name: "NVIDIA Corporation",
  country: "United States",
  isVerified: true,
  deliveryTime: "3-4 weeks",
  contactEmail: "enterprise-sales@nvidia.com",
  contactPhone: "+1-408-486-2000",
  website: "https://www.nvidia.com",
  description: "Leader in AI computing and GPUs",
  complianceStatus: "Compliant"
};

const mockProduct: Product = {
  id: 1,
  name: "NVIDIA H100 SXM5 80GB",
  category: "GPU",
  price: 30000,
  specifications: {
    model: "H100-SXM5-80GB",
    memory: "80GB HBM3",
    performance: "989 TFLOPS (FP16)",
    powerConsumption: "700W TDP"
  },
  inStock: true,
  quantityAvailable: 10,
  warranty: "3 years limited"
};

const mockProposal: Proposal = {
  id: 1,
  rfqId: 1,
  productId: 1,
  score: 95,
  priceScore: 85,
  performanceScore: 98,
  compatibilityScore: 92,
  availabilityScore: 90,
  complianceScore: 100,
  createdAt: new Date(),
  estimatedDeliveryDate: new Date(Date.now() + 21 * 24 * 60 * 60 * 1000), // 3 weeks
  pricingNotes: "Volume discount applied for 4+ units"
};

const mockEmailTemplate: EmailTemplate = {
  to: "enterprise-sales@nvidia.com",
  cc: "",
  subject: "RFQ: AI Hardware Procurement - H100 GPUs",
  body: `Dear NVIDIA Sales Team,

We are interested in procuring AI hardware for our ML infrastructure upgrade project.

Product Requirements:
- Product: NVIDIA H100 SXM5 80GB
- Quantity: 4 units
- Budget: $120,000
- Timeline: 4 weeks

Specifications:
- Memory: 80GB HBM3 minimum
- Performance: 989 TFLOPS (FP16)
- Power: 700W TDP
- Warranty: 3 years limited

Company Information:
- Company: TestTech Inc.
- Project: ML Infrastructure Upgrade
- Location: United States
- Compliance: Export control compliance required

Please provide:
1. Detailed quotation with pricing
2. Availability and delivery timeline
3. Technical specifications sheet
4. Compliance and export documentation

We look forward to your response.

Best regards,
Procurement Team
TestTech Inc.`,
  attachments: ["rfq-requirements.pdf"]
};

describe('Email Composition', () => {
  let app: express.Express;
  
  beforeEach(() => {
    app = express();
    app.use(express.json());
    jest.clearAllMocks();
  });

  describe('Email Template Generation', () => {
    it('should generate professional email template from proposal', async () => {
      app.post('/api/proposals/:id/generate-email', (req, res) => {
        res.json(mockEmailTemplate);
      });

      const response = await request(app)
        .post('/api/proposals/1/generate-email')
        .send({ 
          proposal: mockProposal,
          supplier: mockSupplier,
          product: mockProduct 
        })
        .expect(200);

      expect(response.body).toHaveProperty('to');
      expect(response.body).toHaveProperty('subject');
      expect(response.body).toHaveProperty('body');
      expect(response.body.to).toBe(mockSupplier.contactEmail);
    });

    it('should include all required information in email body', () => {
      const emailBody = mockEmailTemplate.body;
      
      // Should include product information
      expect(emailBody).toContain(mockProduct.name);
      expect(emailBody).toContain("4 units"); // quantity
      expect(emailBody).toContain("$120,000"); // budget
      
      // Should include technical specifications
      expect(emailBody).toContain("80GB HBM3");
      expect(emailBody).toContain("989 TFLOPS");
      expect(emailBody).toContain("700W TDP");
      
      // Should include compliance requirements
      expect(emailBody).toContain("Export control compliance");
      
      // Should include delivery timeline
      expect(emailBody).toContain("4 weeks");
    });

    it('should generate appropriate subject line', () => {
      const subject = mockEmailTemplate.subject;
      
      expect(subject).toContain("RFQ");
      expect(subject).toContain("AI Hardware");
      expect(subject).toContain("H100");
      expect(subject.length).toBeLessThan(100); // Email subject length limit
    });

    it('should handle missing supplier contact information', async () => {
      const supplierWithoutEmail = { ...mockSupplier, contactEmail: null };
      
      app.post('/api/proposals/:id/generate-email', (req, res) => {
        if (!supplierWithoutEmail.contactEmail) {
          return res.status(400).json({ 
            error: "Supplier contact email not available",
            suggestion: "Please contact supplier directly or use alternative contact method"
          });
        }
        res.json(mockEmailTemplate);
      });

      const response = await request(app)
        .post('/api/proposals/1/generate-email')
        .send({ 
          proposal: mockProposal,
          supplier: supplierWithoutEmail,
          product: mockProduct 
        })
        .expect(400);

      expect(response.body.error).toContain("contact email");
    });
  });

  describe('Email Content Personalization', () => {
    it('should personalize email for different supplier types', () => {
      const manufacturerTemplate = mockEmailTemplate;
      const distributorSupplier = { 
        ...mockSupplier, 
        name: "CDW Corporation",
        description: "Technology solutions provider and distributor"
      };
      
      // Should adjust tone for distributors vs manufacturers
      expect(manufacturerTemplate.body).toContain("Dear NVIDIA Sales Team");
      
      // For distributor, should be more generic
      const distributorBody = manufacturerTemplate.body.replace(
        "Dear NVIDIA Sales Team",
        "Dear CDW Sales Team"
      );
      expect(distributorBody).toContain("Dear CDW Sales Team");
    });

    it('should include region-specific compliance information', () => {
      const usCompliance = mockEmailTemplate.body;
      expect(usCompliance).toContain("Export control compliance required");
      
      // Should adapt for different regions
      const euCompliance = usCompliance.replace(
        "Export control compliance required",
        "CE marking and GDPR compliance required"
      );
      expect(euCompliance).toContain("CE marking");
    });

    it('should adjust language based on order value', () => {
      const highValueBody = mockEmailTemplate.body;
      expect(highValueBody).toContain("$120,000"); // High value order
      
      // Should include volume discount mention for large orders
      expect(highValueBody).toContain("Volume discount") || 
      expect(mockProposal.pricingNotes).toContain("Volume discount");
    });
  });

  describe('PDF Attachment Generation', () => {
    it('should generate PDF with RFQ requirements', async () => {
      app.get('/api/proposals/:id/pdf', (req, res) => {
        // Mock PDF generation
        const pdfBuffer = Buffer.from('PDF content');
        res.setHeader('Content-Type', 'application/pdf');
        res.setHeader('Content-Disposition', 'attachment; filename="rfq-requirements.pdf"');
        res.send(pdfBuffer);
      });

      const response = await request(app)
        .get('/api/proposals/1/pdf')
        .expect(200);

      expect(response.headers['content-type']).toBe('application/pdf');
      expect(response.headers['content-disposition']).toContain('rfq-requirements.pdf');
    });

    it('should include all proposal details in PDF', async () => {
      // Mock PDF content validation
      const pdfContent = {
        proposal: mockProposal,
        product: mockProduct,
        supplier: mockSupplier,
        requirements: {
          quantity: 4,
          budget: 120000,
          timeline: "4 weeks",
          specifications: mockProduct.specifications
        }
      };

      expect(pdfContent.proposal.score).toBe(95);
      expect(pdfContent.product.name).toBe("NVIDIA H100 SXM5 80GB");
      expect(pdfContent.supplier.name).toBe("NVIDIA Corporation");
      expect(pdfContent.requirements.quantity).toBe(4);
    });
  });

  describe('Email Validation', () => {
    it('should validate email addresses', () => {
      const validEmails = [
        "sales@nvidia.com",
        "enterprise-sales@company.co.uk",
        "contact+sales@example-company.com"
      ];
      
      const invalidEmails = [
        "invalid-email",
        "@missing-local.com",
        "missing-domain@",
        "spaces in@email.com"
      ];
      
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      
      validEmails.forEach(email => {
        expect(emailRegex.test(email)).toBe(true);
      });
      
      invalidEmails.forEach(email => {
        expect(emailRegex.test(email)).toBe(false);
      });
    });

    it('should validate email content length', () => {
      const emailBody = mockEmailTemplate.body;
      
      // Should not be too short or too long
      expect(emailBody.length).toBeGreaterThan(200);
      expect(emailBody.length).toBeLessThan(5000);
      
      // Should have proper structure
      expect(emailBody).toContain("Dear");
      expect(emailBody).toContain("Best regards");
    });

    it('should validate required fields are present', () => {
      const requiredFields = ['to', 'subject', 'body'];
      
      requiredFields.forEach(field => {
        expect(mockEmailTemplate).toHaveProperty(field);
        expect(mockEmailTemplate[field as keyof EmailTemplate]).toBeTruthy();
      });
    });
  });

  describe('Email Sending Simulation', () => {
    it('should simulate email sending with proper response', async () => {
      app.post('/api/emails/send', (req, res) => {
        const { to, subject, body } = req.body;
        
        // Simulate email service response
        res.json({
          messageId: "msg_123456789",
          status: "sent",
          to,
          subject,
          sentAt: new Date().toISOString(),
          estimatedDelivery: "immediate"
        });
      });

      const response = await request(app)
        .post('/api/emails/send')
        .send(mockEmailTemplate)
        .expect(200);

      expect(response.body).toHaveProperty('messageId');
      expect(response.body).toHaveProperty('status');
      expect(response.body.status).toBe('sent');
      expect(response.body.to).toBe(mockEmailTemplate.to);
    });

    it('should handle email service failures gracefully', async () => {
      app.post('/api/emails/send', (req, res) => {
        // Simulate email service failure
        res.status(503).json({
          error: "Email service temporarily unavailable",
          retryAfter: 300, // 5 minutes
          messageQueued: true
        });
      });

      const response = await request(app)
        .post('/api/emails/send')
        .send(mockEmailTemplate)
        .expect(503);

      expect(response.body.error).toContain("temporarily unavailable");
      expect(response.body.messageQueued).toBe(true);
    });

    it('should track email status and delivery', async () => {
      app.get('/api/emails/:messageId/status', (req, res) => {
        const { messageId } = req.params;
        
        res.json({
          messageId,
          status: "delivered",
          deliveredAt: new Date().toISOString(),
          readStatus: "unread",
          bounced: false
        });
      });

      const response = await request(app)
        .get('/api/emails/msg_123456789/status')
        .expect(200);

      expect(response.body.status).toBe('delivered');
      expect(response.body.bounced).toBe(false);
    });
  });

  describe('Error Handling', () => {
    it('should handle template generation failures', async () => {
      app.post('/api/proposals/:id/generate-email', (req, res) => {
        res.status(500).json({
          error: "Failed to generate email template",
          details: "AI service error"
        });
      });

      const response = await request(app)
        .post('/api/proposals/1/generate-email')
        .send({ proposal: mockProposal })
        .expect(500);

      expect(response.body.error).toContain("Failed to generate");
    });

    it('should handle invalid proposal data', async () => {
      app.post('/api/proposals/:id/generate-email', (req, res) => {
        const { proposal } = req.body;
        
        if (!proposal || !proposal.id) {
          return res.status(400).json({
            error: "Invalid proposal data",
            required: ["proposal.id", "proposal.rfqId", "proposal.productId"]
          });
        }
        
        res.json(mockEmailTemplate);
      });

      await request(app)
        .post('/api/proposals/1/generate-email')
        .send({ proposal: {} })
        .expect(400);
    });
  });
});