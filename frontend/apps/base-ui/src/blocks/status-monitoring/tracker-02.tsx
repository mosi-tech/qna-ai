'use client';

import React, { useState } from 'react';
import { RiArrowDownSLine, RiCheckboxCircleFill } from '@remixicon/react';

import { cx } from '../../lib/utils';

import { Card } from '../../tremor/components/Card';
import { Tracker } from '../../tremor/components/Tracker';

/** Convenience union of built-in status values. Prop types accept any string. */
export type Tracker02Status = 'Operational' | 'Downtime' | 'Inactive';

export interface Tracker02DataItem {
    tooltip: string;
    status: string;
}

export interface LegendItem {
    status: string;
    label: string;
}

export interface Tracker02Props {
    data?: Tracker02DataItem[];
    serviceName?: string;
    displayName?: string;
    uptime?: string;
    /** Label appended after the uptime value, e.g. "uptime", "availability", "SLA" */
    uptimeLabel?: string;
    status?: string;
    daysAgoLabel?: string;
    todayLabel?: string;
    detailsLabel?: string;
    detailsTitle?: string;
    /** Supports rich content (string or ReactNode) */
    detailsContent?: React.ReactNode;
    /** Legend items — extend freely for any domain-specific statuses */
    legendItems?: LegendItem[];
    /** Custom status → Tailwind color class map. Extend or replace the defaults. */
    statusColorMap?: Record<string, string>;
    className?: string;
}

const defaultColorMapping: Record<string, string> = {
    Operational: 'bg-emerald-500 dark:bg-emerald-500',
    Downtime: 'bg-red-500 dark:bg-red-500',
    Inactive: 'bg-gray-300 dark:bg-gray-700',
};

/**
 * Tracker02: Status with Expandable Details
 * Shows service status with collapsible incident details
 */
export const Tracker02 = ({
    data = [],
    serviceName = 'Service',
    displayName = 'service.example.com',
    uptime = '99.7%',
    uptimeLabel = 'uptime',
    status = 'Operational',
    daysAgoLabel = '90 days ago',
    todayLabel = 'Today',
    detailsLabel = 'Show details',
    detailsTitle = 'Incident details',
    detailsContent = 'No additional details available.',
    legendItems = [
        { status: 'Operational', label: 'Operational' },
        { status: 'Downtime', label: 'Downtime' },
        { status: 'Inactive', label: 'Inactive' },
    ],
    statusColorMap = defaultColorMapping,
    className = '',
}: Tracker02Props) => {
    const combinedData = data.map((item) => {
        return {
            ...item,
            color: statusColorMap[item.status] ?? 'bg-gray-300 dark:bg-gray-700',
        };
    });

    const badgeColor = statusColorMap[status] ?? 'bg-gray-300 dark:bg-gray-700';

    const [showContent, setShowContent] = useState(false);

    return (
        <div className={cx(className)}>
            <Card>
                <div className="flex items-center justify-between">
                    <h3 className="font-medium text-gray-900 dark:text-gray-50">
                        {serviceName}
                    </h3>
                    <span
                        tabIndex={1}
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
                    <div className="flex items-center space-x-1.5">
                        <RiCheckboxCircleFill
                            className="size-5 shrink-0 text-emerald-500"
                            aria-hidden={true}
                        />
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-50">
                            {displayName}
                        </p>
                    </div>
                    <div className="flex items-center space-x-2">
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-50">
                            {uptime} {uptimeLabel}
                        </p>
                        <button
                            className="hidden sm:inline-flex sm:items-center sm:space-x-1.5"
                            onClick={() => setShowContent(!showContent)}
                        >
                            <span className="text-sm font-medium text-blue-500 dark:text-blue-500">
                                {detailsLabel}
                            </span>
                            <RiArrowDownSLine
                                className={cx(
                                    showContent ? 'rotate-180' : '',
                                    'size-5 transform text-blue-500 transition-transform dark:text-blue-500',
                                )}
                                aria-hidden={true}
                            />
                        </button>
                    </div>
                </div>
                {showContent && (
                    <div className="mt-3 rounded-md bg-gray-100 p-4 dark:bg-gray-800">
                        <h3 className="text-sm font-medium text-gray-900 dark:text-gray-50">
                            {detailsTitle}
                        </h3>
                        <p className="mt-2 text-sm/6 text-gray-600 dark:text-gray-400">
                            {detailsContent}
                        </p>
                    </div>
                )}
                <Tracker data={combinedData} className="mt-4 hidden w-full lg:flex" />
                <Tracker
                    data={combinedData.slice(30, 90)}
                    className="mt-3 hidden w-full sm:flex lg:hidden"
                />
                <Tracker
                    data={combinedData.slice(60, 90)}
                    className="mt-3 flex w-full sm:hidden"
                />
                <div className="mt-3 flex items-center justify-between text-sm text-gray-500 dark:text-gray-500">
                    <span className="hidden lg:block">{daysAgoLabel}</span>
                    <span className="hidden sm:block lg:hidden">60 days ago</span>
                    <span className="sm:hidden">30 days ago</span>
                    <span>{todayLabel}</span>
                </div>
                <div className="mt-6 flex flex-wrap items-center gap-2">
                    {legendItems.map((item) => (
                        <span
                            key={item.status}
                            className="inline-flex items-center gap-x-2 rounded-md bg-gray-100 px-2 py-0.5 text-sm text-gray-600 dark:bg-gray-800 dark:text-gray-300"
                        >
                            <span
                                className={`size-2 rounded-full ${statusColorMap[item.status] ?? 'bg-gray-300 dark:bg-gray-700'}`}
                                aria-hidden={true}
                            />
                            {item.label}
                        </span>
                    ))}
                </div>
            </Card>
        </div>
    );
};
