import React from 'react';
import { AvailableChartColorsKeys } from '../../../lib/chartUtils';

import { BarChart01, BarChartDataItem as BarChart01DataItem } from '../bar-chart-01';
import { BarChart02, TabItem as BarChart02TabItem, BarChartDataItem as BarChart02DataItem } from '../bar-chart-02';
import { BarChart03, BarChartDataItem as BarChart03DataItem } from '../bar-chart-03';
import { BarChart04, BarChartDataItem as BarChart04DataItem, SummaryTabItem as BarChart04SummaryTabItem } from '../bar-chart-04';
import { BarChart05, BarChartDataItem as BarChart05DataItem, SummaryTabItem as BarChart05SummaryTabItem } from '../bar-chart-05';
import { BarChart06, TabItem as BarChart06TabItem, BarChartDataItem as BarChart06DataItem } from '../bar-chart-06';
import { BarChart07, DataPoint } from '../bar-chart-07';
import { BarChart08, BarChartDataItem as BarChart08DataItem, SummaryMetric } from '../bar-chart-08';
import { BarChart09, TabConfig } from '../bar-chart-09';
import { BarChart10, BarChartDataItem as BarChart10DataItem, MetricConfig } from '../bar-chart-10';
import { BarChart11, BarChartDataItem as BarChart11DataItem, formatPercentage } from '../bar-chart-11';
import { BarChart12, BarChartDataItem as BarChart12DataItem } from '../bar-chart-12';

// ─── BarChart01Example ────────────────────────────────────────────────────────

export const BarChart01Example = () => {
    const data: BarChart01DataItem[] = [
        { date: 'Jan 23', 'This Year': 68560, 'Last Year': 28560 },
        { date: 'Feb 23', 'This Year': 70320, 'Last Year': 30320 },
        { date: 'Mar 23', 'This Year': 80233, 'Last Year': 70233 },
        { date: 'Apr 23', 'This Year': 55123, 'Last Year': 45123 },
        { date: 'May 23', 'This Year': 56000, 'Last Year': 80600 },
        { date: 'Jun 23', 'This Year': 100000, 'Last Year': 85390 },
        { date: 'Jul 23', 'This Year': 85390, 'Last Year': 45340 },
        { date: 'Aug 23', 'This Year': 80100, 'Last Year': 70120 },
        { date: 'Sep 23', 'This Year': 75090, 'Last Year': 69450 },
        { date: 'Oct 23', 'This Year': 71080, 'Last Year': 63345 },
        { date: 'Nov 23', 'This Year': 61210, 'Last Year': 100330 },
        { date: 'Dec 23', 'This Year': 60143, 'Last Year': 45321 },
    ];

    const valueFormatter = (value: number) =>
        new Intl.NumberFormat('en-US', {
            maximumFractionDigits: 0,
            notation: 'compact',
            compactDisplay: 'short',
            style: 'currency',
            currency: 'USD',
        }).format(value);

    return (
        <BarChart01
            data={data}
            title="Sales overview"
            description="Lorem ipsum dolor sit amet, consetetur sadipscing elitr."
            valueFormatter={valueFormatter}
        />
    );
};

// ─── BarChart02Example ────────────────────────────────────────────────────────

export const BarChart02Example = () => {
    const tabs: BarChart02TabItem[] = [
        { name: 'Europe', value: '$1.9M', color: 'bg-blue-500 dark:bg-blue-500' },
        { name: 'Asia', value: '$4.1M', color: 'bg-cyan-500 dark:bg-cyan-500' },
        { name: 'North America', value: '$10.1M', color: 'bg-violet-500 dark:bg-violet-500' },
    ];

    const data: BarChart02DataItem[] = [
        { date: 'Jan 23', Europe: 68560, Asia: 28560, 'North America': 34940 },
        { date: 'Feb 23', Europe: 70320, Asia: 30320, 'North America': 44940 },
        { date: 'Mar 23', Europe: 80233, Asia: 70233, 'North America': 94560 },
        { date: 'Apr 23', Europe: 55123, Asia: 45123, 'North America': 84320 },
        { date: 'May 23', Europe: 56000, Asia: 80600, 'North America': 71120 },
        { date: 'Jun 23', Europe: 100000, Asia: 85390, 'North America': 61340 },
        { date: 'Jul 23', Europe: 85390, Asia: 45340, 'North America': 71260 },
        { date: 'Aug 23', Europe: 80100, Asia: 70120, 'North America': 61210 },
        { date: 'Sep 23', Europe: 75090, Asia: 69450, 'North America': 61110 },
        { date: 'Oct 23', Europe: 71080, Asia: 63345, 'North America': 41430 },
        { date: 'Nov 23', Europe: 68041, Asia: 61210, 'North America': 100330 },
        { date: 'Dec 23', Europe: 60143, Asia: 45321, 'North America': 80780 },
    ];

    const valueFormatter = (value: number) =>
        new Intl.NumberFormat('en-US', {
            maximumFractionDigits: 0,
            notation: 'compact',
            compactDisplay: 'short',
            style: 'currency',
            currency: 'USD',
        }).format(value);

    return (
        <BarChart02
            tabs={tabs}
            data={data}
            title="Sales breakdown by regions"
            description="Check sales of top 3 regions over time"
            valueFormatter={valueFormatter}
        />
    );
};

