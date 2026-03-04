import React from 'react';

import { LineChart01 } from '../line-chart-01';
import { LineChart02 } from '../line-chart-02';
import { ChartGroupItem, LineChart03 } from '../line-chart-03';
import { LineChart04 } from '../line-chart-04';
import { LineChart05 } from '../line-chart-05';
import { ChartSummaryItem, TabDefinition, LineChart06 } from '../line-chart-06';
import { SeriesSummaryItem, RangeTab, LineChart07 } from '../line-chart-07';
import { SeriesSummaryItem as LineChart08SeriesSummaryItem, LineChart08 } from '../line-chart-08';
import { LineChart09 } from '../line-chart-09';

// ─── LineChart01Example ─────────────────────────────────────────────────────────────

export const LineChart01Example = () => {
    const data = [
        { date: 'Jan 23', Organic: 232, Sponsored: 0, Affiliate: 49 },
        { date: 'Feb 23', Organic: 241, Sponsored: 0, Affiliate: 61 },
        { date: 'Mar 23', Organic: 291, Sponsored: 0, Affiliate: 55 },
        { date: 'Apr 23', Organic: 101, Sponsored: 0, Affiliate: 21 },
        { date: 'May 23', Organic: 318, Sponsored: 0, Affiliate: 66 },
        { date: 'Jun 23', Organic: 205, Sponsored: 0, Affiliate: 69 },
        { date: 'Jul 23', Organic: 372, Sponsored: 0, Affiliate: 55 },
        { date: 'Aug 23', Organic: 341, Sponsored: 0, Affiliate: 74 },
        { date: 'Sep 23', Organic: 387, Sponsored: 120, Affiliate: 190 },
        { date: 'Oct 23', Organic: 220, Sponsored: 0, Affiliate: 89 },
        { date: 'Nov 23', Organic: 372, Sponsored: 0, Affiliate: 44 },
        { date: 'Dec 23', Organic: 321, Sponsored: 0, Affiliate: 93 },
    ];

    return (
        <LineChart01
            data={data}
            title="Units sold by channel"
            categories={['Organic', 'Sponsored', 'Affiliate']}
            colors={['blue', 'violet', 'fuchsia']}
            summary={[
                { name: 'Organic', value: 3273 },
                { name: 'Sponsored', value: 120 },
                { name: 'Affiliate', value: 866 },
            ]}
        />
    );
};

// ─── LineChart02Example ─────────────────────────────────────────────────────────────

export const LineChart02Example = () => {
    const data = [
        { date: 'Aug 01', price: 21.2 },
        { date: 'Aug 02', price: 29.0 },
        { date: 'Aug 03', price: 48.5 },
        { date: 'Aug 04', price: 53.8 },
        { date: 'Aug 05', price: 57.7 },
        { date: 'Aug 06', price: 59.9 },
        { date: 'Aug 07', price: 41.4 },
        { date: 'Aug 08', price: 60.2 },
        { date: 'Aug 09', price: 62.8 },
        { date: 'Aug 10', price: 62.5 },
        { date: 'Aug 11', price: 63.6 },
        { date: 'Aug 12', price: 64.4 },
        { date: 'Aug 13', price: 65.1 },
        { date: 'Aug 14', price: 66.4 },
        { date: 'Aug 15', price: 71.6 },
        { date: 'Aug 16', price: 79.5 },
        { date: 'Aug 17', price: 102.8 },
        { date: 'Aug 18', price: 103.2 },
        { date: 'Aug 19', price: 105.4 },
        { date: 'Aug 20', price: 110.9 },
        { date: 'Aug 21', price: 67.7 },
        { date: 'Aug 22', price: 69.8 },
        { date: 'Aug 23', price: 79.5 },
        { date: 'Aug 24', price: 90.0 },
        { date: 'Aug 25', price: 91.2 },
        { date: 'Aug 26', price: 95.1 },
        { date: 'Aug 27', price: 99.8 },
        { date: 'Aug 28', price: 100.6 },
        { date: 'Aug 29', price: 102.8 },
        { date: 'Aug 30', price: 100.5 },
        { date: 'Aug 31', price: 111.6 },
        { date: 'Sep 01', price: 123.2 },
        { date: 'Sep 02', price: 125.8 },
        { date: 'Sep 03', price: 120.4 },
        { date: 'Sep 04', price: 121.9 },
        { date: 'Sep 05', price: 124.5 },
        { date: 'Sep 06', price: 127.7 },
        { date: 'Sep 07', price: 129.2 },
        { date: 'Sep 08', price: 130.8 },
        { date: 'Sep 09', price: 134.4 },
        { date: 'Sep 10', price: 136.0 },
        { date: 'Sep 11', price: 137.5 },
        { date: 'Sep 12', price: 131.1 },
        { date: 'Sep 13', price: 128.6 },
        { date: 'Sep 14', price: 124.2 },
        { date: 'Sep 15', price: 120.8 },
        { date: 'Sep 16', price: 118.3 },
        { date: 'Sep 17', price: 101.9 },
        { date: 'Sep 18', price: 121.5 },
        { date: 'Sep 19', price: 129.1 },
        { date: 'Sep 20', price: 131.6 },
        { date: 'Sep 21', price: 141.2 },
        { date: 'Sep 22', price: 142.8 },
        { date: 'Sep 23', price: 143.3 },
        { date: 'Sep 24', price: 149.9 },
        { date: 'Sep 25', price: 159.5 },
        { date: 'Sep 26', price: 173.3 },
    ];

    return (
        <LineChart02
            data={data}
            subtitle="Amazon, Inc. (AMZN)"
            value="$173.30"
            change="+$9.30 (8.6%)"
            changeType="positive"
            summary={[
                { name: 'Open', value: '$153.56' },
                { name: 'High', value: '$154.78' },
                { name: 'Volume', value: '$48.14M' },
                { name: 'Low', value: '$179.12' },
                { name: 'Close', value: '$173.34' },
                { name: 'Market Cap', value: '$1.58B' },
            ]}
        />
    );
};

// ─── LineChart03Example ─────────────────────────────────────────────────────────────

