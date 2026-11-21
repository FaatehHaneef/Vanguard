# AI tool declaration

Required by Assignments 3 and 4. Kept up to date as the project goes; each member adds their own use.

| Date | Member | Tool | Used for | Checked by |
|---|---|---|---|---|
| 2026-11-21 | Syed Muhammad Faateh Haneef | Claude Code (Anthropic) | Reading and summarising the course documents and the two earlier repositories; drafting `Vanguard.md` and `docs/leakage-spec.md`; writing the backend foundation (contracts, rules, gate, agent loop, store, API) and its tests; extracting and porting reused code from Sentinel | Design decisions made by the team; every file reviewed by Faateh; tests run locally |
| 2026-11-22 | Syed Muhammad Faateh Haneef | Claude Code (Anthropic) | Writing the Playwright executor (observation, event recording, network filter, screen-reader and magnifier perception, conditions), the character overlay, the leakage checker (H1, H3a, H4a, H4b, honeytokens), metrics, batches, labelling and agreement, failure analysis, the explanation generator and verifier, the OpenAI-compatible provider, the related web pages, tests, CI and documentation; verifying the downloaded datasets | Design decisions and scope set by Faateh; code to be reviewed by Faateh before submission; 80 automated tests run locally and in CI against a real Chromium |

Runtime use of AI inside the product (Gemini for the simulated user, and later local models) is described in the AI card, not here.
