'use client';

import { useState, useMemo, useRef, useEffect } from 'react';
import { modules } from '@/config/modules';
import { Module, ParameterValues } from '@/types/modules';
import ParameterControl from '@/components/ParameterControl';
import MockOutput from '@/components/MockOutput';

interface ChatMessage {
  id: string;
  type: 'user' | 'ai' | 'thinking' | 'analyzing' | 'results' | 'interactive';
  content: string;
  timestamp: Date;
  moduleKey?: string;
  isTyping?: boolean;
}

export default function SplitLayout() {
  const [chatInput, setChatInput] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      type: 'ai',
      content: "Hi! I'm your AI financial analyst. Ask me anything about portfolio analysis, trading strategies, risk assessment, or investment research.",
      timestamp: new Date()
    }
  ]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedModule, setSelectedModule] = useState<string | null>(null);
  const [parameterValues, setParameterValues] = useState<ParameterValues>({});
  const [showInteractive, setShowInteractive] = useState(false);
  const [currentAnalysis, setCurrentAnalysis] = useState<{moduleKey: string, messageId: string, originalQuestion?: string} | null>(null);
  const [analysisVersions, setAnalysisVersions] = useState<{[key: string]: number}>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const rightPanelRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const scrollRightPanelToTop = () => {
    if (rightPanelRef.current) {
      rightPanelRef.current.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Enhanced search with fuzzy matching
  const findBestModule = (query: string) => {
    if (!query.trim()) return null;

    const keywords: { [key: string]: string[] } = {
      rebalance: ['rebalance', 'rebalancing', 'portfolio', 'allocation', 'frequency', 'asset allocation', 'diversification'],
      backtest: ['backtest', 'backtesting', 'strategy', 'moving average', 'test', 'historical', 'performance', 'trading', 'rsi', 'macd', 'bollinger'],
      regression: ['regression', 'factor', 'analysis', 'exposure', 'beta', 'alpha', 'risk factor', 'capm'],
      risk: ['risk', 'var', 'value at risk', 'drawdown', 'volatility', 'risk assessment', 'stress test'],
      screening: ['screen', 'screening', 'stock picker', 'find stocks', 'discovery', 'fundamental', 'filter', 'growth'],
      correlation: ['correlation', 'diversification', 'asset correlation', 'relationship', 'covariance']
    };

    const queryLower = query.toLowerCase();
    let bestMatch = null;
    let bestScore = 0;

    for (const [moduleKey, moduleKeywords] of Object.entries(keywords)) {
      const score = moduleKeywords.reduce((acc, keyword) => {
        if (queryLower.includes(keyword)) return acc + 2;
        if (keyword.includes(queryLower) || queryLower.includes(keyword.slice(0, -2))) return acc + 1;
        return acc;
      }, 0);
      
      if (score > bestScore) {
        bestScore = score;
        bestMatch = moduleKey;
      }
    }

    return bestMatch;
  };

  const addMessage = (message: Omit<ChatMessage, 'id' | 'timestamp'>) => {
    const newMessage: ChatMessage = {
      ...message,
      id: Date.now().toString(),
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newMessage]);
    return newMessage.id;
  };

  const updateMessage = (id: string, updates: Partial<ChatMessage>) => {
    setMessages(prev => prev.map(msg => 
      msg.id === id ? { ...msg, ...updates } : msg
    ));
    
    // Set current analysis when results are shown
    if (updates.type === 'results' && updates.moduleKey) {
      // Find the most recent user message to get the original question
      const userMessages = messages.filter(msg => msg.type === 'user');
      const lastUserMessage = userMessages[userMessages.length - 1];
      
      setCurrentAnalysis({ 
        moduleKey: updates.moduleKey, 
        messageId: id,
        originalQuestion: lastUserMessage?.content
      });
      scrollRightPanelToTop();
    }
  };

  const getAnalysisExplanation = (moduleKey: string) => {
    const explanations = {
      rebalance: "I'll analyze portfolio rebalancing strategies for you. Let me examine the impact of different rebalancing frequencies on your portfolio performance, considering transaction costs and risk-adjusted returns.",
      backtest: "I'll backtest your trading strategy using historical data. Let me run a comprehensive analysis including performance metrics, risk assessment, and comparison with buy-and-hold returns.",
      regression: "I'll perform a factor regression analysis to understand your portfolio's risk exposures. Let me analyze how your holdings relate to market factors like size, value, and momentum.",
      risk: "I'll conduct a comprehensive portfolio risk assessment. Let me calculate Value at Risk, stress test scenarios, and analyze your portfolio's volatility characteristics.",
      screening: "I'll screen stocks based on your criteria. Let me find companies that match your fundamental and technical requirements across different market segments.",
      correlation: "I'll analyze asset correlations to assess your portfolio's diversification. Let me examine the relationships between your holdings and identify concentration risks."
    };
    return explanations[moduleKey as keyof typeof explanations] || "I'll run the requested analysis for you.";
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || isProcessing) return;

    const userMessage = chatInput.trim();
    const originalQuestion = userMessage; // Store the original question
    setChatInput('');
    setIsProcessing(true);
    setShowInteractive(false); // Close any open customization forms

    // Add user message
    addMessage({
      type: 'user',
      content: userMessage
    });

    // Small delay for natural feel
    await new Promise(resolve => setTimeout(resolve, 500));

    // Find best matching analysis
    const moduleKey = findBestModule(userMessage);
    
    if (!moduleKey) {
      addMessage({
        type: 'ai',
        content: "I understand you're looking for financial analysis, but I'm not sure which specific analysis would be best. Try asking about portfolio rebalancing, strategy backtesting, risk assessment, stock screening, factor analysis, or correlation analysis."
      });
      setIsProcessing(false);
      return;
    }

    // Start thinking
    const thinkingId = addMessage({
      type: 'thinking',
      content: 'Thinking...',
      isTyping: true
    });

    await new Promise(resolve => setTimeout(resolve, 1500));

    // Update to explanation
    updateMessage(thinkingId, {
      type: 'ai',
      content: getAnalysisExplanation(moduleKey),
      isTyping: false
    });

    await new Promise(resolve => setTimeout(resolve, 2000));

    // Add analyzing message
    const analyzingId = addMessage({
      type: 'analyzing',
      content: 'Running analysis...',
      isTyping: true
    });

    await new Promise(resolve => setTimeout(resolve, 2500));

    // Update to results
    updateMessage(analyzingId, {
      type: 'results',
      content: `I've completed the ${modules[moduleKey]?.title.toLowerCase()} for your portfolio. Here are the key findings:`,
      moduleKey,
      isTyping: false
    });

    // Add interactive offer
    await new Promise(resolve => setTimeout(resolve, 1000));
    addMessage({
      type: 'interactive',
      content: 'Would you like to customize the analysis parameters and rerun with your specific requirements?',
      moduleKey
    });

    setIsProcessing(false);
  };

  const initializeParameters = (moduleKey: string) => {
    const module = modules[moduleKey];
    const initialValues: ParameterValues = {};
    
    module.params.forEach((param, index) => {
      const key = `${moduleKey}_${index}`;
      initialValues[key] = param.defaultValue || (param.type === 'checkbox' ? [] : '');
    });
    
    setParameterValues(initialValues);
    setSelectedModule(moduleKey);
    setShowInteractive(true);
  };

  const handleParameterChange = (paramKey: string, value: string | string[]) => {
    setParameterValues(prev => ({
      ...prev,
      [paramKey]: value
    }));
  };

  const renderMessage = (message: ChatMessage) => {
    const isUser = message.type === 'user';
    const isThinking = message.type === 'thinking';
    const isAnalyzing = message.type === 'analyzing';

    return (
      <div key={message.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3`}>
        <div className={`${isUser ? 'max-w-xs' : 'w-full'} px-3 py-2 rounded-lg text-sm ${
          isUser 
            ? 'bg-blue-600 text-white' 
            : isThinking 
            ? 'bg-gray-100 border-l-2 border-blue-500' 
            : isAnalyzing
            ? 'bg-yellow-50 border-l-2 border-yellow-500'
            : 'bg-gray-100 text-gray-900'
        }`}>
          {!isUser && message.type !== 'results' && (
            <div className="flex items-center gap-1 mb-1">
              <div className="w-4 h-4 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-blue-600 text-xs">🤖</span>
              </div>
              <span className="text-xs text-gray-500">AI</span>
            </div>
          )}

          {isThinking && (
            <div className="flex items-center gap-2">
              <div className="flex space-x-1">
                <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"></div>
              </div>
              <span className="text-gray-600 text-xs">Thinking...</span>
            </div>
          )}

          {isAnalyzing && (
            <div className="flex items-center gap-2">
              <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-yellow-600"></div>
              <span className="text-gray-700 text-xs">Analyzing...</span>
            </div>
          )}

          {!isThinking && !isAnalyzing && (
            <div>
              <div className="whitespace-pre-wrap">{message.content}</div>
              {message.type === 'results' && (
                <div className="mt-2 pt-2 border-t border-gray-200">
                  <div className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">
                    ✓ Analysis Complete - View results on the right →
                  </div>
                </div>
              )}
            </div>
          )}

          {message.type === 'interactive' && message.moduleKey && !showInteractive && (
            <div className="mt-2">
              {(() => {
                const interactiveMessages = messages.filter(m => m.type === 'interactive');
                const isLatestInteractive = interactiveMessages.length > 0 && 
                                          interactiveMessages[interactiveMessages.length - 1].id === message.id;
                
                return isLatestInteractive ? (
                  <button
                    onClick={() => initializeParameters(message.moduleKey!)}
                    className="px-3 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700 transition-colors"
                  >
                    🛠️ Customize
                  </button>
                ) : null;
              })()}
            </div>
          )}

          {!isUser && (
            <div className="text-xs text-gray-400 mt-1">
              {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="h-screen flex bg-gray-50">
      {/* Left Panel - Chat */}
      <div className="w-1/3 bg-white border-r border-gray-200 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-4 py-3 flex-shrink-0">
          <h1 className="text-lg font-bold text-gray-900">AI Financial Chat</h1>
          <p className="text-gray-600 text-xs mt-1">Ask questions about trading & investing</p>
        </header>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-4">
          {messages.map(renderMessage)}
          <div ref={messagesEndRef} />
        </div>

        {/* Chat Input */}
        <div className="border-t border-gray-200 p-4 flex-shrink-0">
          <form onSubmit={handleSubmit} className="relative">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="Ask about portfolio analysis, trading strategies..."
              disabled={isProcessing}
              className="w-full px-3 py-2 pr-10 text-sm text-gray-900 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!chatInput.trim() || isProcessing}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1.5 text-blue-600 hover:text-blue-700 disabled:text-gray-400"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </form>
        </div>
      </div>

      {/* Right Panel - Analysis Results */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-gray-900">Analysis Results</h1>
              {currentAnalysis && (
                <p className="text-gray-600 text-sm mt-1">{modules[currentAnalysis.moduleKey]?.title}</p>
              )}
            </div>
            {currentAnalysis && (
              <div className="flex items-center gap-2">
                <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                  ✓ Complete
                </span>
              </div>
            )}
          </div>
        </header>

        {/* Analysis Content */}
        <div className="flex-1 overflow-y-auto p-6" ref={rightPanelRef}>
          {currentAnalysis ? (
            <MockOutput moduleKey={currentAnalysis.moduleKey} />
          ) : (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">📊</span>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Analysis Yet</h3>
                <p className="text-gray-600 text-sm max-w-sm">
                  Ask a question in the chat to see analysis results here. Try asking about portfolio rebalancing, risk assessment, or strategy backtesting.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Customization Form - Overlay */}
        {showInteractive && selectedModule && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-blue-600 text-sm">🛠️</span>
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">Customize Analysis</h3>
                      <p className="text-sm text-gray-600">{modules[selectedModule]?.title}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => {setShowInteractive(false); setSelectedModule(null);}}
                    className="text-gray-400 hover:text-gray-600 p-2 hover:bg-gray-100 rounded-full transition-colors"
                  >
                    ✕
                  </button>
                </div>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-medium mb-4">Adjust Parameters</h4>
                    {modules[selectedModule]?.params.map((param, index) => {
                      const paramKey = `${selectedModule}_${index}`;
                      return (
                        <ParameterControl
                          key={paramKey}
                          parameter={param}
                          value={parameterValues[paramKey] || param.defaultValue || ''}
                          onChange={(value) => handleParameterChange(paramKey, value)}
                        />
                      );
                    })}
                    <button 
                      onClick={async () => {
                        setIsProcessing(true);
                        
                        // Get the original question for naming and increment version
                        const originalQuestion = currentAnalysis?.originalQuestion || 'analysis';
                        const truncatedQuestion = originalQuestion.length > 50 ? 
                          originalQuestion.substring(0, 47) + '...' : originalQuestion;
                        
                        // Increment version for this question
                        const currentVersion = (analysisVersions[originalQuestion] || 1) + 1;
                        setAnalysisVersions(prev => ({
                          ...prev,
                          [originalQuestion]: currentVersion
                        }));
                        
                        addMessage({
                          type: 'user',
                          content: `${truncatedQuestion} (v${currentVersion} - customized)`
                        });
                        
                        await new Promise(resolve => setTimeout(resolve, 300));
                        
                        addMessage({
                          type: 'ai',
                          content: `Running updated analysis with your custom parameters...`
                        });
                        setShowInteractive(false);
                        
                        await new Promise(resolve => setTimeout(resolve, 1500));
                        
                        const analyzingId = addMessage({
                          type: 'analyzing',
                          content: 'Processing with custom parameters...',
                          isTyping: true
                        });

                        await new Promise(resolve => setTimeout(resolve, 2000));

                        updateMessage(analyzingId, {
                          type: 'results',
                          content: `Updated ${modules[selectedModule!]?.title.toLowerCase()} analysis complete with your custom parameters.`,
                          moduleKey: selectedModule!,
                          isTyping: false
                        });

                        // Remove the used interactive message
                        setMessages(prev => prev.filter(msg => !(msg.type === 'interactive' && msg.moduleKey === selectedModule)));

                        // Add new interactive offer for the updated analysis
                        await new Promise(resolve => setTimeout(resolve, 500));
                        addMessage({
                          type: 'interactive',
                          content: 'Would you like to customize the analysis parameters and rerun with your specific requirements?',
                          moduleKey: selectedModule!
                        });

                        setSelectedModule(null);
                        setIsProcessing(false);
                      }}
                      className="w-full mt-4 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
                      disabled={isProcessing}
                    >
                      {isProcessing ? '🔄 Processing...' : '🚀 Run Updated Analysis'}
                    </button>
                  </div>
                  <div className="bg-blue-50 rounded-lg p-4">
                    <h4 className="font-medium mb-4 text-blue-900">Parameter Guide</h4>
                    <div className="text-sm text-blue-700 space-y-2">
                      <div>Adjust the settings on the left to customize your analysis</div>
                      <div className="bg-blue-100 rounded p-3 text-xs">
                        💡 <strong>Tip:</strong> Different parameters will give you insights into various aspects of your portfolio or strategy
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}