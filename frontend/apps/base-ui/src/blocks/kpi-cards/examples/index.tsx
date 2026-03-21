import React from 'react';
import { RiCashLine, RiLinksLine, RiSafeLine } from '@remixicon/react';

import { MetricItem } from '../index';

import { KpiCard01 } from '../kpi-card-01';
import { KpiCard02 } from '../kpi-card-02';
import { KpiCard03 } from '../kpi-card-03';
import { KpiCard04 } from '../kpi-card-04';
import { KpiCard05 } from '../kpi-card-05';
import { KpiCard06 } from '../kpi-card-06';
import { KpiCard07 } from '../kpi-card-07';
import { KpiCard08 } from '../kpi-card-08';
import { KpiCard09 } from '../kpi-card-09';
import { ConstraintItem, KpiCard10 } from '../kpi-card-10';
import { RegionMetadataItem, KpiCard11 } from '../kpi-card-11';
import { PlanMetricItem, KpiCard12 } from '../kpi-card-12';
import { BudgetMetricItem, KpiCard13 } from '../kpi-card-13';
import { StockMetricItem, KpiCard14 } from '../kpi-card-14';
import { QuotaMetricItem, KpiCard15 } from '../kpi-card-15';
import { ScoreMetricItem, KpiCard16 } from '../kpi-card-16';
import { KpiCard17 } from '../kpi-card-17';
import { KpiCard18 } from '../kpi-card-18';
import { KpiCard19 } from '../kpi-card-19';
import { HeartRateMetric, KpiCard20 } from '../kpi-card-20';
import { CategoryItem, KpiCard21 } from '../kpi-card-21';
import { TokenMetric, KpiCard22 } from '../kpi-card-22';
import { SalesChannel, KpiCard23 } from '../kpi-card-23';
import { MetricCardItem, KpiCard24 } from '../kpi-card-24';
import { MetricCard, KpiCard25 } from '../kpi-card-25';
import { MetricItem as KpiCard26MetricItem, KpiCard26 } from '../kpi-card-26';
import { ChartMetric, KpiCard27 } from '../kpi-card-27';
import { Metric as KpiCard28Metric, IssueItem, KpiCard28 } from '../kpi-card-28';
import { Metric, KpiCard29 } from '../kpi-card-29';

// ─── KpiCard01Example ───────────────────────────────────────────────────────────────

export const KpiCard01Example = () => {
    const data: MetricItem[] = [
        {
            name: 'Unique visitors',
            stat: '10,450',
            change: '-12.5%',
            changeType: 'negative',
        },
        {
            name: 'Bounce rate',
            stat: '56.1%',
            change: '+1.8%',
            changeType: 'positive',
        },
        {
            name: 'Visit duration',
            stat: '5.2min',
            change: '+19.7%',
            changeType: 'positive',
        },
    ];

    return <KpiCard01 metrics={data} />;
};

// ─── KpiCard02Example ───────────────────────────────────────────────────────────────

export const KpiCard02Example = () => {
    const data: MetricItem[] = [
        {
            name: 'Daily active users',
            stat: '3,450',
            change: '+12.1%',
            changeType: 'positive',
        },
        {
            name: 'Weekly sessions',
            stat: '1,342',
            change: '-9.8%',
            changeType: 'negative',
        },
        {
            name: 'Duration',
            stat: '5.2min',
            change: '+7.7%',
            changeType: 'positive',
        },
    ];

    return <KpiCard02 metrics={data} />;
};

// ─── KpiCard03Example ───────────────────────────────────────────────────────────────

export const KpiCard03Example = () => {
    const data: MetricItem[] = [
        {
            name: 'Recurring revenue',
            value: '$34.1K',
            change: '+6.1%',
            changeType: 'positive',
        },
        {
            name: 'Total users',
            value: '500.1K',
            change: '+19.2%',
            changeType: 'positive',
        },
        {
            name: 'User growth',
            value: '11.3%',
            change: '-1.2%',
            changeType: 'negative',
        },
    ];

    return <KpiCard03 metrics={data} />;
};

// ─── KpiCard04Example ───────────────────────────────────────────────────────────────

export const KpiCard04Example = () => {
    const data: MetricItem[] = [
        {
            name: 'Monthly recurring revenue',
            value: '$34.1K',
            change: '+6.1%',
            changeType: 'positive',
            href: '#mrr',
        },
        {
            name: 'Users',
            value: '500.1K',
            change: '+19.2%',
            changeType: 'positive',
            href: '#users',
        },
        {
            name: 'User growth',
            value: '11.3%',
            change: '-1.2%',
            changeType: 'negative',
            href: '#growth',
        },
    ];

    return <KpiCard04 metrics={data} />;
};

// ─── KpiCard05Example ───────────────────────────────────────────────────────────────

