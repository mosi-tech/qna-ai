import React from 'react';
import CountUp from 'react-countup';

import { AvailableChartColorsKeys } from '../../lib/chartUtils';
import { BarChart } from '../../tremor/components/BarChart';
import { defaultCurrencyFormatter } from '../../lib/financeFormatters';
import { cx } from '../../lib/utils';

export interface DataPoint {
    [key: string]: string | number;
}

interface ValueChangeHandler {
    eventType: 'bar' | 'category';
    categoryClicked?: string;
}

export interface BarChart07Props {
    data?: DataPoint[];
    indexField?: string;
    categories?: string[];
    colors?: AvailableChartColorsKeys[];
    valueFormatter?: (value: number) => string;
    /** Label for the average metric (e.g., "Average Value", "Total BPM") */
    metricLabel?: string;
  className?: string;
}

export const BarChart07: React.FC<BarChart07Props> = ({
    data = [],
    indexField = 'date',
    categories = [],
    colors = ['blue', 'violet'] as AvailableChartColorsKeys[],
    valueFormatter = defaultCurrencyFormatter,
    metricLabel = 'Average Value',

    className
}) => {
    const initialAverageValue =
        data.reduce((sum, dataPoint) => {
            categories.forEach((category) => {
                sum += (dataPoint[category] as number) || 0;
            });
            return sum;
        }, 0) / (data.length * categories.length) || 0;

    const [values, setValues] = React.useState<{ start: number; end: number }>({
        start: 0,
        end: initialAverageValue,
    });

    function onValueChangeHandler(value: ValueChangeHandler) {
        if (!value || !value.categoryClicked) {
            return;
        }
        const category = value.categoryClicked;

        switch (value.eventType) {
            case 'bar':
                setValues((prev) => ({
                    start: prev.end,
                    end: (data[0][category] as number) || 0,
                }));
                break;
            case 'category':
                const averageCategoryValue =
                    data.reduce(
                        (sum, dataPoint) => sum + ((dataPoint[category] as number) || 0),
                        0,
                    ) / data.length || 0;

                setValues((prev) => ({
                    start: prev.end,
                    end: averageCategoryValue,
                }));
                break;
            default:
                setValues((prev) => ({
                    start: prev.end,
                    end: initialAverageValue,
                }));
                break;
        }
    }

    return (
        <div className={cx(className)}>
            <h3 className="text-sm text-gray-500 dark:text-gray-500">{metricLabel}</h3>
            <p className="text-3xl font-bold text-gray-900 dark:text-gray-50">
                <CountUp start={values.start} end={values.end} duration={0.6} />
            </p>
            <BarChart
                className="mt-6 hidden !h-80 sm:block"
                data={data}
                index={indexField}
                categories={categories}
                colors={colors as AvailableChartColorsKeys[]}
                valueFormatter={valueFormatter}
                yAxisWidth={60}
                onValueChange={(value) =>
                    onValueChangeHandler(value as ValueChangeHandler)
                }
            />
            <BarChart
                className="mt-6 !h-72 sm:hidden"
                data={data}
                index={indexField}
                categories={categories}
                colors={colors as AvailableChartColorsKeys[]}
                valueFormatter={valueFormatter}
                showYAxis={false}
                onValueChange={(value) =>
                    onValueChangeHandler(value as ValueChangeHandler)
                }
            />
        </div>
    );
};
