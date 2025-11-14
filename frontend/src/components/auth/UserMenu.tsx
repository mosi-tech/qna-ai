/**
 * User Menu Component
 * Shows user info and logout option
 */

'use client';

import React, { useState } from 'react';
import { useAuth } from '@/lib/context/AuthContext';
import { useRouter } from 'next/navigation';

export default function UserMenu() {
    const [isOpen, setIsOpen] = useState(false);
    const { user, logout, isAuthenticated } = useAuth();
    const router = useRouter();

    if (!isAuthenticated || !user) {
        return (
            <div className="flex space-x-2">
                <button
                    onClick={() => router.push('/auth/login')}
                    className="px-3 py-2 text-sm text-blue-600 hover:text-blue-800"
                >
                    Sign in
                </button>
                <button
                    onClick={() => router.push('/auth/signup')}
                    className="px-3 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                    Sign up
                </button>
            </div>
        );
    }

    const handleLogout = async () => {
        try {
            console.log('🔓 Starting logout process...');
            await logout();
            console.log('✅ Logout successful, redirecting to login');
            
            // Clear any application state/caches if needed
            localStorage.removeItem('redirect_after_login');
            
            // Redirect to login page
            router.push('/auth/login');
        } catch (error) {
            console.error('❌ Logout error:', error);
            // Even if logout fails, clear local state and redirect
            router.push('/auth/login');
        }
    };

    return (
        <div className="relative">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center space-x-2 text-sm bg-white p-2 rounded-full shadow-lg border focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-medium">
                    {user.name?.charAt(0).toUpperCase() || user.email?.charAt(0).toUpperCase()}
                </div>
                <span className="hidden md:block text-gray-700">{user.name || user.email}</span>
                <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
            </button>

            {isOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border z-50">
                    <div className="py-1">
                        <div className="px-4 py-2 text-sm text-gray-700 border-b">
                            <div className="font-medium">{user.name}</div>
                            <div className="text-gray-500">{user.email}</div>
                        </div>
                        
                        <button
                            onClick={() => {
                                setIsOpen(false);
                                router.push('/profile');
                            }}
                            className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                            Profile
                        </button>
                        
                        <button
                            onClick={() => {
                                setIsOpen(false);
                                router.push('/settings');
                            }}
                            className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                            Settings
                        </button>
                        
                        <hr className="my-1" />
                        
                        <button
                            onClick={() => {
                                setIsOpen(false);
                                handleLogout();
                            }}
                            className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                        >
                            Sign out
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}