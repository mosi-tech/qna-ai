'use client';

import { Card } from '../../tremor/components/Card';
import { Tracker } from '../../tremor/components/Tracker';
import { cx } from '../../lib/utils';

/** Convenience union of built-in status values. Prop types accept any string. */
export type Tracker03Status = 'Operational' | 'Downtime' | 'Inactive' | 'Degraded';

export interface Tracker03DataItem {
    tooltip: string;
    status: string;
}

/** A generic tag/label item, e.g. a data source, instrument, or feed name */
export interface TagItem {
    name: string;
}

export interface Tracker03Props {
    data?: Tracker03DataItem[];
    headerLabel?: string;
    /** List of tagged items to display (data sources, feeds, instruments, etc.) */
    items?: TagItem[];
    runningLabel?: string;
    nextRunLabel?: string;
    viewMoreLabel?: string;
    /** Custom status → Tailwind color class map. Extend or replace the defaults. */
    statusColorMap?: Record<string, string>;
    className?: string;
}

const defaultColorMapping: Record<string, string> = {
    Operational: 'bg-emerald-500 dark:bg-emerald-500',
    Downtime: 'bg-red-500 dark:bg-red-500',
    Degraded: 'bg-amber-500 dark:bg-amber-500',
    Inactive: 'bg-gray-300 dark:bg-gray-700',
};

/**
 * Tracker03: Database Scan Progress
 * Shows status of scanned databases with 90-day history
 */
export const Tracker03 = ({
    data = [],
    headerLabel = 'Monitored sources:',
    items = [
        { name: 'source-1' },
        { name: 'source-2' },
        { name: 'source-3' },
    ],
    runningLabel = 'Running',
    nextRunLabel = 'Next run: 1 hour',
    viewMoreLabel = 'View more →',
    statusColorMap = defaultColorMapping,
    className = '',
}: Tracker03Props) => {
    const combinedData = data.map((item) => {
        return {
            ...item,
            color: statusColorMap[item.status] ?? 'bg-gray-300 dark:bg-gray-700',
        };
    });

    return (
        <div className={cx(className)}>
            <Card>
                <div className="flex-wrap items-center gap-2 sm:flex">
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-50">
                        {headerLabel}
                    </p>
                    <div className="mt-2 flex flex-wrap items-center gap-2 sm:mt-0">
                        {items.map((item) => (
                            <span
                                key={item.name}
                                className="rounded px-3 py-1 font-mono text-xs text-gray-700 ring-1 ring-inset ring-gray-200 dark:text-gray-300 dark:ring-gray-800"
                            >
                                {item.name}
                            </span>
                        ))}
                    </div>
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
                <div className="mt-6 items-center justify-between sm:flex">
                    <div className="flex items-center gap-2">
                        <div className="flex items-center gap-2">
                            <span
                                className="shrink-0 animate-pulse rounded-full bg-emerald-500/30 p-1 dark:bg-emerald-500/30"
                                aria-hidden={true}
                            >
                                <span className="block size-2 rounded-full bg-emerald-500 dark:bg-emerald-500" />
                            </span>
                            <span className="text-sm font-medium text-gray-900 dark:text-gray-50">
                                {runningLabel}
                            </span>
                        </div>
                        <span className="text-sm text-gray-500 dark:text-gray-500">/</span>
                        <span className="truncate text-sm text-gray-700 dark:text-gray-300">
                            {nextRunLabel}
                        </span>
                    </div>
                    <a
                        href="#"
                        className="mt-4 block text-sm font-medium text-blue-500 dark:text-blue-500 sm:mt-0"
                    >
                        {viewMoreLabel}
                    </a>
                </div>
            </Card>
        </div>
    );
};
