/**
 * OptionComparison
 * 
 * Description: Multiple choice comparison against various criteria/metrics
 * Use Cases: Investment option comparison, strategy evaluation, alternative analysis
 * Data Format: Options array with criteria scores and metadata
 * 
 * @param options - Array of options to compare
 * @param criteria - Array of comparison criteria
 * @param title - Optional title for the comparison
 * @param showScores - Whether to display numerical scores
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface ComparisonOption {
  id: string;
  name: string;
  description?: string;
  scores: Record<string, number | string>;
  totalScore?: number;
  recommendation?: boolean;
}

interface ComparisonCriterion {
  id: string;
  name: string;
  weight?: number;
  format?: 'score' | 'percentage' | 'currency' | 'text';
  description?: string;
}

interface OptionComparisonProps {
  options: ComparisonOption[];
  criteria: ComparisonCriterion[];
  title?: string;
  showScores?: boolean;
  showWeights?: boolean;
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function OptionComparison({
  options,
  criteria,
  title,
  showScores = true,
  showWeights = false,
  onApprove,
  onDisapprove,
  variant = 'default'
}: OptionComparisonProps) {

  const formatValue = (value: number | string, format: string = 'score') => {
    if (typeof value === 'string') return value;

    switch (format) {
      case 'percentage':
        return `${value.toFixed(1)}%`;
      case 'currency':
        return `$${value.toLocaleString()}`;
      case 'score':
        return value.toFixed(1);
      default:
        return value.toString();
    }
  };

  const getScoreColor = (score: number | string, criterionId: string) => {
    if (typeof score !== 'number') return 'text-gray-700';

    // Normalize score to 0-1 range (assuming 0-10 scale)
    const normalized = Math.max(0, Math.min(1, score / 10));

    if (normalized >= 0.8) return 'text-green-700 bg-green-50';
    if (normalized >= 0.6) return 'text-green-600 bg-green-25';
    if (normalized >= 0.4) return 'text-yellow-600 bg-yellow-50';
    if (normalized >= 0.2) return 'text-orange-600 bg-orange-50';
    return 'text-red-600 bg-red-50';
  };

  const getRecommendationBadge = (option: ComparisonOption) => {
    if (option.recommendation) {
      return (
        <span className="inline-flex items-center px-2 py-1 text-xs font-medium text-green-800 bg-green-100 border border-green-200 rounded-full">
          ★ Recommended
        </span>
      );
    }
    return null;
  };

  const getBestScoreForCriterion = (criterionId: string) => {
    const scores = options.map(opt => opt.scores[criterionId]).filter(s => typeof s === 'number') as number[];
    return Math.max(...scores);
  };

  const isHighestScore = (value: number | string, criterionId: string) => {
    if (typeof value !== 'number') return false;
    return value === getBestScoreForCriterion(criterionId);
  };

  return (
    <div className="bg-white  rounded-lg overflow-hidden">
      {title && (
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">{title}</h3>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Option
              </th>
              {criteria.map((criterion) => (
                <th
                  key={criterion.id}
                  className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  <div>
                    <div>{criterion.name}</div>
                    {showWeights && criterion.weight && (
                      <div className="text-xs text-gray-400 normal-case font-normal">
                        Weight: {criterion.weight}x
                      </div>
                    )}
                  </div>
                </th>
              ))}
              {options.some(opt => opt.totalScore !== undefined) && (
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total Score
                </th>
              )}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {options.map((option) => (
              <tr key={option.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="flex items-center gap-2">
                      <div className="text-sm font-medium text-gray-900">
                        {option.name}
                      </div>
                      {getRecommendationBadge(option)}
                    </div>
                    {option.description && (
                      <div className="text-sm text-gray-500 mt-1">
                        {option.description}
                      </div>
                    )}
                  </div>
                </td>
                {criteria.map((criterion) => {
                  const value = option.scores[criterion.id];
                  const isHighest = typeof value === 'number' && isHighestScore(value, criterion.id);

                  return (
                    <td
                      key={criterion.id}
                      className={`px-4 py-4 whitespace-nowrap text-center text-sm ${showScores ? getScoreColor(value, criterion.id) : 'text-gray-900'
                        } ${isHighest ? 'font-bold' : ''}`}
                    >
                      <div className={`inline-block px-2 py-1 rounded ${showScores ? getScoreColor(value, criterion.id) : ''
                        }`}>
                        {formatValue(value, criterion.format)}
                        {isHighest && <span className="ml-1">🏆</span>}
                      </div>
                    </td>
                  );
                })}
                {option.totalScore !== undefined && (
                  <td className="px-4 py-4 whitespace-nowrap text-center">
                    <div className="text-sm font-bold text-blue-900">
                      {option.totalScore.toFixed(1)}
                    </div>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {variant === 'detailed' && (
        <div className="px-6 py-4 border-t border-gray-100 bg-gray-50">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Criteria Details</h4>
          <div className="space-y-1 text-xs text-gray-600">
            {criteria.map((criterion) => (
              <div key={criterion.id} className="flex justify-between">
                <span>{criterion.name}:</span>
                <span>{criterion.description || 'No description'}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {(onApprove || onDisapprove) && (
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex gap-2">
          {onApprove && (
            <button
              onClick={onApprove}
              className="px-4 py-2 bg-green-50 text-green-700 rounded-md hover:bg-green-100 transition-colors text-sm font-medium"
            >
              Approve Comparison
            </button>
          )}
          {onDisapprove && (
            <button
              onClick={onDisapprove}
              className="px-4 py-2 bg-red-50 text-red-700 rounded-md hover:bg-red-100 transition-colors text-sm font-medium"
            >
              Disapprove Comparison
            </button>
          )}
        </div>
      )}
    </div>
  );
}