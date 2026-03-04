// Public API barrel — re-exports all core auth primitives.
//
// Deep imports for handlers, pages, and admin (they have their own sub-paths
// and are not re-exported here to avoid importing next/headers at module init):
//   import { POST } from '@ui-gen/auth-core/handlers/billing-checkout';
//   import LoginPage from '@ui-gen/auth-core/pages/login';
//   import AdminUsers from '@ui-gen/auth-core/admin/users';

export * from './db/schema';
export * from './db/index';
export * from './supabase';
export * from './entitlements';
export * from './stripe';
export * from './novu';
