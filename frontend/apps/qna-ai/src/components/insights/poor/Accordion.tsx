/**
 * Accordion
 * 
 * Description: Collapsible content sections for detailed information
 * Use Cases: Detailed analysis, optional content, expandable sections
 * Data Format: Array of sections with title and content
 * 
 * @param sections - Array of accordion sections
 * @param allowMultiple - Allow multiple sections to be open
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

import { ReactNode, useState } from 'react';

interface AccordionSection {
  id: string;
  title: string;
  content: ReactNode;
}

interface AccordionProps {
  sections: AccordionSection[];
  allowMultiple?: boolean;
  onApprove?: () => void;
  onDisapprove?: () => void;
  variant?: 'default' | 'compact' | 'detailed';
}

export default function Accordion({
  sections,
  allowMultiple = false,
  onApprove,
  onDisapprove,
  variant = 'default'
}: AccordionProps) {

  const [openSections, setOpenSections] = useState<string[]>([]);

  const toggleSection = (sectionId: string) => {
    if (allowMultiple) {
      setOpenSections(prev =>
        prev.includes(sectionId)
          ? prev.filter(id => id !== sectionId)
          : [...prev, sectionId]
      );
    } else {
      setOpenSections(prev =>
        prev.includes(sectionId) ? [] : [sectionId]
      );
    }
  };

  const isOpen = (sectionId: string) => openSections.includes(sectionId);

  return (
    <div className="bg-white  rounded-lg overflow-hidden">
      <div className="divide-y divide-gray-200">
        {sections.map((section, index) => (
          <div key={section.id}>
            <button
              onClick={() => toggleSection(section.id)}
              className="w-full px-6 py-4 text-left hover:bg-gray-50 transition-colors focus:outline-none focus:bg-gray-50"
            >
              <div className="flex justify-between items-center">
                <h3 className="text-md font-medium text-gray-900">
                  {section.title}
                </h3>
                <span className={`transform transition-transform ${isOpen(section.id) ? 'rotate-180' : ''
                  }`}>
                  ▼
                </span>
              </div>
            </button>

            {isOpen(section.id) && (
              <div className="px-6 pb-4 border-t border-gray-100 bg-gray-25">
                <div className="pt-4">
                  {section.content}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {(onApprove || onDisapprove) && (
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex gap-2">
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