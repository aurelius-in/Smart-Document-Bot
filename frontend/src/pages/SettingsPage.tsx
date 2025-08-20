import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid, 
  Card, 
  CardContent, 
  CardHeader,
  Switch,
  FormControlLabel,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Divider,
  Alert,
  Slider,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import { 
  Settings as SettingsIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Security as SecurityIcon,
  Notifications as NotificationsIcon,
  Storage as StorageIcon,
  Speed as SpeedIcon,
  Palette as PaletteIcon,
  Language as LanguageIcon,
  Edit as EditIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useTheme } from '../contexts/ThemeContext';
import { toast } from 'react-hot-toast';

interface Settings {
  general: {
    language: string;
    timezone: string;
    dateFormat: string;
    autoSave: boolean;
    notifications: boolean;
  };
  appearance: {
    theme: 'light' | 'dark' | 'auto';
    fontSize: number;
    compactMode: boolean;
    animations: boolean;
  };
  processing: {
    maxFileSize: number;
    concurrentUploads: number;
    autoProcess: boolean;
    quality: 'low' | 'medium' | 'high';
  };
  security: {
    sessionTimeout: number;
    requireAuth: boolean;
    auditLogging: boolean;
    dataRetention: number;
  };
  notifications: {
    email: boolean;
    browser: boolean;
    processingComplete: boolean;
    errorAlerts: boolean;
  };
}

