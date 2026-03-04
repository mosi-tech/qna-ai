import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';

// Module-level cache: one pool per unique connection URL.
// Next.js hot-module-reload survives across requests in the same process, so
// this prevents a new Postgres pool from being opened on every request.
const clientCache = new Map<string, postgres.Sql>();

/**
 * Creates (or returns a cached) Drizzle DB instance for the given URL and schema.
 * Pool is capped at 10 connections with aggressive idle/lifetime timeouts so
 * serverless invocations don't exhaust Postgres connection slots.
 */
export function createDb<TSchema extends Record<string, unknown>>(
    url: string,
    schema: TSchema,
) {
    let client = clientCache.get(url);
    if (!client) {
        client = postgres(url, {
            prepare: false,
            max: 10,            // hard cap per process
            idle_timeout: 20,   // seconds before an idle connection is closed
            max_lifetime: 1800, // seconds before a connection is recycled
            connect_timeout: 10,
        });
        clientCache.set(url, client);
    }
    return drizzle(client, { schema });
}

export type DbInstance = ReturnType<typeof createDb>;
