'use client';

import { createContext, useContext, ReactNode } from 'react';
import { useConversation as useConversationHook, ChatMessage } from '@/lib/hooks/useConversation';

interface ConversationContextType {
  messages: ChatMessage[];
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => ChatMessage;
  updateMessage: (id: string, updates: Partial<ChatMessage>) => void;
  clearMessages: () => void;
  getMessageById: (id: string) => ChatMessage | undefined;
  setMessages: (messages: ChatMessage[]) => void;
}

const ConversationContext = createContext<ConversationContextType | undefined>(undefined);

export function ConversationProvider({ children }: { children: ReactNode }) {
  const conversation = useConversationHook();

  return (
    <ConversationContext.Provider value={conversation}>
      {children}
    </ConversationContext.Provider>
  );
}

export function useConversation(): ConversationContextType {
  const context = useContext(ConversationContext);
  if (!context) {
    throw new Error('useConversation must be used within ConversationProvider');
  }
  return context;
}
