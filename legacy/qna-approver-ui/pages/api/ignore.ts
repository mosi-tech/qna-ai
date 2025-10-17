import type { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs';
import path from 'path';

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

    const expFile = experimentalPath();
    if (!fs.existsSync(expFile)) {
      return res.status(404).json({ error: 'Experimental file not found' });
    }

    const expRaw = fs.readFileSync(expFile, 'utf-8');
    const expParsed = JSON.parse(expRaw);
    
    // Filter out the item to be ignored/deleted
    const filtered = (Array.isArray(expParsed) ? expParsed : []).filter((item: any) => {
      if (typeof item === 'string') return item !== id;
      if (item && typeof item === 'object') return item.id !== id;
      return true;
    });

    // Write the updated experimental data back to file
    fs.writeFileSync(expFile, JSON.stringify(filtered, null, 2));

    return res.status(200).json({ experimental: filtered });
  } catch (err: any) {
    return res.status(500).json({ error: 'Failed to ignore experimental item' });
  }
}