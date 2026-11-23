# A3 round 2: tasks for Faateh, Abdul Hadi and Ibrahim Malik

**This is the current task file.** `docs/tasks-A3.md` (round 1) is finished and outdated; do not follow it.

Written so that a person, or a coding agent working for them, can follow it from a clone without guessing. Read Section 0 completely, then do only **your own section**, in order, step by step. Every step names the files you may touch, what to build, how to check it, and the commit to make.

Deadline: **everything pushed by Friday 27 November 2026, 12:00 (Pakistan time)**. Saturday 28 November is a backup day only; plan no work for it.

---

## 0. For everyone

### 0.1 What Vanguard is (two minutes)
Vanguard runs AI "simulated users" (personas such as Knock, a keyboard-only shopper) through real websites in a real browser, keeps each persona inside its limits with code (an action gate, bounded perception, a verifier), and audits every step with a deterministic checker. An LLM proposes actions and writes explanations; **code decides leakage, counts and scores**. The instructor's feedback on 2026-11-22 asked for more product (configurable personas, sites and tasks, a trace viewer, usability findings, comparisons) and a fuller evaluation (task level, all four enforcement methods, the verifier against human labels), with **60 to 75% of the full product implemented for A3**. This round does that.

### 0.2 Read first, in this order
1. `CONTRIBUTING.md`: the working rules.
2. This file, Section 0 completely, then your own section.
3. `README.md`, then `Vanguard.md` Sections 1, 3, 4 and 6.
4. `docs/leakage-spec.md`: limits L1 to L4, personas, rules, honeytokens.
5. `docs/test-site-kit.md` and Section 0.7 below (the round 2 quality bar) if your section includes websites.
6. `docs/labelling-guide.md` before you label.
7. Worked examples: `sites/willowbrook-clinic/` (with `MANIFEST.md`), `sites/northgate-library/`, `sites/riverside-council/`, `apps/tallowmere/`.

### 0.3 Hard rules (not optional)
1. **Branches.** Work only on your own branches, named in your section. Never commit to, push to or merge into `main`. Never delete a branch. Faateh merges.
2. **Identity.** Commit under your own GitHub account and git identity. No AI attribution anywhere: no `Co-Authored-By`, "Generated with ...", or similar lines in commits, pull requests or files. Declare your AI tool use in your own row of `AI_USE.md`.
3. **Commits.** Small conventional commits, one per step (or per item where a step says so): `feat(scope): ...`, `fix`, `test`, `docs`, `style`, `chore`. Expect 25 to 35 commits each.
4. **Ownership.** Edit only files in your rows of the ownership map (Section 0.5). If you need a change in someone else's file, stop that step and ask that person.
5. **Checkpoints.** Before every step marked **⛔ CHECKPOINT**, follow the protocol in Section 0.4. Never work around a missing checkpoint.
6. **Secrets.** Gemini keys live only in your local `.env`. Never commit `.env`, never paste a key into code, docs, logs, chat or commit messages.
7. **Model budget** (for anyone running real model calls):
   - at most **80 model calls a day** for Hadi and for Ibrahim (4 keys × 20); Faateh's runs are planned separately;
   - check usage before each batch: `python -m vanguard.cli usage` (after checkpoint CP-G2);
   - always pass `--max-calls` to `vanguard.cli batch`, set to what you have left today;
   - one run at a time, `--max-steps 12`, short tasks only;
   - if a batch stops with "model unavailable", stop model work for that day. No retry loops.
8. **Labelling** is done by the person, by hand, alone, in the browser. A coding agent must never label, suggest labels or read another person's labels. Do not discuss items until both of you have pushed your labels.
9. **Websites** contain nothing about Vanguard, AI agents, tests, personas, barriers, honeytokens or tasks in anything they serve (text, HTML comments, class names, file names, JavaScript). Barriers and honeytokens are described only in the site's `MANIFEST.md` and catalog file. No external requests: no CDNs, no Google Fonts links, no remote images, no analytics.
10. **Contracts.** Do not change `backend/vanguard/contracts/` or `docs/leakage-spec.md`. If you think one needs to change, ask Faateh.
11. **Before every push:** `cd backend && ruff format . && ruff check . && pytest -q`; if you touched `apps/web`: `cd apps/web && npm run typecheck && npm run lint`; if you touched a site: `python -m vanguard.cli check-site <id> --dir <folder> --live`.
12. **Pushes.** Push a mid-week checkpoint on **Wednesday night** and the final work by **Friday 12:00**. Then tell Faateh which branches are ready.

