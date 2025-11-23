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
}

export default function StatGroup({ 
  stats,
  title,
  columns = 3
}: StatGroupProps) {
  return (
    <Container title={title}>
      <div className="p-4">
        <div 
          className="gap-4 md:gap-5 w-full auto-rows-max"
          style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))' }}
        >
          {stats.map((stat, index) => (
            <div key={index} className="min-w-0">
              <StatCard
                value={stat.value}
                label={stat.label}
                subtitle={stat.subtitle}
                change={stat.change}
                changeType={stat.changeType}
                color={stat.color}
                trend={stat.trend}
                format={stat.format}
              />
            </div>
          ))}
        </div>
      </div>
    </Container>
  );
}