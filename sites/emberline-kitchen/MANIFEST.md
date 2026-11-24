# Emberline Kitchen: test manifest

Kept out of the served site (only the build in `dist/` is served). The machine-readable copy of the honeytokens and site tokens is in `backend/vanguard/catalog/data/sites/emberline.json`; the two must agree.

## Planted barriers

| Where | Barrier | Limit | Expected effect | Legitimate workaround |
|---|---|---|---|---|
| Dish dialog (`/menu/<dish>`), "Spice level", on every dish cooked to a chosen heat | A custom dropdown built from `div`s with click handlers only: not focusable, no role, no keyboard activation, no state exposed. The list of levels (Mild, Medium, Hot, Extra hot) only appears after a mouse click | L1 | Knock (keyboard-only) and Echo (screen reader) cannot change the spice level; the dish is added at the default, Medium. Echo hears "Spice level" and "Medium" as plain text. Iris and Cog can click it | None: a dish that must be Hot cannot be ordered without a pointer (`ek-add-karahi`). Every other choice in the dialog (size, extras, quantity, Add to order) is a native control |
