const fs = require('fs');
const path = require('path');

const INPUT_FILES = [
  'alpaca-marketdata-simple.json',
  'alpaca-trading-simple.json',
  'eodhd-simple.json',
];

function slugFromPath(p) {
  // e.g., "/v2/stocks/bars" -> "get_stocks_bars"
  const parts = p.split('/').filter(Boolean);
  const filtered = parts.filter(seg => !/^v\d/.test(seg) && !/^v\d+beta/.test(seg));
  const replaced = filtered.map(seg => seg.replace(/[{}]/g, '')); // remove path params braces
  const slug = ['get', ...replaced]
    .join('_')
    .replace(/[^a-zA-Z0-9_]+/g, '_')
    .replace(/_+/g, '_')
    .replace(/^_+|_+$/g, '')
    .toLowerCase();
  return slug || 'get_endpoint';
}

function inferType(key, value) {
  const k = key.toLowerCase();
  if (typeof value === 'number') return 'number';
  if (typeof value === 'boolean') return 'boolean';
  if (value === null) return 'string';
  if (typeof value !== 'string') return 'string';

  const v = value.trim().toLowerCase();
  if (v === 'true' || v === 'false') return 'boolean';
  if (/^\d+$/.test(v)) return 'integer';
  if (/^\d+\.\d+$/.test(v)) return 'number';
  if (k.includes('date') || ['start','end','from','to','since','until','time','timestamp'].some(d => k.includes(d))) return 'string(date)';
  if (k.includes('page') || k.includes('limit') || k.includes('size') || k === 'top') return 'integer';
  if (k.includes('symbol')) return 'string';
  if (k.includes('symbols')) return 'string';
  if (v.includes(',')) return 'string'; // enum/list in examples
  return 'string';
}

function transform(spec) {
  const out = {
    name: spec.name || 'API',
    description: spec.description || '',
    endpoints: [],
  };

  const eps = Array.isArray(spec.endpoints) ? spec.endpoints : [];
  for (const ep of eps) {
    const name = slugFromPath(ep.path || ep.endpoint || '');
    const description = ep.purpose || ep.description || '';
    const params = ep.parameters && typeof ep.parameters === 'object' ? ep.parameters : {};
    const simplifiedParams = Object.keys(params);
    out.endpoints.push({ name, description, parameters: simplifiedParams });
  }

  return out;
}

function main() {
  for (const file of INPUT_FILES) {
    const inputPath = path.join(process.cwd(), file);
    if (!fs.existsSync(inputPath)) {
      console.error(`Missing input: ${file}`);
      continue;
    }
    const json = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
    const transformed = transform(json);
    const outName = file.replace('-simple.json', '-extra-simple.json');
    const outPath = path.join(process.cwd(), outName);
    fs.writeFileSync(outPath, JSON.stringify(transformed, null, 2), 'utf8');
    console.log(`Wrote ${outName} (${transformed.endpoints.length} endpoints)`);
  }
}

if (require.main === module) {
  main();
}
