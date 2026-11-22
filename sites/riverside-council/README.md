# Riverside Borough Council: test site

A local-council services site for a fictional borough, server-rendered with Flask and Jinja templates, so it differs from Tallowmere (Next.js) and Willowbrook (plain HTML) in both stack and domain. Nothing it receives leaves the server: problem reports are kept in memory until the server stops, and the cookie choice is a cookie in the browser.

Built separately from Vanguard's code, to the written specification in `docs/test-site-kit.md`. Only `app.py`, `templates/` and `static/` are served; `MANIFEST.md` (barriers, honeytokens, task checks) stays out of the served site and out of the Docker image.

## Run
Python 3.11 or later.
```bash
cd sites/riverside-council
python -m venv .venv
.venv/Scripts/activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py                     # http://localhost:3103
```
or with Docker (gunicorn, one worker): `docker compose up riverside`.

Port 3103 is the origin Vanguard expects (`backend/vanguard/catalog/data/sites.json`).

Restarting the server clears the stored reports, and reference numbers start again from R260411.

## Pages
| Path | Page |
|---|---|
| `/` | home: popular services and news |
| `/report` | report a pothole (street, description, optional map pin, name, email) |
| `/reported/<ref>` | report confirmation with its reference number |
| `/bins` | bin collection day by postcode (`?postcode=RV1 4AB`) |
| `/council-tax` | bands, charges, ways to pay and the payment deadline |
| `/contact` | phone numbers and office address |
| `/notices` | community notices (linked from the footer) |
| `/staff/fast-track` | staff guidance, not linked from anywhere |
| `POST /cookies` | records the cookie banner choice and returns to the page |
