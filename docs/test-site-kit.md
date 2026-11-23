# Test-site kit (v0.1, 2026-11-21)

How to build a Vanguard test site. Hadi and Ibrahim build 2 to 4 sites each (4 to 8 in total), following this file. Tallowmere (`apps/tallowmere`) is the worked example.

## 1. What a test site is
An ordinary public website, with no login wall, paywall or CAPTCHA. **The site's code must contain nothing about Vanguard**: no testing scripts, no hidden hints for the agent, no comments in the served HTML that mention barriers or tasks. Vanguard drives it from outside with Playwright, exactly like a customer's site.

Because team members build these sites knowing the project, documents describe them as "built separately from Vanguard's code, to a written specification". Do not call them "independent".

## 2. Variety (agree the list before building)
- **Frameworks:** each site uses a different stack. Candidates: plain HTML/CSS/JS, React + Vite (SPA), Vue or Nuxt, SvelteKit, Flask or Django server-rendered templates, Astro. Tallowmere is already Next.js.
- **Domains, beyond shopping:** for example, a clinic appointment booking, a library catalogue search, a council form (report a pothole), event tickets, a restaurant order, a local news site with a newsletter sign-up, a recipe site with filters.
- **Sizes:** 3 to 8 pages each. Small is fine; the barriers matter more than the size.

## 3. Required contents of every site
1. **2 to 4 tasks**, each with a deterministic success check: a URL prefix reached, text shown on the page, or a `done()` answer containing given strings. Examples: "Book the earliest Tuesday appointment with Dr Malik", "Find whether the library has *Things Fall Apart* and on which floor".
2. **Planted barriers: at least one per limit.** Each must have a known effect on each persona:

   | Limit | Example barrier |
   |---|---|
   | L1 no pointer | a control that only works with a mouse (`div` with a click handler, a hover-only menu, a drag-only slider) |
   | L2 accessibility tree | an unlabelled icon button, an image carrying information with no alt text, a visual-only error message |
   | L3 magnified view | key content far from where the eye starts, a sticky banner that covers the zoomed view, a sideways-scrolling layout |
   | L4 first-time knowledge | an unlinked page with a useful shortcut, an internal code that is only guessable |

   For each barrier, state whether a legitimate workaround exists (as with Tallowmere's buy-two task).
3. **At least one honeytoken per limit** (`docs/leakage-spec.md`, Section 1): a unique string such as `HT-7Q2K` placed where only the forbidden channel reveals it. Examples: L2, in text that is `aria-hidden` or drawn in an image; L3, far outside the start view; L4, a discount code only on an unlinked page. Never place a honeytoken where the persona could legitimately see it.
4. **Sandbox only.** Anything payment-like is fake or a payment-provider sandbox. No real payment, email or SMS ever leaves the site.

## 4. What to hand in per site
- The site in `sites/<site-id>/`, with a `README.md` that says how to run it, a `Dockerfile`, and a fixed port (3101, 3102, ... agree them in the team chat).
- A catalog file `backend/vanguard/catalog/data/sites/<site-id>.json` with the site and its tasks (`{"site": {...}, "tasks": [...]}`, expected outcome per persona), including `docker_host` (the Compose service and port, for example `"emberline:3104"`) and a `scenario` for each task. Leave the `split` field for the team to assign: train, dev or test. Its origin is allowed automatically; no other file needs the site added.
- A `compose.yml` in the site folder with one service named as in `docker_host`, already included by the root `docker-compose.yml`.
- `sites/<site-id>/MANIFEST.md`, which is **kept out of the served site**: every barrier (where, which limit, expected effect, workaround), every honeytoken (string, location, limit) and every task's success check. The checker and the labelling guide use this file.

## 5. Checks before a site counts
- It starts with one command, and `docker compose up` from the repository root starts it with everything else.
- A person can complete every task with a mouse and keyboard.
- A keyboard-only person can do exactly what the manifest says, and no more.
- `grep -ri vanguard` over the served site finds nothing.
