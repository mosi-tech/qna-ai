/**
 * ScenarioBlock
 * 
 * Description: If X then Y scenario analysis with conditions and outcomes
 * Use Cases: Market scenario planning, stress testing, contingency analysis
 */

'use client';

interface ScenarioBlockProps {
  title: string;
  condition: string;
  outcome: string;
  probability?: number;
  impact?: 'high' | 'medium' | 'low';
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function ScenarioBlock({
  title, condition, outcome, probability, impact, onApprove, onDisapprove
}: ScenarioBlockProps) {
  return (
    <div className="bg-white  rounded-lg p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">{title}</h3>
      <div className="space-y-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <h4 className="font-medium text-blue-900">If:</h4>
          <p className="text-blue-800">{condition}</p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <h4 className="font-medium text-green-900">Then:</h4>
          <p className="text-green-800">{outcome}</p>
        </div>
        {(probability || impact) && (
          <div className="flex gap-4 text-sm">
            {probability && <span>Probability: {probability}%</span>}
            {impact && <span>Impact: {impact}</span>}
          </div>
        )}
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