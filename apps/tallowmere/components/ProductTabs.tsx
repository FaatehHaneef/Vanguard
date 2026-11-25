"use client";

import { useRef, useState } from "react";
import type { Product } from "@/lib/store/catalogue";

/** Details about a candle, in tabs. Arrow keys move between the tabs. */
export function ProductTabs({ product }: { product: Product }) {
  const tabs = [
    { id: "about", label: "About", text: product.description },
    {
      id: "burning",
      label: "Burning tips",
      text: `Let the first burn reach the edge of the jar, about two hours, so the wax melts evenly. Trim the wick to 5 mm before each lighting. Expect about ${product.burnHours} hours in all.`,
    },
    {
      id: "made",
      label: "What's inside",
      text: "A soy and beeswax blend, a cotton wick and fragrance oils free of phthalates. The jar is recycled glass and can be washed and used again.",
    },
  ];
  const [active, setActive] = useState(tabs[0].id);
  const buttons = useRef<(HTMLButtonElement | null)[]>([]);

  function move(event: React.KeyboardEvent, index: number) {
    const keys: Record<string, number> = { ArrowRight: index + 1, ArrowLeft: index - 1, Home: 0, End: tabs.length - 1 };
    if (!(event.key in keys)) return;
    event.preventDefault();
    const next = (keys[event.key] + tabs.length) % tabs.length;
    setActive(tabs[next].id);
    buttons.current[next]?.focus();
  }

  const current = tabs.find((tab) => tab.id === active) ?? tabs[0];
  return (
    <div>
      <div role="tablist" aria-label="About this candle" className="flex flex-wrap gap-1 border-b border-line">
        {tabs.map((tab, index) => (
          <button
            key={tab.id}
            ref={(element) => {
              buttons.current[index] = element;
            }}
            id={`tab-${tab.id}`}
            type="button"
            role="tab"
            aria-selected={active === tab.id}
            aria-controls="product-panel"
            tabIndex={active === tab.id ? 0 : -1}
            onClick={() => setActive(tab.id)}
            onKeyDown={(event) => move(event, index)}
            className={`-mb-px border-b-2 px-3 py-2 font-bold transition-colors duration-150 ${
              active === tab.id ? "border-wax text-wax" : "border-transparent text-ink-soft hover:text-ink"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <p id="product-panel" role="tabpanel" aria-labelledby={`tab-${current.id}`} className="rise pt-4 text-lg">
        {current.text}
      </p>
    </div>
  );
}