export const KpiCard05Example = () => {
    const data: MetricItem[] = [
        {
            name: 'Monthly active users',
            stat: '340',
            previousStat: '400',
            change: '-15%',
            changeType: 'negative',
        },
        {
            name: 'Monthly sessions',
            stat: '672',
            previousStat: '350',
            change: '+91.4%',
            changeType: 'positive',
        },
        {
            name: 'Monthly page views',
            stat: '3,290',
            previousStat: '3,012',
            change: '+9.2%',
            changeType: 'positive',
        },
    ];

    return <KpiCard05 metrics={data} />;
};

// ─── KpiCard06Example ───────────────────────────────────────────────────────────────

export const KpiCard06Example = () => {
    const data: MetricItem[] = [
        {
            name: 'Daily active users',
            stat: '3,450',
            change: '12.1%',
            changeType: 'positive',
        },
        {
            name: 'Weekly sessions',
            stat: '1,342',
            change: '9.8%',
            changeType: 'negative',
        },
        {
            name: 'Duration',
            stat: '5.2min',
            change: '7.7%',
            changeType: 'positive',
        },
    ];

    return <KpiCard06 metrics={data} />;
};

// ─── KpiCard07Example ───────────────────────────────────────────────────────────────

export const KpiCard07Example = () => {
    const data: MetricItem[] = [
        {
            name: 'Monthly active users',
            stat: '340',
            previousStat: '400',
            change: '-15%',
            changeType: 'negative',
        },
        {
            name: 'Monthly sessions',
            stat: '672',
            previousStat: '350',
            change: '+91.4%',
            changeType: 'positive',
        },
        {
            name: 'Monthly page views',
            stat: '3,290',
            previousStat: '3,012',
            change: '+9.2%',
            changeType: 'positive',
        },
    ];

    return <KpiCard07 metrics={data} />;
};

// ─── KpiCard08Example ───────────────────────────────────────────────────────────────

export const KpiCard08Example = () => {
    const data: MetricItem[] = [
        {
            name: 'Monthly active users',
            stat: '340',
            previousStat: '400',
            change: '15%',
            changeType: 'negative',
        },
        {
            name: 'Monthly sessions',
            stat: '672',
            previousStat: '350',
            change: '91.4%',
            changeType: 'positive',
        },
        {
            name: 'Monthly page views',
            stat: '3,290',
            previousStat: '3,012',
            change: '9.2%',
            changeType: 'positive',
        },
    ];

    return <KpiCard08 metrics={data} />;
};

// ─── KpiCard09Example ───────────────────────────────────────────────────────────────

export const KpiCard09Example = () => {
    const data: MetricItem[] = [
        {
            name: 'Monthly active users',
            stat: '996',
            change: '+1.3%',
            changeType: 'positive',
            color: 'bg-blue-500',
        },
        {
            name: 'Monthly sessions',
            stat: '1,672',
            change: '+9.1%',
            changeType: 'positive',
            color: 'bg-violet-500',
        },
        {
            name: 'Monthly user growth',
            stat: '5.1%',
            change: '-4.8%',
            changeType: 'negative',
            color: 'bg-fuchsia-500',
        },
    ];

    return <KpiCard09 metrics={data} />;
};

// ─── KpiCard10Example ───────────────────────────────────────────────────────────────

export const KpiCard10Example = () => {
    const data: ConstraintItem[] = [
        {
            name: 'Daily active users',
            stat: '345',
            status: 'within',
            range: '200-410',
        },
        {
            name: 'Weekly sessions',
            stat: '254',
            status: 'critical',
            range: '550-1,200',
        },
        {
            name: 'Open issues',
            stat: '34',
            status: 'observe',
            range: '10-25',
        },
    ];

    return <KpiCard10 metrics={data} />;
};

// ─── KpiCard11Example ───────────────────────────────────────────────────────────────

export const KpiCard11Example = () => {
    const data: RegionMetadataItem[] = [
        {
            name: 'Europe',
            stat: '$10,023',
            goalsAchieved: 3,
            status: 'observe',
            href: '#',
        },
        {
            name: 'North America',
            stat: '$14,092',
            goalsAchieved: 5,
            status: 'within',
            href: '#',
        },
        {
            name: 'Asia',
            stat: '$113,232',
            goalsAchieved: 1,
            status: 'critical',
            href: '#',
        },
    ];

    return <KpiCard11 metrics={data} />;
};

// ─── KpiCard12Example ───────────────────────────────────────────────────────────────

export const KpiCard12Example = () => {
    const data: PlanMetricItem[] = [
        {
            name: 'Workspaces',
            capacity: 20,
            current: 1,
            allowed: 5,
        },
        {
            name: 'Dashboards',
            capacity: 10,
            current: 2,
            allowed: 20,
        },
        {
            name: 'Chart widgets',
            capacity: 0,
            current: 0,
            allowed: 50,
        },
    ];

    return <KpiCard12 metrics={data} />;
};

