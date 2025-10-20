'use client';

import { useEffect, useState } from 'react';
import { useSessionManager, SessionMetadata } from '@/lib/hooks/useSessionManager';
import { formatDistanceToNow } from 'date-fns';

interface SessionListProps {
  userId: string;
  onSelectSession: (sessionId: string) => void;
  currentSessionId?: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function SessionList({
  userId,
  onSelectSession,
  currentSessionId,
  isOpen,
  onClose,
}: SessionListProps) {
  const { sessions, isLoadingSessions, error, listUserSessions, deleteSession, updateSession } =
    useSessionManager();
  const [searchQuery, setSearchQuery] = useState('');
  const [showArchived, setShowArchived] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && userId) {
      listUserSessions(userId, searchQuery || undefined, showArchived || undefined);
    }
  }, [userId, isOpen, showArchived]);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    if (userId && query.length >= 2) {
      listUserSessions(userId, query, showArchived || undefined);
    } else if (!query) {
      listUserSessions(userId, undefined, showArchived || undefined);
    }
  };

  const handleDelete = async (sessionId: string) => {
    if (!confirm('Are you sure you want to delete this session?')) return;

    try {
      setDeletingId(sessionId);
      await deleteSession(sessionId);
    } catch (err) {
      console.error('Failed to delete session:', err);
    } finally {
      setDeletingId(null);
    }
  };

  const handleArchive = async (session: SessionMetadata) => {
    try {
      await updateSession(session.session_id, session.title, !session.is_archived);
    } catch (err) {
      console.error('Failed to archive session:', err);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex">
      <div
        className="absolute inset-0 bg-black bg-opacity-50"
        onClick={onClose}
      />

      <div className="relative w-96 bg-white flex flex-col max-h-screen">
        <div className="border-b border-gray-200 p-4">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-gray-900">Chat History</h2>
            <button
              onClick={onClose}
              className="p-1 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
            >
              ✕
            </button>
          </div>

          <input
            type="text"
            placeholder="Search sessions..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />

          <div className="mt-3 flex items-center gap-2">
            <label className="flex items-center gap-2 text-sm text-gray-600">
              <input
                type="checkbox"
                checked={showArchived}
                onChange={(e) => setShowArchived(e.target.checked)}
                className="rounded"
              />
              Show archived
            </label>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          {isLoadingSessions ? (
            <div className="p-4 text-center text-gray-500">
              <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600" />
              <p className="mt-2 text-sm">Loading sessions...</p>
            </div>
          ) : error ? (
            <div className="p-4 bg-red-50 border border-red-200 text-red-800 text-sm">
              <p className="font-semibold">Error loading sessions</p>
              <p>{error}</p>
            </div>
          ) : sessions.length === 0 ? (
            <div className="p-4 text-center text-gray-500 text-sm">
              No sessions found. Start a new chat to create one!
            </div>
          ) : (
            <ul className="divide-y divide-gray-200">
              {sessions.map((session) => (
                <li
                  key={session.session_id}
                  className={`p-3 border-l-4 transition-colors ${
                    currentSessionId === session.session_id
                      ? 'border-l-blue-600 bg-blue-50'
                      : 'border-l-transparent hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <button
                      onClick={() => onSelectSession(session.session_id)}
                      className="flex-1 text-left min-w-0"
                    >
                      <p className="font-semibold text-sm text-gray-900 truncate">
                        {session.title || `Chat ${session.session_id.slice(0, 8)}`}
                      </p>
                      <p className="text-xs text-gray-500 mt-1 truncate">
                        {session.last_message || 'No messages'}
                      </p>
                      <p className="text-xs text-gray-400 mt-1">
                        {formatDistanceToNow(new Date(session.updated_at), { addSuffix: true })}
                      </p>
                    </button>

                    <div className="flex gap-1 flex-shrink-0">
                      <button
                        onClick={() => handleArchive(session)}
                        className="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-200 rounded"
                        title={session.is_archived ? 'Unarchive' : 'Archive'}
                      >
                        {session.is_archived ? '📂' : '📁'}
                      </button>
                      <button
                        onClick={() => handleDelete(session.session_id)}
                        disabled={deletingId === session.session_id}
                        className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-100 rounded disabled:opacity-50"
                        title="Delete"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
