/**
 * TimeProgressIndicator
 * 
 * Description: Shows time progression through stages with duration markers
 * Use Cases: Recovery timelines, process flows, milestone tracking
 * Data Format: Array of time stages with durations and labels
 * 
 * @param stages - Array of time stages
 * @param title - Optional title for the progress
 * @param totalDuration - Total time span
 * @param unit - Time unit (days, hours, minutes)
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface TimeStage {
  id: string;
  label: string;
  duration: number;
  type?: 'start' | 'milestone' | 'end' | 'event';
  description?: string;
}

interface TimeProgressIndicatorProps {
  stages: TimeStage[];
  title?: string;
  totalDuration?: number;
  unit?: string;
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function TimeProgressIndicator({
  stages,
  title,
  totalDuration,
  unit = 'days',
  onApprove,
  onDisapprove,
  variant = 'default'
}: TimeProgressIndicatorProps) {

  const maxDuration = totalDuration || Math.max(...stages.map(s => s.duration));

  const getStageColor = (type: string = 'milestone') => {
    switch (type) {
      case 'start':
        return 'bg-blue-500 border-blue-600';
      case 'end':
        return 'bg-green-500 border-green-600';
      case 'event':
        return 'bg-red-500 border-red-600';
      case 'milestone':
      default:
        return 'bg-gray-400 border-gray-500';
    }
  };

  const getStageIcon = (type: string = 'milestone') => {
    switch (type) {
      case 'start':
        return '▶';
      case 'end':
        return '✓';
      case 'event':
        return '!';
      case 'milestone':
      default:
        return '●';
    }
  };

  const calculatePosition = (duration: number) => {
    return (duration / maxDuration) * 100;
  };

  return (
    <div className="bg-white  rounded-lg p-6">
      {title && (
        <h3 className="text-lg font-medium text-gray-900 mb-4">{title}</h3>
      )}

      <div className="relative">
        {/* Timeline bar */}
        <div className="relative h-2 bg-gray-200 rounded-full mb-8">
          <div className="absolute inset-0 bg-blue-100 rounded-full"></div>

          {/* Stage markers */}
          {stages.map((stage, index) => {
            const position = calculatePosition(stage.duration);
            return (
              <div
                key={stage.id}
                className="absolute transform -translate-x-1/2"
                style={{ left: `${position}%`, top: '-4px' }}
              >
                <div className={`w-4 h-4 rounded-full border-2 ${getStageColor(stage.type)} flex items-center justify-center`}>
                  <span className="text-white text-xs font-bold">
                    {getStageIcon(stage.type)}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Stage labels */}
        <div className="space-y-3">
          {stages.map((stage, index) => {
            const position = calculatePosition(stage.duration);
            return (
              <div key={`${stage.id}-label`} className="relative">
                <div
                  className="absolute transform -translate-x-1/2"
                  style={{ left: `${position}%` }}
                >
                  <div className="bg-white  rounded-lg p-3 shadow-sm min-w-[120px] text-center">
                    <div className="text-sm font-medium text-gray-900">
                      {stage.label}
                    </div>
                    <div className="text-xs text-gray-600 mt-1">
                      {stage.duration} {unit}
                    </div>
                    {variant === 'detailed' && stage.description && (
                      <div className="text-xs text-gray-500 mt-1">
                        {stage.description}
                      </div>
                    )}
                  </div>

                  {/* Connector line */}
                  <div className="w-px h-4 bg-gray-300 mx-auto"></div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Duration scale */}
        <div className="flex justify-between mt-8 text-xs text-gray-500">
          <span>0 {unit}</span>
          <span>{maxDuration} {unit}</span>
        </div>
      </div>

      {/* Summary */}
      {variant === 'detailed' && (
        <div className="mt-6 bg-gray-50 rounded-lg p-4">
          <div className="grid grid-cols-3 gap-4 text-center text-sm">
            <div>
              <div className="text-gray-500">Total Duration</div>
              <div className="font-semibold text-gray-900">{maxDuration} {unit}</div>
            </div>
            <div>
              <div className="text-gray-500">Stages</div>
              <div className="font-semibold text-gray-900">{stages.length}</div>
            </div>
            <div>
              <div className="text-gray-500">Average Stage</div>
              <div className="font-semibold text-gray-900">
                {(stages.reduce((sum, stage) => sum + stage.duration, 0) / stages.length).toFixed(1)} {unit}
              </div>
            </div>
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