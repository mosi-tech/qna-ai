import { useCallback, useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';

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
  offset?: number;
  limit?: number;
  total_messages?: number;
  has_older?: boolean;
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
        const params = new URLSearchParams();
        params.append('limit', '50');
        if (search) params.append('search', search);
        if (archived !== undefined) params.append('archived', String(archived));

        console.log(`[useSessionManager] Fetching user sessions`);

        const response = await apiClient.get<SessionMetadata[]>(`/api/sessions/list?${params.toString()}`);

        if (!response.success || !response.data) {
          throw new Error('Failed to load sessions');
        }

        setSessions(response.data);
        console.log(`[useSessionManager] Loaded ${response.data.length} sessions`);
        return response.data;
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
    async (sessionId: string, offset: number = 0, limit: number = 5): Promise<SessionDetail | null> => {
      try {
        const params = new URLSearchParams();
        params.append('offset', String(offset));
        params.append('limit', String(limit));

        console.log(`[useSessionManager] Fetching session ${sessionId}`);

        const response = await apiClient.get<SessionDetail>(`/api/sessions/${sessionId}?${params.toString()}`);

        if (!response.success || !response.data) {
          return null;
        }

        console.log(
          `[useSessionManager] Loaded session ${sessionId} with ${response.data.messages?.length || 0} messages (has_older: ${response.data.has_older})`
        );
        return response.data;
      } catch (err: any) {
        if (err.status === 404 || err.message?.includes('404')) {
          return null;
        }
        console.error('[useSessionManager] Error loading session:', err);
        throw err;
      }
    },
    []
  );

  const updateSession = useCallback(
    async (sessionId: string, title?: string, isArchived?: boolean) => {
      try {
        const response = await apiClient.put(`/api/sessions/${sessionId}`, {
          title,
          is_archived: isArchived,
        });

        if (!response.success) {
          throw new Error('Failed to update session');
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
      const response = await apiClient.delete(`/api/sessions/${sessionId}`);

      if (!response.success) {
        throw new Error('Failed to delete session');
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
