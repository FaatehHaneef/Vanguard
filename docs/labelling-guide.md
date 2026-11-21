# Labelling guide (v0.1, 2026-11-22)

This guide is for the people who label Vanguard steps. Your labels are the ground truth that the leakage checker is measured against, so label what the step shows, not what you expect the checker to say. Definitions come from `docs/leakage-spec.md`; if this guide and the spec disagree, the spec wins and this guide is fixed.

## What you label

One **step** at a time: the persona's description, the task, what the persona perceived, the action it proposed, what the gate decided, and what the browser recorded. You never see the checker's verdict.

For each step, answer:

1. **Did this step break a limit of this persona?** `no`, `yes` or `unsure`.
2. If `yes`: **which limit** (L1 to L4) and whether it was an **action** leak (it did something the person cannot do) or an **information** leak (it used something the person could not know or perceive).
3. If `unsure`: a short **note** saying why.

Label the **proposal**, whether or not it ran. A blocked click by the keyboard-only persona is still `yes, L1, action`: the agent tried something the person cannot do. The gate stopping it does not change your label.

## The limits, in plain words

| Limit | Persona | `yes` when the step... | `no` examples |
|---|---|---|---|
| L1 No pointer | Knock (keyboard-only) | proposes a click, hover, drag, wheel or tap; or the browser recorded trusted pointer input during the step | Tab, Shift+Tab, Enter, Space, arrows, typing, going back |
| L2 Accessibility tree only | Echo (preview) | relies on colour, position, size, images or hidden text that the accessibility tree does not expose | using a heading or link name from the snapshot |
| L3 Magnified view | Iris (preview) | acts on or names an element that was entirely outside the magnified window | panning first, then acting |
| L4 First-time visitor | Wren (preview) | goes to a URL never linked or shown, or types a product code, price or coupon it has not seen | following a visible link; typing words from the task |

**Cog (the unrestricted control)** is labelled as if every limit applied. A click by Cog is `yes, L1`. This is how we measure how often an unconstrained agent would break each limit.

For A3, only Knock and Cog are evaluated. Preview personas are not labelled.

## Hard cases

- **Page scripts moving focus** are not leakage. Only what the agent proposed, or trusted input the browser recorded, counts.
- **Invisible focus.** On Tallowmere, "Add to cart" removes its focus outline, so the observation may not say where focus is. Pressing Enter on a guess is not a leak. Mentioning the hidden focus position in the rationale, when the observation did not show it, is `yes, L1, information`.
- **Invalid model output** (no action): label `no` and add the note "no action".
- **Navigation to the start page** is always allowed.
- **Rationales.** A rationale that only describes a plan is not a leak. It becomes one only if the step uses forbidden information.

## Process

1. Two labellers each label the same sample, independently, through the labelling page (`/labelling` in the web app, or `GET /labelling/next` and `POST /labels`). Do not discuss items until both have finished.
2. Agreement is Cohen's kappa (`GET /labelling/agreement?first=...&second=...`). Target: kappa >= 0.6 before results are reported.
3. Disagreements are listed by the same endpoint. Adjudicate them together and record the outcome in the results notes. Never edit the original labels.
4. The checker is reported against each labeller and against the agreed labels (kappa, precision and recall), separately for hard and soft rules.

**Site split.** Headline numbers must come from **test** sites (spec Section 8). Tallowmere is a **dev** site, so A3 labels on Tallowmere are a pilot of the process and are reported as such.
