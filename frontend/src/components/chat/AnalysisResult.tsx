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
  const [isExpanded, setIsExpanded] = useState(expanded);
  
  // Extract execution status from current structure
  const executionStatus = results?.execution?.status || 'unknown';
  const analysisStatus = results?.analysis?.status || 'completed';

  const formatValue = (value: any): string => {
    if (typeof value === 'number') {
      if (value % 1 === 0) return value.toString();
      return value.toFixed(2);
    }
    return String(value);
  };

  const openWorkspace = () => {
    // Extract data from current API structure
    const workspaceData = {
      executionId: results?.response_data?.analysis_result?.execution?.script_name || executionId || null,
      analysisId: results?.response_data?.analysis_id || analysisId || null,
      parameters: results?.response_data?.analysis_result?.execution?.parameters || {},
      analysis_type: 'script_execution', // generic type for current structure
      query_type: results?.response_data?.response_type || 'analysis'
    };
    
    // Build URL with IDs as query parameters for better data extraction
    const params = new URLSearchParams({
      question: question,
      results: JSON.stringify(workspaceData)
    });
    
    if (analysisId || workspaceData.analysisId) {
      params.set('analysisId', analysisId || workspaceData.analysisId);
    }
    
    if (executionId || workspaceData.executionId) {
      params.set('executionId', executionId || workspaceData.executionId);
    }
    
    const analysisUrl = `/analysis/${messageId}?${params.toString()}`;
    router.push(analysisUrl);
  };

  const exportResults = () => {
    if (!results) return;
    
    const dataStr = JSON.stringify(results, null, 2);
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

  // Get summary data for collapsed view
  const getSummary = () => {
    if (!results) return null;

    if (results.analysis_type === 'weekday_performance' || (results.best_day && results.average_return)) {
      return {
        type: 'Weekday Performance Analysis',
        primaryResult: `Best day: ${results.best_day}`,
        secondaryResult: `+${formatValue(results.average_return)}% avg return`,
        confidence: results.confidence ? `${formatValue(results.confidence)}% confidence` : null
      };
    }

    // Check if it's mock data from MockOutput
    if (results.query_type) {
      return {
        type: 'Financial Analysis',
        primaryResult: `Analysis type: ${results.query_type}`,
        secondaryResult: 'View details below',
        confidence: null
      };
    }

    // Generic summary
    const keys = Object.keys(results);
    const firstKey = keys[0];
    return {
      type: 'Analysis Complete',
      primaryResult: firstKey ? `${firstKey}: ${formatValue(results[firstKey])}` : 'Results available',
      secondaryResult: `${keys.length} data points`,
      confidence: null
    };
  };

  const summary = getSummary();

  const renderExpandedContent = () => {
    if (!results) return null;

    // Handle weekday performance analysis
    if (results.analysis_type === 'weekday_performance' || (results.best_day && results.average_return)) {
      return (
        <div className="space-y-4">
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-center">
              <div className="font-medium text-green-900">Best Day</div>
              <div className="text-lg font-bold text-green-700">{results.best_day}</div>
            </div>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-center">
              <div className="font-medium text-blue-900">Avg Return</div>
              <div className="text-lg font-bold text-blue-700">+{formatValue(results.average_return)}%</div>
            </div>

            {results.confidence && (
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-3 text-center">
                <div className="font-medium text-purple-900">Confidence</div>
                <div className="text-lg font-bold text-purple-700">{formatValue(results.confidence)}%</div>
              </div>
            )}
          </div>

          {results.daily_breakdown && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
              <div className="font-medium text-gray-900 mb-2">Daily Performance</div>
              <div className="grid grid-cols-5 gap-2 text-sm">
                {Object.entries(results.daily_breakdown).map(([day, return_pct]: [string, any]) => (
                  <div key={day} className="text-center">
                    <div className="text-gray-600">{day}</div>
                    <div className={`font-medium ${
                      return_pct > 0 ? 'text-green-600' : return_pct < 0 ? 'text-red-600' : 'text-gray-600'
                    }`}>
                      {return_pct > 0 ? '+' : ''}{formatValue(return_pct)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      );
    }

    // Handle mock data (which will show the MockOutput component below)
    if (results.query_type) {
      return (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-blue-600">ℹ️</span>
            <span className="font-medium text-blue-900">Analysis Details</span>
          </div>
          <p className="text-sm text-blue-700">
            This analysis includes detailed metrics and visualizations. 
            Click "Open Workspace" to explore parameters and re-run with different settings.
          </p>
        </div>
      );
    }

    // Generic expanded view
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
        <pre className="text-sm text-gray-800 whitespace-pre-wrap overflow-auto max-h-48">
          {JSON.stringify(results, null, 2)}
        </pre>
      </div>
    );
  };

  if (!summary) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
        <p className="text-gray-600">No analysis results available</p>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      {/* Header - Always Visible */}
      <div className="p-4 bg-gradient-to-r from-blue-50 to-green-50 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-lg">📊</span>
              <h3 className="font-medium text-gray-900">{summary.type}</h3>
              {executionStatus === 'running' && (
                <div className="flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                  <span>Executing</span>
                </div>
              )}
              {executionStatus === 'queued' && (
                <div className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded-full">
                  Queued
                </div>
              )}
              {executionStatus === 'completed' && (
                <div className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                  ✓ Complete
                </div>
              )}
              {executionStatus === 'failed' && (
                <div className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full">
                  ✗ Failed
                </div>
              )}
            </div>
            <div className="space-y-1">
              <p className="text-sm font-medium text-gray-700">{summary.primaryResult}</p>
              <div className="flex items-center gap-3 text-sm text-gray-600">
                <span>{summary.secondaryResult}</span>
                {summary.confidence && (
                  <>
                    <span>•</span>
                    <span>{summary.confidence}</span>
                  </>
                )}
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-white rounded-lg transition-colors"
              title={isExpanded ? "Collapse" : "Expand details"}
            >
              <span className={`transform transition-transform ${isExpanded ? 'rotate-180' : ''}`}>
                ▼
              </span>
            </button>
          </div>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
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
      )}

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