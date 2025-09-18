'use client';

import { useState, useEffect } from 'react';
import { PredictedCategory, SelectedSettings, SettingType, SettingSuggestion, SuggestedQuestion } from './types';

interface AnalysisConfiguratorProps {
  selectedAnalysis: PredictedCategory;
  onBack: () => void;
  onSubmit: (question: string) => void;
  className?: string;
}

export default function AnalysisConfigurator({
  selectedAnalysis,
  onBack,
  onSubmit,
  className = ""
}: AnalysisConfiguratorProps) {
  const [activeSettingType, setActiveSettingType] = useState<string | null>(null);
  const [settingsInput, setSettingsInput] = useState('');
  const [settingsSuggestions, setSettingsSuggestions] = useState<SettingSuggestion[]>([]);
  const [selectedSettings, setSelectedSettings] = useState<SelectedSettings>({});
  const [selectedQuestion, setSelectedQuestion] = useState<string>('');

  // Initialize default settings
  useEffect(() => {
    setSelectedSettings({
      time_settings: 'Monthly Analysis',
      risk_settings: 'Value at Risk',
      comparison_settings: 'S&P 500 Benchmark',
      advanced_settings: 'Transaction Costs'
    });
  }, []);

  // Define setting types
  const settingTypes: SettingType[] = [
    { id: 'time_settings', label: 'Time', emoji: '⏰' },
    { id: 'risk_settings', label: 'Risk', emoji: '🛡️' },
    { id: 'comparison_settings', label: 'Compare', emoji: '📊' },
    { id: 'advanced_settings', label: 'Advanced', emoji: '⚙️' }
  ];

  // Generate dynamic questions based on current settings
  const generateDynamicQuestions = (): SuggestedQuestion[] => {
    if (!selectedAnalysis) return [];

    const questions: SuggestedQuestion[] = [];
    const timeSettings = selectedSettings.time_settings;
    const riskSettings = selectedSettings.risk_settings;
    const comparisonSettings = selectedSettings.comparison_settings;
    const advancedSettings = selectedSettings.advanced_settings;

    // Add time-specific questions first (more specific/varied)
    if (timeSettings) {
      const timeQuestions = {
        'Daily Analysis': [
          { text: `What was my portfolio performance yesterday with ${riskSettings?.toLowerCase() || 'risk analysis'}?`, emoji: '📅', confidence: 'high' as const },
          { text: `What is my daily ${riskSettings?.toLowerCase() || 'risk'} vs ${comparisonSettings?.toLowerCase() || 'market'}?`, emoji: '📊', confidence: 'high' as const }
        ],
        'Weekly Analysis': [
          { text: `How did my portfolio perform this week using ${riskSettings?.toLowerCase() || 'risk metrics'}?`, emoji: '📈', confidence: 'high' as const },
          { text: `What were my weekly ${riskSettings?.toLowerCase() || 'risk'} levels compared to ${comparisonSettings?.toLowerCase() || 'benchmarks'}?`, emoji: '📊', confidence: 'high' as const }
        ],
        'Monthly Analysis': [
          { text: `What is my month-to-date ${riskSettings?.toLowerCase() || 'portfolio performance'}?`, emoji: '📅', confidence: 'high' as const },
          { text: `How does my monthly ${riskSettings?.toLowerCase() || 'risk profile'} compare to ${comparisonSettings?.toLowerCase() || 'market standards'}?`, emoji: '📊', confidence: 'high' as const }
        ],
        'Quarterly Analysis': [
          { text: `How did my ${riskSettings?.toLowerCase() || 'portfolio'} perform this quarter vs ${comparisonSettings?.toLowerCase() || 'benchmarks'}?`, emoji: '🗓️', confidence: 'high' as const },
          { text: `What are my quarterly ${riskSettings?.toLowerCase() || 'risk'} metrics with ${advancedSettings?.toLowerCase() || 'advanced analysis'}?`, emoji: '📊', confidence: 'high' as const }
        ]
      };
      
      const timeQuestionsArray = timeQuestions[timeSettings as keyof typeof timeQuestions];
      if (timeQuestionsArray) {
        timeQuestionsArray.forEach((q, idx) => {
          questions.push({
            id: `time_${timeSettings}_${idx}`,
            ...q
          });
        });
      }
    }

    // Add comprehensive questions using ALL settings
    if (timeSettings && riskSettings && comparisonSettings && advancedSettings) {
      questions.push({
        id: 'comprehensive_summary',
        text: `Complete ${timeSettings.toLowerCase()} analysis: ${riskSettings.toLowerCase()} vs ${comparisonSettings.toLowerCase()} with ${advancedSettings.toLowerCase()}`,
        emoji: '🎯',
        confidence: 'high' as const
      });
    }

    return questions.length > 0 ? questions.slice(0, 3) : [
      {
        id: 'fallback',
        text: selectedAnalysis?.suggestedQuestion || 'Configure your analysis settings to see personalized questions',
        emoji: '💡',
        confidence: 'medium' as const
      }
    ];
  };

  // Infer settings from a question and update them
  const setSettingsFromQuestion = (question: string) => {
    const questionLower = question.toLowerCase();
    const newSettings: Partial<SelectedSettings> = {};

    // Infer time settings
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
    }

    // Infer risk settings
    if (questionLower.includes('value at risk') || questionLower.includes('var')) {
      newSettings.risk_settings = 'Value at Risk';
    } else if (questionLower.includes('volatility analysis') || questionLower.includes('volatile') || 
               questionLower.includes('volatility')) {
      newSettings.risk_settings = 'Volatility Analysis';
    } else if (questionLower.includes('maximum drawdown') || questionLower.includes('drawdown')) {
      newSettings.risk_settings = 'Maximum Drawdown';
    } else if (questionLower.includes('beta analysis') || questionLower.includes('beta')) {
      newSettings.risk_settings = 'Beta Analysis';
    }

    // Infer comparison settings
    if (questionLower.includes('s&p 500 benchmark') || questionLower.includes('s&p 500') || 
        questionLower.includes('market')) {
      newSettings.comparison_settings = 'S&P 500 Benchmark';
    } else if (questionLower.includes('sector comparison') || questionLower.includes('sector') || 
               questionLower.includes('peers')) {
      newSettings.comparison_settings = 'Sector Comparison';
    }

    // Infer advanced settings
    if (questionLower.includes('transaction costs') || questionLower.includes('trading cost')) {
      newSettings.advanced_settings = 'Transaction Costs';
    } else if (questionLower.includes('rebalancing logic') || questionLower.includes('rebalance')) {
      newSettings.advanced_settings = 'Rebalancing Logic';
    }

    const finalSettings = { ...selectedSettings, ...newSettings };
    setSelectedSettings(finalSettings);
  };

  // Get the primary suggested question
  const getPrimaryQuestion = () => {
    if (selectedQuestion) {
      return selectedQuestion;
    }
    
    const questions = generateDynamicQuestions();
    return questions.length > 0 ? questions[0].text : selectedAnalysis?.suggestedQuestion || 'Select settings to see a personalized question';
  };

  // Setting-type-based auto-complete
  useEffect(() => {
    if (!selectedAnalysis || !activeSettingType) {
      setSettingsSuggestions([]);
      return;
    }

    const suggestions: SettingSuggestion[] = [];

    // Time Settings
    if (activeSettingType === 'time_settings') {
      const timeOptions = [
        { id: 'daily_frequency', title: 'Daily Analysis', description: 'Day-by-day performance tracking', emoji: '📅' },
        { id: 'weekly_frequency', title: 'Weekly Analysis', description: 'Week-over-week trends', emoji: '📊' },
        { id: 'monthly_frequency', title: 'Monthly Analysis', description: 'Monthly performance review', emoji: '📈' },
        { id: 'quarterly_frequency', title: 'Quarterly Analysis', description: 'Quarterly business cycles', emoji: '🗓️' }
      ];
      suggestions.push(...timeOptions.slice(0, 4));
    }
    // Risk Settings
    else if (activeSettingType === 'risk_settings') {
      const riskOptions = [
        { id: 'value_at_risk', title: 'Value at Risk', description: '95% confidence VaR calculation', emoji: '💥' },
        { id: 'volatility_analysis', title: 'Volatility Analysis', description: 'Standard deviation & EWMA', emoji: '📉' },
        { id: 'maximum_drawdown', title: 'Maximum Drawdown', description: 'Peak-to-trough decline', emoji: '📊' },
        { id: 'beta_analysis', title: 'Beta Analysis', description: 'Market sensitivity measurement', emoji: '🎯' }
      ];
      suggestions.push(...riskOptions.slice(0, 4));
    }
    // Comparison Settings
    else if (activeSettingType === 'comparison_settings') {
      const comparisonOptions = [
        { id: 'sp500_benchmark', title: 'S&P 500 Benchmark', description: 'Compare against SPY index', emoji: '🏛️' },
        { id: 'sector_comparison', title: 'Sector Comparison', description: 'Compare vs sector ETFs', emoji: '🏭' },
        { id: 'peer_analysis', title: 'Peer Analysis', description: 'Similar funds & strategies', emoji: '👥' },
        { id: 'custom_benchmark', title: 'Custom Benchmark', description: 'Build your own comparison', emoji: '🎨' }
      ];
      suggestions.push(...comparisonOptions.slice(0, 4));
    }
    // Advanced Settings
    else if (activeSettingType === 'advanced_settings') {
      const advancedOptions = [
        { id: 'transaction_costs', title: 'Transaction Costs', description: 'Trading fees & slippage', emoji: '💸' },
        { id: 'rebalancing_logic', title: 'Rebalancing Logic', description: 'Automatic portfolio rebalancing', emoji: '⚖️' },
        { id: 'tax_optimization', title: 'Tax Optimization', description: 'Tax-efficient strategies', emoji: '🏛️' },
        { id: 'liquidity_analysis', title: 'Liquidity Analysis', description: 'Market impact assessment', emoji: '💧' }
      ];
      suggestions.push(...advancedOptions.slice(0, 4));
    }

    setSettingsSuggestions(suggestions);
  }, [selectedAnalysis, activeSettingType, settingsInput]);

  const selectSetting = (suggestion: SettingSuggestion) => {
    if (activeSettingType) {
      const newSettings = { ...selectedSettings };
      newSettings[activeSettingType] = suggestion.title;
      setSelectedSettings(newSettings);
      setSettingsInput('');
      setSelectedQuestion(''); // Clear selected question so it updates dynamically
    }
  };

  const clickSettingBadge = (settingType: string) => {
    setActiveSettingType(settingType);
    setSettingsInput('');
  };

  return (
    <div className={className}>
      {/* Analysis Focus Card */}
      <div className="bg-white rounded-lg border border-blue-300 border-2 p-6 space-y-6">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <span className="text-xl">{selectedAnalysis.emoji}</span>
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <h2 className="text-xl font-semibold text-gray-900">
                {selectedAnalysis.title}
              </h2>
              <button
                onClick={onBack}
                className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
              >
                ← Back
              </button>
            </div>
            <p className="text-gray-600 mb-4">
              {selectedAnalysis.description}
            </p>

            {/* Primary Question */}
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
                  onClick={() => onSubmit(getPrimaryQuestion())}
                  className="px-3 py-1.5 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 transition-colors whitespace-nowrap"
                >
                  🚀 Run Analysis
                </button>
              </div>
            </div>
            
            {/* Current Configuration */}
            <div className="bg-blue-50 rounded-lg p-4">
              <h4 className="text-sm font-medium text-blue-900 mb-3">Current Configuration:</h4>
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

              {/* Settings Configuration */}
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
      </div>

      {/* Dynamic Suggested Questions */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-lg">💡</span>
          <h4 className="text-sm font-medium text-gray-700">
            Suggested questions based on your settings:
          </h4>
          <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
            {generateDynamicQuestions().length} available
          </span>
        </div>
        
        <div className="space-y-2">
          {generateDynamicQuestions().map((question) => (
            <button
              key={question.id}
              onClick={() => {
                setSettingsFromQuestion(question.text);
                setSelectedQuestion(question.text);
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
      </div>
    </div>
  );
}