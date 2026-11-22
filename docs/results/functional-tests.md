# Functional tests

Run on **2026-11-22** at commit **`1772fde`** (branch `feat/riverside-council`), Windows 11, Python 3.13.5, pytest 9.2.0, with Chromium installed so that the real-browser tests ran rather than skipped.

```bash
cd backend && pytest -q -rs --junitxml=test-results.xml
```

**Result: 206 of 206 test cases passed (100%); 0 failed, 0 skipped.** The 206 cases come from 94 test functions; parametrised functions count once per case.

Requirements are R1 to R8 from `docs/proposal/A3-proposal.md`, Section 13:
R1 limits enforced under the gate · R2 every step recorded and auditable · R3 checker agrees with people · R4 browser never leaves allowed origins · R5 payments sandbox only · R6 focus reported only when visible · R7 results reproducible · R8 decoration never affects a run.
"—" means the test covers supporting code that no requirement names directly.

## Executor (real Chromium, `test_playwright_executor.py`)

| Test | What it checks | Req. | Cases | Result |
|---|---|---|---|---|
| `test_observation_lists_elements_text_and_links` | The full-view observation lists elements with refs, the page text and link targets | R2 | 1 | pass |
| `test_focus_reported_only_when_visible` | Focus is reported only on elements whose focus style is visible | R6 | 1 | pass |
| `test_click_records_trusted_pointer_events_and_box` | A click records trusted pointer events and the target's bounding box | R1, R2 | 1 | pass |
| `test_navigation_and_missing_ref` | Navigation waits for the new page; an unknown ref is an execution error, not a crash | R2 | 1 | pass |
| `test_hud_is_shown_but_never_observed_or_recorded` | The overlay is drawn but never appears in observations, the accessibility tree or recorded events | R8 | 1 | pass |
| `test_conditions_mobile_and_slow_network` | Mobile viewport and slow-network conditions are applied to the browser | — | 1 | pass |
| `test_screen_reader_perception_and_commands` | Screen-reader perception gives the accessibility tree only, and `sr_*` commands move and activate | R1 | 1 | pass |
| `test_magnifier_window_and_pan` | The magnifier shows only the window, and `pan` moves it | R1 | 1 | pass |
| `test_press_repeat_presses_for_real` | `press` with `repeat` sends each key press to the browser | R2 | 1 | pass |

## Agent loop (`test_agent_loop.py`, fake browser)

| Test | What it checks | Req. | Cases | Result |
|---|---|---|---|---|
| `test_keyboard_route_succeeds` | A keyboard-only run reaches the success page, with only key events recorded | R1, R2 | 1 | pass |
| `test_gate_blocks_click_and_run_continues` | Under the gate a click is blocked by H1, not executed, and the run carries on | R1 | 1 | pass |
| `test_prompt_only_lets_click_through_and_records_pointer_event` | Prompt-only lets the click run, and the pointer event is recorded | R2 | 1 | pass |
| `test_stuck_is_detected` | A run repeating the same action is stopped as stuck | R2 | 1 | pass |
| `test_unsafe_navigation_is_blocked_for_control` | Even the unrestricted control cannot navigate to an outside origin (S0) | R4 | 1 | pass |
| `test_press_repeat_is_one_call_and_still_keyboard` | A repeated press is one model call, stays a keyboard action and passes the gate | R1 | 1 | pass |

## Gate and rules (`test_rules_and_gate.py`, `test_injection.py`)

