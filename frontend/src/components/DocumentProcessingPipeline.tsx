import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  Divider,
  IconButton,
  Tooltip,
  Collapse
} from '@mui/material';
import {
  Upload,
  TextFields,
  Search,
  Assessment,
  Storage,
  CheckCircle,
  Error,
  Schedule,
  ExpandMore,
  ExpandLess,
  PlayArrow,
  Pause,
  Stop
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

interface PipelineStep {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  progress: number;
  logs: string[];
  startTime?: Date;
  endTime?: Date;
  duration?: number;
}

interface DocumentProcessingPipelineProps {
  isProcessing: boolean;
  currentStep: string;
  pipelineSteps: PipelineStep[];
  onStepClick?: (stepId: string) => void;
  animationSpeed: number;
}

const DocumentProcessingPipeline: React.FC<DocumentProcessingPipelineProps> = ({
  isProcessing,
  currentStep,
  pipelineSteps,
  onStepClick,
  animationSpeed
}) => {
  const [expandedStep, setExpandedStep] = useState<string | null>(null);
  const [showLogs, setShowLogs] = useState(true);

  const stepIcons = {
    upload: <Upload />,
    ocr: <TextFields />,
    ner: <Search />,
    classify: <Assessment />,
    risk: <Assessment />,
    index: <Storage />
  };

  const getStepColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'processing':
        return 'primary';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStepIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle />;
      case 'processing':
        return <Schedule />;
      case 'error':
        return <Error />;
      default:
        return null;
    }
  };

  const formatDuration = (duration?: number) => {
    if (!duration) return '';
    if (duration < 1000) return `${duration}ms`;
    return `${(duration / 1000).toFixed(1)}s`;
  };

  const handleStepClick = (stepId: string) => {
    if (expandedStep === stepId) {
      setExpandedStep(null);
    } else {
      setExpandedStep(stepId);
    }
    onStepClick?.(stepId);
  };

  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Typography variant="h6" gutterBottom>
            Processing Pipeline
          </Typography>
          <Box display="flex" alignItems="center" gap={1}>
            <Tooltip title="Toggle Details">
              <IconButton
                size="small"
                onClick={() => setShowLogs(!showLogs)}
              >
                {showLogs ? <ExpandLess /> : <ExpandMore />}
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* Pipeline Visualization */}
        <Box mb={3}>
          <Box
            display="flex"
            alignItems="center"
            justifyContent="space-between"
            sx={{
              position: 'relative',
              '&::before': {
                content: '""',
                position: 'absolute',
                top: '50%',
                left: 0,
                right: 0,
                height: 2,
                backgroundColor: 'divider',
                zIndex: 0
              }
            }}
          >
            {pipelineSteps.map((step, index) => (
              <motion.div
                key={step.id}
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: index * 0.1 * animationSpeed }}
                style={{ zIndex: 1 }}
              >
                <Box
                  display="flex"
                  flexDirection="column"
                  alignItems="center"
                  sx={{ cursor: 'pointer' }}
                  onClick={() => handleStepClick(step.id)}
                >
                  <Paper
                    elevation={step.status === 'processing' ? 8 : 2}
                    sx={{
                      p: 1,
                      borderRadius: '50%',
                      backgroundColor: step.status === 'processing' ? 'primary.main' : 'background.paper',
                      color: step.status === 'processing' ? 'primary.contrastText' : 'text.primary',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'scale(1.1)',
                        elevation: 4
                      }
                    }}
                  >
                    {step.icon}
                  </Paper>
                                     <Typography
                     variant="body1"
                     sx={{
                       mt: 1,
                       textAlign: 'center',
                       fontWeight: step.status === 'processing' ? 'bold' : 'normal',
                       fontSize: '1.1rem'
                     }}
                   >
                     {step.name}
                   </Typography>
                   {step.status === 'processing' && (
                     <motion.div
                       animate={{ rotate: 360 }}
                       transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                     >
                       <Schedule sx={{ fontSize: 24, color: 'primary.main' }} />
                     </motion.div>
                   )}
                   {step.status === 'completed' && (
                     <CheckCircle sx={{ fontSize: 24, color: 'success.main' }} />
                   )}
                   {step.status === 'error' && (
                     <Error sx={{ fontSize: 24, color: 'error.main' }} />
                   )}
                </Box>
              </motion.div>
            ))}
          </Box>
        </Box>

        {/* Step Details */}
        <List>
          {pipelineSteps.map((step, index) => (
            <motion.div
              key={step.id}
              initial={{ x: -50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: index * 0.1 * animationSpeed }}
            >
              <ListItem
                button
                onClick={() => handleStepClick(step.id)}
                sx={{
                  border: step.status === 'processing' ? 2 : 1,
                  borderColor: step.status === 'processing' ? 'primary.main' : 'divider',
                  borderRadius: 1,
                  mb: 1,
                  backgroundColor: step.status === 'processing' ? 'action.hover' : 'transparent'
                }}
              >
                <ListItemIcon>
                  <Box
                    sx={{
                      color: getStepColor(step.status) === 'success' ? 'success.main' :
                             getStepColor(step.status) === 'error' ? 'error.main' :
                             getStepColor(step.status) === 'primary' ? 'primary.main' : 'text.secondary'
                    }}
                  >
                    {step.icon}
                  </Box>
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="subtitle2">
                        {step.name}
                      </Typography>
                      <Chip
                        label={step.status}
                        color={getStepColor(step.status)}
                        size="small"
                      />
                      {step.duration && (
                        <Typography variant="caption" color="text.secondary">
                          ({formatDuration(step.duration)})
                        </Typography>
                      )}
                    </Box>
                  }
                  secondary={step.description}
                />
                <Box display="flex" alignItems="center" gap={1}>
                  {getStepIcon(step.status)}
                  {expandedStep === step.id ? <ExpandLess /> : <ExpandMore />}
                </Box>
              </ListItem>

              {/* Step Progress */}
              {step.status === 'processing' && (
                <Box sx={{ ml: 4, mb: 1 }}>
                  <LinearProgress
                    variant="determinate"
                    value={step.progress}
                    sx={{ height: 4, borderRadius: 2 }}
                  />
                  <Typography variant="caption" color="text.secondary">
                    {step.progress}% complete
                  </Typography>
                </Box>
              )}

                             {/* Step Details */}
               <Collapse in={expandedStep === step.id && showLogs}>
                 <Paper sx={{ 
                   ml: 4, 
                   mb: 1, 
                   p: 3, 
                   backgroundColor: 'background.paper',
                   border: '1px solid',
                   borderColor: 'divider'
                 }}>
                   <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>
                     Document Processing Results
                   </Typography>
                  
                                     {step.id === 'upload' && (
                     <Box>
                       <Typography variant="body2" sx={{ mb: 2 }}>
                         <strong>File Information:</strong>
                       </Typography>
                       <Box sx={{ pl: 2, mb: 2 }}>
                         <Typography variant="body2">
                           • Filename: Financial_Services_Agreement_2024.pdf
                         </Typography>
                         <Typography variant="body2">
                           • File Size: 2.4 MB
                         </Typography>
                         <Typography variant="body2">
                           • Pages: 12
                         </Typography>
                         <Typography variant="body2">
                           • Format: PDF (Portable Document Format)
                         </Typography>
                         <Typography variant="body2">
                           • Upload Time: {new Date().toLocaleString()}
                         </Typography>
                       </Box>
                       <Typography variant="body2" sx={{ mb: 1 }}>
                         <strong>Validation Results:</strong>
                       </Typography>
                       <Box sx={{ pl: 2 }}>
                         <Typography variant="body2">
                           ✓ File integrity verified
                         </Typography>
                         <Typography variant="body2">
                           ✓ No security threats detected
                         </Typography>
                         <Typography variant="body2">
                           ✓ Document structure validated
                         </Typography>
                       </Box>
                     </Box>
                   )}
                  
                                     {step.id === 'ocr' && (
                     <Box>
                       <Typography variant="body2" sx={{ mb: 2 }}>
                         <strong>Text Extraction Summary:</strong>
                       </Typography>
                       <Box sx={{ pl: 2, mb: 2 }}>
                         <Typography variant="body2">
                           • Total Characters: 1,247
                         </Typography>
                         <Typography variant="body2">
                           • Words: 198
                         </Typography>
                         <Typography variant="body2">
                           • Lines: 45
                         </Typography>
                         <Typography variant="body2">
                           • Language: English (99.8% confidence)
                         </Typography>
                       </Box>
                       <Typography variant="body2" sx={{ mb: 1 }}>
                         <strong>Sample Extracted Text:</strong>
                       </Typography>
                       <Box sx={{ 
                         pl: 2, 
                         p: 2, 
                         bgcolor: 'action.hover',
                         borderRadius: 1, 
                         border: '1px solid',
                         borderColor: 'divider'
                       }}>
                                                   <Typography variant="body2" sx={{ fontFamily: 'serif', fontSize: '0.875rem', lineHeight: 1.6 }}>
                            <Box sx={{ textAlign: 'center', mb: 3 }}>
                              <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 1 }}>
                                GLOBAL FINANCIAL SERVICES, INC.
                              </Typography>
                              <Typography variant="body2" sx={{ color: 'text.secondary', mb: 2 }}>
                                123 Wall Street, New York, NY 10001<br/>
                                Tel: (212) 555-0123 | Fax: (212) 555-0124<br/>
                                www.globalfinancial.com
                              </Typography>
                              <Box sx={{ borderBottom: '2px solid #333', width: '60%', mx: 'auto', mb: 2 }} />
                            </Box>
                            
                            <Box sx={{ textAlign: 'center', mb: 4 }}>
                              <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                                Agreement No: FSA-2024-0015<br/>
                                Effective Date: January 15, 2024
                              </Typography>
                            </Box>
                            
                            <Typography variant="body2" sx={{ mb: 2 }}>
                              This Financial Services Agreement (the "Agreement") is entered into as of January 15, 2024 (the "Effective Date") by and between:
                            </Typography>
                            
                            <Box sx={{ pl: 3, mb: 3 }}>
                              <Typography variant="body2" sx={{ mb: 1 }}>
                                <strong>Global Financial Services, Inc.</strong>, a Delaware corporation with its principal place of business at 123 Wall Street, New York, NY 10001 ("Provider")
                              </Typography>
                              <Typography variant="body2">
                                and
                              </Typography>
                              <Typography variant="body2" sx={{ mb: 1 }}>
                                <strong>Global Investment Partners, LLC</strong>, a New York limited liability company with its principal place of business at 456 Park Avenue, New York, NY 10022 ("Client")
                              </Typography>
                            </Box>
                            
                            <Typography variant="body2" sx={{ mb: 2 }}>
                              WHEREAS, Provider offers comprehensive financial advisory and investment management services;
                            </Typography>
                            
                            <Typography variant="body2" sx={{ mb: 2 }}>
                              WHEREAS, Client desires to engage Provider for such services;
                            </Typography>
                            
                            <Typography variant="body2" sx={{ mb: 3 }}>
                              NOW, THEREFORE, in consideration of the mutual promises and covenants contained herein, the parties agree as follows:
                            </Typography>
                            
                            <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
                              1. SERVICES
                            </Typography>
                            <Typography variant="body2" sx={{ pl: 2, mb: 2 }}>
                              Provider shall provide investment advisory services, portfolio management, and financial planning consultation to Client in accordance with the terms and conditions set forth in this Agreement.
                            </Typography>
                            
                            <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
                              2. COMPENSATION
                            </Typography>
                            <Typography variant="body2" sx={{ pl: 2, mb: 2 }}>
                              Client shall pay Provider a monthly fee of $25,000 for services rendered, payable within thirty (30) days of invoice receipt.
                            </Typography>
                            
                            <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
                              3. TERM
                            </Typography>
                            <Typography variant="body2" sx={{ pl: 2, mb: 2 }}>
                              This Agreement shall commence on the Effective Date and continue for a period of three (3) years, unless terminated earlier in accordance with Section 8.
                            </Typography>
                            
                            <Box sx={{ textAlign: 'center', mt: 4, pt: 2, borderTop: '1px solid #ccc' }}>
                              <Typography variant="body2" sx={{ fontSize: '0.8rem', color: 'text.secondary' }}>
                                Page 1 of 12 | FSA-2024-0015
                              </Typography>
                            </Box>
                          </Typography>
                       </Box>
                     </Box>
                   )}
                  
                                     {step.id === 'ner' && (
                     <Box>
                       <Typography variant="body2" sx={{ mb: 2 }}>
                         <strong>Entity Recognition Results:</strong>
                       </Typography>
                       <Box sx={{ pl: 2, mb: 2 }}>
                         <Typography variant="body2">
                           • Total Entities Found: 6
                         </Typography>
                         <Typography variant="body2">
                           • Average Confidence: 94.2%
                         </Typography>
                       </Box>
                       <Typography variant="body2" sx={{ mb: 1 }}>
                         <strong>Identified Entities:</strong>
                       </Typography>
                       <Box sx={{ pl: 2 }}>
                         <Typography variant="body2">
                           • <strong>Organizations:</strong> Global Financial Services, Inc., Global Investment Partners, LLC
                         </Typography>
                         <Typography variant="body2">
                           • <strong>Dates:</strong> January 15, 2024
                         </Typography>
                         <Typography variant="body2">
                           • <strong>Monetary Values:</strong> $25,000
                         </Typography>
                         <Typography variant="body2">
                           • <strong>Contract Terms:</strong> three (3) years, thirty (30) days
                         </Typography>
                       </Box>
                     </Box>
                   )}
                  
                                     {step.id === 'classify' && (
                     <Box>
                       <Typography variant="body2" sx={{ mb: 2 }}>
                         <strong>Document Classification:</strong>
                       </Typography>
                       <Box sx={{ pl: 2, mb: 2 }}>
                         <Typography variant="body2">
                           • <strong>Primary Type:</strong> Financial Agreement (94% confidence)
                         </Typography>
                         <Typography variant="body2">
                           • <strong>Domain:</strong> Financial Services
                         </Typography>
                         <Typography variant="body2">
                           • <strong>Subcategory:</strong> Service Agreement
                         </Typography>
                         <Typography variant="body2">
                           • <strong>Risk Level:</strong> Medium
                         </Typography>
                       </Box>
                       <Typography variant="body2" sx={{ mb: 1 }}>
                         <strong>Key Indicators:</strong>
                       </Typography>
                       <Box sx={{ pl: 2 }}>
                         <Typography variant="body2">
                           • Contains financial terms and compensation clauses
                         </Typography>
                         <Typography variant="body2">
                           • Includes regulatory compliance references
                         </Typography>
                         <Typography variant="body2">
                           • Structured as a formal business agreement
                         </Typography>
                       </Box>
                     </Box>
                   )}
                  
                                     {step.id === 'risk' && (
                     <Box>
                       <Typography variant="body2" sx={{ mb: 2 }}>
                         <strong>Risk Assessment Analysis:</strong>
                       </Typography>
                       <Box sx={{ pl: 2, mb: 2 }}>
                         <Typography variant="body2">
                           • <strong>Overall Risk Score:</strong> 6.5/10 (Medium)
                         </Typography>
                         <Typography variant="body2">
                           • <strong>Compliance Score:</strong> 87%
                         </Typography>
                         <Typography variant="body2">
                           • <strong>Regulatory Framework:</strong> SEC Regulations
                         </Typography>
                       </Box>
                       <Typography variant="body2" sx={{ mb: 1 }}>
                         <strong>Identified Risk Factors:</strong>
                       </Typography>
                       <Box sx={{ pl: 2 }}>
                         <Typography variant="body2">
                           • High-value financial transaction ($25,000 monthly)
                         </Typography>
                         <Typography variant="body2">
                           • Investment advisory services mentioned
                         </Typography>
                         <Typography variant="body2">
                           • Requires SEC compliance monitoring
                         </Typography>
                         <Typography variant="body2">
                           • Data protection requirements identified
                         </Typography>
                       </Box>
                     </Box>
                   )}
                  
                                     {step.id === 'index' && (
                     <Box>
                       <Typography variant="body2" sx={{ mb: 2 }}>
                         <strong>Document Indexing Results:</strong>
                       </Typography>
                       <Box sx={{ pl: 2, mb: 2 }}>
                         <Typography variant="body2">
                           • <strong>Vector Embeddings:</strong> Generated (1,536 dimensions)
                         </Typography>
                         <Typography variant="body2">
                           • <strong>Search Index:</strong> Created and optimized
                         </Typography>
                         <Typography variant="body2">
                           • <strong>Metadata Tags:</strong> 12 tags applied
                         </Typography>
                         <Typography variant="body2">
                           • <strong>Storage Location:</strong> Document Repository
                         </Typography>
                       </Box>
                       <Typography variant="body2" sx={{ mb: 1 }}>
                         <strong>Applied Tags:</strong>
                       </Typography>
                       <Box sx={{ pl: 2 }}>
                         <Typography variant="body2">
                           • financial-agreement, service-contract, sec-regulated, high-value, compliance-required, data-protection, investment-services, monthly-billing, confidentiality, termination-clause, liability-limitation, new-york-law
                         </Typography>
                       </Box>
                     </Box>
                   )}
                  
                                     <Box sx={{ mt: 3, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
                     <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                       Processing completed at {new Date().toLocaleTimeString()}
                     </Typography>
                   </Box>
                </Paper>
              </Collapse>
            </motion.div>
          ))}
        </List>

        {/* Overall Progress */}
        {isProcessing && (
          <Box mt={2}>
            <Typography variant="subtitle2" gutterBottom>
              Overall Progress
            </Typography>
            <LinearProgress
              variant="determinate"
              value={(pipelineSteps.filter(s => s.status === 'completed').length / pipelineSteps.length) * 100}
              sx={{ height: 8, borderRadius: 4 }}
            />
            <Typography variant="caption" color="text.secondary">
              {pipelineSteps.filter(s => s.status === 'completed').length} of {pipelineSteps.length} steps completed
            </Typography>
          </Box>
        )}

                 {/* Current Step Info */}
         {currentStep && (
           <Box 
             mt={2} 
             p={3} 
             sx={{
               backgroundColor: 'background.paper',
               borderRadius: 2,
               border: '1px solid',
               borderColor: 'divider',
               boxShadow: 1
             }}
           >
                           <Typography 
                variant="h6" 
                sx={{ 
                  fontWeight: 600, 
                  mb: 1,
                  background: 'linear-gradient(90deg, #3b82f6 0%, #10b981 25%, #f59e0b 50%, #10b981 75%, #3b82f6 100%)',
                  backgroundSize: '200% 100%',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  animation: 'gradientShift 3s ease-in-out infinite',
                  '@keyframes gradientShift': {
                    '0%': {
                      backgroundPosition: '0% 50%'
                    },
                    '50%': {
                      backgroundPosition: '100% 50%'
                    },
                    '100%': {
                      backgroundPosition: '0% 50%'
                    }
                  }
                }}
              >
                Currently Processing: {pipelineSteps.find(s => s.id === currentStep)?.name}
              </Typography>
             <Typography variant="body1" sx={{ fontSize: '1.1rem' }}>
               {currentStep === 'upload' && 'Validating file format and preparing for analysis...'}
               {currentStep === 'ocr' && 'Extracting text content from document images...'}
               {currentStep === 'ner' && 'Identifying key entities and data points...'}
               {currentStep === 'classify' && 'Determining document type and category...'}
               {currentStep === 'risk' && 'Analyzing compliance requirements and potential issues...'}
               {currentStep === 'index' && 'Creating searchable index and metadata...'}
             </Typography>
           </Box>
         )}
      </CardContent>
    </Card>
  );
};

export default DocumentProcessingPipeline;
