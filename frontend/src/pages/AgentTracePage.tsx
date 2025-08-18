import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  CircularProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  BugReport as DebugIcon,
  Timeline as TimelineIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  Code as CodeIcon,
  Psychology as BrainIcon,
  Storage as MemoryIcon,
  Security as SecurityIcon
} from '@mui/icons-material';

interface AgentStep {
  id: string;
  stepNumber: number;
  agentType: string;
  tool: string;
  input: any;
  output: any;
  status: 'pending' | 'running' | 'completed' | 'error';
  startTime: Date;
  endTime?: Date;
  duration?: number;
  confidence?: number;
  error?: string;
  metadata?: any;
}

interface AgentTrace {
  id: string;
  documentId: string;
  documentName: string;
  status: 'running' | 'completed' | 'error' | 'paused';
  steps: AgentStep[];
  startTime: Date;
  endTime?: Date;
  totalDuration?: number;
  overallConfidence?: number;
  summary?: string;
}

const AgentTracePage: React.FC = () => {
  const [traces, setTraces] = useState<AgentTrace[]>([]);
  const [selectedTrace, setSelectedTrace] = useState<AgentTrace | null>(null);
  const [isLiveMode, setIsLiveMode] = useState(false);
  const [filterStatus, setFilterStatus] = useState('all');

  // Mock data for demonstration
  useEffect(() => {
    const mockTraces: AgentTrace[] = [
      {
        id: 'trace1',
        documentId: 'doc1',
        documentName: 'Contract_V1.pdf',
        status: 'completed',
        startTime: new Date(Date.now() - 300000),
        endTime: new Date(Date.now() - 60000),
        totalDuration: 240000,
        overallConfidence: 0.89,
        summary: 'Document processed successfully with high confidence',
        steps: [
          {
            id: 'step1',
            stepNumber: 1,
            agentType: 'classifier',
            tool: 'document_classification',
            input: { text: 'Contract document content...' },
            output: { documentType: 'contract', domain: 'legal', confidence: 0.95 },
            status: 'completed',
            startTime: new Date(Date.now() - 300000),
            endTime: new Date(Date.now() - 280000),
            duration: 20000,
            confidence: 0.95
          },
          {
            id: 'step2',
            stepNumber: 2,
            agentType: 'extractor',
            tool: 'entity_extraction',
            input: { text: 'Contract document content...', documentType: 'contract' },
            output: { 
              entities: [
                { type: 'party', value: 'Acme Corp', confidence: 0.98 },
                { type: 'date', value: '2024-01-15', confidence: 0.92 },
                { type: 'amount', value: '$50,000', confidence: 0.89 }
              ]
            },
            status: 'completed',
            startTime: new Date(Date.now() - 280000),
            endTime: new Date(Date.now() - 240000),
            duration: 40000,
            confidence: 0.93
          },
          {
            id: 'step3',
            stepNumber: 3,
            agentType: 'risk',
            tool: 'risk_assessment',
            input: { entities: [...], documentType: 'contract' },
            output: { 
              riskLevel: 'medium',
              riskScore: 0.65,
              riskFactors: ['Payment terms', 'Liability clauses'],
              mitigations: ['Review payment terms', 'Legal consultation recommended']
            },
            status: 'completed',
            startTime: new Date(Date.now() - 240000),
            endTime: new Date(Date.now() - 180000),
            duration: 60000,
            confidence: 0.87
          },
          {
            id: 'step4',
            stepNumber: 4,
            agentType: 'compliance',
            tool: 'compliance_check',
            input: { documentType: 'contract', riskAssessment: {...} },
            output: {
              regulations: ['SOX', 'GDPR'],
              violations: [],
              recommendations: ['Add data protection clause'],
              complianceScore: 0.92
            },
            status: 'completed',
            startTime: new Date(Date.now() - 180000),
            endTime: new Date(Date.now() - 120000),
            duration: 60000,
            confidence: 0.92
          }
        ]
      },
      {
        id: 'trace2',
        documentId: 'doc2',
        documentName: 'Policy_2024.pdf',
        status: 'running',
        startTime: new Date(Date.now() - 120000),
        steps: [
          {
            id: 'step1',
            stepNumber: 1,
            agentType: 'classifier',
            tool: 'document_classification',
            input: { text: 'Policy document content...' },
            output: { documentType: 'policy', domain: 'corporate', confidence: 0.91 },
            status: 'completed',
            startTime: new Date(Date.now() - 120000),
            endTime: new Date(Date.now() - 100000),
            duration: 20000,
            confidence: 0.91
          },
          {
            id: 'step2',
            stepNumber: 2,
            agentType: 'extractor',
            tool: 'entity_extraction',
            input: { text: 'Policy document content...', documentType: 'policy' },
            output: null,
            status: 'running',
            startTime: new Date(Date.now() - 100000),
            confidence: 0.0
          }
        ]
      }
    ];

    setTraces(mockTraces);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'running': return 'primary';
      case 'error': return 'error';
      case 'paused': return 'warning';
      default: return 'default';
    }
  };

  const getStepIcon = (agentType: string) => {
    switch (agentType) {
      case 'classifier': return <BrainIcon />;
      case 'extractor': return <CodeIcon />;
      case 'risk': return <SecurityIcon />;
      case 'compliance': return <SecurityIcon />;
      case 'memory': return <MemoryIcon />;
      default: return <InfoIcon />;
    }
  };

  const getStepStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <SuccessIcon color="success" />;
      case 'running': return <CircularProgress size={20} />;
      case 'error': return <ErrorIcon color="error" />;
      case 'pending': return <InfoIcon color="info" />;
      default: return <InfoIcon />;
    }
  };

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}m`;
  };

  const startNewTrace = () => {
    const newTrace: AgentTrace = {
      id: `trace${Date.now()}`,
      documentId: 'new-doc',
      documentName: 'New Document',
      status: 'running',
      startTime: new Date(),
      steps: []
    };
    setTraces(prev => [newTrace, ...prev]);
    setSelectedTrace(newTrace);
  };

  const filteredTraces = traces.filter(trace => 
    filterStatus === 'all' || trace.status === filterStatus
  );

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
        Agent Trace
      </Typography>

      <Grid container spacing={3}>
        {/* Controls */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                  <Button
                    variant="contained"
                    startIcon={<PlayIcon />}
                    onClick={startNewTrace}
                  >
                    Start New Trace
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<RefreshIcon />}
                    onClick={() => window.location.reload()}
                  >
                    Refresh
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<DebugIcon />}
                    color={isLiveMode ? 'primary' : 'inherit'}
                    onClick={() => setIsLiveMode(!isLiveMode)}
                  >
                    {isLiveMode ? 'Live Mode ON' : 'Live Mode OFF'}
                  </Button>
                </Box>
                <FormControl sx={{ minWidth: 200 }}>
                  <InputLabel>Filter Status</InputLabel>
                  <Select
                    value={filterStatus}
                    label="Filter Status"
                    onChange={(e) => setFilterStatus(e.target.value)}
                  >
                    <MenuItem value="all">All Traces</MenuItem>
                    <MenuItem value="running">Running</MenuItem>
                    <MenuItem value="completed">Completed</MenuItem>
                    <MenuItem value="error">Error</MenuItem>
                    <MenuItem value="paused">Paused</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Trace List */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Traces
              </Typography>
              <List>
                {filteredTraces.map((trace) => (
                  <ListItem
                    key={trace.id}
                    button
                    selected={selectedTrace?.id === trace.id}
                    onClick={() => setSelectedTrace(trace)}
                    sx={{ mb: 1, borderRadius: 1 }}
                  >
                    <ListItemIcon>
                      <TimelineIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={trace.documentName}
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            {trace.startTime.toLocaleTimeString()}
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                            <Chip
                              label={trace.status}
                              color={getStatusColor(trace.status)}
                              size="small"
                            />
                            {trace.totalDuration && (
                              <Chip
                                label={formatDuration(trace.totalDuration)}
                                size="small"
                                variant="outlined"
                              />
                            )}
                          </Box>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Trace Details */}
        <Grid item xs={12} md={8}>
          {selectedTrace ? (
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                  <Typography variant="h6">
                    Trace: {selectedTrace.documentName}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Chip
                      label={selectedTrace.status}
                      color={getStatusColor(selectedTrace.status)}
                    />
                    {selectedTrace.overallConfidence && (
                      <Chip
                        label={`${(selectedTrace.overallConfidence * 100).toFixed(1)}% Confidence`}
                        color="primary"
                        variant="outlined"
                      />
                    )}
                  </Box>
                </Box>

                {/* Trace Summary */}
                {selectedTrace.summary && (
                  <Alert severity="info" sx={{ mb: 3 }}>
                    {selectedTrace.summary}
                  </Alert>
                )}

                {/* Timeline View */}
                <Typography variant="h6" gutterBottom>
                  Execution Timeline
                </Typography>
                <Timeline>
                  {selectedTrace.steps.map((step, index) => (
                    <TimelineItem key={step.id}>
                      <TimelineOppositeContent sx={{ m: 'auto 0' }} variant="body2" color="text.secondary">
                        {step.startTime.toLocaleTimeString()}
                        {step.duration && (
                          <Typography variant="caption" display="block">
                            {formatDuration(step.duration)}
                          </Typography>
                        )}
                      </TimelineOppositeContent>
                      <TimelineSeparator>
                        <TimelineDot color={step.status === 'completed' ? 'success' : step.status === 'error' ? 'error' : 'primary'}>
                          {getStepIcon(step.agentType)}
                        </TimelineDot>
                        {index < selectedTrace.steps.length - 1 && <TimelineConnector />}
                      </TimelineSeparator>
                      <TimelineContent>
                        <Accordion>
                          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                              <Typography variant="subtitle1">
                                Step {step.stepNumber}: {step.agentType} - {step.tool}
                              </Typography>
                              <Box sx={{ display: 'flex', gap: 1, ml: 'auto' }}>
                                {getStepStatusIcon(step.status)}
                                {step.confidence && (
                                  <Chip
                                    label={`${(step.confidence * 100).toFixed(0)}%`}
                                    size="small"
                                    variant="outlined"
                                  />
                                )}
                              </Box>
                            </Box>
                          </AccordionSummary>
                          <AccordionDetails>
                            <Grid container spacing={2}>
                              <Grid item xs={12} md={6}>
                                <Typography variant="subtitle2" gutterBottom>
                                  Input:
                                </Typography>
                                <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                                  <pre style={{ margin: 0, fontSize: '0.875rem' }}>
                                    {JSON.stringify(step.input, null, 2)}
                                  </pre>
                                </Paper>
                              </Grid>
                              <Grid item xs={12} md={6}>
                                <Typography variant="subtitle2" gutterBottom>
                                  Output:
                                </Typography>
                                <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                                  <pre style={{ margin: 0, fontSize: '0.875rem' }}>
                                    {JSON.stringify(step.output, null, 2)}
                                  </pre>
                                </Paper>
                              </Grid>
                              {step.error && (
                                <Grid item xs={12}>
                                  <Alert severity="error">
                                    Error: {step.error}
                                  </Alert>
                                </Grid>
                              )}
                            </Grid>
                          </AccordionDetails>
                        </Accordion>
                      </TimelineContent>
                    </TimelineItem>
                  ))}
                </Timeline>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent>
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <TimelineIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary">
                    Select a trace to view details
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default AgentTracePage;
