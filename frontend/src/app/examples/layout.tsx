import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Financial Components Library - Examples',
  description: 'Live examples of financial analysis components for LLM-generated visualizations',
}

// This layout bypasses the auth providers for public access
export default function ExamplesLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <>
      {children}
    </>
  )
}