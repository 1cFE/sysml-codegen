# Implementation Plan: Self-Binding Replacement

**Status:** Complete (all five phases, 2026-08-16) — awaiting `/_my_audit`
**Created:** 2026-08-16
**Last Updated:** 2026-08-16
**Home Repo:** `/home/reid/1cfe/sysml-codegen`
**Scope:** agentic-mbse, sysml-codegen, fusion-tea, and read-only stellarator triage
**Delivery:** Local commits only. No push and no pull request.

## Source Documents

- **Spec:** [spec.md](spec.md)
- **Design:** [design.md](design.md) — component details, decisions, invariants, and risks
- **Current reviews:** [spec-review.md](spec-review.md), [design-review.md](design-review.md)
- **Measured behavior:** [spike/findings.md](spike/findings.md),
  [verification/post-repair-spike-recheck.md](verification/post-repair-spike-recheck.md)
- **Exact-owner dependency:**
  [anchoring spec](../../completed/20260816_qualified-reference-occurrence-anchoring/spec.md)

## The Point

`in availability = availability` looks as though it passes an owning part's modelled value into a
calculation. It actually binds the calculation input to itself, so the intended value never arrives.
The exact route now refuses that shape, which leaves the fusion-tea whole-plant model unable to
generate and leaves published authoring guidance teaching examples the product rejects.

This work makes the rule usable end to end. Authors and agents learn which form matches where the
value lives. Both validation paths reject the wrong form without rejecting supported owner-qualified
references. The fusion-tea model is changed mechanically to the ratified D-5 form. The deciding proof
is public behavior: an off-default design value reaches every and only its bound consumers.

## Plan-Time Facts and Boundaries

| repo | plan-time state | implementation boundary |
|---|---|---|
| `sysml-codegen` | `main` at `0f89673`; project artifacts and separate anchoring work may be dirty | Preserve unrelated changes. Stage and commit only self-binding paths. |
| `agentic-mbse` | clean `main` at `1decd95` | Use a dedicated local branch or worktree. Do not edit codegen's installed data copy. |
| `fusion-tea` | `item8-fusion-embedded-catalog` at `be1ee7c0`, 6 commits ahead of `main`, with user changes | Create an isolated worktree/branch from this HEAD. Do not stash, reset, or absorb the dirty tree. |
| `fusion-tea-stellarator-mbse-demo` | `feat/stellarator-mbse-demo` at `7781721b`, dirty | Read-only. Record status before and after the single run; make no edits. |

The D12 census found two byte-identical six-file fusion-tea model sets. Each has 15 binding-side and
15 declaration-side edits. The implementation scope is therefore 12 tracked files and 60 line
rewrites. Re-run the census and pair hashes before writing; discovery remains authoritative.

