'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { clientSignOut } from '../auth/client';

const TIMEZONES = [
    'UTC',
    'America/New_York',
    'America/Chicago',
    'America/Denver',
    'America/Los_Angeles',
    'Europe/London',
    'Europe/Paris',
    'Europe/Berlin',
    'Asia/Tokyo',
    'Asia/Shanghai',
    'Asia/Kolkata',
    'Australia/Sydney',
];

interface AccountFormProps {
    userId: string;
    email: string;
    initialDisplayName: string;
    initialAvatarUrl: string;
    initialTimezone: string;
}

export function AccountForm({
    userId: _userId,
    email,
    initialDisplayName,
    initialAvatarUrl,
    initialTimezone,
}: AccountFormProps) {
    const router = useRouter();

    const [displayName, setDisplayName] = useState(initialDisplayName);
    const [avatarUrl, setAvatarUrl] = useState(initialAvatarUrl);
    const [timezone, setTimezone] = useState(initialTimezone);
    const [saving, setSaving] = useState(false);
    const [saveMessage, setSaveMessage] = useState<{
        type: 'success' | 'error';
        text: string;
    } | null>(null);

    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [deleteInput, setDeleteInput] = useState('');
    const [deleting, setDeleting] = useState(false);

    async function handleSave(e: React.FormEvent) {
        e.preventDefault();
        setSaving(true);
        setSaveMessage(null);

        try {
            const res = await fetch('/api/profile/update', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ display_name: displayName, avatar_url: avatarUrl, timezone }),
            });

            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.error ?? 'Failed to save');
            }

            setSaveMessage({ type: 'success', text: 'Profile updated.' });
            router.refresh();
        } catch (err: unknown) {
            setSaveMessage({
                type: 'error',
                text: err instanceof Error ? err.message : 'Something went wrong.',
            });
        } finally {
            setSaving(false);
        }
    }

    async function handleDelete() {
        if (deleteInput !== 'delete my account') return;
        setDeleting(true);

        try {
            const res = await fetch('/api/profile/delete', { method: 'DELETE' });
            if (!res.ok) throw new Error('Failed to delete account');

            await clientSignOut();
            router.push('/login?deleted=1');
        } catch (err: unknown) {
            setSaveMessage({
                type: 'error',
                text: err instanceof Error ? err.message : 'Failed to delete account.',
            });
            setDeleting(false);
            setShowDeleteConfirm(false);
        }
    }

    return (
        <div className="space-y-6">
            {/* Profile card */}
            <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Profile</h2>

                {saveMessage && (
                    <div
                        className={`mb-4 rounded-lg px-4 py-3 text-sm ${saveMessage.type === 'success'
                            ? 'bg-green-50 text-green-700'
                            : 'bg-red-50 text-red-700'
                            }`}
                    >
                        {saveMessage.text}
                    </div>
                )}

                <form onSubmit={handleSave} className="space-y-4">
                    {/* Avatar preview */}
                    <div className="flex items-center gap-4">
                        {avatarUrl ? (
                            // eslint-disable-next-line @next/next/no-img-element
                            <img
                                src={avatarUrl}
                                alt="Avatar"
                                className="h-16 w-16 rounded-full object-cover border border-gray-200"
                            />
                        ) : (
                            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-indigo-100 text-indigo-700 font-bold text-xl">
                                {displayName?.[0]?.toUpperCase() ?? email[0]?.toUpperCase() ?? '?'}
                            </div>
                        )}
                        <div className="flex-1">
                            <label className="block text-sm font-medium text-gray-700">
                                Avatar URL
                            </label>
                            <input
                                type="url"
                                value={avatarUrl}
                                onChange={(e) => setAvatarUrl(e.target.value)}
                                className="mt-1 block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 placeholder-gray-400 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                                placeholder="https://..."
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700">
                            Display name
                        </label>
                        <input
                            type="text"
                            required
                            value={displayName}
                            onChange={(e) => setDisplayName(e.target.value)}
                            className="mt-1 block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 placeholder-gray-400 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                            placeholder="Your name"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700">
                            Email
                        </label>
                        <input
                            type="email"
                            value={email}
                            disabled
                            className="mt-1 block w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-500 shadow-sm cursor-not-allowed"
                        />
                        <p className="mt-1 text-xs text-gray-400">
                            Email cannot be changed here. Contact support.
                        </p>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700">
                            Timezone
                        </label>
                        <select
                            value={timezone}
                            onChange={(e) => setTimezone(e.target.value)}
                            className="mt-1 block w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                        >
                            {TIMEZONES.map((tz) => (
                                <option key={tz} value={tz}>
                                    {tz}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="flex justify-end">
                        <button
                            type="submit"
                            disabled={saving}
                            className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
                        >
                            {saving ? 'Saving…' : 'Save changes'}
                        </button>
                    </div>
                </form>
            </section>

            {/* Danger zone */}
            <section className="rounded-2xl border border-red-200 bg-white p-6 shadow-sm">
                <h2 className="text-lg font-semibold text-red-700 mb-1">Danger zone</h2>
                <p className="text-sm text-gray-500 mb-4">
                    Permanently delete your account and all associated data. This cannot be undone.
                </p>

                {!showDeleteConfirm ? (
                    <button
                        onClick={() => setShowDeleteConfirm(true)}
                        className="rounded-lg border border-red-300 px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                    >
                        Delete account
                    </button>
                ) : (
                    <div className="space-y-3">
                        <p className="text-sm text-gray-700">
                            Type <strong>delete my account</strong> to confirm:
                        </p>
                        <input
                            type="text"
                            value={deleteInput}
                            onChange={(e) => setDeleteInput(e.target.value)}
                            className="block w-full rounded-lg border border-red-300 bg-white px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-red-500 focus:outline-none focus:ring-1 focus:ring-red-500"
                            placeholder="delete my account"
                        />
                        <div className="flex gap-3">
                            <button
                                onClick={handleDelete}
                                disabled={deleteInput !== 'delete my account' || deleting}
                                className="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-500 disabled:cursor-not-allowed disabled:opacity-50"
                            >
                                {deleting ? 'Deleting…' : 'Confirm delete'}
                            </button>
                            <button
                                onClick={() => {
                                    setShowDeleteConfirm(false);
                                    setDeleteInput('');
                                }}
                                className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                )}
            </section>
        </div>
    );
}
