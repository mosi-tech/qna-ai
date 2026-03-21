import React from 'react';

import { SparkChart01 } from '../spark-chart-01';
import { SparkChart02, SparkChart02WatchlistItem, SparkChart02HeaderItem } from '../spark-chart-02';
import { SparkChart03, SparkChart03Tab } from '../spark-chart-03';
import { SparkChart04, SparkChart04MetricItem } from '../spark-chart-04';
import { SparkChart05, SparkChart05HoldingItem } from '../spark-chart-05';
import { SparkChart06, SparkChart06Item } from '../spark-chart-06';

export const SparkChart01Example = () => {
    const data = [
        { date: 'Nov 24, 2023', GOOG: 156.2, AMZN: 68.5, SPOT: 71.8, MSFT: 205.3, TSLA: 1050.6 },
        { date: 'Nov 25, 2023', GOOG: 152.5, AMZN: 69.3, SPOT: 67.2, MSFT: 223.1, TSLA: 945.8 },
        { date: 'Nov 26, 2023', GOOG: 148.7, AMZN: 69.8, SPOT: 61.5, MSFT: 240.9, TSLA: 839.4 },
        { date: 'Nov 27, 2023', GOOG: 155.3, AMZN: 73.5, SPOT: 57.9, MSFT: 254.7, TSLA: 830.2 },
        { date: 'Nov 28, 2023', GOOG: 160.1, AMZN: 75.2, SPOT: 59.6, MSFT: 308.5, TSLA: 845.7 },
        { date: 'Nov 29, 2023', GOOG: 175.6, AMZN: 89.2, SPOT: 57.3, MSFT: 341.4, TSLA: 950.2 },
        { date: 'Nov 30, 2023', GOOG: 180.2, AMZN: 92.7, SPOT: 59.8, MSFT: 378.1, TSLA: 995.9 },
        { date: 'Dec 01, 2023', GOOG: 185.5, AMZN: 95.3, SPOT: 62.4, MSFT: 320.3, TSLA: 1060.4 },
        { date: 'Dec 02, 2023', GOOG: 182.3, AMZN: 93.8, SPOT: 60.7, MSFT: 356.5, TSLA: 965.8 },
        { date: 'Dec 03, 2023', GOOG: 180.7, AMZN: 91.6, SPOT: 58.9, MSFT: 340.7, TSLA: 970.3 },
        { date: 'Dec 04, 2023', GOOG: 178.5, AMZN: 89.7, SPOT: 56.2, MSFT: 365.9, TSLA: 975.9 },
        { date: 'Dec 05, 2023', GOOG: 176.2, AMZN: 87.5, SPOT: 54.8, MSFT: 375.1, TSLA: 964.6 },
        { date: 'Dec 06, 2023', GOOG: 174.8, AMZN: 85.3, SPOT: 53.4, MSFT: 340.3, TSLA: 960.4 },
        { date: 'Dec 07, 2023', GOOG: 178.0, AMZN: 88.2, SPOT: 55.2, MSFT: 335.5, TSLA: 955.3 },
        { date: 'Dec 08, 2023', GOOG: 180.6, AMZN: 90.5, SPOT: 56.8, MSFT: 310.7, TSLA: 950.3 },
        { date: 'Dec 09, 2023', GOOG: 182.4, AMZN: 92.8, SPOT: 58.4, MSFT: 300.9, TSLA: 845.4 },
        { date: 'Dec 10, 2023', GOOG: 179.7, AMZN: 90.2, SPOT: 57.0, MSFT: 290.1, TSLA: 1011.6 },
        { date: 'Dec 11, 2023', GOOG: 154.2, AMZN: 88.7, SPOT: 55.6, MSFT: 291.3, TSLA: 1017.9 },
        { date: 'Dec 12, 2023', GOOG: 151.9, AMZN: 86.5, SPOT: 53.9, MSFT: 293.5, TSLA: 940.3 },
        { date: 'Dec 13, 2023', GOOG: 149.3, AMZN: 83.7, SPOT: 52.1, MSFT: 301.7, TSLA: 900.8 },
        { date: 'Dec 14, 2023', GOOG: 148.8, AMZN: 81.4, SPOT: 50.5, MSFT: 321.9, TSLA: 780.4 },
        { date: 'Dec 15, 2023', GOOG: 145.5, AMZN: 79.8, SPOT: 48.9, MSFT: 328.1, TSLA: 765.1 },
        { date: 'Dec 16, 2023', GOOG: 140.2, AMZN: 84.5, SPOT: 50.2, MSFT: 331.3, TSLA: 745.9 },
        { date: 'Dec 17, 2023', GOOG: 143.8, AMZN: 82.1, SPOT: 49.6, MSFT: 373.5, TSLA: 741.8 },
        { date: 'Dec 18, 2023', GOOG: 157.5, AMZN: 86.9, SPOT: 51.3, MSFT: 381.7, TSLA: 739.8 },
    ];

    const items = [
        { id: 'AMZN', name: 'AMZN', description: 'Amazon', value: '$86.9', change: '+0.92%', changeType: 'positive' as const },
        { id: 'TSLA', name: 'TSLA', description: 'Tesla, Inc.', value: '$739.8', change: '-2.12%', changeType: 'negative' as const },
        { id: 'GOOG', name: 'GOOG', description: 'Alphabet, Inc', value: '$157.5', change: '+0.38%', changeType: 'positive' as const },
        { id: 'SPOT', name: 'SPOT', description: 'Spotify', value: '$51.3', change: '−0.25%', changeType: 'negative' as const },
        { id: 'MSFT', name: 'MSFT', description: 'Microsoft', value: '$381.7', change: '+2.45%', changeType: 'positive' as const },
    ];

    return (
        <SparkChart01
            data={data}
            items={items}
            title="Portfolio Holdings"
            description="Tech stock prices over 2-week period"
        />
    );
};

