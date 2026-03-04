/**
 * KeyValueTable
 * 
 * Description: 2–4 column small tables for key metrics and data points
 * Use Cases: Financial metrics, performance indicators, summary statistics
 * Data Format: Array of objects with key-value pairs
 * 
 * @param data - Array of row objects with key-value pairs
 * @param columns - Array of column definitions
 * @param title - Optional table title
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface TableColumn {
  key: string;
  label: string;
  align?: 'left' | 'center' | 'right';
  format?: 'text' | 'number' | 'percentage' | 'currency';
}

interface KeyValueTableProps {
  data: Record<string, any>[];
  columns: TableColumn[];
  title?: string;
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function KeyValueTable({ 
  data, 
  columns,
  title,
  onApprove, 
  onDisapprove,
  
}: KeyValueTableProps) {
  
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
  
  const getAlignClass = (align: string = 'left') => {
    switch (align) {
      case 'center':
        return 'text-center';
      case 'right':
        return 'text-right';
      default:
        return 'text-left';
    }
  };


  
  return (
    <div className="bg-white rounded-lg overflow-hidden">
      {title && (
        <div className={`${config.headerPadding} border-b border-gray-200`}>
          <h3 className={`${config.titleSize} text-gray-900`}>{title}</h3>
        </div>
      )}
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  className={`${config.cellPadding} ${config.headerTextSize} font-medium text-gray-500 uppercase tracking-wider ${getAlignClass(column.align)}`}
                >
                  {column.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.map((row, index) => (
              <tr key={index} className="hover:bg-gray-50">
                {columns.map((column) => (
                  <td
                    key={column.key}
                    className={`${config.cellPadding} whitespace-nowrap ${config.cellTextSize} text-gray-900 ${getAlignClass(column.align)}`}
                  >
                    {formatValue(row[column.key], column.format)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {(onApprove || onDisapprove) && (
        <div className={`${config.actionPadding} border-t border-gray-200 bg-gray-50 flex gap-2`}>
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