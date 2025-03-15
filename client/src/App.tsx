import { Switch, Route, useLocation } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { RfqProvider, useRfq } from "./context/rfq-context";
import Layout from "./components/layout";
import NotFound from "@/pages/not-found";
import Landing from "@/pages/landing";
import UploadRfq from "@/pages/upload-rfq";
import ReviewRequirements from "@/pages/review-requirements";
import MatchSuppliers from "@/pages/match-suppliers";
import ScoreResults from "@/pages/score-results";
import SendProposals from "@/pages/send-proposals";

// Separate RouterContent to use context hooks
function RouterContent() {
  const [location] = useLocation();
  const { currentStep, setCurrentStep } = useRfq();
  
  // Get current step from URL and update context if needed
  const currentPath = location.split('/')[1] || '';
  
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
  
  // Only show the header and stepper for the RFQ workflow pages
  const isLandingPage = location === "/";
  
  if (isLandingPage) {
    return (
      <>
        <Switch>
          <Route path="/" component={Landing} />
          <Route component={NotFound} />
        </Switch>
      </>
    );
  }
  
  return (
    <Layout currentStep={currentStep}>
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
      <RfqProvider>
        <RouterContent />
        <Toaster />
      </RfqProvider>
    </QueryClientProvider>
  );
}

export default App;
