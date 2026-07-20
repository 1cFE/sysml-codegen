# Design: Trusted Package Bootstrap and Seal Provenance (Lifecycle Item 7)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-20
**Branch:** constraint-exec-epic
**Base commit:** 4ca43a3 (sysml-codegen); TEAx HEAD db23719
**Complexity:** HIGH — cross-repo (sysml-codegen + TEAx), two named attacks

---

## Overview

Move package-verification trust to anchors the package cannot forge: the TEAx runtime
authenticates the package-local verifier *bytes* against a runtime-carried hash before
executing them, and codegen writes a provenance manifest that re-seal consults so a foreign
file cannot be laundered as codegen-produced.

## Related Artifacts

- **Spec:** `.project/active/constraint-lifecycle-package-trust/spec.md`
- **Spec brief:** `.project/active/constraint-lifecycle-package-trust/briefs/spec.md`
- **Epic:** `.project/backlog/epic_constraint_execution_lifecycle_remediation.md` (Item 7, rows 8–9)
- **Ratified authority:** `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`
- **Seal/verify reference:** `docs/architecture/reference/29-contracts-and-sealing.md`

## Research Findings

**The trust chain today.** A generated package carries its own verifier at
`contracts/verify.py`, emitted byte-for-byte from the canonical
`src/sysml_codegen/contracts/verify.py` (`cli/__init__.py:655-657`). The TEAx loader imports
that package-local copy by file path and executes its module body
(`teax package_load.py:38-51`, `exec_module` at :50), then trusts the `verify_package` result
(:74-84) and only then imports the package (:69-72). Byte-identity of the emitted verifier to
the canonical source is checked only at *generation* (INV-8 drift guard,
`tests/conformance/test_seal_step9.py:49-58`), never at load. So the package grades its own
homework: an `ok=True` stub verifier loads.

**Re-seal today.** `seal_package` is a pure function of a directory plus a coverage policy —
it hashes whatever is on disk, excluding only the seal file and `__pycache__`
(`seal.py:93-122`, policy at :18-21). `cmd_seal` gates only on "no symlinks" and "a prior
`model_contract.json` exists" (`cli/__init__.py:728-768`); it records no provenance. A foreign
file dropped anywhere covered is hashed in as a legitimate artifact.

**The version literal is duplicated and drift-prone.** `RUNTIME_CONTRACT_VERSION = "1.0.0"`
lives in both `versions.py:11` and `teax package_load.py:22`. The loader passes it to
`verify_package` (`package_load.py:79`), which does symmetric equality
(`verify.py:319-329`), fatal only under `strict`. There is no explicit accepted-versions
policy and no cross-repo check that the two literals agree.

**Anti-drift machinery already exists — extend it.** `test_fingerprint_stability.py:31-32`
already pins a prior verifier hash (`REVIEWED_VERIFY_SHA256`) against a named revision. The
design generalizes this into a first-class published constant, not a new mechanism.

**Provenance is already known at generation.** `_generate_stencils` tracks each file as
new / preserved / regenerated (`cli/__init__.py:421-489`); `_seal_package` writes
`model_contract.json` and the verbatim `verify.py` itself (`cli/__init__.py:651-657`). Codegen
is the one actor that knows, per file, what it produced.

**Load-bearing surprise (surfaced, see Potential Risks).** The committed TEAx fixtures carry
*stale* verifier bytes — `sealed_package` is `86de6dd…`, `f1_arithmetic` is `24eb356…` — both
different from the current canonical `ad0a855…`, yet all sealed at `runtime_contract_version`
`"1.0.0"`. verify.py's bytes changed without a version bump. This is exactly the silent drift
the spec targets, and it forces a design position (D3) and fixture re-seal work.

**Walker boundary (do-not-collapse).** `_inspect_package_tree` and `_glob_to_regex` are
duplicated verbatim between `seal.py:36-90` and `verify.py:57-135` on purpose — the verifier
must stay stdlib-only (B3/D7). This design adds no walker and edits neither.

## Core Concept

**Trust flows from anchors the package cannot forge — never from bytes the package supplies.**

Today the package supplies both the verifier and the evidence, and each side of the chain
trusts the disk it is handed. The fix plants forgery-proof anchors on each side:

- **Consumer side (TEAx).** The loader carries two runtime-owned anchors: a *trusted hash* of
  the canonical verifier, and a *fail-closed accepted-versions policy*. Before executing the
  package-local `verify.py`, the loader hashes its bytes and compares to the trusted hash — an
  unconditional-success stub has different bytes and is rejected *before any package code
  runs*. We anchor with a **hash, not a second verifier**: verification *semantics* stay in the
  one canonical `verify.py` (still emitted verbatim, INV-8), and the runtime carries only its
  64-character fingerprint, so there is nothing to drift.

