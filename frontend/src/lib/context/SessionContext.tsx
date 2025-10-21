'use client';

import { createContext, useContext, ReactNode } from 'react';
import { useSession as useSessionHook } from '@/lib/hooks/useSession';

export interface SessionMetadata {
  title?: string;
  created_at: string;
  updated_at: string;
  is_archived: boolean;
}

interface SessionContextType {
  session_id: string | null;
  user_id: string | null;
  isLoading: boolean;
  error: string | null;
  sessionMetadata?: SessionMetadata;
  startNewSession: (user_id?: string) => Promise<void>;
  endSession: () => Promise<void>;
  resumeSession: (sessionId: string) => Promise<void>;
  updateSessionMetadata: (metadata: SessionMetadata) => void;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export function SessionProvider({ children }: { children: ReactNode }) {
  const session = useSessionHook();

  return (
    <SessionContext.Provider value={session}>
      {children}
    </SessionContext.Provider>
  );
}

export function useSession(): SessionContextType {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession must be used within SessionProvider');
  }
  return context;
}