export const SparkChart02Example = () => {
    const data = [
        { date: 'Nov 24, 2023', GOOG: 156.2, AMZN: 68.5, SPOT: 71.8, AAPL: 149.1 },
        { date: 'Nov 25, 2023', GOOG: 152.5, AMZN: 69.3, SPOT: 67.2, AAPL: 145.1 },
        { date: 'Nov 26, 2023', GOOG: 148.7, AMZN: 69.8, SPOT: 61.5, AAPL: 146.1 },
        { date: 'Nov 27, 2023', GOOG: 155.3, AMZN: 73.5, SPOT: 57.9, AAPL: 147.1 },
        { date: 'Nov 28, 2023', GOOG: 160.1, AMZN: 75.2, SPOT: 59.6, AAPL: 148.1 },
        { date: 'Nov 29, 2023', GOOG: 175.6, AMZN: 89.2, SPOT: 57.3, AAPL: 149.2 },
        { date: 'Nov 30, 2023', GOOG: 180.2, AMZN: 92.7, SPOT: 59.8, AAPL: 149.1 },
        { date: 'Dec 01, 2023', GOOG: 185.5, AMZN: 95.3, SPOT: 62.4, AAPL: 142.4 },
        { date: 'Dec 02, 2023', GOOG: 182.3, AMZN: 93.8, SPOT: 60.7, AAPL: 143.6 },
        { date: 'Dec 03, 2023', GOOG: 180.7, AMZN: 91.6, SPOT: 58.9, AAPL: 144.3 },
        { date: 'Dec 04, 2023', GOOG: 178.5, AMZN: 89.7, SPOT: 56.2, AAPL: 152.4 },
        { date: 'Dec 05, 2023', GOOG: 176.2, AMZN: 87.5, SPOT: 54.8, AAPL: 156.1 },
        { date: 'Dec 06, 2023', GOOG: 174.8, AMZN: 85.3, SPOT: 53.4, AAPL: 158.6 },
        { date: 'Dec 07, 2023', GOOG: 178.0, AMZN: 88.2, SPOT: 55.2, AAPL: 159.3 },
        { date: 'Dec 08, 2023', GOOG: 180.6, AMZN: 90.5, SPOT: 56.8, AAPL: 164.6 },
        { date: 'Dec 09, 2023', GOOG: 182.4, AMZN: 92.8, SPOT: 58.4, AAPL: 166.6 },
        { date: 'Dec 10, 2023', GOOG: 179.7, AMZN: 90.2, SPOT: 57.0, AAPL: 169.2 },
        { date: 'Dec 11, 2023', GOOG: 154.2, AMZN: 88.7, SPOT: 55.6, AAPL: 169.6 },
        { date: 'Dec 12, 2023', GOOG: 151.9, AMZN: 86.5, SPOT: 53.9, AAPL: 169.1 },
        { date: 'Dec 13, 2023', GOOG: 149.3, AMZN: 83.7, SPOT: 52.1, AAPL: 169.1 },
        { date: 'Dec 14, 2023', GOOG: 148.8, AMZN: 81.4, SPOT: 50.5, AAPL: 171.6 },
        { date: 'Dec 15, 2023', GOOG: 145.5, AMZN: 79.8, SPOT: 48.9, AAPL: 171.1 },
        { date: 'Dec 16, 2023', GOOG: 140.2, AMZN: 84.5, SPOT: 50.2, AAPL: 173.6 },
    ];

    const items: SparkChart02WatchlistItem[] = [
        { ticker: 'AMZN', description: 'Amazon', value: '$84.5', change: '+0.92%', changeType: 'positive' },
        { ticker: 'GOOG', description: 'Alphabet, Inc', value: '$140.2', change: '-0.38%', changeType: 'negative' },
        { ticker: 'AAPL', description: 'Apple', value: '$173.6', change: '+1.67%', changeType: 'positive' },
        { ticker: 'SPOT', description: 'Spotify', value: '$50.2', change: '-0.25%', changeType: 'negative' },
    ];

    const headerItem: SparkChart02HeaderItem = {
        totalValue: '$44,567.10',
        dailyChange: '+$451.30 (1.2%)',
        dailyChangeType: 'positive',
    };

    return (
        <SparkChart02
            data={data}
            headerItem={headerItem}
            items={items}
        />
    );
};

