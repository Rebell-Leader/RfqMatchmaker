import { Switch, Route, useLocation } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { RfqProvider, useRfq } from "./context/rfq-context";
import { DemoProvider, useDemoMode } from "./context/demo-context";
import Layout from "./components/layout";
import NotFound from "@/pages/not-found";
import Landing from "@/pages/landing";
import UploadRfq from "@/pages/upload-rfq";
import ReviewRequirements from "@/pages/review-requirements";
import MatchSuppliers from "@/pages/match-suppliers";
import ScoreResults from "@/pages/score-results";
import SendProposals from "@/pages/send-proposals";
import AIHardwarePlatform from "@/pages/ai-hardware-platform";
import AIHardwareQuestionnaire from "@/pages/ai-hardware-questionnaire";
import { Button } from "@/components/ui/button";
import { Beaker, Cpu } from "lucide-react";
import { useEffect } from "react";

// Demo Mode Toggle Button
function DemoModeToggle() {
  const { isDemoMode, toggleDemoMode } = useDemoMode();
  
  return (
    <Button
      variant={isDemoMode ? "default" : "outline"}
      size="sm"
      className="fixed top-4 right-4 z-50 flex items-center gap-2"
      onClick={toggleDemoMode}
    >
      <Beaker className="h-4 w-4" />
      {isDemoMode ? "Exit Demo" : "Demo Mode"}
    </Button>
  );
}

// Separate RouterContent to use context hooks
function RouterContent() {
  const [location] = useLocation();
  const { currentStep, setCurrentStep } = useRfq();
  const { isDemoMode } = useDemoMode();
  
  // Get current step from URL and update context if needed
  const currentPath = location.split('/')[1] || '';
  
  // Use useEffect to update the step based on the URL
  useEffect(() => {
    // Determine step based on URL path
    let urlStep = 1;
    
    switch (currentPath) {
      case '':
      case 'upload':
        urlStep = 1;
        break;
      case 'review':
        urlStep = 2;
        break;
      case 'match':
        urlStep = 3;
        break;
      case 'score':
        urlStep = 4;
        break;
      case 'proposals':
        urlStep = 5;
        break;
      default:
        urlStep = 1;
    }
    
    // Update context if URL step is different
    if (urlStep !== currentStep) {
      setCurrentStep(urlStep);
    }
  }, [location, currentStep, setCurrentStep, currentPath]);
  
  // Only show the header and stepper for the RFQ workflow pages
  const isLandingPage = location === "/";
  
  // Check if we're on the AI hardware platform page
  const isAIHardwarePage = location === "/ai-hardware";
  
  if (isLandingPage) {
    return (
      <>
        <DemoModeToggle />
        <Switch>
          <Route path="/" component={Landing} />
          <Route component={NotFound} />
        </Switch>
      </>
    );
  }
  
  // Special case for AI Hardware Platform and Questionnaire - render without stepper
  const isAIHardwareQuestionnairePage = location === "/ai-hardware-questionnaire";
  
  if (isAIHardwarePage || isAIHardwareQuestionnairePage) {
    return (
      <>
        <DemoModeToggle />
        <Button
          variant="outline"
          size="sm"
          className="fixed top-4 left-4 z-50 flex items-center gap-2"
          onClick={() => window.location.href = "/"}
        >
          Back to Home
        </Button>
        <Switch>
          <Route path="/ai-hardware" component={AIHardwarePlatform} />
          <Route path="/ai-hardware-questionnaire" component={AIHardwareQuestionnaire} />
        </Switch>
      </>
    );
  }
  
  return (
    <Layout currentStep={currentStep}>
      <DemoModeToggle />
      <Switch>
        <Route path="/upload" component={UploadRfq} />
        <Route path="/review/:id" component={ReviewRequirements} />
        <Route path="/match/:id" component={MatchSuppliers} />
        <Route path="/score/:id" component={ScoreResults} />
        <Route path="/proposals/:id" component={SendProposals} />
        <Route component={NotFound} />
      </Switch>
    </Layout>
  );
}

// Main App wrapper that provides context
function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <DemoProvider>
        <RfqProvider>
          <RouterContent />
          <Toaster />
        </RfqProvider>
      </DemoProvider>
    </QueryClientProvider>
  );
}

export default App;
