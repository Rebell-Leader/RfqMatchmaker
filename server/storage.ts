import { 
  users, type User, type InsertUser,
  rfqs, type Rfq, type InsertRfq,
  suppliers, type Supplier, type InsertSupplier,
  products, type Product, type InsertProduct,
  proposals, type Proposal, type InsertProposal,
  type ExtractedRequirement, type SupplierMatch, type EmailTemplate
} from "@shared/schema";
import { db } from "./db";
import { eq, and } from "drizzle-orm";

// Storage interface
export interface IStorage {
  // User methods
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  
  // RFQ methods
  createRfq(rfq: InsertRfq): Promise<Rfq>;
  getRfqById(id: number): Promise<Rfq | undefined>;
  getAllRfqs(): Promise<Rfq[]>;
  
  // Supplier methods
  createSupplier(supplier: InsertSupplier): Promise<Supplier>;
  getSupplierById(id: number): Promise<Supplier | undefined>;
  getAllSuppliers(): Promise<Supplier[]>;
  
  // Product methods
  createProduct(product: InsertProduct): Promise<Product>;
  getProductById(id: number): Promise<Product | undefined>;
  getProductsBySupplier(supplierId: number): Promise<Product[]>;
  getProductsByCategory(category: string): Promise<Product[]>;
  
  // Proposal methods
  createProposal(proposal: InsertProposal): Promise<Proposal>;
  getProposalById(id: number): Promise<Proposal | undefined>;
  getProposalsByRfq(rfqId: number): Promise<Proposal[]>;
}

// In-memory storage implementation
export class MemStorage implements IStorage {
  private users: Map<number, User>;
  private rfqs: Map<number, Rfq>;
  private suppliers: Map<number, Supplier>;
  private products: Map<number, Product>;
  private proposals: Map<number, Proposal>;
  
  private userId: number;
  private rfqId: number;
  private supplierId: number;
  private productId: number;
  private proposalId: number;
  
  constructor() {
    this.users = new Map();
    this.rfqs = new Map();
    this.suppliers = new Map();
    this.products = new Map();
    this.proposals = new Map();
    
    this.userId = 1;
    this.rfqId = 1;
    this.supplierId = 1;
    this.productId = 1;
    this.proposalId = 1;
    
    // Initialize with sample data
    this.initializeSampleData();
  }
  
