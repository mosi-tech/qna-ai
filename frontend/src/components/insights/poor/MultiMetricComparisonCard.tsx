/**
 * MultiMetricComparisonCard
 * 
 * Description: Compare multiple entities across multiple metrics in a side-by-side table format
 * Use Cases: Investment comparisons, vendor evaluation, product feature comparison, pricing analysis
 * Data Format: Array of entities with metrics and values for comprehensive comparison
 * 
 * @param title - Main comparison title
 * @param entities - Array of entities to compare (stocks, products, vendors, etc.)
 * @param metrics - Array of metrics to evaluate across entities
 * @param highlightBest - Whether to highlight the best value in each metric
 * @param variant - Display variant for different layouts
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

import { insightStyles, cn } from './shared/styles';

interface Entity {
  id: string;
  name: string;
  subtitle?: string;
  featured?: boolean;
  badge?: string;
}

interface Metric {
  id: string;
  name: string;
  format?: 'currency' | 'percentage' | 'number' | 'text' | 'boolean' | 'rating';
  higherIsBetter?: boolean;
  unit?: string;
  description?: string;
}

interface MultiMetricComparisonCardProps {
  title: string;
  entities: Entity[];
  metrics: Metric[];
  data: Record<string, Record<string, any>>;
  highlightBest?: boolean;
  variant?: 'default' | 'compact' | 'detailed';
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function MultiMetricComparisonCard({
  title,
  entities,
  metrics,
  data,
  highlightBest = true,
  variant = 'default',
  onApprove,
  onDisapprove
}: MultiMetricComparisonCardProps) {

  const formatValue = (value: any, metric: Metric) => {
    if (value === null || value === undefined || value === '') return '-';
    
    switch (metric.format) {
      case 'currency':
        return typeof value === 'number' ? `$${value.toLocaleString()}` : value;
      case 'percentage':
        return typeof value === 'number' ? `${value.toFixed(1)}%` : value;
      case 'number':
        return typeof value === 'number' ? value.toLocaleString() : value;
      case 'boolean':
        return value ? '✓' : '✗';
      case 'rating':
        return typeof value === 'number' ? `${value.toFixed(1)}/10` : value;
      case 'text':
      default:
        return value.toString();
    }
  };

  const findBestValue = (metricId: string, metric: Metric) => {
    const values = entities.map(entity => data[entity.id]?.[metricId]).filter(v => v !== null && v !== undefined && v !== '');
    if (values.length === 0) return null;

    if (metric.format === 'boolean') return true;
    if (typeof values[0] === 'string' && metric.format !== 'rating') return null;

    const numericValues = values.filter(v => typeof v === 'number');
    if (numericValues.length === 0) return null;

    return metric.higherIsBetter !== false 
      ? Math.max(...numericValues)
      : Math.min(...numericValues);
  };

  const isBestValue = (value: any, metricId: string, metric: Metric) => {
    if (!highlightBest) return false;
    const bestValue = findBestValue(metricId, metric);
    return bestValue !== null && value === bestValue;
  };

  const getCellClasses = (value: any, metricId: string, metric: Metric, entity: Entity) => {
    let classes = 'p-3 text-sm border-b border-slate-100';
    
    if (entity.featured) {
      classes += ' bg-sky-50';
    }

    if (isBestValue(value, metricId, metric)) {
      classes += ' bg-emerald-50 font-semibold text-emerald-800';
    }

    return classes;
  };

  const getHeaderClasses = (entity: Entity) => {
    let classes = 'p-4 text-center border-b-2';
    
    if (entity.featured) {
      classes += ' bg-sky-100 border-sky-300';
    } else {
      classes += ' bg-slate-50 border-slate-200';
    }

    return classes;
  };

  return (
    <div className={cn(insightStyles.card.base, insightStyles.spacing.component)}>
      {/* Header */}
      <div className="mb-6">
        <h3 className={cn(insightStyles.typography.heading, 'mb-2')}>
          {title}
        </h3>
      </div>

      {/* Comparison Table */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse border border-slate-200 rounded-lg overflow-hidden">
          {/* Entity Headers */}
          <thead>
            <tr>
              <th className={cn('p-4 text-left bg-slate-100 border-b-2 border-slate-200', insightStyles.text.primary)}>
                Metrics
              </th>
              {entities.map((entity) => (
                <th key={entity.id} className={getHeaderClasses(entity)}>
                  <div className="space-y-1">
                    <div className={cn('font-semibold', insightStyles.text.primary)}>
                      {entity.name}
                    </div>
                    {entity.subtitle && (
                      <div className={cn('text-xs', insightStyles.text.secondary)}>
                        {entity.subtitle}
                      </div>
                    )}
                    {entity.badge && (
                      <div className="inline-block px-2 py-1 bg-sky-600 text-white text-xs rounded-full">
                        {entity.badge}
                      </div>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>

          {/* Metrics Rows */}
          <tbody>
            {metrics.map((metric) => (
              <tr key={metric.id}>
                <td className={cn('p-3 font-medium bg-slate-50 border-b border-slate-100', insightStyles.text.primary)}>
                  <div>
                    <div>{metric.name}</div>
                    {metric.description && (
                      <div className={cn('text-xs mt-1', insightStyles.text.tertiary)}>
                        {metric.description}
                      </div>
                    )}
                  </div>
                </td>
                {entities.map((entity) => {
                  const value = data[entity.id]?.[metric.id];
                  return (
                    <td
                      key={entity.id}
                      className={getCellClasses(value, metric.id, metric, entity)}
                    >
                      <div className="text-center">
                        {formatValue(value, metric)}
                        {metric.unit && value !== null && value !== undefined && value !== '' && (
                          <span className={cn('ml-1 text-xs', insightStyles.text.secondary)}>
                            {metric.unit}
                          </span>
                        )}
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Legend */}
      {highlightBest && (
        <div className="mt-4 flex items-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-emerald-50 border border-emerald-200 rounded"></div>
            <span className={insightStyles.text.secondary}>Best Value</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-sky-50 border border-sky-200 rounded"></div>
            <span className={insightStyles.text.secondary}>Featured Option</span>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      {(onApprove || onDisapprove) && (
        <div className={cn('flex gap-2 mt-6 pt-4', insightStyles.border.divider)}>
          {onApprove && (
            <button
              onClick={onApprove}
              className={insightStyles.button.approve.default}
            >
              Approve
            </button>
          )}
          {onDisapprove && (
            <button
              onClick={onDisapprove}
              className={insightStyles.button.disapprove.default}
            >
              Disapprove
            </button>
          )}
        </div>
      )}
    </div>
  );
}