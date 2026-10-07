# langgenius/dify contribution triage — 2026-10-07

Base: upstream `main` @ `e7d9c889` (fork `rahulrao85/dify` was level with upstream).

## Scope and method

- Scanned **all ~458 open issues** (every page of "recently updated"), plus every open `good first issue` (10) and every open `🐞 bug` (125). The brief asked for the 100 most recent; that pool produced **zero** eligible issues, so the scan was widened to the full backlog.
- Filters applied to every issue: real bug or small well-defined improvement in this repo; no linked or open PR (issue Development sidebar + `is:pr <N>` + keyword PR searches); no assignee; nobody claiming it; maintainer engagement or 👍; likely < ~200 changed lines. Model-runtime and tool bugs (dify-plugins / dify-official-plugins), and code that lives in the external `graphon` package, were excluded.
- Each candidate was checked against local `main` to confirm the buggy code still exists (file:line below).

### Limits (read before relying on this)

- GitHub API access to upstream was not available in this session; everything came from public github.com pages. Those pages **do not render issue comments or reaction counts** for logged-out viewers. "Nobody claimed it" and 👍 counts therefore could not be fully confirmed; engagement was judged from labels, PR pages (which do render comments), `commenter:` searches and code TODOs.
- `review: low/medium/high/top` labels are **bot-applied** ("via ghfind author score"), not maintainer engagement.
- On **2026-09-28** maintainer crazywoola closed a large batch of conflicted PRs ("PR queue cleanup… reopen this PR or submit a new one"). Many remaining issues therefore have only a **closed, unmerged** PR. Strictly, that is a "linked PR"; this triage treats it as acceptable but flags it as `closed-PR`, because its author can reopen. Maintainers have stated a duplicate-PR rule: **a PR from the issue author ranks first, then the earliest PR**.

## Ranked candidates

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

## Rejected (grouped by one-word reason)

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
