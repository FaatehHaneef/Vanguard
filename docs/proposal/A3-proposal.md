# Vanguard: Auditing LLM-Simulated Users with Enforced Limits

**Project track: Pure Product**

| Item | Details |
|---|---|
| Product name | Vanguard |
| One-line description | Runs AI "simulated users" with stated limits (for example a keyboard-only shopper) through real websites, enforces and checks those limits in code, and reports where the simulation broke them |
| Project track | Pure Product |
| Group members | Syed Muhammad Faateh Haneef (23i-0688), Abdul Hadi (23i-0676), Ibrahim Malik (23i-0694) |
| Course | AI-4009 Generative AI, FAST-NUCES Islamabad, Section A |
| Repository | https://github.com/FaatehHaneef/Vanguard |

## 1. Title and Team

The proposed product is **Vanguard**, a tool that audits AI agents used as stand-ins for real users. The project follows the Pure Product track: the aim is a complete, reliable, deployed product, not a research result. Design choices are still justified by comparing alternatives for the main AI tasks (Section 6). The team has three members, whose roles are given in Section 12; every member works on both AI and engineering parts.

## 2. Problem and Motivation

Product teams increasingly try AI agents as early, cheap stand-ins for real users: an agent told to behave like "a shopper who only uses a keyboard" or "a blind shopper using a screen reader" is sent through a website to find problems before anyone is recruited for testing. Persona-driven usability agents [4] and agents that use a screen-reader proxy to find accessibility faults in apps [5] are examples of this direction.

Such simulations are only useful if the agent actually stays within the limits it was given, and in practice it often does not. An agent told it cannot use a mouse may still "click"; an agent told it is blind may still describe colours or positions it could not perceive; an agent playing a first-time visitor may type a product code it could never have seen. We call this **leakage**. Published work reports the same tendency for vision: "VLMs tend to infer beyond the specified vision ability when given minimal prompts" [2]. Public data shows how far apart the behaviours are. In the Reduced A11y-CUA logs [1], by our count, blind and low-vision users made 0.1% of their actions with a pointer and 58.4% of their key presses were Tab or arrow keys, against 60.8% pointer actions for sighted users; the two computer-use agents in the dataset used the pointer for 15.0% (Claude Sonnet 4.5) and 89.2% (Qwen3-VL-32B) of their actions under a magnifier condition (`docs/results/a11y-cua-reference.md`; desktop tasks, not web shopping). A related problem is **collapse**: supposedly different personas behaving alike [3]; in the team's earlier project, Gemini given ten different personas named only 9 distinct games across 178 answers.

Today this is handled by writing the limits into the prompt and hoping, or by reading transcripts by hand. Neither scales, and neither produces evidence. Vanguard addresses the gap with three things that existing tools do not combine: limits written as a structured specification; enforcement of those limits in code at the point where the agent acts (and, as alternatives, through what the agent may perceive and through a second checking model); and a deterministic audit that reports, step by step, where a simulation broke its limits.

Generative AI is needed for the simulated user itself: it must read unstructured, changing web pages and choose its next action, which is what tool-calling language models do. Everything that must be exact (whether a step leaked, counts, rates, scores, payment safety) is deterministic code; no model counts, scores or checks a rule.

**Positioning.** Vanguard is early pre-testing. It does **not** replace testing with disabled people and does not claim to simulate them. Reports state this limit.

| Existing approach | What it does | What it lacks for this problem |
|---|---|---|
| Prompt-only persona agents (e.g. [4]) | Describe the persona and its limits in the prompt | No enforcement, no step-level evidence of whether the limits held |
| Screen-reader-proxy agents (e.g. [5]) | Give the agent a screen-reader-like interface for one modality | Specific to one modality and one platform; no general limit specification or leakage audit |
| Automated accessibility checkers (axe, Lighthouse) | Rule checks on page markup | No task-level behaviour; cannot tell whether a keyboard user can actually complete a purchase |
| **Vanguard** | Limits as a spec, enforced in code, every step audited, enforcement methods compared on the same tasks | Not a substitute for real users (stated limit) |

