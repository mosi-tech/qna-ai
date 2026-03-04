'use client';

import React from 'react';
import { CommonFormattingProps } from './index';
import { cx } from '../../lib/utils';
import { Card } from '../../tremor/components/Card';
import { CategoryBar } from '../../tremor/components/CategoryBar';

export interface TokenDetail {
    name: string;
    value: string;
}

export interface CategoryItem {
    name: string;
    total: string;
    split: number[];
    details: TokenDetail[];
}

export interface KpiCard21Props extends CommonFormattingProps {
    metrics?: CategoryItem[];
    valueFormatter?: (value: number | string) => string;
  className?: string;
}

type LegendItem = 'Completion tokens' | 'Prompt tokens';

const legendColor: Record<LegendItem, string> = {
    'Completion tokens': 'bg-sky-500 dark:bg-sky-500',
    'Prompt tokens': 'bg-violet-500 dark:bg-violet-500',
};

export const KpiCard21: React.FC<KpiCard21Props> = ({ metrics = [], valueFormatter ,
    className
}) => {
    if (!metrics || metrics.length === 0) {
        return null;
    }

    return (
        <div className={cx('obfuscate', className)}>
            <dl className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                {metrics.map((item) => (
                    <Card key={item.name}>
                        <dt className="truncate text-sm text-gray-500 dark:text-gray-500">
                            {item.name}
                        </dt>
                        <dd className="mt-1 text-3xl font-semibold text-gray-900 dark:text-gray-50">
                            {item.total}
                        </dd>
                        <CategoryBar
                            values={item.split}
                            colors={['cyan', 'violet']}
                            showLabels={false}
                            className="mt-6"
                        />
                        <ul
                            role="list"
                            className="mt-4 flex flex-wrap items-center gap-x-4 gap-y-2"
                        >
                            {item.details.map((category) => (
                                <li key={category.name} className="flex items-center space-x-2">
                                    <span
                                        className={cx(
                                            legendColor[category.name as LegendItem],
                                            'size-3 shrink-0 rounded-sm',
                                        )}
                                        aria-hidden={true}
                                    />
                                    <span className="text-sm text-gray-500 dark:text-gray-500">
                                        <span className="font-medium text-gray-700 dark:text-gray-300">
                                            {category.value}
                                        </span>{' '}
                                        {category.name}
                                    </span>
                                </li>
                            ))}
                        </ul>
                    </Card>
                ))}
            </dl>
        </div>
    );
};
