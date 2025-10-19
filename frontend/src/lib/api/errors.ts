/**
 * Error Handling and Error Types
 */

import {
  APIError,
  NetworkError,
  TimeoutError,
  ValidationError,
  NotFoundError,
  UnauthorizedError,
} from './types';

/**
 * Determine if an error is an API error
 */
export function isAPIError(error: unknown): error is APIError {
  return error instanceof APIError;
}

/**
 * Get error message from various error types
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === 'string') {
    return error;
  }
  return 'An unknown error occurred';
}

/**
 * Parse error from API response
 */
export function parseAPIError(response: {
  status: number;
  data?: Record<string, any>;
}): APIError {
  const { status, data } = response;
  const message = data?.error || data?.message || 'API request failed';
  const details = data?.details;

  switch (status) {
    case 400:
      return new ValidationError(message, details);
    case 401:
      return new UnauthorizedError(message);
    case 404:
      return new NotFoundError(message);
    case 408:
    case 504:
      return new TimeoutError(message);
    default:
      return new APIError(message, status, details);
  }
}

/**
 * Determine if an error is retryable
 */
export function isRetryableError(error: unknown): boolean {
  if (!isAPIError(error)) {
    return error instanceof NetworkError || error instanceof TimeoutError;
  }

  if (error instanceof NetworkError || error instanceof TimeoutError) {
    return true;
  }

  // Retry on 5xx errors and 408/429 status codes
  if (error.statusCode) {
    return (
      (error.statusCode >= 500 && error.statusCode < 600) ||
      error.statusCode === 408 ||
      error.statusCode === 429
    );
  }

  return false;
}

/**
 * Format error for user display
 */
export function formatErrorForUser(error: unknown): string {
  if (error instanceof ValidationError) {
    return 'Please check your input and try again';
  }

  if (error instanceof UnauthorizedError) {
    return 'Your session has expired. Please log in again';
  }

  if (error instanceof NotFoundError) {
    return 'The requested resource was not found';
  }

  if (error instanceof NetworkError) {
    return 'Network error. Please check your connection and try again';
  }

  if (error instanceof TimeoutError) {
    return 'Request timed out. Please try again';
  }

  if (error instanceof APIError) {
    return error.message || 'An error occurred. Please try again';
  }

  return 'An unexpected error occurred. Please try again';
}

/**
 * Log error for debugging
 */
export function logError(
  context: string,
  error: unknown,
  additionalInfo?: Record<string, any>
): void {
  const timestamp = new Date().toISOString();
  const errorMessage = getErrorMessage(error);

  const logData = {
    timestamp,
    context,
    error: errorMessage,
    ...(isAPIError(error) && {
      statusCode: error.statusCode,
      details: error.details,
    }),
    ...additionalInfo,
  };

  if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
    console.error('[API Error]', logData);
  }

  // Send to error tracking service if available
  // e.g., Sentry, LogRocket, etc.
}

/**
 * Create a user-friendly error message with recovery suggestion
 */
export interface UserErrorMessage {
  title: string;
  message: string;
  suggestion?: string;
  isRetryable: boolean;
}

export function createUserErrorMessage(error: unknown): UserErrorMessage {
  const message = formatErrorForUser(error);
  const retryable = isRetryableError(error);

  if (error instanceof ValidationError) {
    return {
      title: 'Invalid Input',
      message,
      suggestion: 'Please correct the errors and try again',
      isRetryable: false,
    };
  }

  if (error instanceof UnauthorizedError) {
    return {
      title: 'Session Expired',
      message,
      suggestion: 'Please refresh the page to continue',
      isRetryable: false,
    };
  }

  if (error instanceof NetworkError || error instanceof TimeoutError) {
    return {
      title: retryable ? 'Connection Error' : 'Request Failed',
      message,
      suggestion: 'Please try again in a moment',
      isRetryable: retryable,
    };
  }

  return {
    title: 'Error',
    message,
    suggestion: retryable ? 'Please try again' : undefined,
    isRetryable: retryable,
  };
}
