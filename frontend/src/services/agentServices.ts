import axios from 'axios';
import { API_BASE_URL } from '../config';

// Types for agent services
export interface SummarizationRequest {
  document_content: string;
  summary_type?: 'extractive' | 'abstractive' | 'executive' | 'technical';
  summary_length?: 'short' | 'medium' | 'long';
  summary_style?: 'informative' | 'narrative' | 'analytical' | 'technical';
  target_audience?: 'general' | 'professional' | 'technical' | 'executive';
  focus_areas?: string[];
  business_context?: string;
  technical_domain?: string;
}

export interface TranslationRequest {
  text: string;
  target_language: string;
  source_language?: string;
  translation_style?: 'formal' | 'informal' | 'technical' | 'literary';
  preserve_terminology?: boolean;
}

export interface DocumentTranslationRequest {
  document_content: string;
  target_language: string;
  document_type?: 'general' | 'legal' | 'technical' | 'medical' | 'financial' | 'academic';
  preserve_structure?: boolean;
}

export interface SentimentAnalysisRequest {
  text: string;
  analysis_depth?: 'basic' | 'detailed' | 'comprehensive';
}

export interface ToneAnalysisRequest {
  text: string;
  tone_categories?: string[];
}

export interface EmotionDetectionRequest {
  text: string;
  emotion_categories?: string[];
}

