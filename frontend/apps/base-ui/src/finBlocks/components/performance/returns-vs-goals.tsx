import React from 'react';

// Data interface for Returns vs Investment Goals
interface ReturnsVsGoalsProps {
  title?: string;
  data: any;
  loading?: boolean;
  error?: string;
}


// Sample data for development
export const SAMPLE_DATA: ReturnsVsGoalsProps = {
  title: 'Returns vs Investment Goals',
  data: {
    "data": [
        {
            "name": "Jan",
            "value": 2.5
        },
        {
            "name": "Feb",
            "value": 1.8
        },
        {
            "name": "Mar",
            "value": 3.2
        }
    ],
    "categories": [
        "value"
    ]
},
  loading: false,
  error: undefined,
};

/**
 * Returns vs Investment Goals finBlock
 *
 * @description Current return rate vs target for retirement/goals
 * @blockType bar-chart
 * @concepts goal tracking, retirement planning
 * @mcpRequired get_portfolio_history
 */
export const ReturnsVsGoals: React.FC<ReturnsVsGoalsProps> = ({
  title = 'Returns vs Investment Goals',
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
    <div className="finblock returns-vs-goals rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 font-semibold text-gray-800">{title}</h3>
      {/* Block Type: bar-chart */}
      <pre className="max-h-96 overflow-auto rounded bg-gray-50 p-3 text-xs">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
};

export default ReturnsVsGoals;
