import React, { useState } from 'react';
import { Box, Typography, useTheme as useMuiTheme } from '@mui/material';
import { Analytics as AnalyticsIcon, AutoAwesome } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useTheme } from '../contexts/ThemeContext';
import AnalyticsDashboard from '../components/AnalyticsDashboard';

const AnalyticsPage: React.FC = () => {
  const { darkMode } = useTheme();
  const muiTheme = useMuiTheme();
  const [timeRange, setTimeRange] = useState<'1h' | '24h' | '7d' | '30d' | '90d'>('7d');

  const handleTimeRangeChange = (range: string) => {
    setTimeRange(range as '1h' | '24h' | '7d' | '30d' | '90d');
  };

  const handleRefresh = () => {
    // Refresh analytics data
    console.log('Refreshing analytics...');
  };

  const handleExport = () => {
    // Export analytics data
    console.log('Exporting analytics...');
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
            <AnalyticsIcon sx={{ 
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
              Analytics
            </Typography>
            <Typography variant="h6" sx={{ 
              opacity: 0.95,
              background: 'linear-gradient(135deg, #cbd5e1 0%, #94a3b8 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              Comprehensive analytics and insights for document processing performance
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Analytics Dashboard */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <AnalyticsDashboard
          timeRange={timeRange}
          onTimeRangeChange={handleTimeRangeChange}
          onRefresh={handleRefresh}
          onExport={handleExport}
        />
      </motion.div>
    </Box>
  );
};

export default AnalyticsPage;
