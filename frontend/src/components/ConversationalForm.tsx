'use client';

import { useState, useRef, useEffect } from 'react';

interface FormData {
  symbols: string[];
  strategy: string;
  timeframe: string;
  riskTolerance: string;
  investment: number;
  startDate: string;
  endDate: string;
  stopLoss: number;
  takeProfit: number;
}

interface ConversationStep {
  id: string;
  aiMessage: string;
  userResponse?: string;
  field: keyof FormData;
  suggestions?: string[];
  completed: boolean;
}

interface ConversationalFormProps {
  onComplete: (data: FormData) => void;
  onCancel: () => void;
}

export default function ConversationalForm({ onComplete, onCancel }: ConversationalFormProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [userInput, setUserInput] = useState('');
  const [formData, setFormData] = useState<Partial<FormData>>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const conversationSteps: ConversationStep[] = [
    {
      id: 'greeting',
      aiMessage: "What kind of analysis are you looking for? I can set this up perfectly based on your goal:",
      field: 'intent',
      suggestions: [
        'Quick balanced portfolio check',
        'High-growth tech strategy',
        'Safe dividend income focus', 
        'Aggressive momentum trading',
        'Custom setup for my specific needs'
      ],
      completed: false
    }
  ];

  const [steps, setSteps] = useState(conversationSteps);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentStep, steps]);

  const processUserResponse = (response: string) => {
    const step = steps[currentStep];
    const updatedSteps = [...steps];
    updatedSteps[currentStep] = { ...step, userResponse: response, completed: true };
    
    let aiFollowUp = '';
    let completeData: FormData;
    
    // Fast-track based on user intent
    if (response.toLowerCase().includes('quick balanced')) {
      aiFollowUp = "Perfect! Quick balanced portfolio analysis:\n• 📊 Mixed asset allocation (stocks, bonds, ETFs)\n• ⚖️ Moderate risk with diversification\n• 📅 12-month performance review\n• 💰 $100k simulation capital\n\nAnalyzing your balanced approach now! 🚀";
      
      completeData = {
        symbols: ['SPY', 'BND', 'VTI', 'VXUS'],
        strategy: 'balanced_allocation',
        timeframe: 'last_year',
        riskTolerance: 'moderate',
        investment: 100000,
        startDate: '2023-01-01',
        endDate: new Date().toISOString().split('T')[0],
        stopLoss: 5,
        takeProfit: 8
      };
      
    } else if (response.toLowerCase().includes('high-growth tech')) {
      aiFollowUp = "Excellent! High-growth tech strategy:\n• 🚀 FAANG + emerging tech leaders\n• 📈 Growth-focused momentum signals\n• 🎯 Aggressive risk parameters\n• 📊 2-year growth cycle analysis\n\nBuilding your tech portfolio analysis! 💻";
      
      completeData = {
        symbols: ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'NVDA', 'TSLA'],
        strategy: 'high_growth',
        timeframe: '2_years',
        riskTolerance: 'aggressive',
        investment: 150000,
        startDate: '2022-01-01',
        endDate: new Date().toISOString().split('T')[0],
        stopLoss: 10,
        takeProfit: 20
      };
      
    } else if (response.toLowerCase().includes('safe dividend')) {
      aiFollowUp = "Smart choice! Safe dividend income strategy:\n• 💎 Dividend aristocrats & utilities\n• 🛡️ Low volatility, steady income\n• 📈 Long-term compound growth\n• 💵 Income-focused analysis\n\nOptimizing your dividend portfolio! 💰";
      
      completeData = {
        symbols: ['KO', 'JNJ', 'PG', 'VYM', 'SCHD', 'T'],
        strategy: 'dividend_income',
        timeframe: '3_years',
        riskTolerance: 'conservative',
        investment: 75000,
        startDate: '2021-01-01',
        endDate: new Date().toISOString().split('T')[0],
        stopLoss: 3,
        takeProfit: 6
      };
      
    } else if (response.toLowerCase().includes('aggressive momentum')) {
      aiFollowUp = "Let's go! Aggressive momentum trading:\n• ⚡ High-momentum swing trades\n• 📊 RSI + breakout signals\n• 🎯 Quick profit targets\n• ⏰ Short-term tactical moves\n\nSetting up your momentum strategy! 🔥";
      
      completeData = {
        symbols: ['QQQ', 'SOXL', 'TQQQ', 'ARKK', 'SPXL'],
        strategy: 'momentum_trading',
        timeframe: '6_months',
        riskTolerance: 'very_aggressive',
        investment: 50000,
        startDate: '2024-01-01',
        endDate: new Date().toISOString().split('T')[0],
        stopLoss: 15,
        takeProfit: 25
      };
      
    } else {
      // "Custom setup" - show targeted follow-up questions
      aiFollowUp = "Got it! Let's build your custom analysis. What's your primary investment goal?";
      
      // Add targeted follow-up steps
      const additionalSteps = [
        {
          id: 'goal',
          aiMessage: "What's your main investment goal?",
          field: 'strategy',
          suggestions: ['Long-term wealth building', 'Generate monthly income', 'Beat the market', 'Preserve capital', 'Speculative gains'],
          completed: false
        },
        {
          id: 'timeline',
          aiMessage: "What's your investment timeline?",
          field: 'timeframe', 
          suggestions: ['3-6 months', '1-2 years', '3-5 years', '10+ years', 'No specific timeline'],
          completed: false
        },
        {
          id: 'capital',
          aiMessage: "How much capital are you working with?",
          field: 'investment',
          suggestions: ['Under $25k', '$25k - $100k', '$100k - $500k', '$500k+', 'Just testing ideas'],
          completed: false
        }
      ];
      
      setSteps([...updatedSteps, ...additionalSteps]);
      updatedSteps[currentStep].aiMessage += `\n\n${aiFollowUp}`;
      setSteps(updatedSteps);
      setTimeout(() => setCurrentStep(currentStep + 1), 1000);
      return;
    }
    
    // For preset options, complete immediately
    updatedSteps[currentStep].aiMessage += `\n\n${aiFollowUp}`;
    setSteps(updatedSteps);
    
    setTimeout(() => {
      onComplete(completeData);
    }, 2000);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (userInput.trim()) {
      processUserResponse(userInput.trim());
      setUserInput('');
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    processUserResponse(suggestion);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
              <span className="text-blue-600 text-lg">🤖</span>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">AI Strategy Builder</h3>
              <p className="text-sm text-gray-600">Let's build your custom analysis together</p>
            </div>
          </div>
          <button onClick={onCancel} className="text-gray-400 hover:text-gray-600 p-2">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Conversation */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {steps.slice(0, currentStep + 1).map((step, index) => (
            <div key={step.id} className="space-y-3">
              {/* AI Message */}
              <div className="flex gap-3">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-blue-600 text-sm">AI</span>
                </div>
                <div className="bg-blue-50 rounded-lg p-3 max-w-md">
                  <p className="text-sm text-gray-800 whitespace-pre-line">{step.aiMessage}</p>
                </div>
              </div>

              {/* User Response */}
              {step.userResponse && (
                <div className="flex gap-3 justify-end">
                  <div className="bg-gray-100 rounded-lg p-3 max-w-md">
                    <p className="text-sm text-gray-800">{step.userResponse}</p>
                  </div>
                  <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-gray-600 text-sm">You</span>
                  </div>
                </div>
              )}

              {/* Input for current step */}
              {index === currentStep && !step.completed && (
                <div className="ml-11 space-y-3">
                  {/* Suggestions */}
                  {step.suggestions && (
                    <div className="flex flex-wrap gap-2">
                      {step.suggestions.map((suggestion, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleSuggestionClick(suggestion)}
                          className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors"
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Text Input */}
                  <form onSubmit={handleSubmit} className="flex gap-2">
                    <input
                      type="text"
                      value={userInput}
                      onChange={(e) => setUserInput(e.target.value)}
                      placeholder="Type your response..."
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                      autoFocus
                    />
                    <button
                      type="submit"
                      disabled={!userInput.trim()}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                    >
                      Send
                    </button>
                  </form>
                </div>
              )}
            </div>
          ))}

          {currentStep >= steps.length && (
            <div className="flex gap-3">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-green-600 text-sm">✓</span>
              </div>
              <div className="bg-green-50 rounded-lg p-3">
                <p className="text-sm text-gray-800">
                  Perfect! I've got everything I need. Building your custom strategy now... 🚀
                </p>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>
    </div>
  );
}