"""Task-level evaluation: whole tasks across scenarios, realism, diversity and the verifier.

    python -m vanguard.evaluation <command> [options]

Single steps do not show whole failures, so this package scores runs as tasks, grouped
by task and by scenario; compares each persona's input profile with real users'
(A11y-CUA); measures how differently personas and repeated runs behave; and measures the
verifier against human labels. Every number is computed here, by code, from the trace
store. Each command writes a Markdown table to docs/results/.
"""
