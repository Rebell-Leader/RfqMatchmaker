# Overview

The RFQ Processing Platform is an AI-powered B2B procurement solution that automates supplier matching for Request for Quotations (RFQs). The platform specializes in AI hardware procurement, including GPUs and ML accelerators, with intelligent requirement extraction, supplier matching, compliance checking, and automated proposal generation. It features a modern web interface with real-time processing capabilities and supports both general procurement and specialized AI hardware sourcing workflows.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Technology Stack**: React 18 with TypeScript, using Vite as the build tool
- **UI Framework**: Tailwind CSS with Radix UI components for consistent design
- **State Management**: React Context API for RFQ workflow state and demo mode management
- **Routing**: Wouter for lightweight client-side routing
- **Query Management**: TanStack React Query for server state management and caching

## Backend Architecture
- **Dual Backend Approach**: 
  - Node.js/Express server acts as a proxy and serves the frontend
  - Python FastAPI server handles AI processing and database operations
- **API Design**: RESTful APIs with the Node.js server proxying requests to Python backend
- **Database Layer**: PostgreSQL with SQLAlchemy ORM in Python backend, Drizzle ORM configuration for TypeScript compatibility

## Data Storage Solutions
- **Primary Database**: PostgreSQL for production data storage
- **Schema Management**: Drizzle ORM with migration support
- **Vector Database**: Qdrant integration for semantic search capabilities (optional)
- **File Storage**: Local file system for RFQ document uploads with 10MB size limits

## AI and Processing Services
- **Requirement Extraction**: OpenAI GPT models for parsing RFQ documents and extracting structured requirements
- **Alternative AI Provider**: Featherless AI as backup/alternative to OpenAI
- **Embedding Service**: OpenAI embeddings for semantic supplier matching
- **Specialized Matching**: Custom AI hardware matching algorithms for GPU/accelerator procurement

## Authentication and Security
- **Session Management**: Express session handling with PostgreSQL session store
- **CORS Configuration**: Configured for cross-origin requests between frontend and backend services
- **Compliance Checking**: Built-in export control and regulatory compliance verification for AI hardware

## Workflow Management
- **5-Step Process**: Upload RFQ → Review Requirements → Match Suppliers → Score Results → Send Proposals
- **State Persistence**: Context-based state management with optional database persistence
- **Demo Mode**: Built-in demonstration capabilities with mock data for testing and showcasing

# External Dependencies

## AI Services
- **OpenAI API**: GPT models for requirement extraction and text processing
- **Featherless AI**: Alternative AI service provider for requirement extraction
- **Qdrant Vector Database**: Optional semantic search capabilities for advanced supplier matching

## Database and Storage
- **PostgreSQL**: Primary database with connection pooling and SSL support
- **Neon Database**: Serverless PostgreSQL provider integration
- **File System**: Local storage for uploaded RFQ documents

## Development and Deployment
- **Vite**: Frontend build tool and development server
- **Node.js Runtime**: Server-side JavaScript execution
- **Python Environment**: FastAPI backend with uvicorn ASGI server
- **Package Management**: npm for Node.js dependencies, pip for Python packages

## Third-party Integrations
- **Email Services**: Planned integration for automated proposal sending
- **PDF Generation**: jsPDF for client-side proposal document generation
- **Web Scraping**: Product information scraping from manufacturer websites
- **Compliance APIs**: Integration with export control and regulatory checking services

## UI and Styling
- **Tailwind CSS**: Utility-first CSS framework
- **Radix UI**: Accessible component primitives
- **Lucide Icons**: Icon library for UI elements
- **React Hook Form**: Form validation and management