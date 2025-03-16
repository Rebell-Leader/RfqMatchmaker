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

// Demo mode mock data
export const DEMO_RFQ = {
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

// Demo supplier matches
export const DEMO_SUPPLIER_MATCHES = [
  {
    supplier: {
      id: 1,
      name: "Dell Technologies",
      logoUrl: "https://cdn-icons-png.flaticon.com/512/882/882730.png",
      website: "https://www.dell.com",
      country: "United States",
      description: "Dell Technologies is a leading provider of computer equipment and services for businesses and educational institutions.",
      contactEmail: "education@dell.com",
      contactPhone: "+1-800-456-3355",
      deliveryTime: "15-30 days",
      isVerified: true
    },
    product: {
      id: 1,
      supplierId: 1,
      name: "Dell Latitude 5430 Education Edition",
      category: "Laptops",
      description: "Business-class laptop designed for education environments. Features spill-resistant keyboard and rugged design.",
      price: 899.99,
      specifications: {
        os: "Windows 11 Pro Education",
        processor: "Intel Core i5-1235U",
        memory: "16GB DDR4",
        storage: "512GB SSD",
        display: "14-inch Full HD (1920 x 1080)",
        battery: "10 hours",
        durability: "MIL-STD-810H tested",
        connectivity: "Wi-Fi 6E, Bluetooth 5.2, Thunderbolt 4",
        ports: "2x USB-C, 2x USB-A, HDMI, headphone jack",
        warranty: "3 years ProSupport"
      },
      warranty: "3 years ProSupport"
    },
    matchScore: 87.5,
    matchDetails: {
      price: 85,
      quality: 92,
      delivery: 85
    },
    totalPrice: 26999.70
  },
  {
    supplier: {
      id: 2,
      name: "HP Inc.",
      logoUrl: "https://cdn-icons-png.flaticon.com/512/882/882747.png",
      website: "https://www.hp.com",
      country: "United States",
      description: "HP Inc. is a leading technology company that develops personal computers, printers and related supplies, as well as 3D printing solutions.",
      contactEmail: "education-sales@hp.com",
      contactPhone: "+1-800-334-5144",
      deliveryTime: "10-25 days",
      isVerified: true
    },
    product: {
      id: 5,
      supplierId: 2,
      name: "HP E27u G4 QHD Monitor",
      category: "Monitors",
      description: "Business-class QHD monitor with USB-C connectivity and ergonomic stand.",
      price: 349.99,
      specifications: {
        screenSize: "27-inch",
        resolution: "QHD (2560 x 1440)",
        panelTech: "IPS",
        brightness: "300 cd/m²",
        contrastRatio: "1000:1",
        connectivity: "HDMI, DisplayPort, USB-C",
        adjustability: "Height, tilt, swivel adjustable",
        warranty: "3 years"
      },
      warranty: "3 years standard"
    },
    matchScore: 92.4,
    matchDetails: {
      price: 95,
      quality: 88,
      delivery: 94
    },
    totalPrice: 10499.70
  },
  {
    supplier: {
      id: 3,
      name: "Lenovo Group",
      logoUrl: "https://cdn-icons-png.flaticon.com/512/882/882711.png",
      website: "https://www.lenovo.com",
      country: "China",
      description: "Lenovo Group Limited is a Chinese multinational technology company specializing in PCs, tablets, smartphones, workstations, servers, and more.",
      contactEmail: "education@lenovo.com",
      contactPhone: "+1-855-253-6686",
      deliveryTime: "15-35 days",
      isVerified: true
    },
    product: {
      id: 3,
      supplierId: 3,
      name: "Lenovo ThinkPad L14 Gen 3",
      category: "Laptops",
      description: "Reliable business laptop built for productivity with exceptional durability features.",
      price: 1099.99,
      specifications: {
        os: "Windows 11 Pro",
        processor: "AMD Ryzen 5 5600U",
        memory: "16GB DDR4",
        storage: "512GB PCIe SSD",
        display: "14-inch Full HD (1920 x 1080)",
        battery: "9 hours",
        durability: "MIL-STD-810H tested",
        connectivity: "Wi-Fi 6, Bluetooth 5.1",
        ports: "USB-C, 2x USB-A, HDMI, headphone jack",
        warranty: "3 years"
      },
      warranty: "3 years depot"
    },
    matchScore: 79.8,
    matchDetails: {
      price: 75,
      quality: 88,
      delivery: 75
    },
    totalPrice: 32999.70
  }
];

// Demo email proposal
export const DEMO_EMAIL_PROPOSAL = {
  to: "education-sales@hp.com",
  cc: "procurement@example.org",
  subject: "RFQ Response Request: Monitors for Lincoln High School Computer Lab",
  body: `Dear HP Inc. Team,

I hope this message finds you well. My name is [Your Name], and I am the procurement manager at Lincoln High School. We are currently in the process of sourcing high-quality computer equipment for our high school classrooms, and after careful consideration, we are very interested in your HP E27u G4 monitors for this project.

The HP E27u G4 monitor aligns perfectly with our requirements for a reliable and high-performance monitor for our classrooms. This business-class QHD monitor not only meets but exceeds the specifications we have outlined in our RFQ. The 27-inch QHD (2560 x 1440) resolution and IPS panel technology ensure that students and teachers will have a clear and vibrant viewing experience, even in bright classroom environments.

We are particularly impressed by the ergonomic design of the monitor, which includes height, tilt, and swivel adjustments, making it comfortable for students of all sizes. Additionally, the inclusion of USB-C connectivity provides a versatile and user-friendly experience, which is crucial for our educational setting.

For your reference, the detailed pricing information is as follows:
- **Unit Price:** $349.99
- **Quantity:** 30 units
- **Total Price:** $10,499.70

We are also interested in any volume discounts you may offer for this order, as it would significantly benefit our budget.

The technical specifications of the HP E27u G4 monitor are as follows:
- **Screen Size:** 27 inches
- **Resolution:** QHD (2560 x 1440)
- **Panel Technology:** IPS
- **Brightness:** 300 cd/m²
- **Contrast Ratio:** 1000:1
- **Connectivity:** HDMI, DisplayPort, USB-C
- **Adjustability:** Height, tilt, swivel adjustable
- **Warranty:** 3 years standard

These specifications not only meet but surpass our requirements for a 24-inch Full HD monitor with IPS panel technology. The additional features and higher resolution will provide an enhanced visual experience for our students.

Could you please provide us with:
1. Confirmation of availability for 30 units of the HP E27u G4 monitor
2. Detailed delivery timeline
3. Any educational discount that might be applicable
4. Information about extended warranty options

We would appreciate your response by [Response Date], as we are working to complete our computer lab renovation by the start of the next semester.

Thank you for your time and consideration. We look forward to potentially working with HP Inc. on this project.

Best regards,

[Your Name]
Procurement Manager
Lincoln High School
[Your Contact Information]`
};
