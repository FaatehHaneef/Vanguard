# Vanguard web app

Next.js + React + TypeScript + Tailwind. The gamified look (dusk theme, pixel characters, turning lobby) is ported from the author's earlier project Sentinel (MIT; see the top-level `NOTICE.md`). Everything else is Vanguard's own.

The app talks only to the Vanguard API (`NEXT_PUBLIC_VANGUARD_API`, default `http://localhost:8000`). It never calls a model provider or a test site directly.

## Run
```bash
npm install
npm run dev          # http://localhost:3000, with the backend running on :8000
```

## Flow and screens
| Route | Screen |
|---|---|
| `/` | Landing: the five characters in a turning circle; "Start your trial" walks them into a line |
| `/lobby` | Choose the party. Preview personas carry a badge; full or preview comes from `GET /personas` |
| `/sites?party=…` | Choose the site (Tallowmere for now; "your own site" comes later), the task, the enforcement option (prompt-only or gate), the model and the runs per persona |
| `/trials/[batch]` | Every run in the trial, refreshed until all finish |
| `/runs/[id]` | One run, step by step: proposed action and rationale, the gate's decision (refused steps in red with the rule id), and, when expanded, what the persona perceived and the input events |
| `/trials` | Past trials |

## Code map
- `lib/cast.ts`: display data for each character (name, motto, limits in plain words, accent). Matched to personas by id.
- `lib/api.ts`: typed client for the API. The types mirror `backend/vanguard/contracts`.
- `lib/art/`: the sprites as text grids. `wren.ts` is new; the others come from Sentinel. Dash, Pell and Tobin are kept for possible condition characters.
- `lib/audio/sfx.ts`: sound effects from Sentinel, for the live view.
- `components/`: `GameLobby`, `Sprite`, `LobbyBackdrop` (ported); `SitePicker`, `TrialBoard`, `RunFeed`, `TrialList` (new).

## Not built yet
Leakage and metrics on the results page (waiting on the checker and metrics), the ledger across runs, the comparison view, the labelling workspace, the persona builder and own-site testing.
