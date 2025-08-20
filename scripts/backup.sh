#!/bin/bash

# AI Document Agent Backup Script
# This script creates comprehensive backups of the entire system

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

# Configuration
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="ai_document_agent_backup_$DATE"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

# Database configuration
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-ai_document_agent}"
DB_USER="${DB_USER:-postgres}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to create backup directory
create_backup_directory() {
    print_status "Creating backup directory..."
    mkdir -p "$BACKUP_PATH"
    mkdir -p "$BACKUP_PATH/database"
    mkdir -p "$BACKUP_PATH/files"
    mkdir -p "$BACKUP_PATH/config"
    mkdir -p "$BACKUP_PATH/logs"
    print_success "Backup directory created: $BACKUP_PATH"
}

# Function to backup database
backup_database() {
    print_status "Backing up PostgreSQL database..."
    
    if command_exists pg_dump; then
        # Prompt for password if not provided
        if [ -z "$DB_PASSWORD" ]; then
            echo -n "Enter database password: "
            read -s DB_PASSWORD
            echo
        fi
        
        # Set password environment variable
        export PGPASSWORD="$DB_PASSWORD"
        
        # Create database dump
        pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
            --verbose --clean --no-owner --no-privileges \
            --file="$BACKUP_PATH/database/full_backup.sql"
        
        # Create schema-only backup
        pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
            --verbose --schema-only --no-owner --no-privileges \
            --file="$BACKUP_PATH/database/schema_only.sql"
        
        # Create data-only backup
        pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
            --verbose --data-only --no-owner --no-privileges \
            --file="$BACKUP_PATH/database/data_only.sql"
        
        print_success "Database backup completed"
    else
        print_error "pg_dump not found. Please install PostgreSQL client tools."
        return 1
    fi
}

# Function to backup uploaded files
backup_files() {
    print_status "Backing up uploaded files..."
    
    if [ -d "./uploads" ]; then
        tar -czf "$BACKUP_PATH/files/uploads.tar.gz" -C . uploads/
        print_success "Uploaded files backed up"
    else
        print_warning "Uploads directory not found, skipping"
    fi
    
    if [ -d "./output" ]; then
        tar -czf "$BACKUP_PATH/files/output.tar.gz" -C . output/
        print_success "Output files backed up"
    else
        print_warning "Output directory not found, skipping"
    fi
    
    if [ -d "./chroma_db" ]; then
        tar -czf "$BACKUP_PATH/files/chroma_db.tar.gz" -C . chroma_db/
        print_success "ChromaDB vector database backed up"
    else
        print_warning "ChromaDB directory not found, skipping"
    fi
}

# Function to backup configuration files
backup_config() {
    print_status "Backing up configuration files..."
    
    # Backup environment files
    if [ -f ".env" ]; then
        cp .env "$BACKUP_PATH/config/"
        print_success "Environment file backed up"
    fi
    
    if [ -f "backend/.env" ]; then
        cp backend/.env "$BACKUP_PATH/config/"
        print_success "Backend environment file backed up"
    fi
    
    # Backup configuration files
    if [ -d "backend/app/core" ]; then
        tar -czf "$BACKUP_PATH/config/backend_config.tar.gz" -C backend/app core/
        print_success "Backend configuration backed up"
    fi
    
    if [ -d "frontend/src/config" ]; then
        tar -czf "$BACKUP_PATH/config/frontend_config.tar.gz" -C frontend/src config/
        print_success "Frontend configuration backed up"
    fi
    
    # Backup Docker configuration
    if [ -f "docker-compose.yml" ]; then
        cp docker-compose.yml "$BACKUP_PATH/config/"
        print_success "Docker Compose configuration backed up"
    fi
    
    # Backup Nginx configuration
    if [ -d "nginx" ]; then
        tar -czf "$BACKUP_PATH/config/nginx_config.tar.gz" -C . nginx/
        print_success "Nginx configuration backed up"
    fi
    
    # Backup monitoring configuration
    if [ -d "monitoring" ]; then
        tar -czf "$BACKUP_PATH/config/monitoring_config.tar.gz" -C . monitoring/
        print_success "Monitoring configuration backed up"
    fi
}

# Function to backup logs
backup_logs() {
    print_status "Backing up log files..."
    
    if [ -d "./logs" ]; then
        tar -czf "$BACKUP_PATH/logs/application_logs.tar.gz" -C . logs/
        print_success "Application logs backed up"
    else
        print_warning "Logs directory not found, skipping"
    fi
    
    if [ -d "./audit_logs" ]; then
        tar -czf "$BACKUP_PATH/logs/audit_logs.tar.gz" -C . audit_logs/
        print_success "Audit logs backed up"
    else
        print_warning "Audit logs directory not found, skipping"
    fi
}

# Function to backup code (optional)
backup_code() {
    print_status "Backing up source code..."
    
    # Create a git archive if this is a git repository
    if [ -d ".git" ]; then
        git archive --format=tar.gz --output="$BACKUP_PATH/source_code.tar.gz" HEAD
        print_success "Source code backed up (git archive)"
    else
        # Fallback: create a tar of the entire project
        tar -czf "$BACKUP_PATH/source_code.tar.gz" \
            --exclude="$BACKUP_DIR" \
            --exclude="node_modules" \
            --exclude="__pycache__" \
            --exclude="*.pyc" \
            --exclude=".git" \
            --exclude="uploads" \
            --exclude="output" \
            --exclude="chroma_db" \
            --exclude="logs" \
            --exclude="audit_logs" \
            .
        print_success "Source code backed up (full project)"
    fi
}

