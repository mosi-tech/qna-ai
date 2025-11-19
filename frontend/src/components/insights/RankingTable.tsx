/**
 * RankingTable
 * 
 * Description: Displays a ranked table of items sorted by a primary metric
 * Use Cases: Rankings, leaderboards, performance tables, comparative analysis
 * Data Format: Array of ranked items with flexible column structure
 * 
 * @param data - Array of ranked items
 * @param columns - Column definitions for flexible table structure
 * @param primaryColumn - ID of the primary ranking column
 * @param title - Optional table title
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface RankingColumn {
  id: string;
  name: string;
  align?: 'left' | 'center' | 'right';
  format?: 'text' | 'number' | 'percentage' | 'currency' | 'badge';
  width?: 'auto' | 'sm' | 'md' | 'lg';
  colorScale?: (value: any) => string; // Custom color function
}

interface RankingItem {
  id: string;
  name?: string;
  [key: string]: any; // Flexible data structure
}

interface RankingTableProps {
  data: RankingItem[];
  columns: RankingColumn[];
  primaryColumn?: string; // Column ID used for ranking/highlighting
  title?: string;
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function RankingTable({
  data,
  columns,
  primaryColumn,
  title,
  onApprove,
  onDisapprove,
  variant = 'default'
}: RankingTableProps) {

  const formatValue = (value: any, column: RankingColumn) => {
    if (value === null || value === undefined) return '-';

    switch (column.format) {
      case 'percentage':
        return `${(typeof value === 'number' ? value * 100 : value).toFixed(1)}%`;
      case 'currency':
        return `$${value.toLocaleString()}`;
      case 'number':
        return typeof value === 'number' ? value.toLocaleString() : value;
      case 'text':
      default:
        return value;
    }
  };

  const getCellColor = (value: any, column: RankingColumn) => {
    if (column.colorScale) {
      return column.colorScale(value);
    }
    return '';
  };

  const getAlignmentClass = (align: string) => {
    switch (align) {
      case 'center': return 'text-center';
      case 'right': return 'text-right';
      default: return 'text-left';
    }
  };

  return (
    <div className="bg-white  rounded-lg overflow-hidden">
      {title && (
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
          <div className="text-sm text-gray-500">{data.length} items</div>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Rank
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Item
              </th>
              {columns.map((column) => (
                <th
                  key={column.id}
                  className={`px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider ${
                    getAlignmentClass(column.align || 'left')
                  }`}
                >
                  {column.name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.map((item, index) => (
              <tr key={item.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  #{index + 1}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-medium text-gray-900">{item.id}</div>
                    {item.name && (
                      <div className="text-sm text-gray-500 truncate max-w-32">{item.name}</div>
                    )}
                  </div>
                </td>
                {columns.map((column) => {
                  const value = item[column.id];
                  const cellColor = getCellColor(value, column);
                  const isPrimary = column.id === primaryColumn;
                  
                  return (
                    <td
                      key={column.id}
                      className={`px-6 py-4 whitespace-nowrap text-sm ${
                        getAlignmentClass(column.align || 'left')
                      }`}
                    >
                      {column.format === 'badge' ? (
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          cellColor || 'text-gray-700 bg-gray-100'
                        }`}>
                          {formatValue(value, column)}
                        </span>
                      ) : (
                        <span className={`${
                          isPrimary ? 'font-medium' : ''
                        } ${
                          cellColor || 'text-gray-900'
                        }`}>
                          {formatValue(value, column)}
                        </span>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

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