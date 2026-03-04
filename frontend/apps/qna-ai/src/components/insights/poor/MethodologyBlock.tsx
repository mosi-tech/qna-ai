/**
 * MethodologyBlock
 * 
 * Description: Explains the methodology and approach used in analysis
 */

'use client';

interface MethodologyBlockProps {
  methodology: string;
  dataSource?: string;
  timeframe?: string;
  approach?: string;
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function MethodologyBlock({ 
  methodology, dataSource, timeframe, approach, onApprove, onDisapprove 
}: MethodologyBlockProps) {
  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <h4 className="text-sm font-medium text-blue-900 mb-3">Methodology</h4>
      <div className="space-y-3 text-sm text-blue-800">
        <p>{methodology}</p>
        {(dataSource || timeframe || approach) && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-3 pt-3 border-t border-blue-200">
            {dataSource && (
              <div>
                <span className="font-medium">Data Source:</span>
                <div className="text-blue-700">{dataSource}</div>
              </div>
            )}
            {timeframe && (
              <div>
                <span className="font-medium">Timeframe:</span>
                <div className="text-blue-700">{timeframe}</div>
              </div>
            )}
            {approach && (
              <div>
                <span className="font-medium">Approach:</span>
                <div className="text-blue-700">{approach}</div>
              </div>
            )}
          </div>
        )}
      </div>
      {(onApprove || onDisapprove) && (
        <div className="flex gap-2 mt-3">
          {onApprove && <button onClick={onApprove} className="px-3 py-1 bg-blue-100 text-blue-800 rounded text-xs">Approve</button>}
          {onDisapprove && <button onClick={onDisapprove} className="px-3 py-1 bg-blue-100 text-blue-600 rounded text-xs">Disapprove</button>}
        </div>
      )}
    </div>
  );
}