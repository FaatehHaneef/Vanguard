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

> Draft for the team, 2026-11-22. Values marked ⟨TBD⟩ are filled in from the first baseline batch. Items marked ⟨decide⟩ are open decisions listed in `Vanguard.md`, Section 6.2.

## 1. Title and Team

The proposed product is **Vanguard**, a tool that audits AI agents used as stand-ins for real users. The project follows the Pure Product track: the aim is a complete, reliable, deployed product, not a research result. Design choices are still justified by comparing alternatives for the main AI tasks (Section 6). The team has three members, whose roles are given in Section 12; every member works on both AI and engineering parts.

## 2. Problem and Motivation

Product teams increasingly try AI agents as early, cheap stand-ins for real users: an agent told to behave like "a shopper who only uses a keyboard" or "a blind shopper using a screen reader" is sent through a website to find problems before anyone is recruited for testing. Persona-driven usability agents [4] and agents that use a screen-reader proxy to find accessibility faults in apps [5] are examples of this direction.

Such simulations are only useful if the agent actually stays within the limits it was given, and in practice it often does not. An agent told it cannot use a mouse may still "click"; an agent told it is blind may still describe colours or positions it could not perceive; an agent playing a first-time visitor may type a product code it could never have seen. We call this **leakage**. Published work reports the same tendency for vision: "VLMs tend to infer beyond the specified vision ability when given minimal prompts" [2]. A related problem is **collapse**: supposedly different personas behaving alike [3]; in the team's earlier project, Gemini given ten different personas named only 9 distinct games across 178 answers.

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
  A[Pick characters<br/>lobby] --> B[Pick site, task,<br/>enforcement, conditions]
  B --> C[Batch starts:<br/>balanced runs]
  C --> D[Each step: observe →<br/>model proposes action →<br/>gate / verifier → browser]
  D -->|recorded| E[(Trace store)]
  E --> F[Checker and metrics<br/>(code)]
  F --> G[Live view, explanation,<br/>comparison, dashboard]
  E --> H[Blind labelling desk]
  H --> F
```

## 4. System Components and Architecture

```mermaid
flowchart TB
  subgraph Web["Web app (Next.js, React)"]
    L[Lobby / site picker] --- R[Run view and live view] --- D[Results dashboard] --- LB[Labelling desk]
  end
  subgraph API["Backend (FastAPI, Python)"]
    S[Run and batch controller]
    AG[Agent loop]
    GT[Action gate<br/>rules S0, H1, H4a, H4b]
    VF[Verifier agent]
    CK[Leakage checker<br/>+ metrics, failures]
    EX[Explanation generator]
  end
  subgraph Worker["Browser executor (Playwright, Chromium)"]
    OB[Observation builders:<br/>full view, accessibility tree,<br/>magnifier window]
    EV[Trusted input recorder,<br/>network allow-list, screenshots]
    HUD[Character overlay<br/>(decoration only)]
  end
  M[(Gemini API<br/>or OpenAI-compatible model)]
  DB[(PostgreSQL)]
  SITE[Test sites, e.g. Tallowmere]
  BT[Braintree sandbox]
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
| Simulated-user agent | Fixed task × persona × run set on test sites (A3: Tallowmere pilot, 3 tasks) | Task success, steps per task, tool-call validity, stuck rate, executed and attempted leakage per limit | Prompt-only vs gate (and later bounded perception, verifier) |
| Leakage checker (deterministic, validated against people) | ≥ 50 labelled steps (A3), ≥ 100 (A4), two labellers | Cohen's kappa between labellers (target ≥ 0.6); checker vs agreed labels: kappa, precision, recall | Labellers' agreement as the ceiling |
| Verifier agent | Same labelled steps | Precision and recall of refusals vs hard rules and labels | Gate (rules) |
| Explanation generator | ≥ 50 explanations | Rejection rate of the checked mode, factual errors in a human-checked sample | Template |
| Every AI component | All runs | Latency p50 and p95 per step, tokens and cost per run, model failure rate | — |

Error analysis groups every failing run by cause, computed by code (model unavailable, run error, persona leak, invalid output, refusal loop, action errors, stuck, step limit, gave up, wrong answer); at least ten failures are read and described with planned fixes. **First results** (to be filled from the baseline batch): success prompt-only ⟨TBD⟩ vs gate ⟨TBD⟩; runs with an executed leak ⟨TBD⟩ vs ⟨TBD⟩; latency p50/p95 ⟨TBD⟩; cost per run ⟨TBD⟩; kappa ⟨TBD⟩.

**User-level benefit.** For a site owner, the test is whether Vanguard finds the planted barriers that matter to each persona (for example the cart's quantity buttons that a keyboard user cannot reach) and explains them correctly.

## 9. Deployment Plan

Vanguard is deployed with Docker on a cloud VPS, not on a serverless host, because the worker needs a full browser. Docker Compose runs the database, API with the Playwright worker, web app and test sites; the same Compose file runs everything locally. Test sites are ordinary standalone websites and can also be deployed separately (for example on Vercel), in which case Vanguard's allowed origins are set to their public addresses. Secrets live in environment files that are never committed. ⟨decide: VPS provider and the A4 deployment date⟩

## 10. Funding and Business Model

**Target customers.** Small product and UX teams who want early accessibility and usability checks without a large research budget, and university HCI and accessibility researchers who run simulated-user studies and need evidence that their simulations stayed in character.

**Operating cost estimate (pilot).** Model use dominates. Gemini 3.8 Flash costs $0.75 per million input tokens and $3.75 per million output tokens through 31 December 2026, doubling on 1 January 2027, and has a free tier [7]. An estimated 3,000 input and 100 output tokens per step and 25 steps per run give about $0.065 per run at current prices (⟨TBD⟩: replaced by the measured cost per run). A pilot of 2,000 runs per month costs about $130 in model use, plus a VPS of roughly $20–40 per month. Local models remove the model cost for teams with their own hardware.

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

⟨decide: the split above is proposed in `Vanguard.md` §4.9 and not yet confirmed by the team⟩

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

**Evaluation and test plan.** Functional tests: 80 automated backend tests (including 8 in a real Chromium covering observation, focus visibility, pointer evidence, navigation, the overlay, conditions, screen reader and magnifier), all passing in CI; the web app, overlay and test site are type-checked, linted and built in CI. AI quality: Section 8. Latency and cost: per step and per run, p50 and p95. Safety: the network allow-list and sandbox tests above, plus a prompt-injection set of at least 20 hostile page texts (A4). Peer usability test: two peers complete a trial and read its report (A4).

**Documentation plan (A4).** README with setup and deployment; architecture document; API documentation (OpenAPI, generated); the leakage specification and labelling guide (already written); data cards (written); an AI card per component; PRD with these acceptance criteria; user guide; system demonstration paper.

**Target demonstration track.** A system demonstration paper in the style of the ACL or EMNLP demonstration tracks. ⟨decide⟩

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
