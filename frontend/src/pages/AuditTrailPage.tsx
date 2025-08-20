import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Grid,
  Card,
  CardContent,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Badge,
  Tooltip,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Download as DownloadIcon,
  Visibility as ViewIcon,
  ExpandMore as ExpandMoreIcon,
  Security as SecurityIcon,
  Assignment as AssignmentIcon,
  Person as PersonIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  CheckCircle as SuccessIcon,
  Refresh as RefreshIcon,
  Clear as ClearIcon
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { toast } from 'react-hot-toast';
import apiService, { AuditEvent } from '../services/apiService';

const AuditTrailPage: React.FC = () => {
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [filteredEvents, setFilteredEvents] = useState<AuditEvent[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<AuditEvent | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [filterUser, setFilterUser] = useState<string>('all');
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);

  // Load audit events on component mount
  useEffect(() => {
    loadAuditEvents();
  }, []);

  // Filter events when filters change
  useEffect(() => {
    filterEvents();
  }, [auditEvents, searchTerm, filterSeverity, filterCategory, filterUser, startDate, endDate]);

  const loadAuditEvents = async () => {
    try {
      setIsLoading(true);
      const response = await apiService.getAuditEvents(1, 1000); // Get more events for filtering
      setAuditEvents(response.data);
    } catch (error) {
      console.error('Failed to load audit events:', error);
      toast.error('Failed to load audit events');
    } finally {
      setIsLoading(false);
    }
  };

  const filterEvents = () => {
    let filtered = [...auditEvents];

    // Search term filter
    if (searchTerm) {
      filtered = filtered.filter(event =>
        event.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
        event.details.toLowerCase().includes(searchTerm.toLowerCase()) ||
        event.userName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        event.resource.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Severity filter
    if (filterSeverity !== 'all') {
      filtered = filtered.filter(event => event.severity === filterSeverity);
    }

    // Category filter
    if (filterCategory !== 'all') {
      filtered = filtered.filter(event => event.category === filterCategory);
    }

    // User filter
    if (filterUser !== 'all') {
      filtered = filtered.filter(event => event.userName === filterUser);
    }

    // Date range filter
    if (startDate) {
      filtered = filtered.filter(event => new Date(event.timestamp) >= startDate);
    }
    if (endDate) {
      filtered = filtered.filter(event => new Date(event.timestamp) <= endDate);
    }

    setFilteredEvents(filtered);
    setPage(0); // Reset to first page when filtering
  };

  const clearFilters = () => {
    setSearchTerm('');
    setFilterSeverity('all');
    setFilterCategory('all');
    setFilterUser('all');
    setStartDate(null);
    setEndDate(null);
  };

  const viewEventDetails = async (eventId: string) => {
    try {
      const event = await apiService.getAuditEvent(eventId);
      setSelectedEvent(event);
      setViewDialogOpen(true);
    } catch (error) {
      toast.error('Failed to load event details');
    }
  };

  const exportAuditLog = async () => {
    try {
      const csvData = await apiService.exportAuditLog({
        startDate: startDate?.toISOString(),
        endDate: endDate?.toISOString(),
        severity: filterSeverity !== 'all' ? filterSeverity : undefined,
        category: filterCategory !== 'all' ? filterCategory : undefined,
        user: filterUser !== 'all' ? filterUser : undefined,
        searchTerm: searchTerm || undefined
      });

      // Create and download CSV file
      const blob = new Blob([csvData], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit_log_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      toast.success('Audit log exported successfully!');
    } catch (error) {
      console.error('Failed to export audit log:', error);
      toast.error('Failed to export audit log');
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'security': return <SecurityIcon />;
      case 'document': return <AssignmentIcon />;
      case 'user': return <PersonIcon />;
      case 'system': return <InfoIcon />;
      default: return <InfoIcon />;
    }
  };

  const getActionIcon = (action: string) => {
    if (action.includes('login') || action.includes('auth')) return <SecurityIcon />;
    if (action.includes('upload') || action.includes('download')) return <AssignmentIcon />;
    if (action.includes('delete')) return <ErrorIcon />;
    if (action.includes('create') || action.includes('add')) return <SuccessIcon />;
    if (action.includes('update') || action.includes('modify')) return <WarningIcon />;
    return <InfoIcon />;
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const getUniqueUsers = () => {
    const users = Array.from(new Set(auditEvents.map(event => event.userName)));
    return users.sort();
  };

  const getUniqueCategories = () => {
    const categories = Array.from(new Set(auditEvents.map(event => event.category)));
    return categories.sort();
  };

  const getAuditStats = () => {
    const total = filteredEvents.length;
    const critical = filteredEvents.filter(e => e.severity === 'critical').length;
    const high = filteredEvents.filter(e => e.severity === 'high').length;
    const medium = filteredEvents.filter(e => e.severity === 'medium').length;
    const low = filteredEvents.filter(e => e.severity === 'low').length;

    return { total, critical, high, medium, low };
  };

  const stats = getAuditStats();

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
        Audit Trail
      </Typography>

      <Grid container spacing={3}>
        {/* Filters */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  <FilterIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Filters & Search
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    variant="outlined"
                    startIcon={<RefreshIcon />}
                    onClick={loadAuditEvents}
                    disabled={isLoading}
                  >
                    Refresh
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<ClearIcon />}
                    onClick={clearFilters}
                  >
                    Clear Filters
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={<DownloadIcon />}
                    onClick={exportAuditLog}
                  >
                    Export
                  </Button>
                </Box>
              </Box>

              <Grid container spacing={2}>
                <Grid item xs={12} md={3}>
                  <TextField
                    fullWidth
                    label="Search"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    InputProps={{
                      startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
                    }}
                  />
                </Grid>
                <Grid item xs={12} md={2}>
                  <FormControl fullWidth>
                    <InputLabel>Severity</InputLabel>
                    <Select
                      value={filterSeverity}
                      label="Severity"
                      onChange={(e) => setFilterSeverity(e.target.value)}
                    >
                      <MenuItem value="all">All Severities</MenuItem>
                      <MenuItem value="critical">Critical</MenuItem>
                      <MenuItem value="high">High</MenuItem>
                      <MenuItem value="medium">Medium</MenuItem>
                      <MenuItem value="low">Low</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={2}>
                  <FormControl fullWidth>
                    <InputLabel>Category</InputLabel>
                    <Select
                      value={filterCategory}
                      label="Category"
                      onChange={(e) => setFilterCategory(e.target.value)}
                    >
                      <MenuItem value="all">All Categories</MenuItem>
                      {getUniqueCategories().map(category => (
                        <MenuItem key={category} value={category}>
                          {category.charAt(0).toUpperCase() + category.slice(1)}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={2}>
                  <FormControl fullWidth>
                    <InputLabel>User</InputLabel>
                    <Select
                      value={filterUser}
                      label="User"
                      onChange={(e) => setFilterUser(e.target.value)}
                    >
                      <MenuItem value="all">All Users</MenuItem>
                      {getUniqueUsers().map(user => (
                        <MenuItem key={user} value={user}>
                          {user}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <DatePicker
                      label="Start Date"
                      value={startDate}
                      onChange={(newValue) => setStartDate(newValue)}
                      slotProps={{ textField: { fullWidth: true } }}
                    />
                    <DatePicker
                      label="End Date"
                      value={endDate}
                      onChange={(newValue) => setEndDate(newValue)}
                      slotProps={{ textField: { fullWidth: true } }}
                    />
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Statistics */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Audit Statistics
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={2}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="primary">
                      {stats.total}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Events
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={2}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="error">
                      {stats.critical}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Critical
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={2}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="warning.main">
                      {stats.high}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      High
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={2}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="info.main">
                      {stats.medium}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Medium
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={2}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="success.main">
                      {stats.low}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Low
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={2}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" color="text.secondary">
                      {auditEvents.length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total (All)
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Audit Events Table */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Audit Events ({filteredEvents.length} events)
              </Typography>

              {isLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                  {/* Assuming CircularProgress is available, otherwise replace with a simple text or spinner */}
                  <Typography variant="body1">Loading...</Typography>
                </Box>
              ) : filteredEvents.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body1" color="text.secondary">
                    No audit events found
                  </Typography>
                </Box>
              ) : (
                <>
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Timestamp</TableCell>
                          <TableCell>User</TableCell>
                          <TableCell>Action</TableCell>
                          <TableCell>Category</TableCell>
                          <TableCell>Severity</TableCell>
                          <TableCell>Resource</TableCell>
                          <TableCell>IP Address</TableCell>
                          <TableCell>Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {filteredEvents
                          .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                          .map((event) => (
                            <TableRow key={event.id} hover>
                              <TableCell>
                                <Typography variant="body2">
                                  {formatTimestamp(event.timestamp)}
                                </Typography>
                              </TableCell>
                              <TableCell>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                  <PersonIcon fontSize="small" />
                                  {event.userName}
                                </Box>
                              </TableCell>
                              <TableCell>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                  {getActionIcon(event.action)}
                                  <Typography variant="body2">
                                    {event.action}
                                  </Typography>
                                </Box>
                              </TableCell>
                              <TableCell>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                  {getCategoryIcon(event.category)}
                                  <Chip
                                    label={event.category}
                                    size="small"
                                    variant="outlined"
                                  />
                                </Box>
                              </TableCell>
                              <TableCell>
                                <Chip
                                  label={event.severity}
                                  color={getSeverityColor(event.severity)}
                                  size="small"
                                />
                              </TableCell>
                              <TableCell>
                                <Typography variant="body2" noWrap>
                                  {event.resource}
                                </Typography>
                              </TableCell>
                              <TableCell>
                                <Typography variant="body2" color="text.secondary">
                                  {event.ipAddress || 'N/A'}
                                </Typography>
                              </TableCell>
                              <TableCell>
                                <Tooltip title="View Details">
                                  <IconButton
                                    size="small"
                                    onClick={() => viewEventDetails(event.id)}
                                  >
                                    <ViewIcon />
                                  </IconButton>
                                </Tooltip>
                              </TableCell>
                            </TableRow>
                          ))}
                      </TableBody>
                    </Table>
                  </TableContainer>

                  <TablePagination
                    component="div"
                    count={filteredEvents.length}
                    page={page}
                    onPageChange={(_, newPage) => setPage(newPage)}
                    rowsPerPage={rowsPerPage}
                    onRowsPerPageChange={(e) => {
                      setRowsPerPage(parseInt(e.target.value, 10));
                      setPage(0);
                    }}
                    rowsPerPageOptions={[10, 25, 50, 100]}
                  />
                </>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Event Details Dialog */}
      <Dialog
        open={viewDialogOpen}
        onClose={() => setViewDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Audit Event Details
          {selectedEvent && (
            <Typography variant="subtitle2" color="text.secondary">
              Event ID: {selectedEvent.id}
            </Typography>
          )}
        </DialogTitle>
        <DialogContent>
          {selectedEvent && (
            <Box>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Timestamp
                  </Typography>
                  <Typography variant="body1">
                    {formatTimestamp(selectedEvent.timestamp)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    User
                  </Typography>
                  <Typography variant="body1">
                    {selectedEvent.userName}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Action
                  </Typography>
                  <Typography variant="body1">
                    {selectedEvent.action}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Category
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {getCategoryIcon(selectedEvent.category)}
                    <Typography variant="body1">
                      {selectedEvent.category}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Severity
                  </Typography>
                  <Chip
                    label={selectedEvent.severity}
                    color={getSeverityColor(selectedEvent.severity)}
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    IP Address
                  </Typography>
                  <Typography variant="body1">
                    {selectedEvent.ipAddress || 'N/A'}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Resource
                  </Typography>
                  <Typography variant="body1">
                    {selectedEvent.resource}
                  </Typography>
                </Grid>
              </Grid>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="h6">Event Details</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body1" gutterBottom>
                    <strong>Description:</strong>
                  </Typography>
                  <Typography variant="body2" paragraph>
                    {selectedEvent.details}
                  </Typography>

                  {selectedEvent.metadata && Object.keys(selectedEvent.metadata).length > 0 && (
                    <>
                      <Typography variant="body1" gutterBottom>
                        <strong>Metadata:</strong>
                      </Typography>
                      <Box sx={{ bgcolor: 'grey.50', p: 2, borderRadius: 1 }}>
                        <pre style={{ margin: 0, fontSize: '0.875rem' }}>
                          {JSON.stringify(selectedEvent.metadata, null, 2)}
                        </pre>
                      </Box>
                    </>
                  )}


                </AccordionDetails>
              </Accordion>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialogOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AuditTrailPage;
