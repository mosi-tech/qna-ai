'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
import { useSession } from '@/lib/context/SessionContext';
import { useConversation } from '@/lib/context/ConversationContext';
import { ChatMessage } from '@/lib/hooks/useConversation';
import { useUI } from '@/lib/context/UIContext';
import { useAnalysis } from '@/lib/hooks/useAnalysis';
import { useSessionManager } from '@/lib/hooks/useSessionManager';
import { ProgressProvider, useProgress } from '@/lib/context/ProgressContext';
import ChatInterface from '@/components/chat/ChatInterface';
import AnalysisPanel from '@/components/chat/AnalysisPanel';
import ProgressPanel from '@/components/progress/ProgressPanel';
import CustomizationForm from '@/components/chat/CustomizationForm';
import SessionList from '@/components/chat/SessionList';
import UserMenu from '@/components/auth/UserMenu';
import { ParameterValues } from '@/types/modules';
import { ProgressManager } from '@/lib/progress/ProgressManager';
import { withAuth } from '@/lib/context/AuthContext';
import { apiClient } from '@/lib/api/client';

function ChatPageContent({ overrideSessionId }: { overrideSessionId?: string | null }) {
  const { session_id: contextSessionId, user_id, resumeSession, updateSessionMetadata, startNewSession } = useSession();
  
  // Use override session ID if provided, otherwise use context session ID
  const session_id = overrideSessionId || contextSessionId;
  
  console.log('[ChatPageContent] Authentication status:', { 
    user_id, 
    session_id, 
    overrideSessionId,
    contextSessionId 
  });
  const { messages, addMessage, updateMessage, setMessages } = useConversation();
  const { viewMode, setViewMode, isProcessing, setIsProcessing, error: uiError, setError: setUIError } = useUI();
  const { sendChatMessage, isLoading: analysisLoading } = useAnalysis();
  const { logs: progressLogs, isConnected, clearLogs, registerAnalysisCompleteCallback } = useProgress();
  const { getSessionDetail } = useSessionManager();

  // Function to fetch updated message content from API
  const fetchUpdatedMessage = useCallback(async (messageId: string) => {
    if (!session_id) {
      console.warn('No session_id available for fetching message');
      return null;
    }

    try {
      const response = await apiClient.get(`/api/sessions/${session_id}/messages/${messageId}`);
      if (response.success && response.data) {
        return response.data;
      } else {
        console.warn(`Failed to fetch updated message ${messageId}`);
        return null;
      }
    } catch (error) {
      console.error(`Error fetching updated message ${messageId}:`, error);
      return null;
    }
  }, [session_id]);

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
    limit: 10,
    total: 0,
    hasOlder: false,
  });
  const [sessionNotFound, setSessionNotFound] = useState(false);
  const loadedSessionIdRef = useRef<string | null>(null);

  useEffect(() => {
    console.log('[ChatPageContent] useEffect triggered:', { 
      session_id, 
      loadedSessionIdRef: loadedSessionIdRef.current,
      condition: !session_id || loadedSessionIdRef.current === session_id
    });
    
    if (!session_id) {
      console.log('[ChatPageContent] No session_id, skipping message load');
      return;
    }
    
    if (loadedSessionIdRef.current === session_id) {
      console.log('[ChatPageContent] Session already loaded, skipping');
      return;
    }

    console.log('[ChatPageContent] Loading messages for session:', session_id);
    loadedSessionIdRef.current = session_id;
    setSessionNotFound(false);  // Reset 404 state when session changes

    const loadInitialMessages = async () => {
      try {
        console.log('[ChatPageContent] Calling getSessionDetail for:', session_id);
        const sessionDetail = await getSessionDetail(session_id, 0, 10);  // Load 10 messages initially
        console.log('[ChatPageContent] getSessionDetail result:', sessionDetail);
        
        if (!sessionDetail) {
          console.log('[ChatPageContent] No session detail returned, setting sessionNotFound');
          setSessionNotFound(true);
          return;
        }
        const loadedMessages = (sessionDetail.messages || []).map((msg: any, idx: number) => {
          console.log(`[DEBUG] Loading message ${idx}:`, msg);
          return {
            id: msg.id || `${session_id}-${idx}-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`,
            type: (msg.role === 'user' ? 'user' : 'ai') as ChatMessage['type'],
            ...msg,  // Flatten all message properties directly
            timestamp: new Date(msg.timestamp || Date.now()),
          };
        });

        console.log('[ChatPageContent] Processed messages:', loadedMessages);
        
        if (loadedMessages.length > 0) {
          console.log('[ChatPageContent] Setting messages in state:', loadedMessages.length);
          setMessages(loadedMessages);
          setCurrentSessionMessages({
            offset: sessionDetail.offset || 0,
            limit: sessionDetail.limit || 10,
            total: sessionDetail.total_messages || 0,
            hasOlder: sessionDetail.has_older || false,
          });
        } else {
          console.log('[ChatPageContent] No messages to load, sessionDetail.messages:', sessionDetail.messages);
        }
      } catch (err) {
        console.warn('Failed to load initial session messages:', err);
        setSessionNotFound(true);
      }
    };

    loadInitialMessages();
  }, [session_id, getSessionDetail, setMessages]);


  // Helper functions for handleSendMessage
  const setupAnalysisRequest = (userMessage: string) => {
    setIsProcessing(true);
    setChatInput('');
    setUIError(null);
    clearLogs();

    if (session_id) {
      ProgressManager.addLog(session_id, {
        level: 'info',
        message: `Processing question: "${userMessage}"`,
      });
    }

    // Clear any pending clarification
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
  };

  const handleMeaninglessResponse = (response: any) => {
    if (session_id) {
      ProgressManager.addLog(session_id, {
        level: 'warning',
        message: 'Query was not specific enough. Requesting clarification.',
      });
    }

    const errorMsg = response.data.content || 'I need more details to help you. Please tell me what you\'d like to analyze.';
    addMessage({
      type: 'ai',
      content: errorMsg,
    });
  };

  const handleClarificationResponse = (response: any, userMessage: string) => {
    const clarificationData = {
      message_id: response.data.id,
      content: response.data.content,
      ...response.data.metadata,
    };

    if (session_id) {
      ProgressManager.addLog(session_id, {
        level: 'info',
        message: 'Analysis requires user clarification',
        details: {
          confidence: response.data.expansion_confidence || response.data.metadata?.confidence,
        },
      });
    }

    const clarificationMsg = addMessage({
      type: 'clarification',
      content: clarificationData.content || 'Please confirm the interpretation',
      data: clarificationData,
    });

    setLastClarificationMessageId(clarificationMsg.id);
    setCurrentAnalysis({
      messageId: clarificationMsg.id,
      data: clarificationData,
      originalQuestion: userMessage,
    });
  };

  const handleConfirmationResponse = (response: any, userMessage: string) => {
    const clarificationData = {
      message_id: response.data.id,
      content: response.data.content,
      ...response.data.metadata,
    };

    if (session_id) {
      ProgressManager.addLog(session_id, {
        level: 'info',
        message: 'Analysis requires user confirmation',
      });
    }

    const confirmMsg = addMessage({
      type: 'clarification',
      content: clarificationData.content || 'Please confirm',
      data: clarificationData,
    });

    setCurrentAnalysis({
      messageId: confirmMsg.id,
      data: clarificationData,
      originalQuestion: userMessage,
    });
  };

  const handleChatResponse = (response: any) => {
    if (session_id) {
      ProgressManager.addLog(session_id, {
        level: 'success',
        message: 'Chat response ready',
      });
    }

    // Simple chat message - no analysis or execution tracking
    addMessage({
      type: 'ai',
      content: response.data.content || 'Chat response received',
      ...response.data,
      status: 'completed', // Always completed for chat
    });
  };

  const handleAnalysisTriggerResponse = (response: any, userMessage: string) => {
    if (session_id) {
      ProgressManager.addLog(session_id, {
        level: 'info',
        message: 'Analysis triggered - processing...',
      });
    }


    // Create pending message that will show "Analysis in Progress"
    const resultMsg = addMessage({
      type: 'results',
      content: response.data.content || 'Analysis in progress...',
      status: 'pending', // This triggers the pending UI
      ...response.data,
    });

    // Register completion callback for SSE events if analysis was triggered
    const backendMessageId = response.data.id;

    if (backendMessageId) {
      registerAnalysisCompleteCallback(backendMessageId, async (completionStatus: 'completed' | 'failed', data?: any) => {
        // For completed status, fetch updated message content from API instead of relying on SSE data
        if (completionStatus === 'completed') {
          const updatedMessage = await fetchUpdatedMessage(backendMessageId);
          if (updatedMessage) {
            updateMessage(backendMessageId, {
              ...updatedMessage,
              content: updatedMessage.content,
              status: 'completed',
              response_type: updatedMessage.response_type,
            });
            return;
          }
        }

        // Fallback to SSE data for failed status or if fetch fails
        updateMessage(backendMessageId, {
          content: data?.message,
          status: completionStatus,
          error: data?.error,
          ...(data?.details || {}),
        });
      });

      console.log(`[SSE] Registered callback for message: ${backendMessageId}`);
    } else {
      console.error('[SSE] No backend message ID found or analysis not triggered!', response.data);
    }

    setCurrentAnalysis({
      messageId: resultMsg.id,
      data: response.data,
      originalQuestion: userMessage,
    });
  };

  const handleAnalysisResponse = (response: any, userMessage: string) => {
    if (session_id) {
      ProgressManager.addLog(session_id, {
        level: 'success',
        message: 'Analysis results ready for display',
      });
    }

    const resultMsg = addMessage({
      type: 'results',
      //TODO: check if we need backfill
      content: response.data.content || response.data.metadata?.analysis_summary || `Analysis complete for: ${userMessage}`,
      ...response.data,
    });

    // Register completion callback for SSE events
    const backendMessageId = response.data.id;

    if (backendMessageId) {
      registerAnalysisCompleteCallback(backendMessageId, async (completionStatus: 'completed' | 'failed', data?: any) => {
        // For completed status, fetch updated message content from API instead of relying on SSE data
        if (completionStatus === 'completed') {
          const updatedMessage = await fetchUpdatedMessage(backendMessageId);
          if (updatedMessage) {
            updateMessage(backendMessageId, {
              ...updatedMessage,
              content: updatedMessage.content,
              status: 'completed',
              response_type: updatedMessage.response_type,
            });
            return;
          }
        }

        // Fallback to SSE data for failed status or if fetch fails
        updateMessage(backendMessageId, {
          content: data?.message,
          status: completionStatus,
          error: data?.error,
          ...(data?.details || {}),
        });
      });

      console.log(`[SSE] Registered callback for message: ${backendMessageId}`);
    } else {
      console.error('[SSE] No backend message ID found - callback not registered!', response.data);
    }

    setCurrentAnalysis({
      messageId: resultMsg.id,
      data: response.data,
      originalQuestion: userMessage,
    });
  };

  const handleAnalysisError = (response: any) => {
    if (session_id) {
      ProgressManager.addLog(session_id, {
        level: 'error',
        message: response.error || 'Analysis failed',
      });
    }

    const errorContent = response.error || 'Analysis failed. Please try again.';
    addMessage({
      type: 'error',
      content: errorContent,
    });
    setUIError(response.error || 'Analysis failed');
  };

  const handleSendMessage = async (userMessage: string) => {
    if (!session_id || !userMessage.trim()) return;

    try {
      setupAnalysisRequest(userMessage);

      if (session_id) {
        ProgressManager.addLog(session_id, {
          level: 'info',
          message: 'Sending analysis request to server...',
        });
      }

      const response = await sendChatMessage({
        question: userMessage,
        session_id: session_id,
      });

      if (response.success && response.data) {
        if (session_id) {
          ProgressManager.addLog(session_id, {
            level: 'success',
            message: 'Analysis request completed successfully',
          });
        }

        const responseType = response.data.response_type;

        if (responseType === 'meaningless') {
          handleMeaninglessResponse(response);
        } else if (responseType === 'needs_clarification') {
          handleClarificationResponse(response, userMessage);
        } else if (responseType === 'needs_confirmation') {
          handleConfirmationResponse(response, userMessage);
        } else if (responseType === 'chat_response' || responseType === 'educational') {
          // Handle pure chat responses
          handleChatResponse(response);
        } else if (responseType === 'script_generation') {
          // Handle analysis trigger responses (thinking state)
          handleAnalysisTriggerResponse(response, userMessage);
        } else {
          // Default to analysis response for backward compatibility
          handleAnalysisResponse(response, userMessage);
        }
      } else {
        handleAnalysisError(response);
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'An error occurred';
      if (session_id) {
        ProgressManager.addLog(session_id, {
          level: 'error',
          message: `Exception: ${errorMsg}`,
        });
      }

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

  const handleExecutionUpdate = useCallback((messageId: string, update: any) => {
    // Enhanced SSE Event Logging
    console.group('%c[SSE EVENT RECEIVED]', 'color: blue; font-weight: bold; font-size: 14px;');
    console.log('%cMessage ID:', 'font-weight: bold;', messageId);
    console.log('%cFull SSE Event:', 'font-weight: bold;', update);
    console.log('%cSSE Event Type:', 'font-weight: bold;', update.type);
    console.log('%cSSE Level:', 'font-weight: bold;', update.level);
    console.log('%cSSE Message:', 'font-weight: bold;', update.message);
    console.log('%cSSE Details:', 'font-weight: bold;', update.details);

    // Map SSE event details to proper message structure
    const details = update.details || {};
    const messageUpdate: any = {};

    // Map core status and content
    if (details.status) {
      messageUpdate.status = details.status;
    }
    if (update.error) {
      messageUpdate.error = update.error;
    }
    if (update.message || details.content) {
      messageUpdate.content = update.message || details.content;
    }

    // Map execution data to execution object structure (matching API response format)
    if (details.status || details.error || details.execution_id) {
      messageUpdate.execution = {
        ...(messageUpdate.execution || {}),
        status: details.status,
        error: details.error,
        executionId: details.execution_id,
      };
    }

    // Map response type and IDs
    if (details.response_type) {
      messageUpdate.response_type = details.response_type;
    }
    if (details.analysis_id) {
      messageUpdate.analysisId = details.analysis_id;
    }
    if (details.execution_id) {
      messageUpdate.executionId = details.execution_id;
    }

    // Update UI controls based on status
    if (details.status === 'failed') {
      messageUpdate.canRerun = true;
      messageUpdate.canExport = false;
    } else if (details.status === 'completed') {
      messageUpdate.canRerun = true;
      messageUpdate.canExport = true;
    }

    if (details.results) {
      messageUpdate.results = details.results
    }

    // Log the mapped message update
    console.log('%cMapped Message Update:', 'font-weight: bold; color: green;', messageUpdate);

    // Note: This function only UPDATES existing messages, never creates new ones
    const isCompletionStatus = details.status === 'failed' || details.status === 'completed';
    const hasMessageId = !!details.message_id;

    console.log('%cMessage Update Analysis:', 'font-weight: bold; color: purple;');
    console.log('%c- Status is completion status (failed/completed):', 'color: purple;', isCompletionStatus, `(${details.status})`);
    console.log('%c- Has message_id:', 'color: purple;', hasMessageId, `(${details.message_id})`);
    console.log('%c- Target Message ID for update:', 'color: purple;', messageId);

    if (isCompletionStatus) {
      console.log('%c✅ COMPLETION STATUS - Message will be marked as finished', 'color: green; font-size: 14px; font-weight: bold;');
    } else {
      console.log('%c📝 Progress update - Message remains in progress', 'color: orange; font-weight: bold;');
    }

    console.log('%c⚠️  NOTE: This function only UPDATES existing messages, never creates new ones', 'color: orange; font-style: italic;');

    console.groupEnd();

    updateMessage(messageId, messageUpdate);
  }, [updateMessage]);

  // Re-register SSE callbacks for pending messages on page refresh
  useEffect(() => {
    console.log(`[DEBUG] Callback registration effect triggered: messages.length=${messages.length}, isConnected=${isConnected}`);

    if (!messages.length || !isConnected) {
      console.log(`[DEBUG] Skipping callback registration - messages=${messages.length}, connected=${isConnected}`);
      return;
    }

    // Add a small delay to ensure SSE connection is fully established
    const timeoutId = setTimeout(() => {
      console.log(`[DEBUG] Starting callback registration after delay...`);

      let registeredCount = 0;
      messages.forEach((message: ChatMessage) => {
        // Check if message is in pending status and has backend ID for callback registration
        const isPending = message.status && ['pending', 'running', 'queued'].includes(message.status);
        const backendMessageId = (message as any).id;

        console.log(`[DEBUG] Message ${message.id}: status=${message.status}, isPending=${isPending}, backendId=${backendMessageId}`, message);

        if (isPending && backendMessageId) {
          console.log(`[SSE] Re-registering callback for pending message: ${backendMessageId}`);
          registeredCount++;

          registerAnalysisCompleteCallback(backendMessageId, async (completionStatus: 'completed' | 'failed', data?: any) => {
            console.log(`[SSE] Callback triggered for message ${backendMessageId} with status: ${completionStatus}`);
            
            // For completed status, fetch updated message content from API instead of relying on SSE data
            if (completionStatus === 'completed') {
              const updatedMessage = await fetchUpdatedMessage(backendMessageId);
              if (updatedMessage) {
                updateMessage(backendMessageId, {
                  ...updatedMessage,
                  content: updatedMessage.content,
                  status: 'completed',
                  response_type: updatedMessage.response_type,
                });
                return;
              }
            }
            
            // Fallback to SSE data for failed status or if fetch fails
            updateMessage(backendMessageId, {
              content: data?.message,
              status: completionStatus,
              error: data?.error,
              ...(data?.details || {}),
            });
          });
        }
      });

      console.log(`[DEBUG] Registered ${registeredCount} callbacks`);
    }, 500); // Wait 500ms for SSE connection to stabilize

    return () => clearTimeout(timeoutId);
  }, [messages, isConnected, registerAnalysisCompleteCallback, handleExecutionUpdate]);

  const handleSelectSession = useCallback(async (selectedSessionId: string) => {
    try {
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

      // Navigate to new session if different
      if (selectedSessionId !== session_id) {
        await resumeSession(selectedSessionId);
        return; // Navigation will reload the page, let it handle loading messages
      }

      // If same session, just load fresh messages without navigation
      const sessionDetail = await getSessionDetail(selectedSessionId, 0, 5);
      if (!sessionDetail) {
        setUIError('Failed to load session');
        return;
      }
      updateSessionMetadata({
        title: sessionDetail.title,
        created_at: sessionDetail.created_at,
        updated_at: sessionDetail.updated_at,
        is_archived: sessionDetail.is_archived,
      });

      const loadedMessages = (sessionDetail.messages || []).map((msg: any, idx: number) => ({
        id: msg.id || `${selectedSessionId}-${idx}-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`,
        type: (msg.role === 'user' ? 'user' : 'ai') as ChatMessage['type'],
        ...msg,  // Flatten all message properties directly
        timestamp: new Date(msg.timestamp || Date.now()),
      }));

      setMessages(loadedMessages);
      setCurrentSessionMessages({
        offset: sessionDetail.offset || 0,
        limit: sessionDetail.limit || 5,
        total: sessionDetail.total_messages || 0,
        hasOlder: sessionDetail.has_older || false,
      });

      console.log(`[ChatPage] Resumed session ${selectedSessionId} with ${loadedMessages.length} messages`);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to resume session';
      setUIError(errorMsg);
      console.error('Resume session error:', err);
    } finally {
      setIsProcessing(false);
    }
  }, [session_id, getSessionDetail, resumeSession, updateSessionMetadata, setMessages, setUIError]);

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

      const olderMessages: ChatMessage[] = (sessionDetail.messages || []).map((msg: any, idx: number) => ({
        id: msg.id || `${session_id}-${newOffset + idx}-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`,
        type: (msg.role === 'user' ? 'user' : 'ai') as ChatMessage['type'],
        ...msg,  // Flatten all message properties directly
        timestamp: new Date(msg.timestamp || Date.now()),
      }));

      // Deduplicate: filter out messages that already exist
      const existingIds = new Set(messages.map((msg: ChatMessage) => msg.id));
      const newMessages = olderMessages.filter((msg: ChatMessage) => !existingIds.has(msg.id));
      setMessages([...newMessages, ...messages]);
      setCurrentSessionMessages({
        offset: newOffset,
        limit: currentSessionMessages.limit,
        total: sessionDetail.total_messages || 0,
        hasOlder: sessionDetail.has_older || false,
      });

      console.log(`[ChatPage] Loaded ${olderMessages.length} older messages`);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to load older messages';
      setUIError(errorMsg);
      console.error('Load older messages error:', err);
    } finally {
      setIsLoadingOlderMessages(false);
    }
  }, [session_id, currentSessionMessages, getSessionDetail, setMessages, setUIError, isLoadingOlderMessages]);

  const handleStartNewChat = useCallback(async () => {
    try {
      setIsProcessing(true);
      // Call startNewSession to create a new session server-side
      // This will create the session and navigate to the new session URL
      await startNewSession();
      setSessionNotFound(false);
      setMessages([]);
    } catch (err) {
      console.error('Failed to create new session:', err);
      setUIError('Failed to create new session');
    } finally {
      setIsProcessing(false);
    }
  }, [startNewSession, user_id, setMessages, setUIError, setIsProcessing, setSessionNotFound]);

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

  if (sessionNotFound) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-6xl font-bold text-gray-300 mb-4">404</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Session Not Found</h1>
          <p className="text-gray-600 mb-6">
            The session <code className="bg-gray-100 px-2 py-1 rounded text-sm">{session_id}</code> does not exist.
          </p>
          <button
            onClick={handleStartNewChat}
            disabled={isProcessing}
            className="inline-block bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-blue-400 disabled:cursor-not-allowed"
          >
            {isProcessing ? 'Creating...' : 'Start a New Chat'}
          </button>
        </div>
      </div>
    );
  }

  if (viewMode === 'single') {
    return (
      <div className="h-screen bg-gray-50 flex flex-col overflow-hidden">
        {/* Top Header with Logout */}
        <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-xl font-bold text-gray-900">Financial Analysis Chat</h1>
            <span className="text-sm text-gray-500">Session: {session_id?.slice(0, 8)}...</span>
          </div>
          <UserMenu />
        </header>

        {/* Main Content */}
        <div className="flex-1 flex overflow-hidden">
          {showSessionHistory && user_id && (
            <div className="w-96 border-r border-gray-200 flex flex-col">
              <SessionList
                userId={user_id}
                currentSessionId={session_id || undefined}
                onSelectSession={handleSelectSession}
                isOpen={showSessionHistory}
                onClose={() => setShowSessionHistory(false)}
              />
            </div>
          )}
          <div className="flex-1 flex flex-col">
          {!showSessionHistory && (
            <div className="border-b border-gray-200 px-4 py-3 flex items-center gap-2">
              <button
                onClick={() => setShowSessionHistory(!showSessionHistory)}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                title={showSessionHistory ? "Close chat history" : "Open chat history"}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={showSessionHistory ? "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" : "M4 6h16M4 12h16M4 18h16"} />
                </svg>
              </button>
              <button
                onClick={() => setViewMode('split')}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                title="Switch to split view"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                </svg>
              </button>
            </div>
          )}
          <ChatInterface
            messages={messages}
            chatInput={chatInput}
            setChatInput={setChatInput}
            isProcessing={isProcessing || analysisLoading}
            onSendMessage={handleSendMessage}
            onClarificationResponse={handleClarificationResponse}
            pendingClarificationId={lastClarificationMessageId}
            onLoadOlder={handleLoadOlderMessages}
            isLoadingOlder={isLoadingOlderMessages}
            canLoadOlder={currentSessionMessages.hasOlder}
            onExecutionUpdate={handleExecutionUpdate}
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
      </div>
    );
  }

  return (
    <div className="h-screen bg-gray-50 flex flex-col">
      {/* Top Header with Logout */}
      <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-bold text-gray-900">Financial Analysis Chat</h1>
          <span className="text-sm text-gray-500">Session: {session_id?.slice(0, 8)}...</span>
        </div>
        <UserMenu />
      </header>

      {/* Main Content Area */}
      <div className="flex-1 flex">
          <div className="w-1/4 bg-white border-r border-gray-200 flex flex-col relative">
            <div className="border-b border-gray-200 px-4 py-3 flex items-center justify-between">
              <h1 className="text-sm font-bold text-gray-900">Chat History</h1>
              <button
                onClick={() => setViewMode('single')}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                title="Switch to single view"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                </svg>
              </button>
            </div>
            <SessionList
              userId={user_id || ''}
              currentSessionId={session_id || undefined}
              onSelectSession={handleSelectSession}
              isOpen={true}
              onClose={() => { }}
              hideHeader={true}
            />
          </div>

          <div className="flex-1 flex flex-col">
            <ChatInterface
              messages={messages}
              chatInput={chatInput}
              setChatInput={setChatInput}
              isProcessing={isProcessing || analysisLoading}
              onSendMessage={handleSendMessage}
              onClarificationResponse={handleClarificationResponse}
              pendingClarificationId={lastClarificationMessageId}
              onLoadOlder={handleLoadOlderMessages}
              isLoadingOlder={isLoadingOlderMessages}
              canLoadOlder={currentSessionMessages.hasOlder}
              onExecutionUpdate={handleExecutionUpdate}
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

interface ChatPageProps {
  params: {
    sessionId: string;
  };
}

function ChatPage({ params }: ChatPageProps) {
  const { sessionId } = params;

  return (
    <ProgressProvider sessionId={sessionId}>
      <ChatPageWithSession sessionId={sessionId} />
    </ProgressProvider>
  );
}

// Export with authentication protection
export default withAuth(ChatPage);

function ChatPageWithSession({ sessionId }: { sessionId: string }) {
  const { session_id, resumeSession, isLoading } = useSession();
  const [initializing, setInitializing] = useState(true);
  const [forceSessionId, setForceSessionId] = useState<string | null>(null);

  // Initialize session when component mounts
  useEffect(() => {
    const initializeSession = async () => {
      if (sessionId && sessionId !== session_id) {
        try {
          await resumeSession(sessionId);
        } catch (error) {
          console.error('Failed to initialize session via resumeSession:', error);
          // If resumeSession fails, force the sessionId for the chat interface
          console.log('Using fallback: setting session_id directly from URL parameter:', sessionId);
          setForceSessionId(sessionId);
        }
      }
      setInitializing(false);
    };

    initializeSession();
  }, [sessionId, session_id, resumeSession]);

  // Show loading while initializing or session is loading
  if (initializing || isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Loading session...</span>
      </div>
    );
  }

  // Pass the effective session ID (from context or fallback)
  const effectiveSessionId = session_id || forceSessionId;
  
  return <ChatPageContent overrideSessionId={effectiveSessionId} />;
}
