# Vanguard web app

Proposed owner: Hadi. Status: **to be ported** from Sentinel's gamified UI (`sentinel/`, read-only reference clone; copy out of it, never edit it).

Next.js + React + TypeScript + Tailwind, as in Sentinel. It talks only to the Vanguard API (`http://localhost:8000`, OpenAPI at `/docs`). It never talks to model providers or to the test site directly.

## Flow (Vanguard.md, Section 6.1)
landing → lobby (pick characters) → **pick site** (A3: Tallowmere only) → start trial → live view → results / ledger.

## What to bring over from Sentinel

| Sentinel | Vanguard use |
|---|---|
| `app/page.tsx`, `components/sentinel/LobbyBackdrop.tsx`, `GameLobby.tsx` | landing page and animations |
| `app/lobby/page.tsx`, `components/sentinel/PartyPicker.tsx` | lobby: pick characters |
| `engine/art/*.ts`, `engine/art/sprite.ts` | sprites. Knock, Echo, Iris and Cog exist. **Wren** (first-time visitor) is new and needs drawing in the same style |
| `engine/audio/sfx.ts` | sounds |
| `components/sentinel/RunResults.tsx`, `app/runs/[id]/page.tsx` | results page, reading `/runs/{id}` and `/runs/{id}/steps` |
| `components/sentinel/Ledger.tsx`, `app/ledger/page.tsx` | ledger of steps across runs (AG Grid) |

**Leave behind:** `engine/core`, `engine/journeys`, `engine/checks`, `lib/trial/*` (scripted walking, scoring and Sentinel's checks are replaced by the Vanguard backend), the loader and `app/sites` (own-site testing is A4 and works differently).

## Screens to build or adapt for A3
1. **Lobby:** all five characters from `GET /personas`. Echo, Iris and Wren show a **Preview** badge (`status == "preview"`).
2. **Site picker (new):** cards from `GET /sites`; A3 shows Tallowmere only. Then tasks from `GET /sites/{id}/tasks`.
3. **Run setup:** enforcement option (prompt-only or gate; preview personas get prompt-only only), number of repeats. `POST /runs` per run.
4. **Live view:** poll `/runs/{id}/steps`. Show per step: what the persona perceived, the proposed action and rationale, the gate decision (blocked steps in red with the rule id), and the outcome. The sprite overlay on the page itself is done in the worker (Faateh).
5. **Results:** outcome, steps, blocks, leakage (from the checker, once built) and the plain-language verdict. Mark preview personas' results "not validated".

## Provenance
Add a line to the top-level `NOTICE.md` when Sentinel code is first committed here.
