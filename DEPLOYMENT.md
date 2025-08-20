# 🚀 AI Document Agent - Deployment Guide

## Overview

This document provides comprehensive deployment instructions for the AI Document Agent platform across different environments, from development to production. The deployment strategy follows enterprise-grade practices with security, scalability, and reliability as core principles.

## 🎯 Deployment Strategy

### **Environment Tiers**
- **Development**: Local development with hot-reload
- **Staging**: Production-like environment for testing
- **Production**: High-availability, scalable deployment
- **Disaster Recovery**: Backup and failover systems

### **Deployment Models**
- **Docker Compose**: For development and small-scale deployments
- **Kubernetes**: For production and enterprise deployments
- **Cloud Native**: AWS, Azure, GCP deployment options
- **Hybrid**: On-premise with cloud integration

## 🐳 Docker Compose Deployment

### **Development Environment**

```bash
# Clone repository
git clone https://github.com/your-org/ai-document-agent.git
cd ai-document-agent

# Copy environment configuration
cp .env.example .env

# Configure environment variables
nano .env

# Start development services
docker-compose -f docker-compose.dev.yml up -d

# Initialize database
./scripts/init-db.sh

# Access services
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### **Production Environment**

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# With monitoring stack
docker-compose -f docker-compose.prod.yml -f docker-compose.monitoring.yml up -d

# Health check
docker-compose ps
curl http://localhost:8000/health
```

## ☸️ Kubernetes Deployment

### **Prerequisites**
```bash
# Kubernetes cluster (minikube, kind, or cloud provider)
kubectl version --client
helm version

# Install required tools
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.0/cert-manager.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.7.1/deploy/static/provider/cloud/deploy.yaml
```

### **Namespace Setup**
```bash
# Create namespace
kubectl create namespace ai-document-agent

# Set context
kubectl config set-context --current --namespace=ai-document-agent
```

### **Secrets Management**
```bash
# Create secrets
kubectl create secret generic ai-document-agent-secrets \
  --from-literal=postgres-password=your-secure-password \
  --from-literal=redis-password=your-redis-password \
  --from-literal=jwt-secret=your-jwt-secret \
  --from-literal=openai-api-key=your-openai-key

# Create config maps
kubectl create configmap ai-document-agent-config \
  --from-file=config/app.yaml \
  --from-file=config/agents.yaml
```

### **Database Deployment**
```bash
# Deploy PostgreSQL
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgres bitnami/postgresql \
  --set auth.postgresPassword=your-secure-password \
  --set primary.persistence.size=10Gi \
  --set architecture=standalone

# Deploy Redis
helm install redis bitnami/redis \
  --set auth.password=your-redis-password \
  --set architecture=standalone \
  --set master.persistence.size=5Gi
```

### **Application Deployment**
```bash
# Deploy core application
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmaps.yaml
kubectl apply -f k8s/services.yaml
kubectl apply -f k8s/deployments.yaml
kubectl apply -f k8s/ingress.yaml

# Deploy monitoring stack
kubectl apply -f k8s/monitoring/
```

### **Verification**
```bash
# Check deployment status
kubectl get pods
kubectl get services
kubectl get ingress

# Check logs
kubectl logs -f deployment/backend
kubectl logs -f deployment/frontend

# Port forward for local access
kubectl port-forward service/backend 8000:8000
kubectl port-forward service/frontend 3000:3000
```

## ☁️ Cloud Deployment

### **AWS Deployment**

#### **ECS Fargate**
```bash
# Deploy with AWS CLI
aws ecs create-cluster --cluster-name ai-document-agent

# Create task definitions
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster ai-document-agent \
  --service-name backend \
  --task-definition backend:1 \
  --desired-count 2 \
  --launch-type FARGATE
```

#### **EKS (Elastic Kubernetes Service)**
```bash
# Create EKS cluster
eksctl create cluster \
  --name ai-document-agent \
  --region us-west-2 \
  --nodegroup-name workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 1 \
  --nodes-max 5

# Deploy application
kubectl apply -f k8s/
```

### **Azure Deployment**

#### **AKS (Azure Kubernetes Service)**
```bash
# Create AKS cluster
az aks create \
  --resource-group ai-document-agent-rg \
  --name ai-document-agent-cluster \
  --node-count 3 \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group ai-document-agent-rg --name ai-document-agent-cluster

# Deploy application
kubectl apply -f k8s/
```

### **Google Cloud Deployment**

#### **GKE (Google Kubernetes Engine)**
```bash
# Create GKE cluster
gcloud container clusters create ai-document-agent \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-2 \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 5

# Get credentials
gcloud container clusters get-credentials ai-document-agent --zone us-central1-a

# Deploy application
kubectl apply -f k8s/
```

## 🔒 Security Configuration

### **SSL/TLS Setup**
```bash
# Generate SSL certificates
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/private.key \
  -out nginx/ssl/certificate.crt

# Configure Nginx with SSL
kubectl apply -f k8s/ssl/
```

### **Network Security**
```bash
# Configure network policies
kubectl apply -f k8s/network-policies/

# Set up firewall rules
gcloud compute firewall-rules create ai-document-agent \
  --allow tcp:80,tcp:443,tcp:22 \
  --source-ranges 0.0.0.0/0 \
  --target-tags ai-document-agent
```