export const SparkChart03Example = () => {
    const data = [
        { date: 'Nov 24, 2023', GOOG: 156.2, AMZN: 68.5, SPOT: 71.8, AAPL: 149.1, MSFT: 205.3, TSLA: 1050.6 },
        { date: 'Nov 25, 2023', GOOG: 152.5, AMZN: 69.3, SPOT: 67.2, AAPL: 155.1, MSFT: 223.1, TSLA: 945.8 },
        { date: 'Nov 26, 2023', GOOG: 148.7, AMZN: 69.8, SPOT: 61.5, AAPL: 160.1, MSFT: 240.9, TSLA: 839.4 },
        { date: 'Nov 27, 2023', GOOG: 155.3, AMZN: 73.5, SPOT: 57.9, AAPL: 165.1, MSFT: 254.7, TSLA: 830.2 },
        { date: 'Nov 28, 2023', GOOG: 160.1, AMZN: 75.2, SPOT: 59.6, AAPL: 148.1, MSFT: 308.5, TSLA: 845.7 },
        { date: 'Nov 29, 2023', GOOG: 175.6, AMZN: 89.2, SPOT: 57.3, AAPL: 149.2, MSFT: 341.4, TSLA: 950.2 },
        { date: 'Nov 30, 2023', GOOG: 180.2, AMZN: 92.7, SPOT: 59.8, AAPL: 139.1, MSFT: 378.1, TSLA: 995.9 },
        { date: 'Dec 01, 2023', GOOG: 185.5, AMZN: 95.3, SPOT: 62.4, AAPL: 122.4, MSFT: 320.3, TSLA: 1060.4 },
        { date: 'Dec 02, 2023', GOOG: 182.3, AMZN: 93.8, SPOT: 60.7, AAPL: 143.6, MSFT: 356.5, TSLA: 965.8 },
        { date: 'Dec 03, 2023', GOOG: 180.7, AMZN: 91.6, SPOT: 58.9, AAPL: 144.3, MSFT: 340.7, TSLA: 970.3 },
        { date: 'Dec 04, 2023', GOOG: 178.5, AMZN: 89.7, SPOT: 56.2, AAPL: 152.4, MSFT: 367.1, TSLA: 932.5 },
        { date: 'Dec 05, 2023', GOOG: 176.2, AMZN: 87.5, SPOT: 54.8, AAPL: 156.1, MSFT: 389.6, TSLA: 898.2 },
        { date: 'Dec 06, 2023', GOOG: 174.8, AMZN: 85.3, SPOT: 53.4, AAPL: 158.6, MSFT: 375.3, TSLA: 879.4 },
        { date: 'Dec 07, 2023', GOOG: 178.0, AMZN: 88.2, SPOT: 55.2, AAPL: 159.3, MSFT: 401.2, TSLA: 915.7 },
        { date: 'Dec 08, 2023', GOOG: 180.6, AMZN: 90.5, SPOT: 56.8, AAPL: 164.6, MSFT: 423.4, TSLA: 968.3 },
        { date: 'Dec 09, 2023', GOOG: 182.4, AMZN: 92.8, SPOT: 58.4, AAPL: 166.6, MSFT: 441.5, TSLA: 1012.6 },
        { date: 'Dec 10, 2023', GOOG: 179.7, AMZN: 90.2, SPOT: 57.0, AAPL: 169.2, MSFT: 418.7, TSLA: 978.1 },
        { date: 'Dec 11, 2023', GOOG: 154.2, AMZN: 88.7, SPOT: 55.6, AAPL: 169.6, MSFT: 395.2, TSLA: 892.4 },
        { date: 'Dec 12, 2023', GOOG: 151.9, AMZN: 86.5, SPOT: 53.9, AAPL: 169.1, MSFT: 372.8, TSLA: 845.6 },
        { date: 'Dec 13, 2023', GOOG: 149.3, AMZN: 83.7, SPOT: 52.1, AAPL: 169.1, MSFT: 351.4, TSLA: 812.3 },
        { date: 'Dec 14, 2023', GOOG: 148.8, AMZN: 81.4, SPOT: 50.5, AAPL: 171.6, MSFT: 338.9, TSLA: 778.5 },
        { date: 'Dec 15, 2023', GOOG: 145.5, AMZN: 79.8, SPOT: 48.9, AAPL: 178.1, MSFT: 328.1, TSLA: 765.1 },
        { date: 'Dec 16, 2023', GOOG: 140.2, AMZN: 84.5, SPOT: 50.2, AAPL: 192.6, MSFT: 331.3, TSLA: 745.9 },
        { date: 'Dec 17, 2023', GOOG: 143.8, AMZN: 82.1, SPOT: 49.6, AAPL: 201.2, MSFT: 373.5, TSLA: 741.8 },
        { date: 'Dec 18, 2023', GOOG: 148.5, AMZN: 86.9, SPOT: 51.3, AAPL: 209.8, MSFT: 381.7, TSLA: 739.8 },
    ];

    const tabs: SparkChart03Tab[] = [
        {
            name: 'Trending',
            items: [
                { ticker: 'AMZN', description: 'Amazon', value: '$86.9', change: '+0.92%', changeType: 'positive' },
                { ticker: 'GOOG', description: 'Alphabet, Inc', value: '$148.5', change: '-0.38%', changeType: 'negative' },
                { ticker: 'AAPL', description: 'Apple', value: '$209.8', change: '+1.67%', changeType: 'positive' },
            ],
        },
        {
            name: 'Watchlist',
            items: [
                { ticker: 'SPOT', description: 'Spotify', value: '$51.3', change: '-0.25%', changeType: 'negative' },
                { ticker: 'MSFT', description: 'Microsoft', value: '$381.7', change: '+2.45%', changeType: 'positive' },
                { ticker: 'TSLA', description: 'Tesla, Inc.', value: '$739.8', change: '-2.12%', changeType: 'negative' },
            ],
        },
    ];

    return (
        <SparkChart03
            data={data}
            tabs={tabs}
            headerItem={{
                totalValue: '$44,567.10',
                dailyChange: '+$451.30 (1.2%)',
                dailyChangeType: 'positive',
            }}
        />
    );
};

