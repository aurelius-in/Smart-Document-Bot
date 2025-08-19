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
  Collapse,
  Avatar
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
                    {toolCall.name === 'classify_document_type' ? 
                      `Analyzing document content for classification...` :
                      toolCall.name === 'extract_entities' ? 
                        `Extracting named entities from document text...` :
                      toolCall.name === 'assess_compliance_risks' ? 
                        `Evaluating compliance requirements and risk factors...` :
                      `Parameters: ${Object.keys(toolCall.parameters).length} items`
                    }
                  </Typography>
                  {toolCall.result && (
                    <Typography variant="caption" display="block" color="text.secondary">
                      {toolCall.result.type ? 
                        `Classified as: ${toolCall.result.type}` :
                        toolCall.result.entities ? 
                          `Found ${toolCall.result.entities.length} entities` :
                        toolCall.result.risk_level ? 
                          `Risk Level: ${toolCall.result.risk_level}` :
                          `Result: ${JSON.stringify(toolCall.result, null, 2)}`
                      }
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
            <Typography variant="h6" gutterBottom>
              Execution Trace
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

          {/* Timeline View - Replaced with List */}
          <List>
            {steps.map((step, index) => (
              <motion.div
                key={step.id}
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 * animationSpeed }}
              >
                <ListItem
                  sx={{
                    flexDirection: 'column',
                    alignItems: 'stretch',
                    p: 0,
                    mb: 2
                  }}
                >
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
                    <Box display="flex" alignItems="center" gap={2} mb={1}>
                      <Avatar
                        sx={{
                          bgcolor: getStatusColor(step.status) === 'success' ? 'success.main' :
                                   getStatusColor(step.status) === 'error' ? 'error.main' :
                                   getStatusColor(step.status) === 'warning' ? 'warning.main' :
                                   'primary.main',
                          width: 40,
                          height: 40
                        }}
                      >
                        {getAgentIcon(step.agentType)}
                      </Avatar>
                      
                      <Box flex={1}>
                        <Box display="flex" alignItems="center" gap={1} mb={0.5}>
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
                            color={getStatusColor(step.status) as any}
                            size="small"
                          />
                        </Box>
                        
                        <Box display="flex" alignItems="center" gap={2}>
                          <Typography variant="caption" color="text.secondary">
                            {step.startTime.toLocaleTimeString()}
                          </Typography>
                          {step.duration && (
                            <Typography variant="caption" color="text.secondary">
                              {formatDuration(step.duration)}
                            </Typography>
                          )}
                        </Box>
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
                              sx={{ p: 1, mt: 0.5, backgroundColor: 'background.paper', border: '1px solid', borderColor: 'divider' }}
                            >
                              <Typography variant="caption" fontFamily="monospace" sx={{ color: 'text.primary' }}>
                                {step.input.document_text ? 
                                  `Document Text: ${step.input.document_text.substring(0, 100)}${step.input.document_text.length > 100 ? '...' : ''}` :
                                  step.input.document_type ? 
                                    `Document Type: ${step.input.document_type}` :
                                    JSON.stringify(step.input, null, 2)
                                }
                              </Typography>
                            </Paper>
                          </Box>
                          <Box flex={1}>
                            <Typography variant="caption" color="text.secondary">
                              Output:
                            </Typography>
                            <Paper
                              variant="outlined"
                              sx={{ p: 1, mt: 0.5, backgroundColor: 'background.paper', border: '1px solid', borderColor: 'divider' }}
                            >
                              <Typography variant="caption" fontFamily="monospace" sx={{ color: 'text.primary' }}>
                                {step.output.document_type ? 
                                  `Document Type: ${step.output.document_type}` :
                                  step.output.entities ? 
                                    `Entities Found: ${step.output.entities.length} items` :
                                    step.output.risk_assessment ? 
                                      `Risk Assessment: ${step.output.risk_assessment}` :
                                      JSON.stringify(step.output, null, 2)
                                }
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
                            sx={{ p: 1, backgroundColor: 'background.paper', border: '1px solid', borderColor: 'divider' }}
                          >
                            <Typography variant="caption" fontFamily="monospace" sx={{ color: 'text.primary' }}>
                              {step.metadata.processing_time ? 
                                `Processing Time: ${step.metadata.processing_time}ms` :
                                step.metadata.model_used ? 
                                  `Model Used: ${step.metadata.model_used}` :
                                  JSON.stringify(step.metadata, null, 2)
                              }
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
                </ListItem>
              </motion.div>
            ))}
          </List>

          {/* Summary Stats */}
          <Box mt={3} p={2} sx={{ backgroundColor: 'background.paper', border: '1px solid', borderColor: 'divider' }} borderRadius={1}>
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
