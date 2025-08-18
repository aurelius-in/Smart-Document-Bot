import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  LinearProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Upload as UploadIcon,
  Description as DocumentIcon,
  Timeline as TraceIcon,
  Analytics as AnalyticsIcon,
  PlayArrow as PlayIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  Security as SecurityIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();

  const stats = [
    {
      title: 'Documents Processed',
      value: '1,247',
      change: '+12%',
      icon: <DocumentIcon />,
      color: 'primary',
    },
    {
      title: 'Active Traces',
      value: '8',
      change: '+3',
      icon: <TraceIcon />,
      color: 'success',
    },
    {
      title: 'Compliance Score',
      value: '94.2%',
      change: '+2.1%',
      icon: <SecurityIcon />,
      color: 'warning',
    },
    {
      title: 'Processing Time',
      value: '2.3s',
      change: '-0.8s',
      icon: <TrendingUpIcon />,
      color: 'info',
    },
  ];

  const quickActions = [
    {
      title: 'Upload Document',
      description: 'Process a new regulatory document',
      icon: <UploadIcon />,
      path: '/upload',
      color: 'primary',
    },
    {
      title: 'View Traces',
      description: 'Monitor agent execution traces',
      icon: <TraceIcon />,
      path: '/trace',
      color: 'success',
    },
    {
      title: 'Analytics',
      description: 'View processing analytics',
      icon: <AnalyticsIcon />,
      path: '/analytics',
      color: 'info',
    },
  ];

  const recentActivity = [
    {
      id: 1,
      type: 'Document Processed',
      title: 'GDPR Compliance Report',
      time: '2 minutes ago',
      status: 'completed',
    },
    {
      id: 2,
      type: 'Agent Trace',
      title: 'Risk Assessment Pipeline',
      time: '5 minutes ago',
      status: 'running',
    },
    {
      id: 3,
      type: 'Document Uploaded',
      title: 'Contract Amendment',
      time: '12 minutes ago',
      status: 'pending',
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5,
      },
    },
  };

  return (
    <Box>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
          Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Welcome to REDLINE - Your regulatory document intelligence platform
        </Typography>
      </Box>

      {/* Stats Cards */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {stats.map((stat, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <motion.div variants={itemVariants}>
                <Card
                  sx={{
                    height: '100%',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white',
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <Box>
                        <Typography variant="h4" component="div" sx={{ fontWeight: 700, mb: 1 }}>
                          {stat.value}
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.9, mb: 1 }}>
                          {stat.title}
                        </Typography>
                        <Chip
                          label={stat.change}
                          size="small"
                          sx={{
                            backgroundColor: 'rgba(255, 255, 255, 0.2)',
                            color: 'white',
                            fontWeight: 600,
                          }}
                        />
                      </Box>
                      <Box
                        sx={{
                          p: 1,
                          borderRadius: 2,
                          backgroundColor: 'rgba(255, 255, 255, 0.2)',
                        }}
                      >
                        {stat.icon}
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      </motion.div>

      {/* Quick Actions and Recent Activity */}
      <Grid container spacing={3}>
        {/* Quick Actions */}
        <Grid item xs={12} md={6}>
          <motion.div variants={itemVariants}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" component="h2" sx={{ fontWeight: 600 }}>
                    Quick Actions
                  </Typography>
                  <Tooltip title="Refresh">
                    <IconButton size="small">
                      <RefreshIcon />
                    </IconButton>
                  </Tooltip>
                </Box>
                
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {quickActions.map((action, index) => (
                    <Button
                      key={index}
                      variant="outlined"
                      startIcon={action.icon}
                      onClick={() => navigate(action.path)}
                      sx={{
                        justifyContent: 'flex-start',
                        py: 2,
                        px: 2,
                        textTransform: 'none',
                        borderColor: `${action.color}.main`,
                        color: `${action.color}.main`,
                        '&:hover': {
                          backgroundColor: `${action.color}.main`,
                          color: 'white',
                        },
                      }}
                    >
                      <Box sx={{ textAlign: 'left' }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                          {action.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {action.description}
                        </Typography>
                      </Box>
                    </Button>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <motion.div variants={itemVariants}>
            <Card>
              <CardContent>
                <Typography variant="h6" component="h2" sx={{ fontWeight: 600, mb: 2 }}>
                  Recent Activity
                </Typography>
                
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {recentActivity.map((activity) => (
                    <Box
                      key={activity.id}
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 2,
                        p: 2,
                        borderRadius: 1,
                        backgroundColor: 'grey.50',
                      }}
                    >
                      <Box
                        sx={{
                          p: 1,
                          borderRadius: 1,
                          backgroundColor: 'primary.main',
                          color: 'white',
                        }}
                      >
                        <PlayIcon fontSize="small" />
                      </Box>
                      
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                          {activity.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {activity.type} • {activity.time}
                        </Typography>
                      </Box>
                      
                      <Chip
                        label={activity.status}
                        size="small"
                        color={
                          activity.status === 'completed' ? 'success' :
                          activity.status === 'running' ? 'warning' : 'default'
                        }
                        variant="outlined"
                      />
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      {/* System Status */}
      <motion.div variants={itemVariants}>
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" component="h2" sx={{ fontWeight: 600, mb: 2 }}>
              System Status
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Agent System</Typography>
                    <Typography variant="body2" color="success.main" sx={{ fontWeight: 600 }}>
                      Operational
                    </Typography>
                  </Box>
                  <LinearProgress variant="determinate" value={95} color="success" />
                </Box>
                
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Memory Service</Typography>
                    <Typography variant="body2" color="success.main" sx={{ fontWeight: 600 }}>
                      Operational
                    </Typography>
                  </Box>
                  <LinearProgress variant="determinate" value={88} color="success" />
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">API Endpoints</Typography>
                    <Typography variant="body2" color="success.main" sx={{ fontWeight: 600 }}>
                      Operational
                    </Typography>
                  </Box>
                  <LinearProgress variant="determinate" value={100} color="success" />
                </Box>
                
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Database</Typography>
                    <Typography variant="body2" color="success.main" sx={{ fontWeight: 600 }}>
                      Operational
                    </Typography>
                  </Box>
                  <LinearProgress variant="determinate" value={92} color="success" />
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </motion.div>
    </Box>
  );
};

export default DashboardPage;
