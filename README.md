
# RFQ Processing Platform

An AI-powered platform for automating supplier matching in procurement processes, with specialized support for AI hardware requirements.

## 🚀 Features

- **Intelligent RFQ Processing**: Upload RFQ documents (PDF/text) and extract requirements using AI
- **Smart Supplier Matching**: Match suppliers based on technical specifications and business criteria
- **AI Hardware Specialization**: Advanced matching for GPUs, accelerators, and ML hardware
- **Compliance Checking**: Automated export control and regulatory compliance verification
- **Email Automation**: Generate and send professional supplier proposals

## 🏗 Architecture

The platform consists of:
- **Frontend**: React/TypeScript client with modern UI components
- **Backend**: Python FastAPI server with AI services
- **Database**: PostgreSQL with Drizzle ORM
- **AI Services**: Integration with OpenAI/Featherless AI for NLP tasks

## 🛠 Setup & Installation

### Prerequisites
- Node.js 20+
- Python 3.11+
- PostgreSQL database

### Environment Variables
Create a `.env` file in the root directory:
```
DATABASE_URL=your_postgresql_connection_string
OPENAI_API_KEY=your_openai_api_key  # For embeddings and AI processing
FEATHERLESS_API_KEY=your_featherless_key  # For requirement extraction
```

### Quick Start
1. Install dependencies:
```bash
npm install
```

2. Start the application:
```bash
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5000
- API: http://localhost:8000

## 📊 Usage

### Basic Workflow
1. **Upload RFQ**: Submit procurement documents via the upload interface
2. **Review Requirements**: AI extracts and categorizes technical specifications
3. **Match Suppliers**: System finds relevant suppliers based on capabilities
4. **Generate Proposals**: Create professional email proposals for selected suppliers

### AI Hardware Platform
For specialized AI/ML hardware procurement:
1. Use the questionnaire interface for technical requirements
2. System matches GPUs, accelerators, and compute infrastructure
3. Includes compliance checking for export controls
4. Performance benchmarking and framework compatibility

## 🔧 API Endpoints

### Core Endpoints
- `GET /api/rfqs` - List all RFQs
- `POST /api/rfqs/upload` - Upload RFQ document
- `POST /api/rfqs` - Create RFQ manually
- `POST /api/rfqs/{id}/match-suppliers` - Find supplier matches
- `POST /api/proposals/{id}/generate-email` - Generate email proposals

### AI Hardware Endpoints
- `POST /api/seed-ai-hardware-products` - Initialize sample data
- `GET /api/ai-hardware/check-compliance` - Compliance verification
- `GET /api/ai-hardware/frameworks-compatibility` - Framework support check
- `GET /api/ai-hardware/performance-comparison` - Hardware benchmarking

## 🧪 Development

### Frontend Development
```bash
cd client
npm run dev
```

### Backend Development
```bash
cd python_backend
python -m uvicorn api.app:app --reload --port 8000
```

### Database Schema
```bash
npm run db:push
```

## 📦 Deployment

Deploy on Replit:
1. Import project to Replit
2. Configure environment variables in Replit Secrets
3. The project will auto-deploy with the configured run command

## 🚧 Known Limitations (MVP)

- Email sending is simulated (not actually sent)
- Limited supplier database (sample data)
- Basic compliance checking (not comprehensive)
- Single-user system (no authentication)

## 🔮 Roadmap

- [ ] Real email integration (SendGrid/SMTP)
- [ ] Advanced supplier database with real integrations
- [ ] Multi-user support with authentication
- [ ] Advanced analytics and reporting
- [ ] Mobile-responsive design improvements

## 📄 License

MIT License - see LICENSE file for details
