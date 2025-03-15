import { useEffect, useState } from "react";
import { useParams, useLocation } from "wouter";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { Badge } from "@/components/ui/badge";
import { getRFQById } from "@/lib/supplier-service";
import { useRfq } from "@/context/rfq-context";
import { Skeleton } from "@/components/ui/skeleton";

export default function ReviewRequirements() {
  const { id } = useParams<{ id: string }>();
  const [, navigate] = useLocation();
  const { toast } = useToast();
  const { setRfqId, setExtractedRequirements } = useRfq();
  const [loading, setLoading] = useState(true);
  const [rfq, setRfq] = useState<any>(null);
  const [requirements, setRequirements] = useState<any>(null);

  useEffect(() => {
    async function fetchRfq() {
      try {
        setLoading(true);
        const rfqData = await getRFQById(Number(id));
        setRfq(rfqData);
        setRequirements(rfqData.extractedRequirements);
        
        // Update context
        setRfqId(Number(id));
        setExtractedRequirements(rfqData.extractedRequirements);
      } catch (error) {
        console.error("Error fetching RFQ:", error);
        toast({
          title: "Error",
          description: "Failed to load RFQ requirements. Please try again.",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    }
    
    if (id) {
      fetchRfq();
    }
  }, [id, setRfqId, setExtractedRequirements, toast]);
  
  const handleGoBack = () => {
    navigate("/");
  };
  
  const handleFindSuppliers = () => {
    navigate(`/match/${id}`);
  };
  
  // Render loading skeleton
  if (loading) {
    return (
      <div className="max-w-4xl mx-auto">
        <Card>
          <CardContent className="pt-6">
            <Skeleton className="h-8 w-2/5 mb-2" />
            <Skeleton className="h-4 w-4/5 mb-6" />
            
            <Skeleton className="h-16 w-full mb-6" />
            
            <div className="mb-8">
              <Skeleton className="h-6 w-1/4 mb-3" />
              <div className="flex flex-wrap gap-2 mb-4">
                <Skeleton className="h-8 w-24" />
                <Skeleton className="h-8 w-24" />
              </div>
            </div>
            
            {/* Laptop specs skeleton */}
            <div className="mb-8">
              <div className="flex justify-between items-center mb-3">
                <Skeleton className="h-6 w-1/3" />
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Array(10).fill(0).map((_, i) => (
                    <div key={i}>
                      <Skeleton className="h-4 w-1/3 mb-1" />
                      <Skeleton className="h-5 w-4/5" />
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            {/* Monitor specs skeleton */}
            <div className="mb-8">
              <div className="flex justify-between items-center mb-3">
                <Skeleton className="h-6 w-1/3" />
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Array(9).fill(0).map((_, i) => (
                    <div key={i}>
                      <Skeleton className="h-4 w-1/3 mb-1" />
                      <Skeleton className="h-5 w-4/5" />
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="flex justify-between mt-8">
              <Skeleton className="h-10 w-28" />
              <Skeleton className="h-10 w-40" />
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }
  
  if (!rfq || !requirements) {
    return (
      <div className="max-w-4xl mx-auto">
        <Card>
          <CardContent className="pt-6">
            <h2 className="text-2xl font-medium mb-2">RFQ Not Found</h2>
            <p className="text-gray-600 mb-6">
              The requested RFQ could not be found or has not been properly processed.
            </p>
            <Button onClick={handleGoBack}>Return to Upload</Button>
          </CardContent>
        </Card>
      </div>
    );
  }
  
  return (
    <div className="max-w-4xl mx-auto">
      <Card>
        <CardContent className="pt-6">
          <h2 className="text-2xl font-medium mb-2">Extracted RFQ Requirements</h2>
          <p className="text-gray-600 mb-6">
            We've analyzed your RFQ document and extracted the following requirements. 
            Please review and make any necessary corrections before proceeding.
          </p>
          
          <div className="bg-blue-50 border-l-4 border-primary p-4 mb-6">
            <div className="flex">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 text-primary mr-2"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <p className="text-sm text-gray-700">
                <span className="font-medium">RFQ Title:</span> {" "}
                <span>{requirements.title}</span>
              </p>
            </div>
          </div>
          
          <div className="mb-8">
            <h3 className="text-lg font-medium mb-3">Product Categories</h3>
            <div className="flex flex-wrap gap-2 mb-4">
              {requirements.categories?.map((category: string, index: number) => (
                <Badge key={index} variant="outline" className="px-3 py-1 text-sm font-medium">
                  {category}
                </Badge>
              ))}
            </div>
          </div>
          
          {/* Laptops Specifications */}
          {requirements.laptops && (
            <div className="mb-8">
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-lg font-medium">Laptop Specifications</h3>
                <Button variant="ghost" size="sm" className="text-primary hover:text-primary-dark flex items-center text-sm">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-4 w-4 mr-1"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
                    />
                  </svg>
                  Edit
                </Button>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Object.entries(requirements.laptops).map(([key, value]: [string, any]) => (
                    <div key={key}>
                      <p className="text-sm text-gray-500 mb-1">{key.charAt(0).toUpperCase() + key.slice(1)}</p>
                      <p className="font-medium">{value}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
          
          {/* Monitors Specifications */}
          {requirements.monitors && (
            <div className="mb-8">
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-lg font-medium">Monitor Specifications</h3>
                <Button variant="ghost" size="sm" className="text-primary hover:text-primary-dark flex items-center text-sm">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-4 w-4 mr-1"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
                    />
                  </svg>
                  Edit
                </Button>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Object.entries(requirements.monitors).map(([key, value]: [string, any]) => (
                    <div key={key}>
                      <p className="text-sm text-gray-500 mb-1">{key.charAt(0).toUpperCase() + key.slice(1)}</p>
                      <p className="font-medium">{value}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
          
          {/* Award Criteria */}
          {requirements.criteria && (
            <div className="mb-8">
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-lg font-medium">Award Criteria</h3>
                <Button variant="ghost" size="sm" className="text-primary hover:text-primary-dark flex items-center text-sm">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-4 w-4 mr-1"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
                    />
                  </svg>
                  Edit
                </Button>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <div className="flex items-center mb-1">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-5 w-5 text-amber-500 mr-1"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                      <p className="text-sm text-gray-500">Price</p>
                    </div>
                    <p className="font-medium">Weighted at {requirements.criteria.price.weight}%</p>
                  </div>
                  <div>
                    <div className="flex items-center mb-1">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-5 w-5 text-green-500 mr-1"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"
                        />
                      </svg>
                      <p className="text-sm text-gray-500">Quality</p>
                    </div>
                    <p className="font-medium">Weighted at {requirements.criteria.quality.weight}% (durability, technical specs)</p>
                  </div>
                  <div>
                    <div className="flex items-center mb-1">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-5 w-5 text-primary mr-1"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                      <p className="text-sm text-gray-500">Delivery Time</p>
                    </div>
                    <p className="font-medium">
                      Weighted at {requirements.criteria.delivery.weight}% 
                      (must deliver within 30 days of contract award)
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div className="flex justify-between mt-8">
            <Button 
              variant="outline" 
              onClick={handleGoBack}
              className="flex items-center"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 mr-2"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10 19l-7-7m0 0l7-7m-7 7h18"
                />
              </svg>
              Back
            </Button>
            <Button 
              onClick={handleFindSuppliers}
              className="flex items-center"
            >
              Find Matching Suppliers
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 ml-2"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M14 5l7 7m0 0l-7 7m7-7H3"
                />
              </svg>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
