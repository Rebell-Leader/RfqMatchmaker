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

// Do not initialize Featherless AI client in Node.js
// All AI operations should be handled by the Python backend

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
  
  // Get all RFQs - Proxy to Python backend
  app.get("/api/rfqs", async (_req: Request, res: Response) => {
    try {
      log("Forwarding RFQ list request to Python backend", "express");
      
      try {
        // Forward to Python backend
        const pythonResponse = await fetch(`${PYTHON_BACKEND_URL}/api/rfqs`);
        
        if (!pythonResponse.ok) {
          const errorText = await pythonResponse.text();
          log(`Python backend error: ${errorText}`, "express");
          throw new Error(`Python backend returned ${pythonResponse.status}: ${errorText}`);
        }
        
        const responseData = await pythonResponse.json();
        log(`Python backend response: RFQs list retrieved`, "express");
        
        return res.json(responseData);
      } catch (error) {
        log(`Error forwarding to Python backend: ${error}`, "express");
        throw error;
      }
    } catch (error) {
      console.error("Error fetching RFQs:", error);
      res.status(500).json({ error: "Failed to fetch RFQs" });
    }
  });
  
  // Get RFQ by ID - Proxy to Python backend
  app.get("/api/rfqs/:id", async (req: Request, res: Response) => {
    try {
      const id = parseInt(req.params.id);
      log(`Forwarding RFQ fetch request to Python backend for ID ${id}`, "express");
      
      try {
        // Forward to Python backend
        const pythonResponse = await fetch(`${PYTHON_BACKEND_URL}/api/rfqs/${id}`);
        
        if (!pythonResponse.ok) {
          const errorText = await pythonResponse.text();
          log(`Python backend error: ${errorText}`, "express");
          
          // Return the same status code from the Python backend
          return res.status(pythonResponse.status).json({ error: `RFQ not found` });
        }
        
        const responseData = await pythonResponse.json();
        log(`Python backend response: RFQ ${id} retrieved`, "express");
        
        return res.json(responseData);
      } catch (error) {
        log(`Error forwarding to Python backend: ${error}`, "express");
        throw error;
      }
    } catch (error) {
      console.error("Error fetching RFQ:", error);
      res.status(500).json({ error: "Failed to fetch RFQ" });
    }
  });
  
  // Upload RFQ file - Proxy all file uploads to Python backend
  app.post("/api/rfqs/upload", upload.single("file"), async (req: Request, res: Response) => {
    try {
      if (!req.file) {
        return res.status(400).json({ error: "No file uploaded" });
      }
      
      const filePath = req.file.path;
      
      log("Forwarding file upload to Python backend", "express");
      
      try {
        // Create a readable stream from the file
        const fileStream = fs.createReadStream(filePath);
        
        // Create a form-data object
        const formData = new FormData();
        formData.append("file", new Blob([fs.readFileSync(filePath)]), req.file.originalname);
        
        // Forward to Python backend
        const pythonResponse = await fetch(`${PYTHON_BACKEND_URL}/api/rfqs/upload`, {
          method: "POST",
          body: formData
        });
        
        // Clean up the uploaded file
        fs.unlinkSync(filePath);
        
        if (!pythonResponse.ok) {
          const errorText = await pythonResponse.text();
          log(`Python backend error: ${errorText}`, "express");
          throw new Error(`Python backend returned ${pythonResponse.status}: ${errorText}`);
        }
        
        const responseData = await pythonResponse.json();
        log(`Python backend response: ${JSON.stringify(responseData)}`, "express");
        
        return res.status(201).json(responseData);
      } catch (error) {
        log(`Error forwarding to Python backend: ${error}`, "express");
        throw error;
      }
    } catch (error) {
      console.error("Error processing RFQ upload:", error);
      res.status(500).json({ error: "Failed to process uploaded RFQ" });
    }
  });
  
  // Create RFQ manually - Proxy to Python backend
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
      
      log("Forwarding manual RFQ creation to Python backend", "express");
      
      try {
        // Forward to Python backend
        const pythonResponse = await fetch(`${PYTHON_BACKEND_URL}/api/rfqs`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ title, description, specifications })
        });
        
        if (!pythonResponse.ok) {
          const errorText = await pythonResponse.text();
          log(`Python backend error: ${errorText}`, "express");
          throw new Error(`Python backend returned ${pythonResponse.status}: ${errorText}`);
        }
        
        const responseData = await pythonResponse.json();
        log(`Python backend response: ${JSON.stringify(responseData)}`, "express");
        
        return res.status(201).json(responseData);
      } catch (error) {
        log(`Error forwarding to Python backend: ${error}`, "express");
        throw error;
      }
    } catch (error) {
      console.error("Error creating RFQ:", error);
      res.status(500).json({ error: "Failed to create RFQ" });
    }
  });
  
  // Get all suppliers - Proxy to Python backend
  app.get("/api/suppliers", async (_req: Request, res: Response) => {
    try {
      log("Forwarding supplier list request to Python backend", "express");
      
      try {
        // Forward to Python backend
        const pythonResponse = await fetch(`${PYTHON_BACKEND_URL}/api/suppliers`);
        
        if (!pythonResponse.ok) {
          const errorText = await pythonResponse.text();
          log(`Python backend error: ${errorText}`, "express");
          throw new Error(`Python backend returned ${pythonResponse.status}: ${errorText}`);
        }
        
        const responseData = await pythonResponse.json();
        log(`Python backend response: Suppliers list retrieved`, "express");
        
        return res.json(responseData);
      } catch (error) {
        log(`Error forwarding to Python backend: ${error}`, "express");
        throw error;
      }
    } catch (error) {
      console.error("Error fetching suppliers:", error);
      res.status(500).json({ error: "Failed to fetch suppliers" });
    }
  });
  
  // Get products by category - Proxy to Python backend
  app.get("/api/products", async (req: Request, res: Response) => {
    try {
      const category = req.query.category as string;
      
      if (!category) {
        return res.status(400).json({ error: "Category parameter is required" });
      }
      
      log(`Forwarding products request to Python backend for category ${category}`, "express");
      
      try {
        // Forward to Python backend
        const pythonResponse = await fetch(`${PYTHON_BACKEND_URL}/api/products?category=${encodeURIComponent(category)}`);
        
        if (!pythonResponse.ok) {
          const errorText = await pythonResponse.text();
          log(`Python backend error: ${errorText}`, "express");
          throw new Error(`Python backend returned ${pythonResponse.status}: ${errorText}`);
        }
        
        const responseData = await pythonResponse.json();
        log(`Python backend response: Products for category ${category} retrieved`, "express");
        
        return res.json(responseData);
      } catch (error) {
        log(`Error forwarding to Python backend: ${error}`, "express");
        throw error;
      }
    } catch (error) {
      console.error("Error fetching products:", error);
      res.status(500).json({ error: "Failed to fetch products" });
    }
  });
  
  // Match suppliers for an RFQ - Proxy to Python backend
  app.post("/api/rfqs/:id/match-suppliers", async (req: Request, res: Response) => {
    try {
      const id = parseInt(req.params.id);
      
      log(`Forwarding supplier matching to Python backend for RFQ ${id}`, "express");
      
      try {
        // Forward to Python backend
        const pythonResponse = await fetch(`${PYTHON_BACKEND_URL}/api/rfqs/${id}/match-suppliers`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({})
        });
        
        if (!pythonResponse.ok) {
          const errorText = await pythonResponse.text();
          log(`Python backend error: ${errorText}`, "express");
          throw new Error(`Python backend returned ${pythonResponse.status}: ${errorText}`);
        }
        
        const responseData = await pythonResponse.json();
        log(`Python backend response: ${JSON.stringify(responseData)}`, "express");
        
        return res.json(responseData);
      } catch (error) {
        log(`Error forwarding to Python backend: ${error}`, "express");
        throw error;
      }
    } catch (error) {
      console.error("Error matching suppliers:", error);
      res.status(500).json({ error: "Failed to match suppliers" });
    }
  });
  
  // Generate email proposal - Proxy to Python backend
  app.post("/api/proposals/:id/generate-email", async (req: Request, res: Response) => {
    try {
      const id = parseInt(req.params.id);
      
      log(`Forwarding email proposal generation to Python backend for proposal ${id}`, "express");
      
      try {
        // Forward to Python backend
        const pythonResponse = await fetch(`${PYTHON_BACKEND_URL}/api/proposals/${id}/generate-email`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({})
        });
        
        if (!pythonResponse.ok) {
          const errorText = await pythonResponse.text();
          log(`Python backend error: ${errorText}`, "express");
          throw new Error(`Python backend returned ${pythonResponse.status}: ${errorText}`);
        }
        
        const responseData = await pythonResponse.json();
        log(`Python backend response: ${JSON.stringify(responseData)}`, "express");
        
        return res.json(responseData);
      } catch (error) {
        log(`Error forwarding to Python backend: ${error}`, "express");
        throw error;
      }
    } catch (error) {
      console.error("Error generating email proposal:", error);
      res.status(500).json({ error: "Failed to generate email proposal" });
    }
  });
  
  // AI Hardware mockup data for the specialized platform
  const aiHardwareProducts = [
    {
      id: 1,
      supplierId: 1,
      name: "NVIDIA A100 GPU",
      model: "A100-SXM4-80GB",
      manufacturer: "NVIDIA",
      category: "AI Hardware",
      description: "High-performance GPU for AI workloads with 80GB HBM2e memory",
      price: 10000,
      computeSpecs: { 
        tensorFlops: 312,
        fp32Performance: 19.5,
        fp16Performance: 312,
        tensorCores: 432
      },
      memorySpecs: { 
        capacity: 80, 
        type: "HBM2e", 
        bandwidth: 2039, 
        busWidth: 5120,
        eccSupport: true
      },
      powerSpecs: { 
        tdp: 400, 
        requiredPsu: 1200
      },
      thermalSpecs: {
        cooling: "Passive + Active",
        maxTemp: 85
      },
      connectivity: ["NVLink", "PCIe 4.0"],
      supportedFrameworks: ["PyTorch", "TensorFlow", "CUDA", "JAX", "ONNX"],
      formFactor: "SXM4",
      complianceInfo: {
        exportRestrictions: ["RU", "CN"],
        certifications: ["FCC", "CE", "RoHS"]
      },
      benchmarks: {
        mlTraining: { "ResNet50": 32550, "BERT-Large": 8643 },
        llmInference: { "GPT-3": 180, "T5": 320 }
      },
      availability: "2-4 weeks",
      warranty: "3 years",
      releaseDate: "2020-05-14",
      inStock: true
    },
    {
      id: 2,
      supplierId: 1,
      name: "NVIDIA H100 GPU",
      model: "H100-SXM5-80GB",
      manufacturer: "NVIDIA",
      category: "AI Hardware",
      description: "Next-generation GPU for AI computing with 80GB HBM3 memory",
      price: 35000,
      computeSpecs: { 
        tensorFlops: 989,
        fp32Performance: 51,
        fp16Performance: 989,
        tensorCores: 528
      },
      memorySpecs: { 
        capacity: 80, 
        type: "HBM3", 
        bandwidth: 3350, 
        busWidth: 5120,
        eccSupport: true
      },
      powerSpecs: { 
        tdp: 700, 
        requiredPsu: 1800
      },
      thermalSpecs: {
        cooling: "Active",
        maxTemp: 90
      },
      connectivity: ["NVLink 4.0", "PCIe 5.0"],
      supportedFrameworks: ["PyTorch", "TensorFlow", "CUDA", "JAX", "ONNX", "DirectML"],
      formFactor: "SXM5",
      complianceInfo: {
        exportRestrictions: ["RU", "CN", "IR"],
        certifications: ["FCC", "CE", "RoHS"]
      },
      benchmarks: {
        mlTraining: { "ResNet50": 98370, "BERT-Large": 24290 },
        llmInference: { "GPT-3": 580, "T5": 960 }
      },
      availability: "4-8 weeks",
      warranty: "3 years",
      releaseDate: "2022-03-22",
      inStock: false
    },
    {
      id: 3,
      supplierId: 2,
      name: "AMD Instinct MI250X",
      model: "MI250X-OAM",
      manufacturer: "AMD",
      category: "AI Hardware",
      description: "High-performance accelerator with 128GB HBM2e memory",
      price: 12000,
      computeSpecs: { 
        tensorFlops: 383,
        fp32Performance: 47.9,
        fp16Performance: 383,
        tensorCores: 220
      },
      memorySpecs: { 
        capacity: 128, 
        type: "HBM2e", 
        bandwidth: 3200, 
        busWidth: 8192,
        eccSupport: true
      },
      powerSpecs: { 
        tdp: 560, 
        requiredPsu: 1500
      },
      thermalSpecs: {
        cooling: "Active",
        maxTemp: 85
      },
      connectivity: ["Infinity Fabric", "PCIe 4.0"],
      supportedFrameworks: ["ROCm", "PyTorch", "TensorFlow", "ONNX"],
      formFactor: "OAM",
      complianceInfo: {
        exportRestrictions: ["RU", "CN"],
        certifications: ["FCC", "CE", "RoHS", "UKCA"]
      },
      benchmarks: {
        mlTraining: { "ResNet50": 41200, "BERT-Large": 10450 }
      },
      availability: "3-5 weeks",
      warranty: "3 years",
      releaseDate: "2021-11-08",
      inStock: true
    },
    {
      id: 4,
      supplierId: 3,
      name: "Intel Gaudi2",
      model: "Gaudi2-OAM",
      manufacturer: "Intel",
      category: "AI Hardware",
      description: "AI accelerator for deep learning training and inference",
      price: 9500,
      computeSpecs: { 
        tensorFlops: 197,
        fp32Performance: 24.6,
        fp16Performance: 197
      },
      memorySpecs: { 
        capacity: 96, 
        type: "HBM2e", 
        bandwidth: 2450, 
        busWidth: 6144,
        eccSupport: true
      },
      powerSpecs: { 
        tdp: 600, 
        requiredPsu: 1200
      },
      thermalSpecs: {
        cooling: "Active",
        maxTemp: 85
      },
      connectivity: ["RoCE v2", "PCIe 4.0"],
      supportedFrameworks: ["PyTorch", "TensorFlow", "OpenVINO"],
      formFactor: "OAM",
      complianceInfo: {
        exportRestrictions: ["RU"],
        certifications: ["FCC", "CE", "RoHS"]
      },
      benchmarks: {
        mlTraining: { "ResNet50": 26780, "BERT-Large": 7890 },
        llmInference: { "GPT-3": 120, "T5": 240 }
      },
      availability: "2-3 weeks",
      warranty: "2 years",
      releaseDate: "2022-05-10",
      inStock: true
    },
    {
      id: 5,
      supplierId: 4,
      name: "Cerebras CS-2",
      model: "CS-2",
      manufacturer: "Cerebras",
      category: "AI Hardware",
      description: "World's largest AI chip with 850,000 AI-optimized compute cores",
      price: 250000,
      computeSpecs: { 
        fp32Performance: 220,
        fp16Performance: 440
      },
      memorySpecs: { 
        capacity: 40000, 
        type: "On-chip SRAM", 
        bandwidth: 20000, 
        busWidth: 1024000
      },
      powerSpecs: { 
        tdp: 15000
      },
      connectivity: ["100 GbE"],
      supportedFrameworks: ["PyTorch", "TensorFlow"],
      formFactor: "Rack-mounted",
      complianceInfo: {
        exportRestrictions: ["RU", "CN", "IR", "KP"],
        certifications: ["FCC", "CE"]
      },
      benchmarks: {
        mlTraining: { "BERT-Large": 38000 }
      },
      availability: "12-16 weeks",
      warranty: "1 year",
      releaseDate: "2021-08-24",
      inStock: false
    },
    {
      id: 6,
      supplierId: 5,
      name: "Graphcore IPU-POD64",
      model: "IPU-POD64",
      manufacturer: "Graphcore",
      category: "AI Hardware",
      description: "Intelligence Processing Unit designed for AI computing",
      price: 120000,
      computeSpecs: { 
        fp32Performance: 31.1,
        fp16Performance: 125
      },
      memorySpecs: { 
        capacity: 112, 
        type: "In-Processor Memory", 
        bandwidth: 9600,
        busWidth: 3072
      },
      powerSpecs: { 
        tdp: 3200
      },
      connectivity: ["IPU-Link", "100 GbE"],
      supportedFrameworks: ["PyTorch", "TensorFlow", "PopART"],
      formFactor: "Rack-mounted",
      complianceInfo: {
        exportRestrictions: ["RU", "CN"],
        certifications: ["FCC", "CE", "RoHS"]
      },
      benchmarks: {
        mlTraining: { "ResNet50": 28500, "BERT-Large": 9200 }
      },
      availability: "8-10 weeks",
      warranty: "2 years",
      releaseDate: "2021-07-14",
      inStock: false
    }
  ];

  // Get AI hardware products endpoint
  app.get("/api/products/ai-hardware", async (req: Request, res: Response) => {
    try {
      log("Serving AI hardware products data", "express");
      res.json(aiHardwareProducts);
    } catch (error) {
      console.error("Error fetching AI hardware products:", error);
      res.status(500).json({ error: "Failed to fetch AI hardware products" });
    }
  });

  // Compliance check endpoint for AI hardware
  app.get("/api/compliance", async (req: Request, res: Response) => {
    try {
      const countryCode = req.query.country as string;
      const productId = parseInt(req.query.productId as string);

      if (!countryCode) {
        return res.status(400).json({ error: "Country code is required" });
      }

      if (isNaN(productId)) {
        return res.status(400).json({ error: "Valid product ID is required" });
      }

      log(`Checking compliance for product ${productId} in country ${countryCode}`, "express");
      
      const product = aiHardwareProducts.find(p => p.id === productId);
      
      if (!product) {
        return res.status(404).json({ error: "Product not found" });
      }

      // Check if the product has export restrictions for the selected country
      const hasExportRestriction = product.complianceInfo.exportRestrictions?.includes(countryCode);
      
      let riskLevel = "low";
      let notes = "";
      const requiredActions = [];

      if (hasExportRestriction) {
        riskLevel = "critical";
        notes = `${product.name} cannot be exported to the selected country due to export controls.`;
        requiredActions.push("Contact legal department for export control assessment");
        requiredActions.push("Consider alternative products without export restrictions");
      } else if (product.computeSpecs.tensorFlops && product.computeSpecs.tensorFlops > 400) {
        // High-performance equipment often has extra compliance requirements
        riskLevel = "medium";
        notes = `${product.name} is a high-performance AI accelerator that may require additional export documentation.`;
        requiredActions.push("Complete end-user verification form");
        requiredActions.push("Provide statement of intended use case");
      } else if (product.price > 100000) {
        // Very expensive equipment may need financial compliance checks
        riskLevel = "medium";
        notes = `${product.name} exceeds the high-value threshold and requires additional financial verification.`;
        requiredActions.push("Complete financial compliance verification");
      }

      const result = {
        allowed: !hasExportRestriction,
        riskLevel,
        notes,
        requiredActions
      };

      return res.json(result);
    } catch (error) {
      console.error("Error checking compliance:", error);
      res.status(500).json({ error: "Failed to check compliance" });
    }
  });

  // Frameworks compatibility check endpoint for AI hardware
  app.get("/api/frameworks-compatibility", async (req: Request, res: Response) => {
    try {
      const productId = parseInt(req.query.productId as string);
      const frameworks = (req.query.frameworks as string || "").split(",").filter(Boolean);

      if (isNaN(productId)) {
        return res.status(400).json({ error: "Valid product ID is required" });
      }

      if (!frameworks || frameworks.length === 0) {
        return res.status(400).json({ error: "At least one framework must be specified" });
      }

      log(`Checking framework compatibility for product ${productId} with frameworks ${frameworks.join(", ")}`, "express");
      
      const product = aiHardwareProducts.find(p => p.id === productId);
      
      if (!product) {
        return res.status(404).json({ error: "Product not found" });
      }

      const supportedFrameworks = product.supportedFrameworks || [];
      const compatibility = frameworks.map(framework => ({
        framework,
        supported: supportedFrameworks.includes(framework),
        notes: supportedFrameworks.includes(framework) 
          ? `${framework} is fully supported by ${product.name}`
          : `${framework} is not officially supported by ${product.name}`
      }));

      return res.json({
        productId,
        productName: product.name,
        manufacturer: product.manufacturer,
        compatibility
      });
    } catch (error) {
      console.error("Error checking framework compatibility:", error);
      res.status(500).json({ error: "Failed to check framework compatibility" });
    }
  });

  // Performance comparison endpoint for AI hardware
  app.get("/api/hardware-comparison", async (req: Request, res: Response) => {
    try {
      const productIds = (req.query.productIds as string || "").split(",").map(id => parseInt(id)).filter(id => !isNaN(id));
      const metric = req.query.metric as string || "fp32Performance";

      if (!productIds || productIds.length === 0) {
        return res.status(400).json({ error: "At least one product ID must be specified" });
      }

      log(`Comparing performance of products ${productIds.join(", ")} using metric ${metric}`, "express");
      
      const products = aiHardwareProducts.filter(p => productIds.includes(p.id));
      
      if (products.length === 0) {
        return res.status(404).json({ error: "No products found with the specified IDs" });
      }

      // Determine which metrics to compare based on the requested metric
      let comparisonData;
      
      if (metric === "mlTraining") {
        // Compare ML training performance on ResNet50
        comparisonData = products.map(p => ({
          id: p.id,
          name: p.name,
          manufacturer: p.manufacturer,
          metric: "MLPerf ResNet50",
          value: p.benchmarks?.mlTraining?.["ResNet50"] || 0,
          unit: "images/sec"
        })).sort((a, b) => b.value - a.value);
      } else if (metric === "llmInference") {
        // Compare LLM inference performance
        comparisonData = products.map(p => ({
          id: p.id,
          name: p.name,
          manufacturer: p.manufacturer,
          metric: "LLM Inference",
          value: p.benchmarks?.llmInference?.["GPT-3"] || 0,
          unit: "tokens/sec"
        })).sort((a, b) => b.value - a.value);
      } else if (metric === "memoryBandwidth") {
        // Compare memory bandwidth
        comparisonData = products.map(p => ({
          id: p.id,
          name: p.name,
          manufacturer: p.manufacturer,
          metric: "Memory Bandwidth",
          value: p.memorySpecs?.bandwidth || 0,
          unit: "GB/s"
        })).sort((a, b) => b.value - a.value);
      } else {
        // Default to comparing raw performance metrics (fp32, fp16, tensorFlops)
        comparisonData = products.map(p => ({
          id: p.id,
          name: p.name,
          manufacturer: p.manufacturer,
          metric: metric === "fp16Performance" ? "FP16 Performance" : 
                  metric === "tensorFlops" ? "Tensor Performance" : "FP32 Performance",
          value: p.computeSpecs?.[metric as keyof typeof p.computeSpecs] || 0,
          unit: metric === "tensorFlops" ? "TFLOPs" : "TFLOPs"
        })).sort((a, b) => b.value - a.value);
      }

      // Add relative performance compared to the best product
      const maxValue = comparisonData[0].value;
      comparisonData.forEach(item => {
        item.relativePerformance = maxValue > 0 ? (item.value / maxValue) * 100 : 0;
      });

      return res.json({
        metric,
        products: comparisonData
      });
    } catch (error) {
      console.error("Error comparing hardware performance:", error);
      res.status(500).json({ error: "Failed to compare hardware performance" });
    }
  });

  // No helper functions needed - All AI operations are handled by the Python backend
  
  const httpServer = createServer(app);
  
  return httpServer;
}
