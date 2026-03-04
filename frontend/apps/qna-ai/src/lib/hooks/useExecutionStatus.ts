import { useEffect, useState, useCallback } from 'react';
import { useProgressSafe } from '@/lib/context/ProgressContext';

interface ExecutionStatus {
  status: 'pending' | 'queued' | 'running' | 'completed' | 'failed';
  progress: string;
  logs: string[];
  results?: any;
  markdown?: string;
  error?: string;
}

export const useExecutionStatus = (sessionId: string | null, executionId: string | null) => {
  const { logs: allProgressLogs } = useProgressSafe();
  const [executionStatus, setExecutionStatus] = useState<ExecutionStatus>({
    status: 'pending',
    progress: 'Analysis queued for execution...',
    logs: []
  });

  // Filter and process execution-specific events
  useEffect(() => {
    if (!executionId || !allProgressLogs.length) return;

    // Debug log to see event structure
    console.log('[useExecutionStatus] Looking for executionId:', executionId);
    console.log('[useExecutionStatus] All progress logs:', allProgressLogs);

    // Find events related to this execution
    const executionEvents = allProgressLogs.filter(log => {
      const matchesExecId = log.details?.execution_id === executionId ||
        log.details?.executionId === executionId ||
        log.message?.includes(executionId);

      if (matchesExecId) {
        console.log('[useExecutionStatus] Found matching event:', log);
      }

      return matchesExecId;
    });

    console.log('[useExecutionStatus] Filtered execution events:', executionEvents);

    if (executionEvents.length === 0) return;

    // Process the latest execution event
    const latestEvent = executionEvents[executionEvents.length - 1];
    const eventDetails = latestEvent.details || {};

    // Update execution status based on event
    setExecutionStatus(prev => {
      const newStatus: ExecutionStatus = { ...prev };

      // Update status from event details or infer from message
      if (eventDetails.status) {
        newStatus.status = eventDetails.status;
      } else if (latestEvent.message?.includes('queued')) {
        newStatus.status = 'queued';
      } else if (latestEvent.message?.includes('running')) {
        newStatus.status = 'running';
      } else if (latestEvent.message?.includes('completed')) {
        newStatus.status = 'completed';
      } else if (latestEvent.message?.includes('failed')) {
        newStatus.status = 'failed';
      }

      // Update progress message
      newStatus.progress = latestEvent.message || prev.progress;

      // Add to logs if it's a new message
      if (!prev.logs.includes(latestEvent.message)) {
        newStatus.logs = [...prev.logs, latestEvent.message];
      }

      // Extract results and markdown if execution completed
      if (newStatus.status === 'completed' && eventDetails.result) {
        newStatus.results = eventDetails.result;
      }

      // Extract error if execution failed
      if (newStatus.status === 'failed' && eventDetails.error) {
        newStatus.error = eventDetails.error;
      }

      return newStatus;
    });
  }, [allProgressLogs, executionId]);

  // Function to refresh execution data (useful when status is completed)
  const refreshExecutionData = useCallback(async () => {
    if (!executionId || executionStatus.status !== 'completed') return;

    try {
      // Make API call to get latest execution results
      const response = await fetch(`/api/executions/${executionId}`);
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.execution) {
          setExecutionStatus(prev => ({
            ...prev,
            results: data.execution.result?.results,
            markdown: data.execution.result?.markdown,
          }));
        }
      }
    } catch (error) {
      console.error('Failed to refresh execution data:', error);
    }
  }, [executionId, executionStatus.status]);

  return {
    executionStatus,
    refreshExecutionData,
    isExecuting: executionStatus.status === 'running' || executionStatus.status === 'queued',
    isCompleted: executionStatus.status === 'completed',
    hasFailed: executionStatus.status === 'failed',
  };
};