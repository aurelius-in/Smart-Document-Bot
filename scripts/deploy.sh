#!/bin/bash

# Smart Document Bot Deployment Script
# This script deploys the complete Smart Document Bot system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="smart-doc-bot"
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
BACKUP_DIR="./backups"
LOGS_DIR="./logs"
UPLOADS_DIR="./uploads"
CHROMA_DIR="./chroma_db"

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

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Docker
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$LOGS_DIR"
    mkdir -p "$UPLOADS_DIR"
    mkdir -p "$CHROMA_DIR"
    mkdir -p "./config"
    mkdir -p "./monitoring/grafana/dashboards"
    mkdir -p "./monitoring/grafana/datasources"
    mkdir -p "./monitoring/filebeat"
    mkdir -p "./nginx/ssl"
    mkdir -p "./nginx/webroot"
    
    print_success "Directories created"
}

# Function to setup environment file
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f "$ENV_FILE" ]; then
        cat > "$ENV_FILE" << EOF
# Smart Document Bot Environment Configuration

# Application Settings
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=$(openssl rand -hex 32)
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM Configuration
OPENAI_API_KEY=your-openai-api-key-here
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=4000

# Database Configuration
DATABASE_URL=postgresql://postgres:password@postgres:5432/smart_doc_bot
REDIS_URL=redis://redis:6379
CHROMA_PERSIST_DIRECTORY=/app/chroma_db

# File Upload Settings
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=52428800
ALLOWED_FILE_TYPES=.pdf,.docx,.txt,.csv,.xlsx

# Agent Settings
AGENT_TIMEOUT=300
AGENT_MAX_RETRIES=3
AGENT_CONFIDENCE_THRESHOLD=0.7

# Workflow Settings
WORKFLOW_MAX_STAGES=10
WORKFLOW_PARALLEL_EXECUTION=true
WORKFLOW_MONITORING_INTERVAL=5

# Memory Settings
MEMORY_TTL=3600
MEMORY_MAX_SIZE=1000
VECTOR_SIMILARITY_THRESHOLD=0.8

# Monitoring Settings
ENABLE_MONITORING=true
METRICS_PORT=9090
LOG_LEVEL=INFO

# Audit Settings
AUDIT_ENABLED=true
AUDIT_RETENTION_DAYS=90
AUDIT_ENCRYPTION_ENABLED=false

# Compliance Settings
COMPLIANCE_FRAMEWORKS=GDPR,SOX,HIPAA,ISO27001
COMPLIANCE_SCAN_ENABLED=true

# Performance Settings
ENABLE_CACHING=true
CACHE_TTL=300
ENABLE_RATE_LIMITING=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Notification Settings
ENABLE_NOTIFICATIONS=false
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=

# External Services
ENABLE_OCR=true
OCR_SERVICE_URL=
ENABLE_TRANSLATION=false
TRANSLATION_SERVICE_URL=

# Development Settings
ENABLE_SWAGGER=true
ENABLE_RELOAD=true
ENABLE_DEBUG_TOOLBAR=false

# Testing Settings
TESTING=false
TEST_DATABASE_URL=sqlite:///./test.db
EOF
        print_warning "Created .env file. Please update the OPENAI_API_KEY and other settings as needed."
    else
        print_status "Environment file already exists"
    fi
}

# Function to create configuration files
create_config_files() {
    print_status "Creating configuration files..."
    
    # Create ChromaDB auth configuration
    cat > "./config/chroma_auth.json" << EOF
{
    "admin": {
        "password": "admin_password_here"
    },
    "users": {
        "smart_doc_bot": {
            "password": "smart_doc_bot_password_here"
        }
    }
}
EOF
    
    # Create Nginx configuration
    cat > "./nginx/nginx.conf" << EOF
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }
    
    upstream frontend {
        server frontend:3000;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
        
        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        # Backend API
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
        
        # Metrics endpoint
        location /metrics {
            proxy_pass http://backend/metrics;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }
    }
}
EOF
    
    # Create Filebeat configuration
    cat > "./monitoring/filebeat/filebeat.yml" << EOF
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/smart-doc-bot/*.log
  fields:
    service: smart-doc-bot
  fields_under_root: true

- type: container
  paths:
    - '/var/lib/docker/containers/*/*.log'
  processors:
    - add_docker_metadata:
        host: "unix:///var/run/docker.sock"

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  indices:
    - index: "filebeat-%{[agent.version]}-%{+yyyy.MM.dd}"

setup.kibana:
  host: "kibana:5601"

processors:
  - add_host_metadata: ~
  - add_cloud_metadata: ~
EOF
    
    # Create Grafana datasource configuration
    cat > "./monitoring/grafana/datasources/prometheus.yml" << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF
    
    # Create Grafana dashboard configuration
    cat > "./monitoring/grafana/dashboards/dashboards.yml" << EOF
apiVersion: 1

providers:
  - name: 'Smart Document Bot'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
EOF
    
    print_success "Configuration files created"
}

# Function to build and start services
deploy_services() {
    print_status "Building and starting services..."
    
    # Build images
    print_status "Building Docker images..."
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    
    # Start services
    print_status "Starting services..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    print_success "Services started"
}

