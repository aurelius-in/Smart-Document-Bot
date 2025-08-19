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
  MoreVert,
  ExpandMore,
  ExpandLess,
  Person,
  SmartToy,
  Link,
  ContentCopy,
  Refresh,
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
  const [selectedAgents, setSelectedAgents] = useState<Set<string>>(new Set(['qa']));
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
    { value: 'qa', label: 'General Questions', icon: <Help /> },
    { value: 'classifier', label: 'Document Type Analysis', icon: <Psychology /> },
    { value: 'entity', label: 'Entity & Names', icon: <Build /> },
    { value: 'risk', label: 'Risk & Compliance', icon: <Assessment /> }
  ];

  // Mock initial messages
  useEffect(() => {
    const initialMessages: Message[] = [];
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

    // Check for specific healthcare questions
    const isChiefComplaintQuestion = inputValue.toLowerCase().includes('chief complaint') && 
                                   inputValue.toLowerCase().includes('primary symptoms');
    const isRiskFactorsQuestion = inputValue.toLowerCase().includes('risk factors') && 
                                 inputValue.toLowerCase().includes('current medications');

    // Simulate AI response
    setTimeout(() => {
      let assistantMessage: Message;

      if (isChiefComplaintQuestion) {
        // Healthcare-specific response for chief complaint question
        const healthcareCitations: Citation[] = [
          {
            id: '1',
            documentId,
            documentName,
            page: 1,
            text: 'Patient reports sharp chest pain for 3 days, radiating to left arm',
            confidence: 0.94,
            entityType: 'SYMPTOM',
            start: 150,
            end: 200
          },
          {
            id: '2',
            documentId,
            documentName,
            page: 2,
            text: 'SOB with minimal exertion, denies fever or cough',
            confidence: 0.91,
            entityType: 'SYMPTOM',
            start: 300,
            end: 350
          },
          {
            id: '3',
            documentId,
            documentName,
            page: 3,
            text: 'Vital signs: BP 145/95, HR 98, RR 22, O2 sat 94% on RA',
            confidence: 0.96,
            entityType: 'VITAL_SIGNS',
            start: 450,
            end: 500
          }
        ];

        assistantMessage = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: `Based on my analysis of the patient's medical record, I found the following information:

**Chief Complaint:** 
The patient presents with persistent chest pain and shortness of breath for the past 3 days.

**Primary Symptoms:**
- Sharp, stabbing chest pain radiating to left arm
- Shortness of breath, especially with exertion
- Fatigue and general weakness
- Mild nausea without vomiting
- Diaphoresis (excessive sweating)

**Relevant Citations:**
• Page 1: "Patient reports sharp chest pain for 3 days, radiating to left arm"
• Page 2: "SOB with minimal exertion, denies fever or cough"
• Page 3: "Vital signs: BP 145/95, HR 98, RR 22, O2 sat 94% on RA"

**Confidence Level:** 94%
**Processing Time:** 1.8 seconds`,
          timestamp: new Date(),
          citations: healthcareCitations,
          confidence: 0.94,
          agentUsed: selectedAgent,
                     processingTime: 1.8
         };
       } else if (isRiskFactorsQuestion) {
         // Healthcare-specific response for risk factors and medications question
         const riskFactorsCitations: Citation[] = [
           {
             id: '1',
             documentId,
             documentName,
             page: 4,
             text: 'PMH: HTN, DM2, hyperlipidemia',
             confidence: 0.91,
             entityType: 'MEDICAL_HISTORY',
             start: 150,
             end: 200
           },
           {
             id: '2',
             documentId,
             documentName,
             page: 5,
             text: 'Current meds: Metformin, Lisinopril, Atorvastatin, ASA',
             confidence: 0.89,
             entityType: 'MEDICATION',
             start: 300,
             end: 350
           },
           {
             id: '3',
             documentId,
             documentName,
             page: 6,
             text: 'Allergies: PCN, Sulfa',
             confidence: 0.93,
             entityType: 'ALLERGY',
             start: 450,
             end: 500
           }
         ];

         assistantMessage = {
           id: (Date.now() + 1).toString(),
           type: 'assistant',
           content: `Based on my analysis of the patient's medical record, here are the identified risk factors and current medications:

**Risk Factors:**
- Hypertension (diagnosed 2019)
- Type 2 Diabetes Mellitus (diagnosed 2020)
- Family history of coronary artery disease
- Current smoker (20 pack-years)
- Sedentary lifestyle
- BMI: 32.4 (obese)

**Current Medications:**
- Metformin 500mg twice daily (for diabetes)
- Lisinopril 10mg daily (for hypertension)
- Atorvastatin 20mg daily (for cholesterol)
- Aspirin 81mg daily (for cardiovascular protection)

**Medication Allergies:**
- Penicillin (hives)
- Sulfa drugs (rash)

**Relevant Citations:**
• Page 4: "PMH: HTN, DM2, hyperlipidemia"
• Page 5: "Current meds: Metformin, Lisinopril, Atorvastatin, ASA"
• Page 6: "Allergies: PCN, Sulfa"

**Confidence Level:** 91%
**Processing Time:** 2.1 seconds`,
           timestamp: new Date(),
           citations: riskFactorsCitations,
           confidence: 0.91,
           agentUsed: selectedAgent,
           processingTime: 2.1
         };
               } else {
          // Default patient-related response for other questions
          const patientCitations: Citation[] = [
            {
              id: '1',
              documentId,
              documentName,
              page: 1,
              text: 'Patient: Sarah M. Johnson, DOB: 03/15/1985, MRN: 12345678',
              confidence: 0.95,
              entityType: 'PATIENT_INFO',
              start: 50,
              end: 100
            },
            {
              id: '2',
              documentId,
              documentName,
              page: 2,
              text: 'Chief Complaint: Chest pain and shortness of breath for 3 days',
              confidence: 0.93,
              entityType: 'CHIEF_COMPLAINT',
              start: 200,
              end: 250
            },
            {
              id: '3',
              documentId,
              documentName,
              page: 3,
              text: 'Assessment: Acute coronary syndrome, rule out myocardial infarction',
              confidence: 0.91,
              entityType: 'ASSESSMENT',
              start: 350,
              end: 400
            }
          ];

          assistantMessage = {
            id: (Date.now() + 1).toString(),
            type: 'assistant',
            content: `Based on my analysis of the patient's medical record, I can provide you with comprehensive information about this case:

**Patient Information:**
- **Name:** Sarah M. Johnson
- **Date of Birth:** March 15, 1985
- **Medical Record Number:** 12345678
- **Date of Visit:** January 15, 2024

**Clinical Summary:**
The patient presents with acute onset chest pain and shortness of breath, raising concerns for potential cardiac etiology. The symptoms have been present for 3 days with progressive worsening.

**Key Clinical Findings:**
- **Vital Signs:** BP 145/95, HR 98, RR 22, O2 sat 94% on room air
- **Physical Exam:** No acute distress, normal heart sounds, clear lungs
- **ECG:** Sinus rhythm with non-specific ST changes
- **Labs:** Troponin pending, CBC and CMP within normal limits

**Differential Diagnosis:**
1. Acute coronary syndrome
2. Stable angina
3. Gastroesophageal reflux disease
4. Musculoskeletal chest pain
5. Anxiety-related symptoms

**Treatment Plan:**
- Cardiac monitoring
- Serial troponins
- Cardiology consultation
- Aspirin 325mg given
- Nitroglycerin as needed for chest pain

**Relevant Citations:**
• Page 1: "Patient: Sarah M. Johnson, DOB: 03/15/1985, MRN: 12345678"
• Page 2: "Chief Complaint: Chest pain and shortness of breath for 3 days"
• Page 3: "Assessment: Acute coronary syndrome, rule out myocardial infarction"

**Confidence Level:** 92%
**Processing Time:** 2.4 seconds`,
            timestamp: new Date(),
            citations: patientCitations,
            confidence: 0.92,
            agentUsed: selectedAgent,
            processingTime: 2.4
          };
        }

      setMessages(prev => [...prev, assistantMessage]);
      setChatHistory(prev => [...prev, assistantMessage]);
      setIsLoading(false);
         }, 5000);
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

  const handleAgentToggle = (agentValue: string) => {
    const newSelectedAgents = new Set(selectedAgents);
    if (newSelectedAgents.has(agentValue)) {
      newSelectedAgents.delete(agentValue);
    } else {
      newSelectedAgents.add(agentValue);
    }
    setSelectedAgents(newSelectedAgents);
    // Keep the first selected agent as the primary one for backward compatibility
    if (newSelectedAgents.size > 0) {
      setSelectedAgent(Array.from(newSelectedAgents)[0]);
    }
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
                         <Box>
               {message.content.split('\n').map((line, index) => {
                 if (line.trim() === '') {
                   return <Box key={index} height={8} />;
                 }
                                   if (line.startsWith('**') && line.endsWith('**')) {
                    return (
                      <Typography key={index} variant="h6" sx={{ mt: 2, mb: 1, fontWeight: 600, color: 'primary.main' }}>
                        {line.replace(/\*\*/g, '')}
                      </Typography>
                    );
                  }
                  if (line.includes('**') && !line.startsWith('**') && !line.endsWith('**')) {
                    // Handle inline bold text like "**Name:** Sarah M. Johnson"
                    const parts = line.split('**');
                    return (
                      <Typography key={index} variant="body1" sx={{ mb: 1, fontSize: '1.2rem', lineHeight: 1.6 }}>
                        {parts.map((part, partIndex) => 
                          partIndex % 2 === 1 ? 
                            <span key={partIndex} style={{ fontWeight: 600, color: 'primary.main' }}>{part}</span> : 
                            part
                        )}
                      </Typography>
                    );
                  }
                                   if (line.startsWith('- ')) {
                    return (
                      <Typography key={index} variant="body1" sx={{ ml: 2, mb: 0.5, fontSize: '1.2rem', lineHeight: 1.6 }}>
                        • {line.substring(2)}
                      </Typography>
                    );
                  }
                                   if (line.startsWith('• ')) {
                    return (
                      <Typography key={index} variant="body2" sx={{ ml: 2, mb: 0.5, color: 'text.secondary', fontSize: '1.1rem', lineHeight: 1.5 }}>
                        {line}
                      </Typography>
                    );
                  }
                                   if (line.match(/^\d+\./)) {
                    return (
                      <Typography key={index} variant="body1" sx={{ ml: 2, mb: 0.5, fontSize: '1.2rem', lineHeight: 1.6 }}>
                        {line}
                      </Typography>
                    );
                  }
                                   return (
                    <Typography key={index} variant="body1" sx={{ mb: 1, fontSize: '1.2rem', lineHeight: 1.6 }}>
                      {line}
                    </Typography>
                  );
               })}
             </Box>

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


          </Paper>
        </Box>
      </Box>
    </motion.div>
  );

  return (
    <Box height="100%" display="flex" flexDirection="column">
      {/* Search Bar */}
      <Card sx={{ mb: 2 }}>
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
               sx={{
                 '& .MuiInputBase-input::placeholder': {
                   fontSize: '1.1rem',
                   opacity: 0.7
                 }
               }}
               InputProps={{
                 startAdornment: (
                   <InputAdornment position="start">
                     <Search sx={{ color: 'text.secondary', mr: 1 }} />
                   </InputAdornment>
                 ),
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

      {/* Select Agent */}
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center" gap={2}>
              <Typography variant="h6" color="text.primary">
                Select Agent
              </Typography>
              <Box display="flex" gap={1} flexWrap="wrap">
                {agentOptions.map((agent) => (
                  <Chip
                    key={agent.value}
                    label={agent.label}
                    icon={agent.icon}
                    variant={selectedAgents.has(agent.value) ? "filled" : "outlined"}
                    color={selectedAgents.has(agent.value) ? "primary" : "default"}
                    onClick={() => handleAgentToggle(agent.value)}
                    sx={{ cursor: 'pointer' }}
                  />
                ))}
              </Box>
            </Box>

          </Box>
        </CardContent>
      </Card>

      {/* Hello Message Card */}
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={2}>
            <Avatar sx={{ bgcolor: 'secondary.main', width: 48, height: 48 }}>
              <SmartToy />
            </Avatar>
            <Box>
                             <Typography variant="h6" gutterBottom>
                 Hello! I'm aiDa Chat.
               </Typography>
                             <Typography variant="h6" color="text.secondary" sx={{ fontSize: '1.1rem', fontWeight: 400 }}>
                 I can help you understand this document by answering questions about its content, identifying key entities, assessing risks, and more. What would you like to know?
               </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

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

      {/* Sample Questions */}
      {showSampleQuestions && (
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                             <Typography variant="h6" sx={{ fontSize: '1.1rem', fontWeight: 500 }}>
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
