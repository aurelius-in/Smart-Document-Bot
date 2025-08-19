import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Paper,
  Divider,
  IconButton,
  Tooltip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Switch,
  FormControlLabel,
  Tabs,
  Tab,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Speed,
  Psychology,
  Build,
  DataUsage,
  Memory,
  Timeline,
  Assessment,
  CheckCircle,
  Error,
  Warning,
  Info,
  Refresh,
  Download,
  Share,
  Settings,
  BarChart,
  PieChart,
  ShowChart,
  BubbleChart,
  Timeline as TimelineIcon,
  Analytics,
  Dashboard,
  FilterList
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

interface KPI {
  id: string;
  name: string;
  value: number;
  unit: string;
  change: number;
  changeType: 'increase' | 'decrease' | 'neutral';
  icon: React.ReactNode;
  color: string;
}

interface ChartData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    backgroundColor?: string;
    borderColor?: string;
    fill?: boolean;
  }>;
}

interface AnalyticsDashboardProps {
  timeRange: '1h' | '24h' | '7d' | '30d' | '90d';
  onTimeRangeChange: (range: string) => void;
  onRefresh: () => void;
  onExport: () => void;
}

const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({
  timeRange,
  onTimeRangeChange,
  onRefresh,
  onExport
}) => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [showRealTime, setShowRealTime] = useState(true);
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(['all']);

  // Mock KPI data
  const kpis: KPI[] = [
    {
      id: 'documents_processed',
      name: 'Documents Processed',
      value: 1247,
      unit: '',
      change: 12.5,
      changeType: 'increase',
      icon: <Timeline />,
      color: '#4CAF50'
    },
    {
      id: 'avg_processing_time',
      name: 'Avg Processing Time',
      value: 2.3,
      unit: 's',
      change: -8.2,
      changeType: 'decrease',
      icon: <Speed />,
      color: '#2196F3'
    },
    {
      id: 'accuracy_rate',
      name: 'Accuracy Rate',
      value: 94.2,
      unit: '%',
      change: 2.1,
      changeType: 'increase',
      icon: <CheckCircle />,
      color: '#4CAF50'
    },
    {
      id: 'policy_violations',
      name: 'Policy Violations',
      value: 23,
      unit: '',
      change: -15.3,
      changeType: 'decrease',
      icon: <Warning />,
      color: '#FF9800'
    },
    {
      id: 'human_overrides',
      name: 'Human Overrides',
      value: 8,
      unit: '',
      change: 5.2,
      changeType: 'increase',
      icon: <Psychology />,
      color: '#9C27B0'
    },
    {
      id: 'system_uptime',
      name: 'System Uptime',
      value: 99.8,
      unit: '%',
      change: 0.1,
      changeType: 'increase',
      icon: <CheckCircle />,
      color: '#4CAF50'
    }
  ];

  // Mock chart data
  const processingTrendData: ChartData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Documents Processed',
        data: [120, 145, 132, 167, 189, 156, 178],
        borderColor: '#4CAF50',
        backgroundColor: 'rgba(76, 175, 80, 0.1)',
        fill: true
      },
      {
        label: 'Processing Time (s)',
        data: [2.1, 2.3, 2.0, 2.5, 2.2, 2.4, 2.1],
        borderColor: '#2196F3',
        backgroundColor: 'rgba(33, 150, 243, 0.1)',
        fill: true
      }
    ]
  };

  const agentPerformanceData: ChartData = {
    labels: ['Classifier', 'Entity', 'Risk', 'QA', 'Compare', 'Audit', 'Summarizer', 'Translator', 'Sentiment'],
    datasets: [
      {
        label: 'Accuracy (%)',
        data: [96, 94, 89, 92, 91, 95, 93, 88, 90],
        backgroundColor: '#4CAF50'
      }
    ]
  };

  const policyComplianceData: ChartData = {
    labels: ['HIPAA', 'GDPR', 'SOX', 'SEC', 'PCI-DSS', 'ISO 27001'],
    datasets: [
      {
        label: 'Compliance Rate (%)',
        data: [98.5, 97.2, 96.8, 95.4, 99.1, 94.7],
        backgroundColor: '#8BC34A'
      }
    ]
  };

  const renderKPICard = (kpi: KPI) => (
    <motion.div
      key={kpi.id}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <Box
              sx={{
                p: 1,
                borderRadius: '50%',
                backgroundColor: `${kpi.color}20`,
                color: kpi.color
              }}
            >
              {kpi.icon}
            </Box>
            <Chip
              label={`${kpi.change > 0 ? '+' : ''}${kpi.change}%`}
              size="small"
              color={kpi.changeType === 'increase' ? 'success' : kpi.changeType === 'decrease' ? 'error' : 'default'}
              icon={kpi.changeType === 'increase' ? <TrendingUp /> : <TrendingDown />}
            />
          </Box>
          <Typography variant="h4" gutterBottom>
            {kpi.value}{kpi.unit}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {kpi.name}
          </Typography>
        </CardContent>
      </Card>
    </motion.div>
  );

  const renderChart = (title: string, data: ChartData, chartType: 'line' | 'bar' | 'pie' | 'radar') => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Box
          sx={{
            height: 300,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: 'grey.50',
            borderRadius: 1,
            border: '1px dashed',
            borderColor: 'grey.300'
          }}
        >
          <Box textAlign="center">
            {chartType === 'line' && <ShowChart sx={{ fontSize: 48, color: 'grey.400' }} />}
            {chartType === 'bar' && <BarChart sx={{ fontSize: 48, color: 'grey.400' }} />}
            {chartType === 'pie' && <PieChart sx={{ fontSize: 48, color: 'grey.400' }} />}
            {chartType === 'radar' && <BubbleChart sx={{ fontSize: 48, color: 'grey.400' }} />}
            <Typography variant="body2" color="text.secondary">
              {chartType.charAt(0).toUpperCase() + chartType.slice(1)} Chart
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Mock data visualization
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  const renderHeatmap = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Agent Activity Heatmap
        </Typography>
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(24, 1fr)',
            gap: 0.5,
            p: 2,
            backgroundColor: 'grey.50',
            borderRadius: 1
          }}
        >
          {Array.from({ length: 168 }, (_, i) => (
            <Box
              key={i}
              sx={{
                width: 12,
                height: 12,
                backgroundColor: `rgba(76, 175, 80, ${Math.random() * 0.8 + 0.2})`,
                borderRadius: 1
              }}
            />
          ))}
        </Box>
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          Activity over the last 7 days (24 hours × 7 days)
        </Typography>
      </CardContent>
    </Card>
  );

  const renderTopIssues = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Top Issues & Alerts
        </Typography>
        <List>
          {[
            { severity: 'high', message: 'High confidence entity extraction failed', count: 12 },
            { severity: 'medium', message: 'Policy compliance threshold exceeded', count: 8 },
            { severity: 'low', message: 'Processing time above average', count: 5 },
            { severity: 'info', message: 'New document type detected', count: 3 }
          ].map((issue, index) => (
            <ListItem key={index}>
              <ListItemIcon>
                <Box
                  sx={{
                    color: issue.severity === 'high' ? 'error.main' :
                           issue.severity === 'medium' ? 'warning.main' :
                           issue.severity === 'low' ? 'info.main' : 'success.main'
                  }}
                >
                  {issue.severity === 'high' ? <Error /> :
                   issue.severity === 'medium' ? <Warning /> :
                   issue.severity === 'low' ? <Info /> : <CheckCircle />}
                </Box>
              </ListItemIcon>
              <ListItemText
                primary={issue.message}
                secondary={`${issue.count} occurrences`}
              />
              <Chip
                label={issue.severity}
                size="small"
                color={issue.severity === 'high' ? 'error' :
                       issue.severity === 'medium' ? 'warning' :
                       issue.severity === 'low' ? 'info' : 'success'}
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      {/* Header */}
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
        <Typography variant="h5" component="h2" gutterBottom>
          AI Document Agent Analytics
        </Typography>
        <Box display="flex" alignItems="center" gap={2}>
          <FormControlLabel
            control={
              <Switch
                checked={showRealTime}
                onChange={(e) => setShowRealTime(e.target.checked)}
              />
            }
            label="Real-time"
          />
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              onChange={(e) => onTimeRangeChange(e.target.value)}
              label="Time Range"
            >
              <MenuItem value="1h">Last Hour</MenuItem>
              <MenuItem value="24h">Last 24 Hours</MenuItem>
              <MenuItem value="7d">Last 7 Days</MenuItem>
              <MenuItem value="30d">Last 30 Days</MenuItem>
              <MenuItem value="90d">Last 90 Days</MenuItem>
            </Select>
          </FormControl>
          <Tooltip title="Refresh">
            <IconButton onClick={onRefresh}>
              <Refresh />
            </IconButton>
          </Tooltip>
          <Tooltip title="Export">
            <IconButton onClick={onExport}>
              <Download />
            </IconButton>
          </Tooltip>
          <Tooltip title="Settings">
            <IconButton>
              <Settings />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* KPI Cards */}
      <Grid container spacing={3} mb={3}>
        {kpis.map(renderKPICard)}
      </Grid>

      {/* Tabs */}
      <Box mb={3}>
        <Tabs
          value={selectedTab}
          onChange={(_, newValue) => setSelectedTab(newValue)}
        >
          <Tab label="Overview" />
          <Tab label="Performance" />
          <Tab label="Compliance" />
          <Tab label="Alerts" />
        </Tabs>
      </Box>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        {selectedTab === 0 && (
          <motion.div
            key="overview"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <Grid container spacing={3}>
              <Grid item xs={12} md={8}>
                {renderChart('Document Processing Trend', processingTrendData, 'line')}
              </Grid>
              <Grid item xs={12} md={4}>
                {renderHeatmap()}
              </Grid>
              <Grid item xs={12} md={6}>
                {renderChart('Agent Performance', agentPerformanceData, 'bar')}
              </Grid>
              <Grid item xs={12} md={6}>
                {renderTopIssues()}
              </Grid>
            </Grid>
          </motion.div>
        )}

        {selectedTab === 1 && (
          <motion.div
            key="performance"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                {renderChart('Processing Time Distribution', processingTrendData, 'pie')}
              </Grid>
              <Grid item xs={12} md={6}>
                {renderChart('Agent Efficiency Radar', agentPerformanceData, 'radar')}
              </Grid>
              <Grid item xs={12}>
                {renderChart('System Performance Metrics', processingTrendData, 'line')}
              </Grid>
            </Grid>
          </motion.div>
        )}

        {selectedTab === 2 && (
          <motion.div
            key="compliance"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                {renderChart('Policy Compliance Rates', policyComplianceData, 'bar')}
              </Grid>
              <Grid item xs={12} md={6}>
                {renderChart('Compliance Trend', policyComplianceData, 'line')}
              </Grid>
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Compliance Summary
                    </Typography>
                    <Grid container spacing={2}>
                      {policyComplianceData.labels.map((policy, index) => (
                        <Grid item xs={12} sm={6} md={4} key={policy}>
                          <Paper sx={{ p: 2, textAlign: 'center' }}>
                            <Typography variant="h6" color="primary">
                              {policyComplianceData.datasets[0].data[index]}%
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {policy}
                            </Typography>
                            <LinearProgress
                              variant="determinate"
                              value={policyComplianceData.datasets[0].data[index]}
                              sx={{ mt: 1 }}
                            />
                          </Paper>
                        </Grid>
                      ))}
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </motion.div>
        )}

        {selectedTab === 3 && (
          <motion.div
            key="alerts"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <Grid container spacing={3}>
              <Grid item xs={12} md={8}>
                {renderTopIssues()}
              </Grid>
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Alert Statistics
                    </Typography>
                    <Box display="flex" flexDirection="column" gap={2}>
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography>High Priority</Typography>
                        <Chip label="12" color="error" size="small" />
                      </Box>
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography>Medium Priority</Typography>
                        <Chip label="8" color="warning" size="small" />
                      </Box>
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography>Low Priority</Typography>
                        <Chip label="5" color="info" size="small" />
                      </Box>
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography>Resolved</Typography>
                        <Chip label="45" color="success" size="small" />
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </motion.div>
        )}
      </AnimatePresence>
    </Box>
  );
};

export default AnalyticsDashboard;
