import React from 'react';

// Data interface for Portfolio Drift from Target
interface PortfolioDriftMonitoringProps {
  title?: string;
  data: any;
  loading?: boolean;
  error?: string;
}


// Sample data for development
export const SAMPLE_DATA: PortfolioDriftMonitoringProps = {
  title: 'Portfolio Drift from Target',
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
 * Portfolio Drift from Target finBlock
 *
 * @description Holdings that have drifted from target allocation requiring rebalancing
 * @blockType bar-list
 * @concepts rebalancing, drift
 * @mcpRequired get_positions
 */
export const PortfolioDriftMonitoring: React.FC<PortfolioDriftMonitoringProps> = ({
  title = 'Portfolio Drift from Target',
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
    <div className="finblock portfolio-drift-monitoring rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 font-semibold text-gray-800">{title}</h3>
      {/* Block Type: bar-list */}
      <pre className="max-h-96 overflow-auto rounded bg-gray-50 p-3 text-xs">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
};

export default PortfolioDriftMonitoring;
