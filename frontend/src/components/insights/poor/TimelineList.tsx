/**
 * TimelineList
 * 
 * Description: Chronological list of events or milestones
 * Use Cases: Event history, milestone tracking, chronological analysis
 * Data Format: Array of time-ordered events with dates and descriptions
 * 
 * @param events - Array of timeline events
 * @param title - Optional title for the timeline
 * @param showDates - Whether to display dates
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface TimelineEvent {
  id: string;
  date: string | Date;
  title: string;
  description?: string;
  type?: 'positive' | 'negative' | 'neutral' | 'milestone';
  impact?: 'high' | 'medium' | 'low';
}

interface TimelineListProps {
  events: TimelineEvent[];
  title?: string;
  showDates?: boolean;
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function TimelineList({
  events,
  title,
  showDates = true,
  onApprove,
  onDisapprove,
  variant = 'default'
}: TimelineListProps) {

  const formatDate = (date: string | Date) => {
    const d = typeof date === 'string' ? new Date(date) : date;
    return d.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getEventColor = (type: string = 'neutral') => {
    switch (type) {
      case 'positive':
        return 'bg-green-100 border-green-300';
      case 'negative':
        return 'bg-red-100 border-red-300';
      case 'milestone':
        return 'bg-blue-100 border-blue-300';
      case 'neutral':
      default:
        return 'bg-gray-100 border-gray-300';
    }
  };

  const getEventDot = (type: string = 'neutral') => {
    switch (type) {
      case 'positive':
        return 'bg-green-500';
      case 'negative':
        return 'bg-red-500';
      case 'milestone':
        return 'bg-blue-500';
      case 'neutral':
      default:
        return 'bg-gray-400';
    }
  };

  const getImpactBadge = (impact: string = 'medium') => {
    switch (impact) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'low':
        return 'bg-gray-100 text-gray-600';
      case 'medium':
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  return (
    <div className="bg-white  rounded-lg p-6">
      {title && (
        <h3 className="text-lg font-medium text-gray-900 mb-6">{title}</h3>
      )}

      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200"></div>

        <div className="space-y-6">
          {events.map((event, index) => (
            <div key={event.id} className="relative flex items-start">
              {/* Timeline dot */}
              <div className={`absolute left-4 w-4 h-4 rounded-full border-2 border-white ${getEventDot(event.type)}`}></div>

              {/* Event content */}
              <div className="ml-12 w-full">
                <div className={`p-4 rounded-lg border ${getEventColor(event.type)}`}>
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="text-md font-medium text-gray-900">{event.title}</h4>
                    <div className="flex items-center gap-2 text-sm">
                      {event.impact && (
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getImpactBadge(event.impact)}`}>
                          {event.impact} impact
                        </span>
                      )}
                      {showDates && (
                        <span className="text-gray-500 font-medium">
                          {formatDate(event.date)}
                        </span>
                      )}
                    </div>
                  </div>

                  {event.description && (
                    <p className="text-sm text-gray-700 leading-relaxed">
                      {event.description}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
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