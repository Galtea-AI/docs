---
name: fix-docs
description: Audit and fix documentation - prose pages, code snippets, or both - against the actual codebase implementation
argument-hint: [focus-area]
model: sonnet
---

_Classify every discrepancy using code evidence. Never guess Category A/B/C: if the source of truth is unclear, flag it as a question for the user rather than fixing the wrong layer._

# Documentation Audit & Fix

Audit Galtea documentation against the actual implementation and fix any issues found.

## 1. Determine Scope

If `$ARGUMENTS` provides a focus area, use it as the starting scope. Otherwise, ask the user using `AskUserQuestion`:

> "What kind of documentation audit do you want to run?"

Options:
1. **Prose documentation** - Audit MDX pages (parameters, descriptions, links, navigation) against the codebase.
2. **Code snippets** - Audit and fix runnable code examples under `docs/code/` against the current SDK/API.
3. **Both** - Full audit of prose pages and code snippets together.
4. **Recent changes only** - Audit only docs affected by recent code changes (last 10 commits).

Store the choice as `AUDIT_MODE`.

Then ask using `AskUserQuestion`:

> "Which area should I focus on?"

Options:
1. **Everything** - Full audit across all documentation.
2. **SDK API reference** - `docs/sdk/api/` against `sdk/galtea/`.
3. **Concepts & tutorials** - `docs/concepts/` and `docs/sdk/tutorials/` against implementation.
4. **Specific topic** - The user will specify (e.g., "evaluations", "metrics", "traces").

Store the choice as `FOCUS_AREA`.

## 2. Read Context Files

Read these files for context on the documentation system:
- `docs/CLAUDE.md` - Code embed system, page structure, MDX conventions
- `docs/component_reference.md` - Component templates and formatting patterns
- `docs/docs.json` - Navigation structure and all registered pages

If code snippets are in scope, also read:
- `docs/CODE_SNIPPETS.md` - Embed placeholder format, section markers, validation, file naming
- `sdk/CLAUDE.md` - SDK development guidelines, resource patterns, testing

## 3. Read Documentation and Source Code

Read both sides before making any judgment:

1. **Read the documentation pages** in scope. For each page, note what it claims: method names, parameters, types, defaults, behavior descriptions, code examples.
2. **Read the corresponding source code.** The implementation is always the source of truth:
   - SDK: `sdk/galtea/` - method signatures, parameter names and types, docstrings
   - API: `api/src/` - route definitions, request/response schemas, Prisma models
   - Dashboard: `dashboard/src/` - UI components, forms, feature availability
   - Evaluator: `evaluator/` - metric definitions, evaluation logic
   - Other services as relevant to the documentation scope

If code snippets are in scope, also read:
- `sdk/galtea/__init__.py` - all publicly exported classes, enums, functions
- The relevant service files under `sdk/galtea/application/services/`
- The relevant domain model files under `sdk/galtea/domain/models/`
- For tracing/agent snippets: `sdk/galtea/utils/tracing.py`, `sdk/galtea/utils/agent.py`, `sdk/galtea/utils/custom_score_metric.py`

## 4. Cross-Reference and Identify Issues

### 4a. Prose Documentation Checks (when AUDIT_MODE includes prose)

For each documentation page in scope, check:

**Parameters and Signatures:**
- Parameter names match between docs and SDK source
- Types are correct (string vs enum, optional vs required)
- Default values are accurate
- New parameters exist in code but are missing from docs
- Removed parameters are still documented

**Code Embeds:**
- For each `{/* @embed path="..." section="..." */}`:
  - The Python file exists under `docs/code/`
  - The section between `# @start` / `# @end` markers exists
  - The code uses current SDK method names and parameters

**Internal Links:**
- All `[text](/path)` links resolve to existing MDX files
- No dead links to renamed or moved pages
- Links in `docs.json` navigation point to existing files

**Navigation:**
- Every MDX page is registered in `docs.json` (no orphaned pages)
- Every entry in `docs.json` points to an existing page (no dead entries)

**Prose Accuracy:**
- Behavioral descriptions match actual implementation
- Enum values and options are complete and current
- Workflow descriptions reflect current UX flow

**Formatting and Consistency:**
- Frontmatter has required fields (`title`, `description`)
- MDX components are used correctly (`<ResponseField>`, `<Note>`, etc.)
- No inline Python code blocks in MDX files (must use embed system)
- No `---` horizontal rules inside page content (only allowed in frontmatter)
- No triple blank lines (`\n\n\n`): use single blank lines between sections
- Related section heading must be `## Related` (not `## Related Topics`, `## Related Concepts`, `## Related Metrics`, or `## See Also`)

