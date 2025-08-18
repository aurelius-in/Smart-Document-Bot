import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const AnalyticsPage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
        Analytics
      </Typography>
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          Analytics functionality coming soon...
        </Typography>
      </Paper>
    </Box>
  );
};

export default AnalyticsPage;
