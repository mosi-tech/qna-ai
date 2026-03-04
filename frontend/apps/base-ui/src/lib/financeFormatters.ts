/**
 * Finance-specific formatting utilities for numbers, currency, percentages, etc.
 * Designed to work with investment, trading, and general financial data.
 */

export interface FormattingOptions {
    decimals?: number;
    currency?: string;
    abbreviate?: boolean;
    thousandsSeparator?: boolean;
}

/**
 * Format a number with optional decimals and thousand separators
 * @param value The numeric value to format
 * @param decimals Number of decimal places (default: 2)
 * @param abbreviate Whether to abbreviate (1000000 -> 1M)
 * @param thousandsSeparator Whether to add thousand separators (default: true)
 * @returns Formatted string
 */
export const formatNumber = (
    value: number | string,
    decimals: number = 2,
    abbreviate: boolean = false,
    thousandsSeparator: boolean = true
): string => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    if (isNaN(num)) return String(value);

    let formatted: string;

    if (abbreviate) {
        const absNum = Math.abs(num);
        const sign = num < 0 ? '-' : '';

        if (absNum >= 1e9) {
            formatted = `${sign}${(num / 1e9).toFixed(decimals)}B`;
        } else if (absNum >= 1e6) {
            formatted = `${sign}${(num / 1e6).toFixed(decimals)}M`;
        } else if (absNum >= 1e3) {
            formatted = `${sign}${(num / 1e3).toFixed(decimals)}K`;
        } else {
            formatted = num.toFixed(decimals);
        }
    } else {
        formatted = num.toFixed(decimals);
    }

    if (thousandsSeparator && !abbreviate) {
        const parts = formatted.split('.');
        parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        formatted = parts.join('.');
    }

    return formatted;
};

/**
 * Format a value as currency
 * @param value The numeric value to format
 * @param currency Currency code (USD, EUR, GBP, etc.) - default: USD
 * @param decimals Number of decimal places (default: 2)
 * @param abbreviate Whether to abbreviate large numbers
 * @returns Formatted currency string
 */
export const formatCurrency = (
    value: number | string,
    currency: string = 'USD',
    decimals: number = 2,
    abbreviate: boolean = false
): string => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    if (isNaN(num)) return String(value);

    const currencySymbols: { [key: string]: string } = {
        USD: '$',
        EUR: '€',
        GBP: '£',
        JPY: '¥',
        CNY: '¥',
        INR: '₹',
        AUD: '$',
        CAD: '$',
        CHF: 'CHF',
    };

    const symbol = currencySymbols[currency.toUpperCase()] || currency;
    const formatted = formatNumber(num, decimals, abbreviate, true);

    return num < 0 ? `-${symbol}${Math.abs(parseFloat(formatted))}` : `${symbol}${formatted}`;
};

/**
 * Format a value as percentage
 * @param value The numeric value (0-100 or 0-1)
 * @param decimals Number of decimal places (default: 1)
 * @param asDecimal Whether the input is 0-1 range (default: false for 0-100)
 * @returns Formatted percentage string
 */
export const formatPercentage = (
    value: number | string,
    decimals: number = 1,
    asDecimal: boolean = false
): string => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    if (isNaN(num)) return String(value);

    const percentage = asDecimal ? num * 100 : num;
    return `${percentage.toFixed(decimals)}%`;
};

/**
 * Format a value as basis points (1 bp = 0.01%)
 * @param value The basis points value
 * @param decimals Number of decimal places (default: 0)
 * @returns Formatted basis points string
 */
export const formatBasisPoints = (
    value: number | string,
    decimals: number = 0
): string => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    if (isNaN(num)) return String(value);

    return `${num.toFixed(decimals)} bps`;
};

/**
 * Format a numeric value as a trading price/quote
 * For stocks: 123.45
 * For crypto: 0.0001234
 * @param value The price value
 * @param decimals Number of decimal places (auto-detect if not provided)
 * @returns Formatted price string
 */
export const formatPrice = (
    value: number | string,
    decimals?: number
): string => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    if (isNaN(num)) return String(value);

    // Auto-detect decimal places if not provided
    if (decimals === undefined) {
        if (num < 0.01) {
            decimals = 8; // Crypto precision
        } else if (num < 1) {
            decimals = 4; // Small price
        } else if (num < 100) {
            decimals = 2; // Standard stock price
        } else {
            decimals = 0; // Large number
        }
    }

    return formatNumber(num, decimals, false, true);
};

/**
 * Format value with sign indicator (+ or -)
 * Useful for change values
 * @param value The numeric value
 * @param decimals Number of decimal places
 * @param showPlus Whether to show + for positive values
 * @returns Formatted string with sign
 */
export const formatWithSign = (
    value: number | string,
    decimals: number = 2,
    showPlus: boolean = true
): string => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    if (isNaN(num)) return String(value);

    const formatted = formatNumber(num, decimals, false, true);
    if (num > 0) {
        return showPlus ? `+${formatted}` : formatted;
    }
    return formatted;
};

/**
 * Create a combined formatter for common finance scenarios
 * @param options Formatting options
 * @returns A formatter function
 */
export const createFormatter = (options: FormattingOptions) => {
    return (value: number | string): string => {
        if (options.currency) {
            return formatCurrency(value, options.currency, options.decimals, options.abbreviate);
        }
        return formatNumber(value, options.decimals, options.abbreviate, options.thousandsSeparator !== false);
    };
};
/**
 * Default currency formatter: USD with compact notation (e.g., $1.2M, $500K)
 * Suitable for finance/investment dashboards
 */
export const defaultCurrencyFormatter = (value: number): string => {
    return formatCurrency(value, 'USD', 0, true);
};