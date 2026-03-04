'use client';

import { useState } from 'react';

interface SettingsPanelProps {
  initialInvestment: number;
  startDate: string;
  endDate: string;
  stopLoss: number;
  takeProfit: number;
  slippage: number;
  transactionCost: number;
  onInitialInvestmentChange: (value: number) => void;
  onStartDateChange: (value: string) => void;
  onEndDateChange: (value: string) => void;
  onStopLossChange: (value: number) => void;
  onTakeProfitChange: (value: number) => void;
  onSlippageChange: (value: number) => void;
  onTransactionCostChange: (value: number) => void;
}

export default function SettingsPanel({
  initialInvestment,
  startDate,
  endDate,
  stopLoss,
  takeProfit,
  slippage,
  transactionCost,
  onInitialInvestmentChange,
  onStartDateChange,
  onEndDateChange,
  onStopLossChange,
  onTakeProfitChange,
  onSlippageChange,
  onTransactionCostChange
}: SettingsPanelProps) {
  const [showAdvanced, setShowAdvanced] = useState(false);

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Backtest Settings</h3>

      {/* Basic Settings */}
      <div className="space-y-4">
        {/* Initial Investment */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Initial Investment
          </label>
          <div className="relative">
            <span className="absolute left-3 top-2 text-gray-500">$</span>
            <input
              type="number"
              value={initialInvestment}
              onChange={(e) => onInitialInvestmentChange(Number(e.target.value))}
              className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              min="1000"
              step="1000"
            />
          </div>
        </div>

        {/* Date Range */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Start Date
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => onStartDateChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              End Date
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => onEndDateChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Risk Management */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Stop Loss (%)
            </label>
            <input
              type="number"
              value={stopLoss}
              onChange={(e) => onStopLossChange(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              min="0"
              max="50"
              step="0.5"
              placeholder="5.0"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Take Profit (%)
            </label>
            <input
              type="number"
              value={takeProfit}
              onChange={(e) => onTakeProfitChange(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              min="0"
              max="100"
              step="0.5"
              placeholder="10.0"
            />
          </div>
        </div>

        {/* Advanced Settings Toggle */}
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800 transition-colors"
        >
          <span>{showAdvanced ? 'Hide' : 'Show'} Advanced Settings</span>
          <svg
            className={`w-4 h-4 transition-transform ${showAdvanced ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {/* Advanced Settings */}
        {showAdvanced && (
          <div className="border-t border-gray-200 pt-4 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Slippage (%)
                </label>
                <input
                  type="number"
                  value={slippage}
                  onChange={(e) => onSlippageChange(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  min="0"
                  max="5"
                  step="0.01"
                  placeholder="0.05"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Execution price difference vs market price
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Transaction Cost ($)
                </label>
                <input
                  type="number"
                  value={transactionCost}
                  onChange={(e) => onTransactionCostChange(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  min="0"
                  max="50"
                  step="0.01"
                  placeholder="1.00"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Commission per trade
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Settings Summary */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h5 className="text-sm font-medium text-gray-900 mb-2">Settings Summary</h5>
        <div className="text-sm text-gray-600 space-y-1">
          <p>Investment: ${initialInvestment.toLocaleString()}</p>
          <p>Period: {startDate} to {endDate}</p>
          <p>Risk: {stopLoss}% stop loss, {takeProfit}% take profit</p>
          {showAdvanced && (
            <p>Costs: {slippage}% slippage, ${transactionCost} per trade</p>
          )}
        </div>
      </div>
    </div>
  );
}