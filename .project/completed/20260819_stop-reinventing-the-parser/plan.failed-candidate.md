# Failed Candidate Implementation Plan: Exact occurrence derivation and evidence integrity

**Status:** Superseded — do not execute; Revision 6 targeted design confirmation and a replacement
plan are required
**Created:** 2026-08-16
**Last Updated:** 2026-08-17
**Complexity:** HIGH
**Historical implementation endpoint:** the failed audit3-F1/CI-2 through CI-6 remediation chain;
no active implementation is authorized by this file

## Source Documents

- **Spec:** [spec.md](spec.md) — approved revision 4
- **Design:** [design.md](design.md) — draft revision 6; incorporates the finalized Revision-5
  review and supersedes D5, D7, D9, and this plan's remediation strategy
- **Current design review:** [design-review.md](design-review.md) — Revision 5 `Revise`; resolutions
  finalized and incorporated into Revision 6
- **Product lens:** [product-lens.md](product-lens.md) — `BLOCKED` at `audit3-F1`
- **Primary research:** [premise audit](../../research/20260816-205035_premise-audit-fallback-census.md)
- **Revision-5 research:** [evidence-boundary convergence assessment](../../research/20260817-164828_expression-evidence-boundary-convergence-assessment.md)
- **Product promises:** [P-002](../../product/P-002-exact-owner-anchoring.md),
  [P-003](../../product/P-003-no-workarounds-for-bad-models.md), and
  [P-004](../../product/P-004-product-identity-parse-walk-emit.md)

## Fresh Audit Disposition — 2026-08-17

This checklist is retained as the record of the failed candidate and completed work. Implementation
must not resume from its unchecked boxes. After Revision 6 receives targeted design confirmation,
`my-plan` must replace this plan with work organized around semantic-evidence/v2, exact ownership-
manifest closure, the full natural-route matrix, and graph-derived registry authority.

The exact replacement topology and all six findings from the first Needs Work audit reproduce as
fixed on their intended routes. The new independent audit remains **Needs Work**. A licensed public
probe shows A5 can erase an index and bind the wrong occurrence. B3/B4 retain public typed-owner
bypasses, deep-literal reference construction can silently shorten a target path, and B9 accepts an
empty or incorrect invariant value. The final run report was assembled outside the committed runner,
while the settled owner decision below permanently removes the Agentic PDF suite from this evidence
contract. Phase 4/5's public fail-closed claims, Phase 7's
production designation, and Phase 9's run record are reopened. The current artifact topology and
Fusion measurements remain factual but cannot certify this production identity. See [audit.md](audit.md).

## The Point

The product must consume SysIDE's resolved semantic model, derive concrete occurrence identity from
modeled containment and the consumer domain, preserve all parser evidence through one public
boundary, and emit that math into executable TEAx Python. A name, path, nearest candidate, only
candidate, declaration order, or convenient checkout cannot replace modeled semantic or artifact
identity. If the required authority is absent, the public route refuses by name before it produces a
partial graph, snapshot, package, or output mutation.

## Stage Decisions

- Shaping was not rerun because the approved revision-4 spec already fixes the product obligation,
  scope, success criteria, and owner-grade authority. This stage makes sequencing choices only.
- The spec was not rerun because [spec.md](spec.md) is approved revision 4, its adversarial review is
  `Approve`, and the owner stated that intent is fully clear.
- Product design was not rerun for Revision 4 because this item changes an internal
  semantic/evidence route. The later `audit3-F1` product-lens result supersedes that historical
  `CLEAR` result and is now `BLOCKED`.
- The Revision-4 approval-pause decision is historical. It does not authorize this superseded plan
  or the draft Revision-6 design.
- `close` and `pre_pr` are not part of this plan. The orchestrator stops after implementation and a
  fresh `$my-audit`; closing and the branch gate remain later workflow stages.

## Implementation Strategy

### Phasing rationale

The plan freezes reconstructable inputs first, then runs the three premise-killing probes before
any occurrence production change. Agentic-mbse lands its evidence contract as a standalone green
artifact. Codegen then consumes that artifact through one boundary, replaces occurrence election in
place, and proves the behavior from real SysIDE models through generated TEAx execution. Only after
all production code, tests, fixtures, docs, versions, pins, and locks are green is the final codegen
production identity named `C_prod`. Fusion pins only that identity and lands `F_final`. The final
codegen commit is an evidence-only direct child of `C_prod`.

### Critical path

```text
frozen baselines
  -> probe/fixture commit -> lock commit -> baseline/transition seed
  -> B2 + B8a + B10 kill gates
  -> agentic B1-B5/B8b green commit and artifacts
  -> codegen boundary + A1-A6/B6-B10 production commits
  -> real-model/public-mutation matrices + docs/ledgers green
  -> C_prod artifacts
  -> Fusion pins C_prod and lands F_final
  -> five-input isolated green evidence
  -> direct-child six-path C_evidence
  -> fresh audit
```

### First proof point

The first proof point is the Phase 2 gate set. B2 must satisfy all seven real topology rows, B8a
must record `REAL_CORPUS_TOTAL` with nonzero real reference and chain counts and zero missing leaves,
and B10 must record exactly `DELETE_UNREACHABLE`. Any other result stops implementation and returns
the item to design before D1-D7 or any occurrence-identity production edit.

### Required evidence topology

```text
agentic A_final ---------------------> codegen C_prod
                                             |
                                             | exact immutable pin
                                             v
                                       Fusion F_final
                                             |
                                             | completed evidence only
                                             v
codegen C_prod ----------------------> codegen C_evidence
                 direct parent; exactly six changed paths
```

`C_prod -> F_final -> C_evidence` is the causal evidence order. Git ancestry exists only inside each
repository: `C_evidence^ == C_prod`. Fusion pins `C_prod`, never `C_evidence`.

## Frozen Inputs and Worktree Discipline

| Repository | Frozen implementation input | Required role |
|---|---|---|
| sysml-codegen | `7b29d8b636e284364a4fdce9079f153c51c867ea` | production parent; `0.1.0` |
| agentic-mbse | `fcee56d6cee3828b6f3b7f29a9e684aa03b03bbb` | evidence parent; `0.1.2` |
| fusion-tea | `824a876e281a3b9aef58b1873bfbd0b20c4ab77b` | verification parent; `0.1.0` |
| TEAx / teax-simkit | `744745f895677f3344b9884627369a6a47ed987f` | immutable source input; `0.1.0` |
| 1costingfe | `02543850089be175ea7c28b92a8b2a4184e1637e` | immutable source/wheel input; `0.1.0` |

Known immutable artifact anchors:

- TEAx source URL `git@github.com:rwestwood89/teax.git`; deterministic source-tar SHA-256
  `3dea651f0b67340a11e28bac61ff1710b3cf20ef8b7ce498172f79c7ca0f8346`.
- 1costingfe source URL `https://github.com/1cFE/1costingfe.git`; deterministic source-tar SHA-256
  `f8c38bb58af43d667931ad8db9eb4ebd86168f77352d90c98462ae47376d056a`.
- Agentic source URL `https://github.com/1cFE/agentic-mbse.git` and codegen source URL
  `https://github.com/1cFE/sysml-codegen.git`; their final artifact hashes are measured from
  `A_final` and `C_prod`.
- Fusion source URL `https://github.com/1cFE/fusion-tea.git`; its frozen parent source-tar SHA-256 is
  `f83e056ce799a1105aba920baa1d5370891615a4530899bdc4eecbaf41ed38e7`, and its final archive hash is
  measured from `F_final`.

- [x] Before any edit, record `git status --short`, `git diff --binary`, and
  `git diff --cached --binary` for every existing checkout. Hash the records in a private run
  directory. Do not stage, stash, reset, clean, switch, or amend the existing dirty codegen or Fusion
  checkout.
- [x] Create dedicated implementation worktrees at the full SHAs above. Use new item-specific branch
  names for codegen, agentic, and Fusion; use detached read-only worktrees or archive extractions for
  TEAx and 1costingfe.
- [x] Require `git status --porcelain=v1` to be empty in each evidence worktree before a probe,
  archive build, suite run, or commit. The pre-existing working directories are never evidence.
- [x] Verify the three predecessor descendant relations with `git merge-base --is-ancestor` and
  record the full input SHAs. A failed ancestry check stops before Phase 1.
- [x] At every phase end, compare the original-checkout status digest with its entry digest. A change
  outside the dedicated worktrees is a phase failure.

