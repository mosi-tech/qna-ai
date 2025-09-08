import type { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs';
import path from 'path';
import { registryMap } from '../../experimental/registry';

function approvalsPath() {
  return path.join(process.cwd(), 'data', 'approved.json');
}

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    res.setHeader('Allow', ['GET']);
    return res.status(405).json({ error: 'Method Not Allowed' });
  }
  try {
    const file = approvalsPath();
    if (!fs.existsSync(file)) {
      fs.mkdirSync(path.dirname(file), { recursive: true });
      fs.writeFileSync(file, JSON.stringify([]));
    }
    const raw = fs.readFileSync(file, 'utf-8');
    const data = JSON.parse(raw);

    // Migrate legacy format (array of ids) to objects with question/file/name
    const normalized = (Array.isArray(data) ? data : [])
      .map((item: any) => {
        if (typeof item === 'string') {
          const def = registryMap[item];
          return def
            ? { id: def.id, question: '', file: def.file, name: def.name, apis: [], position: undefined }
            : null;
        }
        if (item && typeof item === 'object' && typeof item.id === 'string') {
          const def = registryMap[item.id];
          return {
            id: item.id,
            question: typeof item.question === 'string' ? item.question : '',
            file: item.file || (def ? def.file : ''),
            name: item.name || (def ? def.name : item.id),
            apis: Array.isArray(item.apis) ? item.apis.filter((x: any) => typeof x === 'string') : [],
            position: item.position && typeof item.position === 'object' ? item.position : undefined,
          };
        }
        return null;
      })
      .filter(Boolean);

    return res.status(200).json({ approved: normalized });
  } catch (err: any) {
    return res.status(500).json({ error: 'Failed to read approvals' });
  }
}