// ─── KpiCard13Example ───────────────────────────────────────────────────────────────

export const KpiCard13Example = () => {
    const data: BudgetMetricItem[] = [
        {
            name: 'HR',
            progress: 25,
            budget: '$1,000',
            current: '$250',
            href: '#',
        },
        {
            name: 'Marketing',
            progress: 55,
            budget: '$1,000',
            current: '$550',
            href: '#',
        },
        {
            name: 'Finance',
            progress: 85,
            budget: '$1,000',
            current: '$850',
            href: '#',
        },
    ];

    return <KpiCard13 metrics={data} />;
};

// ─── KpiCard14Example ───────────────────────────────────────────────────────────────

export const KpiCard14Example = () => {
    const chartData = [
        {
            date: 'Nov 24, 2023',
            'Baer Limited': 67.3,
            'QuantData Holding': 59.09,
            'Not Normal, Inc.': 36.69,
        },
        {
            date: 'Nov 25, 2023',
            'Baer Limited': 65.34,
            'QuantData Holding': 42.55,
            'Not Normal, Inc.': 49.13,
        },
        {
            date: 'Nov 26, 2023',
            'Baer Limited': 58.14,
            'QuantData Holding': 49.69,
            'Not Normal, Inc.': 42.77,
        },
        {
            date: 'Nov 27, 2023',
            'Baer Limited': 67.38,
            'QuantData Holding': 57.09,
            'Not Normal, Inc.': 39.43,
        },
        {
            date: 'Nov 28, 2023',
            'Baer Limited': 63.62,
            'QuantData Holding': 69.21,
            'Not Normal, Inc.': 41.78,
        },
        {
            date: 'Nov 29, 2023',
            'Baer Limited': 68.67,
            'QuantData Holding': 72.55,
            'Not Normal, Inc.': 49.39,
        },
        {
            date: 'Nov 30, 2023',
            'Baer Limited': 59.11,
            'QuantData Holding': 39.65,
            'Not Normal, Inc.': 38.41,
        },
        {
            date: 'Dec 01, 2023',
            'Baer Limited': 57.09,
            'QuantData Holding': 48.38,
            'Not Normal, Inc.': 45.87,
        },
        {
            date: 'Dec 02, 2023',
            'Baer Limited': 55.07,
            'QuantData Holding': 59.1,
            'Not Normal, Inc.': 39.05,
        },
        {
            date: 'Dec 03, 2023',
            'Baer Limited': 69.62,
            'QuantData Holding': 80.11,
            'Not Normal, Inc.': 53.6,
        },
        {
            date: 'Dec 04, 2023',
            'Baer Limited': 71.07,
            'QuantData Holding': 78.04,
            'Not Normal, Inc.': 68.52,
        },
        {
            date: 'Dec 05, 2023',
            'Baer Limited': 67.8,
            'QuantData Holding': 79.85,
            'Not Normal, Inc.': 69.0,
        },
        {
            date: 'Dec 06, 2023',
            'Baer Limited': 55.92,
            'QuantData Holding': 89.26,
            'Not Normal, Inc.': 72.34,
        },
        {
            date: 'Dec 07, 2023',
            'Baer Limited': 59.87,
            'QuantData Holding': 99.37,
            'Not Normal, Inc.': 79.39,
        },
        {
            date: 'Dec 08, 2023',
            'Baer Limited': 49.33,
            'QuantData Holding': 129.1,
            'Not Normal, Inc.': 89.47,
        },
    ];

    const data: StockMetricItem[] = [
        {
            name: 'Baer Limited',
            tickerSymbol: 'BAL',
            value: '$49.33',
            change: '-9.85',
            percentageChange: '-1.9%',
            changeType: 'negative',
        },
        {
            name: 'QuantData Holding',
            tickerSymbol: 'QDH',
            value: '$129.10',
            change: '+12.10',
            percentageChange: '+7.1%',
            changeType: 'positive',
        },
        {
            name: 'Not Normal, Inc.',
            tickerSymbol: 'NNO',
            value: '$89.80',
            change: '+7.50',
            percentageChange: '+1.2%',
            changeType: 'positive',
        },
    ];

    return <KpiCard14 metrics={data} chartData={chartData} />;
};

// ─── KpiCard15Example ───────────────────────────────────────────────────────────────

export const KpiCard15Example = () => {
    const data: QuotaMetricItem[] = [
        {
            name: 'Requests',
            stat: '996',
            limit: '10,000',
            percentage: 9.96,
        },
        {
            name: 'Credits',
            stat: '$672',
            limit: '$1,000',
            percentage: 67.2,
        },
        {
            name: 'Storage',
            stat: '1.85',
            limit: '10GB',
            percentage: 18.5,
        },
    ];

    return <KpiCard15 metrics={data} />;
};

