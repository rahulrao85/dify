# PR draft — fix(api): clear and regenerate summary index when re-uploading a duplicate document

> Local working note. Delete this file (drop the last commit on this branch) before opening the upstream PR.

## Title

fix(api): clear and regenerate summary index when re-uploading a duplicate document

## Body

Fixes #36937

### Root cause

Re-uploading a file that already exists in a dataset (`knowledge_config.duplicate = True`) routes the document through `duplicate_document_indexing_task`, not the normal indexing task. That task had two gaps compared with the normal and update indexing paths:

1. It cleaned the old segments with `index_processor.clean(...)` but did not pass `delete_summaries=True`. Every index processor only deletes `DocumentSegmentSummary` rows and their summary vectors when that flag is set, so the old summaries were left behind as orphans (same flag that `delete_segment_from_index_task` already passes).
2. After re-indexing it never queued `generate_summary_index_task`, so no new summaries were produced. `document_indexing_task` and `document_indexing_update_task` both queue it once indexing completes.

### Fix

In `api/tasks/duplicate_document_indexing_task.py`:

- Pass `delete_summaries=True` when cleaning the old segments, so summary records and summary vectors are removed together with the segment vectors.
- After a successful re-index, queue `generate_summary_index_task` using the same eligibility rules as the normal indexing task: high-quality dataset, summary index enabled, document `COMPLETED`, not QA form, and `need_summary is True`. Failures to queue are logged and do not fail the task. Nothing is queued when indexing fails or is paused.

### How tested

- New SQLite-backed unit tests in `api/tests/unit_tests/tasks/test_duplicate_document_indexing_task_summaries.py` (same harness style as `test_document_indexing_update_task.py`):
  - old summaries are deleted: `clean` receives `delete_summaries=True` (failed before the fix with `KeyError: 'delete_summaries'`);
  - summary generation is queued after a completed duplicate re-index (failed before the fix: nothing was queued);
  - nothing is queued for economy datasets, disabled or missing summary settings, `need_summary=False`, QA documents, or failed indexing.
- `pytest api/tests/unit_tests/tasks api/tests/unit_tests/services/test_summary_index_service.py api/tests/unit_tests/services/knowledge` — 797 passed
- `ruff format --check`, `ruff check`, `lint-imports` (64 contracts kept), `dev/pyrefly-check-local api/tasks/duplicate_document_indexing_task.py` — clean
- Not run locally: `api/tests/test_containers_integration_tests/tasks/test_duplicate_document_indexing_task.py` (Docker/Testcontainers, CI-only). It asserts on `clean` call counts, which this change does not alter.

### Notes for reviewers

- Scope is limited to the duplicate path from the issue. `need_summary` is not recomputed for the duplicate document; it keeps the value set when the document was first created, matching how the normal and update tasks decide eligibility.
- Pre-existing edge case, unchanged by this PR: if every old segment lacks `index_node_id`, `clean` is called with an empty list and falls back to dataset-wide deletion. With `delete_summaries=True` that fallback now also covers summaries, consistent with the existing vector behaviour.
- An earlier PR for this issue (#36964) was closed during the 2026-09-28 queue cleanup because of merge conflicts. This PR uses the processor's existing `delete_summaries` flag rather than a separate service call.

AI-assisted (Claude Code); reviewed and tested by the author

## Explain it to Govu

1. Dify can write a short "summary" for every chunk of a document and store it for search.
2. When you upload the same file again, Dify takes a special "duplicate" path that rebuilds the chunks.
3. That path deleted the old chunks but forgot to delete their summaries, and it never asked for new summaries.
4. The fix tells the cleanup step to delete summaries too, and after rebuilding it queues summary generation with the same rules the normal upload uses.
5. New tests prove old summaries are removed and new ones are requested; they failed before and pass now.
