import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import { Toaster } from 'react-hot-toast';

// Import the showpiece dashboard
import ShowpieceDashboard from './components/ShowpieceDashboard';

// Import other components for fallback
import UnifiedAgentInterface from './components/UnifiedAgentInterface';

const App: React.FC = () => {
  const [showLegacyInterface, setShowLegacyInterface] = useState(false);

  // Create a professional theme for the showpiece
  const theme = createTheme({
    palette: {
      mode: 'light',
      primary: {
        main: '#1976d2',
        light: '#42a5f5',
        dark: '#1565c0',
      },
      secondary: {
        main: '#dc004e',
        light: '#ff5983',
        dark: '#9a0036',
      },
      background: {
        default: '#f5f5f5',
        paper: '#ffffff',
      },
    },
    typography: {
      fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
      h4: {
        fontWeight: 600,
      },
      h6: {
        fontWeight: 500,
      },
    },
    components: {
      MuiCard: {
        styleOverrides: {
          root: {
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            borderRadius: 8,
          },
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: 'none',
            borderRadius: 6,
          },
        },
      },
    },
  });

  const handleExport = () => {
    // Implementation for export functionality
    console.log('Export functionality triggered');
  };

  const handleShare = () => {
    // Implementation for share functionality
    console.log('Share functionality triggered');
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ height: '100vh', overflow: 'hidden' }}>
        {/* Showpiece Dashboard - Primary Interface */}
        <ShowpieceDashboard
          onExport={handleExport}
          onShare={handleShare}
        />
        
        {/* Legacy Interface - Hidden by default, accessible via URL parameter */}
        {showLegacyInterface && (
          <UnifiedAgentInterface />
        )}
      </Box>
      
      {/* Toast notifications */}
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
};

export default App;
