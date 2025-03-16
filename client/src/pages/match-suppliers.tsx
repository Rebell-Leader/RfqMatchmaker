import { useEffect, useState } from "react";
import { useParams, useLocation } from "wouter";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import { Label } from "@/components/ui/label";
import { getRFQById, matchSuppliersForRFQ, formatCurrency, calculateTotalPrice } from "@/lib/supplier-service";
import { useRfq } from "@/context/rfq-context";
import { useDemoMode } from "@/context/demo-context";
import { formatSpecifications, formatWarningText, sortSupplierMatches, filterSupplierMatches, getUniqueFilterOptions } from "@/utils/rfq-processor";
import { Skeleton } from "@/components/ui/skeleton";

export default function MatchSuppliers() {
  const { id } = useParams<{ id: string }>();
  const [, navigate] = useLocation();
  const { toast } = useToast();
  const { setRfqId, setSupplierMatches, setSelectedMatches } = useRfq();
  const { isDemoMode, demoRfq, demoSupplierMatches, simulateProcessing } = useDemoMode();
  
  const [loading, setLoading] = useState(true);
  const [matchLoading, setMatchLoading] = useState(false);
  const [rfq, setRfq] = useState<any>(null);
  const [requirements, setRequirements] = useState<any>(null);
  const [matches, setMatches] = useState<any[]>([]);
  const [selectedTab, setSelectedTab] = useState("laptops");
  const [sortBy, setSortBy] = useState("match-score");
  const [filterProcessor, setFilterProcessor] = useState("all");
  const [filterMemory, setFilterMemory] = useState("all");
  const [filterOptions, setFilterOptions] = useState<any>({ processors: [], memories: [] });
  const [page, setPage] = useState(1);
  const [selectedItems, setSelectedItems] = useState<any[]>([]);
  
  const itemsPerPage = 5;
  
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
            
            // Find initial tab based on categories
            const categories = demoRfq.extractedRequirements.categories || [];
            if (categories.includes("Laptops")) {
              setSelectedTab("laptops");
            } else if (categories.includes("Monitors")) {
              setSelectedTab("monitors");
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
        
        // Find initial tab based on categories
        const categories = rfqData.extractedRequirements.categories || [];
        if (categories.includes("Laptops")) {
          setSelectedTab("laptops");
        } else if (categories.includes("Monitors")) {
          setSelectedTab("monitors");
        }
        
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
  }, [id, setRfqId, toast, isDemoMode, demoRfq]);
  
  useEffect(() => {
    async function matchSuppliers() {
      try {
        setMatchLoading(true);
        
        // If in demo mode, use demo matches
        if (isDemoMode && String(demoRfq.id) === id) {
          // Simulate processing delay
          simulateProcessing(() => {
            setMatches(demoSupplierMatches);
            
            // Get filter options from matches
            const options = getUniqueFilterOptions(demoSupplierMatches);
            setFilterOptions(options);
            
            // Update context
            setSupplierMatches(demoSupplierMatches);
            setMatchLoading(false);
          });
          return;
        }
        
        // Otherwise fetch real data
        const matchResults = await matchSuppliersForRFQ(Number(id));
        setMatches(matchResults);
        
        // Get filter options from matches
        const options = getUniqueFilterOptions(matchResults);
        setFilterOptions(options);
        
        // Update context
        setSupplierMatches(matchResults);
      } catch (error) {
        console.error("Error matching suppliers:", error);
        toast({
          title: "Error",
          description: "Failed to match suppliers. Please try again.",
          variant: "destructive",
        });
      } finally {
        if (!isDemoMode) {
          setMatchLoading(false);
        }
      }
    }
    
    if (rfq && !matches.length) {
      matchSuppliers();
    }
  }, [id, rfq, matches.length, setSupplierMatches, toast, isDemoMode, demoRfq, demoSupplierMatches, simulateProcessing]);
  
  const handleGoBack = () => {
    navigate(`/review/${id}`);
  };
  
  const handleCompareSelected = () => {
    // Update selected matches in context
    setSelectedMatches(selectedItems);
    navigate(`/score/${id}`);
  };
  
  const toggleItemSelection = (item: any) => {
    if (selectedItems.some(i => i.product.id === item.product.id)) {
      setSelectedItems(selectedItems.filter(i => i.product.id !== item.product.id));
    } else {
      setSelectedItems([...selectedItems, item]);
    }
  };
  
  // Filter matches by category and sort/filter
  const getFilteredMatches = () => {
    const categoryMatches = matches.filter(match => 
      match.product.category === (selectedTab === "laptops" ? "Laptops" : "Monitors")
    );
    
    // Apply sort
    const sortedMatches = sortSupplierMatches(categoryMatches, sortBy);
    
    // Apply filters
    return filterSupplierMatches(sortedMatches, {
      processor: filterProcessor,
      memory: filterMemory
    });
  };
  
  const filteredMatches = getFilteredMatches();
  const totalPages = Math.ceil(filteredMatches.length / itemsPerPage);
  const paginatedMatches = filteredMatches.slice((page - 1) * itemsPerPage, page * itemsPerPage);
  
  // Render loading skeleton
  if (loading) {
    return (
      <div className="max-w-5xl mx-auto">
        <Card>
          <CardContent className="pt-6">
            <Skeleton className="h-8 w-1/3 mb-2" />
            <Skeleton className="h-4 w-2/3 mb-6" />
            
            <div className="hidden" id="matching-loader">
              <div className="flex flex-col items-center justify-center py-12">
                <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
                <Skeleton className="h-6 w-1/3 mb-2" />
                <Skeleton className="h-4 w-1/2" />
              </div>
            </div>
            
            <div>
              <div className="border-b border-gray-200 mb-6">
                <Skeleton className="h-10 w-64 mb-2" />
              </div>
              
              <div className="flex flex-wrap items-center gap-4 mb-4">
                <div className="w-1/4">
                  <Skeleton className="h-4 w-1/2 mb-1" />
                  <Skeleton className="h-10 w-full" />
                </div>
                <div className="w-1/4">
                  <Skeleton className="h-4 w-1/2 mb-1" />
                  <Skeleton className="h-10 w-full" />
                </div>
                <div className="w-1/4">
                  <Skeleton className="h-4 w-1/2 mb-1" />
                  <Skeleton className="h-10 w-full" />
                </div>
              </div>
              
              {[1, 2].map(i => (
                <Skeleton key={i} className="h-64 w-full mb-4" />
              ))}
              
              <div className="flex justify-center mt-6">
                <Skeleton className="h-10 w-64" />
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
  
  return (
    <div className="max-w-5xl mx-auto">
      <Card>
        <CardContent className="pt-6">
          <h2 className="text-2xl font-medium mb-2">Supplier Matching</h2>
          <p className="text-gray-600 mb-6">
            We've found suppliers that match your RFQ requirements. Review the matches below.
          </p>
          
          {/* Processing Animation */}
          {matchLoading && (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
              <p className="text-lg font-medium">Finding matching suppliers...</p>
              <p className="text-gray-500 mt-2">This may take a moment as we analyze supplier databases.</p>
            </div>
          )}
          
          {/* Results */}
          {!matchLoading && (
            <div>
              {/* Tabs */}
              <Tabs value={selectedTab} onValueChange={setSelectedTab} className="w-full">
                <div className="border-b border-gray-200 mb-6">
                  <TabsList className="bg-transparent border-b-0">
                    {requirements.categories?.includes("Laptops") && (
                      <TabsTrigger 
                        value="laptops" 
                        className="data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:text-primary rounded-none"
                      >
                        Laptops ({matches.filter(m => m.product.category === "Laptops").length} matches)
                      </TabsTrigger>
                    )}
                    {requirements.categories?.includes("Monitors") && (
                      <TabsTrigger 
                        value="monitors" 
                        className="data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:text-primary rounded-none"
                      >
                        Monitors ({matches.filter(m => m.product.category === "Monitors").length} matches)
                      </TabsTrigger>
                    )}
                  </TabsList>
                </div>
                
                <TabsContent value="laptops">
                  {/* Filters */}
                  <div className="flex flex-wrap items-center gap-4 mb-4">
                    <div>
                      <Label htmlFor="sort-by" className="block text-sm font-medium text-gray-700 mb-1">
                        Sort by
                      </Label>
                      <Select value={sortBy} onValueChange={setSortBy}>
                        <SelectTrigger className="w-[180px]" id="sort-by">
                          <SelectValue placeholder="Sort by..." />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="price-asc">Price (lowest first)</SelectItem>
                          <SelectItem value="price-desc">Price (highest first)</SelectItem>
                          <SelectItem value="match-score">Match score</SelectItem>
                          <SelectItem value="delivery-time">Delivery time</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div>
                      <Label htmlFor="filter-processor" className="block text-sm font-medium text-gray-700 mb-1">
                        Processor
                      </Label>
                      <Select value={filterProcessor} onValueChange={setFilterProcessor}>
                        <SelectTrigger className="w-[180px]" id="filter-processor">
                          <SelectValue placeholder="All Processors" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All Processors</SelectItem>
                          {filterOptions.processors.map((processor: string) => (
                            <SelectItem key={processor} value={processor.toLowerCase()}>
                              {processor}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div>
                      <Label htmlFor="filter-memory" className="block text-sm font-medium text-gray-700 mb-1">
                        Memory
                      </Label>
                      <Select value={filterMemory} onValueChange={setFilterMemory}>
                        <SelectTrigger className="w-[180px]" id="filter-memory">
                          <SelectValue placeholder="All Memory" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All Memory</SelectItem>
                          {filterOptions.memories.map((memory: string) => (
                            <SelectItem key={memory} value={memory.toLowerCase()}>
                              {memory}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  
                  {/* Results */}
                  {paginatedMatches.length === 0 ? (
                    <div className="text-center py-8">
                      <p className="text-gray-500">No matching suppliers found.</p>
                    </div>
                  ) : (
                    paginatedMatches.map((match, index) => (
                      <div key={`${match.supplier.id}-${match.product.id}`} className="border border-gray-200 rounded-lg mb-4 overflow-hidden">
                        <div className="flex flex-col md:flex-row">
                          {/* Supplier Info */}
                          <div className="p-4 md:w-1/4 bg-gray-50 border-b md:border-b-0 md:border-r border-gray-200">
                            <div className="flex items-center mb-3">
                              <img 
                                src={match.supplier.logoUrl} 
                                alt={match.supplier.name} 
                                className="w-8 h-8 mr-2 rounded" 
                              />
                              <h3 className="font-medium">{match.supplier.name}</h3>
                            </div>
                            <div className="flex items-center text-sm text-gray-600 mb-2">
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
                                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                                />
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                                />
                              </svg>
                              {match.supplier.country}
                            </div>
                            <div className="flex items-center text-sm text-gray-600 mb-2">
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
                                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                                />
                              </svg>
                              Est. delivery: {match.supplier.deliveryTime}
                            </div>
                            <div className="flex items-center text-sm text-gray-600">
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
                                  d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                                />
                              </svg>
                              {match.supplier.isVerified ? "Verified supplier" : "Standard supplier"}
                            </div>
                          </div>
                          
                          {/* Product Info */}
                          <div className="p-4 md:w-2/4">
                            <h4 className="font-medium mb-2">{match.product.name}</h4>
                            <div className="space-y-1 text-sm mb-3">
                              {formatSpecifications(match.product.specifications).map((spec, i) => (
                                <p key={i}>
                                  <span className="text-gray-500">{spec.key}:</span> {spec.value}
                                  {spec.warning && (
                                    <span className={formatWarningText(spec.warning).color}> {formatWarningText(spec.warning).text}</span>
                                  )}
                                </p>
                              ))}
                            </div>
                            <div className="mt-3">
                              <Button variant="link" size="sm" className="text-primary hover:text-primary-dark p-0 h-auto text-sm">
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
                                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                                  />
                                </svg>
                                View full specifications
                              </Button>
                            </div>
                          </div>
                          
                          {/* Scoring Info */}
                          <div className="p-4 md:w-1/4 bg-gray-50 border-t md:border-t-0 md:border-l border-gray-200">
                            <div className="mb-3">
                              <p className="text-2xl font-medium">
                                {formatCurrency(match.product.price)}
                                <span className="text-sm text-gray-500">/unit</span>
                              </p>
                              <p className="text-sm text-gray-600">
                                {formatCurrency(match.totalPrice)} total 
                                ({requirements.laptops?.quantity || 0} units)
                              </p>
                            </div>
                            
                            <div className="mb-4">
                              <div className="flex justify-between items-center mb-1">
                                <span className="text-sm text-gray-600">Match score</span>
                                <span className="text-sm font-medium">{Math.round(match.matchScore)}%</span>
                              </div>
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div 
                                  className="bg-primary h-2 rounded-full" 
                                  style={{ width: `${Math.round(match.matchScore)}%` }}
                                ></div>
                              </div>
                            </div>
                            
                            <div>
                              <Button 
                                onClick={() => toggleItemSelection(match)}
                                variant={selectedItems.some(i => i.product.id === match.product.id) ? "secondary" : "default"}
                                className="w-full mb-2"
                              >
                                {selectedItems.some(i => i.product.id === match.product.id) ? "Selected" : "Select"}
                              </Button>
                              <Button variant="outline" className="w-full">
                                Compare
                              </Button>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                  
                  {/* Pagination */}
                  {totalPages > 1 && (
                    <div className="flex justify-center mt-6">
                      <Pagination>
                        <PaginationContent>
                          <PaginationItem>
                            <PaginationPrevious 
                              onClick={() => setPage(p => Math.max(1, p - 1))}
                              className={page === 1 ? "pointer-events-none opacity-50" : ""}
                            />
                          </PaginationItem>
                          
                          {Array.from({ length: totalPages }, (_, i) => i + 1).map(p => (
                            <PaginationItem key={p}>
                              <PaginationLink 
                                onClick={() => setPage(p)}
                                isActive={page === p}
                              >
                                {p}
                              </PaginationLink>
                            </PaginationItem>
                          ))}
                          
                          <PaginationItem>
                            <PaginationNext 
                              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                              className={page === totalPages ? "pointer-events-none opacity-50" : ""}
                            />
                          </PaginationItem>
                        </PaginationContent>
                      </Pagination>
                    </div>
                  )}
                </TabsContent>
                
                <TabsContent value="monitors">
                  {/* Similar implementation for monitors tab */}
                  <div className="text-center py-8">
                    <p className="text-gray-500">Monitor matching functionality works the same way as laptops.</p>
                  </div>
                </TabsContent>
              </Tabs>
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
              onClick={handleCompareSelected}
              disabled={selectedItems.length === 0}
              className="flex items-center"
            >
              Compare Selected
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