The implementation may use a private temporary root such as one returned by
`mktemp -d /tmp/stop-parser.XXXXXX`. Record the resolved root once. Machine-absolute paths do not
enter fixture, transition, or semantic evidence; only the execution-provenance record may carry the
explicit extracted/install roots required by [design.md#executable-codegen-execution-pins](design.md#executable-codegen-execution-pins).

## Validation Command Contract

Run targeted commands inside the named clean worktree during development. Phase 9 reruns the same
logical suites from extracted immutable artifacts with the explicit artifact Python, never a sibling
checkout.

### Owner decision — permanently retire the Agentic PDF suite (2026-08-17)

**[OWNER-VERBATIM]** “do not rerun the PDF suite anymore. It's fine -- it is totally separate to
everything we doing. I have ZERO concerns about it. Please mark this SOMEWHERE so we never run it
again.”

This is a settled owner correction to the evidence contract. The Agentic command previously
identified as the deterministic slow PDF/HTML corpus suite,
`uv run pytest tests/ -m slow -k "not test_claude_extraction"`, is permanently retired from this
item and future parser-work validation. Do not invoke it. It is not a certification gate, and a
new Agentic identity does not require it to be rerun. Its existing result remains historical
information only. This supersedes every later plan task that requires, admits, or blocks on that
suite. It does not change any parser/SysIDE, Agentic fast, Codegen, Fusion, TEAx, static, or
mechanical-auditor requirement.

### Agentic-mbse

```bash
set -a
source /home/reid/1cfe/agentic-mbse/.env
set +a
uv run pytest tests/ -m "not slow"
uv run mypy src/
uv run ruff check src/ tests/
```

The fast pytest command plus the focused semantic-evidence tests are the Agentic parser-work gate.
The retired slow PDF/HTML taxonomy is historical information only. The 15 network-backed
`test_claude_extraction[...]` nodes also remain outside this orchestration because they can invoke a
paid external service. They are neither passed, skipped, green, nor required parser evidence. A
missing SysIDE license or an undeclared fast-suite skip fails the phase.

The slow marker inventory is closed as follows:

- `slow, corpus`: the 15
  `tests/test_corpus_integration.py::test_offline_extraction[<slug>]` nodes and
  `tests/test_corpus_integration.py::test_ground_truth_scoring` are deterministic/local.
- `slow`: `tests/test_equations.py::TestCorpusEquations::test_hawker_recall` and
  `tests/test_equations.py::TestCorpusEquations::test_hansen_zero_false_positives` are
  deterministic/local.
- `slow, corpus`: these exact external-service nodes are intentionally not invoked:
  `tests/test_corpus_integration.py::test_claude_extraction[araiinejad_2024]`,
  `tests/test_corpus_integration.py::test_claude_extraction[aries_cost_account]`,
  `tests/test_corpus_integration.py::test_claude_extraction[delene_2001]`,
  `tests/test_corpus_integration.py::test_claude_extraction[energy_amplifier]`,
  `tests/test_corpus_integration.py::test_claude_extraction[hansen_2025]`,
  `tests/test_corpus_integration.py::test_claude_extraction[hawker_2020]`,
  `tests/test_corpus_integration.py::test_claude_extraction[helios_design]`,
  `tests/test_corpus_integration.py::test_claude_extraction[hsu_2020]`,
  `tests/test_corpus_integration.py::test_claude_extraction[paischer_2025]`,
  `tests/test_corpus_integration.py::test_claude_extraction[schulte_1978]`,
  `tests/test_corpus_integration.py::test_claude_extraction[seo_2024]`,
  `tests/test_corpus_integration.py::test_claude_extraction[sparc_overview]`,
  `tests/test_corpus_integration.py::test_claude_extraction[tajima]`,
  `tests/test_corpus_integration.py::test_claude_extraction[woodruff_2026]`, and
  `tests/test_corpus_integration.py::test_claude_extraction[woodruff_2026b]`. These cases can invoke
  a paid external Claude service with corpus page data; repository implementation authority does
  not authorize that transfer or spend.

The one declared fast-suite skip is
`tests/test_sysml/test_adr002.py::test_real_model_expose_patterns_exempt`, reason exactly
`Requires fusion_modeling CATF models not in this repo`. No other fast skip is allowed.

The frozen agentic baseline does not have a globally green `mypy src/` result. The agentic type
gate is therefore a baseline-delta contract: run the identical command and environment at
`fcee56d6cee3828b6f3b7f29a9e684aa03b03bbb`, retain its canonical diagnostics, require targeted
mypy to pass for every changed production module, require no new or changed item-caused diagnostic,
and require the full diagnostic count to be no worse than baseline. Record the full nonzero result
as a baseline refusal; never describe it as globally green and do not repair unrelated modules.

The identical frozen-baseline Ruff command also exits nonzero on unrelated files. Apply the same
no-unrelated-rewrite rule: retain canonical baseline diagnostics, require every changed Python file
to pass targeted Ruff, require no new item-caused finding, and require the full count to be no worse
than baseline. Record the nonzero full result rather than calling it green.

The ignored slow PDF/HTML corpus is a separate immutable test-only input because the repository has
no official byte-reconstructable acquisition procedure. Its private input record must carry the
root-relative inventory, per-file and aggregate SHA-256, frozen source-checkout SHA/context,
declared injection paths, and the rule that only those files are copied: no secrets, ignored run
outputs, baselines, or reports. Never commit the corpus bytes. Before an extracted-archive test,
inject only the declared files and prove the destination inventory and aggregate hash match before
pytest starts. The source archive is not self-contained without this declared test input.

### Sysml-codegen

```bash
set -a
source /home/reid/1cfe/agentic-mbse/.env
set +a
uv run --extra dev pytest tests/
uv run --extra dev mypy src/
uv run --extra dev ruff check src/ tests/
```

The default suite deliberately excludes `execution`. Run the execution lane separately with the
artifact manifest and explicit TEAx root:

```bash
CODEGEN_EXECUTION_PROVENANCE=verification/execution-provenance.json \
TEAX_SIMKIT_PATH=<extracted-teax-root>/packages/teax-simkit \
<artifact-python> -m pytest tests/execution -m execution -q
```

No default, licensed, snapshot, generated-package, or execution-lane failure may be waived as
pre-existing. In particular, the 17 ordering-dependent failures previously recorded at `9ce5548`
must not be carried into `C_prod`; the fresh artifact run decides the result.

### 1costingfe

```bash
uv run pytest tests/ -m ""
uv run ruff check src/ tests/
```

The frozen 1costingfe project config declares pytest and ruff but no mypy/type-check command. Do not
invent a type gate for an unchanged dependency.

### TEAx

```bash
uv run pytest packages/teax-simkit/simkit/tests \
  packages/battery-tea-demo/battery_tea/tests -q
```

The frozen TEAx root declares this pytest battery and no repository lint/type command. TEAx source
does not change in this item.

### Fusion Tea

The offline composed run uses the isolated environment's explicit executables, not `uv run`:

```bash
uv lock --check
<artifact-venv>/bin/python -m pytest tests/
<artifact-venv>/bin/agentic-mbse validate --complete models/
<artifact-venv>/bin/python -m pytest \
  tests/test_codegen_teax_acceptance.py \
  tests/test_occurrence_mutation_teax.py
<artifact-venv>/bin/ruff check tests/
<artifact-venv>/bin/mypy tests/
```

If Fusion does not retain repo-level `ruff` or `mypy` coverage for its existing tree, the two new
artifact-verification test files remain the exact typed/linted scope; do not silently substitute a
different command.

### No-unexpected-skip rule

- [x] Add `-ra` and `--junitxml=<private-run-root>/<suite>.xml` to each recorded pytest invocation
  without changing selection. Store the base command above unchanged in `independent-green.json`.
- [x] Before each isolated run, declare the permitted skip node IDs and reasons in the staged
  dependency/run record. Any undeclared skip, changed reason, deselected required marker, or missing
  collected test fails the run.
- [x] Agentic's parser-focused and fast tests, all licensed codegen tests, the complete codegen
  execution lane, and the two Fusion generated-execution proofs permit no undeclared skips.
  Agentic's 15 external-service nodes are classified unrun inputs, not skips; the complete fast
  suite permits only its one declared missing-Fusion-model skip.
- [x] Record collected, selected, passed, failed, skipped, xfailed, and deselected counts. A report
  missing one of those fields is not independent-green evidence.

### Artifact and audit entry points

These scripts are production-side verification tooling and therefore land in `C_prod`. Their CLI
contracts are fixed before the final evidence exists:

```bash
<C-prod-python> verification/build_artifacts.py \
  --c-prod <full-C_prod-sha> \
  --agentic <full-A_final-sha> \
  --teax 744745f895677f3344b9884627369a6a47ed987f \
  --costingfe 02543850089be175ea7c28b92a8b2a4184e1637e \
  --fusion <full-F_final-sha> \
  --output <private-artifact-root>

<C-prod-python> verification/run_independent_green.py \
  --artifact-root <private-artifact-root> \
  --evidence-output <private-evidence-staging-root>

<C-prod-python> verification/audit_evidence.py \
  --repository <clean-codegen-repository> \
  --c-prod <full-C_prod-sha> \
  --f-final <full-F_final-sha> \
  --c-evidence <full-C_evidence-sha> \
  --artifact-root <private-artifact-root>
```

The angle-bracket values are required run inputs recorded at the phase that creates them; they are
not inferred from a current branch or sibling directory. Each script exits nonzero on a missing
input, dirty source, identity/hash mismatch, wrong import root, unexpected skip, or evidence-boundary
failure.

---

## Phase 1: Freeze probes, fixtures, manifests, hashes, and transition seed

### Goal

Create reconstructable pre-production inputs before any semantic production edit. This phase makes
three independently checkable codegen commits: `P_probe`, `P_lock`, and `P_seed`. See
[design.md#baseline-fixture-and-transition-evidence](design.md#baseline-fixture-and-transition-evidence).

### Assumption under test

The frozen 37-root corpus plus six new roots is closed, hashable, and sufficient to capture every
required before-state without reading dirty or unlisted files.

### Test stencil — write first

```python
def test_closed_fixture_inventory(manifest, repository):
    assert manifest.canonical_roots == 37
    assert manifest.added_roots == 6 and manifest.added_source_files == 7
    assert manifest.graph_records == 15 and manifest.typed_refusals == 22
    assert every_listed_root_has_a_source(manifest)
    assert no_unlisted_sysml_or_kerml_file(manifest, repository)
    assert all_recorded_sha256_values_match(manifest, repository)
```

### Changes required

**See:** [D10](design.md#d10-retained-probes-and-production-gate),
[probe/fixture lock](design.md#probefixture-commit-lock),
[closed inventory](design.md#closed-fixture-inventory), and
[transition seed](design.md#transition-ledger-seed).

- [x] **`sysml-codegen::.project/active/stop-reinventing-the-parser/probes/` (NEW):** add the retained
  `b2_containment_address_feasibility.py`, `b8_resolved_fact_totality.py`, and
  `b10_document_origin.py` probes plus their contract/self-tests. The B8a probe imports no new
  semantic-evidence API and synthesizes no missing leaf.
- [x] **`sysml-codegen::tests/fixtures/occurrence_domain_derivation/model.sysml` (NEW)** and the five
  other added roots named in the design: add exactly six roots and seven source files, including the
  two-file `feature_metadata_multifile` fixture. Do not copy Fusion or SysIDE library sources.
- [x] **`sysml-codegen::verification/fixture-manifest.json` (NEW):** expand the pinned v6 batch into
  exactly 37 canonical records, enumerate every source file and SHA-256, then add the six new roots.
  Reject missing, duplicate, absolute, `..`-containing, hash-mismatched, and unlisted source paths.
- [x] **`sysml-codegen::verification/capture_baseline.py` (NEW):** capture graph bytes, semantic
  identity rows, refusals, generated relative-path hashes, live/snapshot parity, execution hashes,
  versions, and source identities without mutating a model or output baseline.
- [x] Commit only the probes, their fixtures, the closed fixture inventory, and baseline-capture
  tooling as `P_probe`. Assert `P_probe^` is the frozen codegen baseline
  `7b29d8b636e284364a4fdce9079f153c51c867ea`.
- [x] **`sysml-codegen::verification/probe-fixture-lock.json` (NEW):** in a manifest-only `P_lock`
  commit, record the actual 40-lowercase-hex `P_probe`, require `P_lock^ == P_probe`, and hash every
  probe, source fixture, fixture manifest, and canonical batch manifest. Change no other path.
- [x] **`sysml-codegen::verification/pre-change-baseline.json` (NEW):** from a clean descendant,
  capture the 37 canonical roots at the production baseline and the six added roots at `P_probe`.
- [x] **`sysml-codegen::verification/expected-transitions.md` (NEW):** seed exactly the A1-A6,
  B1-B5, B6/B7, B8, B9, and B10 rows from the approved design. At this point it is an allow-list
  skeleton, not a claim that a transition passed.
- [x] Commit the immutable baseline and transition seed as `P_seed`; change no production source.

### Validation

- [x] Run the retained probe contract/self-tests and `capture_baseline.py --check` from `P_seed`.
- [x] Recompute all manifest/lock hashes and prove the pinned batch hash is
  `bd7bf245e3ca3923b9b5d41db97861c9fcdf64435e768d48a2d7027eb52d9288`.
- [x] Prove the anti-vacuity floor: 37 canonical roots; 15 graph records; 22 typed refusals; at least
  one source per canonical root; six added roots; seven added files; and at least one graph or named
  refusal for every inventory root.
- [x] Prove `git diff --name-only P_probe^..P_probe` and `P_probe..P_lock` match their closed path
  sets, `P_lock^ == P_probe`, and production source is byte-identical to the baseline.
- [x] Commit and immediately record the full `P_probe`, `P_lock`, and `P_seed` SHAs, command results,
  manifest counts, original-worktree status digest, deviations, and rollback point in the Phase 1
  completion record.

**What we know works:** every later probe and byte comparison has a closed, immutable input set.

**Rollback point:** `P_seed`. If a locked probe script, SysML/KerML source, or fixture-manifest byte
changes later, invalidate every verdict and restart Phase 1 with new `P_probe`, `P_lock`, and
`P_seed`; never amend the old commits. The live v6 batch manifest is a generated output expectation,
not a semantic model input to those gates. Its 4A/current transitions are reconciled separately in
Phase 6 without rewriting this lock or the Phase 2 verdicts.

---

## Phase 2: Run B2, B8a, and B10 pre-production kill gates

### Goal

Collapse the three design premises on real licensed SysIDE data before D1-D7 or any occurrence
production change. Verdict files land together in an independently green codegen commit.

### Assumption under test

The modeled containment address covers all seven required topology rows, real resolved facts are
leaf-total before D5, and exact document origin makes the B10 sole-glob branch unreachable.

### Test stencil — write first

```python
def test_gate_verdicts(verdicts):
    assert verdicts.b2.topology_rows == 7 and verdicts.b2.all_expected
    assert verdicts.b8.verdict == "REAL_CORPUS_TOTAL"
    assert verdicts.b8.total > 0 and verdicts.b8.feature_refs > 0
    assert verdicts.b8.feature_chains > 0 and verdicts.b8.missing_leaves == 0
    assert verdicts.b10.verdict == "DELETE_UNREACHABLE"
    assert verdicts.b10.documents >= 2 and min(verdicts.b10.unit_features_per_file) >= 1
```

### Changes required

- [x] Run all three retained scripts from clean `P_seed`, using SysIDE `0.8.4`, codegen production
  source from the frozen baseline, agentic `fcee56d6cee3828b6f3b7f29a9e684aa03b03bbb`, the closed
  manifest, and the verified `P_lock`.
- [x] **`verification/probes/b2-verdict.json` (NEW):** record all seven topology rows, live-element
  counts, stable IDs, owner kinds, expected address/domain results, `P_probe`, `P_lock`, source
  hashes, SysIDE version, and the measured verdict.
- [x] **`verification/probes/b8-real-verdict.json` (NEW):** record roots/hashes, total resolved facts,
  feature-reference facts, feature-chain facts, missing leaves, versions, commits, and
  `REAL_CORPUS_TOTAL` only when the defined counts pass.
- [x] **`verification/probes/b10-verdict.json` (NEW):** record exactly `DELETE_UNREACHABLE`, the two
  parser documents, per-file unit-bearing features, exact document URLs, live/admitted results,
  commits, versions, and hashes.
- [x] Commit the three verdicts and no occurrence production file. This commit is the green handoff
  to production work.

### Exact stop and return-to-design conditions

- [x] **B2:** “Any unsupported stable owner shape, unstable/cyclic walk, cross-outer result, split
  redefinition slot, unrelated writer, or nested no-prefix success kills this design before
  production.”
- [x] **B8a:** both reference-kind counts and the total must be nonzero; the only passing verdict is
  `REAL_CORPUS_TOTAL` with `missing_leaf_count == 0`. Any genuine resolved fact without a leaf kills
  the plan and returns to design before D1-D7 production changes.
- [x] **B10:** the one permitted measured verdict is `DELETE_UNREACHABLE`. If the measured result
  differs, production does not start and this design returns for revision.
- [x] A failed gate is not repaired, reclassified, or bypassed in the probe. Preserve the frozen
  outputs, write the measured contrary result, stop the implementation, and return to design.

### Validation

- [x] Run each probe twice from fresh processes and require byte-identical canonical JSON verdicts.
- [x] Recheck every Phase 1 hash before and after each run; probes are read-only outside their
  declared verdict output.
- [x] Assert no `src/sysml_codegen/**`, agentic source, or Fusion source changed in this phase.
- [x] Commit and immediately record the verdict commit SHA, exact counts/verdicts, commands,
  original-worktree status digest, deviations, and rollback point.

**Historical v3 probe-harness non-verdict:** B10 ran twice from fresh, clean v3 `P_seed` processes,
but both runs exited `1`
before producing a verdict. The locked probe calls `.as_posix()` on `SourceFile.referent` at
`b10_document_origin.py:64`; the production field is a `str`, so both runs raised the same
`AttributeError`. The stderr bytes match at SHA-256
`00bc73a152cad5749ad9692ae6301e73ef0373a66e1247d98de482caf73e098a`. No
`DELETE_UNREACHABLE` measurement exists. The corrected probe bytes invalidated that chain for
current evidence. Commit
`aac508fcb09735499e9d9df09bb00aeb8451b505` preserves both passing verdicts and the explicit B10
non-verdict failure record; it changes only the three `verification/probes/*.json` paths.

**What we know works:** the replacement chain measured B2
`CONTAINMENT_ADDRESS_FEASIBLE`, B8a `REAL_CORPUS_TOTAL`, and B10 `DELETE_UNREACHABLE` twice with
byte-identical output. The historical v3 B10 result remains a probe-harness non-verdict.

**Rollback point:** verdict commit `b9886ebcf77d143b9bafb936eac7a7db36262530`. The historical
failure-evidence commit `aac508fcb09735499e9d9df09bb00aeb8451b505` remains unchanged and is
not an input to the replacement gate run.

---

## Phase 3: Land the agentic semantic-evidence contract independently

### Goal

Implement B1-B5 and post-D5 B8b in agentic-mbse, publish the `0.1.3` API and guidance, and produce a
standalone slow-test-green, item-delta-clean source archive and wheel before codegen consumes it. See
[D5](design.md#d5-public-agentic-evidence-contract), [D6](design.md#d6-documenttier-owns-b5), and
[the agentic landing contract](design.md#agentic-semantic-contract).

### Assumption under test

Agentic can expose complete metatype, resolved-target, traversal, document-tier, and leaf evidence
through one backward-compatible typed public contract without taking ownership of codegen
occurrences.

### Test stencil — write first

```python
def test_missing_resolved_leaf_is_typed(real_fact_without_leaf):
    with pytest.raises(SemanticEvidenceError) as caught:
        extract(real_fact_without_leaf)
    assert caught.value.code is SemanticEvidenceCode.RESOLVED_LEAF_MISSING
    assert caught.value.reference and caught.value.location
    assert caught.value.detail.count(caught.value.code.value) == 0
    assert SEMANTIC_EVIDENCE_API_VERSION == "semantic-evidence/v1"
```

### Changes required

- [x] **`agentic-mbse::tests/test_adapter.py`, `tests/test_errors.py`,
  `tests/test_sysml/test_expression.py`, `test_constraint_extraction.py`,
  `test_public_api_exports.py`, and `test_package_version.py`:** write B1-B5/B8b positive and forced
  failure tests first, including cause chains, exact targets, total operands, real `DocumentTier`
  values, a project package named `SI`, missing/foreign tiers, and the explicit non-live mock path.
- [x] **`agentic-mbse::src/agentic_mbse/errors.py` and `__init__.py`:** add the closed error enum,
  typed public error, and `semantic-evidence/v1` version/export exactly as designed.
- [x] **`agentic-mbse::src/agentic_mbse/sysml/syside_adapter.py` and `sysml/__init__.py`:** propagate
  live metatype failures, add direct `document_tier`, and delete the obsolete prefix export.
- [x] **`agentic-mbse::src/agentic_mbse/sysml/expression.py` and
  `constraint_extraction.py`:** use mapped metatypes, materialize all operands, retain only exact
  resolved targets, fail a resolved leaf miss, and filter only exact `DocumentTier.StandardLibrary`.
- [x] **`agentic-mbse::pyproject.toml`, `src/agentic_mbse/__init__.py`, and `uv.lock`:** bump package
  version from `0.1.2` to `0.1.3` everywhere.
- [x] **`agentic-mbse::docs/patterns/plant-idiom.md`:** document supported bare, qualified,
  feature-chain, package, definition-domain, and plural shapes; state the context each requires;
  distinguish ill-formed refusal from the valid-but-unimplemented indexed form. Owner class is one
  input, not the whole derivation.

### Validation

- [ ] Run the complete fast suite and all focused semantic-evidence tests. Permit only the declared
  fast-suite skip, require targeted type/lint success for every changed path, and require full
  type/lint diagnostic sets no worse than their frozen-baseline captures. Do not run the retired
  PDF suite.
- [x] Run static searches proving no production class-name substring dispatch, swallowed operand
  iteration, staged name ladder, QN/path/origin library classifier, or obsolete prefix export
  remains.
- [ ] Commit the complete agentic change as `A_final`; the clean committed tree must pass again.
- [x] Build a deterministic `git archive` and `agentic_mbse-0.1.3` wheel from `A_final`, record their
  filenames and SHA-256 values outside codegen, and verify wheel metadata/import version/API value.
  Inject the separately declared corpus into the extracted source only after exact inventory/hash
  verification; the source archive itself must contain none of those ignored bytes.
- [x] Immediately record `A_final`, exact counts, commands, artifact hashes, skip report,
  original-worktree status digest, deviations, and rollback point.

**What we know works:** agentic independently supplies complete semantic evidence and one typed
failure API, including B8b, without a codegen checkout.

**Rollback point:** `A_final`. Codegen must pin a new independently green agentic descendant if this
phase later changes; never rebuild a different wheel under the old hash.

### Phase 3 causal baseline correction — 2026-08-17

The frozen-baseline extraction at `fcee56d6cee3828b6f3b7f29a9e684aa03b03bbb` was run with the
same main Python environment, installed dependency versions, and verified 16-file corpus as the
item. Only `tests/test_corpus_integration.py::test_ground_truth_scoring` was selected. It failed in
754.864 seconds with the exact item metric: `paischer_2025` detected/truth `62/23`, 170% error
against the unchanged 100% limit. Baseline JUnit SHA-256 is
`98d5d9babfc60c376b86a58d82878e4ae2419eef6afa718b2179dd486a4ca4e2`; item JUnit SHA-256 is
`8ce3ef15d74482db5121bcf172bdfb8a99fbcbd64bd4fb987d3bb050dd7f1201`.

The test source is unchanged at SHA-256
`a0ac0d96818639f8d67a11dcaae57a6c0876a719c1dee3156c8a393530a3f01c`; ground truth is unchanged
at SHA-256 `2a718e06efb76cd1ec9e30214d3ca75bdce2e7abcf80bd4803dbd1047ddabcc1`;
and the corpus aggregate is
`9ab1b4afe2d7af181b8d1979e1b8cf84c17edbc6824c142926e4f0dab14e80e6`. Baseline and item
canonical metric records are byte-identical at SHA-256
`76103f505add9e0951ed526a07789510de7373de2b8766d53e7a2a0673f75f54`.

This establishes a known pre-existing unrelated failure. It is not passed, skipped, waived, or
called green. The deterministic gate therefore requires the other 17 nodes to pass with zero skips
and requires this node's canonical metrics to remain byte-identical and no worse than baseline.
The threshold, ground truth, extraction code, and corpus were not changed. The complete causal
record is `/tmp/stop-parser.QVJIIP/artifacts/agentic-ground-truth-causal-v1.txt`, SHA-256
`5920877de695a81d3610dca2d6b13541af8d656561c08b923beb162ae80d2f14`.

---

## Phase 4: Adopt one codegen boundary and replace all scoped production fallbacks

### Goal

Consume the exact agentic artifact, migrate both public source arms to one conversion boundary, and
implement A1-A6 plus B6-B10 in the existing exact route. This phase uses three small green codegen
commits: boundary/pins, occurrence/producers, then metadata/preflight.

### Assumption under test

The approved private address/domain/index values are sufficient to replace every scoped election
without a second resolver, and every exact-evidence failure can reach one stable public refusal.

### Test stencil — write first

```python
@pytest.mark.parametrize("strict", [True, False])
@pytest.mark.parametrize("source_arm", ["live", "admitted"])
def test_evidence_failure_has_one_public_bridge(source_arm, strict):
    error = call_public_arm_with_missing_evidence(source_arm, strict)
    assert error.code == "SI_EVIDENCE_INCOMPLETE"
    assert error.message.count(error.code) == 1
    assert error.reference and error.root_relative_location
    assert no_graph_snapshot_or_output_was_created()
```

### Changes required

**Commit 4A — dependency pins and public bridge**

- [x] **`tests/conformance/test_upstream_pins.py`, `tests/unit/test_package_metadata.py`, and a new
  `tests/conformance/test_expression_evidence_integrity.py`:** first pin agentic/codegen versions,
  API version, cause conversion, exact location/reference, strict/lenient parity, live/admitted
  parity, one code token, and no partial graph/snapshot/output.
- [x] **`src/sysml_codegen/_upstream_pins.py`, `pyproject.toml`, `src/sysml_codegen/__init__.py`, and
  `uv.lock`:** require `agentic-mbse>=0.1.3,<0.2`, pin `0.1.3` and `semantic-evidence/v1`, bump
  codegen to `0.1.1`, and refresh package metadata/lock.
- [x] **`src/sysml_codegen/orchestration/elaborated_pipeline.py`,
  `elaboration/elaborate.py`, and `elaboration/__init__.py`:** replace the old public two-stage call
  atomically with `elaborate_loaded_extractor`; keep the raw graph builder private; route live,
  admitted-source, and snapshot capture through one conversion. Do not add a compatibility overload.
- [x] Run the targeted boundary/pin tests, full default suite, mypy, and ruff; commit 4A only when
  independently green against `A_final`.

**Commit 4B — D1-D4 occurrence and calculation ownership**

- [x] **`tests/unit/test_elaboration_occurrence.py`, `test_constraint_attachment_cause.py`,
  `test_elaboration_import_boundaries.py`, and new focused address/producer tests:** write exact
  owner acquisition, containment-local validation, address instantiation, producer-index,
  multiplicity-writer, redefinition identity, and static no-fallback tests first.
- [x] **`src/sysml_codegen/elaboration/occurrence.py`:** implement the one general semantic-owner
  selector, containment address/domain, indexed child/root maps, exact multiplicity ownership, and
  strict redefinition family rules from [D1/D2/D4](design.md#d1-one-general-semantic-owner-selector).
- [x] **`src/sysml_codegen/elaboration/elaborate.py`:** build the contextual calculation-output
  producer index and route A1-A4/A6 consumers through the single existing occurrence address
  resolver. Delete nearest, descendant-count, model-root fallback, sole-candidate, graph-wide output
  scan, and model-wide multiplicity-writer arms in the same commit.
- [ ] Add the A5 pre-graph `SI_INDEXED_SOURCE_UNSUPPORTED` refusal without implementing indexing.
- [x] Run the focused occurrence/producer suite, full default suite, mypy, ruff, and static removal
  checks; commit 4B only when independently green.

**Commit 4C — B6/B7/B9/B10 consumers and preflight**

- [x] **`tests/conformance/test_feature_typing_integrity.py`, occurrence/redefinition tests, and
  `test_generation_exit_type_preflight.py`:** write exact-type, stable-redefinition, and public
  fail-before-mutate cases first.
- [x] **`src/sysml_codegen/extraction/extractor.py`:** accept one supported exact qualified typing;
  refuse missing, multiple, user-defined lookalike, and unsupported types as `SI_TYPE_INVALID`.
- [x] **`src/sysml_codegen/extraction/feature_metadata.py`:** after the B10 verdict, delete the
  sole-glob fallback and add no replacement classifier or search.
- [ ] **`src/sysml_codegen/cli/__init__.py` and `generation/registry.py`:** add the
  `EXIT_POINT_TYPE_UNSUPPORTED` preflight before links, rendering, output clearing, directory
  creation, or writes; delete the warning/omit branch.
- [x] Run all B-focused tests, the public B9 status/log/byte-preservation proof, full default suite,
  mypy, ruff, and static removal checks; commit 4C only when independently green.

### Validation

- [ ] Prove every public elaboration caller uses the one loaded-extractor boundary and every A-row
  consumer reaches the one occurrence address resolver. No flag, registry, strategy object,
  compatibility layer, alternate resolver, or fallback architecture exists. Audit remediation at
  `cafd4cb52c1251eec5b94f23673b246d3514a444` removed the last inert B10 interface residue and
  narrowed the occurrence identity boundary; the licensed 119-test matrix and static contract
  checks recorded under replacement Phase 7 prove the closed path.
- [ ] Prove B1-B8 evidence/type/identity failures are identical under strict and lenient modes and
  produce no graph or snapshot.
- [ ] Prove B9 returns status `1`, names token/module/output/type/source exactly once, and preserves
  the complete pre-existing output path-to-bytes map.
- [x] Immediately record each subcommit SHA, commands/counts, removal-search results,
  original-worktree status digest, deviations, and rollback point.

**What we know works:** all scoped production consumers use parser evidence plus one exact occurrence
route, and every scoped failure is public and fail-closed.

**Rollback point:** commit 4C. Fix a later defect in its owning production commit sequence; never
reenable a removed fallback to make a test pass.

---

## Phase 5: Prove real SysIDE semantics and public TEAx mutation behavior

### Goal

Complete the real fixture matrices and prove live/snapshot parity, public strict/lenient refusals,
fail-before-mutate behavior, and off-default every-and-only mutations. Internal graph assertions are
diagnostic support, not acceptance evidence. See [test design](design.md#test-design).

### Assumption under test

The internal exact-route changes survive every public boundary and emit the intended runtime math,
including repeated occurrences and calculation-output producers.

### Test stencil — write first

```python
@pytest.mark.execution
@pytest.mark.parametrize("case", POSITIVE_A1_A4_A6_CASES)
def test_modeled_source_mutates_every_and_only_its_consumers(case):
    live, snapshot = generate_both_public_routes(case.model)
    assert live.package_bytes == snapshot.package_bytes
    before, after = execute_default_and_one_input_mutation(live, case)
    assert movers(before, after) == case.expected_consumers
    assert case.source_public_input_count == 1
    assert no_extra_graph_edge(case.source_identity)
```

### Changes required

- [x] **`tests/conformance/test_occurrence_domain_derivation.py` (NEW):** cover same/nested domain,
  repeated outer, direct package no-prefix, nested explicit-prefix success/no-prefix refusal,
  unrelated target, ambiguity, plural expansion, redefinition slot, and reversed declaration/file
  order using the frozen real fixture.
- [x] **`tests/conformance/test_occurrence_calc_domain_derivation.py` (NEW):** inspect exact producer
  buckets and public outcomes for sibling, explicitly rooted sibling, repeated outer, package, alias,
  and unrelated sole calculation producers.
- [x] **`tests/conformance/test_occurrence_multiplicity_authority.py` (NEW):** prove root/nested exact
  writers and refuse unrelated, incomparable, ambiguous, or unsupported finite shapes.
- [x] Expand **`tests/conformance/test_definition_owned_reference_positions.py`** for local lineage,
  one descendant, several descendants, and sibling subtree outcomes.
- [ ] Complete **`test_expression_evidence_integrity.py`, `test_feature_typing_integrity.py`, and
  `test_generation_exit_type_preflight.py`** with all real positive tiers/types and forced failures
  required by B1-B9.
- [x] **`tests/execution/test_occurrence_derivation_mutation_teax.py` (NEW):** parameterize every
  positive A1-A4/A6 topology, including calculation outputs. Generate live and v6 snapshot packages,
  require byte parity, mutate exactly one public input off default, and compare all outputs and
  constraint responses.
- [x] Update only expected snapshots/generated fixtures named by an
  `expected-transitions.md` row. A changed byte without a row and proving test is a failure.

### Validation

- [x] Run all new conformance files with the SysIDE license and require zero skips.
- [x] Run the full codegen default suite, mypy, and ruff immediately after the conformance matrix.
- [x] Run `tests/execution/test_occurrence_derivation_mutation_teax.py` alone in a fresh process with
  real TEAx, explicit artifact-provenance inputs, and zero skips. Require every intended output to
  move, every sibling/unrelated output to remain unchanged, repeated occurrence `i` to affect only
  `i`, one public source token, and no extra graph edge. The complete execution marker lane remains
  a clean-commit gate in Phases 7 and 9.
- [x] Regenerate every successful baseline through live and snapshot routes; require byte parity.
  For all non-transition rows, require exact equality with Phase 1 hashes.
- [x] Commit the complete public-proof matrix as an independently green codegen commit and
  immediately record its SHA, anti-vacuity counts, suite counts, skip report, original-worktree
  status digest, deviations, and rollback point.

**What we know works:** the modeled source reaches exactly its public runtime consumers on every
supported route, while incomplete authority refuses before mutation.

**Rollback point:** the Phase 5 matrix commit. A failing public proof returns to the owning Phase 4
production code; do not weaken the matrix or expected mover set.

---

## Phase 6: Reconcile outputs, docs, product state, backlog, and ledgers

### Goal

Make the shipped contract and tracked status match the green production behavior before naming
`C_prod`. This phase prepares the historical ledger rows but does not create the evidence-only file
before `F_final`. See [documentation obligations](design.md#documentation-and-backlog-obligations)
and [historical ledger](design.md#historical-census-reconciliation-ledger).

### Assumption under test

Every intended behavior change is named once, every historical row has a durable disposition, and
no public or project document still teaches a removed fallback or warning.

### Test stencil — write first

```python
def test_reconciliation_is_total(records, transitions, docs):
    assert set(records.historical_ids) == {"L-01", ..., "L-14", "U-1", "U-2"}
    assert every_changed_baseline_byte_has_one_transition(transitions)
    assert docs.req_reg_09.names_fail_before_mutate_test
    assert backlog.has("INDEXED-ELEMENT-EXPRESSION-SUPPORT")
    assert backlog.has("OUTPUT-ALIAS-DUPLICATE-SOURCE-SILENCE")
    assert product_status_preserves_owner_verbatim_text()
```

### Changes required

- [x] **`docs/architecture/overview.md` and reference docs `00`, `01`, and `19`:** document the one
  owner walk, containment address, producer index, conversion boundary, exact typing/evidence, and
  named refusals; link to active code/tests rather than restating private signatures.
- [x] **`docs/architecture/reference/20-module-registry-generation.md`:** replace REQ-REG-09's warning
  contract with refusal before output mutation, including token, identity, location, status, and
  byte-preservation proof.
- [x] **`docs/architecture/verification-matrix.md`:** replace the old hygiene test for REQ-REG-09
  with `tests/conformance/test_generation_exit_type_preflight.py`; mark PASS only after the entire
  public proof passes.
- [x] **`docs/architecture/reference/30-diagnostic-severity.md` and any indexed active diagnostic
  reference it delegates to:** update the reference for
  `SI_EVIDENCE_INCOMPLETE`, `SI_TYPE_INVALID`, `SI_INDEXED_SOURCE_UNSUPPORTED`, and
  `EXIT_POINT_TYPE_UNSUPPORTED` with ownership and refusal stage.
- [x] **`verification/expected-transitions.md`:** finalize each seeded row with exact old/new hashes,
  graph/diagnostic differences, proving test IDs, and implementation commit. Prove every other
  maintained output is byte-identical.
- [x] **Private evidence staging, not the codegen tree:** prepare the complete L-01-L-14/U-1-U-2
  reconciliation rows with exact test IDs and commits. Phase 10 writes them to the reserved
  `verification/reconciliation-ledger.md` path after `F_final`; writing that path now would violate
  the approved six-path evidence boundary.
- [x] **`verification/build_artifacts.py`, `run_independent_green.py`, and `audit_evidence.py`
  (NEW):** implement the fixed entry points above for deterministic archives/wheels, isolated suite
  execution, import/skip capture, and the four final evidence checks. They accept full SHAs as
  inputs; they never discover identity from a branch name or adjacent checkout.
- [x] **`tests/conformance/test_evidence_artifact_topology.py` (NEW):** test the three runner CLIs on
  temporary Git repositories and fixture artifacts, including dirty source, wrong parent, seventh
  changed path, self-reference, wrong wheel version/hash, sibling import, unexpected skip, and the
  passing six-path case.
- [x] **`.project/backlog/BACKLOG.md`:** add separate agent-grade rows
  `[INDEXED-ELEMENT-EXPRESSION-SUPPORT]` under P-001 and
  `[OUTPUT-ALIAS-DUPLICATE-SOURCE-SILENCE]`. The first records valid indexed expressions as not yet
  implemented. The second records that a second authored alias currently produces no file and no
  diagnostic. Preserve their source force and do not mark either settled.
- [x] **`.project/product/P-003-no-workarounds-for-bad-models.md`:** reconcile only the agent-written
  first-application status so A3 is described as refusing every definition-owned lineage miss.
  Preserve the owner-verbatim promise unchanged. Check P-002 and P-004 against the shipped result;
  update only their agent-written implementation/evidence status if it is stale, never their
  promise, grade, or owner payload. Update `.project/product/INDEX.md` only as needed to keep the
  active status reachable; do not mint an ADR.
- [x] **`.project/backlog/epic_elaborate_first_architecture.md` and `.project/CURRENT_WORK.md`:**
  replace stale predecessor wording with the actual descendants and record implementation status,
  the ongoing block on `elaborator-downstream`, and the later fresh-audit requirement.

### Validation

- [x] Run the doc/matrix/backlog/reconciliation contract tests first, then the full codegen default
  suite, mypy, ruff, and execution lane.
- [x] Search active docs for the retired nearest/sole/descendant/model-root/glob/type/warning claims;
  every hit must be historical context, a test assertion, or a rejected alternative.
- [x] Recompute every baseline output and transition mapping. Require one transition owner for every
  changed byte and no transition entry for an unchanged byte.
- [x] Commit the docs/status/transition changes as an independently green codegen candidate. Record
  its full SHA as `C_candidate`, not yet as `C_prod`.
- [x] Immediately record exact doc rows, backlog tags, ledger coverage, commands/counts, skip report,
  original-worktree status digest, deviations, and rollback point.

**What we know works:** production behavior, public guidance, matrix truth, product status, backlog
ownership, and transition accounting agree.

**Rollback point:** `C_candidate`. A reconciliation failure changes the owning production/doc commit
and creates a new candidate; it is never deferred to `C_evidence`.

---

## Phase 7: Name `C_prod`, then build and hash its source and wheel

### Goal

Establish the complete, sole codegen production identity only after every production file is green,
then build its deterministic source archive and `0.1.1` wheel. See
[acyclic topology](design.md#acyclic-production-and-evidence-topology).

### Assumption under test

`C_candidate` contains every source, test, fixture, public doc, package version, dependency minimum,
pin, lock, probe verdict, baseline, and expected-transition file needed to build, consume, and test
codegen, while containing none of the six final evidence-only files.

### Test stencil — write first

```python
def test_c_prod_boundary(tree):
    assert tree.production_contract_is_complete()
    assert tree.package_version == "0.1.1"
    assert tree.agentic_pin == ("0.1.3", "semantic-evidence/v1")
    assert tree.final_evidence_paths_present == set()
    assert tree.all_production_suites_green
    assert tree.worktree_is_clean
```

### Changes required

- [ ] From a fresh clean checkout of `C_candidate`, rerun the full licensed default suite, every new
  conformance matrix, the complete execution lane, mypy, ruff, static removals, output reconciliation,
  package metadata, pins, and lock checks.
- [x] Require all Phase 1/2 production-side verification files and retained probes/tests to exist;
  require all six `C_evidence`-only paths to be absent.
- [ ] Only after every command is green, set `C_prod` to the full `C_candidate` SHA and make that
  immutable identity the input to all later builds. No codegen commit may occur between `C_prod`
  designation and `C_evidence`.
- [x] Build `sysml-codegen-C_prod.tar` with deterministic `git archive` prefix and build
  `sysml_codegen-0.1.1` with `SOURCE_DATE_EPOCH` fixed from `C_prod`. Hash both with SHA-256 into the
  private artifact-build record.
- [x] Extract the archive fresh, rebuild the wheel, and require filename, metadata version, contents,
  and SHA-256 to match. Reject imports outside the extraction/install roots.

### Validation

- [x] Verify the certified tuple exactly: `(C_prod full SHA, C_prod source-archive SHA-256,
  sysml_codegen-0.1.1 wheel filename and SHA-256)`.
- [x] Verify `git status --porcelain=v1` is empty and `git rev-parse HEAD` equals `C_prod` for every
  production command and build.
- [x] Verify no codegen/Fusion evidence cites an editable sibling, and no downstream input contains
  or anticipates `C_evidence`.
- [x] Immediately record `C_prod`, all suite counts, skip report, artifact commands/hashes, import
  roots, original-worktree status digest, deviations, and rollback point.

**What we know works:** one immutable codegen production identity is complete, independently green,
and reproducibly buildable.

**Rollback point:** `C_prod`. Any later production defect invalidates its artifacts and all dependent
Fusion/evidence work; fix the owning production repository and repeat from a new `C_prod`.

---

## Phase 8: Pin Fusion to immutable artifacts and land `F_final`

### Goal

Make the clean Fusion descendant consume immutable agentic `A_final`, codegen `C_prod`, and frozen
1costingfe identities, validate the real customer models, and execute the complete generated TEAx
package before landing `F_final`. See
[Fusion dependency and lock changes](design.md#fusion-dependency-and-lock-changes).

### Assumption under test

The final occurrence/evidence rules accept the Fusion models as authored and need no model rewrite;
the only mandatory Fusion source changes are dependency pins, lock, and kept verification tests.

### Test stencil — write first

```python
def test_fusion_uses_immutable_production_artifacts(lock, generated_run):
    assert lock.agentic == ("0.1.3", A_FINAL)
    assert lock.codegen == ("0.1.1", C_PROD)
    assert lock.costingfe == ("0.1.0", COSTINGFE_COMMIT)
    assert not lock.has_editable_or_sibling_path_sources()
    assert generated_run.live_bytes == generated_run.snapshot_bytes
    assert generated_run.executed_with_real_teax
```

### Changes required

- [x] Start from a clean dedicated Fusion worktree at
  `824a876e281a3b9aef58b1873bfbd0b20c4ab77b`; do not use or clean the existing dirty Fusion
  checkout.
- [x] **`fusion-tea::tests/test_dependency_provenance.py` (NEW):** first reject editable/path sources,
  partial SHAs, wrong package/API versions, `C_evidence`, and lock/project disagreement.
- [x] **`fusion-tea::tests/test_codegen_teax_acceptance.py` and
  `tests/test_occurrence_mutation_teax.py` (NEW):** prove public live and snapshot generation,
  package seal/load, registry discovery, full real-TEAx execution, output/channel identity, and
  every-and-only mutation behavior against the actual `models/` tree.
- [x] **`fusion-tea::pyproject.toml`:** pin `agentic-mbse[extract-full,web]==0.1.3`,
  `sysml-codegen==0.1.1`, and `1costingfe==0.1.0`; replace the three editable sibling sources with
  immutable Git URLs/revs for `A_final`, `C_prod`, and the frozen 1costingfe SHA.
- [x] **`fusion-tea::uv.lock`:** regenerate and require precise immutable Git source URLs and commits
  for all three packages. Run `uv lock --check` from the later source archive.
- [x] **`fusion-tea::models/**`:** make no edit unless the immutable-stack model validation or
  public generated execution proves a real semantic violation. If it does, record the exact
  diagnostic/reference/file/line and standard/parser rule, make the smallest model correction, and
  rerun all validation and generation. A dependency or harness problem is not a model violation.

### Validation

- [x] Install only the recorded agentic/codegen/1costingfe wheels in a fresh environment. Assert
  import files and wheel hashes before running Fusion.
- [x] Run the exact Fusion lock, full pytest, complete model validation, generated-execution,
  mutation, ruff, and mypy commands from the validation contract with no unexpected skips.
- [x] Prove the generated package uses real TEAx from the frozen extracted TEAx source, not a stub,
  wrapper, sibling checkout, or manual input fallback.
- [x] Commit all required Fusion pins/lock/tests and any proven model correction as `F_final`; rerun
  from the clean committed tree.
- [x] Build and hash a deterministic Fusion source archive from `F_final`. Immediately record
  `F_final`, model diff/no-diff verdict, exact suite counts, skip report, import roots, artifact hash,
  original-worktree status digest, deviations, and rollback point.

**What we know works:** the customer repository pins only immutable production artifacts and its real
models generate and execute fully under the final rules.

**Rollback point:** `F_final`. A Fusion failure changes Fusion and creates a new `F_final`; a codegen
or agentic failure invalidates `C_prod`/`A_final` and restarts their dependent phases.

---

## Phase 9: Run the five-input isolated battery and stage final evidence

### Goal

Rebuild, install, and test agentic, codegen, TEAx, 1costingfe, and Fusion only from their recorded
archives/wheels. Produce the six final evidence files in a private staging directory, not yet in the
codegen repository. See [required isolated runs](design.md#required-isolated-runs).

### Assumption under test

The result is reproducible without sibling source checkouts, editable installs, hidden path imports,
network resolution during the composed run, omitted slow/license/execution tests, or undeclared
skips.

### Test stencil — write first

```python
def test_independent_green(report, dependencies):
    assert report.input_repositories == FIVE_FROZEN_INPUTS
    assert all(run.status == 0 for run in report.runs)
    assert all(run.unexpected_skips == [] for run in report.runs)
    assert all(import_is_under_recorded_root(p) for p in report.import_files)
    assert report.codegen_identity.commit == C_PROD
    assert report.fusion_identity.commit == F_FINAL
```

### Changes required

- [x] Use `C_prod`'s retained artifact runner/checks to create deterministic source archives for all
  five repositories. Recompute and require the design-pinned TEAx and 1costingfe source-tar hashes;
  record repository URL, full SHA, version, archive filename/hash, and wheel filename/hash where
  applicable.
- [x] Run the exact `verification/build_artifacts.py` command from the artifact/audit contract with
  the recorded full identities and a new empty private artifact root.
- [x] Build a complete transitive wheelhouse and hash-pinned requirements file. Install with
  `--no-index`, `--find-links`, and `--require-hashes`; record `pip freeze` and reject any unresolved
  or editable source.
- [ ] From extracted Agentic, run exactly `uv run pytest tests/ -m "not slow"`, `uv run mypy src/`,
  and `uv run ruff check src/ tests/` with the exported license only. Run the focused parser-evidence
  tests if the broad selection does not include them. Require only the declared fast skip and no
  sibling import. Do not run the retired PDF suite.
- [x] From extracted 1costingfe, run its full pytest and configured ruff command. From extracted TEAx,
  run the root-configured simkit and battery-demo suites.
- [x] From extracted `C_prod`, run the licensed default suite, all new real-model/snapshot/generated
  package tests, mypy, ruff, and the complete execution marker lane using explicit provenance and
  extracted TEAx.
- [x] From extracted `F_final`, run `uv lock --check`, the full configured pytest suite, complete
  model validation, and the final generated Fusion/TEAx execution/mutation proofs with installed
  agentic/codegen/1costingfe wheels.
- [ ] Validate the retained exact immutable-artifact measurements with `C_prod`'s
  `verification/run_independent_green.py` schemas and checks, and generate the final staged report
  from those recorded measurements. Do not hand-edit a count, status, import root, skip record, or
  artifact identity. This is the later orchestration-approved replacement for rerunning already
  valid Phase 7/8 suites; Phase 9 ran its one missing Agentic semantic command directly.
- [x] Stage exactly these final files outside the codegen tree:
  `dependencies.json`, `wheelhouse-requirements.txt`, `execution-provenance.json`,
  `independent-green.json`, `reconciliation-ledger.md`, and `evidence-lock.json`.
- [x] Fill the historical reconciliation ledger with all L-01-L-14/U-1-U-2 rows, exact test IDs and
  implementation commits. Its codegen production row names `C_prod`, never `C_evidence`.
- [x] Hash all five sibling evidence files plus production-side `probe-fixture-lock.json` and
  `expected-transitions.md` into `evidence-lock.json`; do not hash the lock itself. The other five
  files do not name/hash the lock or `C_evidence`.

### Validation

- [ ] Require every source/archive/commit and wheel/version/hash relation to recompute, every import
  to resolve under a recorded extraction/install root, and every suite to satisfy its declared
  skip allow-list.
- [x] Require the Fusion installed codegen wheel hash to equal the certified `C_prod` wheel and its
  project/lock rev to equal full `C_prod` exactly.
- [x] Run evidence-schema, hash-coverage, no-self-reference, no-sibling-path, and reconciliation
  totality checks against the staged files.
- [x] Immediately record exact commands/counts/statuses/skips, staging file hashes, import roots,
  original-worktree status digests, deviations, and rollback point. Do not commit codegen yet.

**What we know works:** the declared immutable artifact set reproduces the recorded five-repository
results under the approved baseline-delta contracts. Passing lanes, known baseline failures and
skips, validator findings, and unrun external-service tests retain the exact classifications and
measurements recorded above; neither every repository nor the composed product is globally green.

**Rollback point:** the Phase 9 private evidence staging set. Any failure returns to the repository
that owns it, creates a new `A_final`, `C_prod`, or `F_final` as needed, and reruns all dependent
artifact evidence. Never patch a production failure in evidence.

---

## Phase 10: Create direct-child six-path `C_evidence` and audit the boundary

### Goal

Land the final evidence as a direct evidence-only child of `C_prod`, then mechanically prove the
parent, changed-path, artifact, lock, and independent-green contracts.

### Assumption under test

All cross-repository facts can be recorded without changing production identity, creating a
self-reference, or allowing a downstream repository to pin the evidence commit.

### Test stencil — write first

```python
def test_evidence_commit_boundary(git, c_prod, c_evidence, f_final):
    assert git.parent(c_evidence) == c_prod
    assert git.changed_paths(c_prod, c_evidence) == EXACT_SIX_PATHS
    assert evidence.codegen_commit == c_prod
    assert evidence.fusion_commit == f_final
    assert c_evidence not in all_evidence_text
    assert all_locked_hashes_recompute()
```

### Changes required

- [x] Create a fresh clean codegen worktree at exact `C_prod`; verify `HEAD == C_prod`, the tree is
  clean, and no codegen commit followed `C_prod`.
- [x] Copy the staged evidence to exactly these paths and no others:

  1. `verification/dependencies.json`
  2. `verification/wheelhouse-requirements.txt`
  3. `verification/execution-provenance.json`
  4. `verification/independent-green.json`
  5. `verification/reconciliation-ledger.md`
  6. `verification/evidence-lock.json`

- [x] Validate all six files before committing. Commit only those six paths as `C_evidence`; do not
  build or certify an archive or wheel from `C_evidence`.
- [x] Assert no Fusion or other downstream ref, project file, or lock names `C_evidence`.

### Validation

**Exact audit commands and checks:**

- [x] **Parent/path boundary:** run
  `git rev-parse C_evidence^`, compare it byte-for-byte with full `C_prod`, then run
  `git diff --name-only C_prod..C_evidence` and require set equality with the six paths above.
- [x] **Codegen reconstruction:** check out/extract `C_prod`, rebuild its source archive and wheel
  with the recorded commands, and require exact filenames/hashes from `dependencies.json`. Require
  the codegen row to name `C_prod`, and search all six files for absence of `C_evidence`.
- [x] **Fusion pin proof:** inspect `F_final:pyproject.toml` and `F_final:uv.lock`; require full
  `C_prod`, reject `C_evidence`, `editable =`, sibling `path =`, and partial SHAs; require the Fusion
  run's installed codegen wheel hash to equal the rebuilt `C_prod` wheel.
- [ ] **Artifact/lock proof:** recompute every source archive, wheel, wheelhouse, requirements,
  production-side record, and five sibling evidence-file digest. Require the lock not to hash itself
  and the independent-green report to contain command, import-root, status, count, and
  no-unexpected-skip records for every required run.
- [x] Rerun the kept evidence-boundary tests from `C_prod`, supplying `C_prod`, `F_final`, and
  `C_evidence` as external command inputs. The test code must come from `C_prod`, not `C_evidence`.
- [x] Run the exact `verification/audit_evidence.py` command from the artifact/audit contract and
  require exit status `0`; its four named check groups must each report PASS.
- [x] Immediately record `C_evidence`, the four audit results, exact changed paths, recomputed hashes,
  original-worktree status digests, deviations, and rollback point.

**What we know works:** the final evidence is acyclic, complete, mechanically reconstructable, and
strictly outside the certified codegen production identity.

**Rollback point:** `C_evidence`. An evidence transcription error creates a new direct child of the
same `C_prod` only after discarding the unaccepted evidence candidate. A production result change
requires new production identities and a complete dependent rerun.

---

## Phase Completion Record Template

Fill the corresponding block immediately after each phase; do not batch these notes at the end.

### Phase 1 completion

- [x] Completed timestamp: `2026-08-17T00:30:02-07:00`.
- [x] Green commits (`P_probe`, `P_lock`, `P_seed`):
  `20f9e60a19b30bc1ec9a27aacb08380f4bc45602`,
  `43edf9bde4db44e7973458ada732d2cd75e764f6`, and
  `52a03cd2d0a9fdd340b60b16cea79a5b72234b08`. Their parent chain ends at frozen baseline
  `7b29d8b636e284364a4fdce9079f153c51c867ea`; `P_probe` changes 14 closed paths, `P_lock`
  changes only `verification/probe-fixture-lock.json`, and no `src/**` byte changes.
- [x] Commands, counts, and hashes: retained probe contracts `4 passed`, with collected/selected/
  passed `4/4/4` and failed/skipped/xfailed/deselected `0/0/0/0`; `capture_baseline.py --check`
  PASS; 118 locked files; manifest counts `37` canonical roots (`15` graph, `22` typed refusal),
  six added roots, seven added source files, and 43 total roots. SHA-256: canonical batch
  `bd7bf245e3ca3923b9b5d41db97861c9fcdf64435e768d48a2d7027eb52d9288`; manifest
  `96dcd3d652a1183168145a05fba3382f560814c4911c9c9cd0be551b70f02009`; lock
  `39e42e3568ae2ef922e07d9d58a6029efb31ea01e2fea3ff864bfe05dd43aa3d`; baseline
  `922b0918ae025d75f2be9e9446af0ed93f79d1052f1050612da8ce1e7135241f`; transition seed
  `291a37d2db8e7f30c2859cb5ebf9705252dec196f509b4eb4c9a1d21227a9c95`.
- [x] Issues and deviations: the final before-state has 19 graph and 24 typed-refusal root outcomes.
  The two added-root refusals are `indexed_expression_source` (`ElaborationError`) and
  `occurrence_domain_derivation` (`ElaborationDiagnosticError`); the other 22 are the pinned
  canonical refusals. Of the 19 graph outcomes, 15 generate with live/snapshot byte parity and four
  retain measured generation refusals: `constraint_inline`, `constraint_non_numerical`, and
  `unresolvable_attr_probe` return false at the public generator, while
  `occurrence_calc_domain_derivation` raises `SnapshotCertifiabilityError`. Eleven generated
  packages execute and carry output hashes; `modeled_default_fidelity`, `retype_model`,
  `sample_model`, and `feature_typing_integrity` retain measured TEAx `ValidationError` execution
  refusals. The v3 chain (`P_probe` `2007ba165092062260eca4e63c50bfb3082dfc84`, `P_lock`
  `22a49bead04d89f478743c4fa9be16d3e13cc1d9`, `P_seed`
  `8066fc2ab72b11abf8845b941a402a024684af21`) and failure-evidence commit
  `aac508fcb09735499e9d9df09bb00aeb8451b505` remain unchanged as historical evidence. That chain
  is superseded because its B10 probe called a `Path`-only method on the production string referent
  and therefore produced no semantic verdict. Two still-earlier Phase 1 candidates also remain
  preserved outside the evidence branch: the first stopped when generation refusal was not
  representable; the second stored graph/identity hashes without the required graph bytes,
  identity rows, and runtime-output hashes. No superseded commit is an evidence input.
- [x] Original-worktree digest unchanged; rollback point recorded: `git status --porcelain=v1
  -uall` remains `55fb5f1be6a5ad124665e73d23c1e61e301326679b6a21e9a23166c9ef35e8f3`;
  rollback point is `P_seed` `52a03cd2d0a9fdd340b60b16cea79a5b72234b08`.

### Phase 2 completion

- [x] Completed timestamp and verdict commit: `2026-08-17T00:33:45-07:00`;
  `b9886ebcf77d143b9bafb936eac7a7db36262530` is a direct child of replacement `P_seed`
  `52a03cd2d0a9fdd340b60b16cea79a5b72234b08` and changes exactly the three verdict paths.
- [x] B2/B8a/B10 verdicts and anti-vacuity counts: B2 `CONTAINMENT_ADDRESS_FEASIBLE`, seven rows,
  `all_expected=true`, 102 live elements; B8a `REAL_CORPUS_TOTAL`, 43 roots, 4,481 total resolved
  facts, 3,483 feature-reference facts, 998 feature-chain facts, and zero missing leaves; B10
  `DELETE_UNREACHABLE`, two parser documents, and one unit-bearing feature in each source file.
- [x] Commands and results: every gate was invoked twice from fresh processes. B2 outputs were
  byte-identical at SHA-256 `13d0de0838d06d27f8ab33add4deeedca19c28876d53fc75d59bbf0f20ab2813`
  with exits `0/0`; B8a outputs were byte-identical at SHA-256
  `b2175966c9505f08ae98fd25e90df967d6570b3a2d3b75f339c4b77c4a927897` with exits `0/0`; B10
  outputs were byte-identical at SHA-256
  `573b7de1ee13d7fe337126dea696dfb34a103a108cb2e3ac870077679b89ac82` with exits `0/0`.
  Phase 1 hashes were rechecked before and after every process. Committed verdict SHA-256 values are
  B2 `ecdc842e95612c5442cf798e92147316fa9af0c77d4932419dfe1d192c9edfa3`, B8a
  `05acf8549201a169e77522ffc121e1ad3870ab0c122696253ea15be61c7a3fd7`, and B10
  `122d50520a7e13a989f6defd763f64b3bf6c84141413c22b8d27128627d1eaca`.
- [x] Issues and deviations: the v3 B10 `AttributeError` was a harness defect and produced no
  semantic verdict. The complete v3 chain through `aac508fcb09735499e9d9df09bb00aeb8451b505`
  remains unchanged as historical evidence. The replacement run used no v3 verdict file and made
  no production-source change.
- [x] Original-worktree digest unchanged; rollback point recorded: `git status --porcelain=v1
  -uall` remains `55fb5f1be6a5ad124665e73d23c1e61e301326679b6a21e9a23166c9ef35e8f3`;
  rollback point is `b9886ebcf77d143b9bafb936eac7a7db36262530`.

### Phase 3 completion

- [x] Completed timestamp and `A_final`: `2026-08-17T03:15:21-07:00`;
  `1804827cb2cc877b3c0bc74309bd3470fb2ee90b`, a direct descendant of frozen agentic parent
  `fcee56d6cee3828b6f3b7f29a9e684aa03b03bbb`. The commit publishes package `0.1.3`, API
  `semantic-evidence/v1`, the seven-member public error enum, B1-B5/B8b behavior, tests, the real
  project-`SI` fixture, lock, and guidance.
- [x] Commands, counts, skips, archive/wheel hashes: focused committed-tree and extracted-source
  selections each passed `150/150` with zero failures/skips. The complete fast suite collected
  `1,892`, selected `1,859`, passed `1,858`, skipped only
  `tests/test_sysml/test_adr002.py::test_real_model_expose_patterns_exempt` for exact reason
  `Requires fusion_modeling CATF models not in this repo`, and deselected the 33 slow nodes. The
  deterministic local selection collected `1,892`, selected `18`, passed the 17 non-baseline nodes,
  skipped zero, and retained the one causal-baseline aggregate failure described below; the 15
  network-backed Claude/API nodes were unrun external-service tests, not passed, skipped, green, or
  required evidence. Targeted mypy passed all six changed production modules; full mypy improved
  from 95 frozen-baseline diagnostics in 20 files to 91 in 19 files with an empty item-only set.
  Targeted Ruff passed every changed Python path; full Ruff improved from 121 baseline findings to
  119 with an empty item-only set. Static removal, package/version/API, two packaged-guidance tests,
  and offline `uv lock --check` passed. Deterministic artifacts are
  `agentic-mbse-1804827cb2cc877b3c0bc74309bd3470fb2ee90b.tar` at SHA-256
  `c6a530e3ccd91bdb005b44bb193066e1f7517288331b4bd485be00d8fdebbd6b` and
  `agentic_mbse-0.1.3-py3-none-any.whl` at SHA-256
  `4d6c29aa0695ca65eb72779bc46b8fc3973bf1c27bbc28c44aa89cab0b4ea95c`; each pair of builds was
  byte-identical. The source archive contained zero ignored corpus bytes. Exactly 16 declared files
  were injected into its extraction and verified against aggregate SHA-256
  `9ab1b4afe2d7af181b8d1979e1b8cf84c17edbc6824c142926e4f0dab14e80e6` before tests. Local-only
  wheel installation verified distribution/package `0.1.3`, API `semantic-evidence/v1`, public
  symbols, and import root
  `/tmp/stop-parser.QVJIIP/agentic-wheel-verify.jmy4nD/target/agentic_mbse/__init__.py`.
- [x] Issues and deviations: the frozen baseline and item both fail unchanged
  `tests/test_corpus_integration.py::test_ground_truth_scoring` for `paischer_2025` at detected/truth
  `62/23`, 170% error against the unchanged 100% limit. Baseline, worktree, and extracted canonical
  metric records are byte-identical at SHA-256
  `76103f505add9e0951ed526a07789510de7373de2b8766d53e7a2a0673f75f54`; this is a known
  pre-existing unrelated failure, not passed, skipped, waived, or called green. No threshold,
  ground truth, extraction code, or corpus changed. Full mypy and Ruff are likewise recorded as
  baseline refusals, not global-green claims. The 16-file ignored copyrighted corpus remains a
  separate immutable test-only input and was never committed. Two post-commit fast harness attempts
  lacked required subprocess `PATH`/private-cache setup; their failures remain preserved, and the
  correct explicit main-venv, private-cache, offline/no-sync run produced the final `1858/1/33`
  result. Because host Python lacks `ensurepip`, isolated wheel verification used the approved local
  `--target --no-index --no-deps` route. The full private evidence record is
  `/tmp/stop-parser.QVJIIP/artifacts/agentic-phase3-evidence-v1.txt`, SHA-256
  `e056d643f507aded9a93d653d50f903b3e821bb6eaf6d656b71d2e09075663c3`.
- [x] Original-worktree digest unchanged; rollback point recorded: codegen
  `55fb5f1be6a5ad124665e73d23c1e61e301326679b6a21e9a23166c9ef35e8f3`, agentic
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, Fusion
  `57fbdc0c302220e538f7978b85752d9278e17b6e19405482b526ce6857cf4618`, TEAx and 1costingfe both
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`; rollback point is `A_final`
  `1804827cb2cc877b3c0bc74309bd3470fb2ee90b`.
- [x] Fresh-audit CI-1 replacement completed at clean `A_final`
  `2171016d3e3e0805525aa4cf787c55c6293dd00c`. Depth exhaustion now raises typed
  `OPERAND_ITERATION_FAILED`; focused expression/error tests passed 98 and the final fast lane
  collected 1,893, selected 1,860, passed 1,859, retained the one declared Fusion-model skip, and
  deselected 33. Its JUnit SHA-256 is
  `3d06fe01af571bc0b063b74f56563b8fe5f7db3bd187f40a9eb61bc6f2783613`.
  Full Ruff is the exact 119-finding prior result and full mypy is byte-identical at 75 canonical
  diagnostics; neither is called globally green. Two earlier fast launches missing the complete
  PATH/cache contract and one stale mypy-cache comparison remain harness non-verdicts.
- [x] The replacement Agentic source and wheel were built twice byte-identically. Source SHA-256 is
  `7dba41e603b769eb81e305847312f3f1d99ef19fe5c093434834f5c7fa5dc755`; wheel SHA-256 is
  `1fd708a360c0fa787204328c289ee98a557eafe81deae5f025d76495e44b449b`. The local-only wheel
  target proved version `0.1.3`, API `semantic-evidence/v1`, the new typed owner, and imports solely
  beneath `/tmp/stop-parser.QVJIIP/artifacts/audit2-remediation-v1/phase7-agentic-wheel-target`.
- [ ] The prior PDF result remains a measurement of historical producer
  `1804827cb2cc877b3c0bc74309bd3470fb2ee90b`; it is not relabeled as a run of the replacement.
  Between old and new Agentic commits, only `src/agentic_mbse/sysml/expression.py` and its focused
  test changed. The extraction tree, both deterministic-slow test files, corpus tree, pyproject,
  and lock have byte-identical Git object IDs, and the slow import roots contain zero references to
  the changed module. The approved final-archive run contract does not admit the old
  17-pass/one-known-failure/zero-skip result as replacement-producer evidence. The corroborating
  proof record is
  `/tmp/stop-parser.QVJIIP/artifacts/audit2-remediation-v1/agentic-pdf-evidence-reuse.json`, SHA-256
  `9fbd6a9e16322dea680e48bb70315b50c5584beee7a49008879e9451077322aa`. The unchanged failure
  remains `paischer_2025` at detected/truth 62/23 and 170%/100%; no PDF test was rerun.

### Phase 4 completion

- [x] Completed timestamp and 4A/4B/4C commits: 4A completed at
  `2026-08-17T03:41:31-07:00` as `09fdae1986c81c2a5738e1401bdc78e0ea5fa607`; 4B completed at
  `2026-08-17T04:17:50-07:00` as `3b97c0dd3fc6de31158df275190b7259b5dbff53`; 4C completed at
  `2026-08-17T04:36:46-07:00` as `38045fda5f1fb4298db12b9ad5dac6f532b331e3`.
- [x] Commands, counts, and static-removal results: 4A focused pins/boundary suite passed `19/19`;
  all six changed production modules passed targeted mypy and the focused production/boundary Ruff
  set had zero findings. The full local suite collected 2,327 nodes: 2,292 passed, 34 declared
  skips, and one unchanged baseline collection-order failure. Full mypy was byte-identical between
  frozen baseline and item at 52 findings in 11 files (`72` files checked), SHA-256
  `823efc28ea0ebddd019a995808446b018249d5c7bb8547646b08e4f5c223b280`. Full Ruff improved from
  907 to 906 findings with no item-only diagnostic. Offline `uv lock --check` passed for 36
  packages. Static proof found no public `elaborate` export and exactly one production raw-builder
  caller, the loaded-extractor boundary. The complete private record is
  `/tmp/stop-parser.QVJIIP/artifacts/codegen-phase4a-evidence-v1.txt`, SHA-256
  `ccb16d45bcd3e38a11dfac9c25d712b4f48ce1acdfa2c1e838290e8d996cfe58`. For 4B, the focused
  occurrence/producer suite passed `204/204`; the wider elaboration selection passed `304/304`
  with 1,066 deselected; and the authoritative configured default suite passed 2,221 with 34
  declared skips and 88 deselected. Targeted mypy was clean for all three changed production
  modules and targeted Ruff had zero findings. Full mypy remained byte-identical to baseline at 52
  findings in 11 files, SHA-256
  `823efc28ea0ebddd019a995808446b018249d5c7bb8547646b08e4f5c223b280`; full Ruff remained at
  906 findings versus 907 at baseline, with no item-only diagnostic. Static searches found exactly
  one general semantic-owner acquisition and zero old selection, descendant, model-root,
  graph-wide calculation, compatibility-lineage, or glob routes. `git diff --check` was clean. The
  complete 4B private record is
  `/tmp/stop-parser.QVJIIP/artifacts/codegen-phase4b-evidence-v1.txt`, SHA-256
  `1e5114f35459940654ec58bdf496240cb30b67def4ad1e90e8e54327fefb0b5f`. For 4C, the B-focused
  suite passed `132/132`, the extraction/conformance causal selection passed 186 with 9 declared
  golden-absence skips, and the authoritative configured default suite passed 2,244 with 34
  declared skips and 88 deselected. The public B9 proof returned status `1`, rendered its token and
  module/output/type/source once, and preserved the complete sentinel tree byte-for-byte. All nine
  changed production modules passed targeted mypy and targeted Ruff had zero findings. In the
  identical environment, full mypy improved from the frozen 52 diagnostics in 11 files to 30 in 8
  files with zero item-only diagnostics; item output SHA-256 is
  `1fa3544f68d44ae40cb93a6d1f3ac41a0be0899429f653b5ee5f8d02a17d2946`. Full Ruff remained at
  906 findings versus 907 frozen, with no item-only finding and raw JSON SHA-256
  `3675022f176cad6cb5b74d9d106cc5e449f27999c2b06dfc25cb5e356bf074d0`. Static searches found
  one SysML/Python type table, one exit-wrapper table, and zero first/simple/unknown extraction
  type routes, B10 glob/sole-file elections, or unsupported-wrapper warning/omit branches. The 4C
  private record is `/tmp/stop-parser.QVJIIP/artifacts/codegen-phase4c-evidence-v1.txt`, SHA-256
  `83903d385b640c23af10ed003656f34729359e5ce3ee956a9fb6718b50b1cdf2`.
- [x] Issues and deviations: bumping the exact codegen/agentic authority required official
  recapture of 23 committed v6 snapshots. The corpus recapture retained 15 graphs, 22 typed
  refusals, and zero ledger deviations; eight non-corpus snapshots also passed live/replay parity.
  The full-suite refusal is
  `tests/execution/test_fusion_tea_real_teax.py::test_the_lane_runs_the_real_simkit`: collecting the
  legacy runtime-stub module first loads `tests.runtime.pipeline_runner`. Frozen `7b29d8b` fails the
  identical two-file causal selection, while the isolated node passes in baseline and item; it is
  recorded as a pre-existing failure, not passed or green. The first offline `uv lock` resolution
  lacked cached SysIDE registry metadata; after the version-only lock fields were updated from the
  already-resolved frozen lock, offline `uv lock --check` resolved all 36 packages and passed.
  The deliberately combined 4B execution-inclusive process produced 2,308 passes, 34 skips, and
  only the same
  `tests/execution/test_fusion_tea_real_teax.py::test_the_lane_runs_the_real_simkit` failure because
  an earlier test imported the in-repository `tests.runtime.pipeline_runner` stub. This exact
  ordering/environment result is recorded as a failure, not green; no semantic code or assertion
  changed. Phase 5 owns execution in its required fresh process. The `deep_cross_scope_probe`
  fixture supplies an exact calculation-output declaration but no occurrence path and now refuses
  `SI_OCCURRENCE_MISSING` instead of electing the prohibited globally sole producer. Fully resolved
  dot and cross-package P-002 controls remain green. B6 also measured one intended corpus
  transition: `PlantValueShapesLib::ChamberSelectCalc::wall` has the exact user-defined enumeration
  typing `PlantValueShapesLib::'Wall Kind'` at `library.sysml:92` and now refuses
  `SI_TYPE_INVALID`. A dedicated real-model assertion records that refusal; the other 18 extraction
  corpus models remain green. Full mypy and Ruff remain baseline-delta refusals, not global-green
  claims.
- [x] Original-worktree digest unchanged; rollback point recorded: 4A rollback is
  `09fdae1986c81c2a5738e1401bdc78e0ea5fa607`. No mutation command targeted original repository
  source files; only this required canonical plan record changed there. At the 4A record point, the
  original status-path digests were codegen
  `79f70b4d94c26ffe4fcdab4255e151c6290680b88024071a6cca9949bbeb2adf`, agentic
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, Fusion
  `523557640c660dfbc2366118f118a4c2dd02a5ee8e8a3673a9a3a463a6979cb8`, and TEAx/1costingfe both
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. These codegen/Fusion
  digests differ from the Phase 3 record because additional orchestrator-visible paths appeared in
  the original checkouts between records; the dedicated 4A implementation worktree remained clean
  at the empty-status digest. The 4B rollback point is
  `3b97c0dd3fc6de31158df275190b7259b5dbff53`. Immediately before the 4B commit, no mutation command
  had targeted an original checkout and status-path digests were codegen
  `55fb5f1be6a5ad124665e73d23c1e61e301326679b6a21e9a23166c9ef35e8f3`, agentic
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, Fusion
  `57fbdc0c302220e538f7978b85752d9278e17b6e19405482b526ce6857cf4618`, and TEAx/1costingfe both
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. The dedicated 4B worktree
  was clean after the commit. Immediately before 4C, the same five status-path digests were
  unchanged from the 4B record; the dedicated worktree was clean after 4C. Phase 4 rollback is
  `38045fda5f1fb4298db12b9ad5dac6f532b331e3`.

### Phase 5 completion

- [x] Completed timestamp and public-proof commit: `2026-08-17T05:01:22-07:00`;
  `c22c269a57fbd1d3a20d6e7fcd7604a659232da3`, a direct child of 4C
  `38045fda5f1fb4298db12b9ad5dac6f532b331e3`. The commit changes exactly one production template,
  six proof files, and two post-probe real SysML fixtures. Its staged binary diff SHA-256 was
  `6c80d287cc102cd79312c5687ad3f3385ef7614f1b885cdc5e479fe3afaa1506`.
- [x] Real-model, parity, mutation, anti-vacuity, and skip counts: the focused real-model/B-boundary
  matrix passed `77/77` with zero skips. It covers same/nested/package-sibling/direct-package and
  repeated domains, scalar/plural cardinality, redefinition, reversed enumeration, exact producer
  buckets, sibling/repeated/package and globally-sole-unrelated producer outcomes, root/nested,
  unrelated, incomparable, duplicate, unresolved, and unsupported multiplicity authority, all four
  definition-owned positions, and exact A5 pre-graph refusal. The fresh-process execution file
  passed `6/6` with zero skips using extracted `A_final`, the dedicated codegen source, and frozen
  TEAx simkit roots. It proved complete live/snapshot package-byte and graph parity, one public
  source token, exact direct port sets, every-and-only output movers, calculation-output
  transitivity, and repeated/sibling isolation. The configured default suite passed `2,267` with
  the same 34 declared skips, 94 execution/slow deselections, and zero failures. The default suite's
  committed live/snapshot and baseline tests remained green; no pre-existing snapshot or generated
  baseline byte changed. Generated `runtime_params.py` passed targeted mypy and every changed Python
  test passed targeted Ruff. Full mypy remained the 4C item result, 30 diagnostics in 8 files/74
  checked versus frozen 52 in 11/72, with byte-identical item SHA-256
  `1fa3544f68d44ae40cb93a6d1f3ac41a0be0899429f653b5ee5f8d02a17d2946`. Full Ruff had 142
  diagnostic objects in 38 files versus frozen 143 in 39, and every Phase 5 Python path was clean.
- [x] Issues and deviations: real TEAx exposed that generated indexed fields could validate by their
  bracket-bearing alias but not by the Python field name that `CandidateBridge` indexes. A focused
  d38 regression failed first; the generated schema now enables `populate_by_name`, and no semantic
  resolver or TEAx source changed. The frozen `occurrence_calc_domain_derivation/model.sysml`
  remains the exact SysIDE/public-elaboration producer matrix, including its package-scoped row.
  Public execution uses two separate post-probe fixtures because package-scoped entry groups in a
  file literally named `model.sysml` deliberately have no semantic package-display owner at the
  projection seam. Their SHA-256 values are execution matrix
  `4fa927d749fde0300f52a017ba230314845fb2cb57c6b591fb490336eb538f9f` and incomparable writer
  `f009debb10a18e08a57b0a11c3effc53d99cd96eb51f0ba1c2d55a7ab8e43414`. They are Phase 5 proof
  inputs, not changes to the closed Phase 1 inventory, so no probe verdict was invalidated. The
  combined-process simkit-stub ordering failure recorded in Phase 4 was not called green; the
  required Phase 5 file ran alone in a fresh process. Full mypy and Ruff remain baseline-delta
  refusals, not global-green claims. The private record is
  `/tmp/stop-parser.QVJIIP/artifacts/codegen-phase5-evidence-v1.txt`, SHA-256
  `cb970b60c99153e48f4b1e974f516e0d8a9309cd6cba4e18be84f3b61ddf78b1`.
- [x] Original-worktree digest unchanged; rollback point recorded: codegen
  `55fb5f1be6a5ad124665e73d23c1e61e301326679b6a21e9a23166c9ef35e8f3`, agentic
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, Fusion
  `57fbdc0c302220e538f7978b85752d9278e17b6e19405482b526ce6857cf4618`, and TEAx/1costingfe both
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. The dedicated worktree is
  clean. Phase 5 rollback is `c22c269a57fbd1d3a20d6e7fcd7604a659232da3`.

### Phase 6 completion

- [x] Completed 2026-08-17T06:08:56-07:00. Replacement `C_candidate` is
  `093796f9fbf80c09be7a15bc716b337119f1dbcf`, a clean direct descendant of Phase 5
  `c22c269a57fbd1d3a20d6e7fcd7604a659232da3`. It changes 25 declared production/doc/test paths;
  binary diff SHA-256 `d545614d5c8aaad5ec7344430cf258efef7b938dcaf73a43a705462e872dc438`.
- [x] Docs/matrix/backlog/transition/reconciliation coverage is complete. References 00/01/19/20/30,
  the overview, matrix, four diagnostic rows, two separate agent-grade backlog entries, P-003's
  agent-written status, P-004/INDEX reachability, epic, and CURRENT_WORK passed the contract tests.
  P-004 is byte-identical to the original owner/source artifact at SHA-256
  `4a08056c3bac1fe7a87c47c51c42e2fcafd72dce2d06cdb040abecf9497dc0d5` and retains its capture
  grades and owner-verbatim quote. `expected-transitions.md` SHA-256 is
  `cf52b62c5f38f648b9542548e548602d16cda122daa572ae1bbfa4fd1754c5c0`. Private L-01-L-14/U-1/U-2
  staging is `/tmp/stop-parser.QVJIIP/artifacts/codegen-phase6-reconciliation-staging.md`, SHA-256
  `f0412fa3f9f2319451db4d235f9be54b64a9278c215be02f797031bd5d4dd623`. All six final evidence-only
  production paths remain absent.
- [x] Commands, counts, and output-diff result: 94 focused documentation/batch/topology/inventory
  tests passed (`85 + 9`); the configured default suite passed 2,293 with 34 declared skips and 94
  deselected; the fresh
  execution lane passed 94 with zero skips. Targeted Ruff passed every changed Python path and
  targeted mypy passed all five changed production tools. Full mypy remains the unchanged
  baseline-delta refusal at 30 diagnostics in 8 files/74 checked, versus frozen 52/11/72. Full Ruff
  remains unchanged at 142 findings/38 files for `src/tests` and 906/127 for the whole project, with
  zero item-only finding. `capture_v6_batch.py --check` measured 14 captured, 23 refused, two named
  transitions, zero deviations. `capture_baseline.py --check --check-current-batch
  --check-output-transitions` verified the immutable 43-root P_seed source inventory separately,
  23 metadata-only P_seed-to-4A snapshots, 22 byte-identical maintained current snapshots, the two
  exact golden rows, and only `deep_cross_scope_probe`/`plant_value_shapes` as current batch-record
  transitions. Frozen/4A/current batch hashes are respectively
  `bd7bf245e3ca3923b9b5d41db97861c9fcdf64435e768d48a2d7027eb52d9288`,
  `79a0ea9f712652a4665deb8304fbb7d4c4529d76d72dbb1097e712aafaddc1b4`, and
  `7f9269781a8938308715229c5be00855490e82b7e54f9cb90939195e3aeefa40`.
- [x] Issues and deviations: the live v6 batch is recorded as a transitioned output expectation,
  not as a current member of the immutable Phase 1 source lock; no lock or verdict was rewritten.
  The removed 4A deep-cross snapshot
  `e8927d0ebb9b28aafcd7410bbc5122354edc4213468f0b2cb2dfc99aedecc46c` is replaced by the exact A2
  `SI_OCCURRENCE_MISSING` refusal. One execution attempt correctly rejected the byte-equivalent
  extracted A_final import because a retained acceptance fixture pins the clean companion-worktree
  root; the recorded fresh run used exact clean A_final `1804827cb2cc877b3c0bc74309bd3470fb2ee90b`.
  An orchestration interruption discarded one incomplete default-suite process with no verdict.
  The first committed candidate `da4aa78b9c4b661604a43876ac67ef18c82d9082` then failed three
  inventory tests in its fresh clean checkout: the tests compared the immutable 23-row Item 8
  history directly with the current Git path set, so the named deep-cross deletion appeared as an
  unexplained historical extra. The historical JSON was preserved unchanged. Replacement commit
  `093796f9fbf80c09be7a15bc716b337119f1dbcf` requires its only non-current historical row to be the
  exact deep-cross A2 transition, verifies the old hash/current absence/current named refusal, and
  passed the complete 2,293-test configured run above. No semantic assertion, threshold, or
  production route was weakened. Full details are private evidence
  `/tmp/stop-parser.QVJIIP/artifacts/codegen-phase6-evidence-v1.txt`, SHA-256
  `edfed4accb11fb39766ce10bf2c3acbceaff1c2d59c96a3646951408b8ced6b2`.
- [x] Original-worktree digests are unchanged: codegen
  `55fb5f1be6a5ad124665e73d23c1e61e301326679b6a21e9a23166c9ef35e8f3`, agentic
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, Fusion
  `57fbdc0c302220e538f7978b85752d9278e17b6e19405482b526ce6857cf4618`, and TEAx/1costingfe both
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. The candidate worktree is
  clean. Phase 6 rollback is `c22c269a57fbd1d3a20d6e7fcd7604a659232da3`; its completed candidate
  was `093796f9fbf80c09be7a15bc716b337119f1dbcf`. The authoritative later identity is recorded below.

### Phase 7 completion

- [x] Superseded historical run completed 2026-08-17T06:24:12-07:00. The provisional production
  identity was `093796f9fbf80c09be7a15bc716b337119f1dbcf`; its fresh worktree had empty status SHA-256
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` before and after every
  command. All retained Phase 1/2 production files exist and all six final evidence-only paths are
  absent from both the commit and its source archive. Phase 9 later proved its artifact extractor
  could not handle tracked workspace-only absolute symlinks, so this identity and its dependent
  Fusion identity are historical, not current.
- [x] Historical suite/skip results and artifact tuple: the configured default suite passed
  `2,293` with 34 declared skips and 94 deselected; the Phase 5 real-model matrix passed `77`, the
  Phase 6 docs/batch/topology/inventory matrix passed `94`, package/pin/lock checks passed `68`, and
  the fresh-process complete execution lane passed `94`, all with zero unexpected skips/failures.
  The former tuple was (`093796f9fbf80c09be7a15bc716b337119f1dbcf`, source archive
  `sysml-codegen-C_prod.tar` SHA-256
  `2f831c29f56781214b6570b5bf4dc80775979d4baa4780057de5ff3946109628`, wheel
  `sysml_codegen-0.1.1-py3-none-any.whl` SHA-256
  `b3414cc81fbb4ac514bb5b34c53847d6c93fd4aef7ebec33ba64c63dda3cac08`). Both archive builds and
  both wheel builds were byte-identical. `SOURCE_DATE_EPOCH` was `1786971992`. The private
  artifact-build record is `/tmp/stop-parser.QVJIIP/artifacts/cprod-093796f/artifact-build.json`,
  SHA-256 `434ba293eee015d4de58591957d24373daa1b600bcc685606dfd87d53ba1dc2c`.
- [x] Issues and deviations: output reconciliation again measured 14 captured/23 refused, two named
  transitions, and zero deviations; the P_seed source lock and current output-expectation manifest
  remain distinct. Targeted type/lint and static removal checks were clean. Full mypy remained the
  canonically identical 30-diagnostic baseline-delta result, and full Ruff remained exactly 142/38 and
  906/127 with zero changed diagnostic rows; neither is called globally green. Uv first refused its
  read-only default cache. The explicit writable private cache initially lacked local PyPI-namespace
  build-backend entries; copying the already local hatchling/dependency cache entries produced two
  matching offline/no-sync/no-sources wheels without network. One ad hoc import smoke used an
  incorrect four-symbol CLI expectation and failed; the corrected smoke took the exact six-symbol
  set from the kept public-authority test and passed from the isolated wheel target. No source or
  artifact byte changed. Full private evidence is
  `/tmp/stop-parser.QVJIIP/artifacts/codegen-phase7-evidence-v1.txt`, SHA-256
  `30c0972ec0936df4bb233b0756edf2df38570bf67677f9176ae413ee2a9266f3`.
- [x] Original-worktree digests remain codegen
  `55fb5f1be6a5ad124665e73d23c1e61e301326679b6a21e9a23166c9ef35e8f3`, agentic
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, Fusion
  `57fbdc0c302220e538f7978b85752d9278e17b6e19405482b526ce6857cf4618`, and TEAx/1costingfe both
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. The former rollback
  identity was `093796f9fbf80c09be7a15bc716b337119f1dbcf`.
- [x] Replacement completed 2026-08-17T07:35:00-07:00. Phase 9's first exact artifact build refused
  the frozen agentic archive with `tarfile.AbsoluteLinkError` at tracked
  `.claude/skills/pdf-analysis`. The same Git-object condition exists in codegen and Fusion and is
  independent of the private checkout layout. The approved full-archive/fresh-closed-extraction
  contract therefore required a production correction. Commits
  `52b0a3411d1377073917b6b0492f6a0978f02cf7` and
  `319be7f78adda903186b7dc5fbe885f7f7f29aaf` classify every absolute or root-escaping archive
  link, omit only those links from the extracted proof tree, retain internal links, and record the
  exact member path/kind plus target SHA-256 without copying sibling workspace paths into evidence.
  The audit independently recomputes that inventory. The failed Phase 9 v1 root is preserved.
- [x] At that replacement run, the authoritative `C_prod` was exactly
  `319be7f78adda903186b7dc5fbe885f7f7f29aaf`. Its fresh detached worktree stayed clean with empty
  status SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
  The configured default suite passed 2,293 with 34 declared skips and 94 deselected; the focused
  artifact topology suite passed 17 with zero skips. Targeted Ruff and Phase-6-flagged mypy passed
  the changed production tools/tests. Project-wide mypy remained the exact canonical 30-row/8-file
  baseline (canonical SHA-256 `9c6c1553ecbf41707543c54e4f68d8c419e66513b8b2056f0a3571980123b5e4`),
  and project-wide Ruff remained exact at 142 and 906 rows (canonical SHA-256 values
  `9cc7d1176c573574d97e23b003eda0af28d40d684621c37620c8c249cae5af5c` and
  `578f3442e8d810c968f2724ef0f338f2c8f3f08bb8b15baf475aecb05bbbeda1`). These
  project-wide commands remain baseline-delta findings, not global-green claims.
- [x] The replacement certified tuple is
  (`319be7f78adda903186b7dc5fbe885f7f7f29aaf`, source archive
  `sysml-codegen-C_prod.tar` SHA-256
  `cd273ddeb6966f0f34e67526a6afafefa04a89fdd8beea0cb52ad33f5e9a094c`, wheel
  `sysml_codegen-0.1.1-py3-none-any.whl` SHA-256
  `5a25ea046e08fe514d62f19e5660da9080456a3cff1baa8216ae22d98c26f3c4`). Both source builds and
  both offline/no-sync/no-sources wheel builds were byte-identical with `SOURCE_DATE_EPOCH`
  `1786976898` and writable cache `/tmp/stop-parser.QVJIIP/uv-cache-cprod`. Isolated local-wheel
  import proved codegen 0.1.1, agentic 0.1.3, `semantic-evidence/v1`, the public root exports, and
  recorded import roots. The artifact record is
  `/tmp/stop-parser.QVJIIP/artifacts/cprod-319be7f/artifact-build.json`, SHA-256
  `86cfdfa16904d7ff054cb083063ab8ee738478191ab49e65e311c63e9326158e`.
- [x] The original checkout digests remain codegen
  `55fb5f1be6a5ad124665e73d23c1e61e301326679b6a21e9a23166c9ef35e8f3`, agentic
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, Fusion
  `57fbdc0c302220e538f7978b85752d9278e17b6e19405482b526ce6857cf4618`, and TEAx/1costingfe both
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. No codegen commit may
  follow authoritative `C_prod` before its direct-child `C_evidence`.
- [x] Final replacement completed 2026-08-17T09:33:14-07:00 after Phase 9 exposed retained
  workspace-relative and Git-history assumptions. Historical `319be7f78adda903186b7dc5fbe885f7f7f29aaf`
  remains recorded above with its measurements but is no longer current. Commits `46694e2`,
  `3149c09`, `9cd856a`, and `1b437e0` make artifact source/history inputs explicit and fail closed,
  produce a byte-reproducible single-threaded retained-history bundle, carry the closed five-commit
  history inventory, and route the last retained Git readers through that input. Missing, wrong,
  dirty, commit-mismatched, archive-mismatched, or history-incomplete roots are refused; no sibling
  checkout or editable fallback was restored.
- [x] The current authoritative `C_prod` is exactly
  `1b437e08002d4e777d9624ef7c36625a96bd3b1d`. Its clean worktree HEAD, staged diff, unstaged diff,
  and status-path digests were the empty SHA-256
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. All retained Phase 1/2
  production files exist, and all six evidence-only paths are absent from both the commit and source
  archive. The full extracted-source default run selected 2,333 and reported 2,299 passed, 34
  declared skips, 94 execution-marker deselections, and zero failures/errors. The fresh-process
  execution lane passed 94 with zero skips/failures. The explicit artifact/history focused matrix
  passed 61, the artifact-source/topology/environment set passed 34, and the final package/version/
  upstream-pin rerun passed 9, all with zero skips.
- [x] Replacement reconciliation and static results: capture remained 14 captured/23 refused, two
  named transitions, 22 maintained snapshots, 23 metadata-only rows, and zero unexplained changes;
  the frozen P_seed batch SHA-256 remains
  `bd7bf245e3ca3923b9b5d41db97861c9fcdf64435e768d48a2d7027eb52d9288`, distinct from current
  output-expectation batch SHA-256
  `7f9269781a8938308715229c5be00855490e82b7e54f9cb90939195e3aeefa40`. Ledger checks reported
  304 rows/0 problems, 0 unrowed breakages, and all six groups READY. Targeted Ruff and flagged mypy
  passed. Full mypy retained the exact canonical 30-diagnostic baseline (SHA-256
  `9c6c1553ecbf41707543c54e4f68d8c419e66513b8b2056f0a3571980123b5e4`). Full Ruff had zero new
  rows and removed two old F401 rows: 140 src/tests rows (canonical SHA-256
  `abecc3a2692363ef4f1620598eaefd68e4bbc87992846671c3bf92154c85750c`) and 904 project rows
  (canonical SHA-256 `f7877c5f64025a61a92b1a1778ce3060d7b750744754d39ab934f43f5d402a29`). The nonzero
  project-wide commands remain baseline-delta findings, not global-green claims.
- [x] The final certified tuple is
  (`1b437e08002d4e777d9624ef7c36625a96bd3b1d`, source archive
  `codegen-1b437e08002d4e777d9624ef7c36625a96bd3b1d.tar` SHA-256
  `bcee40b96c7437579e78f67ff533dc87d9a9967697c70c4960db559839fc0db6`, wheel
  `sysml_codegen-0.1.1-py3-none-any.whl` SHA-256
  `6eef52f1e6a25c13a0f4f76660b54c82a335b9916c7a2de01b368448f07ee760`). Both builds matched;
  `SOURCE_DATE_EPOCH` was `1786981407`. The retained-history bundle also rebuilt byte-identically at
  SHA-256 `09a5e639000fe38dd360e1be63ec2e23f62eaa24082416fd5fc4be90b95a841d`. The artifact-build
  record SHA-256 is `16291e0d50961fc34ca8f1e713bd2184cbf08593e1ea4880a291c9a7d28d4a43`; artifact-source-input
  record SHA-256 is `cc3e5ed8a524e158f50cc16bb2dee53dc25fee0e81abeb3530c4dc2ba7ccadfb`.
- [x] The local-wheel-only import installed with `--no-index --no-deps` and proved codegen 0.1.1,
  Agentic 0.1.3, `semantic-evidence/v1`, both public evidence types, the exact six CLI symbols, and
  imports only under the new wheel target and reused isolated wheel environment. All 90 wheel
  members have one RECORD row. Two extra `uv lock --check --offline --no-sources` probes are recorded
  as environment refusals, not passes: the private registry cache did not index Agentic until local
  wheels were supplied, after which uv correctly reported that suppressing the intentional
  development source would change the lock. No lock byte changed; the retained lock/package tests
  passed in the full run and explicit 9-test rerun. Full private evidence is
  `/tmp/stop-parser.QVJIIP/artifacts/codegen-phase7-evidence-v3.txt`, SHA-256
  `db0f5f574b1040bbc9dec6313298626e894875a16d923a91b4b9f2956716642c`.
- [x] At this resumed handoff boundary the integration codegen, Agentic, TEAx, and 1costingfe
  status-path digests were empty; the preserved dirty Fusion checkout digest was
  `f6a9b1322facdb6ecb7e571981ae571bab5ddf387422957c4739998fc6329d66`. Earlier digest rows remain
  historical. The current Phase 7 rollback point is exact `C_prod`
  `1b437e08002d4e777d9624ef7c36625a96bd3b1d`; no codegen commit may follow it before the
  direct-child evidence commit.
- [x] Audit-tool replacement completed `2026-08-17T11:52:05-07:00`. Historical `C_prod`
  `1b437e08002d4e777d9624ef7c36625a96bd3b1d` remains recorded above. The new authoritative
  `C_prod` is its clean two-path descendant
  `afb766af80ddc28c405b0dd58a7b14b2cc09bc7e`: one production line creates the verified wheel's
  output directory before copy, and one retained real-wheel regression failed before at the exact
  historical `FileNotFoundError` and passed after. Focused topology passed 18/18; targeted mypy on
  the changed production helper and targeted Ruff on both changed files passed with zero findings.
- [x] The clean extracted default suite collected 2,428, selected 2,334, passed 2,300, retained the
  same 34 declared skips, deselected the 94 execution nodes, and had zero failures/errors; JUnit
  SHA-256 is `b962b44a33d5129173c4d10c1734504631170f31362c9ee060be88be8e390830`.
  The fresh execution process passed 94/94 with zero skips; JUnit SHA-256 is
  `d146b4870ee580a62355124ed3041d3e799f1f02a510b7e4c4820705f4d7f182`. Package/version/API/pin
  checks passed 9/9 and the clean source checkout's offline lock check resolved 36 packages with
  status 0. All Phase 1/2 production records remain present and byte-identical; all six
  evidence-only paths remain absent from the commit and source archive.
- [x] Static and artifact results: full mypy is byte-identical to the preceding C_prod's
  30-diagnostic/8-file baseline refusal, raw SHA-256
  `1fa3544f68d44ae40cb93a6d1f3ac41a0be0899429f653b5ee5f8d02a17d2946`. Full Ruff is canonically
  unchanged at 140 `src/tests` findings in 37 files and 904 whole-project findings in 126 files;
  targeted changed paths are clean. Neither project-wide result is called green. The new certified
  tuple is (`afb766af80ddc28c405b0dd58a7b14b2cc09bc7e`, source archive
  `codegen-afb766af80ddc28c405b0dd58a7b14b2cc09bc7e.tar` SHA-256
  `adeb753d0aae13c4640c7d9800f88be6e7144f8cac72a6b9078d6e144cc3222a`, wheel
  `sysml_codegen-0.1.1-py3-none-any.whl` SHA-256
  `0c86f0285fd30aa01e4c0c64b284125731fcc77fa460dc46c5e943ced20273d9`). The deterministic builder
  compared both archive and wheel builds internally with `SOURCE_DATE_EPOCH=1786992014`; the
  retained-history bundle SHA-256 is
  `79eb303145db40892fbc4ae0133604a0c24861fa6b48b2d8e243897b8393981f`. Artifact-build and
  artifact-source-input record SHA-256 values are respectively
  `9de226012e8942282fb954d4df96f1b114275a34b805f02526e657df42918e41` and
  `b85c56d93455a91730fce5cca490380ad41e942e13c6d8d9f50907e013aca596`.
- [x] The local-wheel-only target verified all 90 RECORD rows (89 hashed members), codegen 0.1.1,
  Agentic 0.1.3, `semantic-evidence/v1`, both public evidence types, the exact six CLI symbols, and
  imports under only the declared wheel/environment roots. One full-suite launch without the
  required artifact-source manifest produced six fail-closed collection errors, and one extracted
  launch without the explicit writable uv cache completed 2,299 tests before the new wheel test
  refused the host's read-only default cache. Both are harness non-verdicts; the complete replacement
  run above supplied both required inputs. Original source-checkout digests remain Agentic/TEAx/
  1costingfe empty and preserved dirty Fusion
  `f6a9b1322facdb6ecb7e571981ae571bab5ddf387422957c4739998fc6329d66`; the original codegen
  checkout contains only authorized plan/status updates. The replacement Phase 7 rollback point is
  exact `C_prod` `afb766af80ddc28c405b0dd58a7b14b2cc09bc7e`.
- [x] Independent-audit remediation replacement completed `2026-08-17T13:15:50-07:00`.
  Historical `C_prod` `afb766af80ddc28c405b0dd58a7b14b2cc09bc7e` and its dependent identities
  remain historical. The new exact `C_prod` is clean commit
  `f4d7351355c7dc2ecb575194eea769e9c8fb0db5`. It adds exact public occurrence reference and
  root-relative `file:line` fields, narrows the occurrence identity catch to
  `IdentityBoundaryError` while preserving cause/code, removes the inert B10 `model_paths`
  parameters, and derives exact elaboration's qualified-only scalar view from the canonical map.
  The licensed real-model/focused matrix passed 119/119 and the final extracted default lane
  collected 2,432, selected 2,338, passed 2,304, retained 34 declared skips, and deselected the 94
  execution nodes with zero failures/errors; JUnit SHA-256 is
  `16b519ae73a7de69f6bea8a50c50d9a52e691eaef44ebc6e70a303b40ee03b37`.
- [x] The execution proof ran in the required isolated split: 82 non-real-TEAx nodes passed and the
  fresh-process real-TEAx file passed 12/12, both with zero skips/failures. JUnit SHA-256 values are
  `6414c04a8226f0e5592af972c87e0d4463f236a361aabd9da787ac224b787aad` and
  `c4289d1f3fc7c969f0be5f3763d52436e9b914f5f2378e9c4c03f379e021e58a`.
  The deliberately combined execution process reported 93 passes and only the known
  collection-order stub-import guard failure; it is a harness non-verdict. Earlier launches that
  omitted the artifact manifest, writable uv cache, or updated exact snapshot-diagnostic fixture
  are likewise retained as harness/stale-fixture non-verdicts, not semantic results.
- [x] Phase 7 static/reconciliation/package results remain honest baseline deltas. Full mypy is
  byte-identical to the preceding 30-diagnostic/8-file refusal at SHA-256
  `1fa3544f68d44ae40cb93a6d1f3ac41a0be0899429f653b5ee5f8d02a17d2946`.
  Full Ruff retains exactly 140 `src/tests` and 904 project rows with zero semantic additions;
  normalized semantic SHA-256 values are
  `9b777b34b36ac882e8794200066ffbf048a1ee74c5cb07de10c678a6060099cc` and
  `7b3e091487fdbcc3fb172102f0f63cc47833eacb1f596e555e3c59f1735efdb5`.
  Targeted changed paths are clean. Capture remains 14 captured/23 refused, two named transitions,
  22 maintained snapshots, 23 metadata-only rows, and zero unexplained deviations. Package/API/pin
  checks passed 9/9, offline lock check resolved 36 packages, and local-wheel import proved 0.1.1,
  Agentic 0.1.3, `semantic-evidence/v1`, the exact six CLI exports, and declared artifact roots.
- [x] The replacement deterministic tuple is (`f4d7351355c7dc2ecb575194eea769e9c8fb0db5`,
  source archive SHA-256 `e86ec56f3340e7eb37c3efc50105a1c4b0fbb408eba012bfc5e5db4aaeb8c37d`,
  wheel SHA-256 `707fbbc730b8f28357cbaa37aebe2a9c2bb1856cf2bf7285b3ea8444ce8e5738`).
  The builder compared both archive and wheel builds internally with `SOURCE_DATE_EPOCH=1786996883`;
  retained-history bundle SHA-256 is
  `cb2e1e7be0707694bfc83db773d634c40c18d82a26946e2a945af092d04dda2a`.
  Artifact-build and source-input record SHA-256 values are
  `f44853089f0354089e1b80e4ea2d6ef37aa65c68973ccd83b22c3ea883a583ec` and
  `e3c163b59d47039efe1101ed6dfdf2733f5e3fc7b6a7118ec5867969693c30c5`.
  All six evidence-only paths are absent from the commit and source archive; the production worktree
  is clean. Project-wide mypy/Ruff remain baseline refusals and are not called green.
- [x] Fresh-audit CI-1/CI-2/CI-3 replacement completed at clean `C_prod`
  `78a9beb956f9b5a517c08836b067f0cb0dc4ccc6`. The exact elaborator now consumes Agentic's typed
  operand and resolved-target owners, and the registry's exit-type input is required. The licensed
  real-model/public refusal matrix passed 63/63. The extracted default lane passed 2,311 with 34
  declared skips and 94 execution deselections; JUnit SHA-256 is
  `d0d0b948602c3ec4660adb3e24a8a7cca287371f796e9fff6ffa396e626d5a9d`. The fresh execution split
  passed 82/82 and 12/12 with zero skips; JUnit SHA-256 values are
  `6a5484aa81ff623052992b181b489d3749f51bc5f1c30a94687b8bd94e736f57` and
  `970aa4c5af1ed03bee4e5a9a439af427b8f4d8e2504c59424e890258ef1bd6b1`.
- [x] Static/package/capture certification is an honest baseline delta. Full mypy is byte-identical
  at 30 diagnostics in 8 files/74 checked. Ruff improves from 140 to 138 `src/tests` rows and 904
  to 902 project rows, with zero new semantic finding. Targeted production mypy is clean; the
  changed-path Ruff delta has zero additions. Offline lock validation resolved 36 packages. Capture
  remains 14 captured/23 refused with the exact two named transitions, 22 maintained snapshots,
  23 metadata-only rows, and no unexplained deviation. Missing cache/provenance/TEAx-path launches
  are retained as harness non-verdicts rather than product failures.
- [x] The replacement deterministic Codegen tuple is
  (`78a9beb956f9b5a517c08836b067f0cb0dc4ccc6`, source SHA-256
  `d64b5396e9ce69db35d7bd5c3afb4c9d634b66841ad09ce9d72cfdc2382ecbc7`, wheel SHA-256
  `7ed5002b965594c546f6ad3c2bd066554921b7682ace3dbe7bf9c66b3e278aaa`). Retained-history bundle
  SHA-256 is `8dc5c435dc12a5789448a0c5631595be439183bb615de521a04f9446287ce25a`.
  The local-wheel target proved Codegen 0.1.1, Agentic 0.1.3, `semantic-evidence/v1`, and declared
  artifact-only import roots. The six evidence-only paths are absent and both production worktrees
  are clean. All earlier A/C identities remain historical.

### Phase 8 completion

- [x] Superseded historical run completed 2026-08-17T07:08:34-07:00. The provisional Fusion
  identity was `4c6c500635852b8dc71107f1be1d8e51068125d4`, a clean direct descendant of frozen Fusion baseline
  `824a876e281a3b9aef58b1873bfbd0b20c4ab77b`. Its five-path diff SHA-256 is
  `f548b268fdd83fb4d47dfc3e8d031ef87387694aa45f458948af250ede1c47df`.
- [x] Historical lock/model/generated-execution results and Fusion archive hash: `uv lock --check --offline`
  resolved 179 packages with status 0 from an explicit writable cache. The extracted committed tree's
  three kept immutable-artifact files passed 13/13 with zero skips and proved live/snapshot byte
  parity, exact output/channel identity, real frozen-TEAx execution, and every-and-only mutation.
  The full configured suite selected 507, passed 391, failed 58, and skipped 58. The clean frozen
  archive baseline selected 494, passed 378, failed 58, and skipped 58. Mechanical JUnit comparison
  found the same 58 failure nodes/messages and 58 skip nodes/reasons, no new/removed legacy nodes,
  and exactly 13 new passing tests; delta-record SHA-256 is
  `caea86eb6f0a74192d78201f4b89e199b4600d54be01c32ee2fd6763e403bd00`. Two independent
  `fusion-tea-F_final.tar` builds matched at SHA-256
  `671a28c67f16113115bf17ed97dfb61f531db2cad639f0272773602ccaf1571f`; the frozen parent
  no-prefix archive also re-matched design pin
  `f83e056ce799a1105aba920baa1d5370891615a4530899bdc4eecbaf41ed38e7`.
- [x] Model diff was empty from frozen baseline through the provisional identity. The 11 unchanged SysML files have
  aggregate inventory/content SHA-256
  `a0b32f9e872f2b209aaa29613eda5914f06e83923db8adf4832e1dc0b19b59ad`. The public generated
  execution accepted the authored models, so no unrelated customer-model repair was made.
- [x] Historical issues and deviations: `agentic-mbse validate --complete models/` exited 1 in both clean trees;
  it was not called passed or green. Baseline and provisional output were byte-identical at SHA-256
  `15165438110a0cbaafea97734314c0081e41f6ec1669f14e25ae8ef2bb351890`: Level 2 retains two
  placeholder-binding warnings and Level 6 retains 26 findings (18 incomplete, four unextractable,
  and four unsupported `.` exposures). Targeted Ruff/mypy are clean for all three new files. Full
  Ruff retains the exact baseline 24 rows (normalized SHA-256
  `e1a3ad30fee1bd6cf11ddf205e2f07b641ec65cd42ae5db85b524dbbf733e90a`), and full mypy retains
  its exact three-diagnostic/duplicate-module refusal (SHA-256
  `40294d2f44ef11a31656390cd12c9ecc727255d3df21cdcf7650cf8589a7f79b`); neither is called
  globally green. Because C_prod's source metadata retains its source-tree-relative agentic
  development source, offline lock generation used a private surrogate containing the same three
  direct immutable PEP 508 Git refs, local Git URL rewrites, and local cache only. The resulting
  lock passed both check and resolution in the actual Fusion project. No network was used. Full
  private evidence is `/tmp/stop-parser.QVJIIP/artifacts/fusion-phase8-evidence-v1.txt`, SHA-256
  `8f77b40fe459ca568c1b8434499a89b321d215de2c597c97cc0b0b81980153f4`.
- [x] Original-worktree digests remain codegen
  `55fb5f1be6a5ad124665e73d23c1e61e301326679b6a21e9a23166c9ef35e8f3`, agentic
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, Fusion
  `57fbdc0c302220e538f7978b85752d9278e17b6e19405482b526ce6857cf4618`, and TEAx/1costingfe both
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. The former rollback point
  was `4c6c500635852b8dc71107f1be1d8e51068125d4`; it was invalidated by the C_prod replacement.
- [x] Replacement completed 2026-08-17T07:43:00-07:00. The authoritative `F_final` is
  `9c86b6e0a734043c6ed484dd712b0ea41486a39e`, a clean descendant of the frozen baseline that pins
  authoritative C_prod `319be7f78adda903186b7dc5fbe885f7f7f29aaf` in project, lock, and test, and records codegen wheel
  SHA-256 `5a25ea046e08fe514d62f19e5660da9080456a3cff1baa8216ae22d98c26f3c4`. Its five-path diff SHA-256
  is `7f663e22854e5356881370fb25ecca18fa7fccbc6ec6f955fefb1da70b097cb9`.
- [x] From the closed extracted replacement archive, `uv lock --check --offline` resolved 179
  packages with status 0 and the three immutable-stack files passed 13/13 with zero skips. The full
  command selected 507, passed 391, failed 58, and skipped 58; it did not pass. Against the identical
  frozen baseline environment (494 selected, 378 passed, 58 failed, 58 skipped), mechanical JUnit
  comparison found zero new/resolved/changed failure nodes/messages, zero new/removed/changed skip
  nodes/reasons, exactly 13 new passing nodes, and zero removed nodes. Delta SHA-256 is
  `f258e014485ec733e787cae7b910ff9098b57cb361c3cad8adc052c0c1051e50`.
- [x] The complete validator again exited 1 with byte-identical baseline output SHA-256
  `15165438110a0cbaafea97734314c0081e41f6ec1669f14e25ae8ef2bb351890`: the same two Level 2
  placeholder findings and 26 Level 6 findings. This remains an unchanged baseline refusal, not
  passed, skipped, waived, or green. No model changed; the 11-file inventory/content SHA-256 remains
  `a0b32f9e872f2b209aaa29613eda5914f06e83923db8adf4832e1dc0b19b59ad`.
- [x] Targeted Ruff/mypy passed. Full Ruff retained the exact 24-row baseline (normalized SHA-256
  `e1a3ad30fee1bd6cf11ddf205e2f07b641ec65cd42ae5db85b524dbbf733e90a`). Full mypy retained the
  exact three-diagnostic/duplicate-module refusal in identical environments (raw SHA-256 including
  the current summary line `9989d12fc21095a1abe95b52c13d1eb4a35c044ef8a23ac5708d058a39e3cd92`).
  Neither is called globally green. Two `fusion-tea-F_final.tar` builds matched at SHA-256
  `da20907fc1de04ae5c722bb01a08379be15e4fa0179d0fb6d51e445224244033`; closed extraction recorded
  and omitted three unsafe tracked links while retaining internal links.
- [x] Full replacement evidence is
  `/tmp/stop-parser.QVJIIP/artifacts/fusion-phase8-evidence-v2.txt`, SHA-256
  `ad8237fd9f32d4f4e9b30981a006a57ee5688dbecde043f3ab89e6733c7c16ba`. Original checkout digests
  remain codegen `55fb5f1be6a5ad124665e73d23c1e61e301326679b6a21e9a23166c9ef35e8f3`,
  agentic/TEAx/1costingfe each
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, and Fusion
  `57fbdc0c302220e538f7978b85752d9278e17b6e19405482b526ce6857cf4618`. That replacement's
  rollback point was `F_final` `9c86b6e0a734043c6ed484dd712b0ea41486a39e`; the later codegen
  production replacement made it historical.
- [x] Final replacement completed `2026-08-17T10:16:12-07:00`. The current `F_final` is
  `229e7970fd54cc3b1dfd9cde19e0fc0526a55697`. It pins current `C_prod`
  `1b437e08002d4e777d9624ef7c36625a96bd3b1d` and its wheel SHA-256
  `6eef52f1e6a25c13a0f4f76660b54c82a335b9916c7a2de01b368448f07ee760` in project, lock, and the
  kept provenance tests. Its five-path baseline diff SHA-256 is
  `f5515bf5e859c4107e3ac1da21bae261ea6590ee6d85c115bd5241b502be038c`.
- [x] The focused immutable-stack proof passed `13/13` with zero skips, and the offline lock check
  resolved 179 packages with status 0. Targeted Ruff/mypy passed. Full Ruff retained the exact
  frozen 24-row refusal (normalized SHA-256
  `e1a3ad30fee1bd6cf11ddf205e2f07b641ec65cd42ae5db85b524dbbf733e90a`) and full mypy retained
  the exact frozen three-diagnostic duplicate-module refusal (raw SHA-256
  `9989d12fc21095a1abe95b52c13d1eb4a35c044ef8a23ac5708d058a39e3cd92`). Neither project-wide
  result is called globally green. No model changed; the 11-file aggregate remains
  `a0b32f9e872f2b209aaa29613eda5914f06e83923db8adf4832e1dc0b19b59ad`.
- [x] The final clean licensed extracted-source run selected 507 tests, passed 391, failed 58, and
  skipped 58 with zero errors/deselections. Frozen baseline selected 494, passed 378, failed 58,
  and skipped 58. Mechanical comparison found zero new/resolved/changed failure nodes/messages,
  zero new/removed/changed skip nodes/reasons, exactly 13 added passing nodes, and zero removed
  nodes. The two raw missing-file messages differed only in their declared extraction root and
  were equal after exact baseline/current root normalization. Final JUnit SHA-256 is
  `40fb32f54b389c1cd29dcec740c25e14b9a2785365fba39388aed1b80a09a1a9`; delta-record SHA-256 is
  `41ff531eed6f75f2e7202e397e38b4f2468e3ec8eea16f1718bdabda28446415`. The 58 failures and 58
  skips remain baseline findings: the command did not pass and is not called green.
- [x] Two invalid attempts remain preserved as non-verdicts. The codegen-environment/no-license
  attempt reported 366 passed, 46 failed, 38 setup errors, and 57 skipped (JUnit SHA-256
  `08681a45ce225f60de39c76a4037362508e0650e3f1bbfc52e7d399b880ca767`). The licensed attempt
  against a previously reused/mutated extraction reported 389 passed, 60 failed, and 58 skipped
  (JUnit SHA-256 `1e765f57859436e1cb2658bf5426fb21088ff963f7f9cd77750ed948dcc4c707`), adding two
  stateful/environment failures. Neither is a product verdict. A later clean extraction with the
  explicit TEAx root omitted reproduced the second JUnit bytes and is separately retained as a
  missing-input non-verdict.
- [x] The complete validator still exited 1 with byte-identical frozen output SHA-256
  `15165438110a0cbaafea97734314c0081e41f6ec1669f14e25ae8ef2bb351890`: two Level 2 placeholder
  findings and 26 Level 6 findings. It is an unchanged baseline refusal, never passed, skipped,
  waived, or green. The deterministic `F_final` source archive SHA-256 is
  `f6e440a28e97c3d602f31d620a0f34e7f1531a096d4b8220936703feeccef82d`; the five-input artifact
  record SHA-256 is `19c0b5abba3cee9e5a9731373d6103ca54b5bd423c9b74d7e539a7a2491b8313`.
- [x] Full private evidence is
  `/tmp/stop-parser.QVJIIP/artifacts/fusion-phase8-evidence-v3.txt`, SHA-256
  `9693ea46cc1351073a2a79f74b739901371975318324114d54cd2fa3b42892f6`. Original checkout digests
  remain codegen `55fb5f1be6a5ad124665e73d23c1e61e301326679b6a21e9a23166c9ef35e8f3`, Agentic/TEAx/
  1costingfe each `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, and preserved dirty
  Fusion `f6a9b1322facdb6ecb7e571981ae571bab5ddf387422957c4739998fc6329d66`. The authoritative Phase
  8 rollback point was exact `F_final` `229e7970fd54cc3b1dfd9cde19e0fc0526a55697`; the later
  codegen audit-helper production correction made it historical.
- [x] Audit-helper replacement completed `2026-08-17T12:05:15-07:00`. The authoritative `F_final`
  is `4fdd78f53334e5a9bcd695259b27afeb0b347f62`. It pins authoritative `C_prod`
  `afb766af80ddc28c405b0dd58a7b14b2cc09bc7e` and codegen wheel SHA-256
  `0c86f0285fd30aa01e4c0c64b284125731fcc77fa460dc46c5e943ced20273d9` in project, lock, and kept
  provenance tests. Its five-path frozen-baseline diff SHA-256 is
  `4085af22a3fe5eb91495ed7a8f1a8263b03a72214641c531b5e92195ced7b661`; no model changed.
- [x] The focused immutable-stack proof passed 13/13 with zero skips (JUnit SHA-256
  `fcd19ae43cd08f0ef86cd72477105d4dc9c77c07154475d6f57666ea1a5d4600`), the offline lock check
  resolved 179 packages with status 0, and targeted Ruff/mypy were clean. Full Ruff retained the
  canonically identical frozen 24-row refusal and full mypy retained the byte-identical frozen
  three-diagnostic refusal (SHA-256
  `9989d12fc21095a1abe95b52c13d1eb4a35c044ef8a23ac5708d058a39e3cd92`); neither is called green.
- [x] The clean licensed extracted full suite selected 507, passed 391, failed 58, and skipped 58
  with zero errors/deselections in 282.20 seconds. Frozen baseline selected 494/passed 378/failed
  58/skipped 58. Mechanical comparison found zero new/resolved/changed failure nodes/messages,
  zero new/removed/changed skip nodes/reasons, exactly 13 added passing nodes, and zero removed
  nodes. JUnit SHA-256 is `e85afde95a12abe9272739a5196c5f25ea510aaf7eef1116cbc44af3651de8e5`;
  delta SHA-256 is `8effaf2bf7e409482ceb7cd0e612541f9d6a47652bbf4731b8bf0786c052999e`.
  The command did not pass and is not called green. The complete validator again exited 1 with
  byte-identical frozen output SHA-256
  `15165438110a0cbaafea97734314c0081e41f6ec1669f14e25ae8ef2bb351890` (two Level 2 and 26 Level
  6 findings), an unchanged baseline refusal.
- [x] The deterministic Fusion archive SHA-256 is
  `0c187ccff225cc916bb55a7e1577b884af3d163b813694c16eab111961d6ab6f`; the five-input artifact
  record SHA-256 is `1b762967569e1ad7880bab7066a0e2099603a9e8fee368a6190068f93ac6d4d5`.
  Full private evidence is `/tmp/stop-parser.QVJIIP/artifacts/fusion-phase8-evidence-v4.txt`,
  SHA-256 `f77353187cfd5db61b25c2f84f5b2b32dff994e206f20f2a30b0c279afc4b64e`. A first offline build
  using a cache without hatchling remains a harness non-verdict; the successful build used the
  already-populated writable C_prod cache without network. The authoritative rollback point is
  exact `F_final` `4fdd78f53334e5a9bcd695259b27afeb0b347f62`.
- [x] Independent-audit remediation replacement completed `2026-08-17T13:27:20-07:00`.
  Historical `F_final` `4fdd78f53334e5a9bcd695259b27afeb0b347f62` and every earlier identity
  remain historical. The new clean exact `F_final` is
  `1af570529a7eec489b5e07ea0ab2a02d9cf21eef`; it pins exact `C_prod`
  `f4d7351355c7dc2ecb575194eea769e9c8fb0db5` and codegen wheel SHA-256
  `707fbbc730b8f28357cbaa37aebe2a9c2bb1856cf2bf7285b3ea8444ce8e5738` in project, lock, and
  kept provenance tests. Its five-path frozen-baseline diff SHA-256 is
  `95b4cb41720d5c4f3631452c3de38bc5167b48aea39ea9f7a9540b2ba49d0cc4`.
- [x] The focused immutable-stack/public execution proof passed 23/23 with zero skips (JUnit
  SHA-256 `598f3ee68600ca79316cbd70660e912b85851c5251999da0f1cac2f40aea3723`).
  It proves live/snapshot byte parity, real generated TEAx execution, and every-and-only mutation
  independently over both maintained public trees, `models/` and
  `exploration/ife_e2e/models`. Each tree has 11 SysML files and the same content multiset SHA-256
  `a2eddf1624b0a81d412e5355109f8fe55b65e65f51f72623d1bce47d5ddde7b1`; no model byte changed.
  The offline lock check resolved 179 packages with status 0.
- [x] The clean licensed extracted full suite selected 517, passed 401, failed 58, and skipped 58
  with zero errors. It did not pass and is not called green. The frozen baseline selected 494,
  passed 378, failed 58, and skipped 58. Canonical mechanical comparison found no missing legacy
  nodes, no legacy state or message changes, and 23 new passing nodes. Against the preceding
  current proof it verifies that each of ten formerly unparameterized passing nodes was replaced by
  passing `primary` and `exploration` nodes, with no other state or canonical-message change.
  JUnit SHA-256 is `5ba9f4efc8cf82ce69d15ebc378e0fe8c40405921624b86e95908608369eb8bc`;
  delta-record SHA-256 is `3a2009bf2352354191c03f7aef34773ed7c15f7bf83311ca83095cc746fa6e14`.
  Canonical messages compare the JUnit message field after extraction-root and process-local object
  address normalization; traceback verbosity is not a semantic field. A bare `pytest` launch that
  also collected archive/generated trees produced eight collection errors and remains a
  command-scope harness non-verdict.
- [x] Complete validation of `models/` exited 1 with exact frozen output SHA-256
  `15165438110a0cbaafea97734314c0081e41f6ec1669f14e25ae8ef2bb351890`: two Level 2 and 26 Level
  6 findings. Validation of `exploration/ife_e2e/models` also exited 1 with SHA-256
  `cb0b7a33dc568e0c4729a5421d26a4a154d5615781d8240e00053cbf3af732a2` and the same finding
  categories under its own root. These are baseline refusals, not passes, skips, waivers, or green
  results. Targeted Ruff/mypy passed. Full Ruff retains the canonically identical 24-row frozen
  refusal (normalized SHA-256
  `e1a3ad30fee1bd6cf11ddf205e2f07b641ec65cd42ae5db85b524dbbf733e90a`), and full mypy retains
  the byte-identical frozen three-diagnostic refusal (SHA-256
  `9989d12fc21095a1abe95b52c13d1eb4a35c044ef8a23ac5708d058a39e3cd92`).
- [x] The deterministic Fusion archive SHA-256 is
  `4e5376f1e5e0ddc8bfda0c0711b30f76f93038536b4fa3087b48056ce7614bb4`. The five-input artifact
  record and explicit source-input record SHA-256 values are
  `1e32743f2ffd234d8e78b0a24dc61a825ecd7dc065b668b3ee17ae6e5f2ad908` and
  `e3c163b59d47039efe1101ed6dfdf2733f5e3fc7b6a7118ec5867969693c30c5`.
  Both production worktrees are clean. The Phase 8 rollback point is exact `F_final`
  `1af570529a7eec489b5e07ea0ab2a02d9cf21eef`.
- [x] Fresh-audit CI-1/CI-2/CI-3 dependent replacement completed at clean exact `F_final`
  `028f98741a2aea7c238beed961402857af82d15f`. Project, lock, and provenance tests pin exact
  `A_final` `2171016d3e3e0805525aa4cf787c55c6293dd00c`, exact `C_prod`
  `78a9beb956f9b5a517c08836b067f0cb0dc4ccc6`, and wheel SHA-256 values
  `1fd708a360c0fa787204328c289ee98a557eafe81deae5f025d76495e44b449b` and
  `7ed5002b965594c546f6ad3c2bd066554921b7682ace3dbe7bf9c66b3e278aaa`. The offline lock check
  resolved 179 packages and targeted Ruff/mypy were clean.
- [x] The immutable-stack/public proof passed 23/23 over both maintained model trees with zero
  skips; JUnit SHA-256 is `7b3468611512b8d5b263c442294877d46f3edcbcef4bcdab643e1326e61fa0d2`.
  The clean extracted full suite selected 517, passed 401, failed 58, and skipped 58. It did not
  pass and is not called green. Mechanical comparison against the frozen 494-node baseline found
  zero missing legacy nodes, zero state/message changes, and exactly 23 added passes; comparison
  with the preceding maintained two-tree result found zero node/state/message change. Full-suite
  JUnit SHA-256 is `46c91a96e677dabb54ebdbecb2146cd214ad4f4d7c0b02fe990ec92171b08bf6`;
  the comparison program SHA-256 is
  `662887585009b8dd2e145c6c039c9ffb6bb98158d770ffa434d95b884f6286aa`.
- [x] Both complete model validators remain exact baseline refusals: primary output SHA-256
  `15165438110a0cbaafea97734314c0081e41f6ec1669f14e25ae8ef2bb351890` and exploration output
  SHA-256 `cb0b7a33dc568e0c4729a5421d26a4a154d5615781d8240e00053cbf3af732a2`, each with the existing
  Level 2/Level 6 categories. Full test-tree Ruff retains the 24-row baseline and mypy retains the
  exact three-diagnostic refusal; neither is called green. Deterministic Fusion archive SHA-256 is
  `57f50a63f241eb5d6603c555a9c3c1d67663ba5480ab96b99e07d97c662f9231`; final five-input
  artifact-build SHA-256 is `526f8f872fdf63fa07b46d8c84e03948de148d835e3ff42b5f746d04e81d833c`.
  The first focused launch omitted three declared environment inputs and remains a harness
  non-verdict. No model byte changed. All prior Fusion identities remain historical.

### Phase 9 completion

- [x] Completed timestamp: `2026-08-17T11:28:07-07:00`.
- [x] Five-input commands, counts, skips, import roots, and artifact hashes: the retained
  `C_prod` validators accepted 18 closed run records under extracted roots and the composed
  `/tmp/stop-parser.QVJIIP/artifacts/phase9-v3/isolated-venv`. Agentic fast collected 1,892,
  selected 1,859, passed 1,858, and had its one declared missing-Fusion-model skip; its final
  deterministic slow run collected 1,892, selected 18, passed 17, failed only
  `test_ground_truth_scoring`, skipped zero, and deselected 1,874 in 1,628.19 seconds. The failure
  remained byte-identical to the frozen canonical paischer metrics (`detected=62`, `truth=23`,
  `error=170%`, `limit=100%`), canonical SHA-256
  `76103f505add9e0951ed526a07789510de7373de2b8766d53e7a2a0673f75f54`; final JUnit SHA-256 is
  `d149282c7192a38b1f6cf55f5ea84e4bd895dbbd82cf8fa33795cb0c04e985ab`.
  1costingfe selected 660, passed 602, and retained 58 declared skips; its Ruff command passed with
  zero findings. TEAx passed 406/406. Codegen default collected 2,427, selected 2,333, passed 2,299,
  skipped 34 declared nodes, and deselected 94; its fresh execution lane passed 94/94 with zero
  skips. Fusion focused execution passed 13/13. Fusion full selected 507, passed 391, failed 58,
  and skipped 58, mechanically identical to its frozen failures/skips with 13 added passes; the
  validator retained the byte-identical two-Level-2/26-Level-6 refusal. Those nonzero commands and
  the recorded project-wide static baselines are not called passed or green. The exact source
  hashes are Agentic `c6a530e3ccd91bdb005b44bb193066e1f7517288331b4bd485be00d8fdebbd6b`,
  codegen `bcee40b96c7437579e78f67ff533dc87d9a9967697c70c4960db559839fc0db6`,
  TEAx `9786fec4178975eeefbedb4d8810215e2abb5df4b162ac8290684e3aaf95d884`,
  1costingfe `0a03d387df18bb75b8336a5b471a7203473ba0f2f7255f65846813064b0bc7fa`,
  and Fusion `f6e440a28e97c3d602f31d620a0f34e7f1531a096d4b8220936703feeccef82d`;
  the five-input artifact record SHA-256 is
  `19c0b5abba3cee9e5a9731373d6103ca54b5bd423c9b74d7e539a7a2491b8313`.
- [x] Six staged evidence-file hashes: `dependencies.json`
  `1df296f6903adf9d8645f8e614125cc93cdaa28890489690a5d72400713e4077`,
  `wheelhouse-requirements.txt`
  `8dbf01d92a473f74c5c093a0080a38f730cff9d6d43ed0ed513977c4a884dc0d`,
  `execution-provenance.json`
  `f85d11b7840535dcdbbd06b044f1511d15e6632158be05e151c761b1453a6994`,
  `independent-green.json`
  `8533e5ad4685d2a2de1b333002cc177d393477999fca9f76389496f05e4d237e`,
  `reconciliation-ledger.md`
  `c80a8e82440ff75f961438a3e47a109a31a35a70f674b5a450a4bba22dfb82ea`,
  and `evidence-lock.json`
  `2ca5ed1de096b8327461e30e15755f94471ae7274fd09317672ea314f529362e`.
  The lock covers the other five files plus the production probe lock and expected-transition
  record, and does not cover itself. The L-01-L-14/U-1-U-2 ledger is total. The retained evidence
  topology suite passed 17/17.
- [x] Issues and deviations: all 177 wheel requirements and all 36,741 installed RECORD members
  verified; the restored composed environment has 177 frozen distributions and no editable,
  sibling, or unresolved input. The locked Agentic PDF overlay verified 127 RECORD members and the
  16-file corpus aggregate
  `9ab1b4afe2d7af181b8d1979e1b8cf84c17edbc6824c142926e4f0dab14e80e6` before the slow run, then
  the composed environment was restored from the hash-locked wheelhouse. The terminal-plugin
  zero-selection attempt and the 20-minute timeout after 15 passing nodes remain harness
  non-verdicts. The 15 paid/network Claude nodes remain explicitly unrun external-service cases,
  not passes or skips. Phase 7/8 measurements were reused only for their unchanged exact immutable
  artifacts as permitted; the missing Agentic slow semantic run was run to completion here.
- [x] Original-worktree digests unchanged for source-owned checkouts: Agentic, TEAx, and
  1costingfe each remain
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, and preserved dirty
  Fusion remains `f6a9b1322facdb6ecb7e571981ae571bab5ddf387422957c4739998fc6329d66`.
  The original codegen checkout contains only the authorized canonical-plan update. The Phase 9
  rollback point was the six-file private staging set under
  `/tmp/stop-parser.QVJIIP/artifacts/final-identities-v4/evidence-staging`; its codegen/Fusion
  identities became historical after the audit-helper production correction.
- [x] Replacement staging completed `2026-08-17T12:05:15-07:00` from authoritative `C_prod`
  `afb766af80ddc28c405b0dd58a7b14b2cc09bc7e` and `F_final`
  `4fdd78f53334e5a9bcd695259b27afeb0b347f62`. All 177 wheel requirements and all 36,741 hashed
  RECORD members passed under the reused isolated environment and wheelhouse after replacing only
  the codegen wheel with SHA-256
  `0c86f0285fd30aa01e4c0c64b284125731fcc77fa460dc46c5e943ced20273d9` and its exact hash line.
  The requirements SHA-256 is `a31df8fae7e5088eb460a645828213655c5c37462f63b149bc6d9f3c7620f5d4`.
- [x] The replacement independent record contains 18 non-vacuous closed run records, zero
  unexpected skips, exact declared import roots, and the authoritative five artifact inputs. New
  codegen default collected 2,428, selected 2,334, passed 2,300, retained 34 declared skips, and
  deselected 94; execution passed 94/94. New Fusion focused passed 13/13; full retained exactly 391 passed, 58 baseline failures,
  and 58 baseline skips, with zero mechanical baseline delta. Agentic fast/slow, Agentic static,
  TEAx, and 1costingfe results were reused only from their unchanged immutable inputs. The Agentic
  PDF suite was not rerun: its completed 17-pass/one-byte-identical-baseline-failure/zero-skip result
  and the locked 16-file corpus remain exact. Fifteen paid/network cases remain explicitly unrun
  external-service tests, not passes or skips.
- [x] Replacement six-file hashes: `dependencies.json`
  `86dae2d35b67c44d59b5005a0568e5bf62e9ec4a273855b46948b247181158a2`,
  `wheelhouse-requirements.txt` `a31df8fae7e5088eb460a645828213655c5c37462f63b149bc6d9f3c7620f5d4`,
  `execution-provenance.json` `c50b851ed4bbf75eb61af9cc99eb818e8615b13cbdc92c486719a6d439cf9de6`,
  `independent-green.json` `56f28f8d97de834a826f36f8f8688e40e2db0775cffb2237f5d8ac15b8911bd0`,
  `reconciliation-ledger.md` `038f3b762d89412654c8a5ec7779f7dc16ec00e8cf113c7a18b1ea80996a9b16`,
  and `evidence-lock.json` `c19d197f5d6942af383c3aeb0a811250e89ff648bb9c83d91c7a2f8270845caa`.
  The lock covers the other five evidence files plus the production probe lock and expected
  transitions, never itself. The L-01-L-14/U-1-U-2 ledger is total and names only `C_prod`.
  Retained topology tests passed 18/18 (JUnit SHA-256
  `d84437083ad98cb7a70d02fefc27bc9cddeb0fd39285e64e6b47c6a1d20a01b2`). The current Phase 9
  rollback point is `/tmp/stop-parser.QVJIIP/artifacts/final-identities-v5/evidence-staging`.
- [x] Independent-audit remediation staging completed `2026-08-17T13:30:56-07:00` from exact
  `C_prod` `f4d7351355c7dc2ecb575194eea769e9c8fb0db5` and exact `F_final`
  `1af570529a7eec489b5e07ea0ab2a02d9cf21eef`. The deterministic five-input artifact record is
  `1e32743f2ffd234d8e78b0a24dc61a825ecd7dc065b668b3ee17ae6e5f2ad908`; source archive SHA-256
  values are Agentic `c6a530e3ccd91bdb005b44bb193066e1f7517288331b4bd485be00d8fdebbd6b`,
  codegen `e86ec56f3340e7eb37c3efc50105a1c4b0fbb408eba012bfc5e5db4aaeb8c37d`, TEAx
  `9786fec4178975eeefbedb4d8810215e2abb5df4b162ac8290684e3aaf95d884`, 1costingfe
  `0a03d387df18bb75b8336a5b471a7203473ba0f2f7255f65846813064b0bc7fa`, and Fusion
  `4e5376f1e5e0ddc8bfda0c0711b30f76f93038536b4fa3087b48056ce7614bb4`.
- [x] The closed record has 20 exact runs. Passing semantic lanes are Agentic fast 1,858 passes plus
  one declared skip, 1costingfe 602 passes plus 58 declared skips, TEAx 406/406, codegen default
  2,304 passes plus 34 declared skips, codegen execution 82/82 plus fresh-process real-TEAx 12/12,
  and Fusion focused 23/23 over both maintained model trees. Nonzero results preserve their exact
  contracts: Agentic slow has 17 passes, zero skips, and the one unchanged paischer baseline failure;
  Fusion full has 401 passes, 58 frozen failures, and 58 frozen skips; both Fusion validators and
  project-wide static lanes retain the recorded baseline refusals. Fifteen paid/network Agentic
  cases remain explicitly unrun external-service tests. None is called passed, skipped, waived, or
  globally green. The completed Agentic PDF result and 16-file corpus aggregate
  `9ab1b4afe2d7af181b8d1979e1b8cf84c17edbc6824c142926e4f0dab14e80e6` were reused unchanged and
  were not rerun.
- [x] The retained wheelhouse was updated only with the certified codegen wheel, then all 177 wheels,
  177 hash-locked requirements, and 36,741 RECORD members passed. Requirements SHA-256 is
  `3657e0000150c94b1be1a9c07fe3d5e29142c5458cf30b73316d58c7aaab8d0c`.
  Six staged hashes are `dependencies.json`
  `b1b4282069758d37c4d475c3021e0cc3e0f38d56bb84765ccf9d30964154a102`,
  `wheelhouse-requirements.txt`
  `3657e0000150c94b1be1a9c07fe3d5e29142c5458cf30b73316d58c7aaab8d0c`,
  `execution-provenance.json`
  `8114587daceea57bc92f94f3325653e89f0a09177ed58335fd63c77cd77e4818`,
  `independent-green.json`
  `5fd2b5dc4273d883fda1a2cacbe597bfb951155aa4c1fc3677a1775bf0fd9169`,
  `reconciliation-ledger.md`
  `1777c9eaa71077cfffc6405e0cba214410de5c557d0071c7f6ebdc321b9f92f2`, and
  `evidence-lock.json`
  `eac5ea61da30351aa75ff0124751f1eec81e85bc36ee8c8a1f300ec6222912fe`.
  The lock covers the other five files plus the two production lock inputs, never itself; the
  L-01-L-14/U-1-U-2 ledger is total and names `C_prod`, not an evidence identity.
- [x] Original status digests at staging are codegen
  `17eb7dc21973b210f75e4207beac01498a69cdeff49a2be6f94dd006e007dca4`, preserved dirty Fusion
  `f6a9b1322facdb6ecb7e571981ae571bab5ddf387422957c4739998fc6329d66`, and Agentic/TEAx/
  1costingfe each `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
  The rollback point is
  `/tmp/stop-parser.QVJIIP/artifacts/final-identities-v6/evidence-staging`.

- [x] Fresh-audit CI-1/CI-2/CI-3 replacement staging completed `2026-08-17` from exact
  `A_final` `2171016d3e3e0805525aa4cf787c55c6293dd00c`, exact `C_prod`
  `78a9beb956f9b5a517c08836b067f0cb0dc4ccc6`, and exact `F_final`
  `028f98741a2aea7c238beed961402857af82d15f`. The five-input artifact record SHA-256 is
  `526f8f872fdf63fa07b46d8c84e03948de148d835e3ff42b5f746d04e81d833c`; the closed artifact-source
  manifest SHA-256 is `bf1e43737ad192fbc0e3a51658f4d1a674358e89e8739590ea52d5af0c9010a3`.
  Source archive SHA-256 values are Agentic
  `7dba41e603b769eb81e305847312f3f1d99ef19fe5c093434834f5c7fa5dc755`, codegen
  `d64b5396e9ce69db35d7bd5c3afb4c9d634b66841ad09ce9d72cfdc2382ecbc7`, TEAx
  `9786fec4178975eeefbedb4d8810215e2abb5df4b162ac8290684e3aaf95d884`, 1costingfe
  `0a03d387df18bb75b8336a5b471a7203473ba0f2f7255f65846813064b0bc7fa`, and Fusion
  `57f50a63f241eb5d6603c555a9c3c1d67663ba5480ab96b99e07d97c662f9231`. Agentic and codegen wheel
  SHA-256 values are `1fd708a360c0fa787204328c289ee98a557eafe81deae5f025d76495e44b449b`
  and `7ed5002b965594c546f6ad3c2bd066554921b7682ace3dbe7bf9c66b3e278aaa`.
- [x] The replacement closed record has 20 runs. Passing semantic lanes are Agentic fast 1,859
  passes plus its one declared missing-Fusion-model skip, 1costingfe 602 passes plus 58 declared
  skips, TEAx 406/406, codegen default 2,311 passes plus 34 declared skips, codegen execution 82/82
  plus fresh-process real-TEAx 12/12, and Fusion focused 23/23 across both maintained model trees.
  Nonzero baseline-delta records remain nonzero: Agentic mypy and Ruff, codegen mypy and Ruff,
  Fusion full (401 passes, 58 frozen failures, 58 frozen skips), both Fusion validators, and Fusion
  mypy/Ruff. None is called globally green. The 15 network-backed paid Claude nodes remain unrun
  external-service tests, not passes or skips.
- [x] The settled owner decision permanently retires the Agentic PDF suite from parser-work
  validation. Its old producer, counts, corpus, JUnit, and non-impact record remain historical
  information only. They are not inputs to certification, do not require replacement at a new
  `A_final`, and must not trigger the retired command.
- [x] The reused wheelhouse contains 177 wheels and 177 hash-locked requirements; all 36,741 RECORD
  members passed. Its inventory aggregate is
  `32234868eea49325e9096cb416131bdd976e011a530d3cca05ade7b67ec967ca`, requirements SHA-256 is
  `cc1d00755a08f3a6873010b1b8f71a06b68f6854c5baa083392ae4effee66e67`, and installed freeze
  SHA-256 is `e4441ecb83490078441f8ed0d8688fa051698fcb0cc874895b2b5ba61248c024`.
  The replacement staged hashes are `dependencies.json`
  `6130305dd9b88ece748dda7806d93f23d44bf0a011aa3496c7278c15b04fb4a5`,
  `wheelhouse-requirements.txt`
  `cc1d00755a08f3a6873010b1b8f71a06b68f6854c5baa083392ae4effee66e67`,
  `execution-provenance.json`
  `80759c540ca9a2f7f8e01607c67b6bf2d5bac19884a740b97ba2bab1304534a3`,
  `independent-green.json`
  `c21bad8ba7aec759a8f5ee9814cb0811b131db84521ea4c974cb89cf0e80ffb7`,
  `reconciliation-ledger.md`
  `15d7bf4dc774e6982561648bf2d60383316d81e2fa5636290ea3edc301c4f3be`, and
  `evidence-lock.json`
  `8990c8a3384f3eb7169e1b9bc7a4e976eb0ed209a20fe06b44a2106223209232`. The seven-entry lock covers
  the other five evidence files plus the production probe lock and expected transitions, never
  itself. The L-01-L-14/U-1-U-2 ledger is total. All earlier harness non-verdicts remain explicitly
  classified in provenance.

### Phase 10 completion

The 2026-08-17 continuation authorizes the owning production fix and a replacement identity chain.
Old `C_prod` `1b437e08002d4e777d9624ef7c36625a96bd3b1d`, old `F_final`
`229e7970fd54cc3b1dfd9cde19e0fc0526a55697`, and unaccepted evidence candidate
`b8a48853a0a8fff9f948f046600c91f5bcf4b5e0` remain historical measurements and are not relabeled.
The replacement chain starts from the clean codegen production branch and reruns only proofs
affected by the audit-tool change or new immutable identities; the completed exact Agentic slow
corpus result is reused unchanged and is not rerun.

- [x] Historical unaccepted direct-child candidate
  `b8a48853a0a8fff9f948f046600c91f5bcf4b5e0` remains preserved. It was not built, pinned, merged,
  pushed, or relabeled as accepted evidence.
- [x] Historical candidate parent and six changed paths: parent was byte-exact historical `C_prod`
  `1b437e08002d4e777d9624ef7c36625a96bd3b1d`; the changed set is exactly
  `verification/dependencies.json`, `verification/wheelhouse-requirements.txt`,
  `verification/execution-provenance.json`, `verification/independent-green.json`,
  `verification/reconciliation-ledger.md`, and `verification/evidence-lock.json`. The candidate
  tree is clean, all six staged bytes match, none names the candidate SHA, and no downstream ref,
  Fusion project file, or lock names it.
- [x] Historical blocker record: separable mechanical checks reported
  `parent_and_paths: PASS`, `existing_artifacts_and_wheel_metadata: PASS`, `fusion_pin: PASS`, and
  `artifacts_and_lock: PASS`. The C_prod source/history reconstruction reached the wheel copy, and
  an independent supported deterministic-wheel invocation rebuilt exact
  `sysml_codegen-0.1.1-py3-none-any.whl` SHA-256
  `6eef52f1e6a25c13a0f4f76660b54c82a335b9916c7a2de01b368448f07ee760`. The required exact
  `verification/audit_evidence.py` command cannot report its four groups because the retained
  production auditor passes absent temporary directory `wheels/` to `_deterministic_wheel`, which
  finishes its two deterministic builds and then raises `FileNotFoundError` while copying to that
  missing directory. This is a C_prod-owned verification defect, not an evidence or artifact
  mismatch, so the exact audit box and Phase 10 completion remain open.
- [x] Issues and deviations: the first direct-script launch omitted the explicit C_prod module root
  and is retained as a harness non-verdict (`ModuleNotFoundError: verification`). The corrected
  launch used exact C_prod code and reached the production defect at
  `verification/audit_evidence.py:340` -> `verification/build_artifacts.py:446`. The retained C_prod
  topology suite passed 17/17 after the candidate commit. No evidence value, assertion, artifact,
  or production source was changed to bypass the failure.
- [x] Original-worktree digests unchanged for Agentic, TEAx, and 1costingfe
  (`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`) and preserved dirty
  Fusion (`f6a9b1322facdb6ecb7e571981ae571bab5ddf387422957c4739998fc6329d66`). The original codegen
  checkout contains only authorized plan/status updates. The exact resume point is the clean
  candidate worktree `/tmp/stop-parser.QVJIIP/worktrees/sysml-codegen-evidence-v4`; the owning fix
  must create a replacement production identity and rerun its dependent Fusion/evidence identities
  before any evidence commit can be accepted.
- [x] Replacement Phase 10 completed `2026-08-17T12:13:40-07:00`. Authoritative `C_evidence` is
  `58495607bdf140f1f716aafb95f7122228a4bf52`, a clean direct child of exact `C_prod`
  `afb766af80ddc28c405b0dd58a7b14b2cc09bc7e`. Its changed-path set is exactly the six declared
  evidence paths. Their hashes are `dependencies.json`
  `86dae2d35b67c44d59b5005a0568e5bf62e9ec4a273855b46948b247181158a2`,
  `wheelhouse-requirements.txt` `a31df8fae7e5088eb460a645828213655c5c37462f63b149bc6d9f3c7620f5d4`,
  `execution-provenance.json` `c50b851ed4bbf75eb61af9cc99eb818e8615b13cbdc92c486719a6d439cf9de6`,
  `independent-green.json` `56f28f8d97de834a826f36f8f8688e40e2db0775cffb2237f5d8ac15b8911bd0`,
  `reconciliation-ledger.md` `038f3b762d89412654c8a5ec7779f7dc16ec00e8cf113c7a18b1ea80996a9b16`,
  and `evidence-lock.json` `c19d197f5d6942af383c3aeb0a811250e89ff648bb9c83d91c7a2f8270845caa`.
  No evidence file names its own commit, and no Fusion project/lock or downstream ref pins it.
- [x] The exact retained C_prod auditor exited 0 and reported `parent_and_paths: PASS`,
  `codegen_reconstruction: PASS`, `fusion_pin: PASS`, and `artifacts_and_lock: PASS`; output
  SHA-256 is `309c5edaea6e454a44cb251a6dea5f4777c9691687d699a8130c697757594c7e`.
  The reconstruction rebuilt the exact C_prod source archive SHA-256
  `adeb753d0aae13c4640c7d9800f88be6e7144f8cac72a6b9078d6e144cc3222a`, history bundle, and real
  wheel SHA-256 `0c86f0285fd30aa01e4c0c64b284125731fcc77fa460dc46c5e943ced20273d9`.
  This proves the production directory-creation regression fixed the historical blocker without
  weakening the artifact boundary. Retained C_prod topology tests passed 18/18.
- [x] All five source artifacts, three project wheels, 177 wheel requirements, 36,741 RECORD
  members, seven evidence-lock entries, 18 independent run records, full Fusion pin, and total
  L-01-L-14/U-1-U-2 ledger were revalidated. `C_evidence` was not built or pinned. Original checkout
  status digests at completion are codegen
  `66c5bcd3d484d5abed8d148694bcc9e0ff57054fbe16b38427bc53977a3762c7`, Agentic/TEAx/1costingfe
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, and preserved dirty Fusion
  `1967be58f0bc8e4c430bccca4255a503dbc5e0fc8258fae7d51304f81298e5ee`. The rollback point is exact
  `C_evidence` `58495607bdf140f1f716aafb95f7122228a4bf52`.
- [x] Independent-audit remediation Phase 10 completed `2026-08-17T13:33:22-07:00`.
  Historical `C_prod` `afb766af80ddc28c405b0dd58a7b14b2cc09bc7e`, `F_final`
  `4fdd78f53334e5a9bcd695259b27afeb0b347f62`, and `C_evidence`
  `58495607bdf140f1f716aafb95f7122228a4bf52`, plus every earlier chain and unaccepted candidate,
  remain historical and were not relabeled. New exact `C_evidence` is clean commit
  `2228c60e8149d760b5cac74bf578ef50716237e0`. Its parent is byte-exact `C_prod`
  `f4d7351355c7dc2ecb575194eea769e9c8fb0db5`, and its changed-path set is exactly the six declared
  evidence paths. It was not built or pinned and does not name itself.
- [x] The committed evidence hashes match staging exactly: `dependencies.json`
  `b1b4282069758d37c4d475c3021e0cc3e0f38d56bb84765ccf9d30964154a102`,
  `wheelhouse-requirements.txt`
  `3657e0000150c94b1be1a9c07fe3d5e29142c5458cf30b73316d58c7aaab8d0c`,
  `execution-provenance.json`
  `8114587daceea57bc92f94f3325653e89f0a09177ed58335fd63c77cd77e4818`,
  `independent-green.json`
  `5fd2b5dc4273d883fda1a2cacbe597bfb951155aa4c1fc3677a1775bf0fd9169`,
  `reconciliation-ledger.md`
  `1777c9eaa71077cfffc6405e0cba214410de5c557d0071c7f6ebdc321b9f92f2`, and
  `evidence-lock.json`
  `eac5ea61da30351aa75ff0124751f1eec81e85bc36ee8c8a1f300ec6222912fe`.
- [x] The exact retained `C_prod` auditor exited 0 and reported `parent_and_paths: PASS`,
  `codegen_reconstruction: PASS`, `fusion_pin: PASS`, and `artifacts_and_lock: PASS`; output
  SHA-256 is `309c5edaea6e454a44cb251a6dea5f4777c9691687d699a8130c697757594c7e`.
  It rebuilt exact C_prod archive SHA-256
  `e86ec56f3340e7eb37c3efc50105a1c4b0fbb408eba012bfc5e5db4aaeb8c37d`, history bundle SHA-256
  `cb2e1e7be0707694bfc83db773d634c40c18d82a26946e2a945af092d04dda2a`, and the real wheel
  SHA-256 `707fbbc730b8f28357cbaa37aebe2a9c2bb1856cf2bf7285b3ea8444ce8e5738`.
  It also proved exact `F_final` `1af570529a7eec489b5e07ea0ab2a02d9cf21eef`, the full C_prod
  project/lock pin, installed-wheel equality, five artifact inputs, seven lock entries, 20 closed
  run records, and total reconciliation. Retained topology test code run from exact C_prod passed
  18/18 after the evidence commit; JUnit SHA-256 is
  `edd34a52308f345ea520fe99e6cb419651bbb71e526a70086ea982beb90aae51`.
- [x] Both implementation worktrees and the evidence worktree are clean. Original status digests at
  completion are codegen
  `17eb7dc21973b210f75e4207beac01498a69cdeff49a2be6f94dd006e007dca4`, preserved dirty Fusion
  `f6a9b1322facdb6ecb7e571981ae571bab5ddf387422957c4739998fc6329d66`, and Agentic/TEAx/
  1costingfe each `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
  The implementation rollback point is exact `C_evidence`
  `2228c60e8149d760b5cac74bf578ef50716237e0`.
- [x] Fresh-audit CI-1/CI-2/CI-3 replacement Phase 10 completed `2026-08-17`. Every preceding
  `A_final`/`C_prod`/`F_final`/`C_evidence` chain and unaccepted evidence candidate remains
  historical and was not rewritten or relabeled. The new exact `C_evidence` is clean commit
  `588d5f7c9013d98c838a376ab9c69c95ef444649`; its parent is byte-exact `C_prod`
  `78a9beb956f9b5a517c08836b067f0cb0dc4ccc6`, and its changed-path set is exactly
  `verification/dependencies.json`, `verification/evidence-lock.json`,
  `verification/execution-provenance.json`, `verification/independent-green.json`,
  `verification/reconciliation-ledger.md`, and `verification/wheelhouse-requirements.txt`. It was
  not built or pinned and does not name itself.
- [x] The committed evidence hashes match staging exactly: `dependencies.json`
  `6130305dd9b88ece748dda7806d93f23d44bf0a011aa3496c7278c15b04fb4a5`,
  `wheelhouse-requirements.txt`
  `cc1d00755a08f3a6873010b1b8f71a06b68f6854c5baa083392ae4effee66e67`,
  `execution-provenance.json`
  `80759c540ca9a2f7f8e01607c67b6bf2d5bac19884a740b97ba2bab1304534a3`,
  `independent-green.json`
  `c21bad8ba7aec759a8f5ee9814cb0811b131db84521ea4c974cb89cf0e80ffb7`,
  `reconciliation-ledger.md`
  `15d7bf4dc774e6982561648bf2d60383316d81e2fa5636290ea3edc301c4f3be`, and
  `evidence-lock.json`
  `8990c8a3384f3eb7169e1b9bc7a4e976eb0ed209a20fe06b44a2106223209232`.
- [x] The exact retained `C_prod` auditor exited 0 and reported `parent_and_paths: PASS`,
  `codegen_reconstruction: PASS`, `fusion_pin: PASS`, and `artifacts_and_lock: PASS`. The real
  reconstruction reproduced codegen source archive SHA-256
  `d64b5396e9ce69db35d7bd5c3afb4c9d634b66841ad09ce9d72cfdc2382ecbc7`, closed history-bundle
  SHA-256 `8dc5c435dc12a5789448a0c5631595be439183bb615de521a04f9446287ce25a`, and wheel SHA-256
  `7ed5002b965594c546f6ad3c2bd066554921b7682ace3dbe7bf9c66b3e278aaa`.
  It also proved exact `F_final` `028f98741a2aea7c238beed961402857af82d15f`, full-SHA project/lock
  pins, installed-wheel equality, five immutable artifact inputs, seven lock entries, 20 closed run
  records, and total reconciliation. Retained topology test code run from exact `C_prod` passed
  18/18 after the evidence commit; JUnit SHA-256 is
  `e23525626a07e7c56c61dc7c4a3ad8328a5d30f1c042e81b16f8f78032f46f3b`.
- [x] Agentic, codegen production, Fusion, and evidence implementation worktrees are clean at their
  exact identities. Original status digests at completion are codegen
  `dc0b9214d55309ff68c3e082505e10ea6c6609c888b6c5ac8cfac5795b1a9e4b`, preserved dirty Fusion
  `57fbdc0c302220e538f7978b85752d9278e17b6e19405482b526ce6857cf4618`, and Agentic/TEAx/
  1costingfe each `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
  The implementation rollback point is exact `C_evidence`
  `588d5f7c9013d98c838a376ab9c69c95ef444649`.

## Risk Management

- **Probe premise failure:** Phase 2 has literal stop conditions. Preserve the contrary measurement
  and return to design; do not reinterpret it during implementation.
- **Dirty working directories:** existing changes belong to the owner. Dedicated clean worktrees and
  source archives isolate implementation and evidence. A status-digest change fails the phase.
- **Public-boundary split:** strict/lenient and live/admitted/snapshot tests must all observe the same
  typed conversion. Static caller tests prevent a second bridge.
- **Vacuous green:** closed corpus counts, slow-marker selection, license checks, execution-marker
  selection, declared skip lists, import-root checks, and output mutation counts are gates.
- **Artifact drift:** every archive/wheel is named by full commit and SHA-256. A changed build output
  invalidates dependent Fusion and evidence rather than updating one hash in isolation.
- **Fusion model churn:** immutable-stack validation decides whether a model edit is justified. A
  dependency, lock, harness, or implementation defect is fixed in its owning repository.
- **Evidence cycle:** `C_evidence` changes exactly six files, has parent `C_prod`, never names itself,
  and is never built, certified, or pinned downstream.

## Cleanup Expectations

- [x] Keep all immutable archives, wheels, wheelhouse files, private command logs, JUnit reports, and
  staged evidence until the fresh audit finishes.
- [x] Remove only item-created temporary worktrees/extractions after confirming their exact recorded
  paths and that every required commit has a durable ref. Never remove, clean, or reset an existing
  checkout. No implementation worktree or extraction was removed before audit.
- [x] Remove temporary virtual environments and generated output directories only after their hashes
  and required results are locked and audited. Generated outputs under a user checkout are out of
  bounds. No retained environment or required generated output was removed before audit.
- [x] Do not delete or rewrite failed gate/evidence records. Retain them as the measured reason for a
  new design or production identity.

## Handoff

The latest independent audit in `audit.md` returned **Needs Work**. The exact commit topology,
deterministic artifacts, both Fusion roots, and all four retained auditor groups reproduce, and the
six first-audit findings remain fixed on their intended routes. Certification remains blocked by
product-lens `audit3-F1`, public B3/B4/deep-target/B9 fallbacks, final run records assembled outside
the committed runner. The settled owner decision above permanently retires the Agentic PDF suite;
it is not a blocker and must not be run. Do not run `$my-close` or `$my-pre-pr`.
Run targeted `$my-design-review` confirmation on Revision 6, then replace this plan if the review
approves it.

**Historical status:** Ready for implementation → In Progress → Implemented → Audit Needs Work →
Remediated → Fresh Audit Needs Work → Remediated Again → Fresh Independent Audit Needs Work →
Superseded by draft Design Revision 6
