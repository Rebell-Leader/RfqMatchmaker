#!/bin/bash

# Test Runner Script for RFQ Processing Platform
# Runs both frontend (Node.js/Jest) and backend (Python/pytest) tests

set -e

echo "🧪 Running RFQ Processing Platform Test Suite"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    print_error "package.json not found. Please run this script from the project root."
    exit 1
fi

# Parse command line arguments
RUN_FRONTEND=true
RUN_BACKEND=true
RUN_INTEGRATION=false
COVERAGE=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --frontend-only)
            RUN_BACKEND=false
            shift
            ;;
        --backend-only)
            RUN_FRONTEND=false
            shift
            ;;
        --integration)
            RUN_INTEGRATION=true
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --frontend-only    Run only frontend tests"
            echo "  --backend-only     Run only backend tests"
            echo "  --integration      Run integration tests"
            echo "  --coverage         Generate coverage reports"
            echo "  --verbose          Verbose output"
            echo "  --help             Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Frontend Tests (Node.js/Jest)
if [ "$RUN_FRONTEND" = true ]; then
    print_status "Running Frontend Tests (TypeScript/Jest)"
    echo "----------------------------------------"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_status "Installing Node.js dependencies..."
        npm install
    fi
    
    # Run TypeScript checks
    print_status "Running TypeScript type checks..."
    if npm run check; then
        print_success "TypeScript checks passed"
        ((TESTS_PASSED++))
    else
        print_error "TypeScript checks failed"
        ((TESTS_FAILED++))
    fi
    
    # Run Jest tests
    print_status "Running Jest tests..."
    if [ "$COVERAGE" = true ]; then
        if [ "$VERBOSE" = true ]; then
            npm run test:coverage -- --verbose
        else
            npm run test:coverage
        fi
    else
        if [ "$VERBOSE" = true ]; then
            npm test -- --verbose
        else
            npm test
        fi
    fi
    
    if [ $? -eq 0 ]; then
        print_success "Frontend tests passed"
        ((TESTS_PASSED++))
    else
        print_error "Frontend tests failed"
        ((TESTS_FAILED++))
    fi
    
    echo
fi

# Backend Tests (Python/pytest)
if [ "$RUN_BACKEND" = true ]; then
    print_status "Running Backend Tests (Python/pytest)"
    echo "--------------------------------------"
    
    # Check if we're in a Python virtual environment or have uv
    if command -v uv >/dev/null 2>&1; then
        print_status "Using uv for Python dependency management"
        
        cd python_backend
        
        # Install dependencies if needed
        if [ ! -f "uv.lock" ]; then
            print_status "Installing Python dependencies..."
            uv sync
        fi
        
        # Run pytest
        print_status "Running pytest..."
        if [ "$COVERAGE" = true ]; then
            if [ "$VERBOSE" = true ]; then
                uv run pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html --cov-report=xml
            else
                uv run pytest tests/ --cov=. --cov-report=term-missing --cov-report=xml
            fi
        else
            if [ "$VERBOSE" = true ]; then
                uv run pytest tests/ -v
            else
                uv run pytest tests/
            fi
        fi
        
        if [ $? -eq 0 ]; then
            print_success "Backend tests passed"
            ((TESTS_PASSED++))
        else
            print_error "Backend tests failed"
            ((TESTS_FAILED++))
        fi
        
        cd ..
    else
        print_warning "uv not found. Trying with pip/pytest..."
        
        cd python_backend
        
        # Try with pip
        if command -v pytest >/dev/null 2>&1; then
            print_status "Running pytest with pip environment..."
            if [ "$COVERAGE" = true ]; then
                pytest tests/ --cov=. --cov-report=term-missing
            else
                pytest tests/
            fi
            
            if [ $? -eq 0 ]; then
                print_success "Backend tests passed"
                ((TESTS_PASSED++))
            else
                print_error "Backend tests failed"
                ((TESTS_FAILED++))
            fi
        else
            print_error "Neither uv nor pytest found. Please install Python testing dependencies."
            print_error "Install with: pip install pytest pytest-asyncio pytest-cov"
            ((TESTS_FAILED++))
        fi
        
        cd ..
    fi
    
    echo
fi

# Integration Tests
if [ "$RUN_INTEGRATION" = true ]; then
    print_status "Running Integration Tests"
    echo "-------------------------"
    
    # Start Python backend in background
    print_status "Starting Python backend for integration tests..."
    cd python_backend
    
    if command -v uv >/dev/null 2>&1; then
        nohup uv run python -m python_backend.main > ../backend.log 2>&1 &
    else
        nohup python -m python_backend.main > ../backend.log 2>&1 &
    fi
    
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend to start
    print_status "Waiting for backend to start..."
    sleep 10
    
    # Test basic endpoints
    print_status "Testing health endpoint..."
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        print_success "Health endpoint responding"
        
        # Test other endpoints
        print_status "Testing API endpoints..."
        
        # Test compliance endpoint
        if curl -f http://localhost:8000/api/ai-hardware/check-compliance >/dev/null 2>&1; then
            print_success "Compliance endpoint working"
        else
            print_warning "Compliance endpoint not responding"
        fi
        
        # Test frameworks endpoint
        if curl -f http://localhost:8000/api/ai-hardware/frameworks-compatibility >/dev/null 2>&1; then
            print_success "Frameworks endpoint working"
        else
            print_warning "Frameworks endpoint not responding"
        fi
        
        # Test file upload
        print_status "Testing file upload..."
        echo "Test RFQ content for AI hardware procurement" > test_rfq.txt
        if curl -X POST -F "file=@test_rfq.txt" http://localhost:8000/api/rfqs/upload >/dev/null 2>&1; then
            print_success "File upload working"
        else
            print_warning "File upload not working"
        fi
        rm -f test_rfq.txt
        
        print_success "Integration tests completed"
        ((TESTS_PASSED++))
    else
        print_error "Backend not responding"
        ((TESTS_FAILED++))
    fi
    
    # Clean up backend process
    print_status "Stopping backend..."
    kill $BACKEND_PID 2>/dev/null || true
    rm -f backend.log
    
    echo
fi

# Summary
echo "=============================================="
print_status "Test Summary"
echo "=============================================="

if [ $TESTS_FAILED -eq 0 ]; then
    print_success "All test suites passed! ✅"
    print_success "Passed: $TESTS_PASSED, Failed: $TESTS_FAILED"
    
    if [ "$COVERAGE" = true ]; then
        echo
        print_status "Coverage reports generated:"
        [ -f "coverage/lcov.info" ] && echo "  📊 Frontend: coverage/index.html"
        [ -f "python_backend/htmlcov/index.html" ] && echo "  📊 Backend: python_backend/htmlcov/index.html"
    fi
    
    exit 0
else
    print_error "Some tests failed! ❌"
    print_error "Passed: $TESTS_PASSED, Failed: $TESTS_FAILED"
    
    echo
    print_status "💡 Troubleshooting tips:"
    echo "  • Check that all dependencies are installed (npm install, uv sync)"
    echo "  • Ensure database is running for backend tests"
    echo "  • Verify API keys are set in environment variables"
    echo "  • Run with --verbose flag for detailed output"
    echo "  • Check individual test suites with --frontend-only or --backend-only"
    
    exit 1
fi