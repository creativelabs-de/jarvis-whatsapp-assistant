#!/bin/bash

# JARVIS WhatsApp Assistant Test Runner
# This script runs all tests and generates coverage reports

set -e

echo "🧪 Running JARVIS WhatsApp Assistant Tests"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Change to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_step "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_step "Activating virtual environment..."
source venv/bin/activate

# Install test dependencies
print_step "Installing test dependencies..."
pip install -r test-requirements.txt

# Install main dependencies
pip install -r requirements.txt

# Run tests with coverage
print_step "Running tests with coverage..."
pytest tests/ \
    --cov=app \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-report=xml \
    -v \
    --tb=short

# Check coverage threshold
print_step "Checking coverage threshold..."
coverage report --fail-under=80

# Generate coverage badge
if command -v coverage-badge &> /dev/null; then
    print_step "Generating coverage badge..."
    coverage-badge -o ../docs/coverage.svg
fi

print_status "Tests completed successfully! 🎉"
print_status "Coverage report available at: backend/htmlcov/index.html"

# Deactivate virtual environment
deactivate

echo ""
echo "Test Summary:"
echo "============="
echo "✅ Unit tests passed"
echo "✅ Coverage threshold met"
echo "✅ Reports generated"
echo ""
echo "Next steps:"
echo "- Review coverage report"
echo "- Fix any failing tests"
echo "- Add more tests for new features"