## 3. Product Overview and Features

From the user's view, Vanguard is a web app with a game-like front end. The user picks a party of characters, each a persona (Knock: keyboard-only; Echo: screen-reader user; Iris: magnifier user; Wren: first-time visitor; Cog: an unrestricted control agent), picks a site and a task, chooses how the limits are kept, and starts a trial. Each character then shops on the real site in a real browser; the user watches a live view with the character walking to each element it acts on, and afterwards sees a step-by-step trace, a plain-language explanation, the checker's findings, and a comparison table across characters and enforcement methods.

**Core features (must have):**
1. Persona specifications built from limits L1–L4 (no pointer; accessibility tree only; magnified view; first-time-visitor knowledge), stored as validated JSON.
2. A simulated-user agent driving Chromium from outside the page through tool calls, with real key presses and clicks.
3. Enforcement options: prompt-only (baseline), a code-enforced action gate, bounded perception, and a verifier agent.
4. A deterministic leakage checker sharing its rules with the gate, plus browser evidence (trusted input events) and planted honeytokens.
5. Metrics per run and per group: executed and attempted leakage, success, steps, stuck rate, latency, tokens and cost, with 95% intervals.
6. Balanced, resumable batches of repeated runs; live view; results dashboard; blind labelling desk with inter-rater agreement.
7. Safety: the browser can reach only allowed origins and the payment provider's sandbox hosts.

**Extended features (if time permits):** testing an owner's own site after a verification snippet; four to eight further test sites; diversity metrics across personas; PDF and email reports; a fine-tuned local model as a further enforcement option.

**End-to-end workflow.**

```mermaid
flowchart LR
  A["Pick characters<br/>lobby"] --> B["Pick site, task,<br/>enforcement, conditions"]
  B --> C["Batch starts:<br/>balanced runs"]
  C --> D["Each step: observe →<br/>model proposes action →<br/>gate / verifier → browser"]
  D -->|recorded| E[("Trace store")]
  E --> F["Checker and metrics<br/>(code)"]
  F --> G["Live view, explanation,<br/>comparison, dashboard"]
  E --> H["Blind labelling desk"]
  H --> F
```

## 4. System Components and Architecture

```mermaid
flowchart TB
  subgraph Web["Web app (Next.js, React)"]
    L["Lobby / site picker"] --- R["Run view and live view"] --- D["Results dashboard"] --- LB["Labelling desk"]
  end
  subgraph API["Backend (FastAPI, Python)"]
    S["Run and batch controller"]
    AG["Agent loop"]
    GT["Action gate<br/>rules S0, H1, H4a, H4b"]
    VF["Verifier agent"]
    CK["Leakage checker<br/>+ metrics, failures"]
    EX["Explanation generator"]
  end
  subgraph Worker["Browser executor (Playwright, Chromium)"]
    OB["Observation builders:<br/>full view, accessibility tree,<br/>magnifier window"]
    EV["Trusted input recorder,<br/>network allow-list, screenshots"]
    HUD["Character overlay<br/>(decoration only)"]
  end
  M[("Gemini API<br/>or OpenAI-compatible model")]
  DB[("PostgreSQL")]
  SITE["Test sites, e.g. Tallowmere"]
  BT["Braintree sandbox"]
  Web <--> API
  AG <--> M
  VF <--> M
  EX <--> M
  AG --> GT --> Worker
  Worker <--> SITE
  SITE --> BT
  API <--> DB
```

