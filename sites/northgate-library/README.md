# Northgate Library: test site

A public library catalogue for a fictional town library, built with Vue 3, Vue Router (history mode) and Vite. It differs from Tallowmere (Next.js) and Willowbrook (plain HTML) in stack and domain: a client-side single-page app where every page is drawn in the browser. It lends nothing real; reservations live in the browser's session storage only.

Built separately from Vanguard's code, to the written specification in `docs/test-site-kit.md`. Only the built site (`dist/`) is served; `MANIFEST.md` (barriers, honeytokens, task checks) stays out of it.

## Run
```bash
npm install
npm run dev                          # http://localhost:3102
```
A production build is faster and closer to a real site: `npm run build && npm run preview` (also on port 3102).

With Docker: `docker compose up northgate` from the repository root. The image builds the site with Node 22 and serves `dist/` with nginx on port 3102, sending every client-side route to `index.html`.

Port 3102 is the origin Vanguard expects (`backend/vanguard/catalog/data/sites.json`). The port is fixed (`strictPort`), so the dev server stops with an error instead of moving to another port if 3102 is taken.

## Pages
`/` home, events and borrowing rules · `/search` catalogue search (`/search?q=...`) · `/book/<id>` book details · `/reserve/<id>` reservation form · `/reserved` confirmation · `/hours` opening hours · `/about` about the library · `/staff-picks` (not linked from anywhere)

The catalogue (27 books) is in `src/data/books.js`.

## Layout
```
index.html          the page shell
src/main.js         starts the app
src/router.js       routes and page titles
src/App.vue         header, navigation, main region and footer
src/views/          one component per page
src/data/books.js   the catalogue
src/reservation.js  reservations in session storage
src/styles.css      the stylesheet
nginx.conf          the Docker image's web server settings
```
