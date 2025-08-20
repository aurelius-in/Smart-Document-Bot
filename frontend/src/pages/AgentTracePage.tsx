import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Paper,
  Divider,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
  Avatar,
  Switch,
  FormControlLabel,
  CircularProgress,
  useTheme as useMuiTheme
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Refresh,
  Visibility,
  VisibilityOff,
  ExpandMore,
  ExpandLess,
  Settings,
  BugReport,
  Timeline as TimelineIcon,
  Psychology,
  Build,
  CheckCircle,
  Error,
  Schedule,
  TrendingUp,
  TrendingDown,
  Help,
  Code,
  DataUsage,
  Memory,
  Speed,
  Add,
  Delete,
  Download,
  Share,
  Info,
  Warning,
  History,
  FilterList,
  LiveTv,
  AutoAwesome
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { useTheme } from '../contexts/ThemeContext';
import { apiService } from '../services/apiService';
import { AgentTrace, AgentStep } from '../types/agent';

const AgentTracePage: React.FC = () => {
  const { darkMode } = useTheme();
  const muiTheme = useMuiTheme();
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
      const newTrace = await apiService.startAgentTrace(''); // Will be set by backend based on context
      
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
      case 'ocr': return <Info />;
      case 'extraction': return <Visibility />;
      case 'analysis': return <PlayArrow />;
      case 'validation': return <CheckCircle />;
      case 'compliance_check': return <Warning />;
      default: return <Info />;
    }
  };

  const getStepStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle color="success" />;
      case 'processing': return <CircularProgress size={16} />;
      case 'error': return <Error color="error" />;
      case 'pending': return <Schedule color="disabled" />;
      default: return <Info />;
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
      {/* Header Section */}
      <Box sx={{ 
        mb: 4,
        background: darkMode 
          ? 'linear-gradient(135deg, #0f0f23 0%, #1a1a3a 25%, #2d1b69 50%, #1a1a3a 75%, #0f0f23 100%)'
          : 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 25%, #cbd5e1 50%, #e2e8f0 75%, #f8fafc 100%)',
        color: darkMode ? 'white' : 'inherit',
        p: 4,
        borderRadius: 3,
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 30% 20%, rgba(138, 43, 226, 0.3) 0%, transparent 50%), radial-gradient(circle at 70% 80%, rgba(75, 0, 130, 0.3) 0%, transparent 50%)',
          pointerEvents: 'none'
        }
      }}>
        <Box display="flex" alignItems="center" gap={4} position="relative" zIndex={1}>
          <Box sx={{ 
            background: 'linear-gradient(135deg, rgba(138, 43, 226, 0.8) 0%, rgba(75, 0, 130, 0.8) 100%)',
            borderRadius: '50%', 
            p: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 8px 32px rgba(138, 43, 226, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2)',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <TimelineIcon sx={{ 
              fontSize: '2.5rem',
              color: 'white',
              filter: 'drop-shadow(0 0 12px rgba(138, 43, 226, 0.8))'
            }} />
          </Box>
          <Box>
            <Typography variant="h3" component="h1" gutterBottom sx={{ 
              fontWeight: 700,
              fontFamily: '"Orbitron", "Roboto", sans-serif',
              letterSpacing: '0.05em',
              background: 'linear-gradient(135deg, #ffffff 0%, #e0e7ff 50%, #c7d2fe 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              textShadow: '0 0 30px rgba(138, 43, 226, 0.5)'
            }}>
              Agent Traces
            </Typography>
            <Typography variant="h6" sx={{ 
              opacity: 0.95,
              background: 'linear-gradient(135deg, #cbd5e1 0%, #94a3b8 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              Monitor and analyze agent execution traces in real-time
            </Typography>
          </Box>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Controls */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  <History sx={{ mr: 1, verticalAlign: 'middle' }} />
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
                        <LiveTv sx={{ mr: 1 }} />
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
                  startIcon={<PlayArrow />}
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
                  startIcon={<Refresh />}
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
                <FilterList sx={{ mr: 1, verticalAlign: 'middle' }} />
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
                          <PlayArrow color="primary" />
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
                                {trace.createdAt ? new Date(trace.createdAt).toLocaleString() : trace.startTime ? new Date(trace.startTime).toLocaleString() : 'N/A'}
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                {trace.steps?.length || 0} steps • {formatDuration(trace.duration || trace.totalDuration || 0)}
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
                        label={formatDuration(selectedTrace.duration || selectedTrace.totalDuration || 0)}
                        variant="outlined"
                        size="small"
                      />
                    </Box>
                  </Box>

                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Started: {selectedTrace.createdAt ? new Date(selectedTrace.createdAt).toLocaleString() : selectedTrace.startTime ? new Date(selectedTrace.startTime).toLocaleString() : 'N/A'}
                    {selectedTrace.completedAt && (
                      <> • Completed: {new Date(selectedTrace.completedAt).toLocaleString()}</>
                    )}
                  </Typography>

                  {selectedTrace.steps && selectedTrace.steps.length > 0 ? (
                    <List>
                      {selectedTrace.steps.map((step: AgentStep, index: number) => (
                        <ListItem key={step.id} sx={{ flexDirection: 'column', alignItems: 'stretch', p: 0, mb: 2 }}>
                          <Paper elevation={1} sx={{ p: 2, width: '100%' }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                              <Avatar
                                sx={{
                                  bgcolor: step.status === 'completed' ? 'success.main' :
                                           step.status === 'error' ? 'error.main' :
                                           step.status === 'pending' ? 'warning.main' :
                                           'primary.main',
                                  width: 40,
                                  height: 40
                                }}
                              >
                                {getStepIcon(step.type || step.agentType)}
                              </Avatar>
                              
                              <Box flex={1}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                                  <Typography variant="subtitle2">
                                    {step.name || `Step ${step.stepNumber}`}
                                  </Typography>
                                  <Chip
                                    label={step.type || step.agentType}
                                    size="small"
                                    variant="outlined"
                                  />
                                  <Chip
                                    label={step.status}
                                    color={step.status === 'completed' ? 'success' : 
                                           step.status === 'error' ? 'error' : 
                                           step.status === 'pending' ? 'warning' : 'default'}
                                    size="small"
                                  />
                                </Box>
                                
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                                                     <Typography variant="caption" color="text.secondary">
                                     {new Date(step.startTime).toLocaleTimeString()}
                                   </Typography>
                                  {step.duration && (
                                    <Typography variant="caption" color="text.secondary">
                                      {formatDuration(step.duration)}
                                    </Typography>
                                  )}
                                </Box>
                              </Box>
                              
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                {getStepStatusIcon(step.status)}
                              </Box>
                            </Box>

                            <Typography variant="body2" color="text.secondary" gutterBottom>
                              {step.rationale || `Step ${step.stepNumber} using ${step.agentType}`}
                            </Typography>

                            <Accordion>
                              <AccordionSummary expandIcon={<ExpandMore />}>
                                <Typography variant="subtitle2">Step Details</Typography>
                              </AccordionSummary>
                              <AccordionDetails>
                                <Box>
                                  <Typography variant="body2" gutterBottom>
                                    <strong>Input:</strong>
                                  </Typography>
                                  <Paper variant="outlined" sx={{ p: 1, mb: 2, backgroundColor: 'grey.50' }}>
                                    <Typography variant="caption" fontFamily="monospace">
                                      {JSON.stringify(step.input, null, 2)}
                                    </Typography>
                                  </Paper>
                                  
                                  <Typography variant="body2" gutterBottom>
                                    <strong>Output:</strong>
                                  </Typography>
                                  <Paper variant="outlined" sx={{ p: 1, backgroundColor: 'grey.50' }}>
                                    <Typography variant="caption" fontFamily="monospace">
                                      {JSON.stringify(step.output, null, 2)}
                                    </Typography>
                                  </Paper>
                                </Box>
                              </AccordionDetails>
                            </Accordion>
                          </Paper>
                        </ListItem>
                      ))}
                    </List>
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
                    {formatDuration(selectedTraceDetails.duration || selectedTraceDetails.totalDuration || 0)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Created
                  </Typography>
                  <Typography variant="body1">
                    {selectedTraceDetails.createdAt ? new Date(selectedTraceDetails.createdAt).toLocaleString() : selectedTraceDetails.startTime ? new Date(selectedTraceDetails.startTime).toLocaleString() : 'N/A'}
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
                                  {step.name || `Step ${step.stepNumber}`}
                                </Typography>
                                                                  <Chip label={step.type || step.agentType} size="small" variant="outlined" />
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
