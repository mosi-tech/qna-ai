import type { Config } from 'tailwindcss';
import defaultTheme from 'tailwindcss/defaultTheme';
import forms from '@tailwindcss/forms';

const config: Config = {
    content: [
        './app/**/*.{js,ts,jsx,tsx,mdx}',
        './components/**/*.{js,ts,jsx,tsx}',
        // Scan base-ui source so Tailwind includes all utility classes used by blocks
        '../base-ui/src/**/*.{js,ts,jsx,tsx}',
        // Scan finkit-ui so FK component Tailwind classes are not purged
        '../finkit-ui/src/**/*.{js,jsx}',
        // Scan auth-core so page/admin/handler components are not purged
        '../../packages/auth-core/src/**/*.{js,ts,jsx,tsx}',
    ],
    darkMode: 'class',
    theme: {
        extend: {
            fontFamily: {
                sans: ['var(--font-sans)'],
                mono: ['var(--font-mono)'],
            },
            gridTemplateColumns: {
                12: 'repeat(12, minmax(0, 1fr))',
            },
            keyframes: {
                hide: { from: { opacity: '1' }, to: { opacity: '0' } },
                slideDownAndFade: {
                    from: { opacity: '0', transform: 'translateY(-6px)' },
                    to: { opacity: '1', transform: 'translateY(0)' },
                },
                slideUpAndFade: {
                    from: { opacity: '0', transform: 'translateY(6px)' },
                    to: { opacity: '1', transform: 'translateY(0)' },
                },
                fadeIn: {
                    from: { opacity: '0', transform: 'translateY(4px)' },
                    to: { opacity: '1', transform: 'translateY(0)' },
                },
            },
            animation: {
                hide: 'hide 150ms cubic-bezier(0.16, 1, 0.3, 1)',
                slideDownAndFade: 'slideDownAndFade 200ms cubic-bezier(0.16, 1, 0.3, 1)',
                slideUpAndFade: 'slideUpAndFade 200ms cubic-bezier(0.16, 1, 0.3, 1)',
                fadeIn: 'fadeIn 300ms ease-out both',
            },
        },
    },
    plugins: [forms],
};

export default config;
