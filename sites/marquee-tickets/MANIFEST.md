# Marquee Tickets: test manifest

Kept out of the served site (only the build in `build/` is served). The machine-readable copy of the honeytokens and site tokens is in `backend/vanguard/catalog/data/sites/marquee.json`; the two must agree.

## Planted barriers

| Where | Barrier | Limit | Expected effect | Legitimate workaround |
|---|---|---|---|---|
| Header of every page, "What’s on" | A genre menu that opens only when the pointer hovers over it. The trigger is a `span` (not focusable, no role) and the genre links exist only while the menu is open | L1 | Knock (keyboard-only) and Echo (screen reader) never reach the genre links; Echo hears "What’s on" as plain text. Iris and Cog can hover | Yes: "All events" in the header, and the Genre filter on `/events` (a native `select`) give the same lists. The home page also has "Browse by genre" links |
| `/events/<event>`, each ticket type | Whether a ticket type is available, selling fast or sold out is shown only by the colour of a dot (green, amber, grey) at the end of its option, with no text and no accessible name. The colour key under the options is `aria-hidden`. A sold-out type can still be chosen; "Add to basket" then says it is sold out | L2 | Echo cannot tell which ticket types are sold out before trying. Knock, Iris and Cog see the colours | Yes: choosing a sold-out type and pressing "Add to basket" gives the message "Sorry, <type> tickets for this event are sold out. Please choose another ticket type." No task uses a sold-out type |
