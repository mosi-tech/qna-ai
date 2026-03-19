import type { NextConfig } from 'next';
import path from 'path';

const nextConfig: NextConfig = {
    // Allow workspace packages to be transpiled (workspace symlink, ESM)
    transpilePackages: ['@ui-gen/base-ui', '@ui-gen/auth-core'],
    // Anchor file tracing to the monorepo root (suppresses pnpm workspace warning)
    outputFileTracingRoot: path.join(__dirname, '../../'),
};

export default nextConfig;
