/**
 * Clinical Assistant Component
 * 
 * UI for doctors to interact with שרה (Clinical Assistant) agent.
 * Provides quick access to clinical tools and patient information.
 * 
 * Features:
 * - Chat interface with שרה
 * - Quick actions for common clinical tasks
 * - Patient context awareness
 * - Treatment history display
 * - Prescription management
 * 
 * Reference: AGENT_ARCHITECTURE_ANALYSIS.md
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  IconButton,
  Chip,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  CircularProgress,
  Alert,
  Paper,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Send as SendIcon,
  MedicalServices as MedicalIcon,
  Medication as MedicationIcon,
  Assignment as AssignmentIcon,
  LocalHospital as HospitalIcon,
  History as HistoryIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { chatAPI } from '../services/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface QuickAction {
  id: string;
  label: string;
  icon: React.ReactNode;
  prompt: string;
  category: 'chart' | 'prescription' | 'history' | 'plan';
}

const QUICK_ACTIONS: QuickAction[] = [
  {
    id: 'view_chart',
    label: 'View Dental Chart',
    icon: <MedicalIcon />,
    prompt: 'Show me the dental chart for patient ',
    category: 'chart',
  },
  {
    id: 'treatment_history',
    label: 'Treatment History',
    icon: <HistoryIcon />,
    prompt: 'Show me the treatment history for patient ',
    category: 'history',
  },
  {
    id: 'create_prescription',
    label: 'Create Prescription',
    icon: <MedicationIcon />,
    prompt: 'I need to create a prescription for patient ',
    category: 'prescription',
  },
  {
    id: 'medical_history',
    label: 'Medical History',
    icon: <HospitalIcon />,
    prompt: 'Show me the medical history including allergies for patient ',
    category: 'history',
  },
  {
    id: 'treatment_plan',
    label: 'Treatment Plan',
    icon: <AssignmentIcon />,
    prompt: 'Show me the treatment plans for patient ',
    category: 'plan',
  },
  {
    id: 'update_tooth',
    label: 'Update Tooth Status',
    icon: <MedicalIcon />,
    prompt: 'I need to update tooth status for patient ',
    category: 'chart',
  },
];

interface ClinicalAssistantProps {
  patientId?: string;
  patientName?: string;
}

export const ClinicalAssistant: React.FC<ClinicalAssistantProps> = ({
  patientId,
  patientName,
}) => {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Add welcome message when component mounts
    if (messages.length === 0) {
      setMessages([
        {
          role: 'assistant',
          content: patientId
            ? `שלום! אני שרה, העוזרת הקלינית. אני רואה שאתה עובד עם ${patientName || 'מטופל'}. איך אני יכולה לעזור?`
            : 'שלום! אני שרה, העוזרת הקלינית. איך אני יכולה לעזור היום?',
          timestamp: new Date(),
        },
      ]);
    }
  }, [patientId, patientName]);

  const handleSend = async (messageText?: string) => {
    const textToSend = messageText || input;
    if (!textToSend.trim()) return;

    setError(null);
    setLoading(true);

    // Add user message
    const userMessage: Message = {
      role: 'user',
      content: textToSend,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');

    try {
      // Call chat API
      const response = await chatAPI.sendMessage({
        message: textToSend,
        conversation_id: conversationId || undefined,
      });

      // Add assistant response
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.message,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // Save conversation ID
      if (response.conversation_id && !conversationId) {
        setConversationId(response.conversation_id);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to send message');
      console.error('Chat error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickAction = (action: QuickAction) => {
    let prompt = action.prompt;
    if (patientId && patientName) {
      prompt += patientName;
    } else {
      prompt += '[patient name/ID]';
    }
    setInput(prompt);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const renderQuickActions = () => {
    const categories = ['chart', 'prescription', 'history', 'plan'] as const;
    const currentCategory = categories[activeTab];
    const filteredActions = QUICK_ACTIONS.filter(
      (action) => action.category === currentCategory
    );

    return (
      <Grid container spacing={1}>
        {filteredActions.map((action) => (
          <Grid item xs={12} sm={6} key={action.id}>
            <Button
              variant="outlined"
              fullWidth
              startIcon={action.icon}
              onClick={() => handleQuickAction(action)}
              sx={{ justifyContent: 'flex-start', textAlign: 'left' }}
            >
              {action.label}
            </Button>
          </Grid>
        ))}
      </Grid>
    );
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <MedicalIcon color="primary" />
          שרה - עוזרת קלינית
        </Typography>
        {patientId && (
          <Chip
            label={`מטופל: ${patientName}`}
            size="small"
            color="primary"
            variant="outlined"
            sx={{ mt: 1 }}
          />
        )}
      </Box>

      {/* Quick Actions */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', bgcolor: 'grey.50' }}>
        <Typography variant="subtitle2" gutterBottom>
          פעולות מהירות
        </Typography>
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          variant="scrollable"
          scrollButtons="auto"
          sx={{ mb: 2, minHeight: 36 }}
        >
          <Tab label="תרשים שיניים" sx={{ minHeight: 36 }} />
          <Tab label="מרשמים" sx={{ minHeight: 36 }} />
          <Tab label="היסטוריה" sx={{ minHeight: 36 }} />
          <Tab label="תוכניות טיפול" sx={{ minHeight: 36 }} />
        </Tabs>
        {renderQuickActions()}
      </Box>

      {/* Messages */}
      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          p: 2,
          bgcolor: 'grey.50',
        }}
      >
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {messages.map((message, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
              mb: 2,
            }}
          >
            <Paper
              elevation={1}
              sx={{
                p: 2,
                maxWidth: '70%',
                bgcolor: message.role === 'user' ? 'primary.main' : 'white',
                color: message.role === 'user' ? 'white' : 'text.primary',
              }}
            >
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                {message.content}
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  display: 'block',
                  mt: 1,
                  opacity: 0.7,
                }}
              >
                {message.timestamp.toLocaleTimeString('he-IL', {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </Typography>
            </Paper>
          </Box>
        ))}

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
            <Paper elevation={1} sx={{ p: 2 }}>
              <CircularProgress size={20} />
            </Paper>
          </Box>
        )}

        <div ref={messagesEndRef} />
      </Box>

      {/* Input */}
      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider', bgcolor: 'white' }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="שאל את שרה על מטופל, טיפול, או מרשם..."
            disabled={loading}
            variant="outlined"
            size="small"
          />
          <IconButton
            color="primary"
            onClick={() => handleSend()}
            disabled={loading || !input.trim()}
            sx={{ alignSelf: 'flex-end' }}
          >
            <SendIcon />
          </IconButton>
        </Box>
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          שרה יכולה לעזור עם תרשימי שיניים, מרשמים, היסטוריה רפואית, ותוכניות טיפול
        </Typography>
      </Box>
    </Box>
  );
};

export default ClinicalAssistant;

