import { createContext, useContext, ReactNode, useState, FC } from "react";
import { ExtractedRequirement, SupplierMatch, EmailTemplate } from "@shared/schema";

interface RfqContextType {
  rfqId: number | null;
  setRfqId: (id: number | null) => void;
  extractedRequirements: ExtractedRequirement | null;
  setExtractedRequirements: (requirements: ExtractedRequirement | null) => void;
  supplierMatches: SupplierMatch[];
  setSupplierMatches: (matches: SupplierMatch[]) => void;
  selectedMatches: SupplierMatch[];
  setSelectedMatches: (matches: SupplierMatch[]) => void;
  emailTemplate: EmailTemplate | null;
  setEmailTemplate: (template: EmailTemplate | null) => void;
}

const RfqContext = createContext<RfqContextType | undefined>(undefined);

export const useRfq = (): RfqContextType => {
  const context = useContext(RfqContext);
  if (!context) {
    throw new Error("useRfq must be used within a RfqProvider");
  }
  return context;
};

interface RfqProviderProps {
  children: ReactNode;
}

export const RfqProvider: FC<RfqProviderProps> = ({ children }) => {
  const [rfqId, setRfqId] = useState<number | null>(null);
  const [extractedRequirements, setExtractedRequirements] = useState<ExtractedRequirement | null>(null);
  const [supplierMatches, setSupplierMatches] = useState<SupplierMatch[]>([]);
  const [selectedMatches, setSelectedMatches] = useState<SupplierMatch[]>([]);
  const [emailTemplate, setEmailTemplate] = useState<EmailTemplate | null>(null);
  
  const value = {
    rfqId,
    setRfqId,
    extractedRequirements,
    setExtractedRequirements,
    supplierMatches,
    setSupplierMatches,
    selectedMatches,
    setSelectedMatches,
    emailTemplate,
    setEmailTemplate
  };
  
  return <RfqContext.Provider value={value}>{children}</RfqContext.Provider>;
};
