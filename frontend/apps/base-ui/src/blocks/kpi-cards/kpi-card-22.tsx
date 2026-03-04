'use client';

import React from 'react';
import { CommonFormattingProps } from './index';
import { Card } from '../../tremor/components/Card';
import { ProgressBar } from '../../tremor/components/ProgressBar';
import { cx } from '../../lib/utils';

export interface DetailItem {
    name: string;
    value: string;
    percentageValue: number;
}

export interface TokenMetric {
    name: string;
    total: string;
    details: DetailItem[];
}

export interface KpiCard22Props extends CommonFormattingProps {
    metrics?: TokenMetric[];
    valueFormatter?: (value: number | string) => string;
  className?: string;
}

export const KpiCard22: React.FC<KpiCard22Props> = ({ metrics = [], valueFormatter ,
    className
}) => {
    if (!metrics || metrics.length === 0) {
        return null;
    }

    return (
        <div className={cx('obfuscate', className)}>
            <dl className="grid grid-cols-1 gap-6 md:grid-cols-2">
                {metrics.map((category) => (
                    <Card key={category.name}>
                        <dt className="text-sm text-gray-500 dark:text-gray-500">
                            {category.name}
                        </dt>
                        <dd className="mt-1 text-3xl font-semibold text-gray-900 dark:text-gray-50">
                            {category.total}
                        </dd>
                        <div className="mt-4 space-y-3">
                            {category.details.map((item) => (
                                <dd
                                    key={item.name}
                                    className="lg:flex lg:items-center lg:space-x-3"
                                >
                                    <p className="flex shrink-0 items-center justify-between space-x-2 text-sm lg:w-5/12">
                                        <span className="truncate text-gray-500 dark:text-gray-500">
                                            {item.name}
                                        </span>
                                        <span className="whitespace-nowrap font-semibold text-gray-900 dark:text-gray-50">
                                            {item.value}{' '}
                                            <span className="font-normal">
                                                ({item.percentageValue}&#37;)
                                            </span>
                                        </span>
                                    </p>
                                    <ProgressBar
                                        value={item.percentageValue}
                                        className="mt-2 lg:mt-0"
                                    />
                                </dd>
                            ))}
                        </div>
                    </Card>
                ))}
            </dl>
        </div>
    );
};
