import { GridTemplate } from './types';

export const GRID_TEMPLATES: Record<string, GridTemplate> = {
  '1-col': {
    id: '1-col',
    name: 'Single Column',
    description: 'One full-width column',
    cols: 1,
    slots: [
      { id: 'slot-1', colSpan: 1, rowSpan: 1 },
    ],
    cssClass: 'grid-cols-1',
  },
  '2-col': {
    id: '2-col',
    name: 'Two Columns',
    description: 'Two equal columns',
    cols: 2,
    slots: [
      { id: 'slot-1', colSpan: 1, rowSpan: 1 },
      { id: 'slot-2', colSpan: 1, rowSpan: 1 },
    ],
    cssClass: 'grid-cols-2',
  },
  '3-col': {
    id: '3-col',
    name: 'Three Columns',
    description: 'Three equal columns',
    cols: 3,
    slots: [
      { id: 'slot-1', colSpan: 1, rowSpan: 1 },
      { id: 'slot-2', colSpan: 1, rowSpan: 1 },
      { id: 'slot-3', colSpan: 1, rowSpan: 1 },
    ],
    cssClass: 'grid-cols-3',
  },
  '2-1': {
    id: '2-1',
    name: 'Top 2 + Bottom 1',
    description: 'Two columns top, one full width bottom',
    cols: 2,
    slots: [
      { id: 'slot-1', colSpan: 1, rowSpan: 1 },
      { id: 'slot-2', colSpan: 1, rowSpan: 1 },
      { id: 'slot-3', colSpan: 2, rowSpan: 1 },
    ],
    cssClass: 'grid-cols-2',
  },
  '1-2': {
    id: '1-2',
    name: 'Top 1 + Bottom 2',
    description: 'One full width top, two columns bottom',
    cols: 2,
    slots: [
      { id: 'slot-1', colSpan: 2, rowSpan: 1 },
      { id: 'slot-2', colSpan: 1, rowSpan: 1 },
      { id: 'slot-3', colSpan: 1, rowSpan: 1 },
    ],
    cssClass: 'grid-cols-2',
  },
  '3-1-2': {
    id: '3-1-2',
    name: '3 Rows',
    description: 'Three rows: 2 cols, 1 full, 2 cols',
    cols: 2,
    slots: [
      { id: 'slot-1', colSpan: 1, rowSpan: 1 },
      { id: 'slot-2', colSpan: 1, rowSpan: 1 },
      { id: 'slot-3', colSpan: 2, rowSpan: 1 },
      { id: 'slot-4', colSpan: 1, rowSpan: 1 },
      { id: 'slot-5', colSpan: 1, rowSpan: 1 },
    ],
    cssClass: 'grid-cols-2',
  },
};
