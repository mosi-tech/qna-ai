'use client';

import { useEffect, useState, useRef } from 'react';
import { useSessionManager, SessionMetadata } from '@/lib/hooks/useSessionManager';
import ConfirmDialog from '@/components/ConfirmDialog';
import RenameDialog from '@/components/RenameDialog';
import ArchiveDialog from '@/components/ArchiveDialog';

const formatTimeAgo = (date: string | Date): string => {
  const now = new Date();
  const then = new Date(date);
  const seconds = Math.floor((now.getTime() - then.getTime()) / 1000);
  
  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  const weeks = Math.floor(days / 7);
  if (weeks < 4) return `${weeks}w ago`;
  return then.toLocaleDateString();
};

interface SessionListProps {
  userId: string;
  onSelectSession: (sessionId: string) => void;
  currentSessionId?: string;
  isOpen: boolean;
  onClose: () => void;
  hideHeader?: boolean;
}

interface OpenMenuState {
  sessionId: string | null;
}

export default function SessionList({
  userId,
  onSelectSession,
  currentSessionId,
  isOpen,
  onClose,
  hideHeader = false,
}: SessionListProps) {
  const { sessions, isLoadingSessions, error, listUserSessions, deleteSession, updateSession } =
    useSessionManager();
  const [searchQuery, setSearchQuery] = useState('');
  const [showArchived, setShowArchived] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [openMenu, setOpenMenu] = useState<OpenMenuState>({ sessionId: null });
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [sessionToDelete, setSessionToDelete] = useState<SessionMetadata | null>(null);
  const [showRenameDialog, setShowRenameDialog] = useState(false);
  const [sessionToRename, setSessionToRename] = useState<SessionMetadata | null>(null);
  const [showArchiveDialog, setShowArchiveDialog] = useState(false);
  const [sessionToArchive, setSessionToArchive] = useState<SessionMetadata | null>(null);
  const hasCalledRef = useRef(false);

  useEffect(() => {
    if (isOpen && userId && !hasCalledRef.current) {
      hasCalledRef.current = true;
      listUserSessions(userId, searchQuery || undefined, showArchived || undefined);
    } else if (!isOpen) {
      hasCalledRef.current = false;
    }
  }, [isOpen, userId]);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    if (userId && query.length >= 2) {
      listUserSessions(userId, query, showArchived || undefined);
    } else if (!query) {
      listUserSessions(userId, undefined, showArchived || undefined);
    }
  };

  const handleDeleteClick = (session: SessionMetadata) => {
    setSessionToDelete(session);
    setShowDeleteConfirm(true);
  };

  const handleDeleteConfirm = async () => {
    if (!sessionToDelete) return;

    try {
      setDeletingId(sessionToDelete.session_id);
      await deleteSession(sessionToDelete.session_id);
      setShowDeleteConfirm(false);
      setSessionToDelete(null);
      setOpenMenu({ sessionId: null });
    } catch (err) {
      console.error('Failed to delete session:', err);
    } finally {
      setDeletingId(null);
    }
  };

  const handleArchiveClick = (session: SessionMetadata) => {
    setSessionToArchive(session);
    setShowArchiveDialog(true);
    setOpenMenu({ sessionId: null });
  };

  const handleArchiveConfirm = async () => {
    if (!sessionToArchive) return;

    try {
      await updateSession(sessionToArchive.session_id, sessionToArchive.title, !sessionToArchive.is_archived);
      setShowArchiveDialog(false);
      setSessionToArchive(null);
    } catch (err) {
      console.error('Failed to archive session:', err);
    }
  };

  const handleRenameClick = (session: SessionMetadata) => {
    setSessionToRename(session);
    setShowRenameDialog(true);
    setOpenMenu({ sessionId: null });
  };

  const handleRenameConfirm = async (newTitle: string) => {
    if (!sessionToRename) return;

    try {
      await updateSession(sessionToRename.session_id, newTitle, undefined);
      setShowRenameDialog(false);
      setSessionToRename(null);
    } catch (err) {
      console.error('Failed to rename session:', err);
    }
  };

  if (!isOpen) return null;

  return (
    <div 
      className="w-full h-full flex flex-col bg-white"
    >
        {!hideHeader && (
          <div className="border-b border-gray-200 p-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-gray-900">Chat History</h2>
              <button
                onClick={onClose}
                className="p-1 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                title="Close chat history"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
            </div>

            <button
              onClick={() => onSelectSession('new')}
              className="w-full mb-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              + New Chat
            </button>

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
        )}
        {hideHeader && (
          <div className="border-b border-gray-200 p-4">
            <button
              onClick={() => onSelectSession('new')}
              className="w-full mb-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              + New Chat
            </button>

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
        )}

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
                        {formatTimeAgo(session.updated_at)}
                      </p>
                    </button>

                    <div className="relative flex-shrink-0">
                      <button
                        onClick={() => setOpenMenu({
                          sessionId: openMenu.sessionId === session.session_id ? null : session.session_id
                        })}
                        className="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-200 rounded"
                        title="More options"
                      >
                        ⋮
                      </button>
                      
                      {openMenu.sessionId === session.session_id && (
                        <div className="absolute right-0 mt-1 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
                          <button
                            onClick={() => handleRenameClick(session)}
                            className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                          >
                            <span>✏️</span>
                            Rename
                          </button>
                          <button
                            onClick={() => handleArchiveClick(session)}
                            className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                          >
                            <span>{session.is_archived ? '📂' : '📁'}</span>
                            {session.is_archived ? 'Unarchive' : 'Archive'}
                          </button>
                          <button
                            onClick={() => {
                              handleDeleteClick(session);
                              setOpenMenu({ sessionId: null });
                            }}
                            disabled={deletingId === session.session_id}
                            className="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2 disabled:opacity-50"
                          >
                            <span>🗑️</span>
                            Delete
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

      <ConfirmDialog
        isOpen={showDeleteConfirm}
        title="Delete Session"
        message={`Are you sure you want to delete "${sessionToDelete?.title || 'Untitled'}"? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        isDangerous={true}
        onConfirm={handleDeleteConfirm}
        onCancel={() => {
          setShowDeleteConfirm(false);
          setSessionToDelete(null);
        }}
      />

      <RenameDialog
        isOpen={showRenameDialog}
        currentTitle={sessionToRename?.title || ''}
        onConfirm={handleRenameConfirm}
        onCancel={() => {
          setShowRenameDialog(false);
          setSessionToRename(null);
        }}
      />

      <ArchiveDialog
        isOpen={showArchiveDialog}
        sessionTitle={sessionToArchive?.title || ''}
        isArchived={sessionToArchive?.is_archived || false}
        onConfirm={handleArchiveConfirm}
        onCancel={() => {
          setShowArchiveDialog(false);
          setSessionToArchive(null);
        }}
      />
    </div>
  );
}
