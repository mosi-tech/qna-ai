# QnA AI Admin (Next.js)

A lightweight Next.js app that prototypes a QnA-driven JSON output workflow. It lets you:

- Capture questions in a left chat panel.
- Preview unapproved JSON outputs on the right (auto-shown from an experimental catalog stored in JSON).
- Approve JSON outputs to promote them to the Approved list (persisted to JSON).
- Move JSON outputs between Experimental and Approved lists.

Everything is file‑backed for simplicity (no DB). JSON output files live in `experimental/` and are registered with metadata. Approved and Experimental registries persist in `data/*.json`.

## Features

- Two‑panel layout: left QnA (30%), right JSON Output Layer (70%)
- Three sections:
  - Main: QnA + auto preview of the next experimental JSON output + Approved list
  - Experimental: two‑panel list/detail to preview and “Move to Approved”
  - Approved: two‑panel list/detail to preview and “Move to Experimental”
- JSON persistence:
  - `data/experimental.json` for unapproved JSON outputs
  - `data/approved.json` for approved JSON outputs
- JSON output metadata:
  - `question`: the question the JSON output answers (generated, not required from the user)
  - `apis`: array of APIs the JSON output relies on (e.g., Alpaca endpoints)
  - `followupQuestions`: suggested related questions
  - `output`: path to the well-formatted JSON file with descriptive field explanations
- Preview flow: main page auto‑shows the first experimental JSON output, no extra clicks needed
- Promote/demote: approve/unapprove APIs move entries between JSON stores, preserving metadata

## Getting Started

Requirements: Node 18+ (18.17+) or Node 20+

Install and run:

```bash
npm install
npm run dev
# open http://localhost:3000
```

Build and start (production):

```bash
npm run build
npm run start
```

## Project Structure

- `pages/index.tsx` — Main screen with QnA (left) and JSON output layer (right). Auto‑previews the first experimental JSON output and lists approved outputs. Allows approving from preview.
- `pages/experimental.tsx` — Two‑panel page for Experimental items: list on left, selected JSON output with actions on right.
- `pages/approved.tsx` — Two‑panel page for Approved items: list on left, selected JSON output on right with "Move to Experimental".
- `experimental/` — A registry:
  - `registry.ts` — IDs, names, file paths
- `data/` — JSON persistence:
  - `experimental.json` — array of experimental entries.
  - `approved.json` — array of approved entries.
- `pages/api/` — File‑backed API routes:
  - `approved.ts` (GET) — read approved list
  - `approve.ts` (POST) — move item to approved; removes from experimental
  - `unapprove.ts` (POST) — move item to experimental; removes from approved
  - `experimental.ts` (GET) — read experimental list
  - `move-to-experimental.ts` (POST) — add inbox/unknown item to experimental (internal utility)

## Data Model

Entries in `data/*.json` are lightweight objects:

```jsonc
{
  "id": "news-aapl",                 // matches experimental/registry.ts
  "name": "News: AAPL (24h)",
  "file": "experimental/NewsList.json",
  "description": "Latest headlines for AAPL.",
  "question": "What are the latest AAPL news headlines?",
  "apis": ["marketdata:/v1beta1/news"],         // optional
  "followupQuestions": ["How did price move around these headlines?"],
  "output": "/experimental/NewsList.json"
}
```

Notes:
- Approving carries all fields (including `apis`, `output`) from experimental to approved.
- Unapproving moves the entry back to experimental, preserving fields.

## User Flow

1. Ask a question in the left chat panel on `/` (optional; questions are pre‑generated for JSON outputs).
2. The first experimental JSON output auto‑shows in the right preview card on `/`.
3. Click "Move to Approved" to promote it. It will be removed from `experimental.json` and added to `approved.json`.
4. Manage details in dedicated pages:
   - `/experimental` — choose an item on the left, preview and promote on the right.
   - `/approved` — choose an item on the left, preview and demote on the right.

## Adding a New JSON Output

1. Create a JSON file in `experimental/`, e.g. `MyOutput.json` with well-formatted data and field descriptions.
2. Register it in `experimental/registry.ts` with a unique `id`, `name`, and `file` path.
3. Add an entry to `data/experimental.json` with at least `{ id, name, file, question }`. Optionally add `description`, `apis`, `followupQuestions`, and `output`.
4. Start the app: the JSON output will auto‑preview on the main page until approved.

Tip: JSON outputs should follow this structure:
```jsonc
{
  "description": "Overall explanation of what this JSON output represents and its purpose",
  "body": [
    {
      "key": "unique_identifier",
      "value": "actual_data_value", 
      "description": "Explanation of what this specific data point means"
    }
    // ... more data points
  ]
}
```

## Alpaca

- This repo includes OpenAPI specs for Alpaca Market Data and Trading (`alpaca.marketdata.spec.json`, `alpaca.trading.spec.json`).
- JSON outputs include `apis` metadata listing expected endpoints.
- For production usage, create server‑side fetchers for Alpaca (with keys in env) and generate live JSON data.

## Deployment Notes

- File writes (`data/*.json`) require a persistent filesystem. This works in Node server environments. On serverless platforms, use a database instead.
- No auth is implemented; add auth before exposing beyond local development.

## Scripts

- `npm run dev` — start Next.js in dev
- `npm run build` — build production bundle
- `npm run start` — start production server

## License

Internal prototype; no license specified.

# qna-ai
