import type { Express, Request, Response } from "express";
import { createServer, type Server } from "http";
import { log } from "./vite";
import { createProxyMiddleware } from 'http-proxy-middleware';

// Python backend URL
const PYTHON_BACKEND_URL = "http://localhost:8000";

export async function registerRoutes(app: Express): Promise<Server> {
  // Setup proxy middleware for all API routes to Python backend
  app.use('/api', createProxyMiddleware({
    target: PYTHON_BACKEND_URL,
    changeOrigin: true,
    pathRewrite: {
      '^/api': '/api', // Rewrite path from /api to /api
    },
    logLevel: 'debug',
    onProxyReq: (proxyReq, req) => {
      log(`Proxying ${req.method} request to Python backend: ${PYTHON_BACKEND_URL}${req.url}`, "proxy");
    },
    onProxyRes: (proxyRes, req) => {
      log(`Received response from Python backend: ${proxyRes.statusCode} for ${req.method} ${req.url}`, "proxy");
    },
    onError: (err, req, res) => {
      log(`Proxy error for ${req.method} ${req.url}: ${err.message}`, "proxy");
      log(`Python backend URL: ${PYTHON_BACKEND_URL}`, "proxy");
      res.status(500).json({ error: "Proxy error", message: err.message });
    }
  }));

  // Serve the React frontend
  // This assumes your React app is built and served from a 'dist' or 'build' folder
  // Adjust the path according to your frontend build output directory
  // For example, if Vite builds to './dist', you would use:
  // app.use(express.static(path.join(__dirname, "../dist")));
  // app.get("*", (_req: Request, res: Response) => {
  //   res.sendFile(path.join(__dirname, "../dist/index.html"));
  // });

  // Since this file is for registering routes for an Express app,
  // and the prompt focuses on API routing and backend logic,
  // we will not include frontend serving logic here directly.
  // Frontend serving should be handled by the main server setup
  // or a dedicated static file serving middleware.

  const httpServer = createServer(app);
  return httpServer;
}