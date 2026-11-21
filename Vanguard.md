# Vanguard: project restatement

An audit tool for LLM-simulated users with enforced limits.
AI-4009 Generative AI term project (FAST-NUCES Islamabad), Pure Product track.

Written 2026-11-21 from three sources: the course documents in `docs/`, the two reference repositories (`sentinel/`, `synthetic-users/`), and the planning notes in `docs/Project Context.md`. A reader who has none of those should still understand the project from this file alone.

**Tags.** Every important claim carries one tag:
- `[doc: file, section]`: stated in a course document.
- `[repo: path]`: read in a reference repository.
- `[context-only]`: from the planning notes only, not confirmed in a document or repository.
- `[unverified]`: not yet checked against a primary source. Do not repeat it in a deliverable until it is checked.

Short document names: **A3** = `AI-4009_Assignment#3.pdf`, **A4** = `Assignment#4.pdf`, **R3** = `Assignment_3_Evaluation_Rubric_Form.pdf`, **R4** = `Assignment_4_Evaluation_Rubric_Form.pdf`, **FP** = `FACET_Sample_Proposal_Pure_Product.pdf`, **FR** = `FACET_Sample_Proposal_RD_Product.pdf`.

---

## 1. What Vanguard is, who it is for, and why

**The problem.** Some product teams and researchers use LLM agents as stand-ins for real users, for example "a shopper who only uses a keyboard", to find usability and accessibility problems before testing with people. Examples include persona-driven usability agents `[Touir et al., CEUR Vol-4249 paper 4, abstract]` and screen-reader-proxy agents for app accessibility `[TaskAudit, arXiv:2510.12972, abstract]`. How widespread the practice is has not been measured here `[unverified]`. Two things make these simulations hard to trust:
- **Leakage.** The simulated user uses an ability or a piece of information that its persona should not have, for example a keyboard-only persona that clicks with a mouse, or a screen-reader persona that reads visual layout `[context-only]`. Published work reports a related tendency: "VLMs tend to infer beyond the specified vision ability when given minimal prompts" `[Natalie et al., arXiv:2508.10972, abstract; checked 2026-11-21]`.
- **Collapse.** A group of supposedly different personas behaves alike. The team's own earlier project measured this. Gemini with ten different personas named only 9 distinct games across 178 answers, and single personas named the same game 18 times out of 18 `[repo: synthetic-users/README.md, results/gemini-main/summary.json]`.

**The product.** Vanguard lets a team:
1. define a simulated user's limits in a structured spec (what it can perceive, how it can act, what it knows);
2. run that simulated user through tasks on a demo online store with a sandbox checkout, recording every step;
3. audit the run: a **leakage report** (steps that used a capability or information outside the spec) and a **diversity report** (how varied a group of simulated users is);
4. compare **four enforcement methods** (prompt-only, code-enforced action gate, bounded perception, verifier agent) on identical tasks;
5. view results on a dashboard and export a report (PDF or email) `[context-only]`.

**Users.** Accessibility and UX engineers in small product teams, and students and researchers who run simulated-user studies `[context-only]`.

**Generative AI techniques and where they are used** `[context-only]`:
- **Agentic tool calling**: the simulated user picks browser actions through tools. This covers the "RAG, fine-tuning or agentic tool calling" requirement `[doc: A3, Section 5]`.
- **Bounded context, retrieval-style**: the model sees only what its user could perceive, selected by code.
- **Structured output**: specs, actions and rationales as validated JSON.
- **Verifier agent**: a second model call checks each proposed action against the spec.
- **Text generation**: the LLM explains findings. All counts and scores are computed by code, never by the model.

Mapped to the A3 Table 4 categories, these are: Foundation models (API, function calling, structured output), Agents and tool use, Structured output and reliability, Prompt engineering, Integrations, and Evaluation and observability. The minimum is three `[doc: A3, Table 4]`.

**Data and integrations** `[context-only]`: Gemini API; browser automation on the demo store with a payments-sandbox checkout (Braintree); the public A11y-CUA dataset (Reduced subset, cc-by-4.0) as reference statistics only, never for training; WebAIM screen reader surveys for persona parameters `[unverified]`; the team's own labelled test set; email delivery of reports.

**Team and course** `[context-only]`. AI-4009 Generative AI, FAST-NUCES Islamabad, Section A. Members (maximum three `[doc: A3, Table 1]`): Syed Muhammad Faateh Haneef, 23i-0688 (GitHub `FaatehHaneef`); Abdul Hadi, 23i-0676; Ibrahim Malik, 23i-0694. TA: Sohaib Sulman, who approved the idea for Pure Product on 2026-11-21 with seven suggestions (Section 4). Final approval rests with the supervisor, whose name is not recorded here. Every member must be able to explain all code and the proposal, and is questioned individually `[doc: A3, Section 9; A4, Section 9]`.

**Why AI is needed.** The simulated user has to read unstructured web pages and choose actions in natural-language reasoning, which is what agentic tool calling does. Everything that must be exact (leakage detection, counts, scores, diversity measures, payment safety) is deterministic code. The course penalises using a language model for "arithmetic, date calculations or rule checks that code should perform" (up to 5 marks) `[doc: R3, Section 7; R4, Section 9]`. The FACET sample states the same rule as "AI may propose structured facts, but only deterministic code may count, compare, calculate, authorise or change a case's state" `[doc: FP, Section 4]`.

**Positioning and claim discipline.** Vanguard is cheap, early pre-testing. It is **not** a replacement for testing with disabled people, and it does not claim to simulate real disabled people `[context-only]`. The approval email described it as an engineering product that packages ideas from existing work, with **no claim of a new research result** `[context-only]`. Documents must not say "first", "novel" or "outperforms" without a source and a measurement. Reports must state their limits, because disability simulation has been criticised for reinforcing stereotypes `[context-only]`. Unverifiable claims or references can cost up to 10 marks `[doc: R3, Section 7; R4, Section 9]`.

**Name.** "Vanguard", not "Sentinel". Sentinel is the user's separate hackathon project, and the two must not look like one `[context-only]`.

---

## 2. Assignment requirements that bind the project

### 2.1 Track and approval
| Requirement | Source |
|---|---|
| Track declared at approval. Vanguard declared **Pure Product**: a complete product with no formal research question, but design choices justified by comparing alternatives for AI tasks | `[doc: A3, Section 2]` |
| Pure to R&D switch allowed before Assignment 4, with supervisor consent (no reverse switch is described) | `[doc: A3, Section 2]` |
| Idea approved by the supervisor **before** the proposal is submitted. Proposals without prior approval are not evaluated until approval is obtained | `[doc: A3, Sections 3 and 9]` |
| Eligibility (no marks, but blocking): A1 approval email or meeting note; A2 track declared and approved; A3 title registered in the Project Titles sheet; A4 submission complete, including the repository link **with instructor access**; A5 all members present | `[doc: R3, Section 2, Table 3]` |
| "Any group or member not appearing in the demo will be evaluated to ZERO" | `[doc: R3, page 1; R4, page 1]` |
| Avoid generic chatbots, thin wrappers and copies of tutorials. Two groups may not share an idea; the earlier approved group keeps it | `[doc: A3, Section 3]` |

### 2.2 Assignment 3 (due Sunday 2026-11-22 per the user `[context-only]`)
**Submission package** (one per group, on GCR) `[doc: A3, Section 9]`:
1. Proposal (Word or PDF) with all required sections and diagrams.
2. Evidence of supervisor approval.
3. Track declaration, confirmed in the approval.
4. GitHub repository link and, if available, the deployed app.
5. Slides or a dashboard summarising the AI evaluation results, used during the demo.
6. A short declaration of which AI tools were used for the proposal and code, and for what.