- **Producer side (codegen).** Codegen — the only actor that knows what it produced — writes a
  **generation manifest** classifying every artifact as codegen-produced, preserved-handwritten,
  or runtime. Re-seal authenticates that manifest against the prior seal, then refuses to admit
  any covered file the manifest does not account for. A dropped foreign file has no manifest
  entry and cannot be laundered as codegen-produced.

The single idea under both halves: **the authority for "what is trusted" moves to whoever
legitimately knows it and cannot be impersonated by the package** — the runtime for
verification and version, the generator for provenance — each anchored by a value the adversary
cannot forge without tripping a check. No new verifier, no second walker, no merged boundary.

## Key Bets

- **B1.** TEAx can carry small runtime-owned trust anchors (a verifier hash and an
  accepted-versions policy) without importing sysml-codegen. *If false → B3 forecloses the
  runtime-owned-anchor shape entirely.* Grounded: `package_load.py:22` already vendors the
  version literal; a hash constant is the identical move.
- **B2.** The canonical verifier's bytes are stable in normal operation and change only on
  deliberate policy edits. *If false → every incidental edit forces a version bump plus
  fixture re-seal, making per-version pinning impractical.* Grounded: verify.py changed rarely;
  `test_fingerprint_stability.py` already pins a prior hash.
- **B3.** At generation, codegen knows the exact provenance class of every file it writes.
  *If false → the manifest cannot be authoritative and re-seal has nothing trustworthy to
  consult.* Grounded: `_generate_stencils` already tracks per-file new/preserved/regenerated.
- **B4.** Re-seal's only legitimate job is to pick up handwritten-stencil edits; it never
  legitimately edits a generated file or introduces a new codegen-produced file. *If false →
  freezing codegen-class bytes at re-seal breaks a real workflow.* Grounded: `cmd_seal`
  docstring — "after editing a handwritten stencil" (`cli/__init__.py:729-733`).

## Key Decisions

- **D1. Authenticate the package-local `verify.py` against a runtime-carried hash** (spec
  open-question option ii). *Rejected: TEAx vendoring its own verifier (option i)* — a second
  verifier implementation is exactly the drift the epic forbids; a hash duplicates no
  semantics. The package-local `verify.py` stays and becomes an *authenticated* artifact rather
  than a blindly-trusted one.
- **D2. Compat authority lives in the TEAx loader as a fail-closed accepted-versions policy;
  `verify.py` stays integrity-only.** The loader reads the seal's `runtime_contract_version`,
  accepts/rejects against its own policy (both skew directions, named diagnostic), then runs
  `verify_package` for the hash/symlink integrity check only. *Rejected: putting the table in
  `verify.py`* — those bytes are package-controlled and cannot be the acceptance authority.
  *Rejected: keeping symmetric `==`* — no explicit both-direction policy; drift stays silent.
- **D3. One verifier image per `runtime_contract_version`; any `verify.py` byte change requires
  a version bump and a fixture re-seal.** *Rejected: accepting a set of historical verifier
  hashes* — it institutionalizes the multi-image-per-version drift (the stale fixtures above)
  the spec exists to kill. Enforced by extending the existing hash-pin test.
- **D4. The manifest is a separate artifact `contracts/generation_manifest.json`, covered by
  the seal; the re-seal provenance gate lives in `cmd_seal`, not in `seal_package`.** *Rejected:
  extending `PackageContract`/`seal_package` with provenance* — it entangles the pure seal
  function, re-seal cannot re-derive provenance license-free, and it risks touching the
  certified seal walker. Keeping the gate at the CLI layer leaves both walkers untouched.
- **D5. Provenance classes: codegen-produced is an *enumerated* path set (hash-frozen at
  re-seal); handwritten and runtime are *glob* classes.** This answers the spec's "per-file vs
  glob" question directly. A foreign file under a codegen path (e.g. `modules/evil.py`) is not
  in the enumerated set and not under a glob class → **hard-fail** (fail-closed, names the
  path). A new or edited file under `handwritten/**` stays admissible (human-owned region).
  *Rejected: admitting foreign files under a non-codegen class* — more surface; hard-fail is
  simpler and the owner-preferred posture.

## Architecture

Two independent change sets, one per repo, meeting at two published constants.

**sysml-codegen (producer).**
- `versions.py` gains `TRUSTED_VERIFIER_SHA256` = `sha256(contracts/verify.py)`, published as
  the value TEAx vendors. A drift test asserts it equals the live verifier bytes (extends the
  INV-8 guard and the `REVIEWED_VERIFY_SHA256` precedent).
- Generation writes `contracts/generation_manifest.json` during `_seal_package`, *before*
  `seal_package` runs, so the manifest is itself a covered (hashed) artifact. Its content comes
  from provenance codegen already knows (D5).
