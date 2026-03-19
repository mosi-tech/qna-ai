import React from 'react';

// Data interface for Asset Class Allocation
interface AssetClassAllocationProps {
  title?: string;
  data: any;
  loading?: boolean;
  error?: string;
}


// Sample data for development
export const SAMPLE_DATA: AssetClassAllocationProps = {
  title: 'Asset Class Allocation',
  data: {
    "data": [
        {
            "name": "Technology",
            "value": 35
        },
        {
            "name": "Healthcare",
            "value": 20
        },
        {
            "name": "Finance",
            "value": 25
        },
        {
            "name": "Other",
            "value": 20
        }
    ]
},
  loading: false,
  error: undefined,
};

/**
 * Asset Class Allocation finBlock
 *
 * @description Breakdown of stocks vs ETFs vs bonds vs cash
 * @blockType donut-chart
 * @concepts asset allocation, diversification, portfolio structure
 * @mcpRequired get_positions
 */
export const AssetClassAllocation: React.FC<AssetClassAllocationProps> = ({
  title = 'Asset Class Allocation',
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
    <div className="finblock asset-class-allocation rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 font-semibold text-gray-800">{title}</h3>
      {/* Block Type: donut-chart */}
      <pre className="max-h-96 overflow-auto rounded bg-gray-50 p-3 text-xs">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
};

export default AssetClassAllocation;