### 0.4 Checkpoint protocol
Some steps need work that someone else is building. Each such step starts with **⛔ CHECKPOINT CP-xx**. Checkpoint markers are files in `docs/checkpoints/` **on `origin/main`**, and only Faateh adds them (when the work is merged).

Before a checkpoint step:
```bash
git fetch origin
git ls-tree --name-only origin/main docs/checkpoints/
```
- **If `docs/checkpoints/CP-xx.md` is listed:** bring it into your branch with `git merge origin/main` (resolve nothing in files you do not own; if a conflict appears in someone else's file, stop and ask Faateh), read `docs/checkpoints/CP-xx.md` (it says what is now available), then do the step.
- **If it is not listed:** do **not** start the step and do not build a substitute. Tell your human, word for word: *"Checkpoint CP-xx is not on origin/main yet. Please ask <owner> to finish <what it is>."* Then continue with the next step in your section that is not blocked (each section lists what can run while you wait). Check again later.

| Checkpoint | What it makes available | Owner | Expected |
|---|---|---|---|
| **CP-G1** | Groundwork: per-site catalog files, extra task files, per-site Compose files, the 4 new site folders, allowed origins and Docker routing from the catalog, the API route folder, the studio catalog hook, `Task.scenario`, the comparison API | Faateh | Tue afternoon |
| **CP-G2** | Several actions per model call; `StepRecord.call` and `StepRecord.in_call`; the `usage` command; `--max-calls` on batches | Faateh | Tue night |
| **CP-B2** | Labelling bundle 2 (harder steps, including information leaks) at `data/labelling/a3-b2/` | Faateh | Thu morning |
| **CP-VB** | The verifier-run labelling bundle at `data/labelling/verifier-a3/` (from Hadi's runs) | Hadi, merged by Faateh | Thu afternoon |
| **CP-LB** | Both labellers' files for bundle 2 and the verifier bundle merged | Hadi and Ibrahim, merged by Faateh | Fri morning |
| **CP-IM** | Ibrahim's metrics (repeated attempts, calls) merged | Ibrahim, merged by Faateh | Wed night |

### 0.5 Ownership map
| Owner | May create and edit |
|---|---|
| **Faateh** | everything not listed below, including `backend/vanguard/{agent,executor,gate,rules,checker,providers,store,contracts,catalog/__init__.py,catalog/data/personas}`, `backend/vanguard/{failures,results,batch,cli,api}.py`, `backend/vanguard/findings/`, `backend/vanguard/routes/{trace,compare,live}.py`, the web app except Hadi's folders, `apps/hud/`, the four existing sites and their catalog files (`apps/tallowmere/`, `sites/willowbrook-clinic/`, `sites/northgate-library/`, `sites/riverside-council/`, `catalog/data/sites/{tallowmere,willowbrook,northgate,riverside}.json`), `docker-compose.yml`, `docs/` except the files below |
| **Abdul Hadi** | `backend/vanguard/studio/`, `backend/vanguard/routes/studio.py`, `backend/tests/test_studio*.py`, `apps/web/app/studio/`, `apps/web/components/studio/`, `apps/web/app/compare/`, `apps/web/components/compare/`, `sites/emberline-kitchen/`, `sites/marquee-tickets/`, `backend/vanguard/catalog/data/sites/{emberline,marquee}.json`, `data/labelling/verifier-a3/`, `data/labels/hadi-*.json`, `docs/proposal/sections/studio.md`, his row in `AI_USE.md` |
| **Ibrahim Malik** | `backend/vanguard/evaluation/`, `backend/vanguard/metrics/` (this round), `backend/vanguard/routes/evaluation.py`, `backend/tests/test_evaluation*.py`, `backend/tests/test_metrics*.py`, `backend/vanguard/catalog/data/tasks/a3-suite.json`, `sites/harbour-herald/`, `sites/pantry-notes/`, `backend/vanguard/catalog/data/sites/{herald,pantry}.json`, `docs/results/{task-level,realism,diversity,verifier,functional-tests}.md`, `data/labels/ibrahim-*.json`, `docs/proposal/sections/evaluation.md`, his row in `AI_USE.md` |

Never edit: `CLAUDE.md` (local only), anything in someone else's row, `.env.example` (ask Faateh to add a setting).

### 0.6 Setup (Windows; same commands with `/` on macOS or Linux)
```bash
git clone https://github.com/FaatehHaneef/Vanguard.git && cd Vanguard
git config user.name "<your GitHub username>"; git config user.email "<your GitHub email>"
cd backend && python -m venv .venv && .venv/Scripts/activate
pip install -e ".[dev,worker]" && python -m playwright install chromium && pytest -q && cd ..
cp .env.example .env
cd apps/web && npm install && cd ../..
```
In `.env` set: `VANGUARD_DATABASE_URL=sqlite:///<absolute path to repo>/backend/vanguard-dev.db`, `VANGUARD_DATA_DIR=<a local folder outside the repo>`, `VANGUARD_GEMINI_MODELS=["gemini-3.6-flash"]`, and, if you run model calls, `VANGUARD_GEMINI_API_KEYS=["key1","key2","key3","key4"]` (your own keys; use at most four a day).

Running Vanguard locally: API `cd backend && uvicorn vanguard.api:app --port 8000`; web `cd apps/web && npm run dev` (http://localhost:3000); each site as its README says.

### 0.7 Round 2 website quality bar
The sites must look like websites people actually use today, not stubs. On top of `docs/test-site-kit.md`:
- **Design system:** CSS custom properties for colour, spacing and a type scale; one display and one body typeface, **self-hosted** (for example an `@fontsource/*` npm package; never a Google Fonts link); consistent buttons, inputs, cards and states (hover, active, focus, disabled).
- **Modern layout and components:** a hero section, a responsive card grid, a sticky header with navigation, a footer, and at least three of: modal dialog, slide-in drawer, toast notification, tabs, accordion, carousel, dropdown menu, stepper.
- **Motion:** short transitions (150 to 300 ms) on hover, press, open and close; nothing that loops forever; respect `prefers-reduced-motion`.
- **Imagery:** your own SVG illustrations or CSS art, stored in the site; no stock photos from the web.
- **Size and content:** 6 to 10 pages; at least 20 believable records where there is a list; full sentences.
- **Determinism:** no random content, no time-dependent behaviour; any loading state has a fixed short delay (≤ 300 ms).
- **Accessible except the planted barriers**, as in the kit. Prefer barriers that modern sites really have: a custom dropdown built from `div`s, an icon-only button with no name, a toast that disappears before it can be read, a modal that does not trap or restore focus, a hover-only menu, a drag-only slider, infinite scroll with no "load more", status shown only by colour.
- **Tasks:** 3 or 4, each with a deterministic success check and a `scenario` (Section 0.8). An efficient person finishes each in at most 10 actions. At least one task involves recovering from an error (for example a form that rejects a first attempt with a clear message).
- **Engineering:** one command to run (README), `docker compose up <service>` works, dependencies pinned, `check-site --live` passes.

### 0.8 Catalog format after CP-G1 (what your site file looks like)
Each site has its own file `backend/vanguard/catalog/data/sites/<site-id>.json`:
```json
{
  "site": {
    "id": "emberline", "name": "Emberline Kitchen", "origin": "http://localhost:3104",
    "kind": "test", "description": "...", "docker_host": "emberline:3104",
    "honeytokens": [{"token": "EK-1234", "rule": "H2b", "limit": "L2", "where": "..."}],
    "site_tokens": ["..."]
  },
  "tasks": [
    {"id": "ek-order-curry", "site_id": "emberline", "scenario": "add_to_cart",
     "instruction": "...", "start_path": "/", "success": {"text_present": "..."},
     "expected": {"keyboard-only": "...", "unrestricted": "success"}}
  ]
}
```
`scenario` is one of `search`, `add_to_cart`, `checkout`, `form`, `recovery`, `information`. `docker_host` is the Compose service name and port, used by Vanguard to reach the site inside Docker. Do not edit `settings.py` or the main `docker-compose.yml`: allowed origins and Docker routing come from these files, and each site's own `compose.yml` is already included.

---

## 1. Faateh (owner, merges, the bulk of the model runs)

**Branches:** the standing branches (`engine`, `app`, `evaluation`, `websites`, `docs`). **Model budget:** 10 keys, about 200 calls a day; plan: Tue ≤ 60, Wed 200, Thu 200, Fri ≤ 140 with 50 kept for the demo.

| Step | Day | Work | Marks |
|---|---|---|---|
| F1 | Tue | **Groundwork:** split `sites.json` into per-site files; load extra tasks from `catalog/data/tasks/*.json`; add `Task.scenario` and `Site.docker_host`; allowed origins and Docker origin rewrites from the catalog; `docker-compose.yml` includes `sites/*/compose.yml`; create the four new site folders with stub `compose.yml` files; `backend/vanguard/routes/` auto-included by the API; the studio hook (catalog also reads `vanguard.studio.source` when it exists); the comparison API `GET /compare`; nav links for Studio and Compare; tests | **CP-G1** |
| F2 | Tue | **Several actions per call:** the model may return several tool calls; each becomes its own step, checked by the gate one by one, stopping at the first refusal or page change; `StepRecord.call`/`in_call`; `vanguard.cli usage`; `batch --max-calls`; tests | **CP-G2** |
| F3 | Wed–Thu | **Live view and trace viewer** (point 8): stream the browser (CDP screencast) to the run page with the characters walking; replay any run step by step: what was perceived, proposed, allowed or refused, and why (rule and message) | |
| F4 | Wed–Thu | **Findings report and failure attribution** (points 7, 9, 17): inaccessible controls, navigation failures, repeated actions, failed tasks; each failure attributed to site, agent or restriction using the control run and the barrier manifests; the limits statement on every report. Uses CP-IM when available | waits for CP-IM for the final metric |
| F5 | Wed | **Four-method comparison** (point 11): prompt-only, gate, bounded perception, verifier; same agent, same short tasks; Knock and Cog; 3 repeats | |
| F6 | Thu | **Twin runs** (point 6): each persona with and without its restrictions on the same tasks; comparison | |
| F7 | Tue–Fri | **Upgrade the four existing sites** to the Section 0.7 bar, keeping barriers, honeytokens, URLs and every text a success check uses; keep the old versions for the version comparison (point 16) | |
| F8 | Thu | **Labelling bundle 2** from Wednesday's runs, including bounded-perception and honeytoken steps | **CP-B2** |
| F9 | daily | Merge pushed branches, add checkpoint markers, keep CI green | CP-VB, CP-LB, CP-IM |
| F10 | Fri | Version comparison runs; regenerate all results; rewrite the proposal for all twenty feedback points (with the database design and the A3/A4 split, integrating `docs/proposal/sections/*.md`); slides; rehearsal | |

---

## 2. Abdul Hadi: configuration studio, comparison UI, two sites, verifier runs

**Branches:** `feat/configuration-studio` (product work: steps H1 to H14) and `feat/sites-emberline-marquee` (websites: steps S1 to S12). **Model budget:** your own keys, at most 4 a day (80 calls), Wednesday to Thursday.

**Why this matters (instructor's points 14, 15, 16, 12):** users must be able to create, edit and save their own personas, add any website and define tasks without code changes, compare results across runs or website versions, and the verifier must be measured against human labels.

### 2A. Product (branch `feat/configuration-studio`)
**H1. Branch.** `git switch -c feat/configuration-studio` then `git push -u origin feat/configuration-studio`. (Do Section 0.6 setup first.)

**H2. ⛔ CHECKPOINT CP-G1.** While waiting, start the website steps S1 to S6 on the other branch.

**H3. Storage models.** Create `backend/vanguard/studio/__init__.py` and `backend/vanguard/studio/models.py`: SQLAlchemy tables on `vanguard.store.Base`: `custom_personas`, `custom_sites`, `custom_tasks`, each with `id` (string primary key), `data` (JSON holding the exact contract shape: `PersonaSpec`, `Site`, `Task`), `created_at`, `updated_at`. Every write validates `data` with the contract model before saving. Ids are generated as `custom-<slug>-<4 hex>` and must never equal a built-in id.
Commit: `feat(studio): add storage for custom personas, sites and tasks`

**H4. Repository functions.** `backend/vanguard/studio/repository.py`: `list_personas`, `get_persona`, `save_persona`, `delete_persona`, and the same for sites and tasks, using `RunStore`'s session (`store._session()`). Deleting a site also deletes its custom tasks. A custom task's `site_id` must exist (built-in or custom).
Commit: `feat(studio): add repository functions for custom items`

**H5. Catalog source.** `backend/vanguard/studio/source.py`, the hook CP-G1 defined: functions `personas() -> dict[str, PersonaSpec]`, `sites() -> dict[str, Site]`, `tasks() -> dict[str, Task]` that read the saved custom items (no caching: edits must appear at once). After this, custom personas, sites and tasks appear in the lobby, the site picker, runs, the checker and the results without any other change. Custom personas are always `status: "full"` only if they use limits L1 to L4 exactly as defined in `docs/leakage-spec.md`; otherwise save them as `"preview"`.
Commit: `feat(studio): expose custom items through the catalog hook`

**H6. API.** `backend/vanguard/routes/studio.py` with `router = APIRouter(prefix="/studio")`: `GET/POST /studio/personas`, `GET/PUT/DELETE /studio/personas/{id}`, the same for `/studio/sites` and `/studio/tasks`. Validation errors return 422 with the contract's message. A custom site's origin must be `http://` or `https://` with a host; it is added to the allowed origins automatically by the catalog (CP-G1). Built-in items are read-only: editing one returns 409 with "copy it first".
Commit: `feat(studio): add the studio API`

**H7. Tests.** `backend/tests/test_studio.py`: create, edit, list and delete each kind; validation errors; built-ins are read-only; a custom persona appears in `catalog.personas()`; a custom task on a custom site can be started as a run with the fake provider and fake executor (see `backend/tests/test_api.py` for the pattern).
Commit: `test(studio): cover custom personas, sites and tasks`

**H8. Persona builder UI.** `apps/web/app/studio/personas/` (list, new, edit pages) and components in `apps/web/components/studio/`. Fields: name; character (one of the five sprites); represents (one line); description (what the model is told); limits (checkboxes L1 to L4 with the plain-language meaning from the spec); perception (full, accessibility tree, magnified); permitted tool groups (keyboard, pointer, screen reader, magnifier, navigation, control); magnification (when magnified); knows / does-not-know lists. "Duplicate" on a built-in persona creates an editable copy. Show a live preview with the sprite. Use the existing visual style (`apps/web/app/globals.css`, `pixel-panel`, `pixel-button`) and the API client pattern in `apps/web/lib/api.ts` (add your calls in a new `apps/web/lib/studio.ts`, not in `api.ts`).
Commits: `feat(web): add the persona list`, `feat(web): add the persona editor`, `feat(web): duplicate built-in personas`

**H9. Site and task editor UI.** `apps/web/app/studio/sites/`: add a site (name, URL, description; a clear note that only sites you own or are allowed to test may be added); per site, tasks with instruction, start path, scenario and success check (one of: URL starts with, text appears on the page, answer contains). Validate URLs client-side and show the server's errors.
Commits: `feat(web): add the site editor`, `feat(web): add the task editor`

**H10. Check it end to end.** Create a persona, a site pointing to one of the test sites, and a task; start a trial from the lobby with the **fake** model; confirm it runs and shows on the results page. Fix anything broken in your files; if the problem is in Faateh's files, stop and tell Faateh.
Commit (if fixes): `fix(studio): ...`

**H11. Comparison report UI.** ⛔ **CHECKPOINT CP-G1** (the comparison API). `apps/web/app/compare/` and `apps/web/components/compare/`: choose a baseline and a candidate batch (`GET /batches`), call `GET /compare?baseline=<id>&candidate=<id>` (shape in `docs/checkpoints/CP-G1.md`), and show per persona/task/method group: success, runs with a leak, steps, repeated attempts and failures, with the change marked (better, worse, same), plus "new failures" and "resolved failures" lists linking to `/runs/<id>`. This is how a team sees whether a site change introduced new problems.
Commits: `feat(web): add the comparison page`, `feat(web): show new and resolved failures`

**H12. Verifier runs.** ⛔ **CHECKPOINT CP-G2**. Wednesday and Thursday, at most 80 calls a day (the verifier makes about two calls per step). Start the test sites `tallowmere` and `willowbrook` locally (READMEs), then:
```bash
cd backend
python -m vanguard.cli usage
python -m vanguard.cli batch --site tallowmere --tasks cheapest --personas keyboard-only unrestricted \
  --enforcements verifier --repeats 3 --max-steps 12 --max-calls <left today> --batch verifier-a3-tm
python -m vanguard.cli batch --site willowbrook --tasks wb-callback --personas keyboard-only unrestricted \
  --enforcements verifier --repeats 3 --max-steps 12 --max-calls <left today> --batch verifier-a3-wb
```
Run what fits today; the batches resume tomorrow with the same command.
Commit: none (runs live in your local database).

**H13. Verifier bundle.** When both batches are complete:
```bash
python -m vanguard.cli labelling export --batches verifier-a3-tm verifier-a3-wb --name verifier-a3 --count 60
```
Commit `data/labelling/verifier-a3/` and push. Tell Faateh (he merges it and adds CP-VB).
Commit: `chore(labels): add the verifier-run labelling bundle`

**H14. Labelling.** ⛔ **CHECKPOINT CP-B2** and ⛔ **CHECKPOINT CP-VB**. Follow `docs/labelling-guide.md`. You label **personally**:
```bash
python -m vanguard.cli labelling import data/labelling/a3-b2
python -m vanguard.cli labelling import data/labelling/verifier-a3
```
Label at http://localhost:3000/labelling?batch=label-a3-b2 and ?batch=label-verifier-a3 with labeller name `hadi`. Then export each: `python -m vanguard.cli labelling export-labels --labeller hadi` writes `data/labels/hadi.json`; rename it to `data/labels/hadi-a3-b2.json` after the first bundle and `hadi-verifier-a3.json` after the second (export once per bundle, after labelling that bundle only).
Commits: `chore(labels): add my labels for bundle 2`, `chore(labels): add my labels for the verifier bundle`

**H15. Write-up and declaration.** `docs/proposal/sections/studio.md` (one page: what the studio does, the data model of the three tables, how custom items reach the catalog, validation and safety), and your row in `AI_USE.md`.
Commits: `docs(studio): describe the configuration studio`, `docs(ai-use): declare my AI tool use for round 2`

**What can run while you wait:** before CP-G1, the website steps S1 to S6; before CP-G2, H8 to H11; before CP-B2 or CP-VB, the website steps.

### 2B. Websites (branch `feat/sites-emberline-marquee`)
**S1. Branch.** `git switch main && git switch -c feat/sites-emberline-marquee` then push it.

**Emberline Kitchen** (`sites/emberline-kitchen/`, id `emberline`, port **3104**, **React + Vite + TypeScript**, a restaurant that takes pickup orders): home with hero and featured dishes; full menu with category tabs and a search box; dish detail in a modal with options (size, spice level, extras); cart drawer; checkout (name, phone, pickup time) with a confirmation page; opening hours and location page; about page.
- **S2.** Scaffold and design system (tokens, self-hosted fonts, base components). Commit: `chore(emberline): scaffold the site and its design system`
- **S3.** Pages and menu data (at least 24 dishes in 5 categories). Commits: `feat(emberline): add the home page and menu`, `feat(emberline): add dish details and options`
- **S4.** Cart drawer, checkout and confirmation, with one recoverable error (for example a pickup time outside opening hours, rejected with a clear message). Commit: `feat(emberline): add the cart and checkout`
- **S5.** Barriers, one per limit, modern patterns, and three honeytokens (L2, L3, L4) per Section 0.7; write each into `MANIFEST.md` as you add it. Commits: `feat(emberline): ...` one per barrier, one per honeytoken (describe the feature, never the barrier, in the message)
- **S6.** `README.md`, `MANIFEST.md`, `Dockerfile` (build, then serve `dist/` with nginx on 3104 and an SPA fallback). Commit: `docs(emberline): add the README and manifest`, `chore(emberline): add the Dockerfile`

**Marquee Tickets** (`sites/marquee-tickets/`, id `marquee`, port **3105**, **SvelteKit** with the static adapter, an events and ticketing site): home with upcoming events carousel; event listing with filters (date, venue, genre) and search; event page with ticket type and quantity; basket and checkout with a confirmation; venue pages; FAQ with an accordion.
- **S7 to S11.** Same pattern as S2 to S6 (scaffold and design system; listing and event pages with at least 24 events; basket, checkout and one recoverable error such as "maximum 6 tickets per order"; barriers and honeytokens; README, MANIFEST, Dockerfile). Commits in the same style with scope `marquee`.

**S12. ⛔ CHECKPOINT CP-G1. Register both sites.** Create `backend/vanguard/catalog/data/sites/emberline.json` and `marquee.json` (format in Section 0.8, `docker_host` `emberline:3104` / `marquee:3105`), each with 3 or 4 tasks whose scenarios cover `search`, `add_to_cart`, `checkout` and `recovery` between them. Fill the site's `compose.yml` (stub already created) with one service named after the site id, built from the site's folder, port `"3104:3104"` / `"3105:3105"`. Run `check-site --live` for both and fix until every check passes; try every task yourself with a mouse and with the keyboard only and confirm the manifest.
Commits: `feat(catalog): register Emberline Kitchen and its tasks`, `feat(catalog): register Marquee Tickets and its tasks`, `chore(docker): add the Emberline and Marquee services`

---

## 3. Ibrahim Malik: task-level evaluation, metrics, verifier evaluation, two sites

**Branches:** `feat/task-level-evaluation` (steps E1 to E14) and `feat/sites-herald-pantry` (steps S1 to S12). **Model budget:** your own keys, at most 4 a day (80 calls), Wednesday to Thursday.

**Why this matters (instructor's points 4, 5, 10, 12, 13):** single steps do not show whole failures, so tasks must be evaluated as tasks across scenarios; behaviour must be compared with real users, not only with the rules; diversity must be measured; the verifier's precision, recall and false-positive rate must be measured against human labels; and completion, actions, repeated attempts, latency and cost must be reported.

### 3A. Evaluation (branch `feat/task-level-evaluation`)
**E1. Branch.** `git switch -c feat/task-level-evaluation` then push. (Section 0.6 setup first.)

**E2. Package and command.** `backend/vanguard/evaluation/__init__.py` and `backend/vanguard/evaluation/__main__.py`, giving `python -m vanguard.evaluation <command>` with subcommands added in later steps. Do not edit `vanguard/cli.py`.
Commit: `chore(evaluation): add the evaluation package and command`

**E3. Repeated attempts.** In `backend/vanguard/metrics/` (yours this round): a function `repeated_attempts(steps) -> int` counting proposals that repeat the previous proposal (same tool and same key, ref, text or URL) without any change in URL or focus, plus proposals that repeat an action the gate just refused. Add `repeated_attempts: int = 0` to `RunMetrics` and to the group metrics (mean per run). Tests with hand-made step records.
Commits: `feat(metrics): count repeated attempts`, `test(metrics): cover repeated attempts`

**E4. ⛔ CHECKPOINT CP-G2. Calls vs actions.** With `StepRecord.call` available, add `model_calls` (distinct calls) and `actions` (steps) to `RunMetrics` and the groups. Tests.
Commits: `feat(metrics): report model calls and actions separately`, `test(metrics): cover calls and actions`
Push this branch now and tell Faateh: CP-IM depends on it.

**E5. ⛔ CHECKPOINT CP-G1. Task suite.** `backend/vanguard/catalog/data/tasks/a3-suite.json` with `{"tasks": [...]}` (Section 0.8 task format, each with a `scenario`) defining short tasks on the **existing** sites for the scenarios they do not yet cover: a search task on Northgate (for example "Find who wrote *The Remains of the Day*"), an add-to-cart task on Tallowmere ("Add one Moss Path candle to the cart", success: the cart shows it), a recovery task on Riverside (submitting the pothole report with a missing field first, then fixing it), and an information task on Willowbrook. Plus the tasks of your own two sites (step S12). Use only texts and paths that exist today; Faateh's site upgrades keep them. Read each site's `MANIFEST.md` for its structure.
Commit: `feat(evaluation): define the A3 task suite`

**E6. Task-level scoring.** `backend/vanguard/evaluation/tasks.py` and a subcommand `python -m vanguard.evaluation task-report --batches <ids...>`: per task and per scenario, over runs: completion rate (with Wilson interval), mean actions, mean model calls, repeated attempts, refusals, stuck rate, step-limit rate, latency p50/p95, cost, and the failure cause (from `vanguard.failures`). Writes `docs/results/task-level.md`. Tests.
Commits: `feat(evaluation): score runs at task level`, `test(evaluation): cover task-level scoring`

**E7. Realism.** `backend/vanguard/evaluation/realism.py` and `python -m vanguard.evaluation realism --batches <ids...>`: each persona's input profile (pointer share of actions, Tab and arrow share of key presses, Enter share) compared with the matching A11y-CUA group from `vanguard.reference.a11y_cua` (keyboard-only vs blind and low-vision users, unrestricted vs sighted users): the values side by side and the absolute differences, with a note that A11y-CUA tasks were desktop tasks. Writes `docs/results/realism.md`. Tests with a small fake dataset folder, as in `backend/tests/test_reference.py`.
Commits: `feat(evaluation): compare personas with real users' input profiles`, `test(evaluation): cover realism`

**E8. Diversity.** `backend/vanguard/evaluation/diversity.py` and `python -m vanguard.evaluation diversity --batches <ids...>`: (a) normalised edit distance between the sequences of action types, within a persona across runs and between personas; (b) Shannon entropy of the action-type mix (use `vanguard.metrics.stats.entropy_bits`); (c) spread (standard deviation and interquartile range) of actions and completion across runs and personas; (d) the set of distinct navigation paths (sequence of URL paths) per persona. Writes `docs/results/diversity.md`. Tests.
Commits: `feat(evaluation): measure behavioural diversity`, `test(evaluation): cover diversity`

**E9. Task-suite runs.** ⛔ **CHECKPOINT CP-G2**. Wednesday and Thursday, at most 80 calls a day. Start the sites the suite uses, then for each suite task:
```bash
cd backend
python -m vanguard.cli usage
python -m vanguard.cli batch --site <site> --tasks <suite task ids on that site> \
  --personas keyboard-only unrestricted --enforcements gate --repeats 3 --max-steps 12 \
  --max-calls <left today> --batch suite-a3-<site>
```
Order: Northgate, Tallowmere, Willowbrook, Riverside, then your own sites. Batches resume with the same command the next day.
Commit: none (runs live in your local database).

**E10. Task-level results.** Run E6, E7 and E8 over your `suite-a3-*` batches; commit the generated `docs/results/task-level.md`, `realism.md`, `diversity.md`. Back up your database file (`backend/vanguard-dev.db`) to a folder outside the repo and tell Faateh where it is (he imports it for the final tables).
Commit: `docs(results): add the task-level, realism and diversity results`

**E11. Verifier evaluation.** `backend/vanguard/evaluation/verifier.py` and `python -m vanguard.evaluation verifier-report`: over the steps the verifier judged and that two people labelled, the verifier's precision, recall and **false-positive rate** (valid actions wrongly refused / all valid actions) against (a) the agreed human labels and (b) the hard rules, with the number of steps and the disagreements listed. Tests with hand-made records first; run it on real data after ⛔ **CHECKPOINT CP-LB**. Writes `docs/results/verifier.md`.
Commits: `feat(evaluation): evaluate the verifier against human labels`, `test(evaluation): cover the verifier report`, `docs(results): add the verifier results` (after CP-LB)

**E12. Labelling.** ⛔ **CHECKPOINT CP-B2** and ⛔ **CHECKPOINT CP-VB**. Same as Hadi's H14, with labeller name `ibrahim` and files `data/labels/ibrahim-a3-b2.json` and `ibrahim-verifier-a3.json`. Label personally and alone.
Commits: `chore(labels): add my labels for bundle 2`, `chore(labels): add my labels for the verifier bundle`

**E13. Functional tests (Friday morning).** Re-run the full test suite on your branch after merging `origin/main` and refresh `docs/results/functional-tests.md` the same way as last time.
Commit: `docs(results): refresh the functional test table`

**E14. Write-up and declaration.** `docs/proposal/sections/evaluation.md` (one to two pages: the task-level design and scenarios, each metric's definition, realism, diversity, the verifier evaluation, what each experimental condition changes while the agent and tasks stay fixed), and your row in `AI_USE.md`.
Commits: `docs(evaluation): describe the evaluation design`, `docs(ai-use): declare my AI tool use for round 2`

**What can run while you wait:** before CP-G1, E2 to E3 and the website steps S1 to S6; before CP-G2, E5 to E8 (with tests) and the websites; before CP-B2 or CP-VB, E10, E11 tests, and the websites.

### 3B. Websites (branch `feat/sites-herald-pantry`)
**S1. Branch.** `git switch main && git switch -c feat/sites-herald-pantry` then push.

**Harbour Herald** (`sites/harbour-herald/`, id `herald`, port **3106**, **Astro** static site, a local news site): front page with a lead story and a card grid; section pages (city, business, sport, culture); article pages with related stories; search; a newsletter sign-up in a modal with validation; an events listing; about and contact.
- **S2.** Scaffold and design system. Commit: `chore(herald): scaffold the site and its design system`
- **S3.** Pages and content (at least 24 articles). Commits: `feat(herald): add the front page and sections`, `feat(herald): add article pages and search`
- **S4.** Newsletter sign-up modal with one recoverable error (for example an email already subscribed or a missing consent box). Commit: `feat(herald): add the newsletter sign-up`
- **S5.** Barriers (one per limit, modern patterns) and three honeytokens, each written into `MANIFEST.md`. One commit each, describing the feature.
- **S6.** `README.md`, `MANIFEST.md`, `Dockerfile` (build, serve `dist/` with nginx on 3106). Commits: `docs(herald): add the README and manifest`, `chore(herald): add the Dockerfile`

**Pantry Notes** (`sites/pantry-notes/`, id `pantry`, port **3107**, **Django** with server-rendered templates, a recipe site): home with featured recipes; recipe listing with filters (cuisine, time, diet) and search; recipe pages with ingredients, steps and a servings adjuster; save to a shopping list (stored in the session) and a shopping-list page; a "submit a recipe" form with validation; about.
- **S7 to S11.** Same pattern (scaffold and design system with Django templates and static files; listing and recipe pages with at least 24 recipes; shopping list and the submission form with one recoverable error; barriers and honeytokens; README, MANIFEST, Dockerfile using gunicorn on 3107). Commits in the same style with scope `pantry`.

**S12. ⛔ CHECKPOINT CP-G1. Register both sites.** As Hadi's S12, with `herald.json` and `pantry.json`, `docker_host` `herald:3106` / `pantry:3107`, 3 or 4 tasks each covering `search`, `add_to_cart` (or "save to list"), `form` or `checkout`, and `recovery` between them, the sites' `compose.yml` files, and `check-site --live` passing.
Commits: `feat(catalog): register Harbour Herald and its tasks`, `feat(catalog): register Pantry Notes and its tasks`, `chore(docker): add the Herald and Pantry services`

---

## 4. When you are done
1. All checks in rule 11 pass on each of your branches.
2. Push every branch; the last CI run on each must be green on GitHub.
3. Tell Faateh which branches are ready and anything left unfinished, with the reason. Do not merge anything yourself.
