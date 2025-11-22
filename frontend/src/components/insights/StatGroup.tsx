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

import Container from './Container';
import StatCard from './helper/StatCard';
import { insightStyles, cn } from './shared/styles';

interface Stat {
  value: string | number;
  label: string;
  subtitle?: string;
  change?: string | number;
  changeType?: 'positive' | 'negative' | 'neutral';
  color?: 'green' | 'red' | 'blue' | 'yellow' | 'purple' | 'indigo';
  trend?: 'up' | 'down' | 'neutral';
  format?: 'text' | 'number' | 'percentage' | 'currency';
}

interface StatGroupProps {
  stats: Stat[];
  title?: string;
  columns?: 1 | 2 | 3 | 4 | 5 | 6;
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function StatGroup({ 
  stats,
  title,
  columns = 3,
  onApprove, 
  onDisapprove
}: StatGroupProps) {
  
  const limitedColumns = Math.min(columns, 3);
  
  const getGridClasses = () => {
    const baseGrid = 'grid gap-3';
    
    switch (limitedColumns) {
      case 1:
        return cn(baseGrid, 'grid-cols-1');
      case 2:
        return cn(baseGrid, 'grid-cols-1 md:grid-cols-2');
      case 3:
        return cn(baseGrid, 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3');
      default:
        return cn(baseGrid, 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3');
    }
  };
  
  return (
    <Container title={title} onApprove={onApprove} onDisapprove={onDisapprove}>
      <div className="p-4">
        <div className={getGridClasses()}>
          {stats.map((stat, index) => (
            <StatCard
              key={index}
              value={stat.value}
              label={stat.label}
              subtitle={stat.subtitle}
              change={stat.change}
              changeType={stat.changeType}
              color={stat.color}
              trend={stat.trend}
              format={stat.format}
            />
          ))}
        </div>
      </div>
    </Container>
  );
}