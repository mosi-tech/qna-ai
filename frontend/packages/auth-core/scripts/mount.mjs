#!/usr/bin/env node
/**
 * @ui-gen/auth-core mount.mjs
 *
 * Usage:
 *   node packages/auth-core/scripts/mount.mjs --app <app-name> [--overwrite]
 *
 * Generates 1-line stub files in the target app so it delegates all auth/billing
 * routes and pages to @ui-gen/auth-core. Existing files are skipped unless
 * --overwrite is passed.
 *
 * Example:
 *   node packages/auth-core/scripts/mount.mjs --app ai-builder
 *   node packages/auth-core/scripts/mount.mjs --app ai-builder --overwrite
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

// ── Resolve paths ────────────────────────────────────────────────────────────

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/** Monorepo root (three levels up from packages/auth-core/scripts/) */
const REPO_ROOT = resolve(__dirname, '..', '..', '..');

// ── Parse CLI args ───────────────────────────────────────────────────────────

const args = process.argv.slice(2);

function getArg(name) {
    const idx = args.indexOf(name);
    if (idx === -1) return undefined;
    return args[idx + 1];
}

const appName = getArg('--app');
const overwrite = args.includes('--overwrite');

if (!appName) {
    console.error('Usage: node mount.mjs --app <app-name> [--overwrite]');
    console.error('');
    console.error('Example: node mount.mjs --app ai-builder');
    process.exit(1);
}

// ── Resolve target app directory ─────────────────────────────────────────────

const appDir = resolve(REPO_ROOT, appName);

if (!existsSync(appDir)) {
    console.error(`Error: App directory not found: ${appDir}`);
    process.exit(1);
}

// Verify it looks like a Next.js app (has package.json)
const appPkg = join(appDir, 'package.json');
if (!existsSync(appPkg)) {
    console.error(`Error: ${appDir} does not contain a package.json`);
    process.exit(1);
}

// ── Stub definitions ─────────────────────────────────────────────────────────

/**
 * @type {Array<{ path: string; content: string; skipIfExists?: boolean }>}
 *
 * `skipIfExists: true` means the file is ONLY created if it doesn't exist,
 * even when --overwrite is passed. This is for files the app typically customises
 * (like the db schema and db index).
 */
