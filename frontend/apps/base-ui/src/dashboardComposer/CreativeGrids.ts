import { GridTemplate } from './types';

export const CREATIVE_GRIDS: Record<string, GridTemplate> = {
  // Single column
  'single-col': {
    id: 'single-col',
    name: '📍 Single Column',
    cols: 1,
    slots: [{ id: 'slot-1', colSpan: 1, rowSpan: 1 }],
    cssClass: 'grid-cols-1',
  },
  // Two columns
  'two-col': {
    id: 'two-col',
    name: '📐 Two Equal',
    cols: 2,
    slots: [
      { id: 'slot-1', colSpan: 1, rowSpan: 1 },
      { id: 'slot-2', colSpan: 1, rowSpan: 1 },
    ],
    cssClass: 'grid-cols-2',
  },
  'two-col-wide-narrow': {
    id: 'two-col-wide-narrow',
    name: '📏 Wide + Narrow',
    cols: 3,
    slots: [
      { id: 'slot-1', colSpan: 2, rowSpan: 1 },
      { id: 'slot-2', colSpan: 1, rowSpan: 1 },
    ],
    cssClass: 'grid-cols-3',
  },
  'two-col-stacked': {
    id: 'two-col-stacked',
    name: '📦 Two Stacked',
    cols: 2,
    slots: [
      { id: 'slot-1', colSpan: 1, rowSpan: 2 },
      { id: 'slot-2', colSpan: 1, rowSpan: 1 },
      { id: 'slot-3', colSpan: 1, rowSpan: 1 },
    ],
    cssClass: 'grid-cols-2',
  },
  // Three columns
  'three-col': {
    id: 'three-col',
    name: '🔷 Three Equal',
    cols: 3,
    slots: [
      { id: 'slot-1', colSpan: 1, rowSpan: 1 },
      { id: 'slot-2', colSpan: 1, rowSpan: 1 },
      { id: 'slot-3', colSpan: 1, rowSpan: 1 },
    ],
    cssClass: 'grid-cols-3',
  },
  'three-col-wide': {
    id: 'three-col-wide',
    name: '📊 3Col Large',
    cols: 3,
    slots: [
      { id: 'slot-1', colSpan: 2, rowSpan: 1 },
      { id: 'slot-2', colSpan: 1, rowSpan: 1 },
      { id: 'slot-3', colSpan: 1, rowSpan: 1 },
      { id: 'slot-4', colSpan: 1, rowSpan: 1 },
    ],
    cssClass: 'grid-cols-3',
  },
  'three-col-hero': {
    id: 'three-col-hero',
    name: '🎬 3Col Hero',
    cols: 3,
    slots: [
      { id: 'slot-1', colSpan: 3, rowSpan: 1 },
      { id: 'slot-2', colSpan: 1, rowSpan: 1 },
      { id: 'slot-3', colSpan: 1, rowSpan: 1 },
      { id: 'slot-4', colSpan: 1, rowSpan: 1 },
    ],
    cssClass: 'grid-cols-3',
  },
  // Four columns
  'quad-balance': {
    id: 'quad-balance',
    name: '⚖️ Quad Balance',
    cols: 2,
    slots: [
      { id: 'slot-1', colSpan: 1, rowSpan: 1 },
      { id: 'slot-2', colSpan: 1, rowSpan: 1 },
      { id: 'slot-3', colSpan: 1, rowSpan: 1 },
      { id: 'slot-4', colSpan: 1, rowSpan: 1 },
    ],
    cssClass: 'grid-cols-2',
  },
  'four-col': {
    id: 'four-col',
    name: '📊 Four Col',
    cols: 4,
    slots: [
      { id: 'slot-1', colSpan: 1, rowSpan: 1 },
      { id: 'slot-2', colSpan: 1, rowSpan: 1 },
      { id: 'slot-3', colSpan: 1, rowSpan: 1 },
      { id: 'slot-4', colSpan: 1, rowSpan: 1 },
    ],
    cssClass: 'grid-cols-4',
  },
  'four-col-2tall': {
    id: 'four-col-2tall',
    name: '🏢 4Col 2Tall',
    cols: 4,
    slots: [
      { id: 'slot-1', colSpan: 2, rowSpan: 2 },
      { id: 'slot-2', colSpan: 1, rowSpan: 1 },
      { id: 'slot-3', colSpan: 1, rowSpan: 1 },
      { id: 'slot-4', colSpan: 1, rowSpan: 1 },
      { id: 'slot-5', colSpan: 1, rowSpan: 1 },
    ],
    cssClass: 'grid-cols-4',
  },
  // Asymmetric layouts
  'asymmetric-focus': {
    id: 'asymmetric-focus',
    name: '🔍 Focus',
    cols: 4,
    slots: [
      { id: 'slot-1', colSpan: 2, rowSpan: 2 },
      { id: 'slot-2', colSpan: 2, rowSpan: 1 },
      { id: 'slot-3', colSpan: 1, rowSpan: 1 },
      { id: 'slot-4', colSpan: 1, rowSpan: 1 },
    ],
    cssClass: 'grid-cols-4',
  },
  'asymmetric-alt': {
    id: 'asymmetric-alt',
    name: '🔀 Focus Alt',
    cols: 4,
    slots: [
      { id: 'slot-1', colSpan: 2, rowSpan: 1 },
      { id: 'slot-2', colSpan: 2, rowSpan: 2 },
      { id: 'slot-3', colSpan: 1, rowSpan: 1 },
      { id: 'slot-4', colSpan: 1, rowSpan: 1 },
    ],
    cssClass: 'grid-cols-4',
  },
  // Flowing layouts
  'flowing-rows': {
    id: 'flowing-rows',
    name: '🌊 Flowing',
    cols: 3,
    slots: [
      { id: 'slot-1', colSpan: 3, rowSpan: 1 },
      { id: 'slot-2', colSpan: 1, rowSpan: 1 },
      { id: 'slot-3', colSpan: 1, rowSpan: 1 },
      { id: 'slot-4', colSpan: 1, rowSpan: 1 },
      { id: 'slot-5', colSpan: 3, rowSpan: 1 },
    ],
    cssClass: 'grid-cols-3',
  },
  'flowing-alt': {
    id: 'flowing-alt',
    name: '🌀 Flow Alt',
    cols: 4,
    slots: [
      { id: 'slot-1', colSpan: 4, rowSpan: 1 },
      { id: 'slot-2', colSpan: 2, rowSpan: 1 },
      { id: 'slot-3', colSpan: 2, rowSpan: 1 },
      { id: 'slot-4', colSpan: 4, rowSpan: 1 },
    ],
    cssClass: 'grid-cols-4',
  },
  // Sidebar layouts
  'sidebar-main-footer': {
    id: 'sidebar-main-footer',
    name: '📱 Sidebar+Main',
    cols: 4,
    slots: [
      { id: 'slot-1', colSpan: 1, rowSpan: 2 },
      { id: 'slot-2', colSpan: 3, rowSpan: 1 },
      { id: 'slot-3', colSpan: 3, rowSpan: 1 },
    ],
    cssClass: 'grid-cols-4',
  },
  'sidebar-right': {
    id: 'sidebar-right',
    name: '📋 Side Right',
    cols: 4,
    slots: [
      { id: 'slot-1', colSpan: 3, rowSpan: 2 },
      { id: 'slot-2', colSpan: 1, rowSpan: 1 },
      { id: 'slot-3', colSpan: 1, rowSpan: 1 },
    ],
    cssClass: 'grid-cols-4',
  },
  'double-sidebar': {
    id: 'double-sidebar',
    name: '📑 Double Side',
    cols: 5,
    slots: [
      { id: 'slot-1', colSpan: 1, rowSpan: 2 },
      { id: 'slot-2', colSpan: 3, rowSpan: 2 },
      { id: 'slot-3', colSpan: 1, rowSpan: 2 },
    ],
    cssClass: 'grid-cols-5',
  },
  // Magazine/Feature layouts
  'magazine-layout': {
    id: 'magazine-layout',
    name: '📰 Magazine',
    cols: 4,
    slots: [
      { id: 'slot-1', colSpan: 2, rowSpan: 2 },
      { id: 'slot-2', colSpan: 2, rowSpan: 1 },
      { id: 'slot-3', colSpan: 1, rowSpan: 1 },
      { id: 'slot-4', colSpan: 1, rowSpan: 1 },
    ],
    cssClass: 'grid-cols-4',
  },
  'magazine-alt': {
    id: 'magazine-alt',
    name: '📖 Mag Alt',
    cols: 6,
    slots: [
      { id: 'slot-1', colSpan: 3, rowSpan: 2 },
      { id: 'slot-2', colSpan: 3, rowSpan: 1 },
      { id: 'slot-3', colSpan: 1, rowSpan: 1 },
      { id: 'slot-4', colSpan: 1, rowSpan: 1 },
      { id: 'slot-5', colSpan: 1, rowSpan: 1 },
    ],
    cssClass: 'grid-cols-6',
  },
  // Balanced complex
  'balanced-3x3': {
    id: 'balanced-3x3',
    name: '⚡ Balanced',
    cols: 6,
    slots: [
      { id: 'slot-1', colSpan: 2, rowSpan: 1 },
      { id: 'slot-2', colSpan: 2, rowSpan: 1 },
      { id: 'slot-3', colSpan: 2, rowSpan: 1 },
      { id: 'slot-4', colSpan: 3, rowSpan: 1 },
      { id: 'slot-5', colSpan: 3, rowSpan: 1 },
    ],
    cssClass: 'grid-cols-6',
  },
  'grid-6': {
    id: 'grid-6',
    name: '🎯 Grid 6x1',
    cols: 6,
    slots: Array.from({ length: 6 }, (_, i) => ({
      id: `slot-${i + 1}`,
      colSpan: 1,
      rowSpan: 1,
    })),
    cssClass: 'grid-cols-6',
  },
};
