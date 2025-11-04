'use client';

import { useRouter } from 'next/navigation';
import MockOutput from '@/components/MockOutput';

interface AnalysisResultProps {
  messageId: string;
  question: string;
  results: any;
  analysisId?: string;
  executionId?: string;
}

export default function AnalysisResult({
  messageId,
  question,
  results,
  analysisId,
  executionId
}: AnalysisResultProps) {
  const router = useRouter();

  // Use clean uiData from backend transform (includes unified status)
  const uiData = results?.uiData || results; // Fallback for backward compatibility

  // Use backend status - no SSE handling here, status comes from upstream
  const currentStatus = uiData?.status || results?.status || 'completed';
  const currentError = uiData?.error;
  const analysisResults = uiData?.results || {};
  const analysisType = uiData?.type || 'Analysis';
  const markdown = uiData?.markdown;

  // Extract IDs from submission response if not provided as props
  const effectiveAnalysisId = analysisId || results?.analysis_id;
  const effectiveExecutionId = executionId || results?.execution_id;


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
      executionId: effectiveExecutionId || null,
      analysisId: effectiveAnalysisId || null,
      parameters: uiData?.parameters || {},
      analysis_type: uiData?.type || 'analysis',
      query_type: 'analysis'
    };

    // Build URL with IDs as query parameters for better data extraction
    const params = new URLSearchParams({
      results: JSON.stringify(workspaceData)
    });

    if (effectiveAnalysisId) {
      params.set('analysisId', effectiveAnalysisId);
    }

    if (effectiveExecutionId) {
      params.set('executionId', effectiveExecutionId);
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

  // AnalysisResult should only be used for completed results
  // Progress is now handled by ChatMessage component


  // AnalysisResult component now only handles script_generation responses
  // Other response types (meaningless, needs_clarification) are handled by ChatMessage component
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
            className={`px-3 py-1.5 text-sm border border-gray-300 rounded-lg transition-colors ${!uiData?.canExport
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