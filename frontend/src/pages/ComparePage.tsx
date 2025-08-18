import React, { useState } from 'react';
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
  AccordionDetails
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
  Assessment as AssessmentIcon
} from '@mui/icons-material';

interface ComparisonResult {
  id: string;
  documentA: string;
  documentB: string;
  comparisonType: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  semanticDiffs: SemanticDiff[];
  riskDelta: RiskDelta;
  complianceImpact: ComplianceImpact;
  confidence: number;
  duration: number;
  createdAt: Date;
}

interface SemanticDiff {
  id: string;
  type: 'addition' | 'deletion' | 'modification';
  section: string;
  content: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
}

interface RiskDelta {
  overallRisk: 'low' | 'medium' | 'high' | 'critical';
  riskScore: number;
  riskFactors: string[];
  mitigations: string[];
}

interface ComplianceImpact {
  regulations: string[];
  violations: string[];
  recommendations: string[];
  impact: 'low' | 'medium' | 'high' | 'critical';
}

const ComparePage: React.FC = () => {
  const [documentA, setDocumentA] = useState('');
  const [documentB, setDocumentB] = useState('');
  const [comparisonType, setComparisonType] = useState('semantic');
  const [isComparing, setIsComparing] = useState(false);
  const [comparisonResults, setComparisonResults] = useState<ComparisonResult[]>([]);

  // Mock document list - in real app, this would come from API
  const availableDocuments = [
    { id: 'doc1', name: 'Contract_V1.pdf', type: 'contract' },
    { id: 'doc2', name: 'Contract_V2.pdf', type: 'contract' },
    { id: 'doc3', name: 'Policy_2023.pdf', type: 'policy' },
    { id: 'doc4', name: 'Policy_2024.pdf', type: 'policy' },
    { id: 'doc5', name: 'Invoice_001.pdf', type: 'invoice' },
    { id: 'doc6', name: 'Invoice_002.pdf', type: 'invoice' }
  ];

  const handleCompare = async () => {
    if (!documentA || !documentB) {
      return;
    }

    setIsComparing(true);
    const resultId = Math.random().toString(36).substr(2, 9);
    
    const newResult: ComparisonResult = {
      id: resultId,
      documentA,
      documentB,
      comparisonType,
      status: 'processing',
      semanticDiffs: [],
      riskDelta: {
        overallRisk: 'low',
        riskScore: 0,
        riskFactors: [],
        mitigations: []
      },
      complianceImpact: {
        regulations: [],
        violations: [],
        recommendations: [],
        impact: 'low'
      },
      confidence: 0,
      duration: 0,
      createdAt: new Date()
    };

    setComparisonResults(prev => [newResult, ...prev]);

    // Simulate comparison process
    setTimeout(() => {
      const mockResult: ComparisonResult = {
        ...newResult,
        status: 'completed',
        semanticDiffs: [
          {
            id: 'diff1',
            type: 'modification',
            section: 'Terms and Conditions',
            content: 'Payment terms changed from 30 days to 45 days',
            severity: 'medium',
            description: 'Payment terms modification detected'
          },
          {
            id: 'diff2',
            type: 'addition',
            section: 'Liability Clause',
            content: 'New liability limitation clause added',
            severity: 'high',
            description: 'New liability clause detected'
          },
          {
            id: 'diff3',
            type: 'deletion',
            section: 'Force Majeure',
            content: 'Force majeure clause removed',
            severity: 'critical',
            description: 'Critical clause removal detected'
          }
        ],
        riskDelta: {
          overallRisk: 'high',
          riskScore: 0.75,
          riskFactors: [
            'Removal of force majeure clause',
            'Extended payment terms',
            'New liability limitations'
          ],
          mitigations: [
            'Review force majeure implications',
            'Assess cash flow impact',
            'Legal review of liability changes'
          ]
        },
        complianceImpact: {
          regulations: ['SOX', 'GDPR'],
          violations: ['Insufficient risk disclosure'],
          recommendations: [
            'Add risk disclosure statement',
            'Update compliance documentation'
          ],
          impact: 'high'
        },
        confidence: 0.89,
        duration: 2500
      };

      setComparisonResults(prev => 
        prev.map(r => r.id === resultId ? mockResult : r)
      );
      setIsComparing(false);
    }, 3000);
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
                    >
                      {availableDocuments.map((doc) => (
                        <MenuItem key={doc.id} value={doc.id}>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <FileIcon sx={{ mr: 1 }} />
                            {doc.name}
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
                    >
                      {availableDocuments.map((doc) => (
                        <MenuItem key={doc.id} value={doc.id}>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <FileIcon sx={{ mr: 1 }} />
                            {doc.name}
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
                      onChange={(e) => setComparisonType(e.target.value)}
                    >
                      <MenuItem value="semantic">Semantic Analysis</MenuItem>
                      <MenuItem value="structural">Structural Comparison</MenuItem>
                      <MenuItem value="compliance">Compliance Check</MenuItem>
                      <MenuItem value="risk">Risk Assessment</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
              <Box sx={{ mt: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<CompareIcon />}
                  onClick={handleCompare}
                  disabled={!documentA || !documentB || isComparing}
                  sx={{ mr: 2 }}
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
        {comparisonResults.map((result) => (
          <Grid item xs={12} key={result.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">
                    Comparison Results
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip 
                      label={`${result.confidence * 100}% Confidence`}
                      color="primary"
                      size="small"
                    />
                    <Chip 
                      label={`${result.duration}ms`}
                      color="secondary"
                      size="small"
                    />
                  </Box>
                </Box>

                {result.status === 'processing' && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <CircularProgress size={20} />
                    <Typography>Processing comparison...</Typography>
                  </Box>
                )}

                {result.status === 'completed' && (
                  <Grid container spacing={3}>
                    {/* Semantic Differences */}
                    <Grid item xs={12} md={6}>
                      <Typography variant="h6" gutterBottom>
                        <DifferenceIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                        Semantic Differences
                      </Typography>
                      <List>
                        {result.semanticDiffs.map((diff) => (
                          <ListItem key={diff.id} sx={{ flexDirection: 'column', alignItems: 'flex-start' }}>
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

                    {/* Risk Assessment */}
                    <Grid item xs={12} md={6}>
                      <Typography variant="h6" gutterBottom>
                        <SecurityIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                        Risk Assessment
                      </Typography>
                      <Box sx={{ mb: 2 }}>
                        <Chip 
                          label={`Risk Level: ${result.riskDelta.overallRisk.toUpperCase()}`}
                          color={getRiskColor(result.riskDelta.overallRisk)}
                          sx={{ mb: 1 }}
                        />
                        <Typography variant="body2" gutterBottom>
                          Risk Score: {(result.riskDelta.riskScore * 100).toFixed(1)}%
                        </Typography>
                      </Box>
                      
                      <Typography variant="subtitle2" gutterBottom>
                        Risk Factors:
                      </Typography>
                      <Box sx={{ mb: 2 }}>
                        {result.riskDelta.riskFactors.map((factor, index) => (
                          <Chip 
                            key={index}
                            label={factor}
                            size="small"
                            sx={{ mr: 1, mb: 1 }}
                          />
                        ))}
                      </Box>

                      <Typography variant="subtitle2" gutterBottom>
                        Mitigations:
                      </Typography>
                      <List dense>
                        {result.riskDelta.mitigations.map((mitigation, index) => (
                          <ListItem key={index}>
                            <ListItemText primary={mitigation} />
                          </ListItem>
                        ))}
                      </List>
                    </Grid>

                    {/* Compliance Impact */}
                    <Grid item xs={12}>
                      <Accordion>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                          <AssessmentIcon sx={{ mr: 1 }} />
                          <Typography variant="h6">Compliance Impact</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Grid container spacing={2}>
                            <Grid item xs={12} md={4}>
                              <Typography variant="subtitle2" gutterBottom>
                                Affected Regulations:
                              </Typography>
                              {result.complianceImpact.regulations.map((reg, index) => (
                                <Chip key={index} label={reg} size="small" sx={{ mr: 1, mb: 1 }} />
                              ))}
                            </Grid>
                            <Grid item xs={12} md={4}>
                              <Typography variant="subtitle2" gutterBottom>
                                Potential Violations:
                              </Typography>
                              {result.complianceImpact.violations.map((violation, index) => (
                                <Alert key={index} severity="warning" sx={{ mb: 1 }}>
                                  {violation}
                                </Alert>
                              ))}
                            </Grid>
                            <Grid item xs={12} md={4}>
                              <Typography variant="subtitle2" gutterBottom>
                                Recommendations:
                              </Typography>
                              {result.complianceImpact.recommendations.map((rec, index) => (
                                <Alert key={index} severity="info" sx={{ mb: 1 }}>
                                  {rec}
                                </Alert>
                              ))}
                            </Grid>
                          </Grid>
                        </AccordionDetails>
                      </Accordion>
                    </Grid>
                  </Grid>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default ComparePage;
