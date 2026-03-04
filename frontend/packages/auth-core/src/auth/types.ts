// ─── Normalised user type ─────────────────────────────────────────────────────
// Returned by every auth provider — pages and layouts depend only on this type,
// never on supabase-js or appwrite-js SDK types directly.

export interface AuthUser {
    id: string;
    email: string;
    displayName: string | null;
    /** 'admin' or null — used for admin-section gating */
    role: string | null;
}

// ─── Server-side provider interface ──────────────────────────────────────────
// All operations needed by auth-core pages, layouts, and route handlers.
// Each auth backend (Supabase, Appwrite, …) implements this interface.

export interface AuthServerProvider {
    /**
     * Return the currently authenticated user from the request session.
     * Returns null when no valid session exists.
     */
    getUser(): Promise<AuthUser | null>;

    /** Sign out the current session. */
    signOut(): Promise<void>;

    /** Sign in with email + password. Returns an error string on failure. */
    signIn(
        email: string,
        password: string,
    ): Promise<{ error: string | null }>;

    /**
     * Create a new user account.
     * Returns an error string on failure, or null on success.
     */
    signUp(
        email: string,
        password: string,
    ): Promise<{ error: string | null }>;

    /**
     * Send a password-reset email to the given address.
     * Returns an error string on failure, or null on success.
     */
    resetPassword(email: string): Promise<{ error: string | null }>;

    /**
     * Exchange an OAuth/email-confirm code for a session.
     * Returns an error string on failure, or null on success.
     */
    exchangeCodeForSession(code: string): Promise<{ error: string | null }>;

    /**
     * Update the current user's email, password, and/or display name.
     * Pass only the fields you want to change.
     */
    updateUser(data: {
        email?: string;
        password?: string;
        displayName?: string;
    }): Promise<{ error: string | null }>;

    /**
     * Admin: permanently delete a user by ID.
     * Requires a privileged / service-role credential.
     */
    deleteUser(userId: string): Promise<{ error: string | null }>;
}
