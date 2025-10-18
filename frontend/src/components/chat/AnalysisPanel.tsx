'use client';

import { modules } from '@/config/modules';
import MockOutput from '@/components/MockOutput';

interface AnalysisData {
  moduleKey: string;
  messageId: string;
  originalQuestion?: string;
}

interface AnalysisPanelProps {
  currentAnalysis: AnalysisData | null;
}

export default function AnalysisPanel({ currentAnalysis }: AnalysisPanelProps) {
  if (!currentAnalysis) {
    return (
      <div className="flex-1 overflow-y-auto">
        <div className="h-full flex items-center justify-center">
          <div className="text-center text-gray-500">
            <div className="mb-4">
              <span className="text-2xl">📊</span>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Analysis Yet</h3>
            <p className="text-sm text-gray-600 max-w-sm">
              Start a conversation to see financial analysis results here
            </p>
          </div>
        </div>
      </div>
    );
  }

  const moduleData = modules[currentAnalysis.moduleKey];
  
  return (
    <div className="flex-1 overflow-y-auto">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Analysis Results</h1>
            {moduleData && (
              <p className="text-gray-600 text-sm mt-1">{moduleData.title}</p>
            )}
          </div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
              ✓ Complete
            </span>
          </div>
        </div>
      </header>

      {/* Analysis Content */}
      <div className="p-6">
        <MockOutput moduleKey={currentAnalysis.moduleKey} />
      </div>
    </div>
  );
}