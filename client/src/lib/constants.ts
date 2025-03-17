// Application constants

// Stepper steps
export const STEPS = [
  { id: 1, label: "Upload RFQ" },
  { id: 2, label: "Review Requirements" },
  { id: 3, label: "Match Suppliers" },
  { id: 4, label: "Score Results" },
  { id: 5, label: "Send Proposals" }
];

// Scoring criteria with default weights
export const DEFAULT_SCORING_CRITERIA = {
  price: {
    weight: 50,
    description: "Lowest cost gets the highest score"
  },
  quality: {
    weight: 30,
    description: "Based on specifications and warranty"
  },
  delivery: {
    weight: 20,
    description: "Faster delivery gets higher scores"
  }
};

// Product categories
export const PRODUCT_CATEGORIES = [
  "Laptops",
  "Monitors",
  "Desktops",
  "Tablets",
  "Printers",
  "Servers",
  "Networking"
];

// Email template placeholders
export const EMAIL_PLACEHOLDERS = {
  USER_NAME: "[Your Name]",
  USER_POSITION: "[Your Position]",
  USER_CONTACT: "[Your Contact Information]"
};

// Demo mode flag and mock data
export const DEMO_MODE = {
  enabled: false,
  processingTime: 2000, // Mock processing time in milliseconds
};

// AI Hardware RFQ mock data
export const AI_HARDWARE_RFQ = {
  id: 998,
  title: "Procurement of AI Accelerators for Cloud ML/AI Training Platform",
  description: "Request for quotation for high-performance AI/ML training accelerators for our new cloud computing platform.",
  extractedRequirements: {
    title: "Procurement of AI Accelerators for Cloud ML/AI Training Platform",
    description: "TechInnovate Inc. is seeking qualified suppliers to provide high-performance AI accelerators for our new machine learning cloud platform. The hardware must meet strict performance, memory, and compatibility requirements for large-scale AI model training and inference.",
    categories: ["AI Hardware"],
    aiHardware: {
      type: "GPU",
      quantity: 24,
      preferredManufacturers: ["NVIDIA", "AMD"],
      minMemory: 64, // GB
      minComputePower: 250, // TFLOPS
      powerConstraints: 700, // watts
      frameworks: ["PyTorch", "TensorFlow", "JAX"],
      connectivity: ["NVLink", "PCIe 4.0"],
      formFactor: "OAM/SXM",
      coolingRequirements: "Liquid cooling compatible"
    },
    systemRequirements: {
      rackSpace: "Standard 42U racks",
      powerAvailability: "5kW per rack", 
      coolingCapacity: "Advanced liquid cooling system available",
      networkingRequirements: "100 Gbps InfiniBand",
      operatingSystem: "Linux Ubuntu 20.04 LTS"
    },
    complianceRequirements: {
      allowedCountries: ["US", "EU", "JP", "KR", "TW", "SG"],
      requiredCertifications: ["FCC", "CE", "RoHS"],
      dataPrivacyRequirements: ["GDPR compliant"],
      exportComplianceNeeded: true
    },
    performanceTargets: {
      trainingTime: {
        model: "Large Language Model (200B parameters)",
        dataset: "Text corpus (5TB)",
        targetTime: 14 // days
      },
      inferenceSpeed: {
        model: "BERT-Large",
        batchSize: 64,
        targetThroughput: 2000 // samples/sec
      }
    },
    criteria: {
      price: { weight: 25 },
      performance: { weight: 35 },
      availability: { weight: 15 },
      compliance: { weight: 15 },
      support: { weight: 10 }
    }
  },
  createdAt: new Date().toISOString()
};

// Standard education RFQ mock data
export const EDUCATION_RFQ = {
  id: 999,
  title: "Supply and Delivery of Laptops and Monitors for High School Computer Classes",
  description: "Request for quotation for computer equipment for Lincoln High School's new computer lab renovation project.",
  extractedRequirements: {
    title: "Supply and Delivery of Laptops and Monitors for High School Computer Classes",
    description: "Lincoln High School is seeking qualified suppliers to provide computer equipment for its newly renovated computer lab. The equipment should be high quality, durable, and suitable for educational purposes.",
    categories: ["Laptops", "Monitors"],
    laptops: {
      quantity: 30,
      os: "Windows 11 Pro Education",
      processor: "Intel Core i5 12th Gen or AMD Ryzen 5 5000 Series",
      memory: "16GB DDR4",
      storage: "512GB SSD",
      display: "15.6-inch Full HD (1920 x 1080)",
      battery: "8+ hours battery life",
      durability: "MIL-STD-810G tested",
      connectivity: "Wi-Fi 6, Bluetooth 5.0, USB-C, HDMI",
      warranty: "3-year warranty"
    },
    monitors: {
      quantity: 30, 
      screenSize: "24-inch",
      resolution: "Full HD (1920 x 1080)",
      panelTech: "IPS",
      brightness: "250 cd/m²",
      contrastRatio: "1000:1",
      connectivity: "HDMI, DisplayPort, USB hub",
      adjustability: "Height, tilt, and swivel adjustable",
      warranty: "3-year warranty"
    },
    criteria: {
      price: { weight: 50 },
      quality: { weight: 30 },
      delivery: { weight: 20 }
    }
  },
  createdAt: new Date().toISOString()
};

