'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { api } from '@/lib/api';
import { Session } from '@/lib/api/types';

export interface SessionMetadata {
  title?: string;
  created_at: string;
  updated_at: string;
  is_archived: boolean;
}

interface UseSessionReturn {
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

const SESSION_STORAGE_KEY = 'qna_session_id';
const USER_STORAGE_KEY = 'qna_user_id';

export function useSession(): UseSessionReturn {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [session_id, setSession_id] = useState<string | null>(null);
  const [user_id, setUser_id] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sessionMetadata, setSessionMetadata] = useState<SessionMetadata | undefined>(undefined);

  useEffect(() => {
    const initSession = async () => {
      try {
        const pathname = window.location.pathname;
        const chatMatch = pathname.match(/\/chat\/([^/]+)/);
        const url_session_id = chatMatch ? chatMatch[1] : null;
        const stored_session_id = url_session_id || localStorage.getItem(SESSION_STORAGE_KEY);
        const stored_user_id = localStorage.getItem(USER_STORAGE_KEY);

        if (stored_session_id && stored_session_id !== 'new') {
          setSession_id(stored_session_id);
          setUser_id(stored_user_id);
          if (!url_session_id) {
            router.replace(`/chat/${stored_session_id}`);
          }
        } else {
          await startNewSession(stored_user_id || undefined);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to initialize session');
        console.error('Session init error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    initSession();
  }, []);

  const startNewSession = async (newUser_id?: string) => {
    try {
      setIsLoading(true);
      setError(null);

      const session = await api.session.startSession(newUser_id);
      
      setSession_id(session.session_id);
      setUser_id(session.user_id);
      
      localStorage.setItem(SESSION_STORAGE_KEY, session.session_id);
      if (session.user_id) {
        localStorage.setItem(USER_STORAGE_KEY, session.user_id);
      }
      
      router.replace(`/chat/${session.session_id}`);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to start session';
      setError(errorMsg);
      console.error('Start session error:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const endSession = async () => {
    try {
      setIsLoading(true);
      
      if (session_id) {
        await api.session.endSession(session_id);
      }

      localStorage.removeItem(SESSION_STORAGE_KEY);
      localStorage.removeItem(USER_STORAGE_KEY);
      setSession_id(null);
      setUser_id(null);
      setSessionMetadata(undefined);
    } catch (err) {
      console.error('End session error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const resumeSession = async (sessionId: string) => {
    try {
      setIsLoading(true);
      setError(null);

      localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
      setSession_id(sessionId);
      router.replace(`/chat/${sessionId}`);
      
      console.log(`[useSession] Resumed session: ${sessionId}`);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to resume session';
      setError(errorMsg);
      console.error('Resume session error:', err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const updateSessionMetadata = (metadata: SessionMetadata) => {
    setSessionMetadata(metadata);
  };

  return {
    session_id,
    user_id,
    isLoading,
    error,
    sessionMetadata,
    startNewSession,
    endSession,
    resumeSession,
    updateSessionMetadata,
  };
}
