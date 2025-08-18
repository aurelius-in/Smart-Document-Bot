import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const UploadPage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
        Upload & Pipeline
      </Typography>
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          Upload and Pipeline functionality coming soon...
        </Typography>
      </Paper>
    </Box>
  );
};

export default UploadPage;