// ─── KpiCard16Example ───────────────────────────────────────────────────────────────

export const KpiCard16Example = () => {
    const data: ScoreMetricItem[] = [
        {
            name: 'Performance',
            value: 91,
        },
        {
            name: 'Accessibility',
            value: 65,
        },
        {
            name: 'SEO',
            value: 43,
        },
    ];

    return <KpiCard16 metrics={data} />;
};

// ─── KpiCard17Example ───────────────────────────────────────────────────────────────

export const KpiCard17Example = () => {
    const fmtCurrency = (n: number) => `$${Intl.NumberFormat('en-US').format(Math.round(n))}`;
    const fmtPct = (n: number) => `${n >= 0 ? '+' : ''}${n.toFixed(2)}%`;
    const chartData = [
        { date: 'Jan 26', nav: 1180000, pnl: 38000, ytdReturn: 1.2 },
        { date: 'Feb 26', nav: 1215000, pnl: 45000, ytdReturn: 2.8 },
        { date: 'Mar 26', nav: 1195000, pnl: -12000, ytdReturn: 1.2 },
        { date: 'Apr 26', nav: 1242000, pnl: 61000, ytdReturn: 4.6 },
        { date: 'May 26', nav: 1270000, pnl: 28000, ytdReturn: 6.0 },
        { date: 'Jun 26', nav: 1249000, pnl: -21000, ytdReturn: 4.2 },
        { date: 'Jul 26', nav: 1308000, pnl: 55000, ytdReturn: 9.1 },
        { date: 'Aug 26', nav: 1290000, pnl: -18000, ytdReturn: 7.6 },
        { date: 'Sep 26', nav: 1335000, pnl: 43000, ytdReturn: 11.3 },
        { date: 'Oct 26', nav: 1361000, pnl: 29000, ytdReturn: 13.5 },
        { date: 'Nov 26', nav: 1342000, pnl: -19000, ytdReturn: 11.9 },
        { date: 'Dec 26', nav: 1392000, pnl: 49000, ytdReturn: 15.9 },
    ];
    return (
        <KpiCard17
            chartData={chartData}
            metrics={[
                { name: 'Portfolio NAV', chartCategory: 'nav', valueFormatter: fmtCurrency },
                { name: 'Monthly P&L', chartCategory: 'pnl', valueFormatter: fmtCurrency },
                { name: 'YTD Return', chartCategory: 'ytdReturn', valueFormatter: fmtPct },
            ]}
            indexField="date"
            cols={3}
        />
    );
};

// ─── KpiCard18Example ───────────────────────────────────────────────────────────────

export const KpiCard18Example = () => {
    const fmtCurrency = (n: number) => `$${Intl.NumberFormat('en-US').format(Math.round(n))}`;
    const fmtMillions = (n: number) => `$${(n / 1_000_000).toFixed(1)}M`;
    const fmtPct = (n: number) => `${n >= 0 ? '+' : ''}${n.toFixed(2)}%`;
    const chartData = [
        { date: 'Jan 26', aum: 2340000, sharpe: 1.12, drawdown: -2.1 },
        { date: 'Feb 26', aum: 2480000, sharpe: 1.28, drawdown: -1.8 },
        { date: 'Mar 26', aum: 2310000, sharpe: 0.95, drawdown: -4.2 },
        { date: 'Apr 26', aum: 2620000, sharpe: 1.45, drawdown: -1.2 },
        { date: 'May 26', aum: 2700000, sharpe: 1.61, drawdown: -0.9 },
        { date: 'Jun 26', aum: 2590000, sharpe: 1.38, drawdown: -2.4 },
        { date: 'Jul 26', aum: 2810000, sharpe: 1.72, drawdown: -0.7 },
        { date: 'Aug 26', aum: 2750000, sharpe: 1.55, drawdown: -1.5 },
        { date: 'Sep 26', aum: 2930000, sharpe: 1.89, drawdown: -0.6 },
        { date: 'Oct 26', aum: 3010000, sharpe: 1.95, drawdown: -1.0 },
        { date: 'Nov 26', aum: 2880000, sharpe: 1.64, drawdown: -2.8 },
        { date: 'Dec 26', aum: 3150000, sharpe: 2.01, drawdown: -0.4 },
    ];
    return (
        <KpiCard18
            chartData={chartData}
            metrics={[
                { name: 'AUM', chartCategory: 'aum', valueFormatter: fmtMillions },
                { name: 'Sharpe Ratio', chartCategory: 'sharpe', valueFormatter: (n) => n.toFixed(2) },
                { name: 'Max Drawdown', chartCategory: 'drawdown', valueFormatter: fmtPct },
            ]}
            indexField="date"
            cols={3}
        />
    );
};

