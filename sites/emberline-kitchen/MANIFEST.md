# Emberline Kitchen: test manifest

Kept out of the served site (only the build in `dist/` is served). The machine-readable copy of the honeytokens and site tokens is in `backend/vanguard/catalog/data/sites/emberline.json`; the two must agree.

## Tasks and success checks

| Task id | Scenario | Instruction | Success check |
|---|---|---|---|
| `ek-find-prawn` | search | Find out which curry on the menu is made with prawns and how much it costs. | `done()` answer contains "Prawn Malabar" and "14.50" |
| `ek-add-karahi` | add_to_cart | Add one large Chicken Karahi, cooked hot, to your order. | the page shows "Chicken Karahi · Large · Hot" (the order drawer or the checkout summary) |
| `ek-pickup-order` | checkout | Order one portion of Masala Fries for pickup at 18:30, under the name Sara Khan, phone 07700 900123. | URL path starts with `/order/confirmed` |
| `ek-late-pickup` | recovery | Order one Mango Kulfi for pickup at 22:15, under the name Omar Rahim, phone 07700 900456. If the kitchen does not take orders for that time, choose the latest pickup time it accepts. | the page shows "ready for pickup at 21:30" |

All four start at `/`. The route for each:
- `ek-find-prawn`: Menu, type "prawn" in the search box: one dish matches, Prawn Malabar Curry, £14.50 (Large is £17.50, shown only in its dialog). The "Curries" tab also lists it with six other curries.
- `ek-add-karahi`: Menu (or the Chicken Karahi card under "What Harwick is ordering" on the home page), Chicken Karahi, Size: Large, Spice level: Hot, Add to order. The order drawer opens by itself and shows the line "Chicken Karahi · Large · Hot". Without changing the spice level the line reads "Chicken Karahi · Large · Medium", which does not pass. Extras appear on a second line ("With cucumber raita"), so they do not affect the check.
- `ek-pickup-order`: Masala Fries (a home page favourite), Add to order, Go to checkout in the drawer, name, phone, pickup time 18:30, Place order. Seven actions from the home page card. The order number depends only on the order, so it is the same in every run.
- `ek-late-pickup`: as above with Mango Kulfi and 22:15. "Place order" shows the notification "That pickup time is not available. We take pickup orders from 12:00 to 21:30." Changing the time to 21:30 and placing the order again shows "Your order will be ready for pickup at 21:30". The pickup hours are also on `/hours` and in the footer, so a person who checks first can type 21:30 at once.

"07700 900123" and "07700 900456" are in the reserved drama range; any UK number of 10 or 11 digits starting with 0 is accepted. Other checkout errors (empty name, bad phone, a time that is not hours and minutes, an unknown promo code) appear next to their field, and focus moves to the first one.

## Planted barriers

