import React from 'react';

// Data interface for Top Holdings Recent Price Action
interface PriceMovementsSparkProps {
  title?: string;
  data: any;
  loading?: boolean;
  error?: string;
}


// Sample data for development
export const SAMPLE_DATA: PriceMovementsSparkProps = {
  title: 'Top Holdings Recent Price Action',
  data: {
    "data": [
        {
            "date": "2024-03-01",
            "AAPL": 150,
            "MSFT": 300
        },
        {
            "date": "2024-03-02",
            "AAPL": 152,
            "MSFT": 302
        }
    ],
    "items": [
        {
            "id": "AAPL",
            "name": "Apple",
            "value": "152.50",
            "change": "+1.7%",
            "changeType": "positive"
        }
    ]
},
  loading: false,
  error: undefined,
};

/**
 * Top Holdings Recent Price Action finBlock
 *
 * @description Last 2 weeks of price movements for top 5-10 holdings with sparklines
 * @blockType spark-chart
 * @concepts momentum, volatility, price trends
 * @mcpRequired get_historical_data, get_real_time_data
 */
export const PriceMovementsSpark: React.FC<PriceMovementsSparkProps> = ({
  title = 'Top Holdings Recent Price Action',
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
    <div className="finblock price-movements-spark rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 font-semibold text-gray-800">{title}</h3>
      {/* Block Type: spark-chart */}
      <pre className="max-h-96 overflow-auto rounded bg-gray-50 p-3 text-xs">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
};

export default PriceMovementsSpark;
