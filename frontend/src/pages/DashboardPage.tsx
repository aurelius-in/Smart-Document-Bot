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
  Paper,
  useTheme as useMuiTheme
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
  AutoAwesome,
  Business,
  Assessment
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext';

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { darkMode } = useTheme();
  const muiTheme = useMuiTheme();

  const stats = [
    {
      title: 'Documents Processed',
      value: '1,247',
      change: '+12%',
      icon: <DocumentIcon />,
      color: 'primary',
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    },
    {
      title: 'Active Traces',
      value: '8',
      change: '+3',
      icon: <TraceIcon />,
      color: 'success',
      gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
    },
    {
      title: 'Compliance Score',
      value: '94.2%',
      change: '+2.1%',
      icon: <SecurityIcon />,
      color: 'warning',
      gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'
    },
    {
      title: 'Processing Time',
      value: '2.3s',
      change: '-0.8s',
      icon: <TrendingUpIcon />,
      color: 'info',
      gradient: 'linear-gradient(135deg, #8a2be2 0%, #4c1d95 100%)'
    },
  ];

  const quickActions = [
    {
      title: 'Upload Document',
      description: 'Process a new regulatory document',
      icon: <UploadIcon />,
      path: '/upload',
      color: 'primary',
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    },
    {
      title: 'View Traces',
      description: 'Monitor agent execution traces',
      icon: <TraceIcon />,
      path: '/traces',
      color: 'success',
      gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
    },
    {
      title: 'Analytics',
      description: 'View processing analytics',
      icon: <AnalyticsIcon />,
      path: '/analytics',
      color: 'info',
      gradient: 'linear-gradient(135deg, #8a2be2 0%, #4c1d95 100%)'
    },
  ];

  const recentActivity = [
    {
      id: 1,
      type: 'Document Processed',
      title: 'GDPR Compliance Report',
      time: '2 minutes ago',
      status: 'completed',
      icon: <DocumentIcon />
    },
    {
      id: 2,
      type: 'Agent Trace',
      title: 'Risk Assessment Pipeline',
      time: '5 minutes ago',
      status: 'running',
      icon: <TraceIcon />
    },
    {
      id: 3,
      type: 'Document Uploaded',
      title: 'Contract Amendment',
      time: '12 minutes ago',
      status: 'pending',
      icon: <UploadIcon />
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
      {/* Header Section */}
      <Box sx={{ 
        mb: 4,
        background: darkMode 
          ? 'linear-gradient(135deg, #0f0f23 0%, #1a1a3a 25%, #2d1b69 50%, #1a1a3a 75%, #0f0f23 100%)'
          : 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 25%, #cbd5e1 50%, #e2e8f0 75%, #f8fafc 100%)',
        color: darkMode ? 'white' : 'inherit',
        p: 4,
        borderRadius: 3,
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
              Welcome to aiDa
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
                    background: stat.gradient,
                    color: 'white',
                    borderRadius: 3,
                    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2), 0 2px 8px rgba(0, 0, 0, 0.1)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    position: 'relative',
                    overflow: 'hidden',
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: '2px',
                      background: 'linear-gradient(90deg, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0.1) 100%)'
                    },
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: '0 12px 40px rgba(0, 0, 0, 0.3), 0 4px 12px rgba(0, 0, 0, 0.15)',
                      transition: 'all 0.3s ease'
                    },
                    transition: 'all 0.3s ease'
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <Box>
                        <Typography variant="h4" component="div" sx={{ 
                          fontWeight: 700, 
                          mb: 1,
                          textShadow: '0 2px 8px rgba(0, 0, 0, 0.3)'
                        }}>
                          {stat.value}
                        </Typography>
                        <Typography variant="body2" sx={{ 
                          opacity: 0.9, 
                          mb: 1,
                          fontWeight: 500
                        }}>
                          {stat.title}
                        </Typography>
                        <Chip
                          label={stat.change}
                          size="small"
                          sx={{
                            backgroundColor: 'rgba(255, 255, 255, 0.2)',
                            color: 'white',
                            fontWeight: 600,
                            backdropFilter: 'blur(10px)',
                            border: '1px solid rgba(255, 255, 255, 0.1)'
                          }}
                        />
                      </Box>
                      <Box
                        sx={{
                          p: 1.5,
                          borderRadius: 2,
                          backgroundColor: 'rgba(255, 255, 255, 0.2)',
                          backdropFilter: 'blur(10px)',
                          border: '1px solid rgba(255, 255, 255, 0.1)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}
                      >
                        {React.cloneElement(stat.icon, { 
                          sx: { 
                            fontSize: '2rem',
                            filter: 'drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3))'
                          } 
                        })}
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
            <Paper sx={{ 
              p: 3,
              borderRadius: 3,
              background: darkMode 
                ? 'linear-gradient(135deg, #1a1a3a 0%, #2d1b69 50%, #1a1a3a 100%)'
                : 'linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #e2e8f0 100%)',
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
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" component="h2" sx={{ 
                  fontWeight: 600,
                  color: darkMode ? 'white' : 'inherit'
                }}>
                  Quick Actions
                </Typography>
                <Tooltip title="Refresh">
                  <IconButton size="small" sx={{ color: darkMode ? 'white' : 'inherit' }}>
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
                      py: 2.5,
                      px: 3,
                      textTransform: 'none',
                      borderRadius: 2,
                      border: darkMode 
                        ? '1px solid rgba(138, 43, 226, 0.3)'
                        : '1px solid rgba(138, 43, 226, 0.2)',
                      color: darkMode ? 'white' : 'inherit',
                      background: darkMode 
                        ? 'rgba(138, 43, 226, 0.1)'
                        : 'rgba(138, 43, 226, 0.05)',
                      backdropFilter: 'blur(10px)',
                      '&:hover': {
                        background: darkMode 
                          ? 'rgba(138, 43, 226, 0.2)'
                          : 'rgba(138, 43, 226, 0.1)',
                        borderColor: '#8a2be2',
                        transform: 'translateY(-1px)',
                        boxShadow: '0 4px 12px rgba(138, 43, 226, 0.3)'
                      },
                      transition: 'all 0.2s ease'
                    }}
                  >
                    <Box sx={{ textAlign: 'left' }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        {action.title}
                      </Typography>
                      <Typography variant="body2" sx={{ 
                        opacity: 0.8,
                        color: darkMode ? 'rgba(255, 255, 255, 0.8)' : 'rgba(0, 0, 0, 0.6)'
                      }}>
                        {action.description}
                      </Typography>
                    </Box>
                  </Button>
                ))}
              </Box>
            </Paper>
          </motion.div>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <motion.div variants={itemVariants}>
            <Paper sx={{ 
              p: 3,
              borderRadius: 3,
              background: darkMode 
                ? 'linear-gradient(135deg, #1a1a3a 0%, #2d1b69 50%, #1a1a3a 100%)'
                : 'linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #e2e8f0 100%)',
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
              <Typography variant="h6" component="h2" sx={{ 
                fontWeight: 600, 
                mb: 3,
                color: darkMode ? 'white' : 'inherit'
              }}>
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
                      p: 2.5,
                      borderRadius: 2,
                      background: darkMode 
                        ? 'rgba(255, 255, 255, 0.05)'
                        : 'rgba(138, 43, 226, 0.05)',
                      border: darkMode 
                        ? '1px solid rgba(255, 255, 255, 0.1)'
                        : '1px solid rgba(138, 43, 226, 0.1)',
                      backdropFilter: 'blur(10px)',
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        background: darkMode 
                          ? 'rgba(255, 255, 255, 0.1)'
                          : 'rgba(138, 43, 226, 0.1)',
                        transform: 'translateX(4px)'
                      }
                    }}
                  >
                    <Box
                      sx={{
                        p: 1.5,
                        borderRadius: 2,
                        background: 'linear-gradient(135deg, #8a2be2 0%, #4c1d95 100%)',
                        color: 'white',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        boxShadow: '0 4px 12px rgba(138, 43, 226, 0.3)'
                      }}
                    >
                      {React.cloneElement(activity.icon, { 
                        sx: { 
                          fontSize: '1.5rem',
                          filter: 'drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3))'
                        } 
                      })}
                    </Box>
                    
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="subtitle2" sx={{ 
                        fontWeight: 600,
                        color: darkMode ? 'white' : 'inherit'
                      }}>
                        {activity.title}
                      </Typography>
                      <Typography variant="body2" sx={{ 
                        opacity: 0.8,
                        color: darkMode ? 'rgba(255, 255, 255, 0.8)' : 'rgba(0, 0, 0, 0.6)'
                      }}>
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
                      sx={{
                        background: activity.status === 'completed' 
                          ? 'rgba(16, 185, 129, 0.1)'
                          : activity.status === 'running'
                          ? 'rgba(245, 158, 11, 0.1)'
                          : 'rgba(107, 114, 128, 0.1)',
                        borderColor: activity.status === 'completed' 
                          ? 'rgba(16, 185, 129, 0.3)'
                          : activity.status === 'running'
                          ? 'rgba(245, 158, 11, 0.3)'
                          : 'rgba(107, 114, 128, 0.3)',
                        color: activity.status === 'completed' 
                          ? '#10b981'
                          : activity.status === 'running'
                          ? '#f59e0b'
                          : '#6b7280'
                      }}
                    />
                  </Box>
                ))}
              </Box>
            </Paper>
          </motion.div>
        </Grid>
      </Grid>

      {/* System Status */}
      <motion.div variants={itemVariants}>
        <Paper sx={{ 
          mt: 3,
          p: 3,
          borderRadius: 3,
          background: darkMode 
            ? 'linear-gradient(135deg, #1a1a3a 0%, #2d1b69 50%, #1a1a3a 100%)'
            : 'linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #e2e8f0 100%)',
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
          <Typography variant="h6" component="h2" sx={{ 
            fontWeight: 600, 
            mb: 3,
            color: darkMode ? 'white' : 'inherit'
          }}>
            System Status
          </Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2" sx={{ color: darkMode ? 'rgba(255, 255, 255, 0.8)' : 'rgba(0, 0, 0, 0.7)' }}>
                    Agent System
                  </Typography>
                  <Typography variant="body2" sx={{ 
                    fontWeight: 600,
                    color: '#10b981'
                  }}>
                    Operational
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={95} 
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      background: 'linear-gradient(90deg, #10b981 0%, #059669 100%)',
                      borderRadius: 4
                    }
                  }}
                />
              </Box>
              
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2" sx={{ color: darkMode ? 'rgba(255, 255, 255, 0.8)' : 'rgba(0, 0, 0, 0.7)' }}>
                    Memory Service
                  </Typography>
                  <Typography variant="body2" sx={{ 
                    fontWeight: 600,
                    color: '#10b981'
                  }}>
                    Operational
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={88} 
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      background: 'linear-gradient(90deg, #10b981 0%, #059669 100%)',
                      borderRadius: 4
                    }
                  }}
                />
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2" sx={{ color: darkMode ? 'rgba(255, 255, 255, 0.8)' : 'rgba(0, 0, 0, 0.7)' }}>
                    API Endpoints
                  </Typography>
                  <Typography variant="body2" sx={{ 
                    fontWeight: 600,
                    color: '#10b981'
                  }}>
                    Operational
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={100} 
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      background: 'linear-gradient(90deg, #10b981 0%, #059669 100%)',
                      borderRadius: 4
                    }
                  }}
                />
              </Box>
              
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2" sx={{ color: darkMode ? 'rgba(255, 255, 255, 0.8)' : 'rgba(0, 0, 0, 0.7)' }}>
                    Database
                  </Typography>
                  <Typography variant="body2" sx={{ 
                    fontWeight: 600,
                    color: '#10b981'
                  }}>
                    Operational
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={92} 
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: darkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      background: 'linear-gradient(90deg, #10b981 0%, #059669 100%)',
                      borderRadius: 4
                    }
                  }}
                />
              </Box>
            </Grid>
          </Grid>
        </Paper>
      </motion.div>
    </Box>
  );
};

export default DashboardPage;
