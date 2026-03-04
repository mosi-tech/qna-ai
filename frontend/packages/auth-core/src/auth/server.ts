/**
 * Auth provider factory.
 *
 * All auth-core pages and handlers import from here — never from provider
 * files directly. To switch auth backends set the AUTH_PROVIDER env var:
 *
 *   AUTH_PROVIDER=supabase   (default)
 *   AUTH_PROVIDER=appwrite
 *
 * The selected provider is cached per process so no extra overhead per request.
 */
import type { AuthServerProvider, AuthUser } from './types';

export type { AuthUser };
export type { AuthServerProvider };

// ─── Provider singleton ───────────────────────────────────────────────────────

let _provider: AuthServerProvider | null = null;

export function getProvider(): AuthServerProvider {
    if (_provider) return _provider;

    const name = (process.env.AUTH_PROVIDER ?? 'supabase').toLowerCase();

    if (name === 'appwrite') {
        // Lazily required so that `node-appwrite` is not bundled when unused.
        // eslint-disable-next-line @typescript-eslint/no-require-imports
        const { AppwriteServerProvider } = require('./appwrite-server') as typeof import('./appwrite-server');
        _provider = new AppwriteServerProvider();
    } else {
        // eslint-disable-next-line @typescript-eslint/no-require-imports
        const { SupabaseServerProvider } = require('./supabase-server') as typeof import('./supabase-server');
        _provider = new SupabaseServerProvider();
    }

    return _provider;
}

// ─── Convenience helpers (most pages only need these) ────────────────────────

/**
 * Return the currently authenticated user, or null if not logged in.
 *
 * Usage in RSC:
 * ```ts
 * import { getAuthUser } from '../auth/server';
 * const user = await getAuthUser();
 * if (!user) redirect('/login');
 * ```
 */
export async function getAuthUser(): Promise<AuthUser | null> {
    return getProvider().getUser();
}

/** Sign out the current session. */
export async function signOut(): Promise<void> {
    return getProvider().signOut();
}

/** Sign in with email + password. */
export async function signIn(
    email: string,
    password: string,
): Promise<{ error: string | null }> {
    return getProvider().signIn(email, password);
}

/** Create a new user account. */
export async function signUp(
    email: string,
    password: string,
): Promise<{ error: string | null }> {
    return getProvider().signUp(email, password);
}

/** Send a password-reset email. */
export async function resetPassword(
    email: string,
): Promise<{ error: string | null }> {
    return getProvider().resetPassword(email);
}

/** Exchange an OAuth/email-confirm code for a session. */
export async function exchangeCodeForSession(
    code: string,
): Promise<{ error: string | null }> {
    return getProvider().exchangeCodeForSession(code);
}

/** Update the current user's email, password, and/or display name. */
export async function updateUser(data: {
    email?: string;
    password?: string;
    displayName?: string;
}): Promise<{ error: string | null }> {
    return getProvider().updateUser(data);
}

/** Admin: permanently delete a user by ID. */
export async function deleteUser(
    userId: string,
): Promise<{ error: string | null }> {
    return getProvider().deleteUser(userId);
}

// ─── Reset (for tests / HMR) ──────────────────────────────────────────────────
export function _resetProvider() {
    _provider = null;
}
