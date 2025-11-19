/**
 * Checklist
 * 
 * Description: Task validation checklist with completion status
 * Use Cases: Due diligence, compliance checks, analysis validation
 */

'use client';

interface ChecklistItem {
  id: string;
  text: string;
  completed: boolean;
  required?: boolean;
}

interface ChecklistProps {
  items: ChecklistItem[];
  title?: string;
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function Checklist({ items, title, onApprove, onDisapprove }: ChecklistProps) {
  const completedCount = items.filter(item => item.completed).length;
  const completionRate = (completedCount / items.length) * 100;

  return (
    <div className="bg-white  rounded-lg p-6">
      {title && <h3 className="text-lg font-medium text-gray-900 mb-4">{title}</h3>}
      <div className="mb-4">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>{completedCount} of {items.length} completed</span>
          <span>{completionRate.toFixed(0)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div className="bg-green-500 h-2 rounded-full" style={{ width: `${completionRate}%` }}></div>
        </div>
      </div>
      <div className="space-y-3">
        {items.map(item => (
          <div key={item.id} className="flex items-center space-x-3">
            <div className={`w-4 h-4 rounded border-2 flex items-center justify-center ${item.completed ? 'bg-green-500 border-green-500' : 'border-gray-300'
              }`}>
              {item.completed && <span className="text-white text-xs">✓</span>}
            </div>
            <span className={`text-sm ${item.completed ? 'line-through text-gray-500' : 'text-gray-700'}`}>
              {item.text}
              {item.required && <span className="text-red-500 ml-1">*</span>}
            </span>
          </div>
        ))}
      </div>
      {(onApprove || onDisapprove) && (
        <div className="flex gap-2 mt-4">
          {onApprove && <button onClick={onApprove} className="px-4 py-2 bg-green-50 text-green-700 rounded-md">Approve</button>}
          {onDisapprove && <button onClick={onDisapprove} className="px-4 py-2 bg-red-50 text-red-700 rounded-md">Disapprove</button>}
        </div>
      )}
    </div>
  );
}