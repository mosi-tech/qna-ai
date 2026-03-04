/**
 * ComparisonCard
 * 
 * Description: Generic comparison of two values with visual indicators and performance metrics
 * Use Cases: Value vs target comparison, before/after analysis, A/B testing results, baseline comparisons
 * Data Format: Primary value, comparison value, and relative metrics
 * 
 * @param value - Primary value to display
 * @param comparisonValue - Value to compare against
 * @param label - Metric label
 * @param comparisonLabel - Label for comparison value (e.g., "Target", "Previous", "Average")
 * @param format - Value formatting type
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface ComparisonCardProps {
  value: number;
  comparisonValue: number;
  label: string;
  comparisonLabel?: string;
  format?: 'number' | 'percentage' | 'currency' | 'days' | 'ratio';
  showPercentDiff?: boolean;
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function ComparisonCard({
  value,
  comparisonValue,
  label,
  comparisonLabel = "Comparison",
  format = 'number',
  showPercentDiff = true,
  onApprove,
  onDisapprove,
  variant = 'default'
}: ComparisonCardProps) {

  const formatValue = (val: number) => {
    switch (format) {
      case 'percentage':
        return `${val.toFixed(1)}%`;
      case 'currency':
        return `$${val.toLocaleString()}`;
      case 'days':
        return `${val.toFixed(1)} days`;
      case 'ratio':
        return `${val.toFixed(2)}x`;
      case 'number':
      default:
        return val.toLocaleString();
    }
  };

  const calculateDifference = () => {
    return value - comparisonValue;
  };

  const calculatePercentDifference = () => {
    if (comparisonValue === 0) return 0;
    return ((value - comparisonValue) / Math.abs(comparisonValue)) * 100;
  };

  const difference = calculateDifference();
  const percentDiff = calculatePercentDifference();
  const isHigher = difference > 0;
  const isEqual = Math.abs(difference) < 0.001; // Handle floating point precision

  const getComparisonColor = () => {
    if (isEqual) return 'text-gray-700 bg-gray-50 border-gray-200';
    return isHigher
      ? 'text-green-700 bg-green-50 border-green-200'
      : 'text-red-700 bg-red-50 border-red-200';
  };

  const getComparisonIcon = () => {
    if (isEqual) return '→';
    return isHigher ? '↗' : '↘';
  };

  const getComparisonLabel = () => {
    if (isEqual) return 'Equal';
    return isHigher ? 'Higher' : 'Lower';
  };

  const getRelativeBarWidth = () => {
    const maxVal = Math.max(Math.abs(value), Math.abs(comparisonValue));
    const valueWidth = maxVal > 0 ? (Math.abs(value) / maxVal) * 100 : 0;
    const comparisonWidth = maxVal > 0 ? (Math.abs(comparisonValue) / maxVal) * 100 : 0;
    return { valueWidth, comparisonWidth };
  };

  const { valueWidth, comparisonWidth } = getRelativeBarWidth();

  return (
    <div className="bg-white  rounded-lg p-6">
      <div className="mb-4">
        <h3 className="text-lg font-medium text-gray-900 mb-6">{label}</h3>

        {/* Side by Side Comparison */}
        <div className="grid grid-cols-2 gap-6">

          {/* Primary Value */}
          <div className="text-center p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="text-sm font-medium text-blue-800 mb-2">Current</div>
            <div className="text-3xl font-bold text-blue-900 mb-2">{formatValue(value)}</div>
            <div className={`text-sm font-medium ${isHigher ? 'text-green-600' : 'text-gray-600'}`}>
              {isHigher ? '🏆 Better' : 'Lower'}
            </div>
          </div>

          {/* Comparison Value */}
          <div className="text-center p-4 bg-gray-50 rounded-lg ">
            <div className="text-sm font-medium text-gray-700 mb-2">{comparisonLabel}</div>
            <div className="text-3xl font-bold text-gray-900 mb-2">{formatValue(comparisonValue)}</div>
            <div className={`text-sm font-medium ${!isHigher ? 'text-green-600' : 'text-gray-600'}`}>
              {!isHigher ? '🏆 Better' : 'Lower'}
            </div>
          </div>

        </div>

        {/* Difference Summary */}
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-center gap-4">
            <div className="text-center">
              <div className="text-sm text-gray-600 mb-1">Difference</div>
              <div className={`text-xl font-bold ${isHigher ? 'text-green-600' : 'text-red-600'}`}>
                {difference > 0 ? '+' : ''}{formatValue(Math.abs(difference))}
              </div>
            </div>

            {showPercentDiff && !isEqual && (
              <>
                <div className="h-8 w-px bg-gray-300"></div>
                <div className="text-center">
                  <div className="text-sm text-gray-600 mb-1">Relative Difference</div>
                  <div className={`text-xl font-bold ${percentDiff > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {percentDiff > 0 ? '+' : ''}{percentDiff.toFixed(1)}%
                  </div>
                </div>
              </>
            )}

            <div className="h-8 w-px bg-gray-300"></div>
            <div className="text-center">
              <div className="text-sm text-gray-600 mb-1">Result</div>
              <div className={`text-lg font-semibold ${isHigher ? 'text-blue-600' : 'text-gray-600'}`}>
                {isHigher ? 'Higher' : 'Lower'}
              </div>
            </div>
          </div>
        </div>

      </div>

      {(onApprove || onDisapprove) && (
        <div className="flex gap-2 pt-4 border-t border-gray-100">
          {onApprove && (
            <button
              onClick={onApprove}
              className="px-4 py-2 bg-green-50 text-green-700 rounded-md hover:bg-green-100 transition-colors text-sm font-medium"
            >
              Approve
            </button>
          )}
          {onDisapprove && (
            <button
              onClick={onDisapprove}
              className="px-4 py-2 bg-red-50 text-red-700 rounded-md hover:bg-red-100 transition-colors text-sm font-medium"
            >
              Disapprove
            </button>
          )}
        </div>
      )}
    </div>
  );
}