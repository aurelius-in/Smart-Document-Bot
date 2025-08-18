import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Paper,
  Divider,
  IconButton,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Slider,
  Switch,
  FormControlLabel,
  LinearProgress,
  Badge,
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent
} from '@mui/material';
import {
  PlayArrow,
  Pause,
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
  Speed
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

interface ToolCall {
  id: string;
  name: string;
  parameters: Record<string, any>;
  result: any;
  duration: number;
  status: 'success' | 'error' | 'pending';
}

interface AgentStep {
  id: string;
  agentName: string;
  agentType: string;
  status: 'pending' | 'running' | 'completed' | 'error' | 'skipped';
  startTime: Date;
  endTime?: Date;
  duration?: number;
  confidence: number;
  rationale: string;
  toolCalls: ToolCall[];
  input: any;
  output: any;
  metadata: Record<string, any>;
  error?: string;
}

interface AgentTraceVisualizationProps {
  traceId: string;
  steps: AgentStep[];
  isLive: boolean;
  onStepClick?: (step: AgentStep) => void;
  onRerunStep?: (stepId: string) => void;
  onWhatIf?: (stepId: string, parameters: any) => void;
  animationSpeed: number;
}

const AgentTraceVisualization: React.FC<AgentTraceVisualizationProps> = ({
  traceId,
  steps,
  isLive,
  onStepClick,
  onRerunStep,
  onWhatIf,
  animationSpeed
}) => {
  const [selectedStep, setSelectedStep] = useState<AgentStep | null>(null);
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());
  const [showRationales, setShowRationales] = useState(true);
  const [showToolCalls, setShowToolCalls] = useState(true);
  const [showMetadata, setShowMetadata] = useState(false);
  const [whatIfDialog, setWhatIfDialog] = useState<{ open: boolean; step: AgentStep | null }>({ open: false, step: null });
  const [whatIfParameters, setWhatIfParameters] = useState<Record<string, any>>({});

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'running':
        return 'primary';
      case 'error':
        return 'error';
      case 'skipped':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle />;
      case 'running':
        return <Schedule />;
      case 'error':
        return <Error />;
      case 'skipped':
        return <VisibilityOff />;
      default:
        return null;
    }
  };

  const getAgentIcon = (agentType: string) => {
    switch (agentType) {
      case 'classifier':
        return <Psychology />;
      case 'entity':
        return <Build />;
      case 'risk':
        return <TrendingDown />;
      case 'qa':
        return <Help />;
      case 'compare':
        return <TimelineIcon />;
      case 'audit':
        return <DataUsage />;
      case 'summarizer':
        return <Memory />;
      case 'translator':
        return <Speed />;
      case 'sentiment':
        return <TrendingUp />;
      default:
        return <Code />;
    }
  };

  const formatDuration = (duration?: number) => {
    if (!duration) return '';
    if (duration < 1000) return `${duration}ms`;
    return `${(duration / 1000).toFixed(1)}s`;
  };

  const handleStepClick = (step: AgentStep) => {
    setSelectedStep(step);
    onStepClick?.(step);
  };

  const handleStepExpand = (stepId: string) => {
    const newExpanded = new Set(expandedSteps);
    if (newExpanded.has(stepId)) {
      newExpanded.delete(stepId);
    } else {
      newExpanded.add(stepId);
    }
    setExpandedSteps(newExpanded);
  };

  const handleRerunStep = (step: AgentStep) => {
    onRerunStep?.(step.id);
  };

  const handleWhatIf = (step: AgentStep) => {
    setWhatIfDialog({ open: true, step });
    setWhatIfParameters(step.input || {});
  };

  const handleWhatIfSubmit = () => {
    if (whatIfDialog.step) {
      onWhatIf?.(whatIfDialog.step.id, whatIfParameters);
    }
    setWhatIfDialog({ open: false, step: null });
  };

  const renderConfidenceGauge = (confidence: number) => {
    const color = confidence > 0.8 ? 'success' : confidence > 0.6 ? 'warning' : 'error';
    return (
      <Box display="flex" alignItems="center" gap={1}>
        <LinearProgress
          variant="determinate"
          value={confidence * 100}
          color={color}
          sx={{ width: 60, height: 6, borderRadius: 3 }}
        />
        <Typography variant="caption">
          {Math.round(confidence * 100)}%
        </Typography>
      </Box>
    );
  };

  const renderToolCalls = (toolCalls: ToolCall[]) => {
    return (
      <List dense>
        {toolCalls.map((toolCall) => (
          <ListItem key={toolCall.id} sx={{ pl: 4 }}>
            <ListItemIcon>
              <Box
                sx={{
                  color: toolCall.status === 'success' ? 'success.main' :
                         toolCall.status === 'error' ? 'error.main' : 'text.secondary'
                }}
              >
                <Code />
              </Box>
            </ListItemIcon>
            <ListItemText
              primary={
                <Box display="flex" alignItems="center" gap={1}>
                  <Typography variant="subtitle2">
                    {toolCall.name}
                  </Typography>
                  <Chip
                    label={toolCall.status}
                    size="small"
                    color={toolCall.status === 'success' ? 'success' : 'error'}
                  />
                  {toolCall.duration && (
                    <Typography variant="caption" color="text.secondary">
                      ({formatDuration(toolCall.duration)})
                    </Typography>
                  )}
                </Box>
              }
              secondary={
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Parameters: {JSON.stringify(toolCall.parameters, null, 2)}
                  </Typography>
                  {toolCall.result && (
                    <Typography variant="caption" display="block" color="text.secondary">
                      Result: {JSON.stringify(toolCall.result, null, 2)}
                    </Typography>
                  )}
                </Box>
              }
            />
          </ListItem>
        ))}
      </List>
    );
  };

  return (
    <Box>
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <Typography variant="h6" display="flex" alignItems="center">
              <TimelineIcon sx={{ mr: 1 }} />
              Agent Trace Visualization
            </Typography>
            <Box display="flex" alignItems="center" gap={1}>
              <Chip
                label={isLive ? 'Live' : 'Static'}
                color={isLive ? 'warning' : 'default'}
                size="small"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={showRationales}
                    onChange={(e) => setShowRationales(e.target.checked)}
                    size="small"
                  />
                }
                label="Rationales"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={showToolCalls}
                    onChange={(e) => setShowToolCalls(e.target.checked)}
                    size="small"
                  />
                }
                label="Tool Calls"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={showMetadata}
                    onChange={(e) => setShowMetadata(e.target.checked)}
                    size="small"
                  />
                }
                label="Metadata"
              />
            </Box>
          </Box>

          {/* Timeline View */}
          <Timeline>
            {steps.map((step, index) => (
              <motion.div
                key={step.id}
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 * animationSpeed }}
              >
                <TimelineItem>
                  <TimelineOppositeContent sx={{ m: 'auto 0' }} variant="body2" color="text.secondary">
                    {step.startTime.toLocaleTimeString()}
                    {step.duration && (
                      <Typography variant="caption" display="block">
                        {formatDuration(step.duration)}
                      </Typography>
                    )}
                  </TimelineOppositeContent>
                  <TimelineSeparator>
                    <TimelineDot
                      color={getStatusColor(step.status)}
                      sx={{
                        backgroundColor: step.status === 'running' ? 'primary.main' : undefined
                      }}
                    >
                      {getAgentIcon(step.agentType)}
                    </TimelineDot>
                    {index < steps.length - 1 && <TimelineConnector />}
                  </TimelineSeparator>
                  <TimelineContent>
                    <Paper
                      elevation={selectedStep?.id === step.id ? 4 : 1}
                      sx={{
                        p: 2,
                        cursor: 'pointer',
                        border: selectedStep?.id === step.id ? 2 : 1,
                        borderColor: selectedStep?.id === step.id ? 'primary.main' : 'divider',
                        '&:hover': {
                          elevation: 2
                        }
                      }}
                      onClick={() => handleStepClick(step)}
                    >
                      <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="subtitle1">
                            {step.agentName}
                          </Typography>
                          <Chip
                            label={step.agentType}
                            size="small"
                            variant="outlined"
                          />
                          <Chip
                            label={step.status}
                            color={getStatusColor(step.status)}
                            size="small"
                          />
                        </Box>
                        <Box display="flex" alignItems="center" gap={1}>
                          {getStatusIcon(step.status)}
                          {step.status === 'running' && (
                            <motion.div
                              animate={{ rotate: 360 }}
                              transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                            >
                              <Schedule />
                            </motion.div>
                          )}
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleStepExpand(step.id);
                            }}
                          >
                            {expandedSteps.has(step.id) ? <ExpandLess /> : <ExpandMore />}
                          </IconButton>
                        </Box>
                      </Box>

                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {step.rationale}
                      </Typography>

                      <Box display="flex" alignItems="center" gap={2} mb={1}>
                        <Typography variant="caption">Confidence:</Typography>
                        {renderConfidenceGauge(step.confidence)}
                      </Box>

                      {/* Action Buttons */}
                      <Box display="flex" gap={1} mb={1}>
                        <Button
                          size="small"
                          startIcon={<Refresh />}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRerunStep(step);
                          }}
                          disabled={step.status === 'running'}
                        >
                          Re-run
                        </Button>
                        <Button
                          size="small"
                          startIcon={<Settings />}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleWhatIf(step);
                          }}
                          disabled={step.status === 'running'}
                        >
                          What-if
                        </Button>
                      </Box>

                      {/* Expanded Details */}
                      <Collapse in={expandedSteps.has(step.id)}>
                        <Divider sx={{ my: 1 }} />
                        
                        {/* Tool Calls */}
                        {showToolCalls && step.toolCalls.length > 0 && (
                          <Box mb={2}>
                            <Typography variant="subtitle2" gutterBottom>
                              Tool Calls ({step.toolCalls.length})
                            </Typography>
                            {renderToolCalls(step.toolCalls)}
                          </Box>
                        )}

                        {/* Input/Output */}
                        <Box mb={2}>
                          <Typography variant="subtitle2" gutterBottom>
                            Input/Output
                          </Typography>
                          <Box display="flex" gap={2}>
                            <Box flex={1}>
                              <Typography variant="caption" color="text.secondary">
                                Input:
                              </Typography>
                              <Paper
                                variant="outlined"
                                sx={{ p: 1, mt: 0.5, backgroundColor: 'grey.50' }}
                              >
                                <Typography variant="caption" fontFamily="monospace">
                                  {JSON.stringify(step.input, null, 2)}
                                </Typography>
                              </Paper>
                            </Box>
                            <Box flex={1}>
                              <Typography variant="caption" color="text.secondary">
                                Output:
                              </Typography>
                              <Paper
                                variant="outlined"
                                sx={{ p: 1, mt: 0.5, backgroundColor: 'grey.50' }}
                              >
                                <Typography variant="caption" fontFamily="monospace">
                                  {JSON.stringify(step.output, null, 2)}
                                </Typography>
                              </Paper>
                            </Box>
                          </Box>
                        </Box>

                        {/* Metadata */}
                        {showMetadata && Object.keys(step.metadata).length > 0 && (
                          <Box>
                            <Typography variant="subtitle2" gutterBottom>
                              Metadata
                            </Typography>
                            <Paper
                              variant="outlined"
                              sx={{ p: 1, backgroundColor: 'grey.50' }}
                            >
                              <Typography variant="caption" fontFamily="monospace">
                                {JSON.stringify(step.metadata, null, 2)}
                              </Typography>
                            </Paper>
                          </Box>
                        )}

                        {/* Error Details */}
                        {step.error && (
                          <Box mt={2}>
                            <Typography variant="subtitle2" color="error" gutterBottom>
                              Error Details
                            </Typography>
                            <Paper
                              variant="outlined"
                              sx={{ p: 1, backgroundColor: 'error.light' }}
                            >
                              <Typography variant="caption" color="error">
                                {step.error}
                              </Typography>
                            </Paper>
                          </Box>
                        )}
                      </Collapse>
                    </Paper>
                  </TimelineContent>
                </TimelineItem>
              </motion.div>
            ))}
          </Timeline>

          {/* Summary Stats */}
          <Box mt={3} p={2} bgcolor="grey.50" borderRadius={1}>
            <Typography variant="subtitle2" gutterBottom>
              Trace Summary
            </Typography>
            <Box display="flex" gap={4}>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Total Steps
                </Typography>
                <Typography variant="h6">
                  {steps.length}
                </Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Completed
                </Typography>
                <Typography variant="h6" color="success.main">
                  {steps.filter(s => s.status === 'completed').length}
                </Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Errors
                </Typography>
                <Typography variant="h6" color="error.main">
                  {steps.filter(s => s.status === 'error').length}
                </Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Total Duration
                </Typography>
                <Typography variant="h6">
                  {formatDuration(steps.reduce((acc, step) => acc + (step.duration || 0), 0))}
                </Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Avg Confidence
                </Typography>
                <Typography variant="h6">
                  {Math.round(steps.reduce((acc, step) => acc + step.confidence, 0) / steps.length * 100)}%
                </Typography>
              </Box>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* What-if Dialog */}
      <Dialog
        open={whatIfDialog.open}
        onClose={() => setWhatIfDialog({ open: false, step: null })}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          What-if Analysis: {whatIfDialog.step?.agentName}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Modify parameters to see how the agent would behave differently:
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={8}
            label="Parameters (JSON)"
            value={JSON.stringify(whatIfParameters, null, 2)}
            onChange={(e) => {
              try {
                setWhatIfParameters(JSON.parse(e.target.value));
              } catch (error) {
                // Invalid JSON, keep the text as is
              }
            }}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setWhatIfDialog({ open: false, step: null })}>
            Cancel
          </Button>
          <Button onClick={handleWhatIfSubmit} variant="contained">
            Run What-if
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AgentTraceVisualization;
