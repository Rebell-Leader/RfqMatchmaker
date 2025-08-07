# Makefile for RFQ Processing Platform
# Provides convenient commands for development, testing, and deployment

.PHONY: help install test test-frontend test-backend test-integration test-coverage clean build dev lint format security-scan

# Default target
help:
	@echo "🚀 RFQ Processing Platform - Development Commands"
	@echo "=================================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  make install          Install all dependencies (Node.js + Python)"
	@echo "  make install-frontend Install Node.js dependencies only"
	@echo "  make install-backend  Install Python dependencies only"
	@echo ""
	@echo "Development Commands:"
	@echo "  make dev              Start development servers (frontend + backend)"
	@echo "  make dev-frontend     Start frontend development server only"
	@echo "  make dev-backend      Start backend development server only"
	@echo ""
	@echo "Testing Commands:"
	@echo "  make test             Run all tests (frontend + backend)"
	@echo "  make test-frontend    Run frontend tests (Jest)"
	@echo "  make test-backend     Run backend tests (pytest)"
	@echo "  make test-integration Run integration tests"
	@echo "  make test-coverage    Run tests with coverage reports"
	@echo "  make test-ci          Run CI test suite"
	@echo ""
	@echo "Quality Commands:"
	@echo "  make lint             Run linting (TypeScript + Python)"
	@echo "  make format           Format code (Prettier + Black)"
	@echo "  make security-scan    Run security scans"
	@echo ""
	@echo "Build Commands:"
	@echo "  make build            Build production assets"
	@echo "  make clean            Clean build artifacts and caches"
	@echo ""

# Installation targets
install: install-frontend install-backend
	@echo "✅ All dependencies installed"

install-frontend:
	@echo "📦 Installing Node.js dependencies..."
	npm install

install-backend:
	@echo "🐍 Installing Python dependencies..."
	cd python_backend && uv sync

# Development targets
dev:
	@echo "🚀 Starting development servers..."
	npm run dev

dev-frontend:
	@echo "⚛️ Starting frontend development server..."
	cd client && npm run dev

dev-backend:
	@echo "🐍 Starting backend development server..."
	cd python_backend && uv run python -m python_backend.main

# Testing targets
test:
	@echo "🧪 Running all tests..."
	./run-tests.sh

test-frontend:
	@echo "🧪 Running frontend tests..."
	./run-tests.sh --frontend-only

test-backend:
	@echo "🧪 Running backend tests..."
	./run-tests.sh --backend-only

test-integration:
	@echo "🧪 Running integration tests..."
	./run-tests.sh --integration

test-coverage:
	@echo "📊 Running tests with coverage..."
	./run-tests.sh --coverage

test-ci:
	@echo "🤖 Running CI test suite..."
	./run-tests.sh --coverage --verbose

# Quality targets
lint: lint-frontend lint-backend
	@echo "✅ Linting completed"

lint-frontend:
	@echo "🔍 Linting TypeScript code..."
	npm run check

lint-backend:
	@echo "🔍 Linting Python code..."
	cd python_backend && uv run ruff check . || echo "⚠️ Install ruff for Python linting: uv add ruff"

format: format-frontend format-backend
	@echo "✨ Code formatting completed"

format-frontend:
	@echo "✨ Formatting TypeScript code..."
	npx prettier --write "client/src/**/*.{ts,tsx}" "tests/**/*.{ts,tsx}" "shared/**/*.ts" || echo "⚠️ Prettier not available"

format-backend:
	@echo "✨ Formatting Python code..."
	cd python_backend && uv run black . || echo "⚠️ Install black for Python formatting: uv add black"

security-scan:
	@echo "🔒 Running security scans..."
	@echo "📦 Scanning Node.js dependencies..."
	npm audit --audit-level moderate || echo "⚠️ npm audit found issues"
	@echo "🐍 Scanning Python dependencies..."
	cd python_backend && (uv run safety check || echo "⚠️ Install safety for Python security scanning: uv add safety")

# Build targets
build: clean build-frontend build-backend
	@echo "🏗️ Build completed"

build-frontend:
	@echo "⚛️ Building frontend..."
	npm run build

build-backend:
	@echo "🐍 Building backend..."
	npm run build

# Utility targets
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf dist/
	rm -rf client/dist/
	rm -rf coverage/
	rm -rf python_backend/htmlcov/
	rm -rf python_backend/.coverage
	rm -rf python_backend/coverage.xml
	rm -rf node_modules/.cache/
	rm -rf .pytest_cache/
	rm -f backend.log
	@echo "✅ Clean completed"

# Database targets
db-setup:
	@echo "🗄️ Setting up database..."
	npm run db:push

db-reset:
	@echo "🔄 Resetting database..."
	@echo "⚠️ This will delete all data. Press Ctrl+C to cancel, or wait 5 seconds to continue..."
	@sleep 5
	npm run db:push

# Docker targets (if using Docker)
docker-build:
	@echo "🐳 Building Docker images..."
	docker-compose build

docker-up:
	@echo "🐳 Starting Docker containers..."
	docker-compose up -d

docker-down:
	@echo "🐳 Stopping Docker containers..."
	docker-compose down

docker-logs:
	@echo "📋 Showing Docker logs..."
	docker-compose logs -f

# Deployment targets
deploy-prep: test-ci build
	@echo "🚀 Preparing for deployment..."
	@echo "✅ All tests passed and build completed"
	@echo "📦 Ready for deployment"

# Environment setup
env-example:
	@echo "📄 Creating example environment file..."
	@cat > .env.example << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/rfq_db

# AI Service API Keys
OPENAI_API_KEY=your_openai_api_key_here
FEATHERLESS_API_KEY=your_featherless_api_key_here

# Application Configuration
NODE_ENV=development
PORT=5000
PYTHON_BACKEND_PORT=8000

# Session Configuration
SESSION_SECRET=your_session_secret_here

# Email Configuration (for production)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your_email@example.com
SMTP_PASS=your_email_password

# Security Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5000
EOF
	@echo "✅ .env.example created"

# Health checks
health-check:
	@echo "🏥 Running health checks..."
	@echo "📡 Checking backend health..."
	@curl -f http://localhost:8000/health >/dev/null 2>&1 && echo "✅ Backend healthy" || echo "❌ Backend not responding"
	@echo "📡 Checking frontend..."
	@curl -f http://localhost:5000 >/dev/null 2>&1 && echo "✅ Frontend healthy" || echo "❌ Frontend not responding"

# Performance testing
perf-test:
	@echo "⚡ Running performance tests..."
	@echo "⚠️ This requires k6 to be installed"
	@which k6 >/dev/null 2>&1 || (echo "❌ k6 not found. Install from https://k6.io/docs/getting-started/installation/" && exit 1)
	@k6 run - <<'EOF'
	import http from 'k6/http';
	import { check } from 'k6';
	
	export let options = {
	  stages: [
	    { duration: '30s', target: 10 },
	    { duration: '1m', target: 20 },
	    { duration: '30s', target: 0 },
	  ],
	};
	
	export default function() {
	  let response = http.get('http://localhost:8000/health');
	  check(response, {
	    'status is 200': (r) => r.status === 200,
	    'response time < 500ms': (r) => r.timings.duration < 500,
	  });
	}
	EOF

# Make shell scripts executable
setup-scripts:
	@echo "🔧 Making scripts executable..."
	chmod +x run-tests.sh
	@echo "✅ Scripts are now executable"