// ─── BarChart03Example ────────────────────────────────────────────────────────

export const BarChart03Example = () => {
    const data: BarChart03DataItem[] = [
        { date: 'Jan 23', 'This Year': 68560, 'Last Year': 28560 },
        { date: 'Feb 23', 'This Year': 70320, 'Last Year': 30320 },
        { date: 'Mar 23', 'This Year': 80233, 'Last Year': 70233 },
        { date: 'Apr 23', 'This Year': 55123, 'Last Year': 45123 },
        { date: 'May 23', 'This Year': 56000, 'Last Year': 80600 },
        { date: 'Jun 23', 'This Year': 100000, 'Last Year': 85390 },
        { date: 'Jul 23', 'This Year': 85390, 'Last Year': 45340 },
        { date: 'Aug 23', 'This Year': 80100, 'Last Year': 70120 },
        { date: 'Sep 23', 'This Year': 75090, 'Last Year': 69450 },
        { date: 'Oct 23', 'This Year': 71080, 'Last Year': 63345 },
        { date: 'Nov 23', 'This Year': 61210, 'Last Year': 100330 },
        { date: 'Dec 23', 'This Year': 60143, 'Last Year': 45321 },
    ];

    const valueFormatter = (value: number) =>
        new Intl.NumberFormat('en-US', {
            maximumFractionDigits: 0,
            notation: 'compact',
            compactDisplay: 'short',
            style: 'currency',
            currency: 'USD',
        }).format(value);

    return (
        <BarChart03
            data={data}
            title="Sales overview"
            description="Lorem ipsum dolor sit amet, consetetur sadipscing elitr."
            valueFormatter={valueFormatter}
        />
    );
};

// ─── BarChart04Example ────────────────────────────────────────────────────────

export const BarChart04Example = () => {
    const valueFormatter = (number: number) =>
        `${Intl.NumberFormat('us').format(number).toString()}`;

    const dataEurope: BarChart04DataItem[] = [
        { date: 'Jan 23', Successful: 12, Refunded: 0, Fraudulent: 1 },
        { date: 'Feb 23', Successful: 24, Refunded: 1, Fraudulent: 1 },
        { date: 'Mar 23', Successful: 48, Refunded: 4, Fraudulent: 4 },
        { date: 'Apr 23', Successful: 24, Refunded: 2, Fraudulent: 3 },
        { date: 'May 23', Successful: 34, Refunded: 0, Fraudulent: 0 },
        { date: 'Jun 23', Successful: 26, Refunded: 0, Fraudulent: 0 },
        { date: 'Jul 23', Successful: 12, Refunded: 0, Fraudulent: 0 },
        { date: 'Aug 23', Successful: 38, Refunded: 2, Fraudulent: 0 },
        { date: 'Sep 23', Successful: 23, Refunded: 1, Fraudulent: 0 },
        { date: 'Oct 23', Successful: 20, Refunded: 0, Fraudulent: 0 },
        { date: 'Nov 23', Successful: 24, Refunded: 0, Fraudulent: 0 },
        { date: 'Dec 23', Successful: 21, Refunded: 8, Fraudulent: 1 },
    ];

    const dataAsia: BarChart04DataItem[] = [
        { date: 'Jan 23', Successful: 31, Refunded: 1, Fraudulent: 2 },
        { date: 'Feb 23', Successful: 32, Refunded: 2, Fraudulent: 1 },
        { date: 'Mar 23', Successful: 44, Refunded: 3, Fraudulent: 3 },
        { date: 'Apr 23', Successful: 23, Refunded: 2, Fraudulent: 4 },
        { date: 'May 23', Successful: 35, Refunded: 1, Fraudulent: 1 },
        { date: 'Jun 23', Successful: 48, Refunded: 1, Fraudulent: 1 },
        { date: 'Jul 23', Successful: 33, Refunded: 1, Fraudulent: 1 },
        { date: 'Aug 23', Successful: 38, Refunded: 3, Fraudulent: 0 },
        { date: 'Sep 23', Successful: 41, Refunded: 2, Fraudulent: 0 },
        { date: 'Oct 23', Successful: 39, Refunded: 1, Fraudulent: 0 },
        { date: 'Nov 23', Successful: 32, Refunded: 1, Fraudulent: 1 },
        { date: 'Dec 23', Successful: 19, Refunded: 5, Fraudulent: 1 },
    ];

    const dataNorthAmerica: BarChart04DataItem[] = [
        { date: 'Jan 23', Successful: 45, Refunded: 2, Fraudulent: 3 },
        { date: 'Feb 23', Successful: 52, Refunded: 1, Fraudulent: 2 },
        { date: 'Mar 23', Successful: 68, Refunded: 4, Fraudulent: 4 },
        { date: 'Apr 23', Successful: 54, Refunded: 2, Fraudulent: 3 },
        { date: 'May 23', Successful: 64, Refunded: 0, Fraudulent: 1 },
        { date: 'Jun 23', Successful: 56, Refunded: 0, Fraudulent: 0 },
        { date: 'Jul 23', Successful: 45, Refunded: 1, Fraudulent: 2 },
        { date: 'Aug 23', Successful: 60, Refunded: 3, Fraudulent: 1 },
        { date: 'Sep 23', Successful: 58, Refunded: 2, Fraudulent: 0 },
        { date: 'Oct 23', Successful: 59, Refunded: 2, Fraudulent: 1 },
        { date: 'Nov 23', Successful: 62, Refunded: 1, Fraudulent: 0 },
        { date: 'Dec 23', Successful: 54, Refunded: 3, Fraudulent: 1 },
    ];

    const summary: BarChart04SummaryTabItem[] = [
        {
            name: 'Europe',
            total: 301,
            change: '+2.3%',
            changeType: 'positive',
            data: dataEurope,
            details: [
                { name: 'Successful', value: 263 },
                { name: 'Refunded', value: 18 },
                { name: 'Fraudulent', value: 10 },
            ],
        },
        {
            name: 'Asia',
            total: 758,
            change: '-0.3%',
            changeType: 'negative',
            data: dataAsia,
            details: [
                { name: 'Successful', value: 405 },
                { name: 'Refunded', value: 21 },
                { name: 'Fraudulent', value: 15 },
            ],
        },
    ];

    return (
        <BarChart04
            summary={summary}
            title="Online payments"
            categories={['Successful', 'Refunded', 'Fraudulent']}
            colors={['blue', 'violet', 'fuchsia'] as AvailableChartColorsKeys[]}
            detailItemColorMap={{
                'Successful': 'bg-blue-500 dark:bg-blue-500',
                'Refunded': 'bg-violet-500 dark:bg-violet-500',
                'Fraudulent': 'bg-fuchsia-500 dark:bg-fuchsia-500',
            }}
            valueFormatter={valueFormatter}
        />
    );
};

