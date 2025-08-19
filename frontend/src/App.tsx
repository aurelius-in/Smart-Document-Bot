import React, { useState } from 'react';
import { Box } from '@mui/material';
import { Toaster } from 'react-hot-toast';

// Import the theme provider
import { ThemeProvider } from './contexts/ThemeContext';

// Import the showpiece dashboard
import ShowpieceDashboard from './components/ShowpieceDashboard';

// Import other components for fallback
import UnifiedAgentInterface from './components/UnifiedAgentInterface';

const App: React.FC = () => {
  const [showLegacyInterface, setShowLegacyInterface] = useState(false);

  const handleExport = () => {
    // Implementation for export functionality
    console.log('Export functionality triggered');
  };

  const handleShare = () => {
    // Implementation for share functionality
    console.log('Share functionality triggered');
  };

  return (
    <ThemeProvider>
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
