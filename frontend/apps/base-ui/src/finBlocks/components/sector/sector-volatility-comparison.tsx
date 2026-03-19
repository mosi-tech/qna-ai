import React from 'react';

// Data interface for Volatility by Sector
interface SectorVolatilityComparisonProps {
  title?: string;
  data: any;
  loading?: boolean;
  error?: string;
}


// Sample data for development
export const SAMPLE_DATA: SectorVolatilityComparisonProps = {
  title: 'Volatility by Sector',
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
 * Volatility by Sector finBlock
 *
 * @description Risk level (volatility) for each sector in portfolio
 * @blockType bar-chart
 * @concepts sector risk, defensive vs growth
 * @mcpRequired get_positions, get_technical_indicator
 */
export const SectorVolatilityComparison: React.FC<SectorVolatilityComparisonProps> = ({
  title = 'Volatility by Sector',
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
    <div className="finblock sector-volatility-comparison rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 font-semibold text-gray-800">{title}</h3>
      {/* Block Type: bar-chart */}
      <pre className="max-h-96 overflow-auto rounded bg-gray-50 p-3 text-xs">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
};

export default SectorVolatilityComparison;
