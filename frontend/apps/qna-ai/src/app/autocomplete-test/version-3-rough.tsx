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
  const [selectedAnalysis, setSelectedAnalysis] = useState<PredictedCategory | null>(null);
  const [settingsInput, setSettingsInput] = useState('');
  const [settingsSuggestions, setSettingsSuggestions] = useState<{
    id: string;
    title: string;
    description: string;
    emoji: string;
    level: number;
    parentId?: string;
  }[]>([]);
  const [settingsPath, setSettingsPath] = useState<string[]>([]);
  const [currentSettingsLevel, setCurrentSettingsLevel] = useState(0);

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

  // Progressive cascading settings auto-complete
  useEffect(() => {
    if (!selectedAnalysis) {
      setSettingsSuggestions([]);
      return;
    }

    const settingsLower = settingsInput.toLowerCase();
    const suggestions = [];

    // Level 0 - Main categories (always show 3 default or filtered)
    if (currentSettingsLevel === 0) {
      const level0Options = [
        {
          id: 'time_analysis',
          title: 'Time Analysis',
          description: 'Configure time periods and frequency',
          emoji: '⏰',
          level: 0
        },
        {
          id: 'risk_analysis',
          title: 'Risk Analysis', 
          description: 'Setup risk metrics and confidence levels',
          emoji: '🛡️',
          level: 0
        },
        {
          id: 'comparison_analysis',
          title: 'Comparison Analysis',
          description: 'Benchmark and peer comparisons',
          emoji: '📊',
          level: 0
        }
      ];

      // Filter based on input or show all 3
      if (settingsInput.length < 2) {
        suggestions.push(...level0Options);
      } else {
        suggestions.push(...level0Options.filter(opt => 
          opt.title.toLowerCase().includes(settingsLower) ||
          opt.description.toLowerCase().includes(settingsLower)
        ));
        // If no matches, still show all 3 default
        if (suggestions.length === 0) {
          suggestions.push(...level0Options);
        }
      }
    }

    // Level 1 - Sub-categories based on selected level 0
    else if (currentSettingsLevel === 1) {
      const parentCategory = settingsPath[0];
      
      if (parentCategory === 'time_analysis') {
        suggestions.push(
          {
            id: 'frequency_settings',
            title: 'Frequency Settings',
            description: 'Daily, weekly, monthly analysis',
            emoji: '📅',
            level: 1,
            parentId: 'time_analysis'
          },
          {
            id: 'lookback_period',
            title: 'Lookback Period',
            description: 'Historical data range',
            emoji: '🔙',
            level: 1,
            parentId: 'time_analysis'
          },
          {
            id: 'rolling_windows',
            title: 'Rolling Windows',
            description: 'Moving average periods',
            emoji: '🎢',
            level: 1,
            parentId: 'time_analysis'
          }
        );
      } else if (parentCategory === 'risk_analysis') {
        suggestions.push(
          {
            id: 'risk_metrics',
            title: 'Risk Metrics',
            description: 'VaR, volatility, drawdown',
            emoji: '📈',
            level: 1,
            parentId: 'risk_analysis'
          },
          {
            id: 'confidence_levels',
            title: 'Confidence Levels',
            description: '90%, 95%, 99% confidence',
            emoji: '🎯',
            level: 1,
            parentId: 'risk_analysis'
          },
          {
            id: 'stress_testing',
            title: 'Stress Testing',
            description: 'Market crash scenarios',
            emoji: '⚠️',
            level: 1,
            parentId: 'risk_analysis'
          }
        );
      } else if (parentCategory === 'comparison_analysis') {
        suggestions.push(
          {
            id: 'benchmark_selection',
            title: 'Benchmark Selection',
            description: 'S&P 500, NASDAQ, custom',
            emoji: '🏆',
            level: 1,
            parentId: 'comparison_analysis'
          },
          {
            id: 'peer_comparison',
            title: 'Peer Comparison',
            description: 'Similar funds and strategies',
            emoji: '👥',
            level: 1,
            parentId: 'comparison_analysis'
          },
          {
            id: 'attribution_analysis',
            title: 'Attribution Analysis',
            description: 'Sector, security, allocation',
            emoji: '🔍',
            level: 1,
            parentId: 'comparison_analysis'
          }
        );
      }
    }

    // Level 2 - Specific configurations
    else if (currentSettingsLevel === 2) {
      const currentCategory = settingsPath[settingsPath.length - 1];
      
      if (currentCategory === 'risk_metrics') {
        suggestions.push(
          {
            id: 'value_at_risk',
            title: 'Value at Risk',
            description: 'Historical and Monte Carlo VaR',
            emoji: '💥',
            level: 2,
            parentId: 'risk_metrics'
          },
          {
            id: 'volatility_measures',
            title: 'Volatility Measures',
            description: 'Standard deviation, EWMA',
            emoji: '📊',
            level: 2,
            parentId: 'risk_metrics'
          },
          {
            id: 'drawdown_analysis',
            title: 'Drawdown Analysis',
            description: 'Maximum and average drawdowns',
            emoji: '📉',
            level: 2,
            parentId: 'risk_metrics'
          }
        );
      } else if (currentCategory === 'benchmark_selection') {
        suggestions.push(
          {
            id: 'market_indices',
            title: 'Market Indices',
            description: 'S&P 500, NASDAQ, Russell',
            emoji: '🏛️',
            level: 2,
            parentId: 'benchmark_selection'
          },
          {
            id: 'sector_etfs',
            title: 'Sector ETFs',
            description: 'Technology, healthcare, finance',
            emoji: '🏭',
            level: 2,
            parentId: 'benchmark_selection'
          },
          {
            id: 'custom_portfolio',
            title: 'Custom Portfolio',
            description: 'Build your own benchmark',
            emoji: '🎨',
            level: 2,
            parentId: 'benchmark_selection'
          }
        );
      } else if (currentCategory === 'frequency_settings') {
        suggestions.push(
          {
            id: 'daily_analysis',
            title: 'Daily Analysis',
            description: 'Day-by-day performance',
            emoji: '📅',
            level: 2,
            parentId: 'frequency_settings'
          },
          {
            id: 'weekly_analysis',
            title: 'Weekly Analysis', 
            description: 'Week-over-week trends',
            emoji: '📊',
            level: 2,
            parentId: 'frequency_settings'
          },
          {
            id: 'monthly_analysis',
            title: 'Monthly Analysis',
            description: 'Monthly performance review',
            emoji: '📈',
            level: 2,
            parentId: 'frequency_settings'
          }
        );
      }
    }

    setSettingsSuggestions(suggestions.slice(0, 3)); // Always show exactly 3 options
  }, [selectedAnalysis, settingsInput, currentSettingsLevel, settingsPath]);

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

  const selectAnalysis = (category: PredictedCategory) => {
    setSelectedAnalysis(category);
    setPredictedCategories([]);
    setInput('');
    setSettingsInput('');
    setSettingsPath([]);
    setCurrentSettingsLevel(0);
  };

  const backToAnalysisSelection = () => {
    setSelectedAnalysis(null);
    setSettingsInput('');
    setSettingsSuggestions([]);
    setSettingsPath([]);
    setCurrentSettingsLevel(0);
  };

  const selectSetting = (suggestion: {
    id: string;
    title: string;
    level: number;
    parentId?: string;
  }) => {
    // Add to settings path
    const newPath = [...settingsPath, suggestion.id];
    setSettingsPath(newPath);
    setCurrentSettingsLevel(suggestion.level + 1);
    setSettingsInput('');
  };

  const backToPreviousLevel = () => {
    if (currentSettingsLevel > 0) {
      const newPath = settingsPath.slice(0, -1);
      setSettingsPath(newPath);
      setCurrentSettingsLevel(currentSettingsLevel - 1);
      setSettingsInput('');
    }
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {selectedAnalysis ? 'Recursive Form Builder' : 'Interactive Auto-Complete Test'}
          </h1>
          <p className="text-gray-600">
            {selectedAnalysis 
              ? `Customizing ${selectedAnalysis.title} - Type settings to auto-complete form fields`
              : 'Type keywords like "portfolio", "stock", or "risk" to see predicted analysis categories'
            }
          </p>
          {selectedAnalysis && (
            <button
              onClick={backToAnalysisSelection}
              className="mt-2 text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
            >
              ← Back to analysis selection
            </button>
          )}
        </div>

        {!selectedAnalysis ? (
          /* Analysis Selection Mode */
          <>
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
          </>
        ) : (
          /* Single Analysis Mode - Progressive Cascading */
          <div className="space-y-6">
            {/* Analysis Focus Card */}
            <div className="bg-white rounded-lg border border-blue-300 border-2 p-6">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <span className="text-xl">{selectedAnalysis.emoji}</span>
                </div>
                <div className="flex-1">
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">
                    {selectedAnalysis.title}
                  </h2>
                  <p className="text-gray-600">
                    {selectedAnalysis.description}
                  </p>
                  
                  {/* Settings Path Breadcrumb */}
                  {settingsPath.length > 0 && (
                    <div className="mt-4 flex items-center gap-2 text-sm">
                      <span className="text-gray-500">Configuration path:</span>
                      {settingsPath.map((pathItem, idx) => (
                        <div key={idx} className="flex items-center gap-2">
                          <button
                            onClick={() => {
                              const newPath = settingsPath.slice(0, idx + 1);
                              setSettingsPath(newPath);
                              setCurrentSettingsLevel(idx + 1);
                              setSettingsInput('');
                            }}
                            className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs hover:bg-blue-200"
                          >
                            {pathItem.replace(/_/g, ' ')}
                          </button>
                          {idx < settingsPath.length - 1 && (
                            <span className="text-gray-400">→</span>
                          )}
                        </div>
                      ))}
                      {currentSettingsLevel > 0 && (
                        <button
                          onClick={backToPreviousLevel}
                          className="ml-2 text-xs text-red-600 hover:text-red-700"
                        >
                          ← Back
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Settings Input */}
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Configure settings - Level {currentSettingsLevel}
                {currentSettingsLevel === 0 && ' (Main Categories)'}
                {currentSettingsLevel === 1 && ' (Sub Categories)'}
                {currentSettingsLevel === 2 && ' (Specific Settings)'}
              </label>
              <input
                type="text"
                value={settingsInput}
                onChange={(e) => setSettingsInput(e.target.value)}
                placeholder={
                  currentSettingsLevel === 0 
                    ? "Type to filter main categories or see all 3 default options..."
                    : currentSettingsLevel === 1
                    ? "Choose from 3 sub-categories..."
                    : "Select specific configuration..."
                }
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg"
              />
            </div>

            {/* Always Show Exactly 3 Setting Options */}
            {settingsSuggestions.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {settingsSuggestions.map((suggestion) => (
                  <button
                    key={suggestion.id}
                    onClick={() => selectSetting(suggestion)}
                    className="text-left p-4 bg-white hover:bg-blue-50 rounded-lg border border-gray-200 hover:border-blue-300 transition-all shadow-sm hover:shadow-md"
                  >
                    <div className="flex flex-col items-center text-center gap-3">
                      <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                        <span className="text-xl">{suggestion.emoji}</span>
                      </div>
                      <div>
                        <h3 className="font-medium text-gray-900 text-sm mb-1">
                          {suggestion.title}
                        </h3>
                        <p className="text-xs text-gray-600">
                          {suggestion.description}
                        </p>
                      </div>
                      <div className="text-xs text-blue-600 bg-blue-100 px-2 py-1 rounded-full">
                        Level {suggestion.level} → {suggestion.level + 1}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}

          </div>
        )}

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
                      
                      {/* Select Analysis Button */}
                      <button
                        onClick={() => selectAnalysis(category)}
                        className="p-1 text-gray-400 hover:text-blue-500 transition-colors"
                        title="Select this analysis"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </button>
                    </div>

                    {/* Quick Preview */}
                    <div className="space-y-2 mb-4">
                      <p className="text-xs text-gray-500">
                        Configurable settings: {category.fields.length + (category.expandedFields?.length || 0)} parameters
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {category.fields.slice(0, 2).map((field, idx) => (
                          <span key={idx} className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded-full text-xs">
                            {field.label}
                          </span>
                        ))}
                        {category.expandedFields && (
                          <span className="px-2 py-0.5 bg-blue-100 text-blue-600 rounded-full text-xs">
                            +{category.expandedFields.length} advanced
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Select Button */}
                    <button
                      onClick={() => selectAnalysis(category)}
                      className="w-full px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-xs font-medium"
                    >
                      📋 Customize This Analysis
                    </button>
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