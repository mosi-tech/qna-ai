'use client';

import { createContext, useContext, useState, ReactNode } from 'react';

interface UIState {
  isProcessing: boolean;
  error: string | null;
  notification: string | null;
  viewMode: 'single' | 'split';
}

interface UIContextType extends UIState {
  setIsProcessing: (value: boolean) => void;
  setError: (error: string | null) => void;
  setNotification: (notification: string | null) => void;
  setViewMode: (mode: 'single' | 'split') => void;
  clearError: () => void;
  clearNotification: () => void;
}

const UIContext = createContext<UIContextType | undefined>(undefined);

export function UIProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<UIState>({
    isProcessing: false,
    error: null,
    notification: null,
    viewMode: 'single',
  });

  const setIsProcessing = (value: boolean) => {
    setState(prev => ({ ...prev, isProcessing: value }));
  };

  const setError = (error: string | null) => {
    setState(prev => ({ ...prev, error }));
  };

  const setNotification = (notification: string | null) => {
    setState(prev => ({ ...prev, notification }));
  };

  const setViewMode = (mode: 'single' | 'split') => {
    setState(prev => ({ ...prev, viewMode: mode }));
  };

  const clearError = () => setError(null);
  const clearNotification = () => setNotification(null);

  const value: UIContextType = {
    ...state,
    setIsProcessing,
    setError,
    setNotification,
    setViewMode,
    clearError,
    clearNotification,
  };

  return (
    <UIContext.Provider value={value}>
      {children}
    </UIContext.Provider>
  );
}

export function useUI(): UIContextType {
  const context = useContext(UIContext);
  if (!context) {
    throw new Error('useUI must be used within UIProvider');
  }
  return context;
}
