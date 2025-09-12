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
  isExpanded?: boolean;
}

export default function Home() {
  const [viewMode, setViewMode] = useState<'single' | 'split'>('single');
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
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [expandedResults, setExpandedResults] = useState<Set<string>>(new Set());
  const resultRefs = useRef<{ [key: string]: HTMLDivElement | null }>({});
  const interactiveFormRef = useRef<HTMLDivElement>(null);
  const [currentOriginalQuestion, setCurrentOriginalQuestion] = useState<string>('');
  const [analysisVersions, setAnalysisVersions] = useState<{[key: string]: number}>({});
  const [currentAnalysis, setCurrentAnalysis] = useState<{moduleKey: string, messageId: string, originalQuestion?: string} | null>(null);
  const rightPanelRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const scrollToResult = (messageId: string) => {
    const element = resultRefs.current[messageId];
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  const scrollRightPanelToTop = () => {
    if (rightPanelRef.current) {
      rightPanelRef.current.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  useEffect(() => {
    // Only auto-scroll if the last message is not a results message
    const lastMessage = messages[messages.length - 1];
    if (lastMessage && lastMessage.type !== 'results') {
      scrollToBottom();
    }
  }, [messages]);

  // Scroll to newly expanded results
  useEffect(() => {
    if (expandedResults.size > 0) {
      const latestExpandedId = Array.from(expandedResults)[expandedResults.size - 1];
      if (latestExpandedId) {
        setTimeout(() => scrollToResult(latestExpandedId), 100);
      }
    }
  }, [expandedResults]);

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
      timestamp: new Date(),
      isExpanded: message.type === 'results' ? true : message.isExpanded
    };
    setMessages(prev => [...prev, newMessage]);
    
    // Auto-expand new results and collapse previous ones
    if (message.type === 'results') {
      setExpandedResults(prev => {
        const newSet = new Set([newMessage.id]);
        return newSet;
      });
    }
    
    return newMessage.id;
  };

  const updateMessage = (id: string, updates: Partial<ChatMessage>) => {
    setMessages(prev => prev.map(msg => 
      msg.id === id ? { ...msg, ...updates } : msg
    ));
    
    // Handle results based on view mode
    if (updates.type === 'results') {
      if (viewMode === 'single') {
        // Auto-expand new results and collapse previous ones
        setExpandedResults(prev => {
          const newSet = new Set([id]);
          return newSet;
        });
        // Scroll to the new result after a brief delay for animation
        setTimeout(() => scrollToResult(id), 300);
      } else {
        // Split mode: Set current analysis for right panel
        const userMessages = messages.filter(msg => msg.type === 'user');
        const lastUserMessage = userMessages[userMessages.length - 1];
        
        setCurrentAnalysis({ 
          moduleKey: updates.moduleKey!, 
          messageId: id,
          originalQuestion: lastUserMessage?.content
        });
        scrollRightPanelToTop();
      }
    }
  };

  const toggleResultExpansion = (messageId: string) => {
    setExpandedResults(prev => {
      const newSet = new Set(prev);
      if (newSet.has(messageId)) {
        newSet.delete(messageId);
      } else {
        newSet.add(messageId);
        // Scroll to expanded result after a brief delay
        setTimeout(() => scrollToResult(messageId), 200);
      }
      return newSet;
    });
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
    setCurrentOriginalQuestion(userMessage); // Store for later use
    setChatInput('');
    setIsProcessing(true);

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
    
    // Scroll to the interactive form after a brief delay to allow rendering
    setTimeout(() => {
      interactiveFormRef.current?.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
      });
    }, 100);
  };

  const handleParameterChange = (paramKey: string, value: string | string[]) => {
    setParameterValues(prev => ({
      ...prev,
      [paramKey]: value
    }));
  };

  const renderSplitMessage = (message: ChatMessage) => {
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

  const renderMessage = (message: ChatMessage) => {
    const isUser = message.type === 'user';
    const isThinking = message.type === 'thinking';
    const isAnalyzing = message.type === 'analyzing';

    return (
      <div key={message.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
        <div className={`max-w-3xl px-4 py-3 rounded-lg ${
          isUser 
            ? 'bg-blue-600 text-white' 
            : isThinking 
            ? 'bg-gray-100 border-l-4 border-blue-500' 
            : isAnalyzing
            ? 'bg-yellow-50 border-l-4 border-yellow-500'
            : 'bg-gray-100 text-gray-900'
        }`}>
          {!isUser && (
            <div className="flex items-center gap-2 mb-2">
              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-blue-600 text-xs">🤖</span>
              </div>
              <span className="text-xs text-gray-500">AI Assistant</span>
            </div>
          )}

          {isThinking && (
            <div className="flex items-center gap-3">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
              </div>
              <span className="text-gray-600">Thinking...</span>
            </div>
          )}

          {isAnalyzing && (
            <div className="flex items-center gap-3">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-600"></div>
              <span className="text-gray-700">Running analysis...</span>
            </div>
          )}

          {!isThinking && !isAnalyzing && (
            <div className="whitespace-pre-wrap">{message.content}</div>
          )}

          {message.type === 'results' && message.moduleKey && (
            <div 
              className="mt-4"
              ref={el => { resultRefs.current[message.id] = el; }}
            >
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-semibold text-gray-900">
                  {modules[message.moduleKey]?.title} Results
                </h4>
                <button
                  onClick={() => toggleResultExpansion(message.id)}
                  className="flex items-center gap-2 px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors"
                >
                  {expandedResults.has(message.id) ? (
                    <>
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                      </svg>
                      Collapse
                    </>
                  ) : (
                    <>
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                      Expand
                    </>
                  )}
                </button>
              </div>
              
              {expandedResults.has(message.id) ? (
                <div className="animate-in slide-in-from-top-2 duration-200">
                  <MockOutput moduleKey={message.moduleKey} />
                </div>
              ) : (
                <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors"
                     onClick={() => toggleResultExpansion(message.id)}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                        <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">Analysis Complete</p>
                        <p className="text-sm text-gray-600">Click to view detailed results and insights</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="text-right text-xs text-gray-500">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </div>
                      <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {message.type === 'interactive' && message.moduleKey && !showInteractive && (
            <div className="mt-4">
              {(() => {
                // Find the most recent interactive message
                const interactiveMessages = messages.filter(m => m.type === 'interactive');
                const isLatestInteractive = interactiveMessages.length > 0 && 
                                          interactiveMessages[interactiveMessages.length - 1].id === message.id;
                
                return isLatestInteractive ? (
                  <button
                    onClick={() => initializeParameters(message.moduleKey!)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                  >
                    🛠️ Customize Analysis
                  </button>
                ) : (
                  <div className="text-sm text-gray-500 italic">
                    Customize option available for latest analysis only
                  </div>
                );
              })()}
            </div>
          )}

          {!isUser && (
            <div className="text-xs text-gray-400 mt-2">
              {message.timestamp.toLocaleTimeString()}
            </div>
          )}
        </div>
      </div>
    );
  };

  if (viewMode === 'split') {
    return (
      <div className="h-screen flex bg-gray-50">
        {/* Left Panel - Chat */}
        <div className="w-1/3 bg-white border-r border-gray-200 flex flex-col">
          {/* Header */}
          <header className="bg-white border-b border-gray-200 px-4 py-3 flex-shrink-0">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setViewMode('single')}
                  className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                  title="Switch to single view"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                  </svg>
                </button>
                <div>
                  <h1 className="text-lg font-bold text-gray-900">AI Financial Chat</h1>
                  <p className="text-gray-600 text-xs mt-1">Ask questions about trading & investing</p>
                </div>
              </div>
            </div>
          </header>

          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-4">
            {messages.map(renderSplitMessage)}
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
                        const truncatedQuestion = currentOriginalQuestion.length > 50 ? 
                          currentOriginalQuestion.substring(0, 47) + '...' : currentOriginalQuestion;
                        
                        // Increment version for this question
                        const currentVersion = (analysisVersions[currentOriginalQuestion] || 1) + 1;
                        setAnalysisVersions(prev => ({
                          ...prev,
                          [currentOriginalQuestion]: currentVersion
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
    );
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex-shrink-0">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setViewMode('split')}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              title="Switch to split view"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2" />
              </svg>
            </button>
            <div>
              <h1 className="text-xl font-bold text-gray-900">AI Financial Analyst</h1>
              <p className="text-gray-600 text-sm mt-1">Ask questions about trading, investing, and portfolio management</p>
            </div>
          </div>
        </div>
      </header>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        <div className="max-w-4xl mx-auto">
          {messages.map(renderMessage)}
          
          {/* Interactive Component */}
          {showInteractive && selectedModule && (
            <div 
              ref={interactiveFormRef}
              className="bg-white rounded-lg border border-blue-200 p-6 mb-4 shadow-lg animate-in slide-in-from-top-4 duration-300"
              style={{
                background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(147, 197, 253, 0.05) 100%)'
              }}
            >
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
                      const truncatedQuestion = currentOriginalQuestion.length > 50 ? 
                        currentOriginalQuestion.substring(0, 47) + '...' : currentOriginalQuestion;
                      
                      // Increment version for this question
                      const currentVersion = (analysisVersions[currentOriginalQuestion] || 1) + 1;
                      setAnalysisVersions(prev => ({
                        ...prev,
                        [currentOriginalQuestion]: currentVersion
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
                      
                      // Simulate processing time
                      await new Promise(resolve => setTimeout(resolve, 1500));
                      
                      // Add analyzing message
                      const analyzingId = addMessage({
                        type: 'analyzing',
                        content: 'Processing with custom parameters...',
                        isTyping: true
                      });

                      await new Promise(resolve => setTimeout(resolve, 2000));

                      // Update to results
                      updateMessage(analyzingId, {
                        type: 'results',
                        content: `Updated ${modules[selectedModule!]?.title.toLowerCase()} analysis complete with your custom parameters. Here are the refined results:`,
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
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Chat Input */}
      <div className="bg-white border-t border-gray-200 px-6 py-4 flex-shrink-0">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSubmit} className="relative">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="Ask about portfolio analysis, trading strategies, risk assessment..."
              disabled={isProcessing}
              className="w-full px-4 py-3 pr-12 text-gray-900 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
            />
            <button
              type="submit"
              disabled={!chatInput.trim() || isProcessing}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 text-blue-600 hover:text-blue-700 disabled:text-gray-400 disabled:cursor-not-allowed"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}