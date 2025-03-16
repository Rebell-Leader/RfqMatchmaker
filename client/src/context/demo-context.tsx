import React, { createContext, useState, useContext, ReactNode } from 'react';
import { DEMO_MODE, DEMO_RFQ, DEMO_SUPPLIER_MATCHES, DEMO_EMAIL_PROPOSAL } from '@/lib/constants';

interface DemoContextType {
  isDemoMode: boolean;
  toggleDemoMode: () => void;
  demoRfq: typeof DEMO_RFQ;
  demoSupplierMatches: typeof DEMO_SUPPLIER_MATCHES;
  demoEmailProposal: typeof DEMO_EMAIL_PROPOSAL;
  simulateProcessing: (callback: () => void) => void;
}

const DemoContext = createContext<DemoContextType | undefined>(undefined);

export const useDemoMode = (): DemoContextType => {
  const context = useContext(DemoContext);
  if (!context) {
    throw new Error('useDemoMode must be used within a DemoProvider');
  }
  return context;
};

interface DemoProviderProps {
  children: ReactNode;
}

export const DemoProvider: React.FC<DemoProviderProps> = ({ children }) => {
  const [isDemoMode, setIsDemoMode] = useState<boolean>(DEMO_MODE.enabled);

  // Toggle demo mode on/off
  const toggleDemoMode = () => {
    setIsDemoMode(prev => !prev);
  };

  // Simulate processing delay for demo mode to mimic real processing
  const simulateProcessing = (callback: () => void) => {
    setTimeout(callback, DEMO_MODE.processingTime);
  };

  const value = {
    isDemoMode,
    toggleDemoMode,
    demoRfq: DEMO_RFQ,
    demoSupplierMatches: DEMO_SUPPLIER_MATCHES,
    demoEmailProposal: DEMO_EMAIL_PROPOSAL,
    simulateProcessing
  };

  return <DemoContext.Provider value={value}>{children}</DemoContext.Provider>;
};