**Terminology Standards:**
- Dataset types: `Accuracy` (not "Quality"), `Security & Safety` (not "Red Teaming"), `Behavior` (not "Scenarios")
- Brand: `Galtea` (always capitalized, never lowercase "galtea" in prose)
- Conversation Simulator: use "simulated user" (not "synthetic user" or "Synthetic User")
- Metric categories in intro sentences: `[non-deterministic Metric](/concepts/metric)` (singular), `[Deterministic Metric](/concepts/metric)` (singular), `[Security & Safety Metric](/concepts/metric)` (singular)
- `product_description` parameter: link to `[Product](/concepts/product)`, not to the old create-product-description tutorial

**Canonical Concept Page Structure:**
All concept pages (under `docs/concepts/`) must follow this section order:
1. `## What is [X]?`: intro paragraph
2. Domain-specific sections (use cases, how it works, creating, etc.)
3. `## SDK Integration`: card links to SDK service/tutorial (omit if dashboard-only)
4. `## [X] Properties`: `<ResponseField>` blocks
5. `## Related`: `<CardGroup>` with cards (always last section)

**Canonical Metric Page Structure:**
All individual metric pages (under `docs/concepts/metric/`) must follow:
1. Intro paragraph: what it is + category link (`[non-deterministic Metric](/concepts/metric)`)
2. `## Evaluation Parameters`: bullet list of required parameters
3. `## How Is It Calculated?`: calculation steps + scoring
4. Optional: `## Interpretation of Scores` (only for continuous-score deterministic metrics)
5. `## Suggested Test Case Types`: when to use this metric
6. No `## Related` section on individual metric pages (redundant with sidebar)

**Concept Overview Pages Should Not Contain SDK Code:**
Concept overview pages explain *what* something is. SDK code (decorators, method calls, code examples) belongs in tutorials or SDK API reference pages. Concept pages should link to tutorials via `## SDK Integration` cards instead.

**Tutorial Grouping (Guides tab):**
- **Core Workflows**: Writing Specs → Evaluations from Specs → Simulating Conversations → Create a Custom Dataset → Run Dataset-Based Evaluations → Direct Inferences from Platform
- **Production & Monitoring**: Monitor Production Responses → Evaluating Conversations
- **Advanced**: Judge Prompts → Custom Metrics → Tracing → Agentic Evaluation → Human Evaluation
- Manual/advanced tutorials should have a `<Note>` at the top pointing to the spec-driven workflow as the recommended alternative

**Video Placement:**
Videos must be placed consistently based on their type:
- **Overview/demo videos**: right after the intro paragraph(s) of "What is [X]?", before the first domain section (e.g., `trace.mdx`, `ai-generation.mdx`, `data-augmentation.mdx`)
- **Contextual workflow videos**: inside the relevant creation/setup section they demonstrate (e.g., endpoint connection creation video inside "Creating an Endpoint Connection", dataset generation video inside "Dataset Origin" Tab)
- **Tutorial videos**: right after the intro paragraph or Tip, before the step-by-step content
- Video placeholders for missing videos use `{/* <!-- VIDEO PLACEHOLDER: description ... --> */}` comment wrapping
- Track all pending and existing videos in `docs/VIDEO_PLACEHOLDERS.md`

**Long Concept Pages Should Be Split:**
If a concept page exceeds ~200 lines due to dense reference material (e.g., configuration syntax, parameter tables), split the reference into a sub-page. Examples:
- `metric.mdx` → `evaluation-types.mdx` + `evaluation-parameters.mdx` + `ai-generation.mdx`
- `endpoint-connection.mdx` → `endpoint-connection-configuration.mdx` (templates, mapping, retry)

### 4b. Code Snippet Checks (when AUDIT_MODE includes code snippets)

For each code snippet file in scope, check:

**SDK Method Signatures:**
- Parameter names match the current SDK service methods exactly
- Parameter types are correct (e.g., `str` vs `Union[str, DatasetType]`)
- Removed parameters are no longer used
- Return types and accessed fields are correct
- Deprecated methods are not used when a replacement exists

**Import Statements:**
- All imports resolve to actual exports from `galtea` (check against `__init__.py`)
- No missing or unused imports

