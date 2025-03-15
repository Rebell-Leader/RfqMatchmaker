import { apiRequest } from "./queryClient";
import { SupplierMatch } from "@shared/schema";

export async function matchSuppliersForRFQ(rfqId: number): Promise<SupplierMatch[]> {
  try {
    const response = await apiRequest("POST", `/api/rfqs/${rfqId}/match-suppliers`, {});
    const data = await response.json();
    return data.matches;
  } catch (error) {
    console.error("Error matching suppliers:", error);
    throw new Error("Failed to match suppliers for RFQ");
  }
}

export async function getProductsByCategory(category: string): Promise<any[]> {
  try {
    const response = await fetch(`/api/products?category=${encodeURIComponent(category)}`, {
      credentials: "include",
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch products: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error("Error fetching products:", error);
    throw new Error("Failed to fetch products");
  }
}

export async function getAllSuppliers(): Promise<any[]> {
  try {
    const response = await fetch("/api/suppliers", {
      credentials: "include",
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch suppliers: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error("Error fetching suppliers:", error);
    throw new Error("Failed to fetch suppliers");
  }
}

export async function getRFQById(id: number): Promise<any> {
  try {
    const response = await fetch(`/api/rfqs/${id}`, {
      credentials: "include",
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch RFQ: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error("Error fetching RFQ:", error);
    throw new Error("Failed to fetch RFQ");
  }
}

export function calculateTotalPrice(product: any, quantity: number): number {
  return product.price * quantity;
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
}
