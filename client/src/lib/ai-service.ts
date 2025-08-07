import { apiRequest } from "./queryClient";
import { ExtractedRequirement, EmailTemplate } from "@shared/schema";

/**
 * Extract structured requirements from RFQ content
 * Uses Node.js backend which proxies to Python backend's AI service
 */
export async function extractRequirementsFromRFQ(fileContent: string): Promise<ExtractedRequirement> {
  try {
    // Using the Node.js backend which proxies to Python
    const response = await apiRequest("POST", "/api/rfqs", { 
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

/**
 * Upload an RFQ file for processing
 * Uses Node.js backend which proxies to Python backend
 */
export async function uploadRFQFile(file: File): Promise<number> {
  try {
    console.log("Uploading file:", file.name, file.type, file.size);
    
    const formData = new FormData();
    formData.append("file", file);
    
    // Use Node.js backend which proxies to Python backend
    const response = await fetch("/api/rfqs/upload", {
      method: "POST",
      body: formData,
      credentials: "include",
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error("Upload error:", errorText);
      throw new Error(`Failed to upload RFQ: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log("Upload success:", data);
    return data.id;
  } catch (error) {
    console.error("Error uploading RFQ file:", error);
    throw new Error("Failed to upload RFQ file. Please try again later.");
  }
}

/**
 * Create an RFQ manually with text input
 * Uses Node.js backend which proxies to Python backend
 */
export async function createManualRFQ(
  title: string, 
  description: string, 
  specifications: string
): Promise<number> {
  try {
    console.log("Creating manual RFQ with:", { title, description, specifications });
    
    // Use Node.js backend which proxies to Python backend
    const response = await apiRequest("POST", "/api/rfqs", { 
      title, 
      description, 
      specifications 
    });
    
    const data = await response.json();
    console.log("RFQ creation response:", data);
    return data.id;
  } catch (error) {
    console.error("Error creating manual RFQ:", error);
    throw new Error("Failed to create RFQ. Please try again later.");
  }
}

/**
 * Generate an email proposal for a selected supplier
 * Uses Node.js backend which proxies to Python backend
 */
export async function generateEmailProposal(proposalId: number): Promise<EmailTemplate> {
  try {
    // Use Node.js backend which proxies to Python backend
    const response = await apiRequest(
      "POST", 
      `/api/proposals/${proposalId}/generate-email`,
      {}
    );
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error generating email proposal:", error);
    throw new Error("Failed to generate email proposal");
  }
}
