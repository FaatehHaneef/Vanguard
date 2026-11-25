# Configuration studio

## What it does

The configuration studio (`/studio` in the web app) lets a team create, edit and save its own personas, add any website it may test, and define tasks on that website without changing code. Everything made in the studio appears wherever the built-in catalog does: the site picker, trials, batches, results and the comparison page.

- **Personas.** A form sets the name, description, character sprite, limits (L1 to L4), perception (full, screen reader or magnified, with a magnification factor), and the groups of actions the persona may use. Each option shows its meaning in plain language, and a live preview shows the sprite and the status the persona will get. A built-in persona can be duplicated as a starting point. "Send on a trial" opens the site picker with the persona already in the party.
- **Sites.** A name, an address (`https://shop.example.com`) and an optional description, with a confirmation that the team owns the site or is allowed to test it.
- **Tasks.** On any site, built-in or custom: an instruction, a start page, a scenario (search, add to cart, checkout, form, recovery or information) and a success check. The check is a page address the run reaches, text that appears on the page, or words the final answer must contain.

## Data model

Three tables in the run database, one per kind of item, with the same columns:

| Table | Holds | Columns |
|---|---|---|
| `custom_personas` | `PersonaSpec` | `id` (primary key), `data` (JSON), `created_at`, `updated_at` |
| `custom_sites` | `Site` | the same |
| `custom_tasks` | `Task` | the same |

`data` is the item itself, stored as the contract model's JSON (`backend/vanguard/contracts/`), so a custom item is exactly the shape a built-in one has and no other code needs to know where it came from. Ids are `custom-<slug>-<4 hex>`, made from the name or instruction, so they never clash with built-in ids. The tables are created on first use; no migration is needed.

## How custom items reach the catalog

`vanguard.catalog` is the one place the rest of the backend looks up personas, sites and tasks. On every lookup it calls `vanguard.studio.source`, whose `personas()`, `sites()` and `tasks()` read the three tables, and joins the results with the built-in files. **Built-in items always win**: a custom item can never replace or shadow one. Because the browser's allowed origins are built from the catalog's site origins, a custom site becomes reachable by the agent as soon as it is saved, and only then. The source reads the database the API has open; when there is none (tests, the command line) it returns nothing, so the built-in catalog is never affected by whatever is in a developer's local database.

The API is `GET/POST /studio/{personas,sites,tasks}` and `GET/PUT/DELETE /studio/{kind}/{id}` (`backend/vanguard/routes/studio.py`). Built-in items can be read but not changed (409, "copy it first").

## Validation and safety

- **Every item is validated against its contract before it is written**, then the write happens in one transaction. Errors come back as 422 with the field that is wrong, and the forms show each message next to that field.
- **Personas.** A name, a description, a known character and at least one action group are required; a magnified view needs a magnification above 1. A custom persona is never the control persona. Its **status is computed, not chosen**: it is `full` only when its limits, perception, action groups and magnification exactly match a built-in persona whose status is full, because only those bundles are enforced and validated in code (`docs/leakage-spec.md`, Section 4). Any other combination is `preview`, which states its limits in the prompt only, and the editor says so before saving.
- **Sites.** The address must be an `http` or `https` origin with a host and no path, query or fragment. The form asks the user to confirm they own the site or may test it, and warns against live sites where a form would send a real order or message. The agent can only visit origins that are in the catalog, and the run's network filter still applies.
- **Tasks.** The site must exist, the start page must be a path starting with `/`, and at least one success check is required, so every custom task can be scored by the deterministic checker rather than by a model.
- Deleting a custom site also deletes its custom tasks. Runs refer to the persona, site and task by id and store their own steps and outcome, so deleting an item does not delete its runs or change their recorded results.
