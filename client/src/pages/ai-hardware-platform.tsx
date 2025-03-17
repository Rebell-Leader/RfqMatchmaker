import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Slider } from "@/components/ui/slider";
import { Progress } from "@/components/ui/progress";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import { Cpu, Server, ChevronRight, Globe, Shield, Zap, Award, Check, X, Clock, ArrowUpDown, Download, Activity } from "lucide-react";
import { apiRequest } from "@/lib/queryClient";

// Types for our GPU/AI Hardware products
interface ComputeSpecs {
  tensorFlops?: number;
  fp32Performance?: number; 
  fp16Performance?: number;
  int8Performance?: number;
  tensorCores?: number;
  cudaCores?: number;
  clockSpeed?: number;
}

interface MemorySpecs {
  capacity: number;
  type: string;
  bandwidth: number;
  busWidth: number;
  eccSupport?: boolean;
}

interface PowerSpecs {
  tdp: number;
  requiredPsu?: number;
  powerConnectors?: string;
}

interface ComplianceInfo {
  exportRestrictions?: string[];
  certifications?: string[];
  restrictedCountries?: string[];
}

interface Benchmarks {
  mlTraining?: Record<string, number>;
  llmInference?: Record<string, number>;
  computerVision?: Record<string, number>;
}

interface AIHardwareProduct {
  id: number;
  supplierId: number;
  name: string;
  model: string;
  manufacturer: string;
  category: string;
  description: string;
  price: number;
  computeSpecs: ComputeSpecs;
  memorySpecs: MemorySpecs;
  powerSpecs: PowerSpecs;
  thermalSpecs?: {
    cooling: string;
    maxTemp: number;
  };
  connectivity: string[];
  supportedFrameworks: string[];
  formFactor: string;
  complianceInfo: ComplianceInfo;
  benchmarks?: Benchmarks;
  availability: string;
  warranty: string;
  releaseDate: string;
  imageUrl?: string;
  inStock: boolean;
}

interface ComplianceCheckResult {
  allowed: boolean;
  riskLevel: string;
  notes: string;
  requiredActions: string[];
}

// Dummy data for the frontend UI prototype
const frameworks = [
  "PyTorch", "TensorFlow", "JAX", "ONNX", "DirectML", "CUDA", "ROCm", "OpenVINO"
];

const manufacturers = [
  "NVIDIA", "AMD", "Intel", "Cerebras", "SambaNova", "Graphcore", "Habana Labs", "Qualcomm"
];

const countries = [
  { code: "US", name: "United States" },
  { code: "EU", name: "European Union" },
  { code: "CN", name: "China" },
  { code: "JP", name: "Japan" },
  { code: "KR", name: "South Korea" },
  { code: "IN", name: "India" },
  { code: "RU", name: "Russia" },
  { code: "SG", name: "Singapore" },
  { code: "AE", name: "United Arab Emirates" }
];

