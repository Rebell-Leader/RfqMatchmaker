import { apiRequest } from "./queryClient";

/**
 * Get all suppliers
 */
export async function getSuppliers(): Promise<any> {
  try {
    const response = await apiRequest("GET", "/api/suppliers");
    return await response.json();
  } catch (error) {
    console.error("Error fetching suppliers:", error);
    throw error;
  }
}

/**
 * Get a supplier by ID
 */
export async function getSupplier(id: number): Promise<any> {
  try {
    const response = await apiRequest("GET", `/api/suppliers/${id}`);
    return await response.json();
  } catch (error) {
    console.error(`Error fetching supplier with ID ${id}:`, error);
    throw error;
  }
}

/**
 * Get supplier matches for an RFQ
 */
export async function getSupplierMatches(rfqId: number): Promise<any> {
  try {
    const response = await apiRequest("GET", `/api/rfqs/${rfqId}/matches`);
    return await response.json();
  } catch (error) {
    console.error(`Error fetching supplier matches for RFQ ${rfqId}:`, error);
    throw error;
  }
}

/**
 * Update a supplier match
 */
export async function updateSupplierMatch(
  matchId: number,
  data: { isSelected?: boolean; scores?: any }
): Promise<any> {
  try {
    const response = await apiRequest("PUT", `/api/supplier-matches/${matchId}`, data);
    return await response.json();
  } catch (error) {
    console.error(`Error updating supplier match with ID ${matchId}:`, error);
    throw error;
  }
}

/**
 * Get email templates for an RFQ
 */
export async function getEmailTemplates(rfqId: number): Promise<any> {
  try {
    const response = await apiRequest("GET", `/api/rfqs/${rfqId}/email-templates`);
    return await response.json();
  } catch (error) {
    console.error(`Error fetching email templates for RFQ ${rfqId}:`, error);
    throw error;
  }
}

/**
 * Helper function to filter supplier matches by category
 */
export function filterMatchesByCategory(matches: any[], category: string): any[] {
  return matches.filter(match => 
    match.productDetails.category.toLowerCase() === category.toLowerCase()
  );
}

/**
 * Helper function to sort supplier matches
 */
export function sortSupplierMatches(
  matches: any[],
  sortBy: "price" | "quality" | "delivery" | "totalScore" = "totalScore",
  sortOrder: "asc" | "desc" = "desc"
): any[] {
  return [...matches].sort((a, b) => {
    let aValue: number;
    let bValue: number;

    switch (sortBy) {
      case "price":
        aValue = a.scores.price.score;
        bValue = b.scores.price.score;
        break;
      case "quality":
        aValue = a.scores.quality.score;
        bValue = b.scores.quality.score;
        break;
      case "delivery":
        aValue = a.scores.delivery.score;
        bValue = b.scores.delivery.score;
        break;
      case "totalScore":
      default:
        aValue = a.totalScore;
        bValue = b.totalScore;
        break;
    }

    return sortOrder === "asc" ? aValue - bValue : bValue - aValue;
  });
}

/**
 * Find the best supplier match based on total score
 */
export function findBestSupplierMatch(matches: any[]): any | undefined {
  if (!matches || matches.length === 0) {
    return undefined;
  }

  return matches.reduce((best, current) => {
    return current.totalScore > best.totalScore ? current : best;
  }, matches[0]);
}