export const LineChart03Example = () => {
    const data = [
        { date: 'Jan 23', Munich: 42340, Zurich: 22320, Vienna: 12410 },
        { date: 'Feb 23', Munich: 50120, Zurich: 32310, Vienna: 10300 },
        { date: 'Mar 23', Munich: 45190, Zurich: 23450, Vienna: 10900 },
        { date: 'Apr 23', Munich: 56420, Zurich: 13400, Vienna: 7900 },
        { date: 'May 23', Munich: 40420, Zurich: 16400, Vienna: 12310 },
        { date: 'Jun 23', Munich: 47010, Zurich: 18350, Vienna: 10250 },
        { date: 'Jul 23', Munich: 47490, Zurich: 19950, Vienna: 12650 },
        { date: 'Aug 23', Munich: 39610, Zurich: 10910, Vienna: 4650 },
        { date: 'Sep 23', Munich: 45860, Zurich: 24740, Vienna: 12650 },
        { date: 'Oct 23', Munich: 50910, Zurich: 15740, Vienna: 10430 },
        { date: 'Nov 23', Munich: 4919, Zurich: 2874, Vienna: 2081 },
        { date: 'Dec 23', Munich: 5519, Zurich: 2274, Vienna: 1479 },
    ];

    const summary: ChartGroupItem[] = [
        {
            location: 'Munich',
            address: 'Maximilianstrasse',
            color: 'bg-blue-500 dark:bg-blue-500',
            type: 'Flagship',
            total: '$460.2K',
            change: '+0.7%',
            changeType: 'positive',
        },
        {
            location: 'Zurich',
            address: 'Bahnhofstrasse',
            color: 'bg-violet-500 dark:bg-violet-500',
            type: 'In-Store',
            total: '$237.3K',
            change: '-1.2%',
            changeType: 'negative',
        },
        {
            location: 'Vienna',
            address: 'Stephansplatz',
            color: 'bg-fuchsia-500 dark:bg-fuchsia-500',
            type: 'In-Store',
            total: '$118.2K',
            change: '+4.6%',
            changeType: 'positive',
        },
    ];

    return (
        <LineChart03
            data={data}
            headline="Revenue"
            headlineValue="$815,700"
            categories={['Munich', 'Zurich', 'Vienna']}
            colors={['blue', 'violet', 'fuchsia']}
            summary={summary}
        />
    );
};

// ─── LineChart04Example ─────────────────────────────────────────────────────────────

export const LineChart04Example = () => {
    interface DataPoint {
        date: string;
        currentMonth: number | null;
        lastMonth: number;
    }

    const rawData: DataPoint[] = [
        { date: 'Jun 01', currentMonth: 4837, lastMonth: 1492 },
        { date: 'Jun 02', currentMonth: 503, lastMonth: 1738 },
        { date: 'Jun 03', currentMonth: 2341, lastMonth: 56 },
        { date: 'Jun 04', currentMonth: 1089, lastMonth: 87 },
        { date: 'Jun 05', currentMonth: 578, lastMonth: 15 },
        { date: 'Jun 06', currentMonth: 312, lastMonth: 2301 },
        { date: 'Jun 07', currentMonth: 9695, lastMonth: 5124 },
        { date: 'Jun 08', currentMonth: 12451, lastMonth: 9398 },
        { date: 'Jun 09', currentMonth: 2784, lastMonth: 4267 },
        { date: 'Jun 10', currentMonth: 569, lastMonth: 1509 },
        { date: 'Jun 11', currentMonth: 906, lastMonth: 1356 },
        { date: 'Jun 12', currentMonth: 4738, lastMonth: 671 },
        { date: 'Jun 13', currentMonth: 4012, lastMonth: 483 },
        { date: 'Jun 14', currentMonth: 2845, lastMonth: 729 },
        { date: 'Jun 15', currentMonth: 3167, lastMonth: 2594 },
        { date: 'Jun 16', currentMonth: 934, lastMonth: 11812 },
        { date: 'Jun 17', currentMonth: 256, lastMonth: 1778 },
        { date: 'Jun 18', currentMonth: 89, lastMonth: 14945 },
        { date: 'Jun 19', currentMonth: 312, lastMonth: 10803 },
        { date: 'Jun 20', currentMonth: 6278, lastMonth: 3067 },
        { date: 'Jun 21', currentMonth: 2729, lastMonth: 941 },
        { date: 'Jun 22', currentMonth: null, lastMonth: 184 },
        { date: 'Jun 23', currentMonth: null, lastMonth: 152 },
        { date: 'Jun 24', currentMonth: null, lastMonth: 5326 },
        { date: 'Jun 25', currentMonth: null, lastMonth: 2189 },
        { date: 'Jun 26', currentMonth: null, lastMonth: 11457 },
        { date: 'Jun 27', currentMonth: null, lastMonth: 3295 },
        { date: 'Jun 28', currentMonth: null, lastMonth: 1581 },
        { date: 'Jun 29', currentMonth: null, lastMonth: 2423 },
        { date: 'Jun 30', currentMonth: null, lastMonth: 678 },
    ];

    const calculateCumulativeData = (data: DataPoint[]): DataPoint[] => {
        let cumulativeCurrentMonth = 0;
        let cumulativeLastMonth = 0;
        let lastValidCurrentMonth: number | null = null;

        return data.map((point: any) => {
            if (point.currentMonth !== null) {
                cumulativeCurrentMonth += point.currentMonth;
                lastValidCurrentMonth = cumulativeCurrentMonth;
            }
            cumulativeLastMonth += point.lastMonth || 0;

            return {
                date: point.date,
                currentMonth: point.currentMonth !== null ? lastValidCurrentMonth : null,
                lastMonth: cumulativeLastMonth,
            };
        });
    };

    const cumulativeData = calculateCumulativeData(rawData);

    return (
        <LineChart04
            data={cumulativeData}
            description="Customized chart using a month to date calculation"
        />
    );
};

// ─── LineChart05Example ─────────────────────────────────────────────────────────────

