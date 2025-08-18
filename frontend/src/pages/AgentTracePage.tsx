import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const AgentTracePage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
        Agent Trace
      </Typography>
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          Agent Trace functionality coming soon...
        </Typography>
      </Paper>
    </Box>
  );
};

export default AgentTracePage;
