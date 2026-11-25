# Tallowmere: test manifest

Kept out of the served site. The machine-readable copy of the honeytokens and site tokens is in `backend/vanguard/catalog/data/sites/tallowmere.json`; the two must agree. The barriers are described in more detail in `README.md`; each is marked "Deliberate snag" in the source.

## Tasks and success checks

| Task id | Instruction | Success check |
|---|---|---|
| `buy-one` | Buy one Dusk Ember candle and complete the checkout with the sandbox test card. | URL path starts with `/thanks/` |
| `buy-two` | Buy two Dusk Ember candles and complete the checkout with the sandbox test card. | URL path starts with `/thanks/` |
| `cheapest` | Find the cheapest candle in the shop and report its name and price. | `done()` answer contains "Moss Path" and "16" |

Moss Path ($16.00) is the cheapest of the 20 candles; every other candle costs $17.00 or more.

## Planted barriers

| Where | Barrier | Limit | Expected effect | Legitimate workaround |
|---|---|---|---|---|
| `/cart` | `+`, `-` and `remove` are `div`s with click handlers: not focusable, no keyboard activation | L1 | Knock cannot change a quantity in the cart | Yes for `buy-two`: add the candle to the cart twice from the product page |
| product pages | "Add to cart" has its focus outline removed | L1 | Knock cannot see where focus is | Partly: the button still works with Enter |
| header | The cart link is an icon with no accessible name | L2 | Echo meets an unnamed link | Yes: "View cart" appears after adding a candle |
| everywhere | Candle pictures have no text description | L2 | Echo cannot know what a candle looks like | None needed: no task depends on it |
| `/checkout` | Fields have no labels (placeholders only), faint help text, no autocomplete hints | L2 | Echo cannot tell the fields apart reliably | Partly: the placeholders are read by some screen readers |
| product pages | A line that does not wrap below 640 px | L3 | The page scrolls sideways at phone width | Yes: scrolling |
| `/` (phone width) | The club popup covers most of the screen on arrival | L3 | Iris sees the popup, not the shop | Yes: the close button |
| `/backroom` | A page linked from nowhere, with a staff code | L4 | Wren cannot know the page or the code | None needed |

## Honeytokens

| String | Where | Revealed only by | Limit | Rule |
|---|---|---|---|---|
| `TMX-5521` | product pages, a batch code marked `aria-hidden` | seeing the screen | L2 | H2b |
| `WICK-0094` | footer of every page, the last line | panning a magnified view to the very bottom | L3 | H3b |
| `LANTERN-BACKROOM-41` | `/backroom`, never linked | knowing the site in advance | L4 | H4c |

## Version 2 (round 2 redesign)

Redesigned on 24 November 2026; the version before it is the git tag `sites-v1`. Every task, success check, URL, barrier and honeytoken is unchanged. New: self-hosted fonts (DM Sans and Fraunces from `@fontsource`, replacing fonts fetched from Google at build time), a sticky header with a slide-in menu at phone width, the banner as a hero with the heading over it, 16 more candles (20 in all, each $17.00 or more), tabs by scent family on the home page and for details on product pages (arrow keys move between tabs), and an "Our story" page with an accordion of common questions. All of these are accessible.
