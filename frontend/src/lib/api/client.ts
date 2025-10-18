/**
 * Base HTTP Client for API Communication
 * Handles requests, errors, retries, and caching
 */

import {
  APIClientConfig,
  RequestConfig,
  APIResponse,
  APIError,
  NetworkError,
  TimeoutError,
} from './types';
import {
  parseAPIError,
  isRetryableError,
  logError,
} from './errors';
import { defaultCache, CacheManager } from './cache';

/**
 * HTTP Client with built-in retry, caching, and error handling
 */
export class APIClient {
  private baseURL: string;
  private timeout: number = 30000;
  private retries: number = 3;
  private retryDelay: number = 1000;
  private cache: CacheManager;
  private enableCaching: boolean = true;

  constructor(config: APIClientConfig) {
    this.baseURL = config.baseURL;
    this.timeout = config.timeout || 30000;
    this.retries = config.retries || 3;
    this.retryDelay = config.retryDelay || 1000;
    this.enableCaching = config.enableCaching !== false;
    this.cache = defaultCache;

    if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
      console.log('[APIClient] Initialized with config:', {
        baseURL: this.baseURL,
        timeout: this.timeout,
        retries: this.retries,
      });
    }
  }

  /**
   * Make GET request
   */
  async get<T = any>(path: string, config?: Partial<RequestConfig>): Promise<APIResponse<T>> {
    return this.request<T>({
      method: 'GET',
      path,
      ...config,
    });
  }

  /**
   * Make POST request
   */
  async post<T = any>(
    path: string,
    data?: Record<string, any>,
    config?: Partial<RequestConfig>
  ): Promise<APIResponse<T>> {
    return this.request<T>({
      method: 'POST',
      path,
      data,
      ...config,
    });
  }

  /**
   * Make PUT request
   */
  async put<T = any>(
    path: string,
    data?: Record<string, any>,
    config?: Partial<RequestConfig>
  ): Promise<APIResponse<T>> {
    return this.request<T>({
      method: 'PUT',
      path,
      data,
      ...config,
    });
  }

  /**
   * Make DELETE request
   */
  async delete<T = any>(path: string, config?: Partial<RequestConfig>): Promise<APIResponse<T>> {
    return this.request<T>({
      method: 'DELETE',
      path,
      ...config,
    });
  }

  /**
   * Make generic request with retry logic
   */
  private async request<T = any>(
    config: RequestConfig,
    attempt: number = 1
  ): Promise<APIResponse<T>> {
    const { method, path, data, timeout = this.timeout, retries = this.retries } = config;

    // Check cache for GET requests
    if (method === 'GET' && this.enableCaching) {
      const cached = this.cache.get<APIResponse<T>>(path);
      if (cached) {
        if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
          console.log('[APIClient] Cache hit:', path);
        }
        return cached;
      }
    }

    try {
      const response = await this.makeRequest<T>({
        method,
        path,
        data,
        timeout,
      });

      // Cache successful GET responses
      if (method === 'GET' && this.enableCaching && response.success) {
        this.cache.set(path, response, 'both');
      }

      return response;
    } catch (error) {
      // Check if error is retryable
      if (isRetryableError(error) && attempt < retries) {
        const delay = this.retryDelay * Math.pow(2, attempt - 1); // Exponential backoff
        
        if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
          console.log(
            `[APIClient] Retrying request (attempt ${attempt + 1}/${retries}) after ${delay}ms:`,
            path
          );
        }

        await new Promise(resolve => setTimeout(resolve, delay));
        return this.request<T>(config, attempt + 1);
      }

      // Log error
      logError(`[APIClient] Request failed: ${method} ${path}`, error, {
        attempt,
        retries,
      });

      // Throw error
      throw error;
    }
  }

  /**
   * Make actual HTTP request
   */
  private async makeRequest<T = any>(config: {
    method: string;
    path: string;
    data?: Record<string, any>;
    timeout: number;
  }): Promise<APIResponse<T>> {
    const { method, path, data, timeout } = config;
    const url = this.buildURL(path);
    const headers = this.buildHeaders();

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      const fetchConfig: RequestInit = {
        method,
        headers,
        signal: controller.signal,
      };

      if (data && (method === 'POST' || method === 'PUT')) {
        fetchConfig.body = JSON.stringify(data);
      }

      const response = await fetch(url, fetchConfig);
      clearTimeout(timeoutId);

      // Parse response
      let responseData: any;
      const contentType = response.headers.get('content-type');

      if (contentType?.includes('application/json')) {
        responseData = await response.json();
      } else {
        responseData = await response.text();
      }

      // Check if response is successful
      if (!response.ok) {
        throw parseAPIError({
          status: response.status,
          data: typeof responseData === 'object' ? responseData : { error: responseData },
        });
      }

      // Ensure response has correct format
      if (typeof responseData === 'object' && 'success' in responseData) {
        return responseData as APIResponse<T>;
      }

      // Wrap non-API-format responses
      return {
        success: true,
        data: responseData as T,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      if (error instanceof TypeError) {
        // Network error
        throw new NetworkError(`Failed to connect to ${url}`);
      }

      if ((error as any).name === 'AbortError') {
        throw new TimeoutError(`Request timeout after ${timeout}ms`);
      }

      if (error instanceof APIError) {
        throw error;
      }

      throw new APIError(
        `Request failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        undefined
      );
    }
  }

  /**
   * Build full URL
   */
  private buildURL(path: string): string {
    // Remove leading slash if present
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    return `${this.baseURL}${cleanPath}`;
  }

  /**
   * Build request headers
   */
  private buildHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    // Add authorization token if available
    const token = this.getAuthToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }

  /**
   * Get authorization token (placeholder for future auth implementation)
   */
  private getAuthToken(): string | null {
    if (typeof window === 'undefined') {
      return null;
    }

    try {
      return localStorage.getItem('auth_token');
    } catch {
      return null;
    }
  }

  /**
   * Clear all caches
   */
  clearCache(): void {
    this.cache.clear();
    if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
      console.log('[APIClient] Cache cleared');
    }
  }

  /**
   * Get cache statistics
   */
  getCacheStats() {
    return this.cache.getStats();
  }
}

/**
 * Create API client instance with environment configuration
 */
export function createAPIClient(overrides?: Partial<APIClientConfig>): APIClient {
  const baseURL =
    overrides?.baseURL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const config: APIClientConfig = {
    baseURL,
    timeout: overrides?.timeout || 30000,
    retries: overrides?.retries || 3,
    retryDelay: overrides?.retryDelay || 1000,
    enableCaching: overrides?.enableCaching !== false,
  };

  return new APIClient(config);
}

/**
 * Global API client instance
 */
export const apiClient = createAPIClient();
