"use client";

import React from "react";

const GRID_COLUMNS = 12;

type GridItem = {
  id: string;
  layoutHint: "full" | "half" | "third";
  heightHint: "short" | "medium" | "tall";
};

const layoutHintToCols = {
  full: 12,
  half: 6,
  third: 4,
};

const layoutHintToClass = {
  full: "col-span-12",
  half: "col-span-6", 
  third: "col-span-4",
};

const heightHintToClass = {
  short: "min-h-24",
  medium: "min-h-48", 
  tall: "min-h-72",
};

function DynamicLayout({ items }: { items: GridItem[] }) {
  const rows: GridItem[][] = [];
  let currentRow: GridItem[] = [];
  let currentWidth = 0;

  for (const item of items) {
    const width = layoutHintToCols[item.layoutHint];
    if (currentWidth + width > GRID_COLUMNS) {
      rows.push(currentRow);
      currentRow = [];
      currentWidth = 0;
    }
    currentRow.push(item);
    currentWidth += width;
  }
  if (currentRow.length) rows.push(currentRow);

  return (
    <div className="space-y-4 p-4 h-full w-full">
      {rows.map((row, rowIndex) => (
        <div key={rowIndex} className="grid grid-cols-12 gap-4 auto-rows-min w-full">
          {row.map((item) => (
            <div
              key={item.id}
              className={`${layoutHintToClass[item.layoutHint]} ${heightHintToClass[item.heightHint]} bg-gray-200 border border-gray-400 p-4 text-center`}
            >
              {item.id} ({item.layoutHint}, {item.heightHint})
              <br />
              <div className="mt-4 text-sm text-gray-600">
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
                Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                {item.heightHint === 'tall' && (
                  <>
                    <br />
                    Ut enim ad minim veniam, quis nostrud exercitation ullamco 
                    laboris nisi ut aliquip ex ea commodo consequat. Duis aute 
                    irure dolor in reprehenderit in voluptate velit esse cillum 
                    dolore eu fugiat nulla pariatur.
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

function generateRandomItems() {
  const layoutHints: GridItem["layoutHint"][] = ["full", "half", "third"];
  const heightHints: GridItem["heightHint"][] = ["short", "medium", "tall"];
  const count = Math.floor(Math.random() * 3) + 3;
  const items: GridItem[] = [];

  for (let i = 0; i < count; i++) {
    items.push({
      id: `Item-${i + 1}`,
      layoutHint: layoutHints[Math.floor(Math.random() * layoutHints.length)],
      heightHint: heightHints[Math.floor(Math.random() * heightHints.length)],
    });
  }

  return items;
}

export default function DynamicGridPage() {
  const items = generateRandomItems();

  return (
    <div className="min-h-screen w-full">
      <h1 className="text-xl font-bold p-4">Dynamic Grid Layout Test</h1>
      <div className="h-full">
        <DynamicLayout items={items} />
      </div>
    </div>
  );
}