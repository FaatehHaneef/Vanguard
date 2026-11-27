# Functional tests

Run on **2026-11-27** at commit **`0db371b`** (branch `task-evaluation`, after merging `origin/main`), Windows 11, Python 3.13.5, with Chromium installed so that the real-browser tests ran rather than skipped.

```bash
cd backend && pytest -q -rs --junitxml=test-results.xml
```

**Result: 313 of 313 test cases passed (100%); 0 failed, 0 skipped.** The 313 cases come from 197 test functions in 30 files; parametrised functions count once per case. This round's table lists one row per test file (the first round, on 2026-11-22, listed every function).

Requirements are R1 to R8 from `docs/proposal/A3-proposal.md`, Section 13:
R1 limits enforced under the gate · R2 every step recorded and auditable · R3 checker agrees with people · R4 browser never leaves allowed origins · R5 payments sandbox only · R6 focus reported only when visible · R7 results reproducible · R8 decoration never affects a run.
"—" means the file covers supporting code that no requirement names directly.

| Area | File | What it checks | Req. | Functions | Cases | Result |
|---|---|---|---|---|---|---|
| Executor | `test_playwright_executor.py` | Real Chromium: observation, focus shown only when visible, trusted pointer events, navigation, the overlay never observed, conditions, screen-reader and magnifier perception, repeated key presses | R1, R2, R6, R8 | 12 | 12 | pass |
| Agent loop | `test_agent_loop.py` | Keyboard route, gate refusals, prompt-only pointer evidence, stuck detection, unsafe navigation blocked | R1, R2, R4 | 6 | 6 | pass |
| Agent loop | `test_calls.py` | Several actions per model call: call and position recorded per step, a call cut short by a refusal, a page change or a missing element | R2, R7 | 11 | 11 | pass |
| Gate and rules | `test_rules_and_gate.py` | Hard rules H1, H4a, H4b; the gate per enforcement option; S0 for outside origins | R1, R4, R5 | 8 | 10 | pass |
| Gate and rules | `test_injection.py` | Riverside's injection notices: S0 refuses every outside address for every persona and option, H4a refuses unlinked pages | R1, R4 | 6 | 116 | pass |
| Checker | `test_checker.py` | Attempted and executed leakage, browser evidence, H3a, H4b, honeytokens, agreement with the gate, the manifest kept out of the API | R1, R2 | 12 | 12 | pass |
| Checker | `test_findings.py` | Usability findings and attribution of each failure to site, restriction or agent | R2 | 11 | 11 | pass |
| Metrics | `test_metrics.py` | Percentiles, run metrics prompt-only vs gate, cost, group metrics | R1 | 4 | 4 | pass |
| Metrics | `test_metrics_repetition.py` | Repeated attempts on hand-made steps, in run and group metrics | — | 10 | 10 | pass |
| Metrics | `test_metrics_calls.py` | Model calls vs actions with one and several actions per call | R2 | 3 | 3 | pass |
| Metrics | `test_stats_and_batch.py` | Wilson interval, entropy, balanced resumable groups, kappa, precision and recall | R3, R7 | 4 | 4 | pass |
| Evaluation | `test_evaluation_tasks.py` | Task-level scoring per task and scenario: completion with intervals, actions, calls, repeats, refusals, stuck and step-limit rates, failure causes | R2 | 8 | 8 | pass |
| Evaluation | `test_evaluation_realism.py` | Personas' input profiles vs a fake A11y-CUA folder | — | 6 | 6 | pass |
| Evaluation | `test_evaluation_diversity.py` | Edit distance, entropy, spread and navigation paths | — | 9 | 9 | pass |
| Evaluation | `test_evaluation_verifier.py` | Verifier precision, recall and false-positive rate vs agreed labels and hard rules | R3 | 7 | 7 | pass |
| Verifier | `test_verifier.py` | Verifier decisions and the verifier in the loop | R1 | 2 | 2 | pass |
| Batches | `test_batches.py` | Batches run every group and resume, preview personas, conditions, the batch API | R7 | 4 | 4 | pass |
| Labelling | `test_labels.py` | Blind items, labels and agreement, a yes needs a limit | R3 | 3 | 3 | pass |
| Labelling | `test_bundle.py` | Labelling bundles export and import intact, CLI commands | R3, R7 | 3 | 3 | pass |
| API | `test_api.py` | Health, run lifecycle, preview persona rules, sites never expose the manifest | R2 | 6 | 6 | pass |
| API | `test_live.py` | Watching a run live and replaying it step by step | R2 | 3 | 3 | pass |
| Studio | `test_studio.py` | Custom personas, sites and tasks: validation, built-ins protected, catalog lookup | — | 14 | 18 | pass |
| Catalog | `test_catalog.py` | Personas, the control, tasks on known sites, a honeytoken per limit on every test site | R3 | 5 | 5 | pass |
| Catalog | `test_groundwork.py` | Per-site catalog files, extra task files, studio hook, origins and Docker routing, route folder | R4 | 15 | 15 | pass |
| Catalog | `test_sitecheck.py` | The test-site kit checks | — | 3 | 3 | pass |
| Providers | `test_providers.py` | Tool schemas, invalid replies explained, disabled providers, Gemini keys and rate limits | R2 | 6 | 6 | pass |
| Providers | `test_openai_compatible.py` | Tool calls, bad replies and outages, JSON generation, configuration | R2 | 5 | 5 | pass |
| Explanations | `test_explain.py` | Facts from code, checked mode rejects invented numbers | — | 4 | 4 | pass |
| Failures | `test_failures.py` | Failure tagging and grouping by cause | — | 6 | 6 | pass |
| Reference data | `test_reference.py` | A11y-CUA input modalities per group | — | 1 | 1 | pass |
| **All** | **30 files** | | | **197** | **313** | **313 pass** |

**Pass rate: 313 / 313 = 100%.**

## Requirements not covered by an automated test
- **R3** is measured by labelling (Cohen's kappa between the checker and the agreed labels), not by a unit test. The tests above check only that kappa, the verifier report and the labelling workflow compute correctly.
- **R5**: the backend tests cover the S0 origin block for payment hosts. The shop's refusal to start with a non-sandbox payment environment lives in Tallowmere (`lib/guards/sandbox.ts`) and has no automated test here.
