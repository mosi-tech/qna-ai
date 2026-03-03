/**
 * Authentication Context for Appwrite
 * Manages user authentication state across the application
 */

'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { account, AppwriteUser, AuthSession, UserRole, USER_ROLES } from '../appwrite';
import { AppwriteException, Models } from 'appwrite';

/**
 * Fetch and store CSRF token after successful authentication
 */
async function initializeCSRFToken(): Promise<void> {
    try {
        const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8010';

        if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
            console.log('[AuthContext] Fetching CSRF token from:', backendUrl + '/csrf-token');
        }

        const response = await fetch(`${backendUrl}/csrf-token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include', // Send cookies with request
        });

        if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
            console.log('[AuthContext] CSRF token response status:', response.status);
        }

        if (response.ok) {
            const data = await response.json();

            if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
                console.log('[AuthContext] CSRF token response data:', {
                    success: data.success,
                    hasData: !!data.data,
                    hasCsrfToken: !!(data.csrf_token || (data.data && data.data.csrf_token))
                });
            }

            // Backend returns either { csrf_token: "...", expires_at: "..." } or { success: true, data: { csrf_token: "...", ... } }
            const token = data.csrf_token || (data.data && data.data.csrf_token);
            if (token) {
                if (typeof window !== 'undefined') {
                    localStorage.setItem('csrf_token', token);
                    if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
                        console.log('[AuthContext] ✅ CSRF token fetched and stored in localStorage');
                        console.log('[AuthContext] Token length:', token.length);
                        console.log('[AuthContext] Token preview:', token.substring(0, 10) + '...');
                    }
                }
            } else {
                console.warn('[AuthContext] ⚠️ Response OK but no CSRF token found in response:', data);
            }
        } else {
            console.warn('[AuthContext] ⚠️ Failed to fetch CSRF token:', response.status, await response.text());
        }
    } catch (error) {
        console.warn('[AuthContext] ⚠️ Failed to initialize CSRF token:', error);
        // Continue even if CSRF token fetch fails - app might not need it
    }
}

interface AuthContextType {
    user: AppwriteUser | null;
    session: AuthSession | null;
    loading: boolean;
    login: (email: string, password: string) => Promise<void>;
    register: (email: string, password: string, name: string) => Promise<void>;
    logout: () => Promise<void>;
    checkAuth: () => Promise<void>;
    hasRole: (role: UserRole) => boolean;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<AppwriteUser | null>(null);
    const [session, setSession] = useState<AuthSession | null>(null);
    const [loading, setLoading] = useState(true);

    const checkAuth = async () => {
        try {
            setLoading(true);

            console.log('[AuthContext] Checking authentication...');
            console.log('[AuthContext] Available cookies:', document.cookie);

            // Check if user is authenticated
            const currentUser = await account.get();
            console.log('[AuthContext] User data received:', currentUser);
            setUser(currentUser as AppwriteUser);

            // Get current session
            const currentSession = await account.getSession('current');
            console.log('[AuthContext] Session data received:', currentSession);
            setSession(currentSession as AuthSession);

            console.log('✅ User authenticated:', currentUser.email);

            // Fetch and initialize CSRF token after successful authentication
            await initializeCSRFToken();
        } catch (error) {
            console.log('❌ Authentication check failed:', error);
            setUser(null);
            setSession(null);
        } finally {
            setLoading(false);
        }
    };

    const login = async (email: string, password: string) => {
        try {
            setLoading(true);

            // 1️⃣ Check if user is already signed in before creating session
            try {
                const existingSession = await account.getSession('current');
                if (existingSession) {
                    console.log('✅ User already signed in:', existingSession.$id);
                    // Update state with existing session
                    setSession(existingSession as AuthSession);
                    const user = await account.get();
                    setUser(user as AppwriteUser);

                    // Fetch and initialize CSRF token for already-signed-in user
                    await initializeCSRFToken();
                    return;
                }
            } catch {
                // No active session, safe to create a new one
                console.log('No existing session found, proceeding with login');
            }

            // 2️⃣ Create new session only if none exists
            const session = await account.createEmailPasswordSession(email, password);
            setSession(session as AuthSession);

            // Get user info
            const user = await account.get();
            setUser(user as AppwriteUser);

            console.log('✅ Login successful:', user.email);

            // Fetch and initialize CSRF token after successful login
            await initializeCSRFToken();
        } catch (error) {
            console.error('❌ Login failed:', error);
            throw error;
        } finally {
            setLoading(false);
        }
    };

    const register = async (email: string, password: string, name: string) => {
        try {
            setLoading(true);

            // Create account
            const user = await account.create('unique()', email, password, name);
            console.log('✅ Account created:', user.email);

            // Automatically log in after registration (which also fetches CSRF token)
            await login(email, password);

            // Send email verification after successful registration and login
            try {
                console.log('📧 Sending email verification...');
                await account.createVerification(`${window.location.origin}/auth/verify-email`);
                console.log('✅ Email verification sent');
            } catch (verifyError: unknown) {
                console.warn('⚠️ Email verification failed:', verifyError);
                // Don't throw - user is still registered and logged in
            }
        } catch (error) {
            console.error('❌ Registration failed:', error);
            throw error;
        } finally {
            setLoading(false);
        }
    };

    const logout = async () => {
        try {
            setLoading(true);

            console.log('[AuthContext] Starting logout...');

            // Try to delete current session from Appwrite
            try {
                await account.deleteSession('current');
                console.log('[AuthContext] Session deleted from Appwrite');
            } catch (sessionError) {
                // Session might already be expired/invalid - continue with local cleanup
                console.warn('[AuthContext] Session deletion failed (might be expired):', sessionError);
            }

            // Always clear local state regardless of server response
            setUser(null);
            setSession(null);

            // Clear any cached auth data
            try {
                localStorage.removeItem('auth_token');
            } catch {
                // Ignore localStorage errors
            }

            console.log('✅ Logout completed - local state cleared');
        } catch (error) {
            console.error('❌ Logout process failed:', error);

            // Even if there's an error, clear local state
            setUser(null);
            setSession(null);

            throw error;
        } finally {
            setLoading(false);
        }
    };

    const hasRole = (role: UserRole): boolean => {
        if (!user?.prefs?.roles) return false;
        return user.prefs.roles.includes(role);
    };

    const isAuthenticated = !!user && !!session;

    // Debug authentication state
    if (process.env.NEXT_PUBLIC_DEBUG === 'true') {
        console.log('[AuthContext] Auth state:', {
            user: !!user,
            session: !!session,
            isAuthenticated,
            loading
        });
    }

    // Check authentication on mount
    useEffect(() => {
        checkAuth();
    }, []);

    const value: AuthContextType = {
        user,
        session,
        loading,
        login,
        register,
        logout,
        checkAuth,
        hasRole,
        isAuthenticated
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}

// Custom hook to use auth context
export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}

// HOC to protect routes
export function withAuth<T extends Record<string, any>>(
    Component: React.ComponentType<T>,
    requiredRole?: UserRole
) {
    return function AuthenticatedComponent(props: T) {
        const { user, loading, hasRole, isAuthenticated } = useAuth();
        const router = useRouter();

        useEffect(() => {
            if (!loading && !isAuthenticated) {
                // Store current path for redirect after login
                const currentPath = window.location.pathname;
                if (currentPath !== '/auth/login' && !currentPath.startsWith('/auth/')) {
                    try {
                        localStorage.setItem('redirect_after_login', currentPath);
                    } catch {
                        // Ignore localStorage errors
                    }
                }
                // Redirect to login
                router.push('/auth/login');
            }
        }, [loading, isAuthenticated, router]);

        if (loading) {
            return (
                <div className="flex items-center justify-center min-h-screen">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    <span className="ml-2">Loading...</span>
                </div>
            );
        }

        if (!isAuthenticated) {
            return (
                <div className="flex items-center justify-center min-h-screen">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    <span className="ml-2">Redirecting to login...</span>
                </div>
            );
        }

        if (requiredRole && !hasRole(requiredRole)) {
            return (
                <div className="flex items-center justify-center min-h-screen">
                    <div className="text-center">
                        <h2 className="text-xl font-semibold mb-2">Access Denied</h2>
                        <p className="text-gray-600 mb-4">
                            You don't have the required permissions to access this page.
                        </p>
                        <p className="text-sm text-gray-500">Required role: {requiredRole}</p>
                    </div>
                </div>
            );
        }

        return <Component {...props} />;
    };
}

export default AuthContext;