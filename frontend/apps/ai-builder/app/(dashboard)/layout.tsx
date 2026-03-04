import { createDashboardLayout } from '@ui-gen/auth-core/pages/dashboard-layout';
import { RiLayoutGridLine } from '@remixicon/react';

export default createDashboardLayout({
    appName: 'AI Builder',
    extraNavItems: [
        { href: '/builder', label: 'Builder', icon: RiLayoutGridLine },
    ],
});
