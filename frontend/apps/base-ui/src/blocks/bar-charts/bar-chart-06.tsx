import React from 'react';
import { AvailableChartColorsKeys } from '../../lib/chartUtils';
import { BarChart } from '../../tremor/components/BarChart';
import { RadioCardGroup, RadioCardItem } from '../../tremor/components/RadioCardGroup';
import { defaultCurrencyFormatter } from '../../lib/financeFormatters';
import { cx } from '../../lib/utils';

export interface TabItem {
    name: string;
    value: string;
}

export interface BarChartDataItem {
    [key: string]: string | number;
}

export interface BarChart06Props {
    tabs?: TabItem[];
    data?: BarChartDataItem[];
    title?: string;
    description?: string;
    indexField?: string;
    categories?: string[];
    colors?: AvailableChartColorsKeys[];
    valueFormatter?: (value: number) => string;
  className?: string;
}

export const BarChart06: React.FC<BarChart06Props> = ({
    tabs = [],
    data = [],
    title,
    description,
    indexField = 'date',
    categories = ['Value'],
    colors = ['blue'] as AvailableChartColorsKeys[],
    valueFormatter = defaultCurrencyFormatter,

    className
}) => {
    const [selected, setSelected] = React.useState<string>(tabs[0]?.name || '');

    const filteredData = data.map((item) => ({
        [indexField]: item[indexField],
        [categories[0]]: item[selected] || 0,
    }));

    return (
        <div className={cx(className)}>
            {title && <h3 className="font-semibold text-gray-900 dark:text-gray-50">{title}</h3>}
            {description && <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">{description}</p>}
            <RadioCardGroup value={selected} onValueChange={setSelected} className="mt-6 flex gap-3">
                {tabs.map((tab) => (
                    <RadioCardItem key={tab.name} value={tab.name}>
                        <p className="text-sm font-medium">{tab.name}</p>
                        <p className="text-base font-bold">{tab.value}</p>
                    </RadioCardItem>
                ))}
            </RadioCardGroup>
            <BarChart
                data={filteredData}
                index={indexField}
                categories={categories}
                colors={colors as AvailableChartColorsKeys[]}
                valueFormatter={valueFormatter}
                yAxisWidth={50}
                className="mt-10 hidden !h-72 sm:block"
            />
            <BarChart
                data={filteredData}
                index={indexField}
                categories={categories}
                colors={colors as AvailableChartColorsKeys[]}
                valueFormatter={valueFormatter}
                startEndOnly={true}
                showYAxis={false}
                className="mt-6 !h-56 sm:hidden"
            />
        </div>
    );
};
