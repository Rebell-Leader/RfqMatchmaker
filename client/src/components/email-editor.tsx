import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { EmailTemplate } from '@shared/schema';
import { generatePdfFromEmail } from '@/lib/pdf-generator';
import { toast } from '@/hooks/use-toast';
import { Save, Send, FileDown, Eye } from 'lucide-react';

interface EmailEditorProps {
  emailTemplate: EmailTemplate;
  onSave: (emailTemplate: EmailTemplate) => void;
  readOnly?: boolean;
}

export function EmailEditor({ emailTemplate, onSave, readOnly = false }: EmailEditorProps) {
  const [email, setEmail] = useState<EmailTemplate>(emailTemplate);
  const [activeTab, setActiveTab] = useState<string>("edit");

  const handleInputChange = (field: keyof EmailTemplate, value: string) => {
    setEmail((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = () => {
    onSave(email);
    toast({
      title: "Email template saved",
      description: "Your changes have been saved successfully.",
    });
  };

  const handleSend = () => {
    // This is mocked as requested
    toast({
      title: "Email sent",
      description: `Email proposal sent to ${email.to}.`,
    });
  };

  const handleDownloadPdf = async () => {
    try {
      // Generate PDF
      const pdfBlob = await generatePdfFromEmail(email);
      
      // Create a download link
      const url = URL.createObjectURL(pdfBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `proposal-${new Date().toISOString().slice(0, 10)}.pdf`;
      document.body.appendChild(link);
      link.click();
      
      // Clean up
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      toast({
        title: "PDF Downloaded",
        description: "Your proposal has been downloaded as a PDF.",
      });
    } catch (error) {
      console.error("Error generating PDF:", error);
      toast({
        title: "Error downloading PDF",
        description: "There was an error generating the PDF. Please try again.",
        variant: "destructive",
      });
    }
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex justify-between items-center">
          <span>Email Proposal</span>
          <div className="flex gap-2">
            {!readOnly && (
              <Button variant="outline" size="sm" onClick={handleSave}>
                <Save className="w-4 h-4 mr-2" />
                Save Draft
              </Button>
            )}
            <Button variant="outline" size="sm" onClick={handleDownloadPdf}>
              <FileDown className="w-4 h-4 mr-2" />
              Download PDF
            </Button>
            {!readOnly && (
              <Button size="sm" onClick={handleSend}>
                <Send className="w-4 h-4 mr-2" />
                Send Email
              </Button>
            )}
          </div>
        </CardTitle>
      </CardHeader>
      
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid grid-cols-2 w-[200px] mx-6">
          <TabsTrigger value="edit">Edit</TabsTrigger>
          <TabsTrigger value="preview">Preview</TabsTrigger>
        </TabsList>
        
        <TabsContent value="edit">
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="to">To</Label>
              <Input 
                id="to" 
                value={email.to} 
                onChange={(e) => handleInputChange('to', e.target.value)}
                readOnly={readOnly}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="cc">CC</Label>
              <Input 
                id="cc" 
                value={email.cc || ''} 
                onChange={(e) => handleInputChange('cc', e.target.value)}
                readOnly={readOnly}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="subject">Subject</Label>
              <Input 
                id="subject" 
                value={email.subject} 
                onChange={(e) => handleInputChange('subject', e.target.value)}
                readOnly={readOnly}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="body">Message</Label>
              <Textarea 
                id="body" 
                value={email.body} 
                onChange={(e) => handleInputChange('body', e.target.value)}
                className="min-h-[200px]"
                readOnly={readOnly}
              />
            </div>
          </CardContent>
        </TabsContent>
        
        <TabsContent value="preview">
          <CardContent className="space-y-4">
            <Alert>
              <AlertDescription>
                This is how your email will appear to recipients.
              </AlertDescription>
            </Alert>
            
            <Card className="border-dashed">
              <CardContent className="pt-6 pb-4">
                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-semibold">To: {email.to}</p>
                    {email.cc && <p className="text-sm font-semibold">CC: {email.cc}</p>}
                    <p className="text-sm font-semibold">Subject: {email.subject}</p>
                  </div>
                  
                  <div className="border-t pt-4">
                    <div className="whitespace-pre-wrap text-sm">
                      {email.body}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </CardContent>
        </TabsContent>
      </Tabs>
      
      <CardFooter className="flex justify-end gap-2">
        {!readOnly && (
          <Button variant="outline" onClick={handleSave}>
            <Save className="w-4 h-4 mr-2" />
            Save Draft
          </Button>
        )}
        <Button variant="outline" onClick={handleDownloadPdf}>
          <FileDown className="w-4 h-4 mr-2" />
          Download PDF
        </Button>
        {!readOnly && (
          <Button onClick={handleSend}>
            <Send className="w-4 h-4 mr-2" />
            Send Email
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}