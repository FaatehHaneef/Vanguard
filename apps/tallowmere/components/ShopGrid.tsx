"use client";

import Link from "next/link";
import { useRef, useState } from "react";
import { CandleArt } from "@/components/CandleArt";
import { FAMILIES, type Family, formatPrice, PRODUCTS } from "@/lib/store/catalogue";

type Tab = "all" | Family;
const TABS: { id: Tab; label: string }[] = [{ id: "all", label: "All candles" }, ...FAMILIES];

/** Every candle, with tabs by scent family. Arrow keys move between the tabs. */
export function ShopGrid() {
  const [tab, setTab] = useState<Tab>("all");
  const buttons = useRef<(HTMLButtonElement | null)[]>([]);
  const shown = tab === "all" ? PRODUCTS : PRODUCTS.filter((product) => product.family === tab);

  function move(event: React.KeyboardEvent, index: number) {
    const keys: Record<string, number> = {
      ArrowRight: index + 1,
      ArrowLeft: index - 1,
      Home: 0,
      End: TABS.length - 1,
    };
    if (!(event.key in keys)) return;
    event.preventDefault();
    const next = (keys[event.key] + TABS.length) % TABS.length;
    setTab(TABS[next].id);
    buttons.current[next]?.focus();
  }

  return (
    <section aria-labelledby="candles-heading" className="mt-14" id="candles">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <h2 id="candles-heading" className="font-display text-3xl font-bold">
          Shop by scent
        </h2>
        <div role="tablist" aria-label="Scent families" className="flex flex-wrap gap-1 rounded-full bg-card p-1 shadow-sm">
          {TABS.map((entry, index) => (
            <button
              key={entry.id}
              ref={(element) => {
                buttons.current[index] = element;
              }}
              id={`tab-${entry.id}`}
              type="button"
              role="tab"
              aria-selected={tab === entry.id}
              aria-controls="candle-panel"
              tabIndex={tab === entry.id ? 0 : -1}
              onClick={() => setTab(entry.id)}
              onKeyDown={(event) => move(event, index)}
              className={`rounded-full px-4 py-2 text-sm font-bold transition-colors duration-150 ${
                tab === entry.id ? "bg-wax text-card shadow" : "text-ink-soft hover:text-ink"
              }`}
            >
              {entry.label}
            </button>
          ))}
        </div>
      </div>
      <div id="candle-panel" role="tabpanel" aria-labelledby={`tab-${tab}`}>
        <p className="mt-3 text-ink-soft">
          {shown.length} candle{shown.length === 1 ? "" : "s"}
        </p>
        <ul className="mt-5 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {shown.map((product) => (
            <li key={product.id} className="rise">
              <Link
                href={`/product/${product.id}`}
                className="group flex h-full flex-col items-center gap-3 rounded-2xl border border-line bg-card p-5 text-center shadow-sm transition duration-200 hover:-translate-y-1 hover:border-wax hover:shadow-lg"
              >
                <span className="rounded-full bg-paper p-3 transition-transform duration-200 group-hover:scale-105">
                  <CandleArt product={product} size={112} />
                </span>
                <span className="font-display text-xl font-bold">{product.name}</span>
                <span className="text-ink-soft">{product.blurb}</span>
                <span className="mt-auto flex w-full items-center justify-between pt-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-ink-soft">
                    {product.burnHours} hours
                  </span>
                  <span className="text-lg font-bold text-wax">{formatPrice(product.priceCents)}</span>
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