**Proposal**: about 4 to 8 pages, mainly paragraphs, with diagrams and tables where they help. The 13 required sections are below `[doc: A3, Section 4, Table 3]`.

| # | Section | Must include |
|---|---|---|
| 1 | Title and Team | Product name, one-line description, members and roll numbers; the track stated below the title (Section 13 row) |
| 2 | Problem and Motivation | Problem, who faces it, how it is solved today, why AI; brief review of existing products/tools and how ours differs |
| 3 | Product Overview and Features | Core vs extended features; one end-to-end workflow diagram |
| 4 | System Components and Architecture | Frontend, backend, database, AI layer, integrations, deployment; architecture diagram; which parts are AI and which deterministic |
| 5 | Generative AI Techniques | Techniques (from Table 4), task, why; candidate models |
| 6 | Technical Alternatives | At least two AI tasks, each with two or more alternatives, and how the choice is made |
| 7 | Data | What data, source, volume, privacy |
| 8 | Evaluation Plan | AI metrics, system metrics (latency, cost, failure rate), user-level benefit |
| 9 | Deployment Plan | Where and how deployed |
| 10 | Funding and Business Model | Cost estimate, market, revenue model, seed funding (see below) |
| 11 | Risks and Responsible AI | Technical risks, failure cases, hallucination handling, privacy, security, human approval points |
| 12 | Work Plan and Team Roles | Milestones and each member's responsibilities; every member contributes to both AI and engineering |
| 13 | Track-Specific Plan (Pure) | Requirements with clear acceptance criteria; evaluation and test plan (functional tests, AI quality metric, latency and cost, safety and prompt-injection tests, peer usability test); documentation plan; target demonstration track, if any |

**Funding section** (about one page): target customers and market size; monthly operating cost at pilot scale; revenue model; seed-funding plan with the current eligibility and application process of **at least two** researched sources; MVP; a one-page **Lean Canvas** (problem, customer segments, UVP, solution, channels, revenue streams, cost structure, key metrics, unfair advantage) `[doc: A3, Section 6]`.

**Technique minimums** `[doc: A3, Section 5]`:
- at least three technique categories from Table 4 (a menu, not a checklist);
- at least one of RAG, fine-tuning (LoRA/QLoRA) or **agentic tool calling**;
- at least one real integration or automation with an external system.

**Implementation, about 40 to 45 percent** `[doc: A3, Section 7]`: core features end to end through the real architecture (frontend, backend, AI, storage); main GenAI components integrated in the product (notebook-only does not count); at least one external integration if proposed; running at a public link **or** reproducibly from the repository; all code in a shared Git repository **with commits from every member**.

**AI evaluation, per implemented AI component** `[doc: A3, Section 8]`:
- labelled test set of **at least 50** examples, separate from prompt-writing or training examples;
- suitable metrics (agents: task success rate, correct tool selection, tool-call success rate, steps per task; every component: latency p50/p95, cost per request, failure and fallback rate) `[doc: A3, Table 5]`;
- at least one simple baseline or alternative;
- error analysis with **at least ten** failures grouped by cause, with planned fixes;
- latency and cost per request;
- Pure track: an initial set of **functional test cases with pass rate**.

**A3 marks** `[doc: R3, Table 10]`. Total 100. Individual score = group B1–E2 (92) + own E3 (8).

| Stage | Checkpoints (max) |
|---|---|
| B Proposal (40) | B1 Problem 4 · B2 Features/workflow 4 · B3 Architecture 6 · B4 GenAI techniques 6 · B5 Alternatives 4 · B6 Data and eval plan 4 · B7 Deployment 2 · B8 Funding 4 · B9 Risks/work plan 2 · B10 Track plan 4 |
| C Implementation (25) | C1 Scope 8 · C2 End to end 5 · C3 AI integrated 6 · C4 Integration 2 · C5 Deploy/reproducible 2 · C6 Repo and teamwork 2 |
| D AI evaluation (20) | D1 Test sets 4 · D2 Metrics 4 · D3 Baseline 4 · D4 Error analysis 3 · D5 Latency/cost 2 · D6 Functional tests with pass rate 3 |
| E Demo and viva (15) | E1 Live demo 5 · E2 Presentation 2 · E3 Individual viva 8 (per member) |

