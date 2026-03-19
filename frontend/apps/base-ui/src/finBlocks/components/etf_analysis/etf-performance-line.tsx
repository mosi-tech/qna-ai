import React from 'react';

// Data interface for ETF Performance Comparison
interface EtfPerformanceLineProps {
  title?: string;
  data: any;
  loading?: boolean;
  error?: string;
}


// Sample data for development
export const SAMPLE_DATA: EtfPerformanceLineProps = {
  title: 'ETF Performance Comparison',
  data: {
    "data": [
        {
            "date": "2024-01-01",
            "Portfolio": 100,
            "Benchmark": 100
        },
        {
            "date": "2024-02-01",
            "Portfolio": 105,
            "Benchmark": 102
        },
        {
            "date": "2024-03-01",
            "Portfolio": 110,
            "Benchmark": 104
        }
    ],
    "categories": [
        "Portfolio",
        "Benchmark"
    ],
    "summary": [
        {
            "name": "YTD Return",
            "value": 10
        }
    ]
},
  loading: false,
  error: undefined,
};

/**
 * ETF Performance Comparison finBlock
 *
 * @description Cumulative returns comparison for multiple ETFs over time
 * @blockType line-chart
 * @concepts performance, returns
 * @mcpRequired get_historical_data
 */
export const EtfPerformanceLine: React.FC<EtfPerformanceLineProps> = ({
  title = 'ETF Performance Comparison',
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
    <div className="finblock etf-performance-line rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 font-semibold text-gray-800">{title}</h3>
      {/* Block Type: line-chart */}
      <pre className="max-h-96 overflow-auto rounded bg-gray-50 p-3 text-xs">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
};

export default EtfPerformanceLine;