// ─── KpiCard19Example ───────────────────────────────────────────────────────────────

export const KpiCard19Example = () => {
    const fmtCurrency = (n: number) => `$${Intl.NumberFormat('en-US').format(Math.round(n))}`;
    const chartData = [
        { date: 'Jan 26', equities: 1850000, fixedIncome: 620000, alternatives: 310000 },
        { date: 'Feb 26', equities: 1920000, fixedIncome: 645000, alternatives: 325000 },
        { date: 'Mar 26', equities: 1780000, fixedIncome: 660000, alternatives: 318000 },
        { date: 'Apr 26', equities: 2010000, fixedIncome: 638000, alternatives: 340000 },
        { date: 'May 26', equities: 2090000, fixedIncome: 625000, alternatives: 355000 },
        { date: 'Jun 26', equities: 1980000, fixedIncome: 648000, alternatives: 342000 },
        { date: 'Jul 26', equities: 2180000, fixedIncome: 635000, alternatives: 368000 },
        { date: 'Aug 26', equities: 2140000, fixedIncome: 622000, alternatives: 362000 },
        { date: 'Sep 26', equities: 2320000, fixedIncome: 641000, alternatives: 381000 },
        { date: 'Oct 26', equities: 2410000, fixedIncome: 658000, alternatives: 395000 },
        { date: 'Nov 26', equities: 2280000, fixedIncome: 672000, alternatives: 388000 },
        { date: 'Dec 26', equities: 2520000, fixedIncome: 685000, alternatives: 412000 },
    ];
    return (
        <KpiCard19
            chartData={chartData}
            metrics={[
                { name: 'Equities', chartCategory: 'equities', valueFormatter: fmtCurrency, deltaFormatter: fmtCurrency },
                { name: 'Fixed Income', chartCategory: 'fixedIncome', valueFormatter: fmtCurrency, deltaFormatter: fmtCurrency },
                { name: 'Alternatives', chartCategory: 'alternatives', valueFormatter: fmtCurrency, deltaFormatter: fmtCurrency },
            ]}
            indexField="date"
            cols={3}
        />
    );
};

// ─── KpiCard20Example ───────────────────────────────────────────────────────────────

export const KpiCard20Example = () => {
    const data: HeartRateMetric[] = [
        //array-start
        {
            name: 'Running',
            stat: '156',
            activities: [
                {
                    type: 'Endurance',
                    share: '25.5%',
                    zone: '<126',
                    href: '#',
                },
                {
                    type: 'Moderate',
                    share: '35.3%',
                    zone: '126-157',
                    href: '#',
                },
                {
                    type: 'Tempo',
                    share: '14.2%',
                    zone: '157-173',
                    href: '#',
                },
                {
                    type: 'Threshold',
                    share: '25.0%',
                    zone: '173-189',
                    href: '#',
                },
            ],
        },
        {
            name: 'Cycling',
            stat: '142',
            activities: [
                {
                    type: 'Endurance',
                    share: '20.2%',
                    zone: '<126',
                    href: '#',
                },
                {
                    type: 'Moderate',
                    share: '45.6%',
                    zone: '126-157',
                    href: '#',
                },
                {
                    type: 'Tempo',
                    share: '15.7%',
                    zone: '157-173',
                    href: '#',
                },
                {
                    type: 'Threshold',
                    share: '18.5%',
                    zone: '173-189',
                    href: '#',
                },
            ],
        },
        {
            name: 'Strength',
            stat: '113',
            activities: [
                {
                    type: 'Endurance',
                    share: '80.1%',
                    zone: '<126',
                    href: '#',
                },
                {
                    type: 'Moderate',
                    share: '9.9%',
                    zone: '126-157',
                    href: '#',
                },
                {
                    type: 'Tempo',
                    share: '6.2%',
                    zone: '157-173',
                    href: '#',
                },
                {
                    type: 'Threshold',
                    share: '3.8%',
                    zone: '173-189',
                    href: '#',
                },
            ],
        },
        //array-end
    ];

    return <KpiCard20 metrics={data} />;
};

// ─── KpiCard21Example ───────────────────────────────────────────────────────────────