export const SparkChart04Example = () => {
    const data = [
        { date: 'Jan 23', 'Monthly active users': 673, 'Monthly sessions': 1024, 'Monthly user growth': 4.5 },
        { date: 'Feb 23', 'Monthly active users': 573, 'Monthly sessions': 1224, 'Monthly user growth': 6.5 },
        { date: 'Mar 23', 'Monthly active users': 503, 'Monthly sessions': 1200, 'Monthly user growth': 6.9 },
        { date: 'Apr 23', 'Monthly active users': 523, 'Monthly sessions': 1005, 'Monthly user growth': 4.2 },
        { date: 'May 23', 'Monthly active users': 599, 'Monthly sessions': 1201, 'Monthly user growth': 3.9 },
        { date: 'Jun 23', 'Monthly active users': 481, 'Monthly sessions': 1001, 'Monthly user growth': 3.7 },
        { date: 'Jul 23', 'Monthly active users': 499, 'Monthly sessions': 1129, 'Monthly user growth': 4.7 },
        { date: 'Aug 23', 'Monthly active users': 571, 'Monthly sessions': 1220, 'Monthly user growth': 4.5 },
        { date: 'Sep 23', 'Monthly active users': 579, 'Monthly sessions': 1420, 'Monthly user growth': 4.3 },
        { date: 'Oct 23', 'Monthly active users': 471, 'Monthly sessions': 1230, 'Monthly user growth': 4.0 },
        { date: 'Nov 23', 'Monthly active users': 461, 'Monthly sessions': 1430, 'Monthly user growth': 4.1 },
        { date: 'Dec 23', 'Monthly active users': 341, 'Monthly sessions': 1530, 'Monthly user growth': 4.9 },
    ];

    const items: SparkChart04MetricItem[] = [
        { name: 'Monthly active users', stat: '341', color: 'blue' },
        { name: 'Monthly sessions', stat: '1,530', color: 'emerald' },
        { name: 'Monthly user growth', stat: '4.9%', color: 'indigo' },
    ];

    return <SparkChart04 data={data} items={items} />;
};

