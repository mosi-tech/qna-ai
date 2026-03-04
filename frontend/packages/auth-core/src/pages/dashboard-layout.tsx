import Link from 'next/link';
import { redirect } from 'next/navigation';
import { getAuthUser } from '../auth/server';
import { UserAvatarMenu } from './user-avatar-menu';
import {
    RiUser3Line,
    RiBankCardLine,
    RiBarChartBoxLine,
    RiBellLine,
    RiLogoutBoxLine,
    RiShieldUserLine,
} from '@remixicon/react';
import type { RemixiconComponentType } from '@remixicon/react';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface NavItem {
    href: string;
    label: string;
    icon: RemixiconComponentType;
}

export interface DashboardLayoutConfig {
    /** App name shown in the sidebar header and mobile top bar */
    appName: string;
    /**
     * Nav items to prepend before the standard auth items.
     * Typical use: [{ href: '/builder', label: 'Builder', icon: RiLayoutGridLine }]
     */
    extraNavItems?: NavItem[];
    /**
     * Optional function that receives the authenticated user's ID and returns
     * a React node rendered in the top-right of the header bar.
     * Useful for per-user components like a notification bell.
     *
     * @example
     * headerActions: (userId) => <NovuBell userId={userId} />
     */
    headerActions?: (userId: string) => React.ReactNode;
}

// ─── Standard auth nav items (always present) ─────────────────────────────────

const AUTH_NAV_ITEMS: NavItem[] = [
    { href: '/account', label: 'Account', icon: RiUser3Line },
    { href: '/billing', label: 'Billing', icon: RiBankCardLine },
    { href: '/usage', label: 'Usage', icon: RiBarChartBoxLine },
    { href: '/notifications', label: 'Notifications', icon: RiBellLine },
];

// ─── Factory ──────────────────────────────────────────────────────────────────

/**
 * Returns an async RSC layout suitable for Next.js `app/(dashboard)/layout.tsx`.
 *
 * Usage:
 * ```ts
 * // app/(dashboard)/layout.tsx
 * import { createDashboardLayout } from '@ui-gen/auth-core/pages/dashboard-layout';
 * import { RiLayoutGridLine } from '@remixicon/react';
 *
 * export default createDashboardLayout({
 *   appName: 'AI Builder',
 *   extraNavItems: [{ href: '/builder', label: 'Builder', icon: RiLayoutGridLine }],
 * });
 * ```
 */
export function createDashboardLayout(config: DashboardLayoutConfig) {
    const { appName, extraNavItems = [], headerActions } = config;
    const navItems = [...extraNavItems, ...AUTH_NAV_ITEMS];

    return async function DashboardLayout({
        children,
    }: {
        children: React.ReactNode;
    }) {
        const user = await getAuthUser();
        if (!user) redirect('/login');

        const isAdmin = user.role === 'admin';

        return (
            <div className="flex min-h-screen bg-gray-50">
                {/* Sidebar */}
                <aside className="hidden w-64 flex-shrink-0 border-r border-gray-200 bg-white lg:flex lg:flex-col">
                    <div className="flex h-16 items-center border-b border-gray-200 px-6">
                        <span className="text-lg font-bold text-indigo-600 tracking-tight">
                            {appName}
                        </span>
                    </div>

                    <nav className="flex-1 space-y-1 px-3 py-4">
                        {navItems.map(({ href, label, icon: Icon }) => (
                            <Link
                                key={href}
                                href={href}
                                className="group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-gray-700 hover:bg-indigo-50 hover:text-indigo-700 transition-colors"
                            >
                                <Icon className="h-5 w-5 flex-shrink-0 text-gray-400 group-hover:text-indigo-600" />
                                {label}
                            </Link>
                        ))}

                        {isAdmin && (
                            <>
                                <div className="pt-3 pb-1 px-3">
                                    <p className="text-xs font-semibold uppercase tracking-wide text-gray-400">
                                        Admin
                                    </p>
                                </div>
                                <Link
                                    href="/admin/users"
                                    className="group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-gray-700 hover:bg-red-50 hover:text-red-700 transition-colors"
                                >
                                    <RiShieldUserLine className="h-5 w-5 flex-shrink-0 text-gray-400 group-hover:text-red-600" />
                                    Admin Panel
                                </Link>
                            </>
                        )}
                    </nav>

                    {/* Bottom: user info + sign out */}
                    <div className="border-t border-gray-200 p-4">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-100 text-indigo-700 font-semibold text-sm flex-shrink-0">
                                {user.displayName?.[0]?.toUpperCase() ??
                                    user.email?.[0]?.toUpperCase() ??
                                    '?'}
                            </div>
                            <div className="min-w-0">
                                <p className="truncate text-sm font-medium text-gray-900">
                                    {user.displayName ?? 'User'}
                                </p>
                                <p className="truncate text-xs text-gray-500">{user.email}</p>
                            </div>
                        </div>
                        <form action="/api/auth/signout" method="POST">
                            <button
                                type="submit"
                                className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-colors"
                            >
                                <RiLogoutBoxLine className="h-4 w-4" />
                                Sign out
                            </button>
                        </form>
                    </div>
                </aside>

                {/* Main content */}
                <main className="flex flex-1 flex-col overflow-y-auto">
                    {/* Top header bar */}
                    <header className="sticky top-0 z-10 flex h-16 shrink-0 items-center justify-between border-b border-gray-200 bg-white px-4 sm:px-6">
                        <div className="flex items-center gap-2 lg:hidden">
                            <span className="text-base font-bold text-indigo-600">{appName}</span>
                        </div>
                        <div className="hidden lg:block" />
                        <div className="flex items-center gap-3">
                            {headerActions ? headerActions(user.id) : null}
                            <UserAvatarMenu
                                email={user.email ?? ''}
                                displayName={user.displayName ?? null}
                            />
                        </div>
                    </header>

                    <div className="mx-auto w-full max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
                        {children}
                    </div>
                </main>
            </div>
        );
    };
}
