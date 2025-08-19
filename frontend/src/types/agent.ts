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
  // Additional properties for UI compatibility
  name?: string;
  type?: string;
  rationale?: string;
  toolCalls?: any[];
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
  // Additional properties for UI compatibility
  type?: string;
  createdAt?: string;
  completedAt?: string;
  duration?: number;
  error?: string;
}
