/**
 * Divider
 * 
 * Description: Visual separator between sections and content blocks
 * Use Cases: Section breaks, content separation, visual organization
 * Data Format: Optional label or simple divider line
 * 
 * @param label - Optional text label for the divider
 * @param variant - Visual style variant
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface DividerProps {
  label?: string;
  variant?: 'line' | 'space' | 'dotted';
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function Divider({ 
  label,
  variant = 'line',
  onApprove, 
  onDisapprove
}: DividerProps) {
  
  const renderDivider = () => {
    switch (variant) {
      case 'space':
        return <div className="py-6" />;
      case 'dotted':
        return <div className="border-t border-dotted border-gray-300" />;
      case 'line':
      default:
        return <div className="border-t border-gray-200" />;
    }
  };

  if (label) {
    return (
      <div className="relative py-4">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-200" />
        </div>
        <div className="relative flex justify-center">
          <span className="bg-gray-50 px-4 text-sm text-gray-500 font-medium">
            {label}
          </span>
        </div>
        
        {(onApprove || onDisapprove) && (
          <div className="flex gap-1 justify-center mt-2">
            {onApprove && (
              <button
                onClick={onApprove}
                className="px-2 py-1 bg-green-50 text-green-700 rounded text-xs hover:bg-green-100 transition-colors"
              >
                ✓
              </button>
            )}
            {onDisapprove && (
              <button
                onClick={onDisapprove}
                className="px-2 py-1 bg-red-50 text-red-700 rounded text-xs hover:bg-red-100 transition-colors"
              >
                ✗
              </button>
            )}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="py-2">
      {renderDivider()}
      {(onApprove || onDisapprove) && (
        <div className="flex gap-1 justify-center mt-2">
          {onApprove && (
            <button
              onClick={onApprove}
              className="px-2 py-1 bg-green-50 text-green-700 rounded text-xs hover:bg-green-100 transition-colors"
            >
              ✓
            </button>
          )}
          {onDisapprove && (
            <button
              onClick={onDisapprove}
              className="px-2 py-1 bg-red-50 text-red-700 rounded text-xs hover:bg-red-100 transition-colors"
            >
              ✗
            </button>
          )}
        </div>
      )}
    </div>
  );
}