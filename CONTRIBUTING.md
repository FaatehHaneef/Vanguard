# Working on Vanguard

## Branches and commits
- `main` always passes CI.
- Work on the standing branch for your area: `websites` (test sites), `engine`, `evaluation`, `app` or `docs` (see `Vanguard.md`, Section 4.6b). Merge into `main` with `--no-ff` when a piece is ready, and keep the branch. Add your own branch only for something that fits none of them. Open a pull request into `main` for anything substantial, and ask a teammate to review.
- Small commits with conventional messages: `feat(scope): ...`, `fix: ...`, `docs: ...`, `test: ...`, `chore: ...`, `ci: ...`.
- Commit your own work from your own GitHub account. Never commit for someone else.
- Never commit secrets. `.env` is ignored; add new settings to `.env.example`.

## Contracts
`backend/vanguard/contracts` and `docs/leakage-spec.md` are shared by everyone. Change them only by agreement: update the spec first, then the code, then bump `CONTRACT_VERSION`.

## Rules for AI components
- A language model may propose actions and write explanations. It never counts, scores, checks rules or decides leakage; code does.
- Every model call is logged with the provider, model, prompt version, latency and tokens.

## Before you push
```bash
cd backend && ruff format . && ruff check . && pytest -q
```
