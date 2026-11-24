# Marquee Tickets: test manifest

Kept out of the served site (only the build in `build/` is served). The machine-readable copy of the honeytokens and site tokens is in `backend/vanguard/catalog/data/sites/marquee.json`; the two must agree.

## Planted barriers

| Where | Barrier | Limit | Expected effect | Legitimate workaround |
|---|---|---|---|---|
| Header of every page, "What’s on" | A genre menu that opens only when the pointer hovers over it. The trigger is a `span` (not focusable, no role) and the genre links exist only while the menu is open | L1 | Knock (keyboard-only) and Echo (screen reader) never reach the genre links; Echo hears "What’s on" as plain text. Iris and Cog can hover | Yes: "All events" in the header, and the Genre filter on `/events` (a native `select`) give the same lists. The home page also has "Browse by genre" links |
