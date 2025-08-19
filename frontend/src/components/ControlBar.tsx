import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Slider,
  Switch,
  FormControlLabel,
  Chip,
  IconButton,
  Tooltip,
  Divider,
  Grid,
  Alert,
  LinearProgress
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  FastForward,
  Settings,
  Download,
  Upload,
  Refresh,
  Speed,
  Policy,
  Business,
  Security,
  Timeline,
  Analytics,
  Assessment,
  Tune
} from '@mui/icons-material';
import { toast } from 'react-hot-toast';

interface ControlBarProps {
  onScenarioChange: (scenario: string) => void;
  onPolicyChange: (policy: string) => void;
  onRunModeChange: (mode: string) => void;
  onSpeedChange: (speed: number) => void;
  onSeedDemo: () => void;
  onExport: (type: string) => void;
  isProcessing: boolean;
  currentStatus: string;
}

const ControlBar: React.FC<ControlBarProps> = ({
  onScenarioChange,
  onPolicyChange,
  onRunModeChange,
  onSpeedChange,
  onSeedDemo,
  onExport,
  isProcessing,
  currentStatus
}) => {
  const [selectedScenario, setSelectedScenario] = useState('finance');
  const [selectedPolicy, setSelectedPolicy] = useState('generic');
  const [runMode, setRunMode] = useState('live');
  const [animationSpeed, setAnimationSpeed] = useState(1);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const scenarios = {
    finance: {
      name: 'Finance & Banking',
      icon: '🏦',
      description: 'SEC regulations, banking compliance, financial reporting'
    },
    healthcare: {
      name: 'Healthcare',
      icon: '🏥',
      description: 'HIPAA compliance, medical records, patient privacy'
    },
    insurance: {
      name: 'Insurance',
      icon: '🛡️',
      description: 'Policy compliance, claims processing, regulatory reporting'
    },
    legal: {
      name: 'Legal & Compliance',
      icon: '⚖️',
      description: 'Contract analysis, legal compliance, regulatory frameworks'
    }
  };

  const policies = {
    generic: {
      name: 'Generic Compliance',
      icon: '📋',
      description: 'General regulatory compliance framework'
    },
    hipaa: {
      name: 'HIPAA',
      icon: '🏥',
      description: 'Healthcare privacy and security standards'
    },
    sec: {
      name: 'SEC Regulations',
      icon: '📊',
      description: 'Securities and Exchange Commission compliance'
    },
    gdpr: {
      name: 'GDPR',
      icon: '🌍',
      description: 'General Data Protection Regulation'
    },
    sox: {
      name: 'SOX',
      icon: '📈',
      description: 'Sarbanes-Oxley Act compliance'
    }
  };

  const runModes = {
    live: {
      name: 'Live',
      icon: <PlayArrow />,
      description: 'Real-time agent execution with live updates'
    },
    step: {
      name: 'Step-by-Step',
      icon: <Timeline />,
      description: 'Manual control over each agent step'
    },
    fast: {
      name: 'Fast-Forward',
      icon: <FastForward />,
      description: 'Accelerated processing for demo purposes'
    }
  };

  const handleScenarioChange = (scenario: string) => {
    setSelectedScenario(scenario);
    onScenarioChange(scenario);
    toast.success(`Switched to ${scenarios[scenario as keyof typeof scenarios].name} scenario`);
  };

  const handlePolicyChange = (policy: string) => {
    setSelectedPolicy(policy);
    onPolicyChange(policy);
    toast.success(`Applied ${policies[policy as keyof typeof policies].name} policy`);
  };

  const handleRunModeChange = (mode: string) => {
    setRunMode(mode);
    onRunModeChange(mode);
    toast.success(`Switched to ${runModes[mode as keyof typeof runModes].name} mode`);
  };

  const handleSpeedChange = (event: Event, newValue: number | number[]) => {
    const speed = newValue as number;
    setAnimationSpeed(speed);
    onSpeedChange(speed);
  };

  const handleSeedDemo = () => {
    onSeedDemo();
    toast.success('Processing initialized successfully!');
  };

  const handleExport = (type: string) => {
    onExport(type);
    toast.success(`${type} export started`);
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'processing':
        return 'warning';
      case 'complete':
        return 'success';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Card sx={{ mb: 3, position: 'sticky', top: 0, zIndex: 1000 }}>
      <CardContent>
                 <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
           <Tooltip 
             title="Use the Control Bar to select scenarios, policies, and run modes. Configure your processing settings to get started."
             arrow
             placement="bottom"
           >
             <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1, cursor: 'pointer' }}>
               <Tune sx={{ fontSize: '1.5rem' }} />
               Controls
             </Typography>
           </Tooltip>
          <Box display="flex" alignItems="center" gap={1}>
                         <Chip
               label={currentStatus}
               color={getStatusColor(currentStatus)}
               size="small"
               sx={{
                 animation: currentStatus === 'Ready' ? 'blink 2s ease-in-out infinite' : 'none',
                 '@keyframes blink': {
                   '0%, 100%': { opacity: 1 },
                   '50%': { opacity: 0.3 }
                 },
                 background: currentStatus === 'Ready' 
                   ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                   : currentStatus === 'Processing'
                   ? 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'
                   : 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                 color: 'white',
                 fontWeight: 600,
                 boxShadow: '0 2px 8px rgba(0, 0, 0, 0.2)',
                 border: '1px solid rgba(255, 255, 255, 0.1)'
               }}
             />
            {isProcessing && <LinearProgress sx={{ width: 100 }} />}
          </Box>
        </Box>

                 <Grid container spacing={3}>
                     {/* Scenario Selection */}
           <Grid item xs={12} md={4}>
             <FormControl fullWidth size="small">
               <InputLabel sx={{ fontSize: '1.2rem', fontWeight: 600 }}>Scenario</InputLabel>
                               <Select
                  value={selectedScenario}
                  label="Scenario"
                  onChange={(e) => handleScenarioChange(e.target.value)}
                  disabled={isProcessing}
                  renderValue={(value) => {
                    const scenario = scenarios[value as keyof typeof scenarios];
                    return (
                      <Box display="flex" alignItems="center" sx={{ width: '100%' }}>
                        <span style={{ marginRight: 8 }}>{scenario.icon}</span>
                        <Typography variant="body1" sx={{ fontSize: '1.2rem', wordWrap: 'break-word' }}>
                          {scenario.name}
                        </Typography>
                      </Box>
                    );
                  }}
                  sx={{ 
                    '& .MuiSelect-select': { 
                      fontSize: '1.2rem',
                      minHeight: '120px',
                      maxWidth: 'calc(100% - 20px)',
                      display: 'flex',
                      alignItems: 'flex-start',
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      overflowWrap: 'break-word',
                      lineHeight: 1.4,
                      padding: '12px 16px'
                    },
                    '& .MuiMenuItem-root': { 
                      fontSize: '1.2rem',
                      minHeight: '120px',
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      overflowWrap: 'break-word',
                      lineHeight: 1.4,
                      padding: '12px 16px'
                    }
                  }}
                >
                {Object.entries(scenarios).map(([key, scenario]) => (
                  <MenuItem key={key} value={key}>
                    <Box display="flex" alignItems="flex-start" sx={{ width: '100%' }}>
                      <span style={{ marginRight: 8, marginTop: 2 }}>{scenario.icon}</span>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="body1" sx={{ fontSize: '1rem', wordWrap: 'break-word' }}>{scenario.name}</Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.9rem', wordWrap: 'break-word' }}>
                          {scenario.description}
                        </Typography>
                      </Box>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

                     {/* Policy Selection */}
           <Grid item xs={12} md={4}>
             <FormControl fullWidth size="small">
               <InputLabel sx={{ fontSize: '1.2rem', fontWeight: 600 }}>Policy</InputLabel>
                               <Select
                  value={selectedPolicy}
                  label="Policy"
                  onChange={(e) => handlePolicyChange(e.target.value)}
                  disabled={isProcessing}
                  renderValue={(value) => {
                    const policy = policies[value as keyof typeof policies];
                    return (
                      <Box display="flex" alignItems="center" sx={{ width: '100%' }}>
                        <span style={{ marginRight: 8 }}>{policy.icon}</span>
                        <Typography variant="body1" sx={{ fontSize: '1.2rem', wordWrap: 'break-word' }}>
                          {policy.name}
                        </Typography>
                      </Box>
                    );
                  }}
                  sx={{ 
                    '& .MuiSelect-select': { 
                      fontSize: '1.2rem',
                      minHeight: '120px',
                      maxWidth: 'calc(100% - 20px)',
                      display: 'flex',
                      alignItems: 'flex-start',
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      overflowWrap: 'break-word',
                      lineHeight: 1.4,
                      padding: '12px 16px'
                    },
                    '& .MuiMenuItem-root': { 
                      fontSize: '1.2rem',
                      minHeight: '120px',
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      overflowWrap: 'break-word',
                      lineHeight: 1.4,
                      padding: '12px 16px'
                    }
                  }}
                >
                {Object.entries(policies).map(([key, policy]) => (
                  <MenuItem key={key} value={key}>
                    <Box display="flex" alignItems="flex-start" sx={{ width: '100%' }}>
                      <span style={{ marginRight: 8, marginTop: 2 }}>{policy.icon}</span>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="body1" sx={{ fontSize: '1rem', wordWrap: 'break-word' }}>{policy.name}</Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.9rem', wordWrap: 'break-word' }}>
                          {policy.description}
                        </Typography>
                      </Box>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

                     {/* Run Mode */}
           <Grid item xs={12} md={4}>
             <FormControl fullWidth size="small">
               <InputLabel sx={{ fontSize: '1.2rem', fontWeight: 600 }}>Run Mode</InputLabel>
                               <Select
                  value={runMode}
                  label="Run Mode"
                  onChange={(e) => handleRunModeChange(e.target.value)}
                  disabled={isProcessing}
                  renderValue={(value) => {
                    const mode = runModes[value as keyof typeof runModes];
                    return (
                      <Box display="flex" alignItems="center" sx={{ width: '100%' }}>
                        <Box sx={{ marginRight: 1 }}>{mode.icon}</Box>
                        <Typography variant="body1" sx={{ fontSize: '1.2rem', wordWrap: 'break-word' }}>
                          {mode.name}
                        </Typography>
                      </Box>
                    );
                  }}
                  sx={{ 
                    '& .MuiSelect-select': { 
                      fontSize: '1.2rem',
                      minHeight: '120px',
                      maxWidth: 'calc(100% - 20px)',
                      display: 'flex',
                      alignItems: 'flex-start',
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      overflowWrap: 'break-word',
                      lineHeight: 1.4,
                      padding: '12px 16px'
                    },
                    '& .MuiMenuItem-root': { 
                      fontSize: '1.2rem',
                      minHeight: '120px',
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      overflowWrap: 'break-word',
                      lineHeight: 1.4,
                      padding: '12px 16px'
                    }
                  }}
                >
                                 {Object.entries(runModes).map(([key, mode]) => (
                   <MenuItem key={key} value={key}>
                     <Box display="flex" alignItems="flex-start" sx={{ width: '100%' }}>
                       <Box sx={{ marginRight: 1, marginTop: 1 }}>{mode.icon}</Box>
                                               <Typography variant="body1" sx={{ ml: 1, fontSize: '1rem', wordWrap: 'break-word', flex: 1, marginTop: '10px' }}>
                          {mode.name}
                        </Typography>
                     </Box>
                   </MenuItem>
                 ))}
              </Select>
            </FormControl>
          </Grid>

          
        </Grid>

        {/* Advanced Settings */}
        {showAdvanced && (
          <>
            <Divider sx={{ my: 2 }} />
            <Grid container spacing={3}>
              <Grid item xs={12} md={3}>
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Enable Real-time Updates"
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <FormControlLabel
                  control={<Switch />}
                  label="Show Agent Rationales"
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Auto-save Results"
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <FormControlLabel
                  control={<Switch />}
                  label="Debug Mode"
                />
              </Grid>
            </Grid>

            {/* Export Options */}
            <Box mt={2}>
              <Typography variant="subtitle2" gutterBottom>
                Export Options:
              </Typography>
              <Box display="flex" gap={1} flexWrap="wrap">
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => handleExport('audit')}
                  startIcon={<Assessment />}
                >
                  Audit Bundle
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => handleExport('kpi')}
                  startIcon={<Analytics />}
                >
                  KPI Report
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => handleExport('screenshot')}
                  startIcon={<Download />}
                >
                  Screenshot
                </Button>
              </Box>
            </Box>
          </>
        )}

        {/* Status Messages */}
        {isProcessing && (
          <Alert severity="info" sx={{ mt: 2 }}>
            Processing document with {selectedScenario} scenario and {selectedPolicy} policy...
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

export default ControlBar;
