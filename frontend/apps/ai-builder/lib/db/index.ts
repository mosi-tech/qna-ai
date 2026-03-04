import { createDb } from '@ui-gen/auth-core/db';
import * as schema from './schema';

export const db = createDb(process.env.DATABASE_URL!, schema);
export type { DbInstance } from '@ui-gen/auth-core/db';
