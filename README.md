# Vanguard

**An audit tool for LLM-simulated users with enforced limits.**

Teams use AI agents as stand-ins for real users, for example "a shopper who only uses a keyboard", to find accessibility and usability problems early. Vanguard runs such simulated users on a website and audits every step: did the simulated user stay within its limits (**leakage**), and did different personas behave differently (**diversity**)? Only results that pass that audit are worth acting on.

Vanguard is early, cheap pre-testing. It does not replace testing with disabled people, and it does not claim to simulate them.

AI-4009 Generative AI term project, FAST-NUCES Islamabad. Track: Pure Product.

## Status
Foundation in place: shared contracts, five personas, the action gate, the agent loop, the trace store and the API, all tested with a fake browser and a scripted model. In progress for Assignment 3: the Playwright executor, the web app, the Tallowmere test site, the leakage checker and the evaluation. See `Vanguard.md` for the full plan.

## Layout
```
backend/            Python core (FastAPI, agent loop, gate, rules, store)
  vanguard/
    contracts/      shared data shapes, used by every module and the frontend
    catalog/        personas, sites and tasks as JSON data
    rules/          hard leakage and safety rules (shared by gate and checker)
    gate/           the action gate
    providers/      model providers (Gemini; local and others in local runs)
    executor/       browser executors (fake now; Playwright next)
    agent/          the simulated-user loop, prompts, success and stuck checks
    store/          append-only trace store
    checker/        leakage checker (interface defined)
    metrics/        run and batch metrics (interface defined)
apps/web/           web app, ported from Sentinel's gamified UI
apps/tallowmere/    standalone test shop, extracted from Sentinel
docs/               leakage specification and project documents
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

With Docker: `docker compose up --build` starts Postgres and the API.

## Tests
```bash
cd backend && pytest -q
```

## Data
Public datasets are kept outside the repository, in the folder named by `VANGUARD_DATA_DIR` (default `D:\VanguardData`). See `Vanguard.md`, Section 4.6a.

## Safety
The agent can only send the browser to allowed origins (rule S0, always enforced), and payments run in the Braintree sandbox only.

## Licence and provenance
See `NOTICE.md`.
