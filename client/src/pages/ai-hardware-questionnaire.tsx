import { useState } from "react";
import { useLocation } from "wouter";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { 
  Form, 
  FormControl, 
  FormDescription, 
  FormField, 
  FormItem, 
  FormLabel, 
  FormMessage 
} from "@/components/ui/form";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Checkbox } from "@/components/ui/checkbox";
import { Slider } from "@/components/ui/slider";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { createManualRFQ } from "@/lib/ai-service";
import { useRfq } from "@/context/rfq-context";
import { useDemoMode } from "@/context/demo-context";

// Define the questionnaire schema
const questionnaireSchema = z.object({
  // Company information
  companyName: z.string().min(1, { message: "Company name is required" }),
  companyWebsite: z.string().url({ message: "Please enter a valid URL" }).optional().or(z.literal("")),
  companyLocation: z.string().min(1, { message: "Company location is required" }),
  industry: z.string().min(1, { message: "Industry is required" }),
  
  // Project information
  projectName: z.string().min(1, { message: "Project name is required" }),
  projectDescription: z.string().optional(),
  budget: z.string().optional(),
  timeframe: z.string().optional(),
  
  // Hardware purpose
  usagePurpose: z.array(z.string()).nonempty({ message: "Select at least one purpose" }),
  usagePurposeOther: z.string().optional(),
  
  // Performance requirements
  performanceLevel: z.string().min(1, { message: "Performance level is required" }),
  customPerformanceDetails: z.string().optional(),
  
  // Memory requirements
  minimumMemory: z.string(),
  memoryBandwidth: z.string().optional(),
  
  // Framework compatibility
  frameworks: z.array(z.string()),
  frameworksOther: z.string().optional(),
  
  // Deployment environment
  deploymentEnvironment: z.string().min(1, { message: "Deployment environment is required" }),
  
  // Power and cooling
  maxPowerConsumption: z.string().optional(),
  coolingRequirements: z.string().optional(),
  
  // Compliance and regulatory
  regulatoryRequirements: z.array(z.string()),
  exportControls: z.string().optional(),
  
  // Quantity and timeline
  quantity: z.string().min(1, { message: "Quantity is required" }),
  deliveryTimeline: z.string().optional(),
});

type QuestionnaireFormValues = z.infer<typeof questionnaireSchema>;

const frameworks = [
  { id: "pytorch", label: "PyTorch" },
  { id: "tensorflow", label: "TensorFlow" },
  { id: "jax", label: "JAX" },
  { id: "onnx", label: "ONNX" },
  { id: "triton", label: "NVIDIA Triton" },
  { id: "tensorrt", label: "TensorRT" },
  { id: "directml", label: "DirectML" },
  { id: "mxnet", label: "Apache MXNet" },
  { id: "xla", label: "XLA" },
  { id: "other", label: "Other (specify)" },
];

const usagePurposes = [
  { id: "training", label: "ML Model Training" },
  { id: "inference", label: "Inference/Deployment" },
  { id: "research", label: "Research & Development" },
  { id: "computer-vision", label: "Computer Vision" },
  { id: "nlp", label: "Natural Language Processing" },
  { id: "recommendation", label: "Recommendation Systems" },
  { id: "scientific", label: "Scientific Computing" },
  { id: "other", label: "Other (specify)" },
];

const regulatoryRequirements = [
  { id: "none", label: "None" },
  { id: "cmmc", label: "CMMC (Cybersecurity Maturity Model Certification)" },
  { id: "fedramp", label: "FedRAMP" },
  { id: "gdpr", label: "GDPR Compliance" },
  { id: "hipaa", label: "HIPAA Compliance" },
  { id: "itar", label: "ITAR Restrictions" },
  { id: "tar", label: "Trade Agreements Act (TAA) Compliance" },
];