export const SparkChart05Example = () => {
    const data = [
        { date: 'Nov 24, 2023', 'Doorbell, Inc.': 150.2, 'Off Running AG': 70.5, 'Solid Bit Holding': 71.8 },
        { date: 'Nov 25, 2023', 'Doorbell, Inc.': 152.5, 'Off Running AG': 72.3, 'Solid Bit Holding': 67.2 },
        { date: 'Nov 26, 2023', 'Doorbell, Inc.': 148.7, 'Off Running AG': 69.8, 'Solid Bit Holding': 61.5 },
        { date: 'Nov 27, 2023', 'Doorbell, Inc.': 155.3, 'Off Running AG': 73.5, 'Solid Bit Holding': 57.9 },
        { date: 'Nov 28, 2023', 'Doorbell, Inc.': 160.1, 'Off Running AG': 75.2, 'Solid Bit Holding': 59.6 },
        { date: 'Nov 29, 2023', 'Doorbell, Inc.': 175.6, 'Off Running AG': 89.2, 'Solid Bit Holding': 57.3 },
        { date: 'Nov 30, 2023', 'Doorbell, Inc.': 180.2, 'Off Running AG': 92.7, 'Solid Bit Holding': 59.8 },
        { date: 'Dec 01, 2023', 'Doorbell, Inc.': 185.5, 'Off Running AG': 95.3, 'Solid Bit Holding': 62.4 },
        { date: 'Dec 02, 2023', 'Doorbell, Inc.': 182.3, 'Off Running AG': 93.8, 'Solid Bit Holding': 60.7 },
        { date: 'Dec 03, 2023', 'Doorbell, Inc.': 180.7, 'Off Running AG': 91.6, 'Solid Bit Holding': 58.9 },
        { date: 'Dec 04, 2023', 'Doorbell, Inc.': 178.5, 'Off Running AG': 89.7, 'Solid Bit Holding': 56.2 },
        { date: 'Dec 05, 2023', 'Doorbell, Inc.': 176.2, 'Off Running AG': 87.5, 'Solid Bit Holding': 54.8 },
        { date: 'Dec 06, 2023', 'Doorbell, Inc.': 174.8, 'Off Running AG': 85.3, 'Solid Bit Holding': 53.4 },
        { date: 'Dec 07, 2023', 'Doorbell, Inc.': 178.0, 'Off Running AG': 88.2, 'Solid Bit Holding': 55.2 },
        { date: 'Dec 08, 2023', 'Doorbell, Inc.': 180.6, 'Off Running AG': 90.5, 'Solid Bit Holding': 56.8 },
        { date: 'Dec 09, 2023', 'Doorbell, Inc.': 182.4, 'Off Running AG': 92.8, 'Solid Bit Holding': 58.4 },
        { date: 'Dec 10, 2023', 'Doorbell, Inc.': 179.7, 'Off Running AG': 90.2, 'Solid Bit Holding': 57.0 },
        { date: 'Dec 11, 2023', 'Doorbell, Inc.': 178.2, 'Off Running AG': 88.7, 'Solid Bit Holding': 55.6 },
        { date: 'Dec 12, 2023', 'Doorbell, Inc.': 175.9, 'Off Running AG': 86.5, 'Solid Bit Holding': 53.9 },
        { date: 'Dec 13, 2023', 'Doorbell, Inc.': 172.3, 'Off Running AG': 83.7, 'Solid Bit Holding': 52.1 },
        { date: 'Dec 14, 2023', 'Doorbell, Inc.': 169.8, 'Off Running AG': 81.4, 'Solid Bit Holding': 50.5 },
        { date: 'Dec 15, 2023', 'Doorbell, Inc.': 168.5, 'Off Running AG': 79.8, 'Solid Bit Holding': 48.9 },
        { date: 'Dec 16, 2023', 'Doorbell, Inc.': 170.2, 'Off Running AG': 81.5, 'Solid Bit Holding': 50.2 },
    ];

    const items: SparkChart05HoldingItem[] = [
        { name: 'Doorbell, Inc.', change: '+2.3%', changeType: 'positive' },
        { name: 'Solid Bit Holding', change: '-0.9%', changeType: 'negative' },
        { name: 'Off Running AG', change: '+4.1%', changeType: 'positive' },
    ];

    return <SparkChart05 data={data} items={items} />;
};

