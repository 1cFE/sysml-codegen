# Design: Snapshot Portability and Shape Gates

**Status:** Draft

**Owner:** Reid W

**Created:** 2026-07-18 20:21 PDT

**Revised:** 2026-07-18 20:46 PDT

**Branch:** `constraint-exec-epic`

**Commit:** `512786c`
**Epic:** CONSTRAINT-WAVE-REMEDIATION — Item 4 (R-6, R-11)

---

## Overview

Make excluded source locations one portable projection across live lowering, snapshot capture, and
snapshot replay, while leaving every constraint-ID input unchanged. At load, add one narrow,
path-aware shape gate for the JSON root and the three v3 constraint sections before their existing
typed reconstructors run; legacy extraction sections keep their current compatibility behavior.

## Related Artifacts

- Revised draft contract: [spec.md](spec.md)
- Historical review: [spec-review.md](spec-review.md)
- Design review being resolved: [design-review.md](design-review.md)
- Epic Item 4: [../../backlog/epic_constraint_pr_wave_remediation.md](../../backlog/epic_constraint_pr_wave_remediation.md)
- Primary R-6/R-11 review: [../../research/20260718-192048_constraint-exec-pr-wave-code-review.md](../../research/20260718-192048_constraint-exec-pr-wave-code-review.md)
- Snapshot v3: [spec](../../completed/20260713_snapshot-v3/spec.md),
  [design](../../completed/20260713_snapshot-v3/design.md), and
  [audit](../../completed/20260713_snapshot-v3/audit.md)
- GAP-CLOSE location work: [spec](../gap-lowering-integrity/spec.md),
  [design](../gap-lowering-integrity/design.md), and
  [evidence](../gap-lowering-integrity/evidence.md)
- Snapshot contract: [27-snapshot-generation.md](../../../docs/architecture/reference/27-snapshot-generation.md)

## Research Findings

- The portable grammar and its explicit route split already exist. Live mapping proves lexical
  containment against ordered model roots; replay validates the stored
  `root-<slot>/<percent-encoded-relative-path>` grammar
  (`src/sysml_codegen/analysis/source_referent.py:14-80`). No new path codec is needed.
- The shared profile selector already returns the exact ordered set routed to excluded records
  (`src/sysml_codegen/analysis/constraint_lowering.py:511-526`). Snapshot capture consumes that
  selector but currently filters out named usages before copying the canonical file referent
  (`src/sysml_codegen/snapshot/serializer.py:139-160`).
- Lowering canonicalizes only anonymous locations. Named warning rendering and the initial
  exclusion payload use the raw profile location (`src/sysml_codegen/analysis/constraint_lowering.py:489-508,
  529-570, 895-930`). Named ID minting uses only usage QN, owner kind, and source form; its tuple
  contains no location (`constraint_lowering.py:925-930`). Eligible IDs are minted on the separate
  admitted branch (`constraint_lowering.py:952-1056`).
- Snapshot v3 checks section presence, facts version tags, and the mode enum, then immediately calls
  the companion facts parser and occurrence reconstructor (`src/sysml_codegen/snapshot/loader.py:154-220`).
  It does not validate nested containers or keys. The occurrence reconstructor directly indexes
  `part_def_qn`, `steps`, and step fields (`src/sysml_codegen/analysis/part_instance_index.py:425-447`).
- The companion facts and ExpressionIR codecs are strict reconstructors, not boundary validators:
  they directly index required fields and intentionally ignore extra keys
  (`../agentic-mbse/src/agentic_mbse/sysml/constraint_facts.py:205-340`;
  `../agentic-mbse/src/agentic_mbse/sysml/expression_ir.py:190-283`). Their errors therefore need
  path-aware pre-validation and domain-error normalization in this repository.
- The loader also performs a recursive version-token scan across every mapping and list below
  `constraint_facts`, including values under unknown keys (`src/sysml_codegen/snapshot/loader.py:178-189,
  251-269`). Structural extra keys are ignored by typed reconstruction, but an extra payload that
  declares a foreign `expression-ir/*` version is rejected today. Both behaviors are compatibility
  requirements for this correction.
- Legacy loader behavior is intentionally mixed. Missing `compilation_results` warns and degrades
  (`src/sysml_codegen/snapshot/loader.py:272-288`), while many old fields retain `.get(...)`
  defaults (`loader.py:393-626`). R-11 does not authorize changing those contracts.
- Existing v3 tests cover missing top-level sections and version/mode corruption, but not nested
  shape policy (`tests/unit/test_snapshot_v3_gate.py:164-200`). The current location parity test
  explicitly pins named snapshot locations as raw, which is the R-6 RED anchor
  (`tests/conformance/test_constraint_snapshot_identity.py:188-200`).
- A selector-backed inventory of all committed v3 snapshots confirms the reviewed fixture scope.
  `catf_mfe_model` has named, located exclusions at usage indices 0 through 64;
  `constraint_non_numerical` has one at index 0. No other committed snapshot has an affected usage.
  Both capture entries use the fixture directory as ordered root slot 0
  (`scripts/capture_extraction_snapshots.py:51-120,229-237`).
