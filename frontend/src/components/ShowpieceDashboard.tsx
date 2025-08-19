import React, { useState, useEffect } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Grid,
  Paper,
  Alert,
  Snackbar,
  Tooltip,
  Slider,
  useTheme as useMuiTheme
} from '@mui/material';
import {
  Menu,
  Dashboard,
  Upload,
  Compare,
  Timeline,
  Analytics,
  Chat,
  Settings,
  PlayArrow,
  Pause,
  Stop,
  Refresh,
  Download,
  Share,
  RecordVoiceOver,
  Visibility,
  VisibilityOff,
  DarkMode,
  LightMode,
  Business,
  Security,
  Assessment,
  Help,
  Description,
  AutoAwesome
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

import { useTheme } from '../contexts/ThemeContext';
import ControlBar from './ControlBar';
import DocumentProcessingPipeline from './DocumentProcessingPipeline';
import DocumentViewer from './DocumentViewer';
import AgentTraceVisualization from './AgentTraceVisualization';
import AnalyticsDashboard from './AnalyticsDashboard';
import QAChat from './QAChat';

interface ShowpieceDashboardProps {
  onExport?: () => void;
  onShare?: () => void;
}

const ShowpieceDashboard: React.FC<ShowpieceDashboardProps> = ({
  onExport,
  onShare
}) => {
  const { darkMode, toggleDarkMode } = useTheme();
  const muiTheme = useMuiTheme();
  const [currentView, setCurrentView] = useState('dashboard');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [isDemoMode, setIsDemoMode] = useState(true);
  const [sidebarExpanded, setSidebarExpanded] = useState(false);
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStatus, setCurrentStatus] = useState('Ready');
  const [animationSpeed, setAnimationSpeed] = useState(1);
  const [selectedScenario, setSelectedScenario] = useState('finance');
  const [selectedPolicy, setSelectedPolicy] = useState('generic');
  const [runMode, setRunMode] = useState('live');
  const [showDemoDialog, setShowDemoDialog] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' | 'info' }>({
    open: false,
    message: '',
    severity: 'info'
  });

  // Sample data
  const [currentDocument, setCurrentDocument] = useState({
    id: 'demo-doc-1',
    name: 'Financial Services Agreement',
    content: `This Financial Services Agreement (the "Agreement") is entered into as of January 15, 2024 (the "Effective Date") by and between:

Global Financial Services, Inc., a Delaware corporation with its principal place of business at 123 Wall Street, New York, NY 10001 ("Provider")

and

Global Investment Partners, LLC, a New York limited liability company with its principal place of business at 456 Park Avenue, New York, NY 10022 ("Client")

1. SERVICES
Provider shall provide comprehensive financial advisory services including portfolio management, risk assessment, and compliance monitoring.

2. TERM
This Agreement shall commence on the Effective Date and continue for a period of three (3) years unless terminated earlier in accordance with Section 8.

3. COMPENSATION
Client shall pay Provider a monthly fee of $25,000 for services rendered, payable within 30 days of invoice.

4. CONFIDENTIALITY
Both parties agree to maintain strict confidentiality of all proprietary information shared during the term of this Agreement.

5. COMPLIANCE
Provider shall comply with all applicable SEC regulations, including but not limited to the Investment Advisers Act of 1940.

6. RISK MANAGEMENT
Provider shall implement comprehensive risk management procedures and provide monthly risk assessment reports.

7. DATA PROTECTION
All client data shall be protected in accordance with applicable data protection laws and industry best practices.

8. TERMINATION
Either party may terminate this Agreement with thirty (30) days written notice to the other party.

9. LIABILITY
Provider's liability shall be limited to the amount of fees paid by Client in the twelve months preceding any claim.

10. GOVERNING LAW
This Agreement shall be governed by the laws of the State of New York.`,
    entities: [
      { id: '1', text: 'Global Financial Services, Inc.', type: 'ORGANIZATION', start: 150, end: 180, confidence: 0.95 },
      { id: '2', text: 'Global Investment Partners, LLC', type: 'ORGANIZATION', start: 200, end: 235, confidence: 0.93 },
      { id: '3', text: 'January 15, 2024', type: 'DATE', start: 80, end: 95, confidence: 0.98 },
      { id: '4', text: '$25,000', type: 'MONEY', start: 450, end: 458, confidence: 0.96 },
      { id: '5', text: 'three (3) years', type: 'CONTRACT_TERM', start: 380, end: 395, confidence: 0.89 },
      { id: '6', text: 'thirty (30) days', type: 'CONTRACT_TERM', start: 750, end: 765, confidence: 0.91 }
    ],
    highlights: []
  });

  const [pipelineSteps, setPipelineSteps] = useState([
    {
      id: 'upload',
      name: 'Document Upload',
      icon: <Upload />,
      description: 'Document uploaded and validated',
      status: 'completed' as const,
      progress: 100,
      logs: ['Document uploaded successfully', 'File validation passed', 'OCR processing initiated'],
      duration: 1200
    },
    {
      id: 'ocr',
      name: 'OCR Processing',
      icon: <Upload />,
      description: 'Text extraction and normalization',
      status: 'completed' as const,
      progress: 100,
      logs: ['OCR processing completed', 'Text extracted: 1,247 characters', 'Language detected: English'],
      duration: 2300
    },
    {
      id: 'ner',
      name: 'Entity Recognition',
      icon: <Upload />,
      description: 'Named entity extraction',
      status: 'completed' as const,
      progress: 100,
      logs: ['6 entities identified', 'Confidence scores calculated', 'Entity types classified'],
      duration: 1800
    },
    {
      id: 'classify',
      name: 'Document Classification',
      icon: <Upload />,
      description: 'Document type and domain analysis',
      status: 'completed' as const,
      progress: 100,
      logs: ['Document type: Financial Agreement', 'Domain: Financial Services', 'Risk level: Medium'],
      duration: 1500
    },
    {
      id: 'risk',
      name: 'Risk Assessment',
      icon: <Upload />,
      description: 'Compliance and risk analysis',
      status: 'processing' as const,
      progress: 65,
      logs: ['SEC compliance check initiated', 'Risk factors identified', 'Compliance score calculated'],
      duration: 2100
    },
    {
      id: 'index',
      name: 'Document Indexing',
      icon: <Upload />,
      description: 'Vector indexing and storage',
      status: 'pending' as const,
      progress: 0,
      logs: [],
      duration: 0
    }
  ]);

  const [agentSteps, setAgentSteps] = useState([
    {
      id: '1',
      agentName: 'Classifier Agent',
      agentType: 'classifier',
      status: 'completed' as const,
      startTime: new Date(Date.now() - 5000),
      endTime: new Date(Date.now() - 3000),
      duration: 2000,
      confidence: 0.94,
      rationale: 'Document identified as financial services agreement based on key terms and structure',
      toolCalls: [
        {
          id: '1',
          name: 'classify_document_type',
          parameters: { text: 'document content...' },
          result: { type: 'Financial Agreement', confidence: 0.94 },
          duration: 1500,
          status: 'success' as const
        }
      ],
      input: { document_text: 'document content...' },
      output: { document_type: 'Financial Agreement', domain: 'Financial Services' },
      metadata: { processing_time: 2000, model_used: 'gpt-4' }
    },
    {
      id: '2',
      agentName: 'Entity Agent',
      agentType: 'entity',
      status: 'completed' as const,
      startTime: new Date(Date.now() - 3000),
      endTime: new Date(Date.now() - 1000),
      duration: 2000,
      confidence: 0.91,
      rationale: 'Extracted 6 key entities including organizations, dates, and monetary values',
      toolCalls: [
        {
          id: '2',
          name: 'extract_entities',
          parameters: { text: 'document content...' },
          result: { entities: ['Global Financial Services', 'Global Investment Partners', '$25,000'] },
          duration: 1800,
          status: 'success' as const
        }
      ],
      input: { document_text: 'document content...' },
      output: { entities: currentDocument.entities },
      metadata: { processing_time: 2000, model_used: 'gpt-4' }
    },
    {
      id: '3',
      agentName: 'Risk Agent',
      agentType: 'risk',
      status: 'running' as const,
      startTime: new Date(Date.now() - 1000),
      endTime: undefined,
      duration: 1000,
      confidence: 0.87,
      rationale: 'Analyzing compliance requirements and identifying potential risk factors',
      toolCalls: [
        {
          id: '3',
          name: 'assess_compliance_risks',
          parameters: { document_type: 'Financial Agreement', entities: 'extracted entities' },
          result: { risk_level: 'Medium', compliance_score: 0.87 },
          duration: 1000,
          status: 'success' as const
        }
      ],
      input: { document_type: 'Financial Agreement', entities: currentDocument.entities },
      output: { risk_assessment: 'In progress...' },
      metadata: { processing_time: 1000, model_used: 'gpt-4' }
    }
  ]);

     const navigationItems = [
     { id: 'dashboard', label: 'Dashboard', icon: <Dashboard /> },
     { id: 'upload', label: 'Document Upload', icon: <Upload /> },
     { id: 'viewer', label: 'Document Viewer', icon: <Visibility /> },
     { id: 'pipeline', label: 'Processing Pipeline', icon: <Timeline /> },
     { id: 'traces', label: 'Agent Traces', icon: <RecordVoiceOver /> },
     { id: 'analytics', label: 'Analytics', icon: <Analytics /> },
     { id: 'qa', label: 'aiDa Chat', icon: <Chat /> }
   ];

  const handleScenarioChange = (scenario: string) => {
    setSelectedScenario(scenario);
    setSnackbar({
      open: true,
      message: `Switched to ${scenario} scenario`,
      severity: 'success'
    });
  };

  const handlePolicyChange = (policy: string) => {
    setSelectedPolicy(policy);
    setSnackbar({
      open: true,
      message: `Applied ${policy} policy`,
      severity: 'success'
    });
  };

  const handleRunModeChange = (mode: string) => {
    setRunMode(mode);
    setSnackbar({
      open: true,
      message: `Switched to ${mode} mode`,
      severity: 'success'
    });
  };

  const handleSpeedChange = (speed: number) => {
    setAnimationSpeed(speed);
  };

  const handleSeedDemo = () => {
    setIsProcessing(true);
    setCurrentStatus('Processing');
    
    // Simulate processing
    setTimeout(() => {
      setIsProcessing(false);
      setCurrentStatus('Complete');
      setSnackbar({
        open: true,
        message: 'Processing initialized successfully!',
        severity: 'success'
      });
    }, 3000);
  };

  const handleExport = (type: string) => {
    setSnackbar({
      open: true,
      message: `${type} export started`,
      severity: 'info'
    });
  };

  const handleCitationClick = (citation: any) => {
    setSnackbar({
      open: true,
      message: `Jumping to citation: ${citation.text}`,
      severity: 'info'
    });
  };

  const handleStepClick = (step: any) => {
    setSnackbar({
      open: true,
      message: `Selected step: ${step.agentName}`,
      severity: 'info'
    });
  };

  const handleRerunStep = (stepId: string) => {
    setSnackbar({
      open: true,
      message: `Re-running step: ${stepId}`,
      severity: 'info'
    });
  };

  const handleWhatIf = (stepId: string, parameters: any) => {
    setSnackbar({
      open: true,
      message: `What-if analysis for step: ${stepId}`,
      severity: 'info'
    });
  };

  const renderCurrentView = () => {
    switch (currentView) {
             case 'dashboard':
         return (
           <Box>
                                 
            
            <Grid container spacing={3}>
                             <Grid item xs={12}>
                                   <Paper sx={{ 
                    p: 3, 
                    textAlign: 'center',
                    background: darkMode 
                      ? 'linear-gradient(135deg, #1a1a3a 0%, #2d1b69 50%, #1a1a3a 100%)'
                      : 'linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #e2e8f0 100%)',
                    borderRadius: 3,
                    boxShadow: darkMode 
                      ? '0 8px 32px rgba(0, 0, 0, 0.3), 0 2px 8px rgba(0, 0, 0, 0.2)'
                      : '0 8px 32px rgba(0, 0, 0, 0.1), 0 2px 8px rgba(0, 0, 0, 0.05)',
                    border: darkMode 
                      ? '1px solid rgba(138, 43, 226, 0.3)'
                      : '1px solid rgba(138, 43, 226, 0.1)',
                    position: 'relative',
                    overflow: 'hidden',
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: '2px',
                      background: 'linear-gradient(90deg, #8a2be2 0%, #4c1d95 50%, #8a2be2 100%)'
                    }
                  }}>
                                                            <Box display="flex" alignItems="center" justifyContent="space-between">
                       <Button
                         variant="contained"
                         startIcon={<PlayArrow />}
                         onClick={() => setShowDemoDialog(true)}
                         sx={{
                           background: 'linear-gradient(135deg, #8a2be2 0%, #4c1d95 100%)',
                           boxShadow: '0 4px 16px rgba(138, 43, 226, 0.3)',
                           '&:hover': {
                             background: 'linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%)',
                             boxShadow: '0 6px 20px rgba(138, 43, 226, 0.4)',
                             transform: 'translateY(-1px)'
                           },
                           transition: 'all 0.2s ease'
                         }}
                       >
                         Get Started
                       </Button>
                       
                       {/* Processing Detail Slider */}
                       <Box sx={{ width: '30%', mr: 6 }}>
                                                   <Typography variant="body2" sx={{ fontSize: '1rem', fontWeight: 500, mb: 1, color: darkMode ? '#cbd5e1' : '#64748b', textAlign: 'center' }}>
                            Processing Detail
                          </Typography>
                         <Box display="flex" alignItems="center">
                           <Slider
                             defaultValue={3}
                             min={1}
                             max={5}
                             step={1}
                             size="small"
                             sx={{ 
                               flexGrow: 1,
                               '& .MuiSlider-track': {
                                 background: 'linear-gradient(90deg, #8a2be2 0%, #4c1d95 100%)'
                               },
                               '& .MuiSlider-thumb': {
                                 background: 'linear-gradient(135deg, #8a2be2 0%, #4c1d95 100%)',
                                 boxShadow: '0 2px 8px rgba(138, 43, 226, 0.3)'
                               }
                             }}
                             marks={[
                               { value: 1, label: 'Quick' },
                               { value: 3, label: 'Standard' },
                               { value: 5, label: 'Deep' }
                             ]}
                           />
                         </Box>
                       </Box>
                     </Box>
                 </Paper>
               </Grid>
              
                             <Grid item xs={12}>
                                   <Paper sx={{ 
                    p: 4, 
                    textAlign: 'center',
                    background: darkMode 
                      ? 'linear-gradient(135deg, #1a1a3a 0%, #2d1b69 50%, #1a1a3a 100%)'
                      : 'linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #e2e8f0 100%)',
                    borderRadius: 3,
                    boxShadow: darkMode 
                      ? '0 8px 32px rgba(0, 0, 0, 0.3), 0 2px 8px rgba(0, 0, 0, 0.2)'
                      : '0 8px 32px rgba(0, 0, 0, 0.1), 0 2px 8px rgba(0, 0, 0, 0.05)',
                    border: darkMode 
                      ? '1px solid rgba(138, 43, 226, 0.3)'
                      : '1px solid rgba(138, 43, 226, 0.1)',
                    position: 'relative',
                    overflow: 'hidden',
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: '2px',
                      background: 'linear-gradient(90deg, #8a2be2 0%, #4c1d95 50%, #8a2be2 100%)'
                    }
                  }}>
                                                            <Box display="flex" justifyContent="space-around" mt={1}>
                       <Box textAlign="center">
                                                   <Typography variant="body2" sx={{ color: darkMode ? '#cbd5e1' : '#64748b', fontWeight: 500, mb: 1 }}>Active Agents</Typography>
                         <Typography variant="h3" sx={{
                           background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                           backgroundClip: 'text',
                           WebkitBackgroundClip: 'text',
                           WebkitTextFillColor: 'transparent',
                           fontWeight: 700,
                           textShadow: '0 0 20px rgba(16, 185, 129, 0.3)'
                         }}>
                           9
                         </Typography>
                       </Box>
                       <Box textAlign="center">
                                                   <Typography variant="body2" sx={{ color: darkMode ? '#cbd5e1' : '#64748b', fontWeight: 500, mb: 1 }}>Uptime</Typography>
                         <Typography variant="h3" sx={{
                           background: 'linear-gradient(135deg, #8a2be2 0%, #4c1d95 100%)',
                           backgroundClip: 'text',
                           WebkitBackgroundClip: 'text',
                           WebkitTextFillColor: 'transparent',
                           fontWeight: 700,
                           textShadow: '0 0 20px rgba(138, 43, 226, 0.3)'
                         }}>
                           99.8%
                         </Typography>
                       </Box>
                       <Box textAlign="center">
                                                   <Typography variant="body2" sx={{ color: darkMode ? '#cbd5e1' : '#64748b', fontWeight: 500, mb: 1 }}>Avg Processing</Typography>
                         <Typography variant="h3" sx={{
                           background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                           backgroundClip: 'text',
                           WebkitBackgroundClip: 'text',
                           WebkitTextFillColor: 'transparent',
                           fontWeight: 700,
                           textShadow: '0 0 20px rgba(245, 158, 11, 0.3)'
                         }}>
                           2.3s
                         </Typography>
                       </Box>
                       <Box textAlign="center">
                                                   <Typography variant="body2" sx={{ color: darkMode ? '#cbd5e1' : '#64748b', fontWeight: 500, mb: 1 }}>System Status</Typography>
                         <Box sx={{
                           background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                           borderRadius: '50%',
                           width: '80px',
                           height: '80px',
                           display: 'flex',
                           alignItems: 'center',
                           justifyContent: 'center',
                           margin: '0 auto',
                           boxShadow: '0 4px 16px rgba(16, 185, 129, 0.3)',
                           border: '2px solid rgba(16, 185, 129, 0.2)'
                         }}>
                           <Typography sx={{
                             fontSize: '2.5rem',
                             color: 'white',
                             fontWeight: 'bold',
                             filter: 'drop-shadow(0 0 8px rgba(16, 185, 129, 0.6))'
                           }}>
                             ✓
                           </Typography>
                         </Box>
                       </Box>
                     </Box>
                 </Paper>
               </Grid>
            </Grid>
          </Box>
        );
        
      case 'upload':
        return (
          <Box>
            <DocumentProcessingPipeline
              isProcessing={isProcessing}
              currentStep="risk"
              pipelineSteps={pipelineSteps}
              onStepClick={(stepId) => console.log('Step clicked:', stepId)}
              animationSpeed={animationSpeed}
            />
          </Box>
        );
        
      case 'viewer':
        return (
          <Box>
            <DocumentViewer
              documentId={currentDocument.id}
              documentName={currentDocument.name}
              documentContent={currentDocument.content}
              entities={currentDocument.entities as any}
              highlights={currentDocument.highlights}
              onEntityClick={(entity) => console.log('Entity clicked:', entity)}
              onHighlightToggle={(entity) => console.log('Highlight toggled:', entity)}
              onSearch={(query) => console.log('Search:', query)}
              onExport={() => handleExport('document')}
            />
          </Box>
        );
        
      case 'pipeline':
        return (
          <Box>
            <Typography variant="h4" gutterBottom>
              Processing Pipeline
            </Typography>
            <DocumentProcessingPipeline
              isProcessing={isProcessing}
              currentStep="risk"
              pipelineSteps={pipelineSteps}
              onStepClick={(stepId) => console.log('Step clicked:', stepId)}
              animationSpeed={animationSpeed}
            />
          </Box>
        );
        
      case 'traces':
        return (
          <Box>
            <Typography variant="h4" gutterBottom>
              Agent Trace Visualization
            </Typography>
            <AgentTraceVisualization
              traceId="demo-trace-1"
              steps={agentSteps}
              isLive={isProcessing}
              onStepClick={handleStepClick}
              onRerunStep={handleRerunStep}
              onWhatIf={handleWhatIf}
              animationSpeed={animationSpeed}
            />
          </Box>
        );
        
      case 'analytics':
        return (
          <Box>
            <Typography variant="h4" gutterBottom>
              Analytics Dashboard
            </Typography>
            <AnalyticsDashboard
              timeRange="7d"
              onTimeRangeChange={(range) => console.log('Time range:', range)}
              onRefresh={() => console.log('Refresh analytics')}
              onExport={() => handleExport('analytics')}
            />
          </Box>
        );
        
      case 'qa':
        return (
          <Box>
            <QAChat
              documentId={currentDocument.id}
              documentName={currentDocument.name}
              onCitationClick={handleCitationClick}
              onExport={() => handleExport('chat')}
              onShare={() => onShare?.()}
            />
          </Box>
        );
        
      default:
        return <Typography>Select a view from the navigation</Typography>;
    }
  };

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
             {/* App Bar */}
               <AppBar position="fixed" sx={{ 
          zIndex: (theme) => theme.zIndex.drawer + 1,
          background: darkMode 
            ? 'linear-gradient(135deg, #0f0f23 0%, #1a1a3a 50%, #2d1b69 100%)'
            : 'linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #e2e8f0 100%)',
          backdropFilter: 'blur(10px)',
          borderBottom: darkMode 
            ? '1px solid rgba(138, 43, 226, 0.2)'
            : '1px solid rgba(138, 43, 226, 0.1)',
          boxShadow: darkMode 
            ? '0 4px 20px rgba(0, 0, 0, 0.3)'
            : '0 4px 20px rgba(0, 0, 0, 0.1)'
        }}>
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => setDrawerOpen(!drawerOpen)}
            sx={{ mr: 2 }}
          >
            <Menu />
          </IconButton>
          
                     <Typography variant="h6" component="div" sx={{ 
             flexGrow: 1,
             fontFamily: '"Orbitron", "Roboto", sans-serif',
             fontWeight: 700,
             letterSpacing: '0.05em',
             background: 'linear-gradient(135deg, #ffffff 0%, #e0e7ff 100%)',
             backgroundClip: 'text',
             WebkitBackgroundClip: 'text',
             WebkitTextFillColor: 'transparent',
             textShadow: '0 0 20px rgba(138, 43, 226, 0.3)'
           }}>
             aiDa
           </Typography>
          
                                           <Box display="flex" alignItems="center" gap={1}>
              <Chip
                label={isDemoMode ? 'Processing' : 'Ready'}
                color={isDemoMode ? 'warning' : 'success'}
                size="small"
                sx={{
                  animation: isDemoMode ? 'blink 2s ease-in-out infinite' : 'none',
                  '@keyframes blink': {
                    '0%, 100%': { opacity: 1 },
                    '50%': { opacity: 0.3 }
                  },
                  background: isDemoMode 
                    ? 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'
                    : 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  color: 'white',
                  fontWeight: 600,
                  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.2)',
                  border: '1px solid rgba(255, 255, 255, 0.1)'
                }}
              />
                          <IconButton 
                sx={{ color: darkMode ? 'white' : 'black' }} 
                onClick={toggleDarkMode}
              >
                {darkMode ? <LightMode /> : <DarkMode />}
              </IconButton>
             <IconButton 
               sx={{ color: darkMode ? 'white' : 'black' }} 
               onClick={() => onExport?.()}
             >
               <Download />
             </IconButton>
             <IconButton 
               sx={{ color: darkMode ? 'white' : 'black' }} 
               onClick={() => onShare?.()}
             >
               <Share />
             </IconButton>
             <IconButton sx={{ color: darkMode ? 'white' : 'black' }}>
               <Settings />
             </IconButton>
           </Box>
        </Toolbar>
      </AppBar>

                    {/* Navigation Drawer */}
                 <Drawer
           variant="permanent"
           sx={{
             width: sidebarExpanded ? 240 : 80,
             flexShrink: 0,
             transition: 'width 0.3s ease',
                           '& .MuiDrawer-paper': {
                width: sidebarExpanded ? 240 : 80,
                boxSizing: 'border-box',
                marginTop: '64px',
                display: 'flex',
                flexDirection: 'column',
                alignItems: sidebarExpanded ? 'stretch' : 'center',
                paddingTop: 2,
                transition: 'width 0.3s ease',
                position: 'relative',
                background: darkMode 
                  ? 'linear-gradient(180deg, #0f0f23 0%, #1a1a3a 50%, #2d1b69 100%)'
                  : 'linear-gradient(180deg, #ffffff 0%, #f8fafc 50%, #e2e8f0 100%)',
                borderRight: darkMode 
                  ? '1px solid rgba(138, 43, 226, 0.2)'
                  : '1px solid rgba(138, 43, 226, 0.1)',
                boxShadow: darkMode 
                  ? '4px 0 20px rgba(0, 0, 0, 0.3)'
                  : '4px 0 20px rgba(0, 0, 0, 0.1)'
              }
           }}
         >
          {/* Resize Handle */}
          <Box
            sx={{
              position: 'absolute',
              right: 0,
              top: 0,
              bottom: 0,
              width: '4px',
              cursor: 'col-resize',
              backgroundColor: 'transparent',
              '&:hover': {
                backgroundColor: 'rgba(0, 0, 0, 0.1)'
              },
              '&:active': {
                backgroundColor: 'rgba(0, 0, 0, 0.2)'
              }
            }}
            onMouseDown={(e) => {
              e.preventDefault();
              const startX = e.clientX;
              const startExpanded = sidebarExpanded;
              
              const handleMouseMove = (moveEvent: MouseEvent) => {
                const deltaX = moveEvent.clientX - startX;
                if (deltaX > 50 && !startExpanded) {
                  setSidebarExpanded(true);
                } else if (deltaX < -50 && startExpanded) {
                  setSidebarExpanded(false);
                }
              };
              
              const handleMouseUp = () => {
                document.removeEventListener('mousemove', handleMouseMove);
                document.removeEventListener('mouseup', handleMouseUp);
              };
              
              document.addEventListener('mousemove', handleMouseMove);
              document.addEventListener('mouseup', handleMouseUp);
            }}
          />
          
                     <List sx={{ width: '100%', padding: 0 }}>
             {navigationItems.map((item) => (
               <Tooltip
                 key={item.id}
                 title={item.label}
                 placement="right"
                 arrow
                 sx={{
                                       '& .MuiTooltip-tooltip': {
                      backgroundColor: 'rgba(0, 0, 0, 0.9)',
                      color: 'white',
                      fontSize: '1.25rem',
                      padding: '12px 20px',
                      borderRadius: '8px',
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
                      border: '1px solid rgba(255, 255, 255, 0.1)'
                    }
                 }}
               >
                 <Box>
                   <ListItem
                     button
                     selected={currentView === item.id}
                     onClick={() => setCurrentView(item.id)}
                                 sx={{
                   flexDirection: sidebarExpanded ? 'row' : 'column',
                   padding: sidebarExpanded ? '12px 16px' : '16px 8px',
                   marginBottom: 1,
                   borderRadius: 2,
                   mx: sidebarExpanded ? 1 : 1,
                   minHeight: 'auto',
                   position: 'relative',
                   cursor: 'pointer',
                   transition: 'all 0.2s ease',
                   '&:hover': {
                     backgroundColor: 'rgba(138, 43, 226, 0.15)',
                     transform: 'translateX(4px)',
                     boxShadow: '0 4px 12px rgba(138, 43, 226, 0.3)'
                   },
                   '&.Mui-selected': {
                     backgroundColor: 'rgba(138, 43, 226, 0.25)',
                     boxShadow: '0 4px 16px rgba(138, 43, 226, 0.4)',
                     border: '1px solid rgba(138, 43, 226, 0.3)'
                   }
                 }}
              >
                                                                                                       <ListItemIcon sx={{ 
                     minWidth: sidebarExpanded ? 40 : 'auto',
                     fontSize: sidebarExpanded ? '2.5rem' : '3rem',
                     color: currentView === item.id 
                       ? '#8a2be2' 
                       : darkMode 
                         ? 'rgba(255, 255, 255, 0.7)'
                         : 'rgba(0, 0, 0, 0.7)',
                     transition: 'all 0.2s ease',
                     filter: currentView === item.id 
                       ? 'drop-shadow(0 0 8px rgba(138, 43, 226, 0.6))'
                       : 'none'
                   }}>
                   {item.icon}
                                    </ListItemIcon>
                 </ListItem>
                   </Box>
                 </Tooltip>
             ))}
           </List>
        </Drawer>

                    {/* Main Content */}
                          <Box
            component="main"
                         sx={{
               flexGrow: 1,
               marginTop: '64px',
               marginLeft: sidebarExpanded ? '240px' : '80px',
               padding: 1,
               background: darkMode 
                 ? 'linear-gradient(135deg, #0f0f23 0%, #1a1a3a 25%, #2d1b69 50%, #1a1a3a 75%, #0f0f23 100%)'
                 : 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 25%, #cbd5e1 50%, #e2e8f0 75%, #f8fafc 100%)',
               minHeight: 'calc(100vh - 64px)',
               overflow: 'auto',
               transition: 'margin-left 0.3s ease'
             }}
          >
                          <Box sx={{ 
           background: 'linear-gradient(135deg, #0f0f23 0%, #1a1a3a 25%, #2d1b69 50%, #1a1a3a 75%, #0f0f23 100%)',
           color: 'white',
           p: 4,
           borderRadius: 3,
           mb: 4,
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
               <AutoAwesome sx={{ 
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
                   aiDa Dashboard
                 </Typography>
                 <Typography variant="h6" sx={{ 
                   opacity: 0.95,
                   background: 'linear-gradient(135deg, #cbd5e1 0%, #94a3b8 100%)',
                   backgroundClip: 'text',
                   WebkitBackgroundClip: 'text',
                   WebkitTextFillColor: 'transparent'
                 }}>
                   Intelligent Document Processing & Analysis Platform
                 </Typography>
               </Box>
           </Box>
         </Box>

        {/* Control Bar */}
        <ControlBar
          onScenarioChange={handleScenarioChange}
          onPolicyChange={handlePolicyChange}
          onRunModeChange={handleRunModeChange}
          onSpeedChange={handleSpeedChange}
          onSeedDemo={handleSeedDemo}
          onExport={handleExport}
          isProcessing={isProcessing}
          currentStatus={currentStatus}
        />

        {/* Current View Content */}
        <motion.div
          key={currentView}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
        >
          {renderCurrentView()}
        </motion.div>
      </Box>

      {/* Setup Dialog */}
      <Dialog
        open={showDemoDialog}
        onClose={() => setShowDemoDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Configure Processing</DialogTitle>
        <DialogContent>
          <Typography variant="body1" paragraph>
            Choose your processing scenario and settings:
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Scenario</InputLabel>
                <Select
                  value={selectedScenario}
                  onChange={(e) => setSelectedScenario(e.target.value)}
                  label="Scenario"
                >
                  <MenuItem value="finance">Finance & Banking</MenuItem>
                  <MenuItem value="healthcare">Healthcare</MenuItem>
                  <MenuItem value="insurance">Insurance</MenuItem>
                  <MenuItem value="legal">Legal & Compliance</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Policy</InputLabel>
                <Select
                  value={selectedPolicy}
                  onChange={(e) => setSelectedPolicy(e.target.value)}
                  label="Policy"
                >
                  <MenuItem value="generic">Generic Compliance</MenuItem>
                  <MenuItem value="hipaa">HIPAA</MenuItem>
                  <MenuItem value="sec">SEC Regulations</MenuItem>
                  <MenuItem value="gdpr">GDPR</MenuItem>
                  <MenuItem value="sox">SOX</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowDemoDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              setShowDemoDialog(false);
              handleSeedDemo();
            }}
          >
            Start Processing
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ShowpieceDashboard;
