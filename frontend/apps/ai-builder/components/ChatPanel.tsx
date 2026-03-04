'use client';

/**
 * ChatPanel.tsx
 *
 * Left-panel chat UI — message history, suggestion cards, and input bar.
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { generateSuggestions } from '@/services/dashboardAI';

export interface ChatMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    loading?: boolean;
    error?: string;
}

interface ChatPanelProps {
    messages: ChatMessage[];
    onSend: (text: string) => void;
    isLoading: boolean;
}

function UserBubble({ content }: { content: string }) {
    return (
        <div className="flex justify-end mb-4">
            <div className="max-w-[85%] px-4 py-2.5 rounded-2xl rounded-tr-sm bg-blue-600 text-white text-sm leading-relaxed shadow-sm">
                {content}
            </div>
        </div>
    );
}

function AssistantBubble({ content, loading, error }: { content: string; loading?: boolean; error?: string }) {
    return (
        <div className="flex justify-start mb-4">
            <div className="flex items-start gap-2 max-w-[85%]">
                <div className="flex-shrink-0 w-7 h-7 rounded-full bg-gradient-to-br from-violet-500 to-blue-600 flex items-center justify-center text-white text-xs font-bold shadow-sm">
                    AI
                </div>
                <div
                    className={`px-4 py-2.5 rounded-2xl rounded-tl-sm text-sm leading-relaxed shadow-sm ${error
                            ? 'bg-red-50 dark:bg-red-950 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-800'
                            : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700'
                        }`}
                >
                    {loading ? (
                        <span className="flex items-center gap-1.5 text-slate-400 dark:text-slate-500">
                            <LoadingDots />
                            <span>Building dashboard…</span>
                        </span>
                    ) : error ? (
                        <span>⚠ {error}</span>
                    ) : (
                        content
                    )}
                </div>
            </div>
        </div>
    );
}

function LoadingDots() {
    return (
        <span className="flex gap-1">
            {[0, 1, 2].map((i) => (
                <span
                    key={i}
                    className="w-1.5 h-1.5 rounded-full bg-blue-400 dark:bg-blue-500 animate-bounce"
                    style={{ animationDelay: `${i * 0.15}s` }}
                />
            ))}
        </span>
    );
}

const DEFAULT_SUGGESTIONS = [
    'Show me my equity portfolio with holdings, daily P&L, sector allocation and YTD performance',
    'Build an ETF dashboard with returns, expense ratios, tracking error and benchmark comparison',
    'Create a dividend income tracker with payment calendar, yield by holding and payout history',
    'Display a trade history dashboard with win rate, average gain/loss and strategy breakdown',
];

export default function ChatPanel({ messages, onSend, isLoading }: ChatPanelProps) {
    const [input, setInput] = React.useState('');
    const [suggestions, setSuggestions] = useState<string[]>(DEFAULT_SUGGESTIONS);
    const [suggestionsLoading, setSuggestionsLoading] = useState(false);
    const bottomRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLTextAreaElement>(null);

    const handleRefreshSuggestions = useCallback(async () => {
        setSuggestionsLoading(true);
        try {
            const next = await generateSuggestions();
            setSuggestions(next);
        } catch {
            // keep current suggestions on error
        } finally {
            setSuggestionsLoading(false);
        }
    }, []);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        const trimmed = input.trim();
        if (!trimmed || isLoading) return;
        onSend(trimmed);
        setInput('');
    }

    function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e as unknown as React.FormEvent);
        }
    }

    const isEmpty = messages.length === 0;

    return (
        <div className="flex flex-col h-full bg-slate-50 dark:bg-slate-900">
            {/* Messages area */}
            <div className="flex-1 overflow-y-auto px-4 py-6 space-y-1">
                {isEmpty ? (
                    <div className="flex flex-col items-center justify-center h-full gap-6 text-center px-4">
                        <div>
                            <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-br from-violet-500 to-blue-600 flex items-center justify-center text-white text-2xl font-bold shadow-lg mb-4">
                                ✦
                            </div>
                            <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-1">
                                Dashboard Builder
                            </h2>
                            <p className="text-sm text-slate-500 dark:text-slate-400">
                                Describe what you want to see and I&apos;ll build a live dashboard for you.
                            </p>
                        </div>
                        <div className="w-full">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-xs font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                                    Suggestions
                                </span>
                                <button
                                    onClick={handleRefreshSuggestions}
                                    disabled={suggestionsLoading || isLoading}
                                    title="Get new suggestions"
                                    className="flex items-center gap-1 px-2 py-1 rounded-lg text-xs text-slate-400 dark:text-slate-500 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950 disabled:opacity-40 transition-colors"
                                >
                                    <svg
                                        className={`w-3.5 h-3.5 ${suggestionsLoading ? 'animate-spin' : ''}`}
                                        fill="none"
                                        viewBox="0 0 24 24"
                                        stroke="currentColor"
                                        strokeWidth={2.5}
                                    >
                                        <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                    </svg>
                                    {suggestionsLoading ? 'Refreshing…' : 'Refresh'}
                                </button>
                            </div>
                            <div className="space-y-2">
                                {suggestions.map((s) => (
                                    <button
                                        key={s}
                                        onClick={() => onSend(s)}
                                        disabled={isLoading || suggestionsLoading}
                                        className="w-full text-left px-4 py-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm text-slate-600 dark:text-slate-300 hover:border-blue-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors shadow-sm disabled:opacity-50"
                                    >
                                        &ldquo;{s}&rdquo;
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                ) : (
                    messages.map((msg) =>
                        msg.role === 'user' ? (
                            <UserBubble key={msg.id} content={msg.content} />
                        ) : (
                            <AssistantBubble key={msg.id} content={msg.content} loading={msg.loading} error={msg.error} />
                        ),
                    )
                )}
                <div ref={bottomRef} />
            </div>

            {/* Input bar */}
            <div className="border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-3">
                <form onSubmit={handleSubmit} className="flex items-end gap-2">
                    <textarea
                        ref={inputRef}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        rows={2}
                        placeholder="Describe the dashboard you need…"
                        disabled={isLoading}
                        className="flex-1 resize-none rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-4 py-2.5 text-sm text-slate-800 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 transition-colors"
                    />
                    <button
                        type="submit"
                        disabled={isLoading || !input.trim()}
                        className="flex-shrink-0 w-10 h-10 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 dark:disabled:bg-slate-700 text-white flex items-center justify-center transition-colors shadow-sm"
                        aria-label="Send"
                    >
                        {isLoading ? (
                            <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l3-3-3-3v4a8 8 0 00-8 8h4l-3 3 3 3H4z" />
                            </svg>
                        ) : (
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                                <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
                            </svg>
                        )}
                    </button>
                </form>
                <p className="text-xs text-slate-400 dark:text-slate-600 mt-1.5 text-center">
                    Press Enter to send · Shift+Enter for new line
                </p>
            </div>
        </div>
    );
}
