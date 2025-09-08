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
  if (req.method !== 'GET') {
    res.setHeader('Allow', ['GET']);
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  try {
    const expFile = experimentalPath();
    if (!fs.existsSync(path.dirname(expFile))) fs.mkdirSync(path.dirname(expFile), { recursive: true });
    if (!fs.existsSync(expFile)) fs.writeFileSync(expFile, JSON.stringify([]));

    const expRaw = fs.readFileSync(expFile, 'utf-8');
    const experimental: any[] = Array.isArray(JSON.parse(expRaw)) ? JSON.parse(expRaw) : [];

    // Normalize objects
    const normalized = experimental
      .map((item: any) => {
        if (typeof item === 'string') {
          const def = registryMap[item];
          return def
            ? { id: def.id, question: '', name: def.name, file: def.file, description: def.description, apis: [], position: undefined }
            : null;
        }
        if (item && typeof item === 'object' && typeof item.id === 'string') {
          const def = registryMap[item.id];
          return {
            id: item.id,
            question: typeof item.question === 'string' ? item.question : '',
            name: item.name || (def ? def.name : item.id),
            file: item.file || (def ? def.file : ''),
            description: item.description || (def ? def.description : ''),
            apis: Array.isArray(item.apis) ? item.apis.filter((x: any) => typeof x === 'string') : [],
            position: item.position && typeof item.position === 'object' ? item.position : undefined,
          };
        }
        return null;
      })
      .filter(Boolean);

    return res.status(200).json({ experimental: normalized });
  } catch (err: any) {
    return res.status(500).json({ error: 'Failed to read experimental list' });
  }
}
