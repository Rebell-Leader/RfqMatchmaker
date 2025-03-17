import { pgTable, text, serial, integer, json, float, boolean, timestamp } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// User table with additions for AI hardware sourcing
export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
  company: text("company"),
  country: text("country"),
  industry: text("industry"),
  complianceRestrictions: json("compliance_restrictions"),
});

export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
  company: true,
  country: true,
  industry: true,
  complianceRestrictions: true,
});

export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;

// RFQ table for AI hardware requirements
export const rfqs = pgTable("rfqs", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  description: text("description"),
  originalContent: text("original_content").notNull(),
  extractedRequirements: json("extracted_requirements").notNull(),
  userId: integer("user_id").references(() => users.id),
  createdAt: timestamp("created_at").defaultNow(),
  useCase: text("use_case"),
  budget: float("budget"),
  deadline: timestamp("deadline"),
  complianceRequirements: json("compliance_requirements"),
});

export const insertRfqSchema = createInsertSchema(rfqs).pick({
  title: true,
  description: true,
  originalContent: true,
  extractedRequirements: true,
  userId: true,
  useCase: true,
  budget: true,
  deadline: true,
  complianceRequirements: true,
});

export type InsertRfq = z.infer<typeof insertRfqSchema>;
export type Rfq = typeof rfqs.$inferSelect;

// Supplier table enhanced for hardware vendors
export const suppliers = pgTable("suppliers", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  country: text("country"),
  deliveryTime: text("delivery_time"),
  isVerified: boolean("is_verified").default(false),
  logoUrl: text("logo_url"),
  website: text("website"),
  contactEmail: text("contact_email"),
  contactPhone: text("contact_phone"),
  description: text("description"),
  complianceStatus: text("compliance_status"),
  supportedRegions: json("supported_regions"),
  stockAvailability: text("stock_availability"),
  leadTime: integer("lead_time"), // in days
  minOrderQuantity: integer("min_order_quantity"),
  dataSourceUrl: text("data_source_url"), // URL where supplier info was scraped from
  lastUpdated: timestamp("last_updated").defaultNow(),
});

export const insertSupplierSchema = createInsertSchema(suppliers).pick({
  name: true,
  country: true,
  deliveryTime: true,
  isVerified: true,
  logoUrl: true,
  website: true,
  contactEmail: true,
  contactPhone: true,
  description: true,
  complianceStatus: true,
  supportedRegions: true,
  stockAvailability: true,
  leadTime: true,
  minOrderQuantity: true,
  dataSourceUrl: true,
});

export type InsertSupplier = z.infer<typeof insertSupplierSchema>;
export type Supplier = typeof suppliers.$inferSelect;

// Product table for AI hardware specifics
export const products = pgTable("products", {
  id: serial("id").primaryKey(),
  supplierId: integer("supplier_id").references(() => suppliers.id),
  name: text("name").notNull(),
  category: text("category").notNull(), // e.g., "GPU", "AI Accelerator"
  type: text("type"), // e.g., "GPU", "TPU", "ASIC"
  manufacturer: text("manufacturer"), // e.g., "NVIDIA", "AMD", "Google"
  model: text("model"), // e.g., "A100", "H100"
  specifications: json("specifications").notNull(),
  computeSpecs: json("compute_specs"), // Performance details
  memorySpecs: json("memory_specs"), // Memory specifications
  powerConsumption: json("power_consumption"), // Power requirements
  price: float("price").notNull(),
  warranty: text("warranty"),
  architecture: text("architecture"), // e.g., "Ampere", "Hopper"
  supportedFrameworks: json("supported_frameworks"), // e.g., TensorFlow, PyTorch
  complianceInfo: json("compliance_info"), // Export restrictions, certifications
  benchmarks: json("benchmarks"), // Performance benchmarks
  inStock: boolean("in_stock").default(true),
  leadTime: integer("lead_time"), // in days
  quantityAvailable: integer("quantity_available"),
  lastPriceUpdate: timestamp("last_price_update").defaultNow(),
  dataSourceUrl: text("data_source_url"), // URL where product info was scraped from
});

export const insertProductSchema = createInsertSchema(products).pick({
  supplierId: true,
  name: true,
  category: true,
  type: true,
  manufacturer: true,
  model: true,
  specifications: true,
  computeSpecs: true,
  memorySpecs: true,
  powerConsumption: true,
  price: true,
  warranty: true,
  architecture: true,
  supportedFrameworks: true,
  complianceInfo: true,
  benchmarks: true,
  inStock: true,
  leadTime: true,
  quantityAvailable: true,
  dataSourceUrl: true,
});

export type InsertProduct = z.infer<typeof insertProductSchema>;
export type Product = typeof products.$inferSelect;

