import React from 'react';

// Data interface for Tax-Loss Harvesting Candidates
interface TaxLossHarvestingOpportunitiesProps {
  title?: string;
  data: any;
  loading?: boolean;
  error?: string;
}


// Sample data for development
export const SAMPLE_DATA: TaxLossHarvestingOpportunitiesProps = {
  title: 'Tax-Loss Harvesting Candidates',
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
 * Tax-Loss Harvesting Candidates finBlock
 *
 * @description Holdings with unrealized losses available for tax-loss harvesting
 * @blockType table
 * @concepts tax efficiency, loss harvesting
 * @mcpRequired get_positions
 */
export const TaxLossHarvestingOpportunities: React.FC<TaxLossHarvestingOpportunitiesProps> = ({
  title = 'Tax-Loss Harvesting Candidates',
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
    <div className="finblock tax-loss-harvesting-opportunities rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 font-semibold text-gray-800">{title}</h3>
      {/* Block Type: table */}
      <pre className="max-h-96 overflow-auto rounded bg-gray-50 p-3 text-xs">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
};

export default TaxLossHarvestingOpportunities;
