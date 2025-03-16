import { useEffect, useState } from "react";
import { useParams, useLocation } from "wouter";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useRfq } from "@/context/rfq-context";
import { useDemoMode } from "@/context/demo-context";
import { getRFQById, formatCurrency } from "@/lib/supplier-service";
import { Skeleton } from "@/components/ui/skeleton";

export default function ScoreResults() {
  const { id } = useParams<{ id: string }>();
  const [, navigate] = useLocation();
  const { toast } = useToast();
  const { setRfqId, selectedMatches, setSelectedMatches } = useRfq();
  const { isDemoMode, demoRfq, demoSupplierMatches, simulateProcessing } = useDemoMode();
  
  const [loading, setLoading] = useState(true);
  const [rfq, setRfq] = useState<any>(null);
  const [requirements, setRequirements] = useState<any>(null);
  
  useEffect(() => {
    async function fetchRfq() {
      try {
        setLoading(true);
        
        // If in demo mode, use demo data
        if (isDemoMode && String(demoRfq.id) === id) {
          // Simulate processing delay
          setTimeout(() => {
            setRfq(demoRfq);
            setRequirements(demoRfq.extractedRequirements);
            
            // Update context
            setRfqId(demoRfq.id);
            
            // If no suppliers are selected in demo mode, select top 3
            if (selectedMatches.length === 0) {
              const topMatches = [...demoSupplierMatches]
                .sort((a, b) => b.matchScore - a.matchScore)
                .slice(0, 3);
              setSelectedMatches(topMatches);
            }
            
            setLoading(false);
          }, 1000);
          return;
        }
        
        // Otherwise fetch real data
        const rfqData = await getRFQById(Number(id));
        setRfq(rfqData);
        setRequirements(rfqData.extractedRequirements);
        
        // Update context
        setRfqId(Number(id));
      } catch (error) {
        console.error("Error fetching RFQ:", error);
        toast({
          title: "Error",
          description: "Failed to load RFQ. Please try again.",
          variant: "destructive",
        });
      } finally {
        if (!isDemoMode) {
          setLoading(false);
        }
      }
    }
    
    if (id) {
      fetchRfq();
    }
  }, [id, setRfqId, toast, isDemoMode, demoRfq, demoSupplierMatches, selectedMatches, setSelectedMatches]);
  
  const handleGoBack = () => {
    navigate(`/match/${id}`);
  };
  
  const handleGenerateProposals = () => {
    // Find the recommended supplier (highest match score)
    const recommendedMatch = selectedMatches.length > 0 
      ? selectedMatches.reduce((prev, current) => 
          prev.matchScore > current.matchScore ? prev : current
        )
      : null;
    
    if (recommendedMatch) {
      setSelectedMatches([recommendedMatch]); // Set only the recommended match
      navigate(`/proposals/${id}`);
    } else {
      toast({
        title: "No supplier selected",
        description: "Please go back and select at least one supplier to generate a proposal.",
        variant: "destructive",
      });
    }
  };
  
  // Find the recommended supplier (with highest match score)
  const recommendedSupplier = selectedMatches.length > 0 
    ? selectedMatches.reduce((prev, current) => 
        prev.matchScore > current.matchScore ? prev : current
      )
    : null;
  
  // Render loading skeleton
  if (loading) {
    return (
      <div className="max-w-5xl mx-auto">
        <Card>
          <CardContent className="pt-6">
            <Skeleton className="h-8 w-2/5 mb-2" />
            <Skeleton className="h-4 w-4/5 mb-6" />
            
            <div className="mb-8">
              <Skeleton className="h-6 w-1/4 mb-4" />
              
              <div className="overflow-x-auto">
                <Skeleton className="h-64 w-full mb-4" />
              </div>
            </div>
            
            <Skeleton className="h-28 w-full mb-8" />
            
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
      <div className="max-w-5xl mx-auto">
        <Card>
          <CardContent className="pt-6">
            <h2 className="text-2xl font-medium mb-2">RFQ Not Found</h2>
            <p className="text-gray-600 mb-6">
              The requested RFQ could not be found or has not been properly processed.
            </p>
            <Button onClick={() => navigate("/upload")}>Return to Upload</Button>
          </CardContent>
        </Card>
      </div>
    );
  }
  
  if (selectedMatches.length === 0) {
    return (
      <div className="max-w-5xl mx-auto">
        <Card>
          <CardContent className="pt-6">
            <h2 className="text-2xl font-medium mb-2">No Suppliers Selected</h2>
            <p className="text-gray-600 mb-6">
              You haven't selected any suppliers to compare. Please go back and select at least one supplier.
            </p>
            <Button onClick={handleGoBack}>Return to Supplier Matching</Button>
          </CardContent>
        </Card>
      </div>
    );
  }
  
  return (
    <div className="max-w-5xl mx-auto">
      <Card>
        <CardContent className="pt-6">
          <h2 className="text-2xl font-medium mb-2">Compare and Score Results</h2>
          <p className="text-gray-600 mb-6">
            Compare your selected suppliers based on the scoring criteria defined in your RFQ.
          </p>
          
          {/* Selected Suppliers */}
          <div className="mb-8">
            <h3 className="text-lg font-medium mb-4">Selected Suppliers</h3>
            
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="bg-gray-50">
                    <TableHead className="w-[180px]">Criteria</TableHead>
                    <TableHead>Weight</TableHead>
                    {selectedMatches.map((match, index) => (
                      <TableHead key={index}>
                        <div className="flex items-center">
                          <img 
                            src={match.supplier.logoUrl} 
                            alt={match.supplier.name} 
                            className="w-6 h-6 mr-2 rounded" 
                          />
                          {match.product.name}
                        </div>
                      </TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {/* Price Row */}
                  <TableRow className="border-t border-gray-200">
                    <TableCell>
                      <div className="flex items-center">
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          className="h-5 w-5 text-amber-500 mr-2"
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
                        <span className="font-medium">Price</span>
                      </div>
                    </TableCell>
                    <TableCell>{requirements.criteria?.price?.weight || 50}%</TableCell>
                    {selectedMatches.map((match, index) => (
                      <TableCell key={index}>
                        <div>
                          <div className="font-medium">{formatCurrency(match.product.price)}/unit</div>
                          <div className="text-sm text-gray-500">
                            Score: {Math.round(match.matchDetails.price)}/{requirements.criteria?.price?.weight || 50}
                          </div>
                        </div>
                      </TableCell>
                    ))}
                  </TableRow>
                  
                  {/* Quality Row */}
                  <TableRow className="border-t border-gray-200">
                    <TableCell>
                      <div className="flex items-center">
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          className="h-5 w-5 text-green-500 mr-2"
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
                        <span className="font-medium">Quality</span>
                      </div>
                    </TableCell>
                    <TableCell>{requirements.criteria?.quality?.weight || 30}%</TableCell>
                    {selectedMatches.map((match, index) => {
                      const qualityLevel = match.matchDetails.quality > 25 ? "Premium quality" : 
                                         match.matchDetails.quality > 20 ? "High quality" : "Standard quality";
                      return (
                        <TableCell key={index}>
                          <div>
                            <div className="font-medium">{qualityLevel}</div>
                            <div className="text-sm text-gray-500">
                              Score: {Math.round(match.matchDetails.quality)}/{requirements.criteria?.quality?.weight || 30}
                            </div>
                          </div>
                        </TableCell>
                      )
                    })}
                  </TableRow>
                  
                  {/* Delivery Row */}
                  <TableRow className="border-t border-gray-200">
                    <TableCell>
                      <div className="flex items-center">
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
                            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                          />
                        </svg>
                        <span className="font-medium">Delivery Time</span>
                      </div>
                    </TableCell>
                    <TableCell>{requirements.criteria?.delivery?.weight || 20}%</TableCell>
                    {selectedMatches.map((match, index) => (
                      <TableCell key={index}>
                        <div>
                          <div className="font-medium">{match.supplier.deliveryTime}</div>
                          <div className="text-sm text-gray-500">
                            Score: {Math.round(match.matchDetails.delivery)}/{requirements.criteria?.delivery?.weight || 20}
                          </div>
                        </div>
                      </TableCell>
                    ))}
                  </TableRow>
                  
                  {/* Total Score Row */}
                  <TableRow className="border-t border-gray-200 bg-gray-50">
                    <TableCell className="font-medium" colSpan={2}>Total Score</TableCell>
                    {selectedMatches.map((match, index) => (
                      <TableCell key={index}>
                        <div className="text-lg font-medium">{Math.round(match.matchScore)}%</div>
                      </TableCell>
                    ))}
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </div>
          
          {/* Recommendation */}
          {recommendedSupplier && (
            <Alert className="bg-blue-50 border-l-4 border-primary p-4 mb-8">
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
                    d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                  />
                </svg>
                <div>
                  <p className="font-medium">Recommended Supplier: {recommendedSupplier.product.name} from {recommendedSupplier.supplier.name}</p>
                  <AlertDescription className="text-sm text-gray-700 mt-1">
                    Based on the scoring criteria, {recommendedSupplier.supplier.name} offers the best overall value 
                    with a {Math.round(recommendedSupplier.matchScore)}% match score. 
                    {recommendedSupplier.matchDetails.quality > recommendedSupplier.matchDetails.price ? 
                      " Their superior build quality and specifications justify the cost." :
                      " They provide the best price-to-performance ratio among the selected suppliers."}
                    {recommendedSupplier.matchDetails.delivery > (requirements.criteria?.delivery?.weight || 20) * 0.7 &&
                      " Additionally, their delivery timeline meets or exceeds the requirements."}
                  </AlertDescription>
                </div>
              </div>
            </Alert>
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
              onClick={handleGenerateProposals}
              className="flex items-center"
            >
              Generate Proposals
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
