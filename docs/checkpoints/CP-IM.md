# CP-IM: Ibrahim's metrics are on main

Merged on Tue 24 Nov 2026 (`task-evaluation`, merge commit `76653a3`), together with Hadi's `studio` and `dining-tickets`. Run `git merge origin/main` on your branch first.

## What is now available
- `vanguard.metrics.repeated_attempts(steps)` and, per run, `RunMetrics.repeated_attempts`, `model_calls` and `actions`. Per group: `mean_repeated_attempts`, `mean_model_calls` and `mean_actions`.
- The findings report (`vanguard.findings`, `cli findings`) marks repeated steps with this same metric, so the finding and the number always agree.
- `GET /compare` now has `mean_repeated_attempts` and `mean_model_calls` on each side of every group, and a change for each. Lower is better for both. The compare page already shows repeated attempts when they are present.

## Also fixed on main
- The CLI opens its database through `vanguard.deps`, so `cli batch` and the other commands see custom studio personas, sites and tasks.
- Custom personas appear in the lobby, in the party on the site picker and on run pages. A custom persona uses the sprite named in its `character` field.
- The "Your own site" tile on the site picker links to `/studio/sites`.
