# Evidence — Lifecycle Item 7: Trusted Package Bootstrap and Seal Provenance

Pinned chain: sysml-codegen through Item 6 (`f917787`), agentic-mbse `4c18d61`, TEAx
`db23719`. Cross-repo item: sysml-codegen (producer) + TEAx (consumer). Both named attacks
driven RED-first against pre-fix code, then GREEN. No release-readiness claim; Item 13 owns the
push and the composed proof.

Footprint (codegen): 6 code/test files + 1 new module (`contracts/manifest.py`), +289 / −56 in
tracked files. Footprint (teax): `package_load.py` (+102/−~30) plus the two enumerated fixture
re-seals (2 verify.py, 2 seals, 1 GENERATION.md) and one new test file.

Environment: license loaded via `set -a; source ~/1cfe/agentic-mbse/.env; set +a` (0
`no live syside license` skips in `-rs`). TEAx suite in the agentic-mbse venv
(`~/1cfe/agentic-mbse/.venv/bin/python`).

---

## 1. Attack (a) — unconditional-success verifier (TEAx), RED-first

**The hole.** `ProvisionalPackageLoader._verify_seal` imported the package-local
`contracts/verify.py`, executed its module body, and trusted the `verify_package` result — so a
package that ships an `ok=True` stub verifier certified itself before any authentication.

**RED.** New `simkit/tests/evaluation/test_package_trust.py::
test_unconditional_success_verifier_rejected_before_exec` copies the sealed F1 fixture, replaces
`contracts/verify.py` with a stub that returns `ok=True` and writes a marker on execution, and
asserts `_verify_seal()` raises **and** the marker is absent. Against pre-fix `package_load.py`:

```
FAILED test_unconditional_success_verifier_rejected_before_exec
  (loader executed the stub, returned a fingerprint, marker written — no raise)
```

**Fix.** The loader carries a runtime-owned anchor `TRUSTED_VERIFIER_SHA256`
(`package_load.py`), reads the package-local `verify.py` **once**, hashes it, and on match
executes *exactly those bytes* via `exec(compile(source, ...))` — never `exec_module`, which
would re-read the path (TOCTOU, design Major 1). A stub has different bytes and is rejected
before its module body runs (INV-A). Hash, not a second verifier: semantics stay in the one
canonical module (D1).

**GREEN.** The test passes; the marker is never written. Control
`test_canonical_fixture_still_loads` confirms the untampered re-sealed fixture authenticates and
loads.

## 2. Attack (b) — foreign-file laundering (codegen), RED-first

**The hole.** `cmd_seal` re-hashed whatever was on disk and gated only on no-symlinks + a prior
model contract — a foreign file dropped anywhere covered was laundered into `artifact_hashes`
(`cli/__init__.py:762`).

**RED.** New `tests/conformance/test_seal_step9.py::
test_reseal_rejects_foreign_file_as_codegen_provenance` generates a package, drops
`modules/evil.py`, and asserts `cmd_seal` returns 1 and never records the file. Against pre-fix:

```
FAILED test_reseal_rejects_foreign_file_as_codegen_provenance
  AssertionError: assert 0 == 1   (re-seal returned 0 and laundered the file)
FAILED test_reseal_rejects_edit_to_codegen_produced_file      (edit to a generated file laundered)
FAILED test_generate_emits_generation_manifest                (no manifest emitted)
```

**Fix.** Generation emits `contracts/generation_manifest.json` — the codegen-produced set built
as the covered tree minus `handwritten/**` minus runtime globs (Major 4 completeness), written
before the seal so it is itself covered (`cli/__init__.py` `_seal_package`). A CLI-level
provenance gate (`contracts/manifest.py::check_reseal_provenance`, called from `cmd_seal`)
authenticates the manifest against the prior seal, freezes codegen-class hashes, admits
`handwritten/**`, and hard-fails a foreign or edited-generated file. The pure `seal_package`
function and both walkers are untouched (D4/INV-D); the gate reuses the seal helpers, adds no
walker.

**GREEN.** `test_seal_step9.py` — **13 passed**, including the two attack tests, the manifest
test, and the pre-existing `test_reseal_after_stencil_edit` (a `handwritten/**` edit stays
admissible, now exercising the gate's happy path).

Honest scope (design Major 2 / Non-Goal): the gate defeats a **non-collusive** injection. A
same-privilege adversary who also rewrites the manifest and prior seal is not stopped — the
producer has no runtime-owned secret; seal signing is out of scope. Item 13 inherits this scope.

## 3. Version skew fails closed, both directions (TEAx), RED-first

**RED.** `test_package_trust.py::test_version_skew_fails_closed_both_directions[2.0.0|0.9.0]`
patches the seal's `runtime_contract_version` above and below the accepted version and asserts a
diagnostic naming the *accepted-versions policy*. Against pre-fix (symmetric `==` +
`RUNTIME_MISMATCH`, no explicit policy):

```
FAILED ...[2.0.0] / [0.9.0]
  Regex 'accepted runtime-contract versions' did not match
  Actual: "RUNTIME_MISMATCH(None): loading environment runtime '1.0.0' does not match ..."
```

**Fix.** The bare `RUNTIME_CONTRACT_VERSION = "1.0.0"` literal (`package_load.py:22`) is deleted
and replaced by `ACCEPTED_RUNTIME_CONTRACT_VERSIONS = frozenset({"1.0.0"})` (single-version, D3;
a range is incoherent with one vendored hash — Major 3). The loader owns acceptance and passes
the seal's own version into `verify_package`, making its env-compat check a satisfied no-op (D2,
single authority). **GREEN**: both directions raise with the named policy.

