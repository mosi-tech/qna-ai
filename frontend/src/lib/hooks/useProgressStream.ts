import { useEffect, useState, useCallback, useRef } from 'react';
import { ProgressLog, ProgressManager } from '@/lib/progress/ProgressManager';

export const useProgressStream = (sessionId: string | null, messageId?: string, onAnalysisComplete?: (status: 'completed' | 'failed', data?: any) => void) => {
  const [logs, setLogs] = useState<ProgressLog[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const heartbeatTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);

  const resetHeartbeatTimer = useCallback(() => {
    if (heartbeatTimeoutRef.current) {
      clearTimeout(heartbeatTimeoutRef.current);
    }
    heartbeatTimeoutRef.current = setTimeout(() => {
      console.error('[useProgressStream] No heartbeat for 15s - connection dead');
      setIsConnected(false);
      setError('Connection lost - no heartbeat');
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      if (reconnectAttemptsRef.current < 3) { // Reduced from 5 to 3 attempts
        const delay = 2000;
        console.log(`[useProgressStream] Reconnecting in ${delay}ms after heartbeat timeout`);
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectAttemptsRef.current++;
          connectToBackend();
        }, delay);
      }
    }, 15000);
  }, []);

  const connectToBackend = useCallback(() => {
    if (!sessionId) {
      console.log('[useProgressStream] No sessionId, skipping backend connection');
      return;
    }

    setIsConnected(false);
    setError(null);

    // Use Next.js API route as proxy to backend SSE
    const progressUrl = `/api/progress/${sessionId}`;
    

    try {
      // Close existing connection if any
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }

      eventSourceRef.current = new EventSource(progressUrl);

      eventSourceRef.current.onopen = () => {
        console.log('[useProgressStream] ✓ SSE stream opened');
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;
        setError(null);
        resetHeartbeatTimer();
      };

      eventSourceRef.current.onmessage = (event) => {
        resetHeartbeatTimer();
        
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'connected') {
            console.log('[useProgressStream] Backend confirmed connection for session:', sessionId);
            console.log('%c🔗 SSE Connected!', 'color: green; font-weight: bold');
            return;
          }

          if (data.type === 'heartbeat') {
            // Silent heartbeat - no logging
            return;
          }

          // Enhanced SSE event logging with specific event type highlighting
          const eventTypeStyle = 'color: blue; font-weight: bold;';
          const statusStyle = data.status === 'failed' ? 'color: red; font-weight: bold;' : 
                             data.status === 'completed' ? 'color: green; font-weight: bold;' : 
                             'color: orange; font-weight: bold;';
          
          console.log(`%c[SSE Event] ${data.type || 'unknown'}`, eventTypeStyle, data);
          
          // Log specific event types with enhanced visibility
          if (data.type === 'execution_status') {
            console.log(`%c[SSE] Execution Status: ${data.status}`, statusStyle, data);
          } else if (data.type === 'analysis_progress') {
            const statusInfo = data.status ? `data.status=${data.status}` : '';
            const detailsStatusInfo = data.details?.status ? `details.status=${data.details.status}` : '';
            const statusDisplay = [statusInfo, detailsStatusInfo].filter(Boolean).join(', ') || 'no status';
            console.log(`%c[SSE] Analysis Progress: ${statusDisplay}`, statusStyle, data);
          } else if (data.type === 'progress') {
            console.log(`%c[SSE] Progress: ${data.level}`, 'color: purple;', data);
          } else if (!data.type) {
            console.log(`%c[SSE] No Type - Raw Event:`, 'color: orange; font-weight: bold;', data);
          }

          // Handle analysis completion events
          if (data.type === 'analysis_complete' || data.type === 'execution_complete') {
            console.log('%c[SSE] ANALYSIS/EXECUTION COMPLETED!', 'color: red; font-size: 16px; font-weight: bold;', data);
            if (onAnalysisComplete) {
              onAnalysisComplete(data.status === 'success' ? 'completed' : 'failed', data);
            }
          }
          
          // Highlight and handle analysis error events (final failures)
          // Check both data.status and data.details.status for completion
          const analysisStatus = data.status || data.details?.status;
          const isAnalysisProgress = data.type === 'analysis_progress';
          
          if (isAnalysisProgress && analysisStatus === 'failed') {
            console.log('%c[SSE] FINAL ANALYSIS FAILURE!', 'color: red; font-size: 14px; font-weight: bold; background: yellow;', data);
            // Trigger completion callback for final analysis failures
            if (onAnalysisComplete) {
              onAnalysisComplete('failed', data);
            }
          }
          
          // Handle successful analysis completion
          if (isAnalysisProgress && analysisStatus === 'completed') {
            console.log('%c[SSE] ANALYSIS COMPLETED SUCCESSFULLY!', 'color: green; font-size: 14px; font-weight: bold;', data);
            if (onAnalysisComplete) {
              onAnalysisComplete('completed', data);
            }
          }
          
          // Handle execution completion (which may also signal analysis completion)
          if (data.type === 'execution_status' && data.status === 'completed') {
            console.log('%c[SSE] EXECUTION COMPLETED!', 'color: green; font-size: 14px; font-weight: bold;', data);
            // Note: execution completion doesn't necessarily mean analysis completion
            // Analysis completion is signaled by analysis_progress events
          }
          
          // CRITICAL: Universal completion detection
          // Look for completion indicators in details (correct structure)
          const eventStatus = data.details?.status;
          const messageId = data.details?.message_id;
          const isCompletionEvent = messageId && (eventStatus === 'failed' || eventStatus === 'completed');
          
          if (isCompletionEvent) {
            console.log('%c[SSE] COMPLETION EVENT DETECTED:', 'color: purple; font-weight: bold;', {
              eventStatus,
              messageId,
              level: data.level,
              eventType: data.type || 'no-type'
            });
            
            // Clean completion data - use the event as-is (no more flattening needed)
            const completionData = {
              ...data,
              // Ensure critical fields are accessible at top level for compatibility
              message_id: messageId,
              status: eventStatus,
              error: data.details?.error || (eventStatus === 'failed' ? data.message : undefined)
            };
            
            if (eventStatus === 'failed') {
              console.log('%c[SSE] ANALYSIS FAILURE!', 'color: red; font-size: 14px; font-weight: bold; background: yellow;', completionData);
              if (onAnalysisComplete) {
                onAnalysisComplete('failed', completionData);
              }
            } else if (eventStatus === 'completed') {
              console.log('%c[SSE] ANALYSIS SUCCESS!', 'color: green; font-size: 14px; font-weight: bold;', completionData);
              if (onAnalysisComplete) {
                onAnalysisComplete('completed', completionData);
              }
            }
          }
          
          // Highlight execution retries
          if (data.type === 'execution_status' && data.status === 'failed') {
            console.log('%c[SSE] Execution Failed (check if retry or final)', 'color: orange; font-weight: bold;', data);
          }

          let timestamp = Date.now();
          if (data.timestamp) {
            try {
              timestamp = new Date(data.timestamp).getTime();
            } catch (e) {
              console.warn('[useProgressStream] Invalid timestamp, using current time');
            }
          }

          const progressLog: ProgressLog = {
            id: data.id || `${sessionId}-${timestamp}-${Math.random()}`,
            timestamp,
            level: data.level || 'info',
            message: data.message || JSON.stringify(data),
            step: data.step,
            totalSteps: data.totalSteps,
            details: data.details || data,
          };

          setLogs(prev => [...prev, progressLog]);
          
          if (sessionId) {
            ProgressManager.addLog(sessionId, progressLog);
          }
        } catch (parseError) {
          console.error('[useProgressStream] Failed to parse event data:', parseError);
        }
      };

      eventSourceRef.current.onerror = (event) => {
        console.error('[useProgressStream] SSE error:', event);
        setIsConnected(false);
        
        if (eventSourceRef.current?.readyState === EventSource.CLOSED) {
          console.log('[useProgressStream] SSE connection closed');
          setError('Connection closed');
        } else {
          setError('Connection error');
          
          // Auto-reconnect with exponential backoff (limited attempts)
          if (reconnectAttemptsRef.current < 3) {
            const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 8000);
            console.log(`[useProgressStream] Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current + 1}/3)`);
            reconnectTimeoutRef.current = setTimeout(() => {
              reconnectAttemptsRef.current++;
              connectToBackend();
            }, delay);
          } else {
            console.log('[useProgressStream] Max reconnection attempts reached');
            setError('Connection failed - max attempts reached');
          }
        }
      };

    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to connect to progress stream';
      setError(errorMsg);
      setIsConnected(false);
      console.error('[useProgressStream] Failed to create EventSource:', err);
    }
  }, [sessionId, onAnalysisComplete, resetHeartbeatTimer]);

  const clearLogs = useCallback(() => {
    setLogs([]);
    if (sessionId) {
      ProgressManager.clear(sessionId);
    }
  }, [sessionId]);

  const addLog = useCallback((log: ProgressLog) => {
    setLogs(prev => [...prev, log]);
    if (sessionId) {
      return ProgressManager.addLog(sessionId, log);
    }
  }, [sessionId]);

  // Main effect for managing SSE connection
  useEffect(() => {
    if (!sessionId) {
      console.log('[useProgressStream] No session ID - cleaning up connection');
      setIsConnected(false);
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      if (heartbeatTimeoutRef.current) {
        clearTimeout(heartbeatTimeoutRef.current);
        heartbeatTimeoutRef.current = null;
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      return;
    }

    console.log('[useProgressStream] Starting SSE connection for session:', sessionId);
    connectToBackend();

    return () => {
      console.log('[useProgressStream] Cleaning up SSE connection for session:', sessionId);
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      if (heartbeatTimeoutRef.current) {
        clearTimeout(heartbeatTimeoutRef.current);
        heartbeatTimeoutRef.current = null;
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      setIsConnected(false);
    };
  }, [sessionId]);

  return {
    logs,
    isConnected,
    error,
    clearLogs,
    addLog,
  };
};