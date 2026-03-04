'use client';

import { useState } from 'react';
import {
    RiMailLine,
    RiNotificationLine,
    RiCheckLine,
} from '@remixicon/react';
import { NOTIFICATION_EVENTS } from '../handlers/notification-prefs';
import type { PrefEntry } from '../handlers/notification-prefs';

const CHANNEL_META = {
    email: { label: 'Email', icon: RiMailLine },
    in_app: { label: 'In-App', icon: RiNotificationLine },
} as const;

function getPref(
    prefs: PrefEntry[],
    eventType: string,
    channel: 'email' | 'in_app',
): boolean {
    return (
        prefs.find((p) => p.eventType === eventType && p.channel === channel)
            ?.enabled ?? true
    );
}

interface NotificationPrefsClientProps {
    initialPrefs: PrefEntry[];
    events: typeof NOTIFICATION_EVENTS;
}

export function NotificationPrefsClient({
    initialPrefs,
    events,
}: NotificationPrefsClientProps) {
    const [prefs, setPrefs] = useState<PrefEntry[]>(initialPrefs);
    const [saving, setSaving] = useState<`${string}::${string}` | null>(null);
    const [savedKey, setSavedKey] = useState<`${string}::${string}` | null>(null);
    const [error, setError] = useState<string | null>(null);

    async function handleToggle(
        eventType: string,
        channel: 'email' | 'in_app',
        currentValue: boolean,
    ) {
        const key = `${eventType}::${channel}` as const;
        const newValue = !currentValue;

        // Optimistic update
        setPrefs((prev) =>
            prev.map((p) =>
                p.eventType === eventType && p.channel === channel
                    ? { ...p, enabled: newValue }
                    : p,
            ),
        );
        setSaving(key);
        setError(null);

        try {
            const res = await fetch('/api/notifications/prefs', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ eventType, channel, enabled: newValue }),
            });

            if (!res.ok) throw new Error('Failed to save preference');

            setSavedKey(key);
            setTimeout(() => setSavedKey(null), 1500);
        } catch {
            // Roll back optimistic update
            setPrefs((prev) =>
                prev.map((p) =>
                    p.eventType === eventType && p.channel === channel
                        ? { ...p, enabled: currentValue }
                        : p,
                ),
            );
            setError('Could not update preference — please try again.');
        } finally {
            setSaving(null);
        }
    }

    return (
        <div className="space-y-4">
            {error && (
                <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                    {error}
                </div>
            )}

            {/* Header row */}
            <div
                className="hidden grid-cols-[1fr_80px_80px] gap-4 rounded-xl border border-gray-200 bg-gray-50 px-5 py-2.5 text-xs font-semibold uppercase tracking-wide text-gray-500 sm:grid"
            >
                <span>Event</span>
                <span className="text-center">Email</span>
                <span className="text-center">In-App</span>
            </div>

            {events.map(({ id: eventType, label, channels }) => (
                <div
                    key={eventType}
                    className="grid grid-cols-1 gap-3 rounded-xl border border-gray-200 bg-white px-5 py-4 shadow-sm transition-shadow hover:shadow-md sm:grid-cols-[1fr_80px_80px] sm:items-center sm:gap-4"
                >
                    {/* Event label */}
                    <div>
                        <p className="text-sm font-medium text-gray-900">{label}</p>
                        {/* Mobile channel buttons */}
                        <div className="mt-1 flex flex-wrap gap-1.5 sm:hidden">
                            {(channels as readonly ('email' | 'in_app')[]).map((ch) => {
                                const { label: chLabel, icon: Icon } = CHANNEL_META[ch];
                                const enabled = getPref(prefs, eventType, ch);
                                const key = `${eventType}::${ch}` as const;
                                return (
                                    <button
                                        key={ch}
                                        onClick={() => handleToggle(eventType, ch, enabled)}
                                        disabled={saving === key}
                                        className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium transition-colors ${enabled
                                            ? 'border-indigo-200 bg-indigo-50 text-indigo-700'
                                            : 'border-gray-200 bg-white text-gray-400'
                                            }`}
                                    >
                                        <Icon className="h-3.5 w-3.5" />
                                        {chLabel}
                                        {savedKey === key && (
                                            <RiCheckLine className="h-3.5 w-3.5 text-emerald-500" />
                                        )}
                                    </button>
                                );
                            })}
                        </div>
                    </div>

                    {/* Email column */}
                    <div className="hidden justify-center sm:flex">
                        {(channels as ReadonlyArray<string>).includes('email') ? (
                            <Toggle
                                enabled={getPref(prefs, eventType, 'email')}
                                loading={saving === `${eventType}::email`}
                                saved={savedKey === `${eventType}::email`}
                                onToggle={() =>
                                    handleToggle(
                                        eventType,
                                        'email',
                                        getPref(prefs, eventType, 'email'),
                                    )
                                }
                            />
                        ) : (
                            <span className="text-xs text-gray-300">—</span>
                        )}
                    </div>

                    {/* In-app column */}
                    <div className="hidden justify-center sm:flex">
                        {(channels as ReadonlyArray<string>).includes('in_app') ? (
                            <Toggle
                                enabled={getPref(prefs, eventType, 'in_app')}
                                loading={saving === `${eventType}::in_app`}
                                saved={savedKey === `${eventType}::in_app`}
                                onToggle={() =>
                                    handleToggle(
                                        eventType,
                                        'in_app',
                                        getPref(prefs, eventType, 'in_app'),
                                    )
                                }
                            />
                        ) : (
                            <span className="text-xs text-gray-300">—</span>
                        )}
                    </div>
                </div>
            ))}

            <p className="text-xs text-gray-400">
                Changes save automatically. Transactional notifications (e.g. payment receipts)
                cannot be disabled.
            </p>
        </div>
    );
}

// ─── Toggle switch ────────────────────────────────────────────────────────────

interface ToggleProps {
    enabled: boolean;
    loading: boolean;
    saved: boolean;
    onToggle: () => void;
}

function Toggle({ enabled, loading, saved, onToggle }: ToggleProps) {
    return (
        <div className="relative flex items-center justify-center">
            <button
                role="switch"
                aria-checked={enabled}
                onClick={onToggle}
                disabled={loading}
                className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60 ${enabled ? 'bg-indigo-600' : 'bg-gray-200'
                    }`}
            >
                <span
                    className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition-transform ${enabled ? 'translate-x-5' : 'translate-x-0'
                        }`}
                />
            </button>
            {saved && (
                <span className="absolute -right-5 text-emerald-500">
                    <RiCheckLine className="h-3.5 w-3.5" />
                </span>
            )}
        </div>
    );
}
