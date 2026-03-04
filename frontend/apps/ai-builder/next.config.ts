import type { NextConfig } from 'next';
import path from 'path';

const nextConfig: NextConfig = {
    // Allow @ui-gen/base-ui to be transpiled (workspace symlink, ESM)
    transpilePackages: ['@ui-gen/base-ui'],
    // Anchor file tracing to the monorepo root (suppresses pnpm workspace warning)
    outputFileTracingRoot: path.join(__dirname, '../../'),
};

export default nextConfig;
