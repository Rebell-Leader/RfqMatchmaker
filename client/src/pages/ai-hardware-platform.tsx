import React, { useState, useEffect } from 'react';
import { useLocation } from 'wouter';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Select, 
  SelectContent, 
  SelectGroup, 
  SelectItem, 
  SelectLabel, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { 
  Table, 
  TableBody, 
  TableCaption, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import { 
  Tabs, 
  TabsContent, 
  TabsList, 
  TabsTrigger 
} from "@/components/ui/tabs";
import { toast } from "@/hooks/use-toast";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";

import { apiRequest } from '@/lib/queryClient';
import { formatCurrency } from '@/lib/supplier-service';

const AIHardwarePlatform = () => {
  const [location, setLocation] = useLocation();
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('search');
  const [aiProducts, setAIProducts] = useState<any[]>([]);
  const [selectedProducts, setSelectedProducts] = useState<any[]>([]);
  const [rfqContent, setRfqContent] = useState('');
  const [buyerCountry, setBuyerCountry] = useState('United States');
  const [complianceResult, setComplianceResult] = useState<any>(null);
  const [performanceMetric, setPerformanceMetric] = useState('fp32');
  const [performanceData, setPerformanceData] = useState<any>(null);
  const [frameworks, setFrameworks] = useState<string[]>(['TensorFlow', 'PyTorch']);

  // Initialize with sample data
  useEffect(() => {
    fetchAIHardwareProducts();
  }, []);

  // Fetch AI hardware products
  const fetchAIHardwareProducts = async () => {
    setLoading(true);
    try {
      const response = await apiRequest({
        url: '/api/products?category=GPU',
        method: 'GET',
      });

      if (response.ok) {
        const data = await response.json();
        setAIProducts(data);
      } else {
        const error = await response.text();
        toast({
          title: 'Error fetching products',
          description: error || 'Could not fetch AI hardware products',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Something went wrong while fetching products',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  // Seed sample AI hardware products
  const seedSampleProducts = async () => {
    setLoading(true);
    try {
      const response = await apiRequest({
        url: '/api/seed-ai-hardware-products',
        method: 'POST',
      });

      if (response.ok) {
        const data = await response.json();
        toast({
          title: 'Success',
          description: data.message || 'Sample products added successfully',
        });
        fetchAIHardwareProducts();
      } else {
        const error = await response.text();
        toast({
          title: 'Error seeding products',
          description: error || 'Could not seed sample products',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Something went wrong while seeding products',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  // Check compliance for a product
  const checkCompliance = async (productId: number) => {
    setLoading(true);
    try {
      const response = await apiRequest({
        url: `/api/ai-hardware/check-compliance?buyer_country=${encodeURIComponent(buyerCountry)}&product_id=${productId}`,
        method: 'GET',
      });

      if (response.ok) {
        const data = await response.json();
        setComplianceResult(data);
        // Switch to compliance tab
        setActiveTab('compliance');
      } else {
        const error = await response.text();
        toast({
          title: 'Error checking compliance',
          description: error || 'Could not check compliance',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Something went wrong while checking compliance',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  // Compare performance of selected products
  const comparePerformance = async () => {
    if (selectedProducts.length < 2) {
      toast({
        title: 'Warning',
        description: 'Please select at least 2 products to compare',
        variant: 'destructive',
      });
      return;
    }

    setLoading(true);
    try {
      const productIds = selectedProducts.map(p => p.id);
      const response = await apiRequest({
        url: `/api/ai-hardware/performance-comparison?product_ids=${productIds.join(',')}&metric=${performanceMetric}`,
        method: 'GET',
      });

      if (response.ok) {
        const data = await response.json();
        setPerformanceData(data);
        // Switch to performance tab
        setActiveTab('comparison');
      } else {
        const error = await response.text();
        toast({
          title: 'Error comparing performance',
          description: error || 'Could not compare performance',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Something went wrong while comparing performance',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  // Check framework compatibility
  const checkFrameworksCompatibility = async (productId: number) => {
    setLoading(true);
    try {
      const response = await apiRequest({
        url: `/api/ai-hardware/frameworks-compatibility?product_id=${productId}&frameworks=${frameworks.join(',')}`,
        method: 'GET',
      });

      if (response.ok) {
        const data = await response.json();
        toast({
          title: 'Framework Compatibility',
          description: `Compatibility score: ${Math.round(data.compatibilityScore * 100)}%. ${
            data.compatibilityScore >= 0.8 
              ? 'This product has excellent framework compatibility.' 
              : data.compatibilityScore >= 0.5 
                ? 'This product has good framework compatibility.' 
                : 'This product has limited framework compatibility.'
          }`,
        });
      } else {
        const error = await response.text();
        toast({
          title: 'Error checking framework compatibility',
          description: error || 'Could not check framework compatibility',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Something went wrong while checking framework compatibility',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  // Create RFQ
  const createRFQ = async () => {
    if (!rfqContent.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter RFQ content',
        variant: 'destructive',
      });
      return;
    }

    setLoading(true);
    try {
      const response = await apiRequest({
        url: '/api/rfqs',
        method: 'POST',
        body: JSON.stringify({
          title: "AI Hardware Procurement RFQ",
          description: "Request for quotation for AI computing hardware",
          specifications: rfqContent
        }),
      });

      if (response.ok) {
        const data = await response.json();
        toast({
          title: 'Success',
          description: 'RFQ created successfully',
        });
        
        // Redirect to RFQ review page
        setLocation(`/review-requirements?rfqId=${data.id}`);
      } else {
        const error = await response.text();
        toast({
          title: 'Error creating RFQ',
          description: error || 'Could not create RFQ',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Something went wrong while creating RFQ',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  // Toggle product selection for comparison
  const toggleProductSelection = (product: any) => {
    const isSelected = selectedProducts.some(p => p.id === product.id);
    if (isSelected) {
      setSelectedProducts(selectedProducts.filter(p => p.id !== product.id));
    } else {
      setSelectedProducts([...selectedProducts, product]);
    }
  };

  // Extract specification value from product - handles both simple specs and nested objects
  const getSpecValue = (product: any, specPath: string) => {
    const pathParts = specPath.split('.');
    let current: any = product;
    
    for (const part of pathParts) {
      if (!current || typeof current !== 'object') return 'N/A';
      
      // Handle JSON stored as string
      if (typeof current === 'string' && part === pathParts[0]) {
        try {
          current = JSON.parse(current);
        } catch {
          return 'N/A';
        }
      }
      
      current = current[part];
    }
    
    return current ?? 'N/A';
  };

  // Format specification value with appropriate unit
  const formatSpecValue = (value: any, unit: string = '') => {
    if (value === 'N/A' || value === null || value === undefined) return 'N/A';
    
    if (typeof value === 'boolean') {
      return value ? 'Yes' : 'No';
    }
    
    if (typeof value === 'number') {
      if (unit === 'GB') return `${value} GB`;
      if (unit === 'GB/s') return `${value} GB/s`;
      if (unit === 'W') return `${value}W`;
      if (unit === 'TFLOPS') return `${value} TFLOPS`;
      if (unit === 'TOPS') return `${value} TOPS`;
    }
    
    return value.toString();
  };

  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
          AI Hardware Procurement Platform
        </h1>
        <Button onClick={seedSampleProducts} variant="outline" disabled={loading}>
          {loading ? 'Loading...' : 'Load Sample GPUs'}
        </Button>
      </div>
      
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full mb-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="search">Search Products</TabsTrigger>
          <TabsTrigger value="rfq">Create RFQ</TabsTrigger>
          <TabsTrigger value="compliance">Compliance Check</TabsTrigger>
          <TabsTrigger value="comparison">Performance Comparison</TabsTrigger>
        </TabsList>
        
        {/* Search Products Tab */}
        <TabsContent value="search" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>AI Hardware Products</CardTitle>
              <CardDescription>
                Browse available GPU and AI accelerator products for your machine learning workloads
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-4 flex items-center space-x-2">
                <Label htmlFor="buyer-country">Buyer Country:</Label>
                <Select value={buyerCountry} onValueChange={setBuyerCountry}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Select Country" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectGroup>
                      <SelectLabel>Countries</SelectLabel>
                      <SelectItem value="United States">United States</SelectItem>
                      <SelectItem value="China">China</SelectItem>
                      <SelectItem value="Russia">Russia</SelectItem>
                      <SelectItem value="European Union">European Union</SelectItem>
                      <SelectItem value="India">India</SelectItem>
                      <SelectItem value="Japan">Japan</SelectItem>
                      <SelectItem value="South Korea">South Korea</SelectItem>
                      <SelectItem value="Taiwan">Taiwan</SelectItem>
                      <SelectItem value="Israel">Israel</SelectItem>
                    </SelectGroup>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="mb-4 flex items-center space-x-2">
                <Label>Required ML Frameworks:</Label>
                <div className="flex flex-wrap gap-2">
                  {['TensorFlow', 'PyTorch', 'CUDA', 'ROCm', 'ONNX', 'TensorRT'].map(fw => (
                    <Badge 
                      key={fw} 
                      variant={frameworks.includes(fw) ? "default" : "outline"}
                      className="cursor-pointer"
                      onClick={() => {
                        if (frameworks.includes(fw)) {
                          setFrameworks(frameworks.filter(f => f !== fw));
                        } else {
                          setFrameworks([...frameworks, fw]);
                        }
                      }}
                    >
                      {fw}
                    </Badge>
                  ))}
                </div>
              </div>
              
              <div className="overflow-x-auto">
                <Table>
                  <TableCaption>
                    {aiProducts.length 
                      ? `Available AI Hardware Products (${aiProducts.length})` 
                      : 'No products found. Click "Load Sample GPUs" to load sample data.'}
                  </TableCaption>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[50px]">Select</TableHead>
                      <TableHead>Name</TableHead>
                      <TableHead>Manufacturer</TableHead>
                      <TableHead>Memory</TableHead>
                      <TableHead>Performance</TableHead>
                      <TableHead>Price</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {aiProducts.map((product) => (
                      <TableRow key={product.id}>
                        <TableCell>
                          <input 
                            type="checkbox" 
                            checked={selectedProducts.some(p => p.id === product.id)}
                            onChange={() => toggleProductSelection(product)}
                            className="rounded-sm"
                          />
                        </TableCell>
                        <TableCell className="font-medium">
                          {product.name}
                          {product.model ? ` (${product.model})` : ''}
                        </TableCell>
                        <TableCell>{product.manufacturer || 'Unknown'}</TableCell>
                        <TableCell>
                          {formatSpecValue(
                            getSpecValue(product, 'memorySpecs.capacity') || 
                            getSpecValue(product, 'specifications.Memory Size'), 
                            'GB'
                          )}
                        </TableCell>
                        <TableCell>
                          {formatSpecValue(
                            getSpecValue(product, 'computeSpecs.fp32Performance') || 
                            getSpecValue(product, 'specifications.FP32'), 
                            'TFLOPS'
                          )}
                        </TableCell>
                        <TableCell>{formatCurrency(product.price)}</TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end gap-2">
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => checkCompliance(product.id)}
                            >
                              Check Compliance
                            </Button>
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => checkFrameworksCompatibility(product.id)}
                            >
                              Check Frameworks
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
            <CardFooter className="flex justify-between">
              <Button 
                variant="secondary"
                onClick={fetchAIHardwareProducts}
                disabled={loading}
              >
                Refresh Products
              </Button>
              <Button 
                onClick={comparePerformance}
                disabled={selectedProducts.length < 2 || loading}
              >
                Compare Selected ({selectedProducts.length})
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
        
        {/* Create RFQ Tab */}
        <TabsContent value="rfq" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Create AI Hardware RFQ</CardTitle>
              <CardDescription>
                Describe your AI hardware requirements in detail for the best supplier matches
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                <div className="space-y-2">
                  <Label htmlFor="rfq-template">RFQ Template</Label>
                  <Select defaultValue="gpu" onValueChange={(value) => {
                    if (value === 'gpu') {
                      setRfqContent(
`Request for Quotation: Enterprise GPU Cluster for AI Research

Requirements:
- 8x AI accelerator GPUs with minimum 40GB HBM memory per device
- Minimum FP32 performance: 20 TFLOPS per GPU
- Supported frameworks: TensorFlow, PyTorch, CUDA 12.0
- Power constraints: Maximum 400W TDP per GPU
- Required connectivity: PCIe 4.0, NVLink if available
- Form factor: Standard 2U server configuration
- Cooling: Liquid cooling preferred

Use Case:
Training large language models and running inference workloads for NLP research.

Award Criteria:
- Price: 30%
- Performance: 40%
- Availability: 20%
- Support/Warranty: 10%

Desired delivery timeframe: 4-6 weeks`
                      );
                    } else if (value === 'cluster') {
                      setRfqContent(
`Request for Quotation: AI Accelerator Cluster

Requirements:
- Compute system with 16 accelerator cards
- Each accelerator should have:
  * Minimum 80GB memory
  * At least 2000 GB/s memory bandwidth
  * Support for sparse matrix operations
  * FP16 performance of at least 120 TFLOPS
- Complete rack solution with power distribution
- Maximum power budget: 20kW for entire system
- Required networking: 100 Gbps InfiniBand or equivalent
- Storage: 100TB high-speed NVMe storage
- Framework compatibility: PyTorch, JAX

Use Case:
Training foundation models at scale with datasets exceeding 10TB.

Award Criteria:
- Performance: 50%
- Price: 25%
- Reliability/Support: 15%
- Energy Efficiency: 10%

Delivery timeframe: Within 3 months`
                      );
                    } else if (value === 'edge') {
                      setRfqContent(
`Request for Quotation: Edge AI Computing Devices

Requirements:
- 25x edge AI computing modules
- Each device must have:
  * Minimum 8 TOPS INT8 performance
  * Maximum 15W power consumption
  * 4GB RAM minimum
  * Hardware acceleration for computer vision
  * Small form factor (maximum 100mm x 100mm x 50mm)
- Operating temperature range: -10°C to 55°C
- Connectivity: Ethernet, Wi-Fi, optional 5G
- GPIO pins for sensor integration
- Framework support: TensorFlow Lite, ONNX Runtime

Use Case:
Deploying computer vision models for retail analytics at store locations.

Award Criteria:
- Price: 40%
- Power efficiency: 25%
- Performance: 25%
- Support/Documentation: 10%

Required delivery: Within 6 weeks`
                      );
                    }
                  }}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select RFQ Template" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="gpu">Enterprise GPU Cluster</SelectItem>
                      <SelectItem value="cluster">AI Accelerator Cluster</SelectItem>
                      <SelectItem value="edge">Edge AI Computing</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="rfq-content">RFQ Content</Label>
                  <Textarea 
                    id="rfq-content"
                    value={rfqContent}
                    onChange={(e) => setRfqContent(e.target.value)}
                    placeholder="Describe your AI hardware requirements in detail..."
                    className="min-h-[300px]"
                  />
                </div>
              </div>
            </CardContent>
            <CardFooter>
              <Button onClick={createRFQ} disabled={loading || !rfqContent.trim()}>
                Create RFQ
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
        
        {/* Compliance Check Tab */}
        <TabsContent value="compliance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Regulatory Compliance Check</CardTitle>
              <CardDescription>
                Verify compliance with export regulations and shipping restrictions
              </CardDescription>
            </CardHeader>
            <CardContent>
              {complianceResult ? (
                <div className="space-y-4">
                  <div className="p-4 rounded-lg border bg-card">
                    <h3 className="text-lg font-semibold mb-2">
                      Compliance Status:
                      <span className={
                        complianceResult.canShip 
                          ? "ml-2 text-green-500" 
                          : "ml-2 text-red-500"
                      }>
                        {complianceResult.canShip ? 'Can Ship' : 'Restricted'}
                      </span>
                    </h3>
                    
                    {complianceResult.restrictions && complianceResult.restrictions.length > 0 && (
                      <div className="mb-4">
                        <h4 className="font-medium text-red-500">Restrictions:</h4>
                        <ul className="list-disc pl-5">
                          {complianceResult.restrictions.map((restriction: string, i: number) => (
                            <li key={i}>{restriction}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {complianceResult.requiresLicense && (
                      <div className="mb-4">
                        <h4 className="font-medium text-amber-500">Export License Required</h4>
                        <p>This transaction requires an export license. Required documents:</p>
                        <ul className="list-disc pl-5">
                          {complianceResult.requiredDocuments.map((doc: string, i: number) => (
                            <li key={i}>{doc}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {complianceResult.complianceReport && (
                      <div className="mt-4">
                        <h4 className="font-medium">Detailed Compliance Report:</h4>
                        <div className="mt-2 space-y-2">
                          <div>
                            <span className="font-medium">Risk Level:</span>{' '}
                            <Badge variant={
                              complianceResult.complianceReport.overall_risk_level === 'Low' ? 'default' :
                              complianceResult.complianceReport.overall_risk_level === 'Medium' ? 'outline' :
                              'destructive'
                            }>
                              {complianceResult.complianceReport.overall_risk_level}
                            </Badge>
                          </div>
                          
                          <div>
                            <span className="font-medium">Required Actions:</span>
                            <ul className="list-disc pl-5 mt-1">
                              {complianceResult.complianceReport.required_actions.map((action: string, i: number) => (
                                <li key={i}>{action}</li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-12">
                  <p className="text-muted-foreground mb-4">
                    Select a product and click "Check Compliance" to see regulatory information
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        
        {/* Performance Comparison Tab */}
        <TabsContent value="comparison" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Performance Comparison</CardTitle>
              <CardDescription>
                Compare the performance of selected GPU and AI accelerator products
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-4 flex items-center space-x-2">
                <Label htmlFor="perf-metric">Performance Metric:</Label>
                <Select value={performanceMetric} onValueChange={setPerformanceMetric}>
                  <SelectTrigger className="w-[280px]">
                    <SelectValue placeholder="Select metric" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectGroup>
                      <SelectLabel>Compute Performance</SelectLabel>
                      <SelectItem value="fp32">FP32 Performance (TFLOPS)</SelectItem>
                      <SelectItem value="fp16">FP16 Performance (TFLOPS)</SelectItem>
                      <SelectItem value="int8">INT8 Performance (TOPS)</SelectItem>
                      <SelectLabel>Memory</SelectLabel>
                      <SelectItem value="memory_capacity">Memory Capacity (GB)</SelectItem>
                      <SelectItem value="memory_bandwidth">Memory Bandwidth (GB/s)</SelectItem>
                      <SelectLabel>Power</SelectLabel>
                      <SelectItem value="tdp">Thermal Design Power (W)</SelectItem>
                    </SelectGroup>
                  </SelectContent>
                </Select>
                
                {selectedProducts.length >= 2 && (
                  <Button 
                    onClick={comparePerformance}
                    disabled={loading}
                    size="sm"
                  >
                    Compare
                  </Button>
                )}
              </div>
              
              {performanceData ? (
                <div className="mt-6">
                  <h3 className="text-lg font-semibold mb-4">
                    {performanceData.metricLabel} Comparison
                  </h3>
                  
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Product</TableHead>
                          <TableHead>Manufacturer</TableHead>
                          <TableHead>{performanceData.metricLabel}</TableHead>
                          <TableHead>Relative Performance</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {performanceData.products.map((product: any) => (
                          <TableRow key={product.id}>
                            <TableCell className="font-medium">{product.name}</TableCell>
                            <TableCell>{product.manufacturer}</TableCell>
                            <TableCell>{product.value}</TableCell>
                            <TableCell>
                              <div className="flex items-center space-x-2">
                                <div className="w-full bg-secondary rounded-full h-2.5">
                                  <div 
                                    className="bg-primary h-2.5 rounded-full" 
                                    style={{ width: `${product.relativePerformance}%` }}
                                  ></div>
                                </div>
                                <span>{product.relativePerformance.toFixed(0)}%</span>
                              </div>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-12">
                  <p className="text-muted-foreground mb-4">
                    {selectedProducts.length < 2 
                      ? 'Select at least 2 products to compare' 
                      : 'Click "Compare" to see performance comparison'}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AIHardwarePlatform;