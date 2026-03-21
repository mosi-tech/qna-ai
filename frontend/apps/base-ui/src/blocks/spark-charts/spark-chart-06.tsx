import React from 'react';
import { Card } from '../../tremor/components/Card';
import { SparkAreaChart } from '../../tremor/components/SparkChart';
import { cx } from '../../lib/utils';

export interface SparkChart06Item {
    name: string;
    description: string;
    /** Display value (e.g. index level, price) */
    value?: string;
    category: string;
    change: string;
    changeType: 'positive' | 'negative' | 'neutral';
}

export interface SparkChart06Props {
    data: Array<Record<string, any>>;
    /** Key used for x-axis lookup; defaults to 'date' */
    dataIndex?: string;
    items: SparkChart06Item[];
  className?: string;
}

/**
 * SparkChart06: Market Indices (Grid Layout)
 * Direct implementation matching tremor block structure (spark-chart-06.tsx)
 * Finance: Major market index comparison (Dow Jones, SMI, S&P 500)
 */
export const SparkChart06: React.FC<SparkChart06Props> = ({ data, dataIndex = 'date', items ,
    className
}) => {
    return (
        <dl className={cx('grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3', className)}>
            {items.map((item) => (
                <Card
                    key={item.name}
                    className="flex items-center justify-between space-x-4"
                >
                    <div className="truncate">
                        <div className="flex items-center space-x-1.5">
                            <dt className="text-sm font-medium text-gray-900 dark:text-gray-50">
                                {item.name}
                            </dt>
                            <span
                                className={cx(
                                    item.changeType === 'positive'
                                        ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-400/10 dark:text-emerald-400'
                                        : item.changeType === 'negative'
                                            ? 'bg-red-100 text-red-800 dark:bg-red-400/10 dark:text-red-400'
                                            : 'bg-gray-100 text-gray-700 dark:bg-gray-400/10 dark:text-gray-400',
                                    'inline-flex items-center rounded px-2 py-0.5 text-xs',
                                )}
                            >
                                {item.change}
                            </span>
                        </div>
                        <dd className="mt-0.5 truncate text-xs text-gray-500 dark:text-gray-500">
                            {item.description}
                        </dd>
                        {item.value && (
                            <dd className="mt-0.5 truncate text-sm font-semibold text-gray-900 dark:text-gray-50">
                                {item.value}
                            </dd>
                        )}
                    </div>
                    <SparkAreaChart
                        data={data}
                        index={dataIndex}
                        categories={[item.category]}
                        fill="solid"
                        colors={(item.changeType === 'positive' ? ['emerald'] : item.changeType === 'negative' ? ['red'] : ['gray']) as any}
                        className="h-20 w-32 flex-none"
                    />
                </Card>
            ))}
        </dl>
    );
};
