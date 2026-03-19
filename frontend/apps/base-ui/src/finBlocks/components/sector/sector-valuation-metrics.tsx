import React from 'react';

// Data interface for Average Valuation by Sector
interface SectorValuationMetricsProps {
  title?: string;
  data: any;
  loading?: boolean;
  error?: string;
}


// Sample data for development
export const SAMPLE_DATA: SectorValuationMetricsProps = {
  title: 'Average Valuation by Sector',
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
 * Average Valuation by Sector finBlock
 *
 * @description Average P/E and P/B ratios for sectors in portfolio
 * @blockType bar-list
 * @concepts valuation, growth vs value
 * @mcpRequired get_positions, get_fundamentals
 */
export const SectorValuationMetrics: React.FC<SectorValuationMetricsProps> = ({
  title = 'Average Valuation by Sector',
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
    <div className="finblock sector-valuation-metrics rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 font-semibold text-gray-800">{title}</h3>
      {/* Block Type: bar-list */}
      <pre className="max-h-96 overflow-auto rounded bg-gray-50 p-3 text-xs">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
};

export default SectorValuationMetrics;
