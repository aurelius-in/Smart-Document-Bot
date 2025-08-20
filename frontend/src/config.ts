// Configuration for the AI Document Agent frontend

export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export const CONFIG = {
  API_BASE_URL,
  APP_NAME: 'AI Document Agent',
  VERSION: '1.0.0',
  DEFAULT_TIMEOUT: 30000,
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  SUPPORTED_FILE_TYPES: [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'text/csv'
  ]
};

export default CONFIG;
