'use client';

import { use } from 'react';
import AnalysisWorkspace from '@/components/analysis/AnalysisWorkspace';

interface AnalysisPageProps {
  params: Promise<{ 
    sessionId: string; 
    messageId: string; 
    analysisId: string; 
  }>;
  searchParams: Promise<{ 
    question?: string; 
    results?: string; 
    executionId?: string; 
  }>;
}

export default function AnalysisPage({ params, searchParams }: AnalysisPageProps) {
  const { sessionId, messageId, analysisId } = use(params);
  const { question, results, executionId } = use(searchParams);

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
      analysisId={analysisId}
      initialQuestion={question ? decodeURIComponent(question) : undefined}
      initialResults={initialResults}
      executionId={executionId}
    />
  );
}