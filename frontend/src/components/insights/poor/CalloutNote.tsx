/**
 * CalloutNote
 * 
 * Description: Highlighted info/warning/success note boxes for important information
 * Use Cases: Warnings, important findings, disclaimers, key insights
 * Data Format: Text content with type and optional title
 * 
 * @param content - The note content
 * @param type - Note type for styling and icon
 * @param title - Optional title for the note
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface CalloutNoteProps {
  content: string;
  type: 'info' | 'warning' | 'success' | 'error';
  title?: string;
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function CalloutNote({ 
  content,
  type,
  title,
  onApprove, 
  onDisapprove,
  variant = 'default' 
}: CalloutNoteProps) {
  
  const getVariantConfig = () => {
    switch (variant) {
      case 'compact':
        return {
          padding: 'p-4 sm:p-5',
          spacing: 'space-x-2 sm:space-x-3',
          iconSize: 'text-sm',
          titleSize: 'text-sm sm:text-base font-medium',
          contentSize: 'text-xs sm:text-sm leading-relaxed',
          buttonMargin: 'mt-3 ml-6'
        };
      case 'detailed':
        return {
          padding: 'p-4 sm:p-6',
          spacing: 'space-x-4',
          iconSize: 'text-xl',
          titleSize: 'text-base sm:text-lg font-semibold',
          contentSize: 'text-sm sm:text-base leading-relaxed',
          buttonMargin: 'mt-4 ml-10'
        };
      default:
        return {
          padding: 'p-3 sm:p-4',
          spacing: 'space-x-2 sm:space-x-3',
          iconSize: 'text-base sm:text-lg',
          titleSize: 'text-sm sm:text-base font-medium',
          contentSize: 'text-xs sm:text-sm leading-relaxed',
          buttonMargin: 'mt-3 ml-6 sm:ml-8'
        };
    }
  };

  const getStyleClasses = () => {
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

  const getIcon = () => {
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

  const getTitleColor = () => {
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

  const getButtonClasses = () => {
    switch (type) {
      case 'success':
        return {
          approve: 'bg-green-100 text-green-800 hover:bg-green-200',
          disapprove: 'bg-green-100 text-green-600 hover:bg-green-200'
        };
      case 'warning':
        return {
          approve: 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200',
          disapprove: 'bg-yellow-100 text-yellow-600 hover:bg-yellow-200'
        };
      case 'error':
        return {
          approve: 'bg-red-100 text-red-800 hover:bg-red-200',
          disapprove: 'bg-red-100 text-red-600 hover:bg-red-200'
        };
      case 'info':
      default:
        return {
          approve: 'bg-blue-100 text-blue-800 hover:bg-blue-200',
          disapprove: 'bg-blue-100 text-blue-600 hover:bg-blue-200'
        };
    }
  };

  const buttonClasses = getButtonClasses();
  const config = getVariantConfig();
  
  return (
    <div className={`border rounded-lg ${config.padding} ${getStyleClasses()}`}>
      <div className={`flex items-start ${config.spacing}`}>
        <div className={`flex-shrink-0 ${config.iconSize}`}>
          {getIcon()}
        </div>
        <div className="flex-1 min-w-0">
          {title && (
            <h4 className={`${config.titleSize} mb-1 ${getTitleColor()} truncate`}>
              {title}
            </h4>
          )}
          <p className={`${config.contentSize} break-words`}>
            {content}
          </p>
        </div>
      </div>
      
      {(onApprove || onDisapprove) && (
        <div className={`flex gap-1 sm:gap-2 ${config.buttonMargin} flex-wrap`}>
          {onApprove && (
            <button
              onClick={onApprove}
              className={`px-2 py-1 sm:px-3 sm:py-1 rounded text-xs font-medium transition-colors ${buttonClasses.approve}`}
            >
              Approve
            </button>
          )}
          {onDisapprove && (
            <button
              onClick={onDisapprove}
              className={`px-2 py-1 sm:px-3 sm:py-1 rounded text-xs font-medium transition-colors ${buttonClasses.disapprove}`}
            >
              Disapprove
            </button>
          )}
        </div>
      )}
    </div>
  );
}