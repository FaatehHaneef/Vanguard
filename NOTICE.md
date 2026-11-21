# Notice and provenance

Vanguard reuses and adapts code from two earlier projects by the same author (FaatehHaneef). The code was copied into this repository; the original repositories are unchanged.

| Source | Licence | What Vanguard uses |
|---|---|---|
| [Sentinel](https://github.com/FaatehHaneef/Sentinel), PayPal AI Hackathon submission | MIT | Tallowmere demo store and sandbox checkout (`apps/tallowmere`); gamified UI, characters and sprites (`apps/web`); ideas from its guards and Gemini client |
| [Synthetic Users](https://github.com/FaatehHaneef/Synthetic-Users), CS3014 Tool Talk | none stated | patterns for resumable runs and diversity measures |

## Copied so far
- 2026-11-21: `apps/tallowmere`, from Sentinel's `app/store`, `components/store`, `lib/store`, `lib/payments`, `lib/storage`, `lib/guards/sandbox.ts`, the Braintree part of `lib/env.ts`, `app/api/checkout`, `app/api/braintree`, `app/globals.css` and `public/store`. Adapted: served at the root, layouts merged, Sentinel's loader and links removed.

Entries are added as each piece is committed.

## Datasets
Datasets are not redistributed in this repository. Each is used under its own licence; see `Vanguard.md`, Section 4.6a.
