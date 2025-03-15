import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { Upload, FileText, AlertTriangle, ArrowRight } from "lucide-react";
import { processRfqFile, processRfqText } from "@/lib/ai";
import { useRfq } from "@/contexts/rfq-context";

export function RfqUploadForm() {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [specifications, setSpecifications] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const { toast } = useToast();
  const { setRfq, goToNextStep } = useRfq();

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      if (selectedFile.size > 10 * 1024 * 1024) { // 10MB limit
        setError("File size exceeds the 10MB limit.");
        return;
      }
      
      const fileType = selectedFile.type;
      if (!['application/pdf', 'text/plain', 'application/msword', 
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(fileType)) {
        setError("Only PDF, DOC, DOCX, and TXT files are supported.");
        return;
      }
      
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleBrowseClick = () => {
    document.getElementById("rfq-upload")?.click();
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.currentTarget.classList.add("border-primary");
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.currentTarget.classList.remove("border-primary");
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.currentTarget.classList.remove("border-primary");
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      if (droppedFile.size > 10 * 1024 * 1024) {
        setError("File size exceeds the 10MB limit.");
        return;
      }
      
      const fileType = droppedFile.type;
      if (!['application/pdf', 'text/plain', 'application/msword', 
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(fileType)) {
        setError("Only PDF, DOC, DOCX, and TXT files are supported.");
        return;
      }
      
      setFile(droppedFile);
      setError(null);
    }
  };

  const handleProcessRfq = async () => {
    setIsSubmitting(true);
    setError(null);

    try {
      // Process either file or manually entered text
      let response;
      if (file) {
        response = await processRfqFile(file);
      } else if (title && (description || specifications)) {
        // Create manual text input from form fields
        const manualText = `
          Title: ${title}
          
          Description: ${description}
          
          Technical Specifications:
          ${specifications}
        `;
        
        response = await processRfqText(manualText);
      } else {
        throw new Error("Please either upload a file or fill in the manual entry form.");
      }

      // Store the RFQ data and proceed to next step
      setRfq(response);
      toast({
        title: "RFQ Processed Successfully",
        description: "Your RFQ has been processed. You can now review the extracted requirements.",
      });
      goToNextStep();
    } catch (error) {
      setError(error instanceof Error ? error.message : "An error occurred while processing the RFQ.");
      toast({
        variant: "destructive",
        title: "RFQ Processing Failed",
        description: error instanceof Error ? error.message : "An error occurred while processing the RFQ.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card className="max-w-3xl mx-auto">
      <CardContent className="pt-6">
        <h2 className="text-2xl font-medium mb-6">Upload RFQ Document</h2>
        
        <div className="mb-6">
          <p className="text-gray-600 mb-4">
            Upload a Request for Quotation (RFQ) document to start the supplier matching process. 
            We'll extract the requirements and find matching suppliers.
          </p>
          
          <div 
            className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center"
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <Upload className="h-12 w-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-500 mb-4">
              {file ? `Selected file: ${file.name}` : "Drag and drop your RFQ document here, or click to browse"}
            </p>
            <input 
              type="file" 
              id="rfq-upload" 
              className="hidden" 
              accept=".pdf,.doc,.docx,.txt"
              onChange={handleFileSelect}
            />
            <Button onClick={handleBrowseClick}>Browse Files</Button>
            <p className="text-sm text-gray-400 mt-2">Supported formats: PDF, DOC, DOCX, TXT</p>
          </div>
          
          {error && (
            <div className="bg-red-50 text-red-800 p-3 mt-4 rounded-md flex items-start">
              <AlertTriangle className="h-5 w-5 mr-2 mt-0.5 flex-shrink-0" />
              <p className="text-sm">{error}</p>
            </div>
          )}
        </div>
        
        <div className="border-t border-gray-200 pt-6 mt-6">
          <h3 className="text-lg font-medium mb-4">Or Enter RFQ Details Manually</h3>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="rfq-title">RFQ Title</Label>
              <Input
                id="rfq-title"
                placeholder="e.g., Supply and Delivery of Computer Equipment"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>
            
            <div>
              <Label htmlFor="rfq-description">RFQ Description</Label>
              <Textarea
                id="rfq-description"
                placeholder="Brief description of RFQ requirements..."
                rows={3}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>
            
            <div>
              <Label htmlFor="rfq-specifications">Technical Specifications</Label>
              <Textarea
                id="rfq-specifications"
                placeholder="Enter product specifications, quantities, and requirements..."
                rows={5}
                value={specifications}
                onChange={(e) => setSpecifications(e.target.value)}
              />
            </div>
          </div>
        </div>
        
        <div className="flex justify-end mt-6">
          <Button 
            onClick={handleProcessRfq} 
            disabled={isSubmitting}
            className="flex items-center"
          >
            {isSubmitting ? "Processing..." : "Process RFQ"}
            {!isSubmitting && <ArrowRight className="ml-2 h-4 w-4" />}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
