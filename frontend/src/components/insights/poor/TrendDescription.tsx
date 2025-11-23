/**
 * TrendDescription
 * 
 * Description: Textual description of trends with directional indicators
 * Use Cases: Market trends, performance trajectories, pattern analysis
 * Data Format: Trend text with direction, magnitude, and timeframe
 * 
 * @param trend - Main trend description
 * @param direction - Trend direction (up/down/sideways)
 * @param magnitude - Strength of the trend
 * @param timeframe - Time period for the trend
 * @param confidence - Confidence level in the trend
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface TrendDescriptionProps {
  trend: string;
  direction: 'up' | 'down' | 'sideways' | 'volatile';
  magnitude?: 'weak' | 'moderate' | 'strong';
  timeframe?: string;
  confidence?: 'low' | 'medium' | 'high';
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function TrendDescription({ 
  trend,
  direction,
  magnitude,
  timeframe,
  confidence,
  onApprove, 
  onDisapprove,
  variant = 'default' 
}: TrendDescriptionProps) {
  
  const getDirectionIcon = () => {
    switch (direction) {
      case 'up':
        return '↗️';
      case 'down':
        return '↘️';
      case 'volatile':
        return '⚡';
      case 'sideways':
      default:
        return '→';
    }
  };

  const getDirectionColor = () => {
    switch (direction) {
      case 'up':
        return 'text-green-700 bg-green-50 border-green-200';
      case 'down':
        return 'text-red-700 bg-red-50 border-red-200';
      case 'volatile':
        return 'text-orange-700 bg-orange-50 border-orange-200';
      case 'sideways':
      default:
        return 'text-gray-700 bg-gray-50 border-gray-200';
    }
  };

  const getMagnitudeColor = () => {
    switch (magnitude) {
      case 'strong':
        return 'text-blue-800 bg-blue-100';
      case 'moderate':
        return 'text-blue-700 bg-blue-50';
      case 'weak':
        return 'text-gray-600 bg-gray-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getConfidenceColor = () => {
    switch (confidence) {
      case 'high':
        return 'text-green-700 bg-green-100';
      case 'medium':
        return 'text-yellow-700 bg-yellow-100';
      case 'low':
        return 'text-red-700 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };
  
  return (
    <div className={`border rounded-lg p-4 ${getDirectionColor()}`}>
      <div className="flex items-start space-x-3">
        <div className="text-2xl flex-shrink-0">
          {getDirectionIcon()}
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h4 className="font-medium text-gray-900 capitalize">
              {direction} Trend
            </h4>
            {magnitude && (
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${getMagnitudeColor()}`}>
                {magnitude}
              </span>
            )}
            {confidence && (
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${getConfidenceColor()}`}>
                {confidence} confidence
              </span>
            )}
          </div>
          <p className="text-sm leading-relaxed text-gray-800">
            {trend}
          </p>
          {timeframe && (
            <div className="mt-2 text-xs text-gray-600">
              <span className="font-medium">Timeframe:</span> {timeframe}
            </div>
          )}
        </div>
      </div>
      
      {(onApprove || onDisapprove) && (
        <div className="flex gap-2 mt-4">
          {onApprove && (
            <button
              onClick={onApprove}
              className="px-3 py-1 bg-white bg-opacity-70 text-gray-800 rounded text-xs font-medium hover:bg-opacity-90 transition-colors"
            >
              Approve
            </button>
          )}
          {onDisapprove && (
            <button
              onClick={onDisapprove}
              className="px-3 py-1 bg-white bg-opacity-70 text-gray-800 rounded text-xs font-medium hover:bg-opacity-90 transition-colors"
            >
              Disapprove
            </button>
          )}
        </div>
      )}
    </div>
  );
}