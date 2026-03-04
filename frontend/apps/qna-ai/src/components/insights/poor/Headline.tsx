/**
 * Headline
 * 
 * Description: Large title for analysis sections and reports
 * Use Cases: Report titles, section headers, main findings
 * Data Format: Simple text string
 * 
 * @param text - The headline text to display
 * @param level - Header level (1-3) for semantic hierarchy
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

import { insightStyles, cn } from './shared/styles';

interface HeadlineProps {
  text: string;
  level?: 1 | 2 | 3;
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function Headline({ 
  text, 
  level = 1, 
  onApprove, 
  onDisapprove,
  variant = 'default' 
}: HeadlineProps) {
  
  const getHeadingClasses = () => {
    switch (level) {
      case 1:
        return insightStyles.typography.h1;
      case 2:
        return insightStyles.typography.h2;
      case 3:
        return insightStyles.typography.h3;
      default:
        return insightStyles.typography.h1;
    }
  };

  const HeadingTag = `h${level}` as keyof JSX.IntrinsicElements;

  return (
    <div className={cn(insightStyles.card.base, insightStyles.spacing.component)}>
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4">
        <HeadingTag className={cn(getHeadingClasses(), "flex-1")}>
          {text}
        </HeadingTag>
        
        {(onApprove || onDisapprove) && (
          <div className="flex gap-2 flex-shrink-0">
            {onApprove && (
              <button
                onClick={onApprove}
                className={insightStyles.button.approve.compact}
              >
                ✓
              </button>
            )}
            {onDisapprove && (
              <button
                onClick={onDisapprove}
                className={insightStyles.button.disapprove.compact}
              >
                ✗
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}