- Both affected snapshots currently round-trip byte-exact through
  `snapshot_to_json(json.loads(original_text))`, with no trailing newline. That makes a guarded
  parse/change/render candidate formatting-preserving; the transaction still rechecks this premise
  before any write and aborts if it changes.

## Core Concept

This correction is two boundary projections, not a schema redesign. For locations, the shared
excluded-usage selector remains authoritative. During one lowering run, a lazy, index-keyed
boundary maps or validates each excluded location at most once and returns an immutable canonical
referent/rendered-location pair. Warning rendering, exclusion construction, and anonymous minting
consume that result; none receives a raw location or route and none reinterprets it. The warning
pre-pass requests results only for `NON_NUMERICAL` usages, so a later BLOCK still halts before its
own location is projected. Capture performs its separate one-time projection onto a copied facts
aggregate. Named minting continues to read its old location-free tuple, while anonymous minting
continues to read canonical file/line/column. For loading, a small JSON-shape boundary validates
only the root and three v3 sections with JSON Pointer paths. The existing recursive foreign-version
scan remains intact across known and unknown keys before kind-directed shape validation. Typed
reconstructors remain authoritative for object creation; their residual failures become
`SnapshotFormatError` at their section boundary. The rest of the loader is untouched.

The key insight is placement and ownership. Route interpretation happens once at the lowering
boundary, then downstream code sees canonical data only. Canonicalization does not move into ID
minting or a global facts rewrite. Shape validation belongs immediately before the two strict
reconstructors, while the existing recursive version sentinel remains the forward-version guard.

## Key Bets

- **B1.** Exclusion status is deterministic from the serialized v1 facts and pinned executable
  profile, so live lowering and capture select the same usage indices. *If false → capture could
  canonicalize a different set than live lowering, and replay bytes would diverge.*
- **B2.** Every affected named exclusion with a present location maps beneath the ordered model
  roots supplied to capture/live generation. The current 66-record corpus inventory does.
  *If false → the correction fails loud for a formerly leaking record, and the fixture cannot be
  updated without resolving its root configuration.*
- **B3.** A pre-validator matching the current companion codec's accessed fields can reject
  structural corruption without redefining semantic profile rules. *If false → the gate would
  either accept a raw-exception path or become a second executable-profile/schema authority.*
- **B4.** The same temporary SysML model can yield one named non-numerical exclusion, one anonymous
  non-numerical exclusion, and one admitted named control on supported SysIDE builds. *If false →
  the mandatory licensed relocation harness cannot prove all route/byte controls in one run and
  must fail as a model-shape defect, not be replaced by a weaker claim.*

## Key Decisions

- **D1. Project each lowering location lazily once, then pass canonical data only.** After profile
  evaluation and exclusion selection, lowering owns a local cache keyed by usage index. Its one
  route-aware boundary maps live raw locations or validates replay referents and returns
  `(referent | None, rendered_location)`. The warning pre-pass requests only `NON_NUMERICAL`
  indices. The excluded-record loop reuses those cached results and lazily projects other excluded
  kinds only when reached. `_report_non_numerical_warnings`, `_exclusion_for`, and minting accept
  canonical values, never raw `LocationFact`, roots, or route mode. Named exclusions without a
  `LocationFact` retain `<no location>`; anonymous exclusions still fail because location is
  identity-bearing. *Rejected: call a shared mapper separately from warning and record consumers
  (double boundary and two failure points); eagerly project every exclusion before BLOCK (broadens
  the R-8 masking surface); canonicalize all facts (changes eligible bytes).*
- **D2. Keep ID minting physically separate from location projection.** The named excluded mint
  expression and tuple stay unchanged. The anonymous excluded branch continues to add canonical
  referent/line/column and request its current 32-hex suffix. The eligible branch is untouched.
  *Rejected: pass every ID through a new common tuple builder (unnecessary churn risk); include
  named location in its tuple (violates named-ID stability).*
- **D3. Validate with small path-aware primitives inside `snapshot/loader.py`.** Use helpers for
  mapping, list, string, boolean, integer, nullable value, required key, and string-list checks,
  plus three explicit validators: constraint facts/ExpressionIR, part occurrences, and lowering
  mode. Dynamic mapping keys use RFC 6901 escaping in JSON Pointer paths. *Rejected: JSON Schema or
  Pydantic models (a parallel schema and dependency surface); validation inside companion code
  (cross-repo change and wider consumers); ad hoc `try/except` alone (wrong empty containers can
  still deserialize silently).*
- **D3a. Preserve the recursive unknown-key version sentinel exactly.** After confirming the facts
  envelope is a mapping with the pinned facts version, run the existing recursive
  `_scan_expression_ir_versions` across the complete facts value before kind-directed structural
  validation. Ordinary extra keys and extra payloads carrying `expression-ir/v1` remain accepted;
  any nested `schema_version` string beginning `expression-ir/` with another version remains a
  `SnapshotFormatError`, even below an unknown key. Unrelated schema-version strings retain current
  behavior. *Rejected: scan only recognized IR child slots (weakens forward-version detection);
  structurally validate unknown payloads (turns extras into a new schema surface).*
