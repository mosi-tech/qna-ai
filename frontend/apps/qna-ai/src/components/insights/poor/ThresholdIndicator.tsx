/**
 * ThresholdIndicator
 * 
 * Description: Pass/fail/near threshold status indicator
 * Use Cases: Risk thresholds, compliance checks, performance targets
 * Data Format: Current value, threshold value, and status
 * 
 * @param value - Current value
 * @param threshold - Threshold value
 * @param label - Label for the indicator
 * @param type - Threshold type (above/below/range)
 * @param format - Value formatting
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface ThresholdIndicatorProps {
  value: number;
  threshold: number | { min: number; max: number };
  label: string;
  type?: 'above' | 'below' | 'range';
  format?: 'number' | 'percentage' | 'currency';
  warningMargin?: number; // Percentage margin for warning zone
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function ThresholdIndicator({ 
  value,
  threshold,
  label,
  type = 'above',
  format = 'number',
  warningMargin = 0.1, // 10% margin for warning
  onApprove, 
  onDisapprove,
  variant = 'default' 
}: ThresholdIndicatorProps) {
  
  const formatValue = (val: number) => {
    switch (format) {
      case 'percentage':
        return `${val.toFixed(1)}%`;
      case 'currency':
        return `$${val.toLocaleString()}`;
      case 'number':
      default:
        return val.toLocaleString();
    }
  };

  const getStatus = () => {
    if (typeof threshold === 'number') {
      const margin = Math.abs(threshold * warningMargin);
      
      if (type === 'above') {
        if (value >= threshold) return 'pass';
        if (value >= threshold - margin) return 'warning';
        return 'fail';
      } else if (type === 'below') {
        if (value <= threshold) return 'pass';
        if (value <= threshold + margin) return 'warning';
        return 'fail';
      }
    } else {
      // Range type
      const { min, max } = threshold;
      const minMargin = Math.abs(min * warningMargin);
      const maxMargin = Math.abs(max * warningMargin);
      
      if (value >= min && value <= max) return 'pass';
      if ((value >= min - minMargin && value < min) || (value > max && value <= max + maxMargin)) return 'warning';
      return 'fail';
    }
    
    return 'fail';
  };

  const status = getStatus();

  const getStatusColor = () => {
    switch (status) {
      case 'pass':
        return 'text-green-800 bg-green-100 border-green-200';
      case 'warning':
        return 'text-yellow-800 bg-yellow-100 border-yellow-200';
      case 'fail':
        return 'text-red-800 bg-red-100 border-red-200';
      default:
        return 'text-gray-800 bg-gray-100 border-gray-200';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'pass':
        return '✓';
      case 'warning':
        return '⚠';
      case 'fail':
        return '✗';
      default:
        return '?';
    }
  };

  const getStatusLabel = () => {
    switch (status) {
      case 'pass':
        return 'Within Threshold';
      case 'warning':
        return 'Near Threshold';
      case 'fail':
        return 'Outside Threshold';
      default:
        return 'Unknown';
    }
  };

  const getThresholdDisplay = () => {
    if (typeof threshold === 'number') {
      return `${type === 'above' ? '≥' : '≤'} ${formatValue(threshold)}`;
    } else {
      return `${formatValue(threshold.min)} - ${formatValue(threshold.max)}`;
    }
  };

  const getDistance = () => {
    if (typeof threshold === 'number') {
      const distance = type === 'above' ? value - threshold : threshold - value;
      return distance;
    } else {
      if (value < threshold.min) return value - threshold.min;
      if (value > threshold.max) return value - threshold.max;
      return 0; // Within range
    }
  };

  const distance = getDistance();
  
  return (
    <div className={`border rounded-lg p-4 ${getStatusColor()}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-lg font-semibold">{getStatusIcon()}</span>
            <h4 className="font-medium text-gray-900">{label}</h4>
          </div>
          
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Current Value:</span>
              <span className="font-semibold">{formatValue(value)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Threshold:</span>
              <span className="font-medium">{getThresholdDisplay()}</span>
            </div>
            {status !== 'pass' && (
              <div className="flex justify-between">
                <span className="text-gray-600">Distance:</span>
                <span className={`font-medium ${distance < 0 ? 'text-red-600' : 'text-green-600'}`}>
                  {distance > 0 ? '+' : ''}{formatValue(Math.abs(distance))}
                </span>
              </div>
            )}
          </div>
        </div>
        
        <div className="text-right">
          <div className="text-xs font-medium text-gray-600 uppercase">
            {getStatusLabel()}
          </div>
        </div>
      </div>
      
      {(onApprove || onDisapprove) && (
        <div className="flex gap-2 mt-4 pt-3 border-t border-opacity-30 border-gray-400">
          {onApprove && (
            <button
              onClick={onApprove}
              className="px-3 py-1 bg-white bg-opacity-70 text-gray-800 rounded text-xs font-medium hover:bg-opacity-90 transition-colors"
            >
              Approve
            </button>
          )}
          {onDisapprove && (
            <button
              onClick={onDisapprove}
              className="px-3 py-1 bg-white bg-opacity-70 text-gray-800 rounded text-xs font-medium hover:bg-opacity-90 transition-colors"
            >
              Disapprove
            </button>
          )}
        </div>
      )}
    </div>
  );
}