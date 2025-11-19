/**
 * BadgeList
 * 
 * Description: Collection of positive/negative/neutral flags and labels
 * Use Cases: Risk flags, status indicators, category tags, sentiment markers
 * Data Format: Array of badge objects with text, type, and optional metadata
 * 
 * @param badges - Array of badge objects
 * @param title - Optional title for the badge collection
 * @param layout - Display layout: inline or grid
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface Badge {
  text: string;
  type: 'positive' | 'negative' | 'neutral' | 'warning' | 'info';
  tooltip?: string;
}

interface BadgeListProps {
  badges: Badge[];
  title?: string;
  layout?: 'inline' | 'grid';
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function BadgeList({
  badges,
  title,
  layout = 'inline',
  onApprove,
  onDisapprove,
  variant = 'default'
}: BadgeListProps) {

  const getBadgeClasses = (type: string) => {
    switch (type) {
      case 'positive':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'negative':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'info':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'neutral':
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const containerClasses = layout === 'grid'
    ? 'grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2'
    : 'flex flex-wrap gap-2';

  return (
    <div className="bg-white  rounded-lg p-6">
      {title && (
        <h3 className="text-lg font-medium text-gray-900 mb-4">{title}</h3>
      )}

      <div className={containerClasses}>
        {badges.map((badge, index) => (
          <span
            key={index}
            className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${getBadgeClasses(badge.type)}`}
            title={badge.tooltip}
          >
            {badge.text}
          </span>
        ))}
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