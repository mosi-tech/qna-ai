// ─── Server-side Supabase clients ─────────────────────────────────────────────
// Use these in Server Components, Route Handlers, and Server Actions.

import { createServerClient as createSupabaseServerClient } from '@supabase/ssr';
import { createBrowserClient as createSupabaseBrowserClient } from '@supabase/ssr';
import type { CookieOptions } from '@supabase/ssr';
import { createClient } from '@supabase/supabase-js';
import type { NextRequest } from 'next/server';
import type { User } from '@supabase/supabase-js';

/**
 * Creates a Supabase client for use in Server Components and Route Handlers.
 * Must be called inside a request context (RSC, Route Handler, Server Action).
 */
export async function createServerClient() {
    const { cookies } = await import('next/headers');
    const cookieStore = await cookies();

    return createSupabaseServerClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        {
            cookies: {
                getAll() {
                    return cookieStore.getAll();
                },
                setAll(cookiesToSet: { name: string; value: string; options: CookieOptions }[]) {
                    try {
                        cookiesToSet.forEach(({ name, value, options }) =>
                            // CookieOptions (supabase/ssr) and ResponseCookie (next/headers) are structurally
                            // compatible at runtime; the cast bridges the TypeScript type gap.
                            // eslint-disable-next-line @typescript-eslint/no-explicit-any
                            cookieStore.set(name, value, options as any),
                        );
                    } catch {
                        // setAll called from a Server Component — cookies are read-only,
                        // but the middleware handles refreshing sessions.
                    }
                },
            },
        },
    );
}

/**
 * Creates a Supabase client with the service role key for admin operations.
 * ONLY use server-side, never expose to the client.
 */
export async function createServiceClient() {
    const { cookies } = await import('next/headers');
    const cookieStore = await cookies();

    return createSupabaseServerClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.SUPABASE_SERVICE_ROLE_KEY!,
        {
            cookies: {
                getAll() {
                    return cookieStore.getAll();
                },
                setAll(cookiesToSet: { name: string; value: string; options: CookieOptions }[]) {
                    try {
                        cookiesToSet.forEach(({ name, value, options }) =>
                            // eslint-disable-next-line @typescript-eslint/no-explicit-any
                            cookieStore.set(name, value, options as any),
                        );
                    } catch {
                        // read-only in RSC
                    }
                },
            },
        },
    );
}

/**
 * Resolves the authenticated user from either:
 *  1. An `Authorization: Bearer <jwt>` request header (smoke tests / SDK calls)
 *  2. The Supabase session cookie (browser sessions)
 *
 * Returns `{ user, error }` — user is null when unauthenticated.
 */
export async function requireUser(
    req: NextRequest,
): Promise<{ user: User | null; error: string | null }> {
    const authHeader = req.headers.get('authorization');
    const bearerToken = authHeader?.startsWith('Bearer ')
        ? authHeader.slice(7)
        : null;

    if (bearerToken) {
        // Validate the JWT against Supabase without relying on cookies
        const anonClient = createClient(
            process.env.NEXT_PUBLIC_SUPABASE_URL!,
            process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        );
        const { data, error } = await anonClient.auth.getUser(bearerToken);
        if (!error && data.user) {
            return { user: data.user, error: null };
        }

        // Development fallback: decode payload without signature verification
        // and look up the user by ID via the service role.
        // Disabled in production.
        if (process.env.NODE_ENV !== 'production') {
            try {
                const payloadB64 = bearerToken.split('.')[1];
                const payload = JSON.parse(
                    Buffer.from(payloadB64, 'base64url').toString('utf8'),
                ) as { sub?: string; exp?: number };
                if (payload.sub && payload.exp && payload.exp > Date.now() / 1000) {
                    const serviceClient = createClient(
                        process.env.NEXT_PUBLIC_SUPABASE_URL!,
                        process.env.SUPABASE_SERVICE_ROLE_KEY!,
                    );
                    const { data: adminData } =
                        await serviceClient.auth.admin.getUserById(payload.sub);
                    if (adminData.user) {
                        return { user: adminData.user, error: null };
                    }
                }
            } catch {
                // ignore — fall through to Unauthorized
            }
        }

        return { user: null, error: error?.message ?? 'Invalid token' };
    }

    // Fall back to cookie-based session
    const supabase = await createServerClient();
    const { data, error } = await supabase.auth.getUser();
    if (error || !data.user) {
        return { user: null, error: error?.message ?? 'Unauthorized' };
    }
    return { user: data.user, error: null };
}

// ─── Browser-side Supabase client ─────────────────────────────────────────────
// Use this in Client Components (`"use client"` files only).

/**
 * Creates a Supabase browser client for use in Client Components.
 * Safe to call multiple times — @supabase/ssr deduplicates internally.
 */
export function createBrowserClient() {
    return createSupabaseBrowserClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    );
}
