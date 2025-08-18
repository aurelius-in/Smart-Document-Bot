import axios from 'axios';
import { API_BASE_URL } from '../config';

// Types for unified agent service
export interface AgentExecutionRequest {
  agent_type: string;
  document_content: string;
  goal: string;
  parameters?: Record<string, any>;
}

export interface BatchAgentExecutionRequest {
  executions: AgentExecutionRequest[];
}

export interface AgentCapabilityRequest {
  agent_type: string;
  capability: string;
  parameters?: Record<string, any>;
}

export interface AgentResponse {
  success: boolean;
  execution_id: string;
  agent_type: string;
  result: any;
  confidence: number;
  rationale: string;
}

export interface BatchAgentResponse {
  success: boolean;
  batch_id: string;
  results: AgentResponse[];
}

export interface AgentCapability {
  name: string;
  description: string;
  capabilities: string[];
  status: string;
  version: string;
  supported_formats: string[];
  execution_time: string;
  memory_usage: string;
}

export interface AgentCapabilitiesResponse {
  success: boolean;
  total_agents: number;
  capabilities: Record<string, AgentCapability>;
}

export interface AgentStatusResponse {
  success: boolean;
  workflow_status: any;
  agent_statistics: {
    total_executions: number;
    successful_executions: number;
    failed_executions: number;
    active_processing: number;
  };
  recent_executions: any[];
}

export interface AgentHealthResponse {
  success: boolean;
  health: {
    status: string;
    timestamp: string;
    agents: Record<string, string>;
  };
}

// Base API configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    throw error;
  }
);

// Unified Agent Service
export const unifiedAgentService = {
  // Execute a single agent
  async executeAgent(request: AgentExecutionRequest): Promise<AgentResponse> {
    const response = await api.post('/api/v1/agents/execute', request);
    return response.data;
  },

  // Execute multiple agents in batch
  async batchExecuteAgents(request: BatchAgentExecutionRequest): Promise<BatchAgentResponse> {
    const response = await api.post('/api/v1/agents/batch-execute', request);
    return response.data;
  },

  // Get all agent capabilities
  async getAgentCapabilities(): Promise<AgentCapabilitiesResponse> {
    const response = await api.get('/api/v1/agents/capabilities');
    return response.data;
  },

  // Get agent status
  async getAgentStatus(): Promise<AgentStatusResponse> {
    const response = await api.get('/api/v1/agents/status');
    return response.data;
  },

  // Execute specific agent capability
  async executeAgentCapability(request: AgentCapabilityRequest): Promise<any> {
    const response = await api.post('/api/v1/agents/capability', request);
    return response.data;
  },

  // Get agent health
  async getAgentHealth(): Promise<AgentHealthResponse> {
    const response = await api.get('/api/v1/agents/health');
    return response.data;
  },

  // Cleanup old executions
  async cleanupOldExecutions(maxAgeHours: number = 24): Promise<any> {
    const response = await api.delete(`/api/v1/agents/cleanup?max_age_hours=${maxAgeHours}`);
    return response.data;
  },

  // Convenience methods for specific agent types
  async summarizeDocument(
    content: string,
    summaryType: string = 'abstractive',
    parameters?: Record<string, any>
  ): Promise<AgentResponse> {
    return this.executeAgent({
      agent_type: 'summarizer',
      document_content: content,
      goal: `Generate ${summaryType} summary`,
      parameters: {
        summary_type: summaryType,
        ...parameters
      }
    });
  },

  async translateDocument(
    content: string,
    targetLanguage: string,
    parameters?: Record<string, any>
  ): Promise<AgentResponse> {
    return this.executeAgent({
      agent_type: 'translator',
      document_content: content,
      goal: `Translate to ${targetLanguage}`,
      parameters: {
        target_language: targetLanguage,
        ...parameters
      }
    });
  },

  async analyzeSentiment(
    content: string,
    analysisDepth: string = 'comprehensive',
    parameters?: Record<string, any>
  ): Promise<AgentResponse> {
    return this.executeAgent({
      agent_type: 'sentiment',
      document_content: content,
      goal: `Analyze sentiment with ${analysisDepth} depth`,
      parameters: {
        analysis_depth: analysisDepth,
        ...parameters
      }
    });
  },

  async classifyDocument(
    content: string,
    parameters?: Record<string, any>
  ): Promise<AgentResponse> {
    return this.executeAgent({
      agent_type: 'classifier',
      document_content: content,
      goal: 'Classify document type and domain',
      parameters
    });
  },

  async extractEntities(
    content: string,
    parameters?: Record<string, any>
  ): Promise<AgentResponse> {
    return this.executeAgent({
      agent_type: 'entity',
      document_content: content,
      goal: 'Extract named entities and key information',
      parameters
    });
  },

  async assessRisks(
    content: string,
    parameters?: Record<string, any>
  ): Promise<AgentResponse> {
    return this.executeAgent({
      agent_type: 'risk',
      document_content: content,
      goal: 'Assess compliance, financial, and operational risks',
      parameters
    });
  },

  async generateQA(
    content: string,
    parameters?: Record<string, any>
  ): Promise<AgentResponse> {
    return this.executeAgent({
      agent_type: 'qa',
      document_content: content,
      goal: 'Generate questions and answers about the document',
      parameters
    });
  },

  async compareDocuments(
    contentA: string,
    contentB: string,
    parameters?: Record<string, any>
  ): Promise<AgentResponse> {
    return this.executeAgent({
      agent_type: 'compare',
      document_content: `Document A: ${contentA}\n\nDocument B: ${contentB}`,
      goal: 'Compare documents for differences and changes',
      parameters
    });
  },

  async generateAuditTrail(
    content: string,
    parameters?: Record<string, any>
  ): Promise<AgentResponse> {
    return this.executeAgent({
      agent_type: 'audit',
      document_content: content,
      goal: 'Generate comprehensive audit trail',
      parameters
    });
  },

  // Batch processing convenience methods
  async processDocumentComprehensive(
    content: string,
    includeAgents: string[] = ['classifier', 'entity', 'risk', 'summarizer', 'sentiment']
  ): Promise<BatchAgentResponse> {
    const executions: AgentExecutionRequest[] = includeAgents.map(agentType => ({
      agent_type: agentType,
      document_content: content,
      goal: `Process document with ${agentType} agent`,
      parameters: {}
    }));

    return this.batchExecuteAgents({ executions });
  },

  async analyzeDocumentSentiment(
    content: string,
    includeAnalysis: string[] = ['sentiment', 'tone', 'emotions', 'bias']
  ): Promise<BatchAgentResponse> {
    const executions: AgentExecutionRequest[] = includeAnalysis.map(analysisType => ({
      agent_type: 'sentiment',
      document_content: content,
      goal: `Perform ${analysisType} analysis`,
      parameters: { analysis_type: analysisType }
    }));

    return this.batchExecuteAgents({ executions });
  },

  async translateDocumentMultiLanguage(
    content: string,
    targetLanguages: string[]
  ): Promise<BatchAgentResponse> {
    const executions: AgentExecutionRequest[] = targetLanguages.map(language => ({
      agent_type: 'translator',
      document_content: content,
      goal: `Translate to ${language}`,
      parameters: { target_language: language }
    }));

    return this.batchExecuteAgents({ executions });
  }
};

