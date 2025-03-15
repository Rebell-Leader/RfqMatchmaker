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