const SettingsPage: React.FC = () => {
  const { darkMode, toggleDarkMode } = useTheme();
  const [settings, setSettings] = useState<Settings>({
    general: {
      language: 'en',
      timezone: 'UTC',
      dateFormat: 'MM/DD/YYYY',
      autoSave: true,
      notifications: true
    },
    appearance: {
      theme: 'auto',
      fontSize: 14,
      compactMode: false,
      animations: true
    },
    processing: {
      maxFileSize: 10,
      concurrentUploads: 3,
      autoProcess: true,
      quality: 'medium'
    },
    security: {
      sessionTimeout: 30,
      requireAuth: true,
      auditLogging: true,
      dataRetention: 90
    },
    notifications: {
      email: false,
      browser: true,
      processingComplete: true,
      errorAlerts: true
    }
  });
  const [hasChanges, setHasChanges] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setIsLoading(true);
      // In a real app, you would load settings from the backend
      // const response = await apiService.getSettings();
      // setSettings(response.data);
      toast.success('Settings loaded successfully');
    } catch (error) {
      console.error('Failed to load settings:', error);
      toast.error('Failed to load settings');
    } finally {
      setIsLoading(false);
    }
  };

  const saveSettings = async () => {
    try {
      setIsLoading(true);
      // In a real app, you would save settings to the backend
      // await apiService.updateSettings(settings);
      setHasChanges(false);
      toast.success('Settings saved successfully');
    } catch (error) {
      console.error('Failed to save settings:', error);
      toast.error('Failed to save settings');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSettingChange = (section: keyof Settings, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value
      }
    }));
    setHasChanges(true);
  };

  const resetToDefaults = () => {
    if (window.confirm('Are you sure you want to reset all settings to defaults?')) {
      loadSettings();
      setHasChanges(false);
      toast.success('Settings reset to defaults');
    }
  };

  const formatFileSize = (mb: number) => `${mb} MB`;

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
              Configure application preferences and system settings
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Settings Content */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Grid container spacing={3}>
          {/* General Settings */}
          <Grid item xs={12} md={6}>
            <Card sx={{ 
              borderRadius: 3,
              background: darkMode 
                ? 'linear-gradient(135deg, #1a1a3a 0%, #2d1b69 50%, #1a1a3a 100%)'
                : 'linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #e2e8f0 100%)',
              boxShadow: darkMode 
                ? '0 8px 32px rgba(0, 0, 0, 0.3), 0 2px 8px rgba(0, 0, 0, 0.2)'
                : '0 8px 32px rgba(0, 0, 0, 0.1), 0 2px 8px rgba(0, 0, 0, 0.05)',
              border: darkMode 
                ? '1px solid rgba(138, 43, 226, 0.3)'
                : '1px solid rgba(138, 43, 226, 0.1)'
            }}>
              <CardHeader
                title="General Settings"
                titleTypographyProps={{ 
                  color: darkMode ? 'white' : 'inherit',
                  fontWeight: 600
                }}
                avatar={<LanguageIcon sx={{ color: 'primary.main' }} />}
              />
              <CardContent>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <FormControl fullWidth>
                      <InputLabel>Language</InputLabel>
                      <Select
                        value={settings.general.language}
                        onChange={(e) => handleSettingChange('general', 'language', e.target.value)}
                        sx={{
                          background: darkMode ? 'rgba(255, 255, 255, 0.05)' : 'white'
                        }}
                      >
                        <MenuItem value="en">English</MenuItem>
                        <MenuItem value="es">Spanish</MenuItem>
                        <MenuItem value="fr">French</MenuItem>
                        <MenuItem value="de">German</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12}>
                    <FormControl fullWidth>
                      <InputLabel>Timezone</InputLabel>
                      <Select
                        value={settings.general.timezone}
                        onChange={(e) => handleSettingChange('general', 'timezone', e.target.value)}
                        sx={{
                          background: darkMode ? 'rgba(255, 255, 255, 0.05)' : 'white'
                        }}
                      >
                        <MenuItem value="UTC">UTC</MenuItem>
                        <MenuItem value="EST">Eastern Time</MenuItem>
                        <MenuItem value="PST">Pacific Time</MenuItem>
                        <MenuItem value="GMT">GMT</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.general.autoSave}
                          onChange={(e) => handleSettingChange('general', 'autoSave', e.target.checked)}
                        />
                      }
                      label="Auto-save changes"
                      sx={{ color: darkMode ? 'white' : 'inherit' }}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Appearance Settings */}
          <Grid item xs={12} md={6}>
            <Card sx={{ 
              borderRadius: 3,
              background: darkMode 
                ? 'linear-gradient(135deg, #1a1a3a 0%, #2d1b69 50%, #1a1a3a 100%)'
                : 'linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #e2e8f0 100%)',
              boxShadow: darkMode 
                ? '0 8px 32px rgba(0, 0, 0, 0.3), 0 2px 8px rgba(0, 0, 0, 0.2)'
                : '0 8px 32px rgba(0, 0, 0, 0.1), 0 2px 8px rgba(0, 0, 0, 0.05)',
              border: darkMode 
                ? '1px solid rgba(138, 43, 226, 0.3)'
                : '1px solid rgba(138, 43, 226, 0.1)'
            }}>
              <CardHeader
                title="Appearance"
                titleTypographyProps={{ 
                  color: darkMode ? 'white' : 'inherit',
                  fontWeight: 600
                }}
                avatar={<PaletteIcon sx={{ color: 'primary.main' }} />}
              />
              <CardContent>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={darkMode}
                          onChange={toggleDarkMode}
                        />
                      }
                      label="Dark Mode"
                      sx={{ color: darkMode ? 'white' : 'inherit' }}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Typography gutterBottom sx={{ color: darkMode ? 'white' : 'inherit' }}>
                      Font Size: {settings.appearance.fontSize}px
                    </Typography>
                    <Slider
                      value={settings.appearance.fontSize}
                      onChange={(_, value) => handleSettingChange('appearance', 'fontSize', value)}
                      min={12}
                      max={20}
                      step={1}
                      marks
                      valueLabelDisplay="auto"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.appearance.animations}
                          onChange={(e) => handleSettingChange('appearance', 'animations', e.target.checked)}
                        />
                      }
                      label="Enable animations"
                      sx={{ color: darkMode ? 'white' : 'inherit' }}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Processing Settings */}
          <Grid item xs={12} md={6}>
            <Card sx={{ 
              borderRadius: 3,
              background: darkMode 
                ? 'linear-gradient(135deg, #1a1a3a 0%, #2d1b69 50%, #1a1a3a 100%)'
                : 'linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #e2e8f0 100%)',
              boxShadow: darkMode 
                ? '0 8px 32px rgba(0, 0, 0, 0.3), 0 2px 8px rgba(0, 0, 0, 0.2)'
                : '0 8px 32px rgba(0, 0, 0, 0.1), 0 2px 8px rgba(0, 0, 0, 0.05)',
              border: darkMode 
                ? '1px solid rgba(138, 43, 226, 0.3)'
                : '1px solid rgba(138, 43, 226, 0.1)'
            }}>
              <CardHeader
                title="Processing"
                titleTypographyProps={{ 
                  color: darkMode ? 'white' : 'inherit',
                  fontWeight: 600
                }}
                avatar={<SpeedIcon sx={{ color: 'primary.main' }} />}
              />
              <CardContent>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography gutterBottom sx={{ color: darkMode ? 'white' : 'inherit' }}>
                      Max File Size: {formatFileSize(settings.processing.maxFileSize)}
                    </Typography>
                    <Slider
                      value={settings.processing.maxFileSize}
                      onChange={(_, value) => handleSettingChange('processing', 'maxFileSize', value)}
                      min={1}
                      max={50}
                      step={1}
                      marks
                      valueLabelDisplay="auto"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <FormControl fullWidth>
                      <InputLabel>Processing Quality</InputLabel>
                      <Select
                        value={settings.processing.quality}
                        onChange={(e) => handleSettingChange('processing', 'quality', e.target.value)}
                        sx={{
                          background: darkMode ? 'rgba(255, 255, 255, 0.05)' : 'white'
                        }}
                      >
                        <MenuItem value="low">Low (Fast)</MenuItem>
                        <MenuItem value="medium">Medium (Balanced)</MenuItem>
                        <MenuItem value="high">High (Best)</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.processing.autoProcess}
                          onChange={(e) => handleSettingChange('processing', 'autoProcess', e.target.checked)}
                        />
                      }
                      label="Auto-process uploaded documents"
                      sx={{ color: darkMode ? 'white' : 'inherit' }}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Security Settings */}
          <Grid item xs={12} md={6}>
            <Card sx={{ 
              borderRadius: 3,
              background: darkMode 
                ? 'linear-gradient(135deg, #1a1a3a 0%, #2d1b69 50%, #1a1a3a 100%)'
                : 'linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #e2e8f0 100%)',
              boxShadow: darkMode 
                ? '0 8px 32px rgba(0, 0, 0, 0.3), 0 2px 8px rgba(0, 0, 0, 0.2)'
                : '0 8px 32px rgba(0, 0, 0, 0.1), 0 2px 8px rgba(0, 0, 0, 0.05)',
              border: darkMode 
                ? '1px solid rgba(138, 43, 226, 0.3)'
                : '1px solid rgba(138, 43, 226, 0.1)'
            }}>
              <CardHeader
                title="Security"
                titleTypographyProps={{ 
                  color: darkMode ? 'white' : 'inherit',
                  fontWeight: 600
                }}
                avatar={<SecurityIcon sx={{ color: 'primary.main' }} />}
              />
              <CardContent>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography gutterBottom sx={{ color: darkMode ? 'white' : 'inherit' }}>
                      Session Timeout: {settings.security.sessionTimeout} minutes
                    </Typography>
                    <Slider
                      value={settings.security.sessionTimeout}
                      onChange={(_, value) => handleSettingChange('security', 'sessionTimeout', value)}
                      min={5}
                      max={120}
                      step={5}
                      marks
                      valueLabelDisplay="auto"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.security.auditLogging}
                          onChange={(e) => handleSettingChange('security', 'auditLogging', e.target.checked)}
                        />
                      }
                      label="Enable audit logging"
                      sx={{ color: darkMode ? 'white' : 'inherit' }}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Typography gutterBottom sx={{ color: darkMode ? 'white' : 'inherit' }}>
                      Data Retention: {settings.security.dataRetention} days
                    </Typography>
                    <Slider
                      value={settings.security.dataRetention}
                      onChange={(_, value) => handleSettingChange('security', 'dataRetention', value)}
                      min={30}
                      max={365}
                      step={30}
                      marks
                      valueLabelDisplay="auto"
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Action Buttons */}
        <Box sx={{ mt: 4, display: 'flex', gap: 2, justifyContent: 'center' }}>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={saveSettings}
            disabled={!hasChanges || isLoading}
            sx={{
              borderRadius: 2,
              background: 'linear-gradient(135deg, #8a2be2 0%, #4c1d95 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%)'
              }
            }}
          >
            Save Settings
          </Button>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={resetToDefaults}
            disabled={isLoading}
            sx={{
              borderRadius: 2,
              borderColor: darkMode ? 'rgba(138, 43, 226, 0.5)' : 'rgba(138, 43, 226, 0.3)',
              color: darkMode ? 'white' : 'inherit'
            }}
          >
            Reset to Defaults
          </Button>
        </Box>

        {hasChanges && (
          <Alert severity="info" sx={{ mt: 2 }}>
            You have unsaved changes. Click "Save Settings" to apply your changes.
          </Alert>
        )}
      </motion.div>
    </Box>
  );
};

export default SettingsPage;
