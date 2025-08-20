#!/bin/bash

# AI Document Agent Monitoring Setup Script
# This script sets up comprehensive monitoring for the AI Document Agent

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
MONITORING_DIR="./monitoring"
GRAFANA_ADMIN_USER="admin"
GRAFANA_ADMIN_PASSWORD="admin"

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

# Function to create monitoring directories
create_monitoring_directories() {
    print_status "Creating monitoring directories..."
    
    mkdir -p "$MONITORING_DIR/grafana/dashboards"
    mkdir -p "$MONITORING_DIR/grafana/datasources"
    mkdir -p "$MONITORING_DIR/grafana/provisioning/dashboards"
    mkdir -p "$MONITORING_DIR/grafana/provisioning/datasources"
    mkdir -p "$MONITORING_DIR/prometheus/rules"
    mkdir -p "$MONITORING_DIR/prometheus/alerts"
    mkdir -p "$MONITORING_DIR/alertmanager"
    mkdir -p "$MONITORING_DIR/jaeger"
    mkdir -p "$MONITORING_DIR/elasticsearch"
    mkdir -p "$MONITORING_DIR/kibana"
    mkdir -p "$MONITORING_DIR/filebeat"
    
    print_success "Monitoring directories created"
}

# Function to setup Prometheus configuration
setup_prometheus() {
    print_status "Setting up Prometheus configuration..."
    
    # Create Prometheus configuration
    cat > "$MONITORING_DIR/prometheus/prometheus.yml" << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # AI Document Agent Backend
  - job_name: 'ai-document-agent-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  # AI Document Agent Frontend
  - job_name: 'ai-document-agent-frontend'
    static_configs:
      - targets: ['frontend:3000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  # PostgreSQL
  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres:5432']
    scrape_interval: 30s

  # Redis
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 30s

  # ChromaDB
  - job_name: 'chromadb'
    static_configs:
      - targets: ['chromadb:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  # Node Exporter (system metrics)
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
    scrape_interval: 15s

  # cAdvisor (container metrics)
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
    scrape_interval: 15s

  # Jaeger (tracing)
  - job_name: 'jaeger'
    static_configs:
      - targets: ['jaeger:16686']
    scrape_interval: 30s

  # Elasticsearch
  - job_name: 'elasticsearch'
    static_configs:
      - targets: ['elasticsearch:9200']
    metrics_path: '/_prometheus/metrics'
    scrape_interval: 30s
EOF

    # Create alert rules
    cat > "$MONITORING_DIR/prometheus/rules/ai-document-agent.yml" << 'EOF'
groups:
  - name: ai-document-agent
    rules:
      # High CPU usage
      - alert: HighCPUUsage
        expr: 100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is above 80% for more than 5 minutes"

      # High memory usage
      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Memory usage is above 85% for more than 5 minutes"

      # High disk usage
      - alert: HighDiskUsage
        expr: (node_filesystem_size_bytes - node_filesystem_free_bytes) / node_filesystem_size_bytes * 100 > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High disk usage on {{ $labels.instance }}"
          description: "Disk usage is above 90% for more than 5 minutes"

      # Backend service down
      - alert: BackendServiceDown
        expr: up{job="ai-document-agent-backend"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Backend service is down"
          description: "The AI Document Agent backend service is not responding"

      # Frontend service down
      - alert: FrontendServiceDown
        expr: up{job="ai-document-agent-frontend"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Frontend service is down"
          description: "The AI Document Agent frontend service is not responding"

      # High error rate
      - alert: HighErrorRate
        expr: rate(http_requests_total{status_code=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100 > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is above 5% for more than 5 minutes"

      # Slow response time
      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow response time detected"
          description: "95th percentile response time is above 2 seconds"

      # Agent execution failures
      - alert: AgentExecutionFailures
        expr: rate(agent_execution_failures_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High agent execution failure rate"
          description: "Agent execution failure rate is above 0.1 per second"

      # Database connection issues
      - alert: DatabaseConnectionIssues
        expr: up{job="postgresql"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database connection issues"
          description: "Cannot connect to PostgreSQL database"

      # Redis connection issues
      - alert: RedisConnectionIssues
        expr: up{job="redis"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Redis connection issues"
          description: "Cannot connect to Redis cache"
EOF

    print_success "Prometheus configuration created"
}

# Function to setup Alertmanager configuration
setup_alertmanager() {
    print_status "Setting up Alertmanager configuration..."
    
    cat > "$MONITORING_DIR/alertmanager/alertmanager.yml" << 'EOF'
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/YOUR_SLACK_WEBHOOK'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'
  routes:
    - match:
        severity: critical
      receiver: 'slack.critical'
      continue: true
    - match:
        severity: warning
      receiver: 'slack.warning'

receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://127.0.0.1:5001/'

  - name: 'slack.critical'
    slack_configs:
      - channel: '#alerts-critical'
        title: '{{ template "slack.title" . }}'
        text: '{{ template "slack.text" . }}'
        send_resolved: true

  - name: 'slack.warning'
    slack_configs:
      - channel: '#alerts-warning'
        title: '{{ template "slack.title" . }}'
        text: '{{ template "slack.text" . }}'
        send_resolved: true

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']
EOF

    print_success "Alertmanager configuration created"
}

# Function to setup Grafana datasources
setup_grafana_datasources() {
    print_status "Setting up Grafana datasources..."
    
    cat > "$MONITORING_DIR/grafana/provisioning/datasources/datasources.yml" << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
    jsonData:
      timeInterval: "5s"
      queryTimeout: "60s"
      httpMethod: "POST"
    secureJsonData: {}

  - name: PostgreSQL
    type: postgres
    access: proxy
    url: postgres:5432
    database: ai_document_agent
    user: postgres
    secureJsonData:
      password: "your_password_here"
    jsonData:
      sslmode: "disable"
      maxOpenConns: 100
      maxIdleConns: 100
      connMaxLifetime: 14400

  - name: Elasticsearch
    type: elasticsearch
    access: proxy
    url: http://elasticsearch:9200
    database: "ai-document-agent-logs"
    jsonData:
      timeField: "@timestamp"
      esVersion: 7.0.0
      maxConcurrentShardRequests: 5
      logMessageField: message
      logLevelField: level

  - name: Jaeger
    type: jaeger
    access: proxy
    url: http://jaeger:16686
    jsonData:
      nodeGraph:
        enabled: true
EOF

    print_success "Grafana datasources configuration created"
}

# Function to setup Grafana dashboards provisioning
setup_grafana_dashboards() {
    print_status "Setting up Grafana dashboards provisioning..."
    
    cat > "$MONITORING_DIR/grafana/provisioning/dashboards/dashboards.yml" << 'EOF'
apiVersion: 1

providers:
  - name: 'AI Document Agent'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
EOF

    print_success "Grafana dashboards provisioning created"
}

# Function to setup Elasticsearch configuration
setup_elasticsearch() {
    print_status "Setting up Elasticsearch configuration..."
    
    cat > "$MONITORING_DIR/elasticsearch/elasticsearch.yml" << 'EOF'
cluster.name: ai-document-agent
node.name: node-1
network.host: 0.0.0.0
http.port: 9200
discovery.type: single-node
xpack.security.enabled: false
xpack.monitoring.enabled: true
xpack.monitoring.collection.enabled: true

# Memory settings
bootstrap.memory_lock: true
indices.memory.index_buffer_size: 30%

# Logging
logger.level: INFO
EOF

    print_success "Elasticsearch configuration created"
}

# Function to setup Filebeat configuration
setup_filebeat() {
    print_status "Setting up Filebeat configuration..."
    
    cat > "$MONITORING_DIR/filebeat/filebeat.yml" << 'EOF'
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/ai-document-agent/*.log
    fields:
      service: ai-document-agent
    fields_under_root: true
    multiline.pattern: '^\['
    multiline.negate: true
    multiline.match: after

  - type: log
    enabled: true
    paths:
      - /var/log/audit/*.log
    fields:
      service: audit
    fields_under_root: true

processors:
  - add_host_metadata:
      when.not.contains.tags: forwarded
  - add_cloud_metadata: ~
  - add_docker_metadata: ~
  - add_kubernetes_metadata: ~

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  indices:
    - index: "filebeat-%{[agent.version]}-%{+yyyy.MM.dd}"

setup.kibana:
  host: "kibana:5601"

setup.dashboards.enabled: true
setup.template.enabled: true
setup.template.name: "filebeat"
setup.template.pattern: "filebeat-*"
setup.template.overwrite: true
EOF

    print_success "Filebeat configuration created"
}

# Function to setup Jaeger configuration
setup_jaeger() {
    print_status "Setting up Jaeger configuration..."
    
    cat > "$MONITORING_DIR/jaeger/jaeger.yml" << 'EOF'
sampling:
  default_strategy:
    type: probabilistic
    param: 0.1

storage:
  type: elasticsearch
  options:
    es:
      server_urls: http://elasticsearch:9200
      index_prefix: jaeger
      username: ""
      password: ""

ingester:
  kafka:
    consumer:
      topic: jaeger-spans
      brokers: kafka:9092

agent:
  http_server:
    host_port: ":14268"
EOF

    print_success "Jaeger configuration created"
}

# Function to create monitoring Docker Compose
create_monitoring_compose() {
    print_status "Creating monitoring Docker Compose file..."
    
    cat > "$MONITORING_DIR/docker-compose.monitoring.yml" << 'EOF'
version: '3.8'

services:
  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: ai-doc-bot-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus:/etc/prometheus
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    restart: unless-stopped
    networks:
      - monitoring

  # Alertmanager
  alertmanager:
    image: prom/alertmanager:latest
    container_name: ai-doc-bot-alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager:/etc/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    restart: unless-stopped
    networks:
      - monitoring

  # Grafana
  grafana:
    image: grafana/grafana:latest
    container_name: ai-doc-bot-grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - ./grafana/provisioning:/etc/grafana/provisioning
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - grafana_data:/var/lib/grafana
    restart: unless-stopped
    networks:
      - monitoring

  # Node Exporter
  node-exporter:
    image: prom/node-exporter:latest
    container_name: ai-doc-bot-node-exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    restart: unless-stopped
    networks:
      - monitoring

  # cAdvisor
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: ai-doc-bot-cadvisor
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    restart: unless-stopped
    networks:
      - monitoring

  # Elasticsearch
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.17.0
    container_name: ai-doc-bot-elasticsearch
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - ./elasticsearch/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml
      - elasticsearch_data:/usr/share/elasticsearch/data
    restart: unless-stopped
    networks:
      - monitoring

  # Kibana
  kibana:
    image: docker.elastic.co/kibana/kibana:7.17.0
    container_name: ai-doc-bot-kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
    volumes:
      - kibana_data:/usr/share/kibana/data
    restart: unless-stopped
    networks:
      - monitoring
    depends_on:
      - elasticsearch

  # Filebeat
  filebeat:
    image: docker.elastic.co/beats/filebeat:7.17.0
    container_name: ai-doc-bot-filebeat
    user: root
    volumes:
      - ./filebeat/filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/log/ai-document-agent:/var/log/ai-document-agent:ro
      - /var/log/audit:/var/log/audit:ro
    restart: unless-stopped
    networks:
      - monitoring
    depends_on:
      - elasticsearch

  # Jaeger
  jaeger:
    image: jaegertracing/all-in-one:latest
    container_name: ai-doc-bot-jaeger
    environment:
      - COLLECTOR_OTLP_ENABLED=true
    ports:
      - "16686:16686"
      - "14268:14268"
      - "14250:14250"
    restart: unless-stopped
    networks:
      - monitoring

volumes:
  prometheus_data:
  grafana_data:
  elasticsearch_data:
  kibana_data:

networks:
  monitoring:
    driver: bridge
EOF

    print_success "Monitoring Docker Compose file created"
}

# Function to start monitoring services
start_monitoring_services() {
    print_status "Starting monitoring services..."
    
    cd "$MONITORING_DIR"
    docker-compose -f docker-compose.monitoring.yml up -d
    
    print_success "Monitoring services started"
    print_status "Waiting for services to be ready..."
    sleep 30
    
    print_success "Monitoring services are ready!"
}

# Function to show monitoring status
show_monitoring_status() {
    print_status "Monitoring Service Status:"
    cd "$MONITORING_DIR"
    docker-compose -f docker-compose.monitoring.yml ps
    
    echo ""
    print_status "Monitoring URLs:"
    echo "Grafana: http://localhost:3001 (admin/admin)"
    echo "Prometheus: http://localhost:9090"
    echo "Alertmanager: http://localhost:9093"
    echo "Kibana: http://localhost:5601"
    echo "Jaeger: http://localhost:16686"
    echo "Elasticsearch: http://localhost:9200"
    echo "cAdvisor: http://localhost:8080"
    echo "Node Exporter: http://localhost:9100"
}

# Function to stop monitoring services
stop_monitoring_services() {
    print_status "Stopping monitoring services..."
    
    cd "$MONITORING_DIR"
    docker-compose -f docker-compose.monitoring.yml down
    
    print_success "Monitoring services stopped"
}

# Function to show help
show_help() {
    echo "AI Document Agent Monitoring Setup Script"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  setup     - Complete monitoring setup (default)"
    echo "  start     - Start monitoring services only"
    echo "  stop      - Stop monitoring services"
    echo "  restart   - Restart monitoring services"
    echo "  status    - Show monitoring service status"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup    # Complete setup"
    echo "  $0 start    # Start services"
    echo "  $0 status   # Show status"
}

# Main script logic
main() {
    case "${1:-setup}" in
        "setup")
            print_status "Starting AI Document Agent monitoring setup..."
            
            check_docker
            create_monitoring_directories
            setup_prometheus
            setup_alertmanager
            setup_grafana_datasources
            setup_grafana_dashboards
            setup_elasticsearch
            setup_filebeat
            setup_jaeger
            create_monitoring_compose
            start_monitoring_services
            show_monitoring_status
            
            print_success "Monitoring setup completed successfully!"
            print_status "You can now access Grafana at http://localhost:3001"
            ;;
        "start")
            start_monitoring_services
            show_monitoring_status
            ;;
        "stop")
            stop_monitoring_services
            ;;
        "restart")
            stop_monitoring_services
            start_monitoring_services
            show_monitoring_status
            ;;
        "status")
            show_monitoring_status
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
