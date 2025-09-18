'use client';

import { useRef, useEffect, useState } from 'react';
import MockOutput from '@/components/MockOutput';
import { AutocompleteInput } from '@/components/autocomplete';

interface ChatMessage {
  id: string;
  type: 'user' | 'ai' | 'thinking' | 'analyzing' | 'results' | 'interactive';
  content: string;
  timestamp: Date;
  moduleKey?: string;
  isTyping?: boolean;
  isExpanded?: boolean;
}

interface ChatInterfaceProps {
  messages: ChatMessage[];
  chatInput: string;
  setChatInput: (value: string) => void;
  isProcessing: boolean;
  onSendMessage: (message: string) => void;
  onExpandToggle: (messageId: string) => void;
  expandedResults: Set<string>;
  onCustomizeAnalysis?: (moduleKey: string) => void;
}

export default function ChatInterface({
  messages,
  chatInput,
  setChatInput,
  isProcessing,
  onSendMessage,
  onExpandToggle,
  expandedResults,
  onCustomizeAnalysis
}: ChatInterfaceProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [showInput, setShowInput] = useState(false);
  const [showAdvancedInput, setShowAdvancedInput] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [interactiveForm, setInteractiveForm] = useState<{
    category: string;
    fields: Array<{
      id: string;
      label: string;
      type: 'select' | 'input' | 'multiselect';
      options?: string[];
      value?: any;
    }>;
  } | null>(null);

  // Smart analysis suggestions with intent-based approach
  const analysisOptions = [
    {
      title: "Quick balanced portfolio check",
      description: "Mixed assets • Moderate risk • 12-month review",
      emoji: "📊"
    },
    {
      title: "High-growth tech strategy", 
      description: "FAANG stocks • Aggressive growth • 2-year analysis",
      emoji: "🚀"
    },
    {
      title: "Safe dividend income focus",
      description: "Dividend aristocrats • Low risk • Steady income",
      emoji: "💰"
    },
    {
      title: "Aggressive momentum trading",
      description: "High-momentum ETFs • Quick profits • 6-month focus", 
      emoji: "⚡"
    },
    {
      title: "Custom analysis setup",
      description: "Tell me exactly what you want to analyze",
      emoji: "⚙️"
    }
  ];

  // Comprehensive suggestion database for auto-complete
  const allSuggestions = [
    // Portfolio Analysis
    "How is my portfolio performing this quarter?",
    "What's the risk profile of my current holdings?",
    "Should I rebalance my portfolio now?",
    "How diversified is my portfolio?",
    "What's my portfolio's beta compared to the market?",
    "Analyze my portfolio's correlation with the S&P 500",
    "What's my portfolio's Sharpe ratio?",
    
    // Stock Analysis
    "Analyze AAPL stock performance",
    "Compare AAPL vs MSFT returns",
    "What are the best tech stocks to buy?",
    "Show me momentum signals for TSLA",
    "Is NVDA overbought or oversold?",
    "What's the RSI for QQQ?",
    "Analyze dividend yield for KO",
    
    // Strategy & Trading
    "Build a momentum trading strategy",
    "Create a mean reversion strategy for SPY",
    "Test a moving average crossover strategy",
    "What's the best entry point for growth stocks?",
    "Show me breakout patterns in tech stocks",
    "Analyze support and resistance levels",
    "What are the best swing trading signals?",
    
    // Risk Management
    "What's my maximum drawdown risk?",
    "Calculate Value at Risk for my portfolio",
    "How much should I invest in crypto?",
    "What's the optimal position size for AAPL?",
    "Stress test my portfolio against market crashes",
    "What's my portfolio's volatility?",
    
    // Market Analysis
    "What sectors are outperforming this month?",
    "Show me the most active stocks today",
    "What are the top gainers in tech?",
    "Analyze market sentiment for financials",
    "What's the market outlook for next quarter?",
    "Compare growth vs value stocks performance",
    
    // Specific Scenarios
    "Help me plan for retirement investing",
    "What's a good dividend income strategy?",
    "How to hedge against inflation?",
    "Best defensive stocks for a recession?",
    "Growth stocks for aggressive portfolios"
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Interactive auto-suggest with smart form detection
  useEffect(() => {
    if (chatInput.length > 2) {
      const input = chatInput.toLowerCase();
      
      // Detect category and show interactive form
      if (input.includes('portfolio') || input.includes('allocation') || input.includes('diversif')) {
        setInteractiveForm({
          category: 'Portfolio Analysis',
          fields: [
            {
              id: 'analysis_type',
              label: 'What do you want to analyze?',
              type: 'select',
              options: ['Performance vs benchmark', 'Risk assessment', 'Diversification check', 'Rebalancing needs'],
              value: 'Performance vs benchmark'
            },
            {
              id: 'time_period',
              label: 'Time period',
              type: 'select',
              options: ['Last month', 'Last quarter', 'Last year', 'Since inception'],
              value: 'Last quarter'
            },
            {
              id: 'benchmark',
              label: 'Compare against',
              type: 'select',
              options: ['S&P 500 (SPY)', 'NASDAQ (QQQ)', 'Russell 2000 (IWM)', 'Custom benchmark'],
              value: 'S&P 500 (SPY)'
            }
          ]
        });
        setShowSuggestions(false);
      } else if (input.includes('stock') || input.includes('analyze') || input.includes('compare')) {
        setInteractiveForm({
          category: 'Stock Analysis',
          fields: [
            {
              id: 'symbols',
              label: 'Stock symbols',
              type: 'input',
              value: extractSymbols(input)
            },
            {
              id: 'analysis_type',
              label: 'Analysis type',
              type: 'select',
              options: ['Technical analysis', 'Fundamental analysis', 'Comparison study', 'Risk metrics'],
              value: 'Technical analysis'
            },
            {
              id: 'indicators',
              label: 'Technical indicators',
              type: 'multiselect',
              options: ['RSI', 'MACD', 'Moving Averages', 'Bollinger Bands', 'Volume'],
              value: ['RSI', 'Moving Averages']
            }
          ]
        });
        setShowSuggestions(false);
      } else if (input.includes('strategy') || input.includes('trading') || input.includes('backtest')) {
        setInteractiveForm({
          category: 'Strategy Builder',
          fields: [
            {
              id: 'strategy_type',
              label: 'Strategy type',
              type: 'select',
              options: ['Momentum', 'Mean reversion', 'Breakout', 'Trend following', 'Custom'],
              value: 'Momentum'
            },
            {
              id: 'symbols',
              label: 'Test on symbols',
              type: 'input',
              value: 'SPY, QQQ'
            },
            {
              id: 'timeframe',
              label: 'Timeframe',
              type: 'select',
              options: ['1 minute', '5 minutes', '1 hour', '1 day', '1 week'],
              value: '1 day'
            },
            {
              id: 'period',
              label: 'Backtest period',
              type: 'select',
              options: ['Last 3 months', 'Last year', 'Last 2 years', 'Last 5 years'],
              value: 'Last year'
            }
          ]
        });
        setShowSuggestions(false);
      } else if (input.includes('risk') || input.includes('volatility') || input.includes('var')) {
        setInteractiveForm({
          category: 'Risk Analysis',
          fields: [
            {
              id: 'risk_metric',
              label: 'Risk metric',
              type: 'select',
              options: ['Value at Risk (VaR)', 'Expected Shortfall', 'Maximum Drawdown', 'Beta analysis', 'Volatility'],
              value: 'Value at Risk (VaR)'
            },
            {
              id: 'confidence_level',
              label: 'Confidence level',
              type: 'select',
              options: ['90%', '95%', '99%'],
              value: '95%'
            },
            {
              id: 'time_horizon',
              label: 'Time horizon',
              type: 'select',
              options: ['1 day', '1 week', '1 month', '1 quarter'],
              value: '1 month'
            }
          ]
        });
        setShowSuggestions(false);
      } else {
        // Fallback to text suggestions
        const filteredSuggestions = allSuggestions
          .filter(suggestion => 
            suggestion.toLowerCase().includes(input)
          )
          .slice(0, 5);
        
        setSuggestions(filteredSuggestions);
        setShowSuggestions(filteredSuggestions.length > 0);
        setInteractiveForm(null);
      }
    } else {
      setShowSuggestions(false);
      setSuggestions([]);
      setInteractiveForm(null);
    }
  }, [chatInput]);

  // Helper function to extract stock symbols from text
  const extractSymbols = (text: string): string => {
    const matches = text.match(/\b[A-Z]{1,5}\b/g);
    return matches ? matches.slice(0, 3).join(', ') : 'AAPL, MSFT';
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (chatInput.trim() && !isProcessing) {
      onSendMessage(chatInput.trim());
      setChatInput('');
      setShowInput(false); // Hide input after sending
      setShowAdvancedInput(false); // Hide advanced input after sending
      setShowSuggestions(false); // Hide suggestions after sending
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setChatInput(suggestion);
    setShowSuggestions(false);
    // Auto-submit the suggestion
    onSendMessage(suggestion);
    setChatInput('');
    setShowInput(false);
  };

  const handleInteractiveFormSubmit = () => {
    if (!interactiveForm) return;
    
    // Build natural language query from form data
    let query = `Run ${interactiveForm.category.toLowerCase()} with: `;
    const params = interactiveForm.fields.map(field => {
      if (Array.isArray(field.value)) {
        return `${field.label}: ${field.value.join(', ')}`;
      }
      return `${field.label}: ${field.value}`;
    }).join(', ');
    
    query += params;
    
    onSendMessage(query);
    setChatInput('');
    setShowInput(false);
    setInteractiveForm(null);
  };

  const updateFormField = (fieldId: string, value: any) => {
    if (!interactiveForm) return;
    
    setInteractiveForm({
      ...interactiveForm,
      fields: interactiveForm.fields.map(field => 
        field.id === fieldId ? { ...field, value } : field
      )
    });
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setChatInput(e.target.value);
  };

  const handleAnalysisOption = (option: { title: string; description: string; emoji: string }) => {
    // For custom analysis, show input
    if (option.title.toLowerCase().includes('custom')) {
      setShowInput(true);
      return;
    }
    
    // For preset options, send as message with intent
    onSendMessage(`I want to run a ${option.title.toLowerCase()} analysis`);
  };

  const renderMessage = (message: ChatMessage) => {
    const isUser = message.type === 'user';
    
    return (
      <div key={message.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3`}>
        <div className={`${isUser ? 'max-w-xs' : 'w-full'} px-3 py-2 rounded-lg text-sm ${
          isUser 
            ? 'bg-blue-600 text-white' 
            : message.type === 'thinking' 
              ? 'bg-gray-100 text-gray-600'
              : message.type === 'analyzing'
                ? 'bg-yellow-50 text-yellow-800'
                : 'bg-gray-100 text-gray-800'
        }`}>
          {message.type === 'thinking' && (
            <div className="flex items-center gap-2">
              <div className="flex gap-1">
                <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"></div>
              </div>
              <span className="text-gray-600 text-xs">Thinking...</span>
            </div>
          )}
          
          {message.type === 'analyzing' && (
            <div className="flex items-center gap-2">
              <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-yellow-600"></div>
              <span className="text-gray-700 text-xs">Analyzing...</span>
            </div>
          )}
          
          {message.type === 'results' && (
            <div>
              <div className="flex justify-between items-center mb-2 cursor-pointer" 
                   onClick={() => onExpandToggle(message.id)}>
                <h4 className="font-medium text-gray-900 text-sm flex items-center gap-2">
                  <div className="w-5 h-5 bg-green-100 rounded-full flex items-center justify-center">
                    <svg className="w-3 h-3 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  Analysis Complete
                </h4>
                <svg 
                  className={`w-4 h-4 text-gray-500 transform transition-transform ${
                    expandedResults.has(message.id) ? 'rotate-180' : ''
                  }`} 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
              
              {expandedResults.has(message.id) && message.moduleKey && (
                <div className="mt-3">
                  <MockOutput moduleKey={message.moduleKey} />
                </div>
              )}
            </div>
          )}
          
          {message.type === 'interactive' && onCustomizeAnalysis && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p className="text-sm text-gray-700 mb-3">
                Would you like to customize this analysis with different parameters?
              </p>
              <button
                onClick={() => onCustomizeAnalysis(message.moduleKey!)}
                className="w-full px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
              >
                🎛️ Customize Analysis
              </button>
            </div>
          )}
          
          {(message.type === 'user' || message.type === 'ai') && (
            <div className="whitespace-pre-wrap">{message.content}</div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {messages.map(renderMessage)}
        <div ref={messagesEndRef} />
      </div>

      {/* Bottom Section - Suggested Questions or Input */}
      <div className="border-t border-gray-200 p-4">
        {showAdvancedInput ? (
          /* Advanced Autocomplete Mode */
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Smart Analysis Builder</span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    setShowAdvancedInput(false);
                    setShowInput(true);
                  }}
                  className="text-xs text-blue-600 hover:text-blue-700"
                >
                  Simple Mode
                </button>
                <button
                  onClick={() => setShowAdvancedInput(false)}
                  className="text-xs text-gray-500 hover:text-gray-700"
                >
                  ✕ Close
                </button>
              </div>
            </div>
            <AutocompleteInput
              input={chatInput}
              setInput={setChatInput}
              onSubmit={(question) => {
                onSendMessage(question);
                setShowAdvancedInput(false);
                setChatInput('');
              }}
              placeholder="Type 'portfolio', 'stock', or 'risk' to see smart suggestions..."
              className="space-y-4"
            />
          </div>
        ) : showInput ? (
          /* Simple Input Mode */
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Ask a custom question</span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    setShowInput(false);
                    setShowAdvancedInput(true);
                  }}
                  className="text-xs text-blue-600 hover:text-blue-700"
                >
                  Advanced Mode
                </button>
                <button
                  onClick={() => setShowInput(false)}
                  className="text-xs text-gray-500 hover:text-gray-700"
                >
                  ✕ Close
                </button>
              </div>
            </div>
            <div className="relative">
              <form onSubmit={handleSubmit}>
                <input
                  type="text"
                  value={chatInput}
                  onChange={handleInputChange}
                  placeholder="Ask about portfolio analysis, trading strategies, risk assessment..."
                  className="w-full px-4 py-2 pr-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isProcessing}
                  autoFocus
                />
                <button
                  type="submit"
                  disabled={isProcessing || !chatInput.trim()}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1.5 text-blue-600 hover:text-blue-700 disabled:text-gray-400"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                </button>
              </form>

              {/* Interactive form or text suggestions */}
              {interactiveForm ? (
                <div className="absolute bottom-full left-0 right-0 mb-2 bg-white border border-gray-200 rounded-lg shadow-xl z-10">
                  <div className="p-4">
                    {/* Header */}
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        <span className="text-lg">🎯</span>
                        <h4 className="font-semibold text-gray-900">{interactiveForm.category}</h4>
                      </div>
                      <button
                        onClick={() => setInteractiveForm(null)}
                        className="text-gray-400 hover:text-gray-600"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>

                    {/* Form fields */}
                    <div className="space-y-3">
                      {interactiveForm.fields.map((field) => (
                        <div key={field.id}>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            {field.label}
                          </label>
                          
                          {field.type === 'select' && (
                            <select
                              value={field.value}
                              onChange={(e) => updateFormField(field.id, e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                            >
                              {field.options?.map((option) => (
                                <option key={option} value={option}>{option}</option>
                              ))}
                            </select>
                          )}
                          
                          {field.type === 'input' && (
                            <input
                              type="text"
                              value={field.value}
                              onChange={(e) => updateFormField(field.id, e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                              placeholder={`Enter ${field.label.toLowerCase()}`}
                            />
                          )}
                          
                          {field.type === 'multiselect' && (
                            <div className="flex flex-wrap gap-2">
                              {field.options?.map((option) => {
                                const isSelected = field.value?.includes(option);
                                return (
                                  <button
                                    key={option}
                                    onClick={() => {
                                      const currentValues = field.value || [];
                                      const newValues = isSelected
                                        ? currentValues.filter((v: string) => v !== option)
                                        : [...currentValues, option];
                                      updateFormField(field.id, newValues);
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
                          )}
                        </div>
                      ))}
                    </div>

                    {/* Submit button */}
                    <div className="mt-4 pt-3 border-t border-gray-100">
                      <button
                        onClick={handleInteractiveFormSubmit}
                        className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm font-medium"
                      >
                        🚀 Run Analysis
                      </button>
                    </div>
                  </div>
                </div>
              ) : showSuggestions && suggestions.length > 0 ? (
                <div className="absolute bottom-full left-0 right-0 mb-2 bg-white border border-gray-200 rounded-lg shadow-lg z-10 max-h-60 overflow-y-auto">
                  <div className="p-2">
                    <div className="text-xs text-gray-500 px-2 py-1 border-b border-gray-100">
                      Suggestions:
                    </div>
                    {suggestions.map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => handleSuggestionClick(suggestion)}
                        className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-700 rounded-md transition-colors"
                      >
                        <div className="flex items-start gap-2">
                          <span className="text-blue-500 mt-0.5">💡</span>
                          <span className="flex-1">{suggestion}</span>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>
          </div>
        ) : (
          /* Analysis Options Mode */
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">What kind of analysis are you looking for?</span>
            </div>
            
            <div className="grid grid-cols-1 gap-3">
              {/* Advanced Autocomplete Option */}
              <button
                onClick={() => setShowAdvancedInput(true)}
                disabled={isProcessing}
                className="text-left p-4 bg-gradient-to-r from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 rounded-lg border-2 border-blue-200 hover:border-blue-300 transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
              >
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 bg-blue-200 group-hover:bg-blue-300 rounded-lg flex items-center justify-center transition-colors">
                    <span className="text-lg">🎯</span>
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-gray-900 text-sm mb-1 flex items-center gap-2">
                      Smart Analysis Builder
                      <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">✨ New</span>
                    </div>
                    <div className="text-xs text-gray-600">
                      Advanced autocomplete with dynamic settings and intelligent question generation
                    </div>
                  </div>
                  <div className="text-blue-500 group-hover:text-blue-600 transition-colors">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                </div>
              </button>

              {/* Regular Analysis Options */}
              {analysisOptions.map((option, index) => (
                <button
                  key={index}
                  onClick={() => handleAnalysisOption(option)}
                  disabled={isProcessing}
                  className="text-left p-4 bg-white hover:bg-blue-50 rounded-lg border border-gray-200 hover:border-blue-300 transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
                >
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 bg-gray-100 group-hover:bg-blue-100 rounded-lg flex items-center justify-center transition-colors">
                      <span className="text-lg">{option.emoji}</span>
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-gray-900 text-sm mb-1">
                        {option.title}
                      </div>
                      <div className="text-xs text-gray-600">
                        {option.description}
                      </div>
                    </div>
                    <div className="text-gray-400 group-hover:text-blue-500 transition-colors">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}