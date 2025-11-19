/**
 * QueryRestatement
 * 
 * Description: Restates the original question for clarity and context
 */

'use client';

interface QueryRestatementProps {
  originalQuery: string;
  interpretation: string;
  scope?: string;
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function QueryRestatement({ originalQuery, interpretation, scope, onApprove, onDisapprove }: QueryRestatementProps) {
  return (
    <div className="bg-gray-50  rounded-lg p-4">
      <h4 className="text-sm font-medium text-gray-900 mb-2">Query Analysis</h4>
      <div className="space-y-2 text-sm">
        <div><span className="font-medium text-gray-700">Original:</span> {originalQuery}</div>
        <div><span className="font-medium text-gray-700">Interpretation:</span> {interpretation}</div>
        {scope && <div><span className="font-medium text-gray-700">Scope:</span> {scope}</div>}
      </div>
      {(onApprove || onDisapprove) && (
        <div className="flex gap-2 mt-3">
          {onApprove && <button onClick={onApprove} className="px-3 py-1 bg-green-50 text-green-700 rounded text-xs">Approve</button>}
          {onDisapprove && <button onClick={onDisapprove} className="px-3 py-1 bg-red-50 text-red-700 rounded text-xs">Disapprove</button>}
        </div>
      )}
    </div>
  );
}