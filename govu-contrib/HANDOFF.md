# Dify contribution handoff: three ready fixes and next steps

Prepared: 7 October 2026 (IST), Claude Code cloud session.
Owner: Rahul Rao (fork `rahulrao85/dify`).
Upstream: `langgenius/dify`, `main` at commit `e7d9c889`.

This one document holds everything needed to resume in a new session: what is done, what needs your decision, the exact next steps, the full PR drafts, and the full issue triage.

---

## 1. Where everything is saved

| Item | Location |
|---|---|
| This handoff document | Branch `govu-triage`, file `govu-contrib/HANDOFF.md` — https://github.com/rahulrao85/dify/blob/govu-triage/govu-contrib/HANDOFF.md |
| Full triage (separate copy) | Branch `govu-triage`, file `TRIAGE.md` |
| Fix 1 (#38476) | Branch `fix/38476-trigger-debug-error-messages` |
| Fix 2 (#36937) | Branch `fix/36937-duplicate-reindex-summaries` |
| Fix 3 (#39629) | Branch `fix/39629-mcp-unsupported-param-type` |
| PR draft for each fix | `PR_DRAFT.md` at the root of each fix branch (also copied in full into Appendix A–C below) |

Important: the cloud container used for this work is temporary. The GitHub branches above are the durable copy. Nothing was posted, commented or opened on `langgenius/dify`, and nothing was pushed to `main`.

Branch links:
- https://github.com/rahulrao85/dify/tree/fix/38476-trigger-debug-error-messages
- https://github.com/rahulrao85/dify/tree/fix/36937-duplicate-reindex-summaries
- https://github.com/rahulrao85/dify/tree/fix/39629-mcp-unsupported-param-type
- https://github.com/rahulrao85/dify/tree/govu-triage

---

## 2. Status at a glance

| Branch | Issue | What it fixes (plain English) | Tests | Confidence |
|---|---|---|---|---|
| `fix/38476-trigger-debug-error-messages` | #38476 | Trigger "debug run" errors showed as an ugly tuple instead of a readable sentence | Failing test written first; after fix 256 related tests pass; ruff and pyrefly clean | High |
| `fix/36937-duplicate-reindex-summaries` | #36937 | Re-uploading the same document left old summaries behind and never generated new ones | Failing tests written first; after fix 797 related tests pass; ruff, import linter and pyrefly clean | Medium |
| `fix/39629-mcp-unsupported-param-type` | #39629 | One unusual field type from an external MCP tool server crashed the whole provider | Six failing cases written first; after fix 922 related tests pass; ruff and pyrefly clean | High |

Each fix branch has two commits on top of upstream `main`: (1) the fix plus tests, (2) a commit that only adds `PR_DRAFT.md`. Commit (2) must be removed before opening the upstream PR.

What was NOT verified in the cloud session:
- Full `make lint` and `make type-check` across the whole `api/` package (only the changed files were checked). The upstream PR template asks for the full commands.
- Docker-based integration tests (`api/tests/test_containers_integration_tests/...`). These are CI-only per the repository guidance.
- Issue comment threads and 👍 counts on upstream issues (GitHub hides them from logged-out page fetches). "Nobody has claimed it" is therefore not fully confirmed.

---

## 3. Decisions that depend on you (review these first)

Please review and decide on each item. None of these can be decided by an agent on your behalf.

| # | Decision | Context | My recommendation |
|---|---|---|---|
| D1 | Accept issues that already have a closed, unmerged PR | All three issues had an earlier PR by someone else. Two were closed by maintainer crazywoola on 28 Sep 2026 only for merge conflicts ("reopen this PR or submit a new one"); the #39629 PR was closed by its own author. Maintainers stated a rule: a PR from the issue author ranks first, then the earliest PR. | Proceed, but credit the earlier PR in the description (already done in the drafts) and check the issue page logged in for any recent "I will reopen" comment before submitting. |
| D2 | Order of submission | Submitting all three at once is fine; they touch unrelated files. | Submit #39629 and #38476 first (smallest, highest confidence), then #36937. |
| D3 | #39629 behaviour change | MCP servers can no longer declare Dify-internal types such as `file` or `secret-input`; those become plain text. | Keep it (it matches the issue and the earlier PR) and leave the reviewer note in the PR as written. |
| D4 | #36937 scope | The fix does not recompute `need_summary` for the duplicate document, and inherits a pre-existing edge case (segments without index IDs trigger dataset-wide cleanup). Both are documented in the draft. | Keep the scope minimal; let maintainers ask for more. |
| D5 | AI disclosure wording | CONTRIBUTING.md allows AI tools if you understand and verify every change. Each draft ends with "AI-assisted (Claude Code); reviewed and tested by the author". The PR template also says an automated agent should add `From <Tool Name>` as the final line. Each commit currently carries a `Co-Authored-By: Claude` trailer. | Keep the AI-assisted line. Because you open the PR yourself, `From Claude Code` is optional; adding it is the more transparent choice. Keep or remove the commit trailer per your preference. |
| D6 | Account to submit from | The fork is `rahulrao85/dify`. | Use your personal GitHub account; keep this entirely separate from CloudRock. |
| D7 | Whether to take on more issues | Remaining good candidates are listed in Section 6. | Wait until the first three get maintainer feedback, then pick one more. |

---

## 4. Detailed next steps (in order)

### Step 1 — Re-check upstream before doing anything (5 minutes per issue)

Open each issue while logged in to GitHub and confirm:
- No new open PR has appeared (check the "Development" sidebar and search PRs for the issue number).
- No comment says someone is working on it, and the earlier PR author has not reopened.
- The issue is still open.

Links: https://github.com/langgenius/dify/issues/38476 , https://github.com/langgenius/dify/issues/36937 , https://github.com/langgenius/dify/issues/39629

If an open PR now exists for an issue, drop that fix (do not open a duplicate).

### Step 2 — Read and understand each change

For each branch, read the diff and the "Explain it to Govu" section in its draft (Appendix A–C). You must be able to explain the root cause and the fix in your own words; CONTRIBUTING.md requires this for AI-assisted work.

```bash
git fetch origin
git diff upstream/main...origin/fix/38476-trigger-debug-error-messages -- api
git diff upstream/main...origin/fix/36937-duplicate-reindex-summaries -- api
git diff upstream/main...origin/fix/39629-mcp-unsupported-param-type -- api
```

### Step 3 — Bring each branch up to date and remove the draft commit

Run from a clone of the fork (one-time setup shown first):

```bash
git clone https://github.com/rahulrao85/dify && cd dify
git remote add upstream https://github.com/langgenius/dify
git fetch upstream main
uv sync --project api --group dev

# For each fix branch (example uses #38476):
git checkout fix/38476-trigger-debug-error-messages
git reset --hard HEAD~1                 # removes the PR_DRAFT.md-only commit
git rebase upstream/main                # branch is yours, so rebase is fine
```

Keep a copy of `PR_DRAFT.md` text before resetting (it is also in Appendix A–C of this document).

### Step 4 — Re-run checks on the updated branch

```bash
# Targeted tests per branch
# 38476
uv run --project api --dev pytest -p no:benchmark --no-cov api/tests/unit_tests/core/trigger api/tests/unit_tests/core/test_trigger_debug_event_selectors.py
uv run --project api --dev pytest -p no:benchmark --no-cov api/tests/unit_tests/controllers/console/app -k workflow
# 36937
uv run --project api --dev pytest -p no:benchmark --no-cov api/tests/unit_tests/tasks api/tests/unit_tests/services/test_summary_index_service.py api/tests/unit_tests/services/knowledge
# 39629
uv run --project api --dev pytest -p no:benchmark --no-cov api/tests/unit_tests/services/tools api/tests/unit_tests/core/tools api/tests/unit_tests/core/mcp

# What the upstream PR template asks for (whole backend)
make lint
make type-check
```

If `make lint` reformats any file you did not change, do not commit those changes (no unrelated formatting).

### Step 5 — Push and open the PR from GitHub (by you, manually)

```bash
git push --force-with-lease origin fix/38476-trigger-debug-error-messages
```

Then on GitHub: open the branch in `rahulrao85/dify`, click "Contribute" → "Open pull request" against `langgenius/dify:main`. Fill the upstream template (Section 5 below) using the draft text from Appendix A–C. Leave "Allow edits by maintainers" ticked.

### Step 6 — After opening

- Watch for CI results and the "Claude Approvals"/review bots; fix failures promptly with a normal new commit.
- Reply to reviewer comments within a day or two; maintainers close stale PRs during queue cleanups.
- If the PR gets merge conflicts later, merge or rebase `upstream/main` again and push.

---

## 5. Upstream PR template (fill this for each PR)

```markdown
> [!IMPORTANT]
> 1. Make sure you have read our contribution guidelines
> 1. Ensure there is an associated issue
> 1. Use the correct syntax to link this PR: `Fixes #<issue number>`.

## Summary

Fixes #<N>

<Root cause, fix and how tested: copy from the matching appendix below, in your own words>

AI-assisted (Claude Code); reviewed and tested by the author

## Screenshots

| Before | After |
| ------ | ----- |
| N/A (backend) | N/A (backend) |

## Checklist

- [ ] This change requires a documentation update, included: Dify Document
- [x] I understand that this PR may be closed in case there was no previous discussion or issues.
- [x] I've verified the change and added or updated tests where meaningful regression risk justifies coverage.
- [ ] I've updated the documentation accordingly.
- [x] I ran `make lint && make type-check` (backend) and `vp staged` (frontend) to appease the lint gods
```

Tick the last box only after you have actually run both commands in Step 4.

---

## 6. Further candidates for later (not started)

| Issue | Area | Summary | Effort / risk |
|---|---|---|---|
| #40961 | api, knowledge | Switching the embedding model re-indexes with the old model, because Celery tasks are dispatched before the database commit. Fix: dispatch after commit (precedent in `api/tasks/new_agent_beta_task.py:68`). | ~90 lines / medium |
| #41457 | api, knowledge segments | Deleting a disabled multimodal segment leaves attachment rows orphaned. | ~100 lines / medium |
| #39560 | api, RAG token counting | Token counting sends the whole document in one plugin request (HTTP 413, plugin OOM). Batch it. | ~80 lines / low–medium |
| #40985 | web, model selector | "does not have provider_credential_schema" when adding a customizable-only model. Most 👍 of any candidate (6). | ~60 lines / low–medium |
| #39302 | api, human-in-the-loop forms | Public form endpoints accept console-only tokens. Security-adjacent; coordinate with maintainers first. | ~60 lines / medium |

Full details for all 16 candidates and the 442 rejected issues are in Appendix D.

---

## 7. Ready-to-paste prompt for the next session

```text
Repository: my fork rahulrao85/dify (upstream langgenius/dify).
Read govu-contrib/HANDOFF.md on branch govu-triage first; it is the full context.
Task: for each of the three fix branches (fix/38476-trigger-debug-error-messages,
fix/36937-duplicate-reindex-summaries, fix/39629-mcp-unsupported-param-type):
1. Check upstream (public pages) for any new open PR or claim on the issue; stop and report if found.
2. Check out the branch, drop the last commit (it only adds PR_DRAFT.md), rebase onto upstream/main.
3. Run the targeted tests listed in HANDOFF.md Step 4, then `make lint` and `make type-check`;
   do not commit unrelated formatting. Report exactly what passed and what could not run.
4. Push with --force-with-lease to the same branch on origin (rahulrao85/dify).
Hard rules: never open a PR, comment, react or file an issue on upstream; never push to main;
no unrelated refactors. I will open the upstream PRs myself.
Finish with a table: branch | rebased (y/n) | tests | lint | type-check | ready (y/n) | notes.
```

---

## 8. Key facts to remember in review conversations

- Dify's own guidance: run backend commands through `uv run --project api`; keep new code out of `api/core/`; integration tests are CI-only.
- Model-runtime and tool bugs belong to `dify-plugins` / `dify-official-plugins`, not this repository. (MCP provider handling, fixed in #39629, does live in this repository.)
- The `review: low/medium/high/top` labels on issues are applied by a bot, not by maintainers.
- In this repository most bug reports arrive together with a fix PR on the same day, so speed matters once you decide to submit.

---

## Appendix A — PR draft for #38476 (branch fix/38476-trigger-debug-error-messages)

### PR draft — fix(api): format trigger debug error messages instead of passing logger-style args

> Local working note. Delete this file (drop the last commit on this branch) before opening the upstream PR.

#### Title

fix(api): format trigger debug error messages instead of passing logger-style args

#### Body

Fixes #38476

##### Root cause

Four `raise ValueError(...)` calls in the trigger debug path were written in logger style:

```python
raise ValueError("Node data not found for node %s", node_id)
```

`Exception` does not interpolate `%s`; it stores every positional argument in `args`, so `str(exc)` becomes the tuple
`('Node data not found for node %s', 'abc-123')`. That tuple is what surfaces in logs and API error responses.

Affected locations:

- `api/core/trigger/debug/event_selectors.py` — `create_event_poller` (missing node, unknown node type) and `select_trigger_debug_events` (missing node)
- `api/controllers/console/app/workflow.py` — `DraftWorkflowTriggerNodeApi.post` (missing node)

##### Fix

Convert the four messages to f-strings. No behavioural change other than the message text; the exception type stays `ValueError`.

This is the same class of bug that was fixed for `resume_workflow_execution` in #37607. An earlier PR for this issue (#38478) was closed during the 2026-09-28 queue cleanup because of merge conflicts; this PR applies the same minimal change on current `main`.

##### How tested

- Tightened the existing `create_event_poller` tests to assert the exact message text, and added a `select_trigger_debug_events` test for the missing-node path.
- Before the fix the three assertions failed with, for example:
  `('unable to create event poller for node type %s', 'start')` != `unable to create event poller for node type start`.
- After the fix:
  - `pytest api/tests/unit_tests/core/trigger api/tests/unit_tests/core/test_trigger_debug_event_selectors.py` — 81 passed
  - `pytest api/tests/unit_tests/controllers/console/app -k workflow` — 175 passed
  - `ruff format --check` and `ruff check` on the changed files — clean
  - `dev/pyrefly-check-local api/core/trigger/debug/event_selectors.py` — no errors

AI-assisted (Claude Code); reviewed and tested by the author

#### Explain it to Govu

1. When something goes wrong in the trigger "debug run" feature, Dify throws an error with a message.
2. The code wrote the message the way you write a log line ("node %s", node_id), but errors do not fill in `%s` the way loggers do.
3. So users and logs saw an ugly pair like `('Node data not found for node %s', 'abc')` instead of a clean sentence.
4. The fix fills the value into the sentence directly (an f-string) in the four places, nothing else changes.
5. Tests now check the exact message text; they failed before the change and pass after it.

---

## Appendix B — PR draft for #36937 (branch fix/36937-duplicate-reindex-summaries)

### PR draft — fix(api): clear and regenerate summary index when re-uploading a duplicate document

> Local working note. Delete this file (drop the last commit on this branch) before opening the upstream PR.

#### Title

fix(api): clear and regenerate summary index when re-uploading a duplicate document

#### Body

Fixes #36937

##### Root cause

Re-uploading a file that already exists in a dataset (`knowledge_config.duplicate = True`) routes the document through `duplicate_document_indexing_task`, not the normal indexing task. That task had two gaps compared with the normal and update indexing paths:

1. It cleaned the old segments with `index_processor.clean(...)` but did not pass `delete_summaries=True`. Every index processor only deletes `DocumentSegmentSummary` rows and their summary vectors when that flag is set, so the old summaries were left behind as orphans (same flag that `delete_segment_from_index_task` already passes).
2. After re-indexing it never queued `generate_summary_index_task`, so no new summaries were produced. `document_indexing_task` and `document_indexing_update_task` both queue it once indexing completes.

##### Fix

In `api/tasks/duplicate_document_indexing_task.py`:

- Pass `delete_summaries=True` when cleaning the old segments, so summary records and summary vectors are removed together with the segment vectors.
- After a successful re-index, queue `generate_summary_index_task` using the same eligibility rules as the normal indexing task: high-quality dataset, summary index enabled, document `COMPLETED`, not QA form, and `need_summary is True`. Failures to queue are logged and do not fail the task. Nothing is queued when indexing fails or is paused.

##### How tested

- New SQLite-backed unit tests in `api/tests/unit_tests/tasks/test_duplicate_document_indexing_task_summaries.py` (same harness style as `test_document_indexing_update_task.py`):
  - old summaries are deleted: `clean` receives `delete_summaries=True` (failed before the fix with `KeyError: 'delete_summaries'`);
  - summary generation is queued after a completed duplicate re-index (failed before the fix: nothing was queued);
  - nothing is queued for economy datasets, disabled or missing summary settings, `need_summary=False`, QA documents, or failed indexing.
- `pytest api/tests/unit_tests/tasks api/tests/unit_tests/services/test_summary_index_service.py api/tests/unit_tests/services/knowledge` — 797 passed
- `ruff format --check`, `ruff check`, `lint-imports` (64 contracts kept), `dev/pyrefly-check-local api/tasks/duplicate_document_indexing_task.py` — clean
- Not run locally: `api/tests/test_containers_integration_tests/tasks/test_duplicate_document_indexing_task.py` (Docker/Testcontainers, CI-only). It asserts on `clean` call counts, which this change does not alter.

##### Notes for reviewers

- Scope is limited to the duplicate path from the issue. `need_summary` is not recomputed for the duplicate document; it keeps the value set when the document was first created, matching how the normal and update tasks decide eligibility.
- Pre-existing edge case, unchanged by this PR: if every old segment lacks `index_node_id`, `clean` is called with an empty list and falls back to dataset-wide deletion. With `delete_summaries=True` that fallback now also covers summaries, consistent with the existing vector behaviour.
- An earlier PR for this issue (#36964) was closed during the 2026-09-28 queue cleanup because of merge conflicts. This PR uses the processor's existing `delete_summaries` flag rather than a separate service call.

AI-assisted (Claude Code); reviewed and tested by the author

#### Explain it to Govu

1. Dify can write a short "summary" for every chunk of a document and store it for search.
2. When you upload the same file again, Dify takes a special "duplicate" path that rebuilds the chunks.
3. That path deleted the old chunks but forgot to delete their summaries, and it never asked for new summaries.
4. The fix tells the cleanup step to delete summaries too, and after rebuilding it queues summary generation with the same rules the normal upload uses.
5. New tests prove old summaries are removed and new ones are requested; they failed before and pass now.

---

## Appendix C — PR draft for #39629 (branch fix/39629-mcp-unsupported-param-type)

### PR draft — fix(api): fall back to string for unsupported MCP input schema types

> Local working note. Delete this file (drop the last commit on this branch) before opening the upstream PR.

#### Title

fix(api): fall back to string for unsupported MCP input schema types

#### Body

Fixes #39629

##### Root cause

`ToolTransformService.convert_mcp_schema_to_parameter` turns a remote MCP tool's `inputSchema` into Dify `ToolParameter`s. `resolve_property_type` returns whatever string the remote schema declares (only `integer`/`float` are remapped), and the value is then passed straight into `ToolParameter.ToolParameterType(param_type)`.

- A non-standard type such as `"text"`, `"String"` or `["bogus", "null"]` raises `ValueError: 'text' is not a valid ToolParameter.ToolParameterType`. Because the conversion runs whenever the provider's tools are loaded (`MCPToolProviderController.from_entity`, `ToolTransformService.mcp_tool_to_user_tool`), one bad property makes the whole MCP provider unusable (listing, credential update, invocation).
- Dify-internal parameter types such as `"file"`, `"secret-input"` or `"model-selector"` are accepted from the remote schema and change how Dify renders and handles the parameter, even though they are not JSON schema types.

##### Fix

After resolving and remapping the type, only accept the standard JSON schema types that MCP parameters support (`string`, `number`, `boolean`, `array`, `object`); anything else falls back to `string`. This follows the existing fallbacks in the same function (null-only types and over-deep unions already fall back to `string`).

##### How tested

- Added to `api/tests/unit_tests/services/tools/test_mcp_tools_transform.py`:
  - a parametrized test for `"text"`, `"String"`, `["bogus", "null"]`, `"file"`, `"secret-input"`, `"model-selector"` → `STRING` (all six failed before the fix: three with `ValueError`, three returning the internal type);
  - a test that `string`, `integer`, `number`, `boolean`, `array`, `object` keep their existing mapped types.
- `pytest api/tests/unit_tests/services/tools api/tests/unit_tests/core/tools api/tests/unit_tests/core/mcp` — 922 passed
- `ruff format --check`, `ruff check`, `dev/pyrefly-check-local api/services/tools/tools_transform_service.py` — clean
- Not run locally: `api/tests/test_containers_integration_tests/services/tools/test_mcp_tools_manage_service.py` (Docker/Testcontainers, CI-only); it does not use non-standard parameter types.

##### Notes for reviewers

- Behaviour change: an MCP server that declares a Dify-internal type such as `"file"` used to get a Dify file parameter; it now gets a string parameter. These are not valid JSON schema types, and the issue and the earlier PR both proposed excluding them, but please confirm no supported integration relies on it.
- An earlier PR for this issue (#38788, by the issue author) was closed by its author on 2026-09-18 without review. This PR takes the same whitelist approach on current `main`.

AI-assisted (Claude Code); reviewed and tested by the author

#### Explain it to Govu

1. Dify can connect to external "MCP" tool servers, which describe each tool input with a type such as "string" or "number".
2. If a server sent an unusual type like "text", Dify crashed while loading it, and the whole connected server became unusable.
3. Servers could also send Dify's own internal types (like "file"), which they should not control.
4. The fix accepts only the five standard types and treats anything else as plain text ("string"), so one odd field no longer breaks everything.
5. New tests show six bad types now become "string" and the normal types are unchanged; they failed before the fix.

---

## Appendix D — Full issue triage (same content as TRIAGE.md)

### langgenius/dify contribution triage — 2026-10-07

Base: upstream `main` @ `e7d9c889` (fork `rahulrao85/dify` was level with upstream).

#### Scope and method

- Scanned **all ~458 open issues** (every page of "recently updated"), plus every open `good first issue` (10) and every open `🐞 bug` (125). The brief asked for the 100 most recent; that pool produced **zero** eligible issues, so the scan was widened to the full backlog.
- Filters applied to every issue: real bug or small well-defined improvement in this repo; no linked or open PR (issue Development sidebar + `is:pr <N>` + keyword PR searches); no assignee; nobody claiming it; maintainer engagement or 👍; likely < ~200 changed lines. Model-runtime and tool bugs (dify-plugins / dify-official-plugins), and code that lives in the external `graphon` package, were excluded.
- Each candidate was checked against local `main` to confirm the buggy code still exists (file:line below).

##### Limits (read before relying on this)

- GitHub API access to upstream was not available in this session; everything came from public github.com pages. Those pages **do not render issue comments or reaction counts** for logged-out viewers. "Nobody claimed it" and 👍 counts therefore could not be fully confirmed; engagement was judged from labels, PR pages (which do render comments), `commenter:` searches and code TODOs.
- `review: low/medium/high/top` labels are **bot-applied** ("via ghfind author score"), not maintainer engagement.
- On **2026-09-28** maintainer crazywoola closed a large batch of conflicted PRs ("PR queue cleanup… reopen this PR or submit a new one"). Many remaining issues therefore have only a **closed, unmerged** PR. Strictly, that is a "linked PR"; this triage treats it as acceptable but flags it as `closed-PR`, because its author can reopen. Maintainers have stated a duplicate-PR rule: **a PR from the issue author ranks first, then the earliest PR**.

#### Ranked candidates

| # | Issue | Title | Area | Est. size | Why it is fixable | Risk | Status |
|---|---|---|---|---|---|---|---|
| 1 | #38476 | Trigger debug selectors raise `ValueError("…%s…", var)` | api — `core/trigger/debug/event_selectors.py:214,228,238`, `controllers/console/app/workflow.py:1823` | ~25 | Logger-style args passed to an exception, so `str(e)` is a tuple. f-strings fix it. | Low. Closed-PR #38478 (issue author, closed for conflicts). | **Fixed** → `fix/38476-trigger-debug-error-messages` |
| 2 | #36937 | Summary index not cleared when re-uploading an existing document | api — `tasks/duplicate_document_indexing_task.py:146` | ~200 incl. tests | Duplicate path omits `delete_summaries=True` and never queues summary generation (the normal and update tasks do). | Low–med (Celery task). Closed-PR #36964 (conflicts). | **Fixed** → `fix/36937-duplicate-reindex-summaries` |
| 3 | #39629 | MCP provider crashes on unsupported `inputSchema` type | api — `services/tools/tools_transform_service.py:466-511` | ~50 incl. tests | Raw schema type goes straight into `ToolParameterType(...)`, so `"text"` raises `ValueError`. Whitelist the JSON types, fall back to string. | Low. 2 reactions. Closed-PR #38788 (closed by its author). | **Fixed** → `fix/39629-mcp-unsupported-param-type` |
| 4 | #40961 | Switching the embedding model re-indexes with the old model | api — `services/knowledge/dataset_service.py:719-736` | ~90 | Celery tasks are dispatched after `flush()` but before the caller commits, so the worker reads the old model. Dispatch `after_commit` (precedent: `tasks/new_agent_beta_task.py:68`). | Med (dispatch timing, rollback). Maintainer triaged duplicates. Closed-PR #40965. | Next best backend |
| 5 | #41457 | Deleting a disabled multimodal segment orphans attachment rows | api — `services/knowledge/segments/application.py:815`, `tasks/delete_segment_from_index_task.py:41` | ~100 | Attachment cleanup is bundled into the index-cleanup task, which is skipped for disabled segments or documents. | Med. Maintainer accepted the bug (dedup comment). Closed-PR #41458 (issue author). | Candidate |
| 6 | #39560 | Token counting sends a whole document in one plugin request | api — `core/rag/embedding/token_counter.py:25` | ~80 | No batching (unlike `cached_embedding.py` `MAX_CHUNKS`), causing 413 errors and plugin-daemon OOM. Batch and concatenate. | Low–med. No maintainer engagement seen. Closed-PR #39571 (author). | Candidate |
| 7 | #39302 | Public HITL form endpoints accept console/backstage recipient tokens | api — `controllers/web/human_input_form.py:176` (maintainer TODO) | ~60 | The web surface never calls `is_recipient_type_allowed_for_surface`. | Med. Security-adjacent; must keep email-recipient tokens working. Closed-PR #39661. | Candidate (security: coordinate first) |
| 8 | #41096 | Change-email duplicate guard compares `Account.email` case-sensitively | api — `repositories/account/repository.py:336,380` | ~50 | Mixed-case legacy rows bypass the guard. | Med. `LOWER()` perf trade-off on an unauthenticated path. Closed-PR #41720. | Candidate |
| 9 | #40985 | "does not have provider_credential_schema" in knowledge pipeline | web — `model-selector/popup-item.tsx:88-104` | ~60 | ADD always opens the modal as `predefinedModel`, so customizable-only providers get a null schema. | Low–med. 6 reactions, the most of any candidate. Closed-PR #41086 (author). | Best frontend |
| 10 | #38539 | Agent-app prompt generator sends `agent-chat` as `model_config.mode` | web — `config/automatic/get-automatic-res.tsx:96` | ~40 | Fallback model takes the app mode instead of the LLM mode; backend returns 400. | Low. Closed-PR #38566. | Frontend |
| 11 | #36219 | File upload count limit bypassed by paste/drop | web — `base/file-uploader/hooks.ts:311` | ~80 | Only the picker checks `number_limits`; paste and drop call `handleLocalFileUpload` directly. | Low. Closed-PR #36373. | Frontend |
| 12 | #40041 | Valid plugin output variables marked invalid after refresh | web — `prompt-editor/.../workflow-variable-block/component.tsx:94` | ~45 | Each block's command handler returns `true`, which stops propagation, so only the first block updates. | Low. Closed-PRs #40067, #42958 (both by their authors). | Frontend |
| 13 | #40765 | Dify Agent appends events after a terminal transition | dify-agent — `storage/redis_run_store.py:201` | ~150 | `append_event` has no status check, unlike atomic `finalize_run`. | Med (concurrency). Maintainer triaged. Closed-PR #41084. | Outside api/web |
| 14 | #41921 | Four wrong Italian Knowledge UI strings | web i18n — `i18n/locales/it-IT/dataset.json` | 4 | Translation fixes. | Low but low value. Closed-PR #41923. | Trivial |
| 15 | #39476 | Relyt / AnalyticDB malformed metadata-filter SQL | api providers/vdb | ~10 | `'{key!r}'` double-quotes keys; `"1=1"+"AND"` lacks a space. | Low. **Assigned to the reporter**, so it fails the no-assignee rule. | Near-miss |
| 16 | #39520 | API-based extension requestor ignores `SSRF_PROXY_ALL_URL` | api — `core/extension/api_based_extension_requestor.py:30` | ~30 | Bypasses the shared SSRF proxy client. | Low. No engagement. Closed-PR #39521. | Near-miss |

#### Rejected (grouped by one-word reason)

**has-PR** (open fix PR exists): #43358, #43600, #43596, #43594, #43530, #43516, #43479, #43444, #43482, #43475, #43453, #43449, #43459, #43473, #43471, #43469, #43465, #43455, #43451, #43447, #43445, #43442, #43435, #43397, #43369, #43360, #43359, #43356, #43351, #43350, #43349, #43345, #43339, #43335, #43333, #43331, #43312, #43324, #43302, #43303, #43301, #43300, #43299, #43296, #43277, #43275, #43265, #43251, #43247, #43244, #43242, #43240, #43237, #43186, #43134, #43105, #43086, #43084, #43062, #43046, #43000, #42996, #42994, #42987, #42981, #42948, #42928, #42921, #42905, #42897, #42889, #42875, #42868, #42831, #42807, #42798, #42739, #42722, #42641, #42639, #42637, #42547, #42451, #42446, #42415, #42414, #42387, #42386, #42384, #42380, #42358, #42355, #42353, #42350, #42348, #42341, #42332, #42326, #42313, #42277, #42272, #42237, #42234, #42218, #42207, #42194, #42167, #42142, #42135, #42114, #42103, #42087, #42038, #42006, #41907, #41865, #41860, #41854, #41822, #41809, #41781, #41727, #41712, #41703, #41688, #41675, #41671, #41649, #41626, #41597, #41565, #41556, #41545, #41542, #41488, #41482, #41479, #41476, #41460, #41434, #41376, #41348, #41315, #41236, #41143, #41071, #41059, #40976, #40920, #40907, #40838, #40779, #40729, #40698, #40680, #40635, #40612, #40595, #40448, #40445, #40425, #40423, #40415, #40126, #40097, #40028, #40022, #40003, #39988, #39966, #39961, #39954, #39893, #39892, #39891, #39889, #39851, #39812, #39773, #39733, #39727, #39602, #39518, #39516, #39514, #39460, #39420, #39340, #39327, #39301, #39230, #39177, #39169, #39031, #38998, #38980, #38963, #38895, #38867, #38862, #38633, #38587, #38555, #38537, #38532, #38527, #38522, #38518, #38457, #38413, #38411, #38408, #38403, #38360, #38246, #37824, #37000, #36990, #36230, #34141

**assigned**: #33092, #40372, #36544, #35557, #29314, #28015, #24645, #39993, #31096, #35872, #42285, #41034, #32174, #32679, #38604, #38855, #38524, #38564, #38610, #38611, #40791, #41092, #41364, #41409, #41418, #41461, #41758, #41782, #42226, #42287, #42871, #40671, #39476

**feature**: #43603, #43289, #43113, #43108, #43071, #42650, #42638, #42603, #42522, #42510, #42496, #42450, #42448, #42404, #42352, #42346, #42309, #42265, #42216, #42200, #42104, #42033, #41997, #41996, #41995, #41864, #41849, #41818, #41723, #41536, #41468, #41378, #41377, #41375, #41269, #41139, #41125, #41112, #41048, #40690, #40672, #40575, #40481, #39991, #39955, #39501, #38805, #38665, #38659, #38515, #38508, #38497, #38213, #38212, #38168, #38015, #37842, #37789, #37507, #37259, #37186, #36745, #36395, #36141, #35837, #35653, #26643, #42918

**proposal**: #42092, #42075, #41020, #37572

**refactor** (incl. epics, chores, CI, tooling): #43035, #43341, #42945, #42944, #42940, #42886, #42851, #42477, #42437, #42147, #41710, #41560, #41093, #40450, #40123, #40117, #40012, #39931, #39782, #39546, #38609, #38466, #38351, #38346, #38064, #37827, #36710, #36288, #34240, #34212, #32454, #30269, #24138, #23580

**support** (deployment, environment, Cloud or questions): #43330, #43319, #42754, #42300, #42155, #42154, #42153, #41909, #41895, #41779, #40773, #40601, #40401, #40394, #40036, #39161, #38957, #38492, #38440, #38312

**plugin** (wrong repo, or external graphon/MCP): #18752, #41456, #39431, #37374, #37034, #41851, #39977, #40865

**fixed** (already resolved on main): #42934, #42284, #42230, #40733, #40457, #39914, #39434, #39022, #39011, #38795, #38432, #38409, #38406, #38404, #38353, #38327

**unclear** (vague, no repro or root cause): #42607, #42539, #42292, #41362, #41350, #41214, #40761, #40720, #40603, #40479, #40001, #39944, #39686, #39645, #39222, #38956, #38912, #38852, #38824, #38595, #37739, #37588

**large**: #41451, #41316, #40874, #39685, #39456, #39151, #42268, #38402

**deferred**: #42535, #42203, #41405

**obsolete**: #42213, #41426, #39928, #39522

**by-design**: #42174 (`web/app/components/main-nav/routes.ts:138` deliberately excludes document-create routes; asserted by `main-nav/__tests__/layout.spec.tsx`)

**no-engagement**: #39520