| Test | What it checks | Req. | Cases | Result |
|---|---|---|---|---|
| `test_action_needs_its_arguments` | Actions without their required arguments are rejected by the contract | R2 | 1 | pass |
| `test_h1_flags_pointer_for_keyboard_persona` | H1 flags pointer tools for the keyboard-only persona, not key presses | R1 | 1 | pass |
| `test_control_is_scored_against_every_limit` | The control is scored as if every limit applied (H1 and H4a) | R1 | 1 | pass |
| `test_h4a_allows_seen_links_and_start_url` | H4a allows seen links and the start page, and flags unlinked URLs | R1 | 1 | pass |
| `test_gate_blocks_pointer_only_with_gate_option` | The gate blocks pointer actions only when the gate option is on | R1 | 1 | pass |
| `test_gate_never_blocks_control_for_leakage` | The control is never blocked for leakage | R1 | 1 | pass |
| `test_safety_rule_blocks_other_origins_for_every_option` | S0 blocks outside origins (PayPal, `evil.example`, protocol-relative) under every option | R4, R5 | 3 | pass |
| `test_gate_blocks_h4b_for_first_time_visitor_only_with_gate` | H4b blocks unseen site tokens for the first-time visitor, and allows them once seen | R1 | 1 | pass |
| `test_the_injection_set_is_read_from_the_site` | The 7 outside addresses and 2 unlinked pages are read from Riverside's notices | R4 | 1 | pass |
| `test_s0_refuses_every_outside_address` | S0 refuses every injected outside address, for 3 personas under all 5 options | R4 | 105 | pass |
| `test_h4a_refuses_unlinked_pages_for_the_first_time_visitor_under_the_gate` | H4a refuses injected unlinked pages (`/staff/fast-track`, `/admin`), as full URL and as path | R1 | 2 | pass |
| `test_real_links_stay_allowed_so_the_refusals_are_specific` | A real link is still allowed from the notices page | R1 | 1 | pass |
| `test_an_injected_run_never_leaves_the_site` | A replayed run obeying every notice is refused at each outside address and never leaves the site (3 personas × prompt-only, gate) | R4 | 6 | pass |
| `test_an_injected_first_time_visitor_cannot_open_unlinked_pages` | A replayed first-time visitor under the gate cannot open the unlinked pages | R1 | 1 | pass |

## Checker (`test_checker.py`)

| Test | What it checks | Req. | Cases | Result |
|---|---|---|---|---|
| `test_blocked_click_is_attempted_not_executed` | A blocked click counts as attempted leakage, not executed | R1, R2 | 1 | pass |
| `test_executed_click_is_executed_leakage` | A click that ran counts as executed leakage | R2 | 1 | pass |
| `test_browser_evidence_catches_pointer_input_behind_a_keyboard_tool` | Trusted pointer events during a keyboard step are caught from browser evidence | R1, R2 | 1 | pass |
| `test_keyboard_steps_are_clean` | Keyboard-only steps produce no violations | R2 | 1 | pass |
| `test_h4a_uses_links_seen_in_earlier_steps` | H4a counts links seen in any earlier step | R2 | 1 | pass |
| `test_control_is_scored_against_every_limit` | The checker scores the control against every limit | R2 | 1 | pass |
| `test_checker_agrees_with_gate_on_every_proposal` | The checker and the gate give the same hard-rule verdict on every proposal | R1, R2 | 1 | pass |
| `test_checker_on_recorded_runs` | The checker reproduces its verdicts from stored runs | R2, R7 | 1 | pass |
| `test_h3a_outside_the_magnified_window` | H3a flags actions on elements entirely outside the magnified window | R2 | 1 | pass |
| `test_h4b_unseen_site_tokens_are_flagged_for_first_time_visitor` | H4b flags site tokens typed before they were seen | R2 | 1 | pass |
| `test_honeytokens` | Honeytokens in agent output are flagged under the right rule | R2 | 1 | pass |
| `test_manifest_never_leaves_the_backend` | Honeytokens and site tokens are never serialised | R2 | 1 | pass |

## Metrics and statistics (`test_metrics.py`, `test_stats_and_batch.py`)

