import { apiRequest } from "./queryClient";
import type { RfqRequirements } from "@shared/schema";

// Functions for AI-related operations

/**
 * Process an RFQ document by extracting requirements using AI
 */
export async function processRfqFile(file: File): Promise<any> {
  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("/api/rfqs/upload", {
      method: "POST",
      body: formData,
      credentials: "include",
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Failed to process RFQ: ${error}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Error processing RFQ file:", error);
    throw error;
  }
}

/**
 * Process RFQ text by extracting requirements using AI
 */
export async function processRfqText(text: string): Promise<any> {
  try {
    const response = await fetch("/api/rfqs/upload", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text }),
      credentials: "include",
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Failed to process RFQ: ${error}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Error processing RFQ text:", error);
    throw error;
  }
}

/**
 * Find matching suppliers for an RFQ
 */
export async function findMatchingSuppliers(rfqId: number): Promise<any> {
  try {
    const response = await apiRequest("POST", `/api/rfqs/${rfqId}/match`);
    return await response.json();
  } catch (error) {
    console.error("Error finding matching suppliers:", error);
    throw error;
  }
}

/**
 * Generate an email template for a selected supplier
 */
export async function generateEmailTemplate(rfqId: number, supplierId: number): Promise<any> {
  try {
    const response = await apiRequest("POST", `/api/rfqs/${rfqId}/email-templates`, {
      supplierId
    });
    return await response.json();
  } catch (error) {
    console.error("Error generating email template:", error);
    throw error;
  }
}

/**
 * Update an email template
 */
export async function updateEmailTemplate(
  templateId: number, 
  data: { subject?: string; body?: string; status?: string }
): Promise<any> {
  try {
    const response = await apiRequest("PUT", `/api/email-templates/${templateId}`, data);
    return await response.json();
  } catch (error) {
    console.error("Error updating email template:", error);
    throw error;
  }
}

/**
 * Update RFQ requirements
 */
export async function updateRfqRequirements(
  rfqId: number,
  requirements: RfqRequirements
): Promise<any> {
  try {
    const response = await apiRequest("PUT", `/api/rfqs/${rfqId}`, {
      requirements
    });
    return await response.json();
  } catch (error) {
    console.error("Error updating RFQ requirements:", error);
    throw error;
  }
}
