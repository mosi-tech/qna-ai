'use client';

interface ArchiveDialogProps {
  isOpen: boolean;
  sessionTitle: string;
  isArchived: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ArchiveDialog({
  isOpen,
  sessionTitle,
  isArchived,
  onConfirm,
  onCancel,
}: ArchiveDialogProps) {
  if (!isOpen) return null;

  const action = isArchived ? 'Unarchive' : 'Archive';
  const message = isArchived
    ? `This will move "${sessionTitle}" back to your active sessions.`
    : `This will move "${sessionTitle}" to your archived sessions.`;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/10" onClick={onCancel}>
      <div className="bg-white rounded-lg shadow-2xl max-w-sm w-full mx-4" onClick={(e) => e.stopPropagation()}>
        <div className="p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-2">{action} Session</h2>
          <p className="text-gray-600 text-sm">{message}</p>
        </div>
        <div className="border-t border-gray-200 px-6 py-4 flex gap-3 justify-end">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
          >
            {action}
          </button>
        </div>
      </div>
    </div>
  );
}
