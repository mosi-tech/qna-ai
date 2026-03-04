'use client';

import { useState } from 'react';

interface IndicatorBlockProps {
  id: string;
  indicatorA: string;
  operator: string;
  indicatorB: string;
  onIndicatorAChange: (value: string) => void;
  onOperatorChange: (value: string) => void;
  onIndicatorBChange: (value: string) => void;
  onRemove: () => void;
  canRemove?: boolean;
}

const TECHNICAL_INDICATORS = [
  { 
    id: 'sma', 
    name: 'SMA - Simple Moving Average', 
    params: [{ name: 'Period', defaultValue: 20, type: 'number' }] 
  },
  { 
    id: 'ema', 
    name: 'EMA - Exponential Moving Average', 
    params: [{ name: 'Period', defaultValue: 20, type: 'number' }] 
  },
  { 
    id: 'rsi', 
    name: 'RSI - Relative Strength Index', 
    params: [{ name: 'Period', defaultValue: 14, type: 'number' }] 
  },
  { 
    id: 'macd', 
    name: 'MACD - Moving Average Convergence Divergence', 
    params: [
      { name: 'Fast', defaultValue: 12, type: 'number' },
      { name: 'Slow', defaultValue: 26, type: 'number' },
      { name: 'Signal', defaultValue: 9, type: 'number' }
    ] 
  },
  { 
    id: 'bb', 
    name: 'Bollinger Bands', 
    params: [
      { name: 'Period', defaultValue: 20, type: 'number' },
      { name: 'Std Dev', defaultValue: 2, type: 'number' }
    ] 
  },
  { 
    id: 'stoch', 
    name: 'Stochastic Oscillator', 
    params: [
      { name: '%K Period', defaultValue: 14, type: 'number' },
      { name: '%D Period', defaultValue: 3, type: 'number' }
    ] 
  },
  { 
    id: 'atr', 
    name: 'ATR - Average True Range', 
    params: [{ name: 'Period', defaultValue: 14, type: 'number' }] 
  },
  { 
    id: 'adx', 
    name: 'ADX - Average Directional Index', 
    params: [{ name: 'Period', defaultValue: 14, type: 'number' }] 
  },
  { 
    id: 'cci', 
    name: 'CCI - Commodity Channel Index', 
    params: [{ name: 'Period', defaultValue: 20, type: 'number' }] 
  },
  { 
    id: 'williams', 
    name: 'Williams %R', 
    params: [{ name: 'Period', defaultValue: 14, type: 'number' }] 
  },
  { 
    id: 'price', 
    name: 'Price - Raw Price Data', 
    params: [] 
  }
];

const OPERATORS = [
  { value: '>', label: 'Greater than (>)' },
  { value: '<', label: 'Less than (<)' },
  { value: '>=', label: 'Greater than or equal (≥)' },
  { value: '<=', label: 'Less than or equal (≤)' },
  { value: '==', label: 'Equal to (=)' },
  { value: 'crosses_above', label: 'Crosses above' },
  { value: 'crosses_below', label: 'Crosses below' }
];

// Custom Indicator Dropdown Component
function IndicatorDropdown({ 
  value, 
  onChange, 
  placeholder = "Select Indicator" 
}: { 
  value: string; 
  onChange: (value: string) => void; 
  placeholder?: string; 
}) {
  const [isOpen, setIsOpen] = useState(false);
  // const [selectedIndicator, setSelectedIndicator] = useState<{
  //   id: string;
  //   name: string;
  //   params: Array<{ name: string; defaultValue: number; type: string }>;
  // } | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredIndicators = TECHNICAL_INDICATORS.filter(indicator =>
    indicator.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const selectIndicator = (indicator: typeof TECHNICAL_INDICATORS[0]) => {
    // setSelectedIndicator(indicator);
    // Format the indicator with its default parameters
    const paramString = indicator.params.length > 0 
      ? `(${indicator.params.map(p => p.defaultValue).join(',')})` 
      : '';
    const displayValue = `${indicator.name.split(' - ')[0]}${paramString}`;
    onChange(displayValue);
    setIsOpen(false);
    setSearchTerm('');
  };

  return (
    <div className="relative flex-1">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm text-left bg-white hover:bg-gray-50"
      >
        {value || placeholder}
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 right-0 bg-white border border-gray-300 rounded-md shadow-lg z-20 max-h-80 overflow-hidden">
          {/* Search */}
          <div className="p-3 border-b border-gray-200">
            <input
              type="text"
              placeholder="Search indicators..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
              autoFocus
            />
          </div>

          {/* Indicator List */}
          <div className="max-h-60 overflow-y-auto">
            <div className="p-2 space-y-1">
              {filteredIndicators.map(indicator => (
                <button
                  key={indicator.id}
                  className="w-full px-3 py-3 text-left hover:bg-gray-100 rounded text-sm border-b border-gray-100 last:border-b-0"
                  onClick={() => selectIndicator(indicator)}
                >
                  <div className="font-medium text-gray-900">{indicator.name}</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {indicator.params.length > 0 ? (
                      <span>Parameters: {indicator.params.map(p => `${p.name} (${p.defaultValue})`).join(', ')}</span>
                    ) : (
                      <span>No parameters required</span>
                    )}
                  </div>
                  {/* Parameter Inputs */}
                  {indicator.params.length > 0 && (
                    <div className="mt-2 grid grid-cols-2 gap-2">
                      {indicator.params.map((param, idx: number) => (
                        <div key={idx} className="text-xs">
                          <span className="text-gray-600">{param.name}:</span>
                          <input
                            type="number"
                            defaultValue={param.defaultValue}
                            className="ml-1 w-12 px-1 py-0.5 border border-gray-300 rounded text-xs"
                            onClick={(e) => e.stopPropagation()}
                          />
                        </div>
                      ))}
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Close on outside click */}
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setIsOpen(false)}
          />
        </div>
      )}
    </div>
  );
}

export default function IndicatorBlock({
  indicatorA,
  operator,
  indicatorB,
  onIndicatorAChange,
  onOperatorChange,
  onIndicatorBChange,
  onRemove,
  canRemove = true
}: IndicatorBlockProps) {
  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 flex items-center gap-3">
      {/* Indicator A */}
      <IndicatorDropdown
        value={indicatorA}
        onChange={onIndicatorAChange}
        placeholder="Select Indicator A"
      />

      {/* Operator */}
      <select
        value={operator}
        onChange={(e) => onOperatorChange(e.target.value)}
        className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm min-w-[140px]"
      >
        <option value="">Operator</option>
        {OPERATORS.map((op) => (
          <option key={op.value} value={op.value}>
            {op.label}
          </option>
        ))}
      </select>

      {/* Indicator B */}
      <IndicatorDropdown
        value={indicatorB}
        onChange={onIndicatorBChange}
        placeholder="Select Indicator B"
      />

      {/* Remove Button */}
      {canRemove && (
        <button
          onClick={onRemove}
          className="p-2 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-md transition-colors"
          title="Remove condition"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  );
}