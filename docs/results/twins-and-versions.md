# Twin runs and the version comparison (F6, F10; instructor's points 6, 9, 16)

Run 25 November 2026 with Gemini `gemini-3.6-flash`, prompt `agent-v0.2`, up to 4 actions per model call, at most 12 steps, 3 runs per group. Reproduce with `python -m vanguard.cli report`, `findings` and `GET /compare`, using the batch ids below.

## Twin runs: the same persona with and without its limits enforced (point 6)

A twin pair gives one persona the same task twice: once with its limits only described (prompt-only), and once with them enforced (the gate for an action limit, bounded perception for a perception limit). The control agent Cog ran the same tasks for reference (batch `control-ng`).

| Persona and task (Northgate, version 2) | Condition | Success | Runs with an executed leak | Steps | Repeated attempts per run | Model calls per run |
|---|---|---|---|---|---|---|
| Knock, reserve a book (`ng-reserve`) | prompt-only | 0 of 3 | 2 of 3 | 12.0 | 0.0 | 8.7 |
| | gate | 0 of 3 | 0 of 3 | 12.0 | 0.0 | 9.3 |
| Iris, find the floor (`ng-find-floor`) | prompt-only | 3 of 3 | (preview persona) | 5.0 | 0.0 | 3.0 |
| | bounded perception | 0 of 3 | (preview persona) | 10.0 | 6.3 | 9.0 |
| Cog, reserve a book | prompt-only | 3 of 3 | (reference) | 10.0 | 0.0 | |
| Cog, find the floor | prompt-only | 2 of 2 finished | (reference) | 4.5 | 0.0 | |

Two of the gated Knock runs, one Iris run and three Cog runs on the find-the-floor task stopped on Gemini errors; they are counted as "infrastructure" and left out of the rates above.

**What the twins show.**
- **Iris:** with the whole page visible, the magnifier persona answered in 5 steps every time. With her view enforced (only a 400% window, moved by panning), she failed all three runs and repeated herself about six times per run. The planted barrier, the floor and shelf placed in a sidebar at the far right of the book page, only bites when the perception limit is real. Prompt-only simulation would have missed this barrier entirely.
- **Knock:** the reservation needs about 10 steps even for Cog, so within 12 steps the keyboard-only route was too long under both conditions. The gate changed *how* Knock failed rather than whether: without it, he used the mouse in 2 of 3 runs; with it, every pointer attempt was refused and he stayed within his limit.

## Why the twin runs failed (point 9)

`python -m vanguard.cli findings --batches twin-ng-reserve twin-ng-floor` attributes each failure using the control runs, the twins and the site manifest:

| Batch | Restriction | Agent | Infrastructure |
|---|---|---|---|
| `twin-ng-reserve` (Knock) | 5 | 1 | 2 |
| `twin-ng-floor` (Iris) | 3 | 0 | 1 |

- **Iris's 3 failures are "restriction":** the same persona succeeds on the task when its limits are only described (3 of 3), so the enforced perception limit caused the failure. This is a candidate accessibility barrier for magnifier users, to be confirmed by people.
- **Knock's 5 "restriction" failures:** Cog succeeds on the task (3 of 3), and Knock tried to use a control with the mouse and did not reach it with the keyboard before the run ended. That control was the result link or the Reserve link. Both are keyboard-reachable on this site, so the report marks them as candidates for a person to check, not as proof of a barrier. The cost the keyboard limit really adds here is length: the route takes more steps than the 12-step cap allows.
- **Knock's 1 "agent" failure:** the step limit ran out with no limit involved.

## Website versions (point 16)

Every test site was redesigned during A3 (version 2) with its tasks, barriers and honeytokens unchanged; version 1 is the git tag `sites-v1`. The same persona, task and method were run on both versions of Willowbrook and compared with `GET /compare?baseline=four-methods-callback&candidate=version-wb-v2`:

| Knock, gate, `wb-callback` | Version 1 | Version 2 | Change |
|---|---|---|---|
| Success | 3 of 3 | 3 of 3 | same |
| Runs with an executed leak | 0 | 0 | same |
| Steps | 10.3 | 9.0 | better |
| Model calls per run | 6.0 | 5.0 | better |
| Refused per run | 0.7 | 1.0 | (no direction) |
| Repeated attempts | 0 | 0 | same |

The report found no new failure causes and none resolved: the redesign introduced no new problem for a keyboard user on this task.

## Limits
- 3 runs per group (2 to 3 after model errors); the differences are directions, not precise sizes.
- Iris is a preview persona: her limits are enforced by bounded perception but her steps are not yet validated by labels.
- Simulated users do not establish accessibility compliance or represent real users with disabilities.
