import { apiRequest } from "./queryClient";
import { ExtractedRequirement, EmailTemplate } from "@shared/schema";

export async function extractRequirementsFromRFQ(fileContent: string): Promise<ExtractedRequirement> {
  try {
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

export async function uploadRFQFile(file: File): Promise<number> {
  try {
    const formData = new FormData();
    formData.append("file", file);
    
    const response = await fetch("/api/rfqs/upload", {
      method: "POST",
      body: formData,
      credentials: "include",
    });
    
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
    const response = await apiRequest("POST", "/api/rfqs", { 
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
