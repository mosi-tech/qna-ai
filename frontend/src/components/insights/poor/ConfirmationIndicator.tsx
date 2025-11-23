/**
 * ConfirmationIndicator
 * 
 * Description: Displays confidence levels and confirmation signals with visual indicators
 * Use Cases: Signal confirmation, reliability scores, validation status, quality indicators
 * Data Format: Numeric value with optional thresholds and descriptive text
 * 
 * @param value - The confirmation value/score
 * @param maxValue - Maximum possible value for scaling
 * @param label - Text label for the indicator
 * @param thresholds - Optional thresholds for color coding
 * @param format - Display format (percentage, score, etc.)
 * @param showDetails - Whether to show detailed breakdown
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface ThresholdLevel {
  min: number;
  max: number;
  label: string;
  color: string;
  description?: string;
}

interface ConfirmationIndicatorProps {
  value: number;
  maxValue?: number;
  label: string;
  thresholds?: ThresholdLevel[];
  format?: 'percentage' | 'score' | 'number' | 'currency';
  description?: string;
  showDetails?: boolean;
  variant?: 'default' | 'compact' | 'detailed';
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function ConfirmationIndicator({
  value,
  maxValue = 100,
  label,
  thresholds = [
    { min: 0, max: 25, label: 'Low', color: 'red', description: 'Weak confirmation' },
    { min: 25, max: 50, label: 'Moderate', color: 'yellow', description: 'Moderate confirmation' },
    { min: 50, max: 75, label: 'High', color: 'blue', description: 'Strong confirmation' },
    { min: 75, max: 100, label: 'Very High', color: 'green', description: 'Very strong confirmation' }
  ],
  format = 'percentage',
  description,
  showDetails = true,
  variant = 'default',
  onApprove,
  onDisapprove
}: ConfirmationIndicatorProps) {

  const formatValue = (val: number) => {
    switch (format) {
      case 'percentage':
        return `${val.toFixed(1)}%`;
      case 'currency':
        return `$${val.toLocaleString()}`;
      case 'score':
        return `${val.toFixed(2)}`;
      case 'number':
      default:
        return val.toLocaleString();
    }
  };

  // Normalize value to percentage for threshold calculation
  const normalizedValue = (value / maxValue) * 100;

  const getCurrentThreshold = () => {
    return thresholds.find(threshold =>
      normalizedValue >= threshold.min && normalizedValue <= threshold.max
    ) || thresholds[0];
  };

  const currentThreshold = getCurrentThreshold();

  const getProgressColor = () => {
    switch (currentThreshold.color) {
      case 'green':
        return 'bg-green-500';
      case 'blue':
        return 'bg-blue-500';
      case 'yellow':
        return 'bg-yellow-500';
      case 'red':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getBackgroundColor = () => {
    switch (currentThreshold.color) {
      case 'green':
        return 'bg-green-50';
      case 'blue':
        return 'bg-blue-50';
      case 'yellow':
        return 'bg-yellow-50';
      case 'red':
        return 'bg-red-50';
      default:
        return 'bg-gray-50';
    }
  };

  const getTextColor = () => {
    switch (currentThreshold.color) {
      case 'green':
        return 'text-green-700';
      case 'blue':
        return 'text-blue-700';
      case 'yellow':
        return 'text-yellow-700';
      case 'red':
        return 'text-red-700';
      default:
        return 'text-gray-700';
    }
  };

  const getBorderColor = () => {
    switch (currentThreshold.color) {
      case 'green':
        return 'border-green-200';
      case 'blue':
        return 'border-blue-200';
      case 'yellow':
        return 'border-yellow-200';
      case 'red':
        return 'border-red-200';
      default:
        return 'border-gray-200';
    }
  };

  const getStatusIcon = () => {
    switch (currentThreshold.color) {
      case 'green':
        return '✓';
      case 'blue':
        return '◐';
      case 'yellow':
        return '△';
      case 'red':
        return '⚠';
      default:
        return '?';
    }
  };

  if (variant === 'compact') {
    return (
      <div className={`bg-white border rounded-lg p-4 ${getBorderColor()}`}>
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm text-gray-600">{label}</div>
            <div className={`text-lg font-semibold ${getTextColor()}`}>
              {formatValue(value)} {getStatusIcon()}
            </div>
          </div>

          <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-300 ${getProgressColor()}`}
              style={{ width: `${Math.min(normalizedValue, 100)}%` }}
            ></div>
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
    <div className={`bg-white  rounded-lg p-6`}>
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-medium text-gray-900">{label}</h3>
          {description && (
            <p className="text-sm text-gray-600 mt-1">{description}</p>
          )}
        </div>
        <div className={`px-3 py-1 rounded-full text-sm font-medium ${getBackgroundColor()} ${getTextColor()}`}>
          {getStatusIcon()} {currentThreshold.label}
        </div>
      </div>

      {/* Main value display */}
      <div className="text-center mb-6">
        <div className={`text-4xl font-bold ${getTextColor()} mb-2`}>
          {formatValue(value)}
        </div>
        <div className="text-sm text-gray-500">
          of {formatValue(maxValue)} maximum
        </div>
      </div>

      {/* Progress bar */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs text-gray-500">0</span>
          <span className="text-xs text-gray-500">{formatValue(maxValue)}</span>
        </div>
        <div className="w-full h-4 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${getProgressColor()}`}
            style={{ width: `${Math.min(normalizedValue, 100)}%` }}
          ></div>
        </div>
        <div className="text-center mt-2">
          <span className={`text-sm font-medium ${getTextColor()}`}>
            {normalizedValue.toFixed(1)}% of maximum
          </span>
        </div>
      </div>

      {/* Threshold details */}
      {showDetails && variant === 'detailed' && (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Confirmation Levels</h4>
          <div className="space-y-2">
            {thresholds.map((threshold, index) => (
              <div
                key={index}
                className={`flex items-center justify-between p-2 rounded-lg ${threshold === currentThreshold ? getBackgroundColor() : 'bg-gray-50'
                  }`}
              >
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${threshold.color === 'green' ? 'bg-green-500' :
                      threshold.color === 'blue' ? 'bg-blue-500' :
                        threshold.color === 'yellow' ? 'bg-yellow-500' :
                          threshold.color === 'red' ? 'bg-red-500' : 'bg-gray-500'
                    }`}></div>
                  <span className="text-sm font-medium">{threshold.label}</span>
                  {threshold === currentThreshold && (
                    <span className="text-xs text-gray-500">← Current</span>
                  )}
                </div>
                <div className="text-xs text-gray-500">
                  {threshold.min}%-{threshold.max}%
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Analysis note */}
      {showDetails && (
        <div className={`p-3 rounded-lg ${getBackgroundColor()}`}>
          <div className="text-sm">
            <span className="font-medium">Status:</span> {currentThreshold.description || currentThreshold.label}
            {normalizedValue >= 75 && (
              <span className="text-green-700"> - Exceeds expectations</span>
            )}
            {normalizedValue < 25 && (
              <span className="text-red-700"> - Below minimum threshold</span>
            )}
          </div>
        </div>
      )}

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