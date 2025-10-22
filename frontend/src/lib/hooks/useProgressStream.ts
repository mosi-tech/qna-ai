import { useEffect, useState, useCallback, useRef } from 'react';
import { ProgressLog, ProgressManager } from '@/lib/progress/ProgressManager';

export const useProgressStream = (sessionId: string | null) => {
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
      if (reconnectAttemptsRef.current < 5) {
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

    console.log('[useProgressStream] Connecting to backend for session:', sessionId);
    setIsConnected(true);
    setError(null);

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const progressUrl = `${apiUrl}/api/progress/${sessionId}`;
    
    console.log('[useProgressStream] Progress URL:', progressUrl);

    try {
      eventSourceRef.current = new EventSource(progressUrl);

      eventSourceRef.current.onopen = () => {
        console.log('[useProgressStream] ✓ SSE stream opened');
        setIsConnected(true);
        reconnectAttemptsRef.current = 0;
        setError(null);
        resetHeartbeatTimer();
      };

      eventSourceRef.current.onmessage = (event) => {
        console.log('[useProgressStream] RAW event received:', event.data);
        resetHeartbeatTimer();
        
        try {
          const data = JSON.parse(event.data);
          console.log('[useProgressStream] PARSED event:', data);

          if (data.type === 'connected') {
            console.log('[useProgressStream] Backend confirmed connection for session:', sessionId);
            console.log('%c🔗 SSE Connected!', 'color: green; font-weight: bold');
            return;
          }

          if (data.type === 'heartbeat') {
            console.log('[useProgressStream] 💓 Heartbeat received');
            return;
          }

          let timestamp = Date.now();
          if (data.timestamp) {
            if (typeof data.timestamp === 'number') {
              timestamp = data.timestamp;
            } else {
              const parsed = new Date(data.timestamp).getTime();
              timestamp = isNaN(parsed) ? Date.now() : parsed;
              console.log(`[useProgressStream] Parsed timestamp: "${data.timestamp}" -> ${timestamp}`);
            }
          }

          const progressLog: ProgressLog = {
            id: data.id || `${Date.now()}-${Math.random()}`,
            timestamp: timestamp,
            level: data.level || 'info',
            message: data.message,
            step: data.step,
            totalSteps: data.totalSteps,
            details: data.details,
          };

          console.log(`%c✓ ${progressLog.message}`, `color: ${progressLog.level === 'success' ? 'green' : progressLog.level === 'error' ? 'red' : 'blue'}; font-weight: bold`);
          console.log('[useProgressStream] Adding log:', progressLog.message);
          setLogs((prev) => {
            const updated = [...prev, progressLog];
            console.log(`%c📊 Progress logs count: ${updated.length}`, 'color: cyan');
            return updated;
          });
          ProgressManager.addLog(sessionId, {
            level: progressLog.level as any,
            message: progressLog.message,
            step: progressLog.step,
            totalSteps: progressLog.totalSteps,
            details: progressLog.details,
          });
        } catch (err) {
          console.error('[useProgressStream] Error parsing progress event:', err, event.data);
        }
      };

      eventSourceRef.current.onerror = (err) => {
        console.error('[useProgressStream] ✕ SSE stream error:', err);
        setIsConnected(false);
        if (eventSourceRef.current) {
          eventSourceRef.current.close();
          eventSourceRef.current = null;
        }
        if (heartbeatTimeoutRef.current) {
          clearTimeout(heartbeatTimeoutRef.current);
        }

        if (reconnectAttemptsRef.current < 5) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 10000);
          console.log(`[useProgressStream] Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current + 1}/5)`);
          setError(`Connection lost. Reconnecting in ${delay / 1000}s...`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++;
            connectToBackend();
          }, delay);
        } else {
          setError('Connection lost. Max reconnection attempts reached.');
          console.error('[useProgressStream] Max reconnection attempts reached');
        }
      };
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to connect to progress stream';
      setError(errorMsg);
      setIsConnected(false);
      console.error('[useProgressStream] Failed to create EventSource:', err);
    }
  }, [sessionId]);

  const clearLogs = useCallback(async () => {
    setLogs([]);
    if (sessionId) {
      ProgressManager.clear(sessionId);
    }
  }, [sessionId]);

  useEffect(() => {
    if (!sessionId) {
      setIsConnected(false);
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      if (heartbeatTimeoutRef.current) {
        clearTimeout(heartbeatTimeoutRef.current);
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      return;
    }

    connectToBackend();

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      if (heartbeatTimeoutRef.current) {
        clearTimeout(heartbeatTimeoutRef.current);
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      setIsConnected(false);
    };
  }, [sessionId, connectToBackend, resetHeartbeatTimer]);

  return {
    logs,
    isConnected,
    error,
    clearLogs,
    addLog: (log: Omit<ProgressLog, 'id' | 'timestamp'>) => {
      if (sessionId) {
        return ProgressManager.addLog(sessionId, log);
      }
    },
  };
};