export default function AIHardwareQuestionnaire() {
  const [, navigate] = useLocation();
  const { toast } = useToast();
  const { setRfqId, setCurrentStep } = useRfq();
  const { isDemoMode, demoRfq, simulateProcessing } = useDemoMode();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeTab, setActiveTab] = useState("company");

  // Initialize form with default values focused on AI accelerator procurement
  const form = useForm<QuestionnaireFormValues>({
    resolver: zodResolver(questionnaireSchema),
    defaultValues: {
      // Company information - empty by default
      companyName: "",
      companyWebsite: "",
      companyLocation: "United States",
      industry: "Technology",
      
      // Project information - with AI hardware defaults
      projectName: "AI Accelerator Procurement",
      projectDescription: "Seeking high-performance GPUs for machine learning workloads",
      budget: "",
      timeframe: "3 months",
      
      // Hardware purpose - defaults for AI acceleration
      usagePurpose: ["training", "inference"],
      usagePurposeOther: "",
      
      // Performance requirements
      performanceLevel: "high",
      customPerformanceDetails: "Minimum 40 TFLOPS FP32 performance",
      
      // Memory requirements
      minimumMemory: "32",
      memoryBandwidth: "2000",
      
      // Framework compatibility
      frameworks: ["pytorch", "tensorflow"],
      frameworksOther: "",
      
      // Deployment environment
      deploymentEnvironment: "data-center",
      
      // Power and cooling
      maxPowerConsumption: "300",
      coolingRequirements: "Air cooling preferred, liquid cooling acceptable",
      
      // Compliance and regulatory
      regulatoryRequirements: [],
      exportControls: "",
      
      // Quantity and timeline
      quantity: "4",
      deliveryTimeline: "Within 2 months",
    }
  });

  // Function to handle demo mode processing
  const handleDemoProcessing = () => {
    setIsSubmitting(true);
    
    simulateProcessing(() => {
      setRfqId(demoRfq.id);
      setCurrentStep(2); // Move to step 2 (Review Requirements)
      
      toast({
        title: "Demo RFQ processed",
        description: "Redirecting to review requirements...",
        variant: "default"
      });
      
      setIsSubmitting(false);
      navigate(`/review/${demoRfq.id}`);
    });
  };

  // Function to go to the next tab
  const goToNextTab = () => {
    if (activeTab === "company") setActiveTab("project");
    else if (activeTab === "project") setActiveTab("hardware");
    else if (activeTab === "hardware") setActiveTab("performance");
    else if (activeTab === "performance") setActiveTab("deployment");
    else if (activeTab === "deployment") setActiveTab("compliance");
  };

  // Function to go to the previous tab
  const goToPrevTab = () => {
    if (activeTab === "compliance") setActiveTab("deployment");
    else if (activeTab === "deployment") setActiveTab("performance");
    else if (activeTab === "performance") setActiveTab("hardware");
    else if (activeTab === "hardware") setActiveTab("project");
    else if (activeTab === "project") setActiveTab("company");
  };

  // Function to handle form submission
  const onSubmit = async (values: QuestionnaireFormValues) => {
    try {
      setIsSubmitting(true);
      
      // Log form values for debugging
      console.log("Submitting AI hardware questionnaire with values:", values);
      
      // If in demo mode, use demo data instead of actual API call
      if (isDemoMode) {
        handleDemoProcessing();
        return;
      }
      
      // Prepare RFQ data from questionnaire
      const rfqTitle = `${values.companyName} - ${values.projectName}`;
      const rfqDescription = values.projectDescription || "AI hardware procurement";
      
      // Convert questionnaire data to ExtractedRequirement format
      const specifications = JSON.stringify({
        company: {
          name: values.companyName,
          website: values.companyWebsite,
          location: values.companyLocation,
          industry: values.industry
        },
        project: {
          name: values.projectName,
          description: values.projectDescription,
          budget: values.budget,
          timeframe: values.timeframe
        },
        requirements: {
          usagePurpose: values.usagePurpose,
          usagePurposeOther: values.usagePurposeOther,
          performanceLevel: values.performanceLevel,
          customPerformanceDetails: values.customPerformanceDetails,
          minimumMemory: values.minimumMemory,
          memoryBandwidth: values.memoryBandwidth,
          frameworks: values.frameworks,
          frameworksOther: values.frameworksOther,
          deploymentEnvironment: values.deploymentEnvironment,
          maxPowerConsumption: values.maxPowerConsumption,
          coolingRequirements: values.coolingRequirements,
          regulatoryRequirements: values.regulatoryRequirements,
          exportControls: values.exportControls,
          quantity: values.quantity,
          deliveryTimeline: values.deliveryTimeline
        }
      });
      
      // Create manual RFQ
      const rfqId = await createManualRFQ(
        rfqTitle,
        rfqDescription,
        specifications
      );
      
      console.log("RFQ created successfully with ID:", rfqId);
      
      // Set RFQ ID and next step in context
      setRfqId(rfqId);
      setCurrentStep(2); // Move to step 2 (Review Requirements)
      
      // Navigate to review page
      toast({
        title: "RFQ created successfully",
        description: "Redirecting to review requirements...",
        variant: "default"
      });
      
      navigate(`/review/${rfqId}`);
    } catch (error) {
      console.error("Error creating RFQ from questionnaire:", error);
      
      // More detailed error handling
      let errorMessage = "Failed to create RFQ";
      
      if (error instanceof Error) {
        errorMessage = error.message;
        
        // Add specific error details for common issues
        if (error.message.includes("404")) {
          errorMessage = "The server endpoint for creating RFQs could not be found. Please try again later.";
        } else if (error.message.includes("500")) {
          errorMessage = "The server encountered an error while processing your request. Please try again later.";
        } else if (error.message.includes("Network")) {
          errorMessage = "Network error. Please check your connection and try again.";
        }
      }
      
      toast({
        title: "Submission failed",
        description: errorMessage,
        variant: "destructive"
      });
    } finally {
      if (!isDemoMode) {
        setIsSubmitting(false);
      }
    }
  };

  const isAnyTabValid = () => {
    // Get current errors for the form
    const errors = form.formState.errors;
    
    // Function to check if the company tab has errors
    const isCompanyTabValid = () => {
      const companyFields = ['companyName', 'companyWebsite', 'companyLocation', 'industry'];
      return !companyFields.some(field => field in errors);
    };
    
    // Function to check if the project tab has errors
    const isProjectTabValid = () => {
      const projectFields = ['projectName', 'projectDescription', 'budget', 'timeframe'];
      return !projectFields.some(field => field in errors);
    };
    
    // Function to check if the hardware tab has errors
    const isHardwareTabValid = () => {
      const hardwareFields = ['usagePurpose', 'usagePurposeOther'];
      return !hardwareFields.some(field => field in errors);
    };
    
    // Function to check if the performance tab has errors
    const isPerformanceTabValid = () => {
      const performanceFields = ['performanceLevel', 'customPerformanceDetails', 'minimumMemory', 'memoryBandwidth', 'frameworks', 'frameworksOther'];
      return !performanceFields.some(field => field in errors);
    };
    
    // Function to check if the deployment tab has errors
    const isDeploymentTabValid = () => {
      const deploymentFields = ['deploymentEnvironment', 'maxPowerConsumption', 'coolingRequirements'];
      return !deploymentFields.some(field => field in errors);
    };
    
    // Function to check if the compliance tab has errors
    const isComplianceTabValid = () => {
      const complianceFields = ['regulatoryRequirements', 'exportControls', 'quantity', 'deliveryTimeline'];
      return !complianceFields.some(field => field in errors);
    };
    
    // Check the currently active tab
    switch (activeTab) {
      case "company":
        return isCompanyTabValid();
      case "project":
        return isProjectTabValid();
      case "hardware":
        return isHardwareTabValid();
      case "performance":
        return isPerformanceTabValid();
      case "deployment":
        return isDeploymentTabValid();
      case "compliance":
        return isComplianceTabValid();
      default:
        return true;
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <Card>
        <CardContent className="pt-6">
          <h2 className="text-2xl font-medium mb-6">AI Hardware Requirements Questionnaire</h2>
          
          <div className="mb-6">
            <p className="text-gray-600 mb-4">
              Complete this questionnaire to help us understand your AI hardware needs. 
              This will allow us to match you with the most suitable suppliers.
            </p>
          </div>
          
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                <TabsList className="grid grid-cols-6 mb-8">
                  <TabsTrigger value="company">Company</TabsTrigger>
                  <TabsTrigger value="project">Project</TabsTrigger>
                  <TabsTrigger value="hardware">Hardware</TabsTrigger>
                  <TabsTrigger value="performance">Performance</TabsTrigger>
                  <TabsTrigger value="deployment">Deployment</TabsTrigger>
                  <TabsTrigger value="compliance">Compliance</TabsTrigger>
                </TabsList>
                
                {/* Company Information Tab */}
                <TabsContent value="company" className="space-y-4">
                  <h3 className="text-lg font-medium mb-2">Company Information</h3>
                  
                  <FormField
                    control={form.control}
                    name="companyName"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Company Name*</FormLabel>
                        <FormControl>
                          <Input placeholder="Enter your company name" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="companyWebsite"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Company Website</FormLabel>
                        <FormControl>
                          <Input placeholder="https://www.example.com" {...field} />
                        </FormControl>
                        <FormDescription>
                          This helps us verify your company details
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="companyLocation"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Company Location (Country)*</FormLabel>
                        <FormControl>
                          <Input placeholder="e.g., United States" {...field} />
                        </FormControl>
                        <FormDescription>
                          This is important for compliance and export control checks
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="industry"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Industry*</FormLabel>
                        <Select onValueChange={field.onChange} defaultValue={field.value}>
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select your industry" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="Technology">Technology</SelectItem>
                            <SelectItem value="Finance">Finance & Banking</SelectItem>
                            <SelectItem value="Healthcare">Healthcare</SelectItem>
                            <SelectItem value="Education">Education</SelectItem>
                            <SelectItem value="Manufacturing">Manufacturing</SelectItem>
                            <SelectItem value="Retail">Retail</SelectItem>
                            <SelectItem value="Government">Government</SelectItem>
                            <SelectItem value="Research">Research Institution</SelectItem>
                            <SelectItem value="Automotive">Automotive</SelectItem>
                            <SelectItem value="Other">Other</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <div className="flex justify-end pt-4">
                    <Button
                      type="button"
                      onClick={goToNextTab}
                      disabled={!isAnyTabValid()}
                      className="flex items-center"
                    >
                      Next Step
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
                </TabsContent>
                
                {/* Project Information Tab */}
                <TabsContent value="project" className="space-y-4">
                  <h3 className="text-lg font-medium mb-2">Project Information</h3>
                  
                  <FormField
                    control={form.control}
                    name="projectName"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Project Name*</FormLabel>
                        <FormControl>
                          <Input placeholder="e.g., ML Infrastructure Upgrade" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="projectDescription"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Project Description</FormLabel>
                        <FormControl>
                          <Textarea
                            placeholder="Briefly describe your AI hardware needs and project goals"
                            rows={3}
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="budget"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Budget Range (USD)</FormLabel>
                        <FormControl>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select budget range" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="<10k">Under $10,000</SelectItem>
                              <SelectItem value="10k-50k">$10,000 - $50,000</SelectItem>
                              <SelectItem value="50k-100k">$50,000 - $100,000</SelectItem>
                              <SelectItem value="100k-500k">$100,000 - $500,000</SelectItem>
                              <SelectItem value="500k-1m">$500,000 - $1 million</SelectItem>
                              <SelectItem value=">1m">Over $1 million</SelectItem>
                              <SelectItem value="unknown">I don't know / Flexible</SelectItem>
                            </SelectContent>
                          </Select>
                        </FormControl>
                        <FormDescription>This helps us match solutions within your budget constraints</FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="timeframe"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Project Timeframe</FormLabel>
                        <FormControl>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select project timeframe" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="urgent">Urgent (within 1 month)</SelectItem>
                              <SelectItem value="1-3 months">1-3 months</SelectItem>
                              <SelectItem value="3-6 months">3-6 months</SelectItem>
                              <SelectItem value="6-12 months">6-12 months</SelectItem>
                              <SelectItem value=">12 months">Over 12 months</SelectItem>
                              <SelectItem value="flexible">Flexible / Not time-sensitive</SelectItem>
                            </SelectContent>
                          </Select>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <div className="flex justify-between pt-4">
                    <Button
                      type="button"
                      onClick={goToPrevTab}
                      variant="outline"
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
                      Previous
                    </Button>
                    <Button
                      type="button"
                      onClick={goToNextTab}
                      disabled={!isAnyTabValid()}
                      className="flex items-center"
                    >
                      Next Step
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
                </TabsContent>
                
                {/* Hardware Purpose Tab */}
                <TabsContent value="hardware" className="space-y-4">
                  <h3 className="text-lg font-medium mb-2">Hardware Purpose</h3>
                  
                  <FormField
                    control={form.control}
                    name="usagePurpose"
                    render={() => (
                      <FormItem>
                        <div className="mb-4">
                          <FormLabel className="text-base">Usage Purpose*</FormLabel>
                          <FormDescription>
                            Select all that apply for your AI hardware needs
                          </FormDescription>
                        </div>
                        {usagePurposes.map((item) => (
                          <FormField
                            key={item.id}
                            control={form.control}
                            name="usagePurpose"
                            render={({ field }) => {
                              return (
                                <FormItem
                                  key={item.id}
                                  className="flex flex-row items-start space-x-3 space-y-0 mb-1"
                                >
                                  <FormControl>
                                    <Checkbox
                                      checked={field.value?.includes(item.id)}
                                      onCheckedChange={(checked) => {
                                        return checked
                                          ? field.onChange([...field.value, item.id])
                                          : field.onChange(
                                              field.value?.filter(
                                                (value) => value !== item.id
                                              )
                                            )
                                      }}
                                    />
                                  </FormControl>
                                  <FormLabel className="font-normal">
                                    {item.label}
                                  </FormLabel>
                                </FormItem>
                              )
                            }}
                          />
                        ))}
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="usagePurposeOther"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Other Purpose (please specify)</FormLabel>
                        <FormControl>
                          <Input 
                            placeholder="Describe any other use cases"
                            disabled={!form.watch("usagePurpose").includes("other")}
                            {...field} 
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <div className="flex justify-between pt-4">
                    <Button
                      type="button"
                      onClick={goToPrevTab}
                      variant="outline"
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
                      Previous
                    </Button>
                    <Button
                      type="button"
                      onClick={goToNextTab}
                      disabled={!isAnyTabValid()}
                      className="flex items-center"
                    >
                      Next Step
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
                </TabsContent>
                
                {/* Performance Requirements Tab */}
                <TabsContent value="performance" className="space-y-4">
                  <h3 className="text-lg font-medium mb-2">Performance Requirements</h3>
                  
                  <FormField
                    control={form.control}
                    name="performanceLevel"
                    render={({ field }) => (
                      <FormItem className="space-y-3">
                        <FormLabel>Performance Level*</FormLabel>
                        <FormControl>
                          <RadioGroup
                            onValueChange={field.onChange}
                            defaultValue={field.value}
                            className="flex flex-col space-y-1"
                          >
                            <FormItem className="flex items-center space-x-3 space-y-0">
                              <FormControl>
                                <RadioGroupItem value="entry" />
                              </FormControl>
                              <FormLabel className="font-normal">
                                Entry-level (Academic projects, prototyping)
                              </FormLabel>
                            </FormItem>
                            <FormItem className="flex items-center space-x-3 space-y-0">
                              <FormControl>
                                <RadioGroupItem value="mid" />
                              </FormControl>
                              <FormLabel className="font-normal">
                                Mid-range (Small to medium production workloads)
                              </FormLabel>
                            </FormItem>
                            <FormItem className="flex items-center space-x-3 space-y-0">
                              <FormControl>
                                <RadioGroupItem value="high" />
                              </FormControl>
                              <FormLabel className="font-normal">
                                High-performance (Large-scale training, complex inference)
                              </FormLabel>
                            </FormItem>
                            <FormItem className="flex items-center space-x-3 space-y-0">
                              <FormControl>
                                <RadioGroupItem value="custom" />
                              </FormControl>
                              <FormLabel className="font-normal">
                                Custom performance requirements (specify below)
                              </FormLabel>
                            </FormItem>
                          </RadioGroup>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="customPerformanceDetails"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Custom Performance Details</FormLabel>
                        <FormControl>
                          <Textarea
                            placeholder="e.g., Need 40 TFLOPS for FP32, specific model throughput requirements, etc."
                            rows={2}
                            disabled={form.watch("performanceLevel") !== "custom"}
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="minimumMemory"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Minimum Memory (GB)</FormLabel>
                        <FormControl>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select minimum memory" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="8">8 GB</SelectItem>
                              <SelectItem value="16">16 GB</SelectItem>
                              <SelectItem value="24">24 GB</SelectItem>
                              <SelectItem value="32">32 GB</SelectItem>
                              <SelectItem value="48">48 GB</SelectItem>
                              <SelectItem value="64">64 GB</SelectItem>
                              <SelectItem value="80">80 GB or more</SelectItem>
                              <SelectItem value="unknown">I don't know</SelectItem>
                            </SelectContent>
                          </Select>
                        </FormControl>
                        <FormDescription>
                          Required GPU/accelerator memory capacity
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="memoryBandwidth"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Memory Bandwidth (GB/s)</FormLabel>
                        <FormControl>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select minimum memory bandwidth" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="500">Around 500 GB/s</SelectItem>
                              <SelectItem value="1000">Around 1,000 GB/s</SelectItem>
                              <SelectItem value="1500">Around 1,500 GB/s</SelectItem>
                              <SelectItem value="2000">Around 2,000 GB/s</SelectItem>
                              <SelectItem value="2500">Around 2,500 GB/s or more</SelectItem>
                              <SelectItem value="unknown">I don't know</SelectItem>
                            </SelectContent>
                          </Select>
                        </FormControl>
                        <FormDescription>
                          Higher memory bandwidth improves performance for memory-bound operations
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="frameworks"
                    render={() => (
                      <FormItem>
                        <div className="mb-4">
                          <FormLabel className="text-base">Framework Compatibility</FormLabel>
                          <FormDescription>
                            Select all frameworks that your applications will use
                          </FormDescription>
                        </div>
                        {frameworks.map((item) => (
                          <FormField
                            key={item.id}
                            control={form.control}
                            name="frameworks"
                            render={({ field }) => {
                              return (
                                <FormItem
                                  key={item.id}
                                  className="flex flex-row items-start space-x-3 space-y-0 mb-1"
                                >
                                  <FormControl>
                                    <Checkbox
                                      checked={field.value?.includes(item.id)}
                                      onCheckedChange={(checked) => {
                                        return checked
                                          ? field.onChange([...field.value, item.id])
                                          : field.onChange(
                                              field.value?.filter(
                                                (value) => value !== item.id
                                              )
                                            )
                                      }}
                                    />
                                  </FormControl>
                                  <FormLabel className="font-normal">
                                    {item.label}
                                  </FormLabel>
                                </FormItem>
                              )
                            }}
                          />
                        ))}
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="frameworksOther"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Other Framework (please specify)</FormLabel>
                        <FormControl>
                          <Input 
                            placeholder="List any other frameworks"
                            disabled={!form.watch("frameworks").includes("other")}
                            {...field} 
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <div className="flex justify-between pt-4">
                    <Button
                      type="button"
                      onClick={goToPrevTab}
                      variant="outline"
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
                      Previous
                    </Button>
                    <Button
                      type="button"
                      onClick={goToNextTab}
                      disabled={!isAnyTabValid()}
                      className="flex items-center"
                    >
                      Next Step
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
                </TabsContent>
                
                {/* Deployment Environment Tab */}
                <TabsContent value="deployment" className="space-y-4">
                  <h3 className="text-lg font-medium mb-2">Deployment Environment</h3>
                  
                  <FormField
                    control={form.control}
                    name="deploymentEnvironment"
                    render={({ field }) => (
                      <FormItem className="space-y-3">
                        <FormLabel>Deployment Environment*</FormLabel>
                        <FormControl>
                          <RadioGroup
                            onValueChange={field.onChange}
                            defaultValue={field.value}
                            className="flex flex-col space-y-1"
                          >
                            <FormItem className="flex items-center space-x-3 space-y-0">
                              <FormControl>
                                <RadioGroupItem value="data-center" />
                              </FormControl>
                              <FormLabel className="font-normal">
                                Data Center / Server Room
                              </FormLabel>
                            </FormItem>
                            <FormItem className="flex items-center space-x-3 space-y-0">
                              <FormControl>
                                <RadioGroupItem value="workstation" />
                              </FormControl>
                              <FormLabel className="font-normal">
                                Workstation / Desktop
                              </FormLabel>
                            </FormItem>
                            <FormItem className="flex items-center space-x-3 space-y-0">
                              <FormControl>
                                <RadioGroupItem value="edge" />
                              </FormControl>
                              <FormLabel className="font-normal">
                                Edge Computing / Embedded
                              </FormLabel>
                            </FormItem>
                            <FormItem className="flex items-center space-x-3 space-y-0">
                              <FormControl>
                                <RadioGroupItem value="cloud" />
                              </FormControl>
                              <FormLabel className="font-normal">
                                Cloud Integration
                              </FormLabel>
                            </FormItem>
                            <FormItem className="flex items-center space-x-3 space-y-0">
                              <FormControl>
                                <RadioGroupItem value="hybrid" />
                              </FormControl>
                              <FormLabel className="font-normal">
                                Hybrid (On-premises + Cloud)
                              </FormLabel>
                            </FormItem>
                          </RadioGroup>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="maxPowerConsumption"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Maximum Power Consumption (Watts per GPU/device)</FormLabel>
                        <FormDescription>
                          Select the maximum power draw acceptable for your environment
                        </FormDescription>
                        <FormControl>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select maximum power draw" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="150">Up to 150W</SelectItem>
                              <SelectItem value="250">Up to 250W</SelectItem>
                              <SelectItem value="300">Up to 300W</SelectItem>
                              <SelectItem value="350">Up to 350W</SelectItem>
                              <SelectItem value="500">Up to 500W</SelectItem>
                              <SelectItem value="700">Up to 700W</SelectItem>
                              <SelectItem value="unlimited">No limit</SelectItem>
                              <SelectItem value="unknown">I don't know</SelectItem>
                            </SelectContent>
                          </Select>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="coolingRequirements"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Cooling Requirements</FormLabel>
                        <FormControl>
                          <Textarea
                            placeholder="Describe your cooling capabilities or constraints"
                            rows={2}
                            {...field}
                          />
                        </FormControl>
                        <FormDescription>
                          Specify if you have liquid cooling available, air cooling restrictions, etc.
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <div className="flex justify-between pt-4">
                    <Button
                      type="button"
                      onClick={goToPrevTab}
                      variant="outline"
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
                      Previous
                    </Button>
                    <Button
                      type="button"
                      onClick={goToNextTab}
                      disabled={!isAnyTabValid()}
                      className="flex items-center"
                    >
                      Next Step
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
                </TabsContent>
                
                {/* Compliance and Final Details Tab */}
                <TabsContent value="compliance" className="space-y-4">
                  <h3 className="text-lg font-medium mb-2">Compliance & Order Details</h3>
                  
                  <FormField
                    control={form.control}
                    name="regulatoryRequirements"
                    render={() => (
                      <FormItem>
                        <div className="mb-4">
                          <FormLabel className="text-base">Regulatory Requirements</FormLabel>
                          <FormDescription>
                            Select all compliance requirements that apply
                          </FormDescription>
                        </div>
                        {regulatoryRequirements.map((item) => (
                          <FormField
                            key={item.id}
                            control={form.control}
                            name="regulatoryRequirements"
                            render={({ field }) => {
                              return (
                                <FormItem
                                  key={item.id}
                                  className="flex flex-row items-start space-x-3 space-y-0 mb-1"
                                >
                                  <FormControl>
                                    <Checkbox
                                      checked={field.value?.includes(item.id)}
                                      onCheckedChange={(checked) => {
                                        return checked
                                          ? field.onChange([...field.value, item.id])
                                          : field.onChange(
                                              field.value?.filter(
                                                (value) => value !== item.id
                                              )
                                            )
                                      }}
                                    />
                                  </FormControl>
                                  <FormLabel className="font-normal">
                                    {item.label}
                                  </FormLabel>
                                </FormItem>
                              )
                            }}
                          />
                        ))}
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="exportControls"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Export Control Considerations</FormLabel>
                        <FormControl>
                          <Textarea
                            placeholder="Note any specific export control or compliance concerns"
                            rows={2}
                            {...field}
                          />
                        </FormControl>
                        <FormDescription>
                          Important for international shipments of high-performance computing hardware
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="quantity"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Quantity Needed*</FormLabel>
                        <FormControl>
                          <Input 
                            type="number" 
                            min="1"
                            placeholder="Number of units required"
                            {...field} 
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <FormField
                    control={form.control}
                    name="deliveryTimeline"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Desired Delivery Timeline</FormLabel>
                        <FormControl>
                          <Select onValueChange={field.onChange} defaultValue={field.value}>
                            <FormControl>
                              <SelectTrigger>
                                <SelectValue placeholder="Select desired delivery timeline" />
                              </SelectTrigger>
                            </FormControl>
                            <SelectContent>
                              <SelectItem value="immediate">Immediate (ASAP)</SelectItem>
                              <SelectItem value="2-weeks">Within 2 weeks</SelectItem>
                              <SelectItem value="1-month">Within 1 month</SelectItem>
                              <SelectItem value="2-months">Within 2 months</SelectItem>
                              <SelectItem value="3-months">Within 3 months</SelectItem>
                              <SelectItem value="flexible">Flexible</SelectItem>
                            </SelectContent>
                          </Select>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  
                  <div className="flex justify-between pt-8">
                    <Button
                      type="button"
                      onClick={goToPrevTab}
                      variant="outline"
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
                      Previous
                    </Button>
                    <Button 
                      type="submit" 
                      disabled={isSubmitting || !form.formState.isValid}
                      className="flex items-center"
                    >
                      {isSubmitting ? "Processing..." : "Submit Questionnaire"}
                      {!isSubmitting && (
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
                            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                          />
                        </svg>
                      )}
                    </Button>
                  </div>
                </TabsContent>
              </Tabs>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}