  // User methods
  async getUser(id: number): Promise<User | undefined> {
    return this.users.get(id);
  }
  
  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username === username,
    );
  }
  
  async createUser(insertUser: InsertUser): Promise<User> {
    const id = this.userId++;
    const user: User = { ...insertUser, id };
    this.users.set(id, user);
    return user;
  }
  
  // RFQ methods
  async createRfq(insertRfq: InsertRfq): Promise<Rfq> {
    const id = this.rfqId++;
    const createdAt = new Date();
    const rfq: Rfq = { ...insertRfq, id, createdAt };
    this.rfqs.set(id, rfq);
    return rfq;
  }
  
  async getRfqById(id: number): Promise<Rfq | undefined> {
    return this.rfqs.get(id);
  }
  
  async getAllRfqs(): Promise<Rfq[]> {
    return Array.from(this.rfqs.values());
  }
  
  // Supplier methods
  async createSupplier(insertSupplier: InsertSupplier): Promise<Supplier> {
    const id = this.supplierId++;
    const supplier: Supplier = { ...insertSupplier, id };
    this.suppliers.set(id, supplier);
    return supplier;
  }
  
  async getSupplierById(id: number): Promise<Supplier | undefined> {
    return this.suppliers.get(id);
  }
  
  async getAllSuppliers(): Promise<Supplier[]> {
    return Array.from(this.suppliers.values());
  }
  
  // Product methods
  async createProduct(insertProduct: InsertProduct): Promise<Product> {
    const id = this.productId++;
    const product: Product = { ...insertProduct, id };
    this.products.set(id, product);
    return product;
  }
  
  async getProductById(id: number): Promise<Product | undefined> {
    return this.products.get(id);
  }
  
  async getProductsBySupplier(supplierId: number): Promise<Product[]> {
    return Array.from(this.products.values()).filter(
      (product) => product.supplierId === supplierId,
    );
  }
  
  async getProductsByCategory(category: string): Promise<Product[]> {
    return Array.from(this.products.values()).filter(
      (product) => product.category === category,
    );
  }
  
  // Proposal methods
  async createProposal(insertProposal: InsertProposal): Promise<Proposal> {
    const id = this.proposalId++;
    const createdAt = new Date();
    const proposal: Proposal = { ...insertProposal, id, createdAt };
    this.proposals.set(id, proposal);
    return proposal;
  }
  
  async getProposalById(id: number): Promise<Proposal | undefined> {
    return this.proposals.get(id);
  }
  
  async getProposalsByRfq(rfqId: number): Promise<Proposal[]> {
    return Array.from(this.proposals.values()).filter(
      (proposal) => proposal.rfqId === rfqId,
    );
  }
  
  // Initialize sample data
  private initializeSampleData() {
    // Sample suppliers
    const dellSupplier: InsertSupplier = {
      name: "Dell",
      country: "United States",
      deliveryTime: "15-20 days",
      isVerified: true,
      logoUrl: "https://logo.clearbit.com/dell.com"
    };
    
    const hpSupplier: InsertSupplier = {
      name: "HP",
      country: "United States",
      deliveryTime: "10-15 days",
      isVerified: true,
      logoUrl: "https://logo.clearbit.com/hp.com"
    };
    
    const lenovoSupplier: InsertSupplier = {
      name: "Lenovo",
      country: "China",
      deliveryTime: "20-25 days",
      isVerified: true,
      logoUrl: "https://logo.clearbit.com/lenovo.com"
    };
    
    // Create suppliers
    const dell = this.createSupplier(dellSupplier);
    const hp = this.createSupplier(hpSupplier);
    const lenovo = this.createSupplier(lenovoSupplier);
    
    // Sample products
    const createLaptopProduct = (supplier: Promise<Supplier>, name: string, price: number, specs: any, warranty: string) => {
      supplier.then(s => {
        const product: InsertProduct = {
          supplierId: s.id,
          name,
          category: "Laptops",
          specifications: specs,
          price,
          warranty
        };
        this.createProduct(product);
      });
    };
    
    const createMonitorProduct = (supplier: Promise<Supplier>, name: string, price: number, specs: any, warranty: string) => {
      supplier.then(s => {
        const product: InsertProduct = {
          supplierId: s.id,
          name,
          category: "Monitors",
          specifications: specs,
          price,
          warranty
        };
        this.createProduct(product);
      });
    };
    
    // Laptop products
    createLaptopProduct(
      dell,
      "Dell Latitude 5350",
      899,
      {
        processor: "Intel® Core™ Ultra i5-125U (12 cores, up to 4.3 GHz Turbo)",
        memory: "16 GB LPDDR5x RAM",
        storage: "256 GB PCIe Gen4 NVMe SSD",
        display: "FHD (1920x1080), IPS, non-touch, brightness: 250 nits",
        os: "Windows 11 Pro Education",
        battery: "8 hours",
        connectivity: "Wi-Fi 6, Bluetooth, HDMI port, USB Type-C",
        durability: "MIL-STD 810G certified"
      },
      "1 year basic onsite"
    );
    
    createLaptopProduct(
      hp,
      "HP Fortis Laptop",
      949,
      {
        processor: "Intel® Core™ i5-1235U (12th Gen)",
        memory: "16 GB LPDDR5 RAM",
        storage: "256 GB PCIe NVMe SSD",
        display: "FHD (1920x1080), IPS, non-touch, brightness: 250 nits",
        os: "Windows 11 Pro Education",
        battery: "10 hours",
        connectivity: "Wi-Fi 6E, Bluetooth, HDMI port, USB Type-C",
        durability: "MIL-STD testing for rugged use"
      },
      "3 years onsite"
    );
    
    createLaptopProduct(
      lenovo,
      "Lenovo ThinkPad",
      879,
      {
        processor: "Intel® Core™ i5-1240P (12th Gen)",
        memory: "16 GB LPDDR5 RAM",
        storage: "256 GB PCIe NVMe SSD",
        display: "FHD (1920x1080), IPS, non-touch, brightness: 300 nits",
        os: "Windows 11 Pro Education",
        battery: "12 hours",
        connectivity: "Wi-Fi 6, Bluetooth, HDMI port, USB Type-C",
        durability: "MIL-STD 810H certified"
      },
      "2 years onsite"
    );
    
    // Monitor products
    createMonitorProduct(
      dell,
      "Dell E2318H Monitor",
      199,
      {
        screenSize: "23 inches diagonal",
        resolution: "FHD (1920x1080)",
        panelTech: "IPS with anti-glare coating",
        brightness: "250 cd/m²",
        contrastRatio: "1000:1 static",
        connectivity: "VGA and DisplayPort",
        adjustability: "Tilt only"
      },
      "3 years standard"
    );
    
    createMonitorProduct(
      hp,
      "HP P24v G5 Monitor",
      189,
      {
        screenSize: "23.8 inches diagonal",
        resolution: "FHD (1920x1080)",
        panelTech: "IPS with anti-glare coating",
        brightness: "250 nits",
        contrastRatio: "1000:1 static",
        connectivity: "HDMI and VGA",
        adjustability: "Tilt option included"
      },
      "1 year standard"
    );
    
    createMonitorProduct(
      lenovo,
      "Lenovo ThinkVision T24m-20 Monitor",
      219,
      {
        screenSize: "23.8 inches diagonal with IPS technology",
        resolution: "FHD (1920x1080)",
        panelTech: "IPS with anti-glare coating",
        brightness: "250 cd/m²",
        contrastRatio: "1000:1 static",
        connectivity: "HDMI and DisplayPort",
        adjustability: "Height, tilt, swivel, and pivot"
      },
      "3 years onsite"
    );
  }
}

