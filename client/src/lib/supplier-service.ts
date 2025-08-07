import { apiRequest } from "./queryClient";
import { SupplierMatch } from "@shared/schema";

/**
 * Match suppliers for an RFQ using AI-driven analysis
 * Uses Node.js backend which proxies to Python backend
 */
export async function matchSuppliersForRFQ(rfqId: number): Promise<SupplierMatch[]> {
  try {
    // Use Node.js backend which proxies to Python backend
    const response = await apiRequest("POST", `/api/rfqs/${rfqId}/match-suppliers`, {});
    const data = await response.json();
    return data.matches;
  } catch (error) {
    console.error("Error matching suppliers:", error);
    throw new Error("Failed to match suppliers for RFQ");
  }
}

/**
 * Get products by category
 * Uses Node.js backend which proxies to Python backend
 */
export async function getProductsByCategory(category: string): Promise<any[]> {
  try {
    // Use Node.js backend which proxies to Python backend
    const response = await apiRequest("GET", `/api/products?category=${encodeURIComponent(category)}`, null);
    return await response.json();
  } catch (error) {
    console.error("Error fetching products:", error);
    throw new Error("Failed to fetch products");
  }
}

/**
 * Get all suppliers from the database
 * Uses Node.js backend which proxies to Python backend
 */
export async function getAllSuppliers(): Promise<any[]> {
  try {
    // Use Node.js backend which proxies to Python backend
    const response = await apiRequest("GET", "/api/suppliers", null);
    return await response.json();
  } catch (error) {
    console.error("Error fetching suppliers:", error);
    throw new Error("Failed to fetch suppliers");
  }
}

/**
 * Get RFQ details by ID
 * Uses Node.js backend which proxies to Python backend
 */
export async function getRFQById(id: number): Promise<any> {
  try {
    // Use Node.js backend which proxies to Python backend
    const response = await apiRequest("GET", `/api/rfqs/${id}`, null);
    return await response.json();
  } catch (error) {
    console.error("Error fetching RFQ:", error);
    throw new Error("Failed to fetch RFQ");
  }
}

/**
 * Calculate the total price for a product based on quantity
 */
export function calculateTotalPrice(product: any, quantity: number): number {
  return product.price * quantity;
}

/**
 * Format a number as currency (USD)
 */
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
}
