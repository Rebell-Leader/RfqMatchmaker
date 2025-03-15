export function formatSpecifications(specs: Record<string, any>): Array<{ key: string; value: string; warning?: string }> {
  if (!specs) return [];
  
  return Object.entries(specs).map(([key, value]) => {
    // Format the key with proper capitalization
    const formattedKey = key.charAt(0).toUpperCase() + key.slice(1);
    
    // Format value and check for warnings
    let warning: string | undefined;
    
    // For warranty, check for potential warnings (e.g., if less than 2 years)
    if (key === 'warranty' && typeof value === 'string') {
      const warrantyYears = parseInt(value.match(/\d+/)?.[0] || '0');
      if (warrantyYears < 2) {
        warning = 'Below requirement';
      } else if (warrantyYears > 2) {
        warning = 'Exceeds requirement';
      }
    }
    
    return {
      key: formattedKey,
      value: String(value),
      warning
    };
  });
}

export function parseDeliveryTime(deliveryTime: string): number {
  // Extract numbers from delivery time string (e.g., "15-20 days" -> [15, 20])
  const numbers = deliveryTime.match(/\d+/g)?.map(Number) || [30];
  
  // Calculate the average delivery time
  return numbers.reduce((sum, num) => sum + num, 0) / numbers.length;
}

export function formatWarningText(warningType: string): { text: string; color: string } {
  switch (warningType) {
    case 'Below requirement':
      return { text: '⚠️ Below requirement', color: 'text-amber-600' };
    case 'Exceeds requirement':
      return { text: '✓ Exceeds requirement', color: 'text-green-600' };
    default:
      return { text: warningType, color: 'text-gray-600' };
  }
}

export function sortSupplierMatches(matches: any[], sortBy: string): any[] {
  if (!matches || matches.length === 0) return [];
  
  const clonedMatches = [...matches];
  
  switch (sortBy) {
    case 'price-asc':
      return clonedMatches.sort((a, b) => a.product.price - b.product.price);
    case 'price-desc':
      return clonedMatches.sort((a, b) => b.product.price - a.product.price);
    case 'match-score':
      return clonedMatches.sort((a, b) => b.matchScore - a.matchScore);
    case 'delivery-time':
      return clonedMatches.sort((a, b) => {
        const aTime = parseDeliveryTime(a.supplier.deliveryTime);
        const bTime = parseDeliveryTime(b.supplier.deliveryTime);
        return aTime - bTime;
      });
    default:
      return clonedMatches;
  }
}

export function filterSupplierMatches(matches: any[], filters: Record<string, string>): any[] {
  if (!matches || matches.length === 0) return [];
  
  return matches.filter(match => {
    const specs = match.product.specifications;
    
    // Check processor filter
    if (filters.processor && filters.processor !== 'all') {
      const processorSpec = specs.processor?.toLowerCase() || '';
      if (!processorSpec.includes(filters.processor.toLowerCase())) {
        return false;
      }
    }
    
    // Check memory filter
    if (filters.memory && filters.memory !== 'all') {
      const memorySpec = specs.memory?.toLowerCase() || '';
      if (!memorySpec.includes(filters.memory.toLowerCase())) {
        return false;
      }
    }
    
    return true;
  });
}

export function getUniqueFilterOptions(matches: any[]): Record<string, string[]> {
  if (!matches || matches.length === 0) {
    return {
      processors: [],
      memories: []
    };
  }
  
  const processors = new Set<string>();
  const memories = new Set<string>();
  
  matches.forEach(match => {
    const specs = match.product.specifications;
    
    // Extract processor options
    if (specs.processor) {
      const processorType = specs.processor.includes('i5') ? 'Intel Core i5' :
                           specs.processor.includes('i7') ? 'Intel Core i7' :
                           specs.processor.includes('Ryzen 5') ? 'AMD Ryzen 5' :
                           specs.processor.includes('Ryzen 7') ? 'AMD Ryzen 7' :
                           'Other';
      processors.add(processorType);
    }
    
    // Extract memory options
    if (specs.memory) {
      const memorySize = specs.memory.includes('16 GB') ? '16 GB' :
                         specs.memory.includes('32 GB') ? '32 GB' :
                         specs.memory.includes('64 GB') ? '64 GB' :
                         'Other';
      memories.add(memorySize);
    }
  });
  
  return {
    processors: Array.from(processors),
    memories: Array.from(memories)
  };
}
