/**
 * Email Verification Form Component
 * Handles email verification using Appwrite
 */

'use client';

import React, { useState, useEffect } from 'react';
import { account } from '@/lib/appwrite';
import { useAuth } from '@/lib/context/AuthContext';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';

export default function EmailVerificationForm() {
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [isSuccess, setIsSuccess] = useState(false);
    const [resendLoading, setResendLoading] = useState(false);
    const [resendMessage, setResendMessage] = useState('');
    
    const { user, checkAuth } = useAuth();
    const router = useRouter();
    const searchParams = useSearchParams();
    const userId = searchParams.get('userId');
    const secret = searchParams.get('secret');

    useEffect(() => {
        // Auto-verify if we have URL parameters
        if (userId && secret) {
            handleVerification(userId, secret);
        } else if (user) {
            // Check if user is already verified
            setIsLoading(false);
            if (user.emailVerification) {
                setIsSuccess(true);
            }
        } else {
            setIsLoading(false);
        }
    }, [userId, secret, user]);

    const handleVerification = async (userIdParam: string, secretParam: string) => {
        try {
            setIsLoading(true);
            setError('');
            
            // Complete email verification
            await account.updateVerification(userIdParam, secretParam);
            
            // Refresh user data
            await checkAuth();
            
            setIsSuccess(true);
        } catch (error: any) {
            console.error('Email verification error:', error);
            
            if (error.code === 401) {
                setError('Invalid or expired verification link. Please request a new one.');
            } else {
                setError(error.message || 'Failed to verify email. Please try again.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    const handleResendVerification = async () => {
        if (!user) {
            setError('Please log in to resend verification email');
            return;
        }

        try {
            setResendLoading(true);
            setError('');
            setResendMessage('');
            
            // Create new verification email
            await account.createVerification(`${window.location.origin}/auth/verify-email`);
            
            setResendMessage('Verification email sent! Check your inbox.');
        } catch (error: any) {
            console.error('Resend verification error:', error);
            
            if (error.code === 429) {
                setError('Too many requests. Please wait before requesting another email.');
            } else {
                setError(error.message || 'Failed to send verification email. Please try again.');
            }
        } finally {
            setResendLoading(false);
        }
    };

    // Loading state
    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
                <div className="max-w-md w-full space-y-8 text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="text-gray-600">Verifying your email...</p>
                </div>
            </div>
        );
    }

    // Success state
    if (isSuccess) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
                <div className="max-w-md w-full space-y-8">
                    <div className="text-center">
                        <div className="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center mb-4">
                            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                        </div>
                        <h2 className="text-2xl font-bold text-gray-900 mb-2">
                            Email verified successfully!
                        </h2>
                        <p className="text-gray-600 mb-6">
                            Your email address has been verified. You can now access all features of the platform.
                        </p>
                        <Link 
                            href="/dashboard"
                            className="inline-flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                        >
                            Go to Dashboard
                        </Link>
                    </div>
                </div>
            </div>
        );
    }

    // Default verification needed state
    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8">
                <div className="text-center">
                    <div className="w-16 h-16 mx-auto bg-yellow-100 rounded-full flex items-center justify-center mb-4">
                        <svg className="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">
                        Verify your email address
                    </h2>
                    <p className="text-gray-600 mb-6">
                        {user ? (
                            <>We've sent a verification email to <strong>{user.email}</strong>. Click the link in the email to verify your account.</>
                        ) : (
                            'Please check your email and click the verification link.'
                        )}
                    </p>

                    {error && (
                        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative mb-4">
                            <span className="block sm:inline">{error}</span>
                        </div>
                    )}

                    {resendMessage && (
                        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded relative mb-4">
                            <span className="block sm:inline">{resendMessage}</span>
                        </div>
                    )}

                    <div className="space-y-4">
                        {user && (
                            <button
                                onClick={handleResendVerification}
                                disabled={resendLoading}
                                className="w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {resendLoading ? (
                                    <>
                                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Sending...
                                    </>
                                ) : (
                                    'Resend verification email'
                                )}
                            </button>
                        )}

                        <div className="text-sm text-gray-500 space-y-2">
                            <p>Didn't receive the email? Check your spam folder.</p>
                            <p>
                                Wrong email address?{' '}
                                <Link href="/auth/login" className="font-medium text-blue-600 hover:text-blue-500">
                                    Sign in with a different account
                                </Link>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}