- **D4. Use one normalized error grammar.** Every structural failure is:
  `Snapshot <file>: <json-pointer>: <problem>. Expected <shape>. Recapture the snapshot.` A missing
  key says `missing required field '<name>'`; a wrong value says `found <JSON type/value>`. JSON
  syntax/root failures use pointer `/`. Residual reconstruction failures say
  `reconstruction failed: <original detail>` at `/constraint_facts` or `/part_occurrences`.
  *Rejected: preserve arbitrary companion exception text as the public exception (no section/path
  contract); discard the original detail entirely (harder diagnosis).*
- **D5. Normalize only the in-scope reconstructors.** Catch `AttributeError`, `KeyError`,
  `TypeError`, and `ValueError` around companion facts parsing and occurrence reconstruction,
  separately, and raise `SnapshotFormatError` from the original. Do not wrap legacy calc,
  hierarchy, aggregation, alias, computed-attribute, or compilation-result reconstruction.
  *Rejected: one catch around the whole loader (silently broadens legacy schemas and obscures the
  failing section).*
- **D6. Commit one prevalidated, recoverable two-file transaction.** Build both fixture candidates
  completely before either target changes. Require byte-exact parse/re-render identity on each
  original, exact 65+1 structural pointer diffs, token/format preservation, expected candidate
  hashes, and prospective whole-corpus manifests. Stage candidates, immutable backups, and a
  durable phase journal on the repository filesystem; replace each target atomically with
  `os.replace`. Any exception rolls both targets back and verifies original hashes. An interrupted
  rerun sees the journal and restores both originals before starting. Only after both replacements
  and post-write manifests pass is the journal cleared. *Rejected: independent writes (partial
  corpus state); generic parse/dump without round-trip equality (format churn); full licensed
  recapture (parser/timestamp drift); hand edits.*
- **D7. Keep R-11 and Item 3 structurally disjoint.** Loader validation checks only serialized
  containers, keys, nullability, and leaf types before the unchanged occurrence reconstructor. It
  does not check cardinality closure, owner demand, occurrence completeness, demand collisions, or
  expansion semantics. Lowering edits stop at warning/location projection and the excluded branch;
  the eligible occurrence/demand path remains untouched. *Rejected: validate semantic occurrence
  consistency here (Item 3 scope and a second reconstructor).*

## Architecture

### Location data flow and route parity

| Route | One boundary operation | Later consumers | ID effect |
|---|---|---|---|
| Live lowering | Lazy cache maps raw parser path against ordered roots once per requested excluded index | Warning, exclusion, and anonymous mint consume cached canonical pair | Named tuple unchanged; anonymous tuple unchanged from GAP-CLOSE |
| Snapshot capture | Deep-copy facts and map `location.file` once for every located selected index | Serializer consumes copied canonical facts | No minting occurs |
| Snapshot replay | Lazy cache validates stored referent once per requested excluded index | Warning, exclusion, and anonymous mint consume cached canonical pair | Same named and anonymous IDs as live |

Eligible usages never enter this projection. A named excluded usage with no location preserves the
existing `<no location>` payload and requires no route. Every other selected usage requires an
explicit route. Mapping or grammar failure halts before a warning, record, catalog, or generated
artifact can contain the raw path.

The serializer continues to deep-copy facts (`src/sysml_codegen/snapshot/serializer.py:145-160`).
The only selector change there is removal of the `identity.name is not None` skip. Lowering creates
one cache after it computes `excluded_usage_indices`. The projector is the only code in lowering
that receives `source_location_mode`, `source_roots`, and raw/stored `LocationFact`. A cache value
is an immutable `(referent | None, rendered_location)` pair. The warning pre-pass requests only
non-numerical indices; after the existing BLOCK check, the record loop requests remaining selected
indices. Consumers cannot remap or revalidate because they receive no route inputs.

### Loader data flow

```text
read bytes → JSON decode/root mapping → version gate
          → facts envelope mapping/version
          → existing recursive ExpressionIR version scan (all known/unknown keys)
          → validate three v3 sections with JSON Pointer paths
          → parse ConstraintFacts (normalize residual failure)
          → reconstruct occurrences (normalize residual failure)
          → existing legacy reconstruction, defaults, warnings, freshness
```

Validation runs after the exact v3 version gate and before either strict reconstructor. This keeps
old-version behavior unchanged and prevents partial/torn v3 data from reaching direct indexing.
Valid empty lists and maps remain valid. Extra keys remain structurally ignored, but the existing
recursive `expression-ir/*` version sentinel still examines their nested mappings/lists.

### Pre-validation policy

The validator implements the spec's field tables verbatim:

- Required keys must exist and must match their non-null shape.
- Required-nullable keys must exist; `null` is accepted, otherwise the non-null shape is checked.
- Optional-with-default keys may be absent; when present they accept `null` only where the table
  states mapping-or-null.
- No in-scope field degrades. `/compilation_results` and all legacy `.get(...)` behavior remain
  outside the validator.
- Python `bool` is not accepted as an integer for line, column, or occurrence index.
- Mapping-item lists validate every item before reconstruction. String lists validate every
  element. `literal.value` accepts any JSON value, including `null`.
