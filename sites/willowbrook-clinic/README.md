# Willowbrook Family Clinic: test site

A small appointment-booking site for a fictional family clinic, written in plain HTML, CSS and JavaScript (no framework), so it differs from Tallowmere (Next.js) in both stack and domain. It books nothing real: bookings live in the browser's session storage only.

Built separately from Vanguard's code, to the written specification in `docs/test-site-kit.md`. Only `public/` is served; `MANIFEST.md` (barriers, honeytokens, task checks) stays out of the served site.

## Run
```bash
cd public && python -m http.server 3101      # http://localhost:3101
```
or with Docker: `docker compose up willowbrook`.

Port 3101 is the origin Vanguard expects (`backend/vanguard/catalog/data/sites.json`).

## Pages
`/` home and doctors (opening hours in the footer) · `/book.html` weekly calendar · `/details.html` name and phone · `/confirmed.html` confirmation · `/callback.html` callback request · `/staff.html` (not linked from anywhere)
