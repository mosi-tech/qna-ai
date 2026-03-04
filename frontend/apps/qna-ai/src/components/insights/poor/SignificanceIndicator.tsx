/**
 * SignificanceIndicator
 * 
 * Description: Shows statistical significance and confidence levels
 * Use Cases: A/B test results, statistical analysis, hypothesis testing, model validation
 * Data Format: Statistical test results with p-values, confidence intervals, effect sizes
 * 
 * @param pValue - P-value from statistical test
 * @param confidenceLevel - Confidence level (e.g., 0.95 for 95%)
 * @param effectSize - Effect size measure
 * @param testType - Type of statistical test performed
 * @param sampleSize - Sample size used in analysis
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface SignificanceIndicatorProps {
  pValue: number;
  confidenceLevel?: number;
  effectSize?: number;
  testType?: string;
  sampleSize?: number;
  hypothesis?: string;
  confidenceInterval?: {
    lower: number;
    upper: number;
  };
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function SignificanceIndicator({
  pValue,
  confidenceLevel = 0.95,
  effectSize,
  testType,
  sampleSize,
  hypothesis,
  confidenceInterval,
  onApprove,
  onDisapprove,
  variant = 'default'
}: SignificanceIndicatorProps) {

  const alpha = 1 - confidenceLevel;
  const isSignificant = pValue < alpha;
  const significanceLevel = confidenceLevel * 100;

  const getSignificanceLevel = () => {
    if (pValue < 0.001) return 'Very Strong';
    if (pValue < 0.01) return 'Strong';
    if (pValue < 0.05) return 'Moderate';
    if (pValue < 0.1) return 'Weak';
    return 'Not Significant';
  };

  const getSignificanceColor = () => {
    if (pValue < 0.001) return 'text-green-800 bg-green-100 border-green-300';
    if (pValue < 0.01) return 'text-green-700 bg-green-50 border-green-200';
    if (pValue < 0.05) return 'text-blue-700 bg-blue-50 border-blue-200';
    if (pValue < 0.1) return 'text-yellow-700 bg-yellow-50 border-yellow-200';
    return 'text-red-700 bg-red-50 border-red-200';
  };

  const getEffectSizeInterpretation = () => {
    if (!effectSize) return null;

    const absEffect = Math.abs(effectSize);
    if (absEffect < 0.2) return 'Small';
    if (absEffect < 0.5) return 'Medium';
    if (absEffect < 0.8) return 'Large';
    return 'Very Large';
  };

  const getEffectSizeColor = () => {
    if (!effectSize) return 'text-gray-600';

    const absEffect = Math.abs(effectSize);
    if (absEffect < 0.2) return 'text-gray-600';
    if (absEffect < 0.5) return 'text-blue-600';
    if (absEffect < 0.8) return 'text-green-600';
    return 'text-green-800';
  };

  const formatPValue = () => {
    if (pValue < 0.001) return '< 0.001';
    return pValue.toFixed(4);
  };

  const getSampleSizeAdequacy = () => {
    if (!sampleSize) return null;

    if (sampleSize < 30) return { label: 'Small', color: 'text-red-600' };
    if (sampleSize < 100) return { label: 'Moderate', color: 'text-yellow-600' };
    if (sampleSize < 1000) return { label: 'Good', color: 'text-green-600' };
    return { label: 'Excellent', color: 'text-green-700' };
  };

  const sampleAdequacy = getSampleSizeAdequacy();
  const effectSizeLabel = getEffectSizeInterpretation();

  return (
    <div className="bg-white  rounded-lg p-6">
      <div className="mb-4">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Statistical Significance</h3>
        {hypothesis && (
          <p className="text-sm text-gray-600 mb-4">{hypothesis}</p>
        )}
      </div>

      {/* Main significance indicator */}
      <div className={`border rounded-lg p-4 mb-4 ${getSignificanceColor()}`}>
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-lg font-bold">
                {isSignificant ? '✓' : '✗'}
              </span>
              <div className="font-semibold">
                {isSignificant ? 'Statistically Significant' : 'Not Significant'}
              </div>
            </div>
            <div className="text-sm opacity-90">
              {getSignificanceLevel()} evidence (α = {alpha})
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm opacity-75">p-value</div>
            <div className="text-2xl font-bold">{formatPValue()}</div>
          </div>
        </div>
      </div>

      {/* Statistical details grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-sm text-gray-500">Confidence Level</div>
          <div className="text-lg font-semibold text-gray-900">{significanceLevel}%</div>
        </div>

        {effectSize !== undefined && (
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-500">Effect Size</div>
            <div className={`text-lg font-semibold ${getEffectSizeColor()}`}>
              {effectSize.toFixed(3)}
            </div>
            {effectSizeLabel && (
              <div className="text-xs text-gray-600">{effectSizeLabel}</div>
            )}
          </div>
        )}

        {sampleSize && (
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-500">Sample Size</div>
            <div className="text-lg font-semibold text-gray-900">{sampleSize.toLocaleString()}</div>
            {sampleAdequacy && (
              <div className={`text-xs ${sampleAdequacy.color}`}>{sampleAdequacy.label}</div>
            )}
          </div>
        )}
      </div>

      {/* Confidence interval */}
      {confidenceInterval && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <div className="text-sm font-medium text-blue-900 mb-2">
            {significanceLevel}% Confidence Interval
          </div>
          <div className="flex items-center justify-center space-x-4">
            <div className="text-sm text-blue-800">
              [{confidenceInterval.lower.toFixed(3)}, {confidenceInterval.upper.toFixed(3)}]
            </div>
          </div>
          <div className="text-xs text-blue-700 text-center mt-2">
            We are {significanceLevel}% confident the true value lies within this range
          </div>
        </div>
      )}

      {/* Test details */}
      {variant === 'detailed' && (testType || hypothesis) && (
        <div className="bg-gray-50 rounded-lg p-4 mb-4">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Test Details</h4>
          <div className="space-y-2 text-sm">
            {testType && (
              <div className="flex justify-between">
                <span className="text-gray-600">Test Type:</span>
                <span className="text-gray-900 font-medium">{testType}</span>
              </div>
            )}
            <div className="flex justify-between">
              <span className="text-gray-600">Significance Level (α):</span>
              <span className="text-gray-900 font-medium">{alpha}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Critical Value:</span>
              <span className="text-gray-900 font-medium">p &lt; {alpha}</span>
            </div>
          </div>
        </div>
      )}

      {/* Interpretation */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="text-sm font-medium text-gray-900 mb-2">Interpretation</h4>
        <p className="text-sm text-gray-700 leading-relaxed">
          {isSignificant
            ? `The result is statistically significant (p = ${formatPValue()}) at the ${significanceLevel}% confidence level. This provides ${getSignificanceLevel().toLowerCase()} evidence against the null hypothesis.`
            : `The result is not statistically significant (p = ${formatPValue()}) at the ${significanceLevel}% confidence level. There is insufficient evidence to reject the null hypothesis.`
          }
          {effectSize && effectSizeLabel && (
            ` The effect size of ${effectSize.toFixed(3)} indicates a ${effectSizeLabel.toLowerCase()} practical effect.`
          )}
        </p>
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