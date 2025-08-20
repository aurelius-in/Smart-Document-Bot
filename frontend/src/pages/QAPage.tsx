import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  TextField, 
  Button, 
  List, 
  ListItem, 
  ListItemText, 
  Avatar, 
  Chip,
  CircularProgress,
  Alert,
  IconButton,
  Divider
} from '@mui/material';
import { 
  Chat as ChatIcon, 
  Send as SendIcon,
  Person as PersonIcon,
  SmartToy as BotIcon,
  Refresh as RefreshIcon,
  Clear as ClearIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useTheme } from '../contexts/ThemeContext';
import { toast } from 'react-hot-toast';
import apiService from '../services/apiService';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  isLoading?: boolean;
}

const QAPage: React.FC = () => {
  const { darkMode } = useTheme();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hello! I'm aiDa, your AI document assistant. I can help you analyze documents, answer questions, and provide insights. What would you like to know?",
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      sender: 'user',
      timestamp: new Date()
    };

    const botMessage: Message = {
      id: (Date.now() + 1).toString(),
      text: '',
      sender: 'bot',
      timestamp: new Date(),
      isLoading: true
    };

    setMessages(prev => [...prev, userMessage, botMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      // Call the QA API
      const response = await apiService.askQuestion('', inputText);

      // Update the bot message with the response
      setMessages(prev => prev.map(msg => 
        msg.id === botMessage.id 
          ? { ...msg, text: response.answer || 'I apologize, but I couldn\'t generate a response at this time.', isLoading: false }
          : msg
      ));

      toast.success('Response generated successfully!');
    } catch (error) {
      console.error('Error getting response:', error);
      
      // Update the bot message with error
      setMessages(prev => prev.map(msg => 
        msg.id === botMessage.id 
          ? { ...msg, text: 'I apologize, but I encountered an error while processing your question. Please try again.', isLoading: false }
          : msg
      ));

      toast.error('Failed to get response from AI');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: '1',
        text: "Hello! I'm aiDa, your AI document assistant. I can help you analyze documents, answer questions, and provide insights. What would you like to know?",
        sender: 'bot',
        timestamp: new Date()
      }
    ]);
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
            <ChatIcon sx={{ 
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
              aiDa Chat
            </Typography>
            <Typography variant="h6" sx={{ 
              opacity: 0.95,
              background: 'linear-gradient(135deg, #cbd5e1 0%, #94a3b8 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              Intelligent Q&A system for document analysis and insights
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Chat Interface */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Paper sx={{ 
          height: '70vh',
          display: 'flex',
          flexDirection: 'column',
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
          position: 'relative',
          overflow: 'hidden'
        }}>
          {/* Chat Header */}
          <Box sx={{ 
            p: 2, 
            borderBottom: darkMode ? '1px solid rgba(138, 43, 226, 0.3)' : '1px solid rgba(138, 43, 226, 0.1)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <Typography variant="h6" sx={{ 
              color: darkMode ? 'white' : 'inherit',
              fontWeight: 600
            }}>
              Document Analysis Chat
            </Typography>
            <Box>
              <IconButton onClick={clearChat} size="small" sx={{ color: darkMode ? 'white' : 'inherit' }}>
                <ClearIcon />
              </IconButton>
            </Box>
          </Box>

          {/* Messages Area */}
          <Box sx={{ 
            flex: 1, 
            overflow: 'auto', 
            p: 2,
            display: 'flex',
            flexDirection: 'column',
            gap: 2
          }}>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <Box sx={{ 
                  display: 'flex', 
                  justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                  mb: 2
                }}>
                  <Box sx={{ 
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: 1,
                    maxWidth: '70%'
                  }}>
                    {message.sender === 'bot' && (
                      <Avatar sx={{ 
                        bgcolor: 'primary.main',
                        width: 32,
                        height: 32
                      }}>
                        <BotIcon />
                      </Avatar>
                    )}
                    
                    <Paper sx={{ 
                      p: 2,
                      borderRadius: 2,
                      background: message.sender === 'user' 
                        ? darkMode 
                          ? 'linear-gradient(135deg, #8a2be2 0%, #4c1d95 100%)'
                          : 'linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%)'
                        : darkMode 
                          ? 'linear-gradient(135deg, #2d1b69 0%, #1a1a3a 100%)'
                          : 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
                      border: darkMode 
                        ? '1px solid rgba(138, 43, 226, 0.3)'
                        : '1px solid rgba(138, 43, 226, 0.1)',
                      position: 'relative'
                    }}>
                      {message.isLoading ? (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <CircularProgress size={16} />
                          <Typography variant="body2" sx={{ 
                            color: darkMode ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.6)'
                          }}>
                            Thinking...
                          </Typography>
                        </Box>
                      ) : (
                        <Typography variant="body1" sx={{ 
                          color: darkMode ? 'white' : 'inherit',
                          whiteSpace: 'pre-wrap'
                        }}>
                          {message.text}
                        </Typography>
                      )}
                    </Paper>

                    {message.sender === 'user' && (
                      <Avatar sx={{ 
                        bgcolor: 'secondary.main',
                        width: 32,
                        height: 32
                      }}>
                        <PersonIcon />
                      </Avatar>
                    )}
                  </Box>
                </Box>
              </motion.div>
            ))}
            <div ref={messagesEndRef} />
          </Box>

          {/* Input Area */}
          <Box sx={{ 
            p: 2, 
            borderTop: darkMode ? '1px solid rgba(138, 43, 226, 0.3)' : '1px solid rgba(138, 43, 226, 0.1)',
            display: 'flex',
            gap: 1
          }}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about your documents..."
              variant="outlined"
              size="small"
              disabled={isLoading}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 2,
                  background: darkMode ? 'rgba(255, 255, 255, 0.05)' : 'white',
                  '& fieldset': {
                    borderColor: darkMode ? 'rgba(138, 43, 226, 0.3)' : 'rgba(138, 43, 226, 0.2)'
                  },
                  '&:hover fieldset': {
                    borderColor: darkMode ? 'rgba(138, 43, 226, 0.5)' : 'rgba(138, 43, 226, 0.4)'
                  }
                }
              }}
            />
            <Button
              variant="contained"
              onClick={handleSendMessage}
              disabled={!inputText.trim() || isLoading}
              sx={{
                borderRadius: 2,
                minWidth: 'auto',
                px: 2,
                background: 'linear-gradient(135deg, #8a2be2 0%, #4c1d95 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%)'
                }
              }}
            >
              <SendIcon />
            </Button>
          </Box>
        </Paper>
      </motion.div>
    </Box>
  );
};

export default QAPage;
