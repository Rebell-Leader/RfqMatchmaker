import { useEffect, useState, useRef } from "react";
import { useParams, useLocation } from "wouter";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { useRfq } from "@/context/rfq-context";
import { useDemoMode } from "@/context/demo-context";
import { getRFQById } from "@/lib/supplier-service";
import { generateEmailProposal } from "@/lib/ai-service";
import { Skeleton } from "@/components/ui/skeleton";

export default function SendProposals() {
  const { id } = useParams<{ id: string }>();
  const [, navigate] = useLocation();
  const { toast } = useToast();
  const { setRfqId, selectedMatches, emailTemplate, setEmailTemplate } = useRfq();
  const { isDemoMode, demoRfq, demoEmailProposal, simulateProcessing } = useDemoMode();
  
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [rfq, setRfq] = useState<any>(null);
  const [requirements, setRequirements] = useState<any>(null);
  const [selectedSupplier, setSelectedSupplier] = useState<any>(null);
  const [emailData, setEmailData] = useState({
    to: "",
    cc: "",
    subject: "",
    body: ""
  });
  
  const textAreaRef = useRef<HTMLTextAreaElement>(null);
  
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
            
            // If there's a recommended supplier in demo mode
            if (selectedMatches.length > 0) {
              const recommendedSupplier = selectedMatches.reduce((prev, current) => 
                prev.matchScore > current.matchScore ? prev : current
              );
              setSelectedSupplier(recommendedSupplier);
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
        setLoading(false);
      }
    }
    
    if (id) {
      fetchRfq();
    }
  }, [id, setRfqId, toast]);
  
  useEffect(() => {
    // Set the selected supplier from context
    if (selectedMatches && selectedMatches.length > 0) {
      setSelectedSupplier(selectedMatches[0]);
    }
  }, [selectedMatches]);
  
  useEffect(() => {
    // Generate email proposal if selected supplier exists and no email template yet
    async function generateEmail() {
      if (selectedSupplier && !emailTemplate) {
        try {
          setGenerating(true);
          
          // If in demo mode, use demo email proposal
          if (isDemoMode) {
            simulateProcessing(() => {
              setEmailTemplate(demoEmailProposal);
              setEmailData({
                to: demoEmailProposal.to,
                cc: demoEmailProposal.cc || "",
                subject: demoEmailProposal.subject,
                body: demoEmailProposal.body
              });
              setGenerating(false);
            });
            return;
          }
          
          // Otherwise generate real email
          // Find proposal ID from match
          // For demo purposes, we'll use a placeholder ID
          const proposalId = 1; // In a real implementation, this would come from the database
          
          const generatedEmail = await generateEmailProposal(proposalId);
          setEmailTemplate(generatedEmail);
          setEmailData({
            to: generatedEmail.to,
            cc: generatedEmail.cc || "",
            subject: generatedEmail.subject,
            body: generatedEmail.body
          });
        } catch (error) {
          console.error("Error generating email:", error);
          toast({
            title: "Error",
            description: "Failed to generate email proposal. Please try again.",
            variant: "destructive",
          });
          
          // Set default email if generation fails
          if (selectedSupplier) {
            const defaultTo = `sales@${selectedSupplier.supplier.name.toLowerCase().replace(/\s+/g, '')}.com`;
            const defaultSubject = `RFQ: ${requirements?.title || "Product Request"}`;
            setEmailData({
              to: defaultTo,
              cc: "",
              subject: defaultSubject,
              body: `Dear ${selectedSupplier.supplier.name} Team,\n\nWe are interested in your ${selectedSupplier.product.name} product for our needs. Please provide a formal quotation.\n\nThank you.`
            });
          }
        } finally {
          if (!isDemoMode) {
            setGenerating(false);
          }
        }
      } else if (emailTemplate) {
        // Use existing email template from context
        setEmailData({
          to: emailTemplate.to,
          cc: emailTemplate.cc || "",
          subject: emailTemplate.subject,
          body: emailTemplate.body
        });
      }
    }
    
    if (selectedSupplier && requirements) {
      generateEmail();
    }
  }, [selectedSupplier, requirements, emailTemplate, setEmailTemplate, toast, isDemoMode, demoEmailProposal, simulateProcessing]);
  
  const handleGoBack = () => {
    navigate(`/score/${id}`);
  };
  
  const handleFinishProcess = () => {
    toast({
      title: "Process Completed",
      description: "Your RFQ processing workflow has been completed successfully.",
      variant: "default",
    });
    navigate("/");
  };
  
  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setEmailData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleCopyToClipboard = () => {
    if (textAreaRef.current) {
      textAreaRef.current.select();
      document.execCommand('copy');
      
      toast({
        title: "Copied to clipboard",
        description: "Email content has been copied to clipboard.",
        variant: "default",
      });
    }
  };
  
  const handleSendEmail = () => {
    // In a real implementation, this would send the email via an API
    toast({
      title: "Email Sent",
      description: `Your proposal has been sent to ${emailData.to}`,
      variant: "default",
    });
    
    // Navigate back to home or show a success page
    setTimeout(() => {
      navigate("/");
    }, 1500);
  };
  
  const handleSaveAsDraft = () => {
    toast({
      title: "Draft Saved",
      description: "Your email proposal has been saved as a draft.",
      variant: "default",
    });
  };
  
  const handleDownloadAsPDF = () => {
    toast({
      title: "PDF Downloaded",
      description: "Your email proposal has been downloaded as a PDF.",
      variant: "default",
    });
  };
  
  // Render loading skeleton
  if (loading || generating) {
    return (
      <div className="max-w-3xl mx-auto">
        <Card>
          <CardContent className="pt-6">
            <Skeleton className="h-8 w-2/5 mb-2" />
            <Skeleton className="h-4 w-4/5 mb-6" />
            
            <div className="mb-6">
              <Skeleton className="h-6 w-1/4 mb-3" />
              <Skeleton className="h-16 w-full" />
            </div>
            
            <div className="mb-6">
              <div className="flex justify-between items-center mb-3">
                <Skeleton className="h-6 w-1/3" />
                <Skeleton className="h-6 w-1/4" />
              </div>
              
              <div className="border border-gray-200 rounded-lg">
                <div className="border-b border-gray-200 p-4">
                  <div className="mb-3">
                    <Skeleton className="h-4 w-1/6 mb-1" />
                    <Skeleton className="h-10 w-full" />
                  </div>
                  <div className="mb-3">
                    <Skeleton className="h-4 w-1/6 mb-1" />
                    <Skeleton className="h-10 w-full" />
                  </div>
                  <div>
                    <Skeleton className="h-4 w-1/6 mb-1" />
                    <Skeleton className="h-10 w-full" />
                  </div>
                </div>
                
                <div className="p-4">
                  <Skeleton className="h-4 w-1/6 mb-2" />
                  <Skeleton className="h-48 w-full" />
                </div>
              </div>
            </div>
            
            <div className="mb-6">
              <Skeleton className="h-6 w-1/4 mb-3" />
              <div className="flex flex-col md:flex-row gap-4">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
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
  
  if (!rfq || !requirements || !selectedSupplier) {
    return (
      <div className="max-w-3xl mx-auto">
        <Card>
          <CardContent className="pt-6">
            <h2 className="text-2xl font-medium mb-2">No Supplier Selected</h2>
            <p className="text-gray-600 mb-6">
              No supplier has been selected for proposal generation. Please go back and select a supplier.
            </p>
            <Button onClick={() => navigate(`/match/${id}`)}>Return to Supplier Matching</Button>
          </CardContent>
        </Card>
      </div>
    );
  }
  
  return (
    <div className="max-w-3xl mx-auto">
      <Card>
        <CardContent className="pt-6">
          <h2 className="text-2xl font-medium mb-2">Send Proposals</h2>
          <p className="text-gray-600 mb-6">
            Review and customize the generated email proposals before sending to selected suppliers.
          </p>
          
          {/* Supplier Selection */}
          <div className="mb-6">
            <h3 className="text-lg font-medium mb-3">Selected Supplier</h3>
            <div className="flex items-center p-4 bg-gray-50 rounded-lg">
              <img 
                src={selectedSupplier.supplier.logoUrl} 
                alt={selectedSupplier.supplier.name} 
                className="w-10 h-10 mr-3 rounded" 
              />
              <div>
                <h4 className="font-medium">{selectedSupplier.supplier.name}</h4>
                <p className="text-sm text-gray-600">
                  {selectedSupplier.product.name} - {new Intl.NumberFormat('en-US', {
                    style: 'currency',
                    currency: 'USD',
                  }).format(selectedSupplier.product.price)}/unit
                </p>
              </div>
              <div className="ml-auto">
                <Button 
                  variant="link" 
                  className="text-primary hover:text-primary-dark text-sm flex items-center p-0 h-auto"
                  onClick={() => navigate(`/match/${id}`)}
                >
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
                  Change selection
                </Button>
              </div>
            </div>
          </div>
          
          {/* Email Preview */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-lg font-medium">Email Proposal Preview</h3>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={handleCopyToClipboard}
                className="text-primary hover:text-primary-dark flex items-center text-sm"
              >
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
                    d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                  />
                </svg>
                Copy to clipboard
              </Button>
            </div>
            
            <div className="border border-gray-200 rounded-lg">
              {/* Email Header */}
              <div className="border-b border-gray-200 p-4">
                <div className="mb-3">
                  <Label htmlFor="to" className="block text-sm font-medium text-gray-700 mb-1">To:</Label>
                  <Input 
                    type="text" 
                    id="to"
                    name="to"
                    value={emailData.to} 
                    onChange={handleEmailChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary" 
                  />
                </div>
                <div className="mb-3">
                  <Label htmlFor="cc" className="block text-sm font-medium text-gray-700 mb-1">Cc:</Label>
                  <Input 
                    type="text" 
                    id="cc"
                    name="cc"
                    value={emailData.cc} 
                    onChange={handleEmailChange}
                    placeholder="Add Cc recipients" 
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary" 
                  />
                </div>
                <div>
                  <Label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-1">Subject:</Label>
                  <Input 
                    type="text" 
                    id="subject"
                    name="subject"
                    value={emailData.subject} 
                    onChange={handleEmailChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary" 
                  />
                </div>
              </div>
              
              {/* Email Body */}
              <div className="p-4">
                <Label htmlFor="body" className="block text-sm font-medium text-gray-700 mb-2">Message:</Label>
                <Textarea 
                  id="body"
                  name="body"
                  ref={textAreaRef}
                  value={emailData.body} 
                  onChange={handleEmailChange}
                  rows={12} 
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary" 
                />
              </div>
            </div>
          </div>
          
          {/* Actions */}
          <div className="mb-6">
            <h3 className="text-lg font-medium mb-3">Email Actions</h3>
            <div className="flex flex-col md:flex-row gap-4">
              <Button 
                className="flex-1 bg-primary text-white py-2 px-4 rounded hover:bg-primary-dark flex items-center justify-center"
                onClick={handleSendEmail}
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
                    d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                  />
                </svg>
                Send Email
              </Button>
              <Button 
                variant="outline"
                className="flex-1 border border-gray-300 text-gray-700 py-2 px-4 rounded hover:bg-gray-50 flex items-center justify-center"
                onClick={handleSaveAsDraft}
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
                    d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"
                  />
                </svg>
                Save as Draft
              </Button>
              <Button 
                variant="outline"
                className="flex-1 border border-gray-300 text-gray-700 py-2 px-4 rounded hover:bg-gray-50 flex items-center justify-center"
                onClick={handleDownloadAsPDF}
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
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                  />
                </svg>
                Download as PDF
              </Button>
            </div>
          </div>
          
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
              onClick={handleFinishProcess}
              variant="secondary"
              className="flex items-center"
            >
              Complete Process
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
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
