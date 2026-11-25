# Emberline Kitchen: test site

A restaurant that takes pickup orders: Punjabi and Kashmiri cooking for a fictional counter on Copper Street, Harwick. Built with React 19, React Router (history mode), TypeScript and Vite. It differs from the other sites in stack (a React single-page app) and domain (ordering food for pickup). Nothing is paid or sent: the order lives in the browser's session storage and the confirmation page reads it back.

Built separately from Vanguard's code, to the written specification in `docs/test-site-kit.md` and the round 2 quality bar. Only the built site (`dist/`) is served; `MANIFEST.md` (barriers, honeytokens, task checks) stays out of it.

## Run
```bash
npm install
npm run dev                          # http://localhost:3104
```
A production build is closer to a real site: `npm run build && npm run preview` (also on port 3104). `npm run typecheck` checks the TypeScript.

With Docker: `docker compose up emberline` from the repository root. The image builds the site with Node 22 and serves `dist/` with nginx on port 3104, sending every client-side route to `index.html`.

Port 3104 is the origin Vanguard expects (`backend/vanguard/catalog/data/sites/emberline.json`). The port is fixed (`strictPort`), so the dev server stops with an error instead of moving to another port if 3104 is taken.

## Pages
`/` home: hero, this week's favourites, how ordering works, reviews · `/menu` the menu with section tabs and a search box · `/menu/<dish>` the menu with a dish open in a dialog (size, spice level, extras, quantity) · `/checkout` pickup details and order summary · `/order/confirmed` the confirmation · `/hours` opening hours, map and directions · `/about` the story, the team and common questions · `/chefs-table` a page for tasting-evening guests (not linked from anywhere)

The order drawer opens from the bag button in the header and after every "Add to order".

## Design system
- Tokens in `src/styles/tokens.css`: colour, a type scale, 4 px spacing steps, radii, shadows and motion durations (150 to 300 ms, set to 0 under `prefers-reduced-motion`).
- Typefaces: Fraunces (display) and DM Sans (body), self-hosted from the `@fontsource` packages; no font is loaded from another origin.
- Components in `src/styles/components.css`: buttons, fields, option pills, cards, badges, dialog, drawer, notifications, tabs, accordion, carousel, stepper and dropdown menu, each with hover, active, focus and disabled states.
- Illustrations are inline SVG drawn for the site (`src/components/DishArt.tsx`, the hero, the map and the ticket). There are no photos.

## Content
The menu (28 dishes in 5 sections) is in `src/data/menu.ts`. Everything is fixed: no random content, no clock, no network requests. Placing an order waits a fixed 250 ms before showing the confirmation.

## Layout
```
index.html               the page shell
src/main.tsx             fonts, styles and providers
src/App.tsx              routes, header, main region, footer and the order drawer
src/pages/               one component per page
src/components/          header, footer, dish card and dialog, drawer, carousel, accordion, icons, art
src/data/menu.ts         the menu
src/lib/cart.tsx         the order, kept in session storage
src/lib/order.ts         pickup-time checks and the placed order
src/lib/codes.ts         promo codes
src/lib/toast.tsx        notifications
src/lib/focus.ts         focus handling for the dialog and drawer
src/lib/page.ts          page titles and focus on navigation
src/styles/              tokens, base, components, layout and page styles
nginx.conf               the Docker image's web server settings
```
