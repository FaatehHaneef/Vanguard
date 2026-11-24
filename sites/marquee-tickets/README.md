# Marquee Tickets: test site

An events and ticketing site for a fictional town, Carrick: gigs, theatre, comedy, classical concerts and family shows at four venues. Built with SvelteKit (Svelte 5) and the static adapter: every page is rendered to HTML at build time and then runs in the browser. It differs from the other sites in stack (prerendered SvelteKit) and domain (choosing and booking tickets). Nothing is paid or sent: the basket and the booking live in the browser's session storage.

Built separately from Vanguard's code, to the written specification in `docs/test-site-kit.md` and the round 2 quality bar. Only the built site (`build/`) is served; `MANIFEST.md` (barriers, honeytokens, task checks) stays out of it.

## Run
```bash
npm install
npm run dev                          # http://localhost:3105
```
A production build is closer to a real site: `npm run build && npm run preview` (also on port 3105). `npm run check` checks the Svelte and TypeScript. After a rebuild, restart `npm run preview`: it reads the file list once when it starts.

With Docker: `docker compose up marquee` from the repository root. The image builds the site with Node 22 and serves `build/` with nginx on port 3105; unknown paths get `404.html`.

Port 3105 is the origin Vanguard expects (`backend/vanguard/catalog/data/sites/marquee.json`). The port is fixed (`strictPort`), so the dev server stops with an error instead of moving to another port if 3105 is taken.

## Pages
`/` home: search, the "Coming up" carousel, genres, this month and venues · `/events` all events with search and date, venue and genre filters (`/events?q=...`, `?genre=jazz`, `?venue=the-foundry`) · `/events/<event>` an event, its tickets and the booking form · `/basket` · `/checkout` · `/confirmation` · `/venues` and `/venues/<venue>` (tabs: what's on, getting there, access) · `/faq` questions and answers · `/presale` a members' page (not linked from anywhere)

## Design system
- Tokens in `src/lib/styles/tokens.css`: colour, a type scale, 4 px spacing steps, radii, shadows and motion durations (150 to 300 ms, set to 0 under `prefers-reduced-motion`).
- Typefaces: Anton (display) and Inter (body), self-hosted from the `@fontsource` packages; no font is loaded from another origin.
- Components in `src/lib/styles/components.css`: buttons, fields, radio cards, cards, chips, tabs, accordion, stepper and notifications; the carousel and the header menu in `pages.css` and `layout.css`. Each has hover, active, focus and disabled states.
- Posters and the sign on the home page are inline SVG drawn for the site (`src/lib/components/Poster.svelte`). There are no photos.

## Content
26 events at 4 venues, from December 2026 to February 2027, in `src/lib/data/events.ts` and `src/lib/data/venues.ts`. Everything is fixed: no random content, no clock, no network requests. One order holds at most 6 tickets.

## Layout
```
svelte.config.js                 static adapter and prerendering
src/app.html                     the page shell
src/routes/                      one folder per page (+page.svelte, and +page.ts where it loads data)
src/lib/components/              header, footer, posters, cards, carousel, accordion, steps, icons
src/lib/data/                    events and venues
src/lib/basket.svelte.ts         the basket and the booking, kept in session storage
src/lib/codes.ts                 access and promo codes
src/lib/styles/                  tokens, base, components, layout and page styles
nginx.conf                       the Docker image's web server settings
```