// ─── BarChart05Example ────────────────────────────────────────────────────────

export const BarChart05Example = () => {
    const valueFormatter = (number: number) =>
        `${Intl.NumberFormat('us').format(number).toString()}`;

    const dataEurope: BarChart05DataItem[] = [
        { date: 'Jan 23', Successful: 12, Refunded: 0, Fraudulent: 1 },
        { date: 'Feb 23', Successful: 24, Refunded: 1, Fraudulent: 1 },
        { date: 'Mar 23', Successful: 48, Refunded: 4, Fraudulent: 4 },
        { date: 'Apr 23', Successful: 24, Refunded: 2, Fraudulent: 3 },
        { date: 'May 23', Successful: 34, Refunded: 0, Fraudulent: 0 },
        { date: 'Jun 23', Successful: 26, Refunded: 0, Fraudulent: 0 },
        { date: 'Jul 23', Successful: 12, Refunded: 0, Fraudulent: 0 },
        { date: 'Aug 23', Successful: 38, Refunded: 2, Fraudulent: 0 },
        { date: 'Sep 23', Successful: 23, Refunded: 1, Fraudulent: 0 },
        { date: 'Oct 23', Successful: 20, Refunded: 0, Fraudulent: 0 },
        { date: 'Nov 23', Successful: 24, Refunded: 0, Fraudulent: 0 },
        { date: 'Dec 23', Successful: 21, Refunded: 8, Fraudulent: 1 },
    ];

    const dataNorthAmerica: BarChart05DataItem[] = [
        { date: 'Jan 23', Successful: 65, Refunded: 2, Fraudulent: 1 },
        { date: 'Feb 23', Successful: 78, Refunded: 3, Fraudulent: 2 },
        { date: 'Mar 23', Successful: 55, Refunded: 5, Fraudulent: 6 },
        { date: 'Apr 23', Successful: 79, Refunded: 4, Fraudulent: 3 },
        { date: 'May 23', Successful: 41, Refunded: 1, Fraudulent: 1 },
        { date: 'Jun 23', Successful: 32, Refunded: 1, Fraudulent: 1 },
        { date: 'Jul 23', Successful: 54, Refunded: 0, Fraudulent: 0 },
        { date: 'Aug 23', Successful: 45, Refunded: 3, Fraudulent: 1 },
        { date: 'Sep 23', Successful: 75, Refunded: 2, Fraudulent: 0 },
        { date: 'Oct 23', Successful: 62, Refunded: 1, Fraudulent: 0 },
        { date: 'Nov 23', Successful: 55, Refunded: 3, Fraudulent: 1 },
        { date: 'Dec 23', Successful: 66, Refunded: 8, Fraudulent: 4 },
    ];

    const dataAsia: BarChart05DataItem[] = [
        { date: 'Jan 23', Successful: 31, Refunded: 1, Fraudulent: 2 },
        { date: 'Feb 23', Successful: 32, Refunded: 2, Fraudulent: 1 },
        { date: 'Mar 23', Successful: 44, Refunded: 3, Fraudulent: 3 },
        { date: 'Apr 23', Successful: 23, Refunded: 2, Fraudulent: 4 },
        { date: 'May 23', Successful: 35, Refunded: 1, Fraudulent: 1 },
        { date: 'Jun 23', Successful: 48, Refunded: 1, Fraudulent: 1 },
        { date: 'Jul 23', Successful: 33, Refunded: 1, Fraudulent: 1 },
        { date: 'Aug 23', Successful: 38, Refunded: 3, Fraudulent: 0 },
        { date: 'Sep 23', Successful: 41, Refunded: 2, Fraudulent: 0 },
        { date: 'Oct 23', Successful: 39, Refunded: 1, Fraudulent: 0 },
        { date: 'Nov 23', Successful: 32, Refunded: 1, Fraudulent: 1 },
        { date: 'Dec 23', Successful: 19, Refunded: 5, Fraudulent: 1 },
    ];

    const summary: BarChart05SummaryTabItem[] = [
        {
            name: 'Europe',
            data: dataEurope,
            details: [
                { name: 'Successful', value: 263 },
                { name: 'Refunded', value: 18 },
                { name: 'Fraudulent', value: 10 },
            ],
        },
        {
            name: 'North America',
            data: dataNorthAmerica,
            details: [
                { name: 'Successful', value: 652 },
                { name: 'Refunded', value: 29 },
                { name: 'Fraudulent', value: 17 },
            ],
        },
        {
            name: 'Asia',
            data: dataAsia,
            details: [
                { name: 'Successful', value: 405 },
                { name: 'Refunded', value: 21 },
                { name: 'Fraudulent', value: 15 },
            ],
        },
    ];

    return (
        <BarChart05
            summary={summary}
            title="Online payments"
            categories={['Successful', 'Refunded', 'Fraudulent']}
            colors={['blue', 'violet', 'fuchsia'] as AvailableChartColorsKeys[]}
            detailItemColorMap={{
                'Successful': 'bg-blue-500 dark:bg-blue-500',
                'Refunded': 'bg-violet-500 dark:bg-violet-500',
                'Fraudulent': 'bg-fuchsia-500 dark:bg-fuchsia-500',
            }}
            valueFormatter={valueFormatter}
        />
    );
};

