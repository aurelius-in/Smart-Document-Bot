import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { toast } from 'react-hot-toast';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';
const API_TIMEOUT = 30000; // 30 seconds

// API Response Types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: 'success' | 'error';
  timestamp: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

export interface UploadResponse {
  fileId: string;
  filename: string;
  size: number;
  status: 'uploaded' | 'processing' | 'completed' | 'error';
  message?: string;
}

export interface DocumentInfo {
  id: string;
  filename: string;
  size: number;
  type: string;
  status: 'uploaded' | 'processing' | 'completed' | 'error';
  uploadedAt: string;
  processedAt?: string;
  metadata?: any;
  extractedText?: string;
  entities?: any[];
  confidence?: number;
}

export interface ComparisonRequest {
  documentAId: string;
  documentBId: string;
  comparisonType: 'semantic' | 'structural' | 'compliance' | 'risk';
}

export interface ComparisonResult {
  id: string;
  documentAId: string;
  documentBId: string;
  comparisonType: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  semanticDiffs: any[];
  riskDelta: any;
  complianceImpact: any;
  confidence: number;
  duration: number;
  createdAt: string;
}

export interface AgentTrace {
  id: string;
  documentId: string;
  documentName: string;
  status: 'running' | 'completed' | 'error' | 'paused';
  steps: AgentStep[];
  startTime: string;
  endTime?: string;
  totalDuration?: number;
  overallConfidence?: number;
  summary?: string;
}

export interface AgentStep {
  id: string;
  stepNumber: number;
  agentType: string;
  tool: string;
  input: any;
  output: any;
  status: 'pending' | 'running' | 'completed' | 'error';
  startTime: string;
  endTime?: string;
  duration?: number;
  confidence?: number;
  error?: string;
  metadata?: any;
}

export interface AuditEvent {
  id: string;
  timestamp: string;
  userId: string;
  userName: string;
  action: string;
  resource: string;
  resourceId: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: 'user_action' | 'system_event' | 'security' | 'compliance' | 'data_access';
  details: string;
  ipAddress: string;
  userAgent: string;
  sessionId: string;
  metadata?: any;
  complianceTags?: string[];
}

