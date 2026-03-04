import type { Metadata } from 'next';
import BuilderApp from '@/components/BuilderApp';

export const metadata: Metadata = {
    title: 'AI Dashboard Builder',
    description: 'Describe a dashboard in natural language and watch it build itself in real time.',
};

export default function BuilderPage() {
    return <BuilderApp />;
}