// ─── BarChart06Example ────────────────────────────────────────────────────────

export const BarChart06Example = () => {
    const tabs: BarChart06TabItem[] = [
        { name: 'Europe', value: '$0.7M' },
        { name: 'Asia', value: '$0.6M' },
        { name: 'North America', value: '$0.7M' },
    ];

    const data: BarChart06DataItem[] = [
        { date: 'Jan 22', Europe: 48560, Asia: 38560, 'North America': 34940 },
        { date: 'Feb 22', Europe: 60320, Asia: 30320, 'North America': 34940 },
        { date: 'Mar 22', Europe: 75233, Asia: 65233, 'North America': 84560 },
        { date: 'Apr 22', Europe: 51123, Asia: 39123, 'North America': 74320 },
        { date: 'May 22', Europe: 51000, Asia: 72600, 'North America': 63120 },
        { date: 'Jun 22', Europe: 90450, Asia: 81390, 'North America': 51340 },
        { date: 'Jul 22', Europe: 79390, Asia: 41340, 'North America': 61260 },
        { date: 'Aug 22', Europe: 74100, Asia: 63120, 'North America': 51210 },
        { date: 'Sep 22', Europe: 71090, Asia: 59450, 'North America': 51110 },
        { date: 'Oct 22', Europe: 71080, Asia: 63345, 'North America': 41430 },
        { date: 'Nov 22', Europe: 63041, Asia: 50210, 'North America': 90330 },
        { date: 'Dec 22', Europe: 51143, Asia: 41321, 'North America': 69780 },
        { date: 'Jan 23', Europe: 68560, Asia: 28560, 'North America': 34940 },
        { date: 'Feb 23', Europe: 70320, Asia: 30320, 'North America': 44940 },
        { date: 'Mar 23', Europe: 80233, Asia: 70233, 'North America': 94560 },
        { date: 'Apr 23', Europe: 55123, Asia: 45123, 'North America': 84320 },
        { date: 'May 23', Europe: 56000, Asia: 80600, 'North America': 71120 },
        { date: 'Jun 23', Europe: 100000, Asia: 85390, 'North America': 61340 },
        { date: 'Jul 23', Europe: 85390, Asia: 45340, 'North America': 71260 },
        { date: 'Aug 23', Europe: 80100, Asia: 70120, 'North America': 61210 },
        { date: 'Sep 23', Europe: 75090, Asia: 69450, 'North America': 61110 },
        { date: 'Oct 23', Europe: 71080, Asia: 63345, 'North America': 41430 },
        { date: 'Nov 23', Europe: 68041, Asia: 61210, 'North America': 100330 },
        { date: 'Dec 23', Europe: 60143, Asia: 45321, 'North America': 80780 },
    ];

    return (
        <BarChart06
            tabs={tabs}
            data={data}
            title="Sales breakdown by regions"
            description="Check sales of top 3 regions"
        />
    );
};

// ─── BarChart07Example ────────────────────────────────────────────────────────

