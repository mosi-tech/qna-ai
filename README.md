# QnA AI Admin (Next.js)

A lightweight Next.js app that prototypes a QnA-driven visualization workflow. It lets you:

- Capture questions in a left chat panel.
- Preview unapproved visuals on the right (auto-shown from an experimental catalog stored in JSON).
- Approve visuals to promote them to the Approved list (persisted to JSON).
- Move visuals between Experimental and Approved lists.

Everything is file‑backed for simplicity (no DB). Visual components live in `experimental/` and are registered with metadata. Approved and Experimental registries persist in `data/*.json`.

## Features

- Two‑panel layout: left QnA (30%), right Visual Layer (70%)
- Three sections:
  - Main: QnA + auto preview of the next experimental visual + Approved list
  - Experimental: two‑panel list/detail to preview and “Move to Approved”
  - Approved: two‑panel list/detail to preview and “Move to Experimental”
- JSON persistence:
  - `data/experimental.json` for unapproved visuals
  - `data/approved.json` for approved visuals
- Visual metadata:
  - `question`: the question the visual answers (generated, not required from the user)
  - `apis`: array of APIs the visual relies on (e.g., Alpaca endpoints)
  - `followupQuestions`: suggested related questions
  - `position` (optional): user position context passed into the visual (and rendered by visuals that support it)
- Preview flow: main page auto‑shows the first experimental visual, no extra clicks needed
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

- `pages/index.tsx` — Main screen with QnA (left) and visual layer (right). Auto‑previews the first experimental visual and lists approved visuals. Allows approving from preview.
- `pages/experimental.tsx` — Two‑panel page for Experimental items: list on left, selected visual with actions on right.
- `pages/approved.tsx` — Two‑panel page for Approved items: list on left, selected visual on right with “Move to Experimental”.
- `experimental/` — Visual components and a registry:
  - `registry.ts` — IDs, names, file paths, and component references.
  - `AccountOverview.tsx`, `ForexRatesCard.tsx`, `NewsList.tsx`, `BarChart.tsx`, `StatsCard.tsx` — example visuals.
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
  "file": "experimental/NewsList.tsx",
  "description": "Latest headlines for AAPL.",
  "question": "What are the latest AAPL news headlines?",
  "apis": ["marketdata:/v1beta1/news"],         // optional
  "followupQuestions": ["How did price move around these headlines?"],
  "position": {                                  // optional; if present, passed down to the visual
    "qty": 10,
    "avg_entry_price": 210.5,
    "market_value": 2295.1
  }
}
```

Notes:
- Approving carries all fields (including `apis`, `position`) from experimental to approved.
- Unapproving moves the entry back to experimental, preserving fields.

## User Flow

1. Ask a question in the left chat panel on `/` (optional; questions are pre‑generated for visuals).
2. The first experimental visual auto‑shows in the right preview card on `/`.
3. Click “Move to Approved” to promote it. It will be removed from `experimental.json` and added to `approved.json`.
4. Manage details in dedicated pages:
   - `/experimental` — choose an item on the left, preview and promote on the right.
   - `/approved` — choose an item on the left, preview and demote on the right.

## Adding a New Visual

1. Create a component in `experimental/`, e.g. `MyVisual.tsx`.
2. Register it in `experimental/registry.ts` with a unique `id`, `name`, and `file` path.
3. Add an entry to `data/experimental.json` with at least `{ id, name, file, question }`. Optionally add `description`, `apis`, `followupQuestions`, and `position`.
4. Start the app: the visual will auto‑preview on the main page until approved.

Tip: Visuals can accept optional props like `position`. Unknown props are ignored safely by most components, but prefer defining prop types if you extend visuals.

## Alpaca

- This repo includes OpenAPI specs for Alpaca Market Data and Trading (`alpaca.marketdata.spec.json`, `alpaca.trading.spec.json`).
- Visuals include `apis` metadata listing expected endpoints.
- For production usage, create server‑side fetchers for Alpaca (with keys in env) and wire visuals to live data.

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
