import type { Metadata } from 'next'
import './globals.css'
import { Providers } from '@/lib/context'

export const metadata: Metadata = {
  title: 'Trading Analysis Platform',
  description: 'Interactive Q&A-driven financial analysis',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}