import React from 'react';

// Data interface for Income vs Withdrawal Needs
interface IncomeVsExpensesProps {
  title?: string;
  data: any;
  loading?: boolean;
  error?: string;
}


// Sample data for development
export const SAMPLE_DATA: IncomeVsExpensesProps = {
  title: 'Income vs Withdrawal Needs',
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
 * Income vs Withdrawal Needs finBlock
 *
 * @description Annual dividend income vs target withdrawal for retirement
 * @blockType bar-chart
 * @concepts income planning, retirement
 * @mcpRequired get_dividends, get_positions
 */
export const IncomeVsExpenses: React.FC<IncomeVsExpensesProps> = ({
  title = 'Income vs Withdrawal Needs',
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
    <div className="finblock income-vs-expenses rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 font-semibold text-gray-800">{title}</h3>
      {/* Block Type: bar-chart */}
      <pre className="max-h-96 overflow-auto rounded bg-gray-50 p-3 text-xs">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
};

export default IncomeVsExpenses;
