/**
 * Cache Management for API Responses
 */

import { CachedResponse } from './types';

/**
 * In-memory cache for API responses
 */
class CacheStore {
  private store: Map<string, CachedResponse> = new Map();

  /**
   * Set cache entry
   */
  set<T = unknown>(key: string, data: T, ttlMs: number = 60000): void {
    this.store.set(key, {
      data,
      timestamp: Date.now(),
      ttl: ttlMs,
    });
  }

  /**
   * Get cache entry if not expired
   */
  get<T = unknown>(key: string): T | null {
    const entry = this.store.get(key);

    if (!entry) {
      return null;
    }

    const age = Date.now() - entry.timestamp;

    if (age > entry.ttl) {
      this.store.delete(key);
      return null;
    }

    return entry.data as T;
  }

  /**
   * Check if key exists and is valid
   */
  has(key: string): boolean {
    return this.get(key) !== null;
  }

  /**
   * Remove cache entry
   */
  delete(key: string): boolean {
    return this.store.delete(key);
  }

  /**
   * Clear all cache entries
   */
  clear(): void {
    this.store.clear();
  }

  /**
   * Get all valid cache keys
   */
  keys(): string[] {
    return Array.from(this.store.keys()).filter(key => this.has(key));
  }

  /**
   * Get cache statistics
   */
  stats(): {
    totalEntries: number;
    validEntries: number;
    expiredEntries: number;
  } {
    const validKeys = this.keys();
    const totalEntries = this.store.size;
    const validEntries = validKeys.length;
    const expiredEntries = totalEntries - validEntries;

    return {
      totalEntries,
      validEntries,
      expiredEntries,
    };
  }
}

/**
 * Browser storage cache (localStorage)
 */
class StorageCache {
  private prefix = 'api_cache_';

  /**
   * Set cache entry in localStorage
   */
  set<T = any>(
    key: string,
    data: T,
    ttlMs: number = 3600000 // 1 hour
  ): void {
    try {
      const entry: CachedResponse<T> = {
        data,
        timestamp: Date.now(),
        ttl: ttlMs,
      };
      const cacheKey = this.prefix + key;
      localStorage.setItem(cacheKey, JSON.stringify(entry));
    } catch (error) {
      console.warn('Failed to set storage cache:', error);
    }
  }

  /**
   * Get cache entry from localStorage if not expired
   */
  get<T = any>(key: string): T | null {
    try {
      const cacheKey = this.prefix + key;
      const item = localStorage.getItem(cacheKey);

      if (!item) {
        return null;
      }

      const entry: CachedResponse<T> = JSON.parse(item);
      const age = Date.now() - entry.timestamp;

      if (age > entry.ttl) {
        localStorage.removeItem(cacheKey);
        return null;
      }

      return entry.data;
    } catch (error) {
      console.warn('Failed to get storage cache:', error);
      return null;
    }
  }

  /**
   * Check if key exists
   */
  has(key: string): boolean {
    return this.get(key) !== null;
  }

  /**
   * Remove cache entry
   */
  delete(key: string): void {
    try {
      const cacheKey = this.prefix + key;
      localStorage.removeItem(cacheKey);
    } catch (error) {
      console.warn('Failed to delete storage cache:', error);
    }
  }

  /**
   * Clear all cache entries
   */
  clear(): void {
    try {
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith(this.prefix)) {
          localStorage.removeItem(key);
        }
      });
    } catch (error) {
      console.warn('Failed to clear storage cache:', error);
    }
  }
}

/**
 * Cache key generators
 */
export const cacheKeys = {
  // Session cache
  session: (sessionId: string) => `session:${sessionId}`,
  sessionContext: (sessionId: string) => `context:${sessionId}`,

  // Analysis cache
  analysis: (question: string) => `analysis:${hashString(question)}`,
  search: (query: string) => `search:${hashString(query)}`,

  // Autocomplete cache
  autocomplete: (query: string) => `autocomplete:${hashString(query)}`,
};

/**
 * Cache TTL constants (in milliseconds)
 */
export const CACHE_TTL = {
  SHORT: 5 * 60 * 1000, // 5 minutes
  MEDIUM: 15 * 60 * 1000, // 15 minutes
  LONG: 1 * 60 * 60 * 1000, // 1 hour
  VERY_LONG: 24 * 60 * 60 * 1000, // 24 hours
} as const;

/**
 * Simple hash function for cache keys
 */
function hashString(str: string): string {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return Math.abs(hash).toString(16);
}

/**
 * Create cache manager with both memory and storage
 */
export class CacheManager {
  private memoryCache: CacheStore;
  private storageCache: StorageCache;

  constructor(
    private memoryTTL: number = CACHE_TTL.MEDIUM,
    private storageTTL: number = CACHE_TTL.LONG
  ) {
    this.memoryCache = new CacheStore();
    this.storageCache = new StorageCache();
  }

  /**
   * Set cache in both memory and storage
   */
  set<T = any>(key: string, data: T, level: 'memory' | 'storage' | 'both' = 'both'): void {
    if (level === 'memory' || level === 'both') {
      this.memoryCache.set(key, data, this.memoryTTL);
    }
    if (level === 'storage' || level === 'both') {
      this.storageCache.set(key, data, this.storageTTL);
    }
  }

  /**
   * Get cache from memory first, then storage
   */
  get<T = any>(key: string): T | null {
    // Try memory cache first
    const memoryValue = this.memoryCache.get<T>(key);
    if (memoryValue !== null) {
      return memoryValue;
    }

    // Try storage cache
    const storageValue = this.storageCache.get<T>(key);
    if (storageValue !== null) {
      // Restore to memory cache
      this.memoryCache.set(key, storageValue, this.memoryTTL);
      return storageValue;
    }

    return null;
  }

  /**
   * Check if cache exists
   */
  has(key: string): boolean {
    return this.memoryCache.has(key) || this.storageCache.has(key);
  }

  /**
   * Delete from both caches
   */
  delete(key: string): void {
    this.memoryCache.delete(key);
    this.storageCache.delete(key);
  }

  /**
   * Clear both caches
   */
  clear(): void {
    this.memoryCache.clear();
    this.storageCache.clear();
  }

  /**
   * Clear specific patterns
   */
  clearPattern(pattern: RegExp): void {
    const memoryKeys = this.memoryCache.keys();
    memoryKeys.forEach(key => {
      if (pattern.test(key)) {
        this.memoryCache.delete(key);
      }
    });

    // Note: Can't easily iterate localStorage, so we clear storage on pattern match
    // In production, consider using a more sophisticated approach
  }

  /**
   * Get cache statistics
   */
  getStats() {
    return {
      memory: this.memoryCache.stats(),
    };
  }
}

// Create singleton instance
export const defaultCache = new CacheManager();
