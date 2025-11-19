/**
 * StatWithConfidence
 * 
 * Description: Displays statistical values with confidence intervals, margins of error, and reliability indicators
 * Use Cases: Statistical estimates, forecast values, survey results, model predictions, research findings
 * Data Format: Primary value with confidence interval bounds and optional metadata
 * 
 * @param value - The primary statistical value
 * @param confidenceLevel - Confidence level (e.g., 0.95 for 95%)
 * @param confidenceInterval - Lower and upper bounds
 * @param marginOfError - Optional margin of error
 * @param sampleSize - Sample size for context
 * @param label - Text label for the statistic
 * @param format - Display format (percentage, number, currency, etc.)
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface ConfidenceInterval {
  lower: number;
  upper: number;
}

interface StatWithConfidenceProps {
  value: number;
  confidenceLevel?: number;
  confidenceInterval: ConfidenceInterval;
  marginOfError?: number;
  sampleSize?: number;
  label: string;
  description?: string;
  format?: 'number' | 'percentage' | 'currency' | 'decimal';
  unit?: string;
  showDistribution?: boolean;
  variant?: 'default' | 'compact' | 'detailed';
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function StatWithConfidence({
  value,
  confidenceLevel = 0.95,
  confidenceInterval,
  marginOfError,
  sampleSize,
  label,
  description,
  format = 'number',
  unit,
  showDistribution = true,
  variant = 'default',
  onApprove,
  onDisapprove
}: StatWithConfidenceProps) {

  const formatValue = (val: number) => {
    switch (format) {
      case 'percentage':
        return `${val.toFixed(1)}%`;
      case 'currency':
        return `$${val.toLocaleString()}`;
      case 'decimal':
        return val.toFixed(3);
      case 'number':
      default:
        return val.toLocaleString();
    }
  };

  const confidencePercentage = Math.round(confidenceLevel * 100);
  const intervalWidth = confidenceInterval.upper - confidenceInterval.lower;
  const valuePosition = ((value - confidenceInterval.lower) / intervalWidth) * 100;

  // Calculate margin of error if not provided
  const calculatedMarginOfError = marginOfError || (intervalWidth / 2);
  const marginOfErrorPercent = ((calculatedMarginOfError / Math.abs(value)) * 100);

  const getConfidenceColor = () => {
    if (confidenceLevel >= 0.99) return 'text-green-600';
    if (confidenceLevel >= 0.95) return 'text-blue-600';
    if (confidenceLevel >= 0.90) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceBackground = () => {
    if (confidenceLevel >= 0.99) return 'bg-green-50';
    if (confidenceLevel >= 0.95) return 'bg-blue-50';
    if (confidenceLevel >= 0.90) return 'bg-yellow-50';
    return 'bg-red-50';
  };

  const getReliabilityLabel = () => {
    if (confidenceLevel >= 0.99) return 'Very High';
    if (confidenceLevel >= 0.95) return 'High';
    if (confidenceLevel >= 0.90) return 'Moderate';
    return 'Low';
  };

  if (variant === 'compact') {
    return (
      <div className="bg-white  rounded-lg p-4">
        <div className="flex justify-between items-start">
          <div>
            <div className="text-sm text-gray-600">{label}</div>
            <div className="text-xl font-semibold text-gray-900">
              {formatValue(value)} {unit && <span className="text-sm text-gray-500">{unit}</span>}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              ±{formatValue(calculatedMarginOfError)} ({confidencePercentage}% CI)
            </div>
          </div>
          <div className={`px-2 py-1 rounded text-xs font-medium ${getConfidenceBackground()} ${getConfidenceColor()}`}>
            {getReliabilityLabel()}
          </div>
        </div>

        {(onApprove || onDisapprove) && (
          <div className="flex gap-2 mt-3 pt-3 border-t border-gray-100">
            {onApprove && (
              <button
                onClick={onApprove}
                className="px-3 py-1 bg-green-50 text-green-700 rounded-md hover:bg-green-100 transition-colors text-sm"
              >
                Approve
              </button>
            )}
            {onDisapprove && (
              <button
                onClick={onDisapprove}
                className="px-3 py-1 bg-red-50 text-red-700 rounded-md hover:bg-red-100 transition-colors text-sm"
              >
                Disapprove
              </button>
            )}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="bg-white  rounded-lg p-6">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-medium text-gray-900">{label}</h3>
          {description && (
            <p className="text-sm text-gray-600 mt-1">{description}</p>
          )}
        </div>
        <div className={`px-3 py-1 rounded-full text-sm font-medium ${getConfidenceBackground()} ${getConfidenceColor()}`}>
          {confidencePercentage}% Confidence
        </div>
      </div>

      {/* Main value display */}
      <div className="text-center mb-6">
        <div className="text-4xl font-bold text-gray-900 mb-2">
          {formatValue(value)}
          {unit && <span className="text-lg text-gray-500 ml-2">{unit}</span>}
        </div>
        <div className="text-sm text-gray-600">
          ±{formatValue(calculatedMarginOfError)} margin of error
          {marginOfErrorPercent < 10 && (
            <span className="ml-2 px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs">
              Low variance
            </span>
          )}
        </div>
      </div>

      {/* Confidence interval visualization */}
      {showDistribution && (
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs text-gray-500">{formatValue(confidenceInterval.lower)}</span>
            <span className="text-xs text-gray-600">{confidencePercentage}% Confidence Interval</span>
            <span className="text-xs text-gray-500">{formatValue(confidenceInterval.upper)}</span>
          </div>

          {/* Visual interval bar */}
          <div className="relative h-8 bg-gray-100 rounded-lg overflow-hidden">
            {/* Confidence interval range */}
            <div className="absolute inset-0 bg-blue-200 opacity-50"></div>

            {/* Point estimate */}
            <div
              className="absolute top-1 bottom-1 w-1 bg-blue-600 rounded"
              style={{ left: `${Math.max(0, Math.min(100, valuePosition))}%` }}
            ></div>

            {/* Value label */}
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-xs font-medium text-gray-700">
                {formatValue(value)}
              </span>
            </div>
          </div>

          <div className="mt-2 text-center">
            <span className="text-xs text-gray-500">
              Range: {formatValue(intervalWidth)} {unit || 'units'}
            </span>
          </div>
        </div>
      )}

      {/* Statistical details */}
      {variant === 'detailed' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="bg-gray-50 rounded-lg p-3 text-center">
            <div className="text-xs text-gray-500 mb-1">Lower Bound</div>
            <div className="font-semibold text-gray-900">{formatValue(confidenceInterval.lower)}</div>
          </div>
          <div className="bg-blue-50 rounded-lg p-3 text-center">
            <div className="text-xs text-blue-600 mb-1">Estimate</div>
            <div className="font-semibold text-blue-900">{formatValue(value)}</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3 text-center">
            <div className="text-xs text-gray-500 mb-1">Upper Bound</div>
            <div className="font-semibold text-gray-900">{formatValue(confidenceInterval.upper)}</div>
          </div>
        </div>
      )}

      {/* Metadata and quality indicators */}
      <div className="bg-gray-50 rounded-lg p-4 space-y-3">
        <h4 className="text-sm font-medium text-gray-900">Statistical Summary</h4>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Confidence Level:</span>
            <span className={`ml-2 font-medium ${getConfidenceColor()}`}>
              {confidencePercentage}% ({getReliabilityLabel()})
            </span>
          </div>

          {sampleSize && (
            <div>
              <span className="text-gray-600">Sample Size:</span>
              <span className="ml-2 font-medium text-gray-900">
                {sampleSize.toLocaleString()}
              </span>
              {sampleSize >= 1000 && (
                <span className="ml-2 text-green-600 text-xs">✓ Large sample</span>
              )}
            </div>
          )}

          <div>
            <span className="text-gray-600">Margin of Error:</span>
            <span className="ml-2 font-medium text-gray-900">
              ±{formatValue(calculatedMarginOfError)}
            </span>
          </div>

          <div>
            <span className="text-gray-600">Precision:</span>
            <span className="ml-2 font-medium text-gray-900">
              ±{marginOfErrorPercent.toFixed(1)}%
            </span>
            {marginOfErrorPercent < 5 && (
              <span className="ml-2 text-green-600 text-xs">✓ High</span>
            )}
          </div>
        </div>

        {variant === 'detailed' && (
          <div className="pt-2 border-t border-gray-200">
            <div className="text-xs text-gray-600">
              <strong>Interpretation:</strong> There is a {confidencePercentage}% probability that the true value lies between {formatValue(confidenceInterval.lower)} and {formatValue(confidenceInterval.upper)}.
              {marginOfErrorPercent < 5 && " The estimate shows high precision with low variance."}
              {marginOfErrorPercent > 15 && " Consider increasing sample size to improve precision."}
            </div>
          </div>
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