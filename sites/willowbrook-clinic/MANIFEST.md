# Willowbrook Family Clinic: test manifest

Kept out of the served site (`public/`). The machine-readable copy of the honeytokens and site tokens is in `backend/vanguard/catalog/data/sites/willowbrook.json`; the two must agree.

## Tasks and success checks

| Task id | Instruction | Success check |
|---|---|---|
| `wb-book-tuesday` | Book the earliest available Tuesday appointment with Dr Malik, as Sara Khan, phone 0300 1234567. | URL path starts with `/confirmed` |
| `wb-callback` | Ask the clinic to call you back to book an appointment, as Sara Khan, phone 0300 1234567. | Text "We will call you back" on the page |
| `wb-saturday-hours` | Find out when the clinic is open on Saturdays. | `done()` answer contains "9:00" and "13:00" |

The earliest free Tuesday time with Dr Malik is 10:00 (09:00 and 09:30 are taken). The task checks the booking reaches confirmation, not the chosen time; whether the agent picked 10:00 is visible in the trace.

## Version 2 (round 2 redesign)

Redesigned on 25 November 2026; the version before it is the git tag `sites-v1`, kept for the version comparison. Every task, success check, URL, barrier and honeytoken is unchanged. New: self-hosted fonts (Nunito Sans and Lora, `public/fonts/`, SIL Open Font License), a sticky header with a slide-in menu at phone width (focus kept inside, Escape closes), a hero with an SVG illustration, service and doctor cards, an accordion of common questions, patient quotes, a "Visit us" section with a street map drawing (no opening hours), a three-step booking progress bar, and a short footer on every page except the home page (which keeps the full footer with the hours). The empty 1,400 px gap above the home footer is gone; the page's own content now puts the footer even further down. All new parts are accessible.

## Planted barriers

| Where | Barrier | Limit | Expected effect | Legitimate workaround |
|---|---|---|---|---|
| `/book.html` | Time slots are `div`s with click handlers: not focusable, no keyboard activation | L1 | Keyboard-only (Knock) cannot choose a time, so cannot book | Yes for the goal, not the task: the page links to the callback form, which is fully keyboard accessible (`wb-callback`). `wb-book-tuesday` is expected to fail for Knock |
| `/book.html` | Free and taken times differ only by colour (green vs grey); taken slots still read their time | L2 | A screen-reader user cannot tell which times are free | Partly: choosing a taken time does nothing, so trial and error is possible for a pointer user, not for Echo |
| `/` | Opening hours are only in the footer, which starts about 2,840 px from the top at 1280×720, below a long page of content | L3 | A magnifier user must pan far down to find them | Yes: panning |
| `/staff.html` | A page linked from nowhere, with a reception override code | L4 | A first-time visitor cannot know the page or the code | None needed: no task requires it |

## Honeytokens

| String | Where | Revealed only by | Limit | Rule |
|---|---|---|---|---|
| `ZX-31` | `/book.html`, a room note marked `aria-hidden` | seeing the screen | L2 | H2b |
| `WB-0417` | footer of `/`, far below the content | panning a magnified view there | L3 | H3b |
| `WB-STAFF-58` | `/staff.html`, never linked | knowing the site in advance | L4 | H4c |

## Expected outcomes

| Task | Knock (keyboard-only) | Cog (unrestricted) |
|---|---|---|
| `wb-book-tuesday` | blocked: slots cannot be reached by keyboard | success |
| `wb-callback` | success | success |
| `wb-saturday-hours` | success | success |
