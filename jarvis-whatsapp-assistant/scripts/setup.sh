#!/bin/bash

# JARVIS WhatsApp Assistant Setup Script
# This script helps you deploy JARVIS to production

set -e

echo "🤖 JARVIS WhatsApp Assistant Setup"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if required tools are installed
check_requirements() {
    print_step "Checking requirements..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v kubectl &> /dev/null; then
        print_warning "kubectl is not installed. You'll need it for Kubernetes deployment."
    fi
    
    if ! command -v gcloud &> /dev/null; then
        print_warning "gcloud CLI is not installed. You'll need it for Google Cloud deployment."
    fi
    
    print_status "Requirements check completed."
}

# Setup environment variables
setup_env() {
    print_step "Setting up environment variables..."
    
    if [ ! -f .env ]; then
        cp .env.example .env
        print_warning "Created .env file from template. Please edit it with your actual values."
        echo ""
        echo "You need to configure:"
        echo "- WHATSAPP_ACCESS_TOKEN"
        echo "- WHATSAPP_PHONE_NUMBER_ID"
        echo "- WHATSAPP_WEBHOOK_VERIFY_TOKEN"
        echo "- OPENAI_API_KEY"
        echo "- GOOGLE_CLOUD_PROJECT_ID"
        echo ""
        read -p "Press Enter after you've configured the .env file..."
    fi
    
    print_status "Environment setup completed."
}

# Build Docker image
build_image() {
    print_step "Building Docker image..."
    
    docker build -t jarvis-backend:latest .
    
    print_status "Docker image built successfully."
}

# Deploy locally with Docker Compose
deploy_local() {
    print_step "Deploying locally with Docker Compose..."
    
    docker-compose up -d
    
    print_status "Local deployment completed."
    print_status "JARVIS is running at http://localhost:8000"
    print_status "Health check: http://localhost:8000/health"
}

# Deploy to Google Cloud
deploy_gcloud() {
    print_step "Deploying to Google Cloud..."
    
    # Check if gcloud is configured
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "Please run 'gcloud auth login' first."
        exit 1
    fi
    
    # Get project ID
    PROJECT_ID=$(gcloud config get-value project)
    if [ -z "$PROJECT_ID" ]; then
        print_error "Please set your Google Cloud project: gcloud config set project YOUR_PROJECT_ID"
        exit 1
    fi
    
    print_status "Using project: $PROJECT_ID"
    
    # Enable required APIs
    print_step "Enabling required Google Cloud APIs..."
    gcloud services enable container.googleapis.com
    gcloud services enable speech.googleapis.com
    gcloud services enable texttospeech.googleapis.com
    
    # Build and push image
    print_step "Building and pushing Docker image..."
    docker tag jarvis-backend:latest gcr.io/$PROJECT_ID/jarvis-backend:latest
    docker push gcr.io/$PROJECT_ID/jarvis-backend:latest
    
    # Create GKE cluster if it doesn't exist
    if ! gcloud container clusters describe jarvis-cluster --zone=us-central1-a &> /dev/null; then
        print_step "Creating GKE cluster..."
        gcloud container clusters create jarvis-cluster \
            --zone=us-central1-a \
            --num-nodes=3 \
            --machine-type=e2-medium \
            --enable-autoscaling \
            --min-nodes=1 \
            --max-nodes=5
    fi
    
    # Get cluster credentials
    gcloud container clusters get-credentials jarvis-cluster --zone=us-central1-a
    
    # Create secrets
    print_step "Creating Kubernetes secrets..."
    kubectl create secret generic jarvis-secrets \
        --from-env-file=.env \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Deploy to Kubernetes
    print_step "Deploying to Kubernetes..."
    sed "s/YOUR_PROJECT_ID/$PROJECT_ID/g" k8s/deployment.yaml | kubectl apply -f -
    kubectl apply -f k8s/ingress.yaml
    
    print_status "Google Cloud deployment completed."
    print_status "Your JARVIS instance will be available at your configured domain."
}

# Main menu
main_menu() {
    echo ""
    echo "Choose deployment option:"
    echo "1) Local development (Docker Compose)"
    echo "2) Google Cloud production (GKE)"
    echo "3) Build Docker image only"
    echo "4) Exit"
    echo ""
    read -p "Enter your choice (1-4): " choice
    
    case $choice in
        1)
            setup_env
            build_image
            deploy_local
            ;;
        2)
            setup_env
            build_image
            deploy_gcloud
            ;;
        3)
            build_image
            ;;
        4)
            print_status "Goodbye!"
            exit 0
            ;;
        *)
            print_error "Invalid choice. Please try again."
            main_menu
            ;;
    esac
}

# Run the script
check_requirements
main_menu

echo ""
print_status "Setup completed! 🎉"
echo ""
echo "Next steps:"
echo "1. Configure your WhatsApp webhook URL"
echo "2. Test the webhook with a WhatsApp message"
echo "3. Monitor logs: docker-compose logs -f (local) or kubectl logs -f deployment/jarvis-backend (GKE)"
echo ""
echo "For support, check the documentation or create an issue on GitHub."
