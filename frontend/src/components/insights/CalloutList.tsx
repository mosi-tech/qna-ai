/**
 * CalloutList
 * 
 * Description: A list of callout items with optional title, designed for quarter-width spaces
 * Use Cases: Key highlights, insights, warnings grouped together
 * Data Format: Array of callout items with title, content, and type
 * 
 * @param title - Optional title for the callout list
 * @param items - Array of callout items
 * @param variant - Component variant for different space sizes
 */

'use client';

interface CalloutItem {
  id: string;
  title: string;
  content: string;
  type: 'info' | 'warning' | 'success' | 'error';
}

interface CalloutListProps {
  title?: string;
  items: CalloutItem[];
  variant?: 'default' | 'compact' | 'detailed';
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function CalloutList({ 
  title,
  items,
  variant = 'default',
  onApprove, 
  onDisapprove 
}: CalloutListProps) {
  
  const getVariantConfig = () => {
    switch (variant) {
      case 'compact':
        return {
          containerPadding: 'p-3 sm:p-4',
          titleSize: 'text-sm sm:text-base font-semibold',
          titleMargin: 'mb-3',
          itemSpacing: 'space-y-2',
          itemPadding: 'p-2.5 sm:p-3',
          iconSize: 'text-sm',
          itemTitleSize: 'text-xs sm:text-sm font-medium',
          contentSize: 'text-xs leading-tight'
        };
      case 'detailed':
        return {
          containerPadding: 'p-5 sm:p-6',
          titleSize: 'text-lg sm:text-xl font-bold',
          titleMargin: 'mb-4',
          itemSpacing: 'space-y-4',
          itemPadding: 'p-4 sm:p-5',
          iconSize: 'text-base',
          itemTitleSize: 'text-base font-semibold',
          contentSize: 'text-sm leading-relaxed'
        };
      default:
        return {
          containerPadding: 'p-4 sm:p-5',
          titleSize: 'text-base sm:text-lg font-semibold',
          titleMargin: 'mb-3',
          itemSpacing: 'space-y-3',
          itemPadding: 'p-3 sm:p-4',
          iconSize: 'text-sm',
          itemTitleSize: 'text-sm font-medium',
          contentSize: 'text-sm leading-relaxed'
        };
    }
  };

  const getItemStyleClasses = (type: string) => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'error':
        return 'bg-red-50 border-red-200 text-red-800';
      case 'info':
      default:
        return 'bg-blue-50 border-blue-200 text-blue-800';
    }
  };

  const getIcon = (type: string) => {
    switch (type) {
      case 'success':
        return '✓';
      case 'warning':
        return '⚠';
      case 'error':
        return '✗';
      case 'info':
      default:
        return 'ℹ';
    }
  };

  const getTitleColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'text-green-900';
      case 'warning':
        return 'text-yellow-900';
      case 'error':
        return 'text-red-900';
      case 'info':
      default:
        return 'text-blue-900';
    }
  };

  const config = getVariantConfig();
  
  return (
    <div className={`bg-white rounded-lg ${config.containerPadding}`}>
      {title && (
        <h3 className={`${config.titleSize} text-gray-900 ${config.titleMargin}`}>{title}</h3>
      )}
      
      <div className={config.itemSpacing}>
        {items.map((item) => (
          <div 
            key={item.id} 
            className={`border rounded-lg ${config.itemPadding} ${getItemStyleClasses(item.type)}`}
          >
            <div className="flex items-start space-x-2 sm:space-x-3">
              <div className={`flex-shrink-0 ${config.iconSize}`}>
                {getIcon(item.type)}
              </div>
              <div className="flex-1 min-w-0">
                <h4 className={`${config.itemTitleSize} mb-1 ${getTitleColor(item.type)} truncate`}>
                  {item.title}
                </h4>
                <p className={`${config.contentSize} break-words`}>
                  {item.content}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {(onApprove || onDisapprove) && (
        <div className="flex gap-2 mt-4 pt-3 border-t border-gray-200 flex-wrap">
          {onApprove && (
            <button
              onClick={onApprove}
              className="px-3 py-1.5 bg-green-50 text-green-700 rounded-md hover:bg-green-100 transition-colors text-sm font-medium"
            >
              Approve
            </button>
          )}
          {onDisapprove && (
            <button
              onClick={onDisapprove}
              className="px-3 py-1.5 bg-red-50 text-red-700 rounded-md hover:bg-red-100 transition-colors text-sm font-medium"
            >
              Disapprove
            </button>
          )}
        </div>
      )}
    </div>
  );
}