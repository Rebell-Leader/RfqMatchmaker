import { useState, useEffect } from "react";
import { useRfq } from "@/contexts/rfq-context";
import { STEPS } from "@/lib/constants";
import { Stepper } from "@/components/ui/stepper";
import { Business, HelpCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import UploadRfq from "./upload-rfq";
import ReviewRequirements from "./review-requirements";
import MatchSuppliers from "./match-suppliers";
import ScoreResults from "./score-results";
import SendProposals from "./send-proposals";

export default function Home() {
  const { currentStep } = useRfq();
  
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
            <Business className="text-primary mr-2 h-6 w-6" />
            <h1 className="text-xl font-medium">RFQ Processor</h1>
          </div>
          <div>
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
