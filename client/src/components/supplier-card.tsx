import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Check, Info, MapPin, Clock, Shield } from "lucide-react";

export interface SupplierCardProps {
  supplier: any;
  match: any;
  onSelect: () => void;
  onCompare: () => void;
  isSelected?: boolean;
}

export function SupplierCard({ supplier, match, onSelect, onCompare, isSelected }: SupplierCardProps) {
  const product = match.productDetails;
  const scores = match.scores;
  const totalScore = match.totalScore;

  const checkRequirement = (value: string, requirement: string): { status: 'below' | 'meets' | 'exceeds', text: string } => {
    const valueLower = value.toLowerCase();
    const reqLower = requirement.toLowerCase();

    // Check if value meets requirement
    if (valueLower.includes('year')) {
      // Handle warranty years
      const valueYears = parseInt(valueLower.match(/\d+/)?.[0] || '0');
      const reqYears = parseInt(reqLower.match(/\d+/)?.[0] || '0');
      
      if (valueYears < reqYears) {
        return { status: 'below', text: `⚠️ Below requirement` };
      } else if (valueYears > reqYears) {
        return { status: 'exceeds', text: `✓ Exceeds requirement` };
      }
      return { status: 'meets', text: `✓ Meets requirement` };
    }
    
    return { status: 'meets', text: '' };
  };

  return (
    <Card className="border border-gray-200 rounded-lg mb-4 overflow-hidden">
      <div className="flex flex-col md:flex-row">
        {/* Supplier Info */}
        <div className="p-4 md:w-1/4 bg-gray-50 border-b md:border-b-0 md:border-r border-gray-200">
          <div className="flex items-center mb-3">
            {supplier.logoUrl ? (
              <img 
                src={supplier.logoUrl} 
                alt={supplier.name} 
                className="w-8 h-8 mr-2 rounded"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = 'https://placehold.co/32x32?text=' + supplier.name.charAt(0);
                }}
              />
            ) : (
              <div className="w-8 h-8 mr-2 rounded bg-primary text-white flex items-center justify-center">
                {supplier.name.charAt(0)}
              </div>
            )}
            <h3 className="font-medium">{supplier.name}</h3>
          </div>
          <div className="flex items-center text-sm text-gray-600 mb-2">
            <MapPin className="h-4 w-4 mr-1" />
            {supplier.location || "Not specified"}
          </div>
          <div className="flex items-center text-sm text-gray-600 mb-2">
            <Clock className="h-4 w-4 mr-1" />
            Est. delivery: {match.productDetails.deliveryTime || "Not specified"}
          </div>
          <div className="flex items-center text-sm text-gray-600">
            <Shield className="h-4 w-4 mr-1" />
            {supplier.isVerified ? "Verified supplier" : "Unverified supplier"}
          </div>
        </div>
        
        {/* Product Info */}
        <div className="p-4 md:w-2/4">
          <h4 className="font-medium mb-2">{product.name}</h4>
          <div className="space-y-1 text-sm mb-3">
            {product.specifications && Object.entries(product.specifications).map(([key, value]) => {
              if (key === 'price') return null; // Skip price, it's shown elsewhere
              
              // Check if the spec is a requirement that should be validated
              let requirementStatus = null;
              if (key === 'warranty' && match.rfqRequirements?.warranty) {
                requirementStatus = checkRequirement(String(value), match.rfqRequirements.warranty);
              }
              
              return (
                <p key={key}>
                  <span className="text-gray-500">{key.charAt(0).toUpperCase() + key.slice(1)}:</span> {String(value)}
                  {requirementStatus && (
                    <span className={
                      requirementStatus.status === 'below' ? 'text-amber-600 ml-1' : 
                      requirementStatus.status === 'exceeds' ? 'text-green-600 ml-1' : 
                      'text-gray-600 ml-1'
                    }>
                      {requirementStatus.text}
                    </span>
                  )}
                </p>
              );
            })}
          </div>
          <div className="mt-3">
            <Button variant="link" className="p-0 h-auto text-primary flex items-center" size="sm">
              <Info className="h-4 w-4 mr-1" />
              View full specifications
            </Button>
          </div>
        </div>
        
        {/* Scoring Info */}
        <div className="p-4 md:w-1/4 bg-gray-50 border-t md:border-t-0 md:border-l border-gray-200">
          <div className="mb-3">
            <p className="text-2xl font-medium">
              ${product.specifications?.price || "N/A"}
              <span className="text-sm text-gray-500">/unit</span>
            </p>
            <p className="text-sm text-gray-600">
              ${(product.specifications?.price || 0) * (match.quantity || 1)} total ({match.quantity || "Unknown"} units)
            </p>
          </div>
          
          <div className="mb-4">
            <div className="flex justify-between items-center mb-1">
              <span className="text-sm text-gray-600">Match score</span>
              <span className="text-sm font-medium">{totalScore}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-primary h-2 rounded-full" 
                style={{ width: `${totalScore}%` }}
              ></div>
            </div>
          </div>
          
          <div>
            <Button
              variant={isSelected ? "secondary" : "default"}
              className="w-full mb-2"
              onClick={onSelect}
            >
              {isSelected ? (
                <>
                  <Check className="h-4 w-4 mr-2" />
                  Selected
                </>
              ) : (
                "Select"
              )}
            </Button>
            <Button
              variant="outline"
              className="w-full"
              onClick={onCompare}
            >
              Compare
            </Button>
          </div>
        </div>
      </div>
    </Card>
  );
}
