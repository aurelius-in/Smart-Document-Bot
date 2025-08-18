import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Grid,
  Card,
  CardContent,
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
  TimelineOppositeContent,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Switch,
  FormControlLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Refresh as RefreshIcon,
  Visibility as ViewIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Schedule as PendingIcon,
  Stop as StopIcon,
  PlayCircle as StartIcon,
  History as HistoryIcon,
  FilterList as FilterIcon,
  LiveTv as LiveIcon
} from '@mui/icons-material';
import { toast } from 'react-hot-toast';
import apiService, { AgentTrace, AgentStep } from '../services/apiService';

const AgentTracePage: React.FC = () => {
  const [traces, setTraces] = useState<AgentTrace[]>([]);
  const [selectedTrace, setSelectedTrace] = useState<AgentTrace | null>(null);
  const [isLiveMode, setIsLiveMode] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(false);
  const [isStartingTrace, setIsStartingTrace] = useState(false);
  const [traceDetailsOpen, setTraceDetailsOpen] = useState(false);
  const [selectedTraceDetails, setSelectedTraceDetails] = useState<AgentTrace | null>(null);

  // Load traces on component mount
  useEffect(() => {
    loadTraces();
  }, []);

  // Set up live updates if live mode is enabled
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (isLiveMode) {
      interval = setInterval(() => {
        loadTraces();
      }, 5000); // Refresh every 5 seconds
    }

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [isLiveMode]);

  const loadTraces = async () => {
    try {
      setIsLoading(true);
      const response = await apiService.getAgentTraces(1, 50);
      setTraces(response.data);
      
      // Update selected trace if it exists in the new data
      if (selectedTrace) {
        const updatedTrace = response.data.find(t => t.id === selectedTrace.id);
        if (updatedTrace) {
          setSelectedTrace(updatedTrace);
        }
      }
    } catch (error) {
      console.error('Failed to load traces:', error);
      toast.error('Failed to load agent traces');
    } finally {
      setIsLoading(false);
    }
  };

  const startNewTrace = async () => {
    try {
      setIsStartingTrace(true);
      const newTrace = await apiService.startAgentTrace({
        documentId: '', // Will be set by backend based on context
        traceType: 'document_processing'
      });
      
      setTraces(prev => [newTrace, ...prev]);
      setSelectedTrace(newTrace);
      toast.success('New agent trace started successfully!');
    } catch (error) {
      console.error('Failed to start trace:', error);
      toast.error('Failed to start new agent trace');
    } finally {
      setIsStartingTrace(false);
    }
  };

  const viewTraceDetails = async (traceId: string) => {
    try {
      const trace = await apiService.getAgentTrace(traceId);
      setSelectedTraceDetails(trace);
      setTraceDetailsOpen(true);
    } catch (error) {
      toast.error('Failed to load trace details');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'processing': return 'primary';
      case 'error': return 'error';
      case 'pending': return 'warning';
      default: return 'default';
    }
  };

  const getStepIcon = (stepType: string) => {
    switch (stepType) {
      case 'ocr': return <InfoIcon />;
      case 'extraction': return <ViewIcon />;
      case 'analysis': return <StartIcon />;
      case 'validation': return <SuccessIcon />;
      case 'compliance_check': return <WarningIcon />;
      default: return <InfoIcon />;
    }
  };

  const getStepStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <SuccessIcon color="success" />;
      case 'processing': return <CircularProgress size={16} />;
      case 'error': return <ErrorIcon color="error" />;
      case 'pending': return <PendingIcon color="disabled" />;
      default: return <InfoIcon />;
    }
  };

  const formatDuration = (duration: number) => {
    if (duration < 1000) return `${duration}ms`;
    if (duration < 60000) return `${(duration / 1000).toFixed(1)}s`;
    return `${(duration / 60000).toFixed(1)}m`;
  };

  const filteredTraces = traces.filter(trace => 
    filterStatus === 'all' || trace.status === filterStatus
  );

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
        Agent Trace Monitor
      </Typography>

      <Grid container spacing={3}>
        {/* Controls */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  <HistoryIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Trace Controls
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={isLiveMode}
                        onChange={(e) => setIsLiveMode(e.target.checked)}
                        color="primary"
                      />
                    }
                    label={
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <LiveIcon sx={{ mr: 1 }} />
                        Live Mode
                      </Box>
                    }
                  />
                  <FormControl size="small" sx={{ minWidth: 120 }}>
                    <InputLabel>Filter Status</InputLabel>
                    <Select
                      value={filterStatus}
                      label="Filter Status"
                      onChange={(e) => setFilterStatus(e.target.value)}
                    >
                      <MenuItem value="all">All Status</MenuItem>
                      <MenuItem value="pending">Pending</MenuItem>
                      <MenuItem value="processing">Processing</MenuItem>
                      <MenuItem value="completed">Completed</MenuItem>
                      <MenuItem value="error">Error</MenuItem>
                    </Select>
                  </FormControl>
                </Box>
              </Box>
              
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<PlayIcon />}
                  onClick={startNewTrace}
                  disabled={isStartingTrace}
                >
                  {isStartingTrace ? (
                    <>
                      <CircularProgress size={20} sx={{ mr: 1 }} />
                      Starting...
                    </>
                  ) : (
                    'Start New Trace'
                  )}
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={loadTraces}
                  disabled={isLoading}
                >
                  Refresh Traces
                </Button>
                <Button
                  variant="outlined"
                  onClick={() => setSelectedTrace(null)}
                  disabled={!selectedTrace}
                >
                  Clear Selection
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Traces List */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <FilterIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Recent Traces ({filteredTraces.length})
              </Typography>
              
              {isLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                  <CircularProgress />
                </Box>
              ) : filteredTraces.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body1" color="text.secondary">
                    No traces found
                  </Typography>
                </Box>
              ) : (
                <List>
                  {filteredTraces.map((trace, index) => (
                    <React.Fragment key={trace.id}>
                      <ListItem
                        button
                        selected={selectedTrace?.id === trace.id}
                        onClick={() => setSelectedTrace(trace)}
                      >
                        <ListItemIcon>
                          <StartIcon color="primary" />
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography variant="subtitle2">
                                Trace #{trace.id.slice(-8)}
                              </Typography>
                              <Chip
                                label={trace.status}
                                color={getStatusColor(trace.status)}
                                size="small"
                              />
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography variant="body2" color="text.secondary">
                                {new Date(trace.createdAt).toLocaleString()}
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                {trace.steps?.length || 0} steps • {formatDuration(trace.duration || 0)}
                              </Typography>
                            </Box>
                          }
                        />
                        <Button
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            viewTraceDetails(trace.id);
                          }}
                        >
                          Details
                        </Button>
                      </ListItem>
                      {index < filteredTraces.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Trace Details */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              {selectedTrace ? (
                <>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                    <Typography variant="h6">
                      Trace Execution Timeline
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Chip
                        label={selectedTrace.status}
                        color={getStatusColor(selectedTrace.status)}
                      />
                      <Chip
                        label={formatDuration(selectedTrace.duration || 0)}
                        variant="outlined"
                        size="small"
                      />
                    </Box>
                  </Box>

                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Started: {new Date(selectedTrace.createdAt).toLocaleString()}
                    {selectedTrace.completedAt && (
                      <> • Completed: {new Date(selectedTrace.completedAt).toLocaleString()}</>
                    )}
                  </Typography>

                  {selectedTrace.steps && selectedTrace.steps.length > 0 ? (
                    <Timeline position="alternate">
                      {selectedTrace.steps.map((step: AgentStep, index: number) => (
                        <TimelineItem key={step.id}>
                          <TimelineOppositeContent sx={{ m: 'auto 0' }} variant="body2" color="text.secondary">
                            {step.duration ? formatDuration(step.duration) : 'Pending'}
                          </TimelineOppositeContent>
                          <TimelineSeparator>
                            <TimelineDot color={getStatusColor(step.status)}>
                              {getStepIcon(step.type)}
                            </TimelineDot>
                            {index < selectedTrace.steps!.length - 1 && <TimelineConnector />}
                          </TimelineSeparator>
                          <TimelineContent sx={{ py: '12px', px: 2 }}>
                            <Accordion>
                              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                  {getStepStatusIcon(step.status)}
                                  <Typography variant="subtitle2">
                                    {step.name}
                                  </Typography>
                                  <Chip
                                    label={step.type}
                                    size="small"
                                    variant="outlined"
                                  />
                                </Box>
                              </AccordionSummary>
                              <AccordionDetails>
                                <Box>
                                  <Typography variant="body2" gutterBottom>
                                    <strong>Status:</strong> {step.status}
                                  </Typography>
                                  {step.input && (
                                    <Typography variant="body2" gutterBottom>
                                      <strong>Input:</strong> {step.input}
                                    </Typography>
                                  )}
                                  {step.output && (
                                    <Typography variant="body2" gutterBottom>
                                      <strong>Output:</strong> {step.output}
                                    </Typography>
                                  )}
                                  {step.error && (
                                    <Alert severity="error" sx={{ mt: 1 }}>
                                      {step.error}
                                    </Alert>
                                  )}
                                  {step.metadata && Object.keys(step.metadata).length > 0 && (
                                    <Typography variant="body2" sx={{ mt: 1 }}>
                                      <strong>Metadata:</strong> {JSON.stringify(step.metadata, null, 2)}
                                    </Typography>
                                  )}
                                </Box>
                              </AccordionDetails>
                            </Accordion>
                          </TimelineContent>
                        </TimelineItem>
                      ))}
                    </Timeline>
                  ) : (
                    <Box sx={{ textAlign: 'center', py: 4 }}>
                      <Typography variant="body1" color="text.secondary">
                        No steps recorded yet
                      </Typography>
                    </Box>
                  )}

                  {selectedTrace.error && (
                    <Alert severity="error" sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Trace Error:
                      </Typography>
                      {selectedTrace.error}
                    </Alert>
                  )}
                </>
              ) : (
                <Box sx={{ textAlign: 'center', py: 8 }}>
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    Select a trace to view details
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Choose a trace from the list to see its execution timeline
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Trace Details Dialog */}
      <Dialog
        open={traceDetailsOpen}
        onClose={() => setTraceDetailsOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Trace Details
          {selectedTraceDetails && (
            <Typography variant="subtitle2" color="text.secondary">
              Trace #{selectedTraceDetails.id.slice(-8)}
            </Typography>
          )}
        </DialogTitle>
        <DialogContent>
          {selectedTraceDetails && (
            <Box>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Status
                  </Typography>
                  <Chip
                    label={selectedTraceDetails.status}
                    color={getStatusColor(selectedTraceDetails.status)}
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Duration
                  </Typography>
                  <Typography variant="body1">
                    {formatDuration(selectedTraceDetails.duration || 0)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Created
                  </Typography>
                  <Typography variant="body1">
                    {new Date(selectedTraceDetails.createdAt).toLocaleString()}
                  </Typography>
                </Grid>
                {selectedTraceDetails.completedAt && (
                  <Grid item xs={6}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Completed
                    </Typography>
                    <Typography variant="body1">
                      {new Date(selectedTraceDetails.completedAt).toLocaleString()}
                    </Typography>
                  </Grid>
                )}
              </Grid>

              {selectedTraceDetails.steps && selectedTraceDetails.steps.length > 0 && (
                <>
                  <Typography variant="h6" gutterBottom>
                    Execution Steps ({selectedTraceDetails.steps.length})
                  </Typography>
                  <List>
                    {selectedTraceDetails.steps.map((step: AgentStep, index: number) => (
                      <ListItem key={step.id} sx={{ flexDirection: 'column', alignItems: 'flex-start' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', mb: 1 }}>
                          <ListItemIcon>
                            {getStepStatusIcon(step.status)}
                          </ListItemIcon>
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Typography variant="subtitle1">
                                  {step.name}
                                </Typography>
                                <Chip label={step.type} size="small" variant="outlined" />
                                {step.duration && (
                                  <Chip label={formatDuration(step.duration)} size="small" variant="outlined" />
                                )}
                              </Box>
                            }
                            secondary={step.status}
                          />
                        </Box>
                        {(step.input || step.output || step.error) && (
                          <Box sx={{ ml: 4, width: '100%' }}>
                            {step.input && (
                              <Typography variant="body2" sx={{ mb: 1 }}>
                                <strong>Input:</strong> {step.input}
                              </Typography>
                            )}
                            {step.output && (
                              <Typography variant="body2" sx={{ mb: 1 }}>
                                <strong>Output:</strong> {step.output}
                              </Typography>
                            )}
                            {step.error && (
                              <Alert severity="error" sx={{ mt: 1 }}>
                                {step.error}
                              </Alert>
                            )}
                          </Box>
                        )}
                        {index < selectedTraceDetails.steps!.length - 1 && <Divider sx={{ mt: 2, width: '100%' }} />}
                      </ListItem>
                    ))}
                  </List>
                </>
              )}

              {selectedTraceDetails.error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Trace Error:
                  </Typography>
                  {selectedTraceDetails.error}
                </Alert>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTraceDetailsOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AgentTracePage;
