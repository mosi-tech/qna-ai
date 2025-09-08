import type { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs';
import path from 'path';
import { registryMap } from '../../experimental/registry';

function approvalsPath() {
  return path.join(process.cwd(), 'data', 'approved.json');
}
function experimentalPath() {
  return path.join(process.cwd(), 'data', 'experimental.json');
}

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', ['POST']);
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  try {
    const { id } = req.body || {};
    if (!id || typeof id !== 'string') {
      return res.status(400).json({ error: 'Missing id' });
    }

    const file = approvalsPath();
    if (!fs.existsSync(file)) {
      fs.mkdirSync(path.dirname(file), { recursive: true });
      fs.writeFileSync(file, JSON.stringify([]));
    }
    const raw = fs.readFileSync(file, 'utf-8');
    const parsed = JSON.parse(raw);
    const data: any[] = Array.isArray(parsed) ? parsed : [];

    // Find the entry to move back to experimental
    const index = data.findIndex((item: any) => (typeof item === 'string' ? item === id : item?.id === id));
    let moved: any = null;
    if (index >= 0) {
      const it = data[index];
      if (typeof it === 'string') {
        const def = registryMap[it];
        moved = def ? { id: def.id, question: '', name: def.name, file: def.file, description: def.description } : null;
      } else if (it && typeof it === 'object') {
        const def = registryMap[it.id];
        moved = {
          id: it.id,
          question: typeof it.question === 'string' ? it.question : '',
          name: it.name || def?.name || it.id,
          file: it.file || def?.file || '',
          description: it.description || def?.description || '',
          apis: Array.isArray((it as any).apis) ? (it as any).apis.filter((x: any) => typeof x === 'string') : undefined,
          position: (it as any).position && typeof (it as any).position === 'object' ? (it as any).position : undefined,
        };
      }
    }

    const filtered = data.filter((item: any) => {
      if (typeof item === 'string') return item !== id;
      if (item && typeof item === 'object') return item.id !== id;
      return true;
    });
    fs.writeFileSync(file, JSON.stringify(filtered, null, 2));

    // Append to experimental.json preserving question
    try {
      const expFile = experimentalPath();
      if (!fs.existsSync(path.dirname(expFile))) fs.mkdirSync(path.dirname(expFile), { recursive: true });
      if (!fs.existsSync(expFile)) fs.writeFileSync(expFile, JSON.stringify([]));
      if (moved) {
        const expRaw = fs.readFileSync(expFile, 'utf-8');
        const expParsed = JSON.parse(expRaw);
        let expData: any[] = Array.isArray(expParsed) ? expParsed : [];
        const exists = expData.some((e: any) => (typeof e === 'string' ? e === moved.id : e?.id === moved.id));
        if (!exists) {
          expData = [...expData, moved];
          fs.writeFileSync(expFile, JSON.stringify(expData, null, 2));
        }
      }
    } catch {}

    return res.status(200).json({ approved: filtered });
  } catch (err: any) {
    return res.status(500).json({ error: 'Failed to update approvals' });
  }
}
