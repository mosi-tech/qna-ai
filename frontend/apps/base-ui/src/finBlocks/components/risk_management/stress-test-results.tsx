import React from 'react';

// Data interface for Stress Test Scenarios
interface StressTestResultsProps {
  title?: string;
  data: any;
  loading?: boolean;
  error?: string;
}


// Sample data for development
export const SAMPLE_DATA: StressTestResultsProps = {
  title: 'Stress Test Scenarios',
  data: {
    "data": [
        {
            "name": "AAPL",
            "value": 15.5
        },
        {
            "name": "MSFT",
            "value": 12.3
        },
        {
            "name": "GOOGL",
            "value": 10.8
        }
    ]
},
  loading: false,
  error: undefined,
};

/**
 * Stress Test Scenarios finBlock
 *
 * @description Portfolio impact under historical stress scenarios (2008, 2020, etc.)
 * @blockType bar-list
 * @concepts tail risk, worst-case scenarios
 * @mcpRequired get_portfolio_history, get_positions
 */
export const StressTestResults: React.FC<StressTestResultsProps> = ({
  title = 'Stress Test Scenarios',
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
    <div className="finblock stress-test-results rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 font-semibold text-gray-800">{title}</h3>
      {/* Block Type: bar-list */}
      <pre className="max-h-96 overflow-auto rounded bg-gray-50 p-3 text-xs">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
};

export default StressTestResults;
