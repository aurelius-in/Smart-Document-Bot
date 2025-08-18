import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const AuditTrailPage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
        Audit Trail
      </Typography>
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          Audit Trail functionality coming soon...
        </Typography>
      </Paper>
    </Box>
  );
};

export default AuditTrailPage;
