'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';

export interface ChatMessage {
  id: string;
  type: 'user' | 'ai' | 'thinking' | 'analyzing' | 'results' | 'interactive' | 'error' | 'clarification';
  content: string;
  timestamp: Date;
  moduleKey?: string;
  data?: any;
  isExpanded?: boolean;
  analysisId?: string;
  executionId?: string;
  role?: 'user' | 'assistant';
  response_type?: string;
  status?: 'pending' | 'running' | 'completed' | 'failed';
}

interface UseConversationReturn {
  messages: ChatMessage[];
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => ChatMessage;
  updateMessage: (id: string, updates: Partial<ChatMessage>) => void;
  removeMessage: (id: string) => void;
  clearMessages: () => void;
  getMessageById: (id: string) => ChatMessage | undefined;
  setMessages: (messages: ChatMessage[]) => void;
  resumeSession: (sessionId: string) => Promise<void>;
  loadSessionMessages: (sessionId: string) => Promise<void>;
}

const CONVERSATION_STORAGE_KEY = 'qna_conversation';
const SESSION_MESSAGES_CACHE_KEY = 'qna_session_messages';

export function useConversation(): UseConversationReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  useEffect(() => {
    // Initialize with welcome message only on mount
    // Session messages will be loaded by page.tsx based on session_id
    const initialMessage: ChatMessage = {
      id: `welcome-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type: 'ai',
      content: "Hi! I'm your AI financial analyst. Ask me anything about portfolio analysis, trading strategies, risk assessment, or investment research.",
      timestamp: new Date(),
    };
    setMessages([initialMessage]);
  }, []);

  useEffect(() => {
    localStorage.setItem(CONVERSATION_STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

  const addMessage = (message: Omit<ChatMessage, 'id' | 'timestamp'>): ChatMessage => {
    const newMessage: ChatMessage = {
      ...message,
      id: (message as any).id || `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, newMessage]);
    return newMessage;
  };

  const updateMessage = (id: string, updates: Partial<ChatMessage>) => {
    setMessages(prev =>
      prev.map(msg =>
        msg.id === id ? { ...msg, ...updates } : msg
      )
    );
  };

  const removeMessage = (id: string) => {
    setMessages(prev => prev.filter(msg => msg.id !== id));
  };

  const clearMessages = () => {
    setMessages([]);
    localStorage.removeItem(CONVERSATION_STORAGE_KEY);
  };

  const getMessageById = (id: string): ChatMessage | undefined => {
    return messages.find(msg => msg.id === id);
  };

  const setMessagesHandler = (newMessages: ChatMessage[]) => {
    setMessages(newMessages);
  };

  const loadSessionMessages = async (sessionId: string): Promise<void> => {
    try {
      // Use the shared APIClient for retry, timeout, and normalised error handling
      const response = await api.client.get(`/api/sessions/${sessionId}?offset=0&limit=50`);
      if (!response.success) {
        throw new Error(response.error || 'Failed to load session messages');
      }

      const data = response.data;
      const loadedMessages = (data.messages || []).map((msg: any, idx: number) => {
        // Determine message type based on role and normalized response_type
        let messageType = 'ai'; // default for assistant messages
        if (msg.role === 'user') {
          messageType = 'user';
        } else if (msg.role === 'assistant') {
          // Use the normalized response_type field (primary)
          const responseType = msg.response_type || msg.metadata?.response_type;

          if (responseType === 'analysis') {
            messageType = 'results';
          } else if (responseType === 'needs_clarification' || responseType === 'needs_confirmation' || responseType === 'clarification') {
            messageType = 'clarification';
          } else if (responseType === 'meaningless') {
            messageType = 'ai'; // Render as regular AI message
          } else {
            // Fallback: check for legacy analysis data detection
            if (msg.uiData || (msg.metadata && (
              msg.metadata.query_type ||
              msg.metadata.analysis_type ||
              msg.metadata.best_day ||
              (msg.metadata.response_data && msg.metadata.response_data.analysis_result)
            ))) {
              messageType = 'results';
            }
          }
        }

        return {
          id: msg.id || `${sessionId}-${idx}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          type: messageType,
          content: msg.content,
          timestamp: new Date(msg.timestamp),
          data: msg.uiData || msg.metadata, // Prefer uiData over raw metadata
          analysisId: msg.analysisId,
          executionId: msg.executionId,
          status: msg.status,              // surface DB status for pending-poll detection
          response_type: msg.response_type, // surface for type-based routing on reload
        };
      });

      if (loadedMessages.length > 0) {
        setMessages(loadedMessages);
      }
    } catch (err) {
      console.error('[useConversation] Failed to load session messages:', err);
      throw err;
    }
  };

  const resumeSession = async (sessionId: string): Promise<void> => {
    try {
      console.log(`Resuming session: ${sessionId}`);
    } catch (err) {
      console.error('Failed to resume session:', err);
    }
  };

  return {
    messages,
    addMessage,
    updateMessage,
    removeMessage,
    clearMessages,
    getMessageById,
    setMessages: setMessagesHandler,
    loadSessionMessages,
    resumeSession,
  };
}
