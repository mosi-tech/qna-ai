import React from 'react';

// Data interface for Valuation vs Sector & Market
interface ValuationComparisonProps {
  title?: string;
  data: any;
  loading?: boolean;
  error?: string;
}


// Sample data for development
export const SAMPLE_DATA: ValuationComparisonProps = {
  title: 'Valuation vs Sector & Market',
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
 * Valuation vs Sector & Market finBlock
 *
 * @description Compare stock P/E, P/B, dividend yield to sector average and S&P 500
 * @blockType bar-chart
 * @concepts relative valuation, value vs growth
 * @mcpRequired get_fundamentals, get_historical_data
 */
export const ValuationComparison: React.FC<ValuationComparisonProps> = ({
  title = 'Valuation vs Sector & Market',
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
    <div className="finblock valuation-comparison rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 font-semibold text-gray-800">{title}</h3>
      {/* Block Type: bar-chart */}
      <pre className="max-h-96 overflow-auto rounded bg-gray-50 p-3 text-xs">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
};

export default ValuationComparison;
