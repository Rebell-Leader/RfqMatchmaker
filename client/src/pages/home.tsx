import { useState } from "react";
import { useRfq } from "@/context/rfq-context";
import { STEPS } from "@/lib/constants";
import { Stepper } from "@/components/ui/stepper";
import { Building, HelpCircle, Database, Server } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import UploadRfq from "./upload-rfq";
import ReviewRequirements from "./review-requirements";
import MatchSuppliers from "./match-suppliers";
import ScoreResults from "./score-results";
import SendProposals from "./send-proposals";

export default function Home() {
  const { currentStep } = useRfq();
  const [showAdmin, setShowAdmin] = useState(false);
  const [isSeeding, setIsSeeding] = useState(false);
  const { toast } = useToast();
  
  // Handle seeding AI hardware products
  const handleSeedAIHardware = async () => {
    try {
      setIsSeeding(true);
      const response = await fetch('/api/seed/ai-hardware', {
        method: 'POST',
      });
      
      if (!response.ok) {
        throw new Error(`Failed to seed AI hardware products: ${response.statusText}`);
      }
      
      const result = await response.json();
      
      toast({
        title: "Database Seeded Successfully",
        description: `Added ${result.count} AI hardware products to the database.`,
        duration: 5000,
      });
    } catch (error) {
      console.error('Error seeding AI hardware:', error);
      toast({
        title: "Seeding Failed",
        description: error instanceof Error ? error.message : "Unknown error occurred",
        variant: "destructive",
        duration: 5000,
      });
    } finally {
      setIsSeeding(false);
    }
  };
  
  // Render different component based on current step
  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return <UploadRfq />;
      case 2:
        return <ReviewRequirements />;
      case 3:
        return <MatchSuppliers />;
      case 4:
        return <ScoreResults />;
      case 5:
        return <SendProposals />;
      default:
        return <UploadRfq />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-md">
        <div className="container mx-auto px-4 py-3 flex justify-between items-center">
          <div className="flex items-center">
            <Building className="text-primary mr-2 h-6 w-6" />
            <h1 className="text-xl font-medium">RFQ Processor</h1>
          </div>
          <div className="flex space-x-2">
            <Dialog>
              <DialogTrigger asChild>
                <Button variant="outline" size="sm" onClick={() => setShowAdmin(!showAdmin)}
                  className="flex items-center text-sm">
                  <Database className="mr-1 h-4 w-4" />
                  Admin
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Database Administration</DialogTitle>
                  <DialogDescription>
                    Use these tools to manage the database for the procurement platform.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="flex flex-col space-y-2">
                    <h3 className="text-sm font-medium">AI Hardware Products</h3>
                    <Button 
                      variant="default" 
                      onClick={handleSeedAIHardware}
                      disabled={isSeeding}
                      className="flex items-center"
                    >
                      <Server className="mr-2 h-4 w-4" />
                      {isSeeding ? "Seeding..." : "Seed AI Hardware Products"}
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
            
            <Button variant="ghost" className="text-primary flex items-center">
              <HelpCircle className="mr-1 h-4 w-4" />
              Help
            </Button>
          </div>
        </div>
      </header>

      {/* Stepper Navigation */}
      <Stepper steps={STEPS} currentStep={currentStep} />

      {/* Main Content */}
      <main className="flex-grow container mx-auto px-4 py-6">
        {renderStepContent()}
      </main>

      {/* Footer */}
      <footer className="bg-gray-100 border-t border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex flex-col md:flex-row justify-between items-center text-sm text-gray-600">
            <div className="mb-4 md:mb-0">
              &copy; {new Date().getFullYear()} RFQ Processor - B2B Supplier Matching Platform
            </div>
            <div className="flex gap-4">
              <a href="#" className="hover:text-gray-900">Privacy Policy</a>
              <a href="#" className="hover:text-gray-900">Terms of Service</a>
              <a href="#" className="hover:text-gray-900">Contact Support</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
