import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Paper,
  Divider,
  IconButton,
  Tooltip,
  Drawer,
  Tabs,
  Tab,
  Badge,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  TextField,
  InputAdornment
} from '@mui/material';
import {
  Person,
  Business,
  LocationOn,
  AttachMoney,
  DateRange,
  Description,
  Search,
  FilterList,
  Fullscreen,
  Print,
  Bookmark,
  BookmarkBorder,
  Highlight,
  VisibilityOff
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

interface Entity {
  id: string;
  text: string;
  type: 'PERSON' | 'ORGANIZATION' | 'LOCATION' | 'MONEY' | 'DATE' | 'CONTRACT_TERM' | 'RISK_FACTOR' | 'COMPLIANCE_ITEM';
  start: number;
  end: number;
  confidence: number;
  metadata?: Record<string, any>;
}

interface DocumentViewerProps {
  documentId: string;
  documentName: string;
  documentContent: string;
  entities: Entity[];
  highlights: Entity[];
  onEntityClick?: (entity: Entity) => void;
  onHighlightToggle?: (entity: Entity) => void;
  onSearch?: (query: string) => void;
  onExport?: () => void;
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({
  documentId,
  documentName,
  documentContent,
  entities,
  highlights,
  onEntityClick,
  onHighlightToggle,
  onSearch,
  onExport
}) => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [zoom, setZoom] = useState(100);
  const [showHighlights, setShowHighlights] = useState(true);
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null);
  const [bookmarkedEntities, setBookmarkedEntities] = useState<Set<string>>(new Set());
  const [searchSuggestions, setSearchSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);

  const entityColors = {
    PERSON: '#FF6B6B',
    ORGANIZATION: '#4ECDC4',
    LOCATION: '#45B7D1',
    MONEY: '#96CEB4',
    DATE: '#FFEAA7',
    CONTRACT_TERM: '#DDA0DD',
    RISK_FACTOR: '#FF8A80',
    COMPLIANCE_ITEM: '#81C784'
  };

  const entityIcons = {
    PERSON: <Person />,
    ORGANIZATION: <Business />,
    LOCATION: <LocationOn />,
    MONEY: <AttachMoney />,
    DATE: <DateRange />,
    CONTRACT_TERM: <Description />,
    RISK_FACTOR: <Description />,
    COMPLIANCE_ITEM: <Description />
  };

  const entityLabels = {
    PERSON: 'Person',
    ORGANIZATION: 'Organization',
    LOCATION: 'Location',
    MONEY: 'Money',
    DATE: 'Date',
    CONTRACT_TERM: 'Contract Term',
    RISK_FACTOR: 'Risk Factor',
    COMPLIANCE_ITEM: 'Compliance Item'
  };

  // Sample highlights data for demonstration
  const sampleHighlights: Entity[] = [
    {
      id: 'highlight-1',
      text: 'annual advisory fee of $300,000',
      type: 'MONEY',
      start: 1200,
      end: 1230,
      confidence: 0.95
    },
    {
      id: 'highlight-2',
      text: 'portfolio management and asset allocation strategies',
      type: 'CONTRACT_TERM',
      start: 800,
      end: 850,
      confidence: 0.92
    },
    {
      id: 'highlight-3',
      text: 'Securities and Exchange Commission',
      type: 'COMPLIANCE_ITEM',
      start: 600,
      end: 630,
      confidence: 0.98
    }
  ];

  // Use provided highlights or fall back to sample data
  const displayHighlights = highlights.length > 0 ? highlights : sampleHighlights;

  // Sample bookmarked entities for demonstration - these are user-saved important items
  const sampleBookmarkedEntities = new Set(['bookmark-1', 'bookmark-2', 'bookmark-3', 'bookmark-4']); // IDs of entities to show as bookmarked

  // Search suggestions based on actual Financial Advisory Services Agreement content
  const documentSearchSuggestions = [
    // Key terms from the document
    'Global Financial Services, Inc.',
    'Global Investment Partners, LLC',
    'Sarah M. Johnson',
    'Michael R. Chen',
    'FSA-2024-0015',
    'Effective Date',
    'January 15, 2024',
    
    // Financial terms
    'annual advisory fee',
    '$300,000',
    '$25,000',
    'monthly installments',
    '30 days',
    'compensation',
    'advisory fees',
    
    // Service terms
    'financial advisory services',
    'portfolio management',
    'asset allocation strategies',
    'investment research',
    'risk assessment',
    'compliance monitoring',
    'quarterly performance reports',
    'tax-efficient investment planning',
    
    // Legal terms
    'confidentiality',
    'proprietary information',
    'termination',
    'written notice',
    'liability',
    'governing law',
    'State of New York',
    'binding arbitration',
    
    // Compliance terms
    'Securities and Exchange Commission',
    'Investment Advisers Act of 1940',
    'fiduciary duty',
    'code of ethics',
    'Gramm-Leach-Bliley Act',
    'Regulation S-P',
    'data protection laws',
    'industry best practices'
  ];

  const filteredEntities = entities.filter(entity => {
    const matchesSearch = searchQuery === '' || 
                         entity.text.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         documentContent.toLowerCase().includes(entity.text.toLowerCase());
    const matchesType = filterType === 'all' || entity.type === filterType;
    return matchesSearch && matchesType;
  });

  // Generate search suggestions based on query and document content
  const generateSearchSuggestions = (query: string) => {
    if (!query.trim()) {
      return documentSearchSuggestions.slice(0, 8); // Show top 8 suggestions when empty
    }
    
    // First, search in the document content
    const documentMatches = documentContent.toLowerCase().match(new RegExp(`\\b${query.toLowerCase()}\\w*`, 'g'));
    const uniqueDocumentMatches = documentMatches ? Array.from(new Set(documentMatches)) : [];
    
    // Then search in predefined suggestions
    const suggestionMatches = documentSearchSuggestions.filter(suggestion =>
      suggestion.toLowerCase().includes(query.toLowerCase())
    );
    
    // Combine and prioritize document matches
    const allMatches = [...uniqueDocumentMatches, ...suggestionMatches];
    const uniqueMatches = Array.from(new Set(allMatches));
    
    return uniqueMatches.slice(0, 8);
  };

  // Handle search input changes
  const handleSearchChange = (value: string) => {
    setSearchQuery(value);
    setSearchSuggestions(generateSearchSuggestions(value));
    setShowSuggestions(value.length > 0);
  };

  // Handle suggestion selection
  const handleSuggestionClick = (suggestion: string) => {
    setSearchQuery(suggestion);
    setShowSuggestions(false);
    onSearch?.(suggestion);
  };

  const renderHighlightedContent = () => {
    const documentTitle = (
      <Box sx={{ textAlign: 'center', mb: 3, pb: 2, borderBottom: '2px solid #e0e0e0' }}>
        <Typography
          variant="h6"
          sx={{
            fontWeight: 400,
            color: '#f5f5f5',
            mb: 1,
            fontSize: '1.1rem'
          }}
        >
          FINANCIAL ADVISORY SERVICES AGREEMENT
        </Typography>
        <Typography
          variant="body2"
          sx={{
            color: '#cccccc',
            fontWeight: 400
          }}
        >
          Agreement No: FSA-2024-0015 | Effective Date: January 15, 2024
        </Typography>
      </Box>
    );

    if (!showHighlights) {
      return (
        <Box>
          {documentTitle}
          <Typography
            variant="body1"
            sx={{
              whiteSpace: 'pre-wrap',
              lineHeight: 1.6,
              fontSize: `${zoom}%`
            }}
          >
            {documentContent}
          </Typography>
        </Box>
      );
    }

    const sortedEntities = [...entities].sort((a, b) => a.start - b.start);
    const parts: Array<{ text: string; entity?: Entity }> = [];
    let lastIndex = 0;

    sortedEntities.forEach(entity => {
      if (entity.start > lastIndex) {
        parts.push({ text: documentContent.slice(lastIndex, entity.start) });
      }
      parts.push({ text: documentContent.slice(entity.start, entity.end), entity });
      lastIndex = entity.end;
    });

    if (lastIndex < documentContent.length) {
      parts.push({ text: documentContent.slice(lastIndex) });
    }

    return (
      <Box>
        {documentTitle}
        <Typography
          variant="body1"
          sx={{
            whiteSpace: 'pre-wrap',
            lineHeight: 1.6,
            fontSize: `${zoom}%`
          }}
        >
          {parts.map((part, index) => {
            if (part.entity) {
              const isHighlighted = highlights.some(h => h.id === part.entity!.id);
              const isSelected = selectedEntity?.id === part.entity.id;
              const isBookmarked = bookmarkedEntities.has(part.entity.id);

              return (
                <motion.span
                  key={index}
                  initial={{ backgroundColor: 'transparent' }}
                  animate={{
                    backgroundColor: isHighlighted ? entityColors[part.entity.type] : 'transparent'
                  }}
                  transition={{ duration: 0.3 }}
                  style={{
                    padding: '2px 4px',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    border: isSelected ? `2px solid ${entityColors[part.entity.type]}` : 'none',
                    position: 'relative'
                  }}
                  onMouseEnter={() => setSelectedEntity(part.entity || null)}
                  onMouseLeave={() => setSelectedEntity(null)}
                  onClick={() => onEntityClick?.(part.entity!)}
                >
                  {part.text}
                  {isBookmarked && (
                    <Bookmark
                      sx={{
                        position: 'absolute',
                        top: -8,
                        right: -8,
                        fontSize: 12,
                        color: entityColors[part.entity.type]
                      }}
                    />
                  )}
                </motion.span>
              );
            }
            return part.text;
          })}
        </Typography>
      </Box>
    );
  };

  const handleBookmarkToggle = (entityId: string) => {
    const newBookmarks = new Set(bookmarkedEntities);
    if (newBookmarks.has(entityId)) {
      newBookmarks.delete(entityId);
    } else {
      newBookmarks.add(entityId);
    }
    setBookmarkedEntities(newBookmarks);
  };

  const scrollToEntity = (entity: Entity) => {
    if (contentRef.current) {
      const element = contentRef.current.querySelector(`[data-entity-id="${entity.id}"]`);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  };

  return (
    <Box display="flex" height="100%" gap={2}>
      {/* Main Document Content */}
      <Box flex={1} display="flex" flexDirection="column">
        <Card>
          <CardContent>
                         {/* Document Header */}
                           <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                <Box display="flex" alignItems="center" sx={{ width: '100%', justifyContent: 'space-between' }}>
                  <Tooltip title="Toggle Highlights">
                    <IconButton
                      size="medium"
                      onClick={() => setShowHighlights(!showHighlights)}
                    >
                      <Highlight />
                    </IconButton>
                  </Tooltip>
                  <Typography variant="body2" sx={{ minWidth: '40px', textAlign: 'center' }}>{zoom}%</Typography>
                  <Tooltip title="Fullscreen">
                    <IconButton size="medium">
                      <Fullscreen />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Print">
                    <IconButton size="medium">
                      <Print />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>

            {/* Search Bar */}
            <Box sx={{ position: 'relative', mb: 2 }}>
                             <TextField
                 fullWidth
                 placeholder="Search the Financial Services Agreement for terms, organizations, dates, or amounts..."
                 value={searchQuery}
                 onChange={(e) => handleSearchChange(e.target.value)}
                onFocus={() => setShowSuggestions(true)}
                onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  )
                }}
              />
              
              {/* Search Suggestions Dropdown */}
              <AnimatePresence>
                {showSuggestions && searchSuggestions.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                                         style={{
                       position: 'absolute',
                       top: '100%',
                       left: 0,
                       right: 0,
                       zIndex: 1000,
                       backgroundColor: '#f3e5f5',
                       border: '1px solid #e1bee7',
                       borderRadius: '0 0 4px 4px',
                       boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                       maxHeight: '300px',
                       overflow: 'auto'
                     }}
                  >
                    {searchSuggestions.map((suggestion, index) => (
                      <Box
                        key={index}
                                                 sx={{
                           p: 1.5,
                           cursor: 'pointer',
                           borderBottom: '1px solid',
                           borderColor: '#e1bee7',
                           backgroundColor: '#f3e5f5',
                           '&:hover': {
                             backgroundColor: '#e8d5f2'
                           },
                           '&:last-child': {
                             borderBottom: 'none'
                           }
                         }}
                        onClick={() => handleSuggestionClick(suggestion)}
                      >
                                                 <Typography variant="body2" sx={{ fontWeight: 500, color: 'black' }}>
                           {suggestion}
                         </Typography>
                                                   <Typography variant="caption" sx={{ color: '#666666' }}>
                            {suggestion.includes('Global Financial Services') || suggestion.includes('Global Investment Partners') ? 'Organizations' :
                             suggestion.includes('$') || suggestion.includes('fee') || suggestion.includes('compensation') ? 'Financial Terms' :
                             suggestion.includes('2024') || suggestion.includes('Date') ? 'Dates & Numbers' :
                             suggestion.includes('SEC') || suggestion.includes('Investment Advisers Act') ? 'Compliance' :
                             suggestion.includes('confidentiality') || suggestion.includes('liability') || suggestion.includes('termination') ? 'Legal Terms' :
                             suggestion.includes('services') || suggestion.includes('management') ? 'Services' :
                             'Document Terms'}
                          </Typography>
                      </Box>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </Box>

            {/* Document Content */}
            <Box
              ref={contentRef}
              sx={{
                maxHeight: '70vh',
                overflow: 'auto',
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1,
                p: 2,
                backgroundColor: 'background.paper'
              }}
            >
              {renderHighlightedContent()}
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Sidebar */}
      <Box width={400}>
        <Card>
          <CardContent>
                         <Typography variant="h6" gutterBottom>
               Analysis
             </Typography>

            <Tabs
              value={selectedTab}
              onChange={(_, newValue) => setSelectedTab(newValue)}
              sx={{ mb: 2 }}
            >
              <Tab label="Entities" />
              <Tab label="Highlights" />
              <Tab label="Bookmarks" />
            </Tabs>

            {/* Filter */}
            <Box display="flex" alignItems="center" gap={1} mb={2}>
              <FilterList />
              <TextField
                select
                size="small"
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                sx={{ minWidth: 120 }}
              >
                <option value="all">All Types</option>
                {Object.entries(entityLabels).map(([key, label]) => (
                  <option key={key} value={key}>{label}</option>
                ))}
              </TextField>
            </Box>

            {/* Entity List */}
            {selectedTab === 0 && (
              <List>
                {filteredEntities.map((entity) => (
                  <motion.div
                    key={entity.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <ListItem
                      button
                      onClick={() => {
                        onEntityClick?.(entity);
                        scrollToEntity(entity);
                      }}
                      sx={{
                        border: selectedEntity?.id === entity.id ? 2 : 1,
                        borderColor: selectedEntity?.id === entity.id ? entityColors[entity.type] : 'divider',
                        borderRadius: 1,
                        mb: 1
                      }}
                    >
                      <ListItemIcon>
                        <Box sx={{ color: entityColors[entity.type] }}>
                          {entityIcons[entity.type]}
                        </Box>
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" gap={1}>
                            <Typography variant="subtitle2">
                              {entity.text}
                            </Typography>
                            <Chip
                              label={entityLabels[entity.type]}
                              size="small"
                              sx={{ backgroundColor: entityColors[entity.type], color: 'black', fontWeight: 600 }}
                            />
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography variant="caption" color="text.secondary">
                              Confidence: {Math.round(entity.confidence * 100)}%
                            </Typography>
                            {entity.metadata && (
                              <Typography variant="caption" display="block" color="text.secondary">
                                {Object.entries(entity.metadata).map(([key, value]) => `${key}: ${value}`).join(', ')}
                              </Typography>
                            )}
                          </Box>
                        }
                      />
                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleBookmarkToggle(entity.id);
                        }}
                      >
                        {bookmarkedEntities.has(entity.id) ? <Bookmark /> : <BookmarkBorder />}
                      </IconButton>
                    </ListItem>
                  </motion.div>
                ))}
              </List>
            )}

            {/* Highlights Tab */}
            {selectedTab === 1 && (
              <List>
                {displayHighlights.map((entity) => (
                  <ListItem key={entity.id}>
                    <ListItemIcon>
                      <Box sx={{ color: entityColors[entity.type] }}>
                        <Highlight />
                      </Box>
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="subtitle2">
                            {entity.text}
                          </Typography>
                          <Chip
                            label={entityLabels[entity.type]}
                            size="small"
                            sx={{ backgroundColor: entityColors[entity.type], color: 'black', fontWeight: 600 }}
                          />
                        </Box>
                      }
                      secondary={`Confidence: ${Math.round(entity.confidence * 100)}%`}
                    />
                    <IconButton
                      size="small"
                      onClick={() => onHighlightToggle?.(entity)}
                    >
                      <VisibilityOff />
                    </IconButton>
                  </ListItem>
                ))}
              </List>
            )}

            {/* Bookmarks Tab */}
            {selectedTab === 2 && (
              <List>
                {Array.from(bookmarkedEntities.size > 0 ? bookmarkedEntities : sampleBookmarkedEntities).map((entityId) => {
                  // For bookmarks, show user-saved important items with different data
                  const bookmarkData = [
                    {
                      id: 'bookmark-1',
                      text: 'Critical Risk Clause - Section 6.1',
                      type: 'RISK_FACTOR' as const,
                      confidence: 0.98,
                      metadata: { section: '6.1', importance: 'Critical', userNote: 'Review quarterly' }
                    },
                    {
                      id: 'bookmark-2',
                      text: 'Termination Notice Period - 30 days',
                      type: 'CONTRACT_TERM' as const,
                      confidence: 0.95,
                      metadata: { section: '2.2', importance: 'High', userNote: 'Key for exit strategy' }
                    },
                    {
                      id: 'bookmark-3',
                      text: 'Annual Advisory Fee - $300,000',
                      type: 'MONEY' as const,
                      confidence: 0.97,
                      metadata: { section: '3.1', importance: 'Critical', userNote: 'Budget planning' }
                    },
                    {
                      id: 'bookmark-4',
                      text: 'SEC Registration Requirement',
                      type: 'COMPLIANCE_ITEM' as const,
                      confidence: 0.99,
                      metadata: { section: '5.1', importance: 'Critical', userNote: 'Regulatory compliance' }
                    }
                  ];
                  
                  const bookmarkItem = bookmarkData.find(item => item.id === entityId);
                  if (!bookmarkItem) return null;
                  
                  return (
                    <ListItem key={bookmarkItem.id}>
                      <ListItemIcon>
                        <Box sx={{ color: entityColors[bookmarkItem.type] }}>
                          <Bookmark />
                        </Box>
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" gap={1}>
                            <Typography variant="subtitle2">
                              {bookmarkItem.text}
                            </Typography>
                            <Chip
                              label={entityLabels[bookmarkItem.type]}
                              size="small"
                              sx={{ backgroundColor: entityColors[bookmarkItem.type], color: 'black', fontWeight: 600 }}
                            />
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography variant="caption" color="text.secondary">
                              Confidence: {Math.round(bookmarkItem.confidence * 100)}%
                            </Typography>
                            <Typography variant="caption" display="block" color="text.secondary">
                              Section: {bookmarkItem.metadata.section} | {bookmarkItem.metadata.importance} Priority
                            </Typography>
                            <Typography variant="caption" display="block" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                              Note: {bookmarkItem.metadata.userNote}
                            </Typography>
                          </Box>
                        }
                      />
                      <IconButton
                        size="small"
                        onClick={() => handleBookmarkToggle(bookmarkItem.id)}
                      >
                        <BookmarkBorder />
                      </IconButton>
                    </ListItem>
                  );
                })}
              </List>
            )}
          </CardContent>
        </Card>
      </Box>

      {/* Entity Details Tooltip */}
      <AnimatePresence>
        {selectedEntity && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            style={{
              position: 'fixed',
              zIndex: 1000,
              pointerEvents: 'none'
            }}
          >
            <Paper
              sx={{
                p: 2,
                maxWidth: 300,
                backgroundColor: 'background.paper',
                boxShadow: 3
              }}
            >
              <Typography variant="subtitle2" gutterBottom>
                {selectedEntity.text}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Type: {entityLabels[selectedEntity.type]}
              </Typography>
              <Typography variant="caption" display="block" color="text.secondary">
                Confidence: {Math.round(selectedEntity.confidence * 100)}%
              </Typography>
              {selectedEntity.metadata && (
                <Box mt={1}>
                  {Object.entries(selectedEntity.metadata).map(([key, value]) => (
                    <Typography key={key} variant="caption" display="block" color="text.secondary">
                      {key}: {value}
                    </Typography>
                  ))}
                </Box>
              )}
            </Paper>
          </motion.div>
        )}
      </AnimatePresence>
    </Box>
  );
};

export default DocumentViewer;
