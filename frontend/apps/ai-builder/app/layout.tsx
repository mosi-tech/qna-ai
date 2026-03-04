import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
    title: 'AI Dashboard Builder',
    description: 'Natural-language dashboard generation powered by base-ui blocks',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
    return (
        <html lang="en">
            <body className="h-screen overflow-hidden flex flex-col bg-slate-50 dark:bg-slate-950 font-sans antialiased">
                {children}
            </body>
        </html>
    );
}
