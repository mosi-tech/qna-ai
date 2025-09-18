'use client';

import { useState, useEffect } from 'react';

interface FormField {
  id: string;
  label: string;
  type: 'select' | 'input';
  options?: string[];
  placeholder?: string;
  value?: string;
}

interface PredictedCategory {
  id: string;
  title: string;
  description: string;
  emoji: string;
  fields: FormField[];
}

export default function AutocompleteTestPage() {
  const [input, setInput] = useState('');
  const [predictedCategories, setPredictedCategories] = useState<PredictedCategory[]>([]);

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
        },
        {
          id: 'portfolio_rebalance',
          title: 'Portfolio Rebalancing',
          description: 'Optimize allocation and suggest rebalancing',
          emoji: '⚖️',
          fields: [
            {
              id: 'target_allocation',
              label: 'Target Style',
              type: 'select',
              options: ['Conservative', 'Balanced', 'Growth'],
              value: 'Balanced'
            },
            {
              id: 'rebalance_frequency',
              label: 'Frequency',
              type: 'select',
              options: ['Monthly', 'Quarterly', 'Yearly'],
              value: 'Quarterly'
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
        },
        {
          id: 'stock_comparison',
          title: 'Stock Comparison',
          description: 'Compare performance vs peers',
          emoji: '⚡',
          fields: [
            {
              id: 'primary_symbol',
              label: 'Primary Stock',
              type: 'input',
              placeholder: 'e.g., AAPL',
              value: extractSymbol(input)
            },
            {
              id: 'comparison',
              label: 'Compare vs',
              type: 'select',
              options: ['Sector peers', 'S&P 500', 'Custom list'],
              value: 'Sector peers'
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
        },
        {
          id: 'stress_test',
          title: 'Stress Testing',
          description: 'Test portfolio under market scenarios',
          emoji: '⚠️',
          fields: [
            {
              id: 'scenario',
              label: 'Scenario',
              type: 'select',
              options: ['Market crash', 'Interest rate spike', 'Recession'],
              value: 'Market crash'
            },
            {
              id: 'severity',
              label: 'Severity',
              type: 'select',
              options: ['Mild (-10%)', 'Moderate (-20%)', 'Severe (-40%)'],
              value: 'Moderate (-20%)'
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

  const updateFieldValue = (categoryId: string, fieldId: string, value: string) => {
    setPredictedCategories(prev => 
      prev.map(category => 
        category.id === categoryId 
          ? {
              ...category,
              fields: category.fields.map(field =>
                field.id === fieldId ? { ...field, value } : field
              )
            }
          : category
      )
    );
  };

  const handleCategorySubmit = (category: PredictedCategory) => {
    const formData = category.fields.reduce((acc, field) => {
      acc[field.id] = field.value || '';
      return acc;
    }, {} as Record<string, string>);
    
    console.log(`Submitted ${category.title}:`, formData);
    alert(`Running ${category.title} analysis with your parameters!`);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Interactive Auto-Complete Test</h1>
          <p className="text-gray-600">
            Type keywords like "portfolio", "stock", or "risk" to see predicted analysis categories with mini forms
          </p>
        </div>

        {/* Input Box */}
        <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            What would you like to analyze?
          </label>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Start typing... (e.g., 'portfolio performance', 'stock analysis', 'risk assessment')"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg"
          />
        </div>

        {/* Predicted Categories */}
        {predictedCategories.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">
              Suggested analyses for "{input}":
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {predictedCategories.map((category) => (
                <div
                  key={category.id}
                  className="bg-white rounded-lg border border-gray-200 p-4 hover:border-blue-300 transition-colors"
                >
                  {/* Category Header */}
                  <div className="flex items-start gap-3 mb-4">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <span className="text-lg">{category.emoji}</span>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 text-sm">
                        {category.title}
                      </h3>
                      <p className="text-xs text-gray-600 mt-1">
                        {category.description}
                      </p>
                    </div>
                  </div>

                  {/* Mini Interactive Form */}
                  <div className="space-y-3">
                    {category.fields.map((field) => (
                      <div key={field.id}>
                        <label className="block text-xs font-medium text-gray-700 mb-1">
                          {field.label}
                        </label>
                        {field.type === 'select' ? (
                          <select
                            value={field.value || ''}
                            onChange={(e) => updateFieldValue(category.id, field.id, e.target.value)}
                            className="w-full px-2 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 text-xs"
                          >
                            {field.options?.map((option) => (
                              <option key={option} value={option}>
                                {option}
                              </option>
                            ))}
                          </select>
                        ) : (
                          <input
                            type="text"
                            value={field.value || ''}
                            onChange={(e) => updateFieldValue(category.id, field.id, e.target.value)}
                            placeholder={field.placeholder}
                            className="w-full px-2 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 text-xs"
                          />
                        )}
                      </div>
                    ))}
                  </div>

                  {/* Quick Submit Button */}
                  <button
                    onClick={() => handleCategorySubmit(category)}
                    className="w-full mt-4 px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-xs font-medium"
                  >
                    🚀 Run Analysis
                  </button>
                </div>
              ))}
            </div>
          </div>
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
    </div>
  );
}