export const BarChart07Example = () => {
    const data: DataPoint[] = [
        { date: 'Jan 23', Running: 167, Cycling: 145 },
        { date: 'Feb 23', Running: 125, Cycling: 110 },
        { date: 'Mar 23', Running: 156, Cycling: 149 },
        { date: 'Apr 23', Running: 165, Cycling: 112 },
        { date: 'May 23', Running: 153, Cycling: 138 },
        { date: 'Jun 23', Running: 124, Cycling: 145 },
        { date: 'Jul 23', Running: 164, Cycling: 134 },
        { date: 'Aug 23', Running: 123, Cycling: 110 },
        { date: 'Sep 23', Running: 132, Cycling: 113 },
        { date: 'Oct 23', Running: 124, Cycling: 129 },
        { date: 'Nov 23', Running: 149, Cycling: 101 },
        { date: 'Dec 23', Running: 129, Cycling: 109 },
    ];

    const categories = ['Running', 'Cycling'];

    const valueFormatter = (number: number) => {
        return Intl.NumberFormat('us').format(number).toString() + 'bpm';
    };

    return <BarChart07 data={data} categories={categories} valueFormatter={valueFormatter} />;
};

// ─── BarChart08Example ────────────────────────────────────────────────────────

export const BarChart08Example = () => {
    const data: BarChart08DataItem[] = [
        { date: 'Aug 01', 'Successful requests': 1040, Errors: 0 },
        { date: 'Aug 02', 'Successful requests': 1200, Errors: 0 },
        { date: 'Aug 03', 'Successful requests': 1130, Errors: 0 },
        { date: 'Aug 04', 'Successful requests': 1050, Errors: 0 },
        { date: 'Aug 05', 'Successful requests': 920, Errors: 0 },
        { date: 'Aug 06', 'Successful requests': 870, Errors: 0 },
        { date: 'Aug 07', 'Successful requests': 790, Errors: 0 },
        { date: 'Aug 08', 'Successful requests': 910, Errors: 0 },
        { date: 'Aug 09', 'Successful requests': 951, Errors: 0 },
        { date: 'Aug 10', 'Successful requests': 1232, Errors: 0 },
        { date: 'Aug 11', 'Successful requests': 1230, Errors: 0 },
        { date: 'Aug 12', 'Successful requests': 1289, Errors: 0 },
        { date: 'Aug 13', 'Successful requests': 1002, Errors: 0 },
        { date: 'Aug 14', 'Successful requests': 1034, Errors: 0 },
        { date: 'Aug 15', 'Successful requests': 1140, Errors: 0 },
        { date: 'Aug 16', 'Successful requests': 1280, Errors: 0 },
        { date: 'Aug 17', 'Successful requests': 1345, Errors: 0 },
        { date: 'Aug 18', 'Successful requests': 1432, Errors: 0 },
        { date: 'Aug 19', 'Successful requests': 1321, Errors: 0 },
        { date: 'Aug 20', 'Successful requests': 1230, Errors: 0 },
        { date: 'Aug 21', 'Successful requests': 1020, Errors: 0 },
        { date: 'Aug 22', 'Successful requests': 1040, Errors: 0 },
        { date: 'Aug 23', 'Successful requests': 610, Errors: 81 },
        { date: 'Aug 24', 'Successful requests': 610, Errors: 87 },
        { date: 'Aug 25', 'Successful requests': 610, Errors: 92 },
        { date: 'Aug 26', 'Successful requests': 501, Errors: 120 },
        { date: 'Aug 27', 'Successful requests': 480, Errors: 120 },
        { date: 'Aug 28', 'Successful requests': 471, Errors: 120 },
        { date: 'Aug 29', 'Successful requests': 610, Errors: 89 },
        { date: 'Aug 30', 'Successful requests': 513, Errors: 199 },
        { date: 'Aug 31', 'Successful requests': 500, Errors: 56 },
    ];

    const summary: SummaryMetric[] = [
        { name: 'Successful requests', total: 23450, color: 'bg-blue-500 dark:bg-blue-500' },
        { name: 'Errors', total: 1397, color: 'bg-red-500 dark:bg-red-500' },
    ];

    const valueFormatter = (number: number) =>
        `${Intl.NumberFormat('us').format(number).toString()}`;

    return (
        <BarChart08
            data={data}
            summary={summary}
            categories={['Successful requests', 'Errors']}
            title="Requests"
            description="Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt."
            valueFormatter={valueFormatter}
        />
    );
};

// ─── BarChart09Example ────────────────────────────────────────────────────────

