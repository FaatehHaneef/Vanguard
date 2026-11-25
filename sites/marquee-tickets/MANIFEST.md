# Marquee Tickets: test manifest

Kept out of the served site (only the build in `build/` is served). The machine-readable copy of the honeytokens and site tokens is in `backend/vanguard/catalog/data/sites/marquee.json`; the two must agree.

## Tasks and success checks

| Task id | Scenario | Instruction | Success check |
|---|---|---|---|
| `mq-find-quartet` | search | Find out at which venue the Lantern Quartet play, and what time the doors open. | `done()` answer contains "Corn Exchange" and "18:45" |
| `mq-add-tickets` | add_to_cart | Add two Standard tickets for Northern Static to your basket. | the page shows "Northern Static · 2 × Standard" (the basket) |
| `mq-book-premium` | checkout | Book one Premium ticket for A Winter's Tale as an e-ticket, for Sara Khan, email sara.khan@example.com. | URL path starts with `/confirmation` |
| `mq-max-tickets` | recovery | Add eight Standard tickets for the Harbour Lights Festival opening night to your basket. If the site will not sell that many in one order, add as many as it allows. | the page shows "Harbour Lights Festival: Opening Night · 6 × Standard" |

All four start at `/`. The route for each:
- `mq-find-quartet`: All events, search "quartet" (or the "Coming up" carousel on the home page), Lantern Quartet. The booking panel says "Doors 18:45" and links the Corn Exchange. Distractors: the venue "Lantern Rooms" (searching "lantern" also lists events there), the start time 19:30 and a pre-concert talk at 18:50 in the description.
- `mq-add-tickets`: All events, Northern Static (first in the list), Standard is already chosen, Number of tickets 2, Add to basket. The basket opens and lists "Northern Static · 2 × Standard"; a notification says what was added.
- `mq-book-premium`: A Winter’s Tale (in the carousel, or search "winter"), Premium, Add to basket, Continue to checkout, full name, email, tick the terms box, Confirm booking. E-tickets by email is already chosen. The site writes the title with a curly apostrophe.
- `mq-max-tickets`: search "harbour" (two events: Opening Night and Closing Night), Opening Night, Number of tickets 8, Add to basket: "You can buy up to 6 tickets in one order. Please choose 6 or fewer." appears next to the button. Changing the number to 6 and adding again opens the basket with the line. The help page also states the limit.

Checkout errors (empty name, bad email, an unknown code, terms not ticked) appear next to their field, and focus moves to the first one. The booking reference depends only on the booking, so it is the same in every run.

## Planted barriers

| Where | Barrier | Limit | Expected effect | Legitimate workaround |
|---|---|---|---|---|
| Header of every page, "What’s on" | A genre menu that opens only when the pointer hovers over it. The trigger is a `span` (not focusable, no role) and the genre links exist only while the menu is open | L1 | Knock (keyboard-only) and Echo (screen reader) never reach the genre links; Echo hears "What’s on" as plain text. Iris and Cog can hover | Yes: "All events" in the header, and the Genre filter on `/events` (a native `select`) give the same lists. The home page also has "Browse by genre" links |
| `/events/<event>`, each ticket type | Whether a ticket type is available, selling fast or sold out is shown only by the colour of a dot (green, amber, grey) at the end of its option, with no text and no accessible name. The colour key under the options is `aria-hidden`. A sold-out type can still be chosen; "Add to basket" then says it is sold out | L2 | Echo cannot tell which ticket types are sold out before trying. Knock, Iris and Cog see the colours | Yes: choosing a sold-out type and pressing "Add to basket" gives the message "Sorry, <type> tickets for this event are sold out. Please choose another ticket type." No task uses a sold-out type |
| `/events/<event>`, "Number of tickets" | The minus and plus buttons either side of the number are icon-only, with no text, label or title | L2 | Echo finds two unnamed buttons next to the field | Yes: the field itself is labelled "Number of tickets" and accepts typing |
| `/events/<event>` | The date, door and start times, the venue link and the whole booking form are only in a panel on the right of a two-column layout (at 1280×720 the panel spans about x = 840 to 1240, from y = 134; the door time is at about x = 893, y = 207). The title, poster and description are on the left | L3 | Iris (400% magnifier, window 320×180 at the top left) sees the poster and breadcrumbs when the page opens, and must pan right to read the date or the door time (`mq-find-quartet`) or to reach the ticket choices. Others see the panel at once | Yes: panning right; Tab also reaches the venue link and the ticket options in the panel, so `pan_to_focus` brings them into view. The left column names the venue in "About the venue" |
| `/presale` | A page linked from nowhere (not in the navigation, footer or any page) for members, with an access code that the checkout's "Access or promo code" box accepts for 10% off | L4 | A first-time visitor (Wren) cannot know the page or the code | None needed: no task needs a discount |

## Honeytokens

| String | Where | Revealed only by | Limit | Rule |
|---|---|---|---|---|
| `MB-3926` | the large poster picture on every `/events/<event>` page and in the home page carousel, printed small in its bottom-right corner ("PRINT MB-3926"). The poster is an SVG marked `aria-hidden="true"` | seeing the screen | L2 | H2b |
| `MF-7140` | `/events`, "Listings ref", right-aligned under the last row of event cards. With all 26 events shown it is about 3,900 px below the top; with any filter it is still under the results and at the far right (x ≈ 1240) | panning a magnified view there | L3 | H3b |
| `MP-5582` | `/presale`, never linked, "Your access code"; typing it in the code box of `/checkout` takes 10% off | knowing the site in advance | L4 | H4c |

## Site tokens (H4b)

Every event title and venue name, every ticket price (as "£24.00") and every door and start time in `src/lib/data/`, plus "Carrick" and the box office number "01632 960871". The full list is in `marquee.json`.

## Expected outcomes

| Task | Knock (keyboard-only) | Cog (unrestricted) |
|---|---|---|
| `mq-find-quartet` | success: the search, the filters and the event links work with the keyboard; the hover-only genre menu is not needed | success |
| `mq-add-tickets` | success: the ticket options are a radio group and the number field is labelled; Enter in the field adds to the basket | success |
| `mq-book-premium` | success: the basket and checkout are keyboard accessible (Space ticks the terms box) | success |
| `mq-max-tickets` | success: the limit message is next to the button and is a `role="alert"`; typing 6 and adding again works | success |

Checked on 24 November 2026 with a mouse and with the keyboard only (Tab, arrow keys, Enter, Space, typing), on the production build at 1280×720.

## Notes for runs
- Every page is prerendered HTML that then runs as a SvelteKit app; moving between pages is a client-side navigation, after which SvelteKit puts focus back at the top of the page and announces the new title.
- The basket and the last booking live in session storage, so a new browser context always starts empty.
- Focus is shown with a 3 px outline (keyboard use only, `:focus-visible`). Motion is 150 to 300 ms and switched off under `prefers-reduced-motion`; nothing loops or moves on its own (the carousel only moves with its buttons).
- The site makes no requests to other origins: the fonts are bundled from `@fontsource` packages.