- ExpressionIR dispatch validates the exact v1 version and one recognized kind, then only that
  kind's fields. Child expressions recurse with their full parent pointer. Unknown extra keys are
  not shape-validated, matching the companion codec; the separate recursive scan still rejects a
  foreign `expression-ir/*` version anywhere under `constraint_facts`.

## Exact Relocation Projection Manifest

The dedicated harness is
`tests/conformance/test_constraint_snapshot_portability.py`. It writes the same `model.sysml` bytes
under these exact temporary roots:

- A: `<tmp>/checkout-a/models/model.sysml`
- B: `<tmp>/checkout-b/models/model.sysml`
- moved replay: `<tmp>/moved/models/{model.sysml,extraction_snapshot.json}`

Each live/capture call receives the one-element ordered root list `[<checkout>/models]`. Every
generation uses package name `snapshot_portability`, schema class `Params`, pipeline name
`pipeline`, and `overwrite=True`. The model contains a `Host` part definition and one instance,
with exactly three controls: named `status_annotation` (`String == String`, NON_NUMERICAL), an
anonymous `assert constraint { status == "on" }` (NON_NUMERICAL), and named `positive_value`
(`Real > 0.0`, ADMIT). The harness first asserts those extracted names/eligibilities and that both
excluded usages have non-null locations. A shape mismatch fails the test; it is not skipped.

### Scenario 1: equivalent live roots and replay A

The licensed test entry point is:

`uv run pytest -q tests/conformance/test_constraint_snapshot_portability.py::test_live_capture_replay_relocation_manifest`

It performs these operations in order:

1. Write identical model bytes at A and B.
2. Call `capture_snapshot([A/models], A/models/extraction_snapshot.json)` and the same call at B.
3. Run `build_pipeline_context([A/models])` and `build_pipeline_context([B/models])` under captured
   lowering logs; load A through `build_pipeline_context_from_snapshot` for replay facts/catalog.
4. Run `run_codegen(GenerationConfig(models_path=A/models, ...))`, the same live generation at B,
   and `run_codegen(GenerationConfig(from_snapshot=A snapshot, ...))` into separate output roots.
5. Compare live A, live B, and replay A using the manifest below.

### Scenario 2: unchanged moved replay

After A capture, the harness copies A's `model.sysml` and exact snapshot bytes with `copy2` into
`<tmp>/moved/models`; it asserts the source and snapshot SHA-256 values are unchanged. It runs
`build_pipeline_context_from_snapshot` and `run_codegen` against the original A snapshot and moved
snapshot, with the same generation options, then compares the manifest. No JSON rewriting,
timestamp rewriting, or path substitution occurs during relocation.

### Evidence rule when a license is unavailable

The live test uses the shared `@requires_license` marker from `tests/conftest.py:40-42`. A skip is
recorded as **licensed live relocation unproven** and does not satisfy Scenario 1 or the full Item 4
acceptance gate. It must never be reported as pass/green evidence.

A separate license-free entry point always runs:

`uv run pytest -q tests/conformance/test_constraint_snapshot_portability.py::test_snapshot_only_moved_replay_manifest`

It starts from the corrected `constraint_non_numerical` v3 snapshot, adds a canonical package-owned
anonymous NON_NUMERICAL fact in memory, and asserts the final facts contain the same three controls:
named excluded, anonymous excluded, and named eligible. It writes identical canonical snapshot and
source bytes beneath `<tmp>/replay-a/models` and `<tmp>/replay-b/models`, runs both through
`build_pipeline_context_from_snapshot` and `run_codegen`, and compares the same replay-applicable
manifest. This proves replay validation, warning/catalog bytes, generated artifacts, moved-source
anchoring, and root-leak absence. It does not prove live mapping or capture. Evidence must state one
of two outcomes: `licensed + snapshot fallback passed`, or `snapshot fallback passed; licensed live
relocation skipped/unproven`.

No path, timestamp, JSON, or generated-file normalization is permitted during comparison.

| Compared output | Exact projection | Equality |
|---|---|---|
| Serialized excluded facts | Ordered `/constraint_facts/usages/<i>` objects for production selector indices | Canonical JSON bytes: sorted keys, compact separators, ASCII escaping |
| Warning stream | Ordered lowering logger messages for selected `NON_NUMERICAL` usages | Exact string-list equality |
| Catalog exclusions | `/excluded_records` from `ConstraintCatalog.model_dump(mode="json")` | Canonical JSON bytes |
| Catalog fingerprint | `/fingerprint` from the same dump | Exact string |
| Model contract | `contracts/model_contract.json` | Full bytes, plus explicit equality at `/constraint_catalog/excluded_records`, `/constraint_catalog/fingerprint`, `/semantic_fingerprint` |
| Report aggregator | `modules/constraints/constraintreportaggregatormodule.py` | Full bytes, including embedded catalog fingerprint |
| Package contract effects | `contracts/package_contract.json` | Exact values at `/artifact_hashes/contracts~1model_contract.json` and `/artifact_hashes/modules~1constraints~1constraintreportaggregatormodule.py` |
| Root-leak scan | Every value/file above | Neither root A nor B, including redundant-leading-separator spellings, occurs |

