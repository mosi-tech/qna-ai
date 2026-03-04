/**
 * VelocityIndicator
 * 
 * Description: Visual representation of speed/pace with velocity bars and gauges
 * Use Cases: Recovery speed, trading velocity, momentum analysis, rate changes
 * Data Format: Velocity value with scale and comparison metrics
 * 
 * @param velocity - Velocity/speed value
 * @param maxVelocity - Maximum velocity for scale
 * @param label - Velocity metric label
 * @param unit - Unit of measurement (e.g., "days", "$/sec", "bps/day")
 * @param comparison - Optional comparison velocity
 * @param threshold - Optional threshold values for color coding
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface VelocityThreshold {
  slow: number;
  moderate: number;
  fast: number;
}

interface VelocityIndicatorProps {
  velocity: number;
  maxVelocity?: number;
  label: string;
  unit?: string;
  comparison?: {
    value: number;
    label: string;
  };
  threshold?: VelocityThreshold;
  direction?: 'higher-is-better' | 'lower-is-better';
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function VelocityIndicator({
  velocity,
  maxVelocity,
  label,
  unit = '',
  comparison,
  threshold,
  direction = 'higher-is-better',
  onApprove,
  onDisapprove,
  variant = 'default'
}: VelocityIndicatorProps) {

  const defaultThreshold: VelocityThreshold = threshold || {
    slow: (maxVelocity || Math.max(velocity, comparison?.value || 0)) * 0.3,
    moderate: (maxVelocity || Math.max(velocity, comparison?.value || 0)) * 0.7,
    fast: maxVelocity || Math.max(velocity, comparison?.value || 0)
  };

  const scale = maxVelocity || Math.max(velocity, comparison?.value || 0, defaultThreshold.fast);

  const getVelocityLevel = (vel: number) => {
    if (vel >= defaultThreshold.fast) return 'very-fast';
    if (vel >= defaultThreshold.moderate) return 'fast';
    if (vel >= defaultThreshold.slow) return 'moderate';
    return 'slow';
  };

  const getVelocityColor = (level: string) => {
    const isReverse = direction === 'lower-is-better';

    switch (level) {
      case 'very-fast':
        return isReverse ? 'bg-red-500' : 'bg-green-500';
      case 'fast':
        return isReverse ? 'bg-orange-500' : 'bg-green-400';
      case 'moderate':
        return 'bg-yellow-500';
      case 'slow':
        return isReverse ? 'bg-green-500' : 'bg-red-500';
      default:
        return 'bg-gray-400';
    }
  };

  const getVelocityTextColor = (level: string) => {
    const isReverse = direction === 'lower-is-better';

    switch (level) {
      case 'very-fast':
        return isReverse ? 'text-red-700' : 'text-green-700';
      case 'fast':
        return isReverse ? 'text-orange-700' : 'text-green-600';
      case 'moderate':
        return 'text-yellow-700';
      case 'slow':
        return isReverse ? 'text-green-700' : 'text-red-700';
      default:
        return 'text-gray-700';
    }
  };

  const formatValue = (value: number) => {
    if (value >= 1000) {
      return `${(value / 1000).toFixed(1)}k`;
    }
    return value.toFixed(1);
  };

  const velocityLevel = getVelocityLevel(velocity);
  const velocityPercent = scale > 0 ? (velocity / scale) * 100 : 0;
  const comparisonLevel = comparison ? getVelocityLevel(comparison.value) : null;
  const comparisonPercent = comparison && scale > 0 ? (comparison.value / scale) * 100 : 0;

  const getSpeedLabel = (level: string) => {
    switch (level) {
      case 'very-fast':
        return direction === 'lower-is-better' ? 'Very Slow' : 'Very Fast';
      case 'fast':
        return direction === 'lower-is-better' ? 'Slow' : 'Fast';
      case 'moderate':
        return 'Moderate';
      case 'slow':
        return direction === 'lower-is-better' ? 'Fast' : 'Slow';
      default:
        return 'Unknown';
    }
  };

  return (
    <div className="bg-white  rounded-lg p-6">
      <div className="mb-4">
        <h3 className="text-lg font-medium text-gray-900 mb-2">{label}</h3>

        {/* Main velocity display */}
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="text-3xl font-bold text-gray-900">
              {formatValue(velocity)}{unit && ` ${unit}`}
            </div>
            <div className={`text-sm font-medium ${getVelocityTextColor(velocityLevel)}`}>
              {getSpeedLabel(velocityLevel)}
            </div>
          </div>

          {/* Speed gauge */}
          <div className="relative w-20 h-20">
            <svg className="w-20 h-20 transform -rotate-90" viewBox="0 0 80 80">
              {/* Background circle */}
              <circle
                cx="40"
                cy="40"
                r="32"
                stroke="currentColor"
                strokeWidth="8"
                fill="none"
                className="text-gray-200"
              />
              {/* Progress circle */}
              <circle
                cx="40"
                cy="40"
                r="32"
                stroke="currentColor"
                strokeWidth="8"
                fill="none"
                strokeDasharray={201.06}
                strokeDashoffset={201.06 - (201.06 * velocityPercent) / 100}
                className={getVelocityTextColor(velocityLevel).replace('text-', 'text-')}
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-xs font-bold text-gray-700">{velocityPercent.toFixed(0)}%</span>
            </div>
          </div>
        </div>

        {/* Velocity bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-xs text-gray-600">
            <span>Velocity Scale</span>
            <span>{formatValue(scale)}{unit && ` ${unit}`}</span>
          </div>
          <div className="relative h-4 bg-gray-200 rounded-full overflow-hidden">
            {/* Threshold zones */}
            <div className="absolute inset-y-0 left-0 bg-red-300" style={{ width: `${(defaultThreshold.slow / scale) * 100}%` }}></div>
            <div className="absolute inset-y-0 bg-yellow-300" style={{
              left: `${(defaultThreshold.slow / scale) * 100}%`,
              width: `${((defaultThreshold.moderate - defaultThreshold.slow) / scale) * 100}%`
            }}></div>
            <div className="absolute inset-y-0 bg-green-300" style={{
              left: `${(defaultThreshold.moderate / scale) * 100}%`,
              width: `${((defaultThreshold.fast - defaultThreshold.moderate) / scale) * 100}%`
            }}></div>

            {/* Current velocity indicator */}
            <div
              className="absolute inset-y-0 w-1 bg-gray-900 border-l-2 border-white"
              style={{ left: `${velocityPercent}%` }}
            ></div>

            {/* Comparison indicator */}
            {comparison && (
              <div
                className="absolute inset-y-0 w-1 bg-blue-600 border-l-2 border-white"
                style={{ left: `${comparisonPercent}%` }}
              ></div>
            )}
          </div>

          {/* Scale labels */}
          <div className="flex justify-between text-xs text-gray-500">
            <span>0</span>
            <span className="text-red-600">Slow</span>
            <span className="text-yellow-600">Moderate</span>
            <span className="text-green-600">Fast</span>
          </div>
        </div>

        {/* Comparison */}
        {comparison && (
          <div className="mt-4 bg-gray-50 rounded-lg p-3">
            <div className="flex justify-between items-center text-sm">
              <div>
                <div className="text-gray-600">{comparison.label}</div>
                <div className="font-semibold text-gray-900">
                  {formatValue(comparison.value)}{unit && ` ${unit}`}
                </div>
              </div>
              <div className="text-right">
                <div className={`font-semibold ${velocity > comparison.value
                    ? (direction === 'higher-is-better' ? 'text-green-700' : 'text-red-700')
                    : (direction === 'higher-is-better' ? 'text-red-700' : 'text-green-700')
                  }`}>
                  {velocity > comparison.value ? 'Faster' : 'Slower'}
                </div>
                <div className="text-xs text-gray-500">
                  {((Math.abs(velocity - comparison.value) / comparison.value) * 100).toFixed(1)}% diff
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Detailed metrics */}
        {variant === 'detailed' && (
          <div className="mt-4 pt-4 border-t border-gray-100">
            <div className="grid grid-cols-3 gap-4 text-center text-xs">
              <div>
                <div className="text-gray-500">Relative Speed</div>
                <div className="font-semibold text-gray-900">{velocityPercent.toFixed(1)}%</div>
              </div>
              <div>
                <div className="text-gray-500">Speed Class</div>
                <div className={`font-semibold ${getVelocityTextColor(velocityLevel)}`}>
                  {getSpeedLabel(velocityLevel)}
                </div>
              </div>
              <div>
                <div className="text-gray-500">Max Scale</div>
                <div className="font-semibold text-gray-900">{formatValue(scale)}{unit}</div>
              </div>
            </div>
          </div>
        )}
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