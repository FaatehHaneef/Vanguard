# Evaluation design

Vanguard's evaluation asks two questions: does the simulated user behave like the person it stands for, and do the enforcement methods keep it inside its limits without stopping it doing the task? Single steps cannot answer the first question, so runs are also scored as whole tasks, compared with real users' input, and compared with each other. Every number below is computed by code (`backend/vanguard/metrics/` and `backend/vanguard/evaluation/`) from the stored traces; no model counts, scores or decides leakage.

## Tasks and scenarios

A task is an instruction, a start page and a deterministic success check: a page address reached, text shown on the page, or words the final `done()` answer must contain. Each task has one **scenario**, so results can be grouped by the kind of work rather than by site:

| Scenario | What the user does | Example |
|---|---|---|
| search | finds an item with search or filters | Northgate `ng-author`: who wrote *The Remains of the Day* |
| add_to_cart | adds an item and opens the basket or list | Tallowmere `tm-add-moss`, Pantry Notes `pn-save-tacos` |
| checkout | completes a purchase or booking | Tallowmere `buy-one` |
| form | fills in and sends a form | Pantry Notes `pn-submit-curry` |
| recovery | recovers from a form that refuses the first attempt | Riverside `rc-report-recover`, Harbour Herald `hh-newsletter` |
| information | reads an answer off the site | Willowbrook `wb-ahmed-days`, Harbour Herald `hh-parade-time` |

The A3 suite (`backend/vanguard/catalog/data/tasks/a3-suite.json`, plus the tasks of the two new sites) adds the scenarios each existing site lacked. Every task is short enough for an efficient person to finish in at most ten actions, so a run fits the 12-step cap and the free-tier call budget.

## What is held fixed and what changes

Within one comparison, the model, the prompt version, the tasks, the start pages, the step cap and the number of actions per model call stay the same; only one condition changes:

- **Persona** (keyboard-only Knock vs unrestricted Cog): the limits stated in the prompt and, under the gate, the actions allowed.
- **Enforcement method**: prompt-only (limits stated, nothing enforced), gate (hard rules refuse forbidden actions in code), bounded perception (the model sees only what the persona could perceive), verifier (a second model call judges each action).
- **Site**: the barriers and honeytokens planted in it (each site's `MANIFEST.md`).

Each condition is run at least three times, and every proportion is reported with a 95% Wilson interval.

## Metrics per task

For each task (and each scenario), persona and enforcement method, over its runs (`python -m vanguard.evaluation task-report`):

- **Completion rate**: runs that passed the success check, with a Wilson interval.
- **Actions**: steps per run. **Model calls**: agent calls plus verifier checks per run. One call may propose up to four actions, so the two differ.
- **Repeated attempts**: proposals identical to the previous one (same tool and the same key, element, text or address) that either follow a refusal of that action or follow an attempt that changed neither the address nor the focus. This counts an agent hammering at a barrier.
- **Refusals**: actions the gate refused.
- **Stuck rate and step-limit rate**: runs that ended because nothing changed for several steps, or because the 12-step cap ran out.
- **Task time**: the run's total model and browser time, as the median and 95th percentile over runs; **cost** from tokens and the configured price.
- **Failure cause**: the primary cause of each failed run (model unavailable, persona leak, invalid output, refusal loop, action errors, stuck, step limit, gave up, wrong answer), assigned by `vanguard.failures`.

## Realism: compared with real users

`python -m vanguard.evaluation realism` compares each persona's executed input with the Reduced A11y-CUA logs (reference statistics only; the dataset is never used for training or prompts). Three shares are computed the same way for both: **pointer share** (pointer actions over pointer actions plus key presses), **Tab and arrow share** and **Enter share** of key presses, counting typing as one key press per character, as the logs do. Knock is compared with blind and low-vision users and Cog with sighted users, and the report gives both values and their absolute difference. A11y-CUA's tasks were desktop tasks rather than these sites' tasks, so this compares input habits, not performance.

## Diversity

`python -m vanguard.evaluation diversity` measures how differently personas, and repeated runs of one persona, behave. A run's behaviour is its sequence of proposed action types (the tool, and the key for key presses). It reports:

- the **normalised edit distance** between two runs' sequences (0 = identical, 1 = nothing in common), averaged within a persona on the same task and between pairs of personas;
- the **Shannon entropy** of each persona's action-type mix;
- the **spread** (standard deviation and interquartile range) of actions per run and of completion, per persona and across personas;
- the **distinct navigation paths** per persona and task.

Low distances and identical paths across runs show the collapse that the project's earlier work found; differences between personas show whether the persona description changes behaviour at all.

## The verifier against people

The verifier (enforcement method 4) is itself a model, so it is measured (`python -m vanguard.evaluation verifier-report`) on the steps it judged that both labellers labelled. A refusal is its positive. Against **(a) the agreed human labels** (both labellers gave the same yes or no) and **(b) the hard rules** (the checker's verdict), the report gives **precision** (refusals that were leaks), **recall** (leaks that were refused) and the **false-positive rate** (valid actions wrongly refused, over all valid actions), with the confusion counts and every step where the verifier and the reference differ. Steps where the labellers disagreed or were unsure are listed and left out of (a), and steps where the verifier was unavailable are left out of both. A verifier with a high false-positive rate blocks legitimate users' actions, so this rate matters as much as recall.

## Results

The task-level, realism, diversity and verifier tables are generated from the A3 suite runs and the labelled verifier sample into `docs/results/task-level.md`, `realism.md`, `diversity.md` and `verifier.md`. They are summarised here once those runs and labels are complete.

**Limits of the design.** Three runs per condition give wide intervals, so differences are reported as indications, not significant effects. The test sites were built by the team to a written specification, not independently. Labels made with an AI tool are declared as such in `AI_USE.md`, and agreement between them is not reported as agreement between people.
