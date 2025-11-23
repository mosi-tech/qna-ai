/**
 * ActionList
 * 
 * Description: List of suggested actions with priorities and timelines
 * Use Cases: Investment recommendations, risk mitigation actions, strategic moves
 * Data Format: Array of action items with priority, timeline, and details
 * 
 * @param actions - Array of action items
 * @param title - Optional title for the action list
 * @param showPriority - Whether to display priority indicators
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface Action {
  id: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  timeline?: 'immediate' | 'short-term' | 'medium-term' | 'long-term';
  impact?: 'high' | 'medium' | 'low';
  effort?: 'high' | 'medium' | 'low';
  category?: string;
}

interface ActionListProps {
  actions: Action[];
  title?: string;
  showPriority?: boolean;
  groupByPriority?: boolean;
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function ActionList({
  actions,
  title,
  showPriority = true,
  groupByPriority = false,
  onApprove,
  onDisapprove,
  
}: ActionListProps) {


  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTimelineColor = (timeline: string = '') => {
    switch (timeline) {
      case 'immediate':
        return 'bg-red-50 text-red-700';
      case 'short-term':
        return 'bg-orange-50 text-orange-700';
      case 'medium-term':
        return 'bg-blue-50 text-blue-700';
      case 'long-term':
        return 'bg-purple-50 text-purple-700';
      default:
        return 'bg-gray-50 text-gray-700';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high':
        return '🔴';
      case 'medium':
        return '🟡';
      case 'low':
        return '🟢';
      default:
        return '⚪';
    }
  };

  const groupedActions = groupByPriority ? {
    high: actions.filter(a => a.priority === 'high'),
    medium: actions.filter(a => a.priority === 'medium'),
    low: actions.filter(a => a.priority === 'low')
  } : null;


  const renderActionItem = (action: Action, index: number) => (
    <div key={action.id} className={` rounded-lg ${config.itemPadding} hover:border-gray-300 transition-colors hover:shadow-sm`}>
      <div className="flex justify-between items-start mb-2 sm:mb-3 flex-wrap gap-2">
        <div className="flex items-center gap-2 min-w-0 flex-1">
          <span className="text-base sm:text-lg flex-shrink-0">{getPriorityIcon(action.priority)}</span>
          <h4 className={`${config.actionTitleSize} font-medium text-gray-900 truncate`}>{action.title}</h4>
        </div>

        <div className="flex gap-1 sm:gap-2 flex-wrap flex-shrink-0">
          {showPriority && (
            <span className={`${config.badgeSize} font-medium rounded-full border ${getPriorityColor(action.priority)}`}>
              {variant === 'compact' ? action.priority.charAt(0).toUpperCase() : `${action.priority} priority`}
            </span>
          )}
          {action.timeline && (
            <span className={`${config.badgeSize} font-medium rounded ${getTimelineColor(action.timeline)}`}>
              {variant === 'compact' ?
                action.timeline.split('-')[0] :
                action.timeline
              }
            </span>
          )}
        </div>
      </div>

      <p className={`${config.contentSize} text-gray-700 leading-relaxed mb-2 sm:mb-3 break-words`}>
        {action.description}
      </p>

      {variant === 'detailed' && (action.impact || action.effort || action.category) && (
        <div className="flex gap-2 sm:gap-4 text-xs text-gray-600 flex-wrap">
          {action.impact && (
            <div className="flex-shrink-0">
              <span className="font-medium">Impact:</span> {action.impact}
            </div>
          )}
          {action.effort && (
            <div className="flex-shrink-0">
              <span className="font-medium">Effort:</span> {action.effort}
            </div>
          )}
          {action.category && (
            <div className="flex-shrink-0">
              <span className="font-medium">Category:</span> {action.category}
            </div>
          )}
        </div>
      )}
    </div>
  );

  const renderActionGroup = (groupActions: Action[], groupTitle: string) => (
    <div key={groupTitle} className={config.spacing}>
      <h4 className={`${config.actionTitleSize} font-medium text-gray-900 capitalize`}>
        {groupTitle} Priority Actions
      </h4>
      <div className={config.spacing}>
        {groupActions.map((action, index) => renderActionItem(action, index))}
      </div>
    </div>
  );

  return (
    <div className={`bg-white  rounded-lg ${config.containerPadding}`}>
      {title && (
        <h3 className={`${config.titleSize} font-medium text-gray-900 mb-3 sm:mb-4 truncate`}>{title}</h3>
      )}

      <div className={config.groupSpacing}>
        {groupByPriority && groupedActions ? (
          <>
            {groupedActions.high.length > 0 && renderActionGroup(groupedActions.high, 'high')}
            {groupedActions.medium.length > 0 && renderActionGroup(groupedActions.medium, 'medium')}
            {groupedActions.low.length > 0 && renderActionGroup(groupedActions.low, 'low')}
          </>
        ) : (
          <div className={config.spacing}>
            {actions.map((action, index) => renderActionItem(action, index))}
          </div>
        )}
      </div>

      {(onApprove || onDisapprove) && (
        <div className="flex gap-2 mt-4 sm:mt-6 pt-3 sm:pt-4 border-t border-gray-100 flex-wrap">
          {onApprove && (
            <button
              onClick={onApprove}
              className="px-3 py-1.5 sm:px-4 sm:py-2 bg-green-50 text-green-700 rounded-md hover:bg-green-100 transition-colors text-sm font-medium"
            >
              Approve Actions
            </button>
          )}
          {onDisapprove && (
            <button
              onClick={onDisapprove}
              className="px-3 py-1.5 sm:px-4 sm:py-2 bg-red-50 text-red-700 rounded-md hover:bg-red-100 transition-colors text-sm font-medium"
            >
              Disapprove Actions
            </button>
          )}
        </div>
      )}
    </div>
  );
}