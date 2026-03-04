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
  /** Register the single handler that fires when any message_ready knock arrives. */
  setMessageReadyHandler: (
    fn: ((messageId: string, status: string, responseType: string | null) => void) | null
  ) => void;
}

const ProgressContext = createContext<ProgressContextType | null>(null);

interface ProgressProviderProps {
  children: ReactNode;
  sessionId: string | null;
}

export function ProgressProvider({ children, sessionId }: ProgressProviderProps) {
  const messageReadyHandlerRef = useRef<
    ((messageId: string, status: string, responseType: string | null) => void) | null
  >(null);

  const onMessageReady = useCallback(
    (messageId: string, status: string, responseType: string | null) => {
      if (messageReadyHandlerRef.current) {
        messageReadyHandlerRef.current(messageId, status, responseType);
      } else {
        console.warn('[ProgressProvider] message_ready knock received but no handler registered:', messageId);
      }
    },
    [],
  );

  const setMessageReadyHandler = useCallback(
    (fn: ((messageId: string, status: string, responseType: string | null) => void) | null) => {
      messageReadyHandlerRef.current = fn;
    },
    [],
  );

  const progressState = useProgressStream(sessionId, onMessageReady);

  const contextValue: ProgressContextType = {
    ...progressState,
    setMessageReadyHandler,
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

export function useProgressSafe() {
  const context = useContext(ProgressContext);
  return context || {
    logs: [],
    isConnected: false,
    error: null,
    clearLogs: () => { },
    addLog: () => undefined,
    setMessageReadyHandler: () => { },
  };
}
