
<old_str>import { 
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
    const user: User = { 
      ...insertUser, 
      id,
      company: insertUser.company ?? null,
      country: insertUser.country ?? null,
      industry: insertUser.industry ?? null,
      complianceRestrictions: insertUser.complianceRestrictions ?? null
    };
    this.users.set(id, user);
    return user;
  }
  
  // RFQ methods
  async createRfq(insertRfq: InsertRfq): Promise<Rfq> {
    const id = this.rfqId++;
    const createdAt = new Date();
    const rfq: Rfq = { 
      ...insertRfq, 
      id, 
      createdAt,
      description: insertRfq.description ?? null,
      userId: insertRfq.userId ?? null,
      useCase: insertRfq.useCase ?? null,
      budget: insertRfq.budget ?? null,
      deadline: insertRfq.deadline ?? null,
      complianceRequirements: insertRfq.complianceRequirements ?? null
    };
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
    const supplier: Supplier = { 
      ...insertSupplier, 
      id,
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
      supportedRegions: insertSupplier.supportedRegions ?? null,
      lastUpdated: new Date()
    };
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
    
    // Create a new product object with only the fields defined in the schema
    // First establish required fields that can't be null
    const product: Product = {
      id,
      name: insertProduct.name,
      category: insertProduct.category,
      specifications: insertProduct.specifications,
      price: insertProduct.price,
      
      // Optional fields with null fallbacks
      supplierId: insertProduct.supplierId ?? null,
      type: insertProduct.type ?? null,
      manufacturer: insertProduct.manufacturer ?? null,
      model: insertProduct.model ?? null,
      architecture: insertProduct.architecture ?? null,
      computeSpecs: insertProduct.computeSpecs ?? null,
      memorySpecs: insertProduct.memorySpecs ?? null,
      powerConsumption: insertProduct.powerConsumption ?? null,
      supportedFrameworks: insertProduct.supportedFrameworks ?? null,
      complianceInfo: insertProduct.complianceInfo ?? null,
      benchmarks: insertProduct.benchmarks ?? null,
      inStock: insertProduct.inStock ?? true,
      leadTime: insertProduct.leadTime ?? null,
      quantityAvailable: insertProduct.quantityAvailable ?? null,
      warranty: insertProduct.warranty ?? null,
      lastPriceUpdate: new Date(),
      dataSourceUrl: insertProduct.dataSourceUrl ?? null,
    };
    
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
    
    // Make sure to properly define all fields according to the schema
    const proposal: Proposal = { 
      ...insertProposal, 
      id, 
      createdAt,
      rfqId: insertProposal.rfqId ?? null,
      productId: insertProposal.productId ?? null,
      score: insertProposal.score ?? 0,
      priceScore: insertProposal.priceScore ?? 0,
      performanceScore: insertProposal.performanceScore ?? 0,
      compatibilityScore: insertProposal.compatibilityScore ?? 0,
      availabilityScore: insertProposal.availabilityScore ?? 0,
      complianceScore: insertProposal.complianceScore ?? 0,
      emailContent: insertProposal.emailContent ?? null,
      alternatives: insertProposal.alternatives ?? null,
      estimatedDeliveryDate: insertProposal.estimatedDeliveryDate ?? null,
      pricingNotes: insertProposal.pricingNotes ?? null
    };
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
      logoUrl: "https://logo.clearbit.com/dell.com",
      description: "Global technology provider with solutions for businesses of all sizes",
      website: "https://www.dell.com",
      contactEmail: "sales@dell.com",
      contactPhone: "+1-800-999-3355"
    };
    
    const hpSupplier: InsertSupplier = {
      name: "HP",
      country: "United States",
      deliveryTime: "10-15 days",
      isVerified: true,
      logoUrl: "https://logo.clearbit.com/hp.com",
      description: "Leading provider of computers, printers, and IT solutions",
      website: "https://www.hp.com",
      contactEmail: "sales@hp.com",
      contactPhone: "+1-800-474-6836"
    };
    
    const lenovoSupplier: InsertSupplier = {
      name: "Lenovo",
      country: "China",
      deliveryTime: "20-25 days",
      isVerified: true,
      logoUrl: "https://logo.clearbit.com/lenovo.com",
      description: "Global technology company specializing in PCs and smart devices",
      website: "https://www.lenovo.com",
      contactEmail: "sales@lenovo.com",
      contactPhone: "+1-855-253-6686"
    };
    
    const nvidiaSupplier: InsertSupplier = {
      name: "NVIDIA",
      country: "United States",
      deliveryTime: "3-4 weeks",
      isVerified: true,
      logoUrl: "https://logo.clearbit.com/nvidia.com",
      description: "Leader in AI computing and GPUs for deep learning and scientific computing",
      website: "https://www.nvidia.com",
      contactEmail: "enterprise-sales@nvidia.com",
      contactPhone: "+1-408-486-2000"
    };
    
    const amdSupplier: InsertSupplier = {
      name: "AMD",
      country: "United States",
      deliveryTime: "2-3 weeks",
      isVerified: true,
      logoUrl: "https://logo.clearbit.com/amd.com",
      description: "High-performance computing, graphics, and visualization technologies",
      website: "https://www.amd.com",
      contactEmail: "enterprise-sales@amd.com",
      contactPhone: "+1-877-284-1566"
    };
    
    const intelSupplier: InsertSupplier = {
      name: "Intel",
      country: "United States",
      deliveryTime: "2-3 weeks",
      isVerified: true,
      logoUrl: "https://logo.clearbit.com/intel.com",
      description: "World leader in computing innovation and AI accelerators",
      website: "https://www.intel.com",
      contactEmail: "enterprise-sales@intel.com",
      contactPhone: "+1-408-765-8080"
    };
    
    // Create suppliers
    const dell = this.createSupplier(dellSupplier);
    const hp = this.createSupplier(hpSupplier);
    const lenovo = this.createSupplier(lenovoSupplier);
    const nvidia = this.createSupplier(nvidiaSupplier);
    const amd = this.createSupplier(amdSupplier);
    const intel = this.createSupplier(intelSupplier);
    
    // Sample products helpers
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
    
    const createAIHardwareProduct = (supplier: Promise<Supplier>, name: string, price: number, specs: any, warranty: string) => {
      supplier.then(s => {
        const product: InsertProduct = {
          supplierId: s.id,
          name,
          category: "AI Hardware",
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
    
    // AI Hardware products (GPUs & Accelerators)
    createAIHardwareProduct(
      nvidia,
      "NVIDIA A100 GPU",
      10000,
      {
        model: "A100-SXM4-80GB",
        manufacturer: "NVIDIA",
        description: "High-performance GPU for AI workloads with 80GB HBM2e memory",
        computeSpecs: { 
          tensorFlops: 312,
          fp32Performance: 19.5,
          fp16Performance: 312,
          tensorCores: 432,
          cudaCores: 6912,
          clockSpeed: 1410
        },
        memorySpecs: { 
          capacity: 80, 
          type: "HBM2e", 
          bandwidth: 2039, 
          busWidth: 5120,
          eccSupport: true
        },
        powerSpecs: { 
          tdp: 400, 
          requiredPsu: 1200,
          powerConnectors: "Direct SXM4 connection"
        },
        thermalSpecs: {
          cooling: "Passive + Active",
          maxTemp: 85
        },
        connectivity: ["NVLink", "PCIe 4.0"],
        supportedFrameworks: ["PyTorch", "TensorFlow", "CUDA", "JAX", "ONNX"],
        formFactor: "SXM4",
        complianceInfo: {
          exportRestrictions: ["RU", "CN"],
          certifications: ["FCC", "CE", "RoHS"]
        },
        benchmarks: {
          mlTraining: { "ResNet50": 32550, "BERT-Large": 8643 },
          llmInference: { "GPT-3": 180, "T5": 320 }
        },
        availability: "2-4 weeks",
        releaseDate: "2020-05-14",
        inStock: true
      },
      "3 years limited"
    );
    
    createAIHardwareProduct(
      nvidia,
      "NVIDIA H100 GPU",
      30000,
      {
        model: "H100-SXM5-80GB",
        manufacturer: "NVIDIA",
        description: "Next-generation GPU for AI computing with 80GB HBM3 memory",
        computeSpecs: { 
          tensorFlops: 989,
          fp32Performance: 51,
          fp16Performance: 989,
          tensorCores: 528,
          cudaCores: 14592,
          clockSpeed: 1860
        },
        memorySpecs: { 
          capacity: 80, 
          type: "HBM3", 
          bandwidth: 3350, 
          busWidth: 5120,
          eccSupport: true
        },
        powerSpecs: { 
          tdp: 700, 
          requiredPsu: 1800,
          powerConnectors: "Direct SXM5 connection"
        },
        thermalSpecs: {
          cooling: "Active",
          maxTemp: 90
        },
        connectivity: ["NVLink 4.0", "PCIe 5.0"],
        supportedFrameworks: ["PyTorch", "TensorFlow", "CUDA", "JAX", "ONNX", "Triton"],
        formFactor: "SXM5",
        complianceInfo: {
          exportRestrictions: ["RU", "CN", "IR"],
          certifications: ["FCC", "CE", "RoHS", "UL"]
        },
        benchmarks: {
          mlTraining: { "ResNet50": 98175, "BERT-Large": 25703 },
          llmInference: { "GPT-3": 510, "T5": 980 }
        },
        availability: "4-6 weeks",
        releaseDate: "2022-03-22",
        inStock: true
      },
      "3 years limited"
    );
    
    createAIHardwareProduct(
      nvidia,
      "NVIDIA L40S GPU",
      12000,
      {
        model: "L40S-48GB",
        manufacturer: "NVIDIA",
        description: "Data center GPU for AI inference and graphics with 48GB GDDR6 memory",
        computeSpecs: { 
          tensorFlops: 733,
          fp32Performance: 91.6,
          fp16Performance: 733,
          tensorCores: 304,
          cudaCores: 18176,
          clockSpeed: 1620
        },
        memorySpecs: { 
          capacity: 48, 
          type: "GDDR6", 
          bandwidth: 864, 
          busWidth: 384,
          eccSupport: true
        },
        powerSpecs: { 
          tdp: 300, 
          requiredPsu: 800,
          powerConnectors: "8-pin + 6-pin PCIe"
        },
        thermalSpecs: {
          cooling: "Active",
          maxTemp: 85
        },
        connectivity: ["PCIe 4.0"],
        supportedFrameworks: ["PyTorch", "TensorFlow", "CUDA", "JAX", "ONNX"],
        formFactor: "Full-height, full-length, dual slot",
        complianceInfo: {
          exportRestrictions: ["RU", "CN"],
          certifications: ["FCC", "CE", "RoHS"]
        },
        benchmarks: {
          mlTraining: { "ResNet50": 29000, "BERT-Large": 7500 },
          llmInference: { "GPT-3": 220, "T5": 400 }
        },
        availability: "2-3 weeks",
        releaseDate: "2023-04-18",
        inStock: true
      },
      "3 years limited"
    );
    
    createAIHardwareProduct(
      amd,
      "AMD Instinct MI250X",
      12500,
      {
        model: "MI250X-128GB",
        manufacturer: "AMD",
        description: "High-performance accelerator for HPC and AI workloads with 128GB HBM2e memory",
        computeSpecs: { 
          tensorFlops: 383,
          fp32Performance: 47.9,
          fp16Performance: 383,
          tensorCores: 0,
          cudaCores: 0, // Not CUDA
          clockSpeed: 1700
        },
        memorySpecs: { 
          capacity: 128, 
          type: "HBM2e", 
          bandwidth: 3276, 
          busWidth: 8192,
          eccSupport: true
        },
        powerSpecs: { 
          tdp: 560, 
          requiredPsu: 1500,
          powerConnectors: "OAM socket"
        },
        thermalSpecs: {
          cooling: "Active",
          maxTemp: 85
        },
        connectivity: ["Infinity Fabric", "PCIe 4.0"],
        supportedFrameworks: ["ROCm", "PyTorch", "TensorFlow"],
        formFactor: "OAM",
        complianceInfo: {
          exportRestrictions: ["RU", "CN", "IR"],
          certifications: ["FCC", "CE", "RoHS"]
        },
        benchmarks: {
          mlTraining: { "ResNet50": 25000, "BERT-Large": 6650 },
          llmInference: { "GPT-3": 140, "T5": 260 }
        },
        availability: "3-4 weeks",
        releaseDate: "2021-11-08",
        inStock: true
      },
      "3 years limited"
    );
    
    createAIHardwareProduct(
      amd,
      "AMD Instinct MI210",
      6000,
      {
        model: "MI210-64GB",
        manufacturer: "AMD",
        description: "Mid-range AI accelerator with 64GB HBM2e memory",
        computeSpecs: { 
          tensorFlops: 181,
          fp32Performance: 22.6,
          fp16Performance: 181,
          tensorCores: 0,
          cudaCores: 0, // Not CUDA
          clockSpeed: 1650
        },
        memorySpecs: { 
          capacity: 64, 
          type: "HBM2e", 
          bandwidth: 1638, 
          busWidth: 4096,
          eccSupport: true
        },
        powerSpecs: { 
          tdp: 300, 
          requiredPsu: 850,
          powerConnectors: "Dual 8-pin PCIe"
        },
        thermalSpecs: {
          cooling: "Active",
          maxTemp: 85
        },
        connectivity: ["PCIe 4.0"],
        supportedFrameworks: ["ROCm", "PyTorch", "TensorFlow"],
        formFactor: "Full-height, full-length, dual slot",
        complianceInfo: {
          exportRestrictions: ["RU", "CN"],
          certifications: ["FCC", "CE", "RoHS"]
        },
        benchmarks: {
          mlTraining: { "ResNet50": 14000, "BERT-Large": 3750 },
          llmInference: { "GPT-3": 90, "T5": 170 }
        },
        availability: "2-3 weeks",
        releaseDate: "2022-03-15",
        inStock: true
      },
      "3 years limited"
    );
    
    createAIHardwareProduct(
      intel,
      "Intel Gaudi 2",
      8500,
      {
        model: "Gaudi2-24HBM2E",
        manufacturer: "Intel",
        description: "AI accelerator optimized for deep learning training with 96GB HBM2e memory",
        computeSpecs: { 
          tensorFlops: 624,
          fp32Performance: 52,
          fp16Performance: 208,
          tensorCores: 24,
          cudaCores: 0, // Not CUDA
          clockSpeed: 1600
        },
        memorySpecs: { 
          capacity: 96, 
          type: "HBM2e", 
          bandwidth: 2450, 
          busWidth: 6144,
          eccSupport: true
        },
        powerSpecs: { 
          tdp: 600, 
          requiredPsu: 1500,
          powerConnectors: "OAM socket"
        },
        thermalSpecs: {
          cooling: "Active",
          maxTemp: 85
        },
        connectivity: ["Ethernet 100GbE RoCE", "PCIe 5.0"],
        supportedFrameworks: ["PyTorch", "TensorFlow", "OpenVINO"],
        formFactor: "OAM",
        complianceInfo: {
          exportRestrictions: ["RU", "CN", "IR"],
          certifications: ["FCC", "CE", "RoHS"]
        },
        benchmarks: {
          mlTraining: { "ResNet50": 27000, "BERT-Large": 7200 },
          llmInference: { "GPT-3": 160, "T5": 290 }
        },
        availability: "3-4 weeks",
        releaseDate: "2022-05-10",
        inStock: true
      },
      "3 years limited"
    );
    
    createAIHardwareProduct(
      nvidia,
      "NVIDIA RTX 6000 Ada Generation",
      7500,
      {
        model: "RTX 6000 Ada-48GB",
        manufacturer: "NVIDIA",
        description: "Professional workstation GPU for AI development with 48GB GDDR6 memory",
        computeSpecs: { 
          tensorFlops: 461,
          fp32Performance: 91.1,
          fp16Performance: 461,
          tensorCores: 284,
          cudaCores: 18176,
          clockSpeed: 1800
        },
        memorySpecs: { 
          capacity: 48, 
          type: "GDDR6", 
          bandwidth: 960, 
          busWidth: 384,
          eccSupport: true
        },
        powerSpecs: { 
          tdp: 300, 
          requiredPsu: 850,
          powerConnectors: "1x 16-pin PCIe"
        },
        thermalSpecs: {
          cooling: "Active",
          maxTemp: 89
        },
        connectivity: ["PCIe 4.0"],
        supportedFrameworks: ["PyTorch", "TensorFlow", "CUDA", "JAX", "ONNX"],
        formFactor: "Full-height, full-length, dual slot",
        complianceInfo: {
          exportRestrictions: ["RU", "CN"],
          certifications: ["FCC", "CE", "RoHS"]
        },
        benchmarks: {
          mlTraining: { "ResNet50": 20000, "BERT-Large": 5300 },
          llmInference: { "GPT-3": 120, "T5": 220 }
        },
        availability: "1-2 weeks",
        releaseDate: "2022-12-05",
        inStock: true
      },
      "3 years limited"
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

// Use the in-memory storage implementation for reliability
// This avoids database connection issues while still providing the same functionality
export const storage = new MemStorage();</old_str>
<new_str>// All storage operations are handled by Python backend
// This file exists for TypeScript compatibility but should not be used
// All data operations go through the Python API at http://localhost:8000

export const storage = null; // Placeholder - all operations handled by Python backend</new_str>
