'use client';

import { useState } from 'react';
import { modules } from '@/config/modules';
import { ParameterValues } from '@/types/modules';
import ChatInterface from '@/components/chat/ChatInterface';
import AnalysisPanel from '@/components/chat/AnalysisPanel';
import CustomizationForm from '@/components/chat/CustomizationForm';

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
  // View state
  const [viewMode, setViewMode] = useState<'single' | 'split'>('single');
  
  // Chat state
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
  
  // Analysis state
  const [currentAnalysis, setCurrentAnalysis] = useState<{
    moduleKey: string;
    messageId: string;
    originalQuestion?: string;
  } | null>(null);
  const [expandedResults, setExpandedResults] = useState<Set<string>>(new Set());
  
  // Customization state
  const [selectedModule, setSelectedModule] = useState<string | null>(null);
  const [parameterValues, setParameterValues] = useState<ParameterValues>({});
  const [showCustomization, setShowCustomization] = useState(false);

  // Enhanced search with fuzzy matching
  const findBestMatchingAnalysis = (query: string) => {
    const queryLower = query.toLowerCase();
    const moduleEntries = Object.entries(modules);
    
    for (const [key, module] of moduleEntries) {
      const titleWords = module.title.toLowerCase().split(' ');
      const hasMatch = titleWords.some(word => queryLower.includes(word) || word.includes(queryLower.slice(0, 4)));
      if (hasMatch) return key;
    }
    
    return Object.keys(modules)[0];
  };

  const handleSendMessage = async (userMessage: string) => {
    setIsProcessing(true);
    
    // Add user message
    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: userMessage,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMsg]);
    
    // Small delay for natural feel
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Find best matching analysis
    const moduleKey = findBestMatchingAnalysis(userMessage);
    
    // Add thinking message
    const thinkingId = `thinking-${Date.now()}`;
    setMessages(prev => [...prev, {
      id: thinkingId,
      type: 'thinking',
      content: '',
      timestamp: new Date()
    }]);
    
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Update to explanation
    setMessages(prev => prev.map(msg => 
      msg.id === thinkingId 
        ? {
            ...msg,
            type: 'ai',
            content: `I'll analyze ${modules[moduleKey]?.title.toLowerCase()} for your portfolio. Let me gather the data and run the calculations.`
          }
        : msg
    ));
    
    // Add analyzing message
    const analyzingId = `analyzing-${Date.now()}`;
    setMessages(prev => [...prev, {
      id: analyzingId,
      type: 'analyzing',
      content: '',
      timestamp: new Date()
    }]);
    
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Update to results
    const resultId = `result-${Date.now()}`;
    setMessages(prev => prev.filter(msg => msg.id !== analyzingId));
    
    const resultMessage: ChatMessage = {
      id: resultId,
      type: 'results',
      content: `I've completed the ${modules[moduleKey]?.title.toLowerCase()} for your portfolio. Here are the key findings:`,
      timestamp: new Date(),
      moduleKey,
      isExpanded: false
    };
    
    setMessages(prev => [...prev, resultMessage]);
    
    // Handle results based on view mode
    if (viewMode === 'single') {
      // Collapse ALL previous results and expand only the new one
      setExpandedResults(new Set([resultId]));
    } else {
      // Split mode: Set current analysis for right panel
      setCurrentAnalysis({ moduleKey, messageId: resultId, originalQuestion: userMessage });
    }
    
    // Add interactive offer
    setTimeout(() => {
      const interactiveId = `interactive-${Date.now()}`;
      setMessages(prev => [...prev, {
        id: interactiveId,
        type: 'interactive',
        content: '',
        timestamp: new Date(),
        moduleKey
      }]);
    }, 1000);
    
    setIsProcessing(false);
  };

  const handleExpandToggle = (messageId: string) => {
    setExpandedResults(prev => {
      const newSet = new Set(prev);
      if (newSet.has(messageId)) {
        newSet.delete(messageId);
      } else {
        newSet.add(messageId);
      }
      return newSet;
    });
  };

  const handleCustomizeAnalysis = (moduleKey: string) => {
    setSelectedModule(moduleKey);
    setShowCustomization(true);
    
    // Remove the interactive message that triggered this
    setMessages(prev => prev.filter(msg => !(msg.type === 'interactive' && msg.moduleKey === moduleKey)));
  };

  const handleCustomizationSubmit = () => {
    setShowCustomization(false);
    
    if (selectedModule) {
      const customMessage = `Running updated analysis with your custom parameters...`;
      handleSendMessage(customMessage);
    }
    
    setSelectedModule(null);
  };


  if (viewMode === 'single') {
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-4 py-3">
          <div className="flex items-center justify-between max-w-6xl mx-auto">
            <button
              onClick={() => setViewMode('split')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              title="Switch to split view"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
              </svg>
            </button>
            
            <div className="text-center">
              <h1 className="text-lg font-bold text-gray-900">AI Financial Chat</h1>
              <p className="text-gray-600 text-xs mt-1">Ask questions about trading & investing</p>
            </div>
            
            <div className="w-9"></div> {/* Spacer for centering */}
          </div>
        </header>

        {/* Chat Container */}
        <div className="max-w-4xl mx-auto h-[calc(100vh-80px)]">
          <ChatInterface
            messages={messages}
            chatInput={chatInput}
            setChatInput={setChatInput}
            isProcessing={isProcessing}
            onSendMessage={handleSendMessage}
            onExpandToggle={handleExpandToggle}
            expandedResults={expandedResults}
            onCustomizeAnalysis={handleCustomizeAnalysis}
          />
        </div>

        {/* Customization Form */}
        {showCustomization && (
          <CustomizationForm
            selectedModule={selectedModule}
            parameterValues={parameterValues}
            setParameterValues={setParameterValues}
            onClose={() => setShowCustomization(false)}
            onSubmit={handleCustomizationSubmit}
          />
        )}
      </div>
    );
  }

  // Split view
  return (
    <div className="h-screen bg-gray-50 flex">
      {/* Left Panel - Chat */}
      <div className="w-1/3 bg-white border-r border-gray-200 flex flex-col">
        <header className="border-b border-gray-200 px-4 py-3">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setViewMode('single')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
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
        </header>

        <ChatInterface
          messages={messages}
          chatInput={chatInput}
          setChatInput={setChatInput}
          isProcessing={isProcessing}
          onSendMessage={handleSendMessage}
          onExpandToggle={handleExpandToggle}
          expandedResults={expandedResults}
          onCustomizeAnalysis={handleCustomizeAnalysis}
        />
      </div>

      {/* Right Panel - Analysis Results */}
      <div className="w-2/3 flex flex-col">
        <AnalysisPanel currentAnalysis={currentAnalysis} />
      </div>

      {/* Customization Form */}
      {showCustomization && (
        <CustomizationForm
          selectedModule={selectedModule}
          parameterValues={parameterValues}
          setParameterValues={setParameterValues}
          onClose={() => setShowCustomization(false)}
          onSubmit={handleCustomizationSubmit}
        />
      )}
    </div>
  );
}