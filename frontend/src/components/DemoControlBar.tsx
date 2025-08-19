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
  Assessment
} from '@mui/icons-material';
import { toast } from 'react-hot-toast';

interface DemoControlBarProps {
  onScenarioChange: (scenario: string) => void;
  onPolicyChange: (policy: string) => void;
  onRunModeChange: (mode: string) => void;
  onSpeedChange: (speed: number) => void;
  onSeedDemo: () => void;
  onExport: (type: string) => void;
  isProcessing: boolean;
  currentStatus: string;
}

const DemoControlBar: React.FC<DemoControlBarProps> = ({
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
      name: 'Live Processing',
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
    toast.success('Demo data seeded successfully!');
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
          <Typography variant="h6" gutterBottom>
            AI Document Agent Demo Controls
          </Typography>
          <Box display="flex" alignItems="center" gap={1}>
            <Chip
              label={currentStatus}
              color={getStatusColor(currentStatus)}
              size="small"
            />
            {isProcessing && <LinearProgress sx={{ width: 100 }} />}
            <Tooltip title="Advanced Settings">
              <IconButton
                size="small"
                onClick={() => setShowAdvanced(!showAdvanced)}
              >
                <Settings />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        <Grid container spacing={2}>
          {/* Scenario Selection */}
          <Grid item xs={12} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Scenario</InputLabel>
              <Select
                value={selectedScenario}
                label="Scenario"
                onChange={(e) => handleScenarioChange(e.target.value)}
                disabled={isProcessing}
              >
                {Object.entries(scenarios).map(([key, scenario]) => (
                  <MenuItem key={key} value={key}>
                    <Box display="flex" alignItems="center">
                      <span style={{ marginRight: 8 }}>{scenario.icon}</span>
                      <Box>
                        <Typography variant="body2">{scenario.name}</Typography>
                        <Typography variant="caption" color="text.secondary">
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
          <Grid item xs={12} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Policy</InputLabel>
              <Select
                value={selectedPolicy}
                label="Policy"
                onChange={(e) => handlePolicyChange(e.target.value)}
                disabled={isProcessing}
              >
                {Object.entries(policies).map(([key, policy]) => (
                  <MenuItem key={key} value={key}>
                    <Box display="flex" alignItems="center">
                      <span style={{ marginRight: 8 }}>{policy.icon}</span>
                      <Box>
                        <Typography variant="body2">{policy.name}</Typography>
                        <Typography variant="caption" color="text.secondary">
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
          <Grid item xs={12} md={2}>
            <FormControl fullWidth size="small">
              <InputLabel>Run Mode</InputLabel>
              <Select
                value={runMode}
                label="Run Mode"
                onChange={(e) => handleRunModeChange(e.target.value)}
                disabled={isProcessing}
              >
                {Object.entries(runModes).map(([key, mode]) => (
                  <MenuItem key={key} value={key}>
                    <Box display="flex" alignItems="center">
                      {mode.icon}
                      <Typography variant="body2" sx={{ ml: 1 }}>
                        {mode.name}
                      </Typography>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Animation Speed */}
          <Grid item xs={12} md={2}>
            <Box>
              <Typography variant="caption" display="block" gutterBottom>
                Animation Speed
              </Typography>
              <Box display="flex" alignItems="center" gap={1}>
                <Speed sx={{ fontSize: 16 }} />
                <Slider
                  value={animationSpeed}
                  onChange={handleSpeedChange}
                  min={0.1}
                  max={3}
                  step={0.1}
                  size="small"
                  disabled={isProcessing}
                  sx={{ flexGrow: 1 }}
                />
                <Typography variant="caption" sx={{ minWidth: 30 }}>
                  {animationSpeed}x
                </Typography>
              </Box>
            </Box>
          </Grid>

          {/* Action Buttons */}
          <Grid item xs={12} md={2}>
            <Box display="flex" gap={1}>
              <Button
                variant="contained"
                size="small"
                onClick={handleSeedDemo}
                disabled={isProcessing}
                startIcon={<Refresh />}
                fullWidth
              >
                Seed Demo
              </Button>
            </Box>
          </Grid>
        </Grid>

        {/* Advanced Settings */}
        {showAdvanced && (
          <>
            <Divider sx={{ my: 2 }} />
            <Grid container spacing={2}>
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

export default DemoControlBar;