export const KpiCard21Example = () => {
    const categoryData: CategoryItem[] = [
        //array-start
        {
            name: 'Average tokes per requests',
            total: '341',
            split: [136, 205],
            details: [
                {
                    name: 'Completion tokens',
                    value: '136',
                },
                {
                    name: 'Prompt tokens',
                    value: '205',
                },
            ],
        },
        {
            name: 'Total tokens',
            total: '4,229',
            split: [1480, 2749],
            details: [
                {
                    name: 'Completion tokens',
                    value: '1,480',
                },
                {
                    name: 'Prompt tokens',
                    value: '2,749',
                },
            ],
        },
        {
            name: 'Total tokens by advanced model',
            total: '1,040',
            split: [260, 780],
            details: [
                {
                    name: 'Completion tokens',
                    value: '260',
                },
                {
                    name: 'Prompt tokens',
                    value: '780',
                },
            ],
        },
        {
            name: 'Total tokens by base model',
            total: '2,920',
            split: [847, 2073],
            details: [
                {
                    name: 'Completion tokens',
                    value: '847',
                },
                {
                    name: 'Prompt tokens',
                    value: '2,073',
                },
            ],
        },
        //array-end
    ];

    return <KpiCard21 metrics={categoryData} />;
};

// ─── KpiCard22Example ───────────────────────────────────────────────────────────────

export const KpiCard22Example = () => {
    const data: TokenMetric[] = [
        {
            name: 'Bitcoin',
            total: '2.5 BTC',
            details: [
                { name: 'Holdings', value: '1.2 BTC', percentageValue: 48 },
                { name: 'Staking', value: '0.8 BTC', percentageValue: 32 },
                { name: 'Other', value: '0.5 BTC', percentageValue: 20 },
            ],
        },
        {
            name: 'Ethereum',
            total: '15.3 ETH',
            details: [
                { name: 'Holdings', value: '8.5 ETH', percentageValue: 56 },
                { name: 'Staking', value: '4.2 ETH', percentageValue: 27 },
                { name: 'Other', value: '2.6 ETH', percentageValue: 17 },
            ],
        },
        {
            name: 'Solana',
            total: '250 SOL',
            details: [
                { name: 'Holdings', value: '150 SOL', percentageValue: 60 },
                { name: 'Staking', value: '75 SOL', percentageValue: 30 },
                { name: 'Other', value: '25 SOL', percentageValue: 10 },
            ],
        },
        {
            name: 'Cardano',
            total: '500 ADA',
            details: [
                { name: 'Holdings', value: '300 ADA', percentageValue: 60 },
                { name: 'Staking', value: '150 ADA', percentageValue: 30 },
                { name: 'Other', value: '50 ADA', percentageValue: 10 },
            ],
        },
    ];

    return <KpiCard22 metrics={data} />;
};

// ─── KpiCard23Example ───────────────────────────────────────────────────────────────

export const KpiCard23Example = () => {
    const data: SalesChannel[] = [
        {
            channel: 'Online',
            share: 45,
            revenue: '$131,580',
            color: 'bg-blue-500',
            href: '#online',
        },
        {
            channel: 'Retail',
            share: 30,
            revenue: '$87,720',
            color: 'bg-amber-500',
            href: '#retail',
        },
        {
            channel: 'Partners',
            share: 15,
            revenue: '$43,860',
            color: 'bg-cyan-500',
            href: '#partners',
        },
        {
            channel: 'Wholesale',
            share: 10,
            revenue: '$29,240',
            color: 'bg-gray-500',
            href: '#wholesale',
        },
    ];

    return (
        <KpiCard23
            title="Total sales"
            totalSales="$292,400"
            subtitle="Sales channel distribution"
            channels={data}
        />
    );
};

// ─── KpiCard24Example ───────────────────────────────────────────────────────────────

export const KpiCard24Example = () => {
    const data: MetricCardItem[] = [
        {
            name: 'Revenue',
            stat: '10,450',
            change: '-12.5%',
            changeType: 'negative',
            icon: RiCashLine,
            top3: {
                'Membership Dues': 4734,
                Fundraisers: 3233,
                Donations: 2483,
            },
        },
        {
            name: 'Expenses',
            stat: '3,382',
            change: '+1.8%',
            changeType: 'positive',
            icon: RiSafeLine,
            top3: {
                'Operational Costs': 1691,
                Marketing: 845,
                Equipment: 846,
            },
        },
        {
            name: 'Engagement',
            stat: '80.2%',
            change: '+19.7%',
            changeType: 'positive',
            icon: RiLinksLine,
            top3: {
                'Social Media Interactions': 40.1,
                'Event Attendance': 24.1,
                'Volunteer Participation': 16.0,
            },
        },
    ];

    return <KpiCard24 metrics={data} />;
};

// ─── KpiCard25Example ───────────────────────────────────────────────────────────────

