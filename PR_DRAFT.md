# PR draft — fix(api): format trigger debug error messages instead of passing logger-style args

> Local working note. Delete this file (drop the last commit on this branch) before opening the upstream PR.

## Title

fix(api): format trigger debug error messages instead of passing logger-style args

## Body

Fixes #38476

### Root cause

Four `raise ValueError(...)` calls in the trigger debug path were written in logger style:

```python
raise ValueError("Node data not found for node %s", node_id)
```

`Exception` does not interpolate `%s`; it stores every positional argument in `args`, so `str(exc)` becomes the tuple
`('Node data not found for node %s', 'abc-123')`. That tuple is what surfaces in logs and API error responses.

Affected locations:

- `api/core/trigger/debug/event_selectors.py` — `create_event_poller` (missing node, unknown node type) and `select_trigger_debug_events` (missing node)
- `api/controllers/console/app/workflow.py` — `DraftWorkflowTriggerNodeApi.post` (missing node)

### Fix

Convert the four messages to f-strings. No behavioural change other than the message text; the exception type stays `ValueError`.

This is the same class of bug that was fixed for `resume_workflow_execution` in #37607. An earlier PR for this issue (#38478) was closed during the 2026-09-28 queue cleanup because of merge conflicts; this PR applies the same minimal change on current `main`.

### How tested

- Tightened the existing `create_event_poller` tests to assert the exact message text, and added a `select_trigger_debug_events` test for the missing-node path.
- Before the fix the three assertions failed with, for example:
  `('unable to create event poller for node type %s', 'start')` != `unable to create event poller for node type start`.
- After the fix:
  - `pytest api/tests/unit_tests/core/trigger api/tests/unit_tests/core/test_trigger_debug_event_selectors.py` — 81 passed
  - `pytest api/tests/unit_tests/controllers/console/app -k workflow` — 175 passed
  - `ruff format --check` and `ruff check` on the changed files — clean
  - `dev/pyrefly-check-local api/core/trigger/debug/event_selectors.py` — no errors

AI-assisted (Claude Code); reviewed and tested by the author

## Explain it to Govu

1. When something goes wrong in the trigger "debug run" feature, Dify throws an error with a message.
2. The code wrote the message the way you write a log line ("node %s", node_id), but errors do not fill in `%s` the way loggers do.
3. So users and logs saw an ugly pair like `('Node data not found for node %s', 'abc')` instead of a clean sentence.
4. The fix fills the value into the sentence directly (an f-string) in the four places, nothing else changes.
5. Tests now check the exact message text; they failed before the change and pass after it.
