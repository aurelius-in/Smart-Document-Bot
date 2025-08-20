import React, { useState } from 'react';
import { Box, AppBar, Toolbar, Typography, IconButton, Drawer, List, ListItem, ListItemIcon, ListItemText, Chip } from '@mui/material';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import {
  Menu,
  Dashboard,
  Upload,
  Compare,
  Analytics,
  Chat,
  Settings,
  Download,
  Share,
  DarkMode,
  LightMode,
  Security,
  Visibility,
  RecordVoiceOver
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

// Import the theme provider
import { ThemeProvider, useTheme } from './contexts/ThemeContext';

// Import pages
import DashboardPage from './pages/DashboardPage';
import UploadPage from './pages/UploadPage';
import ComparePage from './pages/ComparePage';
import AgentTracePage from './pages/AgentTracePage';
import AnalyticsPage from './pages/AnalyticsPage';
import QAPage from './pages/QAPage';
import SettingsPage from './pages/SettingsPage';
import DocumentViewerPage from './pages/DocumentViewerPage';
import AuditTrailPage from './pages/AuditTrailPage';
import LoginPage from './pages/LoginPage';

// Import components
import ShowpieceDashboard from './components/ShowpieceDashboard';

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const { darkMode, toggleDarkMode } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [sidebarExpanded, setSidebarExpanded] = useState(false);
  const [isDemoMode, setIsDemoMode] = useState(false);

  const navigationItems = [
    { id: 'dashboard', label: 'Dashboard', icon: <Dashboard />, path: '/' },
    { id: 'upload', label: 'Document Upload', icon: <Upload />, path: '/upload' },
    { id: 'viewer', label: 'Document Viewer', icon: <Visibility />, path: '/viewer' },
    { id: 'compare', label: 'Compare Documents', icon: <Compare />, path: '/compare' },
    { id: 'traces', label: 'Agent Traces', icon: <RecordVoiceOver />, path: '/traces' },
    { id: 'analytics', label: 'Analytics', icon: <Analytics />, path: '/analytics' },
    { id: 'qa', label: 'aiDa Chat', icon: <Chat />, path: '/qa' },
    { id: 'audit', label: 'Audit Trail', icon: <Security />, path: '/audit' },
    { id: 'settings', label: 'Settings', icon: <Settings />, path: '/settings' }
  ];

  const handleNavigation = (path: string) => {
    navigate(path);
    setDrawerOpen(false);
  };

  const handleExport = () => {
    console.log('Export functionality triggered');
  };

  const handleShare = () => {
    console.log('Share functionality triggered');
  };

  const toggleDemoMode = () => {
    setIsDemoMode(!isDemoMode);
  };

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      {/* App Bar */}
      <AppBar position="fixed" sx={{ 
        zIndex: (theme) => theme.zIndex.drawer + 1,
        background: darkMode 
          ? 'linear-gradient(135deg, #0f0f23 0%, #1a1a3a 50%, #2d1b69 100%)'
          : 'linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #e2e8f0 100%)',
        backdropFilter: 'blur(10px)',
        borderBottom: darkMode 
          ? '1px solid rgba(138, 43, 226, 0.2)'
          : '1px solid rgba(138, 43, 226, 0.1)',
        boxShadow: darkMode 
          ? '0 4px 20px rgba(0, 0, 0, 0.3)'
          : '0 4px 20px rgba(0, 0, 0, 0.1)'
      }}>
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => setDrawerOpen(!drawerOpen)}
            sx={{ mr: 2 }}
          >
            <Menu />
          </IconButton>
          
          <Typography variant="h6" component="div" sx={{ 
            flexGrow: 1,
            fontFamily: '"Orbitron", "Roboto", sans-serif',
            fontWeight: 700,
            letterSpacing: '0.05em',
            background: 'linear-gradient(135deg, #ffffff 0%, #e0e7ff 100%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            textShadow: '0 0 20px rgba(138, 43, 226, 0.3)'
          }}>
            aiDa
          </Typography>
          
          <Box display="flex" alignItems="center" gap={1}>
            <Chip
              label={isDemoMode ? 'Demo Mode' : 'Production'}
              color={isDemoMode ? 'warning' : 'success'}
              size="small"
              onClick={toggleDemoMode}
              sx={{
                cursor: 'pointer',
                background: isDemoMode 
                  ? 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'
                  : 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                color: 'white',
                fontWeight: 600,
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.2)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                '&:hover': {
                  transform: 'translateY(-1px)',
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)'
                },
                transition: 'all 0.2s ease'
              }}
            />
            <IconButton 
              sx={{ color: darkMode ? 'white' : 'black' }} 
              onClick={toggleDarkMode}
            >
              {darkMode ? <LightMode /> : <DarkMode />}
            </IconButton>
            <IconButton 
              sx={{ color: darkMode ? 'white' : 'black' }} 
              onClick={handleExport}
            >
              <Download />
            </IconButton>
            <IconButton 
              sx={{ color: darkMode ? 'white' : 'black' }} 
              onClick={handleShare}
            >
              <Share />
            </IconButton>
            <IconButton sx={{ color: darkMode ? 'white' : 'black' }}>
              <Settings />
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Navigation Drawer */}
      <Drawer
        variant="permanent"
        sx={{
          width: sidebarExpanded ? 240 : 80,
          flexShrink: 0,
          transition: 'width 0.3s ease',
          '& .MuiDrawer-paper': {
            width: sidebarExpanded ? 240 : 80,
            boxSizing: 'border-box',
            marginTop: '64px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: sidebarExpanded ? 'stretch' : 'center',
            paddingTop: 2,
            transition: 'width 0.3s ease',
            position: 'relative',
            background: darkMode 
              ? 'linear-gradient(180deg, #0f0f23 0%, #1a1a3a 50%, #2d1b69 100%)'
              : 'linear-gradient(180deg, #ffffff 0%, #f8fafc 50%, #e2e8f0 100%)',
            borderRight: darkMode 
              ? '1px solid rgba(138, 43, 226, 0.2)'
              : '1px solid rgba(138, 43, 226, 0.1)',
            boxShadow: darkMode 
              ? '4px 0 20px rgba(0, 0, 0, 0.3)'
              : '4px 0 20px rgba(0, 0, 0, 0.1)'
          }
        }}
      >
        {/* Resize Handle */}
        <Box
          sx={{
            position: 'absolute',
            right: 0,
            top: 0,
            bottom: 0,
            width: '4px',
            cursor: 'col-resize',
            backgroundColor: 'transparent',
            '&:hover': {
              backgroundColor: 'rgba(0, 0, 0, 0.1)'
            },
            '&:active': {
              backgroundColor: 'rgba(0, 0, 0, 0.2)'
            }
          }}
          onMouseDown={(e) => {
            e.preventDefault();
            const startX = e.clientX;
            const startExpanded = sidebarExpanded;
            
            const handleMouseMove = (moveEvent: MouseEvent) => {
              const deltaX = moveEvent.clientX - startX;
              if (deltaX > 50 && !startExpanded) {
                setSidebarExpanded(true);
              } else if (deltaX < -50 && startExpanded) {
                setSidebarExpanded(false);
              }
            };
            
            const handleMouseUp = () => {
              document.removeEventListener('mousemove', handleMouseMove);
              document.removeEventListener('mouseup', handleMouseUp);
            };
            
            document.addEventListener('mousemove', handleMouseMove);
            document.addEventListener('mouseup', handleMouseUp);
          }}
        />
        
        <List sx={{ width: '100%', padding: 0 }}>
          {navigationItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <ListItem
                key={item.id}
                button
                selected={isActive}
                onClick={() => handleNavigation(item.path)}
                sx={{
                  flexDirection: sidebarExpanded ? 'row' : 'column',
                  padding: sidebarExpanded ? '12px 16px' : '16px 8px',
                  marginBottom: 1,
                  borderRadius: 2,
                  mx: sidebarExpanded ? 1 : 1,
                  minHeight: 'auto',
                  position: 'relative',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    backgroundColor: 'rgba(138, 43, 226, 0.15)',
                    transform: 'translateX(4px)',
                    boxShadow: '0 4px 12px rgba(138, 43, 226, 0.3)'
                  },
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(138, 43, 226, 0.25)',
                    boxShadow: '0 4px 16px rgba(138, 43, 226, 0.4)',
                    border: '1px solid rgba(138, 43, 226, 0.3)'
                  }
                }}
              >
                <ListItemIcon sx={{ 
                  minWidth: sidebarExpanded ? 40 : 'auto',
                  fontSize: sidebarExpanded ? '2.5rem' : '3rem',
                  color: isActive 
                    ? '#8a2be2' 
                    : darkMode 
                      ? 'rgba(255, 255, 255, 0.7)'
                      : 'rgba(0, 0, 0, 0.7)',
                  transition: 'all 0.2s ease',
                  filter: isActive 
                    ? 'drop-shadow(0 0 8px rgba(138, 43, 226, 0.6))'
                    : 'none'
                }}>
                  {item.icon}
                </ListItemIcon>
                {sidebarExpanded && (
                  <ListItemText 
                    primary={item.label} 
                    sx={{
                      '& .MuiListItemText-primary': {
                        fontWeight: isActive ? 600 : 400,
                        color: isActive 
                          ? '#8a2be2' 
                          : darkMode 
                            ? 'rgba(255, 255, 255, 0.9)'
                            : 'rgba(0, 0, 0, 0.9)'
                      }
                    }}
                  />
                )}
              </ListItem>
            );
          })}
        </List>
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          marginTop: '64px',
          marginLeft: sidebarExpanded ? '240px' : '80px',
          padding: 3,
          background: darkMode 
            ? 'linear-gradient(135deg, #0f0f23 0%, #1a1a3a 25%, #2d1b69 50%, #1a1a3a 75%, #0f0f23 100%)'
            : 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 25%, #cbd5e1 50%, #e2e8f0 75%, #f8fafc 100%)',
          minHeight: 'calc(100vh - 64px)',
          overflow: 'auto',
          transition: 'margin-left 0.3s ease'
        }}
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            {children}
          </motion.div>
        </AnimatePresence>
      </Box>
    </Box>
  );
};