- `cmd_seal` gains a provenance gate that runs *before* `seal_package`: authenticate the
  on-disk manifest against the prior seal, then classify every covered file and reject the
  unaccounted. `seal_package` itself is unchanged.

**TEAx (consumer).**
- `package_load.py` gains an authenticate-before-exec step keyed on `TRUSTED_VERIFIER_SHA256`
  (vendored `ad0a855…`) and replaces the bare `"1.0.0"` literal (`:22`) with the accepted-
  versions compat policy.
- The committed fixtures (`sealed_package`, `f1_arithmetic`) are re-sealed to the current
  canonical verifier so they authenticate under the new anchor (see Potential Risks).

**Data flow at load (post-change):**
`read package verify.py bytes → sha256 → compare to TRUSTED_VERIFIER_SHA256` → mismatch ⇒
reject before exec. Then `read seal.runtime_contract_version → accepted-versions policy` →
not accepted ⇒ reject (both directions). Then `exec verify.py → verify_package(integrity)` →
`ok` ⇒ import package.

**Data flow at re-seal (post-change):** `load prior package_contract.json + manifest →
manifest bytes must equal prior seal's recorded manifest hash` → then per covered file:
codegen-enumerated ⇒ hash must equal prior seal (frozen); under `handwritten/**` ⇒ hash may
change; unaccounted ⇒ hard-fail. Then call the unchanged `seal_package`.

## Required Invariants

- **INV-A.** No package-local code executes on the load path before the loader authenticates
  the package-local verifier bytes against the runtime-carried trusted hash.
- **INV-B.** The runtime-carried trusted hash equals `sha256(canonical verify.py)` for the
  accepted `runtime_contract_version`; enforced by a codegen drift test and a TEAx skew test.
- **INV-C.** Verification *semantics* have exactly one implementation (canonical `verify.py`,
  emitted verbatim); the runtime carries only its hash, never a second verifier.
- **INV-D.** The seal walker (`seal.py`) and verify walker (`verify.py`) stay byte-distinct;
  the provenance gate adds no walker and modifies neither.
- **INV-E.** A covered file classified by neither the codegen-produced set nor the
  handwritten/runtime globs is never admitted by re-seal.
- **INV-F.** Codegen-produced files are byte-frozen across re-seal; only handwritten-class
  files may change.
- **INV-G (inherited).** The Item 6 stdlib-only symlink/path policy is unchanged; its
  regression tests stay green.

## Component Overview

- **`versions.py`** (sysml-codegen) — adds `TRUSTED_VERIFIER_SHA256`. The single published
  source of the verifier anchor. Runtime-contract-version single-source stays here.
- **`generation_manifest.json`** (new emitted artifact) — per-artifact provenance:
  `codegen_produced` (enumerated paths), `handwritten_globs`, `runtime_globs`,
  `runtime_contract_version`. Covered by the seal.
- **`_seal_package`** (`cli/__init__.py`) — extended to write the manifest before sealing. No
  change to `seal_package`.
- **Re-seal provenance gate** (`cmd_seal`, `cli/__init__.py`) — new CLI-level gate; reuses the
  link-free walk entries; consults the authenticated manifest.
- **`package_load.py`** (TEAx) — authenticate-before-exec + accepted-versions compat policy;
  bare-literal deletion target at `:22`.

## Non-Goals

- A second catalog schema authority (Item 8 / D-3).
- Re-auditing or reopening the certified Item 6 symlink/path matrix.
- TEAx constraint evidence-durability (Item 11).
- Wiring `runtime_output_globs` to a real runtime write location (Item 10). The manifest
  defines the runtime class conceptually; the globs stay empty.
- Reviving the dead `GENERATOR_MISMATCH` seam (`verify.py:24-30`).
- Editing `verify.py`'s algorithm. Its bytes stay stable so the first vendored hash equals the
  current canonical and existing (freshly re-sealed) packages carry no skew.

## Implementation Notes

- **Manifest schema (illustrative, not final):**
  ```json
  {
    "runtime_contract_version": "1.0.0",
    "codegen_produced": ["__init__.py", "modules/...", "contracts/model_contract.json",
                         "contracts/verify.py", "contracts/generation_manifest.json"],
    "handwritten_globs": ["handwritten/**"],
    "runtime_globs": []
  }
  ```
  The manifest lists itself in `codegen_produced` (frozen). No circularity: its authenticity
  anchor is the *prior* `package_contract.json`'s recorded hash, not the manifest.
- **Emission order (INV-3 extension):** write `model_contract.json` → `verify.py` →
  `generation_manifest.json` → `seal_package` (hashes all three) → `package_contract.json`
  last. The manifest must be final on disk before sealing.
- **Compat policy in TEAx** replaces `verify_package`'s symmetric-`==` as the load-path
  authority. Pass the seal's own version into `verify_package` so its runtime check is a
  satisfied no-op (integrity-only); the loader owns acceptance.
