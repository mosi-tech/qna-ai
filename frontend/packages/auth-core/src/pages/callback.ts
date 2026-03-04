import { NextRequest, NextResponse } from 'next/server';
import { exchangeCodeForSession } from '../auth/server';

/**
 * Supabase OAuth and email confirmation callback.
 * Exchanges the `code` query param for a session, then redirects.
 * SSO relay removed — consuming apps use their own Supabase session only.
 */
export async function GET(request: NextRequest): Promise<NextResponse> {
    const { searchParams, origin } = new URL(request.url);
    const code = searchParams.get('code');
    const next = searchParams.get('next') ?? '/account';

    if (code) {
        const { error } = await exchangeCodeForSession(code);
        if (!error) {
            const redirectUrl = new URL(next, origin);
            return NextResponse.redirect(redirectUrl);
        }
    }

    // Code missing or exchange failed
    const errorUrl = new URL('/login?error=auth_callback_failed', origin);
    return NextResponse.redirect(errorUrl);
}
