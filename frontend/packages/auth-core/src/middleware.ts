import { type NextRequest, NextResponse } from 'next/server';
import { createServerClient, type CookieOptions } from '@supabase/ssr';

export interface AuthMiddlewareConfig {
    /** App identifier stored in usage_events.app_id (e.g. 'ai-builder') */
    appId: string;
    /** Request path prefixes that require an authenticated session */
    protectedPrefixes: string[];
    /** Request path prefixes that require role === 'admin' */
    adminPrefixes?: string[];
    /**
     * Reserved for documentation — quota enforcement must be done in route handlers
     * or server components (not middleware) because Edge Runtime does not support
     * the Node.js `net` module required by the Postgres client.
     */
    quotaEvent?: string;
    /** Where to redirect unauthenticated users. Default: '/login' */
    loginUrl?: string;
    /** Where to redirect users who have exceeded their quota. Default: '/billing' */
    billingUrl?: string;
    /** Unused by the middleware itself, exposed for convenience. Default: '/dashboard' */
    afterLoginUrl?: string;
}

function matchesAny(pathname: string, prefixes: string[] | undefined): boolean {
    return (prefixes ?? []).some((prefix) => pathname.startsWith(prefix));
}

/**
 * Creates a Next.js middleware function that:
 * 1. Refreshes the Supabase session via @supabase/ssr (cookie-based, no HTTP calls).
 * 2. Redirects unauthenticated requests on protected routes to `loginUrl`.
 * 3. Returns 403 for non-admin users on admin routes.
 * 4. Injects `x-user-id` and `x-user-email` request headers for downstream handlers.
 */
export function createAuthMiddleware(config: AuthMiddlewareConfig) {
    const {
        protectedPrefixes,
        adminPrefixes = [],
        loginUrl = '/login',
    } = config;

    return async function middleware(req: NextRequest): Promise<NextResponse> {
        const { pathname } = req.nextUrl;

        // Build a response object that the Supabase SSR client will mutate with
        // refreshed session cookies.
        let supabaseResponse = NextResponse.next({ request: req });

        const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
        const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

        if (!supabaseUrl || !supabaseAnonKey) {
            console.error(
                '[auth-core middleware] NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY must be set.',
            );
            // Still enforce auth on protected/admin routes so misconfiguration
            // doesn't silently grant access to authenticated-only pages.
            const isProtectedEarly = matchesAny(pathname, protectedPrefixes);
            const isAdminEarly = matchesAny(pathname, adminPrefixes);
            if (isProtectedEarly || isAdminEarly) {
                const redirectUrl = req.nextUrl.clone();
                redirectUrl.pathname = loginUrl;
                redirectUrl.searchParams.set('next', pathname);
                return NextResponse.redirect(redirectUrl);
            }
            return NextResponse.next({ request: req });
        }

        // ── 1. Refresh Supabase session ──────────────────────────────────────────
        const supabase = createServerClient(supabaseUrl, supabaseAnonKey, {
            cookies: {
                getAll() {
                    return req.cookies.getAll();
                },
                setAll(cookiesToSet: { name: string; value: string; options: CookieOptions }[]) {
                    cookiesToSet.forEach(({ name, value }) => req.cookies.set(name, value));
                    supabaseResponse = NextResponse.next({ request: req });
                    cookiesToSet.forEach(({ name, value, options }) =>
                        // eslint-disable-next-line @typescript-eslint/no-explicit-any
                        supabaseResponse.cookies.set(name, value, options as any),
                    );
                },
            },
        });

        // IMPORTANT: must await getUser() to ensure the session is refreshed.
        const {
            data: { user },
        } = await supabase.auth.getUser();

        const isProtected = matchesAny(pathname, protectedPrefixes);
        const isAdmin = matchesAny(pathname, adminPrefixes);

        // ── 2. Redirect unauthenticated users on protected routes ────────────────
        if ((isProtected || isAdmin) && !user) {
            const redirectUrl = req.nextUrl.clone();
            redirectUrl.pathname = loginUrl;
            redirectUrl.searchParams.set('next', pathname);
            return NextResponse.redirect(redirectUrl);
        }

        if (user) {
            // ── 3. Admin route guard ───────────────────────────────────────────────
            if (isAdmin) {
                const role = user.user_metadata?.role as string | undefined;
                if (role !== 'admin') {
                    // Return 403 without revealing the route exists (no redirect)
                    return new NextResponse('Forbidden', { status: 403 });
                }
            }

            // ── 4. Inject user identity headers ────────────────────────────────────
            const requestHeaders = new Headers(req.headers);
            requestHeaders.set('x-user-id', user.id);
            requestHeaders.set('x-user-email', user.email ?? '');

            const response = NextResponse.next({
                request: { headers: requestHeaders },
            });

            // Forward any session cookies set by the Supabase client
            supabaseResponse.cookies.getAll().forEach(({ name, value }) => {
                response.cookies.set(name, value);
            });

            return response;
        }

        return supabaseResponse;
    };
}
