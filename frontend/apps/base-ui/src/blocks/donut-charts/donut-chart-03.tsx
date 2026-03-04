import React from 'react';
import { DonutChart } from '../../tremor';
import { type AvailableChartColorsKeys } from '../../lib/chartUtils';
import { Card } from '../../tremor/components/Card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../tremor/components/Tabs';
import { cx } from '../../lib/utils';

export interface DataItem {
    name: string;
    value: number;
    share?: string;
    color?: string;
    [key: string]: any;
}

export interface TabDataSet {
    id: string;
    label: string;
    data: DataItem[];
}

export interface DonutChart03Props {
    title: string;
    tabSets: TabDataSet[];
    description?: string;
    colors?: AvailableChartColorsKeys[];
    showLabel?: boolean;
    showTooltip?: boolean;
    amountLabel?: string;
    valueFormatter?: (value: number) => string;
  className?: string;
}

const defaultCurrencyFormatter = (number: number) => {
    return '$' + Intl.NumberFormat('us').format(number).toString();
};

export const DonutChart03: React.FC<DonutChart03Props> = ({
    title,
    tabSets,
    description = 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr.',
    colors = ['cyan', 'blue', 'emerald', 'violet', 'fuchsia'] as const,
    showLabel = true,
    showTooltip = false,
    amountLabel = 'Amount / Share',
    valueFormatter = defaultCurrencyFormatter,

    className
}) => {
    return (
        <Card className={cx('!p-0 sm:mx-auto sm:max-w-lg', className)}>
            <div className="px-6 pt-6">
                <h3 className="text-sm font-medium text-gray-900 dark:text-gray-50">
                    {title}
                </h3>
                {description && (
                    <p className="mt-1 text-sm/6 text-gray-500 dark:text-gray-500">
                        {description}
                    </p>
                )}
            </div>
            <Tabs defaultValue={tabSets[0]?.id}>
                <TabsList className="px-6 pt-6">
                    {tabSets.map((tabSet) => (
                        <TabsTrigger key={tabSet.id} value={tabSet.id}>
                            {tabSet.label}
                        </TabsTrigger>
                    ))}
                </TabsList>
                <div className="px-6 pb-6">
                    {tabSets.map((tabSet) => (
                        <TabsContent key={tabSet.id} value={tabSet.id}>
                            <DonutChart
                                className="mx-auto mt-8"
                                data={tabSet.data}
                                value="value"
                                category="name"
                                valueFormatter={valueFormatter}
                                showLabel={showLabel}
                                showTooltip={showTooltip}
                                colors={colors as AvailableChartColorsKeys[]}
                            />
                            <p className="mt-8 flex items-center justify-between text-xs text-gray-500 dark:text-gray-500">
                                <span>{tabSet.label}</span>
                                <span>{amountLabel}</span>
                            </p>
                            <ul
                                role="list"
                                className="mt-2 divide-y divide-gray-200 text-sm text-gray-500 dark:divide-gray-800 dark:text-gray-500"
                            >
                                {tabSet.data.map((item) => (
                                    <li
                                        key={item.name}
                                        className="relative flex items-center justify-between py-2"
                                    >
                                        <div className="flex items-center space-x-2.5 truncate">
                                            <span
                                                className={cx(
                                                    item.color || 'bg-gray-300 dark:bg-gray-600',
                                                    'size-2.5 shrink-0 rounded-sm'
                                                )}
                                                aria-hidden={true}
                                            />
                                            <span className="truncate dark:text-gray-300">
                                                {item.name}
                                            </span>
                                        </div>
                                        <p className="flex items-center space-x-2">
                                            <span className="font-medium tabular-nums text-gray-900 dark:text-gray-50">
                                                {valueFormatter(item.value)}
                                            </span>
                                            {item.share && (
                                                <span className="rounded-md bg-gray-100 px-1.5 py-0.5 text-xs font-medium tabular-nums text-gray-700 dark:bg-gray-800 dark:text-gray-300">
                                                    {item.share}
                                                </span>
                                            )}
                                        </p>
                                    </li>
                                ))}
                            </ul>
                        </TabsContent>
                    ))}
                </div>
            </Tabs>
        </Card>
    );
};
