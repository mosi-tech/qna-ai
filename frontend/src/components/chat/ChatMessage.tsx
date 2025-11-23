'use client';

import React from 'react';
import AnalysisResult from './AnalysisResult';
import ClarificationPrompt from './ClarificationPrompt';
import ClarificationSummary from './ClarificationSummary';
import StepProgressDisplay from '@/components/progress/StepProgressDisplay';
import UIConfigurationRenderer from '@/components/insights/UIConfigurationRenderer';
import { useProgress } from '@/lib/context/ProgressContext';
import { renderMarkdown } from '@/lib/utils/markdown';

// Helper function to detect if a message has UI configuration data
const hasUIConfig = (message: any): boolean => {
  // Check the main location where UI config is stored by data transformer
  const uiConfig = message.results?.ui_config || 
                   message.data?.results?.ui_config || 
                   message.data?.ui_config;
  
  return Boolean(
    uiConfig && 
    uiConfig.ui_config?.selected_components && 
    Array.isArray(uiConfig.ui_config.selected_components) && 
    uiConfig.ui_config.selected_components.length > 0
  );
};

// Helper function to extract UI configuration data from message
const getUIConfig = (message: any) => {
  // Check the main location where UI config is stored by data transformer
  return message.results?.ui_config || 
         message.data?.results?.ui_config || 
         message.data?.ui_config;
};

interface ChatMessageProps {
  message: {
    id: string;
    role?: 'user' | 'assistant';
    type?: string; // Legacy field for backward compatibility
    content: string;
    timestamp: Date;
    status?: 'pending' | 'running' | 'completed' | 'failed';
    response_type?: 'script_generation' | 'meaningless' | 'needs_clarification';
    data?: any;
    analysisId?: string;
    executionId?: string;
  };
  onClarificationResponse?: (response: string, clarificationData: any) => void;
  pendingClarificationId?: string | null;
  onExecutionUpdate?: (messageId: string, update: any) => void;
}

