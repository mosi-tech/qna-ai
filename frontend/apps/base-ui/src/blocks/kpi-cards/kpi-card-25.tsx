'use client';

import React from 'react';
import { CommonFormattingProps } from './index';
import { Card } from '../../tremor/components/Card';
import { CategoryBar } from '../../tremor/components/CategoryBar';
import { cx } from '../../lib/utils';

export interface DetailItem {
    percentage: string;
    label: string;
    color: string;
}

export interface MetricCard {
    title: string;
    value: string;
    values: number[];
    details: DetailItem[];
}

export interface KpiCard25Props extends CommonFormattingProps {
    cards?: MetricCard[];
    valueFormatter?: (value: number | string) => string;
  className?: string;
}

export const KpiCard25: React.FC<KpiCard25Props> = ({ cards = [], valueFormatter ,
    className
}) => {
    if (!cards || cards.length === 0) {
        return null;
    }

    return (
        <div className={cx('obfuscate', className)}>
            <dl className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {cards.map((card) => (
                    <Card key={card.title}>
                        <dt className="text-sm font-medium text-gray-900 dark:text-gray-50">
                            {card.title}
                        </dt>
                        <dd className="mt-1 text-3xl font-semibold text-gray-900 dark:text-gray-50">
                            {card.value}
                        </dd>
                        <CategoryBar
                            values={card.values}
                            className="mt-6"
                            colors={['blue', 'gray', 'red']}
                            showLabels={false}
                        />
                        <ul
                            role="list"
                            className="mt-4 flex flex-wrap gap-x-8 gap-y-4 text-sm"
                        >
                            {card.details.map((detail) => (
                                <li key={detail.label}>
                                    <span className="text-base font-semibold text-gray-900 dark:text-gray-50">
                                        {detail.percentage}
                                    </span>
                                    <div className="flex items-center gap-2">
                                        <span
                                            className={`size-2.5 shrink-0 rounded-sm ${detail.color}`}
                                            aria-hidden="true"
                                        />
                                        <span className="text-sm text-gray-900 dark:text-gray-50">
                                            {detail.label}
                                        </span>
                                    </div>
                                </li>
                            ))}
                        </ul>
                    </Card>
                ))}
            </dl>
        </div>
    );
};
