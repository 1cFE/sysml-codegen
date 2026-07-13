# Implementation Plan: Contracts and Sealing — `ModelContract` / `PackageContract`

**Status:** Draft
**Created:** 2026-07-13
**Last Updated:** 2026-07-13
**Epic:** CONSTRAINT-EXEC — Item 9
**Branch:** constraint-exec-epic

## Source Documents
- **Spec:** `.project/active/package-contracts/spec.md`
- **Design:** `.project/active/package-contracts/design.md` ← component details, decisions D1–D8,
  invariants INV-1…INV-8, `verify_package` signature. This plan does not restate them; it links.

## Plan-level decisions (the design's "Open for the plan", resolved)

These four were left `[AGENT]` for the plan (`design.md:377-380`). Resolved here so the
implementer has no open choices. All are agent-grade defaults; the `RUNTIME_CONTRACT_VERSION`
value is owner-overridable.

- **P1. `coverage_policy` schema.** A JSON object recorded inside the seal:
  `{"exclude_globs": [...], "runtime_output_globs": [...]}`. Default `exclude_globs =
  ["contracts/package_contract.json", "**/__pycache__/**"]`; default `runtime_output_globs = []`.
  Verify applies the **recorded** policy, never a hard-coded one (D3). The runtime-output slot is
  the extensible seam finalized against the real teax loader at Item 10 (`design.md:307-309`).
- **P2. `_canonical_json` reuse (design.md:378).** Import `_canonical_json` from
  `generation.constraint_catalog` into the contracts package — one definition, no second
  canonicalizer (INV per `design.md:299`). *If* this creates an import cycle (generation ever
  imports contracts), lift `_canonical_json` to a neutral `sysml_codegen/_canonical.py` and have
  both import it. `verify.py` needs **no** canonicalizer (it only sha256s file bytes and joins
  `"path:hash"` lines — `design.md:210`), so its stdlib-only constraint is unaffected either way.
- **P3. `Diagnostic.kind` enum.** `TAMPER`, `MISSING`, `EXTRA`, `GENERATOR_MISMATCH`,
  `RUNTIME_MISMATCH`, `NAME_MISMATCH`. First three are integrity (always fatal, D4); the two
  `*_MISMATCH` env kinds are advisory unless `strict` (D5); `NAME_MISMATCH` is its own diagnostic
  (`design.md:232`).
- **P4. `RUNTIME_CONTRACT_VERSION` initial value + bump policy.** Initial `"1.0.0"`. Bump the
  major on any breaking change to the runtime API the emitted code targets; minor/patch for
  compatible additions. Pinned generator constant (never read from an installed teax — D5).
  **[AGENT default — owner may override the initial token.]**

## Implementation Strategy

**Phasing rationale.** Build the pure, offline core first (models → fingerprints → seal), because
every later piece depends on the seal format and none of it needs the pipeline or a license. Then
the verifier against that format. Then wire both into `run_codegen` as Step 9 plus the re-seal
subcommand. Finally the stability/parity gate, which is the one criterion (SC-4) this item cannot
prove alone — it rides Item 8's byte-identity.

**Critical path.** contract models + canonical serialization + fingerprints (P1) →
stdlib verifier + verification semantics (P2) → Step 9 wiring + `seal` subcommand + emitted-verbatim
verifier (P3) → SC-4 stability/parity + final gates (P4).

**First proof point.** Phase 1's fingerprint-determinism test: `build_model_contract(graph)` and
`seal_package(dir, …)` produce byte-identical `semantic_fingerprint` / `executable_fingerprint`
across two independent calls in one session. That collapses the core "are the fingerprints a stable
pure function" uncertainty before any pipeline wiring.

**Everything is license-free except one leg.** Sealing and verification are pure directory/graph
operations — no syside license. Only the SC-4 **live-vs-snapshot** parity leg (Phase 4) needs a
license, because the live extraction leg does. All Phase 1–3 tests run offline.

**Environment (implement session).** License-gated runs use:
`env $(grep -v '^#' ~/1cfe/agentic-mbse/.env | xargs) uv run pytest <targets>`.
Offline runs use plain `uv run pytest <targets>`.

