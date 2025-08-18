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
  Snackbar
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
  Help
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

import DemoControlBar from './DemoControlBar';
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
  const [currentView, setCurrentView] = useState('dashboard');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [isDemoMode, setIsDemoMode] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStatus, setCurrentStatus] = useState('Ready');
  const [animationSpeed, setAnimationSpeed] = useState(1);
  const [selectedScenario, setSelectedScenario] = useState('finance');
  const [selectedPolicy, setSelectedPolicy] = useState('generic');
  const [runMode, setRunMode] = useState('live');
  const [darkMode, setDarkMode] = useState(false);
  const [showDemoDialog, setShowDemoDialog] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' | 'info' }>({
    open: false,
    message: '',
    severity: 'info'
  });

  // Sample data
  const [currentDocument, setCurrentDocument] = useState({
    id: 'demo-doc-1',
    name: 'Financial Services Agreement - Demo',
    content: `FINANCIAL SERVICES AGREEMENT

This Financial Services Agreement (the "Agreement") is entered into as of January 15, 2024 (the "Effective Date") by and between:

ACME Financial Services, Inc., a Delaware corporation with its principal place of business at 123 Wall Street, New York, NY 10001 ("Provider")

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
      { id: '1', text: 'ACME Financial Services, Inc.', type: 'ORGANIZATION', start: 150, end: 180, confidence: 0.95 },
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
          result: { entities: ['ACME Financial Services', 'Global Investment Partners', '$25,000'] },
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
    { id: 'traces', label: 'Agent Traces', icon: <Timeline /> },
    { id: 'analytics', label: 'Analytics', icon: <Analytics /> },
    { id: 'qa', label: 'Q&A Chat', icon: <Chat /> }
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
        message: 'Demo data seeded successfully!',
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
            <Typography variant="h4" gutterBottom>
              Smart Document Bot - Showpiece Dashboard
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              Welcome to the fully agentic document processing system. This demo showcases the complete capabilities
              of our AI-powered document analysis platform.
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3, textAlign: 'center' }}>
                  <Typography variant="h6" gutterBottom>
                    🚀 Quick Start
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Use the Demo Control Bar above to select scenarios, policies, and run modes.
                    Then click "Seed Demo" to start the demonstration.
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<PlayArrow />}
                    onClick={() => setShowDemoDialog(true)}
                  >
                    Start Demo
                  </Button>
                </Paper>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3, textAlign: 'center' }}>
                  <Typography variant="h6" gutterBottom>
                    📊 System Status
                  </Typography>
                  <Box display="flex" justifyContent="space-around" mt={2}>
                    <Box textAlign="center">
                      <Typography variant="h4" color="success.main">9</Typography>
                      <Typography variant="caption">Active Agents</Typography>
                    </Box>
                    <Box textAlign="center">
                      <Typography variant="h4" color="primary.main">99.8%</Typography>
                      <Typography variant="caption">Uptime</Typography>
                    </Box>
                    <Box textAlign="center">
                      <Typography variant="h4" color="warning.main">2.3s</Typography>
                      <Typography variant="caption">Avg Processing</Typography>
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
            <Typography variant="h4" gutterBottom>
              Document Upload & Processing
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
        
      case 'viewer':
        return (
          <Box>
            <Typography variant="h4" gutterBottom>
              Document Viewer with Analysis
            </Typography>
            <DocumentViewer
              documentId={currentDocument.id}
              documentName={currentDocument.name}
              documentContent={currentDocument.content}
              entities={currentDocument.entities}
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
            <Typography variant="h4" gutterBottom>
              Q&A Assistant
            </Typography>
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
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => setDrawerOpen(!drawerOpen)}
            sx={{ mr: 2 }}
          >
            <Menu />
          </IconButton>
          
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Smart Document Bot - Showpiece
          </Typography>
          
          <Box display="flex" alignItems="center" gap={1}>
            <Chip
              label={isDemoMode ? 'Demo Mode' : 'Live Mode'}
              color={isDemoMode ? 'warning' : 'success'}
              size="small"
            />
            <IconButton color="inherit" onClick={() => setDarkMode(!darkMode)}>
              {darkMode ? <LightMode /> : <DarkMode />}
            </IconButton>
            <IconButton color="inherit" onClick={() => onExport?.()}>
              <Download />
            </IconButton>
            <IconButton color="inherit" onClick={() => onShare?.()}>
              <Share />
            </IconButton>
            <IconButton color="inherit">
              <Settings />
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Navigation Drawer */}
      <Drawer
        variant="permanent"
        sx={{
          width: 240,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: 240,
            boxSizing: 'border-box',
            marginTop: '64px'
          }
        }}
      >
        <List>
          {navigationItems.map((item) => (
            <ListItem
              button
              key={item.id}
              selected={currentView === item.id}
              onClick={() => setCurrentView(item.id)}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItem>
          ))}
        </List>
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          marginTop: '64px',
          padding: 3,
          backgroundColor: 'background.default',
          minHeight: 'calc(100vh - 64px)',
          overflow: 'auto'
        }}
      >
        {/* Demo Control Bar */}
        <DemoControlBar
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

      {/* Demo Dialog */}
      <Dialog
        open={showDemoDialog}
        onClose={() => setShowDemoDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Start Demo</DialogTitle>
        <DialogContent>
          <Typography variant="body1" paragraph>
            Choose your demo scenario and settings:
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
            Start Demo
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
