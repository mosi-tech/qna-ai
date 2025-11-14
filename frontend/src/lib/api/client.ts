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
    const headers = await this.buildHeaders();

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      const fetchConfig: RequestInit = {
        method,
        headers,
        signal: controller.signal,
        credentials: 'include', // Include cookies in cross-origin requests
      };

      if (data && (method === 'POST' || method === 'PUT')) {
        fetchConfig.body = JSON.stringify(data);
      }

      
      
      const startTime = Date.now();
      
      const response = await fetch(url, fetchConfig);
      const endTime = Date.now();
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
        const apiError = parseAPIError({
          status: response.status,
          data: typeof responseData === 'object' ? responseData : { error: responseData },
        });
        
        // Handle 401 Unauthorized - redirect to login
        if (response.status === 401) {
          this.handleUnauthorized();
        }
        
        throw apiError;
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
      console.error('[APIClient] Request failed:', {
        method,
        url,
        error: error instanceof Error ? error.message : String(error),
        name: error instanceof Error ? error.name : 'Unknown',
        timeout,
        stack: error instanceof Error ? error.stack : undefined
      });
      
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
   * Build request headers with environment-aware authentication
   */
  private async buildHeaders(): Promise<Record<string, string>> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    // Environment-aware authentication
    if (process.env.NEXT_PUBLIC_AUTH_MODE === 'jwt') {
      // DEV: Use JWT tokens for cross-domain authentication
      const jwt = await this.getJWTToken();
      if (jwt) {
        headers['Authorization'] = `Bearer ${jwt}`;
        if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
          console.log('[APIClient] DEV: Adding JWT Authorization header');
        }
      } else {
        console.warn('[APIClient] DEV: No JWT token available');
      }
    } else {
      // PROD: Rely on HttpOnly cookies (automatic)
      if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
        console.log('[APIClient] PROD: Using automatic cookie authentication');
      }
    }

    return headers;
  }

  /**
   * Get JWT token from Appwrite for development
   */
  private async getJWTToken(): Promise<string | null> {
    if (typeof window === 'undefined') {
      return null;
    }

    try {
      const { account } = await import('../appwrite');
      
      // Create JWT token from current session
      const jwt = await account.createJWT();
      
      if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
        console.log('[APIClient] Created JWT token for dev authentication');
      }
      
      return jwt.jwt;
    } catch (error) {
      if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
        console.log('[APIClient] No active session for JWT creation:', error);
      }
      return null;
    }
  }

  /**
   * Handle unauthorized responses (401) by redirecting to login
   */
  private handleUnauthorized(): void {
    if (typeof window === 'undefined') {
      return;
    }

    console.warn('[APIClient] 401 Unauthorized - redirecting to login');
    
    // Clear any stored auth tokens
    try {
      localStorage.removeItem('auth_token');
      // Clear Appwrite session cookies by setting them to expire
      const cookies = document.cookie.split(';');
      cookies.forEach(cookie => {
        const cookieName = cookie.split('=')[0].trim();
        if (cookieName.startsWith('a_session_')) {
          document.cookie = `${cookieName}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
        }
      });
    } catch {
      // Ignore localStorage/cookie errors
    }
    
    // Redirect to login page
    const currentPath = window.location.pathname;
    const loginUrl = '/auth/login';
    
    // Avoid redirect loops
    if (currentPath !== loginUrl && !currentPath.startsWith('/auth/')) {
      // Store the current path to redirect back after login
      try {
        localStorage.setItem('redirect_after_login', currentPath);
      } catch {
        // Ignore localStorage errors
      }
      
      window.location.href = loginUrl;
    }
  }

  /**
   * Clear all caches
   */
  clearCache(): void {
    this.cache.clear();
    if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
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
    overrides?.baseURL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8010';

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
