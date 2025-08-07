
<old_str>import express, { type Request, Response, NextFunction } from "express";
import { registerRoutes } from "./routes";
import { setupVite, serveStatic, log } from "./vite";
import { spawn } from "child_process";
import path from "path";

// Start the Python backend
const startPythonBackend = () => {
  log("Starting Python backend server...", "python");
  
  const pythonProcess = spawn("python", ["-m", "python_backend.main"], {
    stdio: ["ignore", "pipe", "pipe"]
  });
  
  pythonProcess.stdout.on("data", (data) => {
    log(`[Python] ${data.toString().trim()}`, "python");
  });
  
  pythonProcess.stderr.on("data", (data) => {
    log(`[Python Error] ${data.toString().trim()}`, "python");
  });
  
  pythonProcess.on("close", (code) => {
    log(`Python backend process exited with code ${code}`, "python");
    if (code !== 0) {
      // Restart the Python backend after a delay if it crashes
      setTimeout(startPythonBackend, 5000);
    }
  });
};

// Start the Python backend
startPythonBackend();

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

app.use((req, res, next) => {
  const start = Date.now();
  const path = req.path;
  let capturedJsonResponse: Record<string, any> | undefined = undefined;

  const originalResJson = res.json;
  res.json = function (bodyObj, ...args) {
    capturedJsonResponse = bodyObj;
    return originalResJson.apply(res, [bodyObj, ...args]);
  };

  res.on("finish", () => {
    const duration = Date.now() - start;
    if (path.startsWith("/api")) {
      let logLine = `${req.method} ${path} ${res.statusCode} in ${duration}ms`;
      if (capturedJsonResponse) {
        logLine += ` :: ${JSON.stringify(capturedJsonResponse)}`;
      }

      if (logLine.length > 80) {
        logLine = logLine.slice(0, 79) + "…";
      }

      log(logLine, "express");
    }
  });

  next();
});

(async () => {
  registerRoutes(app);
  const server = setupVite(app, server);
})();</old_str>
<new_str>import express, { type Request, Response, NextFunction } from "express";
import { registerRoutes } from "./routes";
import { setupVite, serveStatic, log } from "./vite";
import { spawn } from "child_process";
import { createServer } from "http";

// Start the Python backend
const startPythonBackend = () => {
  log("Starting Python backend server...", "python");
  
  const pythonProcess = spawn("python", ["-m", "python_backend.main"], {
    stdio: ["ignore", "pipe", "pipe"]
  });
  
  pythonProcess.stdout.on("data", (data) => {
    log(`[Python] ${data.toString().trim()}`, "python");
  });
  
  pythonProcess.stderr.on("data", (data) => {
    log(`[Python Error] ${data.toString().trim()}`, "python");
  });
  
  pythonProcess.on("close", (code) => {
    log(`Python backend process exited with code ${code}`, "python");
    if (code !== 0) {
      // Restart the Python backend after a delay if it crashes
      setTimeout(startPythonBackend, 5000);
    }
  });
  
  return pythonProcess;
};

// Start the Python backend
const pythonProcess = startPythonBackend();

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

app.use((req, res, next) => {
  const start = Date.now();
  const path = req.path;
  let capturedJsonResponse: Record<string, any> | undefined = undefined;

  const originalResJson = res.json;
  res.json = function (bodyObj, ...args) {
    capturedJsonResponse = bodyObj;
    return originalResJson.apply(res, [bodyObj, ...args]);
  };

  res.on("finish", () => {
    const duration = Date.now() - start;
    if (path.startsWith("/api")) {
      let logLine = `${req.method} ${path} ${res.statusCode} in ${duration}ms`;
      if (capturedJsonResponse) {
        logLine += ` :: ${JSON.stringify(capturedJsonResponse)}`;
      }

      if (logLine.length > 80) {
        logLine = logLine.slice(0, 79) + "…";
      }

      log(logLine, "express");
    }
  });

  next();
});

(async () => {
  registerRoutes(app);
  const server = createServer(app);
  await setupVite(app, server);
  
  const PORT = process.env.PORT || 5000;
  server.listen(PORT, "0.0.0.0", () => {
    log(`serving on port ${PORT}`, "express");
  });
  
  // Handle shutdown gracefully
  process.on('SIGTERM', () => {
    log("Shutting down gracefully...", "express");
    pythonProcess.kill();
    server.close(() => {
      process.exit(0);
    });
  });
})();</new_str>
