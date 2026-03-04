'use client';

import { useState, useEffect } from 'react';
import { PredictedCategory } from './types';
import AnalysisSelector from './AnalysisSelector';
import AnalysisConfigurator from './AnalysisConfigurator';

interface AutocompleteInputProps {
  input: string;
  setInput: (value: string) => void;
  onSubmit: (question: string) => void;
  placeholder?: string;
  className?: string;
}

export default function AutocompleteInput({
  input,
  setInput,
  onSubmit,
  placeholder = "Start typing... (e.g., 'portfolio performance', 'stock analysis', 'risk assessment')",
  className = ""
}: AutocompleteInputProps) {
  const [predictedCategories, setPredictedCategories] = useState<PredictedCategory[]>([]);
  const [selectedAnalysis, setSelectedAnalysis] = useState<PredictedCategory | null>(null);

  // Prediction logic based on user input
  useEffect(() => {
    const inputLower = input.toLowerCase();
    
    if (inputLower.includes('port') && inputLower.length >= 4) {
      setPredictedCategories([
        {
          id: 'portfolio_performance',
          title: 'Portfolio Performance',
          description: 'Analyze returns and benchmark comparison',
          emoji: '📈',
          suggestedQuestion: 'How has my portfolio performed compared to the S&P 500 over the last quarter, including risk-adjusted returns and sector attribution?',
          fields: [
            {
              id: 'period',
              label: 'Period',
              type: 'select',
              options: ['Last month', 'Last quarter', 'Last year'],
              value: 'Last quarter'
            },
            {
              id: 'benchmark',
              label: 'Compare to',
              type: 'select', 
              options: ['S&P 500', 'NASDAQ', 'Custom'],
              value: 'S&P 500'
            }
          ]
        },
        {
          id: 'portfolio_risk',
          title: 'Portfolio Risk Analysis',
          description: 'Evaluate risk metrics and diversification',
          emoji: '🛡️',
          suggestedQuestion: 'What is my portfolio\'s Value at Risk at 95% confidence level, and how diversified are my holdings across sectors and asset classes?',
          fields: [
            {
              id: 'risk_type',
              label: 'Risk Metric',
              type: 'select',
              options: ['Value at Risk', 'Beta Analysis', 'Volatility'],
              value: 'Value at Risk'
            },
            {
              id: 'confidence',
              label: 'Confidence',
              type: 'select',
              options: ['90%', '95%', '99%'],
              value: '95%'
            }
          ]
        }
      ]);
    } else if (inputLower.includes('stock') && inputLower.length >= 5) {
      setPredictedCategories([
        {
          id: 'stock_analysis',
          title: 'Stock Technical Analysis',
          description: 'RSI, MACD, and momentum signals',
          emoji: '📊',
          suggestedQuestion: `Analyze ${extractSymbol(input) || 'AAPL'} using RSI and MACD indicators with support/resistance levels and volume analysis for the next 30 days.`,
          fields: [
            {
              id: 'symbol',
              label: 'Symbol',
              type: 'input',
              placeholder: 'e.g., AAPL',
              value: extractSymbol(input)
            },
            {
              id: 'indicators',
              label: 'Indicators',
              type: 'select',
              options: ['RSI + MACD', 'Moving Averages', 'Bollinger Bands'],
              value: 'RSI + MACD'
            }
          ]
        }
      ]);
    } else if (inputLower.includes('risk') && inputLower.length >= 4) {
      setPredictedCategories([
        {
          id: 'risk_assessment',
          title: 'Risk Assessment',
          description: 'VaR, drawdown, and volatility analysis',
          emoji: '🛡️',
          suggestedQuestion: 'What is my portfolio\'s Value at Risk at 95% confidence level over the next month, including maximum drawdown and volatility metrics?',
          fields: [
            {
              id: 'risk_metric',
              label: 'Metric',
              type: 'select',
              options: ['Value at Risk', 'Max Drawdown', 'Volatility'],
              value: 'Value at Risk'
            },
            {
              id: 'time_horizon',
              label: 'Horizon',
              type: 'select',
              options: ['1 day', '1 week', '1 month'],
              value: '1 month'
            }
          ]
        }
      ]);
    } else {
      setPredictedCategories([]);
    }
  }, [input]);

  const extractSymbol = (text: string): string => {
    const matches = text.match(/\b[A-Z]{2,5}\b/g);
    return matches ? matches[0] : '';
  };

  const handleAnalysisSelect = (category: PredictedCategory) => {
    setSelectedAnalysis(category);
    setPredictedCategories([]);
    setInput('');
  };

  const handleBackToSelection = () => {
    setSelectedAnalysis(null);
  };

  const handleQuestionSubmit = (question: string) => {
    onSubmit(question);
    setSelectedAnalysis(null);
    setInput('');
  };

  if (selectedAnalysis) {
    return (
      <AnalysisConfigurator
        selectedAnalysis={selectedAnalysis}
        onBack={handleBackToSelection}
        onSubmit={handleQuestionSubmit}
        className={className}
      />
    );
  }

  return (
    <div className={className}>
      {/* Input Box */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={placeholder}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg"
        />
      </div>

      {/* Analysis Categories */}
      {predictedCategories.length > 0 && (
        <AnalysisSelector
          categories={predictedCategories}
          onSelect={handleAnalysisSelect}
        />
      )}

      {/* Help Text */}
      {input.length > 0 && predictedCategories.length === 0 && (
        <div className="bg-gray-100 rounded-lg p-4 text-center">
          <p className="text-gray-600 text-sm">
            Keep typing... Try words like "portfolio", "stock", "risk", "strategy", or "trading"
          </p>
        </div>
      )}
    </div>
  );
}