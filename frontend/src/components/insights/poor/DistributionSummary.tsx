/**
 * DistributionSummary
 * 
 * Description: Textual summary of data distribution (min/max/mean/count)
 * Use Cases: Statistical summaries, data overviews, range analysis
 * Data Format: Distribution statistics object with min, max, mean, count, etc.
 * 
 * @param data - Distribution statistics
 * @param title - Optional title for the summary
 * @param format - Value formatting type
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface DistributionData {
  min: number;
  max: number;
  mean: number;
  median?: number;
  count: number;
  stdDev?: number;
  percentile25?: number;
  percentile75?: number;
}

interface DistributionSummaryProps {
  data: DistributionData;
  title?: string;
  format?: 'number' | 'percentage' | 'currency';
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function DistributionSummary({
  data,
  title,
  format = 'number',
  onApprove,
  onDisapprove,
  variant = 'default'
}: DistributionSummaryProps) {

  const formatValue = (value: number) => {
    switch (format) {
      case 'percentage':
        return `${value.toFixed(2)}%`;
      case 'currency':
        return `$${value.toLocaleString()}`;
      case 'number':
      default:
        return value.toLocaleString();
    }
  };

  const getRange = () => data.max - data.min;
  const getVariability = () => {
    if (data.stdDev) {
      const cv = (data.stdDev / data.mean) * 100;
      if (cv < 15) return { level: 'Low', color: 'text-green-600' };
      if (cv < 30) return { level: 'Moderate', color: 'text-yellow-600' };
      return { level: 'High', color: 'text-red-600' };
    }
    return null;
  };

  const variability = getVariability();

  return (
    <div className="bg-white  rounded-lg p-6">
      {title && (
        <h3 className="text-lg font-medium text-gray-900 mb-4">{title}</h3>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-xs text-gray-500 uppercase font-medium">Min</div>
          <div className="text-lg font-semibold text-gray-900">{formatValue(data.min)}</div>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-xs text-gray-500 uppercase font-medium">Max</div>
          <div className="text-lg font-semibold text-gray-900">{formatValue(data.max)}</div>
        </div>
        <div className="text-center p-3 bg-blue-50 rounded-lg">
          <div className="text-xs text-blue-600 uppercase font-medium">Mean</div>
          <div className="text-lg font-semibold text-blue-900">{formatValue(data.mean)}</div>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-xs text-gray-500 uppercase font-medium">Count</div>
          <div className="text-lg font-semibold text-gray-900">{data.count.toLocaleString()}</div>
        </div>
      </div>

      {variant === 'detailed' && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
          {data.median && (
            <div className="text-center p-2 bg-gray-50 rounded">
              <div className="text-xs text-gray-500 uppercase">Median</div>
              <div className="font-semibold text-gray-900">{formatValue(data.median)}</div>
            </div>
          )}
          <div className="text-center p-2 bg-gray-50 rounded">
            <div className="text-xs text-gray-500 uppercase">Range</div>
            <div className="font-semibold text-gray-900">{formatValue(getRange())}</div>
          </div>
          {data.stdDev && (
            <div className="text-center p-2 bg-gray-50 rounded">
              <div className="text-xs text-gray-500 uppercase">Std Dev</div>
              <div className="font-semibold text-gray-900">{formatValue(data.stdDev)}</div>
            </div>
          )}
        </div>
      )}

      <div className="bg-gray-50 rounded-lg p-4 space-y-2">
        <div className="text-sm font-medium text-gray-900">Distribution Summary</div>
        <p className="text-sm text-gray-700">
          The data ranges from {formatValue(data.min)} to {formatValue(data.max)} across {data.count} observations,
          with an average of {formatValue(data.mean)}.
        </p>
        {variability && (
          <p className="text-sm">
            <span className="text-gray-700">Variability is </span>
            <span className={`font-medium ${variability.color}`}>{variability.level}</span>
            <span className="text-gray-700"> based on the coefficient of variation.</span>
          </p>
        )}
      </div>

      {(onApprove || onDisapprove) && (
        <div className="flex gap-2 mt-6 pt-4 border-t border-gray-100">
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