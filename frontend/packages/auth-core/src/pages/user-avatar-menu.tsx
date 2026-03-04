'use client';

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import {
    RiUser3Line,
    RiBankCardLine,
    RiBarChartBoxLine,
    RiBellLine,
    RiLogoutBoxLine,
} from '@remixicon/react';

interface UserAvatarMenuProps {
    email: string;
    displayName: string | null;
}

const MENU_ITEMS = [
    { href: '/account', label: 'Account', icon: RiUser3Line },
    { href: '/billing', label: 'Billing', icon: RiBankCardLine },
    { href: '/usage', label: 'Usage', icon: RiBarChartBoxLine },
    { href: '/notifications', label: 'Notifications', icon: RiBellLine },
];

export function UserAvatarMenu({ email, displayName }: UserAvatarMenuProps) {
    const [open, setOpen] = useState(false);
    const ref = useRef<HTMLDivElement>(null);

    // Close on outside click
    useEffect(() => {
        function handleClick(e: MouseEvent) {
            if (ref.current && !ref.current.contains(e.target as Node)) {
                setOpen(false);
            }
        }
        document.addEventListener('mousedown', handleClick);
        return () => document.removeEventListener('mousedown', handleClick);
    }, []);

    // Close on Escape
    useEffect(() => {
        function handleKey(e: KeyboardEvent) {
            if (e.key === 'Escape') setOpen(false);
        }
        document.addEventListener('keydown', handleKey);
        return () => document.removeEventListener('keydown', handleKey);
    }, []);

    const initials =
        (displayName?.[0] ?? email?.[0] ?? '?').toUpperCase();

    return (
        <div ref={ref} className="relative">
            {/* Avatar trigger */}
            <button
                onClick={() => setOpen((v) => !v)}
                aria-haspopup="true"
                aria-expanded={open}
                className="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-100 text-indigo-700 font-semibold text-sm ring-2 ring-transparent hover:ring-indigo-400 focus:outline-none focus:ring-indigo-400 transition-shadow"
            >
                {initials}
            </button>

            {/* Dropdown */}
            {open && (
                <div className="absolute right-0 top-11 z-50 w-64 origin-top-right rounded-xl border border-gray-200 bg-white shadow-lg ring-1 ring-black/5 focus:outline-none">
                    {/* User info header */}
                    <div className="border-b border-gray-100 px-4 py-3">
                        <p className="truncate text-sm font-semibold text-gray-900">
                            {displayName ?? email}
                        </p>
                        <p className="truncate text-xs text-gray-500">{email}</p>
                    </div>

                    {/* Nav links */}
                    <div className="py-1">
                        {MENU_ITEMS.map(({ href, label, icon: Icon }) => (
                            <Link
                                key={href}
                                href={href}
                                onClick={() => setOpen(false)}
                                className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-indigo-50 hover:text-indigo-700 transition-colors"
                            >
                                <Icon className="h-4 w-4 flex-shrink-0 text-gray-400" />
                                {label}
                            </Link>
                        ))}
                    </div>

                    {/* Sign out */}
                    <div className="border-t border-gray-100 py-1">
                        <form action="/api/auth/signout" method="POST">
                            <button
                                type="submit"
                                className="flex w-full items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-gray-900 transition-colors"
                            >
                                <RiLogoutBoxLine className="h-4 w-4 flex-shrink-0 text-gray-400" />
                                Sign out
                            </button>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
