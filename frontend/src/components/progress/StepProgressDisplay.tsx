'use client';

import React, { useState, useEffect } from 'react';
import { ProgressLog } from '@/lib/progress/ProgressManager';

interface StepProgressDisplayProps {
  logs: ProgressLog[];
  isProcessing: boolean;
}

export default function StepProgressDisplay({ logs, isProcessing }: StepProgressDisplayProps) {
  const [, setUpdateTrigger] = useState(0);

  // Update timer every second
  useEffect(() => {
    if (!isProcessing || logs.length === 0) return;
    
    const timer = setInterval(() => {
      setUpdateTrigger(prev => prev + 1);
    }, 1000);
    
    return () => clearInterval(timer);
  }, [isProcessing, logs.length]);

  const getStepDuration = (log: ProgressLog, index: number) => {
    const currentTime = Date.now();
    
    // If this is the last log and still processing, show elapsed time from this step start
    if (index === logs.length - 1 && isProcessing) {
      const stepElapsed = Math.floor((currentTime - log.timestamp) / 1000);
      return stepElapsed > 0 ? `${stepElapsed}s` : '0s';
    }
    
    // If there's a next log, calculate duration between this step and next step
    if (index < logs.length - 1) {
      const nextLog = logs[index + 1];
      const stepDuration = Math.floor((nextLog.timestamp - log.timestamp) / 1000);
      return stepDuration > 0 ? `${stepDuration}s` : '0s';
    }
    
    // For completed steps without a next step, show final duration
    return '0s';
  };

  if (logs.length === 0) {
    return (
      <div className="text-gray-500 text-sm text-center py-4">
        Waiting for analysis to start...
      </div>
    );
  }

  return (
    <div className="space-y-2 max-h-96 overflow-y-auto">
      {logs.map((log, index) => {
        const stepDuration = getStepDuration(log, index);
        const isCurrentStep = index === logs.length - 1 && isProcessing;
        
        return (
          <div key={log.id || `log-${index}-${log.timestamp}`} className="text-sm text-gray-700 flex items-start gap-2">
            <span className="flex-shrink-0 mt-0.5">
              {log.level === 'success' && <span className="text-green-600">✓</span>}
              {log.level === 'error' && <span className="text-red-600">✕</span>}
              {log.level === 'warning' && <span className="text-yellow-600">⚠</span>}
              {log.level === 'info' && <span className="text-blue-600">•</span>}
            </span>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="flex-1">{log.message}</span>
                <span className={`font-semibold ${isCurrentStep ? 'text-blue-600 animate-pulse' : 'text-gray-500'}`}>
                  {stepDuration}
                </span>
              </div>
              {log.step && log.totalSteps && (
                <span className="text-xs text-gray-500">
                  Step {log.step} of {log.totalSteps}
                </span>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}