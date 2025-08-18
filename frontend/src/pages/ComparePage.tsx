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
  DialogActions
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
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { toast } from 'react-hot-toast';
import apiService, { DocumentInfo, ComparisonRequest, ComparisonResult } from '../services/apiService';

const ComparePage: React.FC = () => {
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
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
        Document Comparison
      </Typography>

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
