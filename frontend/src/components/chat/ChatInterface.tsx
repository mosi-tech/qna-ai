'use client';

import { useRef, useEffect, useState } from 'react';
import { ChatMessage } from '@/lib/hooks/useConversation';
import { ProgressLog } from '@/lib/progress/ProgressManager';
import MockOutput from '@/components/MockOutput';
import ClarificationPrompt from './ClarificationPrompt';
import ClarificationSummary from './ClarificationSummary';

interface ChatInterfaceProps {
  messages: ChatMessage[];
  chatInput: string;
  setChatInput: (value: string) => void;
  isProcessing: boolean;
  onSendMessage: (message: string) => void;
  onClarificationResponse?: (response: string, clarificationData: any) => void;
  pendingClarificationId?: string | null;
  progressLogs?: ProgressLog[];
  onLoadOlder?: () => void;
  isLoadingOlder?: boolean;
  canLoadOlder?: boolean;
}

export default function ChatInterface({
  messages,
  chatInput,
  setChatInput,
  isProcessing,
  onSendMessage,
  onClarificationResponse,
  pendingClarificationId,
  progressLogs = [],
  onLoadOlder,
  isLoadingOlder = false,
  canLoadOlder = false,
}: ChatInterfaceProps) {
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const [isUserScrolling, setIsUserScrolling] = useState(false);

  const handleScroll = () => {
    if (!messagesContainerRef.current) return;
    
    const { scrollTop, scrollHeight, clientHeight } = messagesContainerRef.current;
    
    // Check if user has scrolled away from bottom
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
    setIsUserScrolling(!isAtBottom);
    
    // If scrolled near top (within 200px) and can load older, load them
    if (scrollTop < 200 && canLoadOlder && !isLoadingOlder && onLoadOlder) {
      onLoadOlder();
    }
  };

  useEffect(() => {
    // Always scroll to bottom if user hasn't scrolled away or on initial load
    if (messages.length > 0 && (!isUserScrolling || isInitialLoad)) {
      setTimeout(() => {
        if (messagesContainerRef.current) {
          messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
        }
        setIsInitialLoad(false);
      }, 0);
    }
  }, [messages, isInitialLoad, isUserScrolling]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (chatInput.trim() && !isProcessing) {
      onSendMessage(chatInput);
    }
  };

  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container) return;
    
    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, [canLoadOlder, isLoadingOlder, onLoadOlder]);

  return (
    <div className="flex flex-col h-full">
      <div 
        ref={messagesContainerRef}
        className="flex-1 overflow-y-auto p-4 space-y-4 flex flex-col items-center"
        onScroll={handleScroll}
      >
        <div className="w-full max-w-[70%] flex flex-col space-y-4">
          {isLoadingOlder && (
            <div className="flex justify-center py-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600" />
            </div>
          )}
          {messages.map((message) => (
          <div key={message.id} className="flex gap-3">
            {message.type === 'user' ? (
              <div className="flex gap-3 justify-end w-full">
                <div className="bg-blue-600 text-white rounded-lg p-3 max-w-md">
                  <p className="text-sm">{message.content}</p>
                </div>
                <div className="w-8 h-8 rounded-full bg-blue-200 flex items-center justify-center flex-shrink-0">
                  <span className="text-xs text-blue-600">You</span>
                </div>
              </div>
            ) : message.type === 'error' ? (
              <div className="flex gap-3 w-full">
                <div className="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
                  <span className="text-red-600 text-sm">✕</span>
                </div>
                <div className="bg-red-50 border border-red-200 rounded-lg p-3 max-w-md">
                  <p className="text-sm text-red-800">{message.content}</p>
                </div>
              </div>
            ) : message.type === 'clarification' ? (
              message.data ? (
                <ClarificationPrompt
                  originalQuery={message.data.original_query}
                  expandedQuery={message.data.expanded_query}
                  message={message.data.message || message.content}
                  suggestion={message.data.suggestion}
                  confidence={message.data.confidence}
                  isLoading={isProcessing && pendingClarificationId === message.id}
                  isPending={pendingClarificationId === message.id}
                  onConfirm={() => {
                    onClarificationResponse?.('yes', message.data);
                  }}
                  onReject={() => {
                    onClarificationResponse?.('no', message.data);
                  }}
                  onProvideDetails={(details) => {
                    onClarificationResponse?.(details, message.data);
                  }}
                />
              ) : (
                <ClarificationSummary
                  message={message.content}
                  expandedQuery={undefined}
                  status="pending"
                />
              )
            ) : message.type === 'results' ? (
              <div className="flex gap-3 w-full">
                <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                  <span className="text-green-600 text-sm">✓</span>
                </div>
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 max-w-2xl flex-1">
                  <p className="text-sm text-gray-800 mb-3">{message.content}</p>
                  {message.data && (
                    <MockOutput moduleKey={message.data.query_type || 'default'} />
                  )}
                </div>
              </div>
            ) : (
              <div className="flex gap-3 w-full">
                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                  <span className="text-blue-600 text-sm">AI</span>
                </div>
                <div className="bg-blue-50 rounded-lg p-3 max-w-md">
                  <p className="text-sm text-gray-800">{message.content}</p>
                </div>
              </div>
            )}
          </div>
          ))}

          {isProcessing && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                <div className="w-4 h-4 border-2 border-gray-400 border-t-gray-600 rounded-full animate-spin"></div>
              </div>
              <div className="bg-gray-100 rounded-lg p-3 max-w-2xl flex-1">
                {progressLogs.length === 0 && console.log('[ChatInterface] progressLogs is empty, count:', progressLogs.length)}
                <div className="space-y-2">
                  {progressLogs.length > 0 ? (
                    <>
                      {progressLogs.map((log, idx) => (
                        <div key={log.id || idx} className="text-sm text-gray-700 flex items-start gap-2">
                          <span className="flex-shrink-0 mt-0.5">
                            {log.level === 'success' && <span className="text-green-600">✓</span>}
                            {log.level === 'error' && <span className="text-red-600">✕</span>}
                            {log.level === 'warning' && <span className="text-yellow-600">⚠</span>}
                            {log.level === 'info' && <span className="text-blue-600">•</span>}
                          </span>
                          <div className="flex-1">
                            <span>{log.message}</span>
                            {log.step && log.totalSteps && (
                              <span className="text-xs text-gray-500 ml-2">
                                (Step {log.step}/{log.totalSteps})
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                    </>
                  ) : (
                    <p className="text-sm text-gray-600">Analyzing...</p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="border-t border-gray-200 p-4 bg-white flex justify-center">
        <div className="w-full max-w-[70%] flex gap-2">
          <input
            type="text"
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            placeholder="Ask a financial question..."
            disabled={isProcessing}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isProcessing || !chatInput.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
