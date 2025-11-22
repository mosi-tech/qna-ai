'use client';

import { insightStyles, cn } from '../shared/styles';

interface StatCardProps {
  value: string | number;
  label: string;
  subtitle?: string;
  change?: string | number;
  changeType?: 'positive' | 'negative' | 'neutral';
  color?: 'green' | 'red' | 'blue' | 'yellow' | 'purple' | 'indigo';
  trend?: 'up' | 'down' | 'neutral';
  format?: 'text' | 'number' | 'percentage' | 'currency';
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function StatCard({
  value,
  label,
  subtitle,
  change,
  changeType = 'neutral',
  color = 'blue',
  trend = 'neutral',
  format = 'text',
  onApprove,
  onDisapprove
}: StatCardProps) {

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

  const getColorClasses = (colorName: string) => {
    const colorMap = {
      green: 'text-green-600',
      red: 'text-red-600',
      blue: 'text-blue-600',
      yellow: 'text-yellow-600',
      purple: 'text-purple-600',
      indigo: 'text-indigo-600'
    };
    return colorMap[colorName as keyof typeof colorMap] || 'text-blue-600';
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

  const getChangeSymbol = (trendType: string) => {
    switch (trendType) {
      case 'up':
        return '↑';
      case 'down':
        return '↓';
      case 'neutral':
      default:
        return '';
    }
  };

  const getCardClasses = () => {
    return cn('bg-white shadow-sm rounded-lg p-3 sm:p-4 w-full');
  };

  const valueTextColor = 'text-gray-900';
  const labelTextColor = 'text-gray-700';
  const subtitleTextColor = 'text-gray-500';
  const changeTextColor = getChangeClasses(changeType);

  return (
    <div className={getCardClasses()}>
      <div className="space-y-2">
        <div className={cn('text-xs sm:text-sm font-medium uppercase tracking-wide truncate', labelTextColor)}>
          {label}
        </div>
        <div className={cn('text-xl sm:text-2xl font-bold truncate', valueTextColor)}>
          {formatValue(value, format)}
          {change && (
            <span className={cn('ml-2 text-xs', changeTextColor)}>
              {getChangeSymbol(trend)}{typeof change === 'number' ? change.toFixed(1) : change}
            </span>
          )}
        </div>
        {subtitle && (
          <div className={cn('text-xs', subtitleTextColor, 'truncate')}>
            {subtitle}
          </div>
        )}
      </div>
    </div>
  );
}
