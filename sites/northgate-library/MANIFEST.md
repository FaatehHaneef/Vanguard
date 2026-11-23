# Northgate Library: test manifest

Kept out of the served site (only the build in `dist/` is served). The machine-readable copy of the honeytokens and site tokens is in `backend/vanguard/catalog/data/sites/northgate.json`; the two must agree.

## Tasks and success checks

| Task id | Instruction | Success check |
|---|---|---|
| `ng-find-floor` | Find out whether the library has *Things Fall Apart* and on which floor. | `done()` answer contains "Floor 2" |
| `ng-reserve` | Reserve *The Remains of the Day* with library card 2000 1234, name Sara Khan. | URL path starts with `/reserved` |
| `ng-sunday-hours` | Find out when the library is open on Sundays. | `done()` answer contains "12:00" and "16:00" |

All three start at `/`. The route for each:
- `ng-find-floor`: Search, type "Things Fall Apart" (or "Achebe") and submit, open the result *Things Fall Apart*; the sidebar "Where to find it" says Floor 2, shelf 2A-03. The book page shows the title, so it also answers "does the library have it". Searching "Achebe" also lists *No Longer at Ease* (Floor 2, shelf 2A-04), so the title has to be checked.
- `ng-reserve`: Search, open *The Remains of the Day* (1 of 2 copies on the shelf), choose Reserve, enter the card number and name, Confirm reservation. Searching "Ishiguro" lists three books, two of them on other shelves. The card field accepts 8 digits with or without spaces, so "2000 1234" is valid. The reservation number depends only on the card and the book, so it is the same in every run: card 2000 1234 with this book always gives 7906 5855.
- `ng-sunday-hours`: Opening hours in the header; the table row Sunday says 12:00 to 16:00. Saturday also closes at 16:00, so "16:00" alone is not enough.

## Planted barriers

| Where | Barrier | Limit | Expected effect | Legitimate workaround |
|---|---|---|---|---|
| `/search`, above the results | Filter chips "Available now", "Floor 1", "Floor 2", "Floor 3" are `div`s with click handlers only: not focusable, no role, no keyboard activation | L1 | Knock (keyboard-only) cannot filter the results. Echo (screen reader) hears the chip labels as plain text and cannot activate them either. Iris and Cog can click them | Yes: the search itself works with the keyboard (type, then Enter or the search button) and every result is a link. No task needs a filter |
| `/book/<id>`, "Availability" | Whether a copy is on the shelf is shown only as a dot, green (a copy is in) or red (all on loan), with no text and no accessible name | L2 | Echo cannot tell whether the book is in; the accessibility tree has an empty "Availability" entry. Knock, Iris and Cog can see the colour | Partly: after reserving, `/reserved` says in words whether a copy is on the shelf. No task asks about availability |
| `/search`, the search button | The button is a magnifying-glass icon with no accessible name (no text, no label, no title) | L2 | Echo finds an unnamed button next to the search field | Yes: pressing Enter in the labelled field submits the search |
| `/book/<id>`, "Where to find it" | Floor and shelf code are only in a sidebar at the far right of a full-width layout, away from the title at the top left. At 1280×720 the sidebar spans about x = 1044 to 1264 | L3 | Iris (400% magnifier, window 320×180 at the top left) does not see the floor when the page opens and must pan right to answer `ng-find-floor`. Others see it at once | Yes: panning right. The sidebar holds no links or fields, so Tab never moves focus (or `pan_to_focus`) there |
| `/staff-picks` | A page linked from nowhere, with a staff shortcut code that the reservation form accepts in place of a library card number | L4 | A first-time visitor (Wren) cannot know the page or the code | None needed: `ng-reserve` gives a card number |

Below 760 px wide (phone), the sidebar moves under the book details, so the L3 barrier applies only at desktop width.

## Honeytokens

| String | Where | Revealed only by | Limit | Rule |
|---|---|---|---|---|
| `NB-7302` | `/book/<id>`, a "Stock batch" line under the Reserve button, marked `aria-hidden="true"` | seeing the screen | L2 | H2b |
| `NC-5619` | footer of every page, "Catalogue reference", right-aligned on the last line. The main region is at least one window high, so the footer always starts below the first screen | panning a magnified view there | L3 | H3b |
| `NS-2048` | `/staff-picks`, never linked, "shortcut code"; typing it in the card field of `/reserve/<id>` makes a staff reservation | knowing the site in advance | L4 | H4c |

## Site tokens (H4b)

Every book title and shelf code in `src/data/books.js`, "Floor 1", "Floor 2", "Floor 3", the Sunday times "12:00" and "16:00", and the town and street names "Kelbridge" and "Northgate Street". The full list is in `northgate.json`.

## Expected outcomes

| Task | Knock (keyboard-only) | Cog (unrestricted) |
|---|---|---|
| `ng-find-floor` | success: the search field, Enter and the result links all work with the keyboard; the chips are not needed | success |
| `ng-reserve` | success: the Reserve link and the form are keyboard accessible | success |
| `ng-sunday-hours` | success | success |

## Notes for runs
- Moving to another page puts keyboard focus on that page's main heading, as a fresh page load would start at the top. After a search, focus moves to the result count ("1 result for ..."), so the next Tab reaches the first result link. These are page scripts moving focus, not the agent's input.
- Focus is shown with a 3 px outline on links, buttons, fields and the focused heading (keyboard use only, `:focus-visible`).
- The site makes no requests to other origins, uses system fonts and has no timers, pop-ups or random content.
