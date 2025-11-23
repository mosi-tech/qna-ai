/**
 * ComparisonTable
 * 
 * Description: Multi-column comparison table for comparing entities across multiple metrics
 * Use Cases: Stock comparisons, portfolio analysis, competitive analysis
 * Data Format: Entities as columns, metrics as rows
 * 
 * @param entities - Array of entities being compared (columns)
 * @param metrics - Array of metrics for comparison (rows)
 * @param data - 2D array or object mapping entity-metric to values
 * @param title - Optional table title
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface ComparisonEntity {
  id: string;
  name: string;
  subtitle?: string;
}

interface ComparisonMetric {
  id: string;
  name: string;
  format?: 'text' | 'number' | 'percentage' | 'currency';
}

interface ComparisonTableProps {
  entities: ComparisonEntity[];
  metrics: ComparisonMetric[];
  data: Record<string, Record<string, any>>;
  title?: string;
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'narrow' | 'wide';
}

export default function ComparisonTable({
  entities,
  metrics,
  data,
  title,
  onApprove,
  onDisapprove,
  
}: ComparisonTableProps) {

  const formatValue = (value: any, format: string = 'text') => {
    if (value === null || value === undefined) return '-';

    switch (format) {
      case 'number':
        return typeof value === 'number' ? value.toLocaleString() : value;
      case 'percentage':
        return typeof value === 'number' ? `${value.toFixed(1)}%` : value;
      case 'currency':
        return typeof value === 'number' ? `$${value.toLocaleString()}` : value;
      default:
        return value;
    }
  };

  const getValue = (entityId: string, metricId: string) => {
    return data[entityId]?.[metricId] ?? data[metricId]?.[entityId] ?? '-';
  };



  return (
    <div className="bg-white  rounded-lg overflow-hidden">
      {title && (
        <div className={config.headerPadding + " border-b border-gray-200"}>
          <h3 className={`${config.titleSize} font-medium text-gray-900 truncate`}>{title}</h3>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full min-w-max">
          <thead className="bg-gray-50">
            <tr>
              <th className={`${config.cellPadding} text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-0`}>
                <span className="truncate">Metric</span>
              </th>
              {config.displayEntities.map((entity) => (
                <th
                  key={entity.id}
                  className={`${config.cellPadding} text-center text-xs font-medium text-gray-500 uppercase tracking-wider min-w-0`}
                >
                  <div className="min-w-0">
                    <div className="truncate">{entity.name}</div>
                    {entity.subtitle && (
                      <div className="text-xs text-gray-400 normal-case font-normal truncate">
                        {entity.subtitle}
                      </div>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {config.displayMetrics.map((metric) => (
              <tr key={metric.id} className="hover:bg-gray-50">
                <td className={`${config.cellPadding} ${config.fontSize} font-medium text-gray-900 min-w-0`}>
                  <span className="truncate block">{metric.name}</span>
                </td>
                {config.displayEntities.map((entity) => (
                  <td
                    key={entity.id}
                    className={`${config.cellPadding} ${config.fontSize} text-gray-900 text-center min-w-0`}
                  >
                    <span className="truncate block">
                      {formatValue(getValue(entity.id, metric.id), metric.format)}
                    </span>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {(onApprove || onDisapprove) && (
        <div className={`${config.headerPadding} border-t border-gray-200 bg-gray-50 flex gap-2 flex-wrap`}>
          {onApprove && (
            <button
              onClick={onApprove}
              className="px-3 py-1.5 sm:px-4 sm:py-2 bg-green-50 text-green-700 rounded-md hover:bg-green-100 transition-colors text-sm font-medium"
            >
              Approve
            </button>
          )}
          {onDisapprove && (
            <button
              onClick={onDisapprove}
              className="px-3 py-1.5 sm:px-4 sm:py-2 bg-red-50 text-red-700 rounded-md hover:bg-red-100 transition-colors text-sm font-medium"
            >
              Disapprove
            </button>
          )}
        </div>
      )}
    </div>
  );
}