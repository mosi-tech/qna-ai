'use client';

import { useState, useCallback, useEffect } from 'react';
import { useSession } from '@/lib/context/SessionContext';
import { useConversation } from '@/lib/context/ConversationContext';
import { useUI } from '@/lib/context/UIContext';
import { useAnalysis } from '@/lib/hooks/useAnalysis';
import { useSessionManager } from '@/lib/hooks/useSessionManager';
import { ProgressProvider, useProgress } from '@/lib/context/ProgressContext';
import ChatInterface from '@/components/chat/ChatInterface';
import AnalysisPanel from '@/components/chat/AnalysisPanel';
import ProgressPanel from '@/components/progress/ProgressPanel';
import CustomizationForm from '@/components/chat/CustomizationForm';
import SessionList from '@/components/chat/SessionList';
import { ParameterValues } from '@/types/modules';
import { ProgressManager } from '@/lib/progress/ProgressManager';
import { api } from '@/lib/api';

function HomeContent() {
  const { session_id, user_id, resumeSession, updateSessionMetadata } = useSession();
  const { messages, addMessage, updateMessage, setMessages, loadSessionMessages } = useConversation();
  const { viewMode, setViewMode, isProcessing, setIsProcessing, error: uiError, setError: setUIError } = useUI();
  const { analyzeQuestion, isLoading: analysisLoading } = useAnalysis();
  const { logs: progressLogs, isConnected, clearLogs } = useProgress();
  const { getSessionDetail } = useSessionManager();

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
  const [showSessionHistory, setShowSessionHistory] = useState(false);
  const [isLoadingOlderMessages, setIsLoadingOlderMessages] = useState(false);
  const [currentSessionMessages, setCurrentSessionMessages] = useState({
    offset: 0,
    limit: 5,
    total: 0,
    hasOlder: false,
  });

  // Load session messages on mount when session_id is available
  useEffect(() => {
    if (session_id) {
      console.log(`[Home] Loading messages for session ${session_id}`);
      loadSessionMessages(session_id).catch((err) => {
        console.warn('[Home] Failed to load session messages (this is expected if session has no prior messages):', err);
        // Don't show error to user - this is normal for new sessions
      });
    }
  }, [session_id]);

  const handleSendMessage = async (userMessage: string) => {
    if (!session_id || !userMessage.trim()) return;

    try {
      setIsProcessing(true);
      setChatInput('');
      setUIError(null);
      clearLogs();

      ProgressManager.addLog(session_id, {
        level: 'info',
        message: `Processing question: "${userMessage}"`,
      });

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

      ProgressManager.addLog(session_id, {
        level: 'info',
        message: 'Sending analysis request to server...',
      });

      const response = await analyzeQuestion({
        question: userMessage,
        session_id: session_id,
        enable_caching: true,
      });

      if (response.success && response.data) {
        ProgressManager.addLog(session_id, {
          level: 'success',
          message: 'Analysis request completed successfully',
        });

        // Check if query is meaningless
        if (response.data.is_meaningless) {
          ProgressManager.addLog(session_id, {
            level: 'warning',
            message: 'Query was not specific enough. Requesting clarification.',
          });

          const errorMsg = response.data.message || 'I need more details to help you. Please tell me what you\'d like to analyze.';
          addMessage({
            type: 'ai',
            content: errorMsg,
          });
        } else {
          // Check if needs_clarification is in context_result or directly in data
          const needsClarification = response.data.needs_clarification || 
            (response.data.context_result && response.data.context_result.needs_clarification);
          const clarificationData = response.data.context_result || response.data;
          
          if (needsClarification) {
            ProgressManager.addLog(session_id, {
              level: 'info',
              message: 'Analysis requires user clarification',
              details: {
                confidence: clarificationData.expansion_confidence || clarificationData.confidence,
              },
            });

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
            ProgressManager.addLog(session_id, {
              level: 'info',
              message: 'Analysis requires user confirmation',
            });

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
            ProgressManager.addLog(session_id, {
              level: 'success',
              message: 'Analysis results ready for display',
            });

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
        ProgressManager.addLog(session_id, {
          level: 'error',
          message: response.error || 'Analysis failed',
        });

        const errorContent = response.error || 'Analysis failed. Please try again.';
        addMessage({
          type: 'error',
          content: errorContent,
        });
        setUIError(response.error || 'Analysis failed');
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'An error occurred';
      ProgressManager.addLog(session_id, {
        level: 'error',
        message: `Exception: ${errorMsg}`,
      });

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

  const handleSelectSession = useCallback(async (selectedSessionId: string) => {
    try {
      setShowSessionHistory(false);
      setIsProcessing(true);

      if (selectedSessionId === 'new') {
        await resumeSession('');
        setMessages([{
          id: '1',
          type: 'ai',
          content: "Hi! I'm your AI financial analyst. Ask me anything about portfolio analysis, trading strategies, risk assessment, or investment research.",
          timestamp: new Date(),
        }]);
        return;
      }

      const sessionDetail = await getSessionDetail(selectedSessionId, 0, 5);
      if (!sessionDetail) {
        setUIError('Failed to load session');
        return;
      }

      await resumeSession(selectedSessionId);
      updateSessionMetadata({
        title: sessionDetail.title,
        created_at: sessionDetail.created_at,
        updated_at: sessionDetail.updated_at,
        is_archived: sessionDetail.is_archived,
      });

      const getMessageType = (msg: any) => {
        if (msg.role === 'user') return 'user';
        if (msg.role === 'assistant') {
          // Check if this assistant message contains analysis results
          if (msg.metadata && (
            msg.metadata.query_type || 
            msg.metadata.analysis_type || 
            msg.metadata.best_day ||
            msg.metadata.response_type === 'analysis' ||
            (msg.metadata.response_data && msg.metadata.response_data.analysis_result)
          )) {
            return 'results';
          }
          return 'ai';
        }
        return 'results'; // fallback
      };

      const loadedMessages = (sessionDetail.messages || []).map((msg: any, idx: number) => ({
        id: msg.id || `${selectedSessionId}-${idx}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        type: getMessageType(msg),
        content: msg.content,
        data: msg.metadata,
        analysisId: msg.analysisId,
        executionId: msg.executionId,
        timestamp: new Date(msg.timestamp || Date.now()),
      }));

      setMessages(loadedMessages);
      setCurrentSessionMessages({
        offset: sessionDetail.offset || 0,
        limit: sessionDetail.limit || 5,
        total: sessionDetail.total_messages || 0,
        hasOlder: sessionDetail.has_older || false,
      });
      
      console.log(`[Home] Resumed session ${selectedSessionId} with ${loadedMessages.length} messages`);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to resume session';
      setUIError(errorMsg);
      console.error('Resume session error:', err);
    } finally {
      setIsProcessing(false);
    }
  }, [getSessionDetail, resumeSession, updateSessionMetadata, setMessages, setUIError]);

  const handleLoadOlderMessages = useCallback(async () => {
    if (!session_id || isLoadingOlderMessages || !currentSessionMessages.hasOlder) return;

    try {
      setIsLoadingOlderMessages(true);
      const newOffset = currentSessionMessages.offset + currentSessionMessages.limit;
      
      const sessionDetail = await getSessionDetail(session_id, newOffset, currentSessionMessages.limit);
      if (!sessionDetail) {
        setUIError('Failed to load older messages');
        return;
      }

      const getMessageType = (msg: any) => {
        if (msg.role === 'user') return 'user';
        if (msg.role === 'assistant') {
          // Check if this assistant message contains analysis results
          if (msg.metadata && (
            msg.metadata.query_type || 
            msg.metadata.analysis_type || 
            msg.metadata.best_day ||
            msg.metadata.response_type === 'analysis' ||
            (msg.metadata.response_data && msg.metadata.response_data.analysis_result)
          )) {
            return 'results';
          }
          return 'ai';
        }
        return 'results'; // fallback
      };

      const olderMessages = (sessionDetail.messages || []).map((msg: any, idx: number) => ({
        id: msg.id || `${session_id}-${newOffset + idx}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        type: getMessageType(msg),
        content: msg.content,
        data: msg.metadata,
        analysisId: msg.analysisId,
        executionId: msg.executionId,
        timestamp: new Date(msg.timestamp || Date.now()),
      }));

      setMessages((prev) => [...olderMessages, ...prev]);
      setCurrentSessionMessages({
        offset: newOffset,
        limit: currentSessionMessages.limit,
        total: sessionDetail.total_messages || 0,
        hasOlder: sessionDetail.has_older || false,
      });

      console.log(`[Home] Loaded ${olderMessages.length} older messages`);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to load older messages';
      setUIError(errorMsg);
      console.error('Load older messages error:', err);
    } finally {
      setIsLoadingOlderMessages(false);
    }
  }, [session_id, currentSessionMessages, getSessionDetail, setMessages, setUIError, isLoadingOlderMessages]);

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
            <div className="flex gap-2">
              <button
                onClick={() => setViewMode('split')}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                title="Switch to split view"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                </svg>
              </button>
              <button
                onClick={() => setShowSessionHistory(true)}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                title="View chat history"
              >
                ☰
              </button>
            </div>

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
            progressLogs={progressLogs}
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

        {showSessionHistory && user_id && (
          <SessionList
            userId={user_id}
            currentSessionId={session_id || undefined}
            onSelectSession={handleSelectSession}
            isOpen={showSessionHistory}
            onClose={() => setShowSessionHistory(false)}
          />
        )}
      </div>
    );
  }

  return (
    <div className="h-screen bg-gray-50 flex">
      <div className="w-1/4 bg-white border-r border-gray-200 flex flex-col">
        <header className="border-b border-gray-200 px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex gap-1">
              <button
                onClick={() => setViewMode('single')}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                title="Switch to single view"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                </svg>
              </button>
              <button
                onClick={() => setShowSessionHistory(true)}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors text-lg"
                title="View chat history"
              >
                ☰
              </button>
            </div>

            <div className="text-center flex-1">
              <h1 className="text-sm font-bold text-gray-900">Chat</h1>
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
          progressLogs={progressLogs}
          onLoadOlder={handleLoadOlderMessages}
          isLoadingOlder={isLoadingOlderMessages}
          canLoadOlder={currentSessionMessages.hasOlder}
        />
      </div>

      <div className="w-1/4 bg-gray-900 border-r border-gray-700 flex flex-col">
        <ProgressPanel
          logs={progressLogs}
          isConnected={isConnected}
          isProcessing={isProcessing || analysisLoading}
          onClear={clearLogs}
        />
      </div>

      <div className="w-1/2 flex flex-col">
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

      {showSessionHistory && user_id && (
        <SessionList
          userId={user_id}
          currentSessionId={session_id || undefined}
          onSelectSession={handleSelectSession}
          isOpen={showSessionHistory}
          onClose={() => setShowSessionHistory(false)}
        />
      )}
    </div>
  );
}

export default function Home() {
  const { session_id } = useSession();
  
  return (
    <ProgressProvider sessionId={session_id}>
      <HomeContent />
    </ProgressProvider>
  );
}
