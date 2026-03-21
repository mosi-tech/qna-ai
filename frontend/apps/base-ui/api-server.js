import fs from 'fs';
import path from 'path';
import express from 'express';
import cors from 'cors';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 3001;
const DATA_FILE = path.join(__dirname, 'approvals.json');

app.use(cors());
app.use(express.json());

// Ensure data file exists
function ensureDataFile() {
  if (!fs.existsSync(DATA_FILE)) {
    fs.writeFileSync(DATA_FILE, JSON.stringify({}), 'utf-8');
  }
}

// GET /api/width-approvals
app.get('/api/width-approvals', (req, res) => {
  try {
    ensureDataFile();
    const data = fs.readFileSync(DATA_FILE, 'utf-8');
    const approvals = JSON.parse(data);
    res.json({ success: true, data: approvals });
  } catch (err) {
    console.error('Error reading approvals:', err);
    res.json({ success: false, data: {} });
  }
});

// POST /api/width-approvals
app.post('/api/width-approvals', (req, res) => {
  try {
    const approvals = req.body;
    fs.writeFileSync(DATA_FILE, JSON.stringify(approvals, null, 2), 'utf-8');
    console.log('✓ Saved approvals:', Object.keys(approvals).length, 'blocks');
    res.json({ success: true, data: { saved: true } });
  } catch (err) {
    console.error('Error saving approvals:', err);
    res.status(500).json({ success: false, error: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`✓ Approvals API running on http://localhost:${PORT}`);
});