export const LineChart05Example = () => {
    interface DataPoint {
        date: string;
        currentMonth: number | null;
        lastMonth: number;
    }

    const rawData: DataPoint[] = [
        { date: 'Jun 01', currentMonth: 4837, lastMonth: 1492 },
        { date: 'Jun 02', currentMonth: 503, lastMonth: 1738 },
        { date: 'Jun 03', currentMonth: 2341, lastMonth: 56 },
        { date: 'Jun 04', currentMonth: 1089, lastMonth: 87 },
        { date: 'Jun 05', currentMonth: 578, lastMonth: 15 },
        { date: 'Jun 06', currentMonth: 312, lastMonth: 2301 },
        { date: 'Jun 07', currentMonth: 9695, lastMonth: 5124 },
        { date: 'Jun 08', currentMonth: 12451, lastMonth: 9398 },
        { date: 'Jun 09', currentMonth: 2784, lastMonth: 4267 },
        { date: 'Jun 10', currentMonth: 569, lastMonth: 1509 },
        { date: 'Jun 11', currentMonth: 906, lastMonth: 1356 },
        { date: 'Jun 12', currentMonth: 4738, lastMonth: 671 },
        { date: 'Jun 13', currentMonth: 4012, lastMonth: 483 },
        { date: 'Jun 14', currentMonth: 2845, lastMonth: 729 },
        { date: 'Jun 15', currentMonth: 3167, lastMonth: 2594 },
        { date: 'Jun 16', currentMonth: 934, lastMonth: 11812 },
        { date: 'Jun 17', currentMonth: 256, lastMonth: 1778 },
        { date: 'Jun 18', currentMonth: 89, lastMonth: 14945 },
        { date: 'Jun 19', currentMonth: 312, lastMonth: 10803 },
        { date: 'Jun 20', currentMonth: 6278, lastMonth: 3067 },
        { date: 'Jun 21', currentMonth: 2729, lastMonth: 941 },
        { date: 'Jun 22', currentMonth: null, lastMonth: 184 },
        { date: 'Jun 23', currentMonth: null, lastMonth: 152 },
        { date: 'Jun 24', currentMonth: null, lastMonth: 5326 },
        { date: 'Jun 25', currentMonth: null, lastMonth: 2189 },
        { date: 'Jun 26', currentMonth: null, lastMonth: 11457 },
        { date: 'Jun 27', currentMonth: null, lastMonth: 3295 },
        { date: 'Jun 28', currentMonth: null, lastMonth: 1581 },
        { date: 'Jun 29', currentMonth: null, lastMonth: 2423 },
        { date: 'Jun 30', currentMonth: null, lastMonth: 678 },
    ];

    const calculateCumulativeData = (data: DataPoint[]): DataPoint[] => {
        let cumulativeCurrentMonth = 0;
        let cumulativeLastMonth = 0;
        let lastValidCurrentMonth: number | null = null;

        return data.map((point: any) => {
            if (point.currentMonth !== null) {
                cumulativeCurrentMonth += point.currentMonth;
                lastValidCurrentMonth = cumulativeCurrentMonth;
            }
            cumulativeLastMonth += point.lastMonth || 0;

            return {
                date: point.date,
                currentMonth: point.currentMonth !== null ? lastValidCurrentMonth : null,
                lastMonth: cumulativeLastMonth,
            };
        });
    };

    const currencyFormatter = (number: number) => {
        return Intl.NumberFormat('en').format(number);
    };

    const cumulativeData = calculateCumulativeData(rawData);
    const companyLimit = 105_000;

    return (
        <LineChart05
            data={cumulativeData}
            description="Customized chart using a month to date calculation"
            referenceLine={{
                value: companyLimit,
                label: `Usage limit: ${currencyFormatter(companyLimit)}`,
            }}
        />
    );
};

// ─── LineChart06Example ─────────────────────────────────────────────────────────────

export const LineChart06Example = () => {
    const data = [
        { date: 'Aug 01', 'Market Index': 44.1, Portfolio: 79.2 },
        { date: 'Aug 02', 'Market Index': 49.1, Portfolio: 89.1 },
        { date: 'Aug 03', 'Market Index': 61.2, Portfolio: 91.7 },
        { date: 'Aug 04', 'Market Index': 49.7, Portfolio: 74.4 },
        { date: 'Aug 05', 'Market Index': 71.1, Portfolio: 95.3 },
        { date: 'Aug 06', 'Market Index': 75.3, Portfolio: 99.4 },
        { date: 'Aug 07', 'Market Index': 74.1, Portfolio: 101.2 },
        { date: 'Aug 08', 'Market Index': 78.4, Portfolio: 102.2 },
        { date: 'Aug 09', 'Market Index': 81.1, Portfolio: 103.6 },
        { date: 'Aug 10', 'Market Index': 82.6, Portfolio: 104.4 },
        { date: 'Aug 11', 'Market Index': 89.3, Portfolio: 106.3 },
        { date: 'Aug 12', 'Market Index': 79.3, Portfolio: 109.5 },
        { date: 'Aug 13', 'Market Index': 78.6, Portfolio: 110.4 },
        { date: 'Aug 14', 'Market Index': 73.8, Portfolio: 113.5 },
        { date: 'Aug 15', 'Market Index': 69.7, Portfolio: 114.1 },
        { date: 'Aug 16', 'Market Index': 62.6, Portfolio: 121.4 },
        { date: 'Aug 17', 'Market Index': 59.3, Portfolio: 120.4 },
        { date: 'Aug 18', 'Market Index': 57.1, Portfolio: 110.7 },
        { date: 'Aug 19', 'Market Index': 55.1, Portfolio: 118.8 },
        { date: 'Aug 20', 'Market Index': 54.3, Portfolio: 123.1 },
        { date: 'Aug 21', 'Market Index': 53.2, Portfolio: 110.2 },
        { date: 'Aug 22', 'Market Index': 49.4, Portfolio: 101.2 },
        { date: 'Aug 23', 'Market Index': 48.1, Portfolio: 99.2 },
        { date: 'Aug 24', 'Market Index': 27.1, Portfolio: 105.8 },
        { date: 'Aug 25', 'Market Index': 21.0, Portfolio: 109.4 },
        { date: 'Aug 26', 'Market Index': 21.3, Portfolio: 110.1 },
        { date: 'Aug 27', 'Market Index': 21.8, Portfolio: 119.6 },
        { date: 'Aug 28', 'Market Index': 29.4, Portfolio: 121.3 },
        { date: 'Aug 29', 'Market Index': 32.4, Portfolio: 129.1 },
        { date: 'Aug 30', 'Market Index': 37.1, Portfolio: 134.5 },
        { date: 'Aug 31', 'Market Index': 41.3, Portfolio: 144.2 },
        { date: 'Sep 01', 'Market Index': 48.1, Portfolio: 145.1 },
        { date: 'Sep 02', 'Market Index': 51.3, Portfolio: 142.5 },
        { date: 'Sep 03', 'Market Index': 52.8, Portfolio: 140.9 },
        { date: 'Sep 04', 'Market Index': 54.4, Portfolio: 138.7 },
        { date: 'Sep 05', 'Market Index': 57.1, Portfolio: 135.2 },
        { date: 'Sep 06', 'Market Index': 67.9, Portfolio: 136.2 },
        { date: 'Sep 07', 'Market Index': 78.8, Portfolio: 136.2 },
        { date: 'Sep 08', 'Market Index': 89.2, Portfolio: 146.2 },
        { date: 'Sep 09', 'Market Index': 99.2, Portfolio: 145.2 },
        { date: 'Sep 10', 'Market Index': 101.2, Portfolio: 141.8 },
        { date: 'Sep 11', 'Market Index': 104.2, Portfolio: 132.2 },
        { date: 'Sep 12', 'Market Index': 109.8, Portfolio: 129.2 },
        { date: 'Sep 13', 'Market Index': 110.4, Portfolio: 120.3 },
        { date: 'Sep 14', 'Market Index': 111.3, Portfolio: 123.4 },
        { date: 'Sep 15', 'Market Index': 114.3, Portfolio: 137.4 },
        { date: 'Sep 16', 'Market Index': 105.1, Portfolio: 130.1 },
        { date: 'Sep 17', 'Market Index': 89.3, Portfolio: 131.8 },
        { date: 'Sep 18', 'Market Index': 102.1, Portfolio: 149.4 },
        { date: 'Sep 19', 'Market Index': 101.7, Portfolio: 149.3 },
        { date: 'Sep 20', 'Market Index': 121.3, Portfolio: 153.2 },
        { date: 'Sep 21', 'Market Index': 132.5, Portfolio: 157.2 },
        { date: 'Sep 22', 'Market Index': 121.4, Portfolio: 139.1 },
        { date: 'Sep 23', 'Market Index': 100.1, Portfolio: 120.2 },
        { date: 'Sep 24', 'Market Index': 89.1, Portfolio: 119.1 },
        { date: 'Sep 25', 'Market Index': 97.1, Portfolio: 112.2 },
        { date: 'Sep 26', 'Market Index': 109.4, Portfolio: 129.1 },
    ];

    const summary: ChartSummaryItem[] = [
        { name: 'Portfolio value', value: '$37,081.89', changeType: null },
        { name: 'Invested', value: '$19,698.65', changeType: null },
        { name: 'Cashflow', value: '$20,033.74', changeType: null },
        { name: 'Price gain', value: '+$15,012.39', changeType: 'positive' },
        { name: 'Realized', value: '+$177.4', changeType: 'positive' },
        { name: 'Dividends (gross)', value: '+$490.97', changeType: 'positive' },
    ];

    const tabs: TabDefinition[] = [
        { name: 'Last 7d', dataRange: data.slice(51, 57) },
        { name: 'Last 30d', dataRange: data.slice(28, 70) },
        { name: 'Max.', dataRange: data },
    ];

    return (
        <LineChart06
            data={data}
            headline="Portfolio performance"
            headlineValue="$37,081.89"
            change="+$430.90 (4.1%)"
            summary={summary}
            tabs={tabs}
        />
    );
};

