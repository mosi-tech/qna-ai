import React from 'react';

// Data interface for SEC Filing Monitoring
interface SecFilingAlertsProps {
  title?: string;
  data: any;
  loading?: boolean;
  error?: string;
}


// Sample data for development
export const SAMPLE_DATA: SecFilingAlertsProps = {
  title: 'SEC Filing Monitoring',
  data: {
    "rows": [
        {
            "Symbol": "AAPL",
            "Shares": 100,
            "AvgCost": 150,
            "MarketValue": 17000,
            "PL": 2000,
            "PL%": 13.3
        },
        {
            "Symbol": "MSFT",
            "Shares": 50,
            "AvgCost": 300,
            "MarketValue": 16000,
            "PL": 1000,
            "PL%": 6.7
        }
    ],
    "columns": [
        "Symbol",
        "Shares",
        "Avg Cost",
        "Market Value",
        "P&L",
        "P&L %"
    ]
},
  loading: false,
  error: undefined,
};

/**
 * SEC Filing Monitoring finBlock
 *
 * @description Recent 10-K, 10-Q, 8-K filings for holdings
 * @blockType table
 * @concepts transparency, insider activity
 * @mcpRequired get_fundamentals
 */
export const SecFilingAlerts: React.FC<SecFilingAlertsProps> = ({
  title = 'SEC Filing Monitoring',
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
    <div className="finblock sec-filing-alerts rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 font-semibold text-gray-800">{title}</h3>
      {/* Block Type: table */}
      <pre className="max-h-96 overflow-auto rounded bg-gray-50 p-3 text-xs">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
};

export default SecFilingAlerts;
