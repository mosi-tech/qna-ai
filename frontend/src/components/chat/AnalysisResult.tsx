'use client';

import { useRouter } from 'next/navigation';
import { renderMarkdown } from '@/lib/utils/markdown';

interface AnalysisResultProps {
  message: any;
}

export default function AnalysisResult({
  message
}: AnalysisResultProps) {
  const router = useRouter();

  // Simplified data access - expect flattened structure
  const messageId = message.id
  const markdown = message?.results?.markdown;
  const canRerun = message?.canRerun;
  const canExport = message?.canExport;

  const openWorkspace = () => {
    if (!messageId) {
      console.error('Cannot open workspace: messageId is required');
      return;
    }

    // Get sessionId from current URL or context - we need this for the new route structure
    const currentPath = window.location.pathname;
    const sessionIdMatch = currentPath.match(/\/chat\/([^\/]+)/);
    
    if (!sessionIdMatch) {
      console.error('Cannot determine sessionId from current URL:', currentPath);
      return;
    }
    
    const sessionId = sessionIdMatch[1];
    
    // Use new nested route structure: /analysis/{sessionId}/{messageId}
    const analysisUrl = `/analysis/${sessionId}/${messageId}`;
    console.log('Opening workspace with new URL structure:', analysisUrl);
    router.push(analysisUrl);
  };

  const exportResults = () => {
    if (!message) return;

    const dataStr = JSON.stringify(message, null, 2);
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


  const renderContent = () => {
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

    return (
      <div className="text-center py-4 text-gray-500">
        <p>Analysis completed successfully</p>
      </div>
    );
  };

  if (!message) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
        <p className="text-gray-600">No analysis results available</p>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      {/* Content */}
      <div className="p-4">
        {renderContent()}
      </div>

      {/* Action Buttons */}
      <div className="p-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <span>🔬</span>
          <span>Analysis completed</span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={exportResults}
            disabled={!canExport}
            className={`px-3 py-1.5 text-sm border border-gray-300 rounded-lg transition-colors ${!canExport
              ? 'opacity-50 cursor-not-allowed'
              : 'hover:bg-gray-100'
              }`}
          >
            Export
          </button>
          <button
            onClick={openWorkspace}
            disabled={!canRerun}
            className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${!canRerun
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
          >
            Open Workspace
          </button>
        </div>
      </div>
    </div>
  );
}