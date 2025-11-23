/**
 * EventImpactBlock
 * 
 * Description: Before/after event comparison showing impact and recovery
 * Use Cases: Market events, earnings impact, crisis analysis, policy changes
 * Data Format: Before/after values with event details and recovery metrics
 * 
 * @param event - Event description and details
 * @param beforeValue - Value before the event
 * @param afterValue - Value immediately after the event
 * @param recoveryValue - Value after recovery (optional)
 * @param metric - Metric being measured
 * @param format - Value formatting
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface EventDetails {
  title: string;
  date: string;
  description: string;
  type: 'positive' | 'negative' | 'neutral';
  category?: string;
}

interface EventImpactBlockProps {
  event: EventDetails;
  beforeValue: number;
  afterValue: number;
  recoveryValue?: number;
  metric: string;
  format?: 'number' | 'percentage' | 'currency' | 'points';
  timeToRecovery?: string;
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function EventImpactBlock({
  event,
  beforeValue,
  afterValue,
  recoveryValue,
  metric,
  format = 'number',
  timeToRecovery,
  onApprove,
  onDisapprove,
  variant = 'default'
}: EventImpactBlockProps) {

  const formatValue = (value: number) => {
    switch (format) {
      case 'percentage':
        return `${value.toFixed(1)}%`;
      case 'currency':
        return `$${value.toLocaleString()}`;
      case 'points':
        return `${value.toFixed(0)}pts`;
      case 'number':
      default:
        return value.toLocaleString();
    }
  };

  const getImpactChange = () => {
    return afterValue - beforeValue;
  };

  const getImpactPercent = () => {
    if (beforeValue === 0) return 0;
    return ((afterValue - beforeValue) / Math.abs(beforeValue)) * 100;
  };

  const getRecoveryChange = () => {
    if (!recoveryValue) return 0;
    return recoveryValue - afterValue;
  };

  const getRecoveryPercent = () => {
    if (!recoveryValue || afterValue === 0) return 0;
    return ((recoveryValue - afterValue) / Math.abs(afterValue)) * 100;
  };

  const isFullyRecovered = () => {
    if (!recoveryValue) return false;
    const impactDirection = getImpactChange() > 0 ? 'positive' : 'negative';
    if (impactDirection === 'negative') {
      return recoveryValue >= beforeValue * 0.95; // Within 5% of original
    } else {
      return recoveryValue <= beforeValue * 1.05; // Within 5% of original
    }
  };

  const impact = getImpactChange();
  const impactPercent = getImpactPercent();
  const recoveryChange = getRecoveryChange();
  const recoveryPercent = getRecoveryPercent();

  const getEventColor = () => {
    switch (event.type) {
      case 'positive':
        return 'border-green-200 bg-green-50';
      case 'negative':
        return 'border-red-200 bg-red-50';
      case 'neutral':
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  const getValueColor = (isPositive: boolean) => {
    return isPositive ? 'text-green-700' : 'text-red-700';
  };

  return (
    <div className="bg-white  rounded-lg p-6">
      <div className="mb-6">
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-lg font-medium text-gray-900">{event.title}</h3>
          {event.category && (
            <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-600 rounded-full">
              {event.category}
            </span>
          )}
        </div>
        <div className="text-sm text-gray-600 mb-2">{event.date}</div>
        <div className={`p-3 rounded-lg border ${getEventColor()}`}>
          <p className="text-sm text-gray-800">{event.description}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        {/* Before Event */}
        <div className="text-center">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="text-sm text-blue-600 font-medium mb-1">Before Event</div>
            <div className="text-2xl font-bold text-blue-900">{formatValue(beforeValue)}</div>
            <div className="text-xs text-blue-700 mt-1">{metric}</div>
          </div>
        </div>

        {/* After Event (Impact) */}
        <div className="text-center">
          <div className="bg-gray-50  rounded-lg p-4">
            <div className="text-sm text-gray-600 font-medium mb-1">Immediate Impact</div>
            <div className="text-2xl font-bold text-gray-900">{formatValue(afterValue)}</div>
            <div className={`text-sm font-medium mt-1 ${getValueColor(impact > 0)}`}>
              {impact > 0 ? '+' : ''}{formatValue(Math.abs(impact))} ({impactPercent > 0 ? '+' : ''}{impactPercent.toFixed(1)}%)
            </div>
          </div>
        </div>

        {/* Recovery (if available) */}
        {recoveryValue !== undefined && (
          <div className="text-center">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="text-sm text-green-600 font-medium mb-1">After Recovery</div>
              <div className="text-2xl font-bold text-green-900">{formatValue(recoveryValue)}</div>
              <div className={`text-sm font-medium mt-1 ${getValueColor(recoveryChange > 0)}`}>
                {recoveryChange > 0 ? '+' : ''}{formatValue(Math.abs(recoveryChange))} ({recoveryPercent > 0 ? '+' : ''}{recoveryPercent.toFixed(1)}%)
              </div>
              {timeToRecovery && (
                <div className="text-xs text-green-700 mt-1">{timeToRecovery}</div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Impact Analysis */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="text-sm font-medium text-gray-900 mb-3">Impact Analysis</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <div className="text-gray-600">Immediate Impact</div>
            <div className={`font-semibold ${getValueColor(impact > 0)}`}>
              {Math.abs(impactPercent).toFixed(1)}% {impact > 0 ? 'increase' : 'decrease'}
            </div>
          </div>

          {recoveryValue !== undefined && (
            <>
              <div>
                <div className="text-gray-600">Recovery Status</div>
                <div className={`font-semibold ${isFullyRecovered() ? 'text-green-700' : 'text-yellow-700'}`}>
                  {isFullyRecovered() ? 'Fully Recovered' : 'Partial Recovery'}
                </div>
              </div>

              {timeToRecovery && (
                <div>
                  <div className="text-gray-600">Recovery Time</div>
                  <div className="font-semibold text-gray-900">{timeToRecovery}</div>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Detailed metrics */}
      {variant === 'detailed' && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
            <div className="text-center">
              <div className="text-gray-500">Peak Impact</div>
              <div className="font-medium">{formatValue(Math.abs(impact))}</div>
            </div>
            <div className="text-center">
              <div className="text-gray-500">Impact Duration</div>
              <div className="font-medium">{timeToRecovery || 'Ongoing'}</div>
            </div>
            {recoveryValue !== undefined && (
              <>
                <div className="text-center">
                  <div className="text-gray-500">Net Change</div>
                  <div className={`font-medium ${getValueColor(recoveryValue - beforeValue > 0)}`}>
                    {formatValue(Math.abs(recoveryValue - beforeValue))}
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-gray-500">Recovery Rate</div>
                  <div className="font-medium">
                    {Math.abs(recoveryPercent).toFixed(0)}%
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}

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