## 4. Version anchor + drift guard (codegen)

`versions.py` publishes `TRUSTED_VERIFIER_SHA256 = ad0a855…` (the current canonical verifier
bytes = the single 1.0.0 image). New `test_seal_step9.py::
test_trusted_verifier_hash_matches_canonical` asserts it equals `sha256(verify.py)`; combined
with the existing verbatim-emit guard (`test_emitted_verifier_is_verbatim`), a verify.py edit
that forgets to re-publish (and re-vendor in TEAx) trips CI. INV-B cross-repo half rests on this
test + manual re-vendoring (B3 forbids an automated cross-repo check).

## 5. D3 stale-fixture drift corrected (TEAx)

The committed fixtures carried pre-current verifier bytes at 1.0.0 (`86de6dd`, `24eb356`). A
surgical re-seal to canonical (`/tmp/reseal_fixtures.py`, run once) swapped each `verify.py` to
`ad0a855`, updated the recorded verify hash and `executable_fingerprint`, and updated f1's
`GENERATION.md` fingerprint. No files added → each seal's covered set is unchanged
(`test_f1_fixture_seal_name_fingerprint_and_order`'s `covered == actual` holds). This is a
correction to the one true 1.0.0 image, not a version bump.

Scope: a repo-wide search found only these two sealed fixtures, so the re-seal set is complete.

## 6. Full battery

**codegen** (licensed, `-rs`):
- `uv run pytest tests/` — **3068 passed, 44 skipped, 17 deselected**; **0** `no live syside
  license` skips.
- `uv run python -O -m pytest tests/` — **3066 passed, 2 failed**. Both failures
  (`test_expression_compiler` assertion-raising tests) reproduce on BASE with Item 7 changes
  stashed — pre-existing `-O` artifacts (`assert` stripped), not an Item 7 regression.
- Execution lane — `PYTHONPATH=…/src TEAX_SIMKIT_PATH=…/teax-simkit … -m execution tests/` —
  **17 passed**.
- `uv run mypy src/` — 72 errors, all pre-existing (BASE = 73; Item 7 adds **0**; `contracts/`
  and `cli` hunks clean).
- `uv run ruff check` on all Item 7 files — **All checks passed**.
- Certified Item 6 surface — `test_verify_package.py` (38), `test_contract_models.py` (17),
  `test_fingerprint_stability.py` (4), `test_seal_step9.py` symlink/verbatim tests — all green
  **unchanged**; `test_fingerprint_stability` needed no fixture regen (every assertion is
  relative; manifest is verifier-byte-independent — design Minor churn correction).
- Byte-identity: codegen has **no** committed sealed-tree fixture, so the manifest adds **no**
  `baseline_outputs` churn (baselines are ComputationGraph-level).

**teax**:
- `~/1cfe/agentic-mbse/.venv/bin/python -m pytest simkit/tests/` — **281 passed**.
- `test_package_trust.py` — 4 passed (attack a, skew ×2, control).
- Byte-identity: the working tree changes are exactly `package_load.py`, the new test, and the
  two enumerated fixture re-seals — nothing else.

---

## Supported checkboxes (Success Criteria)

- [x] Attack (a) — unconditional-success verifier rejected before any package code executes (§1).
- [x] Attack (b) — foreign-file laundering refused; file never admitted as codegen-produced (§2).
- [x] Version skew fails closed in both directions with a naming diagnostic (§3).
- [x] Item 6 guarantees stay green — named tests unchanged (§6).
- [x] One authority, no bypass — verify.py (integrity), loader (compat), manifest+cmd_seal
      (provenance); bare literal + symmetric-`==` authority deleted (§2/§3).
- [x] Generation manifest records per-artifact provenance; re-seal consults it (§2).

## Named deletions landed with their cutover

- `package_load.py:22` bare `RUNTIME_CONTRACT_VERSION = "1.0.0"` — deleted, replaced by the
  accepted-versions policy in the same change (§3).
- The unauthenticated import-then-trust load path (`_load_verify_package` + `exec_module`) —
  replaced by `_load_authenticated_verifier` (read-once, hash, exec hashed bytes) (§1).

## Candidate commits

- sysml-codegen: `<CANDIDATE_REV_CODEGEN>` on `constraint-exec-epic`.
- teax: `<CANDIDATE_REV_TEAX>` on its working branch.
