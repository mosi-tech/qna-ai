'use client';

import { AnalysisRun } from '@/types/parameters';

interface InsightsSectionProps {
  results: any;
  runs: AnalysisRun[];
  parameters: Record<string, any>;
}

export default function InsightsSection({ results, runs, parameters }: InsightsSectionProps) {
  const generateInsights = () => {
    if (!results) return [];

    const insights: Array<{ type: 'finding' | 'recommendation' | 'trend', content: string }> = [];

    // Weekday performance specific insights
    if (results.analysis_type === 'weekday_performance') {
      insights.push({
        type: 'finding',
        content: `${results.best_day} consistently shows the highest average returns at +${results.average_return}%`
      });

      if (results.confidence > 80) {
        insights.push({
          type: 'recommendation',
          content: `High confidence level (${results.confidence}%) suggests ${results.best_day} trading is statistically significant`
        });
      }

      if (parameters.volume_filter && parameters.volume_filter !== '1M') {
        insights.push({
          type: 'finding',
          content: `Using ${parameters.volume_filter}+ volume filter may improve trade quality by focusing on liquid stocks`
        });
      }
    }

    // Multi-run trend analysis
    if (runs.length > 1) {
      const completedRuns = runs.filter(run => run.status === 'completed');
      if (completedRuns.length > 1) {
        const latestRuns = completedRuns.slice(-2);
        const [previousRun, currentRun] = latestRuns;
        
        if (previousRun.results?.average_return && results?.average_return) {
          const returnDiff = results.average_return - previousRun.results.average_return;
          if (Math.abs(returnDiff) > 0.1) {
            insights.push({
              type: 'trend',
              content: `Parameter changes ${returnDiff > 0 ? 'improved' : 'reduced'} returns by ${Math.abs(returnDiff).toFixed(2)}%`
            });
          }
        }
      }
    }

    // Generic insights based on parameters
    if (parameters.period) {
      if (parameters.period < 100) {
        insights.push({
          type: 'recommendation',
          content: 'Consider using a longer analysis period (200+ days) for more reliable patterns'
        });
      } else if (parameters.period > 500) {
        insights.push({
          type: 'finding',
          content: 'Extended analysis period provides robust historical context but may include outdated market patterns'
        });
      }
    }

    return insights;
  };

  const insights = generateInsights();

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'finding': return '💡';
      case 'recommendation': return '🎯';
      case 'trend': return '📈';
      default: return '💭';
    }
  };

  const getInsightColor = (type: string) => {
    switch (type) {
      case 'finding': return 'text-blue-700 bg-blue-50 border-blue-200';
      case 'recommendation': return 'text-green-700 bg-green-50 border-green-200';
      case 'trend': return 'text-purple-700 bg-purple-50 border-purple-200';
      default: return 'text-gray-700 bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Insights</h2>

      {insights.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-8 text-gray-500">
          <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mb-3">
            <span className="text-xl">💡</span>
          </div>
          <p>No insights available</p>
          <p className="text-sm mt-1">Run analysis to see key findings and recommendations</p>
        </div>
      ) : (
        <div className="space-y-3">
          {insights.map((insight, index) => (
            <div
              key={index}
              className={`p-4 rounded-lg border ${getInsightColor(insight.type)}`}
            >
              <div className="flex items-start gap-3">
                <span className="text-lg">{getInsightIcon(insight.type)}</span>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-medium capitalize">
                      {insight.type === 'finding' ? 'Key Finding' :
                       insight.type === 'recommendation' ? 'Recommendation' :
                       insight.type === 'trend' ? 'Trend Analysis' : 'Insight'}
                    </span>
                  </div>
                  <p className="text-sm leading-relaxed">
                    {insight.content}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {runs.length > 1 && (
        <div className="mt-6 pt-4 border-t border-gray-200">
          <div className="text-sm text-gray-600">
            <h4 className="font-medium mb-2">Analysis Summary</h4>
            <div className="space-y-1">
              <p>• Total runs: {runs.length}</p>
              <p>• Successful: {runs.filter(r => r.status === 'completed').length}</p>
              <p>• Current parameters: {Object.keys(parameters).length} configured</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}