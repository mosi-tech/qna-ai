import type { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs/promises';
import path from 'path';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const root = process.cwd();

    // Load main validation assets
    const [promptBuf, alpacaMarketBuf, alpacaTradingBuf, eodhdBuf] = await Promise.all([
      fs.readFile(path.join(root, 'question-validator-prompt.txt'), 'utf8').catch(() => ''),
      fs.readFile(path.join(root, 'alpaca-marketdata-simple.json'), 'utf8').catch(() => '{}'),
      fs.readFile(path.join(root, 'alpaca-trading-simple.json'), 'utf8').catch(() => '{}'),
      fs.readFile(path.join(root, 'eodhd-simple.json'), 'utf8').catch(() => '{}'),
    ]);

    // Load two-stage validation prompts
    const [requirementPromptBuf, matcherPromptBuf] = await Promise.all([
      fs.readFile(path.join(root, 'api-requirement-generator-prompt.txt'), 'utf8').catch(() => ''),
      fs.readFile(path.join(root, 'api-availability-matcher-prompt.txt'), 'utf8').catch(() => ''),
    ]);

    const specs = {
      'Alpaca Market Data API': JSON.parse(alpacaMarketBuf || '{}'),
      'Alpaca Trading API': JSON.parse(alpacaTradingBuf || '{}'),
      'EODHD API': JSON.parse(eodhdBuf || '{}'),
    };

    const totalEndpoints = Object.values(specs).reduce((total, spec: any) => 
      total + (spec.endpoints?.length || 0), 0);

    res.status(200).json({
      validationPrompt: promptBuf,
      specs,
      requirementPrompt: requirementPromptBuf,
      matcherPrompt: matcherPromptBuf,
      stats: {
        validationPromptLength: promptBuf.length,
        specsLength: JSON.stringify(specs).length,
        requirementPromptLength: requirementPromptBuf.length,
        matcherPromptLength: matcherPromptBuf.length,
        totalEndpoints,
        apiCount: Object.keys(specs).length
      }
    });
  } catch (error: any) {
    res.status(500).json({ error: error?.message || 'Failed to load validation assets' });
  }
}

