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
  constructor(private client: APIClient) { }

  /**
   * Send a hybrid chat message (combines chat + analysis)
   */
  async sendChatMessage(request: AnalysisRequest): Promise<AnalysisResponse> {
    try {
      // Validate session_id is required for the new RESTful endpoint
      if (!request.session_id) {
        throw new Error('Session ID is required for chat requests');
      }

      const response = await this.client.post<AnalysisResponse['data']>(
        `/sessions/${request.session_id}/chat`,  // New RESTful chat endpoint
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
        }
      );

      const result = {
        success: response.success,
        data: response.data,
        error: response.error,
        timestamp: response.timestamp,
      } as AnalysisResponse;

      return result;
    } catch (error) {
      console.error('[AnalysisService] sendChatMessage failed with error:', error);
      logError('[AnalysisService] sendChatMessage failed', error, {
        question: request.question?.substring(0, 50),
      });

      throw error;
    }
  }

  /**
   * Analyze a financial question (legacy endpoint)
   */
  async analyzeQuestion(request: AnalysisRequest): Promise<AnalysisResponse> {
    try {


      const response = await this.client.post<AnalysisResponse['data']>(
        '/analyze',  // Back to normal endpoint with SSE disabled
        request,
        {
          // timeout: 300000,
          retries: 0,
        }
      );


      const result = {
        success: response.success,
        data: response.data,
        error: response.error,
        timestamp: response.timestamp,
      } as AnalysisResponse;

      return result;
    } catch (error) {
      console.error('[AnalysisService] analyzeQuestion failed with error:', error);
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

  /**
   * Get analysis details from new analysis API
   */
  async getAnalysisById(analysisId: string): Promise<any> {
    try {
      if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
        console.log('[AnalysisService] Getting analysis by ID:', analysisId);
      }

      const response = await this.client.get(`/api/analysis/${analysisId}`);

      if (!response.success) {
        throw new Error(response.data?.error || 'Failed to fetch analysis');
      }

      return response.data;
    } catch (error) {
      logError('[AnalysisService] getAnalysisById failed', error, { analysisId });
      throw error;
    }
  }

  /**
   * Get analysis associated with a specific message
   */
  async getAnalysisByMessageId(messageId: string): Promise<any> {
    try {
      if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
        console.log('[AnalysisService] Getting analysis by message ID:', messageId);
      }

      const response = await this.client.get(`/api/analysis/messages/${messageId}/analysis`);

      if (!response.success) {
        throw new Error(response.data?.error || 'Failed to fetch message analysis');
      }

      return response.data;
    } catch (error) {
      logError('[AnalysisService] getAnalysisByMessageId failed', error, { messageId });
      throw error;
    }
  }

  /**
   * Get execution history for specific analysis
   */
  async getAnalysisExecutions(analysisId: string, limit: number = 50, executionType?: 'primary' | 'user_rerun' | 'all'): Promise<any[]> {
    try {
      if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
        console.log('[AnalysisService] Getting analysis executions:', analysisId, executionType);
      }

      const params = new URLSearchParams({ limit: limit.toString() });
      if (executionType) {
        params.append('execution_type', executionType);
      }

      const response = await this.client.get(`/api/analysis/${analysisId}/executions?${params.toString()}`);

      if (!response.success) {
        throw new Error(response.data?.error || 'Failed to fetch analysis executions');
      }

      return response.data || [];
    } catch (error) {
      logError('[AnalysisService] getAnalysisExecutions failed', error, { analysisId, limit, executionType });
      return [];
    }
  }

  /**
   * Get the primary (original) execution for an analysis
   */
  async getPrimaryExecution(analysisId: string): Promise<any | null> {
    try {
      const executions = await this.getAnalysisExecutions(analysisId, 1, 'primary');
      return executions.length > 0 ? executions[0] : null;
    } catch (error) {
      logError('[AnalysisService] getPrimaryExecution failed', error, { analysisId });
      return null;
    }
  }

  /**
   * Get user-initiated re-runs for an analysis (workspace history)
   */
  async getUserReruns(analysisId: string, limit: number = 50): Promise<any[]> {
    try {
      return await this.getAnalysisExecutions(analysisId, limit, 'user_rerun');
    } catch (error) {
      logError('[AnalysisService] getUserReruns failed', error, { analysisId, limit });
      return [];
    }
  }

  /**
   * Get execution result associated with a specific message (what's shown in chat)
   */
  async getMessageExecution(messageId: string): Promise<any | null> {
    try {
      if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
        console.log('[AnalysisService] Getting message execution:', messageId);
      }

      const response = await this.client.get(`/api/analysis/messages/${messageId}/execution`);

      if (!response.success) {
        throw new Error(response.data?.error || 'Failed to fetch message execution');
      }

      return response.data;
    } catch (error) {
      logError('[AnalysisService] getMessageExecution failed', error, { messageId });
      return null;
    }
  }

  /**
   * Execute an analysis with given parameters using new analysis API
   */
  async executeAnalysisNew(analysisId: string, parameters?: any, sessionId?: string): Promise<any> {
    try {
      if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
        console.log('[AnalysisService] Executing analysis (new API):', analysisId, parameters);
      }

      const response = await this.client.post(`/api/analysis/${analysisId}/execute`, {
        parameters: parameters || {},
        sessionId
      });

      if (!response.success) {
        throw new Error(response.data?.error || 'Analysis execution failed');
      }

      return response.data;
    } catch (error) {
      logError('[AnalysisService] executeAnalysisNew failed', error, { analysisId });
      throw error;
    }
  }

  /**
   * Execute an analysis with given parameters (legacy)
   */
  async executeAnalysis(analysisId: string, parameters?: any, sessionId?: string): Promise<any> {
    try {
      if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
        console.log('[AnalysisService] Executing analysis:', analysisId, parameters);
      }

      const response = await this.client.post(`/execute/${analysisId}`, {
        parameters,
        session_id: sessionId
      });

      if (!response.success) {
        throw new Error(response.data?.error || 'Analysis execution failed');
      }

      return response.data;
    } catch (error) {
      logError('[AnalysisService] executeAnalysis failed', error, { analysisId });
      throw error;
    }
  }

  /**
   * Get execution status and results
   */
  async getExecutionStatus(executionId: string): Promise<any> {
    try {
      const response = await this.client.get(`/execution/${executionId}/status`);
      
      if (!response.success) {
        throw new Error(response.data?.error || 'Failed to fetch execution status');
      }

      return response.data;
    } catch (error) {
      logError('[AnalysisService] getExecutionStatus failed', error, { executionId });
      throw error;
    }
  }

  /**
   * Get execution logs
   */
  async getExecutionLogs(executionId: string): Promise<string[]> {
    try {
      const response = await this.client.get(`/execution/${executionId}/logs`);
      
      if (!response.success) {
        throw new Error(response.data?.error || 'Failed to fetch execution logs');
      }

      return response.data?.logs || [];
    } catch (error) {
      logError('[AnalysisService] getExecutionLogs failed', error, { executionId });
      return [];
    }
  }

  /**
   * Get user's analyses
   */
  async getUserAnalyses(limit: number = 50): Promise<any[]> {
    try {
      const response = await this.client.get(`/user/analyses?limit=${limit}`);
      
      if (!response.success) {
        throw new Error(response.data?.error || 'Failed to fetch user analyses');
      }

      return response.data?.analyses || [];
    } catch (error) {
      logError('[AnalysisService] getUserAnalyses failed', error, { limit });
      return [];
    }
  }

  /**
   * Get analysis execution history for a session
   */
  async getExecutionHistory(sessionId: string, limit: number = 100): Promise<any[]> {
    try {
      const response = await this.client.get(`/session/${sessionId}/executions?limit=${limit}`);
      
      if (!response.success) {
        throw new Error(response.data?.error || 'Failed to fetch execution history');
      }

      return response.data?.executions || [];
    } catch (error) {
      logError('[AnalysisService] getExecutionHistory failed', error, { sessionId, limit });
      return [];
    }
  }

  /**
   * Poll execution status until completion
   */
  async pollExecutionStatus(
    executionId: string, 
    onProgress?: (status: any) => void,
    timeout: number = 300000 // 5 minutes
  ): Promise<any> {
    const startTime = Date.now();
    const pollInterval = 2000; // Poll every 2 seconds

    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const status = await this.getExecutionStatus(executionId);
          
          // Call progress callback if provided
          if (onProgress) {
            onProgress(status);
          }

          // Check if execution is complete
          if (status.status === 'completed' || status.status === 'failed') {
            resolve(status);
            return;
          }

          // Check timeout
          if (Date.now() - startTime > timeout) {
            reject(new Error('Execution timeout'));
            return;
          }

          // Continue polling if still running
          if (status.status === 'running') {
            setTimeout(poll, pollInterval);
          } else {
            reject(new Error(`Unexpected execution status: ${status.status}`));
          }

        } catch (error) {
          reject(error);
        }
      };

      poll();
    });
  }
}

/**
 * Factory function to create analysis service
 */
export function createAnalysisService(client: APIClient): AnalysisService {
  return new AnalysisService(client);
}
