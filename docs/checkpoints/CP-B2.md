# CP-B2: labelling bundle 2 is on main

Merged on Wed 25 Nov 2026. E12 and H14 can start their bundle 2 part. Run `git merge origin/main` on your branch first.

## The bundle
`data/labelling/a3-b2/`: 60 steps from 26 runs of the four-method comparison (`four-methods-callback`, Willowbrook's call-back form, Knock and Cog under prompt-only, gate, bounded perception and verifier, 3 repeats each), plus the two earlier runs `four-methods-wb` and `smoke-g2`.

- About half the items are harder steps: steps the gate or the verifier refused, or that the checker flagged. The rest are drawn from all steps. They are shuffled together with a fixed seed, and nothing in the bundle says which kind an item is.
- No screenshots: these runs were recorded with the character overlay on, whose focus ring would bias labellers (the same rule as bundle 1). Judge from what the persona perceived, its proposal and the page result.

## How to label
Follow `docs/labelling-guide.md`:
```bash
cd backend
python -m vanguard.cli labelling import data/labelling/a3-b2
# label in the web app at the address the command prints, as your labeller name
python -m vanguard.cli labelling export-labels --labeller <your name>
```
Save the export as `data/labels/<your name>-a3-b2.json` on your branch and push it. CP-LB follows once both files are merged.
