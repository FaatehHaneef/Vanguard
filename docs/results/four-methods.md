# Four enforcement methods compared (F5, instructor's point 11)

Batch `four-methods-callback`, run 24 to 25 November 2026. Reproduce the table with
`python -m vanguard.cli report --batch four-methods-callback`.

## What was held fixed and what changed
- **Fixed:** the same agent (Gemini `gemini-3.6-flash`, prompt `agent-v0.2`, up to 4 actions per model call), the same task (Willowbrook, `wb-callback`: ask the clinic to call you back, a form task, at most 12 steps), the same site version (`sites-v1`), the same two personas, 3 repeats each.
- **Changed, one at a time:**
  - **prompt-only:** the limits are only described to the model;
  - **gate:** code refuses any action outside the limits before it reaches the page;
  - **bounded perception:** each persona is shown only what its user could perceive;
  - **verifier:** a second model call checks each action against the limits before it runs.
- **Knock** is the keyboard-only persona (limit L1, an action limit).
- **Cog** is the unrestricted control. Its "leaks" are a reference rate, scored as if Knock's limits applied; they are expected behaviour, not failures.

## Results (3 runs per group)

| Persona | Method | Success | Runs with an executed leak | Attempted leaks per step | Steps | Refused per run | Model calls per run | Step time p50 |
|---|---|---|---|---|---|---|---|---|
| Knock | prompt-only | 100% | 100% | 0.32 | 7.3 | 0.0 | 3.3 | 2 s |
| Knock | gate | 100% | **0%** | 0.06 | 10.3 | 0.7 | 6.0 | 10 s |
| Knock | bounded perception | 100% | 100% | 0.21 | 7.7 | 0.0 | 4.0 | 5 s |
| Knock | verifier | 100% | 100% | 0.20 | 8.3 | 0.7 | 13.7 | 26 s |
| Cog | prompt-only | 100% | 100% (reference) | 0.67 | 6.0 | 0.0 | 3.0 | 3 s |
| Cog | gate | 100% | 100% (reference) | 0.67 | 6.0 | 0.0 | 3.0 | 5 s |
| Cog | bounded perception | 100% | 100% (reference) | 0.67 | 6.0 | 0.0 | 3.0 | 3 s |
| Cog | verifier | 100% | 100% (reference) | 0.67 | 6.0 | 0.0 | 9.0 | 13 s |

Repeated attempts were 0 in every group. Cost was $0 (free tier). Step time includes Gemini's own delays, which were long on these days.

## What it shows
1. **Only the gate stopped every leak, and it cost no task success.** With the gate, Knock completed all three runs without one executed pointer action. It needed about 3 more steps (10.3 vs 7.3), because refused clicks had to be replaced by keyboard actions, and about twice the model calls. Describing the limit in the prompt was not enough: in every prompt-only run, Knock used the mouse at least once.
2. **Bounded perception does not address an action limit.** It controls what a persona perceives (L2, L3), not what it does, so Knock's pointer use was unchanged: 100% of runs leaked. The method is meant for the perception personas; this comparison shows why the methods are not interchangeable.
3. **The verifier missed most pointer actions.** It was answering throughout (no "verifier unavailable" decisions), yet it allowed 3 of Knock's 5 pointer actions and refused 2. That is a recall of 40% on these actions, and every verifier run still leaked. It also cost the most: about 4 times the model calls of prompt-only (13.7 vs 3.3 per run) and the slowest steps. Its precision and recall against human labels are measured separately (E11, CP-LB).
4. **None of the methods hurt the control.** Cog behaved the same under all four (6 steps, 100% success). The gate and bounded perception change nothing for an unrestricted user, as intended. The verifier only added calls.

## Limits of this comparison
- 3 runs per group and one form task on one site: the success rates have wide 95% intervals (21% to 100% for 3 of 3). The direction is clear; the sizes are not precise.
- One model. A stronger model might follow the prompt-only limits more often.
- The task needs no pointer, so a leak here is always avoidable. Tasks where the pointer is the only way (`wb-book-tuesday`) test a different question: whether the agent gives up honestly.
- As with every result here, simulated users do not establish accessibility compliance or represent real users with disabilities.
