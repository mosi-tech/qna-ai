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
  const [selectedAnalysis, setSelectedAnalysis] = useState<PredictedCategory | null>(null);
  const [activeSettingType, setActiveSettingType] = useState<string | null>(null);
  const [settingsInput, setSettingsInput] = useState('');
  const [settingsSuggestions, setSettingsSuggestions] = useState<{
    id: string;
    title: string;
    description: string;
    emoji: string;
  }[]>([]);
  const [selectedSettings, setSelectedSettings] = useState<{[key: string]: string}>({});
  const [isFormExpanded, setIsFormExpanded] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState<string>('');

  // Dynamic question generation based on current settings
  const generateDynamicQuestions = () => {
    if (!selectedAnalysis) return [];

    const questions = [];
    const timeSettings = selectedSettings.time_settings;
    const riskSettings = selectedSettings.risk_settings;
    const comparisonSettings = selectedSettings.comparison_settings;
    const advancedSettings = selectedSettings.advanced_settings;

    // Always generate questions based on current settings
    // Start with settings-based questions first for dynamic behavior

    // Add time-specific questions first (more specific/varied)
    if (timeSettings) {
      const timeQuestions = {
        'Daily Analysis': [
          { text: `What was my portfolio performance yesterday with ${riskSettings?.toLowerCase() || 'risk analysis'}?`, emoji: '📅', confidence: 'high' },
          { text: `What is my daily ${riskSettings?.toLowerCase() || 'risk'} vs ${comparisonSettings?.toLowerCase() || 'market'}?`, emoji: '📊', confidence: 'high' }
        ],
        'Weekly Analysis': [
          { text: `How did my portfolio perform this week using ${riskSettings?.toLowerCase() || 'risk metrics'}?`, emoji: '📈', confidence: 'high' },
          { text: `What were my weekly ${riskSettings?.toLowerCase() || 'risk'} levels compared to ${comparisonSettings?.toLowerCase() || 'benchmarks'}?`, emoji: '📊', confidence: 'high' }
        ],
        'Monthly Analysis': [
          { text: `What is my month-to-date ${riskSettings?.toLowerCase() || 'portfolio performance'}?`, emoji: '📅', confidence: 'high' },
          { text: `How does my monthly ${riskSettings?.toLowerCase() || 'risk profile'} compare to ${comparisonSettings?.toLowerCase() || 'market standards'}?`, emoji: '📊', confidence: 'high' }
        ],
        'Quarterly Analysis': [
          { text: `How did my ${riskSettings?.toLowerCase() || 'portfolio'} perform this quarter vs ${comparisonSettings?.toLowerCase() || 'benchmarks'}?`, emoji: '🗓️', confidence: 'high' },
          { text: `What are my quarterly ${riskSettings?.toLowerCase() || 'risk'} metrics with ${advancedSettings?.toLowerCase() || 'advanced analysis'}?`, emoji: '📊', confidence: 'high' }
        ]
      };
      
      const timeQuestionsArray = timeQuestions[timeSettings];
      if (timeQuestionsArray) {
        questions.push(...timeQuestionsArray);
      }
    }

    // Add comprehensive questions using ALL settings (lower priority)
    if (timeSettings && riskSettings && comparisonSettings && advancedSettings) {
      questions.push({
        id: 'comprehensive_summary',
        text: `Complete ${timeSettings.toLowerCase()} analysis: ${riskSettings.toLowerCase()} vs ${comparisonSettings.toLowerCase()} with ${advancedSettings.toLowerCase()}`,
        emoji: '🎯',
        confidence: 'high'
      });
    }


    // Always return the first few questions (they're prioritized by comprehensiveness)
    return questions.length > 0 ? questions.slice(0, 3) : [
      {
        id: 'fallback',
        text: selectedAnalysis?.suggestedQuestion || 'Configure your analysis settings to see personalized questions',
        emoji: '💡',
        confidence: 'medium'
      }
    ];
  };

  // Infer settings from a question and update them
  const setSettingsFromQuestion = (question: string) => {
    const questionLower = question.toLowerCase();
    const newSettings = {};

    // Infer time settings (enhanced patterns) - now covers the generated question patterns
    if (questionLower.includes('daily') || questionLower.includes('day') || 
        questionLower.includes('yesterday') || questionLower.includes('today')) {
      newSettings.time_settings = 'Daily Analysis';
    } else if (questionLower.includes('weekly') || questionLower.includes('week')) {
      newSettings.time_settings = 'Weekly Analysis';
    } else if (questionLower.includes('monthly') || questionLower.includes('month') || 
               questionLower.includes('month-to-date')) {
      newSettings.time_settings = 'Monthly Analysis';
    } else if (questionLower.includes('quarterly') || questionLower.includes('quarter')) {
      newSettings.time_settings = 'Quarterly Analysis';
    } else if (questionLower.includes('rolling') || questionLower.includes('30-day') ||
               questionLower.includes('lookback')) {
      newSettings.time_settings = 'Rolling Periods';
    }

    // Infer risk settings (enhanced patterns) - matches the generated templates
    if (questionLower.includes('value at risk') || questionLower.includes('var') ||
        questionLower.includes('lose in a bad day') || questionLower.includes('confidence level')) {
      newSettings.risk_settings = 'Value at Risk';
    } else if (questionLower.includes('volatility analysis') || questionLower.includes('volatile') || 
               questionLower.includes('volatility')) {
      newSettings.risk_settings = 'Volatility Analysis';
    } else if (questionLower.includes('maximum drawdown') || questionLower.includes('drawdown') || 
               questionLower.includes('worst-case') || questionLower.includes('peak-to-trough')) {
      newSettings.risk_settings = 'Maximum Drawdown';
    } else if (questionLower.includes('beta analysis') || questionLower.includes('beta') || 
               questionLower.includes('sensitive') || questionLower.includes('market moves')) {
      newSettings.risk_settings = 'Beta Analysis';
    } else if (questionLower.includes('stress testing') || questionLower.includes('stress') || 
               questionLower.includes('crash') || questionLower.includes('scenario')) {
      newSettings.risk_settings = 'Stress Testing';
    } else if (questionLower.includes('correlation analysis') || questionLower.includes('correlation')) {
      newSettings.risk_settings = 'Correlation Analysis';
    }

    // Infer comparison settings (enhanced patterns) - matches the generated templates  
    if (questionLower.includes('s&p 500 benchmark') || questionLower.includes('s&p 500') || 
        questionLower.includes('spy') || questionLower.includes('market') || 
        questionLower.includes('beating the market')) {
      newSettings.comparison_settings = 'S&P 500 Benchmark';
    } else if (questionLower.includes('sector comparison') || questionLower.includes('sector') || 
               questionLower.includes('peers') || questionLower.includes('rank')) {
      newSettings.comparison_settings = 'Sector Comparison';
    } else if (questionLower.includes('custom benchmark') || questionLower.includes('custom')) {
      newSettings.comparison_settings = 'Custom Benchmark';
    } else if (questionLower.includes('attribution analysis') || questionLower.includes('attribution') || 
               questionLower.includes('driving') || questionLower.includes('drove')) {
      newSettings.comparison_settings = 'Attribution Analysis';
    }

    // Infer advanced settings (enhanced patterns) - matches the generated templates
    if (questionLower.includes('transaction costs') || questionLower.includes('transaction cost') || 
        questionLower.includes('trading cost') || questionLower.includes('trading patterns')) {
      newSettings.advanced_settings = 'Transaction Costs';
    } else if (questionLower.includes('rebalancing logic') || questionLower.includes('rebalance') || 
               questionLower.includes('rebalancing') || questionLower.includes('quarter-end')) {
      newSettings.advanced_settings = 'Rebalancing Logic';
    } else if (questionLower.includes('tax optimization') || questionLower.includes('tax') || 
               questionLower.includes('tax efficient')) {
      newSettings.advanced_settings = 'Tax Optimization';
    } else if (questionLower.includes('monte carlo simulation') || questionLower.includes('monte carlo') || 
               questionLower.includes('simulation') || questionLower.includes('probabilistic')) {
      newSettings.advanced_settings = 'Monte Carlo Simulation';
    } else if (questionLower.includes('liquidity analysis') || questionLower.includes('liquidity')) {
      newSettings.advanced_settings = 'Liquidity Analysis';
    }

    // Only update settings that were actually inferred
    const finalSettings = { ...selectedSettings, ...newSettings };
    setSelectedSettings(finalSettings);
  };

  // Get the primary suggested question based on current settings
  const getPrimaryQuestion = () => {
    // If a specific question was selected from suggestions, use that
    if (selectedQuestion) {
      return selectedQuestion;
    }
    
    // Otherwise generate based on current settings
    const questions = generateDynamicQuestions();
    return questions.length > 0 ? questions[0].text : selectedAnalysis?.suggestedQuestion || 'Select settings to see a personalized question';
  };

  // Define default settings for different analysis types
  const getDefaultSettings = () => ({
    time_settings: 'Monthly Analysis',
    risk_settings: 'Value at Risk',
    comparison_settings: 'S&P 500 Benchmark',
    advanced_settings: 'Transaction Costs'
  });

  // Define setting types with their display info
  const settingTypes = [
    { id: 'time_settings', label: 'Time', emoji: '⏰' },
    { id: 'risk_settings', label: 'Risk', emoji: '🛡️' },
    { id: 'comparison_settings', label: 'Compare', emoji: '📊' },
    { id: 'advanced_settings', label: 'Advanced', emoji: '⚙️' }
  ];

  // Suggested questions with different setting combinations
  const suggestedQuestions = [
    {
      id: 'daily_risk_sp500',
      question: 'What is my daily portfolio risk compared to S&P 500?',
      emoji: '📊',
      description: 'Daily analysis with VaR vs market benchmark',
      settings: {
        time_settings: 'Daily Analysis',
        risk_settings: 'Value at Risk',
        comparison_settings: 'S&P 500 Benchmark',
        advanced_settings: 'Transaction Costs'
      },
      analysisType: 'portfolio_performance'
    },
    {
      id: 'monthly_volatility_sector',
      question: 'How volatile is my portfolio monthly vs my sector peers?',
      emoji: '📈',
      description: 'Monthly volatility analysis with sector comparison',
      settings: {
        time_settings: 'Monthly Analysis',
        risk_settings: 'Volatility Analysis',
        comparison_settings: 'Sector Comparison',
        advanced_settings: 'Rebalancing Logic'
      },
      analysisType: 'portfolio_risk'
    },
    {
      id: 'quarterly_drawdown_custom',
      question: 'What is my maximum quarterly drawdown vs custom benchmark?',
      emoji: '⚠️',
      description: 'Quarterly max drawdown with custom comparison',
      settings: {
        time_settings: 'Quarterly Analysis',
        risk_settings: 'Maximum Drawdown',
        comparison_settings: 'Custom Benchmark',
        advanced_settings: 'Monte Carlo Simulation'
      },
      analysisType: 'portfolio_risk'
    },
    {
      id: 'rolling_beta_attribution',
      question: 'Show me rolling 30-day beta with attribution analysis',
      emoji: '🔄',
      description: 'Rolling periods with beta analysis and performance attribution',
      settings: {
        time_settings: 'Rolling Periods',
        risk_settings: 'Beta Analysis',
        comparison_settings: 'Attribution Analysis',
        advanced_settings: 'Tax Optimization'
      },
      analysisType: 'portfolio_performance'
    },
    {
      id: 'stress_test_rebalance',
      question: 'How would stress scenarios affect my rebalancing strategy?',
      emoji: '💥',
      description: 'Stress testing with optimal rebalancing analysis',
      settings: {
        time_settings: 'Lookback Window',
        risk_settings: 'Stress Testing',
        comparison_settings: 'Peer Analysis',
        advanced_settings: 'Rebalancing Logic'
      },
      analysisType: 'portfolio_rebalance'
    },
    {
      id: 'weekly_correlation_liquidity',
      question: 'What are my weekly correlations with liquidity impact?',
      emoji: '🔗',
      description: 'Weekly correlation analysis considering liquidity',
      settings: {
        time_settings: 'Weekly Analysis',
        risk_settings: 'Correlation Analysis',
        comparison_settings: 'S&P 500 Benchmark',
        advanced_settings: 'Liquidity Analysis'
      },
      analysisType: 'portfolio_risk'
    }
  ];

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

  // Setting-type-based auto-complete
  useEffect(() => {
    if (!selectedAnalysis || !activeSettingType) {
      setSettingsSuggestions([]);
      return;
    }

    const settingsLower = settingsInput.toLowerCase();
    const suggestions = [];

    // Time Settings
    if (activeSettingType === 'time_settings') {
      const timeOptions = [
        {
          id: 'daily_frequency',
          title: 'Daily Analysis',
          description: 'Day-by-day performance tracking',
          emoji: '📅'
        },
        {
          id: 'weekly_frequency', 
          title: 'Weekly Analysis',
          description: 'Week-over-week trends',
          emoji: '📊'
        },
        {
          id: 'monthly_frequency',
          title: 'Monthly Analysis', 
          description: 'Monthly performance review',
          emoji: '📈'
        },
        {
          id: 'quarterly_frequency',
          title: 'Quarterly Analysis',
          description: 'Quarterly business cycles',
          emoji: '🗓️'
        },
        {
          id: 'rolling_periods',
          title: 'Rolling Periods',
          description: 'Moving windows analysis',
          emoji: '🔄'
        },
        {
          id: 'lookback_window',
          title: 'Lookback Window',
          description: '30d, 90d, 1yr historical data',
          emoji: '🔙'
        }
      ];

      // Filter based on input or show default options
      if (settingsInput.length < 2) {
        suggestions.push(...timeOptions.slice(0, 3));
      } else {
        const filtered = timeOptions.filter(opt => 
          opt.title.toLowerCase().includes(settingsLower) ||
          opt.description.toLowerCase().includes(settingsLower)
        );
        suggestions.push(...filtered.slice(0, 3));
        if (suggestions.length === 0) {
          suggestions.push(...timeOptions.slice(0, 3));
        }
      }
    }

    // Risk Settings
    else if (activeSettingType === 'risk_settings') {
      const riskOptions = [
        {
          id: 'value_at_risk',
          title: 'Value at Risk',
          description: '95% confidence VaR calculation',
          emoji: '💥'
        },
        {
          id: 'volatility_analysis',
          title: 'Volatility Analysis',
          description: 'Standard deviation & EWMA',
          emoji: '📉'
        },
        {
          id: 'maximum_drawdown',
          title: 'Maximum Drawdown',
          description: 'Peak-to-trough decline',
          emoji: '📊'
        },
        {
          id: 'beta_analysis',
          title: 'Beta Analysis',
          description: 'Market sensitivity measurement',
          emoji: '🎯'
        },
        {
          id: 'stress_testing',
          title: 'Stress Testing',
          description: 'Market crash scenarios',
          emoji: '⚠️'
        },
        {
          id: 'correlation_analysis',
          title: 'Correlation Analysis',
          description: 'Asset correlation matrix',
          emoji: '🔗'
        }
      ];

      if (settingsInput.length < 2) {
        suggestions.push(...riskOptions.slice(0, 3));
      } else {
        const filtered = riskOptions.filter(opt => 
          opt.title.toLowerCase().includes(settingsLower) ||
          opt.description.toLowerCase().includes(settingsLower)
        );
        suggestions.push(...filtered.slice(0, 3));
        if (suggestions.length === 0) {
          suggestions.push(...riskOptions.slice(0, 3));
        }
      }
    }

    // Comparison Settings
    else if (activeSettingType === 'comparison_settings') {
      const comparisonOptions = [
        {
          id: 'sp500_benchmark',
          title: 'S&P 500 Benchmark',
          description: 'Compare against SPY index',
          emoji: '🏛️'
        },
        {
          id: 'sector_comparison',
          title: 'Sector Comparison',
          description: 'Compare vs sector ETFs',
          emoji: '🏭'
        },
        {
          id: 'peer_analysis',
          title: 'Peer Analysis',
          description: 'Similar funds & strategies',
          emoji: '👥'
        },
        {
          id: 'custom_benchmark',
          title: 'Custom Benchmark',
          description: 'Build your own comparison',
          emoji: '🎨'
        },
        {
          id: 'attribution_analysis',
          title: 'Attribution Analysis',
          description: 'Performance breakdown',
          emoji: '🔍'
        }
      ];

      if (settingsInput.length < 2) {
        suggestions.push(...comparisonOptions.slice(0, 3));
      } else {
        const filtered = comparisonOptions.filter(opt => 
          opt.title.toLowerCase().includes(settingsLower) ||
          opt.description.toLowerCase().includes(settingsLower)
        );
        suggestions.push(...filtered.slice(0, 3));
        if (suggestions.length === 0) {
          suggestions.push(...comparisonOptions.slice(0, 3));
        }
      }
    }

    // Advanced Settings
    else if (activeSettingType === 'advanced_settings') {
      const advancedOptions = [
        {
          id: 'transaction_costs',
          title: 'Transaction Costs',
          description: 'Trading fees & slippage',
          emoji: '💸'
        },
        {
          id: 'rebalancing_logic',
          title: 'Rebalancing Logic',
          description: 'Automatic portfolio rebalancing',
          emoji: '⚖️'
        },
        {
          id: 'tax_optimization',
          title: 'Tax Optimization',
          description: 'Tax-efficient strategies',
          emoji: '🏛️'
        },
        {
          id: 'liquidity_analysis',
          title: 'Liquidity Analysis',
          description: 'Market impact assessment',
          emoji: '💧'
        },
        {
          id: 'monte_carlo',
          title: 'Monte Carlo Simulation',
          description: 'Probabilistic modeling',
          emoji: '🎲'
        }
      ];

      if (settingsInput.length < 2) {
        suggestions.push(...advancedOptions.slice(0, 3));
      } else {
        const filtered = advancedOptions.filter(opt => 
          opt.title.toLowerCase().includes(settingsLower) ||
          opt.description.toLowerCase().includes(settingsLower)
        );
        suggestions.push(...filtered.slice(0, 3));
        if (suggestions.length === 0) {
          suggestions.push(...advancedOptions.slice(0, 3));
        }
      }
    }

    setSettingsSuggestions(suggestions);
  }, [selectedAnalysis, activeSettingType, settingsInput]);

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


  const selectAnalysis = (category: PredictedCategory) => {
    setSelectedAnalysis(category);
    setPredictedCategories([]);
    setInput('');
    setSettingsInput('');
    setActiveSettingType(null);
    setSelectedSettings(getDefaultSettings()); // Set default settings
    setIsFormExpanded(false);
    setSelectedQuestion('');
  };

  const backToAnalysisSelection = () => {
    setSelectedAnalysis(null);
    setSettingsInput('');
    setSettingsSuggestions([]);
    setActiveSettingType(null);
    setSelectedSettings({});
    setIsFormExpanded(false);
    setSelectedQuestion('');
  };

  const selectSetting = (suggestion: {
    id: string;
    title: string;
    description: string;
    emoji: string;
  }) => {
    // Update selected settings for the active setting type
    if (activeSettingType) {
      const newSettings = { ...selectedSettings };
      newSettings[activeSettingType] = suggestion.title;
      setSelectedSettings(newSettings);
      setSettingsInput('');
      setSelectedQuestion(''); // Clear selected question so it updates dynamically based on new settings
      // Keep the setting panel open after selection - don't set activeSettingType to null
    }
  };

  const clickSettingBadge = (settingType: string) => {
    setActiveSettingType(settingType);
    setSettingsInput('');
  };

  const selectSuggestedQuestion = (suggestedQ: typeof suggestedQuestions[0]) => {
    // Find the corresponding analysis type and create a mock category
    const analysisMap = {
      'portfolio_performance': predictedCategories.find(c => c.id === 'portfolio_performance'),
      'portfolio_risk': predictedCategories.find(c => c.id === 'portfolio_risk'), 
      'portfolio_rebalance': predictedCategories.find(c => c.id === 'portfolio_rebalance')
    };

    const baseAnalysis = analysisMap[suggestedQ.analysisType as keyof typeof analysisMap];
    
    if (baseAnalysis) {
      // Create a customized analysis based on the suggested question
      const customAnalysis: PredictedCategory = {
        ...baseAnalysis,
        id: `${baseAnalysis.id}_${suggestedQ.id}`,
        title: `${baseAnalysis.title} (${suggestedQ.question})`,
        suggestedQuestion: suggestedQ.question
      };

      setSelectedAnalysis(customAnalysis);
      setSelectedSettings(suggestedQ.settings);
      setPredictedCategories([]);
      setInput('');
      setActiveSettingType(null);
      setIsFormExpanded(false);
    }
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
          /* Single Analysis Mode - Clickable Config + Expand/Collapse */
          <div className="space-y-6">
            {/* Analysis Focus Card with Current Config */}
            <div className="bg-white rounded-lg border border-blue-300 border-2 p-6">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <span className="text-xl">{selectedAnalysis.emoji}</span>
                </div>
                <div className="flex-1">
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">
                    {selectedAnalysis.title}
                  </h2>
                  <p className="text-gray-600 mb-2">
                    {selectedAnalysis.description}
                  </p>

                  {/* Primary Question Based on Current Settings */}
                  <div className="mb-4 p-3 bg-gray-50 border-l-4 border-blue-500 rounded">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-start gap-2 flex-1">
                        <span className="text-blue-500 mt-0.5">❓</span>
                        <div className="flex-1">
                          <div className="text-xs text-gray-500 mb-1">Suggested question based on your settings:</div>
                          <div className="text-sm text-gray-800 font-medium">
                            {getPrimaryQuestion()}
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => {
                          console.log('Running analysis:', getPrimaryQuestion());
                          alert(`Starting analysis: ${getPrimaryQuestion()}`);
                        }}
                        className="px-3 py-1.5 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 transition-colors whitespace-nowrap"
                      >
                        🚀 Run Analysis
                      </button>
                    </div>
                  </div>
                  
                  {/* Current Configuration - Clickable Badges */}
                  <div className="bg-blue-50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-sm font-medium text-blue-900">Current Configuration:</h4>
                      <button
                        onClick={() => setIsFormExpanded(!isFormExpanded)}
                        className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
                      >
                        {isFormExpanded ? '↑ Collapse' : '↓ Expand Full Form'}
                      </button>
                    </div>
                    <div className="flex flex-wrap gap-2 mb-4">
                      {Object.entries(selectedSettings).map(([settingType, setting]) => {
                        const type = settingTypes.find(t => t.id === settingType);
                        return (
                          <button
                            key={settingType}
                            onClick={() => clickSettingBadge(settingType)}
                            className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm transition-all ${
                              activeSettingType === settingType
                                ? 'bg-blue-200 text-blue-800 border border-blue-300'
                                : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                            }`}
                          >
                            <span>{type?.emoji}</span>
                            <span>{type?.label}: {setting}</span>
                            <span className="text-blue-500">✎</span>
                          </button>
                        );
                      })}
                    </div>

                    {/* Settings Tabs/Tiles Below Configuration */}
                    {activeSettingType && (
                      <div className="border-t border-blue-200 pt-4">
                        <div className="flex items-center justify-between mb-3">
                          <h5 className="text-sm font-medium text-blue-800">
                            Configure {settingTypes.find(t => t.id === activeSettingType)?.label} Settings:
                          </h5>
                          <button
                            onClick={() => setActiveSettingType(null)}
                            className="text-xs text-blue-600 hover:text-blue-700"
                          >
                            ✕ Close
                          </button>
                        </div>
                        
                        {/* Compact Setting Options as Tiles */}
                        {settingsSuggestions.length > 0 && (
                          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                            {settingsSuggestions.map((suggestion) => (
                              <button
                                key={suggestion.id}
                                onClick={() => selectSetting(suggestion)}
                                className={`text-left p-2 rounded-md border transition-all text-xs ${
                                  selectedSettings[activeSettingType] === suggestion.title
                                    ? 'bg-blue-100 border-blue-300 text-blue-800'
                                    : 'bg-white border-gray-200 hover:bg-blue-50 hover:border-blue-300'
                                }`}
                              >
                                <div className="flex items-center gap-2">
                                  <span className="text-sm">{suggestion.emoji}</span>
                                  <div className="flex-1 min-w-0">
                                    <div className="font-medium truncate">{suggestion.title}</div>
                                    <div className="text-gray-500 text-xs truncate">{suggestion.description}</div>
                                  </div>
                                  {selectedSettings[activeSettingType] === suggestion.title && (
                                    <span className="text-green-600 text-xs">✓</span>
                                  )}
                                </div>
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                  </div>
                </div>
              </div>

              {/* Expanded Form View */}
              {isFormExpanded && (
                <div className="mt-6 pt-4 border-t border-gray-200">
                  <h4 className="text-lg font-medium text-gray-900 mb-4">Complete Configuration</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Basic Settings */}
                    <div>
                      <h5 className="font-medium text-gray-900 mb-3">Basic Settings</h5>
                      <div className="space-y-3">
                        {selectedAnalysis.fields.map((field) => (
                          <div key={field.id}>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              {field.label}
                            </label>
                            {renderField(field, selectedAnalysis.id, false)}
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Advanced Settings */}
                    {selectedAnalysis.expandedFields && (
                      <div>
                        <h5 className="font-medium text-gray-900 mb-3">Advanced Options</h5>
                        <div className="space-y-3">
                          {selectedAnalysis.expandedFields.map((field) => (
                            <div key={field.id}>
                              <label className="block text-sm font-medium text-gray-700 mb-1">
                                {field.label}
                              </label>
                              {renderField(field, selectedAnalysis.id, true)}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>


            {/* Dynamic Suggested Questions Based on Settings */}
            {selectedAnalysis && (
              <div className="bg-white rounded-lg border border-gray-200 p-4">
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-lg">💡</span>
                  <h4 className="text-sm font-medium text-gray-700">
                    Suggested questions
                    {Object.keys(selectedSettings).length > 0 
                      ? ' (updated based on your settings)' 
                      : ' (configure settings to see personalized suggestions)'
                    }:
                  </h4>
                  <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                    {generateDynamicQuestions().length} available
                  </span>
                  {Object.keys(selectedSettings).length > 0 && (
                    <span className="text-xs text-blue-600 bg-blue-100 px-2 py-1 rounded-full animate-pulse">
                      ✨ Live
                    </span>
                  )}
                </div>
                
                {generateDynamicQuestions().length > 0 ? (
                  <div className="space-y-2">
                    {generateDynamicQuestions().map((question, idx) => (
                      <button
                        key={question.id}
                        onClick={() => {
                          setSettingsFromQuestion(question.text);
                          setSelectedQuestion(question.text);
                          // Scroll to the settings card to show the selected question
                          window.scrollTo({ top: 0, behavior: 'smooth' });
                        }}
                        className="w-full text-left p-3 rounded-md border border-gray-200 hover:bg-blue-50 hover:border-blue-300 transition-all group"
                      >
                        <div className="flex items-start gap-3">
                          <span className="text-base mt-0.5 group-hover:scale-110 transition-transform">
                            {question.emoji}
                          </span>
                          <div className="flex-1">
                            <span className="text-sm text-gray-700 group-hover:text-blue-700 transition-colors">
                              {question.text}
                            </span>
                            <div className="flex items-center gap-2 mt-1">
                              <span className={`text-xs px-2 py-0.5 rounded-full ${
                                question.confidence === 'high' 
                                  ? 'bg-green-100 text-green-700' 
                                  : 'bg-yellow-100 text-yellow-700'
                              }`}>
                                {question.confidence} confidence
                              </span>
                              <span className="text-xs text-gray-400">
                                Click to select for analysis
                              </span>
                            </div>
                          </div>
                          <svg 
                            className="w-4 h-4 text-gray-400 group-hover:text-blue-500 transition-colors" 
                            fill="none" 
                            stroke="currentColor" 
                            viewBox="0 0 24 24"
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 11l5-5m0 0l5 5m-5-5v12" />
                          </svg>
                        </div>
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-6 text-gray-500">
                    <span className="text-2xl mb-2 block">🔄</span>
                    <p className="text-sm">
                      Loading questions...
                    </p>
                  </div>
                )}
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
                return (
                  <div
                    key={category.id}
                    className="bg-white rounded-lg border border-gray-200 p-4 hover:border-blue-300 transition-all"
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