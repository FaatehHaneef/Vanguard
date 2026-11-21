# Vanguard

**An audit tool for LLM-simulated users with enforced limits.**

Teams use AI agents as stand-ins for real users, for example "a shopper who only uses a keyboard", to find accessibility and usability problems early. Vanguard runs such simulated users on a website and audits every step: did the simulated user stay within its limits (**leakage**), and did different personas behave differently (**diversity**)? Only results that pass that audit are worth acting on.

Vanguard is early, cheap pre-testing. It does not replace testing with disabled people, and it does not claim to simulate them.

AI-4009 Generative AI term project, FAST-NUCES Islamabad. Track: Pure Product.

## Status
Working end to end on the Tallowmere test shop:
- a real Chromium browser driven from outside with Playwright (genuine key presses and clicks, trusted-input recording, network allow-list, screenshots), with mobile and slow-network conditions;
- perception per persona: the full view (focus shown only when visible), the accessibility tree with screen-reader commands, and a 400% magnifier window with panning;
- the agent loop with Gemini (or any OpenAI-compatible model in local runs), the action gate, and a verifier agent as a further enforcement option;
- the leakage checker (H1 with browser evidence, H3a, H4a, H4b, and honeytokens planted in Tallowmere), run and group metrics with Wilson intervals, failure grouping by cause, balanced and resumable batches;
- explanations in three modes (template, LLM, LLM with a fact check);
- the web app: lobby, site picker (compare, gate, verifier, bounded perception, conditions), live run view with the character overlay, comparison per trial, a results dashboard, and a blind labelling desk with Cohen's kappa.

Next: the Gemini baseline batches (they need a Gemini key and Braintree sandbox keys in the local env files), labelling, and the A3 write-up. See `Vanguard.md` for the full plan.

## Layout
```
backend/            Python core (FastAPI, agent loop, gate, rules, store)
  vanguard/
    contracts/      shared data shapes, used by every module and the frontend
    catalog/        personas, sites and tasks as JSON data
    rules/          hard leakage and safety rules (shared by gate and checker)
    gate/           the action gate
    providers/      model providers (Gemini; local and others in local runs)
    executor/       Playwright executor, observation and event scripts, screen reader, fake
    agent/          the simulated-user loop, prompts, success and stuck checks
    store/          append-only trace store (runs, steps, batches)
    checker/        leakage checker (same rules as the gate, plus browser evidence)
    metrics/        run and group metrics, Wilson intervals, kappa
    batch.py        balanced, resumable batches
    failures.py     failing runs tagged and grouped by cause
    verifier.py     the verifier agent (enforcement option 4)
    labels.py       blind labelling and agreement
    results.py      scoring stored runs; tables
    explain/        explanation generator (template, LLM, checked LLM)
    cli.py          run, batch, show and report from the command line
apps/web/           web app, ported from Sentinel's gamified UI
apps/hud/           character overlay injected into the test browser (decoration only)
apps/tallowmere/    standalone test shop, extracted from Sentinel
docs/               leakage specification, labelling guide, test-site kit
```

## Run the backend locally
Requires Python 3.11+.
```bash
cd backend
python -m venv .venv
.venv/Scripts/activate        # Windows; on macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
cp ../.env.example ../.env    # then fill in your Gemini key
uvicorn vanguard.api:app --reload
```
API docs: http://localhost:8000/docs

With Docker: `docker compose up --build` starts Postgres, the API (with Playwright and Chromium), the web app and Tallowmere.

For real browser runs outside Docker:
```bash
pip install -e ".[dev,worker]"
python -m playwright install chromium
# in .env: VANGUARD_EXECUTOR=playwright, plus your Gemini key
python -m vanguard.cli run --persona keyboard-only --task buy-two --enforcement gate
python -m vanguard.cli batch --personas keyboard-only unrestricted --tasks buy-two --repeats 5 --batch a3-baseline
python -m vanguard.cli report --batch a3-baseline
```
Run Tallowmere first (`apps/tallowmere`, port 3100). A production build (`npm run build && npm start`) is faster and closer to a real site than `npm run dev`.

## Tests
```bash
cd backend && pytest -q      # the Playwright tests skip if Chromium is not installed
```
CI runs the backend tests with Chromium, and typechecks, lints and builds the web app, the HUD and Tallowmere.

## Data
Public datasets are kept outside the repository, in the folder named by `VANGUARD_DATA_DIR` (default `D:\VanguardData`). See `Vanguard.md`, Section 4.6a.

## Safety
The agent can only send the browser to allowed origins (rule S0, always enforced), and payments run in the Braintree sandbox only.

## Licence and provenance
See `NOTICE.md`.
