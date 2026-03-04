'use client';

import React from 'react';
import {
    RiArrowRightSLine,
    RiCheckLine,
    RiErrorWarningFill,
    RiEyeFill,
} from '@remixicon/react';

import { cx } from '../../lib/utils';
import { Card } from '../../tremor/components/Card';
import { MetricItem, CommonFormattingProps } from './index';

export interface KpiCard11Props extends CommonFormattingProps {
    metrics?: MetricItem[];
    cols?: number;
    valueFormatter?: (value: number | string) => string;
    className?: string;
}

export interface RegionMetadataItem extends MetricItem {
    status?: 'within' | 'observe' | 'critical';
    goalsAchieved?: number;
    href?: string;
}

const getStatusIcon = (status?: string) => {
    switch (status) {
        case 'within':
            return <RiCheckLine className="size-4 shrink-0" aria-hidden={true} />;
        case 'observe':
            return <RiEyeFill className="size-4 shrink-0" aria-hidden={true} />;
        case 'critical':
            return <RiErrorWarningFill className="size-4 shrink-0" aria-hidden={true} />;
        default:
            return null;
    }
};

const RegionMetadataCard: React.FC<{ item: RegionMetadataItem; valueFormatter?: (value: number | string) => string; valueSizeClass: string }> = ({
    item,
    valueFormatter,
    valueSizeClass,
}) => {
    const getIconBgColor = (status?: string) => {
        switch (status) {
            case 'within':
                return 'bg-emerald-500 text-white dark:bg-emerald-500';
            case 'observe':
                return 'bg-yellow-500 text-white dark:bg-yellow-500';
            case 'critical':
                return 'bg-red-500 text-white dark:bg-red-500';
            default:
                return 'bg-gray-500 text-white dark:bg-gray-500';
        }
    };

    const getStatusTextColor = (status?: string) => {
        switch (status) {
            case 'within':
                return 'text-emerald-800 dark:text-emerald-500';
            case 'observe':
                return 'text-yellow-800 dark:text-yellow-500';
            case 'critical':
                return 'text-red-800 dark:text-red-500';
            default:
                return 'text-gray-800 dark:text-gray-500';
        }
    };

    const Component = item.href ? 'a' : 'div';

    return (
        <Card className={valueSizeClass === 'text-xl' ? 'p-3' : valueSizeClass === 'text-2xl' ? 'p-4' : ''}>
            <Component href={item.href} className={item.href ? 'block no-underline focus:outline-none' : ''}>
                <dt className="text-sm font-medium text-gray-500 dark:text-gray-500">
                    {item.name}
                </dt>
                <dd className={cx(valueSizeClass, 'font-semibold text-gray-900 dark:text-gray-50')}>
                    {valueFormatter ? valueFormatter(item.stat ?? '') : item.stat}
                </dd>
                <div className="group relative mt-6 flex items-center space-x-4 rounded-md bg-gray-100/60 p-2 hover:bg-gray-100 dark:bg-gray-800/60 hover:dark:bg-gray-800">
                    <div className="flex w-full items-center justify-between truncate">
                        <div className="flex items-center space-x-3">
                            <span
                                className={cx(
                                    getIconBgColor(item.status),
                                    'flex size-9 shrink-0 items-center justify-center rounded',
                                )}
                            >
                                {getStatusIcon(item.status)}
                            </span>
                            <dd>
                                <p className="text-sm text-gray-500 dark:text-gray-500">
                                    {item.href && (
                                        <span className="absolute inset-0" aria-hidden={true} />
                                    )}
                                    {item.goalsAchieved}/5 goals
                                </p>
                                <p
                                    className={cx(
                                        getStatusTextColor(item.status),
                                        'text-sm font-medium',
                                    )}
                                >
                                    {item.status}
                                </p>
                            </dd>
                        </div>
                        <RiArrowRightSLine
                            className="size-5 shrink-0 text-gray-400 group-hover:text-gray-500 dark:text-gray-400 group-hover:dark:text-gray-500"
                            aria-hidden={true}
                        />
                    </div>
                </div>
            </Component>
        </Card>
    );
};

const MetricCardGrid: React.FC<{
    items: MetricItem[];
    renderCard: (item: MetricItem) => React.ReactNode;
    cols?: number;
    className?: string;
}> = ({ items, renderCard, cols = 3, className = '' }) => {
    const gridColsClass =
        cols === 1
            ? 'grid-cols-1'
            : cols === 2
                ? 'grid-cols-1 sm:grid-cols-2'
                : cols === 4
                    ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4'
                    : cols === 5
                        ? 'grid-cols-1 sm:grid-cols-3 lg:grid-cols-5'
                        : 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3';

    return (
        <dl className={cx('grid gap-6', gridColsClass, className)}>
            {items.map((item, index) => (
                <div key={`${item.name}-${index}`}>{renderCard(item)}</div>
            ))}
        </dl>
    );
};

export const KpiCard11: React.FC<KpiCard11Props> = ({
    metrics = [],
    cols = 3,
    valueFormatter,

    className
}) => {
    if (!metrics || metrics.length === 0) {
        return null;
    }
    const valueSizeClass = cols >= 5 ? 'text-xl' : cols === 4 ? 'text-2xl' : 'text-3xl';

    return (
        <MetricCardGrid
            className={className}
            items={metrics}
            renderCard={(item) => (
                <RegionMetadataCard item={item as RegionMetadataItem} valueFormatter={valueFormatter} valueSizeClass={valueSizeClass} />
            )}
            cols={cols}
        />
    );
};
