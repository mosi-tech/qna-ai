import React from 'react';

// Data interface for Time-Weighted vs Money-Weighted Returns
interface TimeWeightedReturnsProps {
  title?: string;
  data: any;
  loading?: boolean;
  error?: string;
}


// Sample data for development
export const SAMPLE_DATA: TimeWeightedReturnsProps = {
  title: 'Time-Weighted vs Money-Weighted Returns',
  data: {
    "metrics": [
        {
            "name": "Total Value",
            "stat": 125000,
            "change": "+5.2%",
            "changeType": "positive"
        },
        {
            "name": "P&L YTD",
            "stat": 6250,
            "change": "+12.5%",
            "changeType": "positive"
        },
        {
            "name": "Sharpe Ratio",
            "stat": 1.8,
            "change": "+0.2",
            "changeType": "positive"
        }
    ],
    "cols": 3
},
  loading: false,
  error: undefined,
};

/**
 * Time-Weighted vs Money-Weighted Returns finBlock
 *
 * @description TWR (manager performance) vs MWR (investor returns) comparison
 * @blockType kpi-card
 * @concepts returns, timing impact
 * @mcpRequired get_portfolio_history, get_account
 */
export const TimeWeightedReturns: React.FC<TimeWeightedReturnsProps> = ({
  title = 'Time-Weighted vs Money-Weighted Returns',
  data,
  loading = false,
  error,
}) => {
  if (loading) {
    return <div className="p-4">Loading...</div>;
  }

  if (error) {
    return <div className="p-4 text-red-500">Error: {error}</div>;
  }

  return (
    <div className="finblock time-weighted-returns rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 font-semibold text-gray-800">{title}</h3>
      {/* Block Type: kpi-card */}
      <pre className="max-h-96 overflow-auto rounded bg-gray-50 p-3 text-xs">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
};

export default TimeWeightedReturns;
