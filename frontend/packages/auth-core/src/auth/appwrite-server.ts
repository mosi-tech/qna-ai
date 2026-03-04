/**
 * Appwrite implementation of AuthServerProvider.
 *
 * Install the Appwrite Node.js SDK:
 *   pnpm add node-appwrite
 *
 * Required env vars:
 *   APPWRITE_ENDPOINT          e.g. https://cloud.appwrite.io/v1
 *   APPWRITE_PROJECT_ID
 *   APPWRITE_API_KEY           Server-side API key with users.read + users.write
 *
 * How sessions work in Next.js (App Router) with Appwrite:
 * - On login, Appwrite returns a session secret which must be stored as an
 *   HttpOnly cookie (e.g. 'aw-session').
 * - On each request, the middleware reads that cookie and calls
 *   `client.setSession(secret)` so RSCs can call `account.get()`.
 * - This file handles the server-side operations; the middleware is responsible
 *   for injecting the session into every request.
 */
import type { AuthServerProvider, AuthUser } from './types';

// ─── Lazy import so the package is optional ───────────────────────────────────
// The SDK is only required when AUTH_PROVIDER=appwrite.
// If it's not installed and you're running Supabase mode this file is never used.
async function getAppwriteModules() {
    // node-appwrite is an optional peer dep; install with: pnpm add node-appwrite
    // @ts-ignore TS2307 — module may not be installed when using Supabase provider
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const { Client, Account, Users, ID } = await import('node-appwrite') as typeof import('node-appwrite');
    return { Client, Account, Users, ID };
}

function getSessionFromCookies(): string | null {
    // Synchronously read the Appwrite session cookie set by the middleware.
    // We do this inline because cookies() is async in Next.js 15.
    return null; // resolved in getUser() using async cookies()
}

function endpoint() {
    return process.env.APPWRITE_ENDPOINT ?? 'https://cloud.appwrite.io/v1';
}
function projectId() {
    return process.env.APPWRITE_PROJECT_ID!;
}
function apiKey() {
    return process.env.APPWRITE_API_KEY!;
}

// ─── Provider ─────────────────────────────────────────────────────────────────

export class AppwriteServerProvider implements AuthServerProvider {
    async getUser(): Promise<AuthUser | null> {
        const { Client, Account } = await getAppwriteModules();
        const { cookies } = await import('next/headers');
        const cookieStore = await cookies();
        const session = cookieStore.get('aw-session')?.value;
        if (!session) return null;

        const client = new Client()
            .setEndpoint(endpoint())
            .setProject(projectId())
            .setSession(session);

        try {
            const account = new Account(client);
            const user = await account.get();
            return {
                id: user.$id,
                email: user.email,
                displayName: user.name || null,
                // Appwrite uses `labels` (array) for roles; we treat first label as role.
                role: user.labels?.[0] ?? null,
            };
        } catch {
            return null;
        }
    }

    async signOut(): Promise<void> {
        const { Client, Account } = await getAppwriteModules();
        const { cookies } = await import('next/headers');
        const cookieStore = await cookies();
        const session = cookieStore.get('aw-session')?.value;
        if (!session) return;

        const client = new Client()
            .setEndpoint(endpoint())
            .setProject(projectId())
            .setSession(session);

        try {
            const account = new Account(client);
            await account.deleteSession('current');
        } catch { /* session may already be expired */ }

        // Clear the session cookie
        try {
            cookieStore.set('aw-session', '', { maxAge: 0, path: '/' });
        } catch { /* read-only in RSC — middleware clears on redirect */ }
    }

    async signIn(email: string, password: string): Promise<{ error: string | null }> {
        const { Client, Account } = await getAppwriteModules();
        const { cookies } = await import('next/headers');
        const cookieStore = await cookies();

        const client = new Client()
            .setEndpoint(endpoint())
            .setProject(projectId());

        try {
            const account = new Account(client);
            const session = await account.createEmailPasswordSession(email, password);
            // Persist session secret as an HttpOnly cookie
            cookieStore.set('aw-session', session.secret, {
                httpOnly: true,
                secure: process.env.NODE_ENV === 'production',
                sameSite: 'lax',
                path: '/',
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
            } as any);
            return { error: null };
        } catch (err: unknown) {
            const msg = err instanceof Error ? err.message : 'Sign-in failed';
            return { error: msg };
        }
    }

