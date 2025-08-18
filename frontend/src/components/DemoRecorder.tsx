import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  LinearProgress,
  Paper,
  Divider,
  Tooltip,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  Stop,
  RecordVoiceOver,
  Download,
  Settings,
  Speed,
  Timeline,
  CheckCircle,
  Schedule,
  Error,
  Refresh,
  Save,
  Share,
  Visibility,
  VisibilityOff
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

interface DemoStep {
  id: string;
  title: string;
  description: string;
  action: string;
  duration: number;
  status: 'pending' | 'running' | 'completed' | 'error';
  timestamp?: Date;
}

interface DemoScript {
  id: string;
  name: string;
  description: string;
  scenario: string;
  policy: string;
  steps: DemoStep[];
  totalDuration: number;
  tags: string[];
}

interface DemoRecorderProps {
  onDemoStart?: (script: DemoScript) => void;
  onDemoStep?: (step: DemoStep) => void;
  onDemoComplete?: (script: DemoScript) => void;
  onExport?: (type: string) => void;
}

const DemoRecorder: React.FC<DemoRecorderProps> = ({
  onDemoStart,
  onDemoStep,
  onDemoComplete,
  onExport
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [currentScript, setCurrentScript] = useState<DemoScript | null>(null);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [showScriptDialog, setShowScriptDialog] = useState(false);
  const [recordingSettings, setRecordingSettings] = useState({
    includeAudio: false,
    showCursor: true,
    highlightElements: true,
    autoScroll: true,
    quality: 'high' as 'low' | 'medium' | 'high'
  });
  const [demoProgress, setDemoProgress] = useState(0);
  const recordingRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const predefinedScripts: DemoScript[] = [
    {
      id: 'finance-demo',
      name: 'Financial Services Compliance Demo',
      description: 'Complete demonstration of financial document processing with SEC compliance analysis',
      scenario: 'finance',
      policy: 'sec',
      totalDuration: 180,
      tags: ['finance', 'compliance', 'sec'],
      steps: [
        {
          id: '1',
          title: 'Document Upload',
          description: 'Upload financial services agreement',
          action: 'upload_document',
          duration: 5,
          status: 'pending'
        },
        {
          id: '2',
          title: 'OCR Processing',
          description: 'Extract text from document',
          action: 'ocr_processing',
          duration: 8,
          status: 'pending'
        },
        {
          id: '3',
          title: 'Entity Recognition',
          description: 'Identify key entities and organizations',
          action: 'entity_extraction',
          duration: 12,
          status: 'pending'
        },
        {
          id: '4',
          title: 'Document Classification',
          description: 'Classify document type and domain',
          action: 'document_classification',
          duration: 6,
          status: 'pending'
        },
        {
          id: '5',
          title: 'Risk Assessment',
          description: 'Analyze compliance risks and requirements',
          action: 'risk_assessment',
          duration: 15,
          status: 'pending'
        },
        {
          id: '6',
          title: 'Q&A Analysis',
          description: 'Generate and answer compliance questions',
          action: 'qa_analysis',
          duration: 10,
          status: 'pending'
        },
        {
          id: '7',
          title: 'Report Generation',
          description: 'Create compliance report and recommendations',
          action: 'report_generation',
          duration: 8,
          status: 'pending'
        }
      ]
    },
    {
      id: 'healthcare-demo',
      name: 'Healthcare HIPAA Compliance Demo',
      description: 'Demonstration of healthcare document processing with HIPAA compliance analysis',
      scenario: 'healthcare',
      policy: 'hipaa',
      totalDuration: 150,
      tags: ['healthcare', 'hipaa', 'privacy'],
      steps: [
        {
          id: '1',
          title: 'Patient Data Agreement Upload',
          description: 'Upload patient data processing agreement',
          action: 'upload_document',
          duration: 5,
          status: 'pending'
        },
        {
          id: '2',
          title: 'PHI Detection',
          description: 'Identify protected health information',
          action: 'phi_detection',
          duration: 10,
          status: 'pending'
        },
        {
          id: '3',
          title: 'HIPAA Compliance Check',
          description: 'Verify HIPAA compliance requirements',
          action: 'hipaa_compliance',
          duration: 12,
          status: 'pending'
        },
        {
          id: '4',
          title: 'Security Assessment',
          description: 'Assess security measures and safeguards',
          action: 'security_assessment',
          duration: 8,
          status: 'pending'
        },
        {
          id: '5',
          title: 'Breach Notification Analysis',
          description: 'Review breach notification procedures',
          action: 'breach_analysis',
          duration: 6,
          status: 'pending'
        }
      ]
    },
    {
      id: 'insurance-demo',
      name: 'Insurance Policy Analysis Demo',
      description: 'Demonstration of insurance policy analysis and risk assessment',
      scenario: 'insurance',
      policy: 'generic',
      totalDuration: 120,
      tags: ['insurance', 'risk', 'policy'],
      steps: [
        {
          id: '1',
          title: 'Policy Document Upload',
          description: 'Upload cyber liability insurance policy',
          action: 'upload_document',
          duration: 5,
          status: 'pending'
        },
        {
          id: '2',
          title: 'Coverage Analysis',
          description: 'Analyze coverage limits and terms',
          action: 'coverage_analysis',
          duration: 10,
          status: 'pending'
        },
        {
          id: '3',
          title: 'Risk Assessment',
          description: 'Assess covered and excluded risks',
          action: 'risk_assessment',
          duration: 12,
          status: 'pending'
        },
        {
          id: '4',
          title: 'Claims Process Review',
          description: 'Review claims notification procedures',
          action: 'claims_review',
          duration: 8,
          status: 'pending'
        }
      ]
    },
    {
      id: 'legal-demo',
      name: 'Legal Contract Analysis Demo',
      description: 'Demonstration of legal contract analysis and compliance review',
      scenario: 'legal',
      policy: 'generic',
      totalDuration: 140,
      tags: ['legal', 'contract', 'compliance'],
      steps: [
        {
          id: '1',
          title: 'Contract Upload',
          description: 'Upload software licensing agreement',
          action: 'upload_document',
          duration: 5,
          status: 'pending'
        },
        {
          id: '2',
          title: 'Contract Terms Analysis',
          description: 'Extract and analyze key contract terms',
          action: 'terms_analysis',
          duration: 15,
          status: 'pending'
        },
        {
          id: '3',
          title: 'Liability Assessment',
          description: 'Assess liability limitations and obligations',
          action: 'liability_assessment',
          duration: 10,
          status: 'pending'
        },
        {
          id: '4',
          title: 'Intellectual Property Review',
          description: 'Review IP rights and restrictions',
          action: 'ip_review',
          duration: 8,
          status: 'pending'
        },
        {
          id: '5',
          title: 'Compliance Verification',
          description: 'Verify legal compliance requirements',
          action: 'compliance_verification',
          duration: 12,
          status: 'pending'
        }
      ]
    }
  ];

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: {
          mediaSource: 'screen',
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        },
        audio: recordingSettings.includeAudio
      });

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'video/webm;codecs=vp9'
      });

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'video/webm' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `demo-recording-${Date.now()}.webm`;
        a.click();
        URL.revokeObjectURL(url);
        chunksRef.current = [];
      };

      recordingRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Failed to start recording:', error);
    }
  };

  const stopRecording = () => {
    if (recordingRef.current) {
      recordingRef.current.stop();
      recordingRef.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
    }
  };

  const startDemo = (script: DemoScript) => {
    setCurrentScript(script);
    setCurrentStepIndex(0);
    setDemoProgress(0);
    
    // Reset all steps to pending
    const updatedScript = {
      ...script,
      steps: script.steps.map(step => ({ ...step, status: 'pending' as const }))
    };
    setCurrentScript(updatedScript);
    
    onDemoStart?.(updatedScript);
    
    // Start the demo execution
    executeDemoStep(updatedScript, 0);
  };

  const executeDemoStep = (script: DemoScript, stepIndex: number) => {
    if (stepIndex >= script.steps.length) {
      // Demo complete
      onDemoComplete?.(script);
      return;
    }

    const updatedSteps = [...script.steps];
    updatedSteps[stepIndex] = {
      ...updatedSteps[stepIndex],
      status: 'running',
      timestamp: new Date()
    };

    const updatedScript = { ...script, steps: updatedSteps };
    setCurrentScript(updatedScript);
    setCurrentStepIndex(stepIndex);
    onDemoStep?.(updatedSteps[stepIndex]);

    // Simulate step execution
    setTimeout(() => {
      const completedSteps = [...updatedSteps];
      completedSteps[stepIndex] = {
        ...completedSteps[stepIndex],
        status: 'completed'
      };

      const completedScript = { ...script, steps: completedSteps };
      setCurrentScript(completedScript);
      
      // Update progress
      const progress = ((stepIndex + 1) / script.steps.length) * 100;
      setDemoProgress(progress);

      // Execute next step
      setTimeout(() => {
        executeDemoStep(completedScript, stepIndex + 1);
      }, 1000);
    }, script.steps[stepIndex].duration * 1000);
  };

  const pauseDemo = () => {
    // Implementation for pausing demo
  };

  const resumeDemo = () => {
    // Implementation for resuming demo
  };

  const renderDemoStep = (step: DemoStep, index: number) => {
    const isCurrent = currentStepIndex === index;
    const isCompleted = step.status === 'completed';
    const isRunning = step.status === 'running';

    return (
      <motion.div
        key={step.id}
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: index * 0.1 }}
      >
        <ListItem
          sx={{
            border: isCurrent ? 2 : 1,
            borderColor: isCurrent ? 'primary.main' : 'divider',
            borderRadius: 1,
            mb: 1,
            backgroundColor: isRunning ? 'action.hover' : 'transparent'
          }}
        >
          <ListItemIcon>
            {isCompleted ? (
              <CheckCircle color="success" />
            ) : isRunning ? (
              <Schedule color="primary" />
            ) : (
              <Timeline color="disabled" />
            )}
          </ListItemIcon>
          <ListItemText
            primary={
              <Box display="flex" alignItems="center" gap={1}>
                <Typography variant="subtitle2">
                  {step.title}
                </Typography>
                <Chip
                  label={step.status}
                  size="small"
                  color={isCompleted ? 'success' : isRunning ? 'primary' : 'default'}
                />
                <Typography variant="caption" color="text.secondary">
                  {step.duration}s
                </Typography>
              </Box>
            }
            secondary={step.description}
          />
        </ListItem>
      </motion.div>
    );
  };

  return (
    <Box>
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <Typography variant="h6" display="flex" alignItems="center">
              <RecordVoiceOver sx={{ mr: 1 }} />
              Demo Recorder & Scripts
            </Typography>
            <Box display="flex" alignItems="center" gap={1}>
              <Tooltip title="Recording Settings">
                <IconButton onClick={() => setShowScriptDialog(true)}>
                  <Settings />
                </IconButton>
              </Tooltip>
              <Button
                variant={isRecording ? 'outlined' : 'contained'}
                startIcon={isRecording ? <Stop /> : <RecordVoiceOver />}
                onClick={isRecording ? stopRecording : startRecording}
                color={isRecording ? 'error' : 'primary'}
              >
                {isRecording ? 'Stop Recording' : 'Start Recording'}
              </Button>
            </Box>
          </Box>

          {/* Demo Scripts */}
          <Typography variant="subtitle1" gutterBottom>
            Predefined Demo Scripts
          </Typography>
          
          <Box display="flex" gap={2} mb={3} sx={{ overflowX: 'auto' }}>
            {predefinedScripts.map((script) => (
              <Card
                key={script.id}
                sx={{
                  minWidth: 280,
                  cursor: 'pointer',
                  '&:hover': { elevation: 4 }
                }}
                onClick={() => startDemo(script)}
              >
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {script.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {script.description}
                  </Typography>
                  <Box display="flex" gap={1} mb={2}>
                    {script.tags.map((tag) => (
                      <Chip key={tag} label={tag} size="small" variant="outlined" />
                    ))}
                  </Box>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="caption" color="text.secondary">
                      Duration: {Math.floor(script.totalDuration / 60)}m {script.totalDuration % 60}s
                    </Typography>
                    <Button size="small" variant="outlined">
                      Start Demo
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Box>

          {/* Current Demo Progress */}
          {currentScript && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                Current Demo: {currentScript.name}
              </Typography>
              
              <Box display="flex" alignItems="center" gap={2} mb={2}>
                <LinearProgress
                  variant="determinate"
                  value={demoProgress}
                  sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
                />
                <Typography variant="body2">
                  {Math.round(demoProgress)}%
                </Typography>
              </Box>

              <List>
                {currentScript.steps.map((step, index) => renderDemoStep(step, index))}
              </List>
            </Box>
          )}

          {/* Recording Settings Dialog */}
          <Dialog
            open={showScriptDialog}
            onClose={() => setShowScriptDialog(false)}
            maxWidth="sm"
            fullWidth
          >
            <DialogTitle>Recording Settings</DialogTitle>
            <DialogContent>
              <Box display="flex" flexDirection="column" gap={2}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={recordingSettings.includeAudio}
                      onChange={(e) => setRecordingSettings({
                        ...recordingSettings,
                        includeAudio: e.target.checked
                      })}
                    />
                  }
                  label="Include Audio"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={recordingSettings.showCursor}
                      onChange={(e) => setRecordingSettings({
                        ...recordingSettings,
                        showCursor: e.target.checked
                      })}
                    />
                  }
                  label="Show Cursor"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={recordingSettings.highlightElements}
                      onChange={(e) => setRecordingSettings({
                        ...recordingSettings,
                        highlightElements: e.target.checked
                      })}
                    />
                  }
                  label="Highlight Elements"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={recordingSettings.autoScroll}
                      onChange={(e) => setRecordingSettings({
                        ...recordingSettings,
                        autoScroll: e.target.checked
                      })}
                    />
                  }
                  label="Auto Scroll"
                />
                <FormControl fullWidth>
                  <InputLabel>Recording Quality</InputLabel>
                  <Select
                    value={recordingSettings.quality}
                    onChange={(e) => setRecordingSettings({
                      ...recordingSettings,
                      quality: e.target.value as 'low' | 'medium' | 'high'
                    })}
                    label="Recording Quality"
                  >
                    <MenuItem value="low">Low (720p)</MenuItem>
                    <MenuItem value="medium">Medium (1080p)</MenuItem>
                    <MenuItem value="high">High (4K)</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setShowScriptDialog(false)}>Cancel</Button>
              <Button onClick={() => setShowScriptDialog(false)} variant="contained">
                Save Settings
              </Button>
            </DialogActions>
          </Dialog>
        </CardContent>
      </Card>
    </Box>
  );
};

export default DemoRecorder;
