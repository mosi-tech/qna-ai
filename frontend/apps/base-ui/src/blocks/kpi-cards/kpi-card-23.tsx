'use client';

import React from 'react';
import { RiArrowRightUpLine } from '@remixicon/react';
import { CommonFormattingProps } from './index';
import { cx } from '../../lib/utils';
import { Card } from '../../tremor/components/Card';
import { CategoryBar } from '../../tremor/components/CategoryBar';

export interface SalesChannel {
    channel: string;
    share: number;
    revenue: string;
    color: string;
    href: string;
}

export interface KpiCard23Props extends CommonFormattingProps {
    title?: string;
    totalSales?: string;
    subtitle?: string;
    channels?: SalesChannel[];
    valueFormatter?: (value: number | string) => string;
  className?: string;
}

export const KpiCard23: React.FC<KpiCard23Props> = ({
    title = 'Total sales',
    totalSales = '$292,400',
    subtitle = 'Sales channel distribution',
    channels = [],
    valueFormatter,

    className
}) => {
    if (!channels || channels.length === 0) {
        return null;
    }
    return (
        <div className={cx('obfuscate', className)}>
            <div className="sm:mx-auto sm:max-w-2xl">
                <h3 className="text-sm text-gray-500 dark:text-gray-500">
                    {title}
                </h3>
                <p className="text-3xl font-semibold text-gray-900 dark:text-gray-50">
                    {totalSales}
                </p>
                <h4 className="mt-4 text-sm text-gray-500 dark:text-gray-500">
                    {subtitle}
                </h4>
                <CategoryBar
                    values={channels.map(c => c.share)}
                    colors={['blue', 'amber', 'cyan', 'gray']}
                    showLabels={false}
                    className="mt-4"
                />
                <dl className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2">
                    {channels.map((item) => (
                        <Card key={item.channel} className="group rounded-md px-3 py-2">
                            <div className="flex items-center space-x-2">
                                <span
                                    className={cx(item.color, 'size-2.5 rounded-sm')}
                                    aria-hidden={true}
                                />
                                <dt className="text-sm text-gray-500 dark:text-gray-500">
                                    <a href={item.href} className="focus:outline-none">
                                        {/* Extend link to entire card */}
                                        <span className="absolute inset-0" aria-hidden={true} />
                                        {item.channel}
                                    </a>
                                </dt>
                            </div>
                            <dd className="mt-1 text-sm text-gray-900 dark:text-gray-50">
                                <span className="font-semibold">{item.share}%</span> &#8729;{' '}
                                {item.revenue}
                            </dd>
                            <span
                                className="pointer-events-none absolute right-2 top-2 text-gray-400 group-hover:text-gray-500 dark:text-gray-600 group-hover:dark:text-gray-500"
                                aria-hidden={true}
                            >
                                <RiArrowRightUpLine className="size-4" aria-hidden={true} />
                            </span>
                        </Card>
                    ))}
                </dl>
            </div>
        </div>
    );
};