**⚠️ Item 8 gating (SC-4 snapshot leg) — read before Phase 4.** Item 8's parity implementation has
landed (Phase 3 at `e38110b`: `test_live_vs_snapshot_byte_identical`, constraint-parity fixtures
`wi014_toy` / `constraint_multi_instance` / `constraint_inline`). It is **not yet audit-certified**
(no certify commit). So: author and run the Phase 4 fingerprint-parity canary now against the
landed parity — it will pass if parity holds. **But its green is only as authoritative as Item 8's
certification.** If Item 8's audit surfaces a parity regression and re-lands, this canary MUST be
re-run at Item 8 certification. State that loudly in the Phase 4 completion note; do not certify
Item 9's SC-4 as final while Item 8 is uncertified.

---

## Phase 1: Contract models, canonical serialization, fingerprints (offline core)

### Goal
Stand up the `sysml_codegen/contracts/` package: pydantic models, the pure graph projection
`build_model_contract`, the pure directory function `seal_package`, both fingerprints, and version
constants. No pipeline, no verifier, no license. Proves the fingerprints are a stable pure function
(the first proof point) and that graph-only + zero-constraint hold.

### Assumption Under Test
The semantic and executable fingerprints are deterministic pure functions — of the graph and of the
directory bytes respectively — reproducible byte-exactly within a session (SC-4's within-session
half; cross-session/parity is Phase 4). And `build_model_contract` needs no I/O (SC-5 INV-1).

### Test Stencil (Write This First)
```python
# tests/unit/test_contract_models.py
def test_model_contract_is_graph_only(monkeypatch):
    # INV-1 / SC-5: patch filesystem access to raise; build still succeeds.
    import builtins
    monkeypatch.setattr(builtins, "open", _raise)  # any FS touch -> fail
    mc = build_model_contract(graph_with_constraints())
    assert mc.semantic_fingerprint  # computed, no file read

def test_fingerprints_are_deterministic(tmp_path):
    mc1 = build_model_contract(g); mc2 = build_model_contract(g)
    assert mc1.semantic_fingerprint == mc2.semantic_fingerprint
    seal1 = seal_package(_write_fixture(tmp_path/"a"), "pkg", DEFAULT_POLICY)
    seal2 = seal_package(_write_fixture(tmp_path/"b"), "pkg", DEFAULT_POLICY)
    assert seal1.executable_fingerprint == seal2.executable_fingerprint

def test_zero_constraint_graph_seals(tmp_path):  # SC-6 / INV-7
    mc = build_model_contract(graph_without_constraints())  # catalog is None
    assert mc.constraint_catalog is None       # serializes as null (D6)
    assert mc.semantic_fingerprint             # still stable
```

### Changes Required

**See `design.md` for:** Component Overview (`design.md:263-281`); serialization policies
(`design.md:196-201`); seal data flow (`design.md:203-214`); D6 catalog-by-value; INV-2/INV-6/INV-7.

- [x] `tests/unit/test_contract_models.py` (NEW, write first) — graph-only, determinism,
  zero-constraint, and the two-policy serialization (compact fingerprint payload vs pretty on-disk
  bytes; assert `model_contract.json` bytes are byte-stable across two builds → INV-6).
- [x] `src/sysml_codegen/contracts/__init__.py` (NEW) — package + public exports.
- [x] `src/sysml_codegen/contracts/versions.py` (NEW) — `RUNTIME_CONTRACT_VERSION = "1.0.0"` (P4);
  `generator_version()` reads `sysml_codegen.__version__` (`src/sysml_codegen/__init__.py:9`).
- [x] `src/sysml_codegen/contracts/models.py` (NEW) — `ModelContract`, `PackageContract` pydantic
  BaseModels (fields per `design.md:265-269`); `constraint_catalog: ConstraintCatalog | None`
  imported from `resolution/models.py:357` (embed by value, `null` on None — D6).
- [x] `src/sysml_codegen/contracts/model_contract.py` (NEW) — `build_model_contract(graph) ->
  ModelContract`: project `entry_point_groups[].parameters` + `modules[].outputs` + catalog +
  `evaluation_semantics` tag; compute `semantic_fingerprint = sha256(_canonical_json(payload
  without the fingerprint field))` then insert (`design.md:302-303`). Imports no I/O (INV-1).
