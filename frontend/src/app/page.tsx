'use client';

import { useState } from 'react';
import { useSession } from '@/lib/context/SessionContext';
import { useConversation, ChatMessage } from '@/lib/context/ConversationContext';
import { useUI } from '@/lib/context/UIContext';
import { useAnalysis } from '@/lib/hooks/useAnalysis';
import ChatInterface from '@/components/chat/ChatInterface';
import AnalysisPanel from '@/components/chat/AnalysisPanel';
import CustomizationForm from '@/components/chat/CustomizationForm';
import { ParameterValues } from '@/types/modules';
import { api } from '@/lib/api';

export default function Home() {
  const { session_id } = useSession();
  const { messages, addMessage, updateMessage } = useConversation();
  const { viewMode, setViewMode, isProcessing, setIsProcessing, error: uiError, setError: setUIError } = useUI();
  const { analyzeQuestion, isLoading: analysisLoading } = useAnalysis();

  const [chatInput, setChatInput] = useState('');
  const [currentAnalysis, setCurrentAnalysis] = useState<{
    messageId: string;
    data: Record<string, unknown>;
    originalQuestion?: string;
  } | null>(null);
  const [selectedModule, setSelectedModule] = useState<string | null>(null);
  const [parameterValues, setParameterValues] = useState<ParameterValues>({});
  const [showCustomization, setShowCustomization] = useState(false);
  const [lastClarificationMessageId, setLastClarificationMessageId] = useState<string | null>(null);

  const handleSendMessage = async (userMessage: string) => {
    if (!session_id || !userMessage.trim()) return;

    try {
      setIsProcessing(true);
      setChatInput('');
      setUIError(null);

      // If there's a pending clarification that wasn't answered, collapse it to summary
      if (lastClarificationMessageId) {
        updateMessage(lastClarificationMessageId, {
          type: 'clarification',
          content: 'Clarification was skipped',
          data: undefined,
        });
        setLastClarificationMessageId(null);
      }

      addMessage({
        type: 'user',
        content: userMessage,
      });

      const response = await analyzeQuestion({
        question: userMessage,
        session_id: session_id,
        enable_caching: true,
      });

      if (response.success && response.data) {
        // Check if query is meaningless
        if (response.data.is_meaningless) {
          addMessage({
            type: 'ai',
            content: response.data.message || 'I need more details to help you. Please tell me what you\'d like to analyze.',
          });
        } else {
          // Check if needs_clarification is in context_result or directly in data
          const needsClarification = response.data.needs_clarification || 
            (response.data.context_result && response.data.context_result.needs_clarification);
          const clarificationData = response.data.context_result || response.data;
          
          if (needsClarification) {
            const clarificationMsg = addMessage({
              type: 'clarification',
              content: clarificationData.message || 'Please confirm the interpretation',
              data: {
                original_query: clarificationData.original_query,
                expanded_query: clarificationData.expanded_query,
                message: clarificationData.message,
                suggestion: clarificationData.suggestion,
                confidence: clarificationData.expansion_confidence || clarificationData.confidence,
                session_id: clarificationData.session_id,
              },
            });
            setLastClarificationMessageId(clarificationMsg.id);
            setCurrentAnalysis({
              messageId: clarificationMsg.id,
              data: response.data,
              originalQuestion: userMessage,
            });
          } else if (response.data.needs_confirmation || 
                     (response.data.context_result && response.data.context_result.needs_confirmation)) {
            const confirmMsg = addMessage({
              type: 'clarification',
              content: clarificationData.message || 'Please confirm',
              data: clarificationData,
            });
            setCurrentAnalysis({
              messageId: confirmMsg.id,
              data: response.data,
              originalQuestion: userMessage,
            });
          } else {
            const resultMsg = addMessage({
              type: 'results',
              content: response.data.analysis_summary || `Analysis complete for: ${userMessage}`,
              data: response.data,
            });

            setCurrentAnalysis({
              messageId: resultMsg.id,
              data: response.data,
              originalQuestion: userMessage,
            });

            if (viewMode === 'single') {
              const expandedSet = new Set<string>();
              expandedSet.add(resultMsg.id);
            }
          }
        }
      } else {
        addMessage({
          type: 'error',
          content: response.error || 'Analysis failed. Please try again.',
        });
        setUIError(response.error || 'Analysis failed');
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'An error occurred';
      addMessage({
        type: 'error',
        content: errorMsg,
      });
      setUIError(errorMsg);
      console.error('Message send error:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleClarificationResponse = async (
    userResponse: string,
    clarificationData: any
  ) => {
    if (!session_id || !clarificationData) return;

    try {
      setIsProcessing(true);
      setChatInput('');

      addMessage({
        type: 'user',
        content: userResponse,
      });

      const response = await api.analysis.handleClarificationResponse(
        session_id,
        userResponse,
        clarificationData.original_query,
        clarificationData.expanded_query
      );

      if (response.success && response.data) {
        if (response.data.stage === 'needs_input') {
          if (lastClarificationMessageId) {
            updateMessage(lastClarificationMessageId, {
              type: 'clarification',
              content: 'Your previous response was not accepted. ' + (response.data.message || ''),
              data: undefined,
            });
            setLastClarificationMessageId(null);
          } else {
            addMessage({
              type: 'ai',
              content: response.data.message || 'Please rephrase your question with more details.',
            });
          }
        } else if (response.data.stage === 'ready' || response.data.search_results) {
          if (lastClarificationMessageId) {
            updateMessage(lastClarificationMessageId, {
              type: 'results',
              content: response.data.analysis_summary || 'Analysis complete',
              data: response.data,
            });
            setLastClarificationMessageId(null);
            setCurrentAnalysis({
              messageId: lastClarificationMessageId,
              data: response.data,
              originalQuestion: clarificationData.original_query,
            });
          } else {
            const resultMsg = addMessage({
              type: 'results',
              content: response.data.analysis_summary || 'Analysis complete',
              data: response.data,
            });
            setCurrentAnalysis({
              messageId: resultMsg.id,
              data: response.data,
              originalQuestion: clarificationData.original_query,
            });
          }
        } else {
          if (lastClarificationMessageId) {
            updateMessage(lastClarificationMessageId, {
              type: 'results',
              content: response.data.analysis_summary || 'Analysis complete',
              data: response.data,
            });
            setLastClarificationMessageId(null);
            setCurrentAnalysis({
              messageId: lastClarificationMessageId,
              data: response.data,
              originalQuestion: clarificationData.original_query,
            });
          } else {
            const resultMsg = addMessage({
              type: 'results',
              content: response.data.analysis_summary || 'Analysis complete',
              data: response.data,
            });
            setCurrentAnalysis({
              messageId: resultMsg.id,
              data: response.data,
              originalQuestion: clarificationData.original_query,
            });
          }
        }
      } else {
        addMessage({
          type: 'error',
          content: response.error || 'Failed to process response. Please try again.',
        });
        setUIError(response.error || 'Response processing failed');
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'An error occurred';
      addMessage({
        type: 'error',
        content: errorMsg,
      });
      setUIError(errorMsg);
      console.error('Clarification response error:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCustomizeAnalysis = (moduleKey: string) => {
    setSelectedModule(moduleKey);
    setShowCustomization(true);
  };

  const handleCustomizationSubmit = () => {
    setShowCustomization(false);

    if (selectedModule && Object.keys(parameterValues).length > 0) {
      const customParams = Object.entries(parameterValues)
        .map(([key, value]) => `${key}: ${value}`)
        .join(', ');
      handleSendMessage(`Run analysis with parameters: ${customParams}`);
    }

    setSelectedModule(null);
  };

  if (!session_id) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Initializing session...</p>
        </div>
      </div>
    );
  }

  if (viewMode === 'single') {
    return (
      <div className="min-h-screen bg-gray-50">
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

            <div className="w-9"></div>
          </div>
        </header>

        <div className="max-w-4xl mx-auto h-[calc(100vh-80px)]">
          <ChatInterface
            messages={messages}
            chatInput={chatInput}
            setChatInput={setChatInput}
            isProcessing={isProcessing || analysisLoading}
            onSendMessage={handleSendMessage}
            onClarificationResponse={handleClarificationResponse}
            pendingClarificationId={lastClarificationMessageId}
          />
        </div>

        {showCustomization && (
          <CustomizationForm
            selectedModule={selectedModule}
            parameterValues={parameterValues}
            setParameterValues={setParameterValues}
            onClose={() => setShowCustomization(false)}
            onSubmit={handleCustomizationSubmit}
          />
        )}

        {uiError && (
          <div className="fixed bottom-4 right-4 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
            {uiError}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="h-screen bg-gray-50 flex">
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
          isProcessing={isProcessing || analysisLoading}
          onSendMessage={handleSendMessage}
          onClarificationResponse={handleClarificationResponse}
          pendingClarificationId={lastClarificationMessageId}
        />
      </div>

      <div className="w-2/3 flex flex-col">
        <AnalysisPanel currentAnalysis={currentAnalysis} />
      </div>

      {showCustomization && (
        <CustomizationForm
          selectedModule={selectedModule}
          parameterValues={parameterValues}
          setParameterValues={setParameterValues}
          onClose={() => setShowCustomization(false)}
          onSubmit={handleCustomizationSubmit}
        />
      )}

      {uiError && (
        <div className="fixed bottom-4 right-4 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
          {uiError}
        </div>
      )}
    </div>
  );
}
