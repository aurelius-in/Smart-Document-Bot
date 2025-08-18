# Smart Document Bot 🤖📄

A comprehensive AI-powered document processing and analysis system that uses advanced language models and agentic workflows to extract insights, assess risks, and ensure compliance from regulatory documents.

## 🌟 Features

### 🤖 **Intelligent Agent System**
- **Orchestrator Agent**: Coordinates complex document processing workflows
- **Ingestion Agent**: OCR, PDF extraction, and text normalization
- **Classifier Agent**: Document type classification and content analysis
- **Entity Agent**: Named entity recognition and clause extraction
- **Risk Agent**: Compliance, financial, and operational risk assessment
- **QA Agent**: Automated question generation and answer extraction
- **Compare Agent**: Multi-dimensional document comparison
- **Audit Agent**: Comprehensive audit trail generation

### 📊 **Advanced Analytics**
- Real-time document processing status tracking
- Performance metrics and system monitoring
- Comprehensive audit trails and compliance reporting
- Risk scoring and assessment dashboards
- Document similarity analysis and comparison

### 🔒 **Security & Compliance**
- Role-based access control (RBAC)
- Comprehensive audit logging
- GDPR, SOX, HIPAA compliance frameworks
- Data encryption and secure storage
- Policy enforcement with Open Policy Agent (OPA)

### 🚀 **Scalable Architecture**
- Microservices architecture with Docker containers
- PostgreSQL database with vector search capabilities
- Redis caching for performance optimization
- ChromaDB for vector embeddings and similarity search
- Elasticsearch for advanced logging and search

### 📈 **Monitoring & Observability**
- Prometheus metrics collection
- Grafana dashboards for visualization
- Jaeger distributed tracing
- ELK stack for log aggregation
- Real-time system health monitoring

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Agent System  │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (LLM Agents)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │    │   PostgreSQL    │    │   ChromaDB      │
│   (Load Bal.)   │    │   (Database)    │    │   (Vector DB)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Monitoring    │    │   Redis Cache   │    │   Elasticsearch │
│   (Prometheus)  │    │   (Session)     │    │   (Logging)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

### **Backend**
- **FastAPI**: High-performance web framework
- **SQLAlchemy**: Database ORM and migrations
- **PostgreSQL**: Primary database with pgvector
- **Redis**: Caching and session management
- **ChromaDB**: Vector database for embeddings
- **OpenAI GPT-4**: Large language model integration

### **Frontend**
- **React 18**: Modern UI framework
- **TypeScript**: Type-safe development
- **Material-UI (MUI)**: Component library
- **React Query**: Server state management
- **React Router**: Client-side routing
- **Recharts**: Data visualization

### **Infrastructure**
- **Docker & Docker Compose**: Containerization
- **Nginx**: Reverse proxy and load balancing
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboards
- **Elasticsearch**: Log aggregation
- **Kibana**: Log visualization
- **Jaeger**: Distributed tracing

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API key
- At least 8GB RAM and 20GB disk space

### 1. Clone the Repository
```bash
git clone https://github.com/aurelius-in/Smart-Document-Bot.git
cd Smart-Document-Bot
```

### 2. Configure Environment
```bash
# Copy and edit environment configuration
cp .env.example .env

# Update the following variables in .env:
OPENAI_API_KEY=your-openai-api-key-here
SECRET_KEY=your-secret-key-here
```

### 3. Deploy the System
```bash
# Make deployment script executable (Linux/Mac)
chmod +x scripts/deploy.sh

# Deploy the complete system
./scripts/deploy.sh deploy
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Grafana Dashboard**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Kibana**: http://localhost:5601

## 📖 Usage Guide

### Document Upload and Processing

1. **Upload Documents**
   - Navigate to the Upload page
   - Drag and drop or select files (PDF, DOCX, TXT)
   - Documents are automatically processed by the agent system

2. **Monitor Processing**
   - View real-time processing status
   - Track agent execution progress
   - Monitor system performance metrics

3. **Analyze Results**
   - Review extracted entities and clauses
   - Assess risk scores and compliance status
   - Generate Q&A pairs for document understanding

### Document Comparison

1. **Select Documents**
   - Choose two documents for comparison
   - Select comparison criteria (semantic, structural, compliance)

2. **Run Comparison**
   - Execute multi-dimensional comparison
   - View similarity scores and differences
   - Analyze risk changes between versions

### Audit and Compliance

1. **Generate Audit Trails**
   - Create comprehensive audit reports
   - Track all system activities and changes
   - Export compliance documentation

2. **Monitor Compliance**
   - View compliance framework assessments
   - Track policy violations and risks
   - Generate regulatory reports

## 🔧 Configuration

### Environment Variables

```bash
# Application Settings
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM Configuration
OPENAI_API_KEY=your-openai-api-key
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=4000