export const KpiCard25Example = () => {
    const data: MetricCard[] = [
        {
            title: 'Current Tickets',
            value: '247',
            values: [82, 13, 5],
            details: [
                { percentage: '82%', label: 'Resolved', color: 'bg-blue-500 dark:bg-blue-500' },
                { percentage: '13%', label: 'Progress', color: 'bg-gray-500' },
                { percentage: '5%', label: 'Escalated', color: 'bg-red-500 dark:bg-red-500' },
            ],
        },
        {
            title: 'Database Queries',
            value: '44757',
            values: [57, 12, 31],
            details: [
                { percentage: '57%', label: 'Optimized', color: 'bg-blue-500 dark:bg-blue-500' },
                { percentage: '12%', label: 'Editing', color: 'bg-gray-500' },
                { percentage: '31%', label: 'Slow', color: 'bg-red-500 dark:bg-red-500' },
            ],
        },
        {
            title: 'Query Latency',
            value: '1,247ms',
            values: [75, 20, 5],
            details: [
                { percentage: '75%', label: 'Fast', color: 'bg-blue-500 dark:bg-blue-500' },
                { percentage: '20%', label: 'Medium', color: 'bg-gray-500' },
                { percentage: '5%', label: 'Slow', color: 'bg-red-500 dark:bg-red-500' },
            ],
        },
    ];

    return <KpiCard25 cards={data} />;
};

// ─── KpiCard26Example ───────────────────────────────────────────────────────────────

export const KpiCard26Example = () => {
    const data: KpiCard26MetricItem[] = [
        {
            title: 'SLA Performance',
            primaryLabel: {
                label: 'Within SLA',
                percentage: '83.3%',
                color: 'bg-blue-500 dark:bg-blue-500',
            },
            secondaryLabel: {
                label: 'SLA Breached',
                percentage: '16.7%',
                color: 'bg-red-500 dark:bg-red-500',
            },
            progressValue: 83,
        },
        {
            title: 'Response Time',
            primaryLabel: {
                label: 'Under Threshold',
                percentage: '95.8%',
                color: 'bg-blue-500 dark:bg-blue-500',
            },
            secondaryLabel: {
                label: 'Over Threshold',
                percentage: '4.2%',
                color: 'bg-red-500 dark:bg-red-500',
            },
            progressValue: 96,
        },
        {
            title: 'Cache Performance',
            primaryLabel: {
                label: 'Cache Hits',
                percentage: '78.4%',
                color: 'bg-blue-500 dark:bg-blue-500',
            },
            secondaryLabel: {
                label: 'Cache Misses',
                percentage: '21.6%',
                color: 'bg-red-500 dark:bg-red-500',
            },
            progressValue: 78,
        },
    ];

    return <KpiCard26 metrics={data} />;
};

// ─── KpiCard27Example ───────────────────────────────────────────────────────────────

export const KpiCard27Example = () => {
    const data: ChartMetric[] = [
        {
            title: 'Call Volume Trends',
            labels: {
                Today: 'Today',
                Yesterday: 'Yesterday',
            },
            values: {
                Today: 573,
                Yesterday: 451,
            },
            data: [
                { time: '0:00 AM', Today: 280, Yesterday: 220 },
                { time: '1:00 AM', Today: 210, Yesterday: 180 },
                { time: '2:00 AM', Today: 190, Yesterday: 150 },
                { time: '3:00 AM', Today: 170, Yesterday: 130 },
                { time: '4:00 AM', Today: 220, Yesterday: 160 },
                { time: '5:00 AM', Today: 290, Yesterday: 200 },
                { time: '6:00 AM', Today: 350, Yesterday: 250 },
                { time: '7:00 AM', Today: 420, Yesterday: 310 },
                { time: '8:00 AM', Today: 480, Yesterday: 340 },
                { time: '9:00 AM', Today: 510, Yesterday: 380 },
                { time: '10:00 AM', Today: 490, Yesterday: 360 },
                { time: '11:59 AM', Today: 450, Yesterday: 330 },
            ],
            categories: ['Today', 'Yesterday'],
            colors: ['blue', 'gray'],
        },
        {
            title: 'Query Volume Trends',
            labels: {
                Today: 'Today',
                Yesterday: 'Yesterday',
            },
            values: {
                Today: '5,730',
                Yesterday: '4,510',
            },
            data: [
                { time: '0:00 AM', Current: 2800, Previous: 2200 },
                { time: '1:00 AM', Current: 2100, Previous: 1800 },
                { time: '2:00 AM', Current: 1900, Previous: 1500 },
                { time: '3:00 AM', Current: 1700, Previous: 1300 },
                { time: '4:00 AM', Current: 2200, Previous: 1600 },
                { time: '5:00 AM', Current: 2900, Previous: 2000 },
                { time: '6:00 AM', Current: 3500, Previous: 2500 },
                { time: '7:00 AM', Current: 4200, Previous: 3100 },
                { time: '8:00 AM', Current: 4800, Previous: 3400 },
                { time: '9:00 AM', Current: 5100, Previous: 1800 },
                { time: '10:00 AM', Current: 4900, Previous: 1600 },
                { time: '11:59 AM', Current: 4500, Previous: 3300 },
            ],
            categories: ['Current', 'Previous'],
            colors: ['blue', 'gray'],
        },
        {
            title: 'ETL Pipeline Performance',
            labels: {
                ProcessingTime: 'Processing (ms)',
                DataVolume: 'Volume (MB)',
            },
            values: {
                ProcessingTime: '4,200',
                DataVolume: '3,000',
            },
            data: [
                { time: '0:00 AM', ProcessingTime: 1200, DataVolume: 1000 },
                { time: '1:00 AM', ProcessingTime: 900, DataVolume: 600 },
                { time: '2:00 AM', ProcessingTime: 800, DataVolume: 500 },
                { time: '3:00 AM', ProcessingTime: 1200, DataVolume: 900 },
                { time: '4:00 AM', ProcessingTime: 2100, DataVolume: 1700 },
                { time: '5:00 AM', ProcessingTime: 1500, DataVolume: 1000 },
                { time: '6:00 AM', ProcessingTime: 2200, DataVolume: 1500 },
                { time: '7:00 AM', ProcessingTime: 3100, DataVolume: 2000 },
                { time: '8:00 AM', ProcessingTime: 3800, DataVolume: 2500 },
                { time: '9:00 AM', ProcessingTime: 4200, DataVolume: 3000 },
                { time: '10:00 AM', ProcessingTime: 3900, DataVolume: 2800 },
                { time: '11:59 AM', ProcessingTime: 3500, DataVolume: 2400 },
            ],
            categories: ['ProcessingTime', 'DataVolume'],
            colors: ['pink', 'fuchsia'],
        },
    ];

    return <KpiCard27 metrics={data} />;
};