| Component | Technology | AI or deterministic |
|---|---|---|
| Simulated user (agent loop) | Gemini with forced function calling; one tool call per step | **AI** |
| Verifier agent (option 4) | Second model call, JSON output | **AI** |
| Explanation generator | Model writes text from facts computed by code; template fallback | **AI** (wording only) |
| Observation builders | Playwright, in-page scripts, Chrome accessibility tree | Deterministic |
| Action gate, leakage checker, metrics, failure grouping | Python rules shared by gate and checker | Deterministic |
| Batches, store, API | FastAPI, SQLAlchemy, PostgreSQL | Deterministic |
| Web app | Next.js, React, Tailwind | Deterministic |
| Test site Tallowmere | Next.js shop, Braintree sandbox checkout | Deterministic (external integration) |

Deployment uses Docker Compose with five services: database, API with the Playwright worker image, web app, and the test sites. Continuous integration runs linting, the backend tests (including tests in a real Chromium), the web and site builds, and the Compose build on every push.

## 5. Generative AI Techniques

| Technique (A3 Table 4) | Where it is used | Why |
|---|---|---|
| Foundation model API, function calling | The simulated user chooses each browser action as one forced tool call from a typed tool vocabulary | Actions must be machine-checkable: the gate and checker read the tool name and arguments, not free text |
| **Agents and tool use** (the required agentic component) | Observe → propose → gate → execute loop with keyboard, pointer, screen-reader, magnifier, navigation and control tools | The task is multi-step interaction with live pages |
| Structured output and reliability | Pydantic-validated actions, verifier decisions and explanations; schema-invalid replies recorded as model failures; key and model fallback | Reliability and measurable failure rates |
| Prompt engineering | Versioned system and step prompts (persona, task, short history, current perception); prompt-injection rule for page text | Reproducibility; logged with every run |
| Open-source / local models | OpenAI-compatible provider (Ollama, LM Studio, Groq) in local runs | Model alternative (Section 6) |
| Integrations | Braintree sandbox checkout driven by the agent; PostgreSQL | Required external integration |
| Evaluation and observability | Labelled test set, kappa, per-step traces with latency, tokens and cost | Quantitative evaluation from the start |

Candidate models: Gemini Flash (the deployed default; current model `gemini-3.8-flash`) and Gemini Flash-Lite as a cheaper tier; local open models (for example Qwen family through Ollama) for the model comparison; a LoRA fine-tune of a small open model is a stretch goal for A4.

## 6. Technical Alternatives

**AI task 1: keeping the simulated user within its limits (the core comparison).** Four options run on identical tasks with repeated runs:
1. *Prompt-only* (baseline): limits are described in the prompt only.
2. *Code-enforced gate*: forbidden actions are refused before they reach the browser, and the agent is told why.
3. *Bounded perception*: the agent only receives what its user could perceive (accessibility tree for the screen-reader persona, a 400% magnifier window for the low-vision persona).
4. *Verifier agent*: a second model call checks each proposed action against the persona before it runs.

Options can be combined. The choice is made on executed and attempted leakage, task success, steps, stuck rate, latency and cost, with 95% intervals.

**AI task 2: explaining a run.** (a) template only; (b) model text; (c) model text checked by code, rejected if it contains any number not in the computed facts or skips a finding. Chosen on correctness (human check of a sample), rejection rate and latency.

**AI task 3: the agent's model.** Gemini Flash vs Flash-Lite vs a local open model, on the same tasks; chosen on success, leakage and cost.

**AI task 4: the verifier itself** is measured against the hard rules (precision and recall of its refusals).

## 7. Data

