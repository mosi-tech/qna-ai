/**
 * ComparisonTable
 * 
 * Description: Compare same metrics across different entities (periods, portfolios, strategies, etc.)
 * Use Cases: Period-over-period analysis, portfolio comparisons, strategy analysis, A/B testing
 * Data Format: Metrics with values across multiple comparison entities
 * 
 * @param metrics - Array of metrics to compare
 * @param entities - Array of entities to compare (periods, portfolios, strategies, etc.)
 * @param data - Data matrix with metric values by entity
 * @param title - Optional table title
 * @param showChange - Whether to show change between entities
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface ComparisonMetric {
  id: string;
  name: string;
  format?: 'number' | 'percentage' | 'currency' | 'ratio';
  unit?: string;
}

interface ComparisonEntity {
  id: string;
  name: string;
  shortName?: string;
  description?: string;
  metadata?: Record<string, any>;
}

interface ComparisonTableProps {
  metrics: ComparisonMetric[];
  entities: ComparisonEntity[];
  data: Record<string, Record<string, number>>; // data[metricId][entityId] = value
  title?: string;
  showChange?: boolean;
  highlightBest?: boolean;
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function ComparisonTable({
  metrics,
  entities,
  data,
  title,
  showChange = true,
  highlightBest = false,
  onApprove,
  onDisapprove,
  variant = 'default'
}: ComparisonTableProps) {

  const formatValue = (value: number, metric: ComparisonMetric) => {
    if (value === null || value === undefined) return '-';

    switch (metric.format) {
      case 'percentage':
        return `${value.toFixed(1)}%`;
      case 'currency':
        return `$${value.toLocaleString()}`;
      case 'ratio':
        return `${value.toFixed(2)}x`;
      case 'number':
      default:
        return value.toLocaleString();
    }
  };

  const calculateChange = (current: number, previous: number) => {
    if (!previous || previous === 0) return 0;
    return ((current - previous) / Math.abs(previous)) * 100;
  };

  const getBestValue = (metricId: string) => {
    const values = entities.map(e => data[metricId]?.[e.id]).filter(v => v != null);
    return Math.max(...values);
  };

  const getWorstValue = (metricId: string) => {
    const values = entities.map(e => data[metricId]?.[e.id]).filter(v => v != null);
    return Math.min(...values);
  };

  const isBestValue = (value: number, metricId: string) => {
    return highlightBest && value === getBestValue(metricId);
  };

  const isWorstValue = (value: number, metricId: string) => {
    return highlightBest && value === getWorstValue(metricId);
  };

  const getChangeColor = (change: number) => {
    if (Math.abs(change) < 0.1) return 'text-gray-600';
    return change > 0 ? 'text-green-600' : 'text-red-600';
  };

  const getCellHighlight = (value: number, metricId: string) => {
    if (!highlightBest) return '';
    if (isBestValue(value, metricId)) return 'bg-green-50 border-green-200';
    if (isWorstValue(value, metricId)) return 'bg-red-50 border-red-200';
    return '';
  };

  return (
    <div className="bg-white  rounded-lg overflow-hidden">
      {title && (
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">{title}</h3>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Metric
              </th>
              {entities.map((entity) => (
                <th
                  key={entity.id}
                  className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  <div>
                    <div>{entity.shortName || entity.name}</div>
                    {variant === 'detailed' && entity.description && (
                      <div className="text-xs text-gray-400 normal-case font-normal mt-1">
                        {entity.description}
                      </div>
                    )}
                  </div>
                </th>
              ))}
              {showChange && entities.length > 1 && (
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Change
                </th>
              )}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {metrics.map((metric) => {
              const currentEntity = entities[entities.length - 1];
              const previousEntity = entities[entities.length - 2];
              const currentValue = data[metric.id]?.[currentEntity.id];
              const previousValue = data[metric.id]?.[previousEntity?.id];
              const change = previousValue ? calculateChange(currentValue, previousValue) : 0;

              return (
                <tr key={metric.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    <div>
                      <div>{metric.name}</div>
                      {metric.unit && (
                        <div className="text-xs text-gray-500">({metric.unit})</div>
                      )}
                    </div>
                  </td>
                  {entities.map((entity) => {
                    const value = data[metric.id]?.[entity.id];
                    return (
                      <td
                        key={entity.id}
                        className={`px-4 py-4 whitespace-nowrap text-center text-sm text-gray-900 ${getCellHighlight(value, metric.id)}`}
                      >
                        <div className="space-y-1">
                          <div className={`font-semibold ${isBestValue(value, metric.id) ? 'text-green-700' :
                              isWorstValue(value, metric.id) ? 'text-red-700' : ''
                            }`}>
                            {formatValue(value, metric)}
                          </div>
                          {highlightBest && isBestValue(value, metric.id) && (
                            <div className="text-xs text-green-600">Best</div>
                          )}
                        </div>
                      </td>
                    );
                  })}
                  {showChange && entities.length > 1 && previousValue && (
                    <td className="px-4 py-4 whitespace-nowrap text-center text-sm">
                      <div className={`font-medium ${getChangeColor(change)}`}>
                        {change > 0 ? '+' : ''}{change.toFixed(1)}%
                      </div>
                      <div className="text-xs text-gray-500">
                        vs {previousEntity?.shortName || previousEntity?.name}
                      </div>
                    </td>
                  )}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Summary statistics */}
      {variant === 'detailed' && (
        <div className="px-6 py-4 border-t border-gray-100 bg-gray-50">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Comparison Summary</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <div className="text-gray-600">Total Entities</div>
              <div className="font-semibold text-gray-900">{entities.length}</div>
            </div>
            <div>
              <div className="text-gray-600">Metrics Tracked</div>
              <div className="font-semibold text-gray-900">{metrics.length}</div>
            </div>
            <div>
              <div className="text-gray-600">Comparison Range</div>
              <div className="font-semibold text-gray-900">
                {entities[0]?.name} to {entities[entities.length - 1]?.name}
              </div>
            </div>
          </div>
        </div>
      )}

      {(onApprove || onDisapprove) && (
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex gap-2">
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