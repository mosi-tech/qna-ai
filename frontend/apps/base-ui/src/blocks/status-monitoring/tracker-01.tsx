import React from 'react';
import { RiCheckboxCircleFill } from '@remixicon/react';
import { Card } from '../../tremor/components/Card';
import { Tracker } from '../../tremor/components/Tracker';
import { cx } from '../../lib/utils';

/** Convenience union of built-in status values. Prop types accept any string. */
export type Tracker01StatusType = 'Operational' | 'Downtime' | 'Degraded' | 'Inactive' | 'Maintenance';

export interface Tracker01DataItem {
    tooltip: string;
    status: string;
}

export interface Tracker01Props {
    data?: Tracker01DataItem[];
    serviceName?: string;
    displayName?: string;
    uptime?: string;
    /** Label appended after the uptime value, e.g. "uptime", "availability", "SLA" */
    uptimeLabel?: string;
    status?: string;
    daysAgoLabel?: string;
    todayLabel?: string;
    /** Custom status → Tailwind color class map. Extend or replace the defaults. */
    statusColorMap?: Record<string, string>;
  className?: string;
}

const defaultStatusColorMap: Record<string, string> = {
    Operational: 'bg-emerald-500 dark:bg-emerald-500',
    Downtime: 'bg-red-500 dark:bg-red-500',
    Degraded: 'bg-yellow-500 dark:bg-yellow-500',
    Inactive: 'bg-gray-300 dark:bg-gray-700',
    Maintenance: 'bg-blue-500 dark:bg-blue-500',
};

/**
 * Tracker01: Simple Status Card with 90-day history
 * Shows service status, uptime percentage, and responsive tracker grid
 */
export const Tracker01: React.FC<Tracker01Props> = ({
    data = [] as Tracker01DataItem[],
    serviceName = 'Service',
    displayName = 'Service',
    uptime = '99.9%',
    uptimeLabel = 'uptime',
    status = 'Operational',
    daysAgoLabel = '90 days ago',
    todayLabel = 'Today',
    statusColorMap = defaultStatusColorMap,

    className
}) => {
    const combinedData = data.map((item) => ({
        ...item,
        color: statusColorMap[item.status] ?? 'bg-gray-300 dark:bg-gray-700',
    }));

    const badgeColor = statusColorMap[status] ?? 'bg-gray-300 dark:bg-gray-700';

    return (
        <Card className={cx(className)}>
            <div className="flex items-center justify-between">
                <h3 className="font-medium text-gray-900 dark:text-gray-50">
                    {serviceName}
                </h3>
                <span
                    className="inline-flex items-center gap-2 rounded-full px-3 py-1 text-sm text-gray-700 ring-1 ring-inset ring-gray-200 dark:text-gray-300 dark:ring-gray-800"
                >
                    <span
                        className={`-ml-0.5 size-2 rounded-full ${badgeColor}`}
                        aria-hidden={true}
                    />
                    {status}
                </span>
            </div>
            <div className="mt-8 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                    <RiCheckboxCircleFill
                        className="size-5 shrink-0 text-emerald-500 dark:text-emerald-500"
                        aria-hidden={true}
                    />
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-50">
                        {displayName}
                    </p>
                </div>
                <p className="text-sm font-medium text-gray-900 dark:text-gray-50">
                    {uptime} {uptimeLabel}
                </p>
            </div>
            <Tracker data={combinedData} className="mt-4 hidden w-full lg:flex" />
            <Tracker
                data={combinedData.slice(Math.max(0, combinedData.length - 60))}
                className="mt-3 hidden w-full sm:flex lg:hidden"
            />
            <Tracker
                data={combinedData.slice(Math.max(0, combinedData.length - 30))}
                className="mt-3 flex w-full sm:hidden"
            />
            <div className="mt-3 flex items-center justify-between text-sm text-gray-500 dark:text-gray-500">
                <span className="hidden lg:block">{daysAgoLabel}</span>
                <span className="hidden sm:block lg:hidden">60 days ago</span>
                <span className="sm:hidden">30 days ago</span>
                <span>{todayLabel}</span>
            </div>
        </Card>
    );
};
