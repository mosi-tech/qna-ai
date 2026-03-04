'use client';

import { useState, useEffect } from 'react';
import { AnalysisRun } from '@/types/parameters';
import { api } from '@/lib/api';

interface HistorySectionProps {
  runs: AnalysisRun[];
  activeRunId?: string;
  onSelectRun: (runId: string) => void;
  analysisId?: string;
  sessionId?: string;
}

export default function HistorySection({ runs, activeRunId, onSelectRun, analysisId, sessionId }: HistorySectionProps) {
  const [backendExecutions, setBackendExecutions] = useState<any[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  
  // Load execution history from backend (all executions for workspace)
  useEffect(() => {
    const loadBackendExecutions = async () => {
      if (!analysisId) return;
      
      setIsLoadingHistory(true);
      try {
        console.log('Loading all execution history for analysis:', analysisId);
        // Get all executions for the workspace (primary + user re-runs)
        const executions = await api.analysis.getAnalysisExecutions(analysisId, 10, 'all');
        console.log('Loaded all executions:', executions);
        setBackendExecutions(executions || []);
      } catch (error) {
        console.error('Failed to load execution history:', error);
        setBackendExecutions([]);
      } finally {
        setIsLoadingHistory(false);
      }
    };
    
    loadBackendExecutions();
  }, [analysisId]);

  const formatTimeAgo = (date: Date): string => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
  };

  const getParameterSummary = (parameters: Record<string, any>): string => {
    const summary: string[] = [];
    
    if (parameters.symbol) summary.push(`${parameters.symbol}`);
    if (parameters.period) summary.push(`${parameters.period}d`);
    if (parameters.volume_filter) summary.push(`${parameters.volume_filter}+ vol`);
    
    return summary.join(', ') || 'Default parameters';
  };

  const exportHistory = () => {
    const historyData = {
      exported_at: new Date().toISOString(),
      total_executions: totalExecutions,
      executions: allExecutions.map(execution => ({
        executionId: execution.executionId,
        parameters: execution.parameters,
        results: execution.results,
        status: execution.status,
        duration: execution.duration,
        created_at: execution.createdAt,
        source: execution.source,
        error: execution.error
      }))
    };
    
    const dataStr = JSON.stringify(historyData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `analysis-history-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Combine and sort all executions
  const allExecutions = [
    // Convert local runs to execution format
    ...runs.map(run => ({
      executionId: run.id,
      parameters: run.parameters,
      status: run.status,
      results: run.results,
      createdAt: run.createdAt.toISOString(),
      duration: run.duration,
      error: run.error,
      source: 'local' as const
    })),
    // Add backend executions
    ...backendExecutions.map(exec => ({
      ...exec,
      createdAt: exec.createdAt || exec.created_at,
      source: 'backend' as const
    }))
  ].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());

  const totalExecutions = allExecutions.length;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">History</h2>
        <div className="flex items-center gap-2">
          {isLoadingHistory && (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          )}
          {totalExecutions > 0 && (
            <span className="text-sm text-gray-500">
              {totalExecutions} execution{totalExecutions !== 1 ? 's' : ''}
            </span>
          )}
        </div>
      </div>

      {totalExecutions === 0 && !isLoadingHistory ? (
        <div className="flex flex-col items-center justify-center py-8 text-gray-500">
          <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mb-3">
            <span className="text-xl">📋</span>
          </div>
          <p>No analysis history</p>
          <p className="text-sm mt-1">Previous runs will appear here</p>
        </div>
      ) : (
        <div className="space-y-3">
          {allExecutions.map((execution, index) => {
            const isActive = execution.executionId === activeRunId;
            const executionNumber = index + 1;
            const createdAt = new Date(execution.createdAt);
            
            return (
              <div
                key={execution.executionId}
                onClick={() => onSelectRun(execution.executionId)}
                className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                  isActive 
                    ? 'bg-blue-50 border-blue-200 ring-1 ring-blue-500' 
                    : 'border-gray-200 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${
                      isActive ? 'bg-blue-500' : 'bg-gray-400'
                    }`} />
                    <span className="font-medium text-sm">
                      Execution #{executionNumber}
                      {index === 0 && ' (Latest)'}
                    </span>
                    <div className={`px-2 py-1 rounded-full text-xs ${
                      execution.status === 'completed' || execution.status === 'success' ? 'bg-green-100 text-green-800' :
                      execution.status === 'failed' || execution.status === 'error' ? 'bg-red-100 text-red-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {execution.status}
                    </div>
                    {execution.source === 'backend' && (
                      <div className="px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                        Historical
                      </div>
                    )}
                  </div>
                  <span className="text-xs text-gray-500">
                    {formatTimeAgo(createdAt)}
                  </span>
                </div>
                
                <p className="text-sm text-gray-600 mt-1">
                  {getParameterSummary(execution.parameters)}
                </p>
                
                {execution.duration && (
                  <p className="text-xs text-gray-500 mt-1">
                    Completed in {(execution.duration / 1000).toFixed(1)}s
                  </p>
                )}
                
                {execution.error && (
                  <p className="text-xs text-red-600 mt-1">
                    Error: {execution.error}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}

      {totalExecutions > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200 flex gap-2">
          <button 
            onClick={exportHistory}
            className="px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            📥 Export History
          </button>
          <button 
            onClick={() => {
              // Future: Clear history with confirmation
              console.log('Clear history');
            }}
            className="px-3 py-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
          >
            🗑️ Clear
          </button>
        </div>
      )}
    </div>
  );
}