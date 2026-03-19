import React from 'react';

// Data interface for Long-term vs Short-term Gains Tax Analysis
interface LongTermVsShorttermGainsProps {
  title?: string;
  data: any;
  loading?: boolean;
  error?: string;
}


// Sample data for development
export const SAMPLE_DATA: LongTermVsShorttermGainsProps = {
  title: 'Long-term vs Short-term Gains Tax Analysis',
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
 * Long-term vs Short-term Gains Tax Analysis finBlock
 *
 * @description Unrealized gains categorized by holding period (tax efficiency)
 * @blockType bar-chart
 * @concepts tax brackets, holding periods
 * @mcpRequired get_positions
 */
export const LongTermVsShorttermGains: React.FC<LongTermVsShorttermGainsProps> = ({
  title = 'Long-term vs Short-term Gains Tax Analysis',
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
    <div className="finblock long-term-vs-shortterm-gains rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 font-semibold text-gray-800">{title}</h3>
      {/* Block Type: bar-chart */}
      <pre className="max-h-96 overflow-auto rounded bg-gray-50 p-3 text-xs">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
};

export default LongTermVsShorttermGains;