- [x] `src/sysml_codegen/contracts/seal.py` (NEW) — `DEFAULT_COVERAGE_POLICY` (P1);
  `seal_package(dir, name, policy) -> PackageContract`: walk under policy, hash every covered file
  into `artifact_hashes` (`{rel_path: sha256}`), `executable_fingerprint = sha256("\n".join(sorted
  "path:hash"))`, record `coverage_policy` + `generator_version` + `runtime_contract_version`. Pure
  over the directory (this is also the re-seal entry point — D1/D2).
- [x] Serialization helpers: reuse `_canonical_json` per P2; on-disk writer = `json.dumps(...,
  indent=2, sort_keys=True, ensure_ascii=True) + "\n"` (`design.md:199-201`).

### Validation
**Automated (offline):**
- [x] `uv run pytest tests/unit/test_contract_models.py` → all pass.
- [x] `uv run pytest tests/` → no regressions (new package is additive; nothing imports it yet).
- [x] `uv run mypy src/` → still at the 76-error baseline, no new errors.
- [x] `uv run ruff check src/` → clean.

**What We Know Works After This Phase:** The two fingerprints are stable pure functions;
`build_model_contract` is graph-only (SC-5); a zero-constraint graph seals (SC-6); on-disk contract
bytes are deterministic (INV-6). No circularity: IDs feed the semantic payload, never the reverse
(INV-2, assert the payload contains no fingerprint field before it is inserted).

---

## Phase 2: Stdlib-only verifier + verification semantics (offline)

### Goal
Write the one canonical `verify.py` — stdlib-only (`hashlib`, `json`, `pathlib`; imports **nothing**
from sysml-codegen) — implementing bidirectional integrity (tamper/missing/extra, always fatal) and
advisory-default env-compat, against the seal format from Phase 1. Prove SC-1, SC-2, SC-3 offline
over a hand-sealed fixture directory.

### Assumption Under Test
The verification algorithm is generic — it reads only the seal's self-description (recorded policy +
hashes + versions), not the model — so one small stdlib verifier serves any package (B3). And all
three integrity failure modes plus env-compat are detectable from the seal alone.

### Test Stencil (Write This First)
```python
# tests/unit/test_verify_package.py
def _sealed(tmp_path):  # build a tiny package dir + real seal via seal_package
    ...

def test_tamper_fails(tmp_path):                       # SC-1
    d = _sealed(tmp_path); (d/"pipelines"/"p.yaml").write_text("MUTATED")
    r = verify_package(d, "pkg")
    assert not r.ok and any(x.kind == "TAMPER" for x in r.diagnostics)

def test_missing_and_extra_fail(tmp_path):             # SC-2 (both halves)
    d = _sealed(tmp_path); (d/"modules"/"m.py").unlink()
    assert any(x.kind == "MISSING" for x in verify_package(d,"pkg").diagnostics)
    d2 = _sealed(tmp_path/"b"); (d2/"stray.py").write_text("x")
    assert any(x.kind == "EXTRA" for x in verify_package(d2,"pkg").diagnostics)

def test_env_compat_advisory_then_strict(tmp_path):    # SC-3
    d = _sealed(tmp_path)
    assert verify_package(d, "pkg", runtime_version="99.0").ok is True      # advisory
    assert verify_package(d, "pkg", runtime_version="99.0", strict=True).ok is False

def test_verifier_imports_nothing_from_sysml_codegen():  # INV-8 (import scan)
    src = (CONTRACTS_DIR/"verify.py").read_text()
    assert "sysml_codegen" not in src and "import agentic" not in src
```

### Changes Required

**See `design.md` for:** `verify_package` signature (`design.md:218-234`); D4 bidirectional/fatal;
D5 advisory env-compat; load-by-declared-name (`design.md:312-314`); INV-4/INV-8.

