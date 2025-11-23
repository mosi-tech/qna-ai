/**
 * AssumptionList
 * 
 * Description: Lists key assumptions made in the analysis
 */

'use client';

interface AssumptionListProps {
  assumptions: string[];
  title?: string;
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function AssumptionList({ assumptions, title = "Key Assumptions", onApprove, onDisapprove }: AssumptionListProps) {
  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
      <h4 className="text-sm font-medium text-yellow-900 mb-3">{title}</h4>
      <ul className="space-y-2">
        {assumptions.map((assumption, index) => (
          <li key={index} className="flex items-start text-sm text-yellow-800">
            <span className="w-1 h-1 bg-yellow-600 rounded-full mt-2 mr-3 flex-shrink-0"></span>
            {assumption}
          </li>
        ))}
      </ul>
      {(onApprove || onDisapprove) && (
        <div className="flex gap-2 mt-3">
          {onApprove && <button onClick={onApprove} className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded text-xs">Approve</button>}
          {onDisapprove && <button onClick={onDisapprove} className="px-3 py-1 bg-yellow-100 text-yellow-600 rounded text-xs">Disapprove</button>}
        </div>
      )}
    </div>
  );
}