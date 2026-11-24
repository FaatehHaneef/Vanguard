# Pantry Notes: test site

A recipe site for a fictional home kitchen, server-rendered with **Django** templates, so it differs from the other test sites in stack (Riverside is Flask; Harbour Herald is a static Astro site) and domain. It has no database: the shopping list is kept in a signed session cookie, and submitted recipes are kept in memory until the server restarts. Nothing is sent anywhere.

Built separately from Vanguard's code, to the written specification in `docs/test-site-kit.md` and `docs/tasks-A3-round2.md` Section 0.7. Only the Django app is served; `MANIFEST.md` (barriers, honeytokens, task checks) stays out of the served site and out of the Docker image.

## Run
Python 3.12 or later.
```bash
cd sites/pantry-notes
python -m venv .venv
.venv/Scripts/activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python manage.py runserver        # http://localhost:3107
```
or with Docker (gunicorn, one worker): `docker compose up pantry`.

Port 3107 is the origin Vanguard expects (`backend/vanguard/catalog/data/sites/pantry.json`). Restarting the server clears submitted recipes, and submission numbers start again from 1042.

## Pages
| Path | Page |
|---|---|
| `/` | home: hero with search, this week's favourites, cuisines, quick recipes |
| `/recipes/` | all 24 recipes, with search (`q`), cuisine, time and diet filters, and sorting (`sort`) |
| `/recipes/<slug>/` | a recipe: ingredients scaled with a servings stepper (`?servings=`), method, add to shopping list |
| `/list/` | the shopping list, grouped by recipe; remove one recipe or clear the list (with a confirmation dialog) |
| `/submit/` | submit a recipe, with validation |
| `/submit/thanks/<number>/` | confirmation of a submitted recipe |
| `/about/` | about the site, with questions in an accordion |
| `/club/` | a page for supper club members, not linked from anywhere |

## Design
CSS custom properties for colour, spacing and the type scale (`recipes/static/recipes/css/base.css`); DM Serif Display for headings and Nunito Sans for text, self-hosted (the font files and their SIL Open Font Licences are in `recipes/static/recipes/fonts/`); illustrations are SVG drawn for the site (`recipes/art.py`). Components: a sticky header, a slide-in menu on phones, a stepper, a modal dialog, toasts, a dropdown and an accordion. Transitions are 150 to 250 ms and are switched off under `prefers-reduced-motion`.

## Content
Recipes are in `recipes/data.py`. Static files are served by Django itself (`pantry/urls.py`), so one process serves the whole site.
