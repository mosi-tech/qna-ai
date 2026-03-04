import React from 'react';

import { DonutChart01, type DataItem as DataItem01 } from '../donut-chart-01';
import { DonutChart02 } from '../donut-chart-02';
import { DonutChart03, type DataItem as DataItem03, type TabDataSet as TabDataSet03 } from '../donut-chart-03';
import { DonutChart04, type DataItem as DataItem04, type TabDataSet as TabDataSet04 } from '../donut-chart-04';
import { DonutChart05, type DataItem as DataItem05, type TabDataSet as TabDataSet05 } from '../donut-chart-05';
import { DonutChart06, type DataItem as DataItem06 } from '../donut-chart-06';
import { DonutChart07, type DataItem as DataItem07 } from '../donut-chart-07';

export const DonutChart01Example = () => {
    const data: DataItem01[] = [
        {
            name: 'Travel',
            value: 6730,
            share: '32.1%',
            color: 'bg-cyan-500 dark:bg-cyan-500',
        },
        {
            name: 'IT & equipment',
            value: 4120,
            share: '19.6%',
            color: 'bg-blue-500 dark:bg-blue-500',
        },
        {
            name: 'Training & development',
            value: 3920,
            share: '18.6%',
            color: 'bg-indigo-500 dark:bg-indigo-500',
        },
        {
            name: 'Office supplies',
            value: 3210,
            share: '15.3%',
            color: 'bg-violet-500 dark:bg-violet-500',
        },
        {
            name: 'Communication',
            value: 3010,
            share: '14.3%',
            color: 'bg-fuchsia-500 dark:bg-fuchsia-500',
        },
    ];

    return <DonutChart01 title="Total expenses by category" data={data} />;
};

export const DonutChart02Example = () => {
    return <DonutChart02 title="Sales potential realization ($)" />;
};

export const DonutChart03Example = () => {
    const tabSets: TabDataSet03[] = [
        {
            id: 'category',
            label: 'By Category',
            data: [
                {
                    name: 'Travel',
                    value: 6730,
                    share: '32.1%',
                    color: 'bg-cyan-500 dark:bg-cyan-500',
                },
                {
                    name: 'IT & equipment',
                    value: 4120,
                    share: '19.6%',
                    color: 'bg-blue-500 dark:bg-blue-500',
                },
                {
                    name: 'Training & development',
                    value: 3920,
                    share: '18.6%',
                    color: 'bg-emerald-500 dark:bg-emerald-500',
                },
                {
                    name: 'Office supplies',
                    value: 3210,
                    share: '15.3%',
                    color: 'bg-violet-500 dark:bg-violet-500',
                },
                {
                    name: 'Communication',
                    value: 3010,
                    share: '14.3%',
                    color: 'bg-fuchsia-500 dark:bg-fuchsia-500',
                },
            ],
        },
        {
            id: 'employee',
            label: 'By Employee',
            data: [
                {
                    name: 'Max Down',
                    value: 5710,
                    share: '27.2%',
                    color: 'bg-cyan-500 dark:bg-cyan-500',
                },
                {
                    name: 'Lena Smith',
                    value: 4940,
                    share: '23.5%',
                    color: 'bg-blue-500 dark:bg-blue-500',
                },
                {
                    name: 'Joe Doe',
                    value: 4523,
                    share: '21.5%',
                    color: 'bg-emerald-500 dark:bg-emerald-500',
                },
                {
                    name: 'Kathy Miller',
                    value: 3240,
                    share: '15.4%',
                    color: 'bg-violet-500 dark:bg-violet-500',
                },
                {
                    name: 'Nelly Wave',
                    value: 2577,
                    share: '12.3%',
                    color: 'bg-fuchsia-500 dark:bg-fuchsia-500',
                },
            ],
        },
    ];

    return (
        <DonutChart03
            title="Expenses breakdown"
            description="Lorem ipsum dolor sit amet, consetetur sadipscing elitr."
            tabSets={tabSets}
        />
    );
};

export const DonutChart04Example = () => {
    const tabSets: TabDataSet04[] = [
        {
            id: 'class',
            label: 'By Class',
            data: [
                {
                    name: 'Real estate',
                    value: 2095920,
                    share: '80.5%',
                    borderColor: 'border-blue-500 dark:border-blue-500',
                },
                {
                    name: 'Stocks & ETFs',
                    value: 250120,
                    share: '9.6%',
                    borderColor: 'border-emerald-500 dark:border-emerald-500',
                },
                {
                    name: 'Bonds',
                    value: 140110,
                    share: '5.4%',
                    borderColor: 'border-cyan-500 dark:border-cyan-500',
                },
                {
                    name: 'Metals',
                    value: 72980,
                    share: '2.8%',
                    borderColor: 'border-violet-500 dark:border-violet-500',
                },
                {
                    name: 'Cash & Cash Equivalent',
                    value: 42980,
                    share: '1.7%',
                    borderColor: 'border-fuchsia-500 dark:border-fuchsia-500',
                },
            ],
        },
        {
            id: 'sector',
            label: 'By Sector',
            data: [
                {
                    name: 'Technology',
                    value: 950670,
                    share: '36.5%',
                    borderColor: 'border-blue-500 dark:border-blue-500',
                },
                {
                    name: 'Financial services',
                    value: 750342,
                    share: '28.8%',
                    borderColor: 'border-emerald-500 dark:border-emerald-500',
                },
                {
                    name: 'Consumer products',
                    value: 550709,
                    share: '21.2%',
                    borderColor: 'border-cyan-500 dark:border-cyan-500',
                },
                {
                    name: 'Energy',
                    value: 200220,
                    share: '7.7%',
                    borderColor: 'border-violet-500 dark:border-violet-500',
                },
                {
                    name: 'Media & Entertainment',
                    value: 150169,
                    share: '5.8%',
                    borderColor: 'border-fuchsia-500 dark:border-fuchsia-500',
                },
            ],
        },
    ];

    return (
        <DonutChart04
            title="Portfolio allocation"
            description="Lorem ipsum dolor sit amet, consetetur sadipscing elitr."
            tabSets={tabSets}
        />
    );
};

export const DonutChart05Example = () => {
    const tabSets: TabDataSet05[] = [
        {
            id: 'class',
            label: 'By Class',
            data: [
                {
                    name: 'Real estate',
                    value: 2095920,
                    share: '80.5%',
                    href: '#',
                    borderColor: 'border-blue-500 dark:border-blue-500',
                },
                {
                    name: 'Stocks & ETFs',
                    value: 250120,
                    share: '9.6%',
                    href: '#',
                    borderColor: 'border-emerald-500 dark:border-emerald-500',
                },
                {
                    name: 'Bonds',
                    value: 140110,
                    share: '5.4%',
                    href: '#',
                    borderColor: 'border-cyan-500 dark:border-cyan-500',
                },
                {
                    name: 'Metals',
                    value: 72980,
                    share: '2.8%',
                    href: '#',
                    borderColor: 'border-violet-500 dark:border-violet-500',
                },
                {
                    name: 'Cash & cash equivalent',
                    value: 42980,
                    share: '1.7%',
                    href: '#',
                    borderColor: 'border-fuchsia-500 dark:border-fuchsia-500',
                },
            ],
        },
        {
            id: 'sector',
            label: 'By Sector',
            data: [
                {
                    name: 'Technology',
                    value: 950670,
                    share: '36.5%',
                    href: '#',
                    borderColor: 'border-blue-500 dark:border-blue-500',
                },
                {
                    name: 'Financial services',
                    value: 750342,
                    share: '28.8%',
                    href: '#',
                    borderColor: 'border-emerald-500 dark:border-emerald-500',
                },
                {
                    name: 'Consumer products',
                    value: 550709,
                    share: '21.2%',
                    href: '#',
                    borderColor: 'border-cyan-500 dark:border-cyan-500',
                },
                {
                    name: 'Energy',
                    value: 200220,
                    share: '7.7%',
                    href: '#',
                    borderColor: 'border-violet-500 dark:border-violet-500',
                },
                {
                    name: 'Media & Entertainment',
                    value: 150169,
                    share: '5.8%',
                    href: '#',
                    borderColor: 'border-fuchsia-500 dark:border-fuchsia-500',
                },
            ],
        },
    ];

    return (
        <DonutChart05
            title="Asset allocation"
            description="Lorem ipsum dolor sit amet, consetetur sadipscing elitr."
            tabSets={tabSets}
        />
    );
};

export const DonutChart06Example = () => {
    const data: DataItem06[] = [
        {
            name: 'Real estate',
            value: 2095920,
            share: '84.3%',
            href: '#',
            borderColor: 'bg-blue-500 dark:bg-blue-500',
        },
        {
            name: 'Stocks & ETFs',
            value: 250120,
            share: '10.1%',
            href: '#',
            borderColor: 'bg-violet-500 dark:bg-violet-500',
        },
        {
            name: 'Cash & cash equivalent',
            value: 140110,
            share: '5.6%',
            href: '#',
            borderColor: 'bg-fuchsia-500 dark:bg-fuchsia-500',
        },
    ];

    return (
        <DonutChart06
            title="Asset allocation"
            description="Lorem ipsum dolor sit amet, consetetur sadipscing elitr."
            data={data}
        />
    );
};

export const DonutChart07Example = () => {
    const data: DataItem07[] = [
        {
            name: 'Real estate',
            value: 2095920,
            share: '84.3%',
            href: '#',
            borderColor: 'bg-blue-500 dark:bg-blue-500',
        },
        {
            name: 'Stocks & ETFs',
            value: 250120,
            share: '10.1%',
            href: '#',
            borderColor: 'bg-violet-500 dark:bg-violet-500',
        },
        {
            name: 'Metals',
            value: 160720,
            share: '5.6%',
            href: '#',
            borderColor: 'bg-fuchsia-500 dark:bg-fuchsia-500',
        },
    ];

    return (
        <DonutChart07
            title="Asset allocation"
            data={data}
            totalValue={2506760}
            totalLabel="Total asset value"
        />
    );
};