export default function AIHardwarePlatform() {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState("explore");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedManufacturers, setSelectedManufacturers] = useState<string[]>([]);
  const [selectedFrameworks, setSelectedFrameworks] = useState<string[]>([]);
  const [minPrice, setMinPrice] = useState(0);
  const [maxPrice, setMaxPrice] = useState(100000);
  const [complianceCountry, setComplianceCountry] = useState("US");
  const [productToCheck, setProductToCheck] = useState<number | null>(null);

  // Query to get AI hardware products
  const { data: products, isLoading: isLoadingProducts } = useQuery<AIHardwareProduct[], Error>({
    queryKey: ["/api/products/ai-hardware"],
    queryFn: async () => {
      try {
        // Using our dedicated AI hardware endpoint
        const response = await apiRequest("/api/products/ai-hardware", {
          method: "GET"
        } as any);
        return response as unknown as AIHardwareProduct[];
      } catch (error) {
        console.error("Failed to fetch AI hardware products:", error);
        return [] as AIHardwareProduct[];
      }
    },
    refetchOnWindowFocus: false
  });

  // Query for compliance check results
  const { data: complianceResult, isLoading: isCheckingCompliance } = useQuery<ComplianceCheckResult | null, Error>({
    queryKey: ["/api/compliance", complianceCountry, productToCheck],
    queryFn: async () => {
      if (!productToCheck) return null;
      
      try {
        const response = await apiRequest(`/api/compliance?country=${complianceCountry}&productId=${productToCheck}`, { 
          method: "GET" 
        });
        return response as ComplianceCheckResult;
      } catch (error) {
        console.error("Failed to check compliance:", error);
        return null;
      }
    },
    enabled: !!productToCheck,
    refetchOnWindowFocus: false
  });
  
  // Query for framework compatibility check
  const [selectedProduct, setSelectedProduct] = useState<number | null>(null);
  const [selectedFrameworksToCheck, setSelectedFrameworksToCheck] = useState<string[]>([]);
  
  const { data: frameworkCompatibility, isLoading: isCheckingFrameworks } = useQuery<{
    productId: number;
    productName: string;
    manufacturer: string;
    compatibility: Array<{framework: string; supported: boolean; notes: string}>
  } | null, Error>({
    queryKey: ["/api/frameworks-compatibility", selectedProduct, selectedFrameworksToCheck],
    queryFn: async () => {
      if (!selectedProduct || selectedFrameworksToCheck.length === 0) return null;
      
      try {
        const frameworksStr = selectedFrameworksToCheck.join(',');
        const response = await apiRequest(`/api/frameworks-compatibility?productId=${selectedProduct}&frameworks=${frameworksStr}`, {
          method: "GET"
        });
        return response;
      } catch (error) {
        console.error("Failed to check framework compatibility:", error);
        return null;
      }
    },
    enabled: !!selectedProduct && selectedFrameworksToCheck.length > 0,
    refetchOnWindowFocus: false
  });
  
  // Query for hardware performance comparison
  const [productsToCompare, setProductsToCompare] = useState<number[]>([]);
  const [comparisonMetric, setComparisonMetric] = useState("fp32Performance");
  
  const { data: performanceComparison, isLoading: isComparing } = useQuery<{
    metric: string;
    products: Array<{
      id: number;
      name: string;
      manufacturer: string;
      metric: string;
      value: number;
      unit: string;
      relativePerformance: number;
    }>
  } | null, Error>({
    queryKey: ["/api/hardware-comparison", productsToCompare, comparisonMetric],
    queryFn: async () => {
      if (productsToCompare.length < 2) return null;
      
      try {
        const productIdsStr = productsToCompare.join(',');
        const response = await apiRequest(`/api/hardware-comparison?productIds=${productIdsStr}&metric=${comparisonMetric}`, {
          method: "GET"
        });
        return response;
      } catch (error) {
        console.error("Failed to compare hardware performance:", error);
        return null;
      }
    },
    enabled: productsToCompare.length >= 2,
    refetchOnWindowFocus: false
  });
  
  // Function to check framework compatibility for a product
  const checkFrameworkCompatibility = (productId: number, frameworks: string[]) => {
    setSelectedProduct(productId);
    setSelectedFrameworksToCheck(frameworks);
    setActiveTab("frameworks");
  };
  
  // Function to add or remove a product from comparison
  const toggleProductComparison = (productId: number) => {
    if (productsToCompare.includes(productId)) {
      setProductsToCompare(productsToCompare.filter(id => id !== productId));
    } else {
      setProductsToCompare([...productsToCompare, productId]);
    }
    
    if (productsToCompare.length >= 1) {
      setActiveTab("compare");
    }
  };

  // Function to check compliance for a specific product
  const checkCompliance = (productId: number) => {
    setProductToCheck(productId);
    setActiveTab("compliance");
  };

  // Function to filter products based on search and filters
  const filteredProducts = products?.filter(product => {
    // Search filter
    const matchesSearch = 
      searchQuery === "" || 
      product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      product.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      product.manufacturer.toLowerCase().includes(searchQuery.toLowerCase());
    
    // Manufacturer filter
    const matchesManufacturer = 
      selectedManufacturers.length === 0 || 
      selectedManufacturers.includes(product.manufacturer);
    
    // Framework filter
    const matchesFramework = 
      selectedFrameworks.length === 0 || 
      selectedFrameworks.some(fw => product.supportedFrameworks.includes(fw));
    
    // Price filter
    const matchesPrice = 
      product.price >= minPrice && product.price <= maxPrice;
    
    return matchesSearch && matchesManufacturer && matchesFramework && matchesPrice;
  }) || [];

  // Format large numbers with commas
  const formatNumber = (num: number): string => {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  };

  // Format a performance metric with the appropriate unit
  const formatPerformance = (value: number | undefined, unit: string): string => {
    if (value === undefined) return "N/A";
    return `${formatNumber(value)} ${unit}`;
  };

  // Helper to get compliance status badge
  const getComplianceBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case "low":
        return <Badge className="bg-green-500">Low Risk</Badge>;
      case "medium":
        return <Badge className="bg-yellow-500">Medium Risk</Badge>;
      case "high":
        return <Badge className="bg-orange-500">High Risk</Badge>;
      case "critical":
        return <Badge className="bg-red-500">Critical Risk</Badge>;
      default:
        return <Badge>Unknown</Badge>;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Hero Section */}
      <section className="relative bg-slate-900 py-20 px-6 text-white overflow-hidden">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500 rounded-full opacity-20 blur-3xl"></div>
          <div className="absolute top-20 -left-20 w-80 h-80 bg-purple-500 rounded-full opacity-10 blur-3xl"></div>
          <div className="absolute bottom-0 right-1/4 w-80 h-80 bg-cyan-500 rounded-full opacity-10 blur-3xl"></div>
        </div>
        
        <div className="max-w-6xl mx-auto relative z-10">
          <div className="flex items-center mb-6">
            <Cpu className="text-blue-400 mr-2" />
            <h4 className="text-blue-400 font-medium">AI HARDWARE PROCUREMENT PLATFORM</h4>
          </div>
          
          <h1 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            Accelerate AI Innovation with the Right Hardware
          </h1>
          
          <p className="text-xl text-slate-300 max-w-3xl mb-10">
            Navigate complex specifications, compliance requirements, and global availability to find the perfect 
            AI accelerators for your machine learning workloads.
          </p>
          
          <div className="flex flex-wrap gap-4">
            <Button 
              size="lg" 
              className="bg-blue-600 hover:bg-blue-700"
              onClick={() => setActiveTab("explore")}
            >
              Explore Hardware
              <ChevronRight className="ml-2 h-4 w-4" />
            </Button>
            
            <Button 
              variant="outline" 
              size="lg" 
              className="text-slate-200 border-slate-600"
              onClick={() => setActiveTab("compliance")}
            >
              Check Compliance
              <Shield className="ml-2 h-4 w-4" />
            </Button>
            
            <Button 
              variant="outline" 
              size="lg" 
              className="text-slate-200 border-slate-600"
              onClick={() => setActiveTab("compare")}
            >
              Compare Performance
              <ArrowUpDown className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
      </section>
      
      {/* Main Content */}
      <section className="py-12 px-6">
        <div className="max-w-7xl mx-auto">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-8">
            <TabsList className="grid w-full md:w-auto md:inline-grid grid-cols-4 md:grid-cols-4 gap-4">
              <TabsTrigger value="explore" className="flex items-center">
                <Server className="mr-2 h-4 w-4" />
                <span className="hidden md:inline">Explore Hardware</span>
                <span className="md:hidden">Explore</span>
              </TabsTrigger>
              <TabsTrigger value="compliance" className="flex items-center">
                <Shield className="mr-2 h-4 w-4" />
                <span className="hidden md:inline">Check Compliance</span>
                <span className="md:hidden">Compliance</span>
              </TabsTrigger>
              <TabsTrigger value="frameworks" className="flex items-center">
                <Code2 className="mr-2 h-4 w-4" />
                <span className="hidden md:inline">Framework Support</span>
                <span className="md:hidden">Frameworks</span>
              </TabsTrigger>
              <TabsTrigger value="compare" className="flex items-center">
                <ArrowUpDown className="mr-2 h-4 w-4" />
                <span className="hidden md:inline">Compare Performance</span>
                <span className="md:hidden">Compare</span>
              </TabsTrigger>
            </TabsList>
            
            {/* Explore Hardware Tab */}
            <TabsContent value="explore" className="space-y-8">
              {/* Search and Filters */}
              <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
                <h2 className="text-2xl font-bold mb-4">Find AI Hardware</h2>
                
                <div className="grid md:grid-cols-4 gap-6">
                  <div className="md:col-span-4">
                    <Input
                      placeholder="Search GPUs, accelerators, and AI hardware..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-full"
                    />
                  </div>
                  
                  <div>
                    <h3 className="text-sm font-medium mb-2">Manufacturer</h3>
                    <div className="space-y-2">
                      {manufacturers.map((manufacturer) => (
                        <div key={manufacturer} className="flex items-center">
                          <Checkbox 
                            id={`manufacturer-${manufacturer}`}
                            checked={selectedManufacturers.includes(manufacturer)}
                            onCheckedChange={(checked) => {
                              if (checked) {
                                setSelectedManufacturers([...selectedManufacturers, manufacturer]);
                              } else {
                                setSelectedManufacturers(selectedManufacturers.filter(m => m !== manufacturer));
                              }
                            }}
                          />
                          <Label htmlFor={`manufacturer-${manufacturer}`} className="ml-2 text-sm">
                            {manufacturer}
                          </Label>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="text-sm font-medium mb-2">Framework Support</h3>
                    <div className="space-y-2">
                      {frameworks.slice(0, 6).map((framework) => (
                        <div key={framework} className="flex items-center">
                          <Checkbox 
                            id={`framework-${framework}`}
                            checked={selectedFrameworks.includes(framework)}
                            onCheckedChange={(checked) => {
                              if (checked) {
                                setSelectedFrameworks([...selectedFrameworks, framework]);
                              } else {
                                setSelectedFrameworks(selectedFrameworks.filter(f => f !== framework));
                              }
                            }}
                          />
                          <Label htmlFor={`framework-${framework}`} className="ml-2 text-sm">
                            {framework}
                          </Label>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="text-sm font-medium mb-2">Price Range</h3>
                    <div className="space-y-4">
                      <div className="flex justify-between">
                        <span>${formatNumber(minPrice)}</span>
                        <span>${formatNumber(maxPrice)}</span>
                      </div>
                      <Slider
                        defaultValue={[minPrice, maxPrice]}
                        min={0}
                        max={100000}
                        step={1000}
                        onValueChange={(values) => {
                          setMinPrice(values[0]);
                          setMaxPrice(values[1]);
                        }}
                      />
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="text-sm font-medium mb-2">Compliance</h3>
                    <Select value={complianceCountry} onValueChange={setComplianceCountry}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select your country" />
                      </SelectTrigger>
                      <SelectContent>
                        {countries.map((country) => (
                          <SelectItem key={country.code} value={country.code}>
                            {country.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <p className="text-xs text-slate-500 mt-2">
                      We'll show compliance information for selected products based on this country.
                    </p>
                  </div>
                </div>
              </div>
              
              {/* Results */}
              <div className="space-y-6">
                <div className="flex justify-between items-center">
                  <h2 className="text-xl font-semibold">
                    {isLoadingProducts ? "Loading products..." : `${filteredProducts.length} products found`}
                  </h2>
                  <Select defaultValue="relevance">
                    <SelectTrigger className="w-[180px]">
                      <SelectValue placeholder="Sort by" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="relevance">Relevance</SelectItem>
                      <SelectItem value="price-low">Price: Low to High</SelectItem>
                      <SelectItem value="price-high">Price: High to Low</SelectItem>
                      <SelectItem value="performance">Performance</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                {isLoadingProducts ? (
                  <div className="text-center py-12">
                    <Cpu className="animate-spin h-8 w-8 mx-auto mb-4 text-primary" />
                    <p>Loading AI hardware products...</p>
                  </div>
                ) : filteredProducts.length === 0 ? (
                  <div className="text-center py-12">
                    <p>No products match your filters. Try adjusting your search criteria.</p>
                  </div>
                ) : (
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {/* For the demo, we'll show 6 sample cards */}
                    {Array.from({ length: Math.min(6, filteredProducts.length) }).map((_, index) => {
                      const product = filteredProducts[index] || {
                        id: index,
                        name: "NVIDIA A100 GPU",
                        manufacturer: "NVIDIA",
                        price: 10000,
                        description: "High-performance GPU for AI workloads",
                        computeSpecs: { tensorFlops: 312 },
                        memorySpecs: { capacity: 80, type: "HBM2e", bandwidth: 2039, busWidth: 5120 },
                        powerSpecs: { tdp: 400 },
                        supportedFrameworks: ["PyTorch", "TensorFlow", "CUDA"],
                        complianceInfo: {
                          exportRestrictions: ["RU", "CN"]
                        },
                        inStock: Math.random() > 0.3
                      };
                      
                      return (
                        <Card key={index} className="overflow-hidden">
                          <CardHeader className="pb-3">
                            <div className="flex justify-between items-start">
                              <CardTitle>{product.name}</CardTitle>
                              {product.inStock ? (
                                <Badge className="bg-green-500">In Stock</Badge>
                              ) : (
                                <Badge variant="outline">On Order</Badge>
                              )}
                            </div>
                            <CardDescription>{product.manufacturer}</CardDescription>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-4">
                              <div>
                                <h4 className="text-sm font-medium mb-1">Performance</h4>
                                <div className="flex justify-between text-sm mb-1">
                                  <span>Tensor Performance</span>
                                  <span className="font-medium">{formatPerformance(product.computeSpecs?.tensorFlops, "TFLOPs")}</span>
                                </div>
                                <Progress value={85} className="h-2" />
                              </div>
                              
                              <div>
                                <h4 className="text-sm font-medium mb-1">Memory</h4>
                                <div className="flex justify-between text-sm">
                                  <span>{product.memorySpecs?.capacity}GB {product.memorySpecs?.type}</span>
                                  <span>{product.memorySpecs?.bandwidth} GB/s</span>
                                </div>
                              </div>
                              
                              <div>
                                <h4 className="text-sm font-medium mb-1">Framework Support</h4>
                                <div className="flex flex-wrap gap-1">
                                  {product.supportedFrameworks.slice(0, 3).map((framework) => (
                                    <Badge key={framework} variant="secondary" className="text-xs">{framework}</Badge>
                                  ))}
                                  {product.supportedFrameworks.length > 3 && (
                                    <Badge variant="secondary" className="text-xs">+{product.supportedFrameworks.length - 3} more</Badge>
                                  )}
                                </div>
                              </div>
                              
                              <div>
                                <h4 className="text-sm font-medium mb-1">Compliance Status</h4>
                                {product.complianceInfo?.exportRestrictions?.includes(complianceCountry) ? (
                                  <Badge variant="destructive" className="text-xs">
                                    Export Restricted
                                  </Badge>
                                ) : (
                                  <Badge className="bg-green-500 text-xs">
                                    Available in {countries.find(c => c.code === complianceCountry)?.name}
                                  </Badge>
                                )}
                              </div>
                            </div>
                          </CardContent>
                          <Separator />
                          <CardFooter className="flex justify-between pt-4">
                            <div>
                              <p className="text-2xl font-bold">${formatNumber(product.price)}</p>
                              <p className="text-xs text-slate-500">Enterprise pricing</p>
                            </div>
                            <div className="space-x-2">
                              <Button 
                                variant="outline" 
                                size="sm"
                                onClick={() => checkCompliance(product.id)}
                              >
                                Check Compliance
                              </Button>
                              <Button size="sm">Details</Button>
                            </div>
                          </CardFooter>
                        </Card>
                      );
                    })}
                  </div>
                )}
              </div>
            </TabsContent>
            
            {/* Compliance Check Tab */}
            <TabsContent value="compliance" className="space-y-8">
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-2xl font-bold mb-6">Export Compliance Check</h2>
                
                <div className="grid md:grid-cols-2 gap-8">
                  <div>
                    <h3 className="text-lg font-medium mb-4">Check Hardware Compliance</h3>
                    <p className="text-slate-600 mb-6">
                      Verify if AI hardware can be exported to your country and identify any regulatory issues or restrictions.
                    </p>
                    
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="country-select">Your Country</Label>
                        <Select value={complianceCountry} onValueChange={setComplianceCountry}>
                          <SelectTrigger id="country-select">
                            <SelectValue placeholder="Select your country" />
                          </SelectTrigger>
                          <SelectContent>
                            {countries.map((country) => (
                              <SelectItem key={country.code} value={country.code}>
                                {country.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div>
                        <Label htmlFor="product-select">Select Hardware</Label>
                        <Select
                          value={productToCheck?.toString() || ""}
                          onValueChange={(value) => setProductToCheck(parseInt(value))}
                        >
                          <SelectTrigger id="product-select">
                            <SelectValue placeholder="Select a product" />
                          </SelectTrigger>
                          <SelectContent>
                            {filteredProducts.map((product) => (
                              <SelectItem key={product.id} value={product.id.toString()}>
                                {product.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <Button 
                        onClick={() => {
                          if (!productToCheck) {
                            toast({
                              title: "Please select a product",
                              description: "You need to select a product to check compliance",
                              variant: "destructive"
                            });
                            return;
                          }
                          
                          // The query will automatically run when productToCheck changes
                          toast({
                            title: "Checking compliance",
                            description: "Please wait while we check compliance for this product"
                          });
                        }}
                        disabled={!productToCheck || isCheckingCompliance}
                      >
                        {isCheckingCompliance ? "Checking..." : "Check Compliance"}
                      </Button>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-medium mb-4">Compliance Results</h3>
                    
                    {!productToCheck ? (
                      <div className="bg-slate-50 rounded-lg p-6 text-center h-full flex flex-col items-center justify-center">
                        <Shield className="h-12 w-12 text-slate-400 mb-4" />
                        <p className="text-slate-600">Select a product and country to check compliance</p>
                      </div>
                    ) : isCheckingCompliance ? (
                      <div className="bg-slate-50 rounded-lg p-6 text-center h-full flex flex-col items-center justify-center">
                        <Shield className="h-12 w-12 text-slate-400 mb-4 animate-pulse" />
                        <p className="text-slate-600">Checking compliance status...</p>
                      </div>
                    ) : complianceResult ? (
                      <div className="bg-slate-50 rounded-lg p-6">
                        <div className="flex justify-between items-center mb-4">
                          <h4 className="font-medium">
                            {filteredProducts.find(p => p.id === productToCheck)?.name || "Selected Product"}
                          </h4>
                          {getComplianceBadge(complianceResult.riskLevel)}
                        </div>
                        
                        <div className="space-y-4">
                          <div>
                            <h5 className="text-sm font-medium">Export Status</h5>
                            <div className="flex items-center mt-1">
                              {complianceResult.allowed ? (
                                <>
                                  <Check className="h-4 w-4 text-green-500 mr-2" />
                                  <span className="text-green-700">
                                    Can be exported to {countries.find(c => c.code === complianceCountry)?.name}
                                  </span>
                                </>
                              ) : (
                                <>
                                  <X className="h-4 w-4 text-red-500 mr-2" />
                                  <span className="text-red-700">
                                    Export restricted to {countries.find(c => c.code === complianceCountry)?.name}
                                  </span>
                                </>
                              )}
                            </div>
                          </div>
                          
                          <div>
                            <h5 className="text-sm font-medium">Compliance Notes</h5>
                            <p className="text-sm mt-1">{complianceResult.notes}</p>
                          </div>
                          
                          {complianceResult.requiredActions.length > 0 && (
                            <div>
                              <h5 className="text-sm font-medium">Required Actions</h5>
                              <ul className="list-disc list-inside text-sm mt-1">
                                {complianceResult.requiredActions.map((action, i) => (
                                  <li key={i}>{action}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          
                          <div className="pt-2">
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => {
                                toast({
                                  title: "Report downloaded",
                                  description: "Compliance report has been downloaded"
                                });
                              }}
                              className="w-full"
                            >
                              <Download className="h-4 w-4 mr-2" />
                              Download Compliance Report
                            </Button>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="bg-slate-50 rounded-lg p-6 text-center h-full flex flex-col items-center justify-center">
                        <Shield className="h-12 w-12 text-orange-400 mb-4" />
                        <p className="text-slate-600">No compliance data available</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-lg font-bold mb-4">Export Control Information</h2>
                
                <div className="grid md:grid-cols-3 gap-6">
                  <div className="space-y-2">
                    <h3 className="text-md font-medium">U.S. Export Controls</h3>
                    <p className="text-sm text-slate-600">
                      High-performance AI hardware may be subject to U.S. Export Administration Regulations (EAR).
                      Products exceeding certain performance thresholds require export licenses.
                    </p>
                  </div>
                  
                  <div className="space-y-2">
                    <h3 className="text-md font-medium">Restricted Entities</h3>
                    <p className="text-sm text-slate-600">
                      Sales to entities on the U.S. Commerce Department's Entity List are restricted.
                      Our platform automatically checks compliance with these restrictions.
                    </p>
                  </div>
                  
                  <div className="space-y-2">
                    <h3 className="text-md font-medium">Technical Compliance</h3>
                    <p className="text-sm text-slate-600">
                      Hardware with specific technical characteristics may have additional export controls.
                      This includes systems with high FLOPS ratings or specialized AI capabilities.
                    </p>
                  </div>
                </div>
              </div>
            </TabsContent>
            
            {/* Compare Performance Tab */}
            <TabsContent value="compare" className="space-y-8">
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-2xl font-bold mb-6">Performance Comparison</h2>
                
                <div className="grid md:grid-cols-2 gap-8 items-start">
                  <div>
                    <h3 className="text-lg font-medium mb-4">Select Hardware to Compare</h3>
                    
                    <div className="space-y-4">
                      <div>
                        <Label>Performance Metric</Label>
                        <Select defaultValue="fp32">
                          <SelectTrigger>
                            <SelectValue placeholder="Select metric" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="fp32">FP32 Performance (TFLOPS)</SelectItem>
                            <SelectItem value="fp16">FP16 Performance (TFLOPS)</SelectItem>
                            <SelectItem value="int8">INT8 Performance (TOPS)</SelectItem>
                            <SelectItem value="memory">Memory Bandwidth (GB/s)</SelectItem>
                            <SelectItem value="training">ML Training (Images/sec)</SelectItem>
                            <SelectItem value="inference">LLM Inference (Tokens/sec)</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div className="space-y-2">
                        <Label>Select Products</Label>
                        
                        <div className="space-y-2">
                          {filteredProducts.slice(0, 5).map((product) => (
                            <div key={product.id} className="flex items-center">
                              <Checkbox id={`compare-${product.id}`} />
                              <Label htmlFor={`compare-${product.id}`} className="ml-2 text-sm">
                                {product.name}
                              </Label>
                            </div>
                          ))}
                        </div>
                      </div>
                      
                      <Button>Compare Selected Hardware</Button>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-medium mb-4">Comparison Results</h3>
                    
                    {/* Sample chart for demo */}
                    <div className="bg-slate-50 rounded-lg p-6">
                      <h4 className="text-sm font-medium mb-4 text-center">FP32 Performance (TFLOPS)</h4>
                      
                      <div className="space-y-4">
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span>NVIDIA H100</span>
                            <span>989 TFLOPS</span>
                          </div>
                          <div className="w-full bg-slate-200 rounded-full h-4">
                            <div className="bg-blue-600 h-4 rounded-full" style={{ width: '100%' }}></div>
                          </div>
                        </div>
                        
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span>NVIDIA A100</span>
                            <span>312 TFLOPS</span>
                          </div>
                          <div className="w-full bg-slate-200 rounded-full h-4">
                            <div className="bg-blue-600 h-4 rounded-full" style={{ width: '32%' }}></div>
                          </div>
                        </div>
                        
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span>AMD MI250X</span>
                            <span>383 TFLOPS</span>
                          </div>
                          <div className="w-full bg-slate-200 rounded-full h-4">
                            <div className="bg-blue-600 h-4 rounded-full" style={{ width: '39%' }}></div>
                          </div>
                        </div>
                        
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span>Intel Gaudi2</span>
                            <span>197 TFLOPS</span>
                          </div>
                          <div className="w-full bg-slate-200 rounded-full h-4">
                            <div className="bg-blue-600 h-4 rounded-full" style={{ width: '20%' }}></div>
                          </div>
                        </div>
                      </div>
                      
                      <div className="mt-6">
                        <h4 className="text-sm font-medium mb-2">Performance Analysis</h4>
                        <p className="text-sm text-slate-600">
                          The NVIDIA H100 significantly outperforms other options in raw FP32 compute power.
                          For cost-sensitive applications, the AMD MI250X offers better performance per dollar
                          despite lower absolute performance.
                        </p>
                      </div>
                      
                      <div className="mt-4 text-right">
                        <Button variant="outline" size="sm">
                          <Download className="h-4 w-4 mr-2" />
                          Export Comparison
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-lg font-bold mb-4">Recommended Workloads</h2>
                
                <div className="grid md:grid-cols-3 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Deep Learning Training</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Top pick:</span>
                          <span className="font-medium">NVIDIA H100</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Value pick:</span>
                          <span className="font-medium">AMD MI250X</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Key metric:</span>
                          <span className="font-medium">FP16/BF16 TFLOPS</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Inference & Deployment</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Top pick:</span>
                          <span className="font-medium">NVIDIA A100</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Value pick:</span>
                          <span className="font-medium">Intel Gaudi2</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Key metric:</span>
                          <span className="font-medium">INT8 TOPS, Mem BW</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">LLM Serving</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Top pick:</span>
                          <span className="font-medium">NVIDIA H100</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Value pick:</span>
                          <span className="font-medium">NVIDIA A100</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Key metric:</span>
                          <span className="font-medium">Memory Size, BW</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </section>
      
      {/* Footer */}
      <footer className="bg-slate-900 text-white py-12 px-6 mt-12">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Cpu className="mr-2 h-5 w-5 text-blue-400" />
                <span className="text-blue-400">AI Hardware Platform</span>
              </h3>
              <p className="text-slate-400 text-sm">
                Specialized procurement platform for AI accelerators with compliance checking, 
                performance benchmarking, and global sourcing capabilities.
              </p>
            </div>
            
            <div>
              <h4 className="font-medium mb-3">Key Features</h4>
              <ul className="space-y-2 text-sm text-slate-400">
                <li className="flex items-center">
                  <Globe className="h-4 w-4 mr-2 text-slate-500" />
                  Global Availability Tracking
                </li>
                <li className="flex items-center">
                  <Shield className="h-4 w-4 mr-2 text-slate-500" />
                  Export Compliance Checks
                </li>
                <li className="flex items-center">
                  <Zap className="h-4 w-4 mr-2 text-slate-500" />
                  Performance Benchmarking
                </li>
                <li className="flex items-center">
                  <Award className="h-4 w-4 mr-2 text-slate-500" />
                  Certified Supplier Network
                </li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium mb-3">Resources</h4>
              <ul className="space-y-2 text-sm text-slate-400">
                <li>Hardware Comparison Guide</li>
                <li>Export Compliance FAQ</li>
                <li>AI Workload Optimization</li>
                <li>Technical Specifications</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium mb-3">Contact</h4>
              <div className="space-y-2 text-sm text-slate-400">
                <p>Need help finding the right hardware?</p>
                <Button variant="outline" className="w-full text-white border-slate-700 hover:border-blue-500">
                  Contact Sales Team
                </Button>
              </div>
            </div>
          </div>
          
          <div className="mt-8 pt-8 border-t border-slate-800 text-center text-sm text-slate-500">
            <p>© {new Date().getFullYear()} AI Hardware Procurement Platform. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}