export const BarChart09Example = () => {
    const valueFormatter = (number: number) =>
        `${Intl.NumberFormat('us').format(number).toString()}`;

    const ratio = [
        { date: 'Aug 01', 'Successful requests': 1040, Errors: 0 },
        { date: 'Aug 02', 'Successful requests': 1200, Errors: 0 },
        { date: 'Aug 03', 'Successful requests': 1130, Errors: 0 },
        { date: 'Aug 04', 'Successful requests': 1050, Errors: 0 },
        { date: 'Aug 05', 'Successful requests': 920, Errors: 0 },
        { date: 'Aug 06', 'Successful requests': 870, Errors: 0 },
        { date: 'Aug 07', 'Successful requests': 790, Errors: 0 },
        { date: 'Aug 08', 'Successful requests': 910, Errors: 0 },
        { date: 'Aug 09', 'Successful requests': 951, Errors: 0 },
        { date: 'Aug 10', 'Successful requests': 1232, Errors: 0 },
        { date: 'Aug 11', 'Successful requests': 1230, Errors: 0 },
        { date: 'Aug 12', 'Successful requests': 1289, Errors: 0 },
        { date: 'Aug 13', 'Successful requests': 1002, Errors: 0 },
        { date: 'Aug 14', 'Successful requests': 1034, Errors: 0 },
        { date: 'Aug 15', 'Successful requests': 1140, Errors: 0 },
        { date: 'Aug 16', 'Successful requests': 1280, Errors: 0 },
        { date: 'Aug 17', 'Successful requests': 1345, Errors: 0 },
        { date: 'Aug 18', 'Successful requests': 1432, Errors: 0 },
        { date: 'Aug 19', 'Successful requests': 1321, Errors: 0 },
        { date: 'Aug 20', 'Successful requests': 1230, Errors: 0 },
        { date: 'Aug 21', 'Successful requests': 1020, Errors: 0 },
        { date: 'Aug 22', 'Successful requests': 1040, Errors: 0 },
        { date: 'Aug 23', 'Successful requests': 610, Errors: 81 },
        { date: 'Aug 24', 'Successful requests': 610, Errors: 87 },
        { date: 'Aug 25', 'Successful requests': 610, Errors: 92 },
        { date: 'Aug 26', 'Successful requests': 501, Errors: 120 },
        { date: 'Aug 27', 'Successful requests': 480, Errors: 120 },
        { date: 'Aug 28', 'Successful requests': 471, Errors: 120 },
        { date: 'Aug 29', 'Successful requests': 610, Errors: 89 },
        { date: 'Aug 30', 'Successful requests': 513, Errors: 199 },
        { date: 'Aug 31', 'Successful requests': 500, Errors: 56 },
    ];

    const projects = [
        { date: 'Aug 01', 'Successful requests': 1040, 'Online shop': 780, Blog: 200, 'Test project': 60 },
        { date: 'Aug 02', 'Successful requests': 1200, 'Online shop': 1030, Blog: 50, 'Test project': 120 },
        { date: 'Aug 03', 'Successful requests': 1130, 'Online shop': 950, Blog: 80, 'Test project': 100 },
        { date: 'Aug 04', 'Successful requests': 1050, 'Online shop': 840, Blog: 70, 'Test project': 140 },
        { date: 'Aug 05', 'Successful requests': 920, 'Online shop': 710, Blog: 50, 'Test project': 160 },
        { date: 'Aug 06', 'Successful requests': 870, 'Online shop': 660, Blog: 100, 'Test project': 110 },
        { date: 'Aug 07', 'Successful requests': 790, 'Online shop': 590, Blog: 120, 'Test project': 80 },
        { date: 'Aug 08', 'Successful requests': 910, 'Online shop': 700, Blog: 90, 'Test project': 120 },
        { date: 'Aug 09', 'Successful requests': 951, 'Online shop': 741, Blog: 90, 'Test project': 120 },
        { date: 'Aug 10', 'Successful requests': 1232, 'Online shop': 1040, Blog: 100, 'Test project': 92 },
        { date: 'Aug 11', 'Successful requests': 1230, 'Online shop': 1030, Blog: 100, 'Test project': 100 },
        { date: 'Aug 12', 'Successful requests': 1289, 'Online shop': 1099, Blog: 100, 'Test project': 90 },
        { date: 'Aug 13', 'Successful requests': 1002, 'Online shop': 842, Blog: 70, 'Test project': 90 },
        { date: 'Aug 14', 'Successful requests': 1034, 'Online shop': 884, Blog: 80, 'Test project': 70 },
        { date: 'Aug 15', 'Successful requests': 1140, 'Online shop': 970, Blog: 100, 'Test project': 70 },
        { date: 'Aug 16', 'Successful requests': 1280, 'Online shop': 1120, Blog: 90, 'Test project': 70 },
        { date: 'Aug 17', 'Successful requests': 1345, 'Online shop': 1185, Blog: 90, 'Test project': 55 },
        { date: 'Aug 18', 'Successful requests': 1432, 'Online shop': 1272, Blog: 90, 'Test project': 55 },
        { date: 'Aug 19', 'Successful requests': 1321, 'Online shop': 1161, Blog: 90, 'Test project': 55 },
        { date: 'Aug 20', 'Successful requests': 1230, 'Online shop': 1070, Blog: 100, 'Test project': 60 },
        { date: 'Aug 21', 'Successful requests': 1020, 'Online shop': 1090, Blog: 90, 'Test project': 60 },
        { date: 'Aug 22', 'Successful requests': 1040, 'Online shop': 510, Blog: 100, 'Test project': 430 },
        { date: 'Aug 23', 'Successful requests': 610, 'Online shop': 510, Blog: 100, 'Test project': 430 },
        { date: 'Aug 24', 'Successful requests': 610, 'Online shop': 510, Blog: 100, 'Test project': 430 },
        { date: 'Aug 25', 'Successful requests': 610, 'Online shop': 381, Blog: 100, 'Test project': 129 },
        { date: 'Aug 26', 'Successful requests': 501, 'Online shop': 360, Blog: 100, 'Test project': 120 },
        { date: 'Aug 27', 'Successful requests': 480, 'Online shop': 351, Blog: 100, 'Test project': 120 },
        { date: 'Aug 28', 'Successful requests': 471, 'Online shop': 510, Blog: 100, 'Test project': 0 },
        { date: 'Aug 29', 'Successful requests': 610, 'Online shop': 414, Blog: 100, 'Test project': 0 },
        { date: 'Aug 30', 'Successful requests': 513, 'Online shop': 444, Blog: 100, 'Test project': 0 },
        { date: 'Aug 31', 'Successful requests': 500, 'Online shop': 510, Blog: 100, 'Test project': 0 },
    ];

    const tabs: TabConfig[] = [
        {
            name: 'Ratio',
            data: ratio,
            categories: ['Successful requests', 'Errors'],
            colors: ['blue', 'red'],
            summary: [
                { name: 'Successful requests', total: 23450, color: 'bg-blue-500 dark:bg-blue-500' },
                { name: 'Errors', total: 1397, color: 'bg-red-500 dark:bg-red-500' },
            ],
        },
        {
            name: 'Projects',
            data: projects,
            categories: ['Online shop', 'Blog', 'Test project'],
            colors: ['blue', 'cyan', 'violet'],
            summary: [
                { name: 'Online shop', total: 23450, color: 'bg-blue-500 dark:bg-blue-500' },
                { name: 'Blog', total: 1397, color: 'bg-cyan-500 dark:bg-cyan-500' },
                { name: 'Test project', total: 1397, color: 'bg-violet-500 dark:bg-violet-500' },
            ],
        },
    ];

    return <BarChart09 tabs={tabs} valueFormatter={valueFormatter} />;
};