// API Service Class
class ApiService {
  private api: AxiosInstance;
  private authToken: string | null = null;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: API_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
    this.loadAuthToken();
  }

  private setupInterceptors() {
    // Request interceptor
    this.api.interceptors.request.use(
      (config) => {
        // Add auth token if available
        if (this.authToken) {
          config.headers.Authorization = `Bearer ${this.authToken}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.api.interceptors.response.use(
      (response: AxiosResponse) => {
        return response;
      },
      (error) => {
        this.handleApiError(error);
        return Promise.reject(error);
      }
    );
  }

  private handleApiError(error: any) {
    const message = error.response?.data?.message || error.message || 'An error occurred';
    
    // Don't show toast for 401 errors (handled by auth)
    if (error.response?.status !== 401) {
      toast.error(message);
    }

    // Handle specific error cases
    switch (error.response?.status) {
      case 401:
        this.handleUnauthorized();
        break;
      case 403:
        toast.error('Access denied. You do not have permission to perform this action.');
        break;
      case 404:
        toast.error('Resource not found.');
        break;
      case 500:
        toast.error('Server error. Please try again later.');
        break;
    }
  }

  private handleUnauthorized() {
    this.clearAuthToken();
    // Redirect to login or show login modal
    window.location.href = '/login';
  }

  private loadAuthToken() {
    this.authToken = localStorage.getItem('auth_token');
  }

  private saveAuthToken(token: string) {
    this.authToken = token;
    localStorage.setItem('auth_token', token);
  }

  private clearAuthToken() {
    this.authToken = null;
    localStorage.removeItem('auth_token');
  }

  // Authentication
  async login(email: string, password: string): Promise<{ token: string; user: any }> {
    const response = await this.api.post('/api/v1/auth/login', { email, password });
    const { token, user } = response.data;
    this.saveAuthToken(token);
    return { token, user };
  }

  async logout(): Promise<void> {
    try {
      await this.api.post('/api/v1/auth/logout');
    } finally {
      this.clearAuthToken();
    }
  }

  async getCurrentUser(): Promise<any> {
    const response = await this.api.get('/api/v1/auth/me');
    return response.data;
  }

  // Document Upload
  async uploadDocument(file: File, onProgress?: (progress: number) => void): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const config: AxiosRequestConfig = {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    };

    const response = await this.api.post('/api/v1/documents/upload', formData, config);
    return response.data;
  }

  async getDocuments(page: number = 1, limit: number = 20): Promise<PaginatedResponse<DocumentInfo>> {
    const response = await this.api.get('/api/v1/documents', {
      params: { page, limit }
    });
    return response.data;
  }

  async getDocument(id: string): Promise<DocumentInfo> {
    const response = await this.api.get(`/api/v1/documents/${id}`);
    return response.data;
  }

  async deleteDocument(id: string): Promise<void> {
    await this.api.delete(`/api/v1/documents/${id}`);
  }

  // Document Comparison
  async compareDocuments(request: ComparisonRequest): Promise<ComparisonResult> {
    const response = await this.api.post('/api/v1/compare/documents', request);
    return response.data;
  }

  async getComparisonResult(id: string): Promise<ComparisonResult> {
    const response = await this.api.get(`/api/v1/compare/documents/${id}`);
    return response.data;
  }

  async getComparisonHistory(page: number = 1, limit: number = 20): Promise<PaginatedResponse<ComparisonResult>> {
    const response = await this.api.get('/api/v1/compare/history', {
      params: { page, limit }
    });
    return response.data;
  }

  // Agent Traces
  async startAgentTrace(documentId: string): Promise<AgentTrace> {
    const response = await this.api.post('/api/v1/traces/start', { documentId });
    return response.data;
  }

  async getAgentTraces(page: number = 1, limit: number = 20): Promise<PaginatedResponse<AgentTrace>> {
    const response = await this.api.get('/api/v1/traces', {
      params: { page, limit }
    });
    return response.data;
  }

  async getAgentTrace(id: string): Promise<AgentTrace> {
    const response = await this.api.get(`/api/v1/traces/${id}`);
    return response.data;
  }

  async getTraceUpdates(id: string): Promise<AgentTrace> {
    const response = await this.api.get(`/api/v1/traces/${id}/updates`);
    return response.data;
  }

  // Audit Trail
  async getAuditEvents(
    page: number = 1,
    limit: number = 50,
    filters?: {
      severity?: string;
      category?: string;
      userId?: string;
      startDate?: string;
      endDate?: string;
      search?: string;
    }
  ): Promise<PaginatedResponse<AuditEvent>> {
    const response = await this.api.get('/api/v1/audit/events', {
      params: { page, limit, ...filters }
    });
    return response.data;
  }

  async getAuditEvent(id: string): Promise<AuditEvent> {
    const response = await this.api.get(`/api/v1/audit/events/${id}`);
    return response.data;
  }

  async exportAuditLog(filters?: any): Promise<Blob> {
    const response = await this.api.get('/api/v1/audit/export', {
      params: filters,
      responseType: 'blob'
    });
    return response.data;
  }

  // Q&A System
  async askQuestion(documentId: string, question: string): Promise<any> {
    const response = await this.api.post('/api/v1/qa/ask', {
      documentId,
      question
    });
    return response.data;
  }

  async getQaHistory(page: number = 1, limit: number = 20): Promise<PaginatedResponse<any>> {
    const response = await this.api.get('/api/v1/qa/history', {
      params: { page, limit }
    });
    return response.data;
  }

  // Analytics
  async getAnalytics(timeRange: string = '7d'): Promise<any> {
    const response = await this.api.get('/api/v1/analytics', {
      params: { timeRange }
    });
    return response.data;
  }

  async getDocumentAnalytics(documentId: string): Promise<any> {
    const response = await this.api.get(`/api/v1/analytics/documents/${documentId}`);
    return response.data;
  }

  // Health Check
  async healthCheck(): Promise<any> {
    const response = await this.api.get('/health');
    return response.data;
  }

  // Memory Service
  async getMemoryStats(): Promise<any> {
    const response = await this.api.get('/api/v1/memory/stats');
    return response.data;
  }

  async searchMemory(query: string, k: number = 5): Promise<any[]> {
    const response = await this.api.get('/api/v1/memory/search', {
      params: { query, k }
    });
    return response.data;
  }

  // Settings
  async getSettings(): Promise<any> {
    const response = await this.api.get('/api/v1/settings');
    return response.data;
  }

  async updateSettings(settings: any): Promise<any> {
    const response = await this.api.put('/api/v1/settings', settings);
    return response.data;
  }

  // Utility methods
  isAuthenticated(): boolean {
    return !!this.authToken;
  }

  getAuthToken(): string | null {
    return this.authToken;
  }

  // WebSocket connection for real-time updates
  createWebSocketConnection(traceId?: string): WebSocket {
    const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8001';
    const url = traceId ? `${wsUrl}/ws/traces/${traceId}` : `${wsUrl}/ws`;
    
    const ws = new WebSocket(url);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };
    
    return ws;
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;
