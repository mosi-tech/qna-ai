/**
 * StatGroup
 * 
 * Description: Collection of StatCards arranged in a responsive grid
 * Use Cases: Dashboard metrics, KPI displays, summary statistics
 * Data Format: Array of stat objects for StatCard components
 * 
 * @param stats - Array of statistic objects
 * @param title - Optional title for the stat group
 * @param columns - Number of columns (2-4)
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

import StatCard from './helper/StatCard';
import { insightStyles, cn } from './shared/styles';

interface Stat {
  value: string | number;
  label: string;
  change?: string | number;
  changeType?: 'positive' | 'negative' | 'neutral';
  format?: 'text' | 'number' | 'percentage' | 'currency';
}

interface StatGroupProps {
  stats: Stat[];
  title?: string;
  columns?: 2 | 3 | 4;
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'horizontal' | 'vertical';
}

export default function StatGroup({ 
  stats,
  title,
  columns = 3,
  onApprove, 
  onDisapprove,
  variant = 'default' 
}: StatGroupProps) {
  
  const getVariantConfig = () => {
    switch (variant) {
      case 'compact':
        return {
          columns: 2,
          spacing: 'gap-1.5 sm:gap-2',
          titleSize: 'text-xs sm:text-sm',
          containerPadding: 'p-2 sm:p-2.5'
        };
      case 'horizontal':
        return {
          columns: Math.min(stats.length, 6),
          spacing: 'gap-2 sm:gap-3 lg:gap-4',
          titleSize: 'text-base sm:text-lg', 
          containerPadding: 'p-3 sm:p-4'
        };
      case 'vertical':
        return {
          columns: 1,
          spacing: 'gap-2 sm:gap-3',
          titleSize: 'text-sm sm:text-base',
          containerPadding: 'p-3 sm:p-4'
        };
      default:
        return {
          columns: columns || 3,
          spacing: insightStyles.spacing.gap,
          titleSize: insightStyles.typography.h3,
          containerPadding: insightStyles.spacing.component
        };
    }
  };

  const config = getVariantConfig();
  
  const getGridClasses = () => {
    const baseGrid = 'grid';
    
    // Enhanced responsive grid classes for better overflow handling
    switch (config.columns) {
      case 1:
        return cn(baseGrid, 'grid-cols-1', config.spacing);
      case 2:
        return cn(baseGrid, 'grid-cols-1 sm:grid-cols-2', config.spacing);
      case 3:
        return cn(baseGrid, 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3', config.spacing);
      case 4:
        return cn(baseGrid, 'grid-cols-2 sm:grid-cols-3 lg:grid-cols-4', config.spacing);
      case 5:
        return cn(baseGrid, 'grid-cols-2 sm:grid-cols-3 lg:grid-cols-5', config.spacing);
      case 6:
        return cn(baseGrid, 'grid-cols-2 sm:grid-cols-4 lg:grid-cols-6', config.spacing);
      default:
        return cn(baseGrid, 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3', config.spacing);
    }
  };
  
  return (
    <div className={config.containerPadding}>
      {title && (
        <div className={variant === 'compact' ? 'mb-2 sm:mb-3' : insightStyles.spacing.margin}>
          <h3 className={config.titleSize}>{title}</h3>
        </div>
      )}
      
      <div className={getGridClasses()}>
        {stats.map((stat, index) => (
          <StatCard
            key={index}
            value={stat.value}
            label={stat.label}
            change={stat.change}
            changeType={stat.changeType}
            format={stat.format}
            variant={variant}
          />
        ))}
      </div>
      
      {(onApprove || onDisapprove) && (
        <div className={cn("flex gap-2 mt-6 pt-4", insightStyles.border.divider)}>
          {onApprove && (
            <button
              onClick={onApprove}
              className={insightStyles.button.approve.base}
            >
              Approve Group
            </button>
          )}
          {onDisapprove && (
            <button
              onClick={onDisapprove}
              className={insightStyles.button.disapprove.base}
            >
              Disapprove Group
            </button>
          )}
        </div>
      )}
    </div>
  );
}