/**
 * Subheadline
 * 
 * Description: Optional secondary line below headlines, provides context or summary
 * Use Cases: Analysis descriptions, timeframes, methodology notes
 * Data Format: Simple text string
 * 
 * @param text - The subheadline text to display
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface SubheadlineProps {
  text: string;
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function Subheadline({ 
  text, 
  onApprove, 
  onDisapprove,
  variant = 'default' 
}: SubheadlineProps) {
  
  return (
    <div className="bg-gray-50 border border-gray-100 rounded-lg p-4">
      <div className="flex justify-between items-start">
        <p className="text-gray-600 leading-relaxed">
          {text}
        </p>
        
        {(onApprove || onDisapprove) && (
          <div className="flex gap-2 ml-4 flex-shrink-0">
            {onApprove && (
              <button
                onClick={onApprove}
                className="px-2 py-1 bg-green-50 text-green-700 rounded hover:bg-green-100 transition-colors text-xs"
              >
                ✓
              </button>
            )}
            {onDisapprove && (
              <button
                onClick={onDisapprove}
                className="px-2 py-1 bg-red-50 text-red-700 rounded hover:bg-red-100 transition-colors text-xs"
              >
                ✗
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}