### **Secrets Management**
```bash
# Use external secrets manager
helm install external-secrets external-secrets/external-secrets \
  --set installCRDs=true

# Configure secrets
kubectl apply -f k8s/external-secrets/
```

## 📊 Monitoring & Observability

### **Prometheus & Grafana**
```bash
# Deploy monitoring stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --set grafana.enabled=true \
  --set prometheus.enabled=true

# Access Grafana
kubectl port-forward service/prometheus-grafana 3001:80
# Username: admin, Password: prom-operator
```

### **ELK Stack**
```bash
# Deploy Elasticsearch
helm repo add elastic https://helm.elastic.co
helm install elasticsearch elastic/elasticsearch \
  --set replicas=3

# Deploy Kibana
helm install kibana elastic/kibana \
  --set service.type=LoadBalancer

# Deploy Filebeat
helm install filebeat elastic/filebeat
```

### **Jaeger Tracing**
```bash
# Deploy Jaeger
helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
helm install jaeger jaegertracing/jaeger \
  --set storage.type=elasticsearch \
  --set storage.options.es.server-urls=http://elasticsearch-master:9200
```

## 🔄 CI/CD Pipeline

### **GitHub Actions**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build and push Docker images
        run: |
          docker build -t ai-document-agent/backend:latest ./backend
          docker build -t ai-document-agent/frontend:latest ./frontend
          docker push ai-document-agent/backend:latest
          docker push ai-document-agent/frontend:latest
      
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/backend backend=ai-document-agent/backend:latest
          kubectl set image deployment/frontend frontend=ai-document-agent/frontend:latest
          kubectl rollout status deployment/backend
          kubectl rollout status deployment/frontend
```

### **ArgoCD**
```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Create application
kubectl apply -f argocd/application.yaml
```

## 📈 Scaling & Performance

### **Horizontal Pod Autoscaler**
```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### **Database Scaling**
```bash
# Scale PostgreSQL
helm upgrade postgres bitnami/postgresql \
  --set readReplicas.persistence.size=10Gi \
  --set readReplicas.replicaCount=2

# Scale Redis
helm upgrade redis bitnami/redis \
  --set architecture=replication \
  --set replica.replicaCount=3
```

## 🔄 Backup & Recovery

### **Database Backup**
```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# PostgreSQL backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_DIR/postgres_$DATE.sql

# Redis backup
redis-cli -h $REDIS_HOST BGSAVE

# File storage backup
tar -czf $BACKUP_DIR/files_$DATE.tar.gz /data/uploads/

# Upload to cloud storage
aws s3 cp $BACKUP_DIR/postgres_$DATE.sql s3://ai-document-agent-backups/
aws s3 cp $BACKUP_DIR/files_$DATE.tar.gz s3://ai-document-agent-backups/
```

### **Disaster Recovery**
```bash
# Restore from backup
pg_restore -h $DB_HOST -U $DB_USER -d $DB_NAME $BACKUP_DIR/postgres_$DATE.sql

# Failover procedure
kubectl apply -f k8s/disaster-recovery/failover.yaml
```

## 🧪 Testing Deployment

### **Load Testing**
```bash
# Deploy load testing
kubectl apply -f k8s/load-testing/

# Run load test
kubectl exec -it load-test-pod -- locust -f /app/locustfile.py \
  --host=http://backend-service:8000
```

### **Health Checks**
```bash
# Automated health checks
curl -f http://localhost:8000/health || exit 1
curl -f http://localhost:3000/ || exit 1

# Database connectivity
pg_isready -h $DB_HOST -p $DB_PORT || exit 1

# Redis connectivity
redis-cli -h $REDIS_HOST ping || exit 1
```

## 📋 Deployment Checklist

### **Pre-Deployment**
- [ ] Environment variables configured
- [ ] Secrets and certificates prepared
- [ ] Database migrations ready
- [ ] Load balancer configured
- [ ] Monitoring stack deployed
- [ ] Backup strategy implemented

### **Deployment**
- [ ] Database deployed and initialized
- [ ] Application services deployed
- [ ] Ingress and SSL configured
- [ ] Health checks passing
- [ ] Monitoring dashboards accessible
- [ ] Logs being collected

### **Post-Deployment**
- [ ] Performance testing completed
- [ ] Security scan passed
- [ ] Documentation updated
- [ ] Team notified
- [ ] Rollback plan tested
- [ ] Monitoring alerts configured

## 🚨 Troubleshooting

### **Common Issues**
```bash
# Pod not starting
kubectl describe pod <pod-name>
kubectl logs <pod-name>

# Service not accessible
kubectl get endpoints
kubectl describe service <service-name>

# Database connection issues
kubectl exec -it <pod-name> -- nc -zv <db-host> <db-port>

# Memory issues
kubectl top pods
kubectl describe node <node-name>
```

### **Debug Commands**
```bash
# Get cluster info
kubectl cluster-info
kubectl get nodes

# Check resource usage
kubectl top nodes
kubectl top pods

# View events
kubectl get events --sort-by=.metadata.creationTimestamp

# Port forwarding for debugging
kubectl port-forward service/backend 8000:8000
kubectl port-forward service/grafana 3001:80
```

