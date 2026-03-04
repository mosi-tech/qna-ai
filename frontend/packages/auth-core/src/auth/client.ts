'use client';
/**
 * Provider-agnostic browser-side auth helpers.
 *
 * For Supabase: uses createBrowserClient() directly (sets session cookie client-side).
 * For Appwrite: POSTs to /api/auth/* routes (server sets the aw-session cookie).
 *
 * Select provider via NEXT_PUBLIC_AUTH_PROVIDER env var ('supabase' | 'appwrite').
 * Defaults to 'supabase'.
 */

import { createBrowserClient } from '../supabase';

type AuthResult = { error: string | null };

function isAppwrite(): boolean {
    return (process.env.NEXT_PUBLIC_AUTH_PROVIDER ?? 'supabase') === 'appwrite';
}

async function postJson(path: string, body: Record<string, string>): Promise<AuthResult> {
    const res = await fetch(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });
    const data = (await res.json()) as { error?: string };
    return { error: data.error ?? null };
}

export async function clientSignIn(email: string, password: string): Promise<AuthResult> {
    if (isAppwrite()) return postJson('/api/auth/signin', { email, password });
    const { error } = await createBrowserClient().auth.signInWithPassword({ email, password });
    return { error: error?.message ?? null };
}

export async function clientSignUp(
    email: string,
    password: string,
    options?: { displayName?: string; redirectTo?: string },
): Promise<AuthResult> {
    if (isAppwrite())
        return postJson('/api/auth/signup', {
            email,
            password,
            ...(options?.displayName ? { displayName: options.displayName } : {}),
            ...(options?.redirectTo ? { redirectTo: options.redirectTo } : {}),
        });
    const { error } = await createBrowserClient().auth.signUp({
        email,
        password,
        options: {
            ...(options?.displayName ? { data: { display_name: options.displayName } } : {}),
            ...(options?.redirectTo ? { emailRedirectTo: options.redirectTo } : {}),
        },
    });
    return { error: error?.message ?? null };
}

export async function clientResetPassword(
    email: string,
    redirectTo: string,
): Promise<AuthResult> {
    if (isAppwrite()) return postJson('/api/auth/reset-password', { email, redirectTo });
    const { error } = await createBrowserClient().auth.resetPasswordForEmail(email, {
        redirectTo,
    });
    return { error: error?.message ?? null };
}

export async function clientSignOut(): Promise<void> {
    await fetch('/api/auth/signout', { method: 'POST' });
}
