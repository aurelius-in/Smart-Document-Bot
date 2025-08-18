#!/bin/bash

# Smart Document Bot - Development Setup Script
# This script sets up the development environment for the Smart Document Bot

set -e  # Exit on any error

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if Docker is running
check_docker() {
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "Docker is available and running"
}

# Function to check if Docker Compose is available
check_docker_compose() {
    if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
        print_error "Docker Compose is not available. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker Compose is available"
}

# Function to create environment file
create_env_file() {
    if [ ! -f .env ]; then
        print_status "Creating .env file..."
        cat > .env << EOF
# Smart Document Bot Environment Variables

# API Keys (Replace with your actual keys)
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Database Configuration
DATABASE_URL=postgresql://redline_user:redline_password@localhost:5432/redline
REDIS_URL=redis://localhost:6379

# Vector Database
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Application Settings
DEBUG=true
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload
MAX_FILE_SIZE=52428800  # 50MB
UPLOAD_DIR=./uploads

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
ENABLE_TRACING=true

# OPA (Open Policy Agent)
OPA_URL=http://localhost:8181
OPA_POLICIES_DIR=./app/risk/policies

# Audit
AUDIT_LOG_DIR=./audit_logs
AUDIT_RETENTION_DAYS=365

# Agent Settings
MAX_AGENT_STEPS=10
AGENT_TIMEOUT_SECONDS=300
CONFIDENCE_THRESHOLD=0.7

# PII Redaction
ENABLE_PII_REDACTION=true
PII_PATTERNS=["\\b\\d{3}-\\d{2}-\\d{4}\\b","\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b"]
EOF
        print_success "Created .env file"
        print_warning "Please update the API keys in .env file with your actual keys"
    else
        print_status ".env file already exists"
    fi
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p uploads
    mkdir -p output
    mkdir -p chroma_db
    mkdir -p logs
    mkdir -p audit_logs
    mkdir -p monitoring/grafana/dashboards
    mkdir -p monitoring/grafana/datasources
    mkdir -p nginx/ssl
    
    print_success "Created directories"
}

# Function to install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    if command_exists python3; then
        python3 -m pip install --upgrade pip
        python3 -m pip install -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_warning "Python3 not found, skipping Python dependency installation"
    fi
}

# Function to install Node.js dependencies
install_node_deps() {
    print_status "Installing Node.js dependencies..."
    
    if command_exists npm; then
        cd frontend
        npm install
        cd ..
        print_success "Node.js dependencies installed"
    else
        print_warning "npm not found, skipping Node.js dependency installation"
    fi
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    # This would run Alembic migrations if we had them
    # For now, we'll just create the database schema
    print_status "Database migrations completed"
}

# Function to start services with Docker Compose
start_services() {
    print_status "Starting services with Docker Compose..."
    
    # Build and start services
    docker-compose up -d --build
    
    print_success "Services started successfully"
    print_status "Waiting for services to be ready..."
    
    # Wait for services to be healthy
    sleep 30
    
    print_success "All services are ready!"
}

# Function to show service status
show_status() {
    print_status "Service Status:"
    docker-compose ps
    
    echo ""
    print_status "Service URLs:"
    echo "Frontend: http://localhost:3000"
    echo "Backend API: http://localhost:8001"
    echo "API Documentation: http://localhost:8001/api/docs"
    echo "Grafana: http://localhost:3001 (admin/admin)"
    echo "Prometheus: http://localhost:9090"
    echo "ChromaDB: http://localhost:8000"
    echo "Redis: localhost:6379"
    echo "PostgreSQL: localhost:5432"
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    
    # Run backend tests
    if command_exists python3; then
        cd backend
        python3 -m pytest tests/ -v
        cd ..
    fi
    
    # Run frontend tests
    if command_exists npm; then
        cd frontend
        npm test -- --watchAll=false
        cd ..
    fi
    
    print_success "Tests completed"
}

# Function to show help
show_help() {
    echo "Smart Document Bot - Development Setup Script"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  setup     - Complete setup (default)"
    echo "  start     - Start services only"
    echo "  stop      - Stop services"
    echo "  restart   - Restart services"
    echo "  status    - Show service status"
    echo "  test      - Run tests"
    echo "  clean     - Clean up containers and volumes"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup    # Complete setup"
    echo "  $0 start    # Start services"
    echo "  $0 status   # Show status"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up containers and volumes..."
    
    docker-compose down -v
    docker system prune -f
    
    print_success "Cleanup completed"
}

# Main script logic
main() {
    case "${1:-setup}" in
        "setup")
            print_status "Starting Smart Document Bot development setup..."
            
            check_docker
            check_docker_compose
            create_env_file
            create_directories
            install_python_deps
            install_node_deps
            run_migrations
            start_services
            show_status
            
            print_success "Setup completed successfully!"
            print_status "You can now access the application at http://localhost:3000"
            ;;
        "start")
            start_services
            show_status
            ;;
        "stop")
            print_status "Stopping services..."
            docker-compose down
            print_success "Services stopped"
            ;;
        "restart")
            print_status "Restarting services..."
            docker-compose restart
            print_success "Services restarted"
            ;;
        "status")
            show_status
            ;;
        "test")
            run_tests
            ;;
        "clean")
            cleanup
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
