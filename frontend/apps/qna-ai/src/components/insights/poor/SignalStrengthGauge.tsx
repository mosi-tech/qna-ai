/**
 * SignalStrengthGauge
 * 
 * Description: Displays signal strength or intensity levels with visual gauge representation
 * Use Cases: Signal quality, strength indicators, intensity ratings, quality scores, performance levels
 * Data Format: Numeric value with optional thresholds and descriptive labels
 * 
 * @param strength - The signal strength value (0-100 or custom scale)
 * @param maxStrength - Maximum possible strength value
 * @param label - Text label for the gauge
 * @param thresholds - Custom strength level thresholds
 * @param showNumeric - Whether to show numeric value
 * @param showBars - Whether to show bar visualization
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface StrengthThreshold {
  min: number;
  max: number;
  label: string;
  color: string;
  description: string;
}

interface SignalStrengthGaugeProps {
  strength: number;
  maxStrength?: number;
  label: string;
  description?: string;
  thresholds?: StrengthThreshold[];
  unit?: string;
  showNumeric?: boolean;
  showBars?: boolean;
  showDetails?: boolean;
  variant?: 'default' | 'compact' | 'detailed';
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function SignalStrengthGauge({
  strength,
  maxStrength = 100,
  label,
  description,
  thresholds = [
    { min: 0, max: 20, label: 'Very Weak', color: 'red', description: 'Poor signal quality' },
    { min: 20, max: 40, label: 'Weak', color: 'orange', description: 'Below average signal' },
    { min: 40, max: 60, label: 'Moderate', color: 'yellow', description: 'Average signal strength' },
    { min: 60, max: 80, label: 'Strong', color: 'blue', description: 'Above average signal' },
    { min: 80, max: 100, label: 'Very Strong', color: 'green', description: 'Excellent signal quality' }
  ],
  unit = '%',
  showNumeric = true,
  showBars = true,
  showDetails = true,
  variant = 'default',
  onApprove,
  onDisapprove
}: SignalStrengthGaugeProps) {

  // Normalize strength to percentage
  const normalizedStrength = Math.min(100, (strength / maxStrength) * 100);
  const strengthValue = (strength / maxStrength) * 100;

  const getCurrentThreshold = () => {
    return thresholds.find(threshold =>
      strengthValue >= threshold.min && strengthValue <= threshold.max
    ) || thresholds[0];
  };

  const currentThreshold = getCurrentThreshold();

  const getColorClasses = (color: string) => {
    const colorMap = {
      red: { bg: 'bg-red-500', text: 'text-red-700', bgLight: 'bg-red-50', border: 'border-red-200' },
      orange: { bg: 'bg-orange-500', text: 'text-orange-700', bgLight: 'bg-orange-50', border: 'border-orange-200' },
      yellow: { bg: 'bg-yellow-500', text: 'text-yellow-700', bgLight: 'bg-yellow-50', border: 'border-yellow-200' },
      blue: { bg: 'bg-blue-500', text: 'text-blue-700', bgLight: 'bg-blue-50', border: 'border-blue-200' },
      green: { bg: 'bg-green-500', text: 'text-green-700', bgLight: 'bg-green-50', border: 'border-green-200' }
    };
    return colorMap[color as keyof typeof colorMap] || colorMap.red;
  };

  const currentColors = getColorClasses(currentThreshold.color);

  const getSignalBars = () => {
    const numBars = 5;
    const barsToFill = Math.ceil((strengthValue / 100) * numBars);

    return Array.from({ length: numBars }, (_, index) => {
      const isActive = index < barsToFill;
      let barColor = 'bg-gray-300';

      if (isActive) {
        if (index === 0) barColor = 'bg-red-500';
        else if (index === 1) barColor = 'bg-orange-500';
        else if (index === 2) barColor = 'bg-yellow-500';
        else if (index === 3) barColor = 'bg-blue-500';
        else if (index === 4) barColor = 'bg-green-500';
      }

      return { active: isActive, color: barColor, height: (index + 1) * 20 };
    });
  };

  const signalBars = getSignalBars();

  if (variant === 'compact') {
    return (
      <div className="bg-white  rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="text-sm text-gray-600">{label}</div>
            <div className={`text-lg font-semibold ${currentColors.text}`}>
              {currentThreshold.label}
            </div>
            {showNumeric && (
              <div className="text-xs text-gray-500">
                {strength.toFixed(1)}{unit} / {maxStrength}{unit}
              </div>
            )}
          </div>

          {showBars && (
            <div className="flex items-end gap-1 ml-4">
              {signalBars.map((bar, index) => (
                <div
                  key={index}
                  className={`w-2 rounded-t transition-all duration-300 ${bar.color}`}
                  style={{ height: `${bar.height}px` }}
                ></div>
              ))}
            </div>
          )}
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
        <div className={`px-3 py-1 rounded-full text-sm font-medium ${currentColors.bgLight} ${currentColors.text}`}>
          {currentThreshold.label}
        </div>
      </div>

      {/* Central gauge display */}
      <div className="text-center mb-6">
        {showBars && (
          <div className="flex justify-center items-end gap-2 mb-4 h-20">
            {signalBars.map((bar, index) => (
              <div key={index} className="flex flex-col items-center">
                <div
                  className={`w-6 rounded-t transition-all duration-500 ${bar.color}`}
                  style={{ height: `${bar.height}px` }}
                ></div>
                <div className="text-xs text-gray-400 mt-1">{index + 1}</div>
              </div>
            ))}
          </div>
        )}

        {showNumeric && (
          <div className={`text-4xl font-bold ${currentColors.text} mb-2`}>
            {strength.toFixed(1)}{unit}
          </div>
        )}

        <div className="text-sm text-gray-600">
          {currentThreshold.description}
        </div>
      </div>

      {/* Linear progress indicator */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs text-gray-500">0{unit}</span>
          <span className="text-xs text-gray-600">Signal Strength</span>
          <span className="text-xs text-gray-500">{maxStrength}{unit}</span>
        </div>
        <div className="w-full h-4 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${currentColors.bg}`}
            style={{ width: `${Math.min(normalizedStrength, 100)}%` }}
          ></div>
        </div>
        <div className="text-center mt-2">
          <span className={`text-sm font-medium ${currentColors.text}`}>
            {normalizedStrength.toFixed(1)}% of maximum strength
          </span>
        </div>
      </div>

      {/* Strength level breakdown */}
      {showDetails && variant === 'detailed' && (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Strength Levels</h4>
          <div className="space-y-2">
            {thresholds.map((threshold, index) => {
              const thresholdColors = getColorClasses(threshold.color);
              const isActive = threshold === currentThreshold;

              return (
                <div
                  key={index}
                  className={`flex items-center justify-between p-3 rounded-lg ${isActive ? thresholdColors.bgLight : 'bg-gray-50'
                    }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-4 h-4 rounded-full ${thresholdColors.bg}`}></div>
                    <div>
                      <div className="text-sm font-medium">{threshold.label}</div>
                      <div className="text-xs text-gray-500">{threshold.description}</div>
                    </div>
                    {isActive && (
                      <span className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded-full">
                        Current
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-gray-500">
                    {threshold.min}{unit}-{threshold.max}{unit}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Signal quality metrics */}
      {showDetails && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="bg-gray-50 rounded-lg p-3 text-center">
            <div className="text-xs text-gray-500 mb-1">Current Level</div>
            <div className={`font-semibold ${currentColors.text}`}>
              {strength.toFixed(1)}{unit}
            </div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3 text-center">
            <div className="text-xs text-gray-500 mb-1">Percentage</div>
            <div className="font-semibold text-gray-900">
              {normalizedStrength.toFixed(1)}%
            </div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3 text-center">
            <div className="text-xs text-gray-500 mb-1">Quality</div>
            <div className={`font-semibold ${currentColors.text}`}>
              {currentThreshold.label}
            </div>
          </div>
        </div>
      )}

      {/* Analysis summary */}
      <div className={`p-3 rounded-lg ${currentColors.bgLight}`}>
        <div className="text-sm">
          <span className="font-medium">Assessment:</span> {currentThreshold.description}
          {normalizedStrength >= 80 && (
            <span className="text-green-700"> - Optimal performance level achieved</span>
          )}
          {normalizedStrength < 40 && (
            <span className="text-red-700"> - Signal enhancement recommended</span>
          )}
        </div>
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