// Utility functions
export const agentUtils = {
  // Format confidence score
  formatConfidence(confidence: number): string {
    return `${(confidence * 100).toFixed(1)}%`;
  },

  // Get status color
  getStatusColor(status: string): string {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'success';
      case 'processing':
        return 'warning';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  },

  // Format execution time
  formatExecutionTime(ms: number): string {
    if (ms < 1000) {
      return `${ms}ms`;
    } else if (ms < 60000) {
      return `${(ms / 1000).toFixed(1)}s`;
    } else {
      return `${(ms / 60000).toFixed(1)}m`;
    }
  },

  // Validate text length
  validateTextLength(text: string, maxLength: number = 10000): boolean {
    return text.length <= maxLength;
  },

  // Truncate text for preview
  truncateText(text: string, maxLength: number = 200): string {
    if (text.length <= maxLength) {
      return text;
    }
    return text.substring(0, maxLength) + '...';
  },

  // Get agent icon
  getAgentIcon(agentType: string): string {
    const iconMap: Record<string, string> = {
      'summarizer': '📝',
      'translator': '🌐',
      'sentiment': '😊',
      'classifier': '🏷️',
      'entity': '🔍',
      'risk': '⚠️',
      'qa': '❓',
      'compare': '⚖️',
      'audit': '📋',
      'orchestrator': '🎯'
    };
    return iconMap[agentType] || '🤖';
  },

  // Get agent color
  getAgentColor(agentType: string): string {
    const colorMap: Record<string, string> = {
      'summarizer': '#4CAF50',
      'translator': '#2196F3',
      'sentiment': '#FF9800',
      'classifier': '#9C27B0',
      'entity': '#607D8B',
      'risk': '#F44336',
      'qa': '#00BCD4',
      'compare': '#795548',
      'audit': '#FF5722',
      'orchestrator': '#3F51B5'
    };
    return colorMap[agentType] || '#757575';
  },

  // Format agent result for display
  formatAgentResult(result: any, agentType: string): string {
    if (!result) return 'No result available';

    switch (agentType) {
      case 'summarizer':
        return result.summary || result.executive_summary || result.technical_summary || JSON.stringify(result);
      case 'translator':
        return result.translated_text || result.technical_translation || JSON.stringify(result);
      case 'sentiment':
        return `${result.overall_sentiment} (${this.formatConfidence(result.confidence_score || 0)})`;
      case 'classifier':
        return `${result.document_type} - ${result.domain}`;
      case 'entity':
        return `${result.entities?.length || 0} entities found`;
      case 'risk':
        return `${result.risk_level} risk level`;
      default:
        return JSON.stringify(result, null, 2);
    }
  }
};

export default unifiedAgentService;
