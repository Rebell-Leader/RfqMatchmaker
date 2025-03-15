import { useState } from "react";
import { useLocation } from "wouter";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { useToast } from "@/hooks/use-toast";
import { uploadRFQFile, createManualRFQ } from "@/lib/ai-service";
import { useRfq } from "@/context/rfq-context";

// Form schema for manual RFQ entry
const manualRfqSchema = z.object({
  title: z.string().min(1, { message: "Title is required" }),
  description: z.string().optional(),
  specifications: z.string().min(1, { message: "Specifications are required" })
});

type ManualRfqFormValues = z.infer<typeof manualRfqSchema>;

export default function UploadRfq() {
  const [, navigate] = useLocation();
  const { toast } = useToast();
  const { setRfqId } = useRfq();
  const [isUploading, setIsUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  // Initialize form with default values
  const form = useForm<ManualRfqFormValues>({
    resolver: zodResolver(manualRfqSchema),
    defaultValues: {
      title: "",
      description: "",
      specifications: ""
    }
  });

  // Function to handle file drop
  const handleDrop = async (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragActive(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      await handleFileUpload(files[0]);
    }
  };

  // Function to handle drag events
  const handleDrag = (e: React.DragEvent<HTMLDivElement>, active: boolean) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(active);
  };

  // Function to handle file input change
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      await handleFileUpload(files[0]);
    }
  };

  // Function to handle file selection button click
  const handleFileButtonClick = () => {
    document.getElementById("rfq-upload")?.click();
  };

  // Function to handle file upload
  const handleFileUpload = async (file: File) => {
    try {
      setIsUploading(true);
      
      // Check file type
      const allowedTypes = [".pdf", ".doc", ".docx", ".txt"];
      const fileExt = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();
      
      if (!allowedTypes.includes(fileExt)) {
        toast({
          title: "Invalid file type",
          description: "Please upload a PDF, DOC, DOCX, or TXT file.",
          variant: "destructive"
        });
        return;
      }
      
      // Upload file
      const rfqId = await uploadRFQFile(file);
      
      // Set RFQ ID in context
      setRfqId(rfqId);
      
      // Navigate to review page
      toast({
        title: "RFQ uploaded successfully",
        description: "Redirecting to review requirements...",
        variant: "default"
      });
      
      navigate(`/review/${rfqId}`);
    } catch (error) {
      console.error("Error uploading file:", error);
      toast({
        title: "Upload failed",
        description: error instanceof Error ? error.message : "Failed to upload RFQ file",
        variant: "destructive"
      });
    } finally {
      setIsUploading(false);
    }
  };

  // Function to handle manual RFQ submission
  const onSubmit = async (values: ManualRfqFormValues) => {
    try {
      setIsUploading(true);
      
      // Create manual RFQ
      const rfqId = await createManualRFQ(
        values.title,
        values.description || "",
        values.specifications
      );
      
      // Set RFQ ID in context
      setRfqId(rfqId);
      
      // Navigate to review page
      toast({
        title: "RFQ created successfully",
        description: "Redirecting to review requirements...",
        variant: "default"
      });
      
      navigate(`/review/${rfqId}`);
    } catch (error) {
      console.error("Error creating manual RFQ:", error);
      toast({
        title: "Submission failed",
        description: error instanceof Error ? error.message : "Failed to create RFQ",
        variant: "destructive"
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <Card>
        <CardContent className="pt-6">
          <h2 className="text-2xl font-medium mb-6">Upload RFQ Document</h2>
          
          <div className="mb-6">
            <p className="text-gray-600 mb-4">
              Upload a Request for Quotation (RFQ) document to start the supplier matching process. 
              We'll extract the requirements and find matching suppliers.
            </p>
            
            <div 
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                dragActive ? "border-primary bg-primary/5" : "border-gray-300"
              }`}
              onDragOver={(e) => handleDrag(e, true)}
              onDragEnter={(e) => handleDrag(e, true)}
              onDragLeave={(e) => handleDrag(e, false)}
              onDrop={handleDrop}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-12 w-12 mx-auto text-gray-400 mb-3"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
              <p className="text-gray-500 mb-4">
                Drag and drop your RFQ document here, or click to browse
              </p>
              <input
                type="file"
                id="rfq-upload"
                className="hidden"
                accept=".pdf,.doc,.docx,.txt"
                onChange={handleFileChange}
              />
              <Button
                onClick={handleFileButtonClick}
                disabled={isUploading}
              >
                {isUploading ? "Uploading..." : "Browse Files"}
              </Button>
              <p className="text-sm text-gray-400 mt-2">
                Supported formats: PDF, DOC, DOCX, TXT
              </p>
            </div>
          </div>
          
          <div className="border-t border-gray-200 pt-6 mt-6">
            <h3 className="text-lg font-medium mb-4">Or Enter RFQ Details Manually</h3>
            
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <FormField
                  control={form.control}
                  name="title"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>RFQ Title</FormLabel>
                      <FormControl>
                        <Input 
                          placeholder="e.g., Supply and Delivery of Computer Equipment" 
                          {...field} 
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="description"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>RFQ Description</FormLabel>
                      <FormControl>
                        <Textarea 
                          placeholder="Brief description of RFQ requirements..."
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
                  name="specifications"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Technical Specifications</FormLabel>
                      <FormControl>
                        <Textarea 
                          placeholder="Enter product specifications, quantities, and requirements..."
                          rows={5}
                          {...field} 
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <div className="flex justify-end pt-2">
                  <Button 
                    type="submit" 
                    disabled={isUploading}
                    className="flex items-center"
                  >
                    {isUploading ? "Processing..." : "Process RFQ"}
                    {!isUploading && (
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
                    )}
                  </Button>
                </div>
              </form>
            </Form>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