The whole snapshot and package `/executable_fingerprint` are deliberately excluded for the reasons
fixed in the spec. Eligible facts retain raw locations and `captured_at` is provenance, not a
semantic relocation field.

## Required Invariants

- **I1. One selected set.** Live lowering and capture consume `excluded_usage_indices`; neither
  reproduces profile/owner classification.
- **I1a. One lowering route operation.** Each requested excluded usage index is mapped or validated
  at most once per lowering run. Warning, exclusion, and mint consumers accept only the cached
  canonical pair. BLOCK usages are not projected by the warning pre-pass.
- **I2. Excluded-only location projection.** Every selected usage with a location is canonical;
  no eligible usage is rewritten or route-validated.
- **I3. Route explicitness.** Raw live paths are mapped against ordered roots. Stored replay paths
  are grammar-validated. A string never selects its own route.
- **I4. No ID churn.** Named excluded, named eligible, and anonymous eligible IDs are byte-identical
  to the pre-change baseline. Anonymous excluded IDs retain their current referent/line/column
  tuple and 32-hex suffix.
- **I5. No raw path flow.** A mapped/validated location reaches warnings, exclusions, catalogs,
  fingerprints, contracts, and generated reports; a raw path reaches none of them.
- **I6. Shape gate precedes reconstruction.** No facts or occurrence item reaches direct indexing
  until every in-scope container, key, nullability rule, and leaf type has passed.
- **I7. Domain error totality.** Every malformed in-scope root/section/item raises
  `SnapshotFormatError` with file, JSON Pointer, expected shape/missing field, and recapture text.
  No raw `AttributeError`, `KeyError`, `TypeError`, `ValueError`, or JSON decode error escapes.
- **I8. Compatibility firewall.** Ordinary unknown extra keys remain accepted, while the existing
  recursive scan still rejects a foreign `expression-ir/*` version nested under any known or
  unknown key. Valid empty containers and explicit nullable values remain accepted. No legacy
  section gains a new required field or loses an existing default/warning.
- **I9. Controlled corpus delta.** Only the two named snapshot files change, at their exact pointer
  allowlists. `captured_at`, eligible usage objects, derived baselines, and every other fixture byte
  remain identical.
- **I10. Transactional fixture pair.** Both candidate files and the prospective corpus manifest pass
  before the first replacement. A failure or interrupted rerun restores both original hashes; a
  one-file final state is never accepted as completion.
- **I11. Item 3 disjointness.** Occurrence expansion, owner demand, demand collision behavior,
  cardinality, and eligible lowering remain unchanged. R-11 validates wire shape only.

## Component Overview

- **Source-referent module** (`src/sysml_codegen/analysis/source_referent.py`) — retains the codec;
  updates module/function wording from anonymous-only to excluded-location portability.
- **Constraint lowering** (`src/sysml_codegen/analysis/constraint_lowering.py`) — owns the lazy
  per-run projection cache and passes canonical pairs to warnings/exclusions/minting while
  preserving all mint and eligible occurrence branches.
- **Snapshot serializer** (`src/sysml_codegen/snapshot/serializer.py`) — copies and canonicalizes
  every located selected usage before facts serialization.
- **Snapshot loader** (`src/sysml_codegen/snapshot/loader.py`) — owns JSON Pointer formatting,
  narrow v3 structural validation, normalized messages, and reconstructor exception translation.
- **Snapshot domain error** (`src/sysml_codegen/snapshot/__init__.py`) — broadens the stale
  version-only `SnapshotFormatError` docstring to cover malformed current-version structure; the
  class and imports remain unchanged.
- **Existing reconstructors** (`../agentic-mbse/.../constraint_facts.py`,
  `../agentic-mbse/.../expression_ir.py`, and
  `src/sysml_codegen/analysis/part_instance_index.py`) — remain unchanged; they construct typed
  objects only after loader validation.
- **Portability conformance test** (`tests/conformance/test_constraint_snapshot_portability.py`) —
  owns the two relocation scenarios and exact projection manifest.
- **Shape matrix** (`tests/unit/test_snapshot_v3_gate.py`) — owns exhaustive field-policy mutation
  cases and error grammar.
- **Fixture evidence** (`.project/active/constraint-wave-snapshot-portability/evidence.md`) — records
  pointer-level before/after values and whole-corpus manifests during implementation.
- **Fixture transaction helper**
  (`.project/active/constraint-wave-snapshot-portability/evidence/update_fixture_locations.py`) —
  stages and validates the coordinated, formatting-preserving two-file update; it is audit tooling,
  not production code.

## File-Level Changes