const STUBS = [
    // ── Auth pages ─────────────────────────────────────────────────────────────
    {
        path: 'app/(auth)/login/page.tsx',
        content: "export { default } from '@ui-gen/auth-core/pages/login';\n",
    },
    {
        path: 'app/(auth)/signup/page.tsx',
        content: "export { default } from '@ui-gen/auth-core/pages/signup';\n",
    },
    {
        path: 'app/(auth)/reset/page.tsx',
        content: "export { default } from '@ui-gen/auth-core/pages/reset';\n",
    },
    {
        path: 'app/(auth)/callback/route.ts',
        content: "export { GET } from '@ui-gen/auth-core/pages/callback';\n",
    },

    // ── Dashboard pages ────────────────────────────────────────────────────────
    {
        path: 'app/(dashboard)/account/page.tsx',
        content: "export { default } from '@ui-gen/auth-core/pages/account';\n",
    },
    {
        path: 'app/(dashboard)/billing/page.tsx',
        content: "export { default } from '@ui-gen/auth-core/pages/billing';\n",
    },
    {
        path: 'app/(dashboard)/usage/page.tsx',
        content: "export { default } from '@ui-gen/auth-core/pages/usage';\n",
    },
    {
        path: 'app/(dashboard)/notifications/page.tsx',
        content: "export { default } from '@ui-gen/auth-core/pages/notifications';\n",
    },

    // ── Admin pages ────────────────────────────────────────────────────────────
    {
        path: 'app/(admin)/layout.tsx',
        content: "export { default } from '@ui-gen/auth-core/admin/layout';\n",
    },
    {
        path: 'app/(admin)/admin/users/page.tsx',
        content: "export { default } from '@ui-gen/auth-core/admin/users';\n",
    },
    {
        path: 'app/(admin)/admin/revenue/page.tsx',
        content: "export { default } from '@ui-gen/auth-core/admin/revenue';\n",
    },
    {
        path: 'app/(admin)/admin/usage/page.tsx',
        content: "export { default } from '@ui-gen/auth-core/admin/usage';\n",
    },

    // ── API route handlers ─────────────────────────────────────────────────────
    {
        path: 'app/api/billing/checkout/route.ts',
        content: "export { POST } from '@ui-gen/auth-core/handlers/billing-checkout';\n",
    },
    {
        path: 'app/api/billing/portal/route.ts',
        content: "export { POST } from '@ui-gen/auth-core/handlers/billing-portal';\n",
    },
    {
        path: 'app/api/webhooks/stripe/route.ts',
        content: "export { POST } from '@ui-gen/auth-core/handlers/webhook-stripe';\n",
    },
    {
        path: 'app/api/usage/record/route.ts',
        content: "export { POST } from '@ui-gen/auth-core/handlers/usage-record';\n",
    },
    {
        path: 'app/api/usage/summary/route.ts',
        content: "export { GET } from '@ui-gen/auth-core/handlers/usage-summary';\n",
    },
    {
        path: 'app/api/session/validate/route.ts',
        content: "export { GET } from '@ui-gen/auth-core/handlers/session-validate';\n",
    },
    {
        path: 'app/api/profile/update/route.ts',
        content: "export { PUT } from '@ui-gen/auth-core/handlers/profile-update';\n",
    },
    {
        path: 'app/api/profile/delete/route.ts',
        content: "export { DELETE } from '@ui-gen/auth-core/handlers/profile-delete';\n",
    },
    {
        path: 'app/api/notifications/prefs/route.ts',
        content: "export { GET, PUT } from '@ui-gen/auth-core/handlers/notification-prefs';\n",
    },
    {
        path: 'app/api/notifications/hash/route.ts',
        content: "export { GET } from '@ui-gen/auth-core/handlers/notification-hash';\n",
    },

    // ── DB schema — only create if missing; app customises this file ────────────
    {
        path: 'lib/db/schema.ts',
        skipIfExists: true,
        content: [
            "export * from '@ui-gen/auth-core/db/schema';",
            '// Add app-specific tables below:',
            '// import { pgTable, uuid, text, timestamp, sql } from \'drizzle-orm/pg-core\';',
            '',
        ].join('\n'),
    },

    // ── DB index — only create if missing; app customises this file ─────────────
    {
        path: 'lib/db/index.ts',
        skipIfExists: true,
        content: [
            "import { createDb } from '@ui-gen/auth-core/db';",
            "import * as schema from './schema';",
            '',
            'export const db = createDb(process.env.DATABASE_URL!, schema);',
            'export type { DbInstance } from \'@ui-gen/auth-core/db\';',
            '',
        ].join('\n'),
    },
];

// ── Write stubs ───────────────────────────────────────────────────────────────

/** @type {Array<{ path: string; status: 'created' | 'skipped' | 'overwritten' }>} */
const results = [];

for (const stub of STUBS) {
    const fullPath = join(appDir, stub.path);
    const exists = existsSync(fullPath);

    // Never overwrite files marked skipIfExists
    if (exists && (stub.skipIfExists || !overwrite)) {
        results.push({ path: stub.path, status: 'skipped' });
        continue;
    }

    // Create parent directories if needed
    const dir = dirname(fullPath);
    mkdirSync(dir, { recursive: true });

    writeFileSync(fullPath, stub.content, 'utf8');
    results.push({ path: stub.path, status: exists ? 'overwritten' : 'created' });
}

// ── Print summary table ───────────────────────────────────────────────────────

const PAD = 50;
const STATUS_COLORS = {
    created: '\x1b[32m',    // green
    overwritten: '\x1b[33m', // yellow
    skipped: '\x1b[90m',    // grey
};
const RESET = '\x1b[0m';

console.log('');
console.log(`  @ui-gen/auth-core → ${appName}`);
console.log(`  ${'─'.repeat(PAD + 16)}`);
console.log(`  ${'File'.padEnd(PAD)} Status`);
console.log(`  ${'─'.repeat(PAD + 16)}`);

for (const { path, status } of results) {
    const color = STATUS_COLORS[status] ?? '';
    console.log(`  ${path.padEnd(PAD)} ${color}${status}${RESET}`);
}

const created = results.filter((r) => r.status === 'created').length;
const overwritten = results.filter((r) => r.status === 'overwritten').length;
const skipped = results.filter((r) => r.status === 'skipped').length;

console.log(`  ${'─'.repeat(PAD + 16)}`);
console.log(
    `  \x1b[32m${created} created\x1b[0m  \x1b[33m${overwritten} overwritten\x1b[0m  \x1b[90m${skipped} skipped\x1b[0m`,
);
console.log('');

if (created + overwritten > 0) {
    console.log(
        '  Next: add "@ui-gen/auth-core": "workspace:*" to',
        `${appName}/package.json dependencies.`,
    );
    console.log('');
}
