/**
 * Appwrite Client Configuration
 * Handles authentication for the financial analysis platform
 */

import { Client, Account, Teams, Databases } from 'appwrite';

// Environment configuration
const APPWRITE_ENDPOINT = process.env.NEXT_PUBLIC_APPWRITE_ENDPOINT;
const APPWRITE_PROJECT_ID = process.env.NEXT_PUBLIC_APPWRITE_PROJECT_ID;

if (!APPWRITE_ENDPOINT || !APPWRITE_PROJECT_ID) {
    console.error('❌ Appwrite configuration missing!');
    console.error('Please set the following environment variables in frontend/.env.local:');
    console.error('NEXT_PUBLIC_APPWRITE_ENDPOINT=https://your-appwrite-domain.com/v1');
    console.error('NEXT_PUBLIC_APPWRITE_PROJECT_ID=your-project-id');
}

// Create Appwrite client
export const client = new Client();

// Only set configuration if environment variables are available
if (APPWRITE_ENDPOINT && APPWRITE_PROJECT_ID) {
    client.setEndpoint(APPWRITE_ENDPOINT).setProject(APPWRITE_PROJECT_ID);
    console.log('✅ Appwrite client configured:', APPWRITE_ENDPOINT);
} else {
    console.warn('⚠️ Appwrite client not configured - using defaults');
    // Use placeholder values to prevent crashes
    client.setEndpoint('https://localhost').setProject('test');
}

// Initialize services
export const account = new Account(client);
export const teams = new Teams(client);
export const databases = new Databases(client);

// User roles for the financial platform
export const USER_ROLES = {
    ANALYST: 'analyst',      // Read-only access
    PREMIUM: 'premium',      // Full analysis access  
    ADMIN: 'admin'          // System management
} as const;

export type UserRole = typeof USER_ROLES[keyof typeof USER_ROLES];

// Auth-related types
export interface AppwriteUser {
    $id: string;
    $createdAt: string;
    $updatedAt: string;
    name: string;
    email: string;
    emailVerification: boolean;
    prefs: Record<string, any>;
    roles?: UserRole[];
}

export interface AuthSession {
    $id: string;
    $createdAt: string;
    userId: string;
    expire: string;
    provider: string;
    providerUid: string;
    current: boolean;
}

// Export for easy access
export { Client, Account, Teams, Databases };
export default client;