| File | Planned responsibility |
|---|---|
| `src/sysml_codegen/analysis/source_referent.py` | Generalize anonymous-only documentation; no grammar change |
| `src/sysml_codegen/analysis/constraint_lowering.py` | Add one lazy index-keyed route projection consumed by warnings/exclusions/anonymous mint; preserve ID and eligible occurrence paths |
| `src/sysml_codegen/snapshot/serializer.py` | Extend copied-facts projection to named exclusions with locations |
| `src/sysml_codegen/snapshot/loader.py` | Add root decode normalization, JSON Pointer shape validators, three-section preflight, and narrow reconstructor normalization |
| `src/sysml_codegen/snapshot/__init__.py` | Update `SnapshotFormatError` contract documentation; no type or version change |
| `tests/unit/test_snapshot_v3_gate.py` | Replace the eight-cell gate with exhaustive policy/missing/wrong-shape/valid-control matrices |
| `tests/unit/test_source_referent.py` | Retain grammar/route tests; update names to cover named and anonymous excluded consumers |
| `tests/conformance/test_constraint_snapshot_identity.py` | Flip the named raw-location RED pin; add exact named/anonymous ID byte-firewall checks |
| `tests/conformance/test_constraint_non_numerical.py` | Pin canonical named warning/exclusion bytes on live and replay |
| `tests/conformance/test_constraint_snapshot_portability.py` | Add exact two-scenario artifact/fingerprint relocation manifest and root-leak scan |
| `tests/conformance/test_fingerprint_stability.py` | Keep existing general canary; add the named-exclusion semantic-fingerprint consequence if not wholly covered by the dedicated test |
| `tests/fixtures/catf_mfe_model/extraction_snapshot.json` | Change only `/constraint_facts/usages/0..64/location/file` |
| `tests/fixtures/constraint_non_numerical/extraction_snapshot.json` | Change only `/constraint_facts/usages/0/location/file` |
| `.project/active/constraint-wave-snapshot-portability/evidence.md` | Record RED/GREEN, allowlisted diffs, hashes, and gates during implementation |
| `.project/active/constraint-wave-snapshot-portability/evidence/update_fixture_locations.py` | Perform the prevalidated, journaled two-file fixture transaction |

No production change is planned in `part_instance_index.py`, `collect_bare_actual_demand`,
`_expand_owner_instances`, the companion repository, catalog, contracts, generators, templates,
graph rebuild, snapshot version constants/values, or legacy schemas.

## Controlled Two-Fixture Update

The committed correction is deterministic and pointer-allowlisted:

| Fixture | Exact mutable pointers | Old value class | New value |
|---|---|---|---|
| `catf_mfe_model/extraction_snapshot.json` | `/constraint_facts/usages/0/location/file` through `/constraint_facts/usages/64/location/file` | `///home/reid/1cfe/sysml-codegen/tests/fixtures/catf_mfe_model/<relative>` | `root-0/<same canonical percent-encoded relative path>` |
| `constraint_non_numerical/extraction_snapshot.json` | `/constraint_facts/usages/0/location/file` | `///home/reid/1cfe/sysml-codegen/tests/fixtures/constraint_non_numerical/model.sysml` | `root-0/model.sysml` |

The transaction helper follows this exact protocol:

1. If its durable transaction directory/journal exists from an interrupted run, restore both
   targets from immutable backups and verify the recorded original hashes before doing new work.
2. Read both original byte strings and the sorted SHA-256 manifest of every file under
   `tests/fixtures`. Parse with insertion order preserved. Assert
   `snapshot_to_json(parsed) == original_text` for each file before modification; otherwise abort.
3. In memory, derive the affected indices with the production selector and new values with
   `map_live_source_referent`. Assert the complete discovered set is exactly the 65+1 allowlist,
   every old value is the expected absolute-root form, every new value validates as a canonical
   referent, and `captured_at` plus every eligible usage object are unchanged.
4. Render both candidates with `snapshot_to_json`. Parse each candidate, revert only the 66 new
   values in memory, and assert re-rendered bytes equal the original bytes. Also require a unified
   byte diff whose changed lines are only the allowlisted JSON string values. This proves whitespace,
   indentation, key order, encoding, and all non-target tokens are preserved.
5. Before any target write, compute the prospective full fixture manifest by substituting the two
   staged candidate hashes. Require exactly those two paths to differ. Compute a separate manifest
   of every committed `baseline_outputs` file and require no candidate change.
6. Create a same-filesystem transaction directory containing both original backups, both candidate
   files, their hashes, manifests, and a journal at phase `prepared`; flush files and directory
   metadata. Atomically replace target 1, record/flush `first_replaced`; replace target 2,
   record/flush `second_replaced`.
7. Re-read both targets and all manifests. If any check fails, atomically restore both targets from
   backups and verify the original full manifest. On success, record evidence and mark `verified`
   before clearing the transaction directory. An implementation interruption leaves the journal
   and backups for step 1; it never turns a partial pair into accepted evidence.

Evidence records, per fixture: before/after SHA-256; every changed JSON Pointer with old/new value;
selector identity/QN; count; original timestamp bytes; byte-diff proof; and transaction phases. The
sorted fixture manifest may contain exactly these two snapshot paths. The committed-baseline
manifest must be identical.

## RED/GREEN Matrix

### R-6 portability

