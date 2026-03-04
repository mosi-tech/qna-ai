/**
 * Examples Layout - Bypasses authentication for demo purposes
 */

import { ReactNode } from 'react';

export default function ExamplesLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <div className="examples-layout">
      {/* No auth providers - examples are public */}
      {children}
    </div>
  );
}