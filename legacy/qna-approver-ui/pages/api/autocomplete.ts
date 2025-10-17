import type { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs/promises';
import path from 'path';

type Suggestion = {
  question: string;
  reason?: string;
  required_apis?: string[];
};

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  const inputQuestion = (req.body?.question || req.body?.input || '').toString();
  if (!inputQuestion) {
    return res.status(400).json({ error: 'Missing "question" in request body' });
  }

  try {
    const root = process.cwd();
    const [promptBuf, alpacaMarketBuf, alpacaTradingBuf, eodhdBuf] = await Promise.all([
      fs.readFile(path.join(root, 'question-validator-prompt.txt'), 'utf8'),
      fs.readFile(path.join(root, 'alpaca-marketdata-simple.json'), 'utf8'),
      fs.readFile(path.join(root, 'alpaca-trading-simple.json'), 'utf8'),
      fs.readFile(path.join(root, 'eodhd-simple.json'), 'utf8'),
    ]);

    const specs = {
      'Alpaca Market Data API': JSON.parse(alpacaMarketBuf),
      'Alpaca Trading API': JSON.parse(alpacaTradingBuf),
      'EODHD API': JSON.parse(eodhdBuf),
    };

    const apiSpecs = JSON.stringify(specs, null, 2);

    const systemPrompt = `You are a financial API validation and suggestion assistant. 
Use the validation guidance and API specifications to determine what is feasible. 
Given a user question, propose 5 top alternative questions that are likely answerable using ONLY the available APIs.
Return strictly JSON, no extra text.

${promptBuf}

## API Specifications:
${apiSpecs}`;

    const userPrompt = `User question: "${inputQuestion}"

Produce exactly this JSON schema:
{
  "suggestions": [
    {
      "question": "string",
      "reason": "why this is answerable with available APIs",
      "required_apis": ["api1", "api2"]
    }
  ]
}
Rules:
- Provide exactly 5 suggestions.
- Avoid duplicates; be specific and practically queryable.
- Ensure each suggestion is feasible using the listed APIs.
- No prose outside the JSON.`;

    const ollamaUrl = process.env.OLLAMA_URL || 'http://localhost:11434';
    const ollamaModel = process.env.OLLAMA_MODEL || 'gpt-oss:20b';

    const response = await fetch(`${ollamaUrl}/v1/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ollama',
      },
      body: JSON.stringify({
        model: ollamaModel,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt },
        ],
        temperature: 0.3,
        max_tokens: 1200,
      }),
    });

    if (!response.ok) {
      const text = await response.text();
      return res.status(response.status).json({ error: `Ollama error: ${response.statusText}`, details: text });
    }

    const data = await response.json();
    const content = data?.choices?.[0]?.message?.content;
    if (!content) {
      return res.status(502).json({ error: 'Invalid response format from Ollama' });
    }

    try {
      const parsed = JSON.parse(content) as { suggestions: Suggestion[] };
      if (!Array.isArray(parsed?.suggestions)) {
        throw new Error('Missing suggestions array');
      }
      return res.status(200).json(parsed);
    } catch (e: any) {
      return res.status(502).json({ error: 'Failed to parse JSON from Ollama', content });
    }
  } catch (error: any) {
    return res.status(500).json({ error: error?.message || 'Unknown server error' });
  }
}

