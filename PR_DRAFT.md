# PR draft — fix(api): fall back to string for unsupported MCP input schema types

> Local working note. Delete this file (drop the last commit on this branch) before opening the upstream PR.

## Title

fix(api): fall back to string for unsupported MCP input schema types

## Body

Fixes #39629

### Root cause

`ToolTransformService.convert_mcp_schema_to_parameter` turns a remote MCP tool's `inputSchema` into Dify `ToolParameter`s. `resolve_property_type` returns whatever string the remote schema declares (only `integer`/`float` are remapped), and the value is then passed straight into `ToolParameter.ToolParameterType(param_type)`.

- A non-standard type such as `"text"`, `"String"` or `["bogus", "null"]` raises `ValueError: 'text' is not a valid ToolParameter.ToolParameterType`. Because the conversion runs whenever the provider's tools are loaded (`MCPToolProviderController.from_entity`, `ToolTransformService.mcp_tool_to_user_tool`), one bad property makes the whole MCP provider unusable (listing, credential update, invocation).
- Dify-internal parameter types such as `"file"`, `"secret-input"` or `"model-selector"` are accepted from the remote schema and change how Dify renders and handles the parameter, even though they are not JSON schema types.

### Fix

After resolving and remapping the type, only accept the standard JSON schema types that MCP parameters support (`string`, `number`, `boolean`, `array`, `object`); anything else falls back to `string`. This follows the existing fallbacks in the same function (null-only types and over-deep unions already fall back to `string`).

### How tested

- Added to `api/tests/unit_tests/services/tools/test_mcp_tools_transform.py`:
  - a parametrized test for `"text"`, `"String"`, `["bogus", "null"]`, `"file"`, `"secret-input"`, `"model-selector"` → `STRING` (all six failed before the fix: three with `ValueError`, three returning the internal type);
  - a test that `string`, `integer`, `number`, `boolean`, `array`, `object` keep their existing mapped types.
- `pytest api/tests/unit_tests/services/tools api/tests/unit_tests/core/tools api/tests/unit_tests/core/mcp` — 922 passed
- `ruff format --check`, `ruff check`, `dev/pyrefly-check-local api/services/tools/tools_transform_service.py` — clean
- Not run locally: `api/tests/test_containers_integration_tests/services/tools/test_mcp_tools_manage_service.py` (Docker/Testcontainers, CI-only); it does not use non-standard parameter types.

### Notes for reviewers

- Behaviour change: an MCP server that declares a Dify-internal type such as `"file"` used to get a Dify file parameter; it now gets a string parameter. These are not valid JSON schema types, and the issue and the earlier PR both proposed excluding them, but please confirm no supported integration relies on it.
- An earlier PR for this issue (#38788, by the issue author) was closed by its author on 2026-09-18 without review. This PR takes the same whitelist approach on current `main`.

AI-assisted (Claude Code); reviewed and tested by the author

## Explain it to Govu

1. Dify can connect to external "MCP" tool servers, which describe each tool input with a type such as "string" or "number".
2. If a server sent an unusual type like "text", Dify crashed while loading it, and the whole connected server became unusable.
3. Servers could also send Dify's own internal types (like "file"), which they should not control.
4. The fix accepts only the five standard types and treats anything else as plain text ("string"), so one odd field no longer breaks everything.
5. New tests show six bad types now become "string" and the normal types are unchanged; they failed before the fix.
