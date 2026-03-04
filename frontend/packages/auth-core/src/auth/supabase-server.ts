/**
 * Supabase implementation of AuthServerProvider.
 *
 * Requires env vars:
 *   NEXT_PUBLIC_SUPABASE_URL
 *   NEXT_PUBLIC_SUPABASE_ANON_KEY
 *   SUPABASE_SERVICE_ROLE_KEY   (for deleteUser only)
 */
import { createServerClient as createSupabaseServerClient } from '@supabase/ssr';
import { createClient } from '@supabase/supabase-js';
import type { CookieOptions } from '@supabase/ssr';
import type { AuthServerProvider, AuthUser } from './types';

// ─── Helpers ──────────────────────────────────────────────────────────────────

async function getSupabaseServerClient() {
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
                            // eslint-disable-next-line @typescript-eslint/no-explicit-any
                            cookieStore.set(name, value, options as any),
                        );
                    } catch {
                        // read-only in RSC — middleware refreshes the session
                    }
                },
            },
        },
    );
}

function mapUser(u: { id: string; email?: string | null; user_metadata?: Record<string, unknown> }): AuthUser {
    return {
        id: u.id,
        email: u.email ?? '',
        displayName: (u.user_metadata?.display_name as string) ?? null,
        role: (u.user_metadata?.role as string) ?? null,
    };
}

// ─── Provider ─────────────────────────────────────────────────────────────────

export class SupabaseServerProvider implements AuthServerProvider {
    async getUser(): Promise<AuthUser | null> {
        const supabase = await getSupabaseServerClient();
        const { data: { user }, error } = await supabase.auth.getUser();
        if (error || !user) return null;
        return mapUser(user);
    }

    async signOut(): Promise<void> {
        const supabase = await getSupabaseServerClient();
        await supabase.auth.signOut();
    }

    async signIn(email: string, password: string): Promise<{ error: string | null }> {
        const supabase = await getSupabaseServerClient();
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        return { error: error?.message ?? null };
    }

    async signUp(email: string, password: string): Promise<{ error: string | null }> {
        const supabase = await getSupabaseServerClient();
        const { error } = await supabase.auth.signUp({ email, password });
        return { error: error?.message ?? null };
    }

    async resetPassword(email: string): Promise<{ error: string | null }> {
        const supabase = await getSupabaseServerClient();
        const appUrl = process.env.NEXT_PUBLIC_APP_URL ?? 'http://localhost:3000';
        const { error } = await supabase.auth.resetPasswordForEmail(email, {
            redirectTo: `${appUrl}/auth/callback?next=/account`,
        });
        return { error: error?.message ?? null };
    }

    async exchangeCodeForSession(code: string): Promise<{ error: string | null }> {
        const supabase = await getSupabaseServerClient();
        const { error } = await supabase.auth.exchangeCodeForSession(code);
        return { error: error?.message ?? null };
    }

    async updateUser(data: {
        email?: string;
        password?: string;
        displayName?: string;
    }): Promise<{ error: string | null }> {
        const supabase = await getSupabaseServerClient();
        const update: { email?: string; password?: string; data?: Record<string, unknown> } = {};
        if (data.email) update.email = data.email;
        if (data.password) update.password = data.password;
        if (data.displayName !== undefined) update.data = { display_name: data.displayName };
        const { error } = await supabase.auth.updateUser(update);
        return { error: error?.message ?? null };
    }

    async deleteUser(userId: string): Promise<{ error: string | null }> {
        const serviceClient = createClient(
            process.env.NEXT_PUBLIC_SUPABASE_URL!,
            process.env.SUPABASE_SERVICE_ROLE_KEY!,
        );
        const { error } = await serviceClient.auth.admin.deleteUser(userId);
        return { error: error?.message ?? null };
    }
}
