# Notice and provenance

Vanguard reuses and adapts code from two earlier projects by the same author (FaatehHaneef). The code was copied into this repository; the original repositories are unchanged.

| Source | Licence | What Vanguard uses |
|---|---|---|
| [Sentinel](https://github.com/FaatehHaneef/Sentinel), PayPal AI Hackathon submission | MIT | Tallowmere demo store and sandbox checkout (`apps/tallowmere`); gamified UI, characters and sprites (`apps/web`); ideas from its guards and Gemini client |
| [Synthetic Users](https://github.com/FaatehHaneef/Synthetic-Users), CS3014 Tool Talk | none stated | patterns for resumable runs and diversity measures |

## Copied so far
- 2026-11-21: `apps/tallowmere`, from Sentinel's `app/store`, `components/store`, `lib/store`, `lib/payments`, `lib/storage`, `lib/guards/sandbox.ts`, the Braintree part of `lib/env.ts`, `app/api/checkout`, `app/api/braintree`, `app/globals.css` and `public/store`. Adapted: served at the root, layouts merged, Sentinel's loader and links removed.

- 2026-11-21: `apps/web`, from Sentinel's `engine/art` (sprites), `engine/audio/sfx.ts`, `app/globals.css`, the root layout, `components/sentinel/Sprite.tsx`, `LobbyBackdrop.tsx` and `GameLobby.tsx`, and `public/store/banner.png` (as the lobby backdrop). Adapted to five Vanguard personas; Wren's sprite and every other screen are new.

- 2026-11-21: `backend/vanguard/metrics/stats.py`, from Synthetic Users' `synthusers/analyze.py` (`wilson_interval`, and the entropy calculation in `compute_metrics`). Adapted: proportions instead of percent, typed, entropy as its own function.

- 2026-11-21: `backend/vanguard/batch.py`, the balanced and resumable run pattern from Synthetic Users' `synthusers/generate.py` (`plan_next_job`, `run_generation`). Rewritten as a generic `next_group` over any batch groups.

- 2026-11-21: `backend/vanguard/explain/__init__.py`, the system prompt and response schema from Sentinel's `lib/ai/wick.ts` (the Wick verdict). Adapted to Vanguard's personas and findings; the coin purse and colour suggestions were dropped.

- 2026-11-22: `apps/hud`, a new overlay whose animation table and walking approach are adapted from Sentinel's `engine/hud/stage.ts`. Its sprites are imported from `apps/web/lib/art` (already listed above), not copied again. Sentinel's sound effects and clock were not needed.

Entries are added as each piece is committed.

## Datasets
Datasets are not redistributed in this repository. Each is used under its own licence; see `Vanguard.md`, Section 4.6a.
