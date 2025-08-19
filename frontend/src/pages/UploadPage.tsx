import React, { useState, useCallback, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  LinearProgress,
  Alert,
  Chip,
  Grid,
  Card,
  CardContent,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Description as FileIcon,
  Image as ImageIcon,
  PictureAsPdf as PdfIcon,
  Visibility as ViewIcon,
  Download as DownloadIcon
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { toast } from 'react-hot-toast';
import apiService, { DocumentInfo, UploadResponse } from '../services/apiService';

interface UploadedFile extends UploadResponse {
  id: string;
  progress: number;
  uploadedAt: Date;
}

const UploadPage: React.FC = () => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<DocumentInfo | null>(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);

  // Load existing documents on component mount
  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setIsLoading(true);
      const response = await apiService.getDocuments(1, 100);
      setDocuments(response.data);
    } catch (error) {
      console.error('Failed to load documents:', error);
      toast.error('Failed to load documents');
    } finally {
      setIsLoading(false);
    }
  };

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setIsUploading(true);
    
    for (const file of acceptedFiles) {
      const fileId = Math.random().toString(36).substr(2, 9);
      
      const newFile: UploadedFile = {
        id: fileId,
        fileId: '',
        filename: file.name,
        size: file.size,
        status: 'uploaded',
        progress: 0,
        uploadedAt: new Date()
      };

      setUploadedFiles(prev => [...prev, newFile]);

      try {
        const response = await apiService.uploadDocument(file, (progress) => {
          setUploadedFiles(prev => 
            prev.map(f => 
              f.id === fileId 
                ? { ...f, progress }
                : f
            )
          );
        });

        // Update file with response data
        setUploadedFiles(prev => 
          prev.map(f => 
            f.id === fileId 
              ? { ...f, ...response, progress: 100 }
              : f
          )
        );

        toast.success(`${file.name} uploaded successfully!`);
        
        // Reload documents list
        await loadDocuments();
        
      } catch (error) {
        setUploadedFiles(prev => 
          prev.map(f => 
            f.id === fileId 
              ? { ...f, status: 'error', progress: 0 }
              : f
          )
        );
        toast.error(`Failed to upload ${file.name}`);
      }
    }

    setIsUploading(false);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg']
    },
    maxSize: 50 * 1024 * 1024, // 50MB
    multiple: true
  });

  const removeFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const deleteDocument = async (documentId: string) => {
    try {
      await apiService.deleteDocument(documentId);
      toast.success('Document deleted successfully');
      await loadDocuments();
    } catch (error) {
      toast.error('Failed to delete document');
    }
  };

  const viewDocument = async (documentId: string) => {
    try {
      const document = await apiService.getDocument(documentId);
      setSelectedDocument(document);
      setViewDialogOpen(true);
    } catch (error) {
      toast.error('Failed to load document details');
    }
  };

  const getFileIcon = (type: string) => {
    if (type.includes('pdf')) return <PdfIcon />;
    if (type.includes('image')) return <ImageIcon />;
    return <FileIcon />;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      case 'processing':
        return <LinearProgress />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'processing': return 'primary';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
        AI Document Agent - Upload & Process
      </Typography>

      <Grid container spacing={3}>
        {/* Upload Area */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Paper
                {...getRootProps()}
                sx={{
                  p: 4,
                  textAlign: 'center',
                  border: '2px dashed',
                  borderColor: isDragActive ? 'primary.main' : 'grey.300',
                  backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    borderColor: 'primary.main',
                    backgroundColor: 'action.hover'
                  }
                }}
              >
                <input {...getInputProps()} />
                <UploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  or click to select files
                </Typography>
                <Button variant="contained" sx={{ mt: 2 }}>
                  Select Files
                </Button>
                <Box sx={{ mt: 2 }}>
                  <Chip label="PDF" size="small" sx={{ mr: 1 }} />
                  <Chip label="DOCX" size="small" sx={{ mr: 1 }} />
                  <Chip label="TXT" size="small" sx={{ mr: 1 }} />
                  <Chip label="Images" size="small" />
                </Box>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                  Max file size: 50MB
                </Typography>
              </Paper>
            </CardContent>
          </Card>
        </Grid>

        {/* Upload Stats */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Upload Statistics
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Total Documents: {documents.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Completed: {documents.filter(d => d.status === 'completed').length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Processing: {documents.filter(d => d.status === 'processing').length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Failed: {documents.filter(d => d.status === 'error').length}
                </Typography>
              </Box>
              {isUploading && (
                <Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Uploading...
                  </Typography>
                  <LinearProgress />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Uploads */}
        {uploadedFiles.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Uploads
                </Typography>
                <List>
                  {uploadedFiles.map((file, index) => (
                    <React.Fragment key={file.id}>
                      <ListItem>
                        <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
                          {getFileIcon(file.filename)}
                        </Box>
                        <ListItemText
                          primary={file.filename}
                          secondary={
                            <Box>
                              <Typography variant="body2" color="text.secondary">
                                {formatFileSize(file.size)} • {file.uploadedAt.toLocaleTimeString()}
                              </Typography>
                              {file.status === 'uploaded' && file.progress < 100 && (
                                <LinearProgress 
                                  variant="determinate" 
                                  value={file.progress} 
                                  sx={{ mt: 1, width: 200 }}
                                />
                              )}
                            </Box>
                          }
                        />
                        <ListItemSecondaryAction>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {getStatusIcon(file.status)}
                            <IconButton 
                              edge="end" 
                              onClick={() => removeFile(file.id)}
                              disabled={file.status === 'uploaded' && file.progress < 100}
                            >
                              <DeleteIcon />
                            </IconButton>
                          </Box>
                        </ListItemSecondaryAction>
                      </ListItem>
                      {index < uploadedFiles.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Document Library */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Document Library
                </Typography>
                <Button
                  variant="outlined"
                  onClick={loadDocuments}
                  disabled={isLoading}
                >
                  Refresh
                </Button>
              </Box>
              
              {isLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                  <LinearProgress sx={{ width: '100%' }} />
                </Box>
              ) : documents.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body1" color="text.secondary">
                    No documents uploaded yet
                  </Typography>
                </Box>
              ) : (
                <List>
                  {documents.map((doc, index) => (
                    <React.Fragment key={doc.id}>
                      <ListItem>
                        <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
                          {getFileIcon(doc.filename)}
                        </Box>
                        <ListItemText
                          primary={doc.filename}
                          secondary={
                            <Box>
                              <Typography variant="body2" color="text.secondary">
                                {formatFileSize(doc.size)} • {new Date(doc.uploadedAt).toLocaleString()}
                              </Typography>
                              <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                                <Chip
                                  label={doc.status}
                                  color={getStatusColor(doc.status)}
                                  size="small"
                                />
                                {doc.confidence && (
                                  <Chip
                                    label={`${(doc.confidence * 100).toFixed(1)}% Confidence`}
                                    size="small"
                                    variant="outlined"
                                  />
                                )}
                              </Box>
                            </Box>
                          }
                        />
                        <ListItemSecondaryAction>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <IconButton
                              size="small"
                              onClick={() => viewDocument(doc.id)}
                              title="View Details"
                            >
                              <ViewIcon />
                            </IconButton>
                            <IconButton
                              size="small"
                              onClick={() => deleteDocument(doc.id)}
                              title="Delete Document"
                            >
                              <DeleteIcon />
                            </IconButton>
                          </Box>
                        </ListItemSecondaryAction>
                      </ListItem>
                      {index < documents.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Document Details Dialog */}
      <Dialog
        open={viewDialogOpen}
        onClose={() => setViewDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Document Details
          {selectedDocument && (
            <Typography variant="subtitle2" color="text.secondary">
              {selectedDocument.filename}
            </Typography>
          )}
        </DialogTitle>
        <DialogContent>
          {selectedDocument && (
            <Box>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Basic Information
                  </Typography>
                  <List dense>
                    <ListItem>
                      <ListItemText
                        primary="File Size"
                        secondary={formatFileSize(selectedDocument.size)}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="File Type"
                        secondary={selectedDocument.type}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Upload Date"
                        secondary={new Date(selectedDocument.uploadedAt).toLocaleString()}
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Status"
                        secondary={
                          <Chip
                            label={selectedDocument.status}
                            color={getStatusColor(selectedDocument.status)}
                            size="small"
                          />
                        }
                      />
                    </ListItem>
                  </List>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Processing Results
                  </Typography>
                  {selectedDocument.confidence && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" gutterBottom>
                        Confidence Score: {(selectedDocument.confidence * 100).toFixed(1)}%
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={selectedDocument.confidence * 100}
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                    </Box>
                  )}
                  {selectedDocument.entities && selectedDocument.entities.length > 0 && (
                    <Box>
                      <Typography variant="body2" gutterBottom>
                        Extracted Entities:
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        {selectedDocument.entities.slice(0, 5).map((entity: any, index: number) => (
                          <Chip
                            key={index}
                            label={`${entity.type}: ${entity.value}`}
                            size="small"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    </Box>
                  )}
                </Grid>
                {selectedDocument.extractedText && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom>
                      Extracted Text (Preview)
                    </Typography>
                    <Paper sx={{ p: 2, bgcolor: 'grey.50', maxHeight: 200, overflow: 'auto' }}>
                      <Typography variant="body2">
                        {selectedDocument.extractedText.substring(0, 500)}
                        {selectedDocument.extractedText.length > 500 && '...'}
                      </Typography>
                    </Paper>
                  </Grid>
                )}
              </Grid>
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

export default UploadPage;
