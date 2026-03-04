export * from '@ui-gen/auth-core/db/schema';

import { pgTable, uuid, text, jsonb, timestamp } from 'drizzle-orm/pg-core';
import { sql } from 'drizzle-orm';

export const saved_dashboards = pgTable('saved_dashboards', {
    id: uuid('id').primaryKey().default(sql`gen_random_uuid()`),
    user_id: uuid('user_id').notNull(),
    name: text('name').notNull(),
    config: jsonb('config'),
    created_at: timestamp('created_at').notNull().default(sql`now()`),
    updated_at: timestamp('updated_at').notNull().default(sql`now()`),
});
