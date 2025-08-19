# AI Document Agent

An intelligent document processing and analysis platform powered by AI agents for regulatory compliance and business intelligence.

## Overview

AI Document Agent is a comprehensive platform that leverages multiple AI agents to process, analyze, and extract insights from regulatory documents. The system provides real-time document processing, entity extraction, risk assessment, and compliance monitoring capabilities.

![aiDa Dashboard Demo](tab1.gif)

![aiDa Processing Pipeline Demo](tab2.gif)

![aiDa Document Viewer Demo](tab3.gif)

![aiDa Agent Traces & Analytics Demo](tab4.gif)

![aiDa Q&A Chat Demo](tab5.gif)

## Features

- **Multi-Agent Processing**: Orchestrated AI agents for document ingestion, classification, entity extraction, and analysis
- **Real-time Processing**: Live document processing with progress tracking and status updates
- **Compliance Monitoring**: Automated regulatory compliance checking and risk assessment
- **Interactive Analytics**: Comprehensive analytics dashboard with performance metrics
- **Audit Trail**: Complete audit logging for compliance and transparency
- **Agent Trace Monitoring**: Real-time monitoring of AI agent execution and performance

## Architecture

The platform consists of:

- **Frontend**: React TypeScript application with Material-UI components
- **Backend**: FastAPI Python server with agent orchestration
- **AI Agents**: Specialized agents for different document processing tasks
- **Database**: PostgreSQL with vector embeddings for semantic search
- **Monitoring**: OpenTelemetry integration for observability

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AI-Document-Agent
   ```

2. **Install dependencies**
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd ../frontend
   npm install
   ```

3. **Start the servers**
   ```bash
   # Backend (from project root)
   python simple_server.py
   
   # Frontend (from frontend directory)
   npm start
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001

## Demo Mode

The application includes a comprehensive demo mode that showcases:
- Document upload and processing pipeline
- Real-time agent execution monitoring
- Interactive document viewer with entity highlighting
- Analytics dashboard with performance metrics
- Audit trail and compliance reporting

## Agent System

The AI Document Agent platform uses a sophisticated multi-agent system:

- **OrchestratorAgent**: Coordinates the overall document processing workflow
- **IngestionAgent**: Handles document upload and initial processing
- **ClassifierAgent**: Categorizes documents by type and content
- **EntityAgent**: Extracts key entities and information
- **RiskAgent**: Assesses compliance risks and issues
- **QAAgent**: Provides intelligent Q&A capabilities
- **CompareAgent**: Compares documents for similarities and differences
- **AuditAgent**: Monitors and logs all system activities
- **SummarizerAgent**: Creates document summaries and insights
- **TranslatorAgent**: Handles multi-language document processing
- **SentimentAnalysisAgent**: Analyzes document sentiment and tone

## Configuration

The application can be configured through environment variables:

- `REACT_APP_API_BASE_URL`: Backend API URL (default: http://localhost:8001)
- `OPENAI_API_KEY`: OpenAI API key for AI agent functionality
- `DATABASE_URL`: PostgreSQL database connection string

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
