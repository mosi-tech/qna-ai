/**
 * Simple Logout Button Component
 * Can be used standalone or within other components
 */

'use client';

import React, { useState } from 'react';
import { useAuth } from '@/lib/context/AuthContext';
import { useRouter } from 'next/navigation';

interface LogoutButtonProps {
  className?: string;
  children?: React.ReactNode;
  variant?: 'button' | 'link' | 'icon';
  redirectTo?: string;
}

export default function LogoutButton({ 
  className = '', 
  children,
  variant = 'button',
  redirectTo = '/auth/login'
}: LogoutButtonProps) {
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const { logout, isAuthenticated } = useAuth();
  const router = useRouter();

  if (!isAuthenticated) {
    return null; // Don't show logout button if not authenticated
  }

  const handleLogout = async () => {
    try {
      setIsLoggingOut(true);
      await logout();
      router.push(redirectTo);
    } catch (error) {
      console.error('Logout failed:', error);
      // Still redirect even if logout fails
      router.push(redirectTo);
    } finally {
      setIsLoggingOut(false);
    }
  };

  const getClassName = () => {
    const base = className;
    
    switch (variant) {
      case 'link':
        return `${base} text-blue-600 hover:text-blue-800 underline`;
      case 'icon':
        return `${base} p-2 text-gray-500 hover:text-gray-700`;
      case 'button':
      default:
        return `${base} px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50`;
    }
  };

  const getContent = () => {
    if (children) return children;
    
    if (isLoggingOut) {
      return variant === 'icon' ? '⏳' : 'Signing out...';
    }
    
    switch (variant) {
      case 'icon':
        return '🔓';
      case 'link':
        return 'Sign out';
      case 'button':
      default:
        return 'Sign out';
    }
  };

  return (
    <button
      onClick={handleLogout}
      disabled={isLoggingOut}
      className={getClassName()}
      title="Sign out"
    >
      {getContent()}
    </button>
  );
}