# CP-G2: several actions per call, call accounting, usage and --max-calls

Merged on Tue 24 Nov 2026. Steps that wait on CP-G2 can start: Hadi H12 (verifier runs) and Ibrahim E4 (calls vs actions) and E9 (task-suite runs). Run `git merge origin/main` on your branch first.

## Several actions per model call
- The model may now return up to `VANGUARD_ACTIONS_PER_CALL` tool calls in one reply. The default is 4; set it to 1 for one action per call.
- Each action is its own step: gated, checked by the verifier when that option is on, executed and recorded in order.
- The rest of a call is dropped when one of these happens:
  - an action is refused, invalid or fails;
  - the page address changes;
  - a planned element id is no longer on the page.

  The model then sees the page again.
- The prompt says so. Its version is now `agent-v0.2`.
- The run records the limit it used in `RunConfig.actions_per_call`. Older runs have `null`, which means 1.
- Only observations shown to the model count as perceived (for H3a, H4a and H4b). The checker judges later actions of a call against the call's first observation.

## New step fields (`StepRecord`, contracts 0.8.0)
- `call`: which model call proposed the step (0, 1, ...). It is `null` in runs made before this change, where every step was its own call.
- `in_call`: the step's position within its call. 0 is the first.
- `model_call` (a property): `in_call == 0`. True for exactly one step per call, and for every step of older runs.
- Tokens are recorded on the first step of a call only. `latency_ms` on that step includes the model's time. Later steps of the call have only their execution time.

Model calls for a run (Ibrahim, E4) are:

```python
from vanguard.usage import calls_in
calls_in(steps)  # agent calls (steps with in_call == 0) + verifier checks (steps with a verifier decision)
```

Actions are the steps. Use `calls_in`, so calls are counted the same way everywhere.

## Usage and the call budget
```bash
cd backend
python -m vanguard.cli usage
```
This prints:
- the model calls made from your machine's database since midnight Pacific (1 PM here), when the Gemini free tier resets, split into agent and verifier calls;
- the budget: your keys × 20;
- what is left today, as a ready `--max-calls` value.

`batch --max-calls N` stops before a run that could take the batch past N calls. The first run is allowed `max_steps` calls (twice that with the verifier). After that, the check uses the largest number of calls any run in that batch has needed so far.

Example (Hadi, H12):
```bash
python -m vanguard.cli usage
python -m vanguard.cli batch --site tallowmere --tasks cheapest --personas keyboard-only unrestricted \
  --enforcements verifier --repeats 3 --max-steps 12 --max-calls <left today> --batch verifier-a3-tm
```
The batch prints `stopped: call budget reached (...)` when it stops for this reason. Run the same command the next day to continue: finished runs are never repeated.

`--actions-per-call N` on `run` and `batch` overrides the setting for one run or batch.

## Check on real Gemini
- One keyboard-only gate run on Willowbrook (`wb-callback`, 12 steps at most) used 5 model calls for its 12 steps. One call ran Tab, Tab, Tab, Enter, and another ran Tab, type, Tab, type.
- Gemini was slow on 24 Nov: a bare "Say ok." took 60 to 75 seconds, so a 12-step run took about 10 minutes. Start long batches early and leave them running.