// ─── LineChart07Example ─────────────────────────────────────────────────────────────

export const LineChart07Example = () => {
    const data = [
        { date: 'Aug 01', 'ETF Shares Vital': 2100.2, 'Vitainvest Core': 4434.1, 'iShares Tech Growth': 7943.2 },
        { date: 'Aug 02', 'ETF Shares Vital': 2943.0, 'Vitainvest Core': 4954.1, 'iShares Tech Growth': 8954.1 },
        { date: 'Aug 03', 'ETF Shares Vital': 4889.5, 'Vitainvest Core': 6100.2, 'iShares Tech Growth': 9123.7 },
        { date: 'Aug 04', 'ETF Shares Vital': 3909.8, 'Vitainvest Core': 4909.7, 'iShares Tech Growth': 7478.4 },
        { date: 'Aug 05', 'ETF Shares Vital': 5778.7, 'Vitainvest Core': 7103.1, 'iShares Tech Growth': 9504.3 },
        { date: 'Aug 06', 'ETF Shares Vital': 5900.9, 'Vitainvest Core': 7534.3, 'iShares Tech Growth': 9943.4 },
        { date: 'Aug 07', 'ETF Shares Vital': 4129.4, 'Vitainvest Core': 7412.1, 'iShares Tech Growth': 10112.2 },
        { date: 'Aug 08', 'ETF Shares Vital': 6021.2, 'Vitainvest Core': 7834.4, 'iShares Tech Growth': 10290.2 },
        { date: 'Aug 09', 'ETF Shares Vital': 6279.8, 'Vitainvest Core': 8159.1, 'iShares Tech Growth': 10349.6 },
        { date: 'Aug 10', 'ETF Shares Vital': 6224.5, 'Vitainvest Core': 8260.6, 'iShares Tech Growth': 10415.4 },
        { date: 'Aug 11', 'ETF Shares Vital': 6380.6, 'Vitainvest Core': 8965.3, 'iShares Tech Growth': 10636.3 },
        { date: 'Aug 12', 'ETF Shares Vital': 6414.4, 'Vitainvest Core': 7989.3, 'iShares Tech Growth': 10900.5 },
        { date: 'Aug 13', 'ETF Shares Vital': 6540.1, 'Vitainvest Core': 7839.6, 'iShares Tech Growth': 11040.4 },
        { date: 'Aug 14', 'ETF Shares Vital': 6634.4, 'Vitainvest Core': 7343.8, 'iShares Tech Growth': 11390.5 },
        { date: 'Aug 15', 'ETF Shares Vital': 7124.6, 'Vitainvest Core': 6903.7, 'iShares Tech Growth': 11423.1 },
        { date: 'Aug 16', 'ETF Shares Vital': 7934.5, 'Vitainvest Core': 6273.6, 'iShares Tech Growth': 12134.4 },
        { date: 'Aug 17', 'ETF Shares Vital': 10287.8, 'Vitainvest Core': 5900.3, 'iShares Tech Growth': 12034.4 },
        { date: 'Aug 18', 'ETF Shares Vital': 10323.2, 'Vitainvest Core': 5732.1, 'iShares Tech Growth': 11011.7 },
        { date: 'Aug 19', 'ETF Shares Vital': 10511.4, 'Vitainvest Core': 5523.1, 'iShares Tech Growth': 11834.8 },
        { date: 'Aug 20', 'ETF Shares Vital': 11043.9, 'Vitainvest Core': 5422.3, 'iShares Tech Growth': 12387.1 },
        { date: 'Aug 21', 'ETF Shares Vital': 6700.7, 'Vitainvest Core': 5334.2, 'iShares Tech Growth': 11032.2 },
        { date: 'Aug 22', 'ETF Shares Vital': 6900.8, 'Vitainvest Core': 4943.4, 'iShares Tech Growth': 10134.2 },
        { date: 'Aug 23', 'ETF Shares Vital': 7934.5, 'Vitainvest Core': 4812.1, 'iShares Tech Growth': 9921.2 },
        { date: 'Aug 24', 'ETF Shares Vital': 9021.0, 'Vitainvest Core': 2729.1, 'iShares Tech Growth': 10549.8 },
        { date: 'Aug 25', 'ETF Shares Vital': 9198.2, 'Vitainvest Core': 2178.0, 'iShares Tech Growth': 10968.4 },
        { date: 'Aug 26', 'ETF Shares Vital': 9557.1, 'Vitainvest Core': 2158.3, 'iShares Tech Growth': 11059.1 },
        { date: 'Aug 27', 'ETF Shares Vital': 9959.8, 'Vitainvest Core': 2100.8, 'iShares Tech Growth': 11903.6 },
        { date: 'Aug 28', 'ETF Shares Vital': 10034.6, 'Vitainvest Core': 2934.4, 'iShares Tech Growth': 12143.3 },
        { date: 'Aug 29', 'ETF Shares Vital': 10243.8, 'Vitainvest Core': 3223.4, 'iShares Tech Growth': 12930.1 },
        { date: 'Aug 30', 'ETF Shares Vital': 10078.5, 'Vitainvest Core': 3779.1, 'iShares Tech Growth': 13420.5 },
        { date: 'Aug 31', 'ETF Shares Vital': 11134.6, 'Vitainvest Core': 4190.3, 'iShares Tech Growth': 14443.2 },
        { date: 'Sep 01', 'ETF Shares Vital': 12347.2, 'Vitainvest Core': 4839.1, 'iShares Tech Growth': 14532.1 },
        { date: 'Sep 02', 'ETF Shares Vital': 12593.8, 'Vitainvest Core': 5153.3, 'iShares Tech Growth': 14283.5 },
        { date: 'Sep 03', 'ETF Shares Vital': 12043.4, 'Vitainvest Core': 5234.8, 'iShares Tech Growth': 14078.9 },
        { date: 'Sep 04', 'ETF Shares Vital': 12144.9, 'Vitainvest Core': 5478.4, 'iShares Tech Growth': 13859.7 },
        { date: 'Sep 05', 'ETF Shares Vital': 12489.5, 'Vitainvest Core': 5741.1, 'iShares Tech Growth': 13539.2 },
        { date: 'Sep 06', 'ETF Shares Vital': 12748.7, 'Vitainvest Core': 6743.9, 'iShares Tech Growth': 13643.2 },
        { date: 'Sep 07', 'ETF Shares Vital': 12933.2, 'Vitainvest Core': 7832.8, 'iShares Tech Growth': 14629.2 },
        { date: 'Sep 08', 'ETF Shares Vital': 13028.8, 'Vitainvest Core': 8943.2, 'iShares Tech Growth': 13611.2 },
        { date: 'Sep 09', 'ETF Shares Vital': 13412.4, 'Vitainvest Core': 9932.2, 'iShares Tech Growth': 12515.2 },
        { date: 'Sep 10', 'ETF Shares Vital': 13649.0, 'Vitainvest Core': 10139.2, 'iShares Tech Growth': 11143.8 },
        { date: 'Sep 11', 'ETF Shares Vital': 13748.5, 'Vitainvest Core': 10441.2, 'iShares Tech Growth': 8929.2 },
        { date: 'Sep 12', 'ETF Shares Vital': 13148.1, 'Vitainvest Core': 10933.8, 'iShares Tech Growth': 8943.2 },
        { date: 'Sep 13', 'ETF Shares Vital': 12839.6, 'Vitainvest Core': 11073.4, 'iShares Tech Growth': 7938.3 },
        { date: 'Sep 14', 'ETF Shares Vital': 12428.2, 'Vitainvest Core': 11128.3, 'iShares Tech Growth': 7533.4 },
        { date: 'Sep 15', 'ETF Shares Vital': 12012.8, 'Vitainvest Core': 11412.3, 'iShares Tech Growth': 7100.4 },
        { date: 'Sep 16', 'ETF Shares Vital': 11801.3, 'Vitainvest Core': 10501.1, 'iShares Tech Growth': 6532.1 },
        { date: 'Sep 17', 'ETF Shares Vital': 10102.9, 'Vitainvest Core': 8923.3, 'iShares Tech Growth': 4332.8 },
        { date: 'Sep 18', 'ETF Shares Vital': 12132.5, 'Vitainvest Core': 10212.1, 'iShares Tech Growth': 7847.4 },
        { date: 'Sep 19', 'ETF Shares Vital': 12901.1, 'Vitainvest Core': 10101.7, 'iShares Tech Growth': 7223.3 },
        { date: 'Sep 20', 'ETF Shares Vital': 13132.6, 'Vitainvest Core': 12132.3, 'iShares Tech Growth': 6900.2 },
        { date: 'Sep 21', 'ETF Shares Vital': 14132.2, 'Vitainvest Core': 13212.5, 'iShares Tech Growth': 5932.2 },
        { date: 'Sep 22', 'ETF Shares Vital': 14245.8, 'Vitainvest Core': 12163.4, 'iShares Tech Growth': 5577.1 },
        { date: 'Sep 23', 'ETF Shares Vital': 14328.3, 'Vitainvest Core': 10036.1, 'iShares Tech Growth': 5439.2 },
        { date: 'Sep 24', 'ETF Shares Vital': 14949.9, 'Vitainvest Core': 8985.1, 'iShares Tech Growth': 4463.1 },
        { date: 'Sep 25', 'ETF Shares Vital': 15967.5, 'Vitainvest Core': 9700.1, 'iShares Tech Growth': 4123.2 },
        { date: 'Sep 26', 'ETF Shares Vital': 17349.3, 'Vitainvest Core': 10943.4, 'iShares Tech Growth': 3935.1 },
    ];

    const summary: SeriesSummaryItem[] = [
        { name: 'ETF Shares Vital', value: '$17,349.30', bgColor: 'bg-blue-500 dark:bg-blue-500' },
        { name: 'Vitainvest Core', value: '$10,943.40', bgColor: 'bg-violet-500 dark:bg-violet-500' },
        { name: 'iShares Tech Growth', value: '$3,935.10', bgColor: 'bg-fuchsia-500 dark:bg-fuchsia-500' },
    ];

    const rangeTabs: RangeTab[] = [
        { name: '1W', dataRange: data.slice(-5) },
        { name: '1M', dataRange: data.slice(-22) },
        { name: '3M', dataRange: data },
        { name: '1Y', dataRange: data },
    ];

    return (
        <LineChart07
            data={data}
            title="ETF performance comparison"
            subtitle="Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt."
            summary={summary}
            rangeTabs={rangeTabs}
        />
    );
};

