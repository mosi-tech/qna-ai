'use client';

import { ProgressLog } from '@/lib/progress/ProgressManager';

interface OldProgressDisplayProps {
  isProcessing: boolean;
  progressLogs: ProgressLog[];
}

/**
 * @deprecated This component is no longer used.
 * Progress display is now handled within individual ChatMessage components.
 * Keeping this for reference only - do not use in new code.
 */
export default function OldProgressDisplay({ isProcessing, progressLogs }: OldProgressDisplayProps) {
  const getElapsedTime = (log: ProgressLog, idx: number) => {
    if (idx === 0) return null;
    const prevLog = progressLogs[idx - 1];
    if (!prevLog) return null;
    
    const currentTime = new Date(log.timestamp).getTime();
    const prevTime = new Date(prevLog.timestamp).getTime();
    const diff = Math.abs(currentTime - prevTime);
    
    if (diff < 1000) return `${diff}ms`;
    return `${Math.round(diff / 1000)}s`;
  };

  if (!isProcessing) return null;

  return (
    <div className="flex gap-3">
      <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
        <div className="w-4 h-4 border-2 border-gray-400 border-t-gray-600 rounded-full animate-spin"></div>
      </div>
      <div className="bg-gray-100 rounded-lg p-3 max-w-2xl flex-1">
        <div className="space-y-2">
          {progressLogs.length > 0 ? (
            <>
              {progressLogs.map((log, idx) => {
                const elapsedTime = getElapsedTime(log, idx);
                return (
                  <div key={log.id || `log-${idx}-${log.timestamp}`} className="text-sm text-gray-700 flex items-start gap-2">
                    <span className="flex-shrink-0 mt-0.5">
                      {log.level === 'success' && <span className="text-green-600">✓</span>}
                      {log.level === 'error' && <span className="text-red-600">✕</span>}
                      {log.level === 'warning' && <span className="text-yellow-600">⚠</span>}
                      {log.level === 'info' && <span className="text-blue-600">•</span>}
                    </span>
                    <div className="flex-1">
                      <div className="flex items-center gap-1">
                        <span>{log.message}</span>
                        {elapsedTime && <span className="font-semibold text-blue-600">{elapsedTime}</span>}
                      </div>
                      {log.step && log.totalSteps && (
                        <span className="text-xs text-gray-500 ml-2">
                          (Step {log.step}/{log.totalSteps})
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </>
          ) : (
            <p className="text-sm text-gray-600">Analyzing...</p>
          )}
        </div>
      </div>
    </div>
  );
}