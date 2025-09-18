'use client';

import { useState } from 'react';

interface SymbolSelectorProps {
  selectedSymbols: string[];
  onSymbolsChange: (symbols: string[]) => void;
}

const POPULAR_SYMBOLS = [
  'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX',
  'SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'ARKK', 'XLF', 'XLK'
];

export default function SymbolSelector({ selectedSymbols, onSymbolsChange }: SymbolSelectorProps) {
  const [inputValue, setInputValue] = useState('');

  const addSymbol = (symbol: string) => {
    const upperSymbol = symbol.toUpperCase();
    if (upperSymbol && !selectedSymbols.includes(upperSymbol)) {
      onSymbolsChange([...selectedSymbols, upperSymbol]);
    }
  };

  const removeSymbol = (symbol: string) => {
    onSymbolsChange(selectedSymbols.filter(s => s !== symbol));
  };

  const handleInputKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addSymbol(inputValue);
      setInputValue('');
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Select Symbols</h3>
      
      {/* Symbol Input */}
      <div className="mb-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleInputKeyDown}
            placeholder="Enter symbol (e.g., AAPL)"
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={() => {
              addSymbol(inputValue);
              setInputValue('');
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Add
          </button>
        </div>
      </div>

      {/* Selected Symbols */}
      {selectedSymbols.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Selected Symbols</h4>
          <div className="flex flex-wrap gap-2">
            {selectedSymbols.map((symbol) => (
              <span
                key={symbol}
                className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
              >
                {symbol}
                <button
                  onClick={() => removeSymbol(symbol)}
                  className="ml-2 text-blue-600 hover:text-blue-800"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Popular Symbols */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 mb-2">Popular Symbols</h4>
        <div className="grid grid-cols-4 sm:grid-cols-6 lg:grid-cols-8 gap-2">
          {POPULAR_SYMBOLS.map((symbol) => (
            <button
              key={symbol}
              onClick={() => addSymbol(symbol)}
              disabled={selectedSymbols.includes(symbol)}
              className={`px-3 py-1 text-sm rounded-md transition-colors ${
                selectedSymbols.includes(symbol)
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-50 text-gray-700 hover:bg-gray-100 hover:text-gray-900'
              }`}
            >
              {symbol}
            </button>
          ))}
        </div>
      </div>

      {/* Symbol Count Info */}
      <div className="mt-4 text-sm text-gray-500">
        {selectedSymbols.length === 0 && "Select at least one symbol to get started"}
        {selectedSymbols.length === 1 && "1 symbol selected"}
        {selectedSymbols.length > 1 && `${selectedSymbols.length} symbols selected`}
      </div>
    </div>
  );
}