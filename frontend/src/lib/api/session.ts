/**
 * Session Service
 * Handles session management via API
 */

import { APIClient } from './client';
import {
  Session,
  SessionHistory,
  ContextSummary,
  SessionRequest,
  APIResponse,
} from './types';
import { logError } from './errors';

/**
 * Session Service for managing user sessions
 */
export class SessionService {
  constructor(private client: APIClient) {}

  /**
   * Start a new session
   */
  async startSession(
    title?: string
  ): Promise<Session> {
    try {
      if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
        console.log('[SessionService] Starting new session');
      }

      const request: any = {};
      if (title) {
        request.title = title;
      }

      const response = await this.client.post<Session>('/session/start', request);

      if (!response.success || !response.data) {
        throw new Error('Failed to start session');
      }

      return response.data;
    } catch (error) {
      logError('[SessionService] startSession failed', error);
      throw error;
    }
  }

  /**
   * Get session with full conversation history
   */
  async getSession(session_id: string): Promise<SessionHistory | null> {
    try {
      if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
        console.log('[SessionService] Getting session:', session_id);
      }

      const response = await this.client.get<SessionHistory>(
        `/session/${session_id}`
      );

      if (!response.success || !response.data) {
        return null;
      }

      return response.data;
    } catch (error) {
      logError('[SessionService] getSession failed', error, { session_id });
      return null;
    }
  }

  /**
   * Get session context summary
   */
  async getSessionContext(session_id: string): Promise<ContextSummary | null> {
    try {
      if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
        console.log('[SessionService] Getting session context:', session_id);
      }

      const response = await this.client.get<ContextSummary>(
        `/session/${session_id}/context`
      );

      if (!response.success || !response.data) {
        return null;
      }

      return response.data;
    } catch (error) {
      logError('[SessionService] getSessionContext failed', error, { session_id });
      return null;
    }
  }

  /**
   * Resume an existing session
   */
  async resumeSession(session_id: string): Promise<Session | null> {
    try {
      if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
        console.log('[SessionService] Resuming session:', session_id);
      }

      const response = await this.client.post<Session>(
        `/session/${session_id}/resume`,
        {}
      );

      if (!response.success || !response.data) {
        return null;
      }

      return response.data;
    } catch (error) {
      logError('[SessionService] resumeSession failed', error, { session_id });
      return null;
    }
  }

  /**
   * End/delete a session
   */
  async endSession(session_id: string): Promise<boolean> {
    try {
      if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
        console.log('[SessionService] Ending session:', session_id);
      }

      const response = await this.client.delete(`/session/${session_id}`);

      return response.success;
    } catch (error) {
      logError('[SessionService] endSession failed', error, { session_id });
      return false;
    }
  }

  /**
   * List user's sessions
   */
  async listSessions(
    user_id: string,
    limit: number = 10
  ): Promise<Session[]> {
    try {
      if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
        console.log('[SessionService] Listing sessions for user:', user_id);
      }

      const params = new URLSearchParams();
      params.append('user_id', user_id);
      params.append('limit', limit.toString());

      const response = await this.client.get<{
        sessions: Session[];
      }>(`/sessions?${params.toString()}`);

      if (!response.success || !response.data) {
        return [];
      }

      return response.data.sessions || [];
    } catch (error) {
      logError('[SessionService] listSessions failed', error, { user_id });
      return [];
    }
  }

  /**
   * Update session title
   */
  async updateSessionTitle(
    session_id: string,
    title: string
  ): Promise<Session | null> {
    try {
      if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
        console.log('[SessionService] Updating session title:', session_id);
      }

      const response = await this.client.put<Session>(
        `/session/${session_id}`,
        { title }
      );

      if (!response.success || !response.data) {
        return null;
      }

      return response.data;
    } catch (error) {
      logError('[SessionService] updateSessionTitle failed', error, { session_id });
      return null;
    }
  }

  /**
   * Clear session cache (useful after data changes)
   */
  clearCache(session_id?: string): void {
    // This would be called to invalidate cache after API changes
    if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
      console.log('[SessionService] Cache cleared for session:', session_id || 'all');
    }
  }
}

/**
 * Factory function to create session service
 */
export function createSessionService(client: APIClient): SessionService {
  return new SessionService(client);
}
