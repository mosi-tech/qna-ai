import React from 'react';

// Data interface for Price History with Moving Averages
interface PriceHistoryWithMaProps {
  title?: string;
  data: any;
  loading?: boolean;
  error?: string;
}


// Sample data for development
export const SAMPLE_DATA: PriceHistoryWithMaProps = {
  title: 'Price History with Moving Averages',
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
 * Price History with Moving Averages finBlock
 *
 * @description 12-month price history with 50-day and 200-day moving averages
 * @blockType line-chart
 * @concepts trend, support/resistance, momentum
 * @mcpRequired get_historical_data
 */
export const PriceHistoryWithMa: React.FC<PriceHistoryWithMaProps> = ({
  title = 'Price History with Moving Averages',
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
    <div className="finblock price-history-with-ma rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 font-semibold text-gray-800">{title}</h3>
      {/* Block Type: line-chart */}
      <pre className="max-h-96 overflow-auto rounded bg-gray-50 p-3 text-xs">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
};

export default PriceHistoryWithMa;