export const SparkChart06Example = () => {
    const data = [
        { date: 'Nov 24, 2023', 'Dow Jones': 156.2, SMI: 68.5, 'S&P 500': 71.8 },
        { date: 'Nov 25, 2023', 'Dow Jones': 152.5, SMI: 69.3, 'S&P 500': 67.2 },
        { date: 'Nov 26, 2023', 'Dow Jones': 148.7, SMI: 69.8, 'S&P 500': 61.5 },
        { date: 'Nov 27, 2023', 'Dow Jones': 155.3, SMI: 73.5, 'S&P 500': 57.9 },
        { date: 'Nov 28, 2023', 'Dow Jones': 160.1, SMI: 75.2, 'S&P 500': 59.6 },
        { date: 'Nov 29, 2023', 'Dow Jones': 175.6, SMI: 89.2, 'S&P 500': 57.3 },
        { date: 'Nov 30, 2023', 'Dow Jones': 180.2, SMI: 92.7, 'S&P 500': 59.8 },
        { date: 'Dec 01, 2023', 'Dow Jones': 185.5, SMI: 95.3, 'S&P 500': 62.4 },
        { date: 'Dec 02, 2023', 'Dow Jones': 182.3, SMI: 93.8, 'S&P 500': 60.7 },
        { date: 'Dec 03, 2023', 'Dow Jones': 180.7, SMI: 91.6, 'S&P 500': 58.9 },
        { date: 'Dec 04, 2023', 'Dow Jones': 178.5, SMI: 89.7, 'S&P 500': 56.2 },
        { date: 'Dec 05, 2023', 'Dow Jones': 176.2, SMI: 87.5, 'S&P 500': 54.8 },
        { date: 'Dec 06, 2023', 'Dow Jones': 174.8, SMI: 85.3, 'S&P 500': 53.4 },
        { date: 'Dec 07, 2023', 'Dow Jones': 178.0, SMI: 88.2, 'S&P 500': 55.2 },
        { date: 'Dec 08, 2023', 'Dow Jones': 180.6, SMI: 90.5, 'S&P 500': 56.8 },
        { date: 'Dec 09, 2023', 'Dow Jones': 182.4, SMI: 92.8, 'S&P 500': 58.4 },
        { date: 'Dec 10, 2023', 'Dow Jones': 179.7, SMI: 90.2, 'S&P 500': 57.0 },
        { date: 'Dec 11, 2023', 'Dow Jones': 154.2, SMI: 88.7, 'S&P 500': 55.6 },
        { date: 'Dec 12, 2023', 'Dow Jones': 151.9, SMI: 86.5, 'S&P 500': 53.9 },
        { date: 'Dec 13, 2023', 'Dow Jones': 149.3, SMI: 83.7, 'S&P 500': 52.1 },
        { date: 'Dec 14, 2023', 'Dow Jones': 148.8, SMI: 81.4, 'S&P 500': 50.5 },
        { date: 'Dec 15, 2023', 'Dow Jones': 145.5, SMI: 79.8, 'S&P 500': 48.9 },
        { date: 'Dec 16, 2023', 'Dow Jones': 140.2, SMI: 84.5, 'S&P 500': 50.2 },
    ];

    const items: SparkChart06Item[] = [
        { name: 'Dow Jones', description: 'Dow Jones Industrial Average', category: 'Dow Jones', change: '-3.2%', changeType: 'negative' },
        { name: 'SMI', description: 'Swiss Market Index', category: 'SMI', change: '+4.1%', changeType: 'positive' },
        { name: 'S&P 500', description: "Standard and Poor's 500", category: 'S&P 500', change: '-6.9%', changeType: 'negative' },
    ];

    return <SparkChart06 data={data} items={items} />;
};
