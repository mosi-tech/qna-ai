'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import { AnalysisRequest, AnalysisResponse } from '@/lib/api/types';

interface UseAnalysisReturn {
  isLoading: boolean;
  error: string | null;
  analyzeQuestion: (request: AnalysisRequest) => Promise<AnalysisResponse>;
  sendChatMessage: (request: AnalysisRequest) => Promise<AnalysisResponse>;
  searchSimilar: (query: string, limit?: number) => Promise<any[]>;
  getSuggestions: (query: string) => Promise<string[]>;
}

export function useAnalysis(): UseAnalysisReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyzeQuestion = async (request: AnalysisRequest): Promise<AnalysisResponse> => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await api.analysis.analyzeQuestion(request);

      if (!response.success) {
        throw new Error(response.error || 'Analysis failed');
      }

      return response;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Analysis request failed';
      console.error('[useAnalysis] Analysis error:', err);
      setError(errorMsg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const sendChatMessage = async (request: AnalysisRequest): Promise<AnalysisResponse> => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await api.analysis.sendChatMessage(request);

      if (!response.success) {
        throw new Error(response.error || 'Chat message failed');
      }

      return response;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Chat message failed';
      console.error('[useAnalysis] Chat message error:', err);
      setError(errorMsg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const searchSimilar = async (query: string, limit: number = 5): Promise<any[]> => {
    try {
      setError(null);
      return await api.analysis.searchSimilar(query, limit);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Search failed';
      setError(errorMsg);
      console.error('Search error:', err);
      return [];
    }
  };

  const getSuggestions = async (query: string): Promise<string[]> => {
    try {
      setError(null);
      return await api.analysis.getSuggestions(query);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Suggestions failed';
      setError(errorMsg);
      console.error('Suggestions error:', err);
      return [];
    }
  };

  return {
    isLoading,
    error,
    analyzeQuestion,
    sendChatMessage,
    searchSimilar,
    getSuggestions,
  };
}
