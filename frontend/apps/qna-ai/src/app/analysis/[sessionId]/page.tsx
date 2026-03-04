'use client';

import { use } from 'react';
import AnalysisWorkspace from '@/components/analysis/AnalysisWorkspace';

interface AnalysisPageProps {
  params: Promise<{ sessionId: string }>;
  searchParams: Promise<{ 
    question?: string; 
    results?: string; 
    analysisId?: string; 
    executionId?: string;
    messageId?: string; // Add messageId support to legacy route
  }>;
}

export default function AnalysisPage({ params, searchParams }: AnalysisPageProps) {
  const { sessionId } = use(params);
  const { question, results, analysisId, executionId, messageId } = use(searchParams);

  // Parse initial results if provided
  let initialResults = null;
  if (results) {
    try {
      initialResults = JSON.parse(decodeURIComponent(results));
    } catch (error) {
      console.error('Failed to parse initial results:', error);
    }
  }

  return (
    <AnalysisWorkspace
      sessionId={sessionId}
      messageId={messageId}
      initialQuestion={question ? decodeURIComponent(question) : undefined}
      initialResults={initialResults}
      analysisId={analysisId}
      executionId={executionId}
    />
  );
}