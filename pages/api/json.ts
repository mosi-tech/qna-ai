import type { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs';
import path from 'path';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    res.setHeader('Allow', ['GET']);
    return res.status(405).json({ error: 'Method Not Allowed' });
  }
  try {
    const fileParam = String(req.query.file || '');
    if (!fileParam || !fileParam.startsWith('experimental/') || !fileParam.endsWith('.json')) {
      return res.status(400).json({ error: 'Invalid file path' });
    }
    const abs = path.join(process.cwd(), fileParam);
    // Ensure within project dir and under experimental
    const expDir = path.join(process.cwd(), 'experimental');
    if (!abs.startsWith(expDir)) {
      return res.status(400).json({ error: 'Path traversal blocked' });
    }
    if (!fs.existsSync(abs)) {
      return res.status(404).json({ error: 'Not found' });
    }
    const raw = fs.readFileSync(abs, 'utf-8');
    const json = raw && raw.trim() ? JSON.parse(raw) : {};
    return res.status(200).json(json);
  } catch (e: any) {
    return res.status(500).json({ error: 'Failed to read JSON' });
  }
}

