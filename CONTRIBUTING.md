# Working on Vanguard

## Branches and commits
- `main` always passes CI.
- If you were given tasks in `docs/tasks-A3-round2.md` (the current task file; `docs/tasks-A3.md` is outdated), work only on your own branches named there. Otherwise use the standing branch for your area: `websites` (test sites), `engine`, `evaluation`, `app` or `docs` (see `Vanguard.md`, Section 4.6b).
- Never commit to, push to or merge into `main`, and never delete a branch. Push your branch and tell Faateh; Faateh merges into `main` with `--no-ff`.
- Small commits with conventional messages: `feat(scope): ...`, `fix: ...`, `docs: ...`, `test: ...`, `chore: ...`, `ci: ...`.
- Commit your own work from your own GitHub account and git identity. Never commit for someone else.
- No AI attribution anywhere: no `Co-Authored-By`, "Generated with ..." or similar lines in commits, pull requests or files. Declare your AI tool use in your own row of `AI_USE.md` instead, as the course requires.
- Never commit secrets. `.env` is ignored; add new settings to `.env.example`.

## Data and sites
- Datasets live outside the repository, in the folder named by `VANGUARD_DATA_DIR`. Never commit dataset files.
- Test sites must contain nothing about Vanguard in anything they serve (`docs/test-site-kit.md`).

## Contracts
`backend/vanguard/contracts` and `docs/leakage-spec.md` are shared by everyone. Change them only by agreement: update the spec first, then the code, then bump `CONTRACT_VERSION`.

## Rules for AI components
- A language model may propose actions and write explanations. It never counts, scores, checks rules or decides leakage; code does.
- Every model call is logged with the provider, model, prompt version, latency and tokens.

## Before you push
```bash
cd backend && ruff format . && ruff check . && pytest -q
```