// ─── KpiCard28Example ───────────────────────────────────────────────────────────────

export const KpiCard28Example = () => {
    const metricsData: KpiCard28Metric[][] = [
        [
            { label: 'Total Users', value: '125,430', change: '+17%', changeType: 'positive' },
            { label: 'Average CSAT Score', value: '4.5', change: '+6%', changeType: 'positive' },
            { label: 'Average Response Time', value: '8.3m', change: '+12%', changeType: 'positive' },
        ],
        [
            { label: 'Total Tickets', value: '45,892', change: '+11%', changeType: 'positive' },
            { label: 'Resolution Rate', value: '92.5%', change: '+2%', changeType: 'positive' },
            { label: 'Total Cohorts', value: '24', change: '+5%', changeType: 'positive' },
        ],
        [
            { label: 'Avg. Handling Time', value: '15.2m', change: '+21%', changeType: 'positive' },
            { label: 'First Contact Resolution', value: '85.7%', change: '+3%', changeType: 'positive' },
            { label: 'Retention Rate', value: '94.3%', change: '+2%', changeType: 'positive' },
        ],
    ];

    const issuesData: IssueItem[] = [
        { category: 'Account Service', totalCount: 1815, percentage: 15 },
        { category: 'Claim Status', totalCount: 1599, percentage: 13 },
        { category: 'Coverage Inquiry', totalCount: 1390, percentage: 12 },
        { category: 'Accident Report', totalCount: 1388, percentage: 12 },
        { category: 'Fraud Report', totalCount: 1301, percentage: 11 },
        { category: 'Complaint', totalCount: 1282, percentage: 11 },
    ];

    return <KpiCard28 metrics={metricsData} issues={issuesData} />;
};

// ─── KpiCard29Example ───────────────────────────────────────────────────────────────

export const KpiCard29Example = () => {
    const metricsData: Metric[] = [
        {
            label: 'Lead-to-Quote Ratio',
            value: 0.61,
            percentage: '59.8%',
            fraction: '450/752',
        },
        {
            label: 'Project Load',
            value: 0.24,
            percentage: '12.9%',
            fraction: '129/1K',
        },
        {
            label: 'Win Probability',
            value: 0.8,
            percentage: '85.1%',
            fraction: '280/329',
        },
    ];

    return <KpiCard29 metrics={metricsData} />;
};

// ─── KpiCard05FourItemsExample (4 Items Test) ────────────────────────────────

export const KpiCard05FourItemsExample = () => {
    const data: MetricItem[] = [
        {
            name: 'Total revenue',
            stat: '$128.5K',
            previousStat: '$115.2K',
            change: '+11.5%',
            changeType: 'positive',
        },
        {
            name: 'Active customers',
            stat: '1,240',
            previousStat: '1,089',
            change: '+13.9%',
            changeType: 'positive',
        },
        {
            name: 'Avg order value',
            stat: '$342',
            previousStat: '$298',
            change: '+14.8%',
            changeType: 'positive',
        },
        {
            name: 'Conversion rate',
            stat: '3.2%',
            previousStat: '2.8%',
            change: '+14.3%',
            changeType: 'positive',
        },
    ];

    return <KpiCard05 metrics={data} cols={4} />;
};
