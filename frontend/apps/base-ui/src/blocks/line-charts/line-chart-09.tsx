import React from 'react';
import { LineChart } from '../../tremor/components/LineChart';
import { Button } from '../../tremor/components/Button';
import { DateRangePicker, type DateRange } from '../../tremor';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../tremor/components/Tabs';
import type { RangeTab } from './line-chart-07';
import { cx } from '../../lib/utils';

export interface LineChart09Props {
    data: Array<Record<string, any>>;
    title: string;
    subtitle: string;
    categories?: string[];
    colors?: string[];
    valueFormatter?: (num: number) => string;
    firstAvailableDate?: Date;
    lastAvailableDate?: Date;
    /** Key in the data objects used as the x-axis index. Must be an ISO date string (YYYY-MM-DD) for date filtering to work. Defaults to 'date'. */
    indexField?: string;
    /** Label for the compare action button. Defaults to 'Compare asset'. */
    compareLabel?: string;
    /** Callback fired when the compare button is clicked. */
    onCompare?: () => void;
    /**
     * Optional compact range selector rendered as solid pill tabs.
     * When provided, replaces the DateRangePicker filterbar with simple period pills.
     * When omitted, the existing DateRangePicker filterbar is shown.
     */
    rangeTabs?: RangeTab[];
  className?: string;
}

/**
 * LineChart09: Date-range filtered chart with filterbar and dual responsive display
 */
export const LineChart09: React.FC<LineChart09Props> = ({
    data,
    title,
    subtitle,
    categories = ['ETF Shares Vital', 'Vitainvest Core', 'iShares Tech Growth'],
    colors = ['blue', 'violet', 'fuchsia'],
    valueFormatter = (number) => Intl.NumberFormat('en').format(number),
    firstAvailableDate = new Date(2023, 7, 1),
    lastAvailableDate = new Date(2023, 8, 26),
    indexField = 'date',
    compareLabel = 'Compare asset',
    onCompare,
    rangeTabs,

    className
}) => {
    const [dateRange, setDateRange] = React.useState<DateRange>({
        from: firstAvailableDate,
        to: lastAvailableDate,
    });

    const filterData = (
        startDate: Date | undefined,
        endDate: Date | undefined,
        dataset: any[],
    ) => {
        if (!startDate || !endDate) {
            return dataset;
        }

        const startStr = startDate.toISOString().split('T')[0];
        const endStr = endDate.toISOString().split('T')[0];

        return dataset.filter((item) => {
            const itemDate = item[indexField];
            return itemDate >= startStr && itemDate <= endStr;
        });
    };

    const filteredData = filterData(dateRange.from, dateRange.to, data);

    return (
        <div className={cx('obfuscate', className)}>
            <h3 className="font-medium text-gray-900 dark:text-gray-50">
                {title}
            </h3>
            <p className="mt-1 text-sm/6 text-gray-500 dark:text-gray-500">
                {subtitle}
            </p>
            {rangeTabs && rangeTabs.length > 0 ? (
                <Tabs defaultValue={rangeTabs[0].name}>
                    <div className="mt-4 flex justify-end">
                        <TabsList variant="solid">
                            {rangeTabs.map((t) => (
                                <TabsTrigger key={t.name} value={t.name}>
                                    {t.name}
                                </TabsTrigger>
                            ))}
                        </TabsList>
                    </div>
                    {rangeTabs.map((t) => (
                        <TabsContent key={t.name} value={t.name}>
                            <LineChart
                                data={t.dataRange}
                                index={indexField}
                                categories={categories}
                                colors={colors as any}
                                valueFormatter={valueFormatter}
                                yAxisWidth={60}
                                onValueChange={() => { }}
                                tickGap={10}
                                className="mt-8 hidden !h-96 sm:block"
                            />
                            <LineChart
                                data={t.dataRange}
                                index={indexField}
                                categories={categories}
                                colors={colors as any}
                                valueFormatter={valueFormatter}
                                showYAxis={false}
                                showLegend={false}
                                startEndOnly={true}
                                tickGap={10}
                                className="mt-8 !h-72 sm:hidden"
                            />
                        </TabsContent>
                    ))}
                </Tabs>
            ) : (
                <>
                    <div className="mt-4 rounded-lg bg-gray-50 p-4 ring-1 ring-inset ring-gray-200 dark:bg-gray-900 dark:ring-gray-800 sm:p-6">
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-50">
                            Filterbar
                        </p>
                        <div className="mt-4 flex flex-col gap-4 md:flex-row md:items-center">
                            <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                                <Button className="w-full py-2 sm:w-fit" onClick={onCompare}>{compareLabel}</Button>
                                <DateRangePicker
                                    value={dateRange}
                                    onChange={(dr) => setDateRange(dr || { from: firstAvailableDate, to: lastAvailableDate })}
                                    fromDate={firstAvailableDate}
                                    toDate={lastAvailableDate}
                                />
                            </div>
                            <Button
                                variant="ghost"
                                className="border border-gray-300 py-2 text-gray-600 hover:bg-transparent hover:text-gray-900 dark:border-gray-800 dark:text-gray-400 hover:dark:bg-transparent hover:dark:text-gray-50 md:border-transparent md:dark:border-transparent"
                                onClick={() =>
                                    setDateRange({
                                        from: firstAvailableDate,
                                        to: lastAvailableDate,
                                    })
                                }
                            >
                                Reset datepicker
                            </Button>
                        </div>
                    </div>
                    <LineChart
                        data={filteredData}
                        index={indexField}
                        categories={categories}
                        colors={colors as any}
                        valueFormatter={valueFormatter}
                        yAxisWidth={60}
                        onValueChange={() => { }}
                        tickGap={10}
                        className="mt-8 hidden !h-96 sm:block"
                    />
                    <LineChart
                        data={filteredData}
                        index={indexField}
                        categories={categories}
                        colors={colors as any}
                        valueFormatter={valueFormatter}
                        showYAxis={false}
                        showLegend={false}
                        startEndOnly={true}
                        tickGap={10}
                        className="mt-8 !h-72 sm:hidden"
                    />
                </>
            )}
        </div>
    );
};
