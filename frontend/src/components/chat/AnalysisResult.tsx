'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import MockOutput from '@/components/MockOutput';

interface AnalysisResultProps {
  messageId: string;
  question: string;
  results: any;
  expanded?: boolean;
  analysisId?: string;
  executionId?: string;
  onExecutionUpdate?: (update: any) => void;
}

export default function AnalysisResult({ 
  messageId, 
  question, 
  results, 
  expanded = false,
  analysisId,
  executionId,
  onExecutionUpdate
}: AnalysisResultProps) {
  const router = useRouter();
  // Always expanded, no state needed
  const isExpanded = true;
  
  // Use clean uiData instead of raw results
  const uiData = results?.uiData || results; // Fallback for backward compatibility
  const executionStatus = uiData?.execution?.status || 'completed';
  const analysisResults = uiData?.results || {};
  const analysisType = uiData?.type || 'Analysis';

  const formatValue = (value: any): string => {
    if (typeof value === 'number') {
      if (value % 1 === 0) return value.toString();
      return value.toFixed(2);
    }
    return String(value);
  };

  const openWorkspace = () => {
    // Use clean UI data for workspace navigation
    const workspaceData = {
      executionId: executionId || null,
      analysisId: analysisId || null,
      parameters: uiData?.parameters || {},
      analysis_type: uiData?.type || 'analysis',
      query_type: 'analysis'
    };
    
    // Build URL with IDs as query parameters for better data extraction
    const params = new URLSearchParams({
      results: JSON.stringify(workspaceData)
    });
    
    if (analysisId) {
      params.set('analysisId', analysisId);
    }
    
    if (executionId) {
      params.set('executionId', executionId);
    }
    
    const analysisUrl = `/analysis/${messageId}?${params.toString()}`;
    router.push(analysisUrl);
  };

  const exportResults = () => {
    if (!uiData) return;
    
    // Export clean UI data instead of raw metadata
    const exportData = {
      analysisType: uiData.type,
      results: uiData.results,
      confidence: uiData.confidence,
      parameters: uiData.parameters,
      timestamp: new Date().toISOString(),
    };
    
    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `analysis-results-${messageId}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const renderExpandedContent = () => {
    const resultEntries = Object.entries(analysisResults);
    
    if (!uiData || resultEntries.length === 0) {
      return (
        <div className="text-center py-4 text-gray-500">
          <p>No results available</p>
        </div>
      );
    }

    // Render only analysis results in a clean grid layout (no confidence or other grids)
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {resultEntries.map(([key, value], index) => (
          <div key={index} className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <div className="font-medium text-blue-900 text-sm">{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</div>
            <div className="text-lg font-bold text-blue-700 mt-1">{formatValue(value)}</div>
          </div>
        ))}
      </div>
    );
  };

  if (!uiData) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
        <p className="text-gray-600">No analysis results available</p>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      {/* Content - Always Expanded */}
      <div className="p-4 space-y-4">
        {renderExpandedContent()}
        
        {/* Execution Logs for Running Status */}
        {executionStatus === 'running' && results?.execution?.logs && (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
            <div className="font-medium text-gray-900 mb-2 flex items-center gap-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
              Execution Logs
            </div>
            <div className="space-y-1 max-h-32 overflow-y-auto">
              {results.execution.logs.map((log: any, idx: number) => (
                <div key={idx} className="text-sm text-gray-700 font-mono">
                  <span className="text-gray-500">[{new Date(log.timestamp).toLocaleTimeString()}]</span>
                  <span className="ml-2">{log.message}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Execution Error Display */}
        {executionStatus === 'failed' && results?.execution?.error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <div className="font-medium text-red-900 mb-2">Execution Failed</div>
            <div className="text-sm text-red-700">
              {results.execution.error}
            </div>
          </div>
        )}
        
        {/* Show MockOutput for mock data */}
        {results?.query_type && (
          <div>
            <MockOutput moduleKey={results.query_type} />
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="p-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <span>🔬</span>
          <span>
            {executionStatus === 'running' ? 'Execution in progress...' :
             executionStatus === 'queued' ? 'Waiting for execution...' :
             executionStatus === 'failed' ? 'Execution failed - retry in workspace' :
             'Adjust parameters and re-run analysis'}
          </span>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={exportResults}
            disabled={executionStatus === 'running' || executionStatus === 'queued'}
            className={`px-3 py-1.5 text-sm border border-gray-300 rounded-lg transition-colors ${
              executionStatus === 'running' || executionStatus === 'queued'
                ? 'opacity-50 cursor-not-allowed'
                : 'hover:bg-gray-100'
            }`}
          >
            Export
          </button>
          <button
            onClick={openWorkspace}
            className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
          >
            {executionStatus === 'running' ? 'View Progress' : 'Open Workspace'}
          </button>
        </div>
      </div>
    </div>
  );
}