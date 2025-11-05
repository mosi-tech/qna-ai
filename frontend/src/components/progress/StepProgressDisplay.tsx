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
    
    // Parse timestamp - handle both number and string formats
    let logTimestamp: number;
    if (typeof log.timestamp === 'string') {
      // Handle timestamps like "2025-11-05T20:45:33.285000"
      // Add 'Z' if missing to ensure UTC interpretation, and truncate microseconds to milliseconds
      let timestampStr = log.timestamp;
      
      // Truncate microseconds to milliseconds (keep only 3 digits after decimal)
      if (timestampStr.includes('.') && timestampStr.length > 23) {
        const [datePart, timePart] = timestampStr.split('.');
        timestampStr = `${datePart}.${timePart.substring(0, 3)}`;
      }
      
      // Add Z if not already present to ensure UTC interpretation
      if (!timestampStr.endsWith('Z') && !timestampStr.includes('+') && !timestampStr.includes('-', 19)) {
        timestampStr += 'Z';
      }
      
      logTimestamp = new Date(timestampStr).getTime();
      
      // Debug the parsing
      if (index === logs.length - 1) {
        console.log(`[Timestamp Parse] Original: "${log.timestamp}" -> Processed: "${timestampStr}" -> Parsed: ${logTimestamp}`);
      }
    } else {
      logTimestamp = log.timestamp;
    }
    
    // Check if parsing failed
    if (isNaN(logTimestamp)) {
      console.warn(`[Timer] Invalid timestamp for log ${index}:`, log.timestamp);
      return 'unknown';
    }
    
    // Check if this is a historical log (more than 1 minute old to be safer)
    const timeDiff = currentTime - logTimestamp;
    const isHistorical = timeDiff > 60 * 1000; // 1 minute
    
    // Handle negative time differences (future timestamps due to clock skew)
    const isFuture = timeDiff < 0;
    
    // Debug logging for timer issues (only for last log to reduce spam)
    if (index === logs.length - 1) {
      console.log(`[Timer Debug] Log ${index}: original=${log.timestamp}, parsed=${logTimestamp}, currentTime=${currentTime}, timeDiff=${timeDiff}ms, isHistorical=${isHistorical}, isFuture=${isFuture}, isProcessing=${isProcessing}`);
    }
    
    // If this is the last log and still processing, show elapsed time from this step start
    if (index === logs.length - 1 && isProcessing) {
      // If timestamp is in the future (clock skew), show "0s" and start counting from now
      if (isFuture) {
        return '0s';
      }
      
      // Only show live timer for recent logs, not historical ones
      if (isHistorical) {
        return 'completed';
      }
      
      const stepElapsed = Math.floor(timeDiff / 1000);
      return stepElapsed > 0 ? `${stepElapsed}s` : '0s';
    }
    
    // If there's a next log, calculate duration between this step and next step
    if (index < logs.length - 1) {
      const nextLog = logs[index + 1];
      let nextLogTimestamp: number;
      
      if (typeof nextLog.timestamp === 'string') {
        // Apply same parsing logic for consistency
        let nextTimestampStr = nextLog.timestamp;
        
        // Truncate microseconds to milliseconds
        if (nextTimestampStr.includes('.') && nextTimestampStr.length > 23) {
          const [datePart, timePart] = nextTimestampStr.split('.');
          nextTimestampStr = `${datePart}.${timePart.substring(0, 3)}`;
        }
        
        // Add Z if not already present
        if (!nextTimestampStr.endsWith('Z') && !nextTimestampStr.includes('+') && !nextTimestampStr.includes('-', 19)) {
          nextTimestampStr += 'Z';
        }
        
        nextLogTimestamp = new Date(nextTimestampStr).getTime();
      } else {
        nextLogTimestamp = nextLog.timestamp;
      }
      
      if (isNaN(nextLogTimestamp)) {
        return '0s';
      }
      
      const stepDuration = Math.floor((nextLogTimestamp - logTimestamp) / 1000);
      
      // Debug for older logs showing duration between consecutive logs
      if (index <= 2) { // Debug first few logs
        console.log(`[Step Duration] Log ${index}: ${logTimestamp} -> ${nextLogTimestamp} = ${stepDuration}s`);
      }
      
      return stepDuration > 0 ? `${stepDuration}s` : '0s';
    }
    
    // For completed steps without a next step, show final duration
    return isHistorical ? 'completed' : '0s';
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