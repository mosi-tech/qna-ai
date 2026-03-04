/**
 * Basic markdown parsing utility
 * Converts common markdown elements to HTML with Tailwind classes
 */

export const renderMarkdown = (text: string): string => {
  if (!text) return '';
  
  let html = text
    // Headers
    .replace(/^### (.*$)/gim, '<h3 class="text-lg font-semibold text-gray-900 mt-4 mb-2">$1</h3>')
    .replace(/^## (.*$)/gim, '<h2 class="text-xl font-bold text-gray-900 mt-6 mb-3">$1</h2>')
    .replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold text-gray-900 mt-6 mb-4">$1</h1>')
    // Bold and italic
    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
    // Code blocks
    .replace(/`([^`]+)`/g, '<code class="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono">$1</code>')
    // Lists - convert to proper HTML lists without custom bullets
    .replace(/^• (.*$)/gim, '<li class="ml-4 mb-1 list-none">• $1</li>')  // Keep existing bullet, disable list style
    .replace(/^\* (.*$)/gim, '<li class="ml-4 mb-1 list-disc">$1</li>')     // Use CSS disc bullet
    .replace(/^- (.*$)/gim, '<li class="ml-4 mb-1 list-disc">$1</li>')      // Use CSS disc bullet
    .replace(/^\d+\. (.*$)/gim, '<li class="ml-4 mb-1 list-decimal">$1</li>') // Use CSS numbering
    // Line breaks
    .replace(/\n\n/g, '</p><p class="mb-3">')
    .replace(/\n/g, '<br/>');

  // Wrap in paragraph tags if not already wrapped
  if (!html.includes('<p>') && !html.includes('<h1>') && !html.includes('<h2>') && !html.includes('<h3>')) {
    html = `<p class="mb-3">${html}</p>`;
  }

  return html;
};