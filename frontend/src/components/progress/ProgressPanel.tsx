'use client';

import React, { useEffect, useRef } from 'react';
import { ProgressLog } from '@/lib/progress/ProgressManager';

interface ProgressPanelProps {
  logs: ProgressLog[];
  isConnected: boolean;
  isProcessing?: boolean;
  onClear?: () => void;
}

export default function ProgressPanel({
  logs,
  isConnected,
  isProcessing = false,
  onClear,
}: ProgressPanelProps) {
  const logsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const getLogColor = (level: ProgressLog['level']) => {
    switch (level) {
      case 'success':
        return 'text-green-700 bg-green-50';
      case 'error':
        return 'text-red-700 bg-red-50';
      case 'warning':
        return 'text-yellow-700 bg-yellow-50';
      default:
        return 'text-gray-700 bg-gray-50';
    }
  };

  const getLogIcon = (level: ProgressLog['level']) => {
    switch (level) {
      case 'success':
        return '✓';
      case 'error':
        return '✕';
      case 'warning':
        return '⚠';
      default:
        return '•';
    }
  };

  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true,
    });
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 text-gray-100 font-mono text-sm">
      <div className="flex items-center justify-between p-3 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-gray-500'}`} />
          <span className="text-xs font-semibold">
            {isProcessing ? 'Analyzing...' : 'Ready'}
          </span>
          {isProcessing && <span className="animate-pulse ml-1">⟳</span>}
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{logs.length} steps</span>
          {onClear && logs.length > 0 && (
            <button
              onClick={onClear}
              className="px-2 py-1 text-xs bg-gray-700 hover:bg-gray-600 rounded text-gray-300"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-1">
        {logs.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <p className="text-xs mb-1">No progress logs yet</p>
              <p className="text-xs text-gray-600">Ask a question to see execution steps</p>
            </div>
          </div>
        ) : (
          logs.map((log) => (
            <div key={log.id} className={`px-2 py-1 rounded ${getLogColor(log.level)}`}>
              <div className="flex items-start gap-2">
                <span className="flex-shrink-0 w-4 text-center">{getLogIcon(log.level)}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <span className="break-words text-xs leading-relaxed">{log.message}</span>
                    <span className="text-xs opacity-60 flex-shrink-0">{formatTime(log.timestamp)}</span>
                  </div>
                  {log.step && log.totalSteps && (
                    <div className="mt-1 text-xs opacity-75">
                      Step {log.step} of {log.totalSteps}
                    </div>
                  )}
                  {log.details && Object.keys(log.details).length > 0 && (
                    <div className="mt-1 text-xs opacity-60 pl-2 border-l border-current">
                      {Object.entries(log.details)
                        .map(([key, value]) => `${key}: ${JSON.stringify(value)}`)
                        .join(' | ')}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={logsEndRef} />
      </div>
    </div>
  );
}