// Proposal table with AI hardware specific scoring
export const proposals = pgTable("proposals", {
  id: serial("id").primaryKey(),
  rfqId: integer("rfq_id").references(() => rfqs.id),
  productId: integer("product_id").references(() => products.id),
  score: float("score").notNull(),
  priceScore: float("price_score").notNull(),
  performanceScore: float("performance_score").notNull(),
  compatibilityScore: float("compatibility_score").notNull(),
  availabilityScore: float("availability_score").notNull(),
  complianceScore: float("compliance_score").notNull(),
  emailContent: text("email_content"),
  createdAt: timestamp("created_at").defaultNow(),
  alternatives: json("alternatives"), // Alternative product suggestions
  estimatedDeliveryDate: timestamp("estimated_delivery_date"),
  pricingNotes: text("pricing_notes"),
});

export const insertProposalSchema = createInsertSchema(proposals).pick({
  rfqId: true,
  productId: true,
  score: true,
  priceScore: true,
  performanceScore: true,
  compatibilityScore: true,
  availabilityScore: true,
  complianceScore: true,
  emailContent: true,
  alternatives: true,
  estimatedDeliveryDate: true,
  pricingNotes: true,
});

export type InsertProposal = z.infer<typeof insertProposalSchema>;
export type Proposal = typeof proposals.$inferSelect;

// Type definitions for AI hardware specifications

// Compute Performance Specifications
export type ComputeSpecs = {
  tensorFlops?: number; // in TFLOPS
  fp32Performance?: number; // in TFLOPS
  fp16Performance?: number; // in TFLOPS
  int8Performance?: number; // in TOPS
  tensorCores?: number;
  cudaCores?: number;
  clockSpeed?: number; // in MHz
};

// Memory Specifications
export type MemorySpecs = {
  capacity: number; // in GB
  type: string; // e.g., "HBM2", "GDDR6X"
  bandwidth: number; // in GB/s
  busWidth: number; // in bits
  eccSupport?: boolean;
};

// Power Specifications
export type PowerSpecs = {
  tdp: number; // in watts
  requiredPsu?: number; // in watts
  powerConnectors?: string;
};

// Compliance Information
export type ComplianceInfo = {
  exportRestrictions?: string[];
  certifications?: string[];
  restrictedCountries?: string[];
};

// Benchmark Results
export type Benchmarks = {
  mlTraining?: Record<string, number>; // model name -> performance score
  llmInference?: Record<string, number>; // model name -> tokens per second
  computerVision?: Record<string, number>; // task -> FPS or accuracy
};

// Alternative Product Suggestions
export type AlternativeProducts = {
  similarPerformance?: number[]; // product IDs
  lowerCost?: number[]; // product IDs
  fasterDelivery?: number[]; // product IDs
  betterCompliance?: number[]; // product IDs
};

// RFQ Extract Types for AI Hardware
export type ExtractedRequirement = {
  title: string;
  description?: string;
  categories: string[];
  aiHardware?: AIHardwareRequirements;
  gpuRequirements?: GPURequirements;
  systemRequirements?: SystemRequirements;
  complianceRequirements?: ComplianceRequirements;
  criteria: AwardCriteria;
  useCase?: string;
  performanceTargets?: PerformanceTargets;
};

export type AIHardwareRequirements = {
  type: string; // e.g., "GPU", "AI Accelerator", "TPU"
  quantity: number;
  preferredManufacturers?: string[];
  minMemory?: number; // in GB
  minComputePower?: number; // in TFLOPS/TOPS
  powerConstraints?: number; // max TDP in watts
  frameworks?: string[]; // required frameworks support
  connectivity?: string[];
  formFactor?: string;
  coolingRequirements?: string;
};

export type GPURequirements = {
  quantity: number;
  model?: string;
  minCudaCores?: number;
  minTensorCores?: number;
  minMemoryBandwidth?: number; // in GB/s
  architecture?: string;
};

export type SystemRequirements = {
  rackSpace?: string;
  powerAvailability?: number; // in watts
  coolingCapacity?: string;
  networkingRequirements?: string;
  operatingSystem?: string;
};

export type ComplianceRequirements = {
  allowedCountries?: string[];
  requiredCertifications?: string[];
  dataPrivacyRequirements?: string[];
  exportComplianceNeeded?: boolean;
};

export type PerformanceTargets = {
  trainingTime?: {
    model: string;
    dataset: string;
    targetTime: number; // in hours
  };
  inferenceSpeed?: {
    model: string;
    batchSize: number;
    targetThroughput: number; // e.g., tokens/sec, images/sec
  };
};

export type AwardCriteria = {
  price: { weight: number };
  performance: { weight: number };
  availability: { weight: number };
  compliance: { weight: number };
  support: { weight: number };
};

// Supplier Match Types enhanced for AI hardware
export type SupplierMatch = {
  supplier: Supplier;
  product: Product;
  matchScore: number;
  matchDetails: {
    price: number;
    performance: number;
    compatibility: number;
    availability: number;
    compliance: number;
  };
  totalPrice: number;
  estimatedDelivery: string;
  complianceNotes?: string;
  alternatives?: {
    similarPerformance?: Product;
    lowerCost?: Product;
    fasterDelivery?: Product;
  };
};

// Email Template Type
export type EmailTemplate = {
  to: string;
  cc?: string;
  subject: string;
  body: string;
};