- [x] `tests/unit/test_verify_package.py` (NEW, write first) — tamper/missing/extra, env-compat
  advisory-then-strict, name-mismatch diagnostic, `verify_package_or_raise` raises on `not ok`,
  import-scan (INV-8 half that doesn't need Step 9).
- [x] `src/sysml_codegen/contracts/verify.py` (NEW) — `Diagnostic(kind, path, message)`,
  `VerificationResult(ok, diagnostics)`, `verify_package(package_dir, package_name,
  runtime_version=None, strict=False)`, `verify_package_or_raise(...)`. Reads
  `contracts/package_contract.json`, applies the **recorded** `coverage_policy`. Integrity: each
  recorded path exists + hash matches (TAMPER/MISSING); walk under policy → any surviving
  policy-scoped file not in the coverage set is EXTRA (INV-4). Env-compat: compare recorded
  `generator_version` / `runtime_contract_version` to the loading env; emit `GENERATOR_MISMATCH` /
  `RUNTIME_MISMATCH` (advisory unless `strict` — D5). `NAME_MISMATCH` when recorded name ≠ requested.
  **Stdlib-only (P2) — imports nothing from sysml-codegen.**

### Validation
**Automated (offline):**
- [x] `uv run pytest tests/unit/test_verify_package.py` → all pass (SC-1, SC-2, SC-3).
- [x] `uv run pytest tests/` → no regressions.
- [x] `uv run mypy src/` → 76 baseline; `uv run ruff check src/` → clean.

**Manual:** grep-confirm `verify.py` has no `sysml_codegen` / `agentic_mbse` / template / non-stdlib
import (the B3 property that lets a teax env verify without sysml-codegen installed).

**What We Know Works After This Phase:** Tamper, missing, and extra all raise named fatal
diagnostics; env-compat is advisory by default and fatal under `strict`; the verifier is
self-contained stdlib. SC-1/SC-2/SC-3 proven offline.

---

## Phase 3: Step 9 wiring, `seal` subcommand, emitted-verbatim verifier

### Goal
Join the seal to `run_codegen` as Step 9 (writes the three `contracts/` files in order), add the
`sysml-codegen seal <package>` re-seal subcommand (recomputes the PackageContract only — D2), and
emit `contracts/verify.py` **verbatim** from the canonical in-repo source (INV-8 drift guard). Both
live and from-snapshot paths seal for free (D8).

### Assumption Under Test
Sealing composes as a strictly additive final step over final on-disk state (stubs or preserved
handwritten alike), and re-sealing is the same `seal_package` function run again — so a human
stencil edit invalidates the seal until re-sealed, and re-seal never needs the graph (B4/D2).

### Test Stencil (Write This First)
```python
# tests/conformance/test_seal_step9.py  (offline — sealing needs no license)
def test_generate_emits_three_contract_files(tmp_path):
    run_codegen(_snapshot_config(tmp_path))          # from-snapshot => license-free
    c = tmp_path/"out"/"contracts"
    assert (c/"model_contract.json").exists() and (c/"package_contract.json").exists()
    assert verify_package(tmp_path/"out", "pkg").ok   # a fresh seal verifies

def test_emitted_verifier_is_verbatim(tmp_path):      # INV-8 drift guard
    run_codegen(_snapshot_config(tmp_path))
    emitted = (tmp_path/"out"/"contracts"/"verify.py").read_bytes()
    canonical = (SRC/"contracts"/"verify.py").read_bytes()
    assert emitted == canonical

def test_reseal_after_stencil_edit(tmp_path):         # D1/D2 re-seal workflow
    run_codegen(_snapshot_config(tmp_path)); out = tmp_path/"out"
    mc_before = (out/"contracts"/"model_contract.json").read_bytes()
    (out/"handwritten"/"x_impl.py").write_text("# human edit\n")
    assert not verify_package(out, "pkg").ok           # seal now invalid
    cmd_seal(_seal_args(out, "pkg"))                    # sysml-codegen seal <pkg>
    assert verify_package(out, "pkg").ok               # re-seal fixes it
    assert (out/"contracts"/"model_contract.json").read_bytes() == mc_before  # MC unchanged (D2)
```

### Changes Required

**See `design.md` for:** Step 9 flow (`design.md:203-214`); D1 seal-as-Step-9 + `seal` subcommand;
D2 re-seal recomputes PackageContract only; INV-3 seal ordering; D8 both-paths.

- [ ] `tests/conformance/test_seal_step9.py` (NEW, write first) — three files emitted + fresh seal
  verifies; emitted `verify.py` byte-identical to source (INV-8); re-seal workflow (seal → edit →
  invalid → `seal` → valid; MC bytes unchanged); ordering (`package_contract.json` written last and
  excluded from its own coverage — INV-3).
- [ ] `src/sysml_codegen/cli/__init__.py` — add `_seal_package(ctx, config)` and call it as Step 9
  in `run_codegen`, after `_generate_tests` and before `return True`
  (`cli/__init__.py:934-937`). Order (INV-3): (1) `build_model_contract` + write
  `model_contract.json`; (2) copy canonical `verify.py` verbatim; (3) `seal_package` over the dir
  (now covering both); (4) write `package_contract.json` last.
- [ ] `src/sysml_codegen/cli/__init__.py` — add `cmd_seal(args)` and a `seal` subparser
  (mirror the `generate`/`snapshot` wiring at `cli/__init__.py:715-812`; `set_defaults(func=
  cmd_seal)`). Re-seal recomputes the PackageContract over an existing dir; validates
  `model_contract.json` is present + covered; does **not** rebuild the ModelContract (D2 — graph-free,
  license-free).
- [ ] Update generation tests that assert on the generated file set — the three new `contracts/`
  files are an **expected** additive diff. Candidates to check: `tests/integration/test_full_pipeline.py`
  (`.rglob("*.py")` sweeps at `:88,:460` now include `contracts/verify.py` — it is valid stdlib
  Python, so syntax checks pass; confirm no test asserts an *exact* file count/set). No committed
  baseline changes: `baseline_outputs/` holds only `computation_graph.json` + `registry_init.py`
  (verified), which sealing does not touch.

### Validation
**Automated (offline — sealing is license-free):**
- [ ] `uv run pytest tests/conformance/test_seal_step9.py` → pass.
- [ ] `uv run pytest tests/` → green (update any exact-file-set assertion to include the three
  contract files; that is an expected-diff class for generated packages, not a baseline change).
- [ ] `uv run mypy src/` → 76 baseline; `uv run ruff check src/` → clean.

**Manual:**
- [ ] `uv run sysml-codegen generate --from-snapshot
  tests/fixtures/chain_spike_model/extraction_snapshot.json --output /tmp/c9 --package-name
  chain_spike --overwrite` → `/tmp/c9/contracts/` has all three files.
- [ ] `uv run sysml-codegen seal /tmp/c9 --package-name chain_spike` (after editing a stencil) →
  re-verify passes.

**What We Know Works After This Phase:** Generation emits a self-verifying package on both live and
from-snapshot paths; the emitted verifier is byte-identical to the in-repo source (INV-8); re-seal
recomputes only the PackageContract and is license-free (D2/B4).

---

## Phase 4: SC-4 fingerprint stability + parity, final gates

### Goal
Prove the fingerprints reproduce byte-exactly across independent generation (cross-session offline
leg) and across live-vs-snapshot (the Item-8-contingent leg), then run the full gate wall.

### Assumption Under Test
The only pipeline dependency of either fingerprint is the artifact bytes and the graph, both of
which Item 8 makes byte-identical live-vs-snapshot (B1/INV-5). This test is the **canary** that
fails loudly if that regresses.

### Test Stencil (Write This First)
```python
# tests/conformance/test_fingerprint_stability.py
def test_fingerprints_stable_across_independent_generation(tmp_path):   # offline leg
    run_codegen(_snapshot_config(tmp_path/"a"))
    run_codegen(_snapshot_config(tmp_path/"b"))
    assert _exec_fp(tmp_path/"a") == _exec_fp(tmp_path/"b")
    assert _sem_fp(tmp_path/"a") == _sem_fp(tmp_path/"b")

@requires_license                                                        # Item-8-contingent leg
@pytest.mark.parametrize("fixture", ["wi014_toy", "constraint_multi_instance"])
def test_fingerprints_stable_live_vs_snapshot(fixture, tmp_path):
    live_out = _generate_live(fixture, tmp_path/"live")       # capture snapshot, generate both
    snap_out = _generate_from_snapshot(fixture, tmp_path/"snap")
    assert _exec_fp(live_out) == _exec_fp(snap_out)           # SC-4 executable-fp parity
    assert _sem_fp(live_out) == _sem_fp(snap_out)             # SC-4 semantic-fp parity
```

### Changes Required

**See `design.md` for:** SC-4 (`design.md:356-357`); De-risk-first canary (`design.md:382-385`);
INV-5; the Item 8 parity risk (`design.md:326-328`).

- [ ] `tests/conformance/test_fingerprint_stability.py` (NEW, write first) — offline
  cross-session leg (two from-snapshot generations, compare both fingerprints) + `@requires_license`
  live-vs-snapshot leg over the landed Item 8 constraint-parity fixtures (`wi014_toy`,
  `constraint_multi_instance` — mirror `tests/conformance/test_snapshot_constraint_parity.py:24-40`).
  Compare the extracted `semantic_fingerprint` / `executable_fingerprint` fields directly (a
  fingerprint diff pinpoints a parity regression better than a raw tree diff).
- [ ] No source changes expected. If the live-vs-snapshot leg diverges, the divergence is an **Item 8
  artifact-parity regression** surfaced by this canary — do not patch it in Item 9; surface it
  against Item 8 (`design.md:384-385`).

### Validation
**Automated (offline leg):**
- [ ] `uv run pytest tests/conformance/test_fingerprint_stability.py -k across_independent` → pass.

**Automated (license leg — Item-8-contingent):**
- [ ] `env $(grep -v '^#' ~/1cfe/agentic-mbse/.env | xargs) uv run pytest
  tests/conformance/test_fingerprint_stability.py -k live_vs_snapshot` → pass against landed Item 8
  parity. **⚠️ Re-run at Item 8 certification** (see the gating note at the top); record the result
  and the Item-8 commit it was run against in the completion note.

**Final gate wall:**
- [ ] `env $(grep -v '^#' ~/1cfe/agentic-mbse/.env | xargs) uv run pytest tests/` → full suite
  green (license env so `@requires_license` tests run, not skip — auto-memory
  `syside-license-key-explicit-env-needed`).
- [ ] `uv run mypy src/` → 76-error baseline, no new errors.
- [ ] `uv run ruff check src/` → clean.
- [ ] Corpus/baseline check: `baseline_outputs/` (graph + registry only) is untouched by sealing —
  confirm no committed baseline churned; the three `contracts/` files live in generated output, an
  expected-diff class for generated packages, not a committed baseline.

**What We Know Works After This Phase:** SC-4 within-session and cross-session fingerprint
stability proven; live-vs-snapshot parity proven against landed Item 8 (canary in place for the
certification re-run). All gates green.

---

## Environment Setup
**See CLAUDE.md.** Offline: `uv run pytest <targets>`. License-gated:
`env $(grep -v '^#' ~/1cfe/agentic-mbse/.env | xargs) uv run pytest <targets>`.
Do NOT `git commit` — the orchestrator commits.

## Risk Management
**See `design.md#potential-risks`.**
- **Item 8 parity (Phase 4).** Mitigated by inheriting Item 8's parity gate + the canary; loud
  gating note; re-run at Item 8 certification.
- **Runtime-output location unknown until Item 10 (P1).** Mitigated by the self-describing,
  extensible `coverage_policy`; default excludes seal + `__pycache__`; runtime-output slot empty.
- **Emitted-verifier drift.** Mitigated by the INV-8 verbatim test (Phase 3); the emitted copy is
  seal-covered, so a hand-edit is caught on verify.
- **Exact-file-set test brittleness (Phase 3).** The three new contract files perturb any test that
  asserts an exact generated file set; sweep and update those to expect them.

## Implementation Notes
[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-07-13
**Changes Made:**
- Created `src/sysml_codegen/contracts/{__init__,models,versions,model_contract,seal,serialize}.py`
  — `ModelContract`/`PackageContract`/`CoveragePolicy`/`ContractParameter`/`ContractOutput`
  pydantic models; `build_model_contract(graph)`; `seal_package(dir, name, policy)`;
  `DEFAULT_COVERAGE_POLICY`; `RUNTIME_CONTRACT_VERSION`/`generator_version()`;
  `write_contract_json` on-disk writer.
- `_canonical_json` reused verbatim (imported) from `generation.constraint_catalog` — no import
  cycle (contracts is a new leaf package); P2 resolved without lifting to a shared helper.
- `seal.py`'s `_glob_to_regex` implements `**`-aware glob matching (a bare `fnmatch` translation
  of `"**/__pycache__/**"` fails to match a top-level `__pycache__/x.pyc` because the pattern's
  literal `/` before `__pycache__` has nothing to match against) — not in the original plan text,
  needed once `DEFAULT_COVERAGE_POLICY`'s `**/__pycache__/**` pattern was tested against a real
  top-level case. Documented in the docstring as duplicated-not-imported into `verify.py` (Phase 2)
  per D7's stdlib-only constraint.
- `evaluation_semantics` tag set to `"kleene-three-valued"` (not S4's `"kleene-three-valued-s4"`)
  — matches the concept doc's evaluation-semantics language; the design left the exact string
  unspecified.
- Created `tests/unit/test_contract_models.py` (7 tests) — graph-only (INV-1), fingerprint
  determinism, zero-constraint (SC-6/INV-7), on-disk byte-stability (INV-6), no-circularity
  (INV-2), field projection.
**Validation:** `test_contract_models.py` 7/7 pass; full suite 2052 passed / 23 failed / 96 errors
(unchanged from the pre-existing no-license baseline — confirmed via `git stash` comparison, went
2045→2052 passed with identical failure/error counts); mypy 76-error baseline held; ruff clean.
**Issues Encountered:** None outside the glob-matcher gap noted above.
**Deviations from Plan:** None beyond the glob-matcher addition (an implementation necessity of
the plan's own `DEFAULT_COVERAGE_POLICY` pattern, not a scope change).

### Phase 2 Completion
**Completed:** 2026-07-13
**Changes Made:**
- Created `src/sysml_codegen/contracts/verify.py` — stdlib-only (`hashlib`, `json`, `re`,
  `dataclasses`, `pathlib`); `Diagnostic`, `VerificationResult`, `verify_package`,
  `verify_package_or_raise`; the six `Diagnostic.kind` constants (P3): `TAMPER`, `MISSING`,
  `EXTRA`, `GENERATOR_MISMATCH`, `RUNTIME_MISMATCH`, `NAME_MISMATCH`. Duplicates (does not
  import) `seal.py`'s `_glob_to_regex` per D7's stdlib-only constraint.
- Re-exported `verify_package`/`verify_package_or_raise`/`Diagnostic`/`VerificationResult`
  from `contracts/__init__.py` for in-repo ergonomics; the emitted copy inside a generated
  package remains the self-contained file (INV-8, Phase 3).
- **`GENERATOR_MISMATCH` is defined but not currently produced by `verify_package`.** The
  design's fixed `verify_package` signature (`design.md:218-225`) takes one env axis —
  `runtime_version`, compared against the seal's `runtime_contract_version` (→
  `RUNTIME_MISMATCH`). There is no loading-environment `generator_version` parameter to
  compare against, and `verify.py` cannot import `sysml_codegen.__version__` (stdlib-only,
  D7) to read one itself. `GENERATOR_MISMATCH` stays in the enum per P3 but is currently
  unreachable from this function; flagging this now rather than silently dropping the kind
  or unilaterally widening the fixed signature.
- Created `tests/unit/test_verify_package.py` (10 tests) — tamper/missing/extra (SC-1/SC-2),
  env-compat advisory-then-strict (SC-3), env-compat skipped on `runtime_version=None`,
  name-mismatch, `verify_package_or_raise` raise/pass-through, untampered-package-verifies,
  AST-based import scan (INV-8 half). The import scan uses `ast.parse` rather than the plan
  stencil's substring check — the substring form false-positives on `verify.py`'s own
  docstring, which legitimately mentions `sysml_codegen.contracts.seal` in prose.
**Validation:** `test_verify_package.py` 10/10 pass; full suite 2062 passed / 23 failed / 96
errors (unchanged baseline, 2052→2062 passed with identical failure/error counts); mypy 76
baseline held; ruff clean (one import-order fix applied via `ruff check --fix` on
`contracts/__init__.py`).
**Issues Encountered:** None beyond the GENERATOR_MISMATCH gap and the substring-scan
false-positive, both noted above.
**Deviations from Plan:** Import-scan test implementation (AST instead of substring) —
equivalent intent, more robust. No scope changes.

### Phase 3 Completion
### Phase 4 Completion

---
**Status:** Draft → In Progress → Complete
