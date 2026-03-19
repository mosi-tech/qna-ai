import React from 'react';

// Data interface for RSI Overbought/Oversold Signals
interface RsiOverboughtOversoldProps {
  title?: string;
  data: any;
  loading?: boolean;
  error?: string;
}


// Sample data for development
export const SAMPLE_DATA: RsiOverboughtOversoldProps = {
  title: 'RSI Overbought/Oversold Signals',
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
 * RSI Overbought/Oversold Signals finBlock
 *
 * @description Holdings with RSI > 70 (overbought) or < 30 (oversold)
 * @blockType bar-list
 * @concepts momentum, entry/exit signals
 * @mcpRequired get_technical_indicator
 */
export const RsiOverboughtOversold: React.FC<RsiOverboughtOversoldProps> = ({
  title = 'RSI Overbought/Oversold Signals',
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
    <div className="finblock rsi-overbought-oversold rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 font-semibold text-gray-800">{title}</h3>
      {/* Block Type: bar-list */}
      <pre className="max-h-96 overflow-auto rounded bg-gray-50 p-3 text-xs">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
};

export default RsiOverboughtOversold;
