import { NextResponse } from 'next/server';
import { signOut } from '../auth/server';

/**
 * POST /api/auth/signout
 * Signs the current user out and redirects to /login.
 * Mount via: export { POST } from '@ui-gen/auth-core/handlers/auth-signout';
 */
export async function POST(): Promise<NextResponse> {
    await signOut();
    return NextResponse.redirect(
        new URL('/login', process.env.NEXT_PUBLIC_APP_URL ?? 'http://localhost:3000'),
        { status: 302 },
    );
}
