import React from 'react';
import { Card } from '../../tremor/components/Card';
import { LineChart } from '../../tremor/components/LineChart';
import { cx } from '../../lib/utils';

/** Generic per-series summary row. 'label' is the series/group name; 'detail' is any supporting descriptor (venue, ISIN, address, etc.). */
export interface ChartGroupItem {
    location: string;
    address: string;
    color: string;
    type: string;
    total: string;
    change: string;
    changeType: 'positive' | 'negative';
}

/** @deprecated Use ChartGroupItem instead. */
export type LocationSummaryItem = ChartGroupItem;

export interface LineChart03Props {
    data: Array<Record<string, any>>;
    headline: string;
    headlineValue: string;
    categories: string[];
    colors?: string[];
    summary: ChartGroupItem[];
    valueFormatter?: (num: number) => string;
    /** Key in the data objects used as the x-axis index. Defaults to 'date'. */
    indexField?: string;
  className?: string;
}

/**
 * LineChart03: Geographic performance with responsive desktop/mobile views
 */
export const LineChart03: React.FC<LineChart03Props> = ({
    data,
    headline,
    headlineValue,
    categories,
    colors = ['blue', 'violet', 'fuchsia'],
    summary,
    valueFormatter = (v) => Intl.NumberFormat('en').format(v),
    indexField = 'date',

    className
}) => {
    return (
        <div className={cx('obfuscate', className)}>
            <Card className="sm:mx-auto sm:max-w-lg">
                {/* Headline */}
                <h4 className="text-sm text-gray-500 dark:text-gray-500">
                    {headline}
                </h4>
                <p className="text-3xl font-semibold text-gray-900 dark:text-gray-50">
                    {headlineValue}
                </p>

                {/* Desktop Chart */}
                <LineChart
                    data={data}
                    index={indexField}
                    categories={categories}
                    colors={colors as any}
                    showLegend={false}
                    showYAxis={false}
                    valueFormatter={valueFormatter}
                    className="mt-5 hidden !h-44 sm:block"
                />

                {/* Mobile Chart */}
                <LineChart
                    data={data}
                    index={indexField}
                    categories={categories}
                    colors={colors as any}
                    showLegend={false}
                    startEndOnly={true}
                    showYAxis={false}
                    valueFormatter={valueFormatter}
                    className="mt-5 !h-44 sm:hidden"
                />

                {/* Location Summary */}
                <ul className="mt-4 w-full divide-y divide-gray-200 truncate text-sm text-gray-500 dark:divide-gray-800 dark:text-gray-500">
                    {summary.map((item) => (
                        <li
                            key={item.location}
                            className="flex items-center justify-between py-2.5"
                        >
                            <div>
                                <div className="flex items-center space-x-2">
                                    <span
                                        className={cx(
                                            item.color,
                                            'h-[3px] w-3.5 shrink-0 rounded-full',
                                        )}
                                        aria-hidden={true}
                                    />
                                    <span className="text-sm font-medium text-gray-900 dark:text-gray-50">
                                        {item.location}
                                    </span>
                                    <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs font-medium text-gray-500 dark:bg-gray-400/10 dark:text-gray-400">
                                        {item.type}
                                    </span>
                                </div>
                                <span className="text-xs text-gray-500 dark:text-gray-500">
                                    {item.address}
                                </span>
                            </div>
                            <div className="text-right">
                                <p
                                    className={cx(
                                        item.changeType === 'positive'
                                            ? 'text-emerald-700 dark:text-emerald-500'
                                            : 'text-red-700 dark:text-red-500',
                                        'text-sm font-medium',
                                    )}
                                >
                                    {item.change}
                                </p>
                                <span className="text-xs text-gray-500 dark:text-gray-500">
                                    {item.total}
                                </span>
                            </div>
                        </li>
                    ))}
                </ul>
            </Card>
        </div>
    );
};

// Example usage with sample data
