export interface ProgressLog {
  id: string;
  timestamp: number;
  level: 'info' | 'success' | 'warning' | 'error';
  message: string;
  step?: number;
  totalSteps?: number;
  details?: Record<string, unknown>;
}

export interface ProgressEvent {
  type: 'log' | 'complete' | 'error';
  data: ProgressLog;
}

const progressStore = new Map<string, ProgressLog[]>();
const listeners = new Map<string, Set<(log: ProgressLog) => void>>();

export const ProgressManager = {
  addLog(sessionId: string, log: Omit<ProgressLog, 'id' | 'timestamp'>) {
    const progressLog: ProgressLog = {
      ...log,
      id: `${sessionId}-${Date.now()}-${Math.random()}`,
      timestamp: Date.now(),
    };

    if (!progressStore.has(sessionId)) {
      progressStore.set(sessionId, []);
    }

    progressStore.get(sessionId)!.push(progressLog);
    this.notifyListeners(sessionId, progressLog);
    return progressLog;
  },

  getLogs(sessionId: string): ProgressLog[] {
    return progressStore.get(sessionId) || [];
  },

  subscribe(sessionId: string, callback: (log: ProgressLog) => void): () => void {
    if (!listeners.has(sessionId)) {
      listeners.set(sessionId, new Set());
    }

    listeners.get(sessionId)!.add(callback);

    return () => {
      listeners.get(sessionId)?.delete(callback);
    };
  },

  private notifyListeners(sessionId: string, log: ProgressLog) {
    listeners.get(sessionId)?.forEach((callback) => {
      try {
        callback(log);
      } catch (err) {
        console.error('Progress listener error:', err);
      }
    });
  },

  clear(sessionId: string) {
    progressStore.delete(sessionId);
    listeners.delete(sessionId);
  },
};
