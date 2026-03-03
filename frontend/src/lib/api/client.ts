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
    config?: Partial<RequestConfig & { skipCache?: boolean }>
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
    config: RequestConfig & { skipCache?: boolean },
    attempt: number = 1
  ): Promise<APIResponse<T>> {
    const { method, path, data, timeout = this.timeout, retries = this.retries, skipCache: skipCacheConfig } = config;

    // Check cache for GET requests (skip caching for session/message endpoints)
    const skipCache = skipCacheConfig || path.includes('/sessions/') || path.includes('/messages/');
    if (method === 'GET' && this.enableCaching && !skipCache) {
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

      // Cache successful GET responses (skip caching for session/message endpoints)
      if (method === 'GET' && this.enableCaching && !skipCache && response.success) {
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
    const headers = await this.buildHeaders(method);

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

        // Do NOT auto-redirect on 401 here — withAuth already handles
        // unauthenticated state by redirecting to login. Calling handleUnauthorized
        // here causes spurious redirects when the JWT just hasn't been refreshed yet.
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
  private async buildHeaders(method?: string): Promise<Record<string, string>> {
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
          console.log('[APIClient] DEV: ✅ Adding JWT Authorization header');
        }
      } else {
        if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
          console.warn('[APIClient] DEV: ⚠️ No JWT token available, request may fail');
        }
        // Still try the request - backend might have fallback auth
      }
    } else {
      // PROD: Rely on HttpOnly cookies (automatic)
      if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
        console.log('[APIClient] PROD: Using automatic cookie authentication');
      }
    }

    return headers;
  }

  // Cache JWT to avoid a double Appwrite round-trip on every API call.
  // Appwrite JWTs expire in 15 min; we refresh 60 s before expiry.
  private _jwtCache: { token: string; expiresAt: number } | null = null;
  // Holds an in-progress createJWT promise so concurrent callers share one network request.
  private _jwtInflight: Promise<string | null> | null = null;

  private static readonly JWT_STORAGE_KEY = '_api_jwt';

  private readJWTFromStorage(): { token: string; expiresAt: number } | null {
    try {
      const raw = sessionStorage.getItem(APIClient.JWT_STORAGE_KEY);
      if (!raw) return null;
      const parsed = JSON.parse(raw) as { token: string; expiresAt: number };
      return parsed;
    } catch {
      return null;
    }
  }

  private writeJWTToStorage(token: string, expiresAt: number): void {
    try {
      sessionStorage.setItem(APIClient.JWT_STORAGE_KEY, JSON.stringify({ token, expiresAt }));
    } catch {
      // sessionStorage unavailable — in-memory cache only
    }
  }

  private clearJWTStorage(): void {
    try { sessionStorage.removeItem(APIClient.JWT_STORAGE_KEY); } catch { /* ignore */ }
  }

  /**
   * Get JWT token from Appwrite.
   * Checks sessionStorage first (survives page refresh), then in-memory cache.
   * Concurrent callers share one in-flight createJWT() request.
   */
  private async getJWTToken(): Promise<string | null> {
    if (typeof window === 'undefined') return null;

    // 1. In-memory cache (fastest)
    if (this._jwtCache && Date.now() < this._jwtCache.expiresAt - 60_000) {
      return this._jwtCache.token;
    }

    // 2. sessionStorage (survives page refresh — no network needed)
    const stored = this.readJWTFromStorage();
    if (stored && Date.now() < stored.expiresAt - 60_000) {
      this._jwtCache = stored; // promote to in-memory
      return stored.token;
    }

    // 3. Deduplicate concurrent callers — only one createJWT() at a time
    if (this._jwtInflight) return this._jwtInflight;

    this._jwtInflight = (async () => {
      try {
        const { account } = await import('../appwrite');
        const jwt = await account.createJWT();
        const expiresAt = Date.now() + 15 * 60 * 1000; // Appwrite JWTs last 15 min
        this._jwtCache = { token: jwt.jwt, expiresAt };
        this.writeJWTToStorage(jwt.jwt, expiresAt);
        return jwt.jwt;
      } catch {
        this._jwtCache = null;
        return null;
      } finally {
        this._jwtInflight = null;
      }
    })();

    return this._jwtInflight;
  }

  /**
   * Handle unauthorized responses (401) by redirecting to login
   */
  private handleUnauthorized(): void {
    if (typeof window === 'undefined') {
      return;
    }

    // Clear JWT cache so the next session gets a fresh token.
    this._jwtCache = null;
    this._jwtInflight = null;
    this.clearJWTStorage();

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
      console.log('[APIClient] Cache cleared');
    }
  }

  /**
   * Pre-warm the JWT cache so the first API call after login doesn't block
   * on a separate account.createJWT() round-trip. Call this once after auth
   * resolves, before rendering children that will fire immediate API requests.
   */
  async warmJWTCache(): Promise<void> {
    // fire-and-forget — caller must NOT await this (AuthContext calls it without await)
    if (!this._jwtInflight) this.getJWTToken();
  }

  /**
   * Clear session-specific caches
   */
  clearSessionCache(sessionId?: string): void {
    if (sessionId) {
      // Clear specific session caches
      this.cache.delete(`/api/sessions/${sessionId}`);
      this.cache.delete(`/sessions/${sessionId}`);
    } else {
      // Clear all session-related caches using pattern matching
      this.cache.clearPattern(/\/(sessions|messages)\//);
    }
    if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
      console.log(`[APIClient] Session cache cleared ${sessionId ? `for ${sessionId}` : '(all)'}`);
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

// Clear session caches on module load to ensure fresh data
if (typeof window !== 'undefined') {
  apiClient.clearSessionCache();
}
