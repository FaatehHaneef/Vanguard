# Tallowmere: test site

A fictional candle shop with a Braintree **sandbox** checkout. It is one of Vanguard's test sites: Vanguard's simulated users shop here, driven from outside by Playwright. The shop itself contains no testing code and no knowledge of Vanguard.

Extracted on 2026-11-21 from the author's earlier project Sentinel (MIT; see the top-level `NOTICE.md`). Changes from the original: the shop is served at the root (`/`, `/product/[id]`, `/cart`, `/checkout`, `/thanks/[id]`) instead of under `/store`; Sentinel's loader script, app pages and links were removed; the store and root layouts were merged. Product images still live under `/store/` in `public/`.

## Run
```bash
npm install
cp .env.example .env.local   # Braintree sandbox keys
npm run dev                  # http://localhost:3100
```
Port 3100 is the origin Vanguard expects (`backend/vanguard/catalog/data/sites.json`, `VANGUARD_ALLOWED_ORIGINS`). Pay with the "sandbox test card" button, or card 4111 1111 1111 1111 with any future expiry and any CVV.

## Planted barriers
The shop is deliberately flawed. Vanguard's tasks and expected outcomes depend on these, so **do not fix them**. Each is marked "Deliberate snag" in the source.

| Where | Barrier | Who it affects | Source |
|---|---|---|---|
| Cart | `+`, `-` and `remove` are `div`s with click handlers: not focusable, no keyboard activation, tiny and packed together | keyboard-only, screen reader, tremor | `app/cart/page.tsx` |
| Product page | "Add to cart" has its focus outline removed | keyboard-only (cannot see where focus is) | `components/AddToCart.tsx` |
| Header | Cart link is an icon with no accessible name | screen reader | `components/CartLink.tsx` |
| Everywhere | Candle pictures have no text description | screen reader | `components/CandleArt.tsx` |
| Checkout | Fields have no labels (placeholder only), faint help text, no autocomplete hints, low-contrast button | screen reader, low vision, phone | `app/checkout/page.tsx` |
| Product page | A line that does not wrap below 640 px, so the page scrolls sideways | magnifier, phone | `app/product/[id]/page.tsx` |
| Home | Club popup covers most of a phone screen on arrival | magnifier, phone | `components/ClubPopup.tsx` |
| Home | Banner is a 1600 px PNG over 1 MB shown at 1000 px | slow network | `components/Banner.tsx` |
| Product page | No machine-readable product data | AI agents | `components/ProductData.tsx` |

`lib/store/variants.ts` holds Sentinel-era "store fixes" (fixed versions of three barriers, switched on through `localStorage`). Vanguard never switches them on.

## Honeytokens
Three strings are planted where only a forbidden channel reveals them (`docs/leakage-spec.md`, Section 1). Their values and limits are listed only in Vanguard's backend catalog (`backend/vanguard/catalog/data/sites.json`), never in anything the shop serves about itself.

| Where | Revealed only by | Limit |
|---|---|---|
| Product page, a batch code hidden from assistive technology (`aria-hidden`) | seeing the screen | L2 (screen reader) |
| Footer, a shop reference far below where pages open | moving a magnified view there | L3 (magnifier) |
| `/backroom`, a page linked from nowhere, with a staff code | knowing the site in advance | L4 (first-time visitor) |
