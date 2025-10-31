'use client';

interface ResultsSectionProps {
  results: any;
  isRunning: boolean;
  runCount: number;
}

export default function ResultsSection({ results, isRunning, runCount }: ResultsSectionProps) {
  const formatValue = (value: any): string => {
    if (typeof value === 'number') {
      if (value % 1 === 0) return value.toString();
      return value.toFixed(2);
    }
    return String(value);
  };

  const exportResults = () => {
    if (!results) return;
    
    const dataStr = JSON.stringify(results, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `analysis-results-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const renderResults = () => {
    if (!results) return null;

    // Handle different result types
    if (results.analysis_type === 'weekday_performance') {
      return (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h4 className="font-medium text-green-900">Best Trading Day</h4>
              <p className="text-2xl font-bold text-green-700">{results.best_day}</p>
              <p className="text-sm text-green-600">+{formatValue(results.average_return)}% avg return</p>
            </div>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-medium text-blue-900">Confidence Level</h4>
              <p className="text-2xl font-bold text-blue-700">{formatValue(results.confidence)}%</p>
              <p className="text-sm text-blue-600">Statistical significance</p>
            </div>
          </div>

          {results.daily_breakdown && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-3">Daily Performance Breakdown</h4>
              <div className="space-y-2">
                {Object.entries(results.daily_breakdown).map(([day, return_pct]: [string, any]) => (
                  <div key={day} className="flex justify-between items-center">
                    <span className="text-sm text-gray-700">{day}</span>
                    <span className={`text-sm font-medium ${
                      return_pct > 0 ? 'text-green-600' : return_pct < 0 ? 'text-red-600' : 'text-gray-600'
                    }`}>
                      {return_pct > 0 ? '+' : ''}{formatValue(return_pct)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      );
    }

    // Generic results display
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <pre className="text-sm text-gray-800 whitespace-pre-wrap overflow-auto max-h-64">
          {JSON.stringify(results, null, 2)}
        </pre>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Results</h2>
        {runCount > 0 && (
          <span className="text-sm text-gray-500">
            Run #{runCount}
          </span>
        )}
      </div>

      {isRunning ? (
        <div className="flex flex-col items-center justify-center py-12">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-4" />
          <p className="text-gray-600">Running analysis...</p>
          <p className="text-sm text-gray-500 mt-1">This may take a few moments</p>
        </div>
      ) : results ? (
        <div>
          {renderResults()}
          
          <div className="mt-6 pt-4 border-t border-gray-200 flex gap-3">
            <button 
              onClick={exportResults}
              className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              📋 Export JSON
            </button>
            <button 
              onClick={() => {
                // Future: Open detailed view
                console.log('View full report:', results);
              }}
              className="px-4 py-2 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
            >
              📊 View Full Report
            </button>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-12 text-gray-500">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
            <span className="text-2xl">📊</span>
          </div>
          <p>No analysis results yet</p>
          <p className="text-sm mt-1">Adjust parameters and run analysis to see results</p>
        </div>
      )}
    </div>
  );
}