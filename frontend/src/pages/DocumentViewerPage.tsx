import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid, 
  Card, 
  CardContent, 
  CardActions,
  Button,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  CircularProgress,
  Alert,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import { 
  Visibility as VisibilityIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Description as DocumentIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Sort as SortIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useTheme } from '../contexts/ThemeContext';
import { toast } from 'react-hot-toast';
import apiService, { DocumentInfo } from '../services/apiService';

const DocumentViewerPage: React.FC = () => {
  const { darkMode } = useTheme();
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<DocumentInfo | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [sortBy, setSortBy] = useState('uploadedAt');
  const [viewDialogOpen, setViewDialogOpen] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setIsLoading(true);
      const response = await apiService.getDocuments(1, 100);
      setDocuments(response.data || []);
    } catch (error) {
      console.error('Failed to load documents:', error);
      toast.error('Failed to load documents');
    } finally {
      setIsLoading(false);
    }
  };

  const handleViewDocument = async (documentId: string) => {
    try {
      const document = await apiService.getDocument(documentId);
      setSelectedDocument(document);
      setViewDialogOpen(true);
    } catch (error) {
      console.error('Failed to load document details:', error);
      toast.error('Failed to load document details');
    }
  };

  const handleDeleteDocument = async (documentId: string) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      try {
        await apiService.deleteDocument(documentId);
        setDocuments(prev => prev.filter(doc => doc.id !== documentId));
        toast.success('Document deleted successfully');
      } catch (error) {
        console.error('Failed to delete document:', error);
        toast.error('Failed to delete document');
      }
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'processed':
        return <SuccessIcon color="success" />;
      case 'processing':
        return <CircularProgress size={20} />;
      case 'error':
        return <ErrorIcon color="error" />;
      default:
        return <InfoIcon />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processed':
        return 'success';
      case 'processing':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const filteredDocuments = documents
    .filter(doc => 
      doc.filename.toLowerCase().includes(searchTerm.toLowerCase()) &&
      (filterType === 'all' || doc.type === filterType)
    )
    .sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.filename.localeCompare(b.filename);
        case 'size':
          return b.size - a.size;
        case 'uploadedAt':
          return new Date(b.uploadedAt).getTime() - new Date(a.uploadedAt).getTime();
        default:
          return 0;
      }
    });

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
            <VisibilityIcon sx={{ 
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
              Document Viewer
            </Typography>
            <Typography variant="h6" sx={{ 
              opacity: 0.95,
              background: 'linear-gradient(135deg, #cbd5e1 0%, #94a3b8 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              View and analyze processed documents with intelligent insights
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Controls */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Paper sx={{ 
          p: 3, 
          mb: 3,
          borderRadius: 3,
          background: darkMode 
            ? 'linear-gradient(135deg, #1a1a3a 0%, #2d1b69 50%, #1a1a3a 100%)'
            : 'linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #e2e8f0 100%)',
          boxShadow: darkMode 
            ? '0 8px 32px rgba(0, 0, 0, 0.3), 0 2px 8px rgba(0, 0, 0, 0.2)'
            : '0 8px 32px rgba(0, 0, 0, 0.1), 0 2px 8px rgba(0, 0, 0, 0.05)',
          border: darkMode 
            ? '1px solid rgba(138, 43, 226, 0.3)'
            : '1px solid rgba(138, 43, 226, 0.1)'
        }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Search documents..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                    background: darkMode ? 'rgba(255, 255, 255, 0.05)' : 'white'
                  }
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Filter by Type</InputLabel>
                <Select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  sx={{
                    borderRadius: 2,
                    background: darkMode ? 'rgba(255, 255, 255, 0.05)' : 'white'
                  }}
                >
                  <MenuItem value="all">All Types</MenuItem>
                  <MenuItem value="pdf">PDF</MenuItem>
                  <MenuItem value="docx">DOCX</MenuItem>
                  <MenuItem value="txt">TXT</MenuItem>
                  <MenuItem value="csv">CSV</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Sort by</InputLabel>
                <Select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  sx={{
                    borderRadius: 2,
                    background: darkMode ? 'rgba(255, 255, 255, 0.05)' : 'white'
                  }}
                >
                  <MenuItem value="uploadedAt">Upload Date</MenuItem>
                  <MenuItem value="name">Name</MenuItem>
                  <MenuItem value="size">Size</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="contained"
                onClick={loadDocuments}
                disabled={isLoading}
                sx={{
                  borderRadius: 2,
                  background: 'linear-gradient(135deg, #8a2be2 0%, #4c1d95 100%)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%)'
                  }
                }}
              >
                Refresh
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {/* Documents Grid */}
        {isLoading ? (
          <Box display="flex" justifyContent="center" p={4}>
            <CircularProgress />
          </Box>
        ) : filteredDocuments.length === 0 ? (
          <Paper sx={{ 
            p: 4, 
            textAlign: 'center',
            borderRadius: 3,
            background: darkMode 
              ? 'linear-gradient(135deg, #1a1a3a 0%, #2d1b69 50%, #1a1a3a 100%)'
              : 'linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #e2e8f0 100%)',
            boxShadow: darkMode 
              ? '0 8px 32px rgba(0, 0, 0, 0.3), 0 2px 8px rgba(0, 0, 0, 0.2)'
              : '0 8px 32px rgba(0, 0, 0, 0.1), 0 2px 8px rgba(0, 0, 0, 0.05)',
            border: darkMode 
              ? '1px solid rgba(138, 43, 226, 0.3)'
              : '1px solid rgba(138, 43, 226, 0.1)'
          }}>
            <Typography variant="h6" sx={{ 
              color: darkMode ? 'rgba(255, 255, 255, 0.8)' : 'rgba(0, 0, 0, 0.6)',
              mb: 2
            }}>
              No documents found
            </Typography>
            <Typography variant="body2" sx={{ 
              color: darkMode ? 'rgba(255, 255, 255, 0.6)' : 'rgba(0, 0, 0, 0.5)'
            }}>
              Upload some documents to get started
            </Typography>
          </Paper>
        ) : (
          <Grid container spacing={3}>
            {filteredDocuments.map((document) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={document.id}>
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.3 }}
                >
                  <Card sx={{ 
                    height: '100%',
                    borderRadius: 3,
                    background: darkMode 
                      ? 'linear-gradient(135deg, #1a1a3a 0%, #2d1b69 50%, #1a1a3a 100%)'
                      : 'linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #e2e8f0 100%)',
                    boxShadow: darkMode 
                      ? '0 8px 32px rgba(0, 0, 0, 0.3), 0 2px 8px rgba(0, 0, 0, 0.2)'
                      : '0 8px 32px rgba(0, 0, 0, 0.1), 0 2px 8px rgba(0, 0, 0, 0.05)',
                    border: darkMode 
                      ? '1px solid rgba(138, 43, 226, 0.3)'
                      : '1px solid rgba(138, 43, 226, 0.1)',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: darkMode 
                        ? '0 12px 40px rgba(0, 0, 0, 0.4), 0 4px 12px rgba(0, 0, 0, 0.3)'
                        : '0 12px 40px rgba(0, 0, 0, 0.15), 0 4px 12px rgba(0, 0, 0, 0.1)',
                      transition: 'all 0.3s ease'
                    }
                  }}>
                    <CardContent sx={{ p: 2 }}>
                      <Box display="flex" alignItems="center" gap={1} mb={2}>
                        <DocumentIcon sx={{ color: 'primary.main' }} />
                                                 <Typography variant="h6" noWrap sx={{ 
                           color: darkMode ? 'white' : 'inherit',
                           fontWeight: 600
                         }}>
                           {document.filename}
                         </Typography>
                      </Box>
                      
                      <Box display="flex" alignItems="center" gap={1} mb={1}>
                        <Chip 
                          label={document.type.toUpperCase()} 
                          size="small" 
                          color="primary" 
                          variant="outlined"
                        />
                        <Chip 
                          label={formatFileSize(document.size)} 
                          size="small" 
                          color="secondary" 
                          variant="outlined"
                        />
                      </Box>

                      <Box display="flex" alignItems="center" gap={1} mb={2}>
                        {getStatusIcon(document.status)}
                        <Chip 
                          label={document.status} 
                          size="small" 
                          color={getStatusColor(document.status) as any}
                        />
                      </Box>

                      <Typography variant="caption" sx={{ 
                        color: darkMode ? 'rgba(255, 255, 255, 0.6)' : 'rgba(0, 0, 0, 0.6)'
                      }}>
                        Uploaded: {new Date(document.uploadedAt).toLocaleDateString()}
                      </Typography>

                      
                    </CardContent>

                    <CardActions sx={{ p: 2, pt: 0 }}>
                      <Button
                        size="small"
                        startIcon={<VisibilityIcon />}
                        onClick={() => handleViewDocument(document.id)}
                        sx={{ 
                          borderRadius: 2,
                          background: 'linear-gradient(135deg, #8a2be2 0%, #4c1d95 100%)',
                          color: 'white',
                          '&:hover': {
                            background: 'linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%)'
                          }
                        }}
                      >
                        View
                      </Button>
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteDocument(document.id)}
                        sx={{ color: 'error.main' }}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </CardActions>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        )}
      </motion.div>

      {/* Document Detail Dialog */}
      <Dialog
        open={viewDialogOpen}
        onClose={() => setViewDialogOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 3,
            background: darkMode 
              ? 'linear-gradient(135deg, #1a1a3a 0%, #2d1b69 50%, #1a1a3a 100%)'
              : 'linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #e2e8f0 100%)',
            boxShadow: darkMode 
              ? '0 8px 32px rgba(0, 0, 0, 0.3), 0 2px 8px rgba(0, 0, 0, 0.2)'
              : '0 8px 32px rgba(0, 0, 0, 0.1), 0 2px 8px rgba(0, 0, 0, 0.05)',
            border: darkMode 
              ? '1px solid rgba(138, 43, 226, 0.3)'
              : '1px solid rgba(138, 43, 226, 0.1)'
          }
        }}
      >
        <DialogTitle sx={{ 
          color: darkMode ? 'white' : 'inherit',
          borderBottom: darkMode ? '1px solid rgba(138, 43, 226, 0.3)' : '1px solid rgba(138, 43, 226, 0.1)'
        }}>
          Document Details
        </DialogTitle>
        <DialogContent sx={{ p: 3 }}>
          {selectedDocument && (
            <Box>
                             <Typography variant="h6" gutterBottom sx={{ color: darkMode ? 'white' : 'inherit' }}>
                 {selectedDocument.filename}
               </Typography>
              
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6}>
                  <Typography variant="body2" sx={{ color: darkMode ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.6)' }}>
                    Type: {selectedDocument.type}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" sx={{ color: darkMode ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.6)' }}>
                    Size: {formatFileSize(selectedDocument.size)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" sx={{ color: darkMode ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.6)' }}>
                    Status: {selectedDocument.status}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" sx={{ color: darkMode ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.6)' }}>
                    Uploaded: {new Date(selectedDocument.uploadedAt).toLocaleString()}
                  </Typography>
                </Grid>
              </Grid>

                             {selectedDocument.extractedText && (
                 <Box sx={{ mb: 3 }}>
                   <Typography variant="h6" gutterBottom sx={{ color: darkMode ? 'white' : 'inherit' }}>
                     Extracted Text
                   </Typography>
                   <Typography variant="body2" sx={{ color: darkMode ? 'rgba(255, 255, 255, 0.8)' : 'rgba(0, 0, 0, 0.8)' }}>
                     {selectedDocument.extractedText.substring(0, 500)}...
                   </Typography>
                 </Box>
               )}

               {selectedDocument.entities && selectedDocument.entities.length > 0 && (
                 <Box sx={{ mb: 3 }}>
                   <Typography variant="h6" gutterBottom sx={{ color: darkMode ? 'white' : 'inherit' }}>
                     Extracted Entities
                   </Typography>
                   <Box display="flex" flexWrap="wrap" gap={1}>
                     {selectedDocument.entities.map((entity: any, index: number) => (
                       <Chip
                         key={index}
                         label={`${entity.type}: ${entity.value}`}
                         size="small"
                         color="primary"
                         variant="outlined"
                       />
                     ))}
                   </Box>
                 </Box>
               )}
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 3, borderTop: darkMode ? '1px solid rgba(138, 43, 226, 0.3)' : '1px solid rgba(138, 43, 226, 0.1)' }}>
          <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DocumentViewerPage;