// Set the default demo RFQ to AI Hardware (our new focus)
export const DEMO_RFQ = AI_HARDWARE_RFQ;

// Demo supplier matches for AI Hardware
export const DEMO_SUPPLIER_MATCHES = [
  {
    supplier: {
      id: 1,
      name: "NVIDIA Corporation",
      logoUrl: "https://cdn-icons-png.flaticon.com/512/882/882704.png",
      website: "https://www.nvidia.com",
      country: "United States",
      description: "NVIDIA is a global leader in AI computing hardware, specializing in GPUs and accelerated computing solutions for data centers, AI research, and cloud computing.",
      contactEmail: "enterprise-sales@nvidia.com",
      contactPhone: "+1-800-789-8632",
      deliveryTime: "30-45 days",
      isVerified: true
    },
    product: {
      id: 1,
      supplierId: 1,
      name: "NVIDIA H100 SXM5 GPU",
      category: "AI Hardware",
      description: "The NVIDIA H100 Tensor Core GPU is the most advanced accelerator ever built for AI and HPC workloads, delivering unprecedented performance, scalability, and security.",
      price: 32500.00,
      specifications: {
        computeSpecs: {
          tensorFlops: 989, // FP8
          fp32Performance: 67, // TFLOPS
          fp16Performance: 134, // TFLOPS
          int8Performance: 1979, // TOPS
          tensorCores: 528,
          cudaCores: 16896,
          clockSpeed: 1830 // MHz
        },
        memorySpecs: {
          capacity: 80, // GB
          type: "HBM3",
          bandwidth: 3350, // GB/s
          busWidth: 5120, // bits
          eccSupport: true
        },
        powerSpecs: {
          tdp: 700, // watts
          requiredPsu: 1800, // watts
          powerConnectors: "SXM5"
        },
        formFactor: "SXM5",
        connectivity: ["NVLink", "PCIe 5.0"],
        supportedFrameworks: ["PyTorch", "TensorFlow", "JAX", "CUDA", "MXNet", "RAPIDS"],
        coolingRequirements: "Liquid cooling"
      },
      warranty: "3 years enterprise support"
    },
    matchScore: 96.8,
    matchDetails: {
      price: 88,
      performance: 99,
      compatibility: 98,
      availability: 90,
      compliance: 95,
      support: 93
    },
    totalPrice: 780000.00,
    estimatedDelivery: "35 days",
    complianceNotes: "Fully compliant with US export regulations. Requires end-user verification."
  },
  {
    supplier: {
      id: 2,
      name: "AMD Inc.",
      logoUrl: "https://cdn-icons-png.flaticon.com/512/882/882713.png",
      website: "https://www.amd.com",
      country: "United States",
      description: "Advanced Micro Devices (AMD) is a global semiconductor company specializing in high-performance computing, graphics, and visualization technologies.",
      contactEmail: "enterprise@amd.com",
      contactPhone: "+1-877-284-1566",
      deliveryTime: "25-40 days",
      isVerified: true
    },
    product: {
      id: 5,
      supplierId: 2,
      name: "AMD Instinct MI250X OAM",
      category: "AI Hardware",
      description: "Dual-GPU accelerator designed for the exascale era, featuring powerful compute capabilities for HPC and AI workloads.",
      price: 28750.00,
      specifications: {
        computeSpecs: {
          tensorFlops: 383, // Mixed precision
          fp32Performance: 47.9, // TFLOPS
          fp16Performance: 383.2, // TFLOPS
          int8Performance: 766.4, // TOPS
          tensorCores: 440, // compute units
          clockSpeed: 1700 // MHz
        },
        memorySpecs: {
          capacity: 128, // GB
          type: "HBM2e",
          bandwidth: 3200, // GB/s
          busWidth: 8192, // bits
          eccSupport: true
        },
        powerSpecs: {
          tdp: 560, // watts per GPU (total 560W)
          requiredPsu: 1500, // watts
          powerConnectors: "OAM"
        },
        formFactor: "OAM",
        connectivity: ["Infinity Fabric", "PCIe 4.0"],
        supportedFrameworks: ["PyTorch", "TensorFlow", "ROCm", "OpenCL"],
        coolingRequirements: "Liquid cooling"
      },
      warranty: "3 years standard"
    },
    matchScore: 92.4,
    matchDetails: {
      price: 94,
      performance: 91,
      compatibility: 85,
      availability: 93,
      compliance: 99
    },
    totalPrice: 690000.00,
    estimatedDelivery: "30 days",
    complianceNotes: "Fully compliant with all export controls and regulations."
  },
  {
    supplier: {
      id: 3,
      name: "Intel Corporation",
      logoUrl: "https://cdn-icons-png.flaticon.com/512/882/882702.png",
      website: "https://www.intel.com",
      country: "United States",
      description: "Intel Corporation is a technology leader focused on processor innovation, artificial intelligence, and accelerated computing solutions.",
      contactEmail: "data-center@intel.com",
      contactPhone: "+1-916-377-7000",
      deliveryTime: "20-35 days",
      isVerified: true
    },
    product: {
      id: 3,
      supplierId: 3,
      name: "Intel Gaudi 2",
      category: "AI Hardware",
      description: "Purpose-built deep learning accelerator with integrated 100GbE networking for scaling training workloads.",
      price: 22500.00,
      specifications: {
        computeSpecs: {
          tensorFlops: 197, // BF16
          fp32Performance: 52, // TFLOPS
          fp16Performance: 197, // TFLOPS
          int8Performance: 394, // TOPS
          tensorCores: 24, // Tensor processor cores
          clockSpeed: 1500 // MHz estimate
        },
        memorySpecs: {
          capacity: 96, // GB
          type: "HBM2e",
          bandwidth: 2450, // GB/s
          busWidth: 4096, // bits
          eccSupport: true
        },
        powerSpecs: {
          tdp: 600, // watts
          requiredPsu: 1500, // watts
          powerConnectors: "PCIe/OAM"
        },
        formFactor: "OAM",
        connectivity: ["100GbE RoCE", "PCIe 4.0"],
        supportedFrameworks: ["PyTorch", "TensorFlow", "OneAPI"],
        coolingRequirements: "Liquid cooling recommended"
      },
      warranty: "3 years with next business day support"
    },
    matchScore: 84.7,
    matchDetails: {
      price: 98,
      performance: 78,
      compatibility: 82,
      availability: 95,
      compliance: 97
    },
    totalPrice: 540000.00,
    estimatedDelivery: "25 days",
    complianceNotes: "Compliant with all US export regulations. No restrictions for data centers in approved countries."
  }
];

