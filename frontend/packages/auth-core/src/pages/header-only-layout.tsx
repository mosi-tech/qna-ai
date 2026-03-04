import { redirect } from 'next/navigation';
import { getAuthUser } from '../auth/server';
import { UserAvatarMenu } from './user-avatar-menu';

export interface HeaderOnlyLayoutConfig {
    /** App name shown in the top-left of the header bar */
    appName: string;
    /** Optional extra content rendered beside the app name (left side) */
    headerLeft?: React.ReactNode;
    /** Optional function called with userId for right-side header slots (e.g. NovuBell) */
    headerActions?: (userId: string) => React.ReactNode;
}

/**
 * Returns an async RSC layout with only a top header bar (no sidebar).
 * Suitable for full-screen app pages like /builder.
 *
 * Usage:
 * ```ts
 * // app/(builder)/layout.tsx
 * import { createHeaderOnlyLayout } from '@ui-gen/auth-core/pages/header-only-layout';
 * export default createHeaderOnlyLayout({ appName: 'AI Builder' });
 * ```
 */
export function createHeaderOnlyLayout(config: HeaderOnlyLayoutConfig) {
    const { appName, headerLeft, headerActions } = config;

    return async function HeaderOnlyLayout({
        children,
    }: {
        children: React.ReactNode;
    }) {
        const user = await getAuthUser();
        if (!user) redirect('/login');

        return (
            <div className="flex min-h-screen flex-col bg-gray-50">
                {/* Header */}
                <header className="sticky top-0 z-10 flex h-14 shrink-0 items-center justify-between border-b border-gray-200 bg-white px-4 sm:px-6">
                    <div className="flex items-center gap-3">
                        <span className="text-base font-bold text-indigo-600">
                            {appName}
                        </span>
                        {headerLeft}
                    </div>
                    <div className="flex items-center gap-3">
                        {headerActions ? headerActions(user.id) : null}
                        <UserAvatarMenu
                            email={user.email ?? ''}
                            displayName={user.displayName ?? null}
                        />
                    </div>
                </header>

                {/* Full-width content */}
                <main className="flex flex-1 flex-col overflow-hidden">
                    {children}
                </main>
            </div>
        );
    };
}