**Enum and Constant Values:**
- `DatasetType`: `"ACCURACY"`, `"SECURITY"`, `"BEHAVIOR"` (or legacy: `"QUALITY"`, `"RED_TEAMING"`, `"SCENARIOS"`)
- `TraceType`: `SPAN`, `GENERATION`, `EVENT`, `AGENT`, `TOOL`, `CHAIN`, `RETRIEVER`, `EVALUATOR`, `EMBEDDING`, `GUARDRAIL`
- `EvaluationStatus`: `PENDING`, `PENDING_HUMAN`, `SUCCESS`, `FAILED`, `SKIPPED`, `CANCELLED`
- `SpecificationType`: `CAPABILITY`, `INABILITY`, `POLICY`
- Metric `source`: `"self_hosted"`, `"partial_prompt"`, `"full_prompt"`, `"human_evaluation"`

**MetricInput Format:**
The evaluations.create `metrics` parameter accepts:
- `str` - metric name (legacy)
- `CustomScoreEvaluationMetric` - self-hosted metric instance (legacy)
- `dict` (`MetricInput`) - preferred format: `{"name": "..."}`, `{"id": "..."}`, `{"name": "...", "score": 0.85}`, `{"score": MyCustomMetric()}`

**Agent Function Signatures:**
```python
def my_agent(user_message: str) -> str: ...           # Signature 1
def my_agent(messages: list[dict]) -> str: ...         # Signature 2
def my_agent(input_data: AgentInput) -> AgentResponse: ...  # Signature 3
```

## 5. Diagnose Root Cause of Each Issue

**Not every failure is a stale doc or snippet.** Before fixing anything, classify the root cause:

### Category A: Stale Documentation/Snippet (most common)
The docs or snippet are wrong - outdated method name, wrong parameter, removed field, etc. The SDK and API are correct.
**Action:** Fix the docs/snippet to match the current SDK.

### Category B: SDK Bug
The docs/snippet are correct per intended behavior, but the SDK has a bug.
**Signals:** Snippet matches SDK signature but execution fails; SDK silently ignores a parameter; SDK model missing a field the API returns.
**Action:** Fix the SDK source, run `cd sdk && make test && make lint-fix && make format`, update snippet if needed.

### Category C: API Bug
The SDK correctly sends the request, but the API returns an error or unexpected response.
**Signals:** SDK method sends the right request but gets an error status; API validation rejects valid input.
**Action:** Fix the API source, run `cd api && npm run tests && npm run lint -- --max-warnings 0`, update SDK/snippet if needed.

### Decision Flowchart
```
Issue identified
  |
  +- Does the doc/snippet use wrong method/param names? --> Category A (fix docs)
  |
  +- Snippet matches SDK signatures, but SDK raises error?
  |    -> Read SDK source: is the SDK handling it wrong? --> Category B (fix SDK)
  |
  +- SDK sends correct request, API returns error?
  |    -> Read API route/service: is the API wrong? --> Category C (fix API)
  |
  -> Unclear? --> Flag as question for user. Do NOT guess.
```

## 6. Fix Issues

### Evidence-Based Only
- Link every change to a specific source of evidence in the code.
- If you cannot find clear evidence for a discrepancy, do NOT make the change. Note it in the report as a question.

### Prose Documentation Fixes
- Follow existing Mintlify documentation style: tone, structure, formatting.
- When updating code embeds, edit the Python file in `docs/code/python/`, NOT the MDX.
- When fixing parameters, update both the `<ResponseField>` blocks and the code embeds.
- Only fix what is actually wrong. Do not rewrite correct content.

### Code Snippet Fixes
Preserve the strict code file structure:
1. Docstring (optional)
2. Imports from `galtea`
3. Run identifier: `run_identifier = datetime.now().strftime("%Y%m%d%H%M%S")`
4. SDK client init: `galtea = Galtea(api_key="YOUR_API_KEY")`
5. Setup code (outside sections)
6. Demonstrative sections (`# @start section_name` / `# @end section_name`)
7. Validation/assertions between sections
8. Cleanup at end

**Section Marker Rules:**
- Names: single word, descriptive `snake_case`
- Markers are stripped from embedded output
- Sections cannot overlap

**Placeholder Conventions:**
- API key: `"YOUR_API_KEY"` -> `GALTEA_API_KEY`
- Product ID: `"YOUR_PRODUCT_ID"` -> `GALTEA_PRODUCT_ID`
- Test ID: `"YOUR_TEST_ID"` or `"YOUR_QUALITY_TEST_ID"` -> `GALTEA_QUALITY_TEST_ID`
- Test Case ID: `"YOUR_TEST_CASE_ID"` -> `GALTEA_TEST_CASE_ID`
- Session ID: `"YOUR_SESSION_ID"` -> `GALTEA_SESSION_ID`

