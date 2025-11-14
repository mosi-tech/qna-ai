'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { api } from '@/lib/api';
import { Session } from '@/lib/api/types';
import { useAuth } from '@/lib/context/AuthContext';

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
  startNewSession: (title?: string) => Promise<void>;
  endSession: () => Promise<void>;
  resumeSession: (sessionId: string) => Promise<void>;
  updateSessionMetadata: (metadata: SessionMetadata) => void;
}

const SESSION_STORAGE_KEY = 'qna_session_id';
const USER_STORAGE_KEY = 'qna_user_id';

export function useSession(): UseSessionReturn {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const [session_id, setSession_id] = useState<string | null>(null);
  const [user_id, setUser_id] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sessionMetadata, setSessionMetadata] = useState<SessionMetadata | undefined>(undefined);

  useEffect(() => {
    const initSession = async () => {
      // Wait for authentication to be resolved
      if (authLoading) {
        return;
      }

      // Don't initialize session if user is not authenticated
      if (!isAuthenticated) {
        setIsLoading(false);
        return;
      }

      try {
        const pathname = window.location.pathname;
        const chatMatch = pathname.match(/\/chat\/([^/]+)/);
        const url_session_id = chatMatch ? chatMatch[1] : null;
        const stored_session_id = url_session_id || localStorage.getItem(SESSION_STORAGE_KEY);
        
        // Use authenticated user's ID instead of stored user_id
        const authenticated_user_id = user?.$id;

        if (stored_session_id && stored_session_id !== 'new' && authenticated_user_id) {
          setSession_id(stored_session_id);
          setUser_id(authenticated_user_id);
          if (!url_session_id) {
            router.replace(`/chat/${stored_session_id}`);
          }
        } else {
          // Only start new session if user is authenticated
          await startNewSession();
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to initialize session');
        console.error('Session init error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    initSession();
  }, [authLoading, isAuthenticated, user]);

  const startNewSession = async (title?: string) => {
    // Don't start session without authenticated user
    if (!isAuthenticated || !user) {
      throw new Error('User must be authenticated to start session');
    }

    try {
      setIsLoading(true);
      setError(null);

      const session = await api.session.startSession(title);
      
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

      // First check if the session exists and user has access to it
      const sessionExists = await api.session.getSession(sessionId);
      
      if (!sessionExists) {
        // Session doesn't exist, throw error to trigger fallback behavior
        throw new Error(`Session ${sessionId} not found`);
      }

      localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
      setSession_id(sessionId);
      setUser_id(sessionExists.user_id);
      
      // Only navigate if we're not already on the correct URL
      if (window.location.pathname !== `/chat/${sessionId}`) {
        router.replace(`/chat/${sessionId}`);
      }
      
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