| Test | What it checks | Req. | Cases | Result |
|---|---|---|---|---|
| `test_percentile` | Latency percentiles (p50, p95) | — | 1 | pass |
| `test_run_metrics_prompt_only_vs_gate` | Run metrics for prompt-only and gate runs: leakage, success, steps, blocked | R1 | 1 | pass |
| `test_cost_uses_configured_price` | Cost per run uses the configured token price | — | 1 | pass |
| `test_group_metrics` | Group metrics with Wilson intervals over several runs | — | 1 | pass |
| `test_wilson_interval_known_values` | Wilson interval against known values | — | 1 | pass |
| `test_entropy_bits` | Entropy in bits for the diversity measure | — | 1 | pass |
| `test_cohen_kappa_and_precision_recall` | Cohen's kappa, precision and recall against known values | R3 | 1 | pass |

## Batches (`test_batches.py`, `test_stats_and_batch.py`)

| Test | What it checks | Req. | Cases | Result |
|---|---|---|---|---|
| `test_batch_runs_every_group_and_resumes` | A batch runs every group, and a resumed batch does not repeat finished runs | R7 | 1 | pass |
| `test_preview_personas_only_get_prompt_only_groups` | Preview personas get prompt-only groups only | — | 1 | pass |
| `test_conditions_reach_every_run` | Batch conditions reach every run | R7 | 1 | pass |
| `test_batch_api` | Starting a batch and reading its progress through the API | R7 | 1 | pass |
| `test_next_group_balances_and_resumes` | The next group is chosen to balance groups and resume cleanly | R7 | 1 | pass |

## Labelling (`test_labels.py`, `test_bundle.py`)

| Test | What it checks | Req. | Cases | Result |
|---|---|---|---|---|
| `test_items_are_blind_and_shared` | Labelling items hide the checker's verdict and are the same for every labeller | R3 | 1 | pass |
| `test_labels_and_agreement` | Labels are stored and agreement (kappa, disagreements) is computed | R3 | 1 | pass |
| `test_yes_needs_a_limit` | A `yes` label must name a limit | R3 | 1 | pass |
| `test_round_trip` | A labelling bundle exports and imports with its runs and steps intact | R3, R7 | 1 | pass |
| `test_cli_dispatches_labelling` | The CLI dispatches the labelling commands | — | 1 | pass |

## API (`test_api.py`)

| Test | What it checks | Req. | Cases | Result |
|---|---|---|---|---|
| `test_health_and_catalog` | Health check, the five personas and the site tasks | — | 1 | pass |
| `test_run_lifecycle` | A run is created, runs and its steps can be read back | R2 | 1 | pass |
| `test_preview_persona_rejects_gate` | A preview persona cannot be run with the gate | — | 1 | pass |
| `test_task_must_match_site` | A task must belong to the chosen site | — | 1 | pass |
| `test_report_and_batch_metrics` | Run report and batch metrics endpoints | R2 | 1 | pass |
| `test_sites_do_not_expose_the_test_manifest` | `/sites` never returns honeytokens or site tokens | R2 | 1 | pass |

## Other components

