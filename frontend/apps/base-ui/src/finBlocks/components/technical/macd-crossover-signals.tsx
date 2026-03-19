import React from 'react';

// Data interface for MACD Trend Following Signals
interface MacdCrossoverSignalsProps {
  title?: string;
  data: any;
  loading?: boolean;
  error?: string;
}


// Sample data for development
export const SAMPLE_DATA: MacdCrossoverSignalsProps = {
  title: 'MACD Trend Following Signals',
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
 * MACD Trend Following Signals finBlock
 *
 * @description Holdings with MACD crossovers (bullish/bearish)
 * @blockType bar-list
 * @concepts trend following, momentum
 * @mcpRequired get_technical_indicator
 */
export const MacdCrossoverSignals: React.FC<MacdCrossoverSignalsProps> = ({
  title = 'MACD Trend Following Signals',
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
    <div className="finblock macd-crossover-signals rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 font-semibold text-gray-800">{title}</h3>
      {/* Block Type: bar-list */}
      <pre className="max-h-96 overflow-auto rounded bg-gray-50 p-3 text-xs">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
};

export default MacdCrossoverSignals;
