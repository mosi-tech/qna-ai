/**
 * HeatmapTable
 * 
 * Description: Generic grid/matrix display with flexible formatting and color coding
 * Use Cases: Correlation matrices, performance grids, risk heatmaps, cross-tabulation, comparison grids
 * Data Format: 2D matrix with configurable row/column headers and flexible cell formatting
 * 
 * @param data - 2D array of values
 * @param rowLabels - Labels for rows
 * @param columnLabels - Labels for columns
 * @param title - Optional title for the heatmap
 * @param cellConfig - Configuration for cell formatting and coloring
 * @param legend - Optional legend configuration
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

import Container from './Container';

interface CellConfig {
  format?: 'number' | 'percentage' | 'currency' | 'text' | 'custom';
  decimals?: number;
  colorScheme?: 'correlation' | 'heatmap' | 'traffic' | 'custom' | 'none';
  customFormatter?: (value: any, rowIndex: number, colIndex: number) => string;
  customColorScale?: (value: any, rowIndex: number, colIndex: number) => { background: string; text: string };
  showDiagonal?: boolean;
  highlightDiagonal?: boolean;
}

interface LegendItem {
  color: string;
  label: string;
  description?: string;
}

interface HeatmapTableProps {
  data: (number | string | null)[][];
  rowLabels: string[];
  columnLabels: string[];
  title?: string;
  cellConfig?: CellConfig;
  legend?: LegendItem[];
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function HeatmapTable({
  data,
  rowLabels,
  columnLabels,
  title,
  cellConfig = {},
  legend,
  onApprove,
  onDisapprove,
  
}: HeatmapTableProps) {

  const {
    format = 'number',
    decimals = 2,
    colorScheme = 'none',
    customFormatter,
    customColorScale,
    showDiagonal = true,
    highlightDiagonal = false
  } = cellConfig;

  const formatValue = (value: number | string | null, rowIndex: number, colIndex: number) => {
    if (value === null || value === undefined) return '-';
    if (typeof value === 'string') return value;
    if (customFormatter) return customFormatter(value, rowIndex, colIndex);

    switch (format) {
      case 'percentage':
        return `${(value * 100).toFixed(decimals)}%`;
      case 'currency':
        return `$${value.toLocaleString(undefined, { minimumFractionDigits: decimals })}`;        
      case 'number':
      default:
        return value.toFixed(decimals);
    }
  };

  const getCellStyles = (value: number | string | null, rowIndex: number, colIndex: number) => {
    if (customColorScale) {
      const colors = customColorScale(value, rowIndex, colIndex);
      return { background: colors.background, text: colors.text };
    }

    if (colorScheme === 'none' || typeof value !== 'number') {
      return { background: 'bg-white', text: 'text-gray-900' };
    }

    // Handle diagonal cells
    const isDiagonal = rowIndex === colIndex;
    if (isDiagonal && !showDiagonal) {
      return { background: 'bg-gray-100', text: 'text-gray-400' };
    }
    if (isDiagonal && highlightDiagonal) {
      return { background: 'bg-gray-200', text: 'text-gray-900 font-semibold' };
    }

    switch (colorScheme) {
      case 'correlation':
        if (value > 0.7) return { background: 'bg-green-200', text: 'text-green-900 font-semibold' };
        if (value > 0.3) return { background: 'bg-green-100', text: 'text-green-800' };
        if (value > 0.1) return { background: 'bg-green-50', text: 'text-green-700' };
        if (value < -0.7) return { background: 'bg-red-200', text: 'text-red-900 font-semibold' };
        if (value < -0.3) return { background: 'bg-red-100', text: 'text-red-800' };
        if (value < -0.1) return { background: 'bg-red-50', text: 'text-red-700' };
        return { background: 'bg-white', text: 'text-gray-600' };
        
      case 'heatmap':
        const normalized = Math.abs(value);
        if (normalized > 0.8) return { background: 'bg-blue-200', text: 'text-blue-900 font-semibold' };
        if (normalized > 0.6) return { background: 'bg-blue-100', text: 'text-blue-800' };
        if (normalized > 0.4) return { background: 'bg-blue-50', text: 'text-blue-700' };
        if (normalized > 0.2) return { background: 'bg-blue-25', text: 'text-blue-600' };
        return { background: 'bg-white', text: 'text-gray-600' };
        
      case 'traffic':
        if (value > 0.7) return { background: 'bg-green-100', text: 'text-green-900' };
        if (value > 0.4) return { background: 'bg-yellow-100', text: 'text-yellow-900' };
        return { background: 'bg-red-100', text: 'text-red-900' };
        
      default:
        return { background: 'bg-white', text: 'text-gray-900' };
    }
  };

  return (
    <Container title={title} onApprove={onApprove} onDisapprove={onDisapprove}>
      <div className="p-4 overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {/* Empty corner cell */}
              </th>
              {columnLabels.map((label, index) => (
                <th
                  key={index}
                  className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  {label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, rowIndex) => {
              const isDiagonal = rowIndex === rowIndex; // Keep for future diagonal logic
              return (
                <tr key={rowIndex} className="border-t border-gray-200">
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-900 bg-gray-50">
                    {rowLabels[rowIndex]}
                  </th>
                  {row.map((cell, colIndex) => {
                    const styles = getCellStyles(cell, rowIndex, colIndex);
                    const shouldShow = rowIndex !== colIndex || showDiagonal;
                    
                    return (
                      <td
                        key={colIndex}
                        className={`px-4 py-3 text-center text-sm ${styles.background} ${styles.text}`}
                      >
                        {shouldShow ? formatValue(cell, rowIndex, colIndex) : '-'}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {legend && legend.length > 0 && (
        <div className="px-4 py-3 border-t border-gray-100 bg-gray-50">
          <div className="flex items-center justify-center text-xs text-gray-600">
            <div className="flex items-center gap-4 flex-wrap">
              {legend.map((item, index) => (
                <div key={index} className="flex items-center gap-1">
                  <div className={`w-3 h-3 ${item.color} border`}></div>
                  <span title={item.description}>{item.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </Container>
  );
}