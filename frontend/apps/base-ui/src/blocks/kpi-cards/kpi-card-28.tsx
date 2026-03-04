'use client';

import React from 'react';
import { CommonFormattingProps } from './index';
import { Card } from '../../tremor/components/Card';
import { cx } from '../../lib/utils';

export interface Metric {
    label: string;
    value: string;
    change: string;
    changeType: 'positive' | 'positive';
}

export interface IssueItem {
    category: string;
    totalCount: number;
    percentage: number;
}

export interface KpiCard28Props extends CommonFormattingProps {
    metrics?: Metric[][];
    issues?: IssueItem[];
    valueFormatter?: (value: number | string) => string;
  className?: string;
}

export const KpiCard28: React.FC<KpiCard28Props> = ({ metrics = [], issues = [], valueFormatter ,
    className
}) => {
    if (!metrics || metrics.length === 0) {
        return null;
    }

    return (
        <div className={cx('obfuscate', className)}>
            <div className="mt-8 grid grid-cols-1 gap-5 lg:grid-cols-8">
                <Card className="lg:col-span-5">
                    <p className="font-semibold text-gray-900 dark:text-gray-50">
                        Cohort Statistics
                    </p>
                    <dl className="mt-4 grid grid-cols-1 gap-6 md:grid-cols-3">
                        {metrics.map((column, colIndex) => (
                            <div key={colIndex} className="space-y-6">
                                {column.map((metric) => (
                                    <div key={metric.label}>
                                        <dt className="text-sm text-gray-500 dark:text-gray-500">
                                            {metric.label}
                                        </dt>
                                        <dd className="mt-1 flex items-baseline">
                                            <span className="text-2xl font-semibold text-gray-900 dark:text-gray-50">
                                                {metric.value}
                                            </span>
                                            <span className="ml-2 text-sm text-emerald-600 dark:text-emerald-500">
                                                {metric.change}
                                            </span>
                                        </dd>
                                    </div>
                                ))}
                            </div>
                        ))}
                    </dl>
                </Card>

                <Card className="lg:col-span-3">
                    <p className="font-semibold text-gray-900 dark:text-gray-50">
                        Top Issues
                    </p>
                    <ol className="mt-4 divide-y divide-gray-200 dark:divide-gray-800">
                        {issues.map((issue, index) => (
                            <li
                                key={issue.category}
                                className="flex items-center justify-between py-2"
                            >
                                <div className="flex items-center gap-2">
                                    <span className="text-sm text-gray-500 dark:text-gray-400">
                                        {index + 1}.
                                    </span>
                                    <span className="text-sm font-medium text-gray-900 dark:text-gray-50">
                                        {issue.category}
                                    </span>
                                </div>
                                <div className="text-sm tabular-nums text-gray-600 dark:text-gray-400">
                                    {issue.percentage}% ({issue.totalCount.toLocaleString()})
                                </div>
                            </li>
                        ))}
                    </ol>
                </Card>
            </div>
        </div>
    );
};
