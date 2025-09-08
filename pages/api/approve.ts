import type { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs';
import path from 'path';
import { registryMap } from '../../experimental/registry';
import { } from './experimental';

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
    const { id, question } = req.body || {};
    if (!id || typeof id !== 'string') {
      return res.status(400).json({ error: 'Missing id' });
    }
    if (typeof question !== 'string' || !question.trim()) {
      return res.status(400).json({ error: 'Missing question' });
    }
    const def = registryMap[id];
    if (!def) {
      return res.status(400).json({ error: 'Unknown visual id' });
    }

    const file = approvalsPath();
    if (!fs.existsSync(file)) {
      fs.mkdirSync(path.dirname(file), { recursive: true });
      fs.writeFileSync(file, JSON.stringify([]));
    }
    const raw = fs.readFileSync(file, 'utf-8');
    const parsed = JSON.parse(raw);
    type Approval = { id: string; question: string; file: string; name: string; apis?: string[]; position?: any };
    let data: Approval[] = [];
    if (Array.isArray(parsed)) {
      data = parsed.map((item: any) => {
        if (typeof item === 'string') {
          const d = registryMap[item];
          return d ? { id: d.id, question: '', file: d.file, name: d.name } : null;
        }
        if (item && typeof item === 'object' && typeof item.id === 'string') {
          const d = registryMap[item.id];
          return {
            id: item.id,
            question: typeof item.question === 'string' ? item.question : '',
            file: item.file || (d ? d.file : ''),
            name: item.name || (d ? d.name : item.id),
          };
        }
        return null;
      }).filter(Boolean) as Approval[];
    }

    // Try to pull any extra metadata (like apis) from experimental.json
    let apis: string[] | undefined = undefined;
    let position: any | undefined = undefined;
    try {
      const expFile = path.join(process.cwd(), 'data', 'experimental.json');
      if (fs.existsSync(expFile)) {
        const expRaw = fs.readFileSync(expFile, 'utf-8');
        const expData = JSON.parse(expRaw);
        if (Array.isArray(expData)) {
          const hit = expData.find((e: any) => (typeof e === 'string' ? e === id : e?.id === id));
          if (hit && typeof hit === 'object') {
            if (Array.isArray(hit.apis)) {
              apis = hit.apis.filter((x: any) => typeof x === 'string');
            }
            if (hit.position && typeof hit.position === 'object') {
              position = hit.position;
            }
          }
        }
      }
    } catch {}

    const existingIndex = data.findIndex((a) => a.id === id);
    const entry: Approval = { id, question: question.trim(), file: def.file, name: def.name, apis, position };
    if (existingIndex >= 0) {
      data[existingIndex] = entry;
    } else {
      data.push(entry);
    }
    fs.writeFileSync(file, JSON.stringify(data, null, 2));
    // Also remove from experimental.json if present
    try {
      const expFile = experimentalPath();
      if (fs.existsSync(expFile)) {
        const expRaw = fs.readFileSync(expFile, 'utf-8');
        const expParsed = JSON.parse(expRaw);
        const filtered = (Array.isArray(expParsed) ? expParsed : []).filter((it: any) => {
          if (typeof it === 'string') return it !== id;
          if (it && typeof it === 'object') return it.id !== id;
          return true;
        });
        fs.writeFileSync(expFile, JSON.stringify(filtered, null, 2));
      }
    } catch {}
    return res.status(200).json({ approved: data });
  } catch (err: any) {
    return res.status(500).json({ error: 'Failed to update approvals' });
  }
}
