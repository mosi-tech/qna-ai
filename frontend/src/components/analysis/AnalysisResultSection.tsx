'use client';

import UIConfigurationRenderer from '../insights/UIConfigurationRenderer';

interface AnalysisResultSectionProps {
  results: any;
  isRunning: boolean;
  onConfigureParameters: () => void;
  hasParameterChanges: boolean;
}

export default function AnalysisResultSection({ 
  results, 
  isRunning, 
  onConfigureParameters, 
  hasParameterChanges 
}: AnalysisResultSectionProps) {
  const renderAnalysisContent = () => {
    if (!results) return null;

    // Check if results contain UI configuration (new dynamic UI approach)
    const uiConfig = results.ui_config || results.llmResponse?.ui_config;
    if (uiConfig && uiConfig.ui_config?.selected_components) {
      return (
        <div className="space-y-4">
          <div className="bg-green-50 rounded-lg p-3 border-l-4 border-green-500">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm font-medium text-green-700">Dynamic Dashboard Generated</span>
            </div>
          </div>
          <UIConfigurationRenderer 
            uiConfig={uiConfig}
          />
        </div>
      );
    }

    // Fallback to traditional content rendering
    const content = results.llmResponse?.analysis_result || 
                   results.analysis_result || 
                   results.response_data?.analysis_result ||
                   results.content ||
                   results.description;

    if (!content) {
      return (
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <p className="text-gray-600 text-sm">No detailed analysis content available.</p>
          <pre className="text-xs text-gray-500 mt-2 overflow-auto max-h-32">
            {JSON.stringify(results, null, 2)}
          </pre>
        </div>
      );
    }

    // Render content with proper markdown-like formatting (similar to chat)
    return (
      <div className="prose prose-gray max-w-none">
        <div className="bg-gray-50 rounded-lg p-4 border-l-4 border-blue-500">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span className="text-sm font-medium text-gray-700">Analysis Result</span>
          </div>
          <div className="text-gray-800 leading-relaxed whitespace-pre-wrap">
            {String(content)}
          </div>
        </div>
      </div>
    );
  };

  const renderExecutionInfo = () => {
    if (!results) return null;

    const execution = results.execution || results.llmResponse?.execution;
    if (!execution) return null;

    return (
      <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-blue-600">ℹ️</span>
          <span className="text-sm font-medium text-blue-800">Execution Details</span>
        </div>
        <div className="text-sm text-blue-700 space-y-1">
          {execution.script_name && (
            <div><span className="font-medium">Script:</span> {execution.script_name}</div>
          )}
          {execution.parameters && Object.keys(execution.parameters).length > 0 && (
            <div><span className="font-medium">Parameters:</span> {JSON.stringify(execution.parameters)}</div>
          )}
          {execution.execution_time && (
            <div><span className="font-medium">Duration:</span> {execution.execution_time}s</div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-xl">📊</span>
          <h2 className="text-lg font-semibold text-gray-900">Analysis Result</h2>
        </div>
        <button
          onClick={onConfigureParameters}
          className="inline-flex items-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
        >
          <span className="text-base">⚙️</span>
          Configure Parameters
          {hasParameterChanges && (
            <span className="bg-amber-400 text-amber-900 px-2 py-0.5 rounded-full text-xs font-medium">
              Modified
            </span>
          )}
        </button>
      </div>

      {isRunning ? (
        <div className="flex flex-col items-center justify-center py-16">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-4" />
          <p className="text-gray-600 font-medium">Running analysis...</p>
          <p className="text-sm text-gray-500 mt-1">Please wait while we process your request</p>
        </div>
      ) : results ? (
        <div className="space-y-4">
          {renderAnalysisContent()}
          {renderExecutionInfo()}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-16 text-gray-500">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
            <span className="text-2xl">📋</span>
          </div>
          <p className="font-medium">No analysis results yet</p>
          <p className="text-sm mt-1">Configure parameters and run analysis to see results</p>
        </div>
      )}
    </div>
  );
}