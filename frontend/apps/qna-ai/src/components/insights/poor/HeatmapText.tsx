/**
 * HeatmapText
 * 
 * Description: Textual heatmap representation using color intensity
 * Use Cases: Risk heat maps, performance matrices, intensity mapping
 * Data Format: 2D grid with values and optional labels
 * 
 * @param data - 2D array of values for the heatmap
 * @param rowLabels - Labels for rows
 * @param columnLabels - Labels for columns
 * @param title - Optional title
 * @param scale - Value scale for color mapping
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface HeatmapCell {
  value: number;
  label?: string;
  description?: string;
}

interface HeatmapTextProps {
  data: (number | HeatmapCell)[][];
  rowLabels: string[];
  columnLabels: string[];
  title?: string;
  scale?: 'risk' | 'performance' | 'correlation';
  showValues?: boolean;
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function HeatmapText({
  data,
  rowLabels,
  columnLabels,
  title,
  scale = 'performance',
  showValues = true,
  onApprove,
  onDisapprove,
  variant = 'default'
}: HeatmapTextProps) {

  // Extract values for min/max calculation
  const allValues = data.flat().map(cell =>
    typeof cell === 'number' ? cell : cell.value
  );
  const minValue = Math.min(...allValues);
  const maxValue = Math.max(...allValues);

  const getCellValue = (cell: number | HeatmapCell) => {
    return typeof cell === 'number' ? cell : cell.value;
  };

  const getCellLabel = (cell: number | HeatmapCell) => {
    return typeof cell === 'number' ? null : cell.label;
  };

  const normalizeValue = (value: number) => {
    if (maxValue === minValue) return 0.5;
    return (value - minValue) / (maxValue - minValue);
  };

  const getColorClasses = (value: number) => {
    const normalized = normalizeValue(value);

    switch (scale) {
      case 'risk':
        if (normalized >= 0.8) return 'bg-red-200 text-red-900';
        if (normalized >= 0.6) return 'bg-red-100 text-red-800';
        if (normalized >= 0.4) return 'bg-yellow-100 text-yellow-800';
        if (normalized >= 0.2) return 'bg-green-100 text-green-800';
        return 'bg-green-200 text-green-900';

      case 'correlation':
        const absNormalized = Math.abs(normalized - 0.5) * 2;
        if (absNormalized >= 0.8) return value >= 0 ? 'bg-blue-200 text-blue-900' : 'bg-red-200 text-red-900';
        if (absNormalized >= 0.6) return value >= 0 ? 'bg-blue-100 text-blue-800' : 'bg-red-100 text-red-800';
        if (absNormalized >= 0.4) return value >= 0 ? 'bg-blue-50 text-blue-700' : 'bg-red-50 text-red-700';
        return 'bg-gray-50 text-gray-600';

      case 'performance':
      default:
        if (normalized >= 0.8) return 'bg-green-200 text-green-900';
        if (normalized >= 0.6) return 'bg-green-100 text-green-800';
        if (normalized >= 0.4) return 'bg-yellow-100 text-yellow-800';
        if (normalized >= 0.2) return 'bg-red-100 text-red-800';
        return 'bg-red-200 text-red-900';
    }
  };

  const getIntensityLabel = (value: number) => {
    const normalized = normalizeValue(value);

    if (normalized >= 0.8) return 'Very High';
    if (normalized >= 0.6) return 'High';
    if (normalized >= 0.4) return 'Medium';
    if (normalized >= 0.2) return 'Low';
    return 'Very Low';
  };

  const formatValue = (value: number) => {
    if (scale === 'correlation') return value.toFixed(2);
    if (scale === 'risk') return value.toFixed(1);
    return value.toFixed(1);
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
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {/* Empty corner */}
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
            {data.map((row, rowIndex) => (
              <tr key={rowIndex} className="border-t border-gray-200">
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-900 bg-gray-50">
                  {rowLabels[rowIndex]}
                </th>
                {row.map((cell, colIndex) => {
                  const value = getCellValue(cell);
                  const label = getCellLabel(cell);

                  return (
                    <td
                      key={colIndex}
                      className={`px-4 py-3 text-center text-sm font-medium ${getColorClasses(value)}`}
                      title={`${rowLabels[rowIndex]} × ${columnLabels[colIndex]}: ${getIntensityLabel(value)}`}
                    >
                      <div className="space-y-1">
                        {showValues && (
                          <div className="text-sm font-semibold">
                            {formatValue(value)}
                          </div>
                        )}
                        <div className="text-xs font-medium">
                          {label || getIntensityLabel(value)}
                        </div>
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
      <div className="px-6 py-3 border-t border-gray-100 bg-gray-50">
        <div className="flex items-center justify-center">
          <div className="flex items-center gap-4 text-xs">
            <span className="text-gray-600 font-medium">Intensity:</span>
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1">
                <div className={`w-3 h-3 border ${scale === 'risk' ? 'bg-green-200' : 'bg-red-200'
                  }`}></div>
                <span>{scale === 'risk' ? 'Low Risk' : 'Low'}</span>
              </div>
              <div className="flex items-center gap-1">
                <div className="w-3 h-3 border bg-yellow-100"></div>
                <span>Medium</span>
              </div>
              <div className="flex items-center gap-1">
                <div className={`w-3 h-3 border ${scale === 'risk' ? 'bg-red-200' : 'bg-green-200'
                  }`}></div>
                <span>{scale === 'risk' ? 'High Risk' : 'High'}</span>
              </div>
            </div>
          </div>
        </div>
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