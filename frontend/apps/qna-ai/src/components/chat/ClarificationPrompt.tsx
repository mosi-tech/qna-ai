'use client';

interface ClarificationPromptProps {
  originalQuery: string;
  expandedQuery: string;
  message: string;
  suggestion?: string;
  confidence?: number;
  onConfirm: () => void;
  onReject: () => void;
  onProvideDetails: (details: string) => void;
  isLoading?: boolean;
  isPending?: boolean;
}

export default function ClarificationPrompt({
  originalQuery,
  expandedQuery,
  message,
  suggestion,
  confidence,
  onConfirm,
  onReject,
  onProvideDetails,
  isLoading = false,
  isPending = false,
}: ClarificationPromptProps) {
  return (
    <div className="flex gap-3 w-full">
      <div className="w-8 h-8 rounded-full bg-yellow-100 flex items-center justify-center flex-shrink-0">
        <span className="text-yellow-600 text-sm">{isPending ? '⏳' : '?'}</span>
      </div>
      <div className={`${isPending ? 'bg-gray-50 border-gray-200' : 'bg-yellow-50 border-yellow-200'} border rounded-lg p-4 max-w-2xl flex-1`}>
        <p className={`text-sm ${isPending ? 'text-gray-600' : 'text-gray-800'} mb-3 font-medium`}>{message}</p>
        
        {suggestion && !isPending && (
          <p className="text-sm text-gray-700 mb-3">{suggestion}</p>
        )}

        {confidence !== undefined && !isPending && (
          <p className="text-xs text-gray-500 mb-3">
            Confidence: {Math.round(confidence * 100)}%
          </p>
        )}

        <div className={`${isPending ? 'bg-gray-100 border-gray-200' : 'bg-white border-yellow-100'} border rounded p-3 mb-4`}>
          <p className="text-xs text-gray-500 mb-1">Interpreted as:</p>
          <p className="text-sm text-gray-700">{expandedQuery}</p>
        </div>

        {isPending && isLoading ? (
          <p className="text-xs text-gray-500 italic">Waiting for response processing...</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            <button
              onClick={onConfirm}
              disabled={isLoading}
              className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 disabled:opacity-50"
            >
              Yes, proceed
            </button>
            
            <p className="text-xs text-gray-600 self-center">
              If not, please clarify in the chat box below
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