// DatabaseStorage implementation using Drizzle ORM
export class DatabaseStorage implements IStorage {
  async getUser(id: number): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.id, id));
    return user || undefined;
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.username, username));
    return user || undefined;
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const [user] = await db
      .insert(users)
      .values({
        ...insertUser,
        company: insertUser.company ?? null,
        country: insertUser.country ?? null,
        industry: insertUser.industry ?? null
      })
      .returning();
    return user;
  }

  async createRfq(insertRfq: InsertRfq): Promise<Rfq> {
    const [rfq] = await db
      .insert(rfqs)
      .values({
        ...insertRfq,
        description: insertRfq.description ?? null,
        userId: insertRfq.userId ?? null,
        useCase: insertRfq.useCase ?? null,
        budget: insertRfq.budget ?? null,
        deadline: insertRfq.deadline ?? null
      })
      .returning();
    return rfq;
  }

  async getRfqById(id: number): Promise<Rfq | undefined> {
    const [rfq] = await db.select().from(rfqs).where(eq(rfqs.id, id));
    return rfq || undefined;
  }

  async getAllRfqs(): Promise<Rfq[]> {
    return await db.select().from(rfqs);
  }

  async createSupplier(insertSupplier: InsertSupplier): Promise<Supplier> {
    const [supplier] = await db
      .insert(suppliers)
      .values({
        ...insertSupplier,
        country: insertSupplier.country ?? null,
        description: insertSupplier.description ?? null,
        deliveryTime: insertSupplier.deliveryTime ?? null,
        isVerified: insertSupplier.isVerified ?? false,
        logoUrl: insertSupplier.logoUrl ?? null,
        website: insertSupplier.website ?? null,
        contactEmail: insertSupplier.contactEmail ?? null,
        contactPhone: insertSupplier.contactPhone ?? null,
        complianceStatus: insertSupplier.complianceStatus ?? null,
        stockAvailability: insertSupplier.stockAvailability ?? null,
        leadTime: insertSupplier.leadTime ?? null,
        minOrderQuantity: insertSupplier.minOrderQuantity ?? null,
        dataSourceUrl: insertSupplier.dataSourceUrl ?? null,
        lastUpdated: new Date()
      })
      .returning();
    return supplier;
  }

  async getSupplierById(id: number): Promise<Supplier | undefined> {
    const [supplier] = await db.select().from(suppliers).where(eq(suppliers.id, id));
    return supplier || undefined;
  }

  async getAllSuppliers(): Promise<Supplier[]> {
    return await db.select().from(suppliers);
  }

  async createProduct(insertProduct: InsertProduct): Promise<Product> {
    const [product] = await db
      .insert(products)
      .values({
        ...insertProduct,
        type: insertProduct.type ?? null,
        manufacturer: insertProduct.manufacturer ?? null,
        model: insertProduct.model ?? null,
        architecture: insertProduct.architecture ?? null,
        warranty: insertProduct.warranty ?? null,
        leadTime: insertProduct.leadTime ?? null,
        inStock: insertProduct.inStock ?? true,
        dataSourceUrl: insertProduct.dataSourceUrl ?? null,
        quantityAvailable: insertProduct.quantityAvailable ?? null,
        lastPriceUpdate: new Date()
      })
      .returning();
    return product;
  }

  async getProductById(id: number): Promise<Product | undefined> {
    const [product] = await db.select().from(products).where(eq(products.id, id));
    return product || undefined;
  }

  async getProductsBySupplier(supplierId: number): Promise<Product[]> {
    return await db.select().from(products).where(eq(products.supplierId, supplierId));
  }

  async getProductsByCategory(category: string): Promise<Product[]> {
    return await db.select().from(products).where(eq(products.category, category));
  }

  async createProposal(insertProposal: InsertProposal): Promise<Proposal> {
    const [proposal] = await db
      .insert(proposals)
      .values({
        ...insertProposal,
        rfqId: insertProposal.rfqId ?? null,
        productId: insertProposal.productId ?? null,
        emailContent: insertProposal.emailContent ?? null,
        alternatives: insertProposal.alternatives ?? null,
        estimatedDeliveryDate: insertProposal.estimatedDeliveryDate ?? null,
        pricingNotes: insertProposal.pricingNotes ?? null
      })
      .returning();
    return proposal;
  }

  async getProposalById(id: number): Promise<Proposal | undefined> {
    const [proposal] = await db.select().from(proposals).where(eq(proposals.id, id));
    return proposal || undefined;
  }

  async getProposalsByRfq(rfqId: number): Promise<Proposal[]> {
    return await db.select().from(proposals).where(eq(proposals.rfqId, rfqId));
  }
}

// Use the database storage implementation
export const storage = new DatabaseStorage();
