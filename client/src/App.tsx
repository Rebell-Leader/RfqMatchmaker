import { Switch, Route, useLocation } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { RfqProvider } from "./context/rfq-context";
import Layout from "./components/layout";
import NotFound from "@/pages/not-found";
import UploadRfq from "@/pages/upload-rfq";
import ReviewRequirements from "@/pages/review-requirements";
import MatchSuppliers from "@/pages/match-suppliers";
import ScoreResults from "@/pages/score-results";
import SendProposals from "@/pages/send-proposals";

function Router() {
  const [location] = useLocation();
  
  // Get current step from URL or default to 1
  const currentPath = location.split('/')[1] || '';
  
  let currentStep = 1;
  
  switch (currentPath) {
    case '':
    case 'upload':
      currentStep = 1;
      break;
    case 'review':
      currentStep = 2;
      break;
    case 'match':
      currentStep = 3;
      break;
    case 'score':
      currentStep = 4;
      break;
    case 'proposals':
      currentStep = 5;
      break;
    default:
      currentStep = 1;
  }
  
  return (
    <Layout currentStep={currentStep}>
      <Switch>
        <Route path="/" component={UploadRfq} />
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

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <RfqProvider>
        <Router />
        <Toaster />
      </RfqProvider>
    </QueryClientProvider>
  );
}

export default App;
