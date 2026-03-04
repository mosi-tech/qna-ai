'use client';

import React from 'react';
import { CommonFormattingProps } from './index';
import { Card } from '../../tremor/components/Card';
import { ProgressCircle } from '../../tremor/components/ProgressCircle';
import { cx } from '../../lib/utils';

export interface DetailLabel {
    label: string;
    percentage: string;
    color: string;
}

export interface MetricItem {
    title: string;
    primaryLabel: DetailLabel;
    secondaryLabel: DetailLabel;
    progressValue: number;
}

export interface KpiCard26Props extends CommonFormattingProps {
    metrics?: MetricItem[];
    valueFormatter?: (value: number | string) => string;
  className?: string;
}

export const KpiCard26: React.FC<KpiCard26Props> = ({ metrics = [], valueFormatter ,
    className
}) => {
    if (!metrics || metrics.length === 0) {
        return null;
    }

    return (
        <div className={cx('obfuscate', className)}>
            <dl className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {metrics.map((metric) => (
                    <Card key={metric.title}>
                        <dt className="text-sm font-medium text-gray-900 dark:text-gray-50">
                            {metric.title}
                        </dt>
                        <div className="mt-4 flex flex-nowrap items-center justify-between gap-y-4">
                            <dd className="space-y-3">
                                <div>
                                    <div className="flex items-center gap-2">
                                        <span
                                            className={`size-2.5 shrink-0 rounded-sm ${metric.primaryLabel.color}`}
                                            aria-hidden="true"
                                        />
                                        <span className="text-sm text-gray-900 dark:text-gray-50">
                                            {metric.primaryLabel.label}
                                        </span>
                                    </div>
                                    <span className="mt-1 block text-2xl font-semibold text-gray-900 dark:text-gray-50">
                                        {metric.primaryLabel.percentage}
                                    </span>
                                </div>
                                <div>
                                    <div className="flex items-center gap-2">
                                        <span
                                            className={`size-2.5 shrink-0 rounded-sm ${metric.secondaryLabel.color}`}
                                            aria-hidden="true"
                                        />
                                        <span className="text-sm text-gray-900 dark:text-gray-50">
                                            {metric.secondaryLabel.label}
                                        </span>
                                    </div>
                                    <span className="mt-1 block text-2xl font-semibold text-gray-900 dark:text-gray-50">
                                        {metric.secondaryLabel.percentage}
                                    </span>
                                </div>
                            </dd>
                            <ProgressCircle value={metric.progressValue} radius={45} strokeWidth={7} />
                        </div>
                    </Card>
                ))}
            </dl>
        </div>
    );
};
