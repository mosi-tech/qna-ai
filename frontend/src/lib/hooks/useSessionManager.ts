import { useCallback, useState, useEffect } from 'react';
import { api } from '@/lib/api';

export interface SessionMetadata {
  session_id: string;
  title?: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message?: string;
  is_archived: boolean;
}

export interface SessionMessage {
  id: string;
  role: string;
  content: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

export interface SessionDetail {
  session_id: string;
  user_id: string;
  title?: string;
  created_at: string;
  updated_at: string;
  is_archived: boolean;
  messages: SessionMessage[];
}

export const useSessionManager = () => {
  const [sessions, setSessions] = useState<SessionMetadata[]>([]);
  const [isLoadingSessions, setIsLoadingSessions] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const listUserSessions = useCallback(
    async (userId: string, search?: string, archived?: boolean) => {
      setIsLoadingSessions(true);
      setError(null);
      try {
        const response = await fetch(
          `/api/sessions/user/${userId}?skip=0&limit=50${search ? `&search=${encodeURIComponent(search)}` : ''}${archived !== undefined ? `&archived=${archived}` : ''}`,
          { method: 'GET' }
        );

        if (!response.ok) {
          throw new Error(`Failed to load sessions: ${response.statusText}`);
        }

        const data = await response.json();
        setSessions(data);
        console.log(`[useSessionManager] Loaded ${data.length} sessions`);
        return data;
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Failed to load sessions';
        setError(errorMsg);
        console.error('[useSessionManager] Error:', err);
        throw err;
      } finally {
        setIsLoadingSessions(false);
      }
    },
    []
  );

  const getSessionDetail = useCallback(
    async (sessionId: string): Promise<SessionDetail | null> => {
      try {
        const response = await fetch(`/api/sessions/${sessionId}`);

        if (!response.ok) {
          if (response.status === 404) {
            return null;
          }
          throw new Error(`Failed to load session: ${response.statusText}`);
        }

        const data = await response.json();
        console.log(
          `[useSessionManager] Loaded session ${sessionId} with ${data.messages?.length || 0} messages`
        );
        return data;
      } catch (err) {
        console.error('[useSessionManager] Error loading session:', err);
        throw err;
      }
    },
    []
  );

  const updateSession = useCallback(
    async (sessionId: string, title?: string, isArchived?: boolean) => {
      try {
        const response = await fetch(`/api/sessions/${sessionId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title, is_archived: isArchived }),
        });

        if (!response.ok) {
          throw new Error(`Failed to update session: ${response.statusText}`);
        }

        console.log(`[useSessionManager] Updated session ${sessionId}`);

        setSessions((prev) =>
          prev.map((s) =>
            s.session_id === sessionId
              ? { ...s, title: title ?? s.title, is_archived: isArchived ?? s.is_archived }
              : s
          )
        );
        return true;
      } catch (err) {
        console.error('[useSessionManager] Error updating session:', err);
        throw err;
      }
    },
    []
  );

  const deleteSession = useCallback(async (sessionId: string) => {
    try {
      const response = await fetch(`/api/sessions/${sessionId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`Failed to delete session: ${response.statusText}`);
      }

      console.log(`[useSessionManager] Deleted session ${sessionId}`);

      setSessions((prev) => prev.filter((s) => s.session_id !== sessionId));
      return true;
    } catch (err) {
      console.error('[useSessionManager] Error deleting session:', err);
      throw err;
    }
  }, []);

  return {
    sessions,
    isLoadingSessions,
    error,
    listUserSessions,
    getSessionDetail,
    updateSession,
    deleteSession,
  };
};
