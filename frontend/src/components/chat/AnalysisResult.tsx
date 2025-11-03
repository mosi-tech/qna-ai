'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import MockOutput from '@/components/MockOutput';
import ProgressPanel from '@/components/progress/ProgressPanel';
import { useProgress } from '@/lib/context/ProgressContext';

interface AnalysisResultProps {
  messageId: string;
  question: string;
  results: any;
  expanded?: boolean;
  analysisId?: string;
  executionId?: string;
  sessionId?: string;
  onExecutionUpdate?: (update: any) => void;
}

export default function AnalysisResult({ 
  messageId, 
  question, 
  results, 
  expanded = false,
  analysisId,
  executionId,
  sessionId,
  onExecutionUpdate
}: AnalysisResultProps) {
  const router = useRouter();
  // Always expanded, no state needed
  const isExpanded = true;
  
  
  // State to track when analysis completes via SSE
  const [sseCompleted, setSseCompleted] = useState(false);
  
  // Use clean uiData from backend transform (includes unified status)
  const uiData = results?.uiData || results; // Fallback for backward compatibility
  
  // Use backend's unified status instead of complex detection logic
  const currentStatus = uiData?.status || 'completed';
  const currentError = uiData?.error;
  const analysisResults = uiData?.results || {};
  const analysisType = uiData?.type || 'Analysis';
  const markdown = uiData?.markdown;
  
  // Callback for when analysis completes via SSE
  const handleAnalysisComplete = useCallback((status: 'completed' | 'failed', data?: any) => {
    console.log('[AnalysisResult] Analysis completed via SSE:', status, data);
    setSseCompleted(true);
    
    // Try to trigger refresh via callback first
    if (onExecutionUpdate) {
      onExecutionUpdate({ status, ...data });
    } else {
      // Fallback: trigger page refresh after a short delay to let the backend process
      setTimeout(() => {
        console.log('[AnalysisResult] Refreshing page to load updated message data');
        window.location.reload();
      }, 1500);
    }
  }, [onExecutionUpdate]);
  
  // Use session-level progress context (single SSE connection per session)
  const { logs: progressLogs, isConnected, error, clearLogs, registerAnalysisCompleteCallback } = useProgress();

  // Register analysis completion callback for this specific message
  useEffect(() => {
    if (!messageId) return;
    
    const unregister = registerAnalysisCompleteCallback(messageId, handleAnalysisComplete);
    return unregister;
  }, [messageId, registerAnalysisCompleteCallback, handleAnalysisComplete]);
  
  // Determine if analysis is actively processing
  const isProcessing = currentStatus === 'pending' && !sseCompleted;

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

  const renderMarkdown = (text: string) => {
    // Basic markdown parsing for common elements
    let html = text
      // Headers
      .replace(/^### (.*$)/gim, '<h3 class="text-lg font-semibold text-gray-900 mt-4 mb-2">$1</h3>')
      .replace(/^## (.*$)/gim, '<h2 class="text-xl font-bold text-gray-900 mt-6 mb-3">$1</h2>')
      .replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold text-gray-900 mt-6 mb-4">$1</h1>')
      // Bold and italic
      .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>')
      .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
      // Lists
      .replace(/^\* (.*$)/gim, '<li class="ml-4">• $1</li>')
      .replace(/^- (.*$)/gim, '<li class="ml-4">• $1</li>')
      // Line breaks
      .replace(/\n/g, '<br/>');
    
    return html;
  };

  const renderExpandedContent = () => {
    const hasResults = markdown || (analysisResults && Object.keys(analysisResults).length > 0);
    
    // Show status indicator if no results yet or still processing
    if (!hasResults || currentStatus === 'running' || currentStatus === 'queued') {
      return (
        <div className="text-center py-6">
          <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg ${
            currentStatus === 'pending' ? 'bg-yellow-50 text-yellow-700 border border-yellow-200' :
            currentStatus === 'queued' ? 'bg-yellow-50 text-yellow-700 border border-yellow-200' :
            currentStatus === 'running' ? 'bg-blue-50 text-blue-700 border border-blue-200' :
            currentStatus === 'failed' ? 'bg-red-50 text-red-700 border border-red-200' :
            'bg-gray-50 text-gray-700 border border-gray-200'
          }`}>
            {(currentStatus === 'running' || currentStatus === 'queued') && (
              <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
            )}
            {currentStatus === 'pending' && (
              <div className="w-2 h-2 bg-current rounded-full animate-pulse"></div>
            )}
            {currentStatus === 'failed' && (
              <div className="w-2 h-2 bg-current rounded-full"></div>
            )}
            <span className="font-medium">
              {currentStatus === 'pending' ? 'Analysis in progress...' :
               currentStatus === 'queued' ? 'Queued for execution...' :
               currentStatus === 'running' ? 'Executing analysis...' :
               'Processing...'}
            </span>
          </div>
        </div>
      );
    }
    
    // Prioritize markdown rendering over raw results
    if (markdown) {
      return (
        <div className="prose prose-sm max-w-none">
          <div 
            className="markdown-content space-y-2"
            dangerouslySetInnerHTML={{ 
              __html: renderMarkdown(markdown)
            }}
          />
        </div>
      );
    }

    // Fallback: render raw results if no markdown available
    const resultEntries = Object.entries(analysisResults);
    
    if (resultEntries.length === 0) {
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

  // If this is a pending analysis, show the progress panel
  // But if SSE indicates completion, show a brief "refreshing" message instead
  if (currentStatus === 'pending') {
    if (sseCompleted) {
      return (
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <div className="p-4 text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-green-50 text-green-700 border border-green-200">
              <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
              <span className="font-medium">Analysis completed! Loading results...</span>
            </div>
          </div>
        </div>
      );
    }
    return (
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="p-4">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Analysis in Progress</h3>
            <p className="text-sm text-gray-600">{question}</p>
          </div>
          
          {/* Progress Panel for SSE logs */}
          <div className="h-96 border border-gray-200 rounded-lg overflow-hidden">
            <ProgressPanel 
              logs={progressLogs}
              isConnected={isConnected}
              isProcessing={isProcessing}
              onClear={clearLogs}
            />
          </div>
          
          {/* Status indicator */}
          <div className="mt-4 flex items-center gap-2 text-sm text-gray-600">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
            <span>Analyzing your question...</span>
          </div>
        </div>
      </div>
    );
  }
  
  // If analysis failed, show error message with both uiData.error and content
  if (currentStatus === 'failed') {
    return (
      <div className="bg-white border border-red-200 rounded-lg overflow-hidden">
        <div className="p-4">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-6 h-6 bg-red-100 rounded-full flex items-center justify-center">
              <span className="text-red-600 text-sm">✕</span>
            </div>
            <h3 className="text-lg font-semibold text-red-900">Analysis Failed</h3>
          </div>
          <p className="text-sm text-gray-600 mb-3">{question}</p>
          
          {/* Show structured error message */}
          {currentError && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-3">
              <p className="text-sm text-red-700 font-medium">Error Details:</p>
              <p className="text-sm text-red-700">{currentError}</p>
            </div>
          )}
          
          {/* Show content (which contains the error message from analysis pipeline) */}
          {results?.content && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
              <p className="text-sm text-gray-700">{results.content}</p>
            </div>
          )}
          
          {/* Retry button */}
          <div className="mt-4 flex justify-end">
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      {/* Content - Always Expanded */}
      <div className="p-4 space-y-4">
        {renderExpandedContent()}
        
        
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
            {currentStatus === 'running' ? 'Execution in progress...' :
             currentStatus === 'queued' ? 'Waiting for execution...' :
             currentStatus === 'pending' ? 'Analysis in progress...' :
             currentStatus === 'failed' ? 'Analysis failed - retry in workspace' :
             'Adjust parameters and re-run analysis'}
          </span>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={exportResults}
            disabled={!uiData?.canExport}
            className={`px-3 py-1.5 text-sm border border-gray-300 rounded-lg transition-colors ${
              !uiData?.canExport
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
            {currentStatus === 'running' || currentStatus === 'pending' ? 'View Progress' : 'Open Workspace'}
          </button>
        </div>
      </div>
    </div>
  );
}