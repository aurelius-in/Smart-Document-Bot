import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

interface AgentTrace {
  trace_id: string;
  status: 'running' | 'completed' | 'failed';
  steps: AgentStep[];
  start_time: string;
  end_time?: string;
  total_duration_ms: number;
  overall_confidence: number;
  goal: string;
  context: any;
}

interface AgentStep {
  id: string;
  agent_type: string;
  action: string;
  rationale: string;
  confidence: number;
  duration_ms: number;
  timestamp: string;
  result?: any;
  error?: string;
}

interface AgenticRequest {
  goal: string;
  context?: any;
  file_path?: string;
  document_content?: string;
}

interface AgenticResponse {
  trace_id: string;
  status: string;
  confidence: number;
  duration_ms: number;
  result?: any;
  error?: string;
}

class AgentService {
  async runAgenticPipeline(request: AgenticRequest): Promise<AgenticResponse> {
    try {
      const response = await apiClient.post('/api/v1/agentic/run', request);
      return response.data;
    } catch (error) {
      console.error('Agentic pipeline error:', error);
      throw new Error('Failed to run agentic pipeline');
    }
  }

  async runSingleAgent(agentType: string, request: AgenticRequest): Promise<any> {
    try {
      const response = await apiClient.post(`/api/v1/agentic/single-agent/${agentType}`, request);
      return response.data;
    } catch (error) {
      console.error('Single agent error:', error);
      throw new Error(`Failed to run ${agentType} agent`);
    }
  }

  async startTrace(goal: string, context: any = {}): Promise<string> {
    try {
      const response = await this.runAgenticPipeline({ goal, context });
      return response.trace_id;
    } catch (error) {
      console.error('Start trace error:', error);
      throw new Error('Failed to start trace');
    }
  }

  async getTrace(traceId: string): Promise<AgentTrace> {
    try {
      const response = await apiClient.get(`/api/v1/traces/${traceId}`);
      return response.data;
    } catch (error) {
      console.error('Get trace error:', error);
      throw new Error('Failed to get trace');
    }
  }

  async getTraceUpdates(traceId: string): Promise<any> {
    try {
      const response = await apiClient.get(`/api/v1/traces/${traceId}/updates`);
      return response.data;
    } catch (error) {
      console.error('Get trace updates error:', error);
      throw new Error('Failed to get trace updates');
    }
  }

  async getTraceStatus(traceId: string): Promise<any> {
    try {
      const response = await apiClient.get(`/api/v1/traces/${traceId}/status`);
      return response.data;
    } catch (error) {
      console.error('Get trace status error:', error);
      throw new Error('Failed to get trace status');
    }
  }

  async getAllTraces(): Promise<AgentTrace[]> {
    try {
      const response = await apiClient.get('/api/v1/traces/');
      return response.data.traces || [];
    } catch (error) {
      console.error('Get all traces error:', error);
      throw new Error('Failed to get traces');
    }
  }

  async getRecentTraces(limit: number = 10): Promise<AgentTrace[]> {
    try {
      const response = await apiClient.get(`/api/v1/traces/?limit=${limit}`);
      return response.data.traces || [];
    } catch (error) {
      console.error('Get recent traces error:', error);
      throw new Error('Failed to get recent traces');
    }
  }

  async deleteTrace(traceId: string): Promise<void> {
    try {
      await apiClient.delete(`/api/v1/traces/${traceId}`);
    } catch (error) {
      console.error('Delete trace error:', error);
      throw new Error('Failed to delete trace');
    }
  }

  async getAgentHealth(): Promise<any> {
    try {
      const response = await apiClient.get('/api/v1/agentic/health');
      return response.data;
    } catch (error) {
      console.error('Get agent health error:', error);
      throw new Error('Failed to get agent health');
    }
  }

  async getAgentSummary(): Promise<any> {
    try {
      const response = await apiClient.get('/api/v1/agentic/summary');
      return response.data;
    } catch (error) {
      console.error('Get agent summary error:', error);
      throw new Error('Failed to get agent summary');
    }
  }

  async processDocument(filePath: string, goal: string): Promise<AgenticResponse> {
    try {
      const response = await this.runAgenticPipeline({
        goal,
        file_path: filePath,
      });
      return response;
    } catch (error) {
      console.error('Process document error:', error);
      throw new Error('Failed to process document');
    }
  }

  async answerQuestion(question: string, documentContent: string): Promise<any> {
    try {
      const response = await apiClient.post('/api/v1/qa/ask', {
        question,
        document_content: documentContent,
      });
      return response.data;
    } catch (error) {
      console.error('Answer question error:', error);
      throw new Error('Failed to answer question');
    }
  }

  async compareDocuments(docAPath: string, docBPath: string): Promise<any> {
    try {
      const response = await apiClient.post('/api/v1/compare/content', {
        content_a: docAPath,
        content_b: docBPath,
      });
      return response.data;
    } catch (error) {
      console.error('Compare documents error:', error);
      throw new Error('Failed to compare documents');
    }
  }

  async createAuditBundle(traceId: string, documentId?: string): Promise<any> {
    try {
      const response = await apiClient.post('/api/v1/audit/bundles', {
        trace_id: traceId,
        document_id: documentId,
      });
      return response.data;
    } catch (error) {
      console.error('Create audit bundle error:', error);
      throw new Error('Failed to create audit bundle');
    }
  }

  async downloadAuditBundle(bundleId: string, format: string = 'json'): Promise<Blob> {
    try {
      const response = await apiClient.get(`/api/v1/audit/bundles/${bundleId}/download?format=${format}`, {
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      console.error('Download audit bundle error:', error);
      throw new Error('Failed to download audit bundle');
    }
  }

  // Real-time streaming methods
  async subscribeToTraceStream(traceId: string, onUpdate: (data: any) => void): Promise<() => void> {
    const eventSource = new EventSource(`${API_BASE_URL}/api/v1/stream/agent-trace/${traceId}`);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onUpdate(data);
      } catch (error) {
        console.error('Error parsing SSE data:', error);
      }
    };

    eventSource.onerror = (error) => {
      console.error('SSE error:', error);
      eventSource.close();
    };

    // Return cleanup function
    return () => {
      eventSource.close();
    };
  }

  // Utility methods
  async isTraceComplete(traceId: string): Promise<boolean> {
    try {
      const status = await this.getTraceStatus(traceId);
      return status.is_complete;
    } catch (error) {
      console.error('Check trace completion error:', error);
      return false;
    }
  }

  async getTraceMetrics(traceId: string): Promise<any> {
    try {
      const trace = await this.getTrace(traceId);
      const totalSteps = trace.steps.length;
      const avgConfidence = trace.steps.reduce((sum, step) => sum + step.confidence, 0) / totalSteps;
      const totalDuration = trace.total_duration_ms;

      return {
        totalSteps,
        avgConfidence,
        totalDuration,
        status: trace.status,
      };
    } catch (error) {
      console.error('Get trace metrics error:', error);
      throw new Error('Failed to get trace metrics');
    }
  }
}

export const agentService = new AgentService();
