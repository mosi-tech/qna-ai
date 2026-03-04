/**
 * ChangeIndicator
 * 
 * Description: Directional change indicator with arrows and percentage values
 * Use Cases: Performance changes, price movements, metric variations
 * Data Format: Change value, direction, and optional context
 * 
 * @param value - Change value (number or string)
 * @param direction - Change direction (up/down/neutral)
 * @param label - Optional label for the change
 * @param format - Value formatting type
 * @param size - Display size
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface ChangeIndicatorProps {
  value: number | string;
  direction?: 'up' | 'down' | 'neutral';
  label?: string;
  format?: 'number' | 'percentage' | 'currency';
  size?: 'sm' | 'md' | 'lg';
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function ChangeIndicator({ 
  value,
  direction,
  label,
  format = 'percentage',
  size = 'md',
  onApprove, 
  onDisapprove,
  variant = 'default' 
}: ChangeIndicatorProps) {
  
  const getDirection = () => {
    if (direction) return direction;
    if (typeof value === 'number') {
      if (value > 0) return 'up';
      if (value < 0) return 'down';
      return 'neutral';
    }
    return 'neutral';
  };

  const actualDirection = getDirection();

  const formatValue = (val: number | string) => {
    if (typeof val === 'string') return val;
    
    const absVal = Math.abs(val);
    switch (format) {
      case 'percentage':
        return `${absVal.toFixed(2)}%`;
      case 'currency':
        return `$${absVal.toLocaleString()}`;
      case 'number':
      default:
        return absVal.toLocaleString();
    }
  };

  const getIcon = () => {
    switch (actualDirection) {
      case 'up':
        return '↑';
      case 'down':
        return '↓';
      case 'neutral':
      default:
        return '→';
    }
  };

  const getColorClasses = () => {
    switch (actualDirection) {
      case 'up':
        return 'text-green-700 bg-green-50 border-green-200';
      case 'down':
        return 'text-red-700 bg-red-50 border-red-200';
      case 'neutral':
      default:
        return 'text-gray-700 bg-gray-50 border-gray-200';
    }
  };

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'text-sm px-2 py-1';
      case 'lg':
        return 'text-lg px-4 py-3';
      case 'md':
      default:
        return 'text-base px-3 py-2';
    }
  };

  const getIconSize = () => {
    switch (size) {
      case 'sm':
        return 'text-sm';
      case 'lg':
        return 'text-xl';
      case 'md':
      default:
        return 'text-base';
    }
  };
  
  return (
    <div className="inline-block">
      <div className={`inline-flex items-center gap-2 border rounded-lg font-medium ${getColorClasses()} ${getSizeClasses()}`}>
        <span className={getIconSize()}>
          {getIcon()}
        </span>
        <span>
          {typeof value === 'number' && actualDirection === 'up' && '+'}
          {formatValue(value)}
        </span>
        {label && (
          <span className="text-xs opacity-75">
            {label}
          </span>
        )}
      </div>
      
      {(onApprove || onDisapprove) && (
        <div className="flex gap-1 mt-2">
          {onApprove && (
            <button
              onClick={onApprove}
              className="px-2 py-1 bg-green-50 text-green-700 rounded text-xs hover:bg-green-100 transition-colors"
            >
              ✓
            </button>
          )}
          {onDisapprove && (
            <button
              onClick={onDisapprove}
              className="px-2 py-1 bg-red-50 text-red-700 rounded text-xs hover:bg-red-100 transition-colors"
            >
              ✗
            </button>
          )}
        </div>
      )}
    </div>
  );
}