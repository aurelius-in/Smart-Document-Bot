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
  ZoomIn,
  ZoomOut,
  Fullscreen,
  Download,
  Print,
  Share,
  Bookmark,
  BookmarkBorder,
  Highlight,
  Visibility,
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

  const filteredEntities = entities.filter(entity => {
    const matchesSearch = entity.text.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = filterType === 'all' || entity.type === filterType;
    return matchesSearch && matchesType;
  });

  const renderHighlightedContent = () => {
    if (!showHighlights) {
      return (
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
                onMouseEnter={() => setSelectedEntity(part.entity)}
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
              <Typography variant="h6">{documentName}</Typography>
              <Box display="flex" alignItems="center" gap={1}>
                <Tooltip title="Toggle Highlights">
                  <IconButton
                    size="small"
                    onClick={() => setShowHighlights(!showHighlights)}
                  >
                    {showHighlights ? <Visibility /> : <VisibilityOff />}
                  </IconButton>
                </Tooltip>
                <Tooltip title="Zoom Out">
                  <IconButton
                    size="small"
                    onClick={() => setZoom(Math.max(50, zoom - 10))}
                  >
                    <ZoomOut />
                  </IconButton>
                </Tooltip>
                <Typography variant="caption">{zoom}%</Typography>
                <Tooltip title="Zoom In">
                  <IconButton
                    size="small"
                    onClick={() => setZoom(Math.min(200, zoom + 10))}
                  >
                    <ZoomIn />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Fullscreen">
                  <IconButton size="small">
                    <Fullscreen />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Download">
                  <IconButton size="small" onClick={onExport}>
                    <Download />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Print">
                  <IconButton size="small">
                    <Print />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Share">
                  <IconButton size="small">
                    <Share />
                  </IconButton>
                </Tooltip>
              </Box>
            </Box>

            {/* Search Bar */}
            <TextField
              fullWidth
              placeholder="Search in document..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                )
              }}
              sx={{ mb: 2 }}
            />

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
              Document Analysis
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
                              sx={{ backgroundColor: entityColors[entity.type], color: 'white' }}
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
                {highlights.map((entity) => (
                  <ListItem key={entity.id}>
                    <ListItemIcon>
                      <Box sx={{ color: entityColors[entity.type] }}>
                        <Highlight />
                      </Box>
                    </ListItemIcon>
                    <ListItemText
                      primary={entity.text}
                      secondary={entityLabels[entity.type]}
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
                {Array.from(bookmarkedEntities).map((entityId) => {
                  const entity = entities.find(e => e.id === entityId);
                  if (!entity) return null;
                  
                  return (
                    <ListItem key={entity.id}>
                      <ListItemIcon>
                        <Box sx={{ color: entityColors[entity.type] }}>
                          <Bookmark />
                        </Box>
                      </ListItemIcon>
                      <ListItemText
                        primary={entity.text}
                        secondary={entityLabels[entity.type]}
                      />
                      <IconButton
                        size="small"
                        onClick={() => handleBookmarkToggle(entity.id)}
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
