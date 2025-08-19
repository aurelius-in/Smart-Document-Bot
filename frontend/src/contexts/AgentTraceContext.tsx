import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { agentService } from '../services/agentService';

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

interface AgentTraceContextType {
  currentTrace: AgentTrace | null;
  traces: AgentTrace[];
  isLoading: boolean;
  error: string | null;
  startTrace: (goal: string, context?: any) => Promise<string>;
  updateTrace: (traceId: string, step: AgentStep) => void;
  completeTrace: (traceId: string, result: any) => void;
  getTrace: (traceId: string) => AgentTrace | null;
  clearCurrentTrace: () => void;
  subscribeToTrace: (traceId: string, callback: (trace: AgentTrace) => void) => () => void;
}

const AgentTraceContext = createContext<AgentTraceContextType | undefined>(undefined);

export const useAgentTrace = () => {
  const context = useContext(AgentTraceContext);
  if (context === undefined) {
    throw new Error('useAgentTrace must be used within an AgentTraceProvider');
  }
  return context;
};

interface AgentTraceProviderProps {
  children: ReactNode;
}

export const AgentTraceProvider: React.FC<AgentTraceProviderProps> = ({ children }) => {
  const [currentTrace, setCurrentTrace] = useState<AgentTrace | null>(null);
  const [traces, setTraces] = useState<AgentTrace[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [subscribers, setSubscribers] = useState<Map<string, Set<(trace: AgentTrace) => void>>>(new Map());

  useEffect(() => {
    // Load recent traces on mount
    loadRecentTraces();
  }, []);

  const loadRecentTraces = async () => {
    try {
      setIsLoading(true);
      const recentTraces = await agentService.getRecentTraces();
      setTraces(recentTraces);
    } catch (error) {
      console.error('Failed to load recent traces:', error);
      setError('Failed to load recent traces');
    } finally {
      setIsLoading(false);
    }
  };

  const startTrace = async (goal: string, context: any = {}): Promise<string> => {
    try {
      setIsLoading(true);
      setError(null);

      const traceId = await agentService.startTrace(goal, context);
      
      const newTrace: AgentTrace = {
        trace_id: traceId,
        status: 'running',
        steps: [],
        start_time: new Date().toISOString(),
        total_duration_ms: 0,
        overall_confidence: 0,
        goal,
        context,
      };

      setCurrentTrace(newTrace);
      setTraces(prev => [newTrace, ...prev]);

      // Subscribe to real-time updates
      subscribeToRealTimeUpdates(traceId);

      return traceId;
    } catch (error) {
      console.error('Failed to start trace:', error);
      setError('Failed to start trace');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const updateTrace = (traceId: string, step: AgentStep) => {
    setTraces(prev => prev.map(trace => {
      if (trace.trace_id === traceId) {
        const updatedTrace = {
          ...trace,
          steps: [...trace.steps, step],
          total_duration_ms: trace.steps.reduce((sum, s) => sum + s.duration_ms, 0) + step.duration_ms,
        };
        
        // Update current trace if it's the active one
        if (currentTrace?.trace_id === traceId) {
          setCurrentTrace(updatedTrace);
        }

        // Notify subscribers
        const traceSubscribers = subscribers.get(traceId);
        if (traceSubscribers) {
          traceSubscribers.forEach(callback => callback(updatedTrace));
        }

        return updatedTrace;
      }
      return trace;
    }));
  };

  const completeTrace = (traceId: string, result: any) => {
    setTraces(prev => prev.map(trace => {
      if (trace.trace_id === traceId) {
        const completedTrace = {
          ...trace,
          status: 'completed' as const,
          end_time: new Date().toISOString(),
          overall_confidence: result.confidence || 0,
        };

        // Update current trace if it's the active one
        if (currentTrace?.trace_id === traceId) {
          setCurrentTrace(completedTrace);
        }

        // Notify subscribers
        const traceSubscribers = subscribers.get(traceId);
        if (traceSubscribers) {
          traceSubscribers.forEach(callback => callback(completedTrace));
        }

        return completedTrace;
      }
      return trace;
    }));
  };

  const getTrace = (traceId: string): AgentTrace | null => {
    return traces.find(trace => trace.trace_id === traceId) || null;
  };

  const clearCurrentTrace = () => {
    setCurrentTrace(null);
  };

  const subscribeToTrace = (traceId: string, callback: (trace: AgentTrace) => void) => {
    setSubscribers(prev => {
      const newSubscribers = new Map(prev);
      const traceSubscribers = new Set(newSubscribers.get(traceId) || []);
      traceSubscribers.add(callback);
      newSubscribers.set(traceId, traceSubscribers);
      return newSubscribers;
    });

    // Return unsubscribe function
    return () => {
      setSubscribers(prev => {
        const newSubscribers = new Map(prev);
        const traceSubscribers = new Set(newSubscribers.get(traceId) || []);
        traceSubscribers.delete(callback);
        if (traceSubscribers.size === 0) {
          newSubscribers.delete(traceId);
        } else {
          newSubscribers.set(traceId, traceSubscribers);
        }
        return newSubscribers;
      });
    };
  };

  const subscribeToRealTimeUpdates = (traceId: string) => {
    // In a real implementation, this would set up WebSocket or SSE connection
    // For now, we'll simulate with polling
    const interval = setInterval(async () => {
      try {
        const updates = await agentService.getTraceUpdates(traceId);
        if (updates && updates.steps) {
          updates.steps.forEach((step: any) => {
            updateTrace(traceId, step);
          });
        }

        if (updates?.status === 'completed') {
          completeTrace(traceId, updates.result);
          clearInterval(interval);
        }
      } catch (error) {
        console.error('Failed to get trace updates:', error);
      }
    }, 1000);

    // Cleanup interval when component unmounts
    return () => clearInterval(interval);
  };

  const value: AgentTraceContextType = {
    currentTrace,
    traces,
    isLoading,
    error,
    startTrace,
    updateTrace,
    completeTrace,
    getTrace,
    clearCurrentTrace,
    subscribeToTrace,
  };

  return <AgentTraceContext.Provider value={value}>{children}</AgentTraceContext.Provider>;
};
