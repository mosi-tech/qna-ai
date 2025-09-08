import type { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs';
import path from 'path';
import { registryMap } from '../../experimental/registry';

function experimentalPath() {
  return path.join(process.cwd(), 'data', 'experimental.json');
}

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', ['POST']);
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  try {
    const { id, question } = req.body || {};
    if (!id || typeof id !== 'string') return res.status(400).json({ error: 'Missing id' });
    const def = registryMap[id];
    if (!def) return res.status(400).json({ error: 'Unknown visual id' });

    const file = experimentalPath();
    if (!fs.existsSync(path.dirname(file))) fs.mkdirSync(path.dirname(file), { recursive: true });
    if (!fs.existsSync(file)) fs.writeFileSync(file, JSON.stringify([]));
    const raw = fs.readFileSync(file, 'utf-8');
    const parsed = JSON.parse(raw);
    let data: any[] = Array.isArray(parsed) ? parsed : [];
    const exists = data.some((e: any) => (typeof e === 'string' ? e === id : e?.id === id));
    if (!exists) {
      data.push({ id, question: typeof question === 'string' ? question : '', name: def.name, file: def.file, description: def.description });
      fs.writeFileSync(file, JSON.stringify(data, null, 2));
    }
    return res.status(200).json({ experimental: data });
  } catch (err: any) {
    return res.status(500).json({ error: 'Failed to move to experimental' });
  }
}

