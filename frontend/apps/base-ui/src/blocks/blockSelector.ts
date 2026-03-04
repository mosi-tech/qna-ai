/**
 * Smart Block Selector & Layout Generator
 *
 * This utility:
 * 1. Analyzes block metadata for layout properties
 * 2. Selects N random compatible blocks
 * 3. Generates a responsive layout respecting their constraints
 * 4. Suggests composition patterns
 */

import blockMetadata from './BLOCK_METADATA.json';

export interface SelectedBlock {
    id: string;
    name: string;
    export: string;
    category: string;
    gridSpan: number;
    fullWidth: boolean;
    minHeight: string;
}

export interface GeneratedLayout {
    title: string;
    question: string;
    blocks: SelectedBlock[];
    layoutPattern: string;
    layoutDescription: string;
    gridColumns: number;
    rows: Array<{
        cols: number;
        blocks: SelectedBlock[];
    }>;
}

/**
 * Validate if two blocks can be paired together
 */
function canPair(block1Id: string, block2Id: string): boolean {
    const incompatible = blockMetadata.compositionRules.incompatiblePairs;
    return !incompatible.some(
        (pair) =>
            (pair.block1 === block1Id && pair.block2 === block2Id) ||
            (pair.block1 === block2Id && pair.block2 === block1Id)
    );
}

/**
 * Select N random blocks with composition rules
 */
export function selectRandomBlocks(count: number = 5, intent?: string): SelectedBlock[] {
    const allBlocks = blockMetadata.blocks;

    // Filter by intent if provided
    let availableBlocks = allBlocks;
    if (intent && blockMetadata.selectionRules.byIntent[intent as keyof typeof blockMetadata.selectionRules.byIntent]) {
        const intentBlockIds = blockMetadata.selectionRules.byIntent[intent as keyof typeof blockMetadata.selectionRules.byIntent];
        availableBlocks = allBlocks.filter((b) => intentBlockIds.includes(b.id));
    }

    if (availableBlocks.length < count) {
        availableBlocks = allBlocks;
    }

    const selected: SelectedBlock[] = [];
    const shuffled = [...availableBlocks].sort(() => Math.random() - 0.5);

    for (const block of shuffled) {
        if (selected.length >= count) break;

        // Check if compatible with already selected
        const isCompatible = selected.every((sel) => canPair(sel.id, block.id));

        if (isCompatible) {
            selected.push({
                id: block.id,
                name: block.name,
                export: block.export,
                category: block.category,
                gridSpan: (block.supportedGridCols as number[]).includes(1) ? 1 : 2,
                fullWidth: block.fullWidth,
                minHeight: block.minHeight,
            });
        }
    }

    // If we didn't get enough, add more without strict compatibility
    if (selected.length < count) {
        for (const block of shuffled) {
            if (selected.length >= count) break;
            if (!selected.some((sel) => sel.id === block.id)) {
                selected.push({
                    id: block.id,
                    name: block.name,
                    export: block.export,
                    category: block.category,
                    gridSpan: (block.supportedGridCols as number[]).includes(1) ? 1 : 2,
                    fullWidth: block.fullWidth,
                    minHeight: block.minHeight,
                });
            }
        }
    }

    return selected.slice(0, count);
}

/**
 * Generate responsive layout for selected blocks
 */
export function generateLayout(selectedBlocks: SelectedBlock[], question?: string): GeneratedLayout {
    // Count block types
    const categories = selectedBlocks.map((b) => b.category);
    const hasChart = categories.includes('chart') || categories.includes('composite');
    const hasTable = categories.includes('table') || categories.includes('composite');
    const hasMetric = categories.includes('metric');
    const hasBanner = categories.includes('banner');

    // Choose layout pattern based on composition
    let layoutPattern = 'single-column';
    let gridColumns = 1;

    if (selectedBlocks.length >= 4) {
        if (hasChart && hasTable && hasMetric) {
            layoutPattern = 'mixed-grid';
            gridColumns = 2;
        } else if (selectedBlocks.filter((b) => b.fullWidth).length <= 2) {
            layoutPattern = 'multi-column';
            gridColumns = selectedBlocks.length > 5 ? 3 : 2;
        }
    }

    // Build rows
    const rows: Array<{ cols: number; blocks: SelectedBlock[] }> = [];
    let currentRow: SelectedBlock[] = [];
    let currentRowCols = 0;

    // Banners go first, full width
    const bannerBlocks = selectedBlocks.filter((b) => b.category === 'banner');
    for (const block of bannerBlocks) {
        rows.push({ cols: gridColumns, blocks: [block] });
    }

    // Remaining blocks
    const otherBlocks = selectedBlocks.filter((b) => b.category !== 'banner');
    for (const block of otherBlocks) {
        const blockCols = block.fullWidth ? gridColumns : Math.max(1, Math.ceil(gridColumns / 2));

        if (currentRowCols + blockCols <= gridColumns && currentRow.length > 0) {
            currentRow.push(block);
            currentRowCols += blockCols;
        } else {
            if (currentRow.length > 0) {
                rows.push({ cols: gridColumns, blocks: currentRow });
            }
            currentRow = [block];
            currentRowCols = blockCols;
        }
    }

    if (currentRow.length > 0) {
        rows.push({ cols: gridColumns, blocks: currentRow });
    }

    const layoutDescriptions: Record<string, string> = {
        'single-column': 'Stacked single column layout for mobile-first design',
        'multi-column': 'Responsive grid layout with metrics and charts side-by-side',
        'mixed-grid': 'Mixed grid with full-width charts and multi-column metrics',
    };

    return {
        title: `Generated ${selectedBlocks.length}-Block Dashboard`,
        question: question || 'What is the overall status and performance of my portfolio?',
        blocks: selectedBlocks,
        layoutPattern,
        layoutDescription: layoutDescriptions[layoutPattern] || 'Custom responsive layout',
        gridColumns,
        rows,
    };
}

/**
 * Generate summary of selected blocks
 */
export function generateBlocksSummary(layout: GeneratedLayout): string {
    const blocks = layout.blocks
        .map((b, i) => {
            const metadata = blockMetadata.blocks.find((m) => m.id === b.id);
            return `${i + 1}. **${b.name}** (${b.category})\n   - ${metadata?.purpose || ''}`;
        });

    return blocks.join('\n\n');
}

/**
 * Get all available intents for filtering
 */
export function getAvailableIntents(): string[] {
    return Object.keys(blockMetadata.selectionRules.byIntent);
}

export default {
    selectRandomBlocks,
    generateLayout,
    generateBlocksSummary,
    getAvailableIntents,
    blockMetadata,
};