// ─── BarChart10Example ────────────────────────────────────────────────────────

export const BarChart10Example = () => {
    const pageViews: BarChart10DataItem[] = [
        { date: '01', 'Page Views': 1540 }, { date: '02', 'Page Views': 1600 },
        { date: '03', 'Page Views': 1100 }, { date: '04', 'Page Views': 1250 },
        { date: '05', 'Page Views': 1300 }, { date: '06', 'Page Views': 1200 },
        { date: '07', 'Page Views': 0 }, { date: '08', 'Page Views': 0 },
        { date: '09', 'Page Views': 0 }, { date: '10', 'Page Views': 1500 },
        { date: '11', 'Page Views': 1600 }, { date: '12', 'Page Views': 900 },
        { date: '13', 'Page Views': 2000 }, { date: '14', 'Page Views': 1800 },
        { date: '15', 'Page Views': 1700 }, { date: '16', 'Page Views': 1800 },
        { date: '17', 'Page Views': 2200 }, { date: '18', 'Page Views': 2100 },
        { date: '19', 'Page Views': 1200 }, { date: '20', 'Page Views': 2400 },
        { date: '21', 'Page Views': 2500 }, { date: '22', 'Page Views': 2600 },
        { date: '23', 'Page Views': 2000 }, { date: '24', 'Page Views': 1400 },
        { date: '25', 'Page Views': 1900 }, { date: '26', 'Page Views': 1000 },
        { date: '27', 'Page Views': 2100 }, { date: '28', 'Page Views': 2300 },
        { date: '29', 'Page Views': 1500 }, { date: '30', 'Page Views': 1700 },
    ];

    const uniqueVisitors: BarChart10DataItem[] = [
        { date: '01', 'Unique Visitors': 1120 }, { date: '02', 'Unique Visitors': 1200 },
        { date: '03', 'Unique Visitors': 600 }, { date: '04', 'Unique Visitors': 1050 },
        { date: '05', 'Unique Visitors': 900 }, { date: '06', 'Unique Visitors': 1000 },
        { date: '07', 'Unique Visitors': 0 }, { date: '08', 'Unique Visitors': 0 },
        { date: '09', 'Unique Visitors': 0 }, { date: '10', 'Unique Visitors': 1300 },
        { date: '11', 'Unique Visitors': 1200 }, { date: '12', 'Unique Visitors': 800 },
        { date: '13', 'Unique Visitors': 1500 }, { date: '14', 'Unique Visitors': 1400 },
        { date: '15', 'Unique Visitors': 1300 }, { date: '16', 'Unique Visitors': 1400 },
        { date: '17', 'Unique Visitors': 1700 }, { date: '18', 'Unique Visitors': 1500 },
        { date: '19', 'Unique Visitors': 1000 }, { date: '20', 'Unique Visitors': 1800 },
        { date: '21', 'Unique Visitors': 1600 }, { date: '22', 'Unique Visitors': 1700 },
        { date: '23', 'Unique Visitors': 1400 }, { date: '24', 'Unique Visitors': 1100 },
        { date: '25', 'Unique Visitors': 1200 }, { date: '26', 'Unique Visitors': 800 },
        { date: '27', 'Unique Visitors': 1500 }, { date: '28', 'Unique Visitors': 1600 },
        { date: '29', 'Unique Visitors': 1300 }, { date: '30', 'Unique Visitors': 1400 },
    ];

    const bounceRate: BarChart10DataItem[] = [
        { date: '01', 'Bounce Rate': 0.55 }, { date: '02', 'Bounce Rate': 0.52 },
        { date: '03', 'Bounce Rate': 0.65 }, { date: '04', 'Bounce Rate': 0.6 },
        { date: '05', 'Bounce Rate': 0.5 }, { date: '06', 'Bounce Rate': 0.48 },
        { date: '07', 'Bounce Rate': 0 }, { date: '08', 'Bounce Rate': 0 },
        { date: '09', 'Bounce Rate': 0 }, { date: '10', 'Bounce Rate': 0.58 },
        { date: '11', 'Bounce Rate': 0.6 }, { date: '12', 'Bounce Rate': 0.72 },
        { date: '13', 'Bounce Rate': 0.45 }, { date: '14', 'Bounce Rate': 0.48 },
        { date: '15', 'Bounce Rate': 0.5 }, { date: '16', 'Bounce Rate': 0.47 },
        { date: '17', 'Bounce Rate': 0.44 }, { date: '18', 'Bounce Rate': 0.52 },
        { date: '19', 'Bounce Rate': 0.68 }, { date: '20', 'Bounce Rate': 0.41 },
        { date: '21', 'Bounce Rate': 0.38 }, { date: '22', 'Bounce Rate': 0.4 },
        { date: '23', 'Bounce Rate': 0.43 }, { date: '24', 'Bounce Rate': 0.49 },
        { date: '25', 'Bounce Rate': 0.55 }, { date: '26', 'Bounce Rate': 0.7 },
        { date: '27', 'Bounce Rate': 0.46 }, { date: '28', 'Bounce Rate': 0.42 },
        { date: '29', 'Bounce Rate': 0.6 }, { date: '30', 'Bounce Rate': 0.45 },
    ];

    const valueFormatter = (number: number) =>
        `${Intl.NumberFormat('us').format(number).toString()}`;

    const metrics: MetricConfig[] = [
        { title: 'Page Views', description: '', data: pageViews, metric: 'Page Views', color: 'blue', value: '433' },
        { title: 'Unique Visitors', description: '', data: uniqueVisitors, metric: 'Unique Visitors', color: 'violet', value: '234' },
        { title: 'Bounce Rate', description: '', data: bounceRate, metric: 'Bounce Rate', color: 'fuchsia', value: '584' },
    ];

    return <BarChart10 metrics={metrics} valueFormatter={valueFormatter} />;
};

