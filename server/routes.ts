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
  
  // No helper functions needed - All AI operations are handled by the Python backend
  
  const httpServer = createServer(app);
  
  return httpServer;
}
