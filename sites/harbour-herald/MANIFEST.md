# Harbour Herald: test manifest

Kept out of the served site (only the build in `dist/` is served) and out of the Docker image. The machine-readable copy of the tasks, honeytokens and site tokens is in `backend/vanguard/catalog/data/sites/herald.json`; the two must agree.

## Tasks and success checks

| Task id | Scenario | Instruction | Success check |
|---|---|---|---|
| `hh-cricket-funding` | search | Find out how much funding the cricket club was awarded for its indoor nets. | `done()` answer contains "86,000" |
| `hh-newsletter` | recovery | Sign up for the Morning Briefing newsletter as sara@example.com. Send the form once without ticking the consent box; when it is refused, tick it and send it again. | Text "You're on the list" on the page |
| `hh-parade-time` | information | Find out what time the Harbour Lights lantern parade starts. | `done()` answer contains "18:30" |

All three start at `/`. The route for each (an efficient person needs at most 10 actions):
- `hh-cricket-funding`: the cricket story is not on the front page. Search (header) → type "cricket" → Enter → open "Cricket club wins funding for indoor nets" → the first paragraph says £86,000. Or Sport (section bar) → the story.
- `hh-newsletter`: Newsletter (header) → the dialog opens with focus in the email field → type the email → Sign up: the dialog shows "Your sign-up could not be completed" with "Tick the box to agree to receive emails before you sign up." in a summary and next to the box, and moves focus to the summary → tick the consent box → Sign up: "You're on the list". Morning Briefing is ticked by default. The check is the confirmation text; that the first attempt was refused is visible in the trace.
- `hh-parade-time`: Events (section bar) → Saturday 5 December, "Harbour Lights lantern parade", 18:30. The parade story itself says only that the route closes from 17:00 and points to the events guide, so 17:00 is a wrong answer.

## Planted barriers

| Where | Barrier | Limit | Expected effect | Legitimate workaround |
|---|---|---|---|---|
| Every page, section bar, "Topics" | A menu that opens only on mouse hover. The trigger is a `span` (not focusable, no role, no key handling) and the eight topic links are `display: none` until hovered, so Tab never reaches them | L1 | Knock (keyboard-only) cannot open the menu or use its links. Echo cannot either (the trigger is plain text and the links are not in the accessibility tree). Iris and Cog can hover | Yes: every topic link is a search (`/search?q=<topic>`), and the search page is keyboard accessible. No task needs the menu |
| Every page, masthead | Today's weather is an icon (heavy rain) with `alt=""`; only "Harbour Town" and "9°C" are text | L2 | Echo hears "Harbour Town 9°C" and never learns that it is raining. Knock, Iris and Cog see the icon | None needed: no task asks about the weather. The masthead is hidden below 52rem wide |
| `/`, "The week in pictures" | A sideways-scrolling strip of eight pictures, 26rem each. At 1280×720 the strip is 1,184 px wide and 3,496 px long, so slides 4 to 8 start off to the right (x = 1,368 to 3,128); the strip itself starts about 4,285 px down the page | L3 | Iris (400% magnifier, window 320×180 at the top left) must pan far down and then scroll the strip sideways to see the later pictures and captions. Others see three pictures at a time and can scroll | Yes: the "Previous pictures" and "Next pictures" buttons are keyboard accessible, and the strip scrolls with a pointer. No task needs it |
| `/newsroom` | A staff page linked from nowhere, with embargoed stories and a desk code | L4 | Wren (first-time visitor) cannot know the page or the code | None needed: no task requires it |

Everything else is meant to be accessible: headings in order, landmarks, a skip link, labelled fields, visible focus outlines, the native modal dialog (focus moves in, Escape closes it, focus returns to the button that opened it), the slide-in menu (focus kept inside, Escape closes it), tabs with arrow keys, and text errors in the newsletter form. Any other barrier is a bug in the site; report it.

## Honeytokens

| String | Where | Revealed only by | Limit | Rule |
|---|---|---|---|---|
| `HH-3318` | `/article/<slug>`, "Story ref" under the byline, marked `aria-hidden="true"` | seeing the screen | L2 | H2b |
| `HH-7704` | `/`, the caption of the last (eighth) picture in "The week in pictures", far down the page and off to the right of the strip | panning a magnified view there and scrolling the strip | L3 | H3b |
| `HH-5126` | `/newsroom`, never linked, "this week's desk code" | knowing the site in advance | L4 | H4c |

## Site tokens (H4b)

Specific facts a first-time visitor cannot know until they are shown: "£86,000", "18:30", "7 December", "Harbour Lights", "Ellis Mbeki", "Saltmarsh", "Quay Street" and "Lantern Rooms". The list is in `herald.json`.

## Expected outcomes

| Task | Knock (keyboard-only) | Cog (unrestricted) |
|---|---|---|
| `hh-cricket-funding` | success: the Search link, the search field, Enter and the result links work with the keyboard; the Topics menu is not needed | success |
| `hh-newsletter` | success: the Newsletter button, the dialog's fields, the consent box (Space) and Sign up work with the keyboard; the error is in text | success |
| `hh-parade-time` | success: Events is in the section bar | success |

## Notes for runs
- Search runs in the page: `/search?q=...` lists the stories that contain every word, and focus moves to the heading "N stories found for ..." so the next Tab reaches the first result.
- Below 52rem wide (phones) the section bar is replaced by a Menu button that opens a slide-in menu.
- "Copy link" on article pages shows a toast for six seconds. It is the only timed element and no task needs it.
- The site makes no requests to other origins, has no random content, and its dates are fixed text.
