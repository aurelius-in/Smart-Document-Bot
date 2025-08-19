import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Paper,
  Divider,
  Avatar,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tooltip,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Badge,
  Menu,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  InputAdornment
} from '@mui/material';
import {
  Send,
  Search,
  Help,
  Bookmark,
  BookmarkBorder,
  Share,
  Download,
  MoreVert,
  ExpandMore,
  ExpandLess,
  Person,
  SmartToy,
  Link,
  ContentCopy,
  Refresh,
  Settings,
  History,
  TrendingUp,
  Psychology,
  Build,
  Assessment
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

interface Citation {
  id: string;
  documentId: string;
  documentName: string;
  page: number;
  text: string;
  confidence: number;
  entityType?: string;
  start: number;
  end: number;
}

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  citations?: Citation[];
  confidence?: number;
  agentUsed?: string;
  processingTime?: number;
  isTyping?: boolean;
}

interface QAChatProps {
  documentId: string;
  documentName: string;
  onCitationClick?: (citation: Citation) => void;
  onExport?: () => void;
  onShare?: () => void;
}

const QAChat: React.FC<QAChatProps> = ({
  documentId,
  documentName,
  onCitationClick,
  onExport,
  onShare
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState<string>('');
  const [showSampleQuestions, setShowSampleQuestions] = useState(true);
  const [chatHistory, setChatHistory] = useState<Message[]>([]);
  const [bookmarkedMessages, setBookmarkedMessages] = useState<Set<string>>(new Set());
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedAgent, setSelectedAgent] = useState<string>('qa');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const sampleQuestions = [
    "What are the key risk factors mentioned in this document?",
    "Who are the main parties involved in this agreement?",
    "What are the compliance requirements?",
    "What are the financial terms and conditions?",
    "What are the termination clauses?",
    "What are the data protection requirements?",
    "What are the liability limitations?",
    "What are the dispute resolution procedures?"
  ];

  const agentOptions = [
    { value: 'qa', label: 'Q&A Agent', icon: <Help /> },
    { value: 'classifier', label: 'Classifier Agent', icon: <Psychology /> },
    { value: 'entity', label: 'Entity Agent', icon: <Build /> },
    { value: 'risk', label: 'Risk Agent', icon: <Assessment /> }
  ];

  // Mock initial messages
  useEffect(() => {
    const initialMessages: Message[] = [
      {
        id: '1',
        type: 'assistant',
        content: `Hello! I'm your AI Document Agent for "${documentName}". I can help you understand this document by answering questions about its content, identifying key entities, assessing risks, and more. What would you like to know?`,
        timestamp: new Date(),
        agentUsed: 'qa',
        confidence: 0.95
      }
    ];
    setMessages(initialMessages);
    setChatHistory(initialMessages);
  }, [documentName]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setChatHistory(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const mockCitations: Citation[] = [
        {
          id: '1',
          documentId,
          documentName,
          page: 1,
          text: 'The agreement shall commence on the Effective Date and continue for a period of three (3) years unless terminated earlier in accordance with the terms herein.',
          confidence: 0.92,
          entityType: 'DATE',
          start: 150,
          end: 200
        },
        {
          id: '2',
          documentId,
          documentName,
          page: 2,
          text: 'Either party may terminate this agreement with thirty (30) days written notice to the other party.',
          confidence: 0.88,
          entityType: 'CONTRACT_TERM',
          start: 300,
          end: 350
        }
      ];

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `Based on my analysis of the document, I found several key points related to your question. The agreement has specific terms regarding duration and termination procedures. Here are the relevant details with citations from the document.`,
        timestamp: new Date(),
        citations: mockCitations,
        confidence: 0.89,
        agentUsed: selectedAgent,
        processingTime: 2.3
      };

      setMessages(prev => [...prev, assistantMessage]);
      setChatHistory(prev => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 2000);
  };

  const handleSampleQuestionClick = (question: string) => {
    setInputValue(question);
    setSelectedQuestion(question);
    setShowSampleQuestions(false);
  };

  const handleCitationClick = (citation: Citation) => {
    onCitationClick?.(citation);
  };

  const handleBookmarkToggle = (messageId: string) => {
    const newBookmarks = new Set(bookmarkedMessages);
    if (newBookmarks.has(messageId)) {
      newBookmarks.delete(messageId);
    } else {
      newBookmarks.add(messageId);
    }
    setBookmarkedMessages(newBookmarks);
  };

  const handleCopyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  const renderMessage = (message: Message) => (
    <motion.div
      key={message.id}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Box
        display="flex"
        justifyContent={message.type === 'user' ? 'flex-end' : 'flex-start'}
        mb={2}
      >
        <Box
          maxWidth="70%"
          sx={{
            display: 'flex',
            flexDirection: message.type === 'user' ? 'row-reverse' : 'row',
            alignItems: 'flex-start',
            gap: 1
          }}
        >
          <Avatar
            sx={{
              bgcolor: message.type === 'user' ? 'primary.main' : 'secondary.main',
              width: 32,
              height: 32
            }}
          >
            {message.type === 'user' ? <Person /> : <SmartToy />}
          </Avatar>
          
          <Paper
            elevation={1}
            sx={{
              p: 2,
              backgroundColor: message.type === 'user' ? 'primary.light' : 'background.paper',
              color: message.type === 'user' ? 'primary.contrastText' : 'text.primary',
              borderRadius: 2,
              position: 'relative'
            }}
          >
            <Typography variant="body1" gutterBottom>
              {message.content}
            </Typography>

            {/* Citations */}
            {message.citations && message.citations.length > 0 && (
              <Box mt={2}>
                <Typography variant="caption" color="text.secondary" gutterBottom>
                  Sources:
                </Typography>
                <Box display="flex" flexWrap="wrap" gap={1}>
                  {message.citations.map((citation) => (
                    <Chip
                      key={citation.id}
                      label={`Page ${citation.page} - ${Math.round(citation.confidence * 100)}%`}
                      size="small"
                      variant="outlined"
                      icon={<Link />}
                      onClick={() => handleCitationClick(citation)}
                      sx={{ cursor: 'pointer' }}
                    />
                  ))}
                </Box>
              </Box>
            )}

            {/* Message metadata */}
            <Box
              display="flex"
              alignItems="center"
              gap={1}
              mt={1}
              sx={{ opacity: 0.7 }}
            >
              <Typography variant="caption">
                {message.timestamp.toLocaleTimeString()}
              </Typography>
              {message.confidence && (
                <Typography variant="caption">
                  Confidence: {Math.round(message.confidence * 100)}%
                </Typography>
              )}
              {message.agentUsed && (
                <Typography variant="caption">
                  Agent: {agentOptions.find(a => a.value === message.agentUsed)?.label}
                </Typography>
              )}
              {message.processingTime && (
                <Typography variant="caption">
                  {message.processingTime}s
                </Typography>
              )}
            </Box>

            {/* Message actions */}
            <Box
              position="absolute"
              top={8}
              right={8}
              sx={{ opacity: 0, transition: 'opacity 0.2s' }}
              className="message-actions"
            >
              <IconButton
                size="small"
                onClick={() => handleBookmarkToggle(message.id)}
              >
                {bookmarkedMessages.has(message.id) ? <Bookmark /> : <BookmarkBorder />}
              </IconButton>
              <IconButton
                size="small"
                onClick={() => handleCopyMessage(message.content)}
              >
                <ContentCopy />
              </IconButton>
              <IconButton
                size="small"
                onClick={(e) => setAnchorEl(e.currentTarget)}
              >
                <MoreVert />
              </IconButton>
            </Box>
          </Paper>
        </Box>
      </Box>
    </motion.div>
  );

  return (
    <Box height="100%" display="flex" flexDirection="column">
      {/* Header */}
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Typography variant="h6" display="flex" alignItems="center">
              <Help sx={{ mr: 1 }} />
              Ask Document AI
            </Typography>
            <Box display="flex" alignItems="center" gap={1}>
              <FormControl size="small" sx={{ minWidth: 150 }}>
                <InputLabel>Agent</InputLabel>
                <Select
                  value={selectedAgent}
                  onChange={(e) => setSelectedAgent(e.target.value)}
                  label="Agent"
                >
                  {agentOptions.map((agent) => (
                    <MenuItem key={agent.value} value={agent.value}>
                      <Box display="flex" alignItems="center" gap={1}>
                        {agent.icon}
                        {agent.label}
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Tooltip title="Export Chat">
                <IconButton onClick={onExport}>
                  <Download />
                </IconButton>
              </Tooltip>
              <Tooltip title="Share">
                <IconButton onClick={onShare}>
                  <Share />
                </IconButton>
              </Tooltip>
              <Tooltip title="Settings">
                <IconButton>
                  <Settings />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Sample Questions */}
      {showSampleQuestions && (
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
              <Typography variant="subtitle1">
                Suggested Questions
              </Typography>
              <IconButton
                size="small"
                onClick={() => setShowSampleQuestions(false)}
              >
                <ExpandLess />
              </IconButton>
            </Box>
            <Box display="flex" flexWrap="wrap" gap={1}>
              {sampleQuestions.map((question, index) => (
                <Chip
                  key={index}
                  label={question}
                  variant="outlined"
                  onClick={() => handleSampleQuestionClick(question)}
                  sx={{ cursor: 'pointer' }}
                />
              ))}
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Messages */}
      <Box
        flex={1}
        overflow="auto"
        sx={{
          '& .message-actions': {
            opacity: 0
          },
          '& .MuiPaper-root:hover .message-actions': {
            opacity: 1
          }
        }}
      >
        <Box p={2}>
          {messages.map(renderMessage)}
          
          {/* Loading indicator */}
          {isLoading && (
            <Box display="flex" justifyContent="flex-start" mb={2}>
              <Box display="flex" alignItems="center" gap={1}>
                <Avatar sx={{ bgcolor: 'secondary.main', width: 32, height: 32 }}>
                  <SmartToy />
                </Avatar>
                <Paper elevation={1} sx={{ p: 2, borderRadius: 2 }}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <CircularProgress size={16} />
                    <Typography variant="body2">
                      Analyzing document...
                    </Typography>
                  </Box>
                </Paper>
              </Box>
            </Box>
          )}
          
          <div ref={messagesEndRef} />
        </Box>
      </Box>

      {/* Input */}
      <Card>
        <CardContent>
          <Box display="flex" gap={1}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              placeholder="Ask a question about the document..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <Tooltip title="Send">
                      <IconButton
                        onClick={handleSendMessage}
                        disabled={!inputValue.trim() || isLoading}
                      >
                        <Send />
                      </IconButton>
                    </Tooltip>
                  </InputAdornment>
                )
              }}
            />
          </Box>
        </CardContent>
      </Card>

      {/* Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={() => setAnchorEl(null)}
      >
        <MenuItem onClick={() => setAnchorEl(null)}>
          <ContentCopy sx={{ mr: 1 }} />
          Copy
        </MenuItem>
        <MenuItem onClick={() => setAnchorEl(null)}>
          <Bookmark sx={{ mr: 1 }} />
          Bookmark
        </MenuItem>
        <MenuItem onClick={() => setAnchorEl(null)}>
          <Share sx={{ mr: 1 }} />
          Share
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default QAChat;