**A3 deductions** `[doc: R3, Section 7, Table 8]`: thin API wrapper up to 10; AI used for deterministic work up to 5; unverifiable claims or references up to 10; missing AI tool declaration up to 3; low individual contribution (individual, evaluator's call).

### 2.3 Assignment 4 (final)
**Product** `[doc: A4, Section 2]`: all core features of the approved proposal end to end; A3 feedback addressed; significant scope changes agreed with the supervisor and explained.

**Engineering** `[doc: A4, Section 3]`: GitHub repository with meaningful commits from every member, **using branches and pull requests for major changes**; Dockerfile per service plus Docker Compose that starts everything with one command; environment-based config with no secrets in the repo; CI/CD (GitHub Actions) running tests on every change; public deployment including inference endpoints; AI observability logging model and tool calls with model and prompt versions, latency, cost and errors (Langfuse, LangSmith or MLflow); AI tool declaration.

**Evaluation** `[doc: A4, Section 4]`: held-out labelled test set per main AI component, **normally at least 100**, with hard and edge cases (smaller sets need justification); metrics in tables; at least two alternatives compared for the main AI tasks, with the choice justified by results; categorised error analysis; robustness and safety (out-of-scope, noisy, adversarial inputs, prompt injection; hallucination where text is generated); **human evaluation** of generated text by at least two people with agreement reported, with any LLM-as-judge checked against those ratings; latency p50/p95, cost per request, failure/fallback rate of the deployed system.

**Pure Product written work** `[doc: A4, Section 5]`: system demonstration paper, 4 to 6 pages, IEEE conference or Springer LNCS template (problem, overview and architecture, AI components and justification, evaluation summary, demo scenario, limitations); product evaluation report (functional tests and pass rate, AI evaluation, performance and cost, safety tests); product documents (PRD with acceptance criteria, API docs such as OpenAPI, user guide with deployment runbook).

**Shared docs** `[doc: A4, Section 6]`: README (purpose, setup, Docker, tests, deployment link, status); architecture document (diagram, components, data model, AI vs deterministic); **AI card** per component (models and versions, purpose, data, evaluation, limitations, risks, safeguards).

**Investor pitch** `[doc: A4, Section 7]`: about 5 minutes, 8 to 10 slides (problem, solution, demo, market, business model, costs, competition, team, funding ask and use), with the updated Lean Canvas as an appendix.

**Final demo** `[doc: A4, Section 8]`: deployed product, realistic inputs, main workflows, AI in action, and **at least two difficult or failure cases**.

**A4 marks** `[doc: R4, Table 13]`. Total 100. Individual score = group B1–G1 (92) + own G2 (8).

| Stage | Checkpoints (max) |
|---|---|
| B Product completeness (20) | B1 Core features 8 · B2 End-to-end integration 5 · B3 Feedback/scope 3 · B4 Robustness in use 4 |
| C Engineering (14) | C1 Git repo 2 · C2 Containers 3 · C3 Config/secrets 2 · C4 CI/CD 3 · C5 Public deployment 2 · C6 Observability 2 |
| D AI evaluation (20) | D1 Datasets 3 · D2 Metrics 3 · D3 Alternatives 4 · D4 Error analysis 2 · D5 Robustness/safety 3 · D6 Human evaluation 3 · D7 Performance/cost 2 |
| E Pure track (25) | E1 System description 4 · E2 AI components and eval summary 4 · E3 Demo scenario and writing 4 · E4 Product evaluation report 8 · E5 Product documents 5 |
| F Docs and pitch (10) | F1 README 1 · F2 Architecture doc 2 · F3 AI card 2 · F4 Investor pitch 5 |
| G Demo and viva (11) | G1 Demo delivery 3 · G2 Individual viva 8 (per member) |

**A4 deductions** `[doc: R4, Section 9, Table 11]`: thin wrapper up to 10; AI for deterministic work up to 5; unverifiable results or references up to 10 (written work may be marked zero); exposed secrets in repo **or its history** up to 3; missing AI tool declaration up to 3; low individual contribution.

### 2.4 What the FACET samples show about expected depth
Both samples use: a features table with core/extended IDs reused in the work plan and acceptance criteria; workflow and architecture diagrams; an **AI vs deterministic responsibilities table**, with the rule that AI may propose structured facts but only code may count, compare, calculate, authorise or change state; a techniques-to-task table with candidate models; an alternatives table with decision criteria (for example, prefer the cheaper option when accuracy is within about two points); a data table with volumes; an evaluation table with numeric initial targets; a cost table; four researched seed-funding sources; a Lean Canvas; a risk/safeguard table; a scope-per-part table; roles; weekly milestones; an acceptance-criteria table with "how it is tested"; and a plan for at least 20 prompt-injection attempts plus a three-person usability walkthrough `[doc: FP, Sections 1–13]`. The R&D sample adds RQs with numeric hypotheses, ablations, five resamples × three runs, paired bootstrap and McNemar with Holm correction, an LLM judge only if kappa ≥ 0.7 against two annotators, and threats to validity `[doc: FR, Section 13]`.

---

## 3. Architecture and where each part comes from

### 3.1 Intended flow `[context-only]`
```
persona spec (JSON)
   -> perception filter (code: what this user can perceive, e.g. accessibility tree only)
   -> simulated-user agent (Gemini with tool calling: chooses the next browser action)
   -> action gate (rule-based allow-list; optional LLM verifier)
   -> browser executor on the demo store (sandbox checkout)
   -> trace store (every proposed and executed step)
   -> audit engine (rule-based leakage checks; diversity measures)
   -> dashboard + PDF/email report
run controller: repeats runs with fixed settings so the four enforcement options are compared on identical tasks
```

### 3.2 What the reference repositories actually contain

**Sentinel** (`sentinel/`, the user's PayPal AI Hackathon project, MIT licence `[repo: sentinel/LICENSE]`). Next.js 16.4.6, React 19.3, TypeScript, Tailwind 4, zod 4, Braintree, AG Grid, jose `[repo: sentinel/package.json]`. About 14.6k lines of TS/TSX `[repo: line count of *.ts* files]`. 135 commits, all by FaatehHaneef `[repo: git log]`.

Important for Vanguard. These are facts about how Sentinel works, and several differ from what the planning notes assumed:
- **The seven shoppers are scripted, not LLM agents.** Each character is a fixed record (sprite, check function, canned lines, checkout details) `[repo: sentinel/engine/cast/types.ts, cast/knock.ts]`. The route through the store is a hard-coded journey of six scenes, with an `advance()` function per scene that finds elements by selector or text and acts on them `[repo: sentinel/engine/journeys/tallowmere.ts]`.
- **The engine runs inside the store page.** It is a script bundled with esbuild and loaded by a one-line loader, not a browser driven from outside `[repo: sentinel/engine/loader.ts, engine/index.ts, scripts/build-engine.mjs]`. Actions use DOM calls: `element.click()`, `field.focus()` and value setting `[repo: sentinel/engine/core/run.ts, actor.click/type]`. **Playwright appears only in the end-to-end tests** (`@playwright/test`, `tests/e2e/`), not in `engine/` or `lib/` `[repo: sentinel/playwright.config.ts; grep of engine/ and lib/]`.
- **Even Knock, the keyboard-only shopper, "clicks"** with `element.click()`. Knock's *checks* measure keyboard reachability, focus visibility, tab order and skip link with DOM calls, but its *walk* does not press keys `[repo: sentinel/engine/checks/knock.ts header comment; engine/core/run.ts]`. `element.click()` fires a synthetic click event, not a real mouse movement. Under the draft definition in Section 4.1, which counts any click action as pointer use, Sentinel's own Knock walk would be flagged at every step. That is a concrete example for the proposal of why a persona label alone does not enforce a limit.
- **Checks are deterministic measurements**: a grep for `"<character>.<check>"` strings in `engine/checks/*.ts` finds 29 distinct ids across 7 characters, consistent with the README's "29 checks" `[repo: sentinel/engine/checks/, README.md]`. Not run, so whether each check behaves as described is `[unverified]`.
- **Gemini is used in three places only**: Wick writes verdict text from measurements and may suggest contrast colours, which the contrast maths then checks `[repo: sentinel/lib/ai/wick.ts]`; Cog's agent decides whether to buy from product data, and the server checks that decision against the goal and catalogue `[repo: sentinel/lib/ai/cog.ts, engine/cast/cog.ts]`. Both prompts already tell the model to treat page text as data, not instructions `[repo: sentinel/lib/ai/wick.ts, lib/ai/cog.ts]`.
- **Gemini client with fallback**: JSON-schema output, several models (default `gemini-flash-latest`, `gemini-flash-lite-latest`) and several keys, key resting on 429/401/403, timeouts, and a typed `AiUnavailableError` that callers handle with a non-AI fallback `[repo: sentinel/lib/ai/gemini.ts]`.
- **Guards**: `checkOrigin` is an *origin* allow-list deciding where a trial may run (own origins plus verified sites) `[repo: sentinel/lib/guards/allow-list.ts]`. `assertSandboxOnly` refuses to start if `PAYMENTS_ENVIRONMENT` is anything other than `sandbox` `[repo: sentinel/lib/guards/sandbox.ts]`. Neither is a per-action gate for an agent; that gate is new work.
- **Demo store "Tallowmere"** with deliberate, switchable problems (`hero-image`, `product-data`, `phone-popup`) `[repo: sentinel/lib/store/variants.ts]`. Checkout runs on the **Braintree sandbox**, not a PayPal account, because PayPal accounts are not available to developers in Pakistan `[repo: sentinel/README.md, Limits]`. API routes cover checkout token, order and pay, a webhook, the agent order, runs and verdicts `[repo: sentinel/app/api/]`.
- **Tests and CI**: Vitest unit tests and 24 Playwright e2e tests `[repo: sentinel/tests/]`. The README says 100 unit tests; a grep finds 82 `it`/`test` declarations, possibly because some are parametrised `[unverified: not run]`. GitHub Actions runs format check, lint, typecheck, tests and build `[repo: sentinel/.github/workflows/ci.yml]`. None of this has been run in this setup.
- **Trial records are kept in the browser** (localStorage), with no accounts `[repo: sentinel/README.md, Limits]`. On the server, a key-value interface currently backed by an in-memory store lives for the life of one server instance; a hosted adapter is planned but not present `[repo: sentinel/lib/storage/index.ts, lib/storage/get-store.ts]`. Vanguard needs real persistent storage for traces (rubric C2 "storage") `[doc: R3, C2]`.

**Synthetic Users** (`synthetic-users/`, built for CS3014 Tool Talk, team E01-Insyder). Python 3.11+, Flask, requests, pandas, matplotlib, pytest; React/Vite front end with a built copy in `web/dist` `[repo: synthetic-users/requirements.txt, server.py, web/]`. 42 commits, all by FaatehHaneef `[repo: git log]`. **No LICENSE file** `[repo: file listing]`.
- Prompts: `PROMPT_1` and `PROMPT_2_SUFFIX` are verbatim from the CHI '23 paper; `SYSTEM_INSTRUCTION`; ten `PERSONAS`; `build_prompt` `[repo: synthetic-users/synthusers/prompts.py]`.
- Generation: quality rules (`quality_status`: at least 10 words, no repetition over 10 characters, a title present), a balanced job planner, and resumable append-only JSONL runs that refuse to mix providers or models in one file. Fake provider for offline tests `[repo: synthetic-users/synthusers/generate.py]`.
- Analysis: title cleaning and alias merges; per-group distinct count, distinct per 100, top-1 share with a **Wilson 95% interval**, top-3 share, **Shannon entropy**, mean words; review sample sheet; charts `[repo: synthetic-users/synthusers/analyze.py]`. These are *categorical* diversity measures over a single answer. Sequence measures (edit distance over action sequences) do not exist and are new work.
- Results: 356 requests on `gemini-3.6-flash`; plain prompt 5 distinct games, Journey 92.7%; with personas 9 distinct, Gris 28.7%; real people 110 distinct from 179 mentions (the team's arithmetic on the paper's Table 6) `[repo: synthetic-users/README.md, results/gemini-main/summary.json]`.
- `docs/verification-notes.md` is a claim-by-claim status table (CONFIRMED / CORRECTED / NOT VERIFIED) against primary sources, and the README states "Code drafted with AI assistance" `[repo: synthetic-users/docs/verification-notes.md, README.md]`. The habit is worth reusing; the disclosure matters for the AI tool declaration.

### 3.3 Component mapping
| Vanguard component | Source | Status |
|---|---|---|
| Persona spec (perceive / act / know), JSON with schema validation | Idea from `sentinel/engine/cast/types.ts`; zod already a Sentinel dependency | **New** (Sentinel's cast has no capability model) |
| Perception filter: screen-reader persona sees only the accessibility tree | Playwright `locator.ariaSnapshot()` was suggested by the TA `[context-only]` | **New**. Sentinel's engine has no external browser driver |
| Simulated-user agent (Gemini function calling over browser-action tools) | Gemini client pattern from `sentinel/lib/ai/gemini.ts` (needs extending from JSON output to function calling) | **New** agent loop; client **reused/adapted** |
| Action gate (rule-based allow-list per persona; domain allow-list so a live payment page is never reached) | Origin-check style from `sentinel/lib/guards/allow-list.ts`; sandbox assertion from `sentinel/lib/guards/sandbox.ts` | **New** gate; guards **reused** as the base |
| Verifier agent (second model call checks each proposed action against the spec) | — | **New** |
| Browser executor | Playwright, so keyboard events, mouse events and aria snapshots are real and observable | **New** (Sentinel only uses Playwright in tests) |
| Demo store with sandbox checkout | `sentinel/app/store/`, `components/store/`, `lib/store/`, `lib/payments/`, `app/api/checkout/` | **Reused** (copied with provenance) |
| Deterministic accessibility checks (as context and as store "problems") | `sentinel/engine/checks/*.ts` | **Reusable**, optional |
| Trace store | Append-only JSONL idea from `synthetic-users/synthusers/generate.py` | **New** schema; pattern **reused** |
| Run controller (fixed settings, resumable, balanced across options) | `run_generation`, `plan_next_job` in `synthetic-users/synthusers/generate.py` | **Adapted** |
| Leakage checker (rule-based on browser events and state, not LLM) | — | **New** |
| Diversity analysis | Entropy, Wilson CI from `synthetic-users/synthusers/analyze.py` | **Extended**: normalised edit distance on action-type sequences, spread of steps and success are new |
| Finding explanations (LLM text; all numbers from code) | Pattern from `sentinel/lib/ai/wick.ts` ("measurements are facts") | **Adapted** |
| Dashboard, export, email report | AG Grid ledger idea from `sentinel/components/sentinel/Ledger.tsx` | **New** (email integration new) |
| Labelled step test set, labelling guide, agreement (Cohen's kappa) | — | **New** |
| Observability (Langfuse or similar), Docker Compose, CI | Sentinel CI as a starting point | **New** for A4 |

**The stack is not decided** (see Section 6.2). Sentinel is TypeScript/Next.js; Synthetic Users is Python. Whatever is chosen, an external browser driver is needed for real keyboard events and aria snapshots, which neither repository has outside tests.

**Provenance.** Reused code is the user's own. Copy it into the Vanguard repo as new commits, never modify the originals, and add a short NOTICE or README line naming the source repository, so nothing appears to have been written during this course `[context-only]`. The exact wording is still open.

---

## 4. Evaluation design (draft)

### 4.1 Leakage definition per persona
The TA asked for leakage to be defined precisely per persona, or the rule-based checker and the human labels will not agree `[context-only: TA suggestion 1]`. **The current definition is [docs/leakage-spec.md](docs/leakage-spec.md)** (v0.1, 2026-11-21). It covers the five agreed personas, which are built from limits L1–L4 plus the control, along with hard and soft rules, honeytokens, executed vs attempted leakage, per-option behaviour, metrics, the labelling procedure and the site split. The table below is the earlier three-persona draft, kept only for history:

| Persona | Forbidden actions | Forbidden information | Detection rule (code) |
|---|---|---|---|
| Keyboard-only | Any mouse or pointer action: click, hover, drag, scroll by wheel, coordinate-based action | None beyond the default | Executor logs the input type of every step; any pointer event = executed leakage; any pointer action *proposed* = attempted leakage |
| Screen-reader-style | Actions that require sight (coordinate clicks, "the red button", visual-only cues) | Anything not in the accessibility tree (CSS colour, layout position, visual-only text, image pixels) | The agent receives only the aria snapshot. A step is flagged if it references an element or property absent from the snapshot it was shown (deterministic match of referenced names/roles against the snapshot) |
| First-time shopper, limited domain knowledge | — (normal input) | Knowledge outside the spec: hidden URLs, store internals, product facts not on screen, jargon the spec says the user does not know | Steps that navigate to URLs not linked from the current page, or use terms or values not present in the observed page or the spec's knowledge list |

The third persona's rule is the hardest to make deterministic. It needs a decision before labelling starts.

### 4.2 Metrics per run `[context-only: TA suggestions 2 and 7]`
- **Executed leakage** (forbidden steps that reached the browser) and **attempted leakage** (forbidden steps the agent proposed, including those the gate blocked). Code-enforced options will show about zero executed leakage by design, so attempted leakage is what keeps them comparable.
- **Task success**, **steps per task**, **stuck rate** (no progress within N steps or a repeated-state loop).
- **Latency** (p50, p95) and **cost** per step and per run; failure and fallback rate `[doc: A3, Table 5; A4, Table 2]`.

### 4.3 Diversity `[context-only: TA suggestion 4]`
- Normalised edit distance between action-type sequences, within a persona across runs and between personas.
- Spread (SD or IQR) of step counts and success across runs and personas.
- Entropy of action-type mix (reusing `synthetic-users/synthusers/analyze.py` style).
- Compare with A11y-CUA only on comparable quantities (action mix, share of key presses, Arrow/Tab dominance), and state that its tasks were Windows desktop tasks, not web shopping `[context-only]`.

### 4.4 Test set and labels
- A labelled set of steps across all three personas: **at least 50 for A3** `[doc: A3, Section 8]`, **at least 100 for A4** `[doc: A4, Section 4]`. The TA suggested aiming for 100 or more `[context-only]`.
- Two members label independently with a written guide; report Cohen's kappa. The FACET R&D sample targets kappa ≥ 0.7 `[doc: FR, Section 7]`.
- Keep labelled steps separate from prompt development `[doc: A3, Section 8]`. Never use model-written labels as ground truth for the same model `[context-only]`.

**Which component is evaluated by what.** The rubric asks for a test set per *AI* component `[doc: R3, D1]`. The leakage checker is deterministic code, not an AI component. The labelled steps validate the checker (agreement with humans) and also act as ground truth for the **verifier agent** (precision and recall of flagged steps) once it exists. The **simulated-user agent** is evaluated with agent metrics (task success, steps, tool-call success, leakage rate) over a fixed task × run set `[doc: A3, Table 5]`. The proposal has to make this framing explicit.

### 4.5 Comparison of alternatives (the Pure-track design justification)
Four enforcement options on identical tasks and repeated runs: (1) prompt-only baseline, (2) code-enforced action gate, (3) bounded perception, (4) verifier agent; plus an ablation of the verifier `[context-only]`. This satisfies "at least two AI tasks with two or more alternatives" `[doc: A3, Table 3 row 6]` only if a **second AI task** also has alternatives. Candidates: the explanation generator (template vs LLM), or the agent's model (two Gemini tiers). This needs a decision.

**Second-task alternatives (all wanted, none mandatory yet).** (a) agent model: Gemini tiers vs a local open model; (b) agent perception format: accessibility tree vs simplified DOM vs screenshot; (c) explanation generator: template vs LLM vs LLM checked against measurements; (d) verifier: rules only vs LLM vs both. Each is a pluggable strategy behind one interface, with a baseline that always exists. A run config names one choice per axis. Axes are varied one at a time against a default config rather than fully crossed, so cost grows linearly. An alternative that is not built is simply absent from the results table and leaves no broken path.

**Run budget.** 3 to 5 runs per persona per task `[context-only: TA suggestion 7]`. Illustration: 3 personas × 5 tasks × 5 runs × 4 options = 300 runs; the task count of 5 is an assumption `[context-only]`.

### 4.6 Safety and robustness
- Prompt-injection set: hostile text placed on store pages (product descriptions, reviews, banners) `[context-only]`. FACET plans at least 20 attempts `[doc: FP, Section 13]`.
- An automated test that the agent can never reach a live payment page (domain allow-list in the gate plus the sandbox assertion) `[context-only: TA suggestion 6]`.
- No secrets in the repository or its history `[doc: R4, Section 9]`.

### 4.6a Datasets (decided 2026-11-21)
**Priority:** the deployed product (Gemini) comes first. Local-model and fine-tuning work must never delay or degrade it.

**Our own traces** are the main dataset. Every run writes step records with the fields the checker needs (observation, proposed action and rationale, gate decision, executed action, browser input events, URL, focus, magnifier window, target bounding box, cumulative seen text and links). Records are split by site (train / dev / test, see `docs/leakage-spec.md` Section 8) into: an evaluation set (human-labelled test-site steps), a fine-tuning SFT set (allowed, progress-making steps from train sites), and a preference (DPO) set (blocked vs allowed proposals at the same state, from train sites).

**Public datasets**, stored outside the repo in `D:\VanguardData\` (sizes from the Hugging Face API, 2026-11-21):

| Dataset | Licence | Size | Local copy | Possible use |
|---|---|---|---|---|
| osunlp/Mind2Web | cc-by-4.0 | 6.74 GB | full, verified 2026-11-22 (1,009 tasks) | general web-navigation SFT before our traces; action-mix statistics (mostly click/type) |
| berkeley-hci/Reduced-A11y-CUA | cc-by-4.0 | 3.86 GB | full, verified 2026-11-22 (13,881 files) | reference statistics; contains `web_logs` with accessibility trees, so it is not only Windows desktop data `[repo: HF file listing]`. Decided earlier as reference-only, not training |
| Qwen/WebWorldData | apache-2.0 | 52.2 GB (one JSONL) | first 300 MB sample, verified (4,211 records) | accessibility-tree trajectories; check fit before a bigger pull |
| webagentlab/webchain | cc-by-4.0 | 386 GB | card only | screenshot + DOM + AX-tree trajectories; pull single parts later if needed |
| osunlp/Multimodal-Mind2Web | openrail | 13.6 GB | not pulled | screenshots for perception alternative "b" |
| berkeley-hci/A11y-CUA (full) | cc-by-4.0 | 176 GB | not pulled | includes agent runs (e.g. Claude Sonnet 4.5, Qwen3-VL) under screen-reader and magnifier conditions; pull selected logs only |
| princeton-nlp/WebShop | unconfirmed | — | not pulled | candidate independent test site (simulated shop) |

Disk constraint: about 37 GB were free on C: before the downloads. **Permanent home: `D:\VanguardData\`** (645 GB free; decided 2026-11-21). The partial download was moved from C: to D: on 2026-11-21 and resumed there, so nothing remains on C:. **Verified 2026-11-22; data cards in [docs/data-cards.md](docs/data-cards.md).** When the downloads finish, each dataset is verified: file counts and sizes are checked against the Hugging Face listing, every JSON/JSONL/parquet file is parsed, the schema is inspected, and a short data card is written for each. All future code reads the path from an environment variable (`VANGUARD_DATA_DIR`, default `D:\VanguardData`) and never from a path hard-coded in the repo.

### 4.6b Git workflow (decided 2026-11-21)
- Many small, meaningful commits as work progresses; never one big dump. Conventional style messages (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
- Feature branches for major parts, merged into `main` (A4 C1 asks for branches and pull requests).
- **Standing branches (decided 2026-11-22):** five long-lived branches, each merged into `main` with `--no-ff` when a piece is ready, and kept afterwards:
  - `websites`: Tallowmere and every other test site (`apps/tallowmere`, `sites/*`);
  - `engine`: executor, agent loop, gate, rules, providers, store, API;
  - `evaluation`: checker, metrics, batches, labelling, failure analysis, results scripts;
  - `app`: the web app and the HUD;
  - `docs`: written deliverables, specs, data cards.
  Teammates may add their own branches. (Earlier the same day, 23 small one-feature branches were merged and deleted; their merge commits keep the history.)
- Every member commits their own work from their own GitHub account. Nobody commits on behalf of another member (rubric C6/C1 count real contributions).
- No AI attribution lines anywhere.

### 4.7 Reproducibility (wanted by the user even though the track is Pure) `[context-only]`
Fixed settings and seeds where possible, resumable runs, results saved as files, and a script that regenerates the results tables.

### 4.8 A3 build target (about 40 to 45 percent), as agreed in planning `[context-only]`
One persona (keyboard-only) end to end on the demo store with the action gate; the leakage table and rule-based checker for that persona; prompt-only vs code-enforced comparison; a first labelled set of at least 50 steps; one results slide; the AI-tools declaration. Everything else is A4.

Against the rubric, this also needs: functional tests with a pass rate (D6), at least ten categorised failures (D4), latency and cost on the running system (D5), one working external integration (C4; Gemini API and Braintree sandbox are candidates, email if the report export is built), a frontend → backend → AI → storage path (C2), and commits from all three members (C6) `[doc: R3, Tables 5–6]`.

---

## 4.9 Build plan by part and phase (draft 2026-11-21)

**Foundation status (2026-11-21, evening):** done and committed in `backend/`: contracts, catalog (5 personas, Tallowmere tasks), shared hard and safety rules (S0, H1, H4a), action gate, provider interface (Gemini + scripted fake), executor interface + fake browser, agent loop with deterministic success and stuck checks, trace store, run service and API. 27 tests pass offline. Checker and metrics have defined interfaces only. `apps/web` and `apps/tallowmere` have handover notes only. Next: the Playwright executor and the worker (Faateh).

**Status (2026-11-22):** the foundation is complete and the old clones are no longer needed (every reused piece is copied, with provenance in `NOTICE.md`). Done on top of it, at the user's request to push as much development as possible before the team split takes effect:
- Playwright executor and worker image: real input, full-view observation, trusted-event recording, network allow-list, screenshots, link-navigation waits; focus shown only when visible (spec v0.2). Verified on Tallowmere: the cart's `+`, `-` and `remove` are skipped by Tab, and "Add to cart" focus is hidden.
- Character overlay (`apps/hud`, bundled with esbuild): decoration only, outside observations, the accessibility tree and recorded events.
- Leakage checker (H1 with browser evidence, H4a), run and group metrics (Wilson intervals, latency percentiles, cost from a configured price), balanced and resumable batches (API and CLI), blind labelling with Cohen's kappa and checker precision/recall, a labelling guide.
- Web: live view with screenshots, checker metrics and leak badges per run, comparison table per trial, labelling desk.
- Later the same day: failure analysis by cause, mobile and slow-network conditions, the explanation generator in three modes (alternative c), the verifier agent with precision/recall against the hard rules (option 4), screen-reader perception and commands and the magnifier window for bounded perception (option 3), H3a, H4b and three honeytokens planted in Tallowmere, an OpenAI-compatible provider (alternative a, local runs), a results dashboard, and batches started from the site picker.
- 80 backend tests pass, including 9 against real Chromium; CI runs them all on Linux.
- Waiting on: a Gemini key and Braintree sandbox keys (the user will add them) for the first real baseline batch. Hadi's and Ibrahim's parts were started from the foundation (checker, metrics, labelling first versions; explain prompt and schema); they extend these.

**What "foundation complete" means (decided 2026-11-21).** The foundation is finished when nobody ever needs `sentinel/` or `synthetic-users/` again: every reused piece has been copied into this repo, adapted and committed, so the two clones can be treated as gone. Teammates never clone or extract from them. Faateh (with Claude Code) builds the whole foundation:
1. Backend core: ✅ done (above).
2. **Tallowmere** extracted into `apps/tallowmere`, running standalone on port 3100, with a Dockerfile.
3. **Web app** in `apps/web`: Sentinel's landing, lobby, sprites, sounds, results and ledger ported, wired to the Vanguard API (personas, sites, tasks, start run, step feed). Includes the new Wren sprite.
4. **Playwright executor and worker**: real browser, real key presses, input-event recording, screenshots, HUD/sprite overlay injected as decoration only.
5. **Remaining reusable code copied**: Synthetic Users' statistics helpers (Wilson interval, entropy) and resumable-run pattern; Sentinel's verdict prompt (Wick) as the starting point for the explanation generator.

**Team split after the foundation (proposed, to confirm):** teammates get self-contained building work inside this repo, mostly agent and evaluation components, each covering both AI and engineering as A3 Table 3 row 12 requires.

| Member | Builds |
|---|---|
| Faateh | foundation (all of the above), agent loop and prompts, run controller, the A3 comparison runs |
| Hadi | explanation / verdict generator (alternative c), preview personas' perception and prompts, results page and live-view polish; **2–4 test sites** |
| Ibrahim | leakage checker, metrics and results-table script, labelling workspace and kappa, functional tests, failure analysis, latency and cost; **2–4 test sites** |

The 4–8 test sites (A4 scope, can start now) follow [docs/test-site-kit.md](docs/test-site-kit.md): a different framework per site, domains beyond shopping, 2–4 tasks with deterministic success checks, at least one planted barrier and one honeytoken per limit, and a manifest kept out of the served site. Because team members build them knowing the project, documents call them "built separately from Vanguard's code, to a written specification", not "independent".

| # | Part | A3 (due 2026-11-22) | A4 | Stretch |
|---|---|---|---|---|
| 0 | Foundation: repo layout, Docker Compose (web, api, worker, db, tallowmere), env config, basic CI, `AI_USE.md`, provenance NOTICE | ✅ all | full CI/CD, deploy | — |
| 1 | Tallowmere standalone test site (extracted from Sentinel, Braintree sandbox) | ✅ extract, decouple from Sentinel, keep its existing barriers | add planted barriers and honeytokens for every limit | — |
| 2 | Frontend (Sentinel UI ported): landing, lobby, site picker, live view, results, ledger | ✅ landing, lobby, site picker (Tallowmere only), live step feed, results | own-site flow, compare view, labelling workspace, persona builder | — |
| 3 | Personas and limits (spec schema, limit library) | ✅ All 5 characters in the lobby and runnable. **Full:** keyboard-only (Knock) and control (Cog), with their limits enforced, perceived, checked and evaluated. **Preview:** Echo, Iris and the first-time visitor, with persona spec and prompt-stated limits only, a "Preview" badge in the UI, results marked "not validated", and exclusion from evaluation metrics. The A3 report states this explicitly | full L2, L3, L4 for the three preview personas; conditions | custom personas |
| 4 | Executor (Playwright worker, tool vocabulary, observation builders, input-event recording, screenshot stream) | ✅ keyboard + pointer tools, full-view observation, events, screenshots | ARIA snapshot, screen-reader commands, magnifier window, conditions | — |
| 5 | Agent loop and model providers | ✅ Gemini function calling, provider interface | local (Ollama), Groq, OpenAI in local mode | — |
| 6 | Action gate | ✅ H1 + payment-domain allow-list | H4a/H4b, combinations | — |
| 7 | Run controller and trace store | ✅ configs, repeats, Postgres step records | resumable batches, cost estimate | — |
| 8 | Leakage checker | ✅ H1 (+ H4a for the control) | all hard and soft rules, honeytokens | — |
| 9 | Metrics, diversity, results-table script | ✅ leakage, success, steps, stuck, latency, cost | edit-distance diversity, A11y-CUA comparison | — |
| 10 | Explanation generator (verdict text, numbers from code) | ✅ one LLM version | template vs LLM vs checked LLM (alt c) | — |
| 11 | Reports: dashboard, PDF, email | results page | PDF export, email integration | — |
| 12 | Evaluation kit: labelling, kappa, functional tests, failure analysis, injection set | ✅ ≥50 labelled steps, kappa, functional tests with pass rate, ≥10 failures, latency/cost | ≥100 per component, human eval of text, injection set, robustness | — |
| 13 | Alternatives | ✅ enforcement: prompt-only vs gate (the A3 baseline comparison) | bounded perception, verifier (alt d), models (alt a), perception formats (alt b), explainers (alt c) | fine-tuning (option 5) |
| 14 | Own-site testing and new sites | — | verification snippet, 4–8 independent test sites | — |
| 15 | Production and docs | proposal, slides, AI declaration | deployment, observability, paper, PRD, API docs, user guide, README, architecture doc, AI card, pitch | — |

A3 external integrations: Gemini API and the Braintree sandbox checkout, which the agent drives during a trial `[doc: A3, Section 5; R3, C4]`.

## 5. Research context

**Abstract pages re-checked on 2026-11-21** (only the abstract or first page was read; claims from the paper body stay `[context-only]` until someone reads the body):
- Mohanbabu, Natalie, Kim, Guo, Pavel. *A11y-CUA Dataset: Characterizing the Accessibility Gap in Computer Use Agents.* CHI '26 (arXiv comments). https://arxiv.org/abs/2602.09310.
  - **Abstract confirms:** 60 everyday tasks, 40.4 hours, 158,325 events; the default computer-use agent succeeded on 78.3% of tasks, falling to 41.67% keyboard-only and 28.3% with a magnifier.
  - `[context-only, body not read]`: 16 participants (8 blind or low-vision, 8 sighted); blind and low-vision users at 211.18 s and 84.6% success vs 92.35 s and 99.16% for sighted users; no mouse actions; Arrow/Tab at 72.23% of keystrokes; the agent was Claude Sonnet 4.5.
  - Data: https://huggingface.co/datasets/berkeley-hci/Reduced-A11y-CUA (structured, cc-by-4.0 `[context-only]`), for reference statistics only, not for training.
  - An appendix contains study-account credentials: **never copy them into any file**.
- Natalie, Xu, Chang, Mihalcea, Guo. *Not There Yet: Evaluating Vision Language Models in Simulating the Visual Perception of People with Low Vision.* https://arxiv.org/abs/2508.10972. **Abstract confirms** "VLMs tend to infer beyond the specified vision ability when given minimal prompts", with low agreement (0.59). The 0.59 → 0.70 snippet in the planning notes probably comes from this paper; check in the body.
- Xiao, Zhang, Yang, Xuan, Huang. *The Chameleon's Limit: Investigating Persona Collapse and Homogenization in Large Language Models.* https://arxiv.org/abs/2604.24698 (v2). **Abstract confirms** that responses from LLMs given detailed profiles "cluster into classes, unlike human responses", across eight LLMs, and that "the models with the highest per-persona fidelity produce the most polarized populations". It names three diagnostic metrics: Coverage, Uniformity, Complexity. **No toolkit is mentioned in the abstract.**
- Touir, Ktata, Soui. *Grounding Persona-Driven Usability Simulation in Established Standards.* ACM CHI'26 Workshop on Responsible Use of AI Personas in Human-Centered Design and Research, 13 April 2026, Barcelona; CEUR-WS Vol-4249, paper 4. https://ceur-ws.org/Vol-4249/paper4.pdf. **Abstract confirms:** a Simulation-Based Usability Testing Module (SUTM), a persona-driven multi-agent workflow with a Supervisor-Agent, and persona inconsistency reduced "from 45% to 0.8%". "Accessibility constraints" was not seen in the readable text `[unverified]`. Our critique (no clear counting method, no cross-persona diversity metric, no real end users) is `[context-only]`.
- Huang et al. (46 authors). *AgentPersonaBench: Benchmarking Persona-Driven User Simulation.* https://arxiv.org/abs/2610.04379. **Abstract confirms** 2,460 tasks, 867 traits, 20 frontier model arms, up to 84.7% full-pass adherence unprompted. **"Capability intrusion" is not in the abstract** `[unverified: check the body before using the term]`.
- Zhong, Chen, Win Kyi, Li, Fogarty, Wobbrock. *TaskAudit: Detecting Functiona11ity Errors in Mobile Apps via Agentic Task Execution.* CHI 2026. https://arxiv.org/abs/2510.12972. **Abstract confirms** "a Task Executor that uses agents with a screen reader proxy".
- Playwright: https://playwright.dev/docs/aria-snapshots **confirms** `page.ariaSnapshot()` and `locator.ariaSnapshot()` (YAML of accessible elements). The old `class-accessibility` docs page now returns 404, which is consistent with the API having been removed, but that is not confirmed. Use `ariaSnapshot()`.

**From search snippets only** `[unverified]`: WebAIM Screen Reader Survey #11 (https://webaim.org/projects/screenreadersurvey11/) and #10; ASE 2025 visually-impaired-user agent proposal; persona manifold collapse (arXiv 2606.18263); distribution-first population simulation (arXiv 2607.18310); competence leakage (NeurIPS 2026 poster 169055); KnowSim (arXiv 2608.17150); KAUCUS (arXiv 2401.16454); unlearning for novice student simulation (arXiv 2603.26142).

**Also relevant, already checked in Synthetic Users** `[repo: synthetic-users/docs/verification-notes.md]`: Hämäläinen, Tavast & Kunnari, CHI '23 (https://doi.org/10.1145/3544548.3580688); Agnew et al., CHI '24, "The Illusion of Artificial Inclusion"; ScreenAudit (arXiv 2504.02110, snippet only, which argues LLMs cannot themselves perform screen-reader interaction).

**Gap statement, usable only with its hedges** `[context-only]`: "To our knowledge (search of 2026-11-20, not a systematic review), we did not find prior work that compares enforcement methods for simulated users with limits and scores leakage and diversity together against real behaviour traces." Pure track has no formal research question, so keep this as motivation, not as a contribution claim.

---

## 6. Decisions

### 6.1 Decided `[context-only unless tagged]`
- Name **Vanguard**. Track **Pure Product**, with the four-option enforcement comparison as the design justification.
- Domain: accessibility and usability pre-testing with simulated users on a demo shopping store.
- First three personas: keyboard-only, screen-reader-style, first-time shopper with limited domain knowledge.
- LLM: Gemini.
- All seven TA suggestions adopted.
- Acceptance criteria as sent to the supervisor: core flows (create spec, run, view report, export) covered by automated tests with at least 90% passing; rule-based leakage checks agree with two human labellers on at least 50 labelled steps, with agreement reported; leakage rates of all four options measured against the prompt-only baseline on identical tasks and repeated runs, with the choice justified; latency (p50, p95) and cost per run reported.
- Fine-tuning is not in the plan sent to the supervisor (removed from the email; undecided, not forbidden).
- Repository setup (2026-11-21): local repo at `C:/dev/Vanguard` (moved out of OneDrive on 2026-11-21 to avoid sync locks on node_modules, .venv, .git and Docker mounts), remote `https://github.com/FaatehHaneef/Vanguard.git`, author `FaatehHaneef` with the GitHub noreply address (switched from Gmail on 2026-11-21 when GitHub email privacy refused the first push; all commits were rewritten before anything was published). `sentinel/`, `synthetic-users/`, the six course PDFs and the two planning markdown files in `docs/` are gitignored, while the `docs/` folder itself is tracked (via `.gitkeep`) for future customised documents. First pushed to GitHub on 2026-11-21 at the user's request.
- No AI attribution in commits, PRs or files; commits are authored by FaatehHaneef only. If GitHub refuses the Gmail address on push, switch to the GitHub noreply address and keep the username `FaatehHaneef`.
- Decided by the user on 2026-11-21:
  - **Core in Python**: FastAPI backend, Playwright (Python) worker, Postgres; React frontend.
  - **Web app**, publicly deployed with Docker (not Vercel, because Playwright needs a full browser), and also runnable locally with Docker Compose.
  - **Test sites are separate apps.** Tallowmere is one test site. 4 to 8 more independent websites, possibly in different frameworks, will be built with no knowledge of Vanguard.
  - **Owner-installed snippet** (meta tag or file) for running on other people's sites. Installing it is the owner's consent. Nothing is injected into the page; Playwright drives the browser from outside.
  - **Scope**: public, ungated sites only (no third-party logins, paywalls or CAPTCHAs). Task types beyond checkout are welcome. Our own test sites may include fake accounts.
  - **All four second-task alternatives (a–d) are wanted**, built so that any unfinished alternative leaves no gap (Section 4.5).
  - **Models**: Gemini API, plus a local open model as an alternative.
  - **Personas** (replace the three in Section 4.1, whose leakage table must be extended): keyboard-only; screen-reader; magnifier / low-vision; first-time shopper; plus an unrestricted agent as the **control**. Mobile viewport and slow network are optional *conditions*, not personas. Limits are the basic unit, each with its enforcement and its detection rule, and personas are bundles of limits.
  - **Sentinel's gamified UI is reused** (decided 2026-11-21; this replaces the earlier "plain names" suggestion). That means the landing page and its animations, the lobby, the pixel characters, and the results and ledger flow, adapted to Vanguard. Proposed mapping (to confirm): Knock = keyboard-only, Echo = screen-reader, Iris = magnifier, Cog = unrestricted control agent, plus a new character for the first-time visitor. Dash and Pell could stand for the mobile and slow-network conditions. Tobin is not used for now. The frontend therefore stays Next.js/React (TypeScript, copied from Sentinel with provenance noted); the core backend is Python.
  - **New flow:** landing → lobby (pick characters) → **pick site** → start trial → live view → results / ledger. In A3 the only site is **Tallowmere, extracted from Sentinel into a standalone test site**. In A4 the 4–8 new sites are added as options, together with "test on my own site" (verification snippet).
  - **Model providers behind one interface.** The deployed app offers Gemini only. A local run lets the user pick Gemini, a local model (Ollama) or other APIs (Groq, OpenAI, etc.) for comparisons.
  - **Fine-tuning is in the plan** (A4 work, not A3). Compute: the team's RTX 3050 **4 GB laptop** GPU, or Kaggle's free GPUs (reported at about 30 h/week, P100 or 2×T4; check the account page). Weights may be stored on the Hugging Face Hub. **No paid GPU time or paid online services.**
  - **Roles**: FaatehHaneef is the unofficial scrum master and owns architecture, design decisions and the foundational setup; task breakdown for the other two members comes later.

### 6.2 Open (ask the user; do not guess)
1. Approval: the user confirmed on 2026-11-21 that there is tentative approval to submit A3, with final approval to follow after the formal A3 proposal is submitted. Include the tentative-approval email in the A3 package as evidence `[doc: A3, Section 9; R3, A1]`.
2. Title: the user confirmed on 2026-11-21 that it is registered in the Project Titles sheet `[doc: R3, A3]`.
3. **Stack and code base**: extend Sentinel (TS), keep Python for analysis as a separate service, or rebuild. The planning chat recommended building on Sentinel because of the one-day deadline. That recommendation predates the finding that Sentinel's engine is an in-page scripted walker with no external browser driver and no LLM agent loop (Section 3.2); the reusable parts are the store, checkout, guards and Gemini client.
4. Browser automation library: answered for Sentinel (in-page DOM calls; Playwright only in tests). Still open for Vanguard (Playwright is the obvious candidate for real key events and `ariaSnapshot()`).
5. Store task list (how many, which).
6. Second AI task with alternatives (Section 4.5).
7. Deterministic rule for the first-time-shopper persona (Section 4.1).
8. Seed-funding sources and Lean Canvas.
9. A4 deployment plan.
10. Whether to add LoRA or other fine-tuning later.
11. Ownership split among the three members, and real commits from each in time for A3.
12. Provenance wording for reused code; licence for Synthetic Users code (it has none).
13. ~~Git email visibility~~: resolved 2026-11-21, commits use the GitHub noreply address.

### 6.3 Practical rules `[context-only]`
- Keep a running `AI_USE.md` (tools and what they were used for); the declaration is required for A3 and A4, and a missing one costs up to 3 marks `[doc: A3, Section 9; R3, Section 7]`.
- Secrets only in `.env`; commit `.env.example`. Payments sandbox only.
- Keep functions small and documented so every member can explain them in the viva.
- Do not assume the reference repositories build or pass tests until they are run, and only run them when the user asks.
- Likely build order after the user says "go": leakage table → persona spec and action gate → keyboard-only persona end to end → checker → baseline vs code-enforced → labelled set → 13-section proposal → slides or dashboard.

### 6.4 Rejected (do not re-propose) `[context-only]`
- "ClassTwin" (exam simulation from graded student answers, Mohler / ASAP-SAS): dropped for accessibility testing.
- "HoneyArena" (AI attacker vs honeypot): hosted models would refuse the attacker role.
- "PriorArt" patent search: dropped (it also relied on PatentsView, shut down 2026-03-20).
- Fine-tuning on real student answers as a comparison: already published.
- The name "Sentinel" and the dropped names Limitwise, Scout, Limen.

---

## 7. Where the sources disagree

| # | Planning notes say | Source says | Resolution |
|---|---|---|---|
| 1 | Sentinel is "a base for ... the browser engine and journeys" and "Cog (an AI agent)"; it "runs Cog's agent" | Shoppers are scripted. The engine is an in-page script using DOM calls. Cog's "agent" is a single Gemini buy/no-buy decision, after which the server places the order `[repo: sentinel/engine/, lib/ai/cog.ts]` | Treat the simulated-user agent loop and the external browser executor as **new work** |
| 2 | "Check which browser automation library the engine actually uses before assuming Playwright" | None in the engine; Playwright only for e2e tests `[repo: sentinel/playwright.config.ts]` | Vanguard has to add a driver |
| 3 | Sentinel `lib/guards` as "guards and allow-lists (action gate, sandbox-only payments)" | The allow-list checks trial *origins*; the sandbox guard checks an env variable `[repo: sentinel/lib/guards/]` | A per-step action gate and a payment-domain allow-list are new |
| 4 | Sentinel "100 unit tests" (from its README) | 82 `it`/`test` declarations found by grep; not run `[repo: sentinel/tests/]` | Do not repeat "100" until the tests are run |
| 5 | Commits in the "final repo" by every member | Commits from every member are already required for **A3** `[doc: A3, Section 7 item 5; R3, C6]` | Plan member commits before tomorrow's submission |
| 6 | A4 engineering list omits branching | "Using branches and pull requests for major changes" `[doc: A4, Section 3; R4, C1]` | Use feature branches and PRs from the start |
| 7 | Step 0: commit `CLAUDE.md` and `Project Context.md`; ask whether `docs/` is ignored | The user decided (2026-11-21): ignore the 8 current files in `docs/`, keep the folder tracked, and commit `Vanguard.md` later | Followed the user's decision |
| 8 | Synthetic Users' diversity analysis can be "extended" | It holds categorical single-answer measures only (distinct, top-1 share, entropy, Wilson CI) `[repo: synthetic-users/synthusers/analyze.py]` | Sequence measures are new work |
| 9 | Digest: proposal evaluation plan for Pure covers "peer usability test" and "target demo track" | A3 Table 3 says this; the rubric's B10 Pure descriptor lists requirements, the evaluation/test plan and the documentation plan, without naming the usability test or demo track `[doc: A3, Table 3; R3, B10]` | Include both anyway; the assignment text governs |
| 10 | Digest: "13 sections ... read the exact list" | Matches, with one detail: the track type is to be stated *below the title* `[doc: A3, Table 3 row 13]` | Put "Track: Pure Product" under the title |
| 11 | Chameleon's Limit "also proposes Coverage, Uniformity and Complexity metrics with a released toolkit" | The abstract names the three metrics but mentions no toolkit `[arXiv:2604.24698 abstract, checked 2026-11-21]` | Cite the metrics; do not claim a toolkit |
| 14 | AgentPersonaBench "describes capability intrusion" | The term is not in the abstract `[arXiv:2610.04379 abstract, checked 2026-11-21]` | Check the body before using the term |
| 15 | Playwright `page.accessibility` "deprecated (one source says removed in 1.57)" | The docs page now returns 404 `[checked 2026-11-21]` | Use `ariaSnapshot()` only |
| 16 | Sentinel used for "storage" | The server store is in-memory only; trial records live in the browser `[repo: sentinel/lib/storage/]` | Persistent trace storage is new work |
| 12 | Gemini model unspecified | Sentinel defaults to `gemini-flash-latest` / `gemini-flash-lite-latest`; Synthetic Users used `gemini-3.6-flash` `[repo: sentinel/lib/ai/gemini.ts; synthetic-users/synthusers/generate.py]` | Pin and log exact model versions (needed for A4 observability) |
| 13 | Rubric weights "per the user's earlier reading, verify" | All the weights and deductions in the digest match the rubric forms `[doc: R3, R4]` | No change |

Minor: the FACET R&D sample's Section 1 says "The project follows the Pure Product track", which looks like a copy error in the sample `[doc: FR, Section 1]`. It has no effect on Vanguard.
