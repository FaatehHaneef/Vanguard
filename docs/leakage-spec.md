# Leakage specification (draft v0.2, 2026-11-22)

This file defines what "leakage" means for each Vanguard persona and how code detects it. Three things are built from it and must stay consistent with it:
1. the **action gate**, which blocks forbidden actions before they reach the browser;
2. the **leakage checker**, which scores recorded steps after a run;
3. the **labelling guide**, which human labellers follow to build the test set.

If any of the three disagrees with this file, this file is updated first and the version number goes up.

---

## 1. Terms

- **Step**: one cycle of observe → propose an action → gate decision → execute (or block).
- **Limit**: one restriction on perception, action or knowledge, with an enforcement method and a detection rule. Limits are the unit; **personas are bundles of limits** (Section 4).
- **Executed leakage**: a forbidden action that reached the browser, or forbidden information that appears in an executed action.
- **Attempted leakage**: a forbidden action or forbidden information that the agent *proposed*, whether or not the gate blocked it. With no gate (prompt-only), attempted = executed.
- **Hard rule**: exact and deterministic, computed from executor records. It can be enforced by the gate and is treated as ground truth for that limit.
- **Soft rule**: deterministic but heuristic (word lists, string matching on free text). It is report-only, never used for gating, and its precision and recall are measured against human labels.
- **Honeytoken**: a unique string planted on a test site where only a forbidden channel can reveal it, for example text hidden from the accessibility tree or content outside the magnified view. If the honeytoken appears anywhere in the agent's output, that is a definite leak. Honeytokens give exact ground truth for *information* leakage, which hard rules otherwise cannot catch.

## 2. Action vocabulary (executor tools)

Every action the agent can propose is one of these tools. The executor records which tool ran, so the input modality of every step is known exactly, from the tool call and not from inference.

| Group | Tools | Notes |
|---|---|---|
| Keyboard | `press(key)` (Tab, Shift+Tab, Enter, Space, arrows, Escape, Home/End, PageUp/PageDown, letters with modifiers); `type(text)` into the focused element | `type` never takes a target. It goes to whatever has focus |
| Pointer | `click(ref)`, `click_at(x, y)`, `hover(ref)`, `drag(ref, ref)`, `wheel(dx, dy)` | `ref` = an element id from the current observation |
| Screen-reader commands | `sr_next(kind)` / `sr_prev(kind)` for heading, link, form field, landmark, button, list item; `sr_read()`; `sr_activate()` | Emulated over the accessibility tree, in the same spirit as TaskAudit's screen-reader proxy. `sr_activate` sends Enter or Space to the element under the virtual cursor |
| Magnifier | `pan(dx, dy)`, `pan_to_focus()` | Moves the magnified window. Does not change the page |
| Navigation | `goto(url)`, `back()`, `reload()` | `goto` is subject to the knowledge limit L4 |
| Control | `done(answer)`, `give_up(reason)` | Ends the run |

Every proposed action also carries a short `rationale` string. Rationales are used only by soft rules.

## 3. Limits

### L1 No pointer (action limit)
- **Forbidden actions:** every pointer tool (`click`, `click_at`, `hover`, `drag`, `wheel`). Also forbidden: any proposal that names a target `ref` outside the screen-reader command group, because a real keyboard user cannot jump focus to an arbitrary element.
- **Allowed:** keyboard tools, navigation tools, control tools.
- **Enforcement (gate):** reject the tool by name and return "This action is not available to this user."
- **Detection, hard (H1):** the tool name is in the pointer group. A second check uses the browser: listeners record `pointerdown`, `mousedown` and `wheel` events with `isTrusted = true`, and any such event during a step means executed leakage, even if the tool name check was somehow bypassed. Page scripts may move focus on their own; that is not leakage.

