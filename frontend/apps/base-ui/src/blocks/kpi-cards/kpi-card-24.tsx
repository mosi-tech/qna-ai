'use client';

import React from 'react';
import { RiCashLine, RiLinksLine, RiSafeLine } from '@remixicon/react';
import { CommonFormattingProps } from './index';
import { cx } from '../../lib/utils';
import { Card } from '../../tremor/components/Card';

export interface MetricDetailItem {
    [key: string]: number | string;
}

export interface MetricCardItem {
    name: string;
    stat: string;
    change: string;
    changeType: 'positive' | 'negative';
    icon: React.ComponentType<any>;
    top3: MetricDetailItem;
}

export interface KpiCard24Props extends CommonFormattingProps {
    metrics?: MetricCardItem[];
    valueFormatter?: (value: number | string) => string;
  className?: string;
}

export const KpiCard24: React.FC<KpiCard24Props> = ({ metrics = [], valueFormatter ,
    className
}) => {
    if (!metrics || metrics.length === 0) {
        return null;
    }

    return (
        <div className={cx('obfuscate', className)}>
            <dl className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {metrics.map((item) => (
                    <Card key={item.name}>
                        <dt className="flex flex-nowrap items-center gap-2 text-sm font-semibold text-gray-500 dark:text-gray-400">
                            <div className="rounded-md p-1.5 shadow ring-1 ring-black/5 dark:ring-white/15">
                                <item.icon className="size-5 shrink-0" aria-hidden="true" />
                            </div>
                            <span>{item.name}</span>
                        </dt>
                        <dd className="mt-3 flex items-baseline justify-between space-x-2.5">
                            <span className="text-3xl font-semibold text-gray-900 dark:text-gray-50">
                                {item.stat}
                            </span>
                            <span
                                className={cx(
                                    item.changeType === 'positive'
                                        ? 'text-emerald-700 dark:text-emerald-500'
                                        : 'text-red-700 dark:text-red-500',
                                    'text-sm font-medium',
                                )}
                            >
                                {item.change}
                            </span>
                        </dd>
                        <div className="mt-5 flex flex-col gap-3">
                            {Object.entries(item.top3).map(([title, value]) => (
                                <div key={title} className="flex justify-between text-sm">
                                    <div className="truncate text-gray-600 dark:text-gray-400">
                                        {title}
                                    </div>
                                    <div className="font-medium text-gray-900 dark:text-gray-50">
                                        {typeof value === 'number' && item.name !== 'Engagement'
                                            ? `$${value.toLocaleString()}`
                                            : `${value}${item.name === 'Engagement' ? '%' : ''}`}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </Card>
                ))}
            </dl>
        </div>
    );
};