**File Naming Conventions:**
- SDK API reference: `sdk_api_<service>_<method>.py`
- SDK tutorials: `sdk_tutorials_<topic>.py`
- Concepts: `concepts_<topic>.py`
- Integrations: `sdk_integrations_<platform>.py`

**Python Compatibility:** Target >=3.9. Prefer `Optional[T]` in library code; `T | None` is acceptable in illustrative snippets.

## 7. Verify Fixes

### Prose Verification
1. Confirm modified MDX files have valid frontmatter (`title`, `description`)
2. Verify `@embed` references point to valid file/section combinations
3. Check internal links resolve to existing pages

### Code Snippet Verification
1. Syntax check:
   ```bash
   python -c "import ast; ast.parse(open('docs/code/python/FILENAME.py').read())"
   ```
2. Run validation:
   ```bash
   cd docs && python scripts/validate_snippets.py -f FILENAME.py
   ```
3. Embed integrity:
   ```bash
   cd docs && python scripts/run.py --embed-only
   ```

### Full Docs Validation
```bash
cd docs && python scripts/run.py
```

## 8. Final Review with Git

Before finishing, check that recent codebase changes are reflected:

```bash
git log --oneline --since="2 weeks ago" -- sdk/ api/ dashboard/ evaluator/
```

If any recent commits affect documentation in your audit scope, verify and fix them.

## 9. Report

After completing the audit, report findings in this format:

```
## Documentation Audit Report

### Scope
<what was audited: prose/snippets/both, focus area, and why>

### Summary
- **Pages audited:** N
- **Code files audited:** N
- **Snippet fixes (Category A):** N
- **SDK bug fixes (Category B):** N
- **API bug fixes (Category C):** N
- **Questions for user:** N (if any)

### Changes Made

#### [file path] - Short description
- **What was wrong:** Parameter `X` was renamed to `Y` in SDK
- **Evidence:** `sdk/galtea/application/services/evaluation_service.py:42`
- **Fix applied:** Updated parameter name / ResponseField / code snippet section
- **Related:** Also updated embed in `docs/code/python/file.py`

### MDX Updates (if any)
- [mdx file] - Updated `@embed` section reference from `old_name` to `new_name`

### Questions (if any)
Items where evidence was unclear and user input is needed.

### No Issues Found (if applicable)
Documentation is up to date for the checked scope.
```

## Common Issues Checklist

### Category A - Stale Docs/Snippets
- [ ] Method renamed or moved
- [ ] Parameter renamed/added/removed
- [ ] Return type changed (new/removed fields)
- [ ] Enum value changed or added
- [ ] Import path changed
- [ ] Deprecated method still documented as primary
- [ ] Section markers out of sync with MDX `@embed` references
- [ ] Dead internal links
- [ ] Orphaned or missing navigation entries

### Category B - SDK Bugs
- [ ] SDK method accepts a parameter but silently ignores it
- [ ] SDK model missing a field the API returns
- [ ] SDK raises unhandled exception for valid input
- [ ] SDK serialization breaks for certain types/values

### Category C - API Bugs
- [ ] API route doesn't extract a parameter despite schema support
- [ ] API returns wrong status code for valid request
- [ ] API response body missing a field defined in Prisma schema
- [ ] API validation rejects valid input

## Key File Locations

| What | Where |
|------|-------|
| SDK API docs | `docs/sdk/api/` |
| Concept docs | `docs/concepts/` |
| Tutorials | `docs/sdk/tutorials/` |
| Code snippet files | `docs/code/python/*.py` |
| Bash snippet files | `docs/code/bash/*.sh` |
| Reusable snippets | `docs/snippets/` |
| Navigation config | `docs/docs.json` |
| Embed build script | `docs/scripts/embed_snippets.py` |
| Validation script | `docs/scripts/validate_snippets.py` |
| Quickstart | `docs/quickstart.mdx` |
| SDK source (truth) | `sdk/galtea/` |
| SDK services | `sdk/galtea/application/services/` |
| SDK models | `sdk/galtea/domain/models/` |
| SDK utilities | `sdk/galtea/utils/` |
| SDK exports | `sdk/galtea/__init__.py` |
| API routes | `api/src/infrastructure/in/routes/` |
| API services | `api/src/application/services/` |
| Prisma schema | `api/prisma/schema.prisma` |
| Dashboard source | `dashboard/src/` |
| Evaluator metrics | `evaluator/` |
| Doc conventions | `docs/CLAUDE.md`, `docs/component_reference.md` |
| SDK tests | `sdk/tests/` |
| API tests | `api/tests/` |