// ─── LineChart08Example ─────────────────────────────────────────────────────────────

export const LineChart08Example = () => {
    const data = [
        { date: 'Aug 01', 'ETF Shares Vital': 2100.2, 'Vitainvest Core': 4434.1, 'iShares Tech Growth': 7943.2 },
        { date: 'Aug 02', 'ETF Shares Vital': 2943.0, 'Vitainvest Core': 4954.1, 'iShares Tech Growth': 8954.1 },
        { date: 'Aug 03', 'ETF Shares Vital': 4889.5, 'Vitainvest Core': 6100.2, 'iShares Tech Growth': 9123.7 },
        { date: 'Aug 04', 'ETF Shares Vital': 3909.8, 'Vitainvest Core': 4909.7, 'iShares Tech Growth': 7478.4 },
        { date: 'Aug 05', 'ETF Shares Vital': 5778.7, 'Vitainvest Core': 7103.1, 'iShares Tech Growth': 9504.3 },
        { date: 'Aug 06', 'ETF Shares Vital': 5900.9, 'Vitainvest Core': 7534.3, 'iShares Tech Growth': 9943.4 },
        { date: 'Aug 07', 'ETF Shares Vital': 4129.4, 'Vitainvest Core': 7412.1, 'iShares Tech Growth': 10112.2 },
        { date: 'Aug 08', 'ETF Shares Vital': 6021.2, 'Vitainvest Core': 7834.4, 'iShares Tech Growth': 10290.2 },
        { date: 'Aug 09', 'ETF Shares Vital': 6279.8, 'Vitainvest Core': 8159.1, 'iShares Tech Growth': 10349.6 },
        { date: 'Aug 10', 'ETF Shares Vital': 6224.5, 'Vitainvest Core': 8260.6, 'iShares Tech Growth': 10415.4 },
        { date: 'Aug 11', 'ETF Shares Vital': 6380.6, 'Vitainvest Core': 8965.3, 'iShares Tech Growth': 10636.3 },
        { date: 'Aug 12', 'ETF Shares Vital': 6414.4, 'Vitainvest Core': 7989.3, 'iShares Tech Growth': 10900.5 },
        { date: 'Aug 13', 'ETF Shares Vital': 6540.1, 'Vitainvest Core': 7839.6, 'iShares Tech Growth': 11040.4 },
        { date: 'Aug 14', 'ETF Shares Vital': 6634.4, 'Vitainvest Core': 7343.8, 'iShares Tech Growth': 11390.5 },
        { date: 'Aug 15', 'ETF Shares Vital': 7124.6, 'Vitainvest Core': 6903.7, 'iShares Tech Growth': 11423.1 },
        { date: 'Aug 16', 'ETF Shares Vital': 7934.5, 'Vitainvest Core': 6273.6, 'iShares Tech Growth': 12134.4 },
        { date: 'Aug 17', 'ETF Shares Vital': 10287.8, 'Vitainvest Core': 5900.3, 'iShares Tech Growth': 12034.4 },
        { date: 'Aug 18', 'ETF Shares Vital': 10323.2, 'Vitainvest Core': 5732.1, 'iShares Tech Growth': 11011.7 },
        { date: 'Aug 19', 'ETF Shares Vital': 10511.4, 'Vitainvest Core': 5523.1, 'iShares Tech Growth': 11834.8 },
        { date: 'Aug 20', 'ETF Shares Vital': 11043.9, 'Vitainvest Core': 5422.3, 'iShares Tech Growth': 12387.1 },
        { date: 'Aug 21', 'ETF Shares Vital': 6700.7, 'Vitainvest Core': 5334.2, 'iShares Tech Growth': 11032.2 },
        { date: 'Aug 22', 'ETF Shares Vital': 6900.8, 'Vitainvest Core': 4943.4, 'iShares Tech Growth': 10134.2 },
        { date: 'Aug 23', 'ETF Shares Vital': 7934.5, 'Vitainvest Core': 4812.1, 'iShares Tech Growth': 9921.2 },
        { date: 'Aug 24', 'ETF Shares Vital': 9021.0, 'Vitainvest Core': 2729.1, 'iShares Tech Growth': 10549.8 },
        { date: 'Aug 25', 'ETF Shares Vital': 9198.2, 'Vitainvest Core': 2178.0, 'iShares Tech Growth': 10968.4 },
        { date: 'Aug 26', 'ETF Shares Vital': 9557.1, 'Vitainvest Core': 2158.3, 'iShares Tech Growth': 11059.1 },
        { date: 'Aug 27', 'ETF Shares Vital': 9959.8, 'Vitainvest Core': 2100.8, 'iShares Tech Growth': 11903.6 },
        { date: 'Aug 28', 'ETF Shares Vital': 10034.6, 'Vitainvest Core': 2934.4, 'iShares Tech Growth': 12143.3 },
        { date: 'Aug 29', 'ETF Shares Vital': 10243.8, 'Vitainvest Core': 3223.4, 'iShares Tech Growth': 12930.1 },
        { date: 'Aug 30', 'ETF Shares Vital': 10078.5, 'Vitainvest Core': 3779.1, 'iShares Tech Growth': 13420.5 },
        { date: 'Aug 31', 'ETF Shares Vital': 11134.6, 'Vitainvest Core': 4190.3, 'iShares Tech Growth': 14443.2 },
        { date: 'Sep 01', 'ETF Shares Vital': 12347.2, 'Vitainvest Core': 4839.1, 'iShares Tech Growth': 14532.1 },
        { date: 'Sep 02', 'ETF Shares Vital': 12593.8, 'Vitainvest Core': 5153.3, 'iShares Tech Growth': 14283.5 },
        { date: 'Sep 03', 'ETF Shares Vital': 12043.4, 'Vitainvest Core': 5234.8, 'iShares Tech Growth': 14078.9 },
        { date: 'Sep 04', 'ETF Shares Vital': 12144.9, 'Vitainvest Core': 5478.4, 'iShares Tech Growth': 13859.7 },
        { date: 'Sep 05', 'ETF Shares Vital': 12489.5, 'Vitainvest Core': 5741.1, 'iShares Tech Growth': 13539.2 },
        { date: 'Sep 06', 'ETF Shares Vital': 12748.7, 'Vitainvest Core': 6743.9, 'iShares Tech Growth': 13643.2 },
        { date: 'Sep 07', 'ETF Shares Vital': 12933.2, 'Vitainvest Core': 7832.8, 'iShares Tech Growth': 14629.2 },
        { date: 'Sep 08', 'ETF Shares Vital': 13028.8, 'Vitainvest Core': 8943.2, 'iShares Tech Growth': 13611.2 },
        { date: 'Sep 09', 'ETF Shares Vital': 13412.4, 'Vitainvest Core': 9932.2, 'iShares Tech Growth': 12515.2 },
        { date: 'Sep 10', 'ETF Shares Vital': 13649.0, 'Vitainvest Core': 10139.2, 'iShares Tech Growth': 11143.8 },
        { date: 'Sep 11', 'ETF Shares Vital': 13748.5, 'Vitainvest Core': 10441.2, 'iShares Tech Growth': 8929.2 },
        { date: 'Sep 12', 'ETF Shares Vital': 13148.1, 'Vitainvest Core': 10933.8, 'iShares Tech Growth': 8943.2 },
        { date: 'Sep 13', 'ETF Shares Vital': 12839.6, 'Vitainvest Core': 11073.4, 'iShares Tech Growth': 7938.3 },
        { date: 'Sep 14', 'ETF Shares Vital': 12428.2, 'Vitainvest Core': 11128.3, 'iShares Tech Growth': 7533.4 },
        { date: 'Sep 15', 'ETF Shares Vital': 12012.8, 'Vitainvest Core': 11412.3, 'iShares Tech Growth': 7100.4 },
        { date: 'Sep 16', 'ETF Shares Vital': 11801.3, 'Vitainvest Core': 10501.1, 'iShares Tech Growth': 6532.1 },
        { date: 'Sep 17', 'ETF Shares Vital': 10102.9, 'Vitainvest Core': 8923.3, 'iShares Tech Growth': 4332.8 },
        { date: 'Sep 18', 'ETF Shares Vital': 12132.5, 'Vitainvest Core': 10212.1, 'iShares Tech Growth': 7847.4 },
        { date: 'Sep 19', 'ETF Shares Vital': 12901.1, 'Vitainvest Core': 10101.7, 'iShares Tech Growth': 7223.3 },
        { date: 'Sep 20', 'ETF Shares Vital': 13132.6, 'Vitainvest Core': 12132.3, 'iShares Tech Growth': 6900.2 },
        { date: 'Sep 21', 'ETF Shares Vital': 14132.2, 'Vitainvest Core': 13212.5, 'iShares Tech Growth': 5932.2 },
        { date: 'Sep 22', 'ETF Shares Vital': 14245.8, 'Vitainvest Core': 12163.4, 'iShares Tech Growth': 5577.1 },
        { date: 'Sep 23', 'ETF Shares Vital': 14328.3, 'Vitainvest Core': 10036.1, 'iShares Tech Growth': 5439.2 },
        { date: 'Sep 24', 'ETF Shares Vital': 14949.9, 'Vitainvest Core': 8985.1, 'iShares Tech Growth': 4463.1 },
        { date: 'Sep 25', 'ETF Shares Vital': 15967.5, 'Vitainvest Core': 9700.1, 'iShares Tech Growth': 4123.2 },
        { date: 'Sep 26', 'ETF Shares Vital': 17349.3, 'Vitainvest Core': 10943.4, 'iShares Tech Growth': 3935.1 },
    ];

    const summary: LineChart08SeriesSummaryItem[] = [
        { name: 'ETF Shares Vital', value: '$17,349.30', bgColor: 'bg-blue-500 dark:bg-blue-500' },
        { name: 'Vitainvest Core', value: '$10,943.40', bgColor: 'bg-violet-500 dark:bg-violet-500' },
        { name: 'iShares Tech Growth', value: '$3,935.10', bgColor: 'bg-fuchsia-500 dark:bg-fuchsia-500' },
    ];

    const rangeTabs: RangeTab[] = [
        { name: '1W', dataRange: data.slice(-5) },
        { name: '1M', dataRange: data.slice(-22) },
        { name: '3M', dataRange: data },
        { name: '1Y', dataRange: data },
    ];

    return (
        <LineChart08
            data={data}
            title="ETF performance comparison"
            subtitle="Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt."
            summary={summary}
            rangeTabs={rangeTabs}
        />
    );
};

