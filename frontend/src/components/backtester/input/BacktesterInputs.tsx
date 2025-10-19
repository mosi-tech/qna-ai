'use client';

import { useState } from 'react';
import SymbolSelector from './SymbolSelector';
import StrategyBuilder from './StrategyBuilder';
import SettingsPanel from './SettingsPanel';

interface Condition {
  id: string;
  indicatorA: string;
  operator: string;
  indicatorB: string;
}

const generateId = () => Math.random().toString(36).substr(2, 9);

export default function BacktesterInputs() {
  // State for all input components
  const [selectedSymbols, setSelectedSymbols] = useState<string[]>(['AAPL']);
  const [entryConditions, setEntryConditions] = useState<Condition[]>([
    {
      id: generateId(),
      indicatorA: 'SMA(10)',
      operator: 'crosses_above',
      indicatorB: 'SMA(20)'
    }
  ]);
  const [exitConditions, setExitConditions] = useState<Condition[]>([
    {
      id: generateId(),
      indicatorA: 'SMA(10)',
      operator: 'crosses_below',
      indicatorB: 'SMA(20)'
    }
  ]);

  // Settings
  const [initialInvestment, setInitialInvestment] = useState(100000);
  const [startDate, setStartDate] = useState('2023-01-01');
  const [endDate, setEndDate] = useState('2024-01-01');
  const [stopLoss, setStopLoss] = useState(5.0);
  const [takeProfit, setTakeProfit] = useState(10.0);
  const [slippage, setSlippage] = useState(0.05);
  const [transactionCost, setTransactionCost] = useState(1.0);

  const canRunBacktest = () => {
    return (
      selectedSymbols.length > 0 &&
      entryConditions.some(c => c.indicatorA && c.operator && c.indicatorB) &&
      exitConditions.some(c => c.indicatorA && c.operator && c.indicatorB) &&
      startDate &&
      endDate &&
      initialInvestment > 0
    );
  };

  const handleRunBacktest = () => {
    console.log('Running backtest with:', {
      symbols: selectedSymbols,
      entryConditions,
      exitConditions,
      settings: {
        initialInvestment,
        startDate,
        endDate,
        stopLoss,
        takeProfit,
        slippage,
        transactionCost
      }
    });
    // This would trigger the actual backtesting and switch to results view
  };

  return (
    <div className="space-y-6">
      {/* Top Section - Symbol Search */}
      <SymbolSelector
        selectedSymbols={selectedSymbols}
        onSymbolsChange={setSelectedSymbols}
      />

      {/* Main Layout - Indicator Builder (Left) + Strategy Panel (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column - Indicator Block Builder */}
        <StrategyBuilder
          entryConditions={entryConditions}
          exitConditions={exitConditions}
          onEntryConditionsChange={setEntryConditions}
          onExitConditionsChange={setExitConditions}
        />

        {/* Right Column - Strategy Panel (Settings) */}
        <SettingsPanel
          initialInvestment={initialInvestment}
          startDate={startDate}
          endDate={endDate}
          stopLoss={stopLoss}
          takeProfit={takeProfit}
          slippage={slippage}
          transactionCost={transactionCost}
          onInitialInvestmentChange={setInitialInvestment}
          onStartDateChange={setStartDate}
          onEndDateChange={setEndDate}
          onStopLossChange={setStopLoss}
          onTakeProfitChange={setTakeProfit}
          onSlippageChange={setSlippage}
          onTransactionCostChange={setTransactionCost}
        />
      </div>

      {/* Strategy Summary */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="text-sm font-medium text-gray-900 mb-3">Strategy Summary</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Symbols:</span>
            <div className="font-medium">{selectedSymbols.join(', ')}</div>
          </div>
          <div>
            <span className="text-gray-600">Entry Conditions:</span>
            <div className="font-medium">{entryConditions.length}</div>
          </div>
          <div>
            <span className="text-gray-600">Exit Conditions:</span>
            <div className="font-medium">{exitConditions.length}</div>
          </div>
          <div>
            <span className="text-gray-600">Investment:</span>
            <div className="font-medium">${initialInvestment.toLocaleString()}</div>
          </div>
        </div>
      </div>

      {/* Run Backtest Button */}
      <div className="flex justify-center">
        <button
          onClick={handleRunBacktest}
          disabled={!canRunBacktest()}
          className={`px-8 py-3 rounded-lg font-medium text-white transition-colors ${
            canRunBacktest()
              ? 'bg-blue-600 hover:bg-blue-700'
              : 'bg-gray-400 cursor-not-allowed'
          }`}
        >
          🚀 Run Backtest
        </button>
      </div>
    </div>
  );
}