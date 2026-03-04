'use client';

import { useState, useEffect } from 'react';

interface FormField {
  id: string;
  label: string;
  type: 'select' | 'input' | 'multiselect' | 'range';
  options?: string[];
  placeholder?: string;
  value?: string | string[] | number;
  min?: number;
  max?: number;
  step?: number;
}

interface PredictedCategory {
  id: string;
  title: string;
  description: string;
  emoji: string;
  fields: FormField[];
  expandedFields?: FormField[]; // Additional fields when expanded
  suggestedQuestion: string; // Question that appears in textbox when expanded
}

export default function AutocompleteTestPage() {
  const [input, setInput] = useState('');
  const [predictedCategories, setPredictedCategories] = useState<PredictedCategory[]>([]);
  const [expandedCategory, setExpandedCategory] = useState<string | null>(null);

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
          ],
          expandedFields: [
            {
              id: 'risk_adjusted',
              label: 'Risk Adjustment',
              type: 'multiselect',
              options: ['Sharpe Ratio', 'Sortino Ratio', 'Information Ratio', 'Treynor Ratio'],
              value: ['Sharpe Ratio', 'Sortino Ratio']
            },
            {
              id: 'attribution',
              label: 'Attribution Analysis',
              type: 'multiselect',
              options: ['Sector Attribution', 'Security Selection', 'Asset Allocation', 'Timing Effect'],
              value: ['Sector Attribution']
            },
            {
              id: 'min_return',
              label: 'Min Expected Return (%)',
              type: 'range',
              min: 0,
              max: 20,
              step: 0.5,
              value: 8
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
          ],
          expandedFields: [
            {
              id: 'time_horizon',
              label: 'Time Horizon',
              type: 'select',
              options: ['1 day', '1 week', '1 month', '3 months'],
              value: '1 month'
            },
            {
              id: 'correlation_analysis',
              label: 'Correlation Analysis',
              type: 'multiselect',
              options: ['Asset Correlation', 'Sector Correlation', 'Geographic Correlation', 'Currency Exposure'],
              value: ['Asset Correlation', 'Sector Correlation']
            },
            {
              id: 'stress_scenarios',
              label: 'Stress Test Scenarios',
              type: 'multiselect',
              options: ['2008 Crisis', 'COVID-19 Crash', 'Interest Rate Spike', 'Inflation Surge'],
              value: ['COVID-19 Crash']
            }
          ]
        },
        {
          id: 'portfolio_rebalance',
          title: 'Portfolio Rebalancing',
          description: 'Optimize allocation and suggest rebalancing',
          emoji: '⚖️',
          suggestedQuestion: 'Should I rebalance my portfolio to maintain a balanced allocation, and what would be the optimal frequency considering transaction costs?',
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
          ],
          expandedFields: [
            {
              id: 'transaction_cost',
              label: 'Transaction Cost (%)',
              type: 'range',
              min: 0,
              max: 2,
              step: 0.05,
              value: 0.25
            },
            {
              id: 'rebalance_threshold',
              label: 'Rebalance Threshold (%)',
              type: 'range',
              min: 1,
              max: 20,
              step: 1,
              value: 5
            },
            {
              id: 'optimization_method',
              label: 'Optimization Method',
              type: 'select',
              options: ['Mean Variance', 'Risk Parity', 'Black-Litterman', 'Minimum Variance'],
              value: 'Mean Variance'
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
          ],
          expandedFields: [
            {
              id: 'timeframe',
              label: 'Chart Timeframe',
              type: 'multiselect',
              options: ['1 minute', '5 minutes', '1 hour', '1 day', '1 week'],
              value: ['1 hour', '1 day']
            },
            {
              id: 'additional_indicators',
              label: 'Additional Indicators',
              type: 'multiselect',
              options: ['Stochastic', 'Williams %R', 'CCI', 'ADX', 'Volume Profile'],
              value: ['Volume Profile']
            },
            {
              id: 'forecast_days',
              label: 'Forecast Period (days)',
              type: 'range',
              min: 1,
              max: 90,
              step: 1,
              value: 30
            }
          ]
        },
        {
          id: 'stock_comparison',
          title: 'Stock Comparison',
          description: 'Compare performance vs peers',
          emoji: '⚡',
          suggestedQuestion: `Compare ${extractSymbol(input) || 'AAPL'} performance against sector peers over the last year, including valuation metrics and growth rates.`,
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
          ],
          expandedFields: [
            {
              id: 'metrics',
              label: 'Comparison Metrics',
              type: 'multiselect',
              options: ['P/E Ratio', 'Revenue Growth', 'Profit Margin', 'ROE', 'Beta', 'Dividend Yield'],
              value: ['P/E Ratio', 'Revenue Growth', 'Beta']
            },
            {
              id: 'peer_symbols',
              label: 'Custom Peer List',
              type: 'input',
              placeholder: 'e.g., MSFT, GOOGL, META',
              value: ''
            },
            {
              id: 'time_period',
              label: 'Analysis Period',
              type: 'select',
              options: ['1 month', '3 months', '6 months', '1 year', '2 years'],
              value: '1 year'
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
          ],
          expandedFields: [
            {
              id: 'confidence_level',
              label: 'Confidence Level',
              type: 'select',
              options: ['90%', '95%', '99%'],
              value: '95%'
            },
            {
              id: 'risk_models',
              label: 'Risk Models',
              type: 'multiselect',
              options: ['Historical VaR', 'Monte Carlo VaR', 'Parametric VaR', 'Expected Shortfall'],
              value: ['Historical VaR', 'Expected Shortfall']
            },
            {
              id: 'stress_scenarios',
              label: 'Include Stress Tests',
              type: 'multiselect',
              options: ['2008 Financial Crisis', 'COVID-19 Crash', 'Black Monday 1987', 'Dot-com Crash'],
              value: ['COVID-19 Crash']
            },
            {
              id: 'portfolio_value',
              label: 'Portfolio Value ($)',
              type: 'range',
              min: 10000,
              max: 10000000,
              step: 10000,
              value: 500000
            }
          ]
        },
        {
          id: 'stress_test',
          title: 'Stress Testing',
          description: 'Test portfolio under market scenarios',
          emoji: '⚠️',
          suggestedQuestion: 'How would my portfolio perform during a severe market crash scenario, similar to the 2008 financial crisis with correlation breakdowns?',
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
          ],
          expandedFields: [
            {
              id: 'scenario_types',
              label: 'Scenario Types',
              type: 'multiselect',
              options: ['Equity Market Crash', 'Bond Market Selloff', 'Currency Crisis', 'Commodity Shock', 'Liquidity Crisis'],
              value: ['Equity Market Crash', 'Liquidity Crisis']
            },
            {
              id: 'correlation_breakdown',
              label: 'Model Correlation Breakdown',
              type: 'select',
              options: ['Yes - correlations spike to 1', 'No - maintain historical correlations', 'Partial - 50% correlation increase'],
              value: 'Yes - correlations spike to 1'
            },
            {
              id: 'recovery_period',
              label: 'Recovery Period (months)',
              type: 'range',
              min: 1,
              max: 60,
              step: 1,
              value: 18
            },
            {
              id: 'volatility_multiplier',
              label: 'Volatility Multiplier',
              type: 'range',
              min: 1,
              max: 5,
              step: 0.1,
              value: 2.5
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

  const updateFieldValue = (categoryId: string, fieldId: string, value: string | string[] | number, isExpanded = false) => {
    setPredictedCategories(prev => 
      prev.map(category => 
        category.id === categoryId 
          ? {
              ...category,
              fields: !isExpanded ? category.fields.map(field =>
                field.id === fieldId ? { ...field, value } : field
              ) : category.fields,
              expandedFields: isExpanded && category.expandedFields ? category.expandedFields.map(field =>
                field.id === fieldId ? { ...field, value } : field
              ) : category.expandedFields
            }
          : category
      )
    );
  };

  const toggleExpand = (categoryId: string) => {
    setExpandedCategory(expandedCategory === categoryId ? null : categoryId);
  };

  const fillTextboxFromCategory = (category: PredictedCategory) => {
    setInput(category.suggestedQuestion);
    setExpandedCategory(null);
  };

  const handleCategorySubmit = (category: PredictedCategory) => {
    const formData = category.fields.reduce((acc, field) => {
      acc[field.id] = field.value || '';
      return acc;
    }, {} as Record<string, string>);
    
    console.log(`Submitted ${category.title}:`, formData);
    alert(`Running ${category.title} analysis with your parameters!`);
  };

  const renderField = (field: FormField, categoryId: string, isExpanded = false) => {
    const key = `${categoryId}-${field.id}`;
    
    switch (field.type) {
      case 'select':
        return (
          <select
            key={key}
            value={field.value || ''}
            onChange={(e) => updateFieldValue(categoryId, field.id, e.target.value, isExpanded)}
            className="w-full px-2 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 text-xs"
          >
            {field.options?.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        );
      
      case 'input':
        return (
          <input
            key={key}
            type="text"
            value={field.value || ''}
            onChange={(e) => updateFieldValue(categoryId, field.id, e.target.value, isExpanded)}
            placeholder={field.placeholder}
            className="w-full px-2 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 text-xs"
          />
        );
      
      case 'multiselect':
        return (
          <div key={key} className="flex flex-wrap gap-1">
            {field.options?.map((option) => {
              const isSelected = Array.isArray(field.value) && field.value.includes(option);
              return (
                <button
                  key={option}
                  onClick={() => {
                    const currentValues = Array.isArray(field.value) ? field.value : [];
                    const newValues = isSelected
                      ? currentValues.filter(v => v !== option)
                      : [...currentValues, option];
                    updateFieldValue(categoryId, field.id, newValues, isExpanded);
                  }}
                  className={`px-2 py-1 text-xs rounded-full border transition-colors ${
                    isSelected
                      ? 'bg-blue-100 border-blue-300 text-blue-700'
                      : 'bg-gray-100 border-gray-300 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {option}
                </button>
              );
            })}
          </div>
        );
      
      case 'range':
        return (
          <div key={key} className="space-y-1">
            <input
              type="range"
              min={field.min}
              max={field.max}
              step={field.step}
              value={field.value || field.min || 0}
              onChange={(e) => updateFieldValue(categoryId, field.id, Number(e.target.value), isExpanded)}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>{field.min?.toLocaleString()}</span>
              <span className="font-medium text-gray-700">
                {typeof field.value === 'number' ? field.value.toLocaleString() : field.min?.toLocaleString()}
              </span>
              <span>{field.max?.toLocaleString()}</span>
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Interactive Auto-Complete Test</h1>
          <p className="text-gray-600">
            Type keywords like &quot;portfolio&quot;, &quot;stock&quot;, or &quot;risk&quot; to see predicted analysis categories with mini forms
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
              Suggested analyses for &quot;{input}&quot;:
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {predictedCategories.map((category) => {
                const isExpanded = expandedCategory === category.id;
                return (
                  <div
                    key={category.id}
                    className={`bg-white rounded-lg border border-gray-200 p-4 hover:border-blue-300 transition-all ${
                      isExpanded ? 'col-span-full max-w-4xl mx-auto' : ''
                    }`}
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
                      
                      {/* Expand/Question Fill Icons */}
                      <div className="flex gap-1">
                        {category.suggestedQuestion && (
                          <button
                            onClick={() => fillTextboxFromCategory(category)}
                            className="p-1 text-gray-400 hover:text-blue-500 transition-colors"
                            title="Fill textbox with suggested question"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                          </button>
                        )}
                        
                        {category.expandedFields && (
                          <button
                            onClick={() => toggleExpand(category.id)}
                            className="p-1 text-gray-400 hover:text-blue-500 transition-colors"
                            title={isExpanded ? "Collapse form" : "Expand form"}
                          >
                            <svg className={`w-4 h-4 transform transition-transform ${isExpanded ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Interactive Form */}
                    <div className={`space-y-3 ${isExpanded ? 'grid grid-cols-2 gap-6' : ''}`}>
                      {/* Basic Fields */}
                      <div className={isExpanded ? '' : 'space-y-3'}>
                        {isExpanded && <h4 className="font-medium text-gray-900 text-sm mb-3">Basic Settings</h4>}
                        {category.fields.map((field) => (
                          <div key={field.id}>
                            <label className="block text-xs font-medium text-gray-700 mb-1">
                              {field.label}
                            </label>
                            {renderField(field, category.id, false)}
                          </div>
                        ))}
                      </div>

                      {/* Expanded Fields */}
                      {isExpanded && category.expandedFields && (
                        <div>
                          <h4 className="font-medium text-gray-900 text-sm mb-3">Advanced Options</h4>
                          <div className="space-y-3">
                            {category.expandedFields.map((field) => (
                              <div key={field.id}>
                                <label className="block text-xs font-medium text-gray-700 mb-1">
                                  {field.label}
                                </label>
                                {renderField(field, category.id, true)}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Action Buttons */}
                    <div className={`mt-4 ${isExpanded ? 'flex gap-3' : ''}`}>
                      <button
                        onClick={() => handleCategorySubmit(category)}
                        className={`${isExpanded ? 'flex-1' : 'w-full'} px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-xs font-medium`}
                      >
                        🚀 Run Analysis
                      </button>
                      
                      {isExpanded && (
                        <button
                          onClick={() => setExpandedCategory(null)}
                          className="px-3 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors text-xs font-medium"
                        >
                          Collapse
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Help Text */}
        {input.length > 0 && predictedCategories.length === 0 && (
          <div className="bg-gray-100 rounded-lg p-4 text-center">
            <p className="text-gray-600 text-sm">
              Keep typing... Try words like &quot;portfolio&quot;, &quot;stock&quot;, &quot;risk&quot;, &quot;strategy&quot;, or &quot;trading&quot;
            </p>
          </div>
        )}
      </div>
    </div>
  );
}