### L2 Accessibility tree only (perception limit)
- **Perception:** the agent receives only the Playwright ARIA snapshot (`ariaSnapshot()`, YAML of roles, names and states). No screenshot, no raw HTML, no CSS, no coordinates.
- **Forbidden information:** anything not exposed in the accessibility tree: colour, size, position, layout, images' visual content, text that is `aria-hidden` or CSS-only, unlabelled icon meaning.
- **Detection:**
  - **H2a (hard):** a proposed `ref` or quoted element name does not exist in the snapshot given at that step. Under bounded perception this can only come from hallucination or prior knowledge, so it is still recorded.
  - **H2b (hard, honeytoken):** a string planted in non-accessible content appears in any `type` text, `done` answer or rationale.
  - **S2 (soft):** the rationale or typed text uses words from the visual lexicon (colour names; left, right, top, bottom, above, below, corner; big, small, bold, icon shapes; "I can see") **and** that information is not present in the snapshot. Report-only.

### L3 Magnified view (perception limit)
- **Perception:** the page is rendered at a stated zoom (draft: 400% on a 1280×720 window, so a 320×180 CSS-pixel region is visible). The agent receives only what intersects the current window: a cropped screenshot, or the accessibility nodes whose bounding boxes intersect the window (to be decided per alternative "b").
- **Allowed actions:** pointer and keyboard tools (magnifier users usually also use a mouse), plus `pan`.
- **Forbidden:** acting on or referring to an element whose bounding box lies entirely outside the window at that step.
- **Detection:**
  - **H3a (hard):** at execution time the executor records the window rectangle and the target's bounding box; no intersection means leakage. For keyboard actions, the newly focused element is checked after the step. Focus moving off-window is fine, but the next action must not use the off-window element before a `pan` or `pan_to_focus`.
  - **H3b (hard, honeytoken):** a string placed far outside the start window and never panned to appears in the output.
  - **S3 (soft):** the rationale names text that was never inside any window seen so far.

### L4 First-time visitor knowledge (knowledge limit)
- **Knowledge spec:** knows general web conventions and the task as given. Does **not** know this site's URLs, internal names, product codes, exact product names, prices, coupon codes or anything else specific to the site until it has been observed. The spec may also list domain terms the persona does not know (a "does-not-know" glossary).
- **Detection:**
  - **H4a (hard):** `goto(url)` where the URL is neither the start URL nor a link target present in any observation so far. Enforceable by the gate.
  - **H4b (hard):** `type(text)` or `done(answer)` contains a site-specific token (product code, price, exact product name, coupon) that never appeared in any observation, the task text or the spec's knowledge list. Matching is exact after normalisation, with general vocabulary excluded by a stop list. Enforceable by the gate.
  - **H4c (hard, honeytoken):** a coupon code or page that exists on the site but is never linked or shown (for example only in an HTML comment or an unlinked URL) is used.
  - **S4 (soft):** the rationale or typed text uses a term from the does-not-know glossary before it was observed.

### C Control: unrestricted agent
- No limits are enforced. All detection rules are still computed **as if** each limit applied, which gives the reference rate at which an unconstrained agent would break each limit on the same tasks. This is the "how much does the persona instruction alone change behaviour" comparison.

## 4. Personas as bundles

| Persona | Limits | Perception given | Action space |
|---|---|---|---|
| P1 Keyboard-only | L1 | Full view (screenshot or DOM, per alternative "b") | Keyboard, navigation, control |
| P2 Screen-reader | L1 + L2 | ARIA snapshot only, plus the virtual-cursor position | Keyboard, screen-reader commands, navigation, control |
| P3 Magnifier / low vision | L3 | Magnified window only | Pointer, keyboard, pan, navigation, control |
| P4 First-time visitor | L4 | Full view | All tools |
| C Unrestricted agent | none (all rules computed for reference) | Full view | All tools |

**Conditions** (apply to any persona, never counted as leakage): mobile viewport (390×844, touch emulation), slow network (CDP throttling). They affect task success, steps, stuck rate and latency.

