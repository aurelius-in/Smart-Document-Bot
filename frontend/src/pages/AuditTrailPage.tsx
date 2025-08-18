import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
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
  Tooltip
} from '@mui/material';
import {
  History as HistoryIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Download as DownloadIcon,
  Visibility as ViewIcon,
  Security as SecurityIcon,
  Warning as WarningIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  Person as UserIcon,
  DocumentScanner as DocumentIcon,
  Settings as SettingsIcon,
  Timeline as TimelineIcon
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

interface AuditEvent {
  id: string;
  timestamp: Date;
  userId: string;
  userName: string;
  action: string;
  resource: string;
  resourceId: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: 'user_action' | 'system_event' | 'security' | 'compliance' | 'data_access';
  details: string;
  ipAddress: string;
  userAgent: string;
  sessionId: string;
  metadata?: any;
  complianceTags?: string[];
}

const AuditTrailPage: React.FC = () => {
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [filteredEvents, setFilteredEvents] = useState<AuditEvent[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<AuditEvent | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterUser, setFilterUser] = useState('all');
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);

  // Mock audit data
  useEffect(() => {
    const mockEvents: AuditEvent[] = [
      {
        id: '1',
        timestamp: new Date(Date.now() - 300000),
        userId: 'user1',
        userName: 'John Doe',
        action: 'DOCUMENT_UPLOAD',
        resource: 'Contract_V1.pdf',
        resourceId: 'doc1',
        severity: 'medium',
        category: 'user_action',
        details: 'Uploaded contract document for processing',
        ipAddress: '192.168.1.100',
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        sessionId: 'sess_12345',
        complianceTags: ['SOX', 'GDPR']
      },
      {
        id: '2',
        timestamp: new Date(Date.now() - 600000),
        userId: 'system',
        userName: 'System',
        action: 'DOCUMENT_PROCESSED',
        resource: 'Contract_V1.pdf',
        resourceId: 'doc1',
        severity: 'low',
        category: 'system_event',
        details: 'Document processed successfully by AI agent',
        ipAddress: '127.0.0.1',
        userAgent: 'REDLINE-Agent/1.0',
        sessionId: 'sess_system',
        metadata: {
          processingTime: 2500,
          confidence: 0.89,
          extractedEntities: 15
        }
      },
      {
        id: '3',
        timestamp: new Date(Date.now() - 900000),
        userId: 'user2',
        userName: 'Jane Smith',
        action: 'DOCUMENT_COMPARE',
        resource: 'Contract_V1.pdf vs Contract_V2.pdf',
        resourceId: 'comp1',
        severity: 'high',
        category: 'compliance',
        details: 'Compared contract versions - critical differences detected',
        ipAddress: '192.168.1.101',
        userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        sessionId: 'sess_67890',
        complianceTags: ['SOX', 'Legal Review'],
        metadata: {
          differences: 5,
          riskLevel: 'high',
          complianceImpact: 'significant'
        }
      },
      {
        id: '4',
        timestamp: new Date(Date.now() - 1200000),
        userId: 'user1',
        userName: 'John Doe',
        action: 'SETTINGS_CHANGED',
        resource: 'System Configuration',
        resourceId: 'config1',
        severity: 'medium',
        category: 'user_action',
        details: 'Modified document processing settings',
        ipAddress: '192.168.1.100',
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        sessionId: 'sess_12345'
      },
      {
        id: '5',
        timestamp: new Date(Date.now() - 1500000),
        userId: 'system',
        userName: 'System',
        action: 'SECURITY_ALERT',
        resource: 'Authentication',
        resourceId: 'auth1',
        severity: 'critical',
        category: 'security',
        details: 'Multiple failed login attempts detected',
        ipAddress: '203.0.113.1',
        userAgent: 'Unknown',
        sessionId: 'sess_failed',
        complianceTags: ['Security', 'Access Control']
      },
      {
        id: '6',
        timestamp: new Date(Date.now() - 1800000),
        userId: 'user3',
        userName: 'Bob Wilson',
        action: 'DATA_EXPORT',
        resource: 'Audit Report',
        resourceId: 'report1',
        severity: 'high',
        category: 'data_access',
        details: 'Exported comprehensive audit report',
        ipAddress: '192.168.1.102',
        userAgent: 'Mozilla/5.0 (Linux x86_64)',
        sessionId: 'sess_11111',
        complianceTags: ['Audit', 'Data Export']
      }
    ];

    setAuditEvents(mockEvents);
    setFilteredEvents(mockEvents);
  }, []);

  // Filter events based on search and filters
  useEffect(() => {
    let filtered = auditEvents;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(event =>
        event.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
        event.resource.toLowerCase().includes(searchTerm.toLowerCase()) ||
        event.userName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        event.details.toLowerCase().includes(searchTerm.toLowerCase())
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
      filtered = filtered.filter(event => event.userId === filterUser);
    }

    // Date range filter
    if (startDate) {
      filtered = filtered.filter(event => event.timestamp >= startDate);
    }
    if (endDate) {
      filtered = filtered.filter(event => event.timestamp <= endDate);
    }

    setFilteredEvents(filtered);
    setPage(0);
  }, [auditEvents, searchTerm, filterSeverity, filterCategory, filterUser, startDate, endDate]);

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
      case 'user_action': return <UserIcon />;
      case 'system_event': return <TimelineIcon />;
      case 'security': return <SecurityIcon />;
      case 'compliance': return <DocumentIcon />;
      case 'data_access': return <SettingsIcon />;
      default: return <InfoIcon />;
    }
  };

  const getActionIcon = (action: string) => {
    if (action.includes('UPLOAD')) return <DocumentIcon />;
    if (action.includes('COMPARE')) return <TimelineIcon />;
    if (action.includes('SECURITY')) return <SecurityIcon />;
    if (action.includes('SETTINGS')) return <SettingsIcon />;
    if (action.includes('EXPORT')) return <DownloadIcon />;
    return <InfoIcon />;
  };

  const formatTimestamp = (date: Date) => {
    return date.toLocaleString();
  };

  const exportAuditLog = () => {
    const csvContent = [
      ['Timestamp', 'User', 'Action', 'Resource', 'Severity', 'Category', 'Details'],
      ...filteredEvents.map(event => [
        formatTimestamp(event.timestamp),
        event.userName,
        event.action,
        event.resource,
        event.severity,
        event.category,
        event.details
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit_log_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const uniqueUsers = [...new Set(auditEvents.map(event => event.userId))];

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
              <Typography variant="h6" gutterBottom>
                <FilterIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Filters & Search
              </Typography>
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
                      <MenuItem value="user_action">User Actions</MenuItem>
                      <MenuItem value="system_event">System Events</MenuItem>
                      <MenuItem value="security">Security</MenuItem>
                      <MenuItem value="compliance">Compliance</MenuItem>
                      <MenuItem value="data_access">Data Access</MenuItem>
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
                      {uniqueUsers.map(userId => (
                        <MenuItem key={userId} value={userId}>
                          {auditEvents.find(e => e.userId === userId)?.userName || userId}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <LocalizationProvider dateAdapter={AdapterDateFns}>
                      <DatePicker
                        label="Start Date"
                        value={startDate}
                        onChange={setStartDate}
                        slotProps={{ textField: { size: 'small' } }}
                      />
                      <DatePicker
                        label="End Date"
                        value={endDate}
                        onChange={setEndDate}
                        slotProps={{ textField: { size: 'small' } }}
                      />
                    </LocalizationProvider>
                  </Box>
                </Grid>
              </Grid>
              <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={exportAuditLog}
                >
                  Export CSV
                </Button>
                <Button
                  variant="outlined"
                  onClick={() => {
                    setSearchTerm('');
                    setFilterSeverity('all');
                    setFilterCategory('all');
                    setFilterUser('all');
                    setStartDate(null);
                    setEndDate(null);
                  }}
                >
                  Clear Filters
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Statistics */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Audit Statistics
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography>Total Events:</Typography>
                  <Badge badgeContent={filteredEvents.length} color="primary">
                    <HistoryIcon />
                  </Badge>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography>Critical Events:</Typography>
                  <Badge 
                    badgeContent={filteredEvents.filter(e => e.severity === 'critical').length} 
                    color="error"
                  >
                    <ErrorIcon />
                  </Badge>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography>Security Events:</Typography>
                  <Badge 
                    badgeContent={filteredEvents.filter(e => e.category === 'security').length} 
                    color="warning"
                  >
                    <SecurityIcon />
                  </Badge>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography>Compliance Events:</Typography>
                  <Badge 
                    badgeContent={filteredEvents.filter(e => e.category === 'compliance').length} 
                    color="info"
                  >
                    <DocumentIcon />
                  </Badge>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Audit Table */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Audit Events
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Timestamp</TableCell>
                      <TableCell>User</TableCell>
                      <TableCell>Action</TableCell>
                      <TableCell>Resource</TableCell>
                      <TableCell>Severity</TableCell>
                      <TableCell>Category</TableCell>
                      <TableCell>Details</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filteredEvents
                      .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                      .map((event) => (
                        <TableRow key={event.id} hover>
                          <TableCell>{formatTimestamp(event.timestamp)}</TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <UserIcon fontSize="small" />
                              {event.userName}
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              {getActionIcon(event.action)}
                              {event.action}
                            </Box>
                          </TableCell>
                          <TableCell>{event.resource}</TableCell>
                          <TableCell>
                            <Chip
                              label={event.severity}
                              color={getSeverityColor(event.severity)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              {getCategoryIcon(event.category)}
                              {event.category.replace('_', ' ')}
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                              {event.details}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Tooltip title="View Details">
                              <IconButton
                                size="small"
                                onClick={() => setSelectedEvent(event)}
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
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Event Details Modal */}
        {selectedEvent && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">
                    Event Details
                  </Typography>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => setSelectedEvent(null)}
                  >
                    Close
                  </Button>
                </Box>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>
                      Basic Information
                    </Typography>
                    <List dense>
                      <ListItem>
                        <ListItemText
                          primary="Event ID"
                          secondary={selectedEvent.id}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Timestamp"
                          secondary={formatTimestamp(selectedEvent.timestamp)}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="User"
                          secondary={`${selectedEvent.userName} (${selectedEvent.userId})`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Action"
                          secondary={selectedEvent.action}
                        />
                      </ListItem>
                    </List>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Typography variant="subtitle2" gutterBottom>
                      Technical Details
                    </Typography>
                    <List dense>
                      <ListItem>
                        <ListItemText
                          primary="IP Address"
                          secondary={selectedEvent.ipAddress}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Session ID"
                          secondary={selectedEvent.sessionId}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="User Agent"
                          secondary={selectedEvent.userAgent}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Severity"
                          secondary={
                            <Chip
                              label={selectedEvent.severity}
                              color={getSeverityColor(selectedEvent.severity)}
                              size="small"
                            />
                          }
                        />
                      </ListItem>
                    </List>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom>
                      Details
                    </Typography>
                    <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                      <Typography variant="body2">
                        {selectedEvent.details}
                      </Typography>
                    </Paper>
                  </Grid>
                  {selectedEvent.complianceTags && selectedEvent.complianceTags.length > 0 && (
                    <Grid item xs={12}>
                      <Typography variant="subtitle2" gutterBottom>
                        Compliance Tags
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {selectedEvent.complianceTags.map((tag, index) => (
                          <Chip key={index} label={tag} size="small" color="primary" variant="outlined" />
                        ))}
                      </Box>
                    </Grid>
                  )}
                  {selectedEvent.metadata && (
                    <Grid item xs={12}>
                      <Accordion>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                          <Typography variant="subtitle2">Metadata</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                            <pre style={{ margin: 0, fontSize: '0.875rem' }}>
                              {JSON.stringify(selectedEvent.metadata, null, 2)}
                            </pre>
                          </Paper>
                        </AccordionDetails>
                      </Accordion>
                    </Grid>
                  )}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default AuditTrailPage;
