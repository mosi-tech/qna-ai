import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

interface Question {
  question: string;
  status?: 'pending' | 'validating' | 'valid' | 'invalid' | 'needs_refinement';
  validation_result?: any;
}

interface ValidationResult {
  status: 'VALID' | 'INVALID' | 'NEEDS_REFINEMENT';
  original_question: string;
  validated_question?: string;
  validation_notes: string;
  required_apis?: string[];
  data_requirements?: string[];
  rejection_reason?: string;
  missing_data?: string[];
  suggested_alternatives?: string[];
}

function ValidationPage() {
  const router = useRouter();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [validatedQuestions, setValidatedQuestions] = useState<any[]>([]);
  const [invalidQuestions, setInvalidQuestions] = useState<any[]>([]);
  const [isValidating, setIsValidating] = useState(false);
  const [currentValidatingIndex, setCurrentValidatingIndex] = useState(-1);
  const [ollamaModel, setOllamaModel] = useState('gpt-oss:20b');
  const [ollamaUrl, setOllamaUrl] = useState('http://localhost:11434');
  const [validationPrompt, setValidationPrompt] = useState('');
  const [apiSpecs, setApiSpecs] = useState('');
  const [stats, setStats] = useState({ valid: 0, invalid: 0, needsRefinement: 0, pending: 0 });
  const [connectionStatus, setConnectionStatus] = useState<'checking' | 'connected' | 'error'>('checking');
  const [lastError, setLastError] = useState<string>('');

  // Load data on component mount
  useEffect(() => {
    loadQuestions();
    loadValidationPrompt();
    loadAPISpecs();
    loadValidatedQuestions();
    loadInvalidQuestions();
    checkOllamaConnection();
  }, []);

  // Check Ollama connection when URL/model changes
  useEffect(() => {
    checkOllamaConnection();
  }, [ollamaUrl, ollamaModel]);

  // Update stats whenever questions change
  useEffect(() => {
    const pending = questions.filter(q => !q.status || q.status === 'pending').length;
    const validating = questions.filter(q => q.status === 'validating').length;
    setStats({
      valid: validatedQuestions.length,
      invalid: invalidQuestions.length,
      needsRefinement: validatedQuestions.filter(q => q.status === 'NEEDS_REFINEMENT').length,
      pending: pending + validating
    });
  }, [questions, validatedQuestions, invalidQuestions]);

  const loadQuestions = async () => {
    try {
      const response = await fetch('/api/questions');
      const data = await response.json();
      setQuestions(data.questions?.map((q: string) => ({ question: q, status: 'pending' })) || []);
    } catch (error) {
      console.error('Error loading questions:', error);
    }
  };

  const loadValidationPrompt = async () => {
    try {
      const response = await fetch('/api/validation-assets');
      const data = await response.json();
      if (data.validationPrompt) setValidationPrompt(data.validationPrompt);
    } catch (error) {
      console.error('Error loading validation prompt:', error);
    }
  };

  const loadAPISpecs = async () => {
    try {
      // Load simplified API specs via API to avoid 404s on static fetch
      const response = await fetch('/api/validation-assets');
      const data = await response.json();
      if (data.specs) setApiSpecs(JSON.stringify(data.specs, null, 2));
    } catch (error) {
      console.error('Error loading API specs:', error);
    }
  };

  const loadValidatedQuestions = async () => {
    try {
      const response = await fetch('/api/valid-questions');
      const data = await response.json();
      setValidatedQuestions(data.valid_questions || []);
    } catch (error) {
      console.error('Error loading validated questions:', error);
    }
  };

  const loadInvalidQuestions = async () => {
    try {
      const response = await fetch('/api/invalid-questions');
      const data = await response.json();
      setInvalidQuestions(data.invalid_questions || []);
    } catch (error) {
      console.error('Error loading invalid questions:', error);
    }
  };

  const checkOllamaConnection = async () => {
    setConnectionStatus('checking');
    try {
      const response = await fetch(`${ollamaUrl}/api/tags`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (response.ok) {
        const data = await response.json();
        const modelExists = data.models?.some((m: any) => m.name.includes(ollamaModel));
        if (modelExists) {
          setConnectionStatus('connected');
          setLastError('');
        } else {
          setConnectionStatus('error');
          setLastError(`Model "${ollamaModel}" not found. Available models: ${data.models?.map((m: any) => m.name).join(', ') || 'none'}`);
        }
      } else {
        setConnectionStatus('error');
        setLastError(`Failed to connect to Ollama: ${response.statusText}`);
      }
    } catch (error) {
      setConnectionStatus('error');
      setLastError(`Connection error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const validateWithOllama = async (question: string): Promise<ValidationResult> => {
    const systemPrompt = `You are a financial API validation expert. Validate questions against available APIs and respond in JSON format only.

${validationPrompt}

## API Specifications:
${apiSpecs}`;

    // Debug: Log the full system prompt to the console
    try {
      console.log('[Validation] System prompt length:', systemPrompt.length);
      console.log('[Validation] System prompt start ->');
      console.log(systemPrompt);
      console.log('<- [Validation] System prompt end');
    } catch (_) {
      // no-op
    }

    const userPrompt = `Validate this financial question: "${question}"

Respond with a JSON object in this exact format:
{
  "status": "VALID" | "INVALID" | "NEEDS_REFINEMENT",
  "original_question": "${question}",
  "validated_question": "refined version if needed",
  "validation_notes": "explanation of validation result",
  "required_apis": ["api1", "api2"],
  "data_requirements": ["requirement1", "requirement2"],
  "rejection_reason": "reason if invalid",
  "missing_data": ["missing1", "missing2"],
  "suggested_alternatives": ["alternative1", "alternative2"]
}

Only respond with valid JSON, no other text.`;

    const response = await fetch(`${ollamaUrl}/v1/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ollama'
      },
      body: JSON.stringify({
        model: ollamaModel,
        messages: [
          {
            role: 'system',
            content: systemPrompt
          },
          {
            role: 'user',
            content: userPrompt
          }
        ],
        temperature: 0.1,
        max_tokens: 2000
      }),
    });

    if (!response.ok) {
      throw new Error(`Ollama API error: ${response.statusText}`);
    }

    const data = await response.json();
    
    if (!data.choices || !data.choices[0] || !data.choices[0].message) {
      throw new Error('Invalid response format from Ollama');
    }

    const content = data.choices[0].message.content;

    try {
      return JSON.parse(content);
    } catch (error) {
      console.error('Failed to parse JSON:', content);
      throw new Error('Invalid JSON in Ollama response');
    }
  };

  const validateSingleQuestion = async (index: number) => {
    if (index >= questions.length) return;

    const question = questions[index];
    setCurrentValidatingIndex(index);
    
    // Update question status to validating
    setQuestions(prev => prev.map((q, i) => 
      i === index ? { ...q, status: 'validating' as const } : q
    ));

    try {
      const result = await validateWithOllama(question.question);
      
      // Update question with result
      setQuestions(prev => prev.map((q, i) => 
        i === index ? { 
          ...q, 
          status: result.status.toLowerCase() as any,
          validation_result: result 
        } : q
      ));

      // Add to appropriate list and save
      if (result.status === 'VALID' || result.status === 'NEEDS_REFINEMENT') {
        const validQuestion = {
          question: result.validated_question || result.original_question,
          status: result.status,
          original_question: result.original_question,
          validation_notes: result.validation_notes,
          required_apis: result.required_apis || [],
          data_requirements: result.data_requirements || [],
          validation_date: new Date().toISOString().split('T')[0],
          implementation_ready: true
        };
        
        await fetch('/api/valid-questions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(validQuestion)
        });
        
        setValidatedQuestions(prev => [...prev, validQuestion]);
      } else {
        const invalidQuestion = {
          question: result.original_question,
          rejection_reason: result.rejection_reason,
          missing_data: result.missing_data || [],
          suggested_alternatives: result.suggested_alternatives || [],
          validation_date: new Date().toISOString().split('T')[0],
          category: 'api_limitation'
        };
        
        await fetch('/api/invalid-questions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(invalidQuestion)
        });
        
        setInvalidQuestions(prev => [...prev, invalidQuestion]);
      }

      // Remove from generated questions
      await fetch('/api/questions', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question.question })
      });

    } catch (error) {
      console.error(`Error validating question ${index}:`, error);
      setQuestions(prev => prev.map((q, i) => 
        i === index ? { ...q, status: 'pending' as const } : q
      ));
    }
  };

  const validateAllQuestions = async () => {
    setIsValidating(true);
    const pendingQuestions = questions.filter(q => !q.status || q.status === 'pending');
    
    for (let i = 0; i < questions.length; i++) {
      if (questions[i].status === 'pending' || !questions[i].status) {
        await validateSingleQuestion(i);
        // Small delay to prevent overwhelming Ollama
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
    
    setIsValidating(false);
    setCurrentValidatingIndex(-1);
    
    // Reload questions after validation
    await loadQuestions();
  };

  const stopValidation = () => {
    setIsValidating(false);
    setCurrentValidatingIndex(-1);
  };

  return (
    <div style={{ height: '100vh', display: 'flex', fontFamily: 'Inter, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell' }}>
      {/* Left Panel */}
      <div style={{ width: '60%', borderRight: '1px solid #e5e7eb', display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <div style={{ padding: 16, borderBottom: '1px solid #e5e7eb' }}>
          <button
            onClick={() => router.push('/')}
            style={{ 
              marginBottom: 12, 
              padding: '8px 12px', 
              background: '#6b7280', 
              color: 'white', 
              border: 0, 
              borderRadius: 6, 
              cursor: 'pointer',
              fontSize: 14
            }}
          >
            ← Back to Main
          </button>
          <h1 style={{ fontSize: 24, fontWeight: 700, margin: 0, marginBottom: 4 }}>Question Validation</h1>
          <p style={{ fontSize: 14, color: '#6b7280', margin: 0 }}>
            Automated validation using local Ollama LLM
          </p>
        </div>

        {/* Configuration */}
        <div style={{ padding: 16, borderBottom: '1px solid #e5e7eb' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 12 }}>
            <div>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 500, marginBottom: 4 }}>
                Ollama URL
              </label>
              <input
                type="text"
                value={ollamaUrl}
                onChange={(e) => setOllamaUrl(e.target.value)}
                style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 14 }}
                placeholder="http://localhost:11434"
              />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 500, marginBottom: 4 }}>
                Model
              </label>
              <input
                type="text"
                value={ollamaModel}
                onChange={(e) => setOllamaModel(e.target.value)}
                style={{ width: '100%', padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: 4, fontSize: 14 }}
                placeholder="llama3.1"
              />
            </div>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
            <button
              onClick={checkOllamaConnection}
              disabled={connectionStatus === 'checking'}
              style={{ 
                padding: '6px 12px', 
                background: '#4b5563', 
                color: 'white', 
                border: 0, 
                borderRadius: 4, 
                cursor: 'pointer',
                fontSize: 12,
                opacity: connectionStatus === 'checking' ? 0.5 : 1
              }}
            >
              {connectionStatus === 'checking' ? 'Testing...' : 'Test Connection'}
            </button>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <div style={{ 
                width: 8, 
                height: 8, 
                borderRadius: '50%', 
                background: connectionStatus === 'connected' ? '#10b981' : 
                           connectionStatus === 'error' ? '#ef4444' : '#f59e0b' 
              }}></div>
              <span style={{ fontSize: 12, color: '#374151' }}>
                {connectionStatus === 'connected' ? 'Connected' : 
                 connectionStatus === 'error' ? 'Connection failed' : 'Connecting...'}
              </span>
            </div>
          </div>
          
          {lastError && (
            <div style={{ padding: 8, background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 4, marginBottom: 12 }}>
              <p style={{ fontSize: 12, color: '#dc2626', margin: 0 }}>{lastError}</p>
            </div>
          )}

          {/* Stats */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 12 }}>
            <div style={{ textAlign: 'center', padding: 8, background: '#eff6ff', borderRadius: 4 }}>
              <div style={{ fontSize: 18, fontWeight: 700, color: '#2563eb' }}>{stats.pending}</div>
              <div style={{ fontSize: 10, color: '#1d4ed8' }}>Pending</div>
            </div>
            <div style={{ textAlign: 'center', padding: 8, background: '#f0fdf4', borderRadius: 4 }}>
              <div style={{ fontSize: 18, fontWeight: 700, color: '#059669' }}>{stats.valid}</div>
              <div style={{ fontSize: 10, color: '#047857' }}>Valid</div>
            </div>
            <div style={{ textAlign: 'center', padding: 8, background: '#fffbeb', borderRadius: 4 }}>
              <div style={{ fontSize: 18, fontWeight: 700, color: '#d97706' }}>{stats.needsRefinement}</div>
              <div style={{ fontSize: 10, color: '#92400e' }}>Needs Fix</div>
            </div>
            <div style={{ textAlign: 'center', padding: 8, background: '#fef2f2', borderRadius: 4 }}>
              <div style={{ fontSize: 18, fontWeight: 700, color: '#dc2626' }}>{stats.invalid}</div>
              <div style={{ fontSize: 10, color: '#991b1b' }}>Invalid</div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 8 }}>
            <button
              onClick={validateAllQuestions}
              disabled={isValidating || questions.length === 0 || connectionStatus !== 'connected'}
              style={{ 
                padding: '8px 16px', 
                background: isValidating || questions.length === 0 || connectionStatus !== 'connected' ? '#9ca3af' : '#2563eb', 
                color: 'white', 
                border: 0, 
                borderRadius: 4, 
                cursor: isValidating || questions.length === 0 || connectionStatus !== 'connected' ? 'not-allowed' : 'pointer',
                fontSize: 14,
                fontWeight: 500
              }}
            >
              {isValidating ? 'Validating...' : 'Validate All'}
            </button>
            {isValidating && (
              <button
                onClick={stopValidation}
                style={{ 
                  padding: '8px 16px', 
                  background: '#dc2626', 
                  color: 'white', 
                  border: 0, 
                  borderRadius: 4, 
                  cursor: 'pointer',
                  fontSize: 14
                }}
              >
                Stop
              </button>
            )}
            <button
              onClick={loadQuestions}
              style={{ 
                padding: '8px 16px', 
                background: '#4b5563', 
                color: 'white', 
                border: 0, 
                borderRadius: 4, 
                cursor: 'pointer',
                fontSize: 14
              }}
            >
              Reload
            </button>
          </div>
          
          {isValidating && currentValidatingIndex >= 0 && (
            <div style={{ marginTop: 12, padding: 8, background: '#eff6ff', borderRadius: 4 }}>
              <div style={{ fontSize: 12, color: '#1e40af', marginBottom: 4 }}>
                Validating {currentValidatingIndex + 1} of {questions.length} ({Math.round(((currentValidatingIndex + 1) / questions.length) * 100)}%)
              </div>
              <div style={{ width: '100%', height: 4, background: '#bfdbfe', borderRadius: 2 }}>
                <div 
                  style={{ 
                    width: `${((currentValidatingIndex + 1) / questions.length) * 100}%`, 
                    height: '100%', 
                    background: '#2563eb', 
                    borderRadius: 2,
                    transition: 'width 0.3s ease'
                  }}
                ></div>
              </div>
            </div>
          )}
        </div>

        {/* Questions List */}
        <div style={{ flex: 1, padding: 16, overflow: 'auto' }}>
          <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 12, margin: 0 }}>
            Questions ({questions.filter(q => !q.status || q.status === 'pending' || q.status === 'validating').length} pending)
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {questions.length === 0 ? (
              <div style={{ textAlign: 'center', padding: 32, color: '#6b7280' }}>
                <div style={{ marginBottom: 8 }}>No questions to validate</div>
                <div style={{ fontSize: 12 }}>Load questions from generated_questions.json</div>
              </div>
            ) : questions
              .filter(q => !q.status || q.status === 'pending' || q.status === 'validating').length === 0 ? (
              <div style={{ textAlign: 'center', padding: 32, color: '#059669' }}>
                <div style={{ marginBottom: 8 }}>All questions validated!</div>
                <div style={{ fontSize: 12, color: '#6b7280' }}>Check results in the right panel</div>
              </div>
            ) : (
              questions
                .filter(q => !q.status || q.status === 'pending' || q.status === 'validating')
                .map((question, index) => (
                <div
                  key={index}
                  style={{ 
                    padding: 12, 
                    border: `1px solid ${question.status === 'validating' ? '#93c5fd' : '#e5e7eb'}`, 
                    borderRadius: 6,
                    background: question.status === 'validating' ? '#eff6ff' : '#f9fafb',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-start',
                    gap: 12
                  }}
                >
                  <div style={{ flex: 1, fontSize: 14, lineHeight: 1.4, color: '#374151' }}>
                    {question.question}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    {question.status === 'validating' && (
                      <div style={{ fontSize: 12, color: '#2563eb' }}>Validating...</div>
                    )}
                    <button
                      onClick={() => {
                        const questionIndex = questions.findIndex(q => q.question === question.question);
                        validateSingleQuestion(questionIndex);
                      }}
                      disabled={isValidating || question.status === 'validating' || connectionStatus !== 'connected'}
                      style={{ 
                        padding: '4px 8px', 
                        background: isValidating || question.status === 'validating' || connectionStatus !== 'connected' ? '#9ca3af' : '#2563eb',
                        color: 'white', 
                        border: 0, 
                        borderRadius: 4, 
                        cursor: isValidating || question.status === 'validating' || connectionStatus !== 'connected' ? 'not-allowed' : 'pointer',
                        fontSize: 12
                      }}
                    >
                      Validate
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Right Panel - Validation Results */}
      <div style={{ width: '40%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: 16, borderBottom: '1px solid #e5e7eb' }}>
          <h2 style={{ fontSize: 18, fontWeight: 600, margin: 0 }}>Validation Results</h2>
        </div>
        
        <div style={{ flex: 1, overflow: 'auto' }}>
          {/* Valid Questions */}
          <div style={{ padding: 16, borderBottom: '1px solid #e5e7eb' }}>
            <h3 style={{ fontSize: 14, fontWeight: 600, color: '#059669', marginBottom: 12, margin: 0 }}>
              ✓ Valid Questions ({validatedQuestions.length})
            </h3>
            <div style={{ maxHeight: 200, overflow: 'auto' }}>
              {validatedQuestions.length === 0 ? (
                <div style={{ textAlign: 'center', padding: 16, color: '#6b7280', fontSize: 12 }}>
                  No valid questions yet
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {validatedQuestions.slice(-5).map((question, index) => (
                    <div key={index} style={{ padding: 8, background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: 4 }}>
                      <div style={{ fontSize: 12, fontWeight: 500, color: '#374151', marginBottom: 4 }}>
                        {question.question}
                      </div>
                      <div style={{ fontSize: 10, color: '#059669', marginBottom: 4 }}>
                        {question.validation_notes}
                      </div>
                      {question.required_apis && question.required_apis.length > 0 && (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                          {question.required_apis.map((api: string, apiIndex: number) => (
                            <span key={apiIndex} style={{ 
                              fontSize: 9, 
                              background: '#dbeafe', 
                              color: '#1d4ed8', 
                              padding: '2px 6px', 
                              borderRadius: 10 
                            }}>
                              {api}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Invalid Questions */}
          <div style={{ padding: 16 }}>
            <h3 style={{ fontSize: 14, fontWeight: 600, color: '#dc2626', marginBottom: 12, margin: 0 }}>
              ✗ Invalid Questions ({invalidQuestions.length})
            </h3>
            <div style={{ maxHeight: 200, overflow: 'auto' }}>
              {invalidQuestions.length === 0 ? (
                <div style={{ textAlign: 'center', padding: 16, color: '#6b7280', fontSize: 12 }}>
                  No invalid questions yet
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {invalidQuestions.slice(-5).map((question, index) => (
                    <div key={index} style={{ padding: 8, background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 4 }}>
                      <div style={{ fontSize: 12, fontWeight: 500, color: '#374151', marginBottom: 4 }}>
                        {question.question}
                      </div>
                      <div style={{ fontSize: 10, color: '#dc2626', marginBottom: 4 }}>
                        {question.rejection_reason}
                      </div>
                      {question.suggested_alternatives && question.suggested_alternatives.length > 0 && (
                        <div>
                          <div style={{ fontSize: 9, color: '#6b7280', marginBottom: 2 }}>Alternatives:</div>
                          {question.suggested_alternatives.slice(0, 2).map((alt: string, altIndex: number) => (
                            <div key={altIndex} style={{ 
                              fontSize: 9, 
                              color: '#6b7280', 
                              background: '#f3f4f6', 
                              padding: '2px 4px', 
                              borderRadius: 2,
                              marginBottom: 2
                            }}>
                              {alt}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ValidationPage;
