import React, { useState } from 'react';
import { Box, Typography } from '@mui/material';
import AnalyticsDashboard from '../components/AnalyticsDashboard';

const AnalyticsPage: React.FC = () => {
  const [timeRange, setTimeRange] = useState<'1h' | '24h' | '7d' | '30d' | '90d'>('7d');

  const handleTimeRangeChange = (range: string) => {
    setTimeRange(range as '1h' | '24h' | '7d' | '30d' | '90d');
  };

  const handleRefresh = () => {
    // Refresh analytics data
    console.log('Refreshing analytics...');
  };

  const handleExport = () => {
    // Export analytics data
    console.log('Exporting analytics...');
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
        Analytics
      </Typography>
      <AnalyticsDashboard
        timeRange={timeRange}
        onTimeRangeChange={handleTimeRangeChange}
        onRefresh={handleRefresh}
        onExport={handleExport}
      />
    </Box>
  );
};

export default AnalyticsPage;
