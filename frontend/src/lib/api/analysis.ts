/**
 * Analysis Service
 * Handles analysis operations via API
 */

import { APIClient } from './client';
import {
  AnalysisRequest,
  AnalysisResponse,
  AnalysisResult,
  APIResponse,
} from './types';
import { logError } from './errors';

/**
 * Analysis Service for making analysis API calls
 */
export class AnalysisService {
  constructor(private client: APIClient) {}

  /**
   * Analyze a financial question
   */
  async analyzeQuestion(request: AnalysisRequest): Promise<AnalysisResponse> {
    try {
      if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
        console.log('[AnalysisService] Analyzing question:', request.question);
      }

      const response = await this.client.post<AnalysisResponse['data']>(
        '/analyze',
        request,
        {
          timeout: 300000,
          retries: 1,
        }
      );

      return {
        success: response.success,
        data: response.data,
        error: response.error,
        timestamp: response.timestamp,
      } as AnalysisResponse;
    } catch (error) {
      logError('[AnalysisService] analyzeQuestion failed', error, {
        question: request.question?.substring(0, 50),
      });

      throw error;
    }
  }

  /**
   * Search for similar analyses
   */
  async searchSimilar(
    query: string,
    limit: number = 5,
    similarityThreshold: number = 0.3
  ): Promise<AnalysisResult[]> {
    try {
      if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
        console.log('[AnalysisService] Searching similar:', query);
      }

      const response = await this.client.post<{
        analyses: AnalysisResult[];
      }>('/search', {
        query,
        limit,
        similarity_threshold: similarityThreshold,
      });

      if (!response.success || !response.data) {
        return [];
      }

      return response.data.analyses || [];
    } catch (error) {
      logError('[AnalysisService] searchSimilar failed', error, {
        query: query.substring(0, 50),
      });

      // Return empty array on error instead of throwing
      return [];
    }
  }

  /**
   * Get analysis details
   */
  async getAnalysisDetails(analysisId: string): Promise<AnalysisResult | null> {
    try {
      if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
        console.log('[AnalysisService] Getting analysis details:', analysisId);
      }

      const response = await this.client.get<AnalysisResult>(
        `/analysis/${analysisId}`
      );

      if (!response.success) {
        return null;
      }

      return response.data || null;
    } catch (error) {
      logError('[AnalysisService] getAnalysisDetails failed', error, {
        analysisId,
      });

      return null;
    }
  }

  /**
   * Get analysis list
   */
  async getAnalysisList(
    category?: string,
    limit: number = 10
  ): Promise<AnalysisResult[]> {
    try {
      if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
        console.log('[AnalysisService] Getting analysis list:', { category, limit });
      }

      const params = new URLSearchParams();
      params.append('limit', limit.toString());
      if (category) {
        params.append('category', category);
      }

      const response = await this.client.get<{
        analyses: AnalysisResult[];
      }>(`/analyses?${params.toString()}`);

      if (!response.success || !response.data) {
        return [];
      }

      return response.data.analyses || [];
    } catch (error) {
      logError('[AnalysisService] getAnalysisList failed', error, { category, limit });
      return [];
    }
  }

  /**
   * Save analysis result
   */
  async saveAnalysis(
    question: string,
    analysisResult: AnalysisResult
  ): Promise<string | null> {
    try {
      if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
        console.log('[AnalysisService] Saving analysis:', question);
      }

      const response = await this.client.post<{
        id: string;
      }>('/save_analysis', {
        question,
        ...analysisResult,
      });

      if (!response.success || !response.data) {
        return null;
      }

      return response.data.id || null;
    } catch (error) {
      logError('[AnalysisService] saveAnalysis failed', error, {
        question: question.substring(0, 50),
      });

      return null;
    }
  }

  /**
   * Get analysis suggestions based on partial query
   */
  async getSuggestions(partialQuery: string): Promise<string[]> {
    try {
      if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
        console.log('[AnalysisService] Getting suggestions for:', partialQuery);
      }

      const response = await this.client.post<{
        suggestions: string[];
      }>('/suggestions', {
        query: partialQuery,
      });

      if (!response.success || !response.data) {
        return [];
      }

      return response.data.suggestions || [];
    } catch (error) {
      logError('[AnalysisService] getSuggestions failed', error, {
        query: partialQuery.substring(0, 50),
      });

      return [];
    }
  }

  /**
   * Handle user response to clarification prompt
   */
  async handleClarificationResponse(
    sessionId: string,
    userResponse: string,
    originalQuery: string,
    expandedQuery: string
  ): Promise<AnalysisResponse> {
    try {
      if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
        console.log('[AnalysisService] Handling clarification response:', {
          sessionId,
          userResponse,
          originalQuery,
          expandedQuery,
        });
      }

      const response = await this.client.post<AnalysisResponse['data']>(
        `/clarification/${sessionId}`,
        {
          user_response: userResponse,
          original_query: originalQuery,
          expanded_query: expandedQuery,
        },
        {
          timeout: 300000,
          retries: 1,
        }
      );

      return {
        success: response.success,
        data: response.data,
        error: response.error,
        timestamp: response.timestamp,
      } as AnalysisResponse;
    } catch (error) {
      logError('[AnalysisService] handleClarificationResponse failed', error, {
        sessionId,
        userResponse: userResponse.substring(0, 50),
      });

      throw error;
    }
  }
}

/**
 * Factory function to create analysis service
 */
export function createAnalysisService(client: APIClient): AnalysisService {
  return new AnalysisService(client);
}
