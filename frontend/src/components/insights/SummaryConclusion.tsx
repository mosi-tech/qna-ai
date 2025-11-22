'use client';

import Container from './Container';

interface SummaryConclusionProps {
  title?: string;
  keyFindings: string[];
  conclusion: string;
  nextSteps?: string[];
  confidence?: 'high' | 'medium' | 'low';
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function SummaryConclusion({
  title = "Summary & Conclusion", 
  keyFindings, 
  conclusion, 
  nextSteps, 
  confidence, 
  onApprove, 
  onDisapprove
}: SummaryConclusionProps) {

  return (
    <Container title={title} onApprove={onApprove} onDisapprove={onDisapprove}>
      <div className="p-4 space-y-4">
        <div>
          <h4 className="text-md font-medium text-gray-900 mb-2">Key Findings</h4>
          <ul className="space-y-2">
            {keyFindings.map((finding, index) => (
              <li key={index} className="flex items-start">
                <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                <span className="text-sm text-gray-700">{finding}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="text-md font-medium text-blue-900 mb-2">Conclusion</h4>
          <p className="text-sm text-blue-800 leading-relaxed">{conclusion}</p>
          {confidence && (
            <div className="mt-2">
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${confidence === 'high' ? 'bg-green-100 text-green-800' :
                  confidence === 'low' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                }`}>
                {confidence} confidence
              </span>
            </div>
          )}
        </div>

        {nextSteps && nextSteps.length > 0 && (
          <div>
            <h4 className="text-md font-medium text-gray-900 mb-2">Next Steps</h4>
            <ol className="space-y-2">
              {nextSteps.map((step, index) => (
                <li key={index} className="flex items-start">
                  <span className="inline-flex items-center justify-center w-5 h-5 bg-gray-200 text-gray-600 text-xs font-semibold rounded-full mr-3 mt-0.5 flex-shrink-0">
                    {index + 1}
                  </span>
                  <span className="text-sm text-gray-700">{step}</span>
                </li>
              ))}
            </ol>
          </div>
        )}
      </div>
    </Container>
  );
}
