'use client';

import { ReactNode } from 'react';
import { SessionProvider } from './SessionContext';
import { ConversationProvider } from './ConversationContext';
import { UIProvider } from './UIContext';
import { AuthProvider } from './AuthContext';

export function Providers({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <SessionProvider>
        <ConversationProvider>
          <UIProvider>
            {children}
          </UIProvider>
        </ConversationProvider>
      </SessionProvider>
    </AuthProvider>
  );
}
