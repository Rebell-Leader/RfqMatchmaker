import { pgTable, text, serial, integer, json, float, boolean, timestamp } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// User table
export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
});

export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
});

export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;

// RFQ table
export const rfqs = pgTable("rfqs", {
  id: serial("id").primaryKey(),
  title: text("title").notNull(),
  description: text("description"),
  originalContent: text("original_content").notNull(),
  extractedRequirements: json("extracted_requirements").notNull(),
  userId: integer("user_id").references(() => users.id),
  createdAt: timestamp("created_at").defaultNow(),
});

export const insertRfqSchema = createInsertSchema(rfqs).pick({
  title: true,
  description: true,
  originalContent: true,
  extractedRequirements: true,
  userId: true,
});

export type InsertRfq = z.infer<typeof insertRfqSchema>;
export type Rfq = typeof rfqs.$inferSelect;

// Supplier table
export const suppliers = pgTable("suppliers", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  country: text("country"),
  deliveryTime: text("delivery_time"),
  isVerified: boolean("is_verified").default(false),
  logoUrl: text("logo_url"),
});

export const insertSupplierSchema = createInsertSchema(suppliers).pick({
  name: true,
  country: true,
  deliveryTime: true,
  isVerified: true,
  logoUrl: true,
});

export type InsertSupplier = z.infer<typeof insertSupplierSchema>;
export type Supplier = typeof suppliers.$inferSelect;

// Product table
export const products = pgTable("products", {
  id: serial("id").primaryKey(),
  supplierId: integer("supplier_id").references(() => suppliers.id),
  name: text("name").notNull(),
  category: text("category").notNull(),
  specifications: json("specifications").notNull(),
  price: float("price").notNull(),
  warranty: text("warranty"),
});

export const insertProductSchema = createInsertSchema(products).pick({
  supplierId: true,
  name: true,
  category: true,
  specifications: true,
  price: true,
  warranty: true,
});

export type InsertProduct = z.infer<typeof insertProductSchema>;
export type Product = typeof products.$inferSelect;

// Proposal table
export const proposals = pgTable("proposals", {
  id: serial("id").primaryKey(),
  rfqId: integer("rfq_id").references(() => rfqs.id),
  productId: integer("product_id").references(() => products.id),
  score: float("score").notNull(),
  priceScore: float("price_score").notNull(),
  qualityScore: float("quality_score").notNull(),
  deliveryScore: float("delivery_score").notNull(), 
  emailContent: text("email_content"),
  createdAt: timestamp("created_at").defaultNow(),
});

export const insertProposalSchema = createInsertSchema(proposals).pick({
  rfqId: true,
  productId: true,
  score: true,
  priceScore: true,
  qualityScore: true,
  deliveryScore: true,
  emailContent: true,
});

export type InsertProposal = z.infer<typeof insertProposalSchema>;
export type Proposal = typeof proposals.$inferSelect;

// RFQ Extract Types
export type ExtractedRequirement = {
  title: string;
  description?: string;
  categories: string[];
  laptops?: LaptopRequirements;
  monitors?: MonitorRequirements;
  criteria: AwardCriteria;
}

export type LaptopRequirements = {
  quantity: number;
  os: string;
  processor: string;
  memory: string;
  storage: string;
  display: string;
  battery: string;
  durability: string;
  connectivity: string;
  warranty: string;
}

export type MonitorRequirements = {
  quantity: number;
  screenSize: string;
  resolution: string;
  panelTech: string;
  brightness: string;
  contrastRatio: string;
  connectivity: string;
  adjustability: string;
  warranty: string;
}

export type AwardCriteria = {
  price: { weight: number };
  quality: { weight: number };
  delivery: { weight: number };
}

// Supplier Match Types
export type SupplierMatch = {
  supplier: Supplier;
  product: Product;
  matchScore: number;
  matchDetails: {
    price: number;
    quality: number;
    delivery: number;
  };
  totalPrice: number;
}

// Email Template Type
export type EmailTemplate = {
  to: string;
  cc?: string;
  subject: string;
  body: string;
}
