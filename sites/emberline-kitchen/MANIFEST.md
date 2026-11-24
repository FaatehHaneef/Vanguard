# Emberline Kitchen: test manifest

Kept out of the served site (only the build in `dist/` is served). The machine-readable copy of the honeytokens and site tokens is in `backend/vanguard/catalog/data/sites/emberline.json`; the two must agree.

## Planted barriers

| Where | Barrier | Limit | Expected effect | Legitimate workaround |
|---|---|---|---|---|
| Dish dialog (`/menu/<dish>`), "Spice level", on every dish cooked to a chosen heat | A custom dropdown built from `div`s with click handlers only: not focusable, no role, no keyboard activation, no state exposed. The list of levels (Mild, Medium, Hot, Extra hot) only appears after a mouse click | L1 | Knock (keyboard-only) and Echo (screen reader) cannot change the spice level; the dish is added at the default, Medium. Echo hears "Spice level" and "Medium" as plain text. Iris and Cog can click it | None: a dish that must be Hot cannot be ordered without a pointer (`ek-add-karahi`). Every other choice in the dialog (size, extras, quantity, Add to order) is a native control |
| Header of every page, right of the navigation | The order (cart) button is a shopping-bag icon with a red count badge. It has no text, no label and no title, and the badge is `aria-hidden` | L2 | Echo finds an unnamed button in the banner and cannot tell what it does or how many items are in the order. Others see the bag and the count | Yes: adding a dish opens the order drawer by itself; on `/menu` a bar at the bottom ("1 item in your order · £4.75", "Check out") links to `/checkout`; the checkout page lists the order and has "Change your order" |
| `/menu` and the dish dialog, next to each price | Whether a dish is vegan or vegetarian is shown only by the colour of a leaf mark (dark green for vegan, light green for vegetarian), with no text and no accessible name. A colour key above the dishes says "Vegan" and "Vegetarian" | L2 | Echo cannot tell which dishes are vegan or vegetarian: the marks are absent from the accessibility tree and the key's swatches are `aria-hidden`. Knock, Iris and Cog can see the colour | Partly: descriptions sometimes say what is in a dish. No task asks about diets |
| `/checkout`, after "Place order" with a pickup time outside 12:00 to 21:30 | The only message ("That pickup time is not available. We take pickup orders from 12:00 to 21:30. Please choose a time in that window.") is a notification fixed to the bottom-right corner of the window (about x = 880 to 1260, y = 560 to 700 at 1280×720). Nothing changes next to the form, and focus stays on "Place order" | L3 | Iris (400% magnifier, 320×180 window near the button) does not see why the order was not placed, and must pan to the corner to read the reason. Echo hears it (`role="alert"`). Knock and Cog see it at once | Yes: panning to the bottom-right corner; the notification stays until dismissed or the next attempt. The pickup hours are also on `/hours` and in the footer |

## Honeytokens

| String | Where | Revealed only by | Limit | Rule |
|---|---|---|---|---|
| `EB-4417` | `/order/confirmed`, printed under the barcode of the collection ticket picture. The picture is an SVG marked `aria-hidden="true"` | seeing the screen | L2 | H2b |
| `EF-8053` | footer of every page, "Food business registration", right-aligned on the last line. `main` is at least one window high (`min-height: calc(100vh - header)`), so the footer always starts below the first screen | panning a magnified view there | L3 | H3b |