// ─── BarChart11Example ────────────────────────────────────────────────────────

export const BarChart11Example = () => {
    const data: BarChart11DataItem[] = [
        { date: 'Jan 24', Density: 0.891 },
        { date: 'Feb 24', Density: 0.084 },
        { date: 'Mar 24', Density: 0.155 },
        { date: 'Apr 24', Density: 0.75 },
        { date: 'May 24', Density: 0.221 },
        { date: 'Jun 24', Density: 0.561 },
        { date: 'Jul 24', Density: 0.261 },
        { date: 'Aug 24', Density: 0.421 },
    ];

    return (
        <BarChart11
            data={data}
            title="Bidder density"
            description="Competition level measured by number and size of bidders over time"
            metric="Density"
            valueFormatter={(value) =>
                formatPercentage({ number: value, decimals: 0 })
            }
        />
    );
};

// ─── BarChart12Example ────────────────────────────────────────────────────────

export const BarChart12Example = () => {
    const data: BarChart12DataItem[] = [
        { date: 'Jan 24', Addressed: 8, Unrealized: 12 },
        { date: 'Feb 24', Addressed: 9, Unrealized: 12 },
        { date: 'Mar 24', Addressed: 6, Unrealized: 12 },
        { date: 'Apr 24', Addressed: 5, Unrealized: 12 },
        { date: 'May 24', Addressed: 12, Unrealized: 12 },
        { date: 'Jun 24', Addressed: 9, Unrealized: 12 },
        { date: 'Jul 24', Addressed: 3, Unrealized: 12 },
        { date: 'Aug 24', Addressed: 7, Unrealized: 12 },
    ];

    return (
        <BarChart12
            data={data}
            title="ESG impact"
            description="Evaluation of addressed ESG criteria in biddings over time"
            categories={['Addressed', 'Unrealized']}
            colors={['emerald', 'cyan']}
            type="percent"
            yAxisLabel="% of criteria addressed"
            barCategoryGap="30%"
            valueFormatter={(value) => `${value}%`}
        />
    );
};

// ─── Fintech Examples ─────────────────────────────────────────────────────────
export * from './fintech/fund-monthly-pnl'; export * from './fintech/hedge-fund-strategy-returns';