# Function to create backup manifest
create_manifest() {
    print_status "Creating backup manifest..."
    
    cat > "$BACKUP_PATH/backup_manifest.txt" << EOF
AI Document Agent Backup Manifest
=================================
Backup Date: $(date)
Backup Name: $BACKUP_NAME
System: $(uname -a)

Backup Contents:
$(find "$BACKUP_PATH" -type f -name "*.tar.gz" -o -name "*.sql" -o -name "*.env" | sort)

Database Information:
- Host: $DB_HOST
- Port: $DB_PORT
- Database: $DB_NAME
- User: $DB_USER

Backup Size: $(du -sh "$BACKUP_PATH" | cut -f1)

Restore Instructions:
1. Extract the backup: tar -xzf $BACKUP_NAME.tar.gz
2. Restore database: psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME < database/full_backup.sql
3. Restore files: tar -xzf files/*.tar.gz
4. Restore configuration: tar -xzf config/*.tar.gz
5. Restart services: docker-compose up -d

EOF
    
    print_success "Backup manifest created"
}

# Function to compress backup
compress_backup() {
    print_status "Compressing backup..."
    
    cd "$BACKUP_DIR"
    tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
    cd - > /dev/null
    
    # Remove uncompressed directory
    rm -rf "$BACKUP_PATH"
    
    print_success "Backup compressed: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
}

# Function to verify backup
verify_backup() {
    print_status "Verifying backup..."
    
    BACKUP_FILE="$BACKUP_DIR/${BACKUP_NAME}.tar.gz"
    
    if [ -f "$BACKUP_FILE" ]; then
        # Check if tar file is valid
        if tar -tzf "$BACKUP_FILE" > /dev/null 2>&1; then
            print_success "Backup verification successful"
            print_status "Backup size: $(du -sh "$BACKUP_FILE" | cut -f1)"
        else
            print_error "Backup verification failed - tar file is corrupted"
            return 1
        fi
    else
        print_error "Backup file not found"
        return 1
    fi
}

# Function to cleanup old backups
cleanup_old_backups() {
    print_status "Cleaning up old backups..."
    
    # Keep backups for 30 days
    find "$BACKUP_DIR" -name "ai_document_agent_backup_*.tar.gz" -mtime +30 -delete
    
    print_success "Old backups cleaned up"
}

# Function to show backup status
show_backup_status() {
    print_status "Backup Status:"
    echo "Backup Directory: $BACKUP_DIR"
    echo "Latest Backup: $BACKUP_NAME"
    echo "Backup Size: $(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1 || echo 'N/A')"
    echo ""
    echo "Recent Backups:"
    ls -la "$BACKUP_DIR"/*.tar.gz 2>/dev/null | tail -5 || echo "No backups found"
}

# Function to restore backup
restore_backup() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        print_error "No backup file specified"
        echo "Usage: $0 restore <backup_file.tar.gz>"
        return 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        print_error "Backup file not found: $backup_file"
        return 1
    fi
    
    print_status "Restoring backup: $backup_file"
    
    # Extract backup
    local temp_dir=$(mktemp -d)
    tar -xzf "$backup_file" -C "$temp_dir"
    
    # Restore database
    if [ -f "$temp_dir"/*/database/full_backup.sql ]; then
        print_status "Restoring database..."
        if [ -z "$DB_PASSWORD" ]; then
            echo -n "Enter database password: "
            read -s DB_PASSWORD
            echo
        fi
        export PGPASSWORD="$DB_PASSWORD"
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" < "$temp_dir"/*/database/full_backup.sql
        print_success "Database restored"
    fi
    
    # Restore files
    if [ -f "$temp_dir"/*/files/uploads.tar.gz ]; then
        print_status "Restoring uploaded files..."
        tar -xzf "$temp_dir"/*/files/uploads.tar.gz -C .
        print_success "Uploaded files restored"
    fi
    
    if [ -f "$temp_dir"/*/files/output.tar.gz ]; then
        print_status "Restoring output files..."
        tar -xzf "$temp_dir"/*/files/output.tar.gz -C .
        print_success "Output files restored"
    fi
    
    if [ -f "$temp_dir"/*/files/chroma_db.tar.gz ]; then
        print_status "Restoring ChromaDB..."
        tar -xzf "$temp_dir"/*/files/chroma_db.tar.gz -C .
        print_success "ChromaDB restored"
    fi
    
    # Cleanup
    rm -rf "$temp_dir"
    
    print_success "Backup restoration completed"
}

# Function to show help
show_help() {
    echo "AI Document Agent Backup Script"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  backup     - Create a full backup (default)"
    echo "  restore    - Restore from backup"
    echo "  status     - Show backup status"
    echo "  cleanup    - Clean up old backups"
    echo "  help       - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 backup                    # Create backup"
    echo "  $0 restore backup.tar.gz     # Restore from backup"
    echo "  $0 status                    # Show backup status"
    echo "  $0 cleanup                   # Clean old backups"
    echo ""
    echo "Environment Variables:"
    echo "  DB_HOST     - Database host (default: localhost)"
    echo "  DB_PORT     - Database port (default: 5432)"
    echo "  DB_NAME     - Database name (default: ai_document_agent)"
    echo "  DB_USER     - Database user (default: postgres)"
    echo "  DB_PASSWORD - Database password (will prompt if not set)"
}

# Main script logic
main() {
    case "${1:-backup}" in
        "backup")
            print_status "Starting AI Document Agent backup..."
            
            create_backup_directory
            backup_database
            backup_files
            backup_config
            backup_logs
            backup_code
            create_manifest
            compress_backup
            verify_backup
            cleanup_old_backups
            
            print_success "Backup completed successfully!"
            print_status "Backup location: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
            ;;
        "restore")
            restore_backup "$2"
            ;;
        "status")
            show_backup_status
            ;;
        "cleanup")
            cleanup_old_backups
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
