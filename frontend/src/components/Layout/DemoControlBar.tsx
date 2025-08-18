import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Chip,
  IconButton,
  Tooltip,
  Collapse,
  Grid,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  Stop as StopIcon,
  Speed as SpeedIcon,
  Settings as SettingsIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  AutoAwesome as AutoAwesomeIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

interface DemoControlBarProps {}

const DemoControlBar: React.FC<DemoControlBarProps> = () => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [demoSpeed, setDemoSpeed] = useState<'slow' | 'normal' | 'fast'>('normal');
  const [autoMode, setAutoMode] = useState(true);

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleStop = () => {
    setIsPlaying(false);
  };

  const handleSpeedChange = () => {
    const speeds: ('slow' | 'normal' | 'fast')[] = ['slow', 'normal', 'fast'];
    const currentIndex = speeds.indexOf(demoSpeed);
    const nextIndex = (currentIndex + 1) % speeds.length;
    setDemoSpeed(speeds[nextIndex]);
  };

  const getSpeedLabel = () => {
    switch (demoSpeed) {
      case 'slow': return '1x';
      case 'normal': return '2x';
      case 'fast': return '4x';
      default: return '2x';
    }
  };

  const getSpeedColor = () => {
    switch (demoSpeed) {
      case 'slow': return 'warning';
      case 'normal': return 'success';
      case 'fast': return 'error';
      default: return 'success';
    }
  };

  return (
    <Paper
      elevation={3}
      sx={{
        position: 'fixed',
        top: 64,
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 1000,
        borderRadius: 2,
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(0, 0, 0, 0.1)',
      }}
    >
      <Box sx={{ p: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Chip
            icon={<AutoAwesomeIcon />}
            label="DEMO MODE"
            color="primary"
            size="small"
            sx={{ fontWeight: 'bold' }}
          />
          
          <Typography variant="caption" sx={{ color: 'text.secondary' }}>
            Interactive Demo Controls
          </Typography>

          <Box sx={{ flexGrow: 1 }} />

          <Tooltip title="Play/Pause Demo">
            <IconButton
              size="small"
              onClick={handlePlayPause}
              color={isPlaying ? 'primary' : 'default'}
            >
              {isPlaying ? <PauseIcon /> : <PlayIcon />}
            </IconButton>
          </Tooltip>

          <Tooltip title="Stop Demo">
            <IconButton size="small" onClick={handleStop}>
              <StopIcon />
            </IconButton>
          </Tooltip>

          <Tooltip title={`Speed: ${getSpeedLabel()}`}>
            <IconButton
              size="small"
              onClick={handleSpeedChange}
              color={getSpeedColor() as any}
            >
              <SpeedIcon />
            </IconButton>
          </Tooltip>

          <Tooltip title="Demo Settings">
            <IconButton size="small">
              <SettingsIcon />
            </IconButton>
          </Tooltip>

          <Tooltip title={isExpanded ? 'Collapse' : 'Expand'}>
            <IconButton
              size="small"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? <CollapseIcon /> : <ExpandIcon />}
            </IconButton>
          </Tooltip>
        </Box>

        <Collapse in={isExpanded}>
          <Box sx={{ pt: 1, borderTop: '1px solid rgba(0, 0, 0, 0.1)' }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={autoMode}
                      onChange={(e) => setAutoMode(e.target.checked)}
                      size="small"
                    />
                  }
                  label="Auto Mode"
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="caption">Speed:</Typography>
                  <Chip
                    label={getSpeedLabel()}
                    size="small"
                    color={getSpeedColor() as any}
                    variant="outlined"
                  />
                </Box>
              </Grid>
            </Grid>

            <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Button
                size="small"
                variant="outlined"
                onClick={() => {/* Trigger demo scenario */}}
              >
                Load Sample Document
              </Button>
              <Button
                size="small"
                variant="outlined"
                onClick={() => {/* Trigger demo scenario */}}
              >
                Run Full Pipeline
              </Button>
              <Button
                size="small"
                variant="outlined"
                onClick={() => {/* Trigger demo scenario */}}
              >
                Show Agent Trace
              </Button>
            </Box>
          </Box>
        </Collapse>
      </Box>

      {/* Animated status indicator */}
      <AnimatePresence>
        {isPlaying && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            style={{
              position: 'absolute',
              top: -8,
              right: -8,
              width: 16,
              height: 16,
              borderRadius: '50%',
              backgroundColor: '#4caf50',
              boxShadow: '0 0 8px rgba(76, 175, 80, 0.6)',
            }}
          />
        )}
      </AnimatePresence>
    </Paper>
  );
};

export default DemoControlBar;