The installed `agentic_mbse_data` documents are copied package data, not hardlinks. Per
[design.md#key-decisions](design.md#key-decisions), documentation tests use
`agentic_mbse.cli.get_docs_dir()` and a separate built-wheel contract. No test asserts inode or link
count.

ADR-010 is not a plan input. Arrayed-owner aggregation remains under
`[ANCHORING-ARRAYED-DIAGNOSTIC]`. Do not expand either into this item.

## Implementation Strategy

**Phasing rationale:** First make the two validation paths truthful and all later failures legible.
Then retain the exact-route evidence and make the migration tool safe. Publish guidance only after
its examples have executable witnesses. Migrate the customer last, after the separate exact-owner
evidence gate closes. Run stellarator after the final diagnostic behavior exists.

**Critical path:** F-3 named diagnostic → D5 preconditions and reversible tool → anchoring evidence
gate → dual-tree customer migration → live/snapshot generation → 11-supplier enumeration and two
public mutations.

**First proof point:** `s4a_qual_one_occ` passes agentic validation while a real self-binding still
fails, and `s5_sibling_formal` returns a named cycle diagnostic with participants instead of a raw
`GraphValidationError` traceback.

**Overall validation:** Every phase begins with a failing or precondition test. License-free checks
run first. Licensed checks source `/home/reid/1cfe/agentic-mbse/.env`; a run that skipped for lack of
`SYSIDE_LICENSE_KEY` does not count. Record pre-existing full-suite failures before changing code and
require no new failures.

---

## Phase 1: Make Failures Legible and Validators Agree

### Goal

Fix F-2 in agentic-mbse and F-3 in codegen. Preserve unconditional refusal of a genuine self-binding,
accept a supported usage-qualified reference by referent identity, and convert producer cycles into
stable authored-model diagnostics. See [design.md#key-decisions](design.md#key-decisions), D6 and D7,
and [design.md#implementation-notes](design.md#implementation-notes).

### Assumption Under Test

The agentic false positive can be removed by comparing SysIDE element identity without spelling
special cases. The cycle repair fits inside graph cycle validation plus the existing elaboration
boundary; it does not require a new graph layer or change non-cycle invariant failures.

### Test Stencil — Write First

```python
def test_supported_qualified_binding_is_not_self_named():
    issues = check_self_named_bindings(load_fixture("usage_qualified_local"))
    assert L2_SELF_NAMED_BINDING not in codes(issues)

def test_sibling_formal_cycle_is_a_named_model_diagnostic():
    result = run_exact_route("sibling_formal_cycle")
    assert result.exit_code == 1
    assert "typed producer dependency cycle" in result.stderr
    assert "Traceback" not in result.stderr
```

### Changes Required

**Agentic-mbse — test first**

- [x] Add a retained usage-qualified local fixture under
  `tests/fixtures/item12/usage_qualified_local/`, based on `s4a_qual_one_occ` but owned by this repo.
- [x] Extend `tests/test_validation/test_item12_checks.py` with both directions: the qualified
  referent is accepted; existing `self_named_deadend`, `self_named_trap`, and `self_named_rescue`
  remain `L2_SELF_NAMED_BINDING` errors.
- [x] Change `src/agentic_mbse/validation/level2_structure.py` to compare the value-expression
  referent element with the bound input member, not `source_path == param_name`.
- [x] Change `src/agentic_mbse/sysml/binding.py` only if the exact referent is not already reachable
  at the validator boundary. Keep any new data identity-bearing; do not add a qualified-string flag.
  *(Not needed: the referent is reachable from the calc usage's own parameter members at the
  validator boundary; `binding.py` is unchanged.)*

**Sysml-codegen — test first**

- [x] Promote the `s5_sibling_formal` shape into a retained fixture under
  `tests/fixtures/sibling_formal_cycle/` with `PROVENANCE.md`; do not make tests depend on an active
  project directory.
- [x] Add `tests/conformance/test_elaboration_cycle_diagnostics.py` covering CLI/error-boundary
  behavior and deterministic participant detail.
- [x] Add a graph-level test in `tests/conformance/test_elaboration_identity_collisions.py` that
  builds a producer cycle and asserts the diagnostic carries every cycle participant once, in
  stable order.
- [x] Update `src/sysml_codegen/elaboration/graph.py::_validate_producer_cycles` to retain the active
  path or use an equivalent contained traversal that can name the cycle.
- [x] Update `src/sysml_codegen/elaboration/elaborate.py` so `GraphValidationError` from final graph
  validation becomes `ElaborationDiagnosticError`; keep internal graph-integrity diagnostics
  distinguishable from the authored binding-cycle diagnostic.

Stop and file an owned follow-up if either repair needs a new resolution architecture, a shared
validator implementation, or broad graph-layer restructuring. Do not grow this phase silently.

### Validation

**Automated**

- [x] Agentic targeted tests:
  `uv run pytest tests/test_validation/test_item12_checks.py tests/test_validation/test_level2_integration.py`
  — 28 passed (21 + 7), including the new acceptance test; the three self-named fixtures still fail.
- [x] Codegen targeted tests:
  `uv run --extra dev pytest tests/conformance/test_elaboration_cycle_diagnostics.py tests/conformance/test_elaboration_identity_collisions.py`
  — 7 passed; all 4 new tests were red pre-repair for the expected reasons.
- [x] Existing refusal checks:
  `uv run --extra dev pytest tests/conformance/test_elaboration_spike_parity.py tests/conformance/test_cli_snapshot_refusal.py`
  — 21 passed (18 + 3), license loaded.
- [x] Lint changed Python in both repos; run each repo's documented Ruff command.
  — Ruff clean on all changed files in both repos; mypy findings for the changed agentic file are
  line-identical to `main`'s; codegen `mypy src/` = 52 errors in 11 files, the recorded pre-existing
  baseline, none in `elaboration/`.

**Manual / licensed**

- [x] Source the SysIDE license and run the retained qualified fixture through agentic validation.
  Confirm success and no `L2_SELF_NAMED_BINDING`.
  — `validate_structure` over the fixture: `success=True`, zero issues; `self_named_trap` still
  refuses with exactly one `L2_SELF_NAMED_BINDING`.
- [x] Run the retained cycle fixture through `sysml-codegen generate`. Confirm exit 1, a named
  binding/cycle diagnostic with participants, no traceback, and no generated package.
  — Exit 1; stderr: `Model failed exact-route validation: SI_EDGE_DANGLING:
  sibling_formal_cycle__plant__revenue_calc: typed producer dependency cycle:
  sibling_formal_cycle__plant__revenue_calc`; zero `Traceback` lines; output directory not created.

**What We Know Works After This Phase:** Both paths reject only the true self-binding in this family,
and a D-5 collision fails in a form a model author can act on.

---

## Phase 2: Pin the Evidence and Build the Safe Migration Tool

### Goal

Turn the surviving definition-owned D-6 measurements into retained conformance evidence and extend
the D-5 tool to operate safely on an external, duplicated customer tree. See
[design.md#component-overview](design.md#component-overview), D3–D5, and Required Invariants 3–5.

### Assumption Under Test

The three definition-owned outcomes remain stable on the shipped route. A root-parameterized tool
can prove rename-only edits and refuse every known collision, overreach, and aggregation hazard
before customer files are replaced.

### Test Stencil — Write First

```python
def test_external_dual_tree_migration_is_reversible(tmp_path):
    customer = copy_dual_tree_fixture(tmp_path)
    result = build_variant(root=customer, formals=EXPECTED_FORMALS)
    assert result.preconditions == []
    assert strip_check(result.originals, result.variant) == []
    assert paired_model_files(result.variant) == byte_identical_pairs()

def test_aggregation_or_sibling_formal_stops_before_write(tmp_path):
    assert migrate(hazard_fixture(tmp_path)).exit_code == 1
    assert tree_bytes(tmp_path) == bytes_before_run
```

### Changes Required

**Definition-owned evidence — test first**

- [x] Promote `s4b_qual_two_occ`, `s8_qual_outside_two`, and `s6_qual_sibling_scope` from the spike
  into named `tests/fixtures/` directories, each with `PROVENANCE.md` identifying the leaf as
  definition-owned. *(`def_qual_two_occ_inside`, `def_qual_two_occ_above`,
  `def_qual_sibling_scope`; packages renamed to match, shapes unchanged.)*
- [x] Add `tests/conformance/test_definition_owned_reference_positions.py`:
  two occurrences inside the definition generate with per-occurrence values; two occurrences above
  the definition refuse with `SI_OCCURRENCE_AMBIGUOUS`; the sibling-scope case reaches 7.0 and is
  explicitly labelled as positional fallback, not checked author intent.

**Migration tool — test first**

- [x] Extend `tests/conformance/test_d5_variants.py` with external-root, no-write-on-failure, and
  duplicated-tree tests.
- [x] Add one test for each D5 precondition: a sibling member of the old bare name, an existing
  `<name>_in`, an unrelated calc usage with the same left-side name, and any
  `aggregation_rewrites()` match.
- [x] Add pairwise-byte tests for the six logical paths and assert the expected 30 rows per copied
  model set. The test fixture may duplicate the vendored fusion model under `tmp_path`; it must not
  depend on `/home/reid/1cfe/fusion-tea`. *(The 30 census rows are asserted as 15 binding + 15
  declaration rows per set; expression uses inside declaring blocks rename with their formal, and
  every changed line must revert by stripping `_in` alone.)*
- [x] Extend `scripts/make_d5_variant.py` with `--root`, explicit discovery/precondition output, a
  scratch destination, and the aggregation guard. Keep `--formals` explicit for non-corpus roots.
- [x] Update the script docstring: customer mode builds a scratch variant and later replaces
  originals only after the strip check; it does not promise that the final customer operation never
  touches originals.

### Validation

**License-free**

- [x] `uv run --extra dev pytest tests/conformance/test_d5_variants.py` — 29 passed (20 existing +
  9 new).
- [x] Run every hazard case with a before/after tree digest; all refuse and leave the tree unchanged.
  — Each precondition test runs `main()` end to end and asserts exit 1, no scratch tree created,
  and a byte-level tree digest unchanged.
- [x] Run `--root` against a temporary duplicate of `tests/fixtures/fusion_tea`; strip check reports
  zero problems and all paired paths remain byte-identical. — The closed-loop test strips the
  vendored fixture's renames to reconstruct the pre-migration shape, duplicates it into both model
  sets, migrates, and requires byte-identity with the vendored fixture per file plus cross-set pair
  identity; the CLI test drives the same pipeline through `--root/--scratch/--formals` (exit 0,
  census printed, `preconditions: clear`, `strip check: 0 problems`).

**Licensed**

- [x] `uv run --extra dev pytest tests/conformance/test_definition_owned_reference_positions.py`
  — 3 passed.
- [x] Re-run `tests/conformance/test_usage_owned_reference_anchoring.py` beside the new tests so the
  evidence visibly covers both owner classes without conflating them. — 80 passed together
  (48 anchoring + 3 definition-owned positions + 29 d5), license loaded.

**What We Know Works After This Phase:** Every situation the guidance will teach has a labelled
exact-route witness, and the migration mechanism stops before any known rename hazard or non-rename
transformation can reach customer files.

---

## Phase 3: Publish One Guidance Story and Enforce Drift

### Goal

Make `plant-idiom.md` the one full situational rule, update every live agent/template surface, review
all existing qualified examples against exact-owner behavior, and turn example provenance and
package inclusion into tests. See [design.md#the-teaching-organized-by-situation](design.md#the-teaching-organized-by-situation),
D1–D3, D9, and D11.

### Assumption Under Test

One authoritative source plus three short summaries reaches authors and agents without creating a
second rule copy. The public docs resolver and built-wheel contract cover both editable development
and installed-package consumption.

### Test Stencil — Write First

```python
def test_marked_guidance_examples_equal_their_fixture_sources():
    doc = (get_docs_dir() / "patterns/plant-idiom.md").read_text()
    for example in marked_examples(doc):
        assert example.text in cited_fixture(example).read_text()
        assert example.owner_class in {"usage", "definition", "n/a"}

def test_built_wheel_contains_authoritative_guidance_bytes(tmp_path):
    wheel = build_wheel(tmp_path)
    assert wheel_member(wheel, PACKAGED_PLANT_IDIOM) == SOURCE_PLANT_IDIOM.read_bytes()
```

### Changes Required

**Agentic-mbse — tests and authority first**

- [x] Add `tests/test_packaged_guidance_contract.py` before editing docs. It must exercise
  `get_docs_dir()` in editable mode and inspect a built wheel for byte-identical
  `agentic_mbse_data/docs/patterns/plant-idiom.md`; do not inspect inode counts.
- [x] Rewrite `docs/patterns/plant-idiom.md` around where the value lives: D-5 for the same owning
  part, D-7 for another part, D-6 split by resolved owner class, and the refused self-binding.
- [x] Correct the four worked refused examples and add machine-readable provenance markers to each
  pinned fenced block. Label the three measured-but-unpinned shapes honestly, as required by
  Invariant 3. *(Two remain `@measured` — the inherited-attribute D-5 case and the EXPOSE + D-5
  case; the attribute-rename spelling turned out to exist verbatim in `wi014_toy`, so it is
  `@pinned` rather than merely labelled, which exceeds the invariant.)*
- [x] Review and record all 13 positive usage-qualified sites in
  `docs/patterns/expose-pattern.md`, `docs/patterns/cross-file-binding.md`,
  `docs/patterns/adr002-calculations.md`, `docs/patterns/syntax-reference.md`, and
  `project_templates/MODELING_PROCESS.md.template`. Retain only exact-usage-owner intent; give the
  local-collision template D-5 as the recommendation and D-6 only as a labelled alternative.
  *(11 retained — each qualifies the enclosing part usage and intends that usage's own feature;
  the two template sites are rewritten to D-5 with the supported D-6 spelling kept as a labelled
  prose alternative. Dispositions are pinned in the codegen contract test.)*
- [x] Confirm the three existing “won't resolve” examples in `syntax-reference.md`,
  `cross-file-binding.md`, and `common-mistakes.md` remain negatives and do not need invented edits.
- [x] Add the short rule and authoritative pointer to
  `claude/skills/sysml-conventions/SKILL.md`,
  `project_templates/MODELING_PROCESS.md.template`, and
  `project_templates/MODELING_GUIDE.md.template`.
- [x] Record the plan-time `.claude/` zero-edit inventory in test data or assertions. Do not create a
  counterpart solely to make both trees look symmetrical.

**Sysml-codegen — test first**

- [x] Add `tests/conformance/test_self_binding_guidance_contract.py`. Resolve the doc through
  `agentic_mbse.cli.get_docs_dir()`, parse only explicitly marked examples, verify owner labels, and
  compare the exact snippet with the cited codegen fixture/test source. *(Comparison is
  whitespace-normalized, order-preserving line containment, so doc excerpts may dedent but not
  reword; 7 of the 9 tests were red against the pre-rewrite tree.)*
- [x] Add a single-authority assertion and a zero-unmarked-self-binding sweep across agentic-mbse's
  `claude/`, `.claude/`, `docs/patterns/`, and `project_templates/` trees.
- [x] Add the `SI_SELF_BINDING` row to `docs/architecture/modeling-assumptions.md`. Point to the
  authoritative plant idiom; do not create ADR-010 or a product-ledger row.

### Validation

**Automated**

- [x] Agentic package and validation contracts:
  `uv run pytest tests/test_packaged_guidance_contract.py tests/test_validation/test_item12_checks.py`
  — 23 passed (2 + 21), re-run green after the branch relocation.
- [x] Codegen drift contract:
  `uv run --extra dev pytest tests/conformance/test_self_binding_guidance_contract.py`
  — 9 passed against the relocated branch (7 red pre-rewrite).
- [x] Run the owner-class conformance tests from Phase 2 with the drift contract.
  — 92 passed combined (drift 9 + positions 3 + anchoring 48 + d5 29 + cycle diagnostics 3).
- [x] Run agentic Ruff over `src/` and `tests/`; run codegen Ruff over changed Python.
  — Codegen changed files clean. Agentic `ruff check src/ tests/` under the main checkout's
  ruff 0.14.11 reports 121 findings, byte-identical between clean `main` and the branch — a
  pre-existing venv-version backlog, zero introduced. (The Phase-1 worktree venv's ruff was
  clean on the changed files.)

**Inventory guards**

- [x] The corrected PCRE2 self-binding search returns zero unmarked worked examples across all four
  source areas. Explicit refused-by-design fixtures and prose counterexamples remain allowed.
  — The only match is the marked trap excerpt inside the authoritative doc; prose warnings carry
  no statement terminator. Pinned by the sweep test.
- [x] The owner-qualified search returns the same 13 positive sites, each with a recorded exact-owner
  disposition, plus the same three deliberate negatives.
  — Post-review inventory: 11 of the 13 retained in place; the 2 template sites rewritten to D-5
  per the owner's D11 ruling (disposition recorded in the contract test's pinned table); plus 4
  new `@pinned` qualified examples inside the authoritative doc itself; the 3 negatives
  unchanged. The contract test pins exactly this end state.
- [x] Build the agentic wheel in a temporary directory and compare the packaged marked doc bytes with
  the source. Delete only the temporary build directory after the comparison.
  — `test_built_wheel_carries_the_authoritative_guidance_bytes` builds into pytest `tmp_path`
  (auto-cleaned) and compares bytes; green before and after the rewrite.

**What We Know Works After This Phase:** Humans, initialized projects, and the live SysML agent skill
receive one consistent rule; every pinned example is checked against the route that gives it meaning;
and installed package data cannot silently omit or stale the authoritative document.

---

## Phase 4: Migrate Both Fusion-Tea Trees and Prove the Public Spine

### Goal

Apply the D-5 migration to both synchronized customer model sets, prove the diff is rename-only,
generate/seal/snapshot with zero readiness diagnostics, and demonstrate every-and-only value arrival
through shipped `inputs/*.json` and `pipelines/pipeline.yaml`. See
[design.md#the-migration-as-a-pipeline-with-a-proof-in-the-middle](design.md#the-migration-as-a-pipeline-with-a-proof-in-the-middle)
and [design.md#the-spine](design.md#the-spine).

### Entry Gate

- [x] The separate anchoring item's current re-verification records a certified result for the
  exact-owner premise. If it still says Needs Work, stop before customer migration and surface it;
  do not silently substitute an older audit. A direct runtime suite may substitute only with owner
  approval recorded in the implementation notes.
  *`[OWNER 2026-08-16]` stated at Phase 2 kickoff that the anchoring item was certified. Confirmed
  against the artifact at Phase 4 start: the item is archived at
  `.project/completed/20260816_qualified-reference-occurrence-anchoring/` and its `audit.md`
  header reads **Verdict: Certify** with the final reconciliation superseding the earlier
  Needs Work outcome.*
- [x] `tests/conformance/test_usage_owned_reference_anchoring.py` and the full codegen baseline are
  green at the implementation commit. — 48 anchoring nodes green in the Phase-3 combined run;
  full baseline 17 pre-existing / 2170 passed at `20a8bb7`.
- [x] An isolated fusion-tea worktree/branch exists from `be1ee7c0`; the original dirty worktree is
  unchanged. — `/home/reid/1cfe/fusion-tea-self-binding`, branch `self-binding-replacement` from
  `be1ee7c0`; the original tree's 22 dirty entries verified unchanged after the run.

### Assumption Under Test

The current post-R-2 customer model still has two byte-identical six-file sets, the expected 11
renamed suppliers, and no D5 precondition hazard. Public generation artifacts expose enough
information to prove both exact source classification and every-and-only consumer wiring without
TEAx execution.

### Test Stencil — Write First

```python
def test_migrated_hif_public_spine(tmp_path):
    baseline = generate_live(MIGRATED_MODELS, tmp_path / "baseline")
    assert baseline.entry_point_counts == {"all": 23, "design_attribute": 18}
    assert renamed_supplier_keys(baseline) == EXPECTED_ELEVEN

    gain = generate_mutation(MIGRATED_MODELS, "gain", 81.0, tmp_path / "gain")
    assert changed_entry_points(baseline, gain) == {GAIN_KEY}
    assert wired_consumers(gain, GAIN_KEY) == {LCOE, RECIRC, VIABILITY}
```

### Changes Required

**Fusion-tea integration proof — write first**

- [x] Add `tests/models/test_self_binding_replacement.py`. Work only on copies under `tmp_path`.
  The test captures a snapshot, generates live and from snapshot, compares package bytes, and makes
  gain/beam mutations on separate scratch copies. It must never rewrite tracked models while
  running. *(Red pre-migration: the 15 `SI_SELF_BINDING` findings, site for site with Appendix A.
  License required and asserted — the suite fails, never skips, without the key.)*
- [x] Encode two separate oracles so their scopes cannot be conflated:
  - Full classification: 23 total entry points, 18 `DESIGN_ATTRIBUTE`.
  - Renamed-supplier sub-oracle: the exact 11 keys below.
- [x] Assert the seven non-renamed design attributes separately: nested driver `efficiency`,
  `energy`, `lifetime_shots`, `pulse_rate_ref`; chamber `blanket_energy_multiple` and
  `yield_cost_constant`; target factory `cost_per_target`.
- [x] For gain, assert the one key changes, no other input value changes, and exactly the two calc
  modules plus the viability constraint module wire to it. Assert the constraint's
  `formal_identity`, not only its rendered module name. *(The catalog entry's `predicate_ir`
  carries `fusion_cycle::'Viability Threshold'::gain_in`; the module input formal is `gain_in`.)*
- [x] For nested `beam_energy_mj`, assert only the nested key changes and enumerate every bound
  consumer. Do not weaken this to “the package still generates.”
  *(Exactly `hif_plant_pkg__hif_plant__driver__meier_cost` via `beam_energy_mj_in`.)*

**Exact 11 renamed-supplier keys**

```text
hif_plant_pkg__hif_plant__availability
hif_plant_pkg__hif_plant__discount_rate
hif_plant_pkg__hif_plant__frequency
hif_plant_pkg__hif_plant__gain
hif_plant_pkg__hif_plant__net_electric_power_gw
hif_plant_pkg__hif_plant__om_cost_constant
hif_plant_pkg__hif_plant__plant_cost_constant
hif_plant_pkg__hif_plant__thermal_efficiency
hif_plant_pkg__hif_plant__thermal_power_gw
hif_plant_pkg__hif_plant__driver__beam_energy_mj
hif_plant_pkg__hif_plant__driver__num_chambers
```

**Customer migration — only after the red integration test and preconditions**

- [x] Re-run D12 over both model roots. Require 30 exact self-binding hits, 30 declaration rows,
  12 tracked affected files, and six byte-identical corresponding pairs. A different result stops
  the phase. *(Measured: 30 hits — 10+2+3 per set; 15 declaration blocks per set via
  `discover_sites`; 12 tracked files; all six pairs hash-identical. One layout discovery: the
  exploration set stores the library files at `analyses/`, `cost_structure/`, `foundation/`
  without the `library/` prefix — pair contents identical, paths differ. Census authoritative
  per D12; the replace list below uses the census paths.)*
- [x] Run D5(a)–(d) over the live files. Save the license-free precondition output in the Phase 4
  completion notes. *(Both sets: `preconditions: clear`; full discovery + precondition + strip
  output saved as `verification/phase4-d5-models.log` and `verification/phase4-d5-exploration.log`.)*
- [x] Use `make_d5_variant.py --root ... --formals ...` to build scratch variants for both model
  sets. Run the strip check while originals and variants both exist. *(Two runs, one per set
  root, `--formals` = the 11 names; `strip check: 0 problems` in both while both trees existed.)*
- [x] Replace only these six paths under each root, for 12 files total:
  - `designs/generic_ife/ife_plant.sysml`
  - `designs/hif_ife/hif_driver.sysml`
  - `designs/hif_ife/hif_plant.sysml`
  - `library/analyses/ife_lcoe.sysml`
  - `library/analyses/hif_economics.sysml`
  - `library/analyses/fusion_cycle.sysml`

  *(Under the exploration root the last three live at `analyses/*.sysml` — same six logical
  files, census paths.)*
- [x] Assert 30 binding left sides and 30 formal declarations now carry `_in`, exact self-binding
  hits are zero in both customer model roots, and every corresponding file pair remains
  byte-identical. *(15+15 binding rows, 15+15 declaration rows, 0 self-binding hits, six pairs
  byte-identical.)*
- [x] Review the diff mechanically: stripping `_in` from the 12 migrated files reproduces all 12
  pre-migration files byte for byte. No arithmetic, literal, comment, formatting, or physics edit is
  allowed. *(All 12 `strip OK` against `git show HEAD:` bytes.)*

### Validation

**License-free migration proof**

- [x] D12 census, D5(a)–(d), strip check, pair hashes, and zero-self-binding guard all pass.

**Licensed public proof**

- [x] `uv run pytest tests/models/test_self_binding_replacement.py -v` in the isolated fusion-tea
  worktree with `SYSIDE_LICENSE_KEY` loaded; no license skip is accepted. — **8 passed**; the
  module fixture hard-fails without the key.
- [x] Generate the migrated `models/` tree into a temporary output. Confirm zero readiness
  diagnostics and the generated package contains a valid model and package contract; `generate`
  performs the seal, so do not re-seal or edit generated files. — Covered by the suite (every
  test generates into pytest temp dirs; `run_codegen` returned True = generated and sealed, zero
  diagnostics; oracles read `model_contract.json`).
- [x] Capture a v6 snapshot, generate from it into a second temporary output, and compare the two
  generated package trees byte for byte. — `test_live_and_snapshot_generation_are_byte_identical`.
- [x] Read the 23/18 full oracle and exact 11-key sub-oracle from public artifacts, then run both
  off-default mutations. TEAx execution is out of scope. — Oracles read from
  `contracts/model_contract.json` + `inputs/*.json`; consumers from `pipelines/pipeline.yaml`;
  gain 80→81 and nested beam 5.0→6.5 both proved every-and-only.
- [x] Run the existing fusion-tea model tests and Ruff on the new test file. Record any pre-existing
  failures separately; introduce none. — Full worktree suite: 58 failed / 376 passed / 58 skipped.
  The 14 `tests/models/{test_foundation,test_power_balance}` failures are **byte-identical with
  the migration stashed** (pre-existing on `be1ee7c0`; they expect a model tree this branch does
  not carry); the 44 `tests/scoring_v2/` failures read no model files. Zero introduced. Ruff on
  the new test file clean after an import-sort autofix.

**What We Know Works After This Phase:** Both customer trees carry only the intended rename, the
whole-plant model generates and seals identically live or from snapshot, and mutations at two
occurrence depths reach every and only their intended public consumers.

---

## Phase 5: Stellarator Triage and Integrated Certification

### Goal

Observe the final exact route once on stellarator, record the actionable result without fixing that
repository, and certify the changed repos together. See D10 and
[design.md#validation-approach](design.md#validation-approach).

### Assumption Under Test

The finished diagnostic boundary makes the stellarator failure class and count recordable without a
traceback or model edits. The three changed repositories pass their targeted and full regression
checks together.

### Test Stencil — Write First

```python
before = capture_git_state(STELLARATOR_REPO)
result = run_exact_generate(STELLARATOR_REPO / "models", temporary_output)
after = capture_git_state(STELLARATOR_REPO)

assert before == after
assert triage_record.names(result.command, result.exit_code)
assert triage_record.names(result.first_diagnostic, result.count, result.follow_up)
```

### Changes Required

- [x] Create `.project/active/self-binding-replacement/stellarator-triage.md` with the model root,
  exact command, repo HEAD/status before and after, exit code, first diagnostic class, diagnostic
  count, whether a traceback appeared, and the owning follow-up/vehicle.
- [x] Run `sysml-codegen generate` once over
  `/home/reid/1cfe/fusion-tea-stellarator-mbse-demo/models` into a new temporary directory. Do not
  retry after editing the model; triage is the outcome. — Exit 1, exactly **114
  `SI_SELF_BINDING`** findings (the only class), zero tracebacks, nothing written; no retry.
- [x] If the result is not already covered by a named backlog item, add one concise row to
  `.project/backlog/BACKLOG.md` with an owner and vehicle. Do not add repair instructions to the
  stellarator repository. — No live row existed; `[STELLARATOR-D5-MIGRATION]` filed at P2,
  unowned, hold preserved. Nothing was added to the stellarator repo.
- [x] Fill the completion notes below with cross-repo commits, validation counts, known pre-existing
  failures, and any approved deviations.

### Validation

**No-mutation proof**

- [x] Stellarator HEAD, tracked diff, and untracked-file inventory are byte-for-byte/line-for-line
  unchanged before versus after the one run. — HEAD `7781721b` + branch, 3-entry status, 13-line
  tracked diff, 73-file untracked inventory: all four compared equal.
- [x] The triage record has every required field and names a follow-up when the run refuses.
  — `stellarator-triage.md`; follow-up `[STELLARATOR-D5-MIGRATION]`.

**Cross-repo automated checks**

- [x] Agentic targeted tests, then `uv run pytest tests/`. — 23 targeted (packaged + item12);
  full suite **1834 passed / 1 skipped / 33 deselected**, zero failures, at `3e9734b`.
- [x] Agentic `uv run ruff check src/ tests/` and `uv run mypy src/`. — Ruff 121 findings and
  mypy **95-in-20**, both **byte-identical between clean `main` and the branch** under the main
  venv's tool versions: pre-existing backlog, zero introduced.
- [x] Codegen targeted Phase 1–3 conformance tests, then licensed
  `uv run --extra dev pytest tests/`. — Final-state battery (cycle diagnostics, identity
  collisions, positions, d5 variants, guidance contract, anchoring, spike parity, CLI refusal):
  **117 passed**. Full licensed suite at `20a8bb7`: **17 failed / 2170 passed / 34 skipped /
  88 deselected**, zero license skips — the same 17 pre-existing missing-`pandas` failures.
- [x] Codegen `uv run --extra dev ruff check src/` and `uv run --extra dev mypy src/`. — Ruff
  src clean; mypy **52-in-11**, the recorded pre-existing baseline, none in `elaboration/`.
- [x] Fusion migration/spine test, existing `uv run pytest tests/`, and Ruff over changed Python.
  — Spine 8 passed; full worktree suite 58 failed / 376 passed / 58 skipped, all 58 pre-existing
  (14 models-family proven byte-identical with the migration stashed; 44 scoring_v2
  model-independent); Ruff clean on the new test file.
- [x] `git diff --check` in every changed repository. — Clean in codegen, agentic, and the
  fusion worktree.

**Delivery checks**

- [x] Review each repository's final diff against its phase-owned paths. Preserve every unrelated
  user change. — Codegen: three code commits touch only elaboration/, scripts/, docs/, tests/
  paths owned by Phases 1–3; the concurrent anchoring session's staged archival (81 files,
  including its repoints inside this item's `spec.md`, `product-lens.md`, and `CURRENT_WORK.md`)
  is left staged and uncommitted for its owning session. Agentic: two commits on the dedicated
  branch; main checkout diff-clean. Fusion: one commit, 12 model files + the test; `uv.lock` and
  the scoring-test-rewritten `concepts.json` left uncommitted. Stellarator: zero changes.
- [x] Create path-scoped local commits in agentic-mbse, sysml-codegen, and the isolated fusion-tea
  worktree. Record hashes here. Do not commit anything in stellarator.
  — **agentic-mbse** (branch `self-binding-replacement`): `6e7bf5c` (F-2), `3e9734b` (guidance).
  **sysml-codegen** (local `main`): `00825a1` (F-3), `816d35e` (D-5 tool + evidence),
  `20a8bb7` (drift contract), plus the Phase-5 docs commit recorded in CURRENT_WORK.
  **fusion-tea** (worktree branch `self-binding-replacement`): `9e1ff87b` (migration + spine).
  **stellarator**: nothing.
- [x] Confirm no push or pull request was created. — No `git push` and no PR anywhere this item;
  all commits are local.

**What We Know Works After This Phase:** The documented rule, validation behavior, migration tool,
customer model, and public mutation proof agree. Stellarator's remaining work is named without
reversing its hold.

---

## Environment Setup

See each repository's `CLAUDE.md` for the authoritative commands.

- Source `/home/reid/1cfe/agentic-mbse/.env` before every SysIDE-dependent command and confirm
  `SYSIDE_LICENSE_KEY` is present without printing it.
- Use each repository's existing `uv` environment. Do not refresh locks unless implementation
  changes dependencies; none are planned.
- Use `mktemp -d` or pytest `tmp_path` for variants, snapshots, generated packages, and built wheels.
  Validate the exact temporary path before deleting it.
- Never edit `sysml-codegen/.venv/.../agentic_mbse_data`. Edit the agentic-mbse source checkout.
- Never clean, reset, or stash a dirty user worktree. Use an isolated worktree when a clean branch is
  required.

## Risk Management

See [design.md#potential-risks](design.md#potential-risks) for the full analysis.

- **F-2/F-3 exceed their contained boundaries:** Stop, record the failing test and required owner,
  and file the follow-up. Documentation and customer migration do not proceed on a false premise.
- **Package data goes stale:** Codegen reads through the public resolver; agentic builds and inspects
  a wheel. Neither relies on the current venv copy being live.
- **Customer census changes:** D12 and pair hashes rerun immediately before writing. Any count or hash
  difference stops Phase 4.
- **Anchoring evidence remains Needs Work:** Phase 4 is blocked until the exact-owner premise is
  certified or the owner explicitly approves direct runtime evidence as the substitute.
- **Licensed tests skip:** Treat the phase as unvalidated. A green summary with skips is not the
  required proof.
- **Dirty worktrees overlap:** Preserve user state and move implementation to isolated worktrees;
  never solve overlap with destructive Git commands.

## Implementation Notes

Fill these during implementation. Do not pre-certify a phase.

### Phase 1 Completion

**Completed:** 2026-08-16

**Commits:**

- sysml-codegen `main` `00825a1` — F-3 repair + `sibling_formal_cycle` fixture + conformance tests
  (parent `d61ac58`, one commit past the plan-time `0f89673`; that commit is the anchoring census
  fix and does not touch elaboration).
- agentic-mbse `6e7bf5c` on branch `self-binding-replacement` in the isolated worktree
  `/home/reid/1cfe/agentic-mbse-self-binding` (branched from clean `main` `1decd95`; the main
  checkout is untouched on `main`).

**Actual Changes:**

- Agentic: `src/agentic_mbse/validation/level2_structure.py` — `check_self_named_bindings` now
  walks the calc usage's own parameter members and flags a binding only when the value
  expression's resolved referent element is identity-equal to the bound member
  (`SysideAdapter.element_id`), mirroring codegen's SRC-01 rule. `binding.py` unchanged — the
  referent is reachable at the validator boundary, so the plan's conditional edit was not needed.
  New fixture `tests/fixtures/item12/usage_qualified_local/` pins both supported qualified
  spellings (definition-qualified `QualifiedPlant::availability`, usage-qualified
  `station::availability`); one new test in `test_item12_checks.py`.
- Codegen: `elaboration/elaborate.py` wraps final `graph.validate()` so `GraphValidationError`
  becomes `ElaborationDiagnosticError`; `elaboration/graph.py::_validate_producer_cycles` retains
  the DFS active stack, visits in display order, and emits one diagnostic per cycle naming every
  participant once (consumer = first participant, not `<instance-graph>`). New fixture
  `tests/fixtures/sibling_formal_cycle/` (+ `PROVENANCE.md`) promoted from spike
  `s5_sibling_formal`; new `tests/conformance/test_elaboration_cycle_diagnostics.py` (3 tests) and
  one graph-level test appended to `test_elaboration_identity_collisions.py`.

**Validation:**

- Test-first proven: all 4 new codegen tests red pre-repair (raw `GraphValidationError`, bare
  detail); the new agentic test red pre-fix (2 false-positive `L2_SELF_NAMED_BINDING` hits, one
  per qualified spelling). All green post-repair.
- Targeted: agentic 28 passed (item12 + level2 integration); codegen 7 passed (cycle diagnostics +
  identity collisions); refusal checks 21 passed (spike parity + CLI snapshot refusal).
- Full suites, license loaded, zero license-skip lines:
  - Codegen: 17 failed / 2149 passed / 34 skipped / 88 deselected. The 17 are the recorded
    pre-existing missing-`pandas` family, file-for-file (`test_report_precedence` 12,
    `test_fusion_tea_acceptance` 4, `test_output_schema_contract` 1); +4 passed = exactly the new
    tests. Baseline taken from the 2026-08-16 recorded 17/2145/34/88 rather than a fresh
    pre-change run; the failing-file counts match it exactly.
  - Agentic (worktree, `--all-extras`): 1832 passed / 1 skipped / 5 deselected = baseline 1831 +
    the new test. (A first run under plain `uv sync` showed 18 environmental
    `test_web_backend.py` failures from missing `web` extras; they pass on clean `main` and after
    `uv sync --all-extras`, so they are venv-provisioning, not regressions.)
- Lint/type: Ruff clean on all changed files in both repos; codegen `mypy src/` = 52-in-11, the
  recorded pre-existing baseline, none in `elaboration/`; agentic mypy findings for the changed
  file line-identical to `main`'s.
- Manual licensed: `validate_structure` accepts the qualified fixture (`success=True`, zero
  issues) while `self_named_trap` still refuses with exactly one error; `sysml-codegen generate`
  on the cycle fixture exits 1 with `SI_EDGE_DANGLING:
  sibling_formal_cycle__plant__revenue_calc: typed producer dependency cycle: …`, zero
  `Traceback` lines, no output directory created.

**Issues / Deviations:**

- No new resolution architecture, shared validator, or graph-layer restructuring was needed; the
  stop-and-file condition never triggered.
- `tests/unit/test_direct_reference_unknown_leaf.py` turned up modified in the codegen tree
  mid-session — it is the anchoring item's finding-5 docstring narrowing, not this item's work.
  Preserved uncommitted; excluded from the path-scoped commit.
- `.project` artifacts (this plan, design rev 4, CURRENT_WORK) remain uncommitted alongside the
  other active items' in-flight docs; final delivery commits are Phase 5's job.

### Phase 2 Completion

**Completed:** 2026-08-16

**Commits:**

- sysml-codegen `main` `816d35e` — definition-owned fixtures + position conformance test +
  customer-mode migration tool (9 files, path-scoped).

**Actual Changes:**

- Promoted `def_qual_two_occ_inside` (s4b), `def_qual_two_occ_above` (s8), and
  `def_qual_sibling_scope` (s6), each with a `PROVENANCE.md` labelling the leaf
  definition-owned; packages renamed to match the directories, shapes unchanged.
- New `tests/conformance/test_definition_owned_reference_positions.py` (3 tests): inside-the-def
  two occurrences generate per-occurrence values (0.11/0.99, own-occurrence edges); above-the-def
  refuses strict with exactly one `SI_OCCURRENCE_AMBIGUOUS` and leaves the lenient consumer
  unbound; sibling scope reaches 7.0, named as positional fallback rather than author intent.
- `scripts/make_d5_variant.py`: customer mode (`--root`/`--scratch`, `--formals` mandatory),
  `discover_sites` census (file:line per binding/declaration), `precondition_findings` with the
  four D5 gates (a)–(d) refusing before any write, `build_variant_tree`/`strip_check_tree`
  Path-based generalizations (fixture mode wraps them unchanged), and the corrected two-mode
  docstring. The aggregation guard is D5(d): fixture mode keeps the unconditional split; customer
  mode refuses when any rollup would match, so the split can never fire on customer files.
- `tests/conformance/test_d5_variants.py`: +9 tests — the dual-tree closed loop (strip the
  vendored fixture's renames → duplicate into `models/` + `exploration/ife_e2e/models/` → migrate
  → byte-identical to the vendored fixture per file, cross-set pairs identical, originals
  untouched by digest), the 30-census-rows check (15 binding + 15 declaration rows per set; every
  changed line must revert by stripping `_in` alone), the discovery census (30 + 30 sites), one
  end-to-end refusal test per precondition (exit 1, no scratch created, tree digest unchanged),
  the CLI end-to-end run, and the `--formals`-required refusal.

**Validation:**

- Test-first: all 8 implementable new d5 tests were red before the tool changes (no `--root`).
- License-free: `test_d5_variants.py` 29 passed (20 existing + 9 new); every hazard case proves
  no-write by tree digest inside its test.
- Licensed: positions file 3 passed; combined run with
  `test_usage_owned_reference_anchoring.py` — **80 passed** (48 anchoring + 3 positions + 29 d5),
  covering both owner classes side by side.
- Full licensed suite: **17 failed / 2161 passed / 34 skipped / 88 deselected**, zero
  license-skip lines — same 17 pre-existing missing-`pandas` failures file-for-file; +12 = the
  new tests.
- Ruff clean on the changed script and both test files; `mypy src/` unchanged at the 52-in-11
  pre-existing baseline.

**Issues / Deviations:**

- **The closed-loop test caught a real tool defect:** the block-wide rename also rewrote formal
  names inside doc-comment prose (`fusion_cycle.sysml` "fusion cycle gain below ~4" →
  `gain_in`), an edit the ratified migration never made and Phase 4's diff rule forbids.
  `_rename_in_span` now renames identifiers only, outside `//` and `/* */` regions. Existing
  committed variants are unaffected (the strip check is symmetric over comments).
- The plan's "30 rows per set" is asserted as the 15 + 15 census rows; the recipe also renames
  expression uses *inside* declaring blocks (17 further lines per set), each proven rename-only
  by per-line reversal. Total changed lines per set is 47, matching the vendored fixture exactly.
- **Commit hygiene near-miss:** the first Phase-2 commit swept in 73 files the concurrent
  anchoring session had staged (its `active/` → `completed/20260816_…` archival). Repaired
  immediately by `git reset --soft` and a pathspec-scoped recommit; the archival renames are back
  to staged-and-uncommitted for their owning session, and `816d35e` carries exactly the 9
  Phase-2 files. Phase 5's delivery step must use pathspec commits for the same reason.
- `[OWNER 2026-08-16]` stated the anchoring item is certified; its folder is now archived at
  `.project/completed/20260816_qualified-reference-occurrence-anchoring/` (done by its own
  session). Recorded at the Phase 4 entry gate.

### Phase 3 Completion

**Completed:** 2026-08-16

**Commits:**

- agentic-mbse `3e9734b` on `self-binding-replacement` — authoritative rewrite, 13-site review,
  three summary surfaces, packaged-guidance contract (5 files).
- sysml-codegen `main` `20a8bb7` — drift contract test + `SI_SELF_BINDING` validation row
  (2 files, pathspec-scoped).

**Actual Changes:**

- `docs/patterns/plant-idiom.md`: the self-binding section is now "Binding a modelled value into
  a calculation — match the form to where the value lives", carrying the `@authoritative` marker,
  seven `@pinned` fixture excerpts (D-5 both spellings, D-7, usage-owned D-6, the three
  definition-owned positions, the refused trap), two `@measured` labels (inherited-attribute
  D-5 in the retyping example; EXPOSE + D-5), the arrayed-owner boundary note pointing at
  `[ANCHORING-ARRAYED-DIAGNOSTIC]`, and the KerML §7.3.4.5 / §8.2.3.5.1 redefinition citation.
  The four refused worked examples (`:79/:84/:85/:200`) are corrected to D-5. No live surface
  cites SysML Part 1 §7.17.2 (verified; only the excluded spec dump mentions it).
- `claude/skills/sysml-conventions/SKILL.md`: one Common-Pitfalls row, the three-situation
  subsection, one pointer line. `project_templates/MODELING_PROCESS.md.template`: collision
  example rewritten to D-5, new §2.2.2 short rule with the labelled D-6 alternative, pointer.
  `project_templates/MODELING_GUIDE.md.template`: three-bullet rule + pointer.
- `tests/test_packaged_guidance_contract.py` (agentic): editable-mode resolver assertion + built
  wheel byte-identity via `uv build` into `tmp_path`.
- `tests/conformance/test_self_binding_guidance_contract.py` (codegen): 9 tests — single
  authority, marker labels, pinned-example containment, pinned refusal, zero-unmarked sweep,
  qualified inventory with dispositions, negatives, pointer surfaces, `.claude/` zero-inventory.
- `docs/architecture/modeling-assumptions.md`: `SI_SELF_BINDING` row appended to the Validation
  Rules table. No ADR-010, no product-ledger row (open owner call preserved).

**Validation:** see the ticked Validation subsection above. Codegen full licensed suite:
**17 failed / 2170 passed / 34 skipped / 88 deselected**, zero license-skip lines — same 17
pre-existing missing-`pandas` failures file-for-file, +9 = the drift-contract tests. Agentic full
suite on the relocated branch (main checkout venv): **1834 passed / 1 skipped / 33 deselected**,
zero failures (= prior baseline + the two packaged-contract tests; the deselected count differs
from the worktree venv's 5 because the two venvs collect different slow-marker parametrizations —
all deselected, none failing).

**Issues / Deviations:**

- **Branch relocation, surfaced deliberately:** the codegen drift contract resolves agentic-mbse
  through the editable install, which points at `/home/reid/1cfe/agentic-mbse`. The Phase-1
  worktree was therefore removed (its venv discarded) and the `self-binding-replacement` branch
  is now checked out in the **main agentic checkout**. Codegen's agent symlinks
  (`.claude/skills/sysml-conventions`) now also resolve the corrected skill — the intended end
  state. Cost: the main agentic checkout is parked off-`main` until delivery, the same trade the
  epic previously accepted with `elaborate-first-salvage`. Returning it to `main` is a
  delivery-time (owner-run) step.
- The drift comparison is whitespace-normalized, order-preserving line containment rather than a
  raw byte substring, so doc excerpts can dedent; any rewording or value change still fails.
- The "same 13 positive sites" guard is recorded as 11 retained + 2 rewritten-to-D-5 (the owner's
  D11 ruling directs the template rewrite, which necessarily removes those two sites from the
  search result); the contract test pins the post-review inventory including the doc's own 4
  pinned qualified examples.
- The `wi014_toy` attribute-rename spelling was pinnable (the fixture carries it verbatim), so
  only two shapes remain `@measured` instead of the expected three.

### Phase 4 Completion

**Completed:** 2026-08-16

**Commits:**

- fusion-tea `9e1ff87b` on branch `self-binding-replacement` in the isolated worktree
  `/home/reid/1cfe/fusion-tea-self-binding` (from `be1ee7c0`) — the 12 migrated model files plus
  `tests/models/test_self_binding_replacement.py`. The original dirty checkout is untouched
  (22 dirty entries before and after).

**Actual Changes:**

- The mechanical D-5 migration: 15 binding left sides + 15 formal declarations per set gain
  `_in`, in both `models/` and `exploration/ife_e2e/models/` (12 files, 60 census rows; the
  block-wide rename also renames formal uses inside declaring def bodies, comment prose
  untouched). Applied via `make_d5_variant.py --root` per set after preconditions cleared;
  originals replaced only after the strip check passed with both trees present.
- The spine test (8 nodes, all `tmp_path` copies, license hard-required): dual-set generation,
  live/snapshot byte identity, 23/18 classification oracle, exact 11-key renamed-supplier
  sub-oracle, the 7 non-renamed design attributes, and the two off-default mutations proving
  every-and-only arrival — gain to `lcoe_calc` + `recirc_calc` + the viability constraint module
  (formal identity `fusion_cycle::'Viability Threshold'::gain_in` in the catalog predicate), and
  nested `beam_energy_mj` to exactly `driver__meier_cost.beam_energy_mj_in`.

**Validation:** all boxes above; the pre-migration red run recorded the 15 `SI_SELF_BINDING`
findings site-for-site with Appendix A.

**Issues / Deviations:**

- **Layout discovery (census over plan text):** the exploration set stores the library files
  without the `library/` prefix (`analyses/…`, `cost_structure/…`, `foundation/…`). Pair contents
  are byte-identical; only relative paths differ. D12 makes the census authoritative, so the six
  logical files were replaced at their census paths.
- The fusion-tea branch carries 58 pre-existing test failures (14 models-family, proven
  byte-identical with the migration stashed; 44 scoring_v2, model-independent). Recorded, not
  absorbed.
- Worktree-local, uncommitted: `uv.lock` (moved by `uv sync` for the worktree venv) and
  `tools/score_explorer/data/concepts.json` (rewritten by the scoring_v2 tests during the full
  run — a test that mutates tracked data; pre-existing behavior, left alone).

### Phase 5 Completion

**Completed:** 2026-08-16

**Commits:** the cross-repo inventory is in the Delivery checks above; this phase's own changes
(triage record, D5 precondition logs, the backlog row, design rev 4, and this plan) ship as the
codegen docs commit recorded in CURRENT_WORK.

**Actual Changes:**

- `stellarator-triage.md` — the one-run record with the no-mutation proof.
- `[STELLARATOR-D5-MIGRATION]` filed in `BACKLOG.md` (P2, unowned; July hold preserved).
- `verification/phase4-d5-{models,exploration}.log` — the saved D5 discovery/precondition/strip
  output for both customer sets.

**Validation:** all cross-repo boxes above ticked with their counts.

**Issues / Deviations:**

- The item's `spec.md` (status line) and `.project/CURRENT_WORK.md` entries remain uncommitted:
  both files also carry the concurrent anchoring session's **staged** archival repoints, and a
  pathspec commit would absorb that session's in-flight work. They ride with whichever session
  commits the shared files; the substance of this item's record lives in this plan, the triage
  record, and the per-repo commits.
- Tool-version note: agentic ruff/mypy and codegen ruff report different totals under different
  venvs (worktree venv vs main checkout venv). Every changed-repo check above was therefore
  proven by **main-vs-branch identity** under one venv rather than by absolute counts.

---

**Status:** Draft → In Progress → Complete