// ─── LineChart09Example ─────────────────────────────────────────────────────────────

export const LineChart09Example = () => {
    const data = [
        { date: '2023-08-01', 'ETF Shares Vital': 2100.2, 'Vitainvest Core': 4434.1, 'iShares Tech Growth': 7943.2 },
        { date: '2023-08-02', 'ETF Shares Vital': 2943.0, 'Vitainvest Core': 4954.1, 'iShares Tech Growth': 8954.1 },
        { date: '2023-08-03', 'ETF Shares Vital': 4889.5, 'Vitainvest Core': 6100.2, 'iShares Tech Growth': 9123.7 },
        { date: '2023-08-04', 'ETF Shares Vital': 3909.8, 'Vitainvest Core': 4909.7, 'iShares Tech Growth': 7478.4 },
        { date: '2023-08-05', 'ETF Shares Vital': 5778.7, 'Vitainvest Core': 7103.1, 'iShares Tech Growth': 9504.3 },
        { date: '2023-08-06', 'ETF Shares Vital': 5900.9, 'Vitainvest Core': 7534.3, 'iShares Tech Growth': 9943.4 },
        { date: '2023-08-07', 'ETF Shares Vital': 4129.4, 'Vitainvest Core': 7412.1, 'iShares Tech Growth': 10112.2 },
        { date: '2023-08-08', 'ETF Shares Vital': 6021.2, 'Vitainvest Core': 7834.4, 'iShares Tech Growth': 10290.2 },
        { date: '2023-08-09', 'ETF Shares Vital': 6279.8, 'Vitainvest Core': 8159.1, 'iShares Tech Growth': 10349.6 },
        { date: '2023-08-10', 'ETF Shares Vital': 6224.5, 'Vitainvest Core': 8260.6, 'iShares Tech Growth': 10415.4 },
        { date: '2023-08-11', 'ETF Shares Vital': 6380.6, 'Vitainvest Core': 8965.3, 'iShares Tech Growth': 10636.3 },
        { date: '2023-08-12', 'ETF Shares Vital': 6414.4, 'Vitainvest Core': 7989.3, 'iShares Tech Growth': 10900.5 },
        { date: '2023-08-13', 'ETF Shares Vital': 6540.1, 'Vitainvest Core': 7839.6, 'iShares Tech Growth': 11040.4 },
        { date: '2023-08-14', 'ETF Shares Vital': 6634.4, 'Vitainvest Core': 7343.8, 'iShares Tech Growth': 11390.5 },
        { date: '2023-08-15', 'ETF Shares Vital': 7124.6, 'Vitainvest Core': 6903.7, 'iShares Tech Growth': 11423.1 },
        { date: '2023-08-16', 'ETF Shares Vital': 6934.2, 'Vitainvest Core': 6343.9, 'iShares Tech Growth': 11524.7 },
        { date: '2023-08-17', 'ETF Shares Vital': 7189.5, 'Vitainvest Core': 7012.4, 'iShares Tech Growth': 11678.2 },
        { date: '2023-08-18', 'ETF Shares Vital': 6845.3, 'Vitainvest Core': 7234.1, 'iShares Tech Growth': 11834.5 },
        { date: '2023-08-19', 'ETF Shares Vital': 7234.8, 'Vitainvest Core': 7456.3, 'iShares Tech Growth': 11945.1 },
        { date: '2023-08-20', 'ETF Shares Vital': 7456.1, 'Vitainvest Core': 7678.9, 'iShares Tech Growth': 12034.2 },
        { date: '2023-08-21', 'ETF Shares Vital': 7634.5, 'Vitainvest Core': 7834.2, 'iShares Tech Growth': 12123.5 },
        { date: '2023-08-22', 'ETF Shares Vital': 7845.2, 'Vitainvest Core': 8012.3, 'iShares Tech Growth': 12234.1 },
        { date: '2023-08-23', 'ETF Shares Vital': 8012.4, 'Vitainvest Core': 8234.5, 'iShares Tech Growth': 12345.6 },
        { date: '2023-08-24', 'ETF Shares Vital': 8234.7, 'Vitainvest Core': 8456.2, 'iShares Tech Growth': 12456.3 },
        { date: '2023-08-25', 'ETF Shares Vital': 8456.1, 'Vitainvest Core': 8634.3, 'iShares Tech Growth': 12567.4 },
        { date: '2023-08-26', 'ETF Shares Vital': 8634.5, 'Vitainvest Core': 8834.1, 'iShares Tech Growth': 12678.2 },
        { date: '2023-08-27', 'ETF Shares Vital': 8834.2, 'Vitainvest Core': 9012.3, 'iShares Tech Growth': 12734.1 },
        { date: '2023-08-28', 'ETF Shares Vital': 9012.5, 'Vitainvest Core': 9234.5, 'iShares Tech Growth': 12834.5 },
        { date: '2023-08-29', 'ETF Shares Vital': 9234.8, 'Vitainvest Core': 9456.2, 'iShares Tech Growth': 12945.3 },
        { date: '2023-08-30', 'ETF Shares Vital': 9456.1, 'Vitainvest Core': 9634.1, 'iShares Tech Growth': 13045.2 },
        { date: '2023-09-01', 'ETF Shares Vital': 9634.2, 'Vitainvest Core': 9834.3, 'iShares Tech Growth': 13156.4 },
        { date: '2023-09-02', 'ETF Shares Vital': 10012.5, 'Vitainvest Core': 10012.5, 'iShares Tech Growth': 13267.1 },
        { date: '2023-09-03', 'ETF Shares Vital': 10234.3, 'Vitainvest Core': 10234.2, 'iShares Tech Growth': 13378.5 },
        { date: '2023-09-04', 'ETF Shares Vital': 10456.1, 'Vitainvest Core': 10456.3, 'iShares Tech Growth': 13489.2 },
        { date: '2023-09-05', 'ETF Shares Vital': 10634.5, 'Vitainvest Core': 10634.1, 'iShares Tech Growth': 13567.3 },
        { date: '2023-09-06', 'ETF Shares Vital': 10834.2, 'Vitainvest Core': 10834.5, 'iShares Tech Growth': 13678.4 },
        { date: '2023-09-07', 'ETF Shares Vital': 11012.8, 'Vitainvest Core': 11012.2, 'iShares Tech Growth': 13789.1 },
        { date: '2023-09-08', 'ETF Shares Vital': 11234.5, 'Vitainvest Core': 11234.3, 'iShares Tech Growth': 13867.5 },
        { date: '2023-09-09', 'ETF Shares Vital': 11456.1, 'Vitainvest Core': 11456.2, 'iShares Tech Growth': 13978.2 },
        { date: '2023-09-10', 'ETF Shares Vital': 11634.4, 'Vitainvest Core': 11634.1, 'iShares Tech Growth': 14089.3 },
        { date: '2023-09-11', 'ETF Shares Vital': 11834.2, 'Vitainvest Core': 11834.5, 'iShares Tech Growth': 14134.2 },
        { date: '2023-09-12', 'ETF Shares Vital': 12012.5, 'Vitainvest Core': 12012.3, 'iShares Tech Growth': 14245.1 },
        { date: '2023-09-13', 'ETF Shares Vital': 12234.3, 'Vitainvest Core': 12234.2, 'iShares Tech Growth': 14356.5 },
        { date: '2023-09-14', 'ETF Shares Vital': 12456.1, 'Vitainvest Core': 12456.3, 'iShares Tech Growth': 14467.2 },
        { date: '2023-09-15', 'ETF Shares Vital': 12634.5, 'Vitainvest Core': 12634.1, 'iShares Tech Growth': 14512.3 },
        { date: '2023-09-16', 'ETF Shares Vital': 12834.2, 'Vitainvest Core': 12834.5, 'iShares Tech Growth': 14623.4 },
        { date: '2023-09-17', 'ETF Shares Vital': 13012.8, 'Vitainvest Core': 13012.2, 'iShares Tech Growth': 14734.1 },
        { date: '2023-09-18', 'ETF Shares Vital': 13234.5, 'Vitainvest Core': 13234.3, 'iShares Tech Growth': 14812.5 },
        { date: '2023-09-19', 'ETF Shares Vital': 13456.1, 'Vitainvest Core': 13456.2, 'iShares Tech Growth': 14923.2 },
        { date: '2023-09-20', 'ETF Shares Vital': 13634.4, 'Vitainvest Core': 13634.1, 'iShares Tech Growth': 15034.3 },
        { date: '2023-09-21', 'ETF Shares Vital': 13834.2, 'Vitainvest Core': 13834.5, 'iShares Tech Growth': 15100.5 },
        { date: '2023-09-22', 'ETF Shares Vital': 14012.5, 'Vitainvest Core': 14012.3, 'iShares Tech Growth': 15211.1 },
        { date: '2023-09-23', 'ETF Shares Vital': 14234.3, 'Vitainvest Core': 14234.2, 'iShares Tech Growth': 15322.5 },
        { date: '2023-09-24', 'ETF Shares Vital': 14456.1, 'Vitainvest Core': 14456.3, 'iShares Tech Growth': 15433.2 },
        { date: '2023-09-25', 'ETF Shares Vital': 14634.5, 'Vitainvest Core': 14634.1, 'iShares Tech Growth': 15544.3 },
        { date: '2023-09-26', 'ETF Shares Vital': 14834.2, 'Vitainvest Core': 14834.5, 'iShares Tech Growth': 15655.4 },
    ];

    const rangeTabs: RangeTab[] = [
        { name: '1W', dataRange: data.slice(-5) },
        { name: '1M', dataRange: data.slice(-22) },
        { name: '3M', dataRange: data },
        { name: '1Y', dataRange: data },
    ];

    return (
        <LineChart09
            data={data}
            title="ETF performance comparison"
            subtitle="Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt."
            rangeTabs={rangeTabs}
        />
    );
};

// ─── Fintech Examples ─────────────────────────────────────────────────────────
export * from './fintech/asset-class-ytd-returns';
export * from './fintech/spy-ytd-return';