| Case | RED on current code | GREEN criterion |
|---|---|---|
| Named capture projection | Named selected usage remains absolute (`test_constraint_snapshot_identity.py:188-200`) | Canonical file; source facts object unchanged |
| Named live warning/record | Raw checkout prefix renders (`constraint_lowering.py:489-508,563-565`) | Exact `root-0/...:line:column` |
| NON_NUMERICAL route count | Warning and record paths can each map/validate | Instrument mapper/validator: exactly one call per excluded index per lowering run |
| BLOCK control | Warning pre-pass runs before BLOCK | Only NON_NUMERICAL sibling indices project; BLOCK index has zero route calls |
| Named ID firewall | Existing ID already location-independent | Exact pre-change ID remains equal while location changes |
| Anonymous control | GAP-CLOSE route parity is green | Existing ID, warning, location, record, fingerprint remain byte-identical |
| Eligible controls | Eligible facts remain raw and outside selector | Named/anonymous eligible IDs, location, grouping, serialized bytes unchanged |
| Equivalent live roots | Named warning/catalog/contract/report bytes differ by root | Every exact manifest row equal across live A/live B/replay A |
| Moved replay | Current named raw stored path leaks capture root | Replay A equals unchanged snapshot/tree moved to B; no root leak |
| Fixture scope | Two snapshots contain 65+1 raw selected locations | Only 66 allowlisted pointers in exactly two files change |

### R-11 shape boundary

| Mutation family | Representative current failure | GREEN criterion |
|---|---|---|
| JSON syntax or non-mapping root | `JSONDecodeError` or `.get` `AttributeError` | `/` `SnapshotFormatError` with expected mapping/valid JSON and recapture |
| Missing/wrong section | Existing missing gate is green; wrong empty list/dict can pass farther | Section pointer names exact expected mapping/string enum |
| Aggregate wrong container/item | `usages = 42` raises raw `TypeError` | `/constraint_facts/usages` expected list; item pointer expected mapping |
| Required key absent | Companion codec raises raw `KeyError` | Missing field's full child pointer names the required field |
| Required-nullable absent/null | Absence raw `KeyError`; null may be valid | Absence rejects; explicit null loads |
| Optional-with-default absent/wrong | Optional operand type currently absent-valid | Absence loads; present wrong non-null type rejects at exact pointer |
| Occurrence wrong mapping/list/item | List root raises `.items` `AttributeError`; missing `steps` raises `KeyError` | Exact owner/index/step pointer and expected shape |
| Integer versus boolean | Python would accept bool as int in unchecked dataclass | bool rejects; int and nullable occurrence index load |
| ExpressionIR version/kind/children | Some version checks exist; nested shape can raise raw exceptions | Exact parent predicate/child pointer; recognized kind and v1 required |
| Valid empties/ordinary extras | `{}` occurrence table and empty fact lists are valid | Continue to load; ordinary unknown keys ignored structurally |
| Foreign IR version under unknown key | Current recursive scan rejects `expression-ir/v2` | Still rejects with `SnapshotFormatError`; v1 extra payload remains accepted |
| Legacy compatibility control | Legacy defaults/warnings remain current behavior | Same result/error/warning before and after; no v3 validator path mentions legacy section |
| Residual reconstructor fault | Raw companion/reconstructor `ValueError`/container error | Chained `SnapshotFormatError` at its section with original detail and recapture |
| Item 3 disjoint control | Existing occurrence/demand behavior | Byte/behavior-identical controls; no new semantic occurrence validation |

The unit matrix is generated from explicit case records, not from production validator tables, so
tests cannot pass by sharing the same omission. It includes at least one missing and one wrong-type
case for every field-policy row, every ExpressionIR kind, every list-item layer, and both valid-null
and valid-empty controls.

## Non-Goals

- Snapshot v4, migration, v2 coexistence, or constraint-facts/ExpressionIR schema changes.
- Canonicalizing eligible locations or implementing `[ANON-ELIGIBLE-KEY]`.
- Broad legacy loader hardening, new defaults, or promotion of warnings into errors.
- Weakening or narrowing the recursive unknown-key ExpressionIR version scan.
- Changing profile classification, exclusion kinds, catalog shape, constraint IDs, or model-root
  ordering semantics.
- Updating any fixture or derived baseline outside the exact two-file allowlist.
- Implementing Item 3 occurrence expansion, cardinality, owner-demand, or demand-collision
  corrections. Production code in this stage, commits, pushes, PR comments, and remote state are
  also outside this design revision.

## Implementation Notes

- Keep JSON Pointer construction central and escape `~` as `~0`, `/` as `~1`; owner keys are data,
  not trusted path fragments.
- Report JSON types as `object`, `array`, `string`, `number`, `boolean`, and `null`; include a short
  value only for enums/version tags. Do not dump entire malformed payloads into errors.
- Validate the mode as a string before membership testing so `[]` cannot cause a raw unhashable
  `TypeError` (`src/sysml_codegen/snapshot/loader.py:191`).
- Parse the JSON once. Root validation must occur before `.get`; version validation remains before
  v3 nested validation.
- Keep serializer copy semantics. Never mutate `PipelineContext.constraint_facts`.
- Keep the lowering projection cache local to one `lower_constraints` call. The projector asserts
  the index is selected, stores the canonical pair before returning, and is the only lowering code
  allowed to receive route/roots. Tests instrument both source-referent entry points.
- Run the existing recursive version scan after facts envelope validation and before kind-directed
  shape traversal. Do not refactor it into the recognized-node validator.
- Do not move canonical locations into `UsageDecision`, `ConstraintFacts` live objects, or named ID
  tuples. Those placements invite hidden identity changes.
