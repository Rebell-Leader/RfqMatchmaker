import { apiRequest } from "./queryClient";
import { ExtractedRequirement, EmailTemplate } from "@shared/schema";

// Use Python backend API endpoints
const PYTHON_API_PREFIX = "/api-python";

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
    console.log("Uploading file to Python backend...");
    const formData = new FormData();
    formData.append("file", file);
    
    // For debugging
    console.log("File being uploaded:", file.name, file.type, file.size);
    
    const response = await fetch(`${PYTHON_API_PREFIX}/rfqs/upload`, {
      method: "POST",
      body: formData,
      credentials: "include",
    });
    
    console.log("Upload response status:", response.status);
    
    if (!response.ok) {
      throw new Error(`Failed to upload RFQ: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.id;
  } catch (error) {
    console.error("Error uploading RFQ file:", error);
    throw new Error("Failed to upload RFQ file");
  }
}

export async function createManualRFQ(
  title: string, 
  description: string, 
  specifications: string
): Promise<number> {
  try {
    const response = await apiRequest("POST", `${PYTHON_API_PREFIX}/rfqs`, { 
      title, 
      description, 
      specifications 
    });
    
    const data = await response.json();
    return data.id;
  } catch (error) {
    console.error("Error creating manual RFQ:", error);
    throw new Error("Failed to create RFQ");
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