const App: React.FC = () => {
  const [isDemoMode, setIsDemoMode] = useState(false);

  if (isDemoMode) {
    return (
      <ThemeProvider>
        <ShowpieceDashboard
          onExport={() => console.log('Export')}
          onShare={() => console.log('Share')}
        />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#4caf50',
                secondary: '#fff',
              },
            },
            error: {
              duration: 5000,
              iconTheme: {
                primary: '#f44336',
                secondary: '#fff',
              },
            },
          }}
        />
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider>
      <LocalizationProvider dateAdapter={AdapterDateFns}>
        <Router>
          <MainLayout>
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/upload" element={<UploadPage />} />
              <Route path="/compare" element={<ComparePage />} />
              <Route path="/traces" element={<AgentTracePage />} />
              <Route path="/analytics" element={<AnalyticsPage />} />
              <Route path="/qa" element={<QAPage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="/viewer" element={<DocumentViewerPage />} />
              <Route path="/audit" element={<AuditTrailPage />} />
              <Route path="/login" element={<LoginPage />} />
            </Routes>
          </MainLayout>
        </Router>
        
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#4caf50',
                secondary: '#fff',
              },
            },
            error: {
              duration: 5000,
              iconTheme: {
                primary: '#f44336',
                secondary: '#fff',
              },
            },
          }}
        />
      </LocalizationProvider>
    </ThemeProvider>
  );
};

export default App;
