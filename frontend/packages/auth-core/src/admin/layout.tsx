import { redirect } from 'next/navigation';
import Link from 'next/link';
import { getAuthUser } from '../auth/server';
import {
    RiShieldUserLine,
    RiGroupLine,
    RiLineChartLine,
    RiBarChart2Line,
    RiArrowLeftLine,
} from '@remixicon/react';

const ADMIN_NAV = [
    { href: '/admin/users', label: 'Users', icon: RiGroupLine },
    { href: '/admin/revenue', label: 'Revenue', icon: RiLineChartLine },
    { href: '/admin/usage', label: 'Usage', icon: RiBarChart2Line },
];

export default async function AdminLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const user = await getAuthUser();
    if (!user) redirect('/login');

    const isAdmin = user.role === 'admin';
    if (!isAdmin) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-gray-50 p-6">
                <div className="max-w-sm text-center">
                    <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-red-100">
                        <RiShieldUserLine className="h-7 w-7 text-red-500" />
                    </div>
                    <h1 className="text-xl font-bold text-gray-900">Access Denied</h1>
                    <p className="mt-2 text-sm text-gray-500">
                        You do not have permission to view this page. Contact your administrator if
                        you believe this is an error.
                    </p>
                    <Link
                        href="/account"
                        className="mt-6 inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-indigo-700"
                    >
                        <RiArrowLeftLine className="h-4 w-4" />
                        Back to Dashboard
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="flex min-h-screen bg-gray-50">
            {/* Sidebar */}
            <aside className="hidden w-64 flex-shrink-0 border-r border-gray-200 bg-white lg:flex lg:flex-col">
                <div className="flex h-16 items-center gap-3 border-b border-gray-200 px-6">
                    <RiShieldUserLine className="h-5 w-5 text-red-500" />
                    <span className="text-lg font-bold tracking-tight text-gray-900">
                        Admin Panel
                    </span>
                </div>

                <nav className="flex-1 space-y-1 px-3 py-4">
                    {ADMIN_NAV.map(({ href, label, icon: Icon }) => (
                        <Link
                            key={href}
                            href={href}
                            className="group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-red-50 hover:text-red-700"
                        >
                            <Icon className="h-5 w-5 flex-shrink-0 text-gray-400 group-hover:text-red-600" />
                            {label}
                        </Link>
                    ))}
                </nav>

                <div className="border-t border-gray-200 p-4">
                    <Link
                        href="/account"
                        className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900"
                    >
                        <RiArrowLeftLine className="h-4 w-4" />
                        Back to Dashboard
                    </Link>
                </div>
            </aside>

            {/* Mobile top-bar */}
            <div className="flex flex-1 flex-col overflow-hidden">
                <div className="flex h-14 items-center justify-between border-b border-gray-200 bg-white px-4 lg:hidden">
                    <div className="flex items-center gap-2">
                        <RiShieldUserLine className="h-5 w-5 text-red-500" />
                        <span className="text-base font-bold text-gray-900">Admin Panel</span>
                    </div>
                    <nav className="flex items-center gap-3">
                        {ADMIN_NAV.map(({ href, label, icon: Icon }) => (
                            <Link
                                key={href}
                                href={href}
                                className="rounded p-1.5 text-gray-500 hover:bg-gray-100 hover:text-red-600"
                                title={label}
                            >
                                <Icon className="h-5 w-5" />
                            </Link>
                        ))}
                    </nav>
                </div>

                <main className="flex-1 overflow-y-auto px-6 py-8 lg:px-10">
                    {children}
                </main>
            </div>
        </div>
    );
}
