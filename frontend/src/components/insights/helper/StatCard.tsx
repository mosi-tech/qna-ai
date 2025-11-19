/**
 * StatCard
 * 
 * Description: Single statistic display with value, label, and optional change indicator
 * Use Cases: KPIs, financial metrics, performance indicators
 * Data Format: Value, label, and optional change/trend data
 * 
 * @param value - The main statistic value
 * @param label - Descriptive label for the statistic
 * @param change - Optional change value (number or string)
 * @param changeType - Type of change for styling
 * @param format - Value formatting type
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

import { insightStyles, cn } from '../shared/styles';

interface StatCardProps {
  value: string | number;
  label: string;
  change?: string | number;
  changeType?: 'positive' | 'negative' | 'neutral';
  format?: 'text' | 'number' | 'percentage' | 'currency';
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function StatCard({
  value,
  label,
  change,
  changeType = 'neutral',
  format = 'text',
  onApprove,
  onDisapprove,
  variant = 'default'
}: StatCardProps) {

  const getVariantConfig = () => {
    switch (variant) {
      case 'compact':
        return {
          padding: 'p-3 sm:p-3.5',
          spacing: 'space-y-1',
          labelSize: 'text-sm',
          valueSize: 'text-base sm:text-lg font-bold',
          changeSize: 'text-sm'
        };
      case 'detailed':
        return {
          padding: 'p-4 sm:p-6',
          spacing: 'space-y-3',
          labelSize: 'text-sm font-medium',
          valueSize: 'text-2xl sm:text-3xl font-bold',
          changeSize: 'text-sm'
        };
      default:
        return {
          padding: 'p-3 sm:p-4',
          spacing: 'space-y-2',
          labelSize: 'text-xs sm:text-sm font-medium',
          valueSize: 'text-xl sm:text-2xl font-bold',
          changeSize: 'text-xs sm:text-sm'
        };
    }
  };

  const formatValue = (val: string | number, fmt: string) => {
    if (typeof val === 'string') return val;

    switch (fmt) {
      case 'number':
        return val.toLocaleString();
      case 'percentage':
        return `${val.toFixed(1)}%`;
      case 'currency':
        return `$${val.toLocaleString()}`;
      default:
        return val.toString();
    }
  };

  const getChangeClasses = (type: string) => {
    switch (type) {
      case 'positive':
        return insightStyles.status.success.textLight;
      case 'negative':
        return insightStyles.status.error.textLight;
      case 'neutral':
      default:
        return insightStyles.text.secondary;
    }
  };

  const getChangeSymbol = (type: string) => {
    switch (type) {
      case 'positive':
        return '↑';
      case 'negative':
        return '↓';
      case 'neutral':
      default:
        return '';
    }
  };

  const config = getVariantConfig();

  const getCardClasses = () => {
    if (variant === 'compact') {
      return cn('bg-gray-50  rounded-lg', config.padding); // Balanced styling for compact
    }
    return cn(insightStyles.card.base, config.padding);
  };

  return (
    <div className={getCardClasses()}>
      <div className={config.spacing}>
        <div className={cn(config.labelSize, 'uppercase tracking-wide truncate', insightStyles.text.tertiary)}>
          {label}
        </div>
        <div className={cn(config.valueSize, 'text-gray-900 truncate')}>
          {formatValue(value, format)}
          {change && variant === 'compact' && (
            <span className={cn('ml-2 text-xs', getChangeClasses(changeType))}>
              {getChangeSymbol(changeType)}{typeof change === 'number' ? change.toFixed(1) : change}
            </span>
          )}
        </div>
        {change && variant !== 'compact' && (
          <div className={cn(config.changeSize, 'font-medium flex items-center truncate', getChangeClasses(changeType))}>
            <span className="mr-1 flex-shrink-0">{getChangeSymbol(changeType)}</span>
            <span className="truncate">
              {typeof change === 'number' ? change.toFixed(1) : change}
              {typeof change === 'number' && format === 'percentage' && '%'}
            </span>
          </div>
        )}
      </div>

      {(onApprove || onDisapprove) && (
        <div className={cn('flex gap-1 mt-4 pt-4', insightStyles.border.divider)}>
          {onApprove && (
            <button
              onClick={onApprove}
              className={cn('flex-1 text-xs', insightStyles.button.approve.compact)}
            >
              ✓
            </button>
          )}
          {onDisapprove && (
            <button
              onClick={onDisapprove}
              className={cn('flex-1 text-xs', insightStyles.button.disapprove.compact)}
            >
              ✗
            </button>
          )}
        </div>
      )}
    </div>
  );
}