- `constraint_lowering_mode == "grandfathered_off"` still serializes facts without applying the
  exclusion selector, matching current v3 semantics. The shape gate validates the facts regardless
  of mode.
- Keep occurrence validation syntactic. Do not call occurrence expansion or demand collectors from
  the loader, and do not add fields beyond the spec table.

## Potential Risks

- **Validator drift from the companion codec.** Mitigation: field policy is pinned in the spec and
  tests independently enumerate every row. The current recursive unknown-key version scan remains
  an independent sentinel. Companion codec pins stay at v1; any repin requires reviewing both.
- **Named ID churn through refactoring.** Mitigation: keep mint code untouched and pin exact IDs for
  all three exclusion kinds before and after.
- **Eligible bytes accidentally canonicalized.** Mitigation: selector-index controls compare entire
  eligible usage objects before/after capture and across fixture updates.
- **Root-dependent generated headers contaminate the manifest.** Mitigation: compare only the
  spec-fixed full files/pointers. Do not expand to package executable fingerprint or whole snapshot.
- **Mechanical fixture update encodes the wrong capture roots.** Mitigation: assert the capture
  script supplies each fixture directory as slot 0 and corroborate all mapped values with the
  production helper before writing.
- **Interruption after one fixture replacement.** Mitigation: both candidates and manifests pass
  before writes; immutable backups plus a flushed phase journal make an interrupted rerun restore
  the pair before proceeding.
- **License absence is mistaken for parity evidence.** Mitigation: the shared marker reports a skip;
  evidence labels live relocation unproven and reports snapshot-only fallback separately.
- **Overbroad exception normalization hides a real legacy bug.** Mitigation: exception scopes end
  immediately after each in-scope reconstructor call; legacy reconstruction runs outside them.

## Integration Strategy

Land behavior and evidence in four separable steps at the implementation stage:

1. Add R-6 RED controls and exact pre-change ID/fixture manifests; implement the lazy once-per-index
   lowering boundary and capture projection, including call-count/BLOCK controls.
2. Add the R-11 malformed-shape matrix against current code; implement the loader boundary until
   every failure is a normalized, exact-path `SnapshotFormatError` while valid controls and the
   recursive unknown-key version sentinel pass.
3. Run the prevalidated journaled two-fixture transaction; record byte/token diffs, rollback state,
   and prove all unrelated fixture/baseline bytes unchanged.
4. Run the snapshot-only moved-replay manifest unconditionally. Run the licensed live/capture/replay
   manifest when the shared license marker permits it; otherwise record it as skipped and unproven.
   Then run focused normal/optimized gates, existing v3/parity/fingerprint tests,
   formatting/lint/type checks, and `git diff --check` without commit or remote actions.

No schema-version coordination is required because accepted v3 semantics are narrowed, not changed:
previously valid v3 snapshots remain valid; structurally malformed v3 data now fails through the
promised domain exception.

## Validation Approach

- **Focused unit:** source-referent grammar; exhaustive v3 shape matrix; facts and occurrences
  round-trip; legacy degradation controls; exact message grammar.
- **Focused conformance:** named/anonymous live-capture-replay identity; non-numerical warning and
  catalog parity; exact relocation manifest; catalog determinism; semantic/package artifact hashes.
- **Fixture evidence:** selector inventory across all committed snapshots; exact 66-pointer diff;
  `captured_at` equality; two-path fixture manifest; unchanged derived-baseline manifest.
- **Route proof:** equivalent A/B live trees and moved A snapshot/tree replayed at both roots, with
  exact bytes and root-leak scans. The exact roots, model controls, entry points, commands, and
  license claims are defined above. Repeated live/replay controls detect nondeterminism.
- **Regression:** existing `test_snapshot_v3_gate.py`, `test_occurrence_roundtrip_parity.py`,
  `test_snapshot_contract.py`, `test_hygiene_tail_loader.py`, constraint parity, fingerprint,
  contract, and generated-package tests.
- **Execution modes:** focused tests under normal Python and `python -O`; snapshot fallback always;
  licensed live leg only when actually executed; touched-file Ruff/format, targeted mypy, full
  fixture manifests, and `git diff --check`.

## Next-Stage Handoff

Carry these reviewed design decisions into planning: excluded-only selector authority; one lazy
lowering route boundary; explicit live/replay routes; unchanged ID mint expressions; the preserved
recursive unknown-key version scan; loader-local pre-validation of only the three v3 sections;
exact message grammar; narrow reconstructor normalization; executable licensed/fallback relocation
harnesses; and the journaled 65+1 pointer fixture transaction. These mechanism choices are
agent-grade design decisions unless their source requirement is owner-originated in the draft spec;
approval does not relabel inferred manifest or fixture details as owner-settled.

There is no unresolved design decision. De-risk the once-per-index call count and named ID firewall
first. Then get the independent field-policy and unknown-extra version cases RED before writing
validators. Build and validate both fixture candidates before testing the replacement transaction.

After implementation, run `my-audit` in a fresh session. Do not self-certify from implementation
evidence.

---

Next step after approval: `my-plan`, then `my-implement`; use `my-audit` for independent
certification.
