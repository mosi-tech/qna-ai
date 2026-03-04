'use client';

interface AnalysisPanelProps {
  currentAnalysis: {
    messageId: string;
    data: Record<string, unknown>;
    originalQuestion?: string;
  } | null;
}

export default function AnalysisPanel({ currentAnalysis }: AnalysisPanelProps) {
  if (!currentAnalysis?.data) {
    return (
      <div className="flex-1 overflow-y-auto flex items-center justify-center">
        <div className="text-center text-gray-500">
          <div className="mb-4">
            <span className="text-2xl">📊</span>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Analysis Yet</h3>
          <p className="text-sm text-gray-600 max-w-sm">
            Ask a question in the chat to see financial analysis results here
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4 sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Analysis Results</h1>
            {currentAnalysis.originalQuestion && (
              <p className="text-gray-600 text-sm mt-1">{currentAnalysis.originalQuestion}</p>
            )}
          </div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
              ✓ Complete
            </span>
          </div>
        </div>
      </header>

      <div className="p-6">
        <pre className="text-xs text-gray-600 bg-gray-100 rounded p-4 overflow-auto max-h-96 whitespace-pre-wrap">
          {JSON.stringify(currentAnalysis.data, null, 2)}
        </pre>
      </div>
    </div>
  );
}
