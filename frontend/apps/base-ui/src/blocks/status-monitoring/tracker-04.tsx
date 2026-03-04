import React from 'react';
import { RiCheckboxCircleFill } from '@remixicon/react';
import { Card } from '../../tremor/components/Card';
import { Tracker } from '../../tremor/components/Tracker';
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from '../../tremor/components/Accordion';
import { cx } from '../../lib/utils';

/** Convenience union of built-in status values. Prop types accept any string. */
export type Tracker04StatusType = 'Operational' | 'Downtime' | 'Degraded' | 'Inactive' | 'Maintenance';

export interface Tracker04DataItem {
    tooltip: string;
    status: string;
}

export interface TrackerIncident {
    date: string;
    duration: string;
}

export interface Tracker04Props {
    data?: Tracker04DataItem[];
    serviceName?: string;
    uptime?: string;
    /** Label appended after the uptime value, e.g. "uptime", "availability", "SLA" */
    uptimeLabel?: string;
    status?: string;
    daysAgoLabel?: string;
    todayLabel?: string;
    incidents?: TrackerIncident[];
    /** Section heading above the incidents list */
    incidentsSectionTitle?: string;
    /**
     * When true, wraps the incident log in a collapsible accordion instead of
     * always-visible list. Useful when incident history is long (>5 entries).
     * Default: false
     */
    collapsibleIncidents?: boolean;
    /** Legend items — extend freely for any domain-specific statuses */
    legendItems?: Array<{ status: string; label: string }>;
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
 * Tracker04: Market Data Feed Status
 * Shows service with sparse downtime events
 */
export const Tracker04: React.FC<Tracker04Props> = ({
    data = [],
    serviceName = 'Service',
    uptime = '99.9%',
    uptimeLabel = 'uptime',
    status = 'Operational',
    daysAgoLabel = '90 days ago',
    todayLabel = 'Today',
    incidents = [],
    incidentsSectionTitle = 'Incident overview',
    collapsibleIncidents = false,
    legendItems = [
        { status: 'Operational', label: 'Operational' },
        { status: 'Downtime', label: 'Downtime' },
        { status: 'Maintenance', label: 'Maintenance' },
    ],
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
                        {serviceName}
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

            {/* Legend */}
            <div className="mt-6 flex flex-wrap items-center gap-2">
                {legendItems.map((item) => (
                    <span
                        key={item.status}
                        className="inline-flex items-center gap-x-2 rounded-md bg-gray-100 px-2 py-0.5 text-sm text-gray-600 dark:bg-gray-800 dark:text-gray-300"
                    >
                        <span
                            className={`size-2 rounded-full ${statusColorMap[item.status] ?? 'bg-gray-300 dark:bg-gray-700'}`}
                        />
                        {item.label}
                    </span>
                ))}
            </div>

            {/* Incidents */}
            {incidents && incidents.length > 0 && (
                collapsibleIncidents ? (
                    <Accordion type="single" collapsible className="mt-6">
                        <AccordionItem
                            value="incidents"
                            className="rounded-md border border-gray-200 px-4 dark:border-gray-800"
                        >
                            <AccordionTrigger>
                                {incidentsSectionTitle} ({incidents.length})
                            </AccordionTrigger>
                            <AccordionContent>
                                <ul className="mt-2 w-full divide-y divide-gray-200 text-sm text-gray-500 dark:divide-gray-800 dark:text-gray-500">
                                    {incidents.map((incident, idx) => (
                                        <li
                                            key={idx}
                                            className="flex w-full items-center justify-between py-2"
                                        >
                                            <span>{incident.date}</span>
                                            <span>{incident.duration}</span>
                                        </li>
                                    ))}
                                </ul>
                            </AccordionContent>
                        </AccordionItem>
                    </Accordion>
                ) : (
                    <div className="mt-6">
                        <h4 className="mb-3 text-sm font-medium text-gray-900 dark:text-gray-50">
                            {incidentsSectionTitle}
                        </h4>
                        <ul className="divide-y divide-gray-200 dark:divide-gray-800">
                            {incidents.map((incident, idx) => (
                                <li
                                    key={idx}
                                    className="flex items-center justify-between py-2 text-sm text-gray-600 dark:text-gray-400"
                                >
                                    <span>{incident.date}</span>
                                    <span>{incident.duration}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                )
            )}
        </Card>
    );
};
