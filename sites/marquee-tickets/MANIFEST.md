# Marquee Tickets: test manifest

Kept out of the served site (only the build in `build/` is served). The machine-readable copy of the honeytokens and site tokens is in `backend/vanguard/catalog/data/sites/marquee.json`; the two must agree.

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
| `MF-7140` | `/events`, "Listings ref", right-aligned under the last row of event cards. With all 26 events shown it is about 4,000 px below the top; with any filter it is still under the results and at the far right (x ≈ 1240) | panning a magnified view there | L3 | H3b |
| `MP-5582` | `/presale`, never linked, "Your access code"; typing it in the code box of `/checkout` takes 10% off | knowing the site in advance | L4 | H4c |
