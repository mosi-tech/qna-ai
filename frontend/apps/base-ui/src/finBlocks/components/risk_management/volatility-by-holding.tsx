import React from 'react';

// Data interface for Volatility Breakdown by Holding
interface VolatilityByHoldingProps {
  title?: string;
  data: any;
  loading?: boolean;
  error?: string;
}


// Sample data for development
export const SAMPLE_DATA: VolatilityByHoldingProps = {
  title: 'Volatility Breakdown by Holding',
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
 * Volatility Breakdown by Holding finBlock
 *
 * @description Individual stock volatility ranked from highest to lowest
 * @blockType bar-chart
 * @concepts volatility, risk concentration
 * @mcpRequired get_positions, get_technical_indicator
 */
export const VolatilityByHolding: React.FC<VolatilityByHoldingProps> = ({
  title = 'Volatility Breakdown by Holding',
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
    <div className="finblock volatility-by-holding rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 font-semibold text-gray-800">{title}</h3>
      {/* Block Type: bar-chart */}
      <pre className="max-h-96 overflow-auto rounded bg-gray-50 p-3 text-xs">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
};

export default VolatilityByHolding;
