import { createAuthMiddleware } from '@ui-gen/auth-core/middleware';

export const middleware = createAuthMiddleware({
  appId: 'ai-builder',
  protectedPrefixes: ['/builder', '/dashboard'],
  adminPrefixes: ['/admin'],
  quotaEvent: 'ai_builds',
  loginUrl: '/login',
  billingUrl: '/billing',
});

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|.*\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
};
