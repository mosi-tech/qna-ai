'use client';

import React, { createContext, useContext, ReactNode, useRef, useCallback } from 'react';
import { useProgressStream } from '@/lib/hooks/useProgressStream';
import { ProgressLog } from '@/lib/progress/ProgressManager';

interface ProgressContextType {
  logs: ProgressLog[];
  isConnected: boolean;
  error: string | null;
  clearLogs: () => void;
  addLog: (log: ProgressLog) => ProgressLog | undefined;
  registerAnalysisCompleteCallback: (messageId: string, callback: (status: 'completed' | 'failed', data?: any) => void) => () => void;
}

const ProgressContext = createContext<ProgressContextType | null>(null);

interface ProgressProviderProps {
  children: ReactNode;
  sessionId: string | null;
}

export function ProgressProvider({ children, sessionId }: ProgressProviderProps) {
  const callbacksRef = useRef<Map<string, (status: 'completed' | 'failed', data?: any) => void>>(new Map());

  const handleAnalysisComplete = useCallback((status: 'completed' | 'failed', data?: any) => {
    console.group('%c[ANALYSIS COMPLETION DETECTED]', 'color: red; font-weight: bold; font-size: 16px; background: yellow;');
    console.log('%cCompletion Status:', 'font-weight: bold;', status);
    console.log('%cCompletion Data:', 'font-weight: bold;', data);
    // Extract message_id from correct SSE event structure  
    const messageId = data?.details?.message_id;
    
    console.log('%cMessage ID from SSE (data.message_id):', 'font-weight: bold;', data?.message_id);
    console.log('%cMessage ID from SSE (data.details.message_id):', 'font-weight: bold;', data?.details?.message_id);
    console.log('%cFinal Message ID:', 'font-weight: bold; color: green;', messageId);
    console.log('%cRegistered Callbacks:', 'font-weight: bold;', Array.from(callbacksRef.current.keys()));
    console.log('%c🔍 ID MATCHING DEBUG:', 'font-weight: bold; color: blue;', {
      sseMessageId: messageId,
      registeredCallbacks: Array.from(callbacksRef.current.keys()),
      exactMatch: callbacksRef.current.has(messageId),
      callbackCount: callbacksRef.current.size
    });
    
    // If we have a specific message_id, only notify that callback
    if (messageId) {
      const callback = callbacksRef.current.get(messageId);
      if (callback) {
        try {
          console.log('%c🎯 CALLBACK FOUND - WILL TRIGGER MESSAGE CREATION/UPDATE!', 'color: green; font-size: 16px; font-weight: bold; background: lightgreen;');
          console.log('%cCalling completion callback for message:', 'font-weight: bold;', messageId);
          callback(status, data);
          console.log('%c✅ Completion callback executed successfully', 'color: green; font-weight: bold;');
        } catch (error) {
          console.error('%c❌ Error in completion callback:', 'color: red; font-weight: bold;', error);
        }
      } else {
        console.warn('%c❌ NO CALLBACK REGISTERED - NO MESSAGE WILL BE CREATED!', 'color: red; font-size: 14px; font-weight: bold; background: pink;');
        console.warn('%cMissing callback for message_id:', 'color: red;', messageId);
        console.warn('%cAvailable callbacks:', 'color: red;', Array.from(callbacksRef.current.keys()));
        
        // Debug: Try partial matching in case there's a mismatch
        const availableIds = Array.from(callbacksRef.current.keys());
        const targetId = messageId;
        const partialMatches = availableIds.filter(id => 
          id.includes(targetId.slice(-8)) || targetId.includes(id.slice(-8))
        );
        if (partialMatches.length > 0) {
          console.warn(`[ProgressProvider] 🔍 Potential partial matches: [${partialMatches.join(', ')}]`);
        }
        
        // FALLBACK: If no exact match and only one callback registered, use it
        if (callbacksRef.current.size === 1) {
          const [onlyCallbackId, onlyCallback] = Array.from(callbacksRef.current.entries())[0];
          console.warn(`[ProgressProvider] 🚨 FALLBACK: Using only available callback: ${onlyCallbackId}`);
          try {
            onlyCallback(status, data);
          } catch (error) {
            console.error('[ProgressProvider] Error in fallback callback:', error);
          }
        }
      }
    } else {
      // Fallback: notify all registered callbacks if no message_id
      console.log('[ProgressProvider] No message_id in completion data, notifying all callbacks');
      callbacksRef.current.forEach((callback, messageId) => {
        try {
          console.log(`[ProgressProvider] Calling completion callback for message: ${messageId} (fallback)`);
          callback(status, data);
        } catch (error) {
          console.error('[ProgressProvider] Error in analysis complete callback:', error);
        }
      });
    }
    
    console.groupEnd();
  }, []);

  const progressState = useProgressStream(sessionId, undefined, handleAnalysisComplete);
  
  const registerAnalysisCompleteCallback = useCallback((messageId: string, callback: (status: 'completed' | 'failed', data?: any) => void) => {
    console.log(`[ProgressProvider] Registering completion callback for message: ${messageId}`);
    callbacksRef.current.set(messageId, callback);
    console.log(`[ProgressProvider] Total registered callbacks: ${callbacksRef.current.size}`);
    
    // Return unregister function
    return () => {
      console.log(`[ProgressProvider] Unregistering completion callback for message: ${messageId}`);
      callbacksRef.current.delete(messageId);
      console.log(`[ProgressProvider] Total registered callbacks: ${callbacksRef.current.size}`);
    };
  }, []);

  const contextValue = {
    ...progressState,
    registerAnalysisCompleteCallback,
  };
  
  return (
    <ProgressContext.Provider value={contextValue}>
      {children}
    </ProgressContext.Provider>
  );
}

export function useProgress() {
  const context = useContext(ProgressContext);
  if (!context) {
    throw new Error('useProgress must be used within a ProgressProvider');
  }
  return context;
}

// Export a hook that returns empty state when no provider exists
export function useProgressSafe() {
  const context = useContext(ProgressContext);
  return context || {
    logs: [],
    isConnected: false,
    error: null,
    clearLogs: () => {},
    addLog: () => {},
    registerAnalysisCompleteCallback: () => () => {}
  };
}