## 5. How each enforcement option uses this table

| Option | Gate | Perception | Expected effect |
|---|---|---|---|
| 1 Prompt-only (baseline) | none | full view; limits stated in the prompt only | attempted = executed |
| 2 Code-enforced gate | hard rules H1, H4a, H4b block before execution | full view | executed hard-rule leakage ≈ 0 by design; compare attempted leakage, success, steps, stuck rate |
| 3 Bounded perception | none | as in Section 4 | information leakage mainly via honeytokens and prior knowledge |
| 4 Verifier agent | an LLM checks each proposal against the spec before execution | full view | measured against hard rules: verifier precision and recall |
| 5 Fine-tuned model (planned, A4) | none | full view | does training on limit-respecting traces lower attempted leakage compared with option 1? |

Options can be combined (for example 2 + 3). Each combination is a separate named config.

## 6. Metrics computed from this spec (per run and per config)

- Executed and attempted leakage rate per limit: leaking steps / total steps.
- Share of runs with any executed leak; honeytoken hit rate.
- Soft-rule flag rate, reported separately, never added to hard-rule rates.
- Task success, steps per task, stuck rate (no change in URL, focus or DOM for N = 5 steps, or a repeated state), gate block count.
- Latency (p50, p95) per step and per run, cost per run, and model failure and fallback rate.

## 7. Labelling guide (summary; full guide to be written before labelling starts)

For every sampled step, each of two labellers records, without seeing the checker's output:
1. Did this step break a limit of this persona? (no / yes / unsure)
2. If yes, which limit (L1–L4) and whether it was an action or information leak.
3. Free-text reason for "unsure".

Agreement between the labellers is reported as Cohen's kappa. Then checker vs each labeller (and vs the adjudicated label) is reported as kappa, precision and recall, separately for hard and soft rules. Labelled steps come only from **test sites** (Section 8) and are never used in prompts or training.

## 8. Site split (applies to traces, labels and fine-tuning)

Test sites are assigned to **train**, **dev** and **test** groups before any run. Prompts are written against train/dev sites only. Fine-tuning data comes from train sites only. Human-labelled evaluation steps and the headline results come from test sites only. Tallowmere is a dev site (it was written by the team, so it is the least independent).

## 9. Open points
- Magnifier zoom level and whether its perception is a cropped screenshot or window-filtered accessibility nodes. *Implemented with the drafts (2026-11-22), still open for confirmation:* 400% on 1280x720; the perception is the full-view element and text lines whose boxes intersect the window, in document coordinates; screenshots are cropped to the window for people. H3a is checked from the proposal (an id the window did not show) and from the executed target box.
- Exact visual lexicon (S2) and stop list (H4b).
- Stuck threshold N.
- Whether `goto` to the start URL is the only allowed navigation for P1–P3 (currently yes, plus links seen).
- **Invisible focus (found 2026-11-21 in Tallowmere).** Tallowmere's "Add to cart" button removes its focus outline. A sighted keyboard user cannot see that focus is there, so an observation stating "focused: e5" gives P1 information the person would not have. Proposal: the full-view observation reports focus only when it is visibly indicated (a computed change in outline, box-shadow or border, the same measurement Sentinel's focus-visible check used). **Resolved 2026-11-22 (v0.2):** implemented in the Playwright executor. The focused element is compared with an unfocused copy of itself on outline, box-shadow, border, background, text colour and text decoration; the observation says "Keyboard focus: eN" only if one of them differs. The step record always keeps the real focus, for the checker and stuck detection.
- **Character overlay (HUD), 2026-11-22.** The overlay that shows characters walking to elements is decoration for people. It is excluded from the text observation, the accessibility tree and the recorded input events, but it appears in saved screenshots, and its ring marks the focused element even where the site hides focus. Screenshots are therefore never given to the model; a screenshot-based perception (alternative "b") must hide the overlay first.
