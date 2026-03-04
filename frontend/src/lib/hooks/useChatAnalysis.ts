'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import { AnalysisRequest, AnalysisResponse } from '@/lib/api/types';

interface UseChatAnalysisReturn {
  isLoading: boolean;
  error: string | null;
  chatWithAnalysis: (request: AnalysisRequest) => Promise<AnalysisResponse>;
}

/**
 * Hook for hybrid chat + analysis using the /sessions/{session_id}/chat endpoint
 * 
 * This provides:
 * - Educational responses about financial topics
 * - Analysis suggestions when appropriate
 * - Direct analysis execution when confirmed
 * - Professional financial analyst persona
 * 
 * Note: Requires session_id in the request for the RESTful API design
 */
export function useChatAnalysis(): UseChatAnalysisReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const chatWithAnalysis = async (request: AnalysisRequest): Promise<AnalysisResponse> => {
    try {
      setIsLoading(true);
      setError(null);

      // Validate session_id is required for the new RESTful endpoint
      if (!request.session_id) {
        throw new Error('Session ID is required for chat requests');
      }

      // Use the new RESTful chat endpoint: POST /sessions/{session_id}/chat
      const response = await api.client.post<AnalysisResponse['data']>(
        `/sessions/${request.session_id}/chat`,
        {
          // Remove session_id from body since it's now in the URL path
          question: request.question,
          user_id: request.user_id,
          enable_caching: request.enable_caching,
          auto_expand: request.auto_expand,
          model: request.model,
        },
        {
          retries: 0,
          timeout: 90000, // LLM calls (clarification, hybrid chat) can exceed the default 30s
        }
      );

      if (!response.success) {
        throw new Error(response.error || 'Hybrid chat failed');
      }

      return {
        success: response.success,
        data: response.data,
        error: response.error,
        timestamp: response.timestamp,
      } as AnalysisResponse;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Hybrid chat request failed';
      console.error('[useChatAnalysis] Chat error:', err);
      setError(errorMsg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    isLoading,
    error,
    chatWithAnalysis,
  };
}