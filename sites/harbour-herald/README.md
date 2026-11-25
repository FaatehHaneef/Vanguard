# Harbour Herald: test site

A local news site for the fictional Harbour Town, built as a static site with **Astro**, so it differs from the other test sites in stack (Tallowmere is Next.js, Willowbrook plain HTML, Northgate Vue, Riverside Flask) and domain. It has no server: the newsletter sign-up is confirmed in the page and nothing is sent anywhere.

Built separately from Vanguard's code, to the written specification in `docs/test-site-kit.md` and `docs/tasks-A3-round2.md` Section 0.7. Only the build in `dist/` is served; `MANIFEST.md` (barriers, honeytokens, task checks) stays out of the served site and out of the Docker image.

## Run
Node 22.12 or later.
```bash
cd sites/harbour-herald
npm ci
npm run build
npm run preview          # http://localhost:3106
```
`npm run dev` also serves on 3106, with live reload, for editing. With Docker: `docker compose up herald` (nginx serves the build).

Port 3106 is the origin Vanguard expects (`backend/vanguard/catalog/data/sites/herald.json`).

## Pages
| Path | Page |
|---|---|
| `/` | front page: lead story, top stories, the briefing tabs, newsletter call to action, a block per section, the week in pictures |
| `/section/<city, business, sport, culture>` | every story in a section |
| `/article/<slug>` | 24 stories, each with related stories from its section |
| `/search?q=<words>` | search over every story (every word must appear) |
| `/events` | 21 events by date |
| `/about` | about the paper, with questions in an accordion |
| `/contact` | the newsroom's desks |
| `/newsroom` | desk notes for staff, not linked from anywhere |

The newsletter sign-up opens in a dialog from the header, the front page and the footer.

## Design
CSS custom properties for colour, spacing and the type scale (`src/styles/global.css`); Fraunces for headlines and Libre Franklin for text, self-hosted from `@fontsource`; illustrations are SVG drawn for the site (`src/components/Art.astro`). Components: a sticky header, a slide-in menu on phones, tabs, a modal dialog, toasts, an accordion and a carousel. Transitions are 150 to 250 ms and are switched off under `prefers-reduced-motion`.

## Content
Articles are in `src/data/articles.js`, events in `src/data/events.js`. All dates are fixed text, so every build serves the same pages.
