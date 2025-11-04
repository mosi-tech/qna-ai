'use client';

import { useRef, useEffect, useLayoutEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { ChatMessage as ChatMessageType } from '@/lib/hooks/useConversation';
import ChatMessage from './ChatMessage';

interface ChatInterfaceProps {
  messages: ChatMessageType[];
  chatInput: string;
  setChatInput: (value: string) => void;
  isProcessing: boolean;
  onSendMessage: (message: string) => void;
  onClarificationResponse?: (response: string, clarificationData: any) => void;
  pendingClarificationId?: string | null;
  onLoadOlder?: () => void;
  isLoadingOlder?: boolean;
  canLoadOlder?: boolean;
  onExecutionUpdate?: (messageId: string, update: any) => void;
}

export default function ChatInterface({
  messages,
  chatInput,
  setChatInput,
  isProcessing,
  onSendMessage,
  onClarificationResponse,
  pendingClarificationId,
  onLoadOlder,
  isLoadingOlder = false,
  canLoadOlder = false,
  onExecutionUpdate,
}: ChatInterfaceProps) {
  const router = useRouter();
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const [isUserScrolling, setIsUserScrolling] = useState(false);
  const previousScrollHeightRef = useRef(0);
  const previousMessageCountRef = useRef(0);
  const wasLoadingOlderRef = useRef(false);
  const savedScrollTopRef = useRef(0);

  // Debounced load older function to prevent multiple rapid calls
  const loadOlderTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const debouncedLoadOlder = useCallback(() => {
    if (!onLoadOlder || isLoadingOlder || !canLoadOlder) return;
    
    // Clear existing timeout
    if (loadOlderTimeoutRef.current) {
      clearTimeout(loadOlderTimeoutRef.current);
    }
    
    // Set new timeout for debounced call
    loadOlderTimeoutRef.current = setTimeout(() => {
      if (onLoadOlder && !isLoadingOlder && canLoadOlder) {
        // Save current scroll position before loading
        if (messagesContainerRef.current) {
          savedScrollTopRef.current = messagesContainerRef.current.scrollTop;
          previousScrollHeightRef.current = messagesContainerRef.current.scrollHeight;
        }
        onLoadOlder();
      }
    }, 200); // 200ms debounce
  }, [onLoadOlder, isLoadingOlder, canLoadOlder]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (loadOlderTimeoutRef.current) {
        clearTimeout(loadOlderTimeoutRef.current);
      }
    };
  }, []);



  const handleScroll = () => {
    if (!messagesContainerRef.current) return;

    const { scrollTop, scrollHeight, clientHeight } = messagesContainerRef.current;

    // Check if user has scrolled away from bottom
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
    setIsUserScrolling(!isAtBottom);

    // If scrolled near top (within 400px) and can load older, load them (debounced)
    if (scrollTop < 400 && canLoadOlder && !isLoadingOlder) {
      console.log('[ChatInterface] Triggering load older - scrollTop:', scrollTop);
      debouncedLoadOlder();
    }
  };

  useLayoutEffect(() => {
    if (!messagesContainerRef.current || messages.length === 0) return;

    const container = messagesContainerRef.current;
    const currentScrollHeight = container.scrollHeight;

    // Detect if older messages just finished loading (was loading, now not loading, and messages increased)
    const justFinishedLoadingOlder = wasLoadingOlderRef.current && !isLoadingOlder;
    const messageCountIncreased = messages.length > previousMessageCountRef.current;
    const heightIncreased = currentScrollHeight > previousScrollHeightRef.current;
    
    if (justFinishedLoadingOlder && messageCountIncreased && heightIncreased && previousScrollHeightRef.current > 0) {
      // Maintain scroll position: calculate exactly where user was
      const heightDifference = currentScrollHeight - previousScrollHeightRef.current;
      const newScrollTop = savedScrollTopRef.current + heightDifference;
      
      // Instantly set scroll position to maintain user's view (no animation)
      container.scrollTop = newScrollTop;
      
      console.log('[ChatInterface] Maintained scroll position after loading older messages', {
        savedScrollTop: savedScrollTopRef.current,
        heightDifference,
        newScrollTop
      });
    }
    // Otherwise, scroll to bottom for new messages (if user hasn't scrolled away or initial load)
    else if (!isUserScrolling || isInitialLoad) {
      setTimeout(() => {
        container.scrollTop = container.scrollHeight;
        // Scroll a bit more to ensure bottom message is fully visible
        container.scrollTop += 50;
        setIsInitialLoad(false);
      }, 0);
    }

    // Update previous values for next comparison
    previousScrollHeightRef.current = currentScrollHeight;
    previousMessageCountRef.current = messages.length;
    wasLoadingOlderRef.current = isLoadingOlder;
  }, [messages, isInitialLoad, isUserScrolling, isLoadingOlder]);

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
        style={{ paddingBottom: '200px' }}
        onScroll={handleScroll}
      >
        <div className="w-full max-w-[70%] flex flex-col space-y-4">
          {isLoadingOlder && (
            <div className="flex justify-center py-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600" />
            </div>
          )}
          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message}
              onClarificationResponse={onClarificationResponse}
              pendingClarificationId={pendingClarificationId}
              onExecutionUpdate={onExecutionUpdate}
            />
          ))}

        </div>
      </div>

      <form onSubmit={handleSubmit} className="fixed bottom-0 left-0 right-0 border-t border-gray-200 p-4 bg-white flex justify-center z-10">
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