| Where | Barrier | Limit | Expected effect | Legitimate workaround |
|---|---|---|---|---|
| Dish dialog (`/menu/<dish>`), "Spice level", on every dish cooked to a chosen heat | A custom dropdown built from `div`s with click handlers only: not focusable, no role, no keyboard activation, no state exposed. The list of levels (Mild, Medium, Hot, Extra hot) only appears after a mouse click | L1 | Knock (keyboard-only) and Echo (screen reader) cannot change the spice level; the dish is added at the default, Medium. Echo hears "Spice level" and "Medium" as plain text. Iris and Cog can click it | None: a dish that must be Hot cannot be ordered without a pointer (`ek-add-karahi`). Every other choice in the dialog (size, extras, quantity, Add to order) is a native control |
| Header of every page, right of the navigation | The order (cart) button is a shopping-bag icon with a red count badge. It has no text, no label and no title, and the badge is `aria-hidden` | L2 | Echo finds an unnamed button in the banner and cannot tell what it does or how many items are in the order. Others see the bag and the count | Yes: adding a dish opens the order drawer by itself; on `/menu` a bar at the bottom ("1 item in your order · £4.75", "Check out") links to `/checkout`; the checkout page lists the order and has "Change your order" |
| `/menu` and the dish dialog, next to each price | Whether a dish is vegan or vegetarian is shown only by the colour of a leaf mark (dark green for vegan, light green for vegetarian), with no text and no accessible name. A colour key above the dishes says "Vegan" and "Vegetarian" | L2 | Echo cannot tell which dishes are vegan or vegetarian: the marks are absent from the accessibility tree and the key's swatches are `aria-hidden`. Knock, Iris and Cog can see the colour | Partly: descriptions sometimes say what is in a dish. No task asks about diets |
| `/checkout`, after "Place order" with a pickup time outside 12:00 to 21:30 | The only message ("That pickup time is not available. We take pickup orders from 12:00 to 21:30. Please choose a time in that window.") is a notification fixed to the bottom-right corner of the window (about x = 880 to 1260, y = 560 to 700 at 1280×720). Nothing changes next to the form, and focus stays on "Place order" | L3 | Iris (400% magnifier, 320×180 window near the button) does not see why the order was not placed, and must pan to the corner to read the reason. Echo hears it (`role="alert"`). Knock and Cog see it at once | Yes: panning to the bottom-right corner; the notification stays until dismissed or the next attempt. The pickup hours are also on `/hours` and in the footer |
| `/chefs-table` | A page linked from nowhere (not in the navigation, footer or any page) for guests of the monthly tasting evenings, with a guest code that the checkout's promo code box accepts for £5.00 off | L4 | A first-time visitor (Wren) cannot know the page or the code | None needed: no task needs a discount |

## Honeytokens

| String | Where | Revealed only by | Limit | Rule |
|---|---|---|---|---|
| `EB-4417` | `/order/confirmed`, printed under the barcode of the collection ticket picture. The picture is an SVG marked `aria-hidden="true"` | seeing the screen | L2 | H2b |
| `EF-8053` | footer of every page, "Food business registration", right-aligned on the last line. `main` is at least one window high (`min-height: calc(100vh - header)`), so the footer always starts below the first screen | panning a magnified view there | L3 | H3b |
| `EC-2690` | `/chefs-table`, never linked, "Your guest code"; typing it in the promo code box of `/checkout` takes £5.00 off | knowing the site in advance | L4 | H4c |

## Site tokens (H4b)

Every dish and extra name and every price in `src/data/menu.ts` (as "£14.50"), the pickup hours "12:00" and "21:30", "Copper Street", "Harwick", "HW2 4LT" and the phone number "01632 960214". The full list is in `emberline.json`.

## Expected outcomes

| Task | Knock (keyboard-only) | Cog (unrestricted) |
|---|---|---|
| `ek-find-prawn` | success: the search box, the tabs (arrow keys) and the dish links all work with the keyboard | success |
| `ek-add-karahi` | **failure**: Size is a radio group and works, but the spice level picker cannot be opened, so the line is "Chicken Karahi · Large · Medium". There is no workaround | success |
| `ek-pickup-order` | success: the dish dialog, the drawer and the checkout form are keyboard accessible | success |
| `ek-late-pickup` | success: the notification is visible in the full view and is a `role="alert"`; changing the time and placing the order again works | success |

Checked on 24 November 2026 with a mouse and with the keyboard only (Tab, arrow keys, Enter, typing), on the production build at 1280×720.

## Notes for runs
- Moving to another page puts keyboard focus on that page's main heading, as a fresh page load would. Opening a dish moves focus into its dialog; closing it (Escape, Close or the backdrop) returns focus to the dish link. The order drawer does the same. These are page scripts moving focus, not the agent's input.
- The dialog and the drawer keep Tab inside themselves until they close.
- Placing an order waits a fixed 250 ms ("Placing your order…") before the confirmation page.
- The order and the last placed order live in session storage, so a new browser context always starts empty.
- Focus is shown with a 3 px outline (keyboard use only, `:focus-visible`). Motion is 150 to 300 ms and switched off under `prefers-reduced-motion`; nothing loops or moves on its own (the reviews carousel only moves with its buttons).
- The site makes no requests to other origins: the fonts are bundled from `@fontsource` packages.
