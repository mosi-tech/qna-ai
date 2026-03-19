import React from 'react';

// Data interface for Correlation Matrix
interface CorrelationMatrixProps {
  title?: string;
  data: any;
  loading?: boolean;
  error?: string;
}


// Sample data for development
export const SAMPLE_DATA: CorrelationMatrixProps = {
  title: 'Correlation Matrix',
  data: {
    "data": [
        [
            1.0,
            0.6,
            0.4
        ],
        [
            0.6,
            1.0,
            0.5
        ],
        [
            0.4,
            0.5,
            1.0
        ]
    ],
    "labels": [
        "AAPL",
        "MSFT",
        "GOOGL"
    ]
},
  loading: false,
  error: undefined,
};

/**
 * Correlation Matrix finBlock
 *
 * @description Correlation between top holdings showing diversification benefits
 * @blockType heatmap
 * @concepts correlation, diversification
 * @mcpRequired get_positions, get_historical_data
 */
export const CorrelationMatrix: React.FC<CorrelationMatrixProps> = ({
  title = 'Correlation Matrix',
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
    <div className="finblock correlation-matrix rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 font-semibold text-gray-800">{title}</h3>
      {/* Block Type: heatmap */}
      <pre className="max-h-96 overflow-auto rounded bg-gray-50 p-3 text-xs">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
};

export default CorrelationMatrix;
