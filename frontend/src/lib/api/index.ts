/**
 * API Client Library
 * Exports all API-related types, clients, and services
 */

// Types
export * from './types';

// Errors
export * from './errors';

// Cache
export { defaultCache, cacheKeys, CACHE_TTL, CacheManager } from './cache';

// Client
export { APIClient, createAPIClient, apiClient } from './client';

// Services
export { AnalysisService, createAnalysisService } from './analysis';
export { SessionService, createSessionService } from './session';

// Factory to create all services at once
import { APIClient, apiClient } from './client';
import { AnalysisService, createAnalysisService } from './analysis';
import { SessionService, createSessionService } from './session';

export interface APIServices {
  client: APIClient;
  analysis: AnalysisService;
  session: SessionService;
}

/**
 * Create all API services with custom client
 */
export function createAPIServices(client: APIClient = apiClient): APIServices {
  return {
    client,
    analysis: createAnalysisService(client),
    session: createSessionService(client),
  };
}

/**
 * Global API services instance
 */
export const api = createAPIServices(apiClient);
