import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Grid,
  Paper,
  Tabs,
  Tab,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Badge,
  Switch,
  FormControlLabel,
  Slider,
  Rating,
  LinearProgress
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Refresh,
  Settings,
  Info,
  CheckCircle,
  Error,
  Warning,
  ExpandMore,
  Add,
  Remove,
  ContentCopy,
  Download,
  Upload,
  Analytics,
  Psychology,
  Translate,
  Summarize,
  Security,
  Compare,
  QuestionAnswer,
  Audit,
  Classify,
  Search
} from '@mui/icons-material';
import { unifiedAgentService, agentUtils, AgentCapabilitiesResponse, AgentStatusResponse } from '../services/unifiedAgentService';
import { toast } from 'react-hot-toast';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`agent-tabpanel-${index}`}
      aria-labelledby={`agent-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

interface AgentExecutionState {
  loading: boolean;
  result: any;
  error: string | null;
  executionId: string | null;
}

const UnifiedAgentInterface: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [capabilities, setCapabilities] = useState<AgentCapabilitiesResponse | null>(null);
  const [status, setStatus] = useState<AgentStatusResponse | null>(null);
  const [selectedAgent, setSelectedAgent] = useState<string>('summarizer');
  const [documentContent, setDocumentContent] = useState<string>('');
  const [goal, setGoal] = useState<string>('');
  const [parameters, setParameters] = useState<Record<string, any>>({});
  const [executionState, setExecutionState] = useState<AgentExecutionState>({
    loading: false,
    result: null,
    error: null,
    executionId: null
  });
  const [batchMode, setBatchMode] = useState<boolean>(false);
  const [selectedAgents, setSelectedAgents] = useState<string[]>(['summarizer']);
  const [executionHistory, setExecutionHistory] = useState<any[]>([]);

  // Load capabilities and status on component mount
  useEffect(() => {
    loadCapabilities();
    loadStatus();
    const interval = setInterval(loadStatus, 30000); // Refresh status every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadCapabilities = async () => {
    try {
      const response = await unifiedAgentService.getAgentCapabilities();
      setCapabilities(response);
    } catch (error) {
      console.error('Failed to load capabilities:', error);
      toast.error('Failed to load agent capabilities');
    }
  };

  const loadStatus = async () => {
    try {
      const response = await unifiedAgentService.getAgentStatus();
      setStatus(response);
    } catch (error) {
      console.error('Failed to load status:', error);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleAgentChange = (agentType: string) => {
    setSelectedAgent(agentType);
    setGoal(`Process document with ${agentType} agent`);
    setParameters({});
  };

  const handleParameterChange = (key: string, value: any) => {
    setParameters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const executeAgent = async () => {
    if (!documentContent.trim()) {
      toast.error('Please enter document content');
      return;
    }

    setExecutionState({
      loading: true,
      result: null,
      error: null,
      executionId: null
    });

    try {
      const response = await unifiedAgentService.executeAgent({
        agent_type: selectedAgent,
        document_content: documentContent,
        goal: goal || `Process document with ${selectedAgent} agent`,
        parameters
      });

      setExecutionState({
        loading: false,
        result: response.result,
        error: null,
        executionId: response.execution_id
      });

      // Add to execution history
      setExecutionHistory(prev => [{
        id: response.execution_id,
        agent_type: selectedAgent,
        timestamp: new Date().toISOString(),
        result: response.result,
        confidence: response.confidence,
        status: 'completed'
      }, ...prev.slice(0, 9)]); // Keep last 10 executions

      toast.success(`Agent execution completed with ${agentUtils.formatConfidence(response.confidence)} confidence`);
      loadStatus(); // Refresh status
    } catch (error: any) {
      setExecutionState({
        loading: false,
        result: null,
        error: error.message || 'Execution failed',
        executionId: null
      });
      toast.error('Agent execution failed');
    }
  };

  const executeBatch = async () => {
    if (!documentContent.trim()) {
      toast.error('Please enter document content');
      return;
    }

    if (selectedAgents.length === 0) {
      toast.error('Please select at least one agent');
      return;
    }

    setExecutionState({
      loading: true,
      result: null,
      error: null,
      executionId: null
    });

    try {
      const executions = selectedAgents.map(agentType => ({
        agent_type: agentType,
        document_content: documentContent,
        goal: `Process document with ${agentType} agent`,
        parameters: {}
      }));

      const response = await unifiedAgentService.batchExecuteAgents({ executions });

      setExecutionState({
        loading: false,
        result: response.results,
        error: null,
        executionId: response.batch_id
      });

      // Add to execution history
      response.results.forEach((result: any) => {
        setExecutionHistory(prev => [{
          id: result.execution_id,
          agent_type: result.agent_type,
          timestamp: new Date().toISOString(),
          result: result.result,
          confidence: result.confidence,
          status: 'completed'
        }, ...prev.slice(0, 9)]);
      });

      toast.success(`Batch execution completed with ${response.results.length} agents`);
      loadStatus();
    } catch (error: any) {
      setExecutionState({
        loading: false,
        result: null,
        error: error.message || 'Batch execution failed',
        executionId: null
      });
      toast.error('Batch execution failed');
    }
  };

  const handleAgentToggle = (agentType: string) => {
    setSelectedAgents(prev => 
      prev.includes(agentType)
        ? prev.filter(agent => agent !== agentType)
        : [...prev, agentType]
    );
  };

  const copyResult = () => {
    if (executionState.result) {
      navigator.clipboard.writeText(JSON.stringify(executionState.result, null, 2));
      toast.success('Result copied to clipboard');
    }
  };

  const clearResults = () => {
    setExecutionState({
      loading: false,
      result: null,
      error: null,
      executionId: null
    });
  };

  const getAgentParameters = (agentType: string) => {
    const parameterConfigs: Record<string, any> = {
      summarizer: {
        summary_type: {
          type: 'select',
          label: 'Summary Type',
          options: ['abstractive', 'extractive', 'executive', 'technical'],
          default: 'abstractive'
        },
        summary_length: {
          type: 'select',
          label: 'Summary Length',
          options: ['short', 'medium', 'long'],
          default: 'medium'
        }
      },
      translator: {
        target_language: {
          type: 'select',
          label: 'Target Language',
          options: ['es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko'],
          default: 'es'
        },
        translation_style: {
          type: 'select',
          label: 'Translation Style',
          options: ['formal', 'informal', 'technical', 'literary'],
          default: 'formal'
        }
      },
      sentiment: {
        analysis_depth: {
          type: 'select',
          label: 'Analysis Depth',
          options: ['basic', 'detailed', 'comprehensive'],
          default: 'comprehensive'
        }
      }
    };

    return parameterConfigs[agentType] || {};
  };

  const renderParameterInput = (key: string, config: any) => {
    const value = parameters[key] || config.default;

    switch (config.type) {
      case 'select':
        return (
          <FormControl fullWidth key={key} sx={{ mb: 2 }}>
            <InputLabel>{config.label}</InputLabel>
            <Select
              value={value}
              label={config.label}
              onChange={(e) => handleParameterChange(key, e.target.value)}
            >
              {config.options.map((option: string) => (
                <MenuItem key={option} value={option}>
                  {option.charAt(0).toUpperCase() + option.slice(1)}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        );
      case 'slider':
        return (
          <Box key={key} sx={{ mb: 2 }}>
            <Typography gutterBottom>{config.label}</Typography>
            <Slider
              value={value}
              onChange={(e, newValue) => handleParameterChange(key, newValue)}
              min={config.min || 0}
              max={config.max || 100}
              valueLabelDisplay="auto"
            />
          </Box>
        );
      default:
        return (
          <TextField
            key={key}
            fullWidth
            label={config.label}
            value={value}
            onChange={(e) => handleParameterChange(key, e.target.value)}
            sx={{ mb: 2 }}
          />
        );
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Unified Agent Interface
      </Typography>

      {/* Status Overview */}
      {status && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              System Status
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="primary">
                    {status.agent_statistics.total_executions}
                  </Typography>
                  <Typography variant="body2">Total Executions</Typography>
                </Box>
              </Grid>
              <Grid item xs={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="success.main">
                    {status.agent_statistics.successful_executions}
                  </Typography>
                  <Typography variant="body2">Successful</Typography>
                </Box>
              </Grid>
              <Grid item xs={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="error.main">
                    {status.agent_statistics.failed_executions}
                  </Typography>
                  <Typography variant="body2">Failed</Typography>
                </Box>
              </Grid>
              <Grid item xs={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="warning.main">
                    {status.agent_statistics.active_processing}
                  </Typography>
                  <Typography variant="body2">Active</Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Single Agent" />
          <Tab label="Batch Processing" />
          <Tab label="Agent Capabilities" />
          <Tab label="Execution History" />
        </Tabs>
      </Box>

      {/* Single Agent Tab */}
      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Agent Selection
                </Typography>
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Select Agent</InputLabel>
                  <Select
                    value={selectedAgent}
                    label="Select Agent"
                    onChange={(e) => handleAgentChange(e.target.value)}
                  >
                    {capabilities?.capabilities && Object.keys(capabilities.capabilities).map(agentType => (
                      <MenuItem key={agentType} value={agentType}>
                        <Box display="flex" alignItems="center">
                          <span style={{ marginRight: 8 }}>{agentUtils.getAgentIcon(agentType)}</span>
                          {capabilities.capabilities[agentType].name}
                        </Box>
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                {capabilities?.capabilities[selectedAgent] && (
                  <Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {capabilities.capabilities[selectedAgent].description}
                    </Typography>
                    <Box sx={{ mt: 1 }}>
                      {capabilities.capabilities[selectedAgent].capabilities.map((capability: string) => (
                        <Chip
                          key={capability}
                          label={capability}
                          size="small"
                          sx={{ mr: 0.5, mb: 0.5 }}
                        />
                      ))}
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>

            {/* Parameters */}
            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Parameters
                </Typography>
                {Object.entries(getAgentParameters(selectedAgent)).map(([key, config]) =>
                  renderParameterInput(key, config)
                )}
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Document Content
                </Typography>
                <TextField
                  fullWidth
                  multiline
                  rows={8}
                  value={documentContent}
                  onChange={(e) => setDocumentContent(e.target.value)}
                  placeholder="Enter document content to process..."
                  sx={{ mb: 2 }}
                />

                <TextField
                  fullWidth
                  value={goal}
                  onChange={(e) => setGoal(e.target.value)}
                  placeholder="Enter processing goal..."
                  sx={{ mb: 2 }}
                />

                <Button
                  variant="contained"
                  onClick={executeAgent}
                  disabled={executionState.loading || !documentContent.trim()}
                  startIcon={executionState.loading ? <CircularProgress size={20} /> : <PlayArrow />}
                  sx={{ mr: 1 }}
                >
                  {executionState.loading ? 'Processing...' : 'Execute Agent'}
                </Button>

                <Button
                  variant="outlined"
                  onClick={clearResults}
                  disabled={executionState.loading}
                >
                  Clear
                </Button>
              </CardContent>
            </Card>

            {/* Results */}
            {executionState.result && (
              <Card sx={{ mt: 2 }}>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="h6">
                      Results
                    </Typography>
                    <Box>
                      <Tooltip title="Copy Result">
                        <IconButton onClick={copyResult} size="small">
                          <ContentCopy />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </Box>

                  {executionState.executionId && (
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Execution ID: {executionState.executionId}
                    </Typography>
                  )}

                  <Paper sx={{ p: 2, bgcolor: 'grey.50', maxHeight: 400, overflow: 'auto' }}>
                    <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                      {JSON.stringify(executionState.result, null, 2)}
                    </pre>
                  </Paper>
                </CardContent>
              </Card>
            )}

            {executionState.error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {executionState.error}
              </Alert>
            )}
          </Grid>
        </Grid>
      </TabPanel>

      {/* Batch Processing Tab */}
      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Select Agents for Batch Processing
                </Typography>
                {capabilities?.capabilities && Object.keys(capabilities.capabilities).map(agentType => (
                  <FormControlLabel
                    key={agentType}
                    control={
                      <Switch
                        checked={selectedAgents.includes(agentType)}
                        onChange={() => handleAgentToggle(agentType)}
                      />
                    }
                    label={
                      <Box display="flex" alignItems="center">
                        <span style={{ marginRight: 8 }}>{agentUtils.getAgentIcon(agentType)}</span>
                        {capabilities.capabilities[agentType].name}
                      </Box>
                    }
                  />
                ))}
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Document Content
                </Typography>
                <TextField
                  fullWidth
                  multiline
                  rows={8}
                  value={documentContent}
                  onChange={(e) => setDocumentContent(e.target.value)}
                  placeholder="Enter document content to process with multiple agents..."
                  sx={{ mb: 2 }}
                />

                <Button
                  variant="contained"
                  onClick={executeBatch}
                  disabled={executionState.loading || !documentContent.trim() || selectedAgents.length === 0}
                  startIcon={executionState.loading ? <CircularProgress size={20} /> : <PlayArrow />}
                >
                  {executionState.loading ? 'Processing...' : `Execute ${selectedAgents.length} Agents`}
                </Button>
              </CardContent>
            </Card>

            {/* Batch Results */}
            {executionState.result && Array.isArray(executionState.result) && (
              <Card sx={{ mt: 2 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Batch Results
                  </Typography>
                  {executionState.result.map((result: any, index: number) => (
                    <Accordion key={index}>
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Box display="flex" alignItems="center" width="100%">
                          <span style={{ marginRight: 8 }}>
                            {agentUtils.getAgentIcon(result.agent_type)}
                          </span>
                          <Typography sx={{ flexGrow: 1 }}>
                            {result.agent_type.charAt(0).toUpperCase() + result.agent_type.slice(1)}
                          </Typography>
                          <Chip
                            label={agentUtils.formatConfidence(result.confidence)}
                            color="primary"
                            size="small"
                          />
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                          <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                            {JSON.stringify(result.result, null, 2)}
                          </pre>
                        </Paper>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </CardContent>
              </Card>
            )}
          </Grid>
        </Grid>
      </TabPanel>

      {/* Agent Capabilities Tab */}
      <TabPanel value={tabValue} index={2}>
        {capabilities && (
          <Grid container spacing={2}>
            {Object.entries(capabilities.capabilities).map(([agentType, agentInfo]) => (
              <Grid item xs={12} md={6} lg={4} key={agentType}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center" mb={2}>
                      <span style={{ fontSize: '2rem', marginRight: 12 }}>
                        {agentUtils.getAgentIcon(agentType)}
                      </span>
                      <Box>
                        <Typography variant="h6">{agentInfo.name}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {agentInfo.status} • v{agentInfo.version}
                        </Typography>
                      </Box>
                    </Box>

                    <Typography variant="body2" gutterBottom>
                      {agentInfo.description}
                    </Typography>

                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Capabilities:
                      </Typography>
                      {agentInfo.capabilities.map((capability: string) => (
                        <Chip
                          key={capability}
                          label={capability}
                          size="small"
                          sx={{ mr: 0.5, mb: 0.5 }}
                        />
                      ))}
                    </Box>

                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Technical Info:
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Formats: {agentInfo.supported_formats.join(', ')}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Execution: {agentInfo.execution_time}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Memory: {agentInfo.memory_usage}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </TabPanel>

      {/* Execution History Tab */}
      <TabPanel value={tabValue} index={3}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recent Executions
            </Typography>
            {executionHistory.length === 0 ? (
              <Typography color="text.secondary">
                No executions yet. Run an agent to see history.
              </Typography>
            ) : (
              <List>
                {executionHistory.map((execution) => (
                  <ListItem key={execution.id} divider>
                    <ListItemIcon>
                      <span style={{ fontSize: '1.5rem' }}>
                        {agentUtils.getAgentIcon(execution.agent_type)}
                      </span>
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box display="flex" alignItems="center">
                          <Typography variant="subtitle1">
                            {execution.agent_type.charAt(0).toUpperCase() + execution.agent_type.slice(1)}
                          </Typography>
                          <Chip
                            label={agentUtils.formatConfidence(execution.confidence)}
                            color="primary"
                            size="small"
                            sx={{ ml: 1 }}
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            {new Date(execution.timestamp).toLocaleString()}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Status: {execution.status}
                          </Typography>
                        </Box>
                      }
                    />
                    <IconButton
                      onClick={() => {
                        setExecutionState({
                          loading: false,
                          result: execution.result,
                          error: null,
                          executionId: execution.id
                        });
                        setTabValue(0);
                      }}
                    >
                      <Info />
                    </IconButton>
                  </ListItem>
                ))}
              </List>
            )}
          </CardContent>
        </Card>
      </TabPanel>
    </Box>
  );
};

export default UnifiedAgentInterface;
