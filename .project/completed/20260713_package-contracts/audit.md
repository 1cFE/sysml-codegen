# Audit: Item 9 — Contracts and Sealing (`ModelContract` / `PackageContract`)

**Verdict:** Certify-with-notes *(contingent on the Requested Live Probes below returning green — test execution was blocked in this session by the permission mode, so evidence is static reading + the plan's recorded runs)*
**Audited:** 2026-07-13
**Branch:** constraint-exec-epic
**Commit range:** `fba7ddd..8c82b9b` (four phase commits)
**Auditor:** fresh session; did not implement this item

---

## Summary

The implementation matches the spec and design cleanly. All eight success criteria and invariants
INV-1…INV-8 have direct, well-constructed tests that call the real `seal_package` / `verify_package`
on real sealed package directories (not mocks). The seal is a pure directory function; the verifier
is genuinely stdlib-only; Step 9 wiring and the `seal` re-seal subcommand are correct and ordered
per INV-3. The two flagged completion-note items are both benign and honestly recorded.

Three notes keep this from a clean Certify, none a blocker: (1) the two `_glob_to_regex` copies
(seal producer / verify consumer) are byte-identical today but have **no drift guard** — the exact
gap the brief asked me to check; (2) `GENERATOR_MISMATCH` is an unreachable-but-reserved enum kind
(documented seam, adjudicated acceptable); (3) the graph-only SC-5 test is a partial guard (purity
holds by construction). I could not execute the suite; the probe list re-confirms the plan's runs.

## Findings

### Plan completion
All four phases are implemented and their checkboxes are genuine — every listed file exists and
carries the claimed content (verified by reading, not by function name):

- **Phase 1** — `contracts/{__init__,models,versions,model_contract,seal,serialize}.py` all present.
  `_canonical_json` is imported from `generation.constraint_catalog` (no second canonicalizer, P2).
  `evaluation_semantics = "kleene-three-valued"` (deviation from S4's suffix, documented, matches
  the concept doc).
- **Phase 2** — `verify.py` present, stdlib-only, six `Diagnostic.kind` constants (P3).
- **Phase 3** — `_seal_package` (Step 9) and `cmd_seal` + `seal` subparser wired in
  `cli/__init__.py`; `shutil` and `Path` imports present (`cli/__init__.py:14,17`), so the Step 9
  `shutil.copy` of `verify.py` is valid.
- **Phase 4** — `test_fingerprint_stability.py` present with both legs.

No placeholder code, no TODOs, no partial implementations found.

### Spec conformance

- **SC-1 Tamper fails load** — ✅ (static). `test_tamper_fails` (`test_verify_package.py:40`) seals a
  real dir via `seal_package`, mutates `pipelines/p.yaml`, asserts `not ok` and a `TAMPER`
  diagnostic **naming the file** (`x.path == "pipelines/p.yaml"`). Runs through the load path
  (`verify_package` reads the on-disk seal).
- **SC-2 Stale-file detection (both halves)** — ✅ (static). `test_missing_fails` deletes a covered
  file → `MISSING` naming it; `test_extra_fails` adds `stray.py` → `EXTRA` naming it. The
  missing-file half (S4's gap) is closed by the recorded-path existence check
  (`verify.py:132-138`); the extra half by the policy walk (`verify.py:145-157`).
- **SC-3 Environment compatibility** — ✅ with note. `test_env_compat_advisory_then_strict`: a
  mismatched `runtime_version` yields `ok=True` + `RUNTIME_MISMATCH` advisory; under `strict=True`,
  `ok=False`. Only the **runtime** axis is exercised (see Finding 2 on `GENERATOR_MISMATCH`).
- **SC-4 Fingerprint stability** — ✅ pending probe. Offline cross-session leg
  (`test_fingerprints_stable_across_independent_generation`) compares both fingerprints across two
  independent from-snapshot generations. License leg (`test_fingerprints_stable_live_vs_snapshot`,
  `@requires_license`, `wi014_toy` + `constraint_multi_instance`) compares live-vs-snapshot. Plan
  records both green against Item 8 CERTIFIED `847bbba`. **Requested probe 3** re-confirms.
- **SC-5 ModelContract is graph-only** — ✅ by construction, partial test (Finding 3).
  `build_model_contract` imports only `hashlib`, `typing`, `contracts.models`, and
  `_canonical_json` — no filesystem, no template. `test_model_contract_is_graph_only` patches
  `builtins.open` to raise and builds successfully. What it asserts: the build path calls no
  `builtins.open`. What it would **miss**: a `pathlib.Path.read_text/read_bytes` or a jinja load
  (pathlib uses `io.open`, not `builtins.open`). The invariant holds by construction; the guard is
  weaker than the design's stated "module-import scan confirms no template/Path dependency"
  (`design.md:358-359`), which is not implemented as a test.
- **SC-6 Zero-constraint packages seal** — ✅ (static). `test_zero_constraint_graph_seals`: a
  `constraint_catalog is None` graph yields `mc.constraint_catalog is None`, serializes to
  `constraint_catalog: null`, and still produces a stable `semantic_fingerprint`. Matches D6/INV-7.

**Known-requirement spot checks:** ModelContract embeds the catalog **by value** (`models.py:71`,
D6) ✅; `PackageContract` carries `coverage_policy` + `artifact_hashes` + both versions (D3) ✅;
no *Provided* capabilities leaked into `ModelContract` (the fields are `parameters`, `outputs`,
`constraint_catalog`, `evaluation_semantics`, `semantic_fingerprint` only) ✅; load-by-declared-name
via `package_name` param + `NAME_MISMATCH` ✅; catalog fingerprint (Item 7) read, not rebuilt ✅.

### Design conformance

D1–D8 all followed:

- **D1/D2** — seal is Step 9 (`cli/__init__.py:1016`, after `_generate_tests`, before `return True`);
  `cmd_seal` recomputes the `PackageContract` only and refuses a dir with no prior
  `model_contract.json` (`cli/__init__.py` `cmd_seal`, returns 1). `test_reseal_after_stencil_edit`
  proves edit→invalid→`seal`→valid with **MC bytes unchanged**.
- **D3** — `CoveragePolicy` recorded in the seal; verify applies the **recorded** policy
  (`verify.py:145` reads `seal["coverage_policy"]`), not a hard-coded one. *Minor:* verify also
  hard-codes a skip of `contracts/package_contract.json` (`verify.py:150`) in addition to it being
  in `exclude_globs` — belt-and-suspenders, harmless, slightly at odds with D3's "never hard-coded"
  but the file is excluded both ways.
- **D4** — integrity always fatal (`_INTEGRITY_KINDS` frozenset, `verify.py:28,172`); env-compat
  fatal only under `strict`. Bidirectional (INV-4): tamper + missing (recorded-path loop) + extra
  (policy walk).
- **D5** — `generator_version()` (reads `__version__`) and `RUNTIME_CONTRACT_VERSION = "1.0.0"`
  pinned constants, never read from an installed runtime. Advisory-default/strict-promotable ✅.
- **D6** — catalog by value, `null` on None ✅ (SC-6).
- **D7** — `verify.py` stdlib-only, emitted verbatim; INV-8 drift test
  (`test_emitted_verifier_is_verbatim`) asserts emitted == in-repo source byte-for-byte.
- **D8** — contracts recomputed at generation, both paths (from-snapshot generation seals in the
  offline tests); nothing persisted into the snapshot.

INV-3 ordering verified by `test_seal_ordering_excludes_itself_from_coverage`:
`package_contract.json` absent from `artifact_hashes`; `model_contract.json` + `verify.py` present.

### Code integrity

- **Finding 1 — [Note] No drift guard between the two `_glob_to_regex` copies.**
  `seal.py:24` (producer) and `verify.py:61` (consumer) carry byte-identical function **bodies**
  today (only the docstrings differ). But the only drift test in the suite (INV-8) guards *emitted
  `verify.py` == in-repo `verify.py`* — **nothing asserts `seal.py`'s matcher equals `verify.py`'s
  matcher.** `grep -rn _glob_to_regex tests/` returns nothing. If a future edit changes one copy,
  the seal's coverage decision (which files get hashed) and verify's coverage decision (which files
  are "extra") silently diverge — a covered file could read as `EXTRA`, or an excluded path could
  escape the tamper check. This is precisely the "producer and consumer never disagree on scope"
  property D3/D7 rest on. **Change:** add a test that extracts both function source bodies and
  asserts equality (or lift the matcher to one shared stdlib-only module both import — but D7
  forbids `verify.py` importing anything in-repo, so the byte-equality-test route is the fit).

- **Finding 2 — [Note, recorded & adjudicated] `GENERATOR_MISMATCH` is unreachable.**
  Confirmed: `verify.py` defines it (`:24`), exports it (`:198`), and references it in the fatal
  computation (`:173`), but **no code path ever constructs `Diagnostic(kind=GENERATOR_MISMATCH)`**.
  The completion note (`plan.md:436-442`) flags this honestly. **Adjudication: acceptable-and-recorded,
  not a dead field to rip out now.** The design fixed the `verify_package` signature with a single
  env axis — `runtime_version` (`design.md:218-225`) — and `verify.py` cannot import
  `sysml_codegen.__version__` (stdlib-only, D7) to self-source a generator version. The seal *does*
  record `generator_version`, so the data to compare against already exists; wiring the check needs
  one more parameter (`generator_version: str | None`) the loading env passes. That is an Item 10 /
  Item 14 integration decision (the same wiring that injects teax's runtime marker), not an Item 9
  defect. **Change (deferred, not blocking):** at Item 10/14, either add the `generator_version`
  parameter + comparison, or delete the constant if the second axis is decided out of scope. Leave
  as a documented seam for now.

- **Finding 3 — [Minor] SC-5 graph-only test is a partial guard.** See SC-5 above. The purity holds
  by construction (import set is clean); the test only catches `builtins.open`. **Change (optional):**
  add an import-scan test on `model_contract.py` mirroring the design's stated SC-5 validation, so
  a future I/O import is caught mechanically rather than by reviewer vigilance.

- **Finding 4 — [Minor robustness] Missing seal file raises instead of diagnosing.**
  `verify.py:117` does `json.loads(seal_path.read_text())` with no guard. A package directory with
  no `contracts/package_contract.json` raises `FileNotFoundError` out of `verify_package`, rather
  than returning a `VerificationResult` with a diagnostic. The seam contract implies verify returns
  a result; a caller (e.g. teax loader, Item 10) handling "unsealed package" would get an unexpected
  exception type. Low severity — arguably an unsealed dir is not a package to verify — but worth a
  one-line note or an explicit diagnostic. **Change (optional):** guard the seal read and emit a
  named "no seal" diagnostic, or document that a missing seal is an exception by contract.

No god functions, no policy-in-utility, no broad `except Exception`, no backwards-compat shims, no
`None`-default data-papering found. `seal_package` and `verify_package` each do one job readable
from the signature. Abstraction quality is good.

**Non-goals respected:** no teax loader wiring, no signing, no catalog changes, no contracts in the
snapshot. Nothing out of scope was built.

---

## Certification

**Checked (by static reading of the four phase commits + all four test files):**
- All eight success criteria have direct tests asserting the criterion through the real seal/verify
  path; each test's assertions were read and confirmed to match the SC.
- D1–D8 and INV-1…INV-8 traced to code with `file:line` evidence.
- The two completion-note flags (GENERATOR_MISMATCH, glob matcher) adjudicated.
- The `_glob_to_regex` copies compared body-for-body (identical) and searched for a drift test (none).
- The three `rglob("*.py")` sweeps in `test_full_pipeline.py` (`:88,:302,:460`) confirmed to be
  **content** checks, not exact-file-set counts — the new `contracts/verify.py` does not perturb
  them (no `FusionParams`/`fusion_simkit` strings; valid stdlib Python; `modules/` sweep is scoped
  away from `contracts/`). Plan's "no exact-file-set assertion breaks" claim verified.

**Spec/plan checkboxes:** marked SC-1…SC-6 in `spec.md` and left plan checkboxes as-is (already all
`[x]`), on the basis of **static verification + the plan's recorded green runs**. The live probes
below are requested for independent execution confirmation.

**Not checked (execution blocked this session — permission mode denied `pytest`/`python3`):**
- I did **not** run any test, mypy, or ruff in-session. Every "✅" above is static (code+test
  reading) plus the plan's recorded run counts, not a fresh execution.
- The mutation probe (disable extra-sweep → EXTRA test RED) was not executed — requested below.
- The SC-4 license leg (live-vs-snapshot parity) depends on Item 8 byte-identity; not re-run here.
- Real teax loader interop (mismatch 8) — out of sandbox by design; an Item 10 concern.

---

## Requested Live Probes (for the orchestrator)

Run these; if all green, this audit stands as **Certify-with-notes**. If any fails, downgrade.

1. **Offline contract suite (expect 23 passed):**
   ```
   uv run pytest tests/unit/test_contract_models.py tests/unit/test_verify_package.py \
     tests/conformance/test_seal_step9.py \
     tests/conformance/test_fingerprint_stability.py -k "not live_vs_snapshot" -q
   ```

2. **Mutation probe — extra-file sweep (expect RED then revert):** in
   `src/sysml_codegen/contracts/verify.py`, neutralize the policy walk at lines 146-157 (e.g.
   change `for path in sorted(package_dir.rglob("*")):` to `for path in []:`), then:
   ```
   uv run pytest tests/unit/test_verify_package.py::test_extra_fails -q   # expect FAILED
   git checkout -- src/sysml_codegen/contracts/verify.py                  # revert
   ```
   (Valid because `test_extra_fails` imports the in-repo `verify_package` directly.)

3. **SC-4 license leg + full gate wall (license env):**
   ```
   env $(grep -v '^#' ~/1cfe/agentic-mbse/.env | xargs) uv run pytest \
     tests/conformance/test_fingerprint_stability.py -k live_vs_snapshot -q   # expect 2 passed
   env $(grep -v '^#' ~/1cfe/agentic-mbse/.env | xargs) uv run pytest tests/ -q  # full suite green
   ```

4. **Gates + baseline:**
   ```
   uv run mypy src/                                        # expect 76-error baseline, no new
   uv run ruff check src/                                  # clean
   git status --short -- tests/fixtures/baseline_outputs/  # empty (no baseline churn)
   ```

**Recommended follow-ups (non-blocking, can land in this item or be logged):**
- Add the `_glob_to_regex` seal↔verify body-equality drift test (Finding 1) — the one guard the
  design's own scope-agreement property depends on and currently lacks.
- Decide `GENERATOR_MISMATCH` at Item 10/14: wire a `generator_version` axis or remove the constant.

---

## Addendum: probes + cure executed by orchestrator (2026-07-13)

- **Contract/seal/verify suites:** 61 passed (incl. the new drift guard). **Full suite:** 2282 passed / 4 skipped (license env). **mypy:** 76 = baseline. **ruff:** clean.
- **Extra-sweep mutation probe:** silently skipping the EXTRA append → exactly `test_extra_fails` RED (`assert not True`) → revert → 10 passed. The load-path extra-file detection has teeth.
- **Cure (Finding 1):** `test_glob_matcher_bodies_identical_across_seal_and_verify` added — AST-compares the two `_glob_to_regex` bodies with docstrings stripped (`_is_covered` differs by design: typed model vs raw dict). Drift now fails CI.
- GENERATOR_MISMATCH adjudication (documented seam for Item 14 integration) accepted as recorded.

**Final verdict: Certify** (upgraded; probes executed, cure landed).