# Database Configuration
DATABASE_URL=postgresql://postgres:password@postgres:5432/smart_doc_bot
REDIS_URL=redis://redis:6379
CHROMA_PERSIST_DIRECTORY=/app/chroma_db

# Monitoring
ENABLE_MONITORING=true
ENABLE_CACHING=true
ENABLE_RATE_LIMITING=true
```

### Agent Configuration

Each agent can be configured independently:

```python
# Agent-specific settings
AGENT_TIMEOUT=300
AGENT_MAX_RETRIES=3
AGENT_CONFIDENCE_THRESHOLD=0.7

# Workflow settings
WORKFLOW_MAX_STAGES=10
WORKFLOW_PARALLEL_EXECUTION=true
WORKFLOW_MONITORING_INTERVAL=5
```

## 🧪 Testing

### Run Integration Tests
```bash
# Run all tests
cd backend
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_integration.py -v
python -m pytest tests/test_agents.py -v
python -m pytest tests/test_api.py -v
```

### Run Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

## 📊 Monitoring and Observability

### Metrics Dashboard
- **System Performance**: CPU, memory, disk usage
- **Agent Performance**: Execution times, success rates, confidence scores
- **API Performance**: Response times, error rates, throughput
- **Database Performance**: Query times, connection pool status

### Logging
- **Application Logs**: Structured logging with correlation IDs
- **Access Logs**: API request/response logging
- **Error Logs**: Exception tracking and alerting
- **Audit Logs**: Security and compliance event logging

### Alerting
- **System Alerts**: High resource usage, service failures
- **Performance Alerts**: Slow response times, high error rates
- **Security Alerts**: Failed authentication, policy violations
- **Business Alerts**: Low confidence scores, processing failures

## 🔒 Security Features

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- Multi-factor authentication support
- Session management and timeout

### Data Protection
- Data encryption at rest and in transit
- PII detection and redaction
- Secure file upload and storage
- Audit trail for all data access

### Compliance
- GDPR compliance features
- SOX compliance reporting
- HIPAA data protection
- ISO 27001 security controls

## 🚀 Deployment Options

### Development
```bash
# Local development setup
./scripts/deploy.sh start
```

### Production
```bash
# Production deployment with SSL
./scripts/deploy.sh deploy
```

### Kubernetes
```bash
# Deploy to Kubernetes cluster
kubectl apply -f k8s/
```

## 📈 Performance Optimization

### Caching Strategy
- Redis caching for frequently accessed data
- Database query result caching
- Static asset caching with Nginx
- Agent result caching for similar documents

### Database Optimization
- Connection pooling
- Query optimization and indexing
- Read replicas for scaling
- Database partitioning for large datasets

### Agent Optimization
- Parallel agent execution
- Result caching and reuse
- Batch processing for multiple documents
- Resource usage monitoring and limits

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Standards
- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Write comprehensive tests
- Update documentation for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- [API Documentation](http://localhost:8000/docs)
- [User Guide](docs/user-guide.md)
- [Developer Guide](docs/developer-guide.md)
- [Deployment Guide](docs/deployment-guide.md)

### Community
- [GitHub Issues](https://github.com/aurelius-in/Smart-Document-Bot/issues)
- [Discussions](https://github.com/aurelius-in/Smart-Document-Bot/discussions)
- [Wiki](https://github.com/aurelius-in/Smart-Document-Bot/wiki)

### Contact
- Email: support@smartdocbot.com
- Discord: [Smart Document Bot Community](https://discord.gg/smartdocbot)

## 🙏 Acknowledgments

- OpenAI for providing the GPT-4 language model
- FastAPI community for the excellent web framework
- React and Material-UI teams for the frontend tools
- All contributors and users of this project

---

**Smart Document Bot** - Transforming document processing with AI-powered intelligence 🤖✨
