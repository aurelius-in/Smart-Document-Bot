import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  useTheme as useMuiTheme
} from '@mui/material';
import {
  Compare as CompareIcon,
  Description as FileIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  ExpandMore as ExpandMoreIcon,
  Difference as DifferenceIcon,
  Security as SecurityIcon,
  Assessment as AssessmentIcon,
  History as HistoryIcon,
  Refresh as RefreshIcon,
  AutoAwesome
} from '@mui/icons-material';
import { toast } from 'react-hot-toast';
import { motion } from 'framer-motion';
import { useTheme } from '../contexts/ThemeContext';
import apiService, { DocumentInfo, ComparisonRequest, ComparisonResult } from '../services/apiService';

const ComparePage: React.FC = () => {
  const { darkMode } = useTheme();
  const muiTheme = useMuiTheme();
  const [documentA, setDocumentA] = useState('');
  const [documentB, setDocumentB] = useState('');
  const [comparisonType, setComparisonType] = useState<'semantic' | 'structural' | 'compliance' | 'risk'>('semantic');
  const [isComparing, setIsComparing] = useState(false);
  const [comparisonResults, setComparisonResults] = useState<ComparisonResult[]>([]);
  const [availableDocuments, setAvailableDocuments] = useState<DocumentInfo[]>([]);
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(false);
  const [selectedResult, setSelectedResult] = useState<ComparisonResult | null>(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);

  // Load available documents on component mount
  useEffect(() => {
    loadDocuments();
    loadComparisonHistory();
  }, []);

  const loadDocuments = async () => {
    try {
      setIsLoadingDocuments(true);
      const response = await apiService.getDocuments(1, 100);
      setAvailableDocuments(response.data.filter(doc => doc.status === 'completed'));
    } catch (error) {
      console.error('Failed to load documents:', error);
      toast.error('Failed to load documents');
    } finally {
      setIsLoadingDocuments(false);
    }
  };

  const loadComparisonHistory = async () => {
    try {
      const response = await apiService.getComparisonHistory(1, 20);
      setComparisonResults(response.data);
    } catch (error) {
      console.error('Failed to load comparison history:', error);
      toast.error('Failed to load comparison history');
    }
  };

  const handleCompare = async () => {
    if (!documentA || !documentB) {
      toast.error('Please select both documents to compare');
      return;
    }

    if (documentA === documentB) {
      toast.error('Please select different documents for comparison');
      return;
    }

    setIsComparing(true);
    
    try {
      const request: ComparisonRequest = {
        documentAId: documentA,
        documentBId: documentB,
        comparisonType
      };

      const result = await apiService.compareDocuments(request);
      
      // Add the new result to the beginning of the list
      setComparisonResults(prev => [result, ...prev]);
      
      toast.success('Document comparison started successfully!');
      
      // Clear the form
      setDocumentA('');
      setDocumentB('');
      setComparisonType('semantic');
      
    } catch (error) {
      console.error('Failed to start comparison:', error);
      toast.error('Failed to start document comparison');
    } finally {
      setIsComparing(false);
    }
  };

  const viewComparisonResult = async (resultId: string) => {
    try {
      const result = await apiService.getComparisonResult(resultId);
      setSelectedResult(result);
      setViewDialogOpen(true);
    } catch (error) {
      toast.error('Failed to load comparison result');
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

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'processing': return 'primary';
      case 'error': return 'error';
      case 'pending': return 'warning';
      default: return 'default';
    }
  };

  const getDocumentName = (documentId: string) => {
    const doc = availableDocuments.find(d => d.id === documentId);
    return doc ? doc.filename : `Document ${documentId}`;
  };

  return (
    <Box>
      {/* Header Section */}
      <Box sx={{ 
        mb: 4,
        background: darkMode 
          ? 'linear-gradient(135deg, #0f0f23 0%, #1a1a3a 25%, #2d1b69 50%, #1a1a3a 75%, #0f0f23 100%)'
          : 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 25%, #cbd5e1 50%, #e2e8f0 75%, #f8fafc 100%)',
        color: darkMode ? 'white' : 'inherit',
        p: 4,
        borderRadius: 3,
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 30% 20%, rgba(138, 43, 226, 0.3) 0%, transparent 50%), radial-gradient(circle at 70% 80%, rgba(75, 0, 130, 0.3) 0%, transparent 50%)',
          pointerEvents: 'none'
        }
      }}>
        <Box display="flex" alignItems="center" gap={4} position="relative" zIndex={1}>
          <Box sx={{ 
            background: 'linear-gradient(135deg, rgba(138, 43, 226, 0.8) 0%, rgba(75, 0, 130, 0.8) 100%)',
            borderRadius: '50%', 
            p: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 8px 32px rgba(138, 43, 226, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2)',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <CompareIcon sx={{ 
              fontSize: '2.5rem',
              color: 'white',
              filter: 'drop-shadow(0 0 12px rgba(138, 43, 226, 0.8))'
            }} />
          </Box>
          <Box>
            <Typography variant="h3" component="h1" gutterBottom sx={{ 
              fontWeight: 700,
              fontFamily: '"Orbitron", "Roboto", sans-serif',
              letterSpacing: '0.05em',
              background: 'linear-gradient(135deg, #ffffff 0%, #e0e7ff 50%, #c7d2fe 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              textShadow: '0 0 30px rgba(138, 43, 226, 0.5)'
            }}>
              Document Comparison
            </Typography>
            <Typography variant="h6" sx={{ 
              opacity: 0.95,
              background: 'linear-gradient(135deg, #cbd5e1 0%, #94a3b8 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              Compare documents for semantic, structural, compliance, and risk analysis
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Rest of the existing content */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Grid container spacing={3}>
          {/* Comparison Controls */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Select Documents to Compare
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={4}>
                    <FormControl fullWidth>
                      <InputLabel>Document A</InputLabel>
                      <Select
                        value={documentA}
                        label="Document A"
                        onChange={(e) => setDocumentA(e.target.value)}
                        disabled={isLoadingDocuments}
                      >
                        {availableDocuments.map((doc) => (
                          <MenuItem key={doc.id} value={doc.id}>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <FileIcon sx={{ mr: 1 }} />
                              {doc.filename}
                            </Box>
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <FormControl fullWidth>
                      <InputLabel>Document B</InputLabel>
                      <Select
                        value={documentB}
                        label="Document B"
                        onChange={(e) => setDocumentB(e.target.value)}
                        disabled={isLoadingDocuments}
                      >
                        {availableDocuments.map((doc) => (
                          <MenuItem key={doc.id} value={doc.id}>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <FileIcon sx={{ mr: 1 }} />
                              {doc.filename}
                            </Box>
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <FormControl fullWidth>
                      <InputLabel>Comparison Type</InputLabel>
                      <Select
                        value={comparisonType}
                        label="Comparison Type"
                        onChange={(e) => setComparisonType(e.target.value as any)}
                      >
                        <MenuItem value="semantic">Semantic Analysis</MenuItem>
                        <MenuItem value="structural">Structural Comparison</MenuItem>
                        <MenuItem value="compliance">Compliance Check</MenuItem>
                        <MenuItem value="risk">Risk Assessment</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>
                <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                  <Button
                    variant="contained"
                    startIcon={<CompareIcon />}
                    onClick={handleCompare}
                    disabled={!documentA || !documentB || isComparing || isLoadingDocuments}
                  >
                    {isComparing ? (
                      <>
                        <CircularProgress size={20} sx={{ mr: 1 }} />
                        Comparing...
                      </>
                    ) : (
                      'Compare Documents'
                    )}
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<RefreshIcon />}
                    onClick={loadDocuments}
                    disabled={isLoadingDocuments}
                  >
                    Refresh Documents
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={() => {
                      setDocumentA('');
                      setDocumentB('');
                      setComparisonType('semantic');
                    }}
                  >
                    Clear Selection
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Comparison Results */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">
                    <HistoryIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Comparison History
                  </Typography>
                  <Button
                    variant="outlined"
                    startIcon={<RefreshIcon />}
                    onClick={loadComparisonHistory}
                  >
                    Refresh
                  </Button>
                </Box>
                
                {comparisonResults.length === 0 ? (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <Typography variant="body1" color="text.secondary">
                      No comparison results yet
                    </Typography>
                  </Box>
                ) : (
                  <List>
                    {comparisonResults.map((result, index) => (
                      <React.Fragment key={result.id}>
                        <ListItem>
                          <ListItemIcon>
                            <CompareIcon color="primary" />
                          </ListItemIcon>
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                <Typography variant="subtitle1">
                                  {getDocumentName(result.documentAId)} vs {getDocumentName(result.documentBId)}
                                </Typography>
                                <Chip
                                  label={result.comparisonType}
                                  size="small"
                                  variant="outlined"
                                />
                                <Chip
                                  label={result.status}
                                  color={getStatusColor(result.status)}
                                  size="small"
                                />
                              </Box>
                            }
                            secondary={
                              <Box>
                                <Typography variant="body2" color="text.secondary">
                                  {new Date(result.createdAt).toLocaleString()}
                                </Typography>
                                {result.status === 'completed' && (
                                  <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                                    <Chip
                                      label={`${(result.confidence * 100).toFixed(1)}% Confidence`}
                                      size="small"
                                      variant="outlined"
                                    />
                                    <Chip
                                      label={`${result.duration}ms`}
                                      size="small"
                                      variant="outlined"
                                    />
                                    {result.semanticDiffs && (
                                      <Chip
                                        label={`${result.semanticDiffs.length} differences`}
                                        size="small"
                                        variant="outlined"
                                      />
                                    )}
                                  </Box>
                                )}
                              </Box>
                            }
                          />
                          <Button
                            variant="outlined"
                            size="small"
                            onClick={() => viewComparisonResult(result.id)}
                            disabled={result.status !== 'completed'}
                          >
                            View Details
                          </Button>
                        </ListItem>
                        {index < comparisonResults.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </motion.div>

      {/* Comparison Result Details Dialog */}
      <Dialog
        open={viewDialogOpen}
        onClose={() => setViewDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          Comparison Results
          {selectedResult && (
            <Typography variant="subtitle2" color="text.secondary">
              {getDocumentName(selectedResult.documentAId)} vs {getDocumentName(selectedResult.documentBId)}
            </Typography>
          )}
        </DialogTitle>
        <DialogContent>
          {selectedResult && selectedResult.status === 'completed' && (
            <Grid container spacing={3}>
              {/* Semantic Differences */}
              {selectedResult.semanticDiffs && selectedResult.semanticDiffs.length > 0 && (
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" gutterBottom>
                    <DifferenceIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Semantic Differences
                  </Typography>
                  <List>
                    {selectedResult.semanticDiffs.map((diff: any, index: number) => (
                      <ListItem key={index} sx={{ flexDirection: 'column', alignItems: 'flex-start' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                          <ListItemIcon>
                            {diff.type === 'addition' && <CheckIcon color="success" />}
                            {diff.type === 'deletion' && <ErrorIcon color="error" />}
                            {diff.type === 'modification' && <WarningIcon color="warning" />}
                          </ListItemIcon>
                          <ListItemText
                            primary={diff.section}
                            secondary={diff.content}
                          />
                          <Chip 
                            label={diff.severity}
                            color={getSeverityColor(diff.severity)}
                            size="small"
                          />
                        </Box>
                        <Typography variant="body2" color="text.secondary" sx={{ ml: 4 }}>
                          {diff.description}
                        </Typography>
                      </ListItem>
                    ))}
                  </List>
                </Grid>
              )}

              {/* Risk Assessment */}
              {selectedResult.riskDelta && (
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" gutterBottom>
                    <SecurityIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Risk Assessment
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Chip 
                      label={`Risk Level: ${selectedResult.riskDelta.overallRisk?.toUpperCase() || 'UNKNOWN'}`}
                      color={getRiskColor(selectedResult.riskDelta.overallRisk || 'low')}
                      sx={{ mb: 1 }}
                    />
                    <Typography variant="body2" gutterBottom>
                      Risk Score: {((selectedResult.riskDelta.riskScore || 0) * 100).toFixed(1)}%
                    </Typography>
                  </Box>
                  
                  {selectedResult.riskDelta.riskFactors && (
                    <>
                      <Typography variant="subtitle2" gutterBottom>
                        Risk Factors:
                      </Typography>
                      <Box sx={{ mb: 2 }}>
                        {selectedResult.riskDelta.riskFactors.map((factor: string, index: number) => (
                          <Chip 
                            key={index}
                            label={factor}
                            size="small"
                            sx={{ mr: 1, mb: 1 }}
                          />
                        ))}
                      </Box>
                    </>
                  )}

                  {selectedResult.riskDelta.mitigations && (
                    <>
                      <Typography variant="subtitle2" gutterBottom>
                        Mitigations:
                      </Typography>
                      <List dense>
                        {selectedResult.riskDelta.mitigations.map((mitigation: string, index: number) => (
                          <ListItem key={index}>
                            <ListItemText primary={mitigation} />
                          </ListItem>
                        ))}
                      </List>
                    </>
                  )}
                </Grid>
              )}

              {/* Compliance Impact */}
              {selectedResult.complianceImpact && (
                <Grid item xs={12}>
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <AssessmentIcon sx={{ mr: 1 }} />
                      <Typography variant="h6">Compliance Impact</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Grid container spacing={2}>
                        {selectedResult.complianceImpact.regulations && (
                          <Grid item xs={12} md={4}>
                            <Typography variant="subtitle2" gutterBottom>
                              Affected Regulations:
                            </Typography>
                            {selectedResult.complianceImpact.regulations.map((reg: string, index: number) => (
                              <Chip key={index} label={reg} size="small" sx={{ mr: 1, mb: 1 }} />
                            ))}
                          </Grid>
                        )}
                        {selectedResult.complianceImpact.violations && (
                          <Grid item xs={12} md={4}>
                            <Typography variant="subtitle2" gutterBottom>
                              Potential Violations:
                            </Typography>
                            {selectedResult.complianceImpact.violations.map((violation: string, index: number) => (
                              <Alert key={index} severity="warning" sx={{ mb: 1 }}>
                                {violation}
                              </Alert>
                            ))}
                          </Grid>
                        )}
                        {selectedResult.complianceImpact.recommendations && (
                          <Grid item xs={12} md={4}>
                            <Typography variant="subtitle2" gutterBottom>
                              Recommendations:
                            </Typography>
                            {selectedResult.complianceImpact.recommendations.map((rec: string, index: number) => (
                              <Alert key={index} severity="info" sx={{ mb: 1 }}>
                                {rec}
                              </Alert>
                            ))}
                          </Grid>
                        )}
                      </Grid>
                    </AccordionDetails>
                  </Accordion>
                </Grid>
              )}
            </Grid>
          )}
          
          {selectedResult && selectedResult.status !== 'completed' && (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <CircularProgress sx={{ mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Comparison in Progress
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Please wait while the comparison is being processed...
              </Typography>
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

export default ComparePage;
