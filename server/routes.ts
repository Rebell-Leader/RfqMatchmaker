import type { Express, Request, Response } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { z } from "zod";
import multer from "multer";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { OpenAI } from "openai";
import { createProxyMiddleware } from 'http-proxy-middleware';
import { log } from "./vite";

// Setup file uploads
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const uploadsDir = path.join(__dirname, "../uploads");

// Ensure uploads directory exists
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

const upload = multer({
  storage: multer.diskStorage({
    destination: (_req, _file, cb) => {
      cb(null, uploadsDir);
    },
    filename: (_req, file, cb) => {
      const uniqueSuffix = Date.now() + "-" + Math.round(Math.random() * 1e9);
      cb(null, uniqueSuffix + "-" + file.originalname);
    },
  }),
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB limit
  },
});

// Initialize Featherless AI client
const API_KEY = process.env.FEATHERLESS_API_KEY || "rc_f8cf96bf43de3fde06f99a693f4d11e32d0c68a3bf3b7cdcaf851efec169d0b8";
const client = new OpenAI({
  baseUrl: "https://api.featherless.ai/v1",
  apiKey: API_KEY,
});

// Python backend URL
const PYTHON_BACKEND_URL = "http://localhost:8000";

export async function registerRoutes(app: Express): Promise<Server> {
  // Set up proxy middleware for Python backend with better logging
  app.use('/api-python/api', createProxyMiddleware({
    target: PYTHON_BACKEND_URL,
    changeOrigin: true,
    pathRewrite: {
      '^/api-python/api': '/api' // Rewrite path from /api-python/api to /api
    },
    logLevel: 'debug',
    onProxyReq: (proxyReq, req, res) => {
      // Enhanced logging for debugging
      const fullPath = `${PYTHON_BACKEND_URL}/api${req.url}`;
      log(`Proxying ${req.method} request to Python backend: ${fullPath}`, "proxy");
      
      // Log request body for POST/PUT requests
      if (req.method === 'POST' || req.method === 'PUT') {
        if (req.body) {
          log(`Request body: ${JSON.stringify(req.body)}`, "proxy");
        }
      }
    },
    onProxyRes: (proxyRes, req, res) => {
      log(`Received response from Python backend: ${proxyRes.statusCode} for ${req.method} ${req.url}`, "proxy");
      
      // Log detailed error information for non-2xx responses
      if (proxyRes.statusCode >= 400) {
        let responseBody = '';
        proxyRes.on('data', (chunk) => {
          responseBody += chunk;
        });
        proxyRes.on('end', () => {
          try {
            log(`Python backend error response: ${responseBody}`, "proxy");
          } catch (e) {
            log(`Could not parse Python backend error response: ${responseBody}`, "proxy");
          }
        });
      }
    },
    onError: (err, req, res) => {
      log(`Proxy error for ${req.method} ${req.url}: ${err.message}`, "proxy");
      log(`Python backend URL: ${PYTHON_BACKEND_URL}`, "proxy");
      res.status(500).json({ error: "Proxy error", message: err.message });
    }
  }));
  // API Routes
  
  // Get all RFQs
  app.get("/api/rfqs", async (_req: Request, res: Response) => {
    try {
      const rfqs = await storage.getAllRfqs();
      res.json(rfqs);
    } catch (error) {
      console.error("Error fetching RFQs:", error);
      res.status(500).json({ error: "Failed to fetch RFQs" });
    }
  });
  
  // Get RFQ by ID
  app.get("/api/rfqs/:id", async (req: Request, res: Response) => {
    try {
      const id = parseInt(req.params.id);
      const rfq = await storage.getRfqById(id);
      
      if (!rfq) {
        return res.status(404).json({ error: "RFQ not found" });
      }
      
      res.json(rfq);
    } catch (error) {
      console.error("Error fetching RFQ:", error);
      res.status(500).json({ error: "Failed to fetch RFQ" });
    }
  });
  
  // Upload RFQ file
  app.post("/api/rfqs/upload", upload.single("file"), async (req: Request, res: Response) => {
    try {
      if (!req.file) {
        return res.status(400).json({ error: "No file uploaded" });
      }
      
      const filePath = req.file.path;
      const fileName = req.file.originalname.toLowerCase();
      let fileContent = "";
      
      // Handle based on file extension
      if (fileName.endsWith('.pdf')) {
        // For PDF files, we'll forward to Python backend for processing
        log("PDF detected, forwarding to Python backend", "express");
        
        // We'll forward the file to the Python backend
        // We're not trying to read it here since that requires PyPDF2
        
        // Create a readable stream from the file
        const fileStream = fs.createReadStream(filePath);
        
        // Create a form-data object
        const formData = new FormData();
        formData.append("file", fileStream, req.file.originalname);
        
        // Forward to Python backend
        const pythonResponse = await fetch(`${PYTHON_BACKEND_URL}/api/rfqs/upload`, {
          method: "POST",
          body: formData
        });
        
        if (!pythonResponse.ok) {
          throw new Error(`Python backend returned: ${pythonResponse.status} ${pythonResponse.statusText}`);
        }
        
        const responseData = await pythonResponse.json();
        
        // Clean up the uploaded file
        fs.unlinkSync(filePath);
        
        return res.status(201).json(responseData);
      } else {
        // For text files, process directly
        fileContent = fs.readFileSync(filePath, "utf8");
        
        // Extract requirements using Featherless AI
        const extractedRequirements = await extractRequirementsFromRFQ(fileContent);
        
        // Create RFQ in storage
        const newRfq = await storage.createRfq({
          title: extractedRequirements.title || "Untitled RFQ",
          description: extractedRequirements.description || "",
          originalContent: fileContent,
          extractedRequirements,
          userId: 1, // Default user for now
        });
        
        // Clean up the uploaded file
        fs.unlinkSync(filePath);
        
        res.status(201).json(newRfq);
      }
    } catch (error) {
      console.error("Error processing RFQ upload:", error);
      res.status(500).json({ error: "Failed to process uploaded RFQ" });
    }
  });
  
  // Create RFQ manually
  app.post("/api/rfqs", async (req: Request, res: Response) => {
    try {
      const schema = z.object({
        title: z.string().min(1),
        description: z.string().optional(),
        specifications: z.string().min(1),
      });
      
      const result = schema.safeParse(req.body);
      
      if (!result.success) {
        return res.status(400).json({ error: "Invalid input", details: result.error });
      }
      
      const { title, description, specifications } = result.data;
      const content = `${title}\n\n${description || ""}\n\n${specifications}`;
      
      // Extract requirements using Featherless AI
      const extractedRequirements = await extractRequirementsFromRFQ(content);
      
      // Create RFQ in storage
      const newRfq = await storage.createRfq({
        title,
        description: description || "",
        originalContent: content,
        extractedRequirements,
        userId: 1, // Default user for now
      });
      
      res.status(201).json(newRfq);
    } catch (error) {
      console.error("Error creating RFQ:", error);
      res.status(500).json({ error: "Failed to create RFQ" });
    }
  });
  
  // Get all suppliers
  app.get("/api/suppliers", async (_req: Request, res: Response) => {
    try {
      const suppliers = await storage.getAllSuppliers();
      res.json(suppliers);
    } catch (error) {
      console.error("Error fetching suppliers:", error);
      res.status(500).json({ error: "Failed to fetch suppliers" });
    }
  });
  
  // Get products by category
  app.get("/api/products", async (req: Request, res: Response) => {
    try {
      const category = req.query.category as string;
      
      if (!category) {
        return res.status(400).json({ error: "Category parameter is required" });
      }
      
      const products = await storage.getProductsByCategory(category);
      res.json(products);
    } catch (error) {
      console.error("Error fetching products:", error);
      res.status(500).json({ error: "Failed to fetch products" });
    }
  });
  
  // Match suppliers for an RFQ
  app.post("/api/rfqs/:id/match-suppliers", async (req: Request, res: Response) => {
    try {
      const id = parseInt(req.params.id);
      const rfq = await storage.getRfqById(id);
      
      if (!rfq) {
        return res.status(404).json({ error: "RFQ not found" });
      }
      
      // Get products by categories from the RFQ
      const requirements = rfq.extractedRequirements as any;
      const categories = requirements.categories || [];
      
      const matchResults = [];
      
      for (const category of categories) {
        const products = await storage.getProductsByCategory(category);
        
        // For each product, get supplier details and calculate match score
        for (const product of products) {
          const supplier = await storage.getSupplierById(product.supplierId);
          
          if (supplier) {
            // Calculate match score based on RFQ criteria
            const matchScore = calculateMatchScore(product, supplier, requirements, category);
            
            matchResults.push({
              supplier,
              product,
              matchScore: matchScore.totalScore,
              matchDetails: {
                price: matchScore.priceScore,
                quality: matchScore.qualityScore,
                delivery: matchScore.deliveryScore,
              },
              totalPrice: product.price * (category === "Laptops" ? requirements.laptops?.quantity || 1 : requirements.monitors?.quantity || 1)
            });
            
            // Create a proposal in storage
            await storage.createProposal({
              rfqId: id,
              productId: product.id,
              score: matchScore.totalScore,
              priceScore: matchScore.priceScore,
              qualityScore: matchScore.qualityScore,
              deliveryScore: matchScore.deliveryScore,
              emailContent: null,
            });
          }
        }
      }
      
      // Sort match results by match score (descending)
      matchResults.sort((a, b) => b.matchScore - a.matchScore);
      
      res.json({
        rfqId: id,
        matches: matchResults
      });
    } catch (error) {
      console.error("Error matching suppliers:", error);
      res.status(500).json({ error: "Failed to match suppliers" });
    }
  });
  
  // Generate email proposal
  app.post("/api/proposals/:id/generate-email", async (req: Request, res: Response) => {
    try {
      const id = parseInt(req.params.id);
      const proposal = await storage.getProposalById(id);
      
      if (!proposal) {
        return res.status(404).json({ error: "Proposal not found" });
      }
      
      const rfq = await storage.getRfqById(proposal.rfqId);
      const product = await storage.getProductById(proposal.productId);
      const supplier = product ? await storage.getSupplierById(product.supplierId) : undefined;
      
      if (!rfq || !product || !supplier) {
        return res.status(404).json({ error: "Related RFQ, product, or supplier not found" });
      }
      
      // Generate email content using Featherless AI
      const emailContent = await generateEmailProposal(rfq, product, supplier);
      
      // Update proposal with email content
      proposal.emailContent = emailContent.body;
      
      res.json(emailContent);
    } catch (error) {
      console.error("Error generating email proposal:", error);
      res.status(500).json({ error: "Failed to generate email proposal" });
    }
  });
  
  // Helper functions
  
  // Extract requirements from RFQ using Featherless AI
  async function extractRequirementsFromRFQ(content: string) {
    try {
      const systemPrompt = `
        You are an AI assistant that extracts structured information from Request for Quotations (RFQs).
        Given an RFQ document, extract the following information in JSON format:
        - title: The title of the RFQ
        - description: A brief description of the RFQ purpose
        - categories: Array of product categories (e.g., "Laptops", "Monitors")
        - laptops: If present, extract details about laptop requirements including:
          - quantity: Number of units
          - os: Operating system requirements
          - processor: Processor specifications
          - memory: RAM specifications
          - storage: Storage specifications
          - display: Display specifications
          - battery: Battery life requirements
          - durability: Durability certifications needed
          - connectivity: Required ports and wireless connectivity
          - warranty: Warranty requirements
        - monitors: If present, extract details about monitor requirements including:
          - quantity: Number of units
          - screenSize: Screen size specifications
          - resolution: Resolution requirements
          - panelTech: Panel technology requirements
          - brightness: Brightness specifications
          - contrastRatio: Contrast ratio requirements
          - connectivity: Required ports
          - adjustability: Adjustability features required
          - warranty: Warranty requirements
        - criteria: Award criteria with weights for:
          - price: {weight: number from 0-100}
          - quality: {weight: number from 0-100}
          - delivery: {weight: number from 0-100}
        
        Return ONLY the JSON response with no other text or explanation.
      `;
      
      const response = await client.chat.completions.create({
        model: "Qwen/Qwen2.5-32B-Instruct",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: content }
        ],
        temperature: 0.2,
      });
      
      const extractedContent = response.choices[0].message.content;
      
      try {
        return JSON.parse(extractedContent || "{}");
      } catch (error) {
        console.error("Error parsing AI response as JSON:", error);
        return {
          title: "Failed to parse RFQ",
          description: "Could not extract structured data from the RFQ document",
          categories: [],
          criteria: { price: { weight: 50 }, quality: { weight: 30 }, delivery: { weight: 20 } }
        };
      }
    } catch (error) {
      console.error("Error extracting requirements from RFQ:", error);
      return {
        title: "Error Processing RFQ",
        description: "An error occurred while processing the RFQ document",
        categories: [],
        criteria: { price: { weight: 50 }, quality: { weight: 30 }, delivery: { weight: 20 } }
      };
    }
  }
  
  // Calculate match score for a product based on RFQ criteria
  function calculateMatchScore(product: any, supplier: any, requirements: any, category: string) {
    // Get category-specific requirements
    const categoryReqs = category === "Laptops" ? requirements.laptops : requirements.monitors;
    if (!categoryReqs) {
      return { totalScore: 0, priceScore: 0, qualityScore: 0, deliveryScore: 0 };
    }
    
    // Get criteria weights
    const priceWeight = requirements.criteria?.price?.weight || 50;
    const qualityWeight = requirements.criteria?.quality?.weight || 30;
    const deliveryWeight = requirements.criteria?.delivery?.weight || 20;
    
    // Calculate price score (lower price is better)
    // For simplicity, we'll use a range of prices and score within that range
    const priceScore = Math.min(100, Math.max(0, 100 - (product.price / 1000) * 100)) * (priceWeight / 100);
    
    // Calculate quality score
    // Based on matching specifications and warranty
    let qualityScore = 0;
    const specs = product.specifications;
    
    if (category === "Laptops") {
      // Check processor
      if (specs.processor && specs.processor.includes("i5") && categoryReqs.processor.includes("i5")) {
        qualityScore += 20;
      } else if (specs.processor && specs.processor.includes("i7")) {
        qualityScore += 25;
      }
      
      // Check memory
      if (specs.memory && specs.memory.includes("16 GB") && categoryReqs.memory.includes("16 GB")) {
        qualityScore += 20;
      } else if (specs.memory && specs.memory.includes("32 GB")) {
        qualityScore += 25;
      }
      
      // Check warranty
      const requiredWarrantyYears = parseInt(categoryReqs.warranty.match(/\d+/)?.[0] || "0");
      const productWarrantyYears = parseInt(product.warranty.match(/\d+/)?.[0] || "0");
      
      if (productWarrantyYears >= requiredWarrantyYears) {
        qualityScore += 20;
      }
      
      // Check durability
      if (specs.durability && specs.durability.includes("MIL-STD") && categoryReqs.durability.includes("MIL-STD")) {
        qualityScore += 20;
      }
    } else if (category === "Monitors") {
      // Check screen size
      const reqScreenSize = parseFloat(categoryReqs.screenSize.match(/\d+(\.\d+)?/)?.[0] || "0");
      const productScreenSize = parseFloat(specs.screenSize.match(/\d+(\.\d+)?/)?.[0] || "0");
      
      if (productScreenSize >= reqScreenSize) {
        qualityScore += 25;
      }
      
      // Check resolution
      if (specs.resolution && specs.resolution.includes("1920x1080") && categoryReqs.resolution.includes("1920x1080")) {
        qualityScore += 25;
      }
      
      // Check adjustability
      const adjustabilityFeatures = categoryReqs.adjustability.toLowerCase();
      const productAdjustability = specs.adjustability.toLowerCase();
      
      if (productAdjustability.includes("tilt") && adjustabilityFeatures.includes("tilt")) {
        qualityScore += 15;
      }
      
      if (productAdjustability.includes("height") && adjustabilityFeatures.includes("height")) {
        qualityScore += 15;
      }
    }
    
    // Normalize quality score to the weight
    qualityScore = Math.min(100, qualityScore) * (qualityWeight / 100);
    
    // Calculate delivery score
    // Extract delivery time range and calculate score based on required delivery time
    let deliveryScore = 0;
    const deliveryDays = supplier.deliveryTime.match(/\d+/g)?.map(Number) || [30, 30];
    const averageDeliveryDays = (deliveryDays[0] + (deliveryDays[1] || deliveryDays[0])) / 2;
    
    // If delivery time is within 30 days (from the requirements), give full score
    if (averageDeliveryDays <= 30) {
      deliveryScore = 100;
    } else {
      // Linear decrease in score as delivery time increases
      deliveryScore = Math.max(0, 100 - ((averageDeliveryDays - 30) * 5));
    }
    
    deliveryScore = deliveryScore * (deliveryWeight / 100);
    
    // Calculate total score
    const totalScore = priceScore + qualityScore + deliveryScore;
    
    return {
      totalScore,
      priceScore,
      qualityScore,
      deliveryScore
    };
  }
  
  // Generate email proposal using Featherless AI
  async function generateEmailProposal(rfq: any, product: any, supplier: any) {
    try {
      const requirements = rfq.extractedRequirements;
      const category = product.category;
      const categoryReqs = category === "Laptops" ? requirements.laptops : requirements.monitors;
      const quantity = categoryReqs.quantity || 1;
      const totalPrice = product.price * quantity;
      
      const prompt = `
        Generate a professional email to request a quote from a supplier for ${category} in response to an RFQ.
        
        RFQ Title: ${requirements.title}
        Product Selected: ${product.name} from ${supplier.name}
        Price: $${product.price} per unit, for a total of $${totalPrice} (${quantity} units)
        
        Product Specifications:
        ${Object.entries(product.specifications).map(([key, value]) => `- ${key}: ${value}`).join('\n')}
        
        Supplier delivery time: ${supplier.deliveryTime}
        Warranty: ${product.warranty}
        
        Generate a formal but friendly email that includes:
        1. Introduction referencing the RFQ
        2. Mention of the selected product and why it was chosen
        3. List the key specifications matching the RFQ requirements
        4. Mention the price per unit and total price
        5. Request confirmation of:
           - Final pricing
           - Delivery timeline
           - Warranty details
           - Payment terms
        6. Professional closing
        
        Format the email with appropriate spacing and sections.
      `;
      
      const response = await client.chat.completions.create({
        model: "Qwen/Qwen2.5-32B-Instruct",
        messages: [
          { role: "system", content: "You are a professional procurement assistant that writes clear, concise business emails." },
          { role: "user", content: prompt }
        ],
        temperature: 0.7,
      });
      
      const emailBody = response.choices[0].message.content || "";
      
      return {
        to: `sales@${supplier.name.toLowerCase().replace(/\s+/g, '')}.com`,
        subject: `RFQ: ${requirements.title}`,
        body: emailBody
      };
    } catch (error) {
      console.error("Error generating email proposal:", error);
      return {
        to: `sales@${supplier.name.toLowerCase().replace(/\s+/g, '')}.com`,
        subject: `RFQ: ${rfq.title}`,
        body: `Dear ${supplier.name} Team,\n\nWe are interested in your ${product.name} product for our needs. Please provide a formal quotation.\n\nThank you.`
      };
    }
  }
  
  const httpServer = createServer(app);
  
  return httpServer;
}
