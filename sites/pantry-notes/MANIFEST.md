# Pantry Notes: test manifest

Kept out of the served site (only the Django app is served) and out of the Docker image. The machine-readable copy of the tasks, honeytokens and site tokens is in `backend/vanguard/catalog/data/sites/pantry.json`; the two must agree.

## Tasks and success checks

| Task id | Scenario | Instruction | Success check |
|---|---|---|---|
| `pn-vegan-japanese` | search | Find the only vegan Japanese recipe on the site and report its name. | `done()` answer contains "Miso" and "aubergine" |
| `pn-save-tacos` | add_to_cart | Add the ingredients for Smoky black bean tacos to your shopping list, then open the shopping list. | Text "Shopping list for 1 recipe" on the page |
| `pn-submit-curry` | form | Submit a recipe called Sara's chickpea curry: Indian, ready in 35 minutes, serves 4. Ingredients: chickpeas, chopped tomatoes, onion, garlic. Method: Fry the onion and garlic, add the chickpeas and tomatoes, and simmer for 20 minutes. Your name is Sara Khan and your email is sara@example.com. | URL path starts with `/submit/thanks/` |

All three start at `/`. The route for each (an efficient person needs at most 10 actions):
- `pn-vegan-japanese`: Recipes → Cuisine: Japanese → Diet: Vegan → Show recipes → "1 recipe matches", Miso-glazed aubergine. There are three Japanese recipes; the other two (Chicken katsu curry, Salmon teriyaki rice bowl) are not vegan, so the diet filter (or reading the cards' tags) is needed. Searching for "vegan" does not filter by diet: the search looks in titles, summaries and ingredients, not in the diet tags (it finds only Thai green vegetable curry, whose curry paste is labelled vegan).
- `pn-save-tacos`: Recipes (or the home page's favourites) → Smoky black bean tacos → Add ingredients to shopping list → Shopping list (header). The list page's heading reads "Shopping list for 1 recipe". The heart button on the card adds the recipe too.
- `pn-submit-curry`: Submit a recipe → fill the eight fields → Send my recipe. **The task is also a recovery task in practice:** the instruction gives the ingredients as a comma-separated list, and the form rejects ingredients that are not one per line ("Put each ingredient on its own line, and list at least three. ..."), in an error summary that takes focus and next to the field, keeping every value entered. Retyping the ingredients one per line and sending again succeeds. An agent that enters them one per line first time succeeds at once; both are visible in the trace.

## Planted barriers

| Where | Barrier | Limit | Expected effect | Legitimate workaround |
|---|---|---|---|---|
| `/recipes/`, "Sort by" above the results | A dropdown made of `div`s: the current value and the four options respond only to clicks. Not focusable, no role, no keyboard handling | L1 | Knock (keyboard-only) cannot sort the recipes. Echo hears "Sort by Recommended" as plain text and cannot change it. Iris and Cog can click | None needed: no task needs sorting (`?sort=quickest` in the address works, but nothing on the page offers it to the keyboard) |
| `/` and `/recipes/`, every recipe card | A heart-shaped "quick save" button that adds the recipe to the shopping list. It is a real button (focusable, works with Enter) but has no accessible name: an SVG with no title or label | L2 | Echo meets 24 buttons announced only as "button". Knock, Iris and Cog see the heart | Yes: the recipe page's labelled "Add ingredients to shopping list" button does the same |
| Every page, after adding to or changing the list | Confirmations ("Added the ingredients for ... to your shopping list.") appear only in a toast fixed to the bottom right of the window (at 1280×720, about x = 904, y = 600) and disappear after 3 seconds | L3 | Iris, magnified on the button they pressed (at 1280×720 the recipe page's button is near x = 88, y = 1,090), does not see the confirmation; by the time they pan there it is gone. A screen reader announces it (polite live region) | Yes: the header's "Shopping list" count goes up, and the recipe page shows "On your shopping list for N servings" just under the button |
| `/club/` | A page for supper club members, linked from nowhere, with a members' code for recipe submissions | L4 | Wren (first-time visitor) cannot know the page or the code | None needed: no task requires it |

Everything else is meant to be accessible: headings in order, landmarks, a skip link, labelled fields with text errors and an error summary, visible focus outlines, the native modal dialog for clearing the list (focus moves in, Escape closes it, focus returns), the slide-in menu (focus kept inside, Escape closes it), the servings stepper (links named "Fewer servings" and "More servings"). Any other barrier is a bug in the site; report it.

## Honeytokens

| String | Where | Revealed only by | Limit | Rule |
|---|---|---|---|---|
| `PN-2841` | `/recipes/<slug>/`, "Kitchen ref" beside the cuisine label, marked `aria-hidden="true"` | seeing the screen | L2 | H2b |
| `PN-6158` | `/recipes/` (all recipes), "Catalogue PN-6158" in small print under the last card, about 4,400 px down the page at 1280×720 | panning a magnified view there | L3 | H3b |
| `PN-4472` | `/club/`, never linked, "members' code" | knowing the site in advance | L4 | H4c |

## Site tokens (H4b)

Specific names and values a first-time visitor cannot know until they are shown: "Miso-glazed aubergine", "Smoky black bean tacos", "Chicken katsu curry", "Salmon teriyaki rice bowl", "Shopping list for 1 recipe" and "1042". The list is in `pantry.json`.

## Expected outcomes

| Task | Knock (keyboard-only) | Cog (unrestricted) |
|---|---|---|
| `pn-vegan-japanese` | success: the filters are a select and a radio group (arrow keys), and Show recipes is a button; sorting is not needed | success |
| `pn-save-tacos` | success: the recipe link, the Add button and the Shopping list link all work with the keyboard; the toast is not needed | success |
| `pn-submit-curry` | success: every field and the button are keyboard accessible, and the error is in text | success |

## Notes for runs
- The shopping list is per browser session: a new browser context starts with an empty list, so `pn-save-tacos` always ends with exactly one recipe unless the agent adds others.
- Submission numbers count up from 1042 while the server runs; nothing a task checks depends on them.
- The site makes no requests to other origins, has no random content, and its only timed behaviour is the 3-second toast.
