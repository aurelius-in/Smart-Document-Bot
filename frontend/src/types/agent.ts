export interface AgentStep {
  id: string;
  name: string;
  type: string;
  status: 'pending' | 'running' | 'completed' | 'error' | 'skipped';
  startTime: Date;
  endTime?: Date;
  duration?: number;
  confidence: number;
  rationale: string;
  toolCalls: any[];
  input: any;
  output: any;
  metadata: Record<string, any>;
  error?: string;
}

export interface AgentTrace {
  id: string;
  documentId: string;
  type: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  steps?: AgentStep[];
  createdAt: Date;
  completedAt?: Date;
  duration?: number;
  error?: string;
}
