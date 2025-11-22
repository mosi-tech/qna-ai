/**
 * SectionedInsightCard
 * 
 * Description: Multi-section card layout for organized analysis presentation with flexible content sections
 * Use Cases: Analysis reports, performance reviews, project summaries, research findings, audit reports
 * Data Format: Title, description, and array of sections with titles and content
 * 
 * @param title - Main card title
 * @param description - Optional description text
 * @param sections - Array of section objects with title and content
 * @param variant - Display variant for different layouts
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

import Container from './Container';
import { insightStyles, cn } from './shared/styles';

interface SectionData {
  title: string;
  content: string[];
  type?: 'default' | 'highlight' | 'warning' | 'info';
}

interface SectionedInsightCardProps {
  title: string;
  description?: string;
  sections: SectionData[];
  onApprove?: () => void;
  onDisapprove?: () => void;
}

export default function SectionedInsightCard({
  title,
  description,
  sections,
  onApprove,
  onDisapprove
}: SectionedInsightCardProps) {

  const getSectionClasses = (type: string = 'default') => {
    switch (type) {
      case 'highlight':
        return 'bg-sky-50 border-sky-200';
      case 'warning':
        return 'bg-amber-50 border-amber-200';
      case 'info':
        return 'bg-emerald-50 border-emerald-200';
      case 'default':
      default:
        return insightStyles.surface.secondary + ' border-slate-200';
    }
  };

  const getSectionTextClasses = (type: string = 'default') => {
    switch (type) {
      case 'highlight':
        return 'text-sky-800';
      case 'warning':
        return 'text-amber-800';
      case 'info':
        return 'text-emerald-800';
      case 'default':
      default:
        return insightStyles.text.primary;
    }
  };

  return (
    <Container title={title} onApprove={onApprove} onDisapprove={onDisapprove}>
      <div className="p-4">
        {description && (
          <p className={cn(insightStyles.text.secondary, 'text-sm leading-relaxed mb-4')}>
            {description}
          </p>
        )}

        {/* Sections Grid */}
      <div className={cn(
        'grid gap-4',
        sections.length <= 2 ? 'grid-cols-1 md:grid-cols-2' : 
        sections.length <= 4 ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-2' :
        'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
      )}>
        {sections.map((section, index) => (
          <div
            key={index}
            className={cn(
              'p-4 rounded-lg border',
              getSectionClasses(section.type)
            )}
          >
            <h3 className={cn(
              'text-sm font-semibold mb-3 uppercase tracking-wide',
              getSectionTextClasses(section.type)
            )}>
              {section.title}
            </h3>
            <div className="space-y-2">
              {section.content.map((item, itemIndex) => (
                <div
                  key={itemIndex}
                  className={cn(
                    'text-sm leading-relaxed',
                    getSectionTextClasses(section.type)
                  )}
                >
                  {item}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
      </div>
    </Container>
  );
}