    async signUp(email: string, password: string): Promise<{ error: string | null }> {
        const { Client, Account, ID } = await getAppwriteModules();
        const client = new Client().setEndpoint(endpoint()).setProject(projectId());

        try {
            const account = new Account(client);
            await account.create(ID.unique(), email, password);
            // Sign in immediately after sign-up
            return this.signIn(email, password);
        } catch (err: unknown) {
            const msg = err instanceof Error ? err.message : 'Sign-up failed';
            return { error: msg };
        }
    }

    async resetPassword(email: string): Promise<{ error: string | null }> {
        const { Client, Account } = await getAppwriteModules();
        const appUrl = process.env.NEXT_PUBLIC_APP_URL ?? 'http://localhost:3000';
        const client = new Client().setEndpoint(endpoint()).setProject(projectId());

        try {
            const account = new Account(client);
            await account.createRecovery(email, `${appUrl}/auth/callback`);
            return { error: null };
        } catch (err: unknown) {
            const msg = err instanceof Error ? err.message : 'Password reset failed';
            return { error: msg };
        }
    }

    async exchangeCodeForSession(code: string): Promise<{ error: string | null }> {
        // Appwrite OAuth flows use userId + secret query params instead of a single code.
        // This is a compatibility shim; the callback route handler passes the full
        // code string — parse it as "userId:secret" if needed, or adapt your
        // callback page to call signIn() directly after OAuth redirect.
        const [userId, secret] = code.split(':');
        if (!userId || !secret) {
            return { error: 'Invalid callback code format — expected "userId:secret"' };
        }

        const { Client, Account } = await getAppwriteModules();
        const { cookies } = await import('next/headers');
        const cookieStore = await cookies();
        const client = new Client().setEndpoint(endpoint()).setProject(projectId());

        try {
            const account = new Account(client);
            const session = await account.createSession(userId, secret);
            cookieStore.set('aw-session', session.secret, {
                httpOnly: true,
                secure: process.env.NODE_ENV === 'production',
                sameSite: 'lax',
                path: '/',
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
            } as any);
            return { error: null };
        } catch (err: unknown) {
            const msg = err instanceof Error ? err.message : 'Code exchange failed';
            return { error: msg };
        }
    }

    async updateUser(data: {
        email?: string;
        password?: string;
        displayName?: string;
    }): Promise<{ error: string | null }> {
        const { Client, Account } = await getAppwriteModules();
        const { cookies } = await import('next/headers');
        const cookieStore = await cookies();
        const session = cookieStore.get('aw-session')?.value;
        if (!session) return { error: 'Not authenticated' };

        const client = new Client()
            .setEndpoint(endpoint())
            .setProject(projectId())
            .setSession(session);
        const account = new Account(client);

        try {
            if (data.displayName !== undefined) {
                await account.updateName(data.displayName);
            }
            if (data.email && data.password) {
                await account.updateEmail(data.email, data.password);
            }
            if (data.password && !data.email) {
                // Appwrite requires old password for password update — not available here.
                // The account-form.tsx should pass current password separately if needed.
                return { error: 'Appwrite requires current password to update password' };
            }
            return { error: null };
        } catch (err: unknown) {
            const msg = err instanceof Error ? err.message : 'Update failed';
            return { error: msg };
        }
    }

    async deleteUser(userId: string): Promise<{ error: string | null }> {
        const { Client, Users } = await getAppwriteModules();
        const client = new Client()
            .setEndpoint(endpoint())
            .setProject(projectId())
            .setKey(apiKey());

        try {
            const users = new Users(client);
            await users.delete(userId);
            return { error: null };
        } catch (err: unknown) {
            const msg = err instanceof Error ? err.message : 'Delete failed';
            return { error: msg };
        }
    }
}

void getSessionFromCookies; // suppress unused warning
