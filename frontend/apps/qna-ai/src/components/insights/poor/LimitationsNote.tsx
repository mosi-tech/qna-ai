/**
 * LimitationsNote
 * 
 * Description: Important limitations and caveats of the analysis
 */

'use client';

interface LimitationsNoteProps {
  limitations: string[];
  title?: string;
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function LimitationsNote({ limitations, title = "Analysis Limitations", onApprove, onDisapprove }: LimitationsNoteProps) {
  return (
    <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
      <div className="flex items-start space-x-2 mb-3">
        <span className="text-orange-600 text-lg">⚠</span>
        <h4 className="text-sm font-medium text-orange-900">{title}</h4>
      </div>
      <ul className="space-y-2">
        {limitations.map((limitation, index) => (
          <li key={index} className="flex items-start text-sm text-orange-800">
            <span className="w-1 h-1 bg-orange-600 rounded-full mt-2 mr-3 flex-shrink-0"></span>
            {limitation}
          </li>
        ))}
      </ul>
      {(onApprove || onDisapprove) && (
        <div className="flex gap-2 mt-3">
          {onApprove && <button onClick={onApprove} className="px-3 py-1 bg-orange-100 text-orange-800 rounded text-xs">Approve</button>}
          {onDisapprove && <button onClick={onDisapprove} className="px-3 py-1 bg-orange-100 text-orange-600 rounded text-xs">Disapprove</button>}
        </div>
      )}
    </div>
  );
}