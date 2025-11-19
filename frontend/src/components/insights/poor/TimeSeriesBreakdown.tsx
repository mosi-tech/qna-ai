/**
 * TimeSeriesBreakdown
 * 
 * Description: Continuous time period progression with performance breakdown
 * Use Cases: Intraday patterns, hourly performance, seasonal analysis, time-based trends
 * Data Format: Array of time periods with values and optional metadata
 * 
 * @param data - Array of time period data points
 * @param title - Optional title for the breakdown
 * @param timeFormat - Format for time labels (12h, 24h, date, etc.)
 * @param valueFormat - Format for values (percentage, currency, etc.)
 * @param showTrend - Whether to show trend line/direction
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface TimeDataPoint {
  time: string;
  value: number;
  label?: string;
  volume?: number;
  count?: number;
  metadata?: Record<string, any>;
}

interface TimeSeriesBreakdownProps {
  data: TimeDataPoint[];
  title?: string;
  timeFormat?: '12h' | '24h' | 'date' | 'custom';
  valueFormat?: 'number' | 'percentage' | 'currency';
  showTrend?: boolean;
  highlightPeak?: boolean;
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function TimeSeriesBreakdown({
  data,
  title,
  timeFormat = 'custom',
  valueFormat = 'percentage',
  showTrend = true,
  highlightPeak = true,
  onApprove,
  onDisapprove,
  variant = 'default'
}: TimeSeriesBreakdownProps) {

  const formatValue = (value: number) => {
    switch (valueFormat) {
      case 'percentage':
        return `${value.toFixed(1)}%`;
      case 'currency':
        return `$${value.toLocaleString()}`;
      case 'number':
      default:
        return value.toLocaleString();
    }
  };

  const formatTime = (time: string) => {
    switch (timeFormat) {
      case '12h':
        return new Date(`2024-01-01 ${time}`).toLocaleTimeString('en-US', {
          hour: 'numeric',
          minute: '2-digit',
          hour12: true
        });
      case '24h':
        return time;
      case 'date':
        return new Date(time).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      case 'custom':
      default:
        return time;
    }
  };

  const maxValue = Math.max(...data.map(d => d.value));
  const minValue = Math.min(...data.map(d => d.value));
  const range = maxValue - minValue;

  const getBarHeight = (value: number) => {
    if (range === 0) return 50;
    return ((value - minValue) / range) * 100;
  };

  const getValueColor = (value: number) => {
    if (value > 0) return 'bg-green-500';
    if (value < 0) return 'bg-red-500';
    return 'bg-gray-400';
  };

  const getTextColor = (value: number) => {
    if (value > 0) return 'text-green-700';
    if (value < 0) return 'text-red-700';
    return 'text-gray-700';
  };

  const isPeakValue = (value: number) => {
    return highlightPeak && (value === maxValue || value === minValue);
  };

  const getTrendDirection = () => {
    if (data.length < 2) return 'neutral';
    const first = data[0].value;
    const last = data[data.length - 1].value;
    if (last > first) return 'up';
    if (last < first) return 'down';
    return 'neutral';
  };

  const getTrendIcon = () => {
    switch (getTrendDirection()) {
      case 'up': return '↗';
      case 'down': return '↘';
      case 'neutral': return '→';
    }
  };

  const getTrendColor = () => {
    switch (getTrendDirection()) {
      case 'up': return 'text-green-600';
      case 'down': return 'text-red-600';
      case 'neutral': return 'text-gray-600';
    }
  };

  const averageValue = data.reduce((sum, d) => sum + d.value, 0) / data.length;

  return (
    <div className="bg-white  rounded-lg p-6">
      {title && (
        <div className="flex justify-between items-start mb-4">
          <h3 className="text-lg font-medium text-gray-900">{title}</h3>
          {showTrend && (
            <div className={`flex items-center gap-1 text-sm font-medium ${getTrendColor()}`}>
              <span>{getTrendIcon()}</span>
              <span>Trend</span>
            </div>
          )}
        </div>
      )}

      {/* Time series bars */}
      <div className="mb-6">
        <div className="flex items-end justify-between h-32 gap-1">
          {data.map((point, index) => (
            <div key={index} className="flex-1 flex flex-col items-center">
              {/* Bar */}
              <div className="relative w-full h-24 bg-gray-100 rounded-t flex items-end">
                <div
                  className={`w-full rounded-t transition-all duration-300 ${getValueColor(point.value)} ${isPeakValue(point.value) ? 'opacity-90 ring-2 ring-blue-400' : 'opacity-75'
                    }`}
                  style={{ height: `${getBarHeight(point.value)}%` }}
                ></div>

                {/* Value label on hover */}
                <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 opacity-0 hover:opacity-100 transition-opacity">
                  <div className="bg-gray-800 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                    {formatValue(point.value)}
                  </div>
                </div>
              </div>

              {/* Time label */}
              <div className="text-xs text-gray-600 mt-1 text-center transform -rotate-45 origin-center">
                {formatTime(point.time)}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Summary statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-sm text-gray-500">Average</div>
          <div className="font-semibold text-gray-900">{formatValue(averageValue)}</div>
        </div>
        <div className="text-center p-3 bg-green-50 rounded-lg">
          <div className="text-sm text-green-600">Peak High</div>
          <div className="font-semibold text-green-700">{formatValue(maxValue)}</div>
        </div>
        <div className="text-center p-3 bg-red-50 rounded-lg">
          <div className="text-sm text-red-600">Peak Low</div>
          <div className="font-semibold text-red-700">{formatValue(minValue)}</div>
        </div>
        <div className="text-center p-3 bg-blue-50 rounded-lg">
          <div className="text-sm text-blue-600">Range</div>
          <div className="font-semibold text-blue-700">{formatValue(range)}</div>
        </div>
      </div>

      {/* Detailed breakdown table */}
      {variant === 'detailed' && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-3 py-2 text-left">Time</th>
                <th className="px-3 py-2 text-center">Value</th>
                {data.some(d => d.volume) && (
                  <th className="px-3 py-2 text-center">Volume</th>
                )}
                {data.some(d => d.count) && (
                  <th className="px-3 py-2 text-center">Count</th>
                )}
              </tr>
            </thead>
            <tbody>
              {data.map((point, index) => (
                <tr key={index} className="border-t border-gray-100">
                  <td className="px-3 py-2 font-medium">{formatTime(point.time)}</td>
                  <td className={`px-3 py-2 text-center font-medium ${getTextColor(point.value)}`}>
                    {formatValue(point.value)}
                    {isPeakValue(point.value) && <span className="ml-1 text-blue-500">★</span>}
                  </td>
                  {point.volume && (
                    <td className="px-3 py-2 text-center text-gray-600">
                      {point.volume.toLocaleString()}
                    </td>
                  )}
                  {point.count && (
                    <td className="px-3 py-2 text-center text-gray-600">
                      {point.count}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Analysis notes */}
      <div className="mt-4 bg-gray-50 rounded-lg p-4">
        <h4 className="text-sm font-medium text-gray-900 mb-2">Time Series Analysis</h4>
        <div className="text-sm text-gray-700 space-y-1">
          <div>Period analyzed: {formatTime(data[0]?.time)} to {formatTime(data[data.length - 1]?.time)}</div>
          <div>Data points: {data.length}</div>
          <div>Overall trend: <span className={getTrendColor()}>{getTrendDirection().charAt(0).toUpperCase() + getTrendDirection().slice(1)}</span></div>
          {highlightPeak && (
            <div>Peak values are marked with ★ symbol</div>
          )}
        </div>
      </div>

      {(onApprove || onDisapprove) && (
        <div className="flex gap-2 mt-6 pt-4 border-t border-gray-100">
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