// Demo email proposal for AI Hardware
export const DEMO_EMAIL_PROPOSAL = {
  to: "enterprise-sales@nvidia.com",
  cc: "infrastructure@techinnovate.com",
  subject: "RFQ Response Request: AI Accelerators for TechInnovate ML Cloud Platform",
  body: `Dear NVIDIA Enterprise Team,

I hope this message finds you well. My name is [Your Name], and I am the AI Infrastructure Director at TechInnovate Inc. We are in the process of building a high-performance machine learning cloud platform for large-scale AI model training, and after a comprehensive evaluation, we are particularly interested in your NVIDIA H100 SXM5 GPUs for this initiative.

The NVIDIA H100 Tensor Core GPU aligns exceptionally well with our performance and technical requirements. The extraordinary compute capabilities with 989 TFLOPS for FP8 operations and 80GB of HBM3 memory with 3350 GB/s bandwidth will provide the foundation we need for training our large language models and handling complex AI workloads.

We're especially impressed with the following aspects of the H100:
- The advanced Tensor Cores that deliver breakthrough performance for AI operations
- The robust support for our required frameworks (PyTorch, TensorFlow, JAX)
- The scalability through NVLink and PCIe 5.0 connectivity
- The enterprise-grade security features and compliance with export regulations

For your reference, our order specifications are as follows:
- **Unit Price:** $32,500.00
- **Quantity:** 24 units
- **Total Estimated Investment:** $780,000.00

Given the scale of this procurement, we would like to discuss potential volume pricing that might be available for this order.

The technical requirements from our RFQ that your H100 SXM5 GPU meets or exceeds:
- **Compute Performance:** 989 TFLOPs (FP8) vs. our 250 TFLOPs requirement
- **Memory:** 80GB HBM3 vs. our 64GB minimum requirement
- **Memory Bandwidth:** 3350 GB/s vs. our estimated 3000 GB/s requirement
- **Form Factor:** SXM5 (compatible with our liquid cooling infrastructure)
- **Framework Support:** Complete coverage of our required ML frameworks
- **Connectivity:** NVLink and PCIe 5.0, exceeding our specifications

Our system requirements include rack space in a standard 42U configuration with liquid cooling infrastructure already in place. We have 5kW per rack power availability and are prepared to handle the thermal requirements of the H100 GPUs.

We would appreciate if you could provide us with:
1. Confirmation of availability for 24 units of the NVIDIA H100 SXM5 GPU
2. Detailed delivery timeline and deployment support options
3. Information on volume pricing and enterprise discounts
4. Details on extended warranty and support packages
5. Compliance verification process and documentation requirements

We aim to begin deployment by [Target Date] and would greatly appreciate your response by [Response Date]. Our team is available for technical discussions and to address any questions about our infrastructure or workload requirements.

Thank you for your time and consideration. We look forward to the possibility of working with NVIDIA on this strategic AI infrastructure project.

Best regards,

[Your Name]
AI Infrastructure Director
TechInnovate Inc.
[Your Contact Information]`
};
