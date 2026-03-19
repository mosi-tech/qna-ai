import React from 'react';

// Data interface for Sector Rebalancing Opportunities
interface SectorRebalancingRecommendationProps {
  title?: string;
  data: any;
  loading?: boolean;
  error?: string;
}


// Sample data for development
export const SAMPLE_DATA: SectorRebalancingRecommendationProps = {
  title: 'Sector Rebalancing Opportunities',
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
 * Sector Rebalancing Opportunities finBlock
 *
 * @description Sectors over/underweight vs target allocation
 * @blockType bar-list
 * @concepts rebalancing, target allocation
 * @mcpRequired get_positions
 */
export const SectorRebalancingRecommendation: React.FC<SectorRebalancingRecommendationProps> = ({
  title = 'Sector Rebalancing Opportunities',
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
    <div className="finblock sector-rebalancing-recommendation rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 font-semibold text-gray-800">{title}</h3>
      {/* Block Type: bar-list */}
      <pre className="max-h-96 overflow-auto rounded bg-gray-50 p-3 text-xs">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
};

export default SectorRebalancingRecommendation;
