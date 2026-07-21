# Implementation Plan: GAP-CLOSE Item 5 — Packaging, Docs, and Hygiene Closeout

**Status:** Local Scope Certified — Ready for Explicitly Partial Pre-PR

**Created:** 2026-07-18

**Last Updated:** 2026-07-18
**Scope:** GAP-CLOSE Item 5 only

## Source Documents

- **Spec:** [spec.md](spec.md)
- **Epic:** [epic_gap_close.md](../../backlog/epic_gap_close.md), Item 5
- **Verified findings:**
  [final gap review](../../research/20260718-123558_constraint-expression-final-gap-review.md),
  F3, F10, and hygiene 2/4–8; [independent verification](../../research/20260718_gap-review-verification.md),
  F3, F10, and hygiene 2/4–8
- **Inherited v3 contract:**
  [numerical-profile spec](../numerical-constraint-profile/spec.md) and
  [design](../numerical-constraint-profile/design.md)
- **Design:** deliberately omitted by the recorded stage disposition in
  [spec.md#related-artifacts](spec.md#related-artifacts). The spec and epic fix the mechanisms and
  leave only local file choices; this plan supplies sequencing, test stencils, and validation.

## Implementation Strategy

### Phasing Rationale

Close the installability gap first because editable siblings can make every later paired test green
against an illegal distribution pairing. Once built metadata and the resolver prove the floor, make
the three durable documents agree with v3. Then cure the local API, diagnostic, loader, execution,
and whitespace defects. Run focused cross-repository checks and literal documentation assertions
before paying for the final licensed suites and wave-wide artifact gates.

### Critical Path

Built companion `0.1.1` + codegen floor `>=0.1.1` → metadata-only old/new resolver proof → three
durable F10 documents → hygiene contracts → focused paired checks → final licensed paired candidate
and static/diff/fixture/metadata gates → evidence and status sync for independent audit.

### First Proof Point

Build the pre-change companion wheel as the `0.1.0` negative candidate before editing version
files. After the bump, build fresh companion and codegen wheels into isolated directories. Read
their wheel metadata without importing either package, then run the same resolver probe twice with
the editable sibling disabled: the codegen wheel plus `agentic-mbse 0.1.0` must fail specifically
on `agentic-mbse>=0.1.1`; the same codegen wheel plus `0.1.1` must resolve. A source-text check, an
import-time v3 pin failure, or a green editable checkout does not count.

### Compatible Patch Decision

Use **agentic-mbse `0.1.1`** and raise sysml-codegen's requirement to
**`agentic-mbse>=0.1.1`**. Current packaging evidence has both companion version surfaces at
`0.1.0`, codegen at `agentic-mbse>=0.1.0`, and no repository tag that consumes `0.1.1`. This is the
smallest compatible patch increment and changes neither major/minor compatibility nor the v3
semantic-profile identifier. If implementation discovers published or branch packaging evidence
that makes `0.1.1` already used for incompatible bytes, stop and amend the plan rather than silently
choosing another version.

### Scope and Ordering Firewall

- Item 5 depends on all Items 1–4. Record both repository revisions and dirty status before edits;
  do not start while any Item 1–4 implementation is absent from the paired candidate.
- Preserve every Item 1–4 behavior, test, artifact, and dirty hunk. Do not reset, restore, stash,
  clean, recapture fixtures, or bulk-format Python. The branch-wide whitespace cure may remove only
  trailing spaces or tabs; prove non-whitespace content is unchanged.
- Do not change executable-profile decisions or semantic version, expression/fact schemas,
  generated predicate behavior, package/seal formats, or the external evaluator.
- Do not commit, push, or comment on either PR. A fresh independent epic audit followed by
  `my-pre-pr` owns those actions.
- `[GAP-CLOSE-F1-TEAX-NORMALIZATION]` remains an external dependency. Codegen propagation is done;
  evaluator normalization and constraint-module identity are not. No Item 5 artifact may mark F1
  or GAP-CLOSE complete while that row remains open.
- Merge order is load-bearing: **agentic-mbse PR #11 before sysml-codegen PR #9**. Keep this order
  in evidence, status notes, and the later PR-comment handoff.

### Overall Validation Approach

- Start each phase with a kept test or executable assertion that is RED or demonstrably stale
  before the phase's changes.
- Keep packaging proof separate from runtime/schema guards: wheel metadata proves legal selection;
  runtime/profile/schema pins prove loaded-code compatibility.
- Record exact revisions, resolved import roots, Python/uv versions, commands, exit codes, test
  counts, fixture manifests, generated-tree manifests, and permitted byte diffs in
  `.project/active/gap-closeout/evidence.md` during implementation.
- Run no fixture capture command. Any unexpected fixture or generated-byte change is a stop
  condition until it is traced and explicitly justified against the spec.

---

## Phase 1: Metadata Version, Floor, and Resolver Pairing Proof

### Goal

Publish one internally consistent companion patch identity, require it from codegen metadata, and
prove a real resolver cannot legally select the pre-v3 `0.1.0` companion.

### Assumption Under Test

The packaging sources are sufficient to make built distributions distinguish the v3-capable
companion without relying on imports, editable source configuration, or runtime pins.

### Test Stencil (Write This First)

```python
def test_built_metadata_requires_compatible_companion(codegen_wheel, companion_wheel):
    codegen = read_wheel_metadata(codegen_wheel)       # no imports
    companion = read_wheel_metadata(companion_wheel)
    requirement = requirement_named(codegen, "agentic-mbse")
    assert companion["Version"] == "0.1.1"
    assert Version("0.1.0") not in requirement.specifier
    assert Version("0.1.1") in requirement.specifier
```

```python
def test_companion_runtime_and_build_versions_match():
    assert project_version("pyproject.toml") == "0.1.1"
    assert agentic_mbse.__version__ == "0.1.1"
```

### Changes Required

- [x] Before edits, build and hash the current companion `0.1.0` wheel into a temporary negative
  wheelhouse. Record its `Name`/`Version` metadata and exact companion revision in `evidence.md`.
- [x] `../agentic-mbse/tests/test_package_version.py` (new, write first): assert the project version
  and lazy package `__version__` agree and equal `0.1.1`; keep the import license-free.
- [x] `tests/unit/test_package_metadata.py` (new, write first): parse codegen's declared requirement
  and assert it rejects `0.1.0` and accepts `0.1.1`. Use standards-aware version/requirement parsing,
  not substring comparison.
- [x] `../agentic-mbse/pyproject.toml`: set the built distribution version to `0.1.1`.
- [x] `../agentic-mbse/src/agentic_mbse/__init__.py`: set `__version__` to `0.1.1`; preserve lazy
  import behavior and the public export list.
- [x] `pyproject.toml`: raise only the companion floor to `agentic-mbse>=0.1.1`; retain the editable
  sibling source for development, but do not use it in the pairing proof.
- [x] Build fresh wheels for both repositories in isolated output directories. Inspect codegen
  `Requires-Dist`, companion `Version`, and the wheel's packaged `__init__.py` directly.
- [x] Run an actual resolver in fresh temporary environments against two otherwise identical local
  wheelhouses: old companion only must fail on the version conflict; new companion only must
  resolve. Disable editable sources and prove the resolved files come from the wheels.

### Validation

**Automated:**

- [x] Run both new version/metadata tests in their owning repositories; require GREEN.
- [x] Run `uv build --wheel` for each repository and inspect the built `METADATA` without imports.
- [x] Run both resolver legs with the same codegen wheel and resolver command. Record full command,
  wheel hashes, exit status, selected versions, and the old-leg incompatibility diagnostic.
- [x] Install the accepted pair into a clean temporary environment and query distribution metadata
  plus `agentic_mbse.__version__`; record module/distribution roots and require `0.1.1` throughout.

**Manual review:**

- [x] Confirm the codegen package remains `0.1.0`; only its companion dependency floor changes.
- [x] Confirm `PROFILE_SEMANTIC_VERSION` remains `executable-profile/v3` and no schema pin moved.

**What We Know Works After This Phase:**

Built metadata identifies the compatible companion patch consistently, and a resolver can accept
`0.1.1` but cannot pair the final codegen distribution with companion `0.1.0`.

---

## Phase 2: Durable F10 Documentation

### Goal

Correct exactly the three named durable documents so companion authors and codegen consumers see
the same four-outcome v3 contract and the real snapshot lockstep boundary.

### Assumption Under Test

The shipped behavior can be documented without changing profile semantics, widening the docs
refresh, or weakening the distinction between package selection and runtime/schema guards.

### Test Stencil (Write This First)

```python
def test_durable_docs_pin_v3_contract(read_doc):
    companion = read_doc("agentic-mbse/docs/patterns/constraints.md")
    assert all(term in companion for term in ("ADMIT", "BLOCK", "NON_NUMERICAL", "UNASSESSED"))
    assert "excluded_records" in read_doc("sysml-codegen/docs/architecture/reference/28-constraint-lowering-and-catalog.md")
    snapshot = read_doc("sysml-codegen/docs/architecture/reference/27-snapshot-generation.md")
    assert "no lockstep surface" not in snapshot
```

### Changes Required

- [x] `../agentic-mbse/docs/patterns/constraints.md`: replace three-outcome and stale operator
  teaching with the four exact v3 outcomes and their consequences. State the equality split and
  reasons from the inherited v3 contract; state valid binary `xor`/`implies` numerical-containment
  classification and malformed-arity default denial.
- [x] `docs/architecture/reference/28-constraint-lowering-and-catalog.md`: use the same four-outcome
  vocabulary. Document `excluded_records`, its validated `ConstraintExclusion` payload, and its
  inclusion with source and concrete records in the fingerprint.
- [x] `docs/architecture/reference/27-snapshot-generation.md`: replace the false no-companion-impact
  statement with the coordinated boundary. Explain that snapshot re-lowering consumes companion
  fact/IR schemas and executable-profile v3, while the package floor and runtime/schema guards
  protect different failure modes.
- [x] Do not edit other docs. Do not turn examples into new requirements or introduce claims about
  evaluator normalization or completed F1.

### Validation

**Automated:**

- [x] Run exact positive and negative `rg` assertions for the four outcome tokens, equality type
  split, `xor`/`implies`, malformed arity, `excluded_records`, all three fingerprint inputs,
  snapshot re-lowering, package floor, runtime/schema guards, and retired stale claims.
- [x] If the repositories have Markdown/document checks, run them on only these three surfaces.

**Contract review:**

- [x] Compare every operator/outcome statement with the v3 spec/design and current companion tests.
- [x] Confirm only the three named files changed and no line says F1 or GAP-CLOSE is complete.

**What We Know Works After This Phase:**

The wheel-shipped companion guide and both codegen references describe the same current v3
behavior, catalog shape, and coordinated snapshot boundary.

---

## Phase 3: Hygiene Contracts and Literal Whitespace Gate

### Goal

Make the two catalog types explicitly public, correct local contract text and warnings, make TEAx
discovery portable and validated, and remove literal trailing whitespace across both PR ranges.

### Assumption Under Test

Each hygiene defect is local and can be fixed without changing model schemas, catalog bytes,
lowering decisions, execution semantics, or any non-whitespace Item 1–4 content.

### Test Stencil (Write This First)

```python
def test_non_numerical_warning_preserves_profile_walk_order(caplog, facts):
    lower_constraints(facts, **empty_context())
    text = caplog.records[0].getMessage()
    assert usage_identity(facts) in text and rendered_location(facts) in text
    assert diagnostics(facts)[0].message in text
    assert text.index(diagnostics(facts)[0].message) < text.index(diagnostics(facts)[1].message)
```

```python
def test_teax_discovery_rejects_invalid_candidates(tmp_path):
    with pytest.raises(RuntimeError, match="TEAX_SIMKIT_PATH.*checkout-relative"):
        discover_teax_simkit({"TEAX_SIMKIT_PATH": str(tmp_path)}, missing_checkout(tmp_path))
```

### Changes Required

- [x] `tests/unit/test_concrete_constraint_model.py` (tests first): assert
  `ConstraintExclusion` and `ConstraintCatalogExcludedRecord` are present in the defining module's
  `__all__`; assert the catalog docstring names all three fingerprint collections.
- [x] `src/sysml_codegen/resolution/models.py`: keep both existing PascalCase models public and add
  both to `__all__`. Correct `ConstraintCatalog`'s docstring to name `source_records`,
  `concrete_entries`, and `excluded_records`. Do not rename fields or alter serialization.
- [x] `src/sysml_codegen/snapshot/loader.py`: replace the obsolete source-line citation with a
  symbol-level pointer to the current profile guard. Preserve the guard and its exception behavior.
- [x] `tests/conformance/test_constraint_non_numerical.py` (tests first): pin statement identity,
  rendered location, every diagnostic message in profile walk order, and live/snapshot warning
  equality. Reason codes may remain but cannot substitute for messages.
- [x] `src/sysml_codegen/analysis/constraint_lowering.py`: render all actionable diagnostic messages
  in `_report_non_numerical_warnings` without changing decision order, warning count, halt order, or
  exclusion payloads.
- [x] `tests/helpers/teax_discovery.py` and `tests/unit/test_teax_discovery.py` (new, tests first):
  isolate and test discovery of `TEAX_SIMKIT_PATH` and the checkout-relative
  `../teax/packages/teax-simkit` fallback. Accept only an existing directory containing the expected
  `simkit` package; pin precedence, duplicate avoidance, and actionable failure text.
- [x] `tests/execution/conftest.py`: use the tested helper, insert the validated package root only
  once, remove every user-specific absolute path and command example, and fail during execution-lane
  collection when neither route is valid.
- [x] Enumerate trailing-whitespace paths from each proposed PR range (`merge-base(main, HEAD)..HEAD`)
  and each current worktree before cleanup. Remove trailing spaces/tabs from every reported line,
  including Markdown hard breaks and EOF whitespace.
- [x] For the whitespace-only path set, compare a normalized pre/post content manifest that ignores
  trailing horizontal whitespace and final blank lines; require equality so Items 1–4 content is
  preserved. Do not run a general formatter.

### Validation

**Automated:**

- [x] Run the export/docstring, warning, snapshot parity, and TEAx discovery tests normally and
  under `python -O` where applicable.
- [x] Collect the execution lane with an explicit valid `TEAX_SIMKIT_PATH`, with the sibling
  fallback, and with neither candidate; require success, success, and the pinned early diagnostic.
- [x] Run `git diff --check <merge-base>..HEAD` and worktree `git diff --check` in both repositories;
  require no output. Repeat after all later phases.
- [x] Run the normalized content comparison for every whitespace-cleaned file.

**Scope review:**

- [x] Confirm no API/model field, profile decision, schema, fixture, or generated artifact changed.
- [x] Confirm live and snapshot warning strings are identical and messages remain in profile walk
  order.

**What We Know Works After This Phase:**

The public catalog API is explicit, local documentation is accurate, D5 warnings are actionable
and route-identical, execution discovery is portable, and both literal diff-check surfaces are
clean without changing Items 1–4 substance.

---

## Phase 4: Focused Cross-Repository Checks and Spot-Grep Assertions

### Goal

Exercise every Item 5 seam as one paired candidate and turn the documentation requirements into a
reviewable positive/negative assertion record before full-suite validation.

### Assumption Under Test

The metadata, docs, and hygiene changes compose across repositories and do not disturb v3 profile
decisions, lowering/catalog parity, or the completed Item 1–4 fixes.

### Test Stencil (Write This First)

```python
def test_item5_cross_repo_contract(pair):
    assert pair.companion_version == "0.1.1"
    assert pair.codegen_requirement_accepts("0.1.1")
    assert not pair.codegen_requirement_accepts("0.1.0")
    assert pair.live_warning == pair.snapshot_warning
    assert pair.catalog_fingerprint_changes_when_exclusions_change
```

### Changes Required

- [x] Add a table to `evidence.md` mapping every Item 5 success criterion to an exact focused test,
  resolver command, grep assertion, or later Phase 5 gate. Record actual command output, not only a
  checkbox.
- [x] Record both repository revisions, status, resolved import roots, built-wheel hashes, and
  `agentic_mbse` distribution/module versions before running paired checks.
- [x] Run companion focused tests covering package version plus executable-profile v3 equality,
  containment, malformed arity, diagnostics, codec, and hygiene surfaces.
- [x] Run codegen focused tests covering package metadata, model exports/docstring, non-numerical
  warnings, lowering, catalog fingerprint/exclusions, snapshot warning parity/guards, and execution
  discovery.
- [x] Run the focused codegen set against the exact companion checkout/revision intended for the
  wave. Assert resolved `agentic_mbse` module paths before pytest collection.
- [x] Execute and record literal spot-grep assertions for all three durable docs and negative greps
  for three-outcome teaching, admitted equality, always-blocked valid `xor`/`implies`, missing
  catalog exclusions, and no-lockstep/no-companion-impact claims.

### Validation

**Automated:**

- [x] Run both focused sets in normal mode and optimized Python. No assertion-dependent production
  behavior or Item 1–4 regression is permitted.
- [x] Run touched-file Ruff and format checks in both repositories, plus targeted mypy for changed
  production Python. Record project-wide static baselines for comparison in Phase 5.
- [x] Repeat built metadata inspection, both resolver legs, both repository diff checks, fixture
  manifests, and no-capture/no-generated-churn assertions.

**Review:**

- [x] Inspect every grep hit in context; token presence alone does not prove the surrounding claim
  is correct.
- [x] Confirm the external F1 row remains open and the #11-before-#9 merge order appears in the
  evidence/status handoff.

**What We Know Works After This Phase:**

Every Item 5 seam passes focused paired validation, and each durable prose requirement has an exact,
reviewed assertion rather than an unverified documentation claim.

---

## Phase 5: Final Licensed Suites, Wave Gates, and Artifact Sync

### Goal

Validate the exact final paired candidate with licensed full suites and all static, diff, fixture,
generated-byte, metadata, and status gates, then leave a complete record for independent audit and
pre-PR without externalizing changes.

### Assumption Under Test

The final companion/codegen pair is releasable as a coordinated wave, with no hidden editable
override, fixture drift, generated churn, new static debt, or regression in Items 1–4.

### Test Stencil (Write This First)

```python
def test_final_wave_evidence(record):
    assert record.licensed_codegen.green and record.licensed_companion.green
    assert record.fixture_manifests.before == record.fixture_manifests.after
    assert record.branch_diff_checks == {"codegen": "clean", "companion": "clean"}
    assert record.resolved_pair == record.declared_pair == ("0.1.0", "0.1.1")
    assert record.external_f1_status == "open"
```

### Changes Required

- [x] Freeze and record exact codegen and companion revisions, worktree status, import roots,
  distribution metadata, Python/uv versions, license route, and merge bases. Any edit after this
  point invalidates the suite record and requires rerunning affected gates.
- [x] Run the full licensed companion suite at the exact companion candidate.
- [x] Run the full licensed codegen suite against that exact companion candidate, including the
  execution lane through the validated TEAx discovery route. Record selected/deselected/skipped
  counts and reasons; do not call an unlicensed or editable-mismatched run the suite of record.
- [x] Re-run focused normal/optimized checks, project-wide and touched-file Ruff/format, project-wide
  and targeted mypy, both metadata resolver legs, wheel inspection, branch/worktree diff checks,
  fixture manifests, and placeholder/debug/secret scans.
- [x] Compare before/after manifests for both repositories' fixture trees. Require byte identity;
  no fixture recapture is authorized.
- [x] Run every already-required licensed live/snapshot generation comparison from the wave using
  the same input and final pair. Compare complete generated-tree manifests and review every byte
  diff. Accept only previously approved Item 1–4 changes; Item 5 itself should cause no generated
  artifact churn.
- [x] Complete `evidence.md` with the success-criterion matrix, exact outputs, justified byte-change
  table, unresolved external F1 statement, and #11-before-#9 merge order.
- [x] Update this plan's Implementation Notes and `.project/CURRENT_WORK.md` with Item 5's actual
  status and audit handoff. Synchronize companion current-work context if needed, without claiming
  certification.
- [x] Leave Item 5 **awaiting independent epic audit**. Do not check epic completion, commit, push,
  or comment. The next stages are a fresh independent GAP-CLOSE epic audit and `my-pre-pr`; only
  their success can authorize the paired external actions.

### Validation

**Suites and static gates:**

- [x] Licensed companion full suite: green, with exact counts and revision recorded.
- [x] Licensed codegen full suite including execution: green, with exact counts, companion revision,
  TEAx discovery route, and resolved roots recorded.
- [x] Ruff/format: clean on changed files and no new project-wide debt. Mypy: targeted clean and
  project-wide no worse than the recorded baseline, with every difference classified.

**Metadata, diff, fixture, and artifact gates:**

- [x] Old companion resolver leg rejects; `0.1.1` leg accepts; built/runtime metadata agree; no
  editable override participates.
- [x] Branch-range and worktree `git diff --check` are clean in both repositories.
- [x] Fixture manifests are identical; fixture diffs are empty; no capture command ran.
- [x] Required live/snapshot generated trees are byte-identical except for reviewed, inherited
  Item 1–4 changes. Every permitted change has a path, hash, reason, and owning item.
- [x] `git status --short` is classified path by path. No unrelated or pre-existing user change is
  absorbed into Item 5.

**What We Know Works After This Phase:**

The exact licensed companion/codegen candidate passes the wave gates with legal package pairing,
clean static/diff/fixture surfaces, reviewed artifact bytes, preserved Items 1–4, and an honest open
external F1 dependency. It is ready for independent epic audit, not yet for commit or PR updates.

---

## Risk Management

- **Editable override masks F3:** build and resolve wheels in isolated environments, inspect roots,
  and keep the old/new resolver legs identical except for the companion wheel.
- **Documentation drifts from executable truth:** derive assertions from current v3 tests and review
  each grep hit in context; touch only the three named surfaces.
- **Whitespace cleanup damages prior work:** enumerate exact paths, remove horizontal trailing
  whitespace only, and require normalized pre/post content equality.
- **Execution discovery passes only on one checkout:** test explicit-env, sibling-fallback, invalid,
  and missing routes; validate the actual `simkit` package before changing `sys.path`.
- **Full suites test the wrong pair:** record distribution metadata, module roots, and exact revisions
  before collection and in the final evidence.
- **Closeout overclaims F1:** keep `[GAP-CLOSE-F1-TEAX-NORMALIZATION]` visibly open in every status
  and handoff; distinguish codegen propagation from evaluator normalization/module identity.

## Environment Setup

Use each repository's documented `uv` environment and commands. The final codegen suite requires
the SysIDE license and a TEAx SimKit location accepted by the new discovery contract. Use temporary
directories for wheels, resolver environments, and generated comparisons. Do not write build
outputs into tracked repository paths.

## Implementation Notes

Fill these sections during implementation. Check phase boxes immediately after the recorded gate
passes; do not reconstruct results at session end.

### Phase 1 Completion

**Completed:** 2026-07-18

**Actual Changes:** Added package-version tests, bumped agentic-mbse's build/runtime/lock identity
to `0.1.1`, raised codegen's companion floor and lock record to `>=0.1.1`, and retained codegen at
`0.1.0`.

**Validation Results:** The pre-edit `0.1.0` wheel is preserved with sha256 `b1126ccc...`. Final
wheel metadata and packaged runtime source agree on companion `0.1.1`; codegen metadata declares
`agentic-mbse>=0.1.1`. The isolated old leg exited 1 as unsatisfiable, while the new leg installed
28 packages and resolved both imports from its wheel-only site-packages environment.

**Issues / Deviations:** Both lockfiles were refreshed because leaving root package metadata at
`0.1.0` would contradict the package sources. No dependency version churn was introduced for Item
5 beyond the root metadata/floor records.

### Phase 2 Completion

**Completed:** 2026-07-18

**Actual Changes:** Corrected exactly the three durable docs: companion constraints, codegen
constraint lowering/catalog, and codegen snapshot generation.

**Validation Results:** Positive assertions cover four outcomes, equality type split,
`xor`/`implies`, malformed arity, exclusions/fingerprint inputs, and snapshot lockstep guards.
Negative assertions found none of the retired three-outcome, admitted-equality,
always-blocked-binary-connective, or no-lockstep claims.

**Issues / Deviations:** None.

**Independent audit cure (2026-07-18):** Replaced the opening guide section with the exact v3
`ADMIT` / `BLOCK` / `NON_NUMERICAL` / `UNASSESSED` contract. Added a kept document regression that
rejects “one of three” and “three-outcome.” A rebuilt `0.1.1` wheel contains the corrected guide;
its sha256 is `b7ddf326342aede2b4de8b7eed03a9e9b182be880c2e19a77e8d17e324b7c20f`.

### Phase 3 Completion

**Completed:** 2026-07-18

**Actual Changes:** Exported both public exclusion models, corrected the catalog docstring and
loader pointer, rendered every D5 diagnostic reason/message in walk order, added validated portable
TEAx discovery, and removed literal branch-range whitespace without changing normalized content.

**Validation Results:** Focused codegen hygiene/lowering/catalog/snapshot tests passed 120 in both
normal and optimized mode. Explicit discovery executed 9 real-SimKit tests; sibling fallback
collected the same 9; invalid-route helper tests fail early with both accepted routes named. Final
candidate and worktree diff checks are clean.

**Issues / Deviations:** With commits forbidden, immutable `merge-base..HEAD` objects retain their
historical whitespace. `git diff --check <merge-base>` proves the proposed candidate including the
worktree cleanup is clean; `evidence.md` records this distinction. Independent audit cure:
candidate resolution and package validation now normalize `OSError` and `RuntimeError` into the
route-aware discovery failure. A self-referential symlink regression proves the final diagnostic
names both accepted routes and the symlink failure. Explicit execution passes 9 tests; fallback
collection finds the same 9.

### Phase 4 Completion

**Completed:** 2026-07-18

**Actual Changes:** Composed the exact paired source candidate and mapped each Item 5 criterion to
focused tests, resolver legs, documentation assertions, or a Phase 5 gate.

**Validation Results:** Companion focused gates passed 169 normal and 169 optimized; codegen passed
120 normal and 120 optimized. Touched-file Ruff/format checks passed in both repositories. Final
wheel hashes, import roots, resolver outcomes, fixtures, and diff results are in `evidence.md`.

**Issues / Deviations:** Project-wide static debt remains and is classified in Phase 5. No Item 5
Python path adds a Ruff or mypy finding.

### Phase 5 Completion

**Completed:** 2026-07-18

**Actual Changes:** Froze and validated the paired candidate, completed the evidence record, and
synchronized the spec, plan, and both current-work files for independent audit.

**Validation Results:** Licensed companion suite: 1,525 passed / 1 skipped / 33 deselected.
Licensed codegen suite: 2,516 passed / 26 skipped / 9 deselected. Licensed execution: 9 passed.
Required live/snapshot family: 11 passed. Touched static checks, metadata pairing, candidate/worktree
diff checks, placeholder scan, and both fixture manifests pass.

**Fixture / Artifact Results:** All 179 codegen and 61 companion fixture hashes match the pre-edit
manifests. Fixture diffs are empty. The live/snapshot gate found no Item 5 generated byte change.

**External F1 Status:** `[GAP-CLOSE-F1-TEAX-NORMALIZATION]` remains open. Codegen propagation is
complete; evaluator normalization and failed constraint-module identity are not. F1 and GAP-CLOSE
remain open.

**Issues / Deviations:** Codegen mypy remains at 76 errors in 17 files. Companion's current broad
mypy command reports 104 errors in 22 files outside Item 5, versus the earlier narrower 21-error
record; this discrepancy is preserved for audit. Companion source-wide Ruff retains one existing
N806 finding, and project-wide format checks retain pre-existing debt. Changed-file checks pass.

### Independent Audit Cure Completion

**Completed:** 2026-07-18

**RED evidence:** The document test failed on the wheel-shipped “one of three” passage. The route
parity test showed live absolute paths versus snapshot `root-0/model.sysml`. The hostile-path test
received a raw `Symlink loop` exception without either accepted discovery route.

**Changes:** Corrected the opening companion guide and pinned it with a kept document test;
canonicalized anonymous warning locations through the existing live/snapshot referent mechanism;
captured and compared exact warning strings across repeated live, relocated live, and snapshot
routes; normalized TEAx candidate filesystem failures and added a symlink-loop regression.

**Validation:** Three defect tests pass independently. Companion relevant selection: 36 passed.
Codegen relevant normal and optimized selections: 63 passed / 13 skipped each. Licensed route and
snapshot selection: 16 passed. Real SimKit execution: 9 passed; fallback collection: 9 nodes.
Touched Ruff/format checks pass, including the formatted kept companion regression
`tests/test_constraint_documentation.py`. Targeted mypy retains the same three inherited lowering
findings. Final candidate and worktree diff checks are clean in both repositories; fixture
manifests remain identical and fixture diffs remain empty at 179 codegen / 61 companion files.

**Deviations:** Full suites were not rerun because the audit cures are confined to one guide, one
warning-location seam, and the test-only TEAx discovery helper. The prior licensed full-suite
records remain the wave evidence; the relevant broader and licensed seams were rerun above.

### Second Re-audit Cure Completion

**Completed:** 2026-07-18

**RED evidence:** The strengthened guide regression failed because the opening and later subtype
summary called blocked L6 diagnostics warnings and the latter omitted asserted `NON_NUMERICAL`.
The injected `Path.expanduser()` regression received only raw `injected expanduser failure` text,
without either accepted TEAx discovery route.

**Changes:** Corrected both wheel-shipped guide passages to state one L6 `ERROR` per blocked
construct and route asserted predicates to admitted, blocked, or non-numerical. Extended the kept
document regression to pin both sections and reject `WARNING per blocked construct`. Moved explicit
path expansion inside the existing candidate normalization boundary so expansion, resolution, and
validation failures share one route-aware diagnostic.

**Validation:** Isolated cure tests pass 1 companion and 1 codegen. Focused files pass 1 companion
and 5 codegen; the TEAx file also passes 5 under optimized Python. Relevant broader companion
guide/profile/L6 selection passes 119. The established licensed companion environment passes all 9
real SimKit execution tests. Touched Ruff/format checks pass after formatting the companion test.
The rebuilt `0.1.1` wheel is byte-identical to the corrected source guide and has sha256
`160e7eb55eb6bf4bfba3b422166e6e8f4eef50f7a6c09aa2f7ed91a7cd8a8d4f`. Both worktree diff checks
are clean and fixture diffs remain empty.

**Deviations:** The first execution attempt used codegen's smaller environment and stopped on its
known missing license export and `pandas`. Re-running through the established licensed companion
environment with explicit local source roots passed 9/9. Full suites were not rerun because these
cures affect only shipped prose and test-only discovery normalization; the focused, broader, and
real execution seams were rerun.

---

**Status:** Local Scope Certified — Ready for Explicitly Partial Pre-PR