# Function to wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for PostgreSQL
    print_status "Waiting for PostgreSQL..."
    until docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U postgres -d smart_doc_bot; do
        sleep 2
    done
    
    # Wait for Redis
    print_status "Waiting for Redis..."
    until docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping; do
        sleep 2
    done
    
    # Wait for ChromaDB
    print_status "Waiting for ChromaDB..."
    until curl -f http://localhost:8001/api/v1/heartbeat; do
        sleep 2
    done
    
    # Wait for Backend
    print_status "Waiting for Backend API..."
    until curl -f http://localhost:8000/health; do
        sleep 2
    done
    
    # Wait for Frontend
    print_status "Waiting for Frontend..."
    until curl -f http://localhost:3000; do
        sleep 2
    done
    
    # Wait for Elasticsearch
    print_status "Waiting for Elasticsearch..."
    until curl -f http://localhost:9200/_cluster/health; do
        sleep 5
    done
    
    # Wait for Grafana
    print_status "Waiting for Grafana..."
    until curl -f http://localhost:3001/api/health; do
        sleep 2
    done
    
    print_success "All services are ready"
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    # Wait a bit more for database to be fully ready
    sleep 5
    
    # Run migrations (if any)
    docker-compose -f "$COMPOSE_FILE" exec -T backend python -m alembic upgrade head || true
    
    print_success "Database migrations completed"
}

# Function to initialize the system
initialize_system() {
    print_status "Initializing system..."
    
    # Create initial admin user (if needed)
    docker-compose -f "$COMPOSE_FILE" exec -T backend python -c "
from app.core.config import get_settings
from app.services.auth_service import AuthService
from app.models.user import UserCreate

settings = get_settings()
auth_service = AuthService()

# Create admin user if it doesn't exist
try:
    admin_user = UserCreate(
        email='admin@smartdocbot.com',
        password='admin123',
        full_name='System Administrator',
        is_active=True,
        is_superuser=True
    )
    auth_service.create_user(admin_user)
    print('Admin user created successfully')
except Exception as e:
    print(f'Admin user already exists or error: {e}')
" || true
    
    print_success "System initialization completed"
}

# Function to check service health
check_health() {
    print_status "Checking service health..."
    
    local failed_services=()
    
    # Check each service
    services=("backend" "frontend" "postgres" "redis" "chromadb" "elasticsearch" "grafana" "prometheus")
    
    for service in "${services[@]}"; do
        if docker-compose -f "$COMPOSE_FILE" ps "$service" | grep -q "Up"; then
            print_success "$service is running"
        else
            print_error "$service is not running"
            failed_services+=("$service")
        fi
    done
    
    if [ ${#failed_services[@]} -eq 0 ]; then
        print_success "All services are healthy"
    else
        print_error "The following services failed: ${failed_services[*]}"
        return 1
    fi
}

# Function to display service URLs
display_urls() {
    print_status "Service URLs:"
    echo -e "${GREEN}Frontend:${NC} http://localhost:3000"
    echo -e "${GREEN}Backend API:${NC} http://localhost:8000"
    echo -e "${GREEN}API Documentation:${NC} http://localhost:8000/docs"
    echo -e "${GREEN}Grafana Dashboard:${NC} http://localhost:3001 (admin/admin)"
    echo -e "${GREEN}Prometheus:${NC} http://localhost:9090"
    echo -e "${GREEN}Kibana:${NC} http://localhost:5601"
    echo -e "${GREEN}Jaeger Tracing:${NC} http://localhost:16686"
    echo -e "${GREEN}cAdvisor:${NC} http://localhost:8080"
    echo -e "${GREEN}ChromaDB:${NC} http://localhost:8001"
    echo -e "${GREEN}Open Policy Agent:${NC} http://localhost:8181"
}

# Function to create backup
create_backup() {
    print_status "Creating backup..."
    
    local backup_name="backup-$(date +%Y%m%d-%H%M%S)"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    mkdir -p "$backup_path"
    
    # Backup PostgreSQL
    docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_dump -U postgres smart_doc_bot > "$backup_path/database.sql"
    
    # Backup uploads
    cp -r "$UPLOADS_DIR" "$backup_path/"
    
    # Backup ChromaDB
    cp -r "$CHROMA_DIR" "$backup_path/"
    
    # Backup configuration
    cp "$ENV_FILE" "$backup_path/"
    cp -r "./config" "$backup_path/"
    
    # Create archive
    tar -czf "$backup_path.tar.gz" -C "$BACKUP_DIR" "$backup_name"
    rm -rf "$backup_path"
    
    print_success "Backup created: $backup_path.tar.gz"
}

# Function to show logs
show_logs() {
    local service=${1:-"backend"}
    print_status "Showing logs for $service..."
    docker-compose -f "$COMPOSE_FILE" logs -f "$service"
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    docker-compose -f "$COMPOSE_FILE" down
    print_success "Services stopped"
}

# Function to restart services
restart_services() {
    print_status "Restarting services..."
    docker-compose -f "$COMPOSE_FILE" restart
    print_success "Services restarted"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up..."
    docker-compose -f "$COMPOSE_FILE" down -v
    docker system prune -f
    print_success "Cleanup completed"
}

# Function to show help
show_help() {
    echo "Smart Document Bot Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy      - Deploy the complete system"
    echo "  start       - Start services"
    echo "  stop        - Stop services"
    echo "  restart     - Restart services"
    echo "  status      - Check service status"
    echo "  logs [SVC]  - Show logs (default: backend)"
    echo "  backup      - Create backup"
    echo "  cleanup     - Clean up everything"
    echo "  help        - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 deploy"
    echo "  $0 logs frontend"
    echo "  $0 status"
}

# Main script logic
main() {
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            create_directories
            setup_environment
            create_config_files
            deploy_services
            wait_for_services
            run_migrations
            initialize_system
            check_health
            display_urls
            print_success "Deployment completed successfully!"
            ;;
        "start")
            deploy_services
            wait_for_services
            check_health
            display_urls
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            wait_for_services
            check_health
            ;;
        "status")
            check_health
            display_urls
            ;;
        "logs")
            show_logs "$2"
            ;;
        "backup")
            create_backup
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
