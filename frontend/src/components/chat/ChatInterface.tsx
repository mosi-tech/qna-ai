'use client';

import { useRef, useEffect } from 'react';
import { ChatMessage } from '@/lib/hooks/useConversation';
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
}

export default function ChatInterface({
  messages,
  chatInput,
  setChatInput,
  isProcessing,
  onSendMessage,
  onClarificationResponse,
  pendingClarificationId,
}: ChatInterfaceProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (chatInput.trim() && !isProcessing) {
      onSendMessage(chatInput);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
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
            <div className="bg-gray-100 rounded-lg p-3 max-w-md">
              <p className="text-sm text-gray-600">Analyzing...</p>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="border-t border-gray-200 p-4 bg-white">
        <div className="flex gap-2">
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