export default function ChatMessage({
  message,
  onClarificationResponse,
  pendingClarificationId,
  onExecutionUpdate
}: ChatMessageProps) {
  const { logs: progressLogs } = useProgress();

  // Handle user messages
  if (message.role === 'user' || message.type === 'user') {
    return (
      <div className="flex gap-3 justify-end w-full">
        <div className="bg-blue-600 text-white rounded-lg p-3 max-w-md">
          <p className="text-sm">{message.content}</p>
        </div>
        <div className="w-8 h-8 rounded-full bg-blue-200 flex items-center justify-center flex-shrink-0">
          <span className="text-xs text-blue-600">You</span>
        </div>
      </div>
    );
  }

  // Handle error messages
  if (message.type === 'error' || message.status === 'failed' || message.data?.status === 'failed') {
    const errorMessage = message.data?.error || message.content || 'Analysis failed';
    const questionText = message.data?.question || 'Unknown question';

    return (
      <div className="flex gap-3 w-full">
        <div className="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
          <span className="text-red-600 text-sm">✕</span>
        </div>
        <div className="flex-1 max-w-4xl">
          <div className="bg-white border border-red-200 rounded-lg overflow-hidden">
            <div className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-6 h-6 bg-red-100 rounded-full flex items-center justify-center">
                  <span className="text-red-600 text-sm">✕</span>
                </div>
                <h3 className="text-lg font-semibold text-red-900">Analysis Failed</h3>
              </div>
              <p className="text-sm text-gray-600 mb-3">{questionText}</p>
              {/* Show structured error message */}
              {message.data?.error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-3">
                  <p className="text-sm text-red-700 font-medium">Error Details:</p>
                  <p className="text-sm text-red-700">{message.data.error}</p>
                </div>
              )}
              {/* Show content (which contains the error message from analysis pipeline) */}
              {message.content && (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                  <p className="text-sm text-gray-700">{message.content}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Handle clarification messages (legacy type-based)
  if (message.type === 'clarification') {
    if (message.data) {
      return (
        <div className="flex gap-3 w-full">
          <div className="w-8 h-8 rounded-full bg-yellow-100 flex items-center justify-center flex-shrink-0">
            <span className="text-yellow-600 text-sm">?</span>
          </div>
          <div className="flex-1 max-w-4xl">
            <ClarificationPrompt
              originalQuery={message.data.original_query}
              expandedQuery={message.data.expanded_query}
              message={message.data.message || message.content}
              suggestion={message.data.suggestion}
              confidence={message.data.confidence}
              isLoading={pendingClarificationId === message.id}
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
          </div>
        </div>
      );
    } else {
      return (
        <div className="flex gap-3 w-full">
          <div className="w-8 h-8 rounded-full bg-yellow-100 flex items-center justify-center flex-shrink-0">
            <span className="text-yellow-600 text-sm">?</span>
          </div>
          <div className="flex-1 max-w-4xl">
            <ClarificationSummary
              originalQuery=""
              expandedQuery={undefined}
              status="pending"
            />
          </div>
        </div>
      );
    }
  }

  // Handle assistant messages based on status and response_type

  // Show progress for pending/running states
  if (message.status === 'pending' || message.status === 'running') {
    // Combine historical logs from message with live progress logs
    const historicalLogs = (message as any).logs || [];
    const combinedLogs = [...historicalLogs, ...progressLogs];

    return (
      <div className="flex gap-3 w-full">
        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
          <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
        <div className="flex-1 max-w-4xl">
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <div className="p-4">
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  {message.status === 'pending' ? 'Analysis in Progress' : 'Executing Analysis'}
                </h3>
                <p className="text-sm text-gray-600">{message.content}</p>
              </div>
              <StepProgressDisplay
                logs={combinedLogs}
                isProcessing={true}
              />
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Handle completed states based on response_type
  if (message.status === 'completed') {
    // Check if message has UI configuration data first (regardless of response_type)
    if (hasUIConfig(message)) {
      const uiConfig = getUIConfig(message);
      return (
        <div className="flex gap-3 w-full">
          <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
            <span className="text-green-600 text-sm">🎨</span>
          </div>
          <div className="flex-1 max-w-4xl">
            <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-1 mb-4">
              <div className="bg-white rounded-lg p-3 shadow-sm">
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-sm font-medium text-green-700">Dynamic Analysis Dashboard</span>
                  <span className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded-full">
                    Interactive
                  </span>
                </div>
                <UIConfigurationRenderer uiConfig={uiConfig} />
              </div>
            </div>
          </div>
        </div>
      );
    } else if (message.response_type === 'script_generation') {
      // Fallback to existing AnalysisResult for script_generation without UI config
      return (
        <div className="flex gap-3 w-full">
          <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
            <span className="text-green-600 text-sm">✓</span>
          </div>
          <div className="flex-1 max-w-4xl">
            <AnalysisResult
              message={message}
            />
          </div>
        </div>
      );
    } else if (message.response_type === 'meaningless') {
      // Show simple AI message for meaningless queries
      return (
        <div className="flex gap-3 w-full">
          <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
            <span className="text-blue-600 text-sm">💭</span>
          </div>
          <div className="flex-1 max-w-4xl">
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
              <div
                className="text-sm text-gray-700 prose prose-sm max-w-none"
                dangerouslySetInnerHTML={{
                  __html: renderMarkdown(message.content || "I understand your question, but it doesn't seem to require financial analysis. Feel free to ask about portfolio analysis, trading strategies, risk assessment, or investment research.")
                }}
              />
            </div>
          </div>
        </div>
      );
    } else if (message.response_type === 'needs_clarification') {
      // Show clarification prompt for clarification needed
      return (
        <div className="flex gap-3 w-full">
          <div className="w-8 h-8 rounded-full bg-yellow-100 flex items-center justify-center flex-shrink-0">
            <span className="text-yellow-600 text-sm">❓</span>
          </div>
          <div className="flex-1 max-w-4xl">
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-yellow-800 font-medium mb-2">I need more information</p>
              <div
                className="text-yellow-700 prose prose-sm max-w-none"
                dangerouslySetInnerHTML={{
                  __html: renderMarkdown(message.content || "Could you provide more details about what you're looking for? This will help me give you a more accurate analysis.")
                }}
              />
              <p className="text-yellow-600 text-sm mt-2">
                Please ask a follow-up question with more specific details.
              </p>
            </div>
          </div>
        </div>
      );
    }
  }

  // Default: simple AI message
  return (
    <div className="flex gap-3 w-full">
      <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
        <span className="text-blue-600 text-sm">AI</span>
      </div>
      <div className="flex-1 max-w-4xl">
        <div className="bg-white border border-gray-200 rounded-lg p-3">
          <div
            className="text-sm text-gray-700 prose prose-sm max-w-none"
            dangerouslySetInnerHTML={{
              __html: renderMarkdown(message.content)
            }}
          />
        </div>
      </div>
    </div>
  );
}