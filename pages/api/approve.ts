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
    let { id, question } = req.body || {};
    if (!id || typeof id !== 'string') {
      return res.status(400).json({ error: 'Missing id' });
    }
    // Load experimental list early so we can default the question if missing
    const expFile = experimentalPath();
    const expRaw = fs.existsSync(expFile) ? fs.readFileSync(expFile, 'utf-8') : '[]';
    const expList: any[] = Array.isArray(JSON.parse(expRaw)) ? JSON.parse(expRaw) : [];
    const expIdx = expList.findIndex((e: any) => (typeof e === 'string' ? e === id : e?.id === id));
    const expHit = expIdx !== -1 ? expList[expIdx] : null;

    if (typeof question !== 'string' || !question.trim()) {
      const fallbackQ = expHit && typeof expHit === 'object' && typeof expHit.question === 'string' ? expHit.question : '';
      if (!fallbackQ.trim()) return res.status(400).json({ error: 'Missing question' });
      question = fallbackQ;
    }
    const def = registryMap[id];

    const file = approvalsPath();
    if (!fs.existsSync(file)) {
      fs.mkdirSync(path.dirname(file), { recursive: true });
      fs.writeFileSync(file, JSON.stringify([]));
    }
    const raw = fs.readFileSync(file, 'utf-8');
    let parsed: any = [];
    try {
      parsed = raw && raw.trim().length > 0 ? JSON.parse(raw) : [];
    } catch {
      parsed = [];
    }
    let approvedArr: any[] = Array.isArray(parsed) ? parsed : [];

    // Load experimental list and find the entry by id
    const idx = expIdx;

    let entry: any = null;
    if (idx !== -1) {
      const hit = expList[idx];
      if (typeof hit === 'string') {
        // Minimal expansion from registry if only an id string is present
        const d = registryMap[hit];
        entry = d ? { id: d.id, name: d.name, file: d.file, output: d.file } : { id: hit };
      } else if (hit && typeof hit === 'object') {
        entry = { ...hit };
      }
    } else {
      // Fallback: construct minimal entry from registry if not present in experimental.json
      entry = def ? { id: def.id, name: def.name, file: def.file, output: def.file } : { id };
    }

    // Always set/override the question from the request
    entry.question = question.trim();

    // Upsert into approved array
    const exist = approvedArr.findIndex((a: any) => a && a.id === id);
    if (exist >= 0) approvedArr[exist] = entry; else approvedArr.push(entry);
    fs.writeFileSync(file, JSON.stringify(approvedArr, null, 2));

    // Remove from experimental.json
    try {
      const filtered = expList.filter((it: any) => {
        if (typeof it === 'string') return it !== id;
        return !(it && typeof it === 'object' && it.id === id);
      });
      fs.writeFileSync(expFile, JSON.stringify(filtered, null, 2));
    } catch {}

    // Respond with the approved list as stored
    return res.status(200).json({ approved: approvedArr });
  } catch (err: any) {
    return res.status(500).json({ error: 'Failed to update approvals' });
  }
}
