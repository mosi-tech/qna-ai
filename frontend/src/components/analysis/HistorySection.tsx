'use client';

import { AnalysisRun } from '@/types/parameters';

interface HistorySectionProps {
  runs: AnalysisRun[];
  activeRunId?: string;
  onSelectRun: (runId: string) => void;
}

export default function HistorySection({ runs, activeRunId, onSelectRun }: HistorySectionProps) {
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
      total_runs: runs.length,
      runs: runs.map(run => ({
        id: run.id,
        parameters: run.parameters,
        results: run.results,
        status: run.status,
        duration: run.duration,
        created_at: run.createdAt.toISOString()
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

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">History</h2>
        {runs.length > 0 && (
          <span className="text-sm text-gray-500">
            {runs.length} run{runs.length !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {runs.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-8 text-gray-500">
          <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mb-3">
            <span className="text-xl">📋</span>
          </div>
          <p>No analysis history</p>
          <p className="text-sm mt-1">Previous runs will appear here</p>
        </div>
      ) : (
        <div className="space-y-3">
          {runs.slice().reverse().map((run, index) => {
            const isActive = run.id === activeRunId;
            const runNumber = runs.length - index;
            
            return (
              <div
                key={run.id}
                onClick={() => onSelectRun(run.id)}
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
                      Run #{runNumber}
                      {index === 0 && ' (Current)'}
                    </span>
                    <div className={`px-2 py-1 rounded-full text-xs ${
                      run.status === 'completed' ? 'bg-green-100 text-green-800' :
                      run.status === 'failed' ? 'bg-red-100 text-red-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {run.status}
                    </div>
                  </div>
                  <span className="text-xs text-gray-500">
                    {formatTimeAgo(run.createdAt)}
                  </span>
                </div>
                
                <p className="text-sm text-gray-600 mt-1">
                  {getParameterSummary(run.parameters)}
                </p>
                
                {run.duration && (
                  <p className="text-xs text-gray-500 mt-1">
                    Completed in {(run.duration / 1000).toFixed(1)}s
                  </p>
                )}
                
                {run.error && (
                  <p className="text-xs text-red-600 mt-1">
                    Error: {run.error}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}

      {runs.length > 0 && (
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