- **Our own traces (main data).** Every step stores what the persona perceived, the proposed action and rationale, the gate and verifier decisions, browser input events, URL, focus, target box and timings. Sites are split before any run into train, dev and test groups; prompts are written against train and dev sites, and headline results and labels come from test sites only. Tallowmere was written by the team, so it is a dev site.
- **Labels.** Two members label sampled steps independently with a written guide, without seeing the checker's output (Section 8).
- **Public datasets (verified, stored outside the repository).** Reduced A11y-CUA [1] (CC BY 4.0; sessions of blind and low-vision users, sighted users and two agents under screen-reader and magnifier conditions), used for reference statistics only, never training; Mind2Web (CC BY 4.0, 1,009 tasks) for possible general web-navigation fine-tuning; a sample of WebWorldData (Apache 2.0). Data cards are in `docs/data-cards.md`.
- **Privacy.** Test sites are fictional with fake accounts; payments run in the sandbox only, enforced in code. A11y-CUA comes from a user study: only aggregate statistics are used and no individual session is quoted. No personal data from users of Vanguard is collected beyond their own runs.

## 8. Evaluation Plan

| Component | Test set | Metrics | Baseline |
|---|---|---|---|
| Simulated-user agent | Fixed task × persona × run set (A3: 16 runs on Tallowmere and Willowbrook, 2 tasks × 2 personas × 2 options × 2 repeats) | Task success, steps per task, tool-call validity, stuck rate, executed and attempted leakage per limit | Prompt-only vs gate (and later bounded perception, verifier) |
| Leakage checker (deterministic, validated against people) | 60 labelled steps in A3 (≥ 100 in A4), two labellers | Cohen's kappa between labellers (target ≥ 0.6); checker vs agreed labels: kappa, precision, recall | Labellers' agreement as the ceiling |
| Verifier agent | Same labelled steps | Precision and recall of refusals vs hard rules and labels | Gate (rules) |
| Explanation generator | ≥ 50 explanations | Rejection rate of the checked mode, factual errors in a human-checked sample | Template |
| Every AI component | All runs | Latency p50 and p95 per step, tokens and cost per run, model failure rate | — |

Error analysis groups every failing run by cause, computed by code (model unavailable, run error, persona leak, invalid output, refusal loop, action errors, stuck, step limit, gave up, wrong answer); at least ten failures are read and described with planned fixes. **First results (A3; full tables in `docs/results/a3-results.md`, regenerated by `backend/scripts/a3_results.py`).** Model gemini-3.6-flash; Tallowmere `cheapest` and Willowbrook `wb-callback`; 16 runs, 80 steps, 12-step cap.

| Keyboard-only persona | Success | Runs with an executed leak | Mean steps |
|---|---|---|---|
| Prompt-only | 4 of 4 | **4 of 4** (it clicked with a mouse every time) | 5.0 |
| Gate | 4 of 4 | **0 of 4** (3 attempted clicks refused, in 3 runs; it then finished by keyboard) | 6.5 |

The control persona leaked in every run under both options (its reference rate). Step latency p50 5.8 s and p95 18.4 s; about 1,900 input tokens per step; $0 on the free tier, about $0.008 per run at the paid list price. Labelled test set: 60 steps from the real runs labelled independently by two members; Cohen's kappa 1.00, and the checker matched the agreed labels with kappa 1.00, precision and recall 100%. Because this sample is dominated by unambiguous input-type cases, A4 adds harder information-leak cases (preview personas, honeytokens). Failure analysis over all 29 A3 runs with the real model: 14 failing runs, 8 stopped by model quota (planned fix: several actions per model call and local models for volume) and 6 keyboard-only runs that clicked under prompt-only (the leak the gate exists to stop). In A3 the agent and the checker are evaluated; the verifier and the explanation generator are implemented and integrated, and their evaluation on labelled sets is planned for A4.

