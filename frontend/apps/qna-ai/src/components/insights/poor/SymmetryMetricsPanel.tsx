/**
 * SymmetryMetricsPanel
 * 
 * Description: Displays portfolio-level symmetry statistics and summary metrics
 * Use Cases: Executive dashboards, portfolio overview reports, symmetry analysis summary
 * Data Format: Aggregated symmetry metrics across the entire portfolio
 * 
 * @param data - Portfolio symmetry summary data
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface PortfolioSymmetryData {
  totalPositions: number;
  avgSymmetryScore: number;
  mostSymmetricPosition: string;
  leastSymmetricPosition: string;
  symmetricPositions: number;
  asymmetricPositions: number;
  portfolioUpDays: number;
  portfolioDownDays: number;
  overallBalance: number;
}

interface SymmetryMetricsPanelProps {
  data: PortfolioSymmetryData;
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function SymmetryMetricsPanel({
  data,
  onApprove,
  onDisapprove,
  variant = 'default'
}: SymmetryMetricsPanelProps) {

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'text-green-700';
    if (score >= 0.5) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getBalanceColor = (balance: number) => {
    if (Math.abs(balance) <= 0.1) return 'text-green-700';
    if (Math.abs(balance) <= 0.2) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="bg-white  rounded-lg p-6">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Portfolio Symmetry Overview</h2>
          <p className="text-sm text-gray-600">Analysis of up vs down day patterns across {data.totalPositions} positions</p>
        </div>
        <div className="text-right">
          <div className={`text-2xl font-bold ${getScoreColor(data.avgSymmetryScore)}`}>
            {(data.avgSymmetryScore * 100).toFixed(1)}%
          </div>
          <div className="text-xs text-gray-500">Avg Symmetry</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-50 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-gray-900">{data.totalPositions}</div>
          <div className="text-sm text-gray-600">Total Positions</div>
        </div>
        <div className="bg-green-50 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-green-700">{data.symmetricPositions}</div>
          <div className="text-sm text-gray-600">Symmetric (≥70%)</div>
        </div>
        <div className="bg-red-50 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-red-600">{data.asymmetricPositions}</div>
          <div className="text-sm text-gray-600">Asymmetric (&lt;50%)</div>
        </div>
        <div className="bg-blue-50 rounded-lg p-4 text-center">
          <div className={`text-2xl font-bold ${getBalanceColor(data.overallBalance)}`}>
            {data.overallBalance > 0 ? '+' : ''}{(data.overallBalance * 100).toFixed(1)}%
          </div>
          <div className="text-sm text-gray-600">Portfolio Balance</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="border border-gray-100 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-900">Most Symmetric</span>
            <span className="text-green-700 text-sm">Best Balance</span>
          </div>
          <div className="text-lg font-semibold text-gray-900">{data.mostSymmetricPosition}</div>
        </div>
        <div className="border border-gray-100 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-900">Least Symmetric</span>
            <span className="text-red-600 text-sm">Needs Attention</span>
          </div>
          <div className="text-lg font-semibold text-gray-900">{data.leastSymmetricPosition}</div>
        </div>
      </div>

      <div className="bg-gray-50 rounded-lg p-4 mb-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Portfolio Up Days</span>
          <span className="font-medium text-green-600">{data.portfolioUpDays}</span>
        </div>
        <div className="flex items-center justify-between text-sm mt-2">
          <span className="text-gray-600">Portfolio Down Days</span>
          <span className="font-medium text-red-600">{data.portfolioDownDays}</span>
        </div>
        <div className="mt-3 bg-gray-200 rounded-full h-2">
          <div
            className="bg-green-500 h-2 rounded-full"
            style={{
              width: `${(data.portfolioUpDays / (data.portfolioUpDays + data.portfolioDownDays)) * 100}%`
            }}
          ></div>
        </div>
      </div>

      <div className="flex gap-2">
        <button
          onClick={onApprove}
          className="flex-1 px-4 py-2 bg-green-50 text-green-700 rounded-md hover:bg-green-100 transition-colors text-sm font-medium"
        >
          Approve Summary
        </button>
        <button
          onClick={onDisapprove}
          className="flex-1 px-4 py-2 bg-red-50 text-red-700 rounded-md hover:bg-red-100 transition-colors text-sm font-medium"
        >
          Disapprove Summary
        </button>
      </div>
    </div>
  );
}