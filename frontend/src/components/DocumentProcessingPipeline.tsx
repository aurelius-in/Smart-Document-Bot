import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  Divider,
  IconButton,
  Tooltip,
  Collapse
} from '@mui/material';
import {
  Upload,
  TextFields,
  Search,
  Assessment,
  Storage,
  CheckCircle,
  Error,
  Schedule,
  ExpandMore,
  ExpandLess,
  PlayArrow,
  Pause,
  Stop
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

interface PipelineStep {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  progress: number;
  logs: string[];
  startTime?: Date;
  endTime?: Date;
  duration?: number;
}

interface DocumentProcessingPipelineProps {
  isProcessing: boolean;
  currentStep: string;
  pipelineSteps: PipelineStep[];
  onStepClick?: (stepId: string) => void;
  animationSpeed: number;
}

const DocumentProcessingPipeline: React.FC<DocumentProcessingPipelineProps> = ({
  isProcessing,
  currentStep,
  pipelineSteps,
  onStepClick,
  animationSpeed
}) => {
  const [expandedStep, setExpandedStep] = useState<string | null>(null);
  const [showLogs, setShowLogs] = useState(true);

  const stepIcons = {
    upload: <Upload />,
    ocr: <TextFields />,
    ner: <Search />,
    classify: <Assessment />,
    risk: <Assessment />,
    index: <Storage />
  };

  const getStepColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'processing':
        return 'primary';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStepIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle />;
      case 'processing':
        return <Schedule />;
      case 'error':
        return <Error />;
      default:
        return null;
    }
  };

  const formatDuration = (duration?: number) => {
    if (!duration) return '';
    if (duration < 1000) return `${duration}ms`;
    return `${(duration / 1000).toFixed(1)}s`;
  };

  const handleStepClick = (stepId: string) => {
    if (expandedStep === stepId) {
      setExpandedStep(null);
    } else {
      setExpandedStep(stepId);
    }
    onStepClick?.(stepId);
  };

  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Typography variant="h6" display="flex" alignItems="center">
            <PlayArrow sx={{ mr: 1 }} />
            Document Processing Pipeline
          </Typography>
          <Box display="flex" alignItems="center" gap={1}>
            <Chip
              label={isProcessing ? 'Processing' : 'Ready'}
              color={isProcessing ? 'warning' : 'success'}
              size="small"
            />
            <Tooltip title="Toggle Logs">
              <IconButton
                size="small"
                onClick={() => setShowLogs(!showLogs)}
              >
                {showLogs ? <ExpandLess /> : <ExpandMore />}
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* Pipeline Visualization */}
        <Box mb={3}>
          <Box
            display="flex"
            alignItems="center"
            justifyContent="space-between"
            sx={{
              position: 'relative',
              '&::before': {
                content: '""',
                position: 'absolute',
                top: '50%',
                left: 0,
                right: 0,
                height: 2,
                backgroundColor: 'divider',
                zIndex: 0
              }
            }}
          >
            {pipelineSteps.map((step, index) => (
              <motion.div
                key={step.id}
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: index * 0.1 * animationSpeed }}
                style={{ zIndex: 1 }}
              >
                <Box
                  display="flex"
                  flexDirection="column"
                  alignItems="center"
                  sx={{ cursor: 'pointer' }}
                  onClick={() => handleStepClick(step.id)}
                >
                  <Paper
                    elevation={step.status === 'processing' ? 8 : 2}
                    sx={{
                      p: 1,
                      borderRadius: '50%',
                      backgroundColor: step.status === 'processing' ? 'primary.main' : 'background.paper',
                      color: step.status === 'processing' ? 'primary.contrastText' : 'text.primary',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'scale(1.1)',
                        elevation: 4
                      }
                    }}
                  >
                    {step.icon}
                  </Paper>
                  <Typography
                    variant="caption"
                    sx={{
                      mt: 1,
                      textAlign: 'center',
                      fontWeight: step.status === 'processing' ? 'bold' : 'normal'
                    }}
                  >
                    {step.name}
                  </Typography>
                  {step.status === 'processing' && (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    >
                      <Schedule sx={{ fontSize: 16, color: 'primary.main' }} />
                    </motion.div>
                  )}
                  {step.status === 'completed' && (
                    <CheckCircle sx={{ fontSize: 16, color: 'success.main' }} />
                  )}
                  {step.status === 'error' && (
                    <Error sx={{ fontSize: 16, color: 'error.main' }} />
                  )}
                </Box>
              </motion.div>
            ))}
          </Box>
        </Box>

        {/* Step Details */}
        <List>
          {pipelineSteps.map((step, index) => (
            <motion.div
              key={step.id}
              initial={{ x: -50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: index * 0.1 * animationSpeed }}
            >
              <ListItem
                button
                onClick={() => handleStepClick(step.id)}
                sx={{
                  border: step.status === 'processing' ? 2 : 1,
                  borderColor: step.status === 'processing' ? 'primary.main' : 'divider',
                  borderRadius: 1,
                  mb: 1,
                  backgroundColor: step.status === 'processing' ? 'action.hover' : 'transparent'
                }}
              >
                <ListItemIcon>
                  <Box
                    sx={{
                      color: getStepColor(step.status) === 'success' ? 'success.main' :
                             getStepColor(step.status) === 'error' ? 'error.main' :
                             getStepColor(step.status) === 'primary' ? 'primary.main' : 'text.secondary'
                    }}
                  >
                    {step.icon}
                  </Box>
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="subtitle2">
                        {step.name}
                      </Typography>
                      <Chip
                        label={step.status}
                        color={getStepColor(step.status)}
                        size="small"
                      />
                      {step.duration && (
                        <Typography variant="caption" color="text.secondary">
                          ({formatDuration(step.duration)})
                        </Typography>
                      )}
                    </Box>
                  }
                  secondary={step.description}
                />
                <Box display="flex" alignItems="center" gap={1}>
                  {getStepIcon(step.status)}
                  {expandedStep === step.id ? <ExpandLess /> : <ExpandMore />}
                </Box>
              </ListItem>

              {/* Step Progress */}
              {step.status === 'processing' && (
                <Box sx={{ ml: 4, mb: 1 }}>
                  <LinearProgress
                    variant="determinate"
                    value={step.progress}
                    sx={{ height: 4, borderRadius: 2 }}
                  />
                  <Typography variant="caption" color="text.secondary">
                    {step.progress}% complete
                  </Typography>
                </Box>
              )}

              {/* Step Logs */}
              <Collapse in={expandedStep === step.id && showLogs}>
                <Paper sx={{ ml: 4, mb: 1, p: 2, backgroundColor: 'grey.50' }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Processing Logs:
                  </Typography>
                  <List dense>
                    {step.logs.map((log, logIndex) => (
                      <ListItem key={logIndex} sx={{ py: 0 }}>
                        <ListItemText
                          primary={
                            <Typography variant="caption" fontFamily="monospace">
                              {log}
                            </Typography>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                </Paper>
              </Collapse>
            </motion.div>
          ))}
        </List>

        {/* Overall Progress */}
        {isProcessing && (
          <Box mt={2}>
            <Typography variant="subtitle2" gutterBottom>
              Overall Progress
            </Typography>
            <LinearProgress
              variant="determinate"
              value={(pipelineSteps.filter(s => s.status === 'completed').length / pipelineSteps.length) * 100}
              sx={{ height: 8, borderRadius: 4 }}
            />
            <Typography variant="caption" color="text.secondary">
              {pipelineSteps.filter(s => s.status === 'completed').length} of {pipelineSteps.length} steps completed
            </Typography>
          </Box>
        )}

        {/* Current Step Info */}
        {currentStep && (
          <Box mt={2} p={2} bgcolor="primary.light" borderRadius={1}>
            <Typography variant="subtitle2" color="primary.contrastText">
              Currently Processing: {pipelineSteps.find(s => s.id === currentStep)?.name}
            </Typography>
            <Typography variant="caption" color="primary.contrastText">
              {pipelineSteps.find(s => s.id === currentStep)?.description}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default DocumentProcessingPipeline;