**User-level benefit.** For a site owner, the test is whether Vanguard finds the planted barriers that matter to each persona (for example the cart's quantity buttons that a keyboard user cannot reach) and explains them correctly.

## 9. Deployment Plan

Vanguard is deployed with Docker on a cloud VPS, not on a serverless host, because the worker needs a full browser. Docker Compose runs the database, API with the Playwright worker, web app and test sites; the same Compose file runs everything locally. Test sites are ordinary standalone websites and can also be deployed separately (for example on Vercel), in which case Vanguard's allowed origins are set to their public addresses. Secrets live in environment files that are never committed. Concretely, for A4: one cloud VPS with at least 4 GB of RAM (for example DigitalOcean or Hetzner) running the Compose stack behind HTTPS; the agent model through the Gemini API (Google-hosted); local open models through Ollama on a team laptop or Kaggle's free GPUs for bulk evaluation runs. For A3 the system runs reproducibly from the repository (`docker compose up`).

## 10. Funding and Business Model

**Target customers.** Small product and UX teams who want early accessibility and usability checks without a large research budget, and university HCI and accessibility researchers who run simulated-user studies and need evidence that their simulations stayed in character.

**Operating cost estimate (pilot).** Model use dominates. Gemini 3.8 Flash costs $0.75 per million input tokens and $3.75 per million output tokens through 31 December 2026, doubling on 1 January 2027, and has a free tier [7]. Measured in A3: about 1,900 input and 34 output tokens per step, so about $0.0016 per step; a typical 20-step task costs about $0.03. A pilot of 2,000 runs per month costs about $60 in model use (about $120 after the January price change), plus a VPS of roughly $20–40 per month. Local models remove the model cost for teams with their own hardware.

**Revenue model.** Freemium: free runs on the public test sites; paid plans per monthly run volume for testing one's own sites; an institutional licence for research groups and courses.

**Seed funding sources (researched 2026-11-22; to be re-checked before applying).**
- *National Incubation Center (NIC) Islamabad*, funded through the Ignite National Technology Fund. Cohort 6 accepted tech-enabled startups at idea, MVP or growth stage, solo founders or teams with at least one Pakistani national, with AI among the listed sectors; its window closed on 21 September 2026, and Cohort 7 dates are not yet announced [8]. Other centres (for example NIC Peshawar) were reported open in October 2026.
- *Google for Startups Cloud Program*, which offers cloud and Gemini credits in tiers for early and funded startups, with a larger tier for AI-first companies [9]. Credit amounts and eligibility were reported only by unofficial guides and must be confirmed on Google's official page.

**MVP.** One persona pair (keyboard-only and control), one test site, prompt-only vs gate, with the live view, checker report and comparison table: this exists today.

**Lean Canvas.**

| Problem | Solution | Unique value proposition | Unfair advantage | Customer segments |
|---|---|---|---|---|
| AI simulated users break their stated limits unseen; results cannot be trusted; manual transcript review does not scale | Limits as specs, enforced in code; every step audited; methods compared on the same tasks | Evidence, step by step, of whether a simulated user stayed in character, before acting on its findings | A shared rule core for enforcement and audit, planted honeytokens, and a test-site kit | Small product and UX teams; HCI and accessibility researchers; courses |
| **Key metrics** | runs per month, share of runs with executed leakage found, checker agreement with people | **Channels** | accessibility and HCI communities, university labs, demo tracks | |
| **Cost structure** | model tokens, VPS, maintenance of test sites | **Revenue streams** | freemium plans by run volume; institutional licence | |

## 11. Risks and Responsible AI

- **Over-claiming.** The biggest risk is that a simulated persona is mistaken for a real disabled person's experience. Every report states that Vanguard is pre-testing and not a substitute for testing with disabled people.
- **Prompt injection from pages.** Page text is content, never instructions; the prompt says so, the gate limits what any action can do, and a set of injected pages is tested (Section 13).
- **Payments.** The browser can reach only allowed origins and sandbox payment hosts; this is enforced by the network filter and the gate, and tested.
- **Model failures and hallucination.** Invalid tool calls are recorded as model failures, never silently replaced. Explanations only word facts computed by code; the checked mode rejects text with numbers not in those facts.
- **Measurement validity.** The checker is validated against two human labellers; preview personas are marked "not validated" until their checks are complete.
- **Human approval.** Testing a site that the team does not own requires the owner's consent, given by installing a verification snippet (A4).
- **Security and secrets.** Keys stay in untracked environment files; the repository history is scanned before each push.

## 12. Work Plan and Team Roles

| Member | AI work | Engineering work |
|---|---|---|
| Syed Muhammad Faateh Haneef | Agent loop and prompts, enforcement options, the A3 comparison runs | Architecture, executor and worker, gate and rules, API, CI, deployment |
| Abdul Hadi | Explanation generator (alternative c), perception and prompts for the preview personas | Results and live-view polish; 2–4 test sites |
| Ibrahim Malik | Verifier evaluation, labelling and kappa, failure analysis | Leakage checker and metrics extensions, functional tests; 2–4 test sites |

| Milestone | Content |
|---|---|
| A3 (2026-11-22) | Proposal; end-to-end product on Tallowmere; prompt-only vs gate baseline; ≥ 50 labelled steps with kappa; functional tests |
| A3 + 1 week | Further test sites (different frameworks and domains); bounded-perception and verifier batches |
| A3 + 2 weeks | Full checks for the preview personas; model comparison; explanation evaluation |
| A3 + 3 weeks | Own-site testing with verification snippet; reports; deployment |
| A4 | Hardening, ≥ 100 labelled steps per component, demonstration paper, documentation, pitch |

## 13. Track-Specific Plan (Pure Product)

**Requirements and acceptance criteria.**

| # | Requirement | Acceptance criterion |
|---|---|---|
| R1 | A persona's limits are enforced under the gate | 0 executed hard-rule violations across all gated runs |
| R2 | Every step is recorded and auditable | Each step has observation, proposal, gate decision, input events and timing; checker output is reproducible from the store |
| R3 | The checker agrees with people | Kappa between checker and agreed labels ≥ 0.6 on the test set |
| R4 | The browser never leaves allowed origins | No request to a non-allowed host succeeds (automated test) |
| R5 | Payments are sandbox only | The shop refuses to start with a non-sandbox payment environment; no live payment host is reachable |
| R6 | Focus is reported only when it is visible | The full-view observation omits focus on elements whose focus style is removed (automated test) |
| R7 | Results are reproducible | Same config and seed give the same scripted traces; batches resume without repeating finished runs |
| R8 | The decoration never affects a run | The overlay never appears in observations, the accessibility tree or recorded input events (automated test) |

**Evaluation and test plan.** Functional tests: 208 automated tests, including 10 in a real Chromium (observation, focus visibility, pointer evidence, navigation, the overlay, conditions, screen reader, magnifier, key repeat, focus containers) and the prompt-injection set; the recorded functional-test run passed 206 of 206 cases (100%, `docs/results/functional-tests.md`), and CI runs every test on each push. The web app, overlay and test sites are type-checked, linted and built in CI. AI quality: Section 8. Latency and cost: per step and per run, p50 and p95. Safety: the network allow-list and sandbox tests above, plus a prompt-injection set of at least 20 hostile page texts (A4). Peer usability test: two peers complete a trial and read its report (A4).

**Documentation plan (A4).** README with setup and deployment; architecture document; API documentation (OpenAPI, generated); the leakage specification and labelling guide (already written); data cards (written); an AI card per component; PRD with these acceptance criteria; user guide; system demonstration paper.

**Target demonstration track.** ACL System Demonstrations (with EMNLP System Demonstrations as the alternative).

## References

[1] Mohanbabu, Natalie, Kim, Guo, Pavel. *A11y-CUA Dataset: Characterizing the Accessibility Gap in Computer Use Agents.* arXiv:2602.09310 (CHI '26).
[2] Natalie, Xu, Chang, Mihalcea, Guo. *Not There Yet: Evaluating Vision Language Models in Simulating the Visual Perception of People with Low Vision.* arXiv:2508.10972.
[3] Xiao, Zhang, Yang, Xuan, Huang. *The Chameleon's Limit: Investigating Persona Collapse and Homogenization in Large Language Models.* arXiv:2604.24698.
[4] Touir, Ktata, Soui. *Grounding Persona-Driven Usability Simulation in Established Standards.* CHI '26 Workshop on Responsible Use of AI Personas, CEUR-WS Vol-4249, paper 4.
[5] Zhong, Chen, Win Kyi, Li, Fogarty, Wobbrock. *TaskAudit: Detecting Functiona11ity Errors in Mobile Apps via Agentic Task Execution.* arXiv:2510.12972 (CHI 2026).
[6] Deng et al. *Mind2Web: Towards a Generalist Agent for the Web.* arXiv:2306.06070.
[7] Google. *Gemini API pricing.* https://ai.google.dev/gemini-api/docs/pricing (read 2026-11-22).
[8] startup.pk. *NIC Islamabad's Cohort 6 applications are open.* https://startup.pk/nic-islamabads-cohort-6-applications-are-open-heres-everything-you-need-to-apply/ ; techx.pk, *NIC Islamabad Cohort 6 window shuts* (read 2026-11-22).
[9] Google. *Google for Startups Cloud Program.* https://cloud.google.com/startup (terms to be confirmed; secondary summary read 2026-11-22).

## Appendix: AI tool declaration

As required by Assignment 3, Section 9. Kept in the repository as `AI_USE.md`; runtime use of AI inside the product is described in Sections 4 and 5.

| Date | Member | Tool | Used for | Checked by |
|---|---|---|---|---|
| 2026-11-21 | Syed Muhammad Faateh Haneef | Claude Code (Anthropic) | Reading and summarising the course documents and the two earlier repositories; drafting `Vanguard.md` and `docs/leakage-spec.md`; writing the backend foundation (contracts, rules, gate, agent loop, store, API) and its tests; extracting and porting reused code from Sentinel | Design decisions made by the team; every file reviewed by Faateh; tests run locally |
| 2026-11-22 | Syed Muhammad Faateh Haneef | Claude Code (Anthropic) | Writing the Playwright executor (observation, event recording, network filter, screen-reader and magnifier perception, conditions), the character overlay, the leakage checker (H1, H3a, H4a, H4b, honeytokens), metrics, batches, labelling and agreement, failure analysis, the explanation generator and verifier, the OpenAI-compatible provider, the related web pages, tests, CI and documentation; verifying the downloaded datasets | Design decisions and scope set by Faateh; code to be reviewed by Faateh before submission; 80 automated tests run locally and in CI against a real Chromium |
| 2026-11-22 | Abdul Hadi | Claude Code (Anthropic) | Building the Northgate Library test site from `docs/tasks-A3.md` Section 1: the Vue 3 + Vite scaffold, pages, styles, catalogue data, planted barriers and honeytokens, Dockerfile, README and manifest; registering the site and its tasks in the catalog, Compose and the allowed origins; running the site checks; labelling the 60 steps of the A3 sample (`data/labels/hadi.json`) by following `docs/labelling-guide.md` | `check-site northgate --live` and `pytest -q` run locally; each task tried in Chromium with a mouse and with the keyboard only against the manifest; code and labels to be reviewed by Abdul before pushing |
| 2026-11-22 | Ibrahim Malik | Claude Code (Anthropic) | Building the Riverside Council test site (Flask templates, styles, planted barriers, honeytokens, Dockerfile, README and manifest), the 24-notice prompt-injection set, `backend/tests/test_injection.py`, the catalog and Compose entries, and the functional test table; checking the site in Chromium by keyboard and mouse; labelling the 60 steps of the A3 sample (`data/labels/ibrahim.json`) | Site design and steps from `docs/tasks-A3.md`; code to be reviewed by Ibrahim before submission; `check-site --live` (15/15) and 206 backend tests run locally. The A3 labels were made with Claude Code, so agreement involving them is not agreement between two people |
