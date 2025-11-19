/**
 * NarrativeParagraph
 * 
 * Description: Freeform explanation text with proper formatting for analysis narratives
 * Use Cases: Analysis explanations, insights, commentary, conclusions
 * Data Format: String or array of strings for multiple paragraphs
 * 
 * @param content - Text content (string or string array)
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

interface NarrativeParagraphProps {
  content: string | string[];
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function NarrativeParagraph({
  content,
  onApprove,
  onDisapprove,
  variant = 'default'
}: NarrativeParagraphProps) {

  const paragraphs = Array.isArray(content) ? content : [content];

  return (
    <div className="bg-white  rounded-lg p-6">
      <div className="space-y-4">
        {paragraphs.map((paragraph, index) => (
          <p key={index} className="text-gray-800 leading-relaxed">
            {paragraph}
          </p>
        ))}
      </div>

      {(onApprove || onDisapprove) && (
        <div className="flex gap-2 mt-6 pt-4 border-t border-gray-100">
          {onApprove && (
            <button
              onClick={onApprove}
              className="px-4 py-2 bg-green-50 text-green-700 rounded-md hover:bg-green-100 transition-colors text-sm font-medium"
            >
              Approve
            </button>
          )}
          {onDisapprove && (
            <button
              onClick={onDisapprove}
              className="px-4 py-2 bg-red-50 text-red-700 rounded-md hover:bg-red-100 transition-colors text-sm font-medium"
            >
              Disapprove
            </button>
          )}
        </div>
      )}
    </div>
  );
}