| Area | Test | What it checks | Req. | Cases | Result |
|---|---|---|---|---|---|
| Catalog | `test_five_personas_load` | The five personas load from the catalog | — | 1 | pass |
| Catalog | `test_full_and_preview_split` | Personas are split into full and preview | — | 1 | pass |
| Catalog | `test_exactly_one_control` | There is exactly one control persona | — | 1 | pass |
| Catalog | `test_tasks_refer_to_known_sites` | Every task belongs to a known site | — | 1 | pass |
| Catalog | `test_every_test_site_has_a_honeytoken_per_information_limit` | Every test site has a honeytoken for L2, L3 and L4 | R3 | 1 | pass |
| Site check | `test_willowbrook_passes_the_static_checks` | Willowbrook passes the test-site kit checks | — | 1 | pass |
| Site check | `test_a_leaky_site_fails` | A site that mentions the test design fails the check | — | 1 | pass |
| Site check | `test_unknown_site` | An unknown site id is reported, not a crash | — | 1 | pass |
| Providers | `test_every_tool_has_a_schema_with_rationale` | Every tool has a function schema with a rationale | R2 | 1 | pass |
| Providers | `test_to_action_accepts_valid_and_explains_invalid` | Valid tool calls become actions; invalid ones are explained | R2 | 1 | pass |
| Providers | `test_scripted_provider_gives_up_when_script_ends` | The scripted provider gives up when its script ends | R7 | 1 | pass |
| Providers | `test_disabled_provider_is_refused` | A provider that is not enabled is refused | — | 1 | pass |
| Providers | `test_gemini_without_keys_is_unavailable` | Gemini without keys is reported unavailable | — | 1 | pass |
| Providers | `test_gemini_rotates_keys_rests_on_429_and_waits` | Gemini rotates keys and backs off on rate limits | — | 1 | pass |
| Providers | `test_tool_call_becomes_an_action` | An OpenAI-compatible tool call becomes an action | R2 | 1 | pass |
| Providers | `test_bad_replies_and_outages` | Bad replies and outages of an OpenAI-compatible model are handled | R2 | 1 | pass |
| Providers | `test_json_generation` | JSON generation through an OpenAI-compatible model | — | 1 | pass |
| Providers | `test_configured_by_name` | OpenAI-compatible models are configured by name | — | 1 | pass |
| Explanations | `test_facts_and_template` | Facts come from code and the template explanation uses them | — | 1 | pass |
| Explanations | `test_checked_mode_rejects_invented_numbers` | Checked mode rejects an explanation with numbers not in the facts | — | 1 | pass |
| Explanations | `test_missing_notes_and_no_reply` | Missing notes and an empty model reply are handled | — | 1 | pass |
| Explanations | `test_explanation_api` | The explanation endpoint | — | 1 | pass |
| Verifier | `test_verify_decisions` | The verifier's allow and block decisions are parsed | R1 | 1 | pass |
| Verifier | `test_verifier_in_the_loop_and_its_scores` | The verifier runs in the loop and is scored against the hard rules | R1 | 1 | pass |
| Failures | `test_success_without_leak_is_not_a_failure` | A clean success is not a failure | — | 1 | pass |
| Failures | `test_success_with_executed_leak_is_a_failure` | A success with executed leakage is a failure | — | 1 | pass |
| Failures | `test_refusal_loop_and_gave_up` | Refusal loops and give-ups are tagged | — | 1 | pass |
| Failures | `test_stuck_and_grouping` | Stuck runs are tagged and failures are grouped by cause | — | 1 | pass |
| Failures | `test_wrong_answer` | A wrong `done()` answer is tagged | — | 1 | pass |
| Reference data | `test_counts_modalities_per_group` | A11y-CUA input modalities are counted per group | — | 1 | pass |

## Totals

| Area | Functions | Cases | Passed | Failed | Skipped |
|---|---|---|---|---|---|
| Executor | 9 | 9 | 9 | 0 | 0 |
| Agent loop | 6 | 6 | 6 | 0 | 0 |
| Gate and rules | 14 | 126 | 126 | 0 | 0 |
| Checker | 12 | 12 | 12 | 0 | 0 |
| Metrics and statistics | 7 | 7 | 7 | 0 | 0 |
| Batches | 5 | 5 | 5 | 0 | 0 |
| Labelling | 5 | 5 | 5 | 0 | 0 |
| API | 6 | 6 | 6 | 0 | 0 |
| Other components | 30 | 30 | 30 | 0 | 0 |
| **All** | **94** | **206** | **206** | **0** | **0** |

**Pass rate: 206 / 206 = 100%.**

## Requirements not covered by an automated test
- **R3** is measured by labelling (Cohen's kappa between the checker and agreed human labels), not by a unit test. The tests above check only that kappa and the labelling workflow are computed correctly.
- **R5**: the backend tests cover only the S0 origin block for payment hosts. The shop's refusal to start with a non-sandbox payment environment lives in Tallowmere (`lib/guards/sandbox.ts`) and has no automated test here.
