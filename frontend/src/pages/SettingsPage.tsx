import React from 'react';
import { Box, Typography, Paper, useTheme as useMuiTheme } from '@mui/material';
import { Settings as SettingsIcon, AutoAwesome } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useTheme } from '../contexts/ThemeContext';

const SettingsPage: React.FC = () => {
  const { darkMode } = useTheme();
  const muiTheme = useMuiTheme();

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
            <SettingsIcon sx={{ 
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
              Settings
            </Typography>
            <Typography variant="h6" sx={{ 
              opacity: 0.95,
              background: 'linear-gradient(135deg, #cbd5e1 0%, #94a3b8 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              Configure system preferences and application settings
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Content */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Paper sx={{ 
          p: 4, 
          textAlign: 'center',
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
          <Typography variant="h6" sx={{ 
            color: darkMode ? 'rgba(255, 255, 255, 0.8)' : 'rgba(0, 0, 0, 0.6)',
            mb: 2
          }}>
            Settings functionality coming soon...
          </Typography>
          <Typography variant="body2" sx={{ 
            color: darkMode ? 'rgba(255, 255, 255, 0.6)' : 'rgba(0, 0, 0, 0.5)'
          }}>
            Configure system preferences, user settings, and application options
          </Typography>
        </Paper>
      </motion.div>
    </Box>
  );
};

export default SettingsPage;