- **`verify.py` stays byte-stable** — do not delete `RUNTIME_MISMATCH`/`strict` (bytes + a
  standalone-CLI use); the loader simply stops leaning on them.

## Potential Risks

- **Stale TEAx fixtures (surfaced premise conflict).** `sealed_package` and `f1_arithmetic`
  carry pre-current verifier bytes at version `"1.0.0"`. Under D1 authentication they would be
  rejected. This design *resolves it in one direction* — D3: re-seal the committed fixtures to
  the current canonical verifier in the same TEAx change set — and flags it loudly here for the
  design review rather than resolving silently. If the reviewer prefers accepting historical
  hashes, D3 flips and INV-B/INV-F loosen; dependent conclusions (single-image-per-version)
  are parked on that call.
- **Baseline churn.** Adding `generation_manifest.json` changes every package's
  `artifact_hashes` and `executable_fingerprint`. Committed `baseline_outputs` /
  fingerprint-stability fixtures must be regenerated (generator-owned bytes, format-exempt).
  Expected; called out in the plan, not a regression.
- **Cross-repo hash sync is manual.** B3 forecloses an import-time single source, so
  `TRUSTED_VERIFIER_SHA256` is published in codegen and vendored in TEAx. The codegen drift
  test plus the TEAx skew test catch a stale vendor; the process risk (someone bumps verify.py
  without re-vendoring) is mitigated by, not eliminated by, the tests.

## Integration Strategy

- **Cross-repo phasing — sysml-codegen first, then TEAx.** sysml-codegen's change is
  self-contained and backward-compatible: it publishes the anchor TEAx will consume and adds
  producer-side provenance; old TEAx still loads new packages (the manifest is just another
  covered file). TEAx's change *depends on* the published hash, so it lands second, vendoring
  `ad0a855…`. Moving TEAx first would authenticate against a hash codegen has not yet blessed
  as a named constant.
- **Vehicles:** sysml-codegen via PR #9; TEAx via its own path. Item 7 has no expected
  agentic-mbse (PR #11) diff — verified: the vulnerability and fix live in codegen + TEAx only;
  surface if that changes.
- **Deletions land with their cutover.** The bare `"1.0.0"` literal (`package_load.py:22`) is
  removed in the same change set that introduces the compat policy; the unauthenticated
  import-then-trust path is replaced (not left beside the new one) in the same TEAx change.

## Validation Approach

RED-first on both attack coordinates and both skew directions. Phasing:

- **Phase 0 — RED (both repos).**
  - Attack (b), sysml-codegen: seal a package, drop a foreign file, run re-seal, assert it is
    currently hashed into `artifact_hashes` (reproduces `cli/__init__.py:762`).
  - Attack (a), TEAx: build a sealed package, replace `contracts/verify.py` with an `ok=True`
    stub, assert the loader currently loads it (reproduces `package_load.py:70-84`).
  - Skew, TEAx: two RED tests — seal version newer than runtime, and runtime newer than seal —
    each asserting current behavior does not name/reject as required.
- **Phase 1 — sysml-codegen (GREEN for attack b).** Publish `TRUSTED_VERIFIER_SHA256` + drift
  test; emit the manifest; add the `cmd_seal` provenance gate. Attack (b) → GREEN. Regenerate
  baselines. Item 6 tests (`test_verify_package.py`, `test_seal_step9.py`,
  `test_fingerprint_stability.py`, `test_contract_models.py`) stay green unchanged.
- **Phase 2 — TEAx (GREEN for attack a + skew).** Authenticate-before-exec against the vendored
  hash; replace the bare literal with the compat policy; re-seal the committed fixtures. Attack
  (a) + both skew directions → GREEN. Existing loader tests
  (`test_f1_arithmetic_fixture.py`, `test_failure_normalization.py`, study conftests) stay
  green against the re-sealed fixtures.

Success = every spec Success Criterion has a GREEN test that was RED before its phase, and the
named Item 6 regression tests are untouched-green.

## Next-Stage Handoff

- **Fixed:** the five decisions (D1–D5); the invariants (INV-A…G); sysml-codegen-first phasing;
  `verify.py` bytes stay stable; the walker boundary is not touched.
- **Open (for the plan / review):** exact manifest field names and whether
  `runtime_contract_version` belongs in the manifest or is read only from the seal; the precise
  form of the TEAx accepted-versions policy (single-version set vs range); whether the codegen
  drift test lives in `test_seal_step9.py` (extending INV-8) or `versions.py`'s own test.
- **De-risk first:** the stale-fixture position (D3). Confirm at review before Phase 2 writes
  the re-seal work, because flipping it changes INV-B/INV-F and the fixture change set.

---
Next Step: independent `/_my_design_review` in a fresh session, then `/_my_plan`.
