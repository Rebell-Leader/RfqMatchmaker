import { apiRequest } from "./queryClient";
import { ExtractedRequirement, EmailTemplate } from "@shared/schema";

// Use Python backend API endpoints
// We need to use "/api-python/api" because:
// 1. "/api-python" is the proxy path in Express
// 2. "/api" is the prefix in the Python FastAPI app
const PYTHON_API_PREFIX = "/api-python/api";

export async function extractRequirementsFromRFQ(fileContent: string): Promise<ExtractedRequirement> {
  try {
    const response = await apiRequest("POST", `${PYTHON_API_PREFIX}/rfqs`, { 
      title: "Extracted RFQ", 
      specifications: fileContent 
    });
    
    const data = await response.json();
    return data.extractedRequirements;
  } catch (error) {
    console.error("Error extracting requirements:", error);
    throw new Error("Failed to extract requirements from RFQ");
  }
}

export async function uploadRFQFile(file: File): Promise<number> {
  try {
    console.log("Attempting to upload file to Python backend...");
    const formData = new FormData();
    formData.append("file", file);
    
    // For debugging
    console.log("File being uploaded:", file.name, file.type, file.size);
    
    try {
      // Try Python backend first
      const response = await fetch(`${PYTHON_API_PREFIX}/rfqs/upload`, {
        method: "POST",
        body: formData,
        credentials: "include",
      });
      
      console.log("Python upload response status:", response.status);
      
      if (!response.ok) {
        throw new Error(`Failed to upload RFQ to Python backend: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log("Python backend upload success:", data);
      return data.id;
    } catch (pythonError) {
      console.error("Python backend upload failed:", pythonError);
      console.log("Falling back to Node.js backend...");
      
      // Fallback to Node.js backend
      const nodeFormData = new FormData();
      nodeFormData.append("file", file);
      
      const nodeResponse = await fetch("/api/rfqs/upload", {
        method: "POST",
        body: nodeFormData,
        credentials: "include",
      });
      
      console.log("Node.js upload response status:", nodeResponse.status);
      
      if (!nodeResponse.ok) {
        throw new Error(`Failed to upload RFQ to Node.js backend: ${nodeResponse.statusText}`);
      }
      
      const nodeData = await nodeResponse.json();
      console.log("Node.js backend upload success:", nodeData);
      return nodeData.id;
    }
  } catch (error) {
    console.error("Error uploading RFQ file (both backends failed):", error);
    throw new Error("Failed to upload RFQ file. Please try again later.");
  }
}

export async function createManualRFQ(
  title: string, 
  description: string, 
  specifications: string
): Promise<number> {
  try {
    console.log("Creating manual RFQ with:", { title, description, specifications });
    
    // First, try the Python backend
    try {
      const response = await apiRequest("POST", `${PYTHON_API_PREFIX}/rfqs`, { 
        title, 
        description, 
        specifications 
      });
      
      const data = await response.json();
      console.log("Python backend RFQ creation response:", data);
      return data.id;
    } catch (pythonError) {
      console.error("Python backend RFQ creation failed:", pythonError);
      console.log("Falling back to Node backend...");
      
      // Fallback to the Node backend if Python fails
      const nodeResponse = await apiRequest("POST", "/api/rfqs", { 
        title, 
        description, 
        specifications 
      });
      
      const nodeData = await nodeResponse.json();
      console.log("Node backend RFQ creation response:", nodeData);
      return nodeData.id;
    }
  } catch (error) {
    console.error("Error creating manual RFQ (both backends failed):", error);
    throw new Error("Failed to create RFQ. Please try again later.");
  }
}

export async function generateEmailProposal(proposalId: number): Promise<EmailTemplate> {
  try {
    const response = await apiRequest(
      "POST", 
      `${PYTHON_API_PREFIX}/proposals/${proposalId}/generate-email`,
      {}
    );
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error generating email proposal:", error);
    throw new Error("Failed to generate email proposal");
  }
}
