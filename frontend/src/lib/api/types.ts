/**
 * API Types and Interfaces
 * Shared types for API client, services, and components
 */

// ============================================================================
// REQUEST TYPES
// ============================================================================

export interface AnalysisRequest {
  question: string;
  session_id?: string;
  user_id?: string;
  enable_caching?: boolean;
  auto_expand?: boolean;
  model?: string;
}

export interface SessionRequest {
  user_id?: string;
  title?: string;
}

// ============================================================================
// RESPONSE TYPES
// ============================================================================

export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  details?: Record<string, any>;
  timestamp: string;
}

export interface AnalysisResult {
  id: string;
  name: string;
  description: string;
  category?: string;
  score?: number;
}

export interface AnalysisData {
  session_id: string;
  turn_id?: string;
  query_type: QueryType;
  original_query: string;
  expanded_query?: string;
  expansion_confidence?: number;
  search_results: AnalysisResult[];
  found_similar: boolean;
  context_used: boolean;
  analysis_summary?: string;
  needs_confirmation?: boolean;
  needs_clarification?: boolean;
  message?: string;
  options?: string[];
  suggestion?: string;
  // Additional properties from backend response
  response_type?: string;
  content?: string;
  metadata?: Record<string, any>;
  message_id?: string;
  analysis_id?: string;
  execution_id?: string;
  stage?: string;
  uiData?: any;
  // Allow additional dynamic properties
  [key: string]: unknown;
}

export interface AnalysisResponse extends APIResponse<AnalysisData> {}

export interface Session {
  session_id: string;
  user_id: string;
  created_at: string;
  last_activity: string;
  message_count: number;
  title?: string;
}

export interface SessionMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  query_type?: QueryType;
}

export interface ContextSummary {
  has_history: boolean;
  turn_count: number;
  last_query?: string;
  last_query_type?: string;
  last_analysis?: string;
}

export interface SessionHistory {
  session_id: string;
  messages: SessionMessage[];
  context_summary: ContextSummary;
}

// ============================================================================
// ENUMS
// ============================================================================

export enum QueryType {
  COMPLETE = 'complete',
  CONTEXTUAL = 'contextual',
  COMPARATIVE = 'comparative',
  PARAMETER = 'parameter',
}

// ============================================================================
// ERROR TYPES
// ============================================================================

export class APIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: Record<string, any>
  ) {
    super(message);
    this.name = 'APIError';
    Object.setPrototypeOf(this, APIError.prototype);
  }
}

export class NetworkError extends APIError {
  constructor(message: string = 'Network request failed') {
    super(message, undefined);
    this.name = 'NetworkError';
    Object.setPrototypeOf(this, NetworkError.prototype);
  }
}

export class TimeoutError extends APIError {
  constructor(message: string = 'Request timeout') {
    super(message, undefined);
    this.name = 'TimeoutError';
    Object.setPrototypeOf(this, TimeoutError.prototype);
  }
}

export class ValidationError extends APIError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, 400, details);
    this.name = 'ValidationError';
    Object.setPrototypeOf(this, ValidationError.prototype);
  }
}

export class NotFoundError extends APIError {
  constructor(message: string) {
    super(message, 404);
    this.name = 'NotFoundError';
    Object.setPrototypeOf(this, NotFoundError.prototype);
  }
}

export class UnauthorizedError extends APIError {
  constructor(message: string = 'Unauthorized') {
    super(message, 401);
    this.name = 'UnauthorizedError';
    Object.setPrototypeOf(this, UnauthorizedError.prototype);
  }
}

// ============================================================================
// CLIENT CONFIG
// ============================================================================

export interface APIClientConfig {
  baseURL: string;
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  enableCaching?: boolean;
}

export interface RequestConfig {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  path: string;
  data?: Record<string, any>;
  headers?: Record<string, string>;
  timeout?: number;
  retries?: number;
}

export interface CachedResponse<T = any> {
  data: T;
  timestamp: number;
  ttl: number;
}

// ============================================================================
// HOOKS TYPES
// ============================================================================

export interface UseAnalysisOptions {
  onSuccess?: (response: AnalysisResponse) => void;
  onError?: (error: Error) => void;
  onLoading?: (loading: boolean) => void;
}

export interface UseAnalysisState {
  loading: boolean;
  error: Error | null;
  data: AnalysisData | null;
}

export interface UseSessionOptions {
  onSessionChange?: (session: Session | null) => void;
  persistToStorage?: boolean;
}

export interface UseSessionState {
  session_id: string | null;
  user_id: string | null;
  isLoggedIn: boolean;
  loading: boolean;
  error: Error | null;
}

export interface UseConversationState {
  messages: SessionMessage[];
  loading: boolean;
  error: Error | null;
}

// ============================================================================
// CONTEXT TYPES
// ============================================================================

export interface SessionContextType {
  session_id: string | null;
  user_id: string | null;
  isLoggedIn: boolean;
  startSession: (user_id: string) => Promise<void>;
  endSession: () => Promise<void>;
  resumeSession: (session_id: string) => Promise<void>;
}

export interface ConversationContextType {
  messages: SessionMessage[];
  addMessage: (message: SessionMessage) => void;
  clearMessages: () => void;
  loadHistory: (session_id: string) => Promise<void>;
  isLoading: boolean;
  error: Error | null;
}

export interface UIContextType {
  isLoading: boolean;
  error: Error | null;
  setLoading: (loading: boolean) => void;
  setError: (error: Error | null) => void;
}
