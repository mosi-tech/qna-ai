'use client';

import { useState } from 'react';
import SymbolSelector from './SymbolSelector';
import StrategyBuilder from './StrategyBuilder';
import SettingsPanel from './SettingsPanel';
import BacktestResults from '../output/BacktestResults';

interface Condition {
  id: string;
  indicatorA: string;
  operator: string;
  indicatorB: string;
}

const generateId = () => Math.random().toString(36).substr(2, 9);

// Mock data generator for demo
const generateMockResults = (symbols: string[]) => {
  const mockTrades = [
    {
      id: generateId(),
      symbol: symbols[0] || 'AAPL',
      type: 'buy' as const,
      date: '2023-01-15',
      price: 150.25,
      quantity: 10,
      reason: 'SMA(10) > SMA(20)'
    },
    {
      id: generateId(),
      symbol: symbols[0] || 'AAPL',
      type: 'sell' as const,
      date: '2023-02-18',
      price: 165.80,
      quantity: 10,
      pnl: 155.50,
      reason: 'Take profit triggered'
    },
    {
      id: generateId(),
      symbol: symbols[1] || 'MSFT',
      type: 'buy' as const,
      date: '2023-02-20',
      price: 245.60,
      quantity: 6,
      reason: 'RSI < 30'
    },
    {
      id: generateId(),
      symbol: symbols[1] || 'MSFT',
      type: 'sell' as const,
      date: '2023-03-25',
      price: 255.30,
      quantity: 6,
      pnl: 58.20,
      reason: 'SMA(10) < SMA(20)'
    }
  ];

  return {
    totalReturn: 18.7,
    annualizedReturn: 15.3,
    sharpeRatio: 1.42,
    maxDrawdown: -8.2,
    winRate: 67.5,
    totalTrades: mockTrades.length,
    avgTradeReturn: 2.8,
    trades: mockTrades
  };
};

export default function Backtester() {
  // State for all components
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

  // Results state
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<{
    totalReturn: number;
    annualizedReturn: number;
    sharpeRatio: number;
    maxDrawdown: number;
    winRate: number;
    totalTrades: number;
    avgTradeReturn: number;
    trades: Array<{
      id: string;
      symbol: string;
      type: 'buy' | 'sell';
      date: string;
      price: number;
      quantity: number;
      pnl?: number;
      reason: string;
    }>;
  } | null>(null);

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

  const runBacktest = async () => {
    if (!canRunBacktest()) return;

    setIsRunning(true);
    setResults(null);

    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Generate mock results
    const mockResults = generateMockResults(selectedSymbols);
    setResults(mockResults);
    setIsRunning(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Strategy Backtester</h1>
          <p className="text-gray-600">
            Build and test your trading strategies with historical data
          </p>
        </div>

        {/* Main Layout */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {/* Left Column - Configuration */}
          <div className="xl:col-span-1 space-y-6">
            <SymbolSelector
              selectedSymbols={selectedSymbols}
              onSymbolsChange={setSelectedSymbols}
            />

            <StrategyBuilder
              entryConditions={entryConditions}
              exitConditions={exitConditions}
              onEntryConditionsChange={setEntryConditions}
              onExitConditionsChange={setExitConditions}
            />

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

            {/* Run Backtest Button */}
            <div className="sticky bottom-4">
              <button
                onClick={runBacktest}
                disabled={!canRunBacktest() || isRunning}
                className={`w-full py-3 px-6 rounded-lg font-medium text-white transition-colors ${
                  canRunBacktest() && !isRunning
                    ? 'bg-blue-600 hover:bg-blue-700'
                    : 'bg-gray-400 cursor-not-allowed'
                }`}
              >
                {isRunning ? (
                  <span className="flex items-center justify-center gap-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Running Backtest...
                  </span>
                ) : (
                  '🚀 Run Backtest'
                )}
              </button>
            </div>
          </div>

          {/* Right Column - Results */}
          <div className="xl:col-span-2">
            <BacktestResults
              isRunning={isRunning}
              results={results}
            />
          </div>
        </div>
      </div>
    </div>
  );
}