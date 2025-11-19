/**
 * BulletList
 * 
 * Description: Simple bullet points for key findings, risks, or recommendations
 * Use Cases: Risk factors, key points, action items, features
 * Data Format: Array of strings or objects with text and optional metadata
 * 
 * @param items - Array of bullet point items
 * @param title - Optional title for the bullet list
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface BulletItem {
  text: string;
  emphasis?: 'normal' | 'strong' | 'subtle';
}

interface BulletListProps {
  items: (string | BulletItem)[];
  title?: string;
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function BulletList({
  items,
  title,
  onApprove,
  onDisapprove,
  variant = 'default'
}: BulletListProps) {

  const getTextClasses = (emphasis: string = 'normal') => {
    switch (emphasis) {
      case 'strong':
        return 'text-gray-900 font-medium';
      case 'subtle':
        return 'text-gray-500';
      case 'normal':
      default:
        return 'text-gray-700';
    }
  };

  return (
    <div className="bg-white  rounded-lg p-6">
      {title && (
        <h3 className="text-lg font-medium text-gray-900 mb-4">{title}</h3>
      )}

      <ul className="space-y-3">
        {items.map((item, index) => {
          const isObject = typeof item === 'object';
          const text = isObject ? item.text : item;
          const emphasis = isObject ? item.emphasis || 'normal' : 'normal';

          return (
            <li key={index} className="flex items-start">
              <div className="w-1.5 h-1.5 bg-gray-400 rounded-full mt-2.5 mr-3 flex-shrink-0"></div>
              <span className={getTextClasses(emphasis)}>{text}</span>
            </li>
          );
        })}
      </ul>

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