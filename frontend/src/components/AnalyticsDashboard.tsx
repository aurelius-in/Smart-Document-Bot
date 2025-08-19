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
            backgroundColor: 'background.paper',
            borderRadius: 1,
            border: '1px solid',
            borderColor: 'divider',
            p: 2
          }}
        >
                     {chartType === 'line' && (
             <Box sx={{ width: '100%', height: '100%' }}>
               <svg width="100%" height="100%" viewBox="0 0 400 250">
                 <defs>
                   <linearGradient id="lineGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                     <stop offset="0%" stopColor="#4CAF50" stopOpacity="0.3" />
                     <stop offset="100%" stopColor="#4CAF50" stopOpacity="0.1" />
                   </linearGradient>
                 </defs>
                 {/* Y-axis labels */}
                 {[0, 1, 2, 3, 4].map(i => (
                   <text
                     key={i}
                     x="10"
                     y={40 + i * 40 + 5}
                     fontSize="12"
                     fill="#666"
                     textAnchor="end"
                   >
                     {Math.round((4 - i) * 50)}
                   </text>
                 ))}
                 {/* X-axis labels */}
                 {data.labels.map((label, index) => {
                   const x = (index / (data.labels.length - 1)) * 360 + 20;
                   return (
                     <text
                       key={index}
                       x={x}
                       y="240"
                       fontSize="12"
                       fill="#666"
                       textAnchor="middle"
                     >
                       {label}
                     </text>
                   );
                 })}
                 {/* Grid lines */}
                 {[0, 1, 2, 3, 4].map(i => (
                   <line
                     key={i}
                     x1="40"
                     y1={40 + i * 40}
                     x2="380"
                     y2={40 + i * 40}
                     stroke="#e0e0e0"
                     strokeWidth="1"
                     opacity="0.3"
                   />
                 ))}
                 {/* Data line */}
                 <path
                   d={data.datasets[0].data.map((value, index) => {
                     const x = (index / (data.datasets[0].data.length - 1)) * 320 + 40;
                     const y = 200 - (value / 200) * 160 - 20;
                     return `${index === 0 ? 'M' : 'L'} ${x} ${y}`;
                   }).join(' ')}
                   stroke="#4CAF50"
                   strokeWidth="3"
                   fill="none"
                 />
                 {/* Area under line */}
                 <path
                   d={`M 40 200 ${data.datasets[0].data.map((value, index) => {
                     const x = (index / (data.datasets[0].data.length - 1)) * 320 + 40;
                     const y = 200 - (value / 200) * 160 - 20;
                     return `L ${x} ${y}`;
                   }).join(' ')} L 360 200 Z`}
                   fill="url(#lineGradient)"
                 />
                 {/* Data points with values */}
                 {data.datasets[0].data.map((value, index) => {
                   const x = (index / (data.datasets[0].data.length - 1)) * 320 + 40;
                   const y = 200 - (value / 200) * 160 - 20;
                   return (
                     <g key={index}>
                       <circle
                         cx={x}
                         cy={y}
                         r="4"
                         fill="#4CAF50"
                         stroke="#fff"
                         strokeWidth="2"
                       />
                       <text
                         x={x}
                         y={y - 10}
                         fontSize="10"
                         fill="#4CAF50"
                         textAnchor="middle"
                         fontWeight="bold"
                       >
                         {value}
                       </text>
                     </g>
                   );
                 })}
                 {/* Chart title */}
                 <text
                   x="200"
                   y="15"
                   fontSize="14"
                   fill="#333"
                   textAnchor="middle"
                   fontWeight="bold"
                 >
                   {data.datasets[0].label}
                 </text>
               </svg>
             </Box>
           )}
                     {chartType === 'bar' && (
             <Box sx={{ width: '100%', height: '100%' }}>
               <svg width="100%" height="100%" viewBox="0 0 400 280">
                 {/* Y-axis labels */}
                 {[0, 1, 2, 3, 4].map(i => (
                   <text
                     key={i}
                     x="10"
                     y={40 + i * 40 + 5}
                     fontSize="12"
                     fill="#666"
                     textAnchor="end"
                   >
                     {Math.round((4 - i) * 25)}%
                   </text>
                 ))}
                 {/* X-axis labels */}
                 {data.labels.map((label, index) => {
                   const barWidth = 30;
                   const barSpacing = 10;
                   const x = index * (barWidth + barSpacing) + 20 + barWidth / 2;
                   return (
                     <text
                       key={index}
                       x={x}
                       y="270"
                       fontSize="10"
                       fill="#666"
                       textAnchor="middle"
                       transform={`rotate(-45 ${x} 270)`}
                     >
                       {label}
                     </text>
                   );
                 })}
                 {/* Grid lines */}
                 {[0, 1, 2, 3, 4].map(i => (
                   <line
                     key={i}
                     x1="40"
                     y1={40 + i * 40}
                     x2="380"
                     y2={40 + i * 40}
                     stroke="#e0e0e0"
                     strokeWidth="1"
                     opacity="0.3"
                   />
                 ))}
                 {/* Bars with values */}
                 {data.datasets[0].data.map((value, index) => {
                   const barWidth = 30;
                   const barSpacing = 10;
                   const x = index * (barWidth + barSpacing) + 40;
                   const height = (value / 100) * 160;
                   const y = 200 - height - 20;
                   return (
                     <g key={index}>
                       <rect
                         x={x}
                         y={y}
                         width={barWidth}
                         height={height}
                         fill="#2196F3"
                         rx="2"
                       />
                       <text
                         x={x + barWidth / 2}
                         y={y - 5}
                         fontSize="10"
                         fill="#2196F3"
                         textAnchor="middle"
                         fontWeight="bold"
                       >
                         {value}%
                       </text>
                     </g>
                   );
                 })}
                 {/* Chart title */}
                 <text
                   x="200"
                   y="15"
                   fontSize="14"
                   fill="#333"
                   textAnchor="middle"
                   fontWeight="bold"
                 >
                   {data.datasets[0].label}
                 </text>
               </svg>
             </Box>
           )}
                     {chartType === 'pie' && (
             <Box sx={{ width: '100%', height: '100%' }}>
               <svg width="100%" height="100%" viewBox="0 0 300 250">
                 {/* Chart title */}
                 <text
                   x="150"
                   y="20"
                   fontSize="14"
                   fill="#333"
                   textAnchor="middle"
                   fontWeight="bold"
                 >
                   {data.datasets[0].label}
                 </text>
                 
                 {/* Pie chart */}
                 <g transform="translate(150, 120)">
                   {data.datasets[0].data.map((value, index) => {
                     const total = data.datasets[0].data.reduce((sum, val) => sum + val, 0);
                     const percentage = value / total;
                     const angle = percentage * 2 * Math.PI;
                     const startAngle = data.datasets[0].data.slice(0, index).reduce((sum, val) => sum + val, 0) / total * 2 * Math.PI;
                     const colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336', '#00BCD4'];
                     
                     const x1 = 60 * Math.cos(startAngle);
                     const y1 = 60 * Math.sin(startAngle);
                     const x2 = 60 * Math.cos(startAngle + angle);
                     const y2 = 60 * Math.sin(startAngle + angle);
                     
                     const largeArcFlag = angle > Math.PI ? 1 : 0;
                     
                     // Calculate center point for label
                     const midAngle = startAngle + angle / 2;
                     const labelRadius = 45;
                     const labelX = labelRadius * Math.cos(midAngle);
                     const labelY = labelRadius * Math.sin(midAngle);
                     
                     return (
                       <g key={index}>
                         <path
                           d={`M 0 0 L ${x1} ${y1} A 60 60 0 ${largeArcFlag} 1 ${x2} ${y2} Z`}
                           fill={colors[index % colors.length]}
                         />
                         <text
                           x={labelX}
                           y={labelY}
                           fontSize="10"
                           fill="white"
                           textAnchor="middle"
                           fontWeight="bold"
                         >
                           {Math.round(percentage * 100)}%
                         </text>
                       </g>
                     );
                   })}
                 </g>
                 
                 {/* Legend */}
                 <g transform="translate(20, 200)">
                   {data.labels.map((label, index) => {
                     const colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336', '#00BCD4'];
                     const percentage = Math.round((data.datasets[0].data[index] / data.datasets[0].data.reduce((sum, val) => sum + val, 0)) * 100);
                     
                     return (
                       <g key={index} transform={`translate(0, ${index * 20})`}>
                         <rect
                           x="0"
                           y="0"
                           width="12"
                           height="12"
                           fill={colors[index % colors.length]}
                           rx="2"
                         />
                         <text
                           x="20"
                           y="10"
                           fontSize="11"
                           fill="#666"
                         >
                           {label} ({percentage}%)
                         </text>
                       </g>
                     );
                   })}
                 </g>
               </svg>
             </Box>
           )}
                     {chartType === 'radar' && (
             <Box sx={{ width: '100%', height: '100%' }}>
               <svg width="100%" height="100%" viewBox="0 0 250 250">
                 {/* Chart title */}
                 <text
                   x="125"
                   y="20"
                   fontSize="14"
                   fill="#333"
                   textAnchor="middle"
                   fontWeight="bold"
                 >
                   {data.datasets[0].label}
                 </text>
                 
                 {/* Radar grid */}
                 <g transform="translate(125, 125)">
                   {[1, 2, 3, 4, 5].map(level => (
                     <circle
                       key={level}
                       cx="0"
                       cy="0"
                       r={level * 15}
                       fill="none"
                       stroke="#e0e0e0"
                       strokeWidth="1"
                       opacity="0.3"
                     />
                   ))}
                   
                   {/* Axis lines */}
                   {data.labels.map((label, index) => {
                     const angle = (index / data.labels.length) * 2 * Math.PI - Math.PI / 2;
                     const x = 75 * Math.cos(angle);
                     const y = 75 * Math.sin(angle);
                     
                     return (
                       <g key={index}>
                         <line
                           x1="0"
                           y1="0"
                           x2={x}
                           y2={y}
                           stroke="#e0e0e0"
                           strokeWidth="1"
                           opacity="0.5"
                         />
                         <text
                           x={x * 1.1}
                           y={y * 1.1}
                           fontSize="10"
                           fill="#666"
                           textAnchor="middle"
                         >
                           {label}
                         </text>
                       </g>
                     );
                   })}
                   
                   {/* Radar data */}
                   <polygon
                     points={data.datasets[0].data.map((value, index) => {
                       const angle = (index / data.datasets[0].data.length) * 2 * Math.PI - Math.PI / 2;
                       const radius = (value / 100) * 75;
                       const x = radius * Math.cos(angle);
                       const y = radius * Math.sin(angle);
                       return `${x},${y}`;
                     }).join(' ')}
                     fill="rgba(76, 175, 80, 0.2)"
                     stroke="#4CAF50"
                     strokeWidth="2"
                   />
                   
                   {/* Data points with values */}
                   {data.datasets[0].data.map((value, index) => {
                     const angle = (index / data.datasets[0].data.length) * 2 * Math.PI - Math.PI / 2;
                     const radius = (value / 100) * 75;
                     const x = radius * Math.cos(angle);
                     const y = radius * Math.sin(angle);
                     
                     return (
                       <g key={index}>
                         <circle
                           cx={x}
                           cy={y}
                           r="3"
                           fill="#4CAF50"
                           stroke="white"
                           strokeWidth="2"
                         />
                         <text
                           x={x}
                           y={y - 8}
                           fontSize="9"
                           fill="#4CAF50"
                           textAnchor="middle"
                           fontWeight="bold"
                         >
                           {value}%
                         </text>
                       </g>
                     );
                   })}
                 </g>
                 
                 {/* Scale labels */}
                 <g transform="translate(20, 50)">
                   {[0, 25, 50, 75, 100].map((value, index) => (
                     <text
                       key={index}
                       x="0"
                       y={index * 15}
                       fontSize="10"
                       fill="#666"
                     >
                       {value}%
                     </text>
                   ))}
                 </g>
               </svg>
             </Box>
           )}
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
            backgroundColor: 'background.paper',
            borderRadius: 1,
            border: '1px solid',
            borderColor: 'divider'
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
