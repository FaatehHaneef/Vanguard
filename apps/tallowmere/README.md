# Tallowmere: standalone test site

Proposed owner: Hadi. Status: **to be extracted** from `sentinel/` (read-only reference clone; never edit it, copy out of it).

Tallowmere is the candle shop Vanguard's simulated users shop in. It becomes its own Next.js app with no knowledge of Vanguard, exactly like a customer's site. Vanguard drives it from outside with Playwright.

## What to copy (all paths relative to `sentinel/`)

| From | To | Notes |
|---|---|---|
| `app/store/**` | `app/**` | Serve the shop at the **root**: `/`, `/product/[id]`, `/cart`, `/checkout`, `/thanks/[id]`. The Vanguard tasks use these paths (`backend/vanguard/catalog/data/sites.json`) |
| `components/store/**` | `components/**` | Update `/store/...` links to the new root paths (16 occurrences found by grep) |
| `lib/store/**` | `lib/store/**` | `variants.ts` holds Sentinel's "store fixes"; keep the file but nothing in Vanguard switches fixes on |
| `lib/payments/**`, `lib/guards/sandbox.ts`, the Braintree parts of `lib/env.ts` | same | Sandbox only; `assertSandboxOnly` must stay |
| `app/api/checkout/**`, `app/api/braintree/webhook/**` | `app/api/**` | Server-side prices and order ids stay as they are |
| `public/store/**`, store fonts and styles from `app/globals.css` | same | |

**Do not copy** `engine/`, `lib/trial/`, `lib/ai/`, `components/sentinel/` or the loader: the shop must not contain any testing code.

## Must stay exactly as it is
- The **deliberate barriers**, especially the cart's `+`, `-` and `remove` controls, which are `div`s with click handlers and are not keyboard reachable (`sentinel/app/store/cart/page.tsx`, lines 40-65). The `buy-two` task depends on it.
- The "Pay with the sandbox test card" button on the payment step.
- Product names and prices (the `cheapest` task expects Moss Path at $16.00).

## Run
- Port **3100** (`next dev -p 3100`); this is the origin in `sites.json` and in `VANGUARD_ALLOWED_ORIGINS`.
- Add a `Dockerfile` and a `tallowmere` service to `docker-compose.yml`.
- Needs Braintree **sandbox** keys in its own `.env.local` (never committed).

## Provenance
Add a line to the top-level `NOTICE.md` when the copy is committed.
