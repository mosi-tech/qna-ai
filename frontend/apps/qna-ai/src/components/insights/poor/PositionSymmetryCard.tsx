/**
 * PositionSymmetryCard
 * 
 * Description: Displays symmetry metrics for a single position showing up vs down day patterns
 * Use Cases: Portfolio analysis dashboards, risk assessment reports, position evaluation
 * Data Format: Position data with symmetry calculations and statistical metrics
 * 
 * @param data - The position symmetry data to display
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface PositionSymmetryData {
  symbol: string;
  name: string;
  symmetryScore: number;
  upDays: number;
  downDays: number;
  upDayAvg: number;
  downDayAvg: number;
  totalDays: number;
  volatility: number;
  beta: number;
}

interface PositionSymmetryCardProps {
  data: PositionSymmetryData;
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function PositionSymmetryCard({
  data,
  onApprove,
  onDisapprove,
  variant = 'default'
}: PositionSymmetryCardProps) {

  const getSymmetryColor = (score: number) => {
    if (score >= 0.8) return 'text-green-700';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getSymmetryLabel = (score: number) => {
    if (score >= 0.9) return 'Highly Symmetric';
    if (score >= 0.7) return 'Moderately Symmetric';
    if (score >= 0.5) return 'Somewhat Symmetric';
    return 'Asymmetric';
  };

  return (
    <div className="bg-white  rounded-lg p-6 hover:border-gray-300 transition-colors">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{data.symbol}</h3>
          <p className="text-sm text-gray-600">{data.name}</p>
        </div>
        <div className="text-right">
          <div className={`text-2xl font-bold ${getSymmetryColor(data.symmetryScore)}`}>
            {(data.symmetryScore * 100).toFixed(1)}%
          </div>
          <div className="text-xs text-gray-500">{getSymmetryLabel(data.symmetryScore)}</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-green-50 rounded-lg p-3">
          <div className="text-sm text-gray-600">Up Days</div>
          <div className="text-lg font-semibold text-gray-900">{data.upDays}</div>
          <div className="text-xs text-green-600">Avg: +{data.upDayAvg.toFixed(2)}%</div>
        </div>
        <div className="bg-red-50 rounded-lg p-3">
          <div className="text-sm text-gray-600">Down Days</div>
          <div className="text-lg font-semibold text-gray-900">{data.downDays}</div>
          <div className="text-xs text-red-600">Avg: {data.downDayAvg.toFixed(2)}%</div>
        </div>
      </div>

      {variant === 'detailed' && (
        <div className="grid grid-cols-3 gap-3 mb-4 text-sm">
          <div className="text-center">
            <div className="text-gray-500">Total Days</div>
            <div className="font-medium">{data.totalDays}</div>
          </div>
          <div className="text-center">
            <div className="text-gray-500">Volatility</div>
            <div className="font-medium">{data.volatility.toFixed(1)}%</div>
          </div>
          <div className="text-center">
            <div className="text-gray-500">Beta</div>
            <div className="font-medium">{data.beta.toFixed(2)}</div>
          </div>
        </div>
      )}

      <div className="flex gap-2 pt-4 border-t border-gray-100">
        <button
          onClick={onApprove}
          className="flex-1 px-3 py-2 bg-green-50 text-green-700 rounded-md hover:bg-green-100 transition-colors text-sm font-medium"
        >
          Approve
        </button>
        <button
          onClick={onDisapprove}
          className="flex-1 px-3 py-2 bg-red-50 text-red-700 rounded-md hover:bg-red-100 transition-colors text-sm font-medium"
        >
          Disapprove
        </button>
      </div>
    </div>
  );
}