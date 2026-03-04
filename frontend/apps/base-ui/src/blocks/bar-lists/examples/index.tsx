import React from 'react';

import { BarList01, BarListItem as BarList01Item } from '../bar-list-01';
import { BarList02, BarListItem as BarList02Item } from '../bar-list-02';
import { BarList03, BarListItem as BarList03Item } from '../bar-list-03';
import { BarList04, OrderItem as BarList04OrderItem } from '../bar-list-04';
import { BarList05, OrderItem as BarList05OrderItem } from '../bar-list-05';
import { BarList06, TabData } from '../bar-list-06';
import { BarList07, BarListItem as BarList07Item } from '../bar-list-07';

// ─── BarList01Example ────────────────────────────────────────────────────────

export const BarList01Example = () => {
    const pages: BarList01Item[] = [
        { name: '/home', value: 2019 },
        { name: '/blocks', value: 1053 },
        { name: '/components', value: 997 },
        { name: '/docs/getting-started/installation', value: 982 },
        { name: '/docs/components/button', value: 782 },
        { name: '/docs/components/table', value: 752 },
        { name: '/docs/components/area-chart', value: 741 },
        { name: '/docs/components/badge', value: 750 },
        { name: '/docs/components/bar-chart', value: 750 },
        { name: '/docs/components/tabs', value: 720 },
    ];

    const valueFormatter = (number: number) =>
        `${Intl.NumberFormat('us').format(number).toString()}`;

    return (
        <BarList01
            data={pages}
            valueFormatter={valueFormatter}
            title="Top pages"
            subtitle="Visitors"
        />
    );
};

// ─── BarList02Example ────────────────────────────────────────────────────────

export const BarList02Example = () => {
    const pages: BarList02Item[] = [
        { name: '/home', value: 2019 },
        { name: '/blocks', value: 1053 },
        { name: '/components', value: 997 },
        { name: '/docs/getting-started/installation', value: 982 },
        { name: '/docs/components/button', value: 782 },
        { name: '/docs/components/table', value: 752 },
        { name: '/docs/components/area-chart', value: 741 },
        { name: '/docs/components/badge', value: 750 },
        { name: '/docs/components/bar-chart', value: 750 },
        { name: '/docs/components/tabs', value: 720 },
        { name: '/docs/components/tracker', value: 723 },
        { name: '/docs/components/icons', value: 678 },
        { name: '/docs/components/list', value: 645 },
        { name: '/journal', value: 701 },
        { name: '/spotlight', value: 650 },
        { name: '/resources', value: 601 },
        { name: '/imprint', value: 345 },
        { name: '/about', value: 302 },
    ];

    const valueFormatter = (number: number) =>
        `${Intl.NumberFormat('us').format(number).toString()}`;

    return (
        <BarList02
            data={pages}
            valueFormatter={valueFormatter}
            title="Top pages"
            subtitle="Visitors"
        />
    );
};

// ─── BarList03Example ────────────────────────────────────────────────────────

export const BarList03Example = () => {
    const pages: BarList03Item[] = [
        { name: '/home', value: 2019 },
        { name: '/blocks', value: 1053 },
        { name: '/components', value: 997 },
        { name: '/docs/getting-started/installation', value: 982 },
        { name: '/docs/components/button', value: 782 },
        { name: '/docs/components/table', value: 752 },
        { name: '/docs/components/area-chart', value: 741 },
        { name: '/docs/components/badge', value: 750 },
        { name: '/docs/components/bar-chart', value: 750 },
        { name: '/docs/components/tabs', value: 720 },
        { name: '/docs/components/tracker', value: 723 },
        { name: '/docs/components/icons', value: 678 },
        { name: '/docs/components/list', value: 645 },
        { name: '/journal', value: 701 },
        { name: '/spotlight', value: 650 },
        { name: '/resources', value: 601 },
        { name: '/imprint', value: 345 },
        { name: '/about', value: 302 },
    ];

    const valueFormatter = (number: number) =>
        `${Intl.NumberFormat('us').format(number).toString()}`;

    return (
        <BarList03
            data={pages}
            valueFormatter={valueFormatter}
            title="Top 5 pages"
            subtitle="Visitors"
            headerValue="113,061"
            headerLabel="Website visitors"
        />
    );
};

// ─── BarList04Example ────────────────────────────────────────────────────────

export const BarList04Example = () => {
    const orders: BarList04OrderItem[] = [
        { name: 'ID-2340', date: '31/08/2023 13:45' },
        { name: 'ID-2344', date: '30/08/2023 10:41' },
        { name: 'ID-1385', date: '29/08/2023 09:01' },
        { name: 'ID-1393', date: '29/08/2023 09:23' },
        { name: 'ID-1264', date: '28/08/2023 15:12' },
        { name: 'ID-434', date: '27/08/2023 14:27' },
        { name: 'ID-1234', date: '26/08/2023 11:34' },
        { name: 'ID-1235', date: '25/08/2023 18:50' },
        { name: 'ID-1236', date: '24/08/2023 16:22' },
        { name: 'ID-1237', date: '23/08/2023 12:15' },
        { name: 'ID-1238', date: '22/08/2023 09:30' },
        { name: 'ID-1239', date: '21/08/2023 08:08' },
        { name: 'ID-1240', date: '20/08/2023 07:55' },
        { name: 'ID-1241', date: '19/08/2023 17:09' },
        { name: 'ID-1242', date: '18/08/2023 19:40' },
    ];

    return (
        <BarList04
            data={orders}
            title="Order overview"
            progressValue={78.2}
            fulfilledCount={1543}
            fulfilledPercent={78.2}
            openCount={431}
            openPercent={21.8}
        />
    );
};

// ─── BarList05Example ────────────────────────────────────────────────────────

export const BarList05Example = () => {
    const orders: BarList05OrderItem[] = [
        { name: 'ID-2340', date: '31/08/2023 13:45' },
        { name: 'ID-2344', date: '30/08/2023 10:41' },
        { name: 'ID-1385', date: '29/08/2023 09:01' },
        { name: 'ID-1393', date: '29/08/2023 09:23' },
        { name: 'ID-1264', date: '28/08/2023 15:12' },
        { name: 'ID-434', date: '27/08/2023 14:27' },
        { name: 'ID-1234', date: '26/08/2023 11:34' },
        { name: 'ID-1235', date: '25/08/2023 18:50' },
        { name: 'ID-1236', date: '24/08/2023 16:22' },
        { name: 'ID-1237', date: '23/08/2023 12:15' },
        { name: 'ID-1238', date: '22/08/2023 09:30' },
        { name: 'ID-1239', date: '21/08/2023 08:08' },
        { name: 'ID-1240', date: '20/08/2023 07:55' },
        { name: 'ID-1241', date: '19/08/2023 17:09' },
        { name: 'ID-1242', date: '18/08/2023 19:40' },
        { name: 'ID-1243', date: '17/08/2023 14:59' },
        { name: 'ID-1244', date: '16/08/2023 10:15' },
        { name: 'ID-1245', date: '15/08/2023 20:30' },
        { name: 'ID-1246', date: '14/08/2023 08:40' },
        { name: 'ID-1247', date: '13/08/2023 12:57' },
    ];

    return (
        <BarList05
            data={orders}
            title="Order overview"
            progressValue={78.2}
            fulfilledCount={456}
            fulfilledPercent={23.1}
            openCount={1518}
            openPercent={76.9}
        />
    );
};

// ─── BarList06Example ────────────────────────────────────────────────────────

export const BarList06Example = () => {
    const tabs: TabData[] = [
        {
            name: 'Country',
            data: [
                { name: 'United States of America', value: 2422 },
                { name: 'India', value: 1560 },
                { name: 'Germany', value: 680 },
                { name: 'Brazil', value: 580 },
                { name: 'United Kingdom', value: 510 },
            ],
        },
        {
            name: 'City',
            data: [
                { name: 'London', value: 1393 },
                { name: 'New York', value: 1219 },
                { name: 'Mumbai', value: 921 },
                { name: 'Berlin', value: 580 },
                { name: 'San Francisco', value: 492 },
            ],
        },
    ];

    const valueFormatter = (number: number) =>
        `${Intl.NumberFormat('us').format(number).toString()}`;

    return (
        <BarList06
            tabs={tabs}
            valueFormatter={valueFormatter}
            title="Locations"
        />
    );
};

// ─── BarList07Example ────────────────────────────────────────────────────────

export const BarList07Example = () => {
    const location: BarList07Item[] = [
        { name: 'United States of America', value: 5422 },
        { name: 'India', value: 3560 },
        { name: 'Germany', value: 680 },
        { name: 'Brazil', value: 580 },
        { name: 'United Kingdom', value: 510 },
    ];

    const valueFormatter = (number: number) =>
        `${Intl.NumberFormat('us').format(number).toString()}`;

    return (
        <BarList07
            data={location}
            valueFormatter={valueFormatter}
            title="Locations"
        />
    );
};

export * from './fintech/active-position-pnl';
