# CP-G1: groundwork is on main

Merged on Tue 24 Nov 2026 (merge commit `374f27c`). Steps that wait on CP-G1 can start: Hadi H2, H5, H6, H11 and S12; Ibrahim E5 and S12. Run `git merge origin/main` on your branch first.

## What is now available

### Catalog: one file per site
- Built-in sites are `backend/vanguard/catalog/data/sites/<site-id>.json`, each `{"site": {...}, "tasks": [...]}` (format in `docs/tasks-A3-round2.md`, Section 0.8). The old `sites.json` is gone.
- Extra tasks on any site go in `backend/vanguard/catalog/data/tasks/<name>.json` as `{"tasks": [...]}`. The folder exists and is empty (Ibrahim's `a3-suite.json` goes here).
- `Task.scenario` is one of `search`, `add_to_cart`, `checkout`, `form`, `recovery`, `information`. Every built-in task has one.
- `Site.docker_host` is the Compose `service:port`, for example `"emberline:3104"`. It is not sent to the frontend.
- A task or site id defined twice is an error when the catalog loads. So is a task on an unknown site.
- `python -m vanguard.cli check-site <site-id> --dir <folder> [--live]` now also checks the site's own `compose.yml`, its port and a service named as in `docker_host`.

### Studio hook (Hadi, H5)
- When `backend/vanguard/studio/source.py` exists, the catalog calls its functions `personas()`, `sites()` and `tasks()`. Each returns a dict by id: `PersonaSpec`, `Site` and `Task` from `vanguard.contracts`.
- The catalog calls them on every lookup, with no caching, so edits show up at once. A missing function counts as returning nothing.
- A custom item never replaces a built-in item with the same id: the built-in wins. Reject such ids in the studio with 409.
- Custom sites' origins are allowed automatically. Tests can replace `vanguard.catalog._studio` with a fake object (see `backend/tests/test_groundwork.py`).

### Origins and Docker
- Every catalog site's origin is always allowed: built-in and custom. `VANGUARD_ALLOWED_ORIGINS` now lists only extra origins (the default is empty).
- Inside Docker (`VANGUARD_IN_DOCKER=true`, set for the `api` service), requests go to each site's `docker_host`.
- Do not edit `settings.py`, `.env.example` or the root `docker-compose.yml` for a new site.
- The root `docker-compose.yml` includes each site folder's `compose.yml`. The four new folders already have a stub file with `services: {}`. Replace it with one service named after the site id, as `sites/willowbrook-clinic/compose.yml` does:
  ```yaml
  services:
    emberline:
      build: .
      ports:
        - "3104:3104"
  ```

### API route folder
- Every module in `backend/vanguard/routes/` that has a `router = APIRouter(...)` is included in the API automatically. Do not edit `api.py`.
- Get the store and the settings from `vanguard.deps`, for example:
  ```python
  from fastapi import APIRouter, Depends
  from vanguard.deps import get_settings, get_store
  from vanguard.store import RunStore

  router = APIRouter(prefix="/studio", tags=["studio"])

  @router.get("/personas")
  def list_custom(store: RunStore = Depends(get_store)): ...
  ```
- `routes/compare.py` is the example.

### Web
- The placeholder pages `apps/web/app/studio/page.tsx` and `apps/web/app/compare/page.tsx` are Hadi's to replace.
- The Results page links to both. The lobby links to Studio.

## GET /compare (Hadi, H11)

`GET /compare?baseline=<batch_id>&candidate=<batch_id>[&match=full|persona_task]`

- It returns 404 if either batch has no runs. Only finished runs count.
- `match=full` (the default) pairs groups on `persona/task/enforcement/provider`, the same setup before and after. Use it for "did this site change introduce new problems".
- `match=persona_task` pairs groups on `persona/task` only. Use it for comparing methods or providers.

The response is the `Comparison` model in `backend/vanguard/contracts/compare.py`:

```json
{
  "baseline": "before",
  "candidate": "after",
  "match": "full",
  "groups": [
    {
      "key": "keyboard-only/buy-one/gate/gemini",
      "baseline":  {"runs": 4, "success_rate": 0.5, "any_leak_rate": 0.25, "mean_steps": 9.0,
                    "stuck_rate": 0.0, "mean_blocked": 1.5, "mean_cost_usd": 0.0, "failures": 2},
      "candidate": {"runs": 4, "success_rate": 0.75, "any_leak_rate": 0.0, "mean_steps": 8.0,
                    "stuck_rate": 0.0, "mean_blocked": 2.0, "mean_cost_usd": 0.0, "failures": 1},
      "changes": [
        {"metric": "success_rate", "baseline": 0.5, "candidate": 0.75, "delta": 0.25, "verdict": "better"},
        {"metric": "any_leak_rate", "baseline": 0.25, "candidate": 0.0, "delta": -0.25, "verdict": "better"},
        {"metric": "mean_steps", "...": "..."},
        {"metric": "stuck_rate", "...": "..."},
        {"metric": "mean_cost_usd", "...": "..."},
        {"metric": "mean_blocked", "baseline": 1.5, "candidate": 2.0, "delta": 0.5, "verdict": "same"}
      ],
      "verdict": "better"
    }
  ],
  "new_failures": [
    {"key": "keyboard-only/buy-one/gate/gemini", "cause": "refusal_loop",
     "meaning": "The agent kept proposing actions the gate refused", "run_ids": ["..."]}
  ],
  "resolved_failures": []
}
```

- `delta` is the candidate value minus the baseline value.
- A metric's verdict is `better`, `worse` or `same`:
  - higher is better for `success_rate`;
  - lower is better for `any_leak_rate`, `mean_steps`, `stuck_rate` and `mean_cost_usd`;
  - `mean_blocked` has no direction, so it is always `same`.
- A group's verdict:
  - `worse` if any metric got worse, otherwise `better` if any metric got better, otherwise `same`;
  - `only_baseline` or `only_candidate` when the group is in one batch only. Its `changes` list is then empty and the other side is `null`.
- `new_failures` lists the primary failure causes (`vanguard.failures.CAUSES`) that a group has in the candidate but not in the baseline. `resolved_failures` is the reverse. `run_ids` are the runs in the batch where the cause appears. Link each one to `/runs/<id>`.
- Groups that are in one batch only are left out of both lists.
- Repeated attempts are not in the comparison yet. When Ibrahim's E3 adds `repeated_attempts` to the metrics and is merged, Faateh adds `mean_repeated_attempts` to each side and to `changes`, and says so in the team chat. Show it when it is present.