export interface AgentResponse {
  success: boolean;
  execution_id: string;
  confidence: number;
  rationale: string;
  [key: string]: any;
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

// Summarizer Agent Services
export const summarizerService = {
  // General summarization
  async summarizeDocument(request: SummarizationRequest): Promise<AgentResponse> {
    const response = await api.post('/api/v1/summarizer/summarize', request);
    return response.data;
  },

  // Extractive summarization
  async extractiveSummary(document_content: string, summary_length: string = 'medium', focus_areas?: string[]): Promise<AgentResponse> {
    const response = await api.post('/api/v1/summarizer/extractive', {
      document_content,
      summary_length,
      focus_areas
    });
    return response.data;
  },

  // Executive summarization
  async executiveSummary(document_content: string, business_context: string = 'general'): Promise<AgentResponse> {
    const response = await api.post('/api/v1/summarizer/executive', {
      document_content,
      business_context
    });
    return response.data;
  },

  // Technical summarization
  async technicalSummary(document_content: string, technical_domain: string = 'general'): Promise<AgentResponse> {
    const response = await api.post('/api/v1/summarizer/technical', {
      document_content,
      technical_domain
    });
    return response.data;
  },

  // Key points extraction
  async extractKeyPoints(document_content: string, point_categories?: string[]): Promise<AgentResponse> {
    const response = await api.post('/api/v1/summarizer/key-points', {
      document_content,
      point_categories
    });
    return response.data;
  },

  // Summary comparison
  async compareSummaries(summary_a: string, summary_b: string, comparison_criteria?: string[]): Promise<AgentResponse> {
    const response = await api.post('/api/v1/summarizer/compare', {
      summary_a,
      summary_b,
      comparison_criteria
    });
    return response.data;
  },

  // Summary validation
  async validateSummary(summary: string, original_content: string, validation_criteria?: string[]): Promise<AgentResponse> {
    const response = await api.post('/api/v1/summarizer/validate', {
      summary,
      original_content,
      validation_criteria
    });
    return response.data;
  },

  // Get summary types
  async getSummaryTypes(): Promise<any> {
    const response = await api.get('/api/v1/summarizer/types');
    return response.data;
  }
};

// Translator Agent Services
export const translatorService = {
  // Text translation
  async translateText(request: TranslationRequest): Promise<AgentResponse> {
    const response = await api.post('/api/v1/translator/translate', request);
    return response.data;
  },

  // Document translation
  async translateDocument(request: DocumentTranslationRequest): Promise<AgentResponse> {
    const response = await api.post('/api/v1/translator/document', request);
    return response.data;
  },

  // Language detection
  async detectLanguage(text: string): Promise<AgentResponse> {
    const response = await api.post('/api/v1/translator/detect-language', { text });
    return response.data;
  },

  // Preserve formatting
  async preserveFormatting(original_text: string, translated_text: string): Promise<AgentResponse> {
    const response = await api.post('/api/v1/translator/preserve-formatting', {
      original_text,
      translated_text
    });
    return response.data;
  },

  // Technical translation
  async technicalTranslation(technical_text: string, target_language: string, technical_domain: string = 'general'): Promise<AgentResponse> {
    const response = await api.post('/api/v1/translator/technical', {
      technical_text,
      target_language,
      technical_domain
    });
    return response.data;
  },

  // Cultural adaptation
  async culturalAdaptation(text: string, target_culture: string, adaptation_level: string = 'moderate'): Promise<AgentResponse> {
    const response = await api.post('/api/v1/translator/cultural-adaptation', {
      text,
      target_culture,
      adaptation_level
    });
    return response.data;
  },

  // Translation validation
  async validateTranslation(original_text: string, translated_text: string, target_language: string): Promise<AgentResponse> {
    const response = await api.post('/api/v1/translator/validate', {
      original_text,
      translated_text,
      target_language
    });
    return response.data;
  },

  // Create glossary
  async createGlossary(text: string, target_language: string, domain: string = 'general'): Promise<AgentResponse> {
    const response = await api.post('/api/v1/translator/glossary', {
      text,
      target_language,
      domain
    });
    return response.data;
  },

  // Get supported languages
  async getSupportedLanguages(): Promise<any> {
    const response = await api.get('/api/v1/translator/languages');
    return response.data;
  },

  // Get translation styles
  async getTranslationStyles(): Promise<any> {
    const response = await api.get('/api/v1/translator/translation-styles');
    return response.data;
  },

  // Get document types
  async getDocumentTypes(): Promise<any> {
    const response = await api.get('/api/v1/translator/document-types');
    return response.data;
  }
};

// Sentiment Analysis Agent Services
export const sentimentService = {
  // General sentiment analysis
  async analyzeSentiment(request: SentimentAnalysisRequest): Promise<AgentResponse> {
    const response = await api.post('/api/v1/sentiment/analyze', request);
    return response.data;
  },

  // Tone analysis
  async analyzeTone(request: ToneAnalysisRequest): Promise<AgentResponse> {
    const response = await api.post('/api/v1/sentiment/tone', request);
    return response.data;
  },

  // Emotion detection
  async detectEmotions(request: EmotionDetectionRequest): Promise<AgentResponse> {
    const response = await api.post('/api/v1/sentiment/emotions', request);
    return response.data;
  },

  // Sentiment tracking
  async trackSentiment(text: string, tracking_granularity: string = 'paragraph'): Promise<AgentResponse> {
    const response = await api.post('/api/v1/sentiment/tracking', {
      text,
      tracking_granularity
    });
    return response.data;
  },

  // Bias detection
  async detectBias(text: string, bias_types?: string[]): Promise<AgentResponse> {
    const response = await api.post('/api/v1/sentiment/bias', {
      text,
      bias_types
    });
    return response.data;
  },

  // Context sentiment analysis
  async contextSentiment(text: string, context_type: string = 'general'): Promise<AgentResponse> {
    const response = await api.post('/api/v1/sentiment/context', {
      text,
      context_type
    });
    return response.data;
  },

  // Sentiment comparison
  async compareSentiment(text_a: string, text_b: string, comparison_criteria?: string[]): Promise<AgentResponse> {
    const response = await api.post('/api/v1/sentiment/compare', {
      text_a,
      text_b,
      comparison_criteria
    });
    return response.data;
  },

  // Sentiment validation
  async validateSentiment(text: string, sentiment_analysis: any): Promise<AgentResponse> {
    const response = await api.post('/api/v1/sentiment/validate', {
      text,
      sentiment_analysis
    });
    return response.data;
  },

  // Get analysis depths
  async getAnalysisDepths(): Promise<any> {
    const response = await api.get('/api/v1/sentiment/analysis-depths');
    return response.data;
  },

  // Get tone categories
  async getToneCategories(): Promise<any> {
    const response = await api.get('/api/v1/sentiment/tone-categories');
    return response.data;
  },

  // Get emotion categories
  async getEmotionCategories(): Promise<any> {
    const response = await api.get('/api/v1/sentiment/emotion-categories');
    return response.data;
  },

  // Get bias types
  async getBiasTypes(): Promise<any> {
    const response = await api.get('/api/v1/sentiment/bias-types');
    return response.data;
  },

  // Get context types
  async getContextTypes(): Promise<any> {
    const response = await api.get('/api/v1/sentiment/context-types');
    return response.data;
  }
};

// Legacy agent services (keeping existing functionality)
export const agentService = {
  // Document processing
  async processDocument(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/api/v1/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get document status
  async getDocumentStatus(documentId: string): Promise<any> {
    const response = await api.get(`/api/v1/documents/${documentId}/status`);
    return response.data;
  },

  // Get document content
  async getDocumentContent(documentId: string): Promise<any> {
    const response = await api.get(`/api/v1/documents/${documentId}/content`);
    return response.data;
  },

  // Compare documents
  async compareDocuments(documentId1: string, documentId2: string, comparisonType: string = 'semantic'): Promise<any> {
    const response = await api.post('/api/v1/compare/documents', {
      document_id_1: documentId1,
      document_id_2: documentId2,
      comparison_type: comparisonType
    });
    return response.data;
  },

  // Generate QA
  async generateQA(documentId: string, questionType: string = 'factual'): Promise<any> {
    const response = await api.post('/api/v1/qa/generate', {
      document_id: documentId,
      question_type: questionType
    });
    return response.data;
  },

  // Get agent traces
  async getAgentTraces(documentId?: string): Promise<any> {
    const params = documentId ? { document_id: documentId } : {};
    const response = await api.get('/api/v1/traces', { params });
    return response.data;
  },

  // Get audit trail
  async getAuditTrail(documentId?: string): Promise<any> {
    const params = documentId ? { document_id: documentId } : {};
    const response = await api.get('/api/v1/audit/trail', { params });
    return response.data;
  },

  // Get agent capabilities
  async getAgentCapabilities(): Promise<any> {
    const response = await api.get('/api/v1/agents/capabilities');
    return response.data;
  },

  // Get system status
  async getSystemStatus(): Promise<any> {
    const response = await api.get('/api/v1/system/status');
    return response.data;
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
  }
};

export default {
  summarizer: summarizerService,
  translator: translatorService,
  sentiment: sentimentService,
  agent: agentService,
  utils: agentUtils
};
