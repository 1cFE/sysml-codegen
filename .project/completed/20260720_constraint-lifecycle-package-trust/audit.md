# Audit: Lifecycle Item 7 — Trusted Package Bootstrap and Seal Provenance

**Verdict:** Certify
**Audited:** 2026-07-20
**Branch:** constraint-exec-epic (both repos)
**Commits:** sysml-codegen `280a2bd`, teax `98a6d07`

---

## Summary

Both named attacks are closed, and every claim reproduced first-hand. The consumer-side
anchor (TEAx authenticates the package-local verifier bytes before executing them) is a
genuinely unforgeable hash gate with the TOCTOU seam closed — the executed bytes are the
hashed bytes. The producer-side gate (codegen's generation manifest + `cmd_seal` provenance
check) hard-fails a foreign file dropped in a non-glob location, and the prose is honest that
this is defense-in-depth, not proof against a same-privilege adversary. All four design-review
Majors landed correctly in code and design prose. The full battery is green in both repos.
One non-blocking hygiene gap: the evidence's candidate-commit line still carries placeholders.

## Findings

### Plan completion

No `plan.md` exists for this item; the design's Validation Approach (Phase 0 RED → Phase 1/2
GREEN) served as the plan. All phases are done and were reproduced:

- **Phase 0 RED, attack (a) + skew (TEAx)** — reverted the loader to pre-fix (`98a6d07^`),
  kept the HEAD test: **3 failed** — `test_unconditional_success_verifier_rejected_before_exec`
  (stub loaded, no raise) and both `test_version_skew_fails_closed_both_directions[2.0.0|0.9.0]`
  (pre-fix message is `RUNTIME_MISMATCH`, not the named accepted-versions policy). Control
  passed. Restored clean.
- **Phase 0 RED, attack (b) (codegen)** — reverted the five Item-7 src files to pre-fix
  (`280a2bd^`), removed `manifest.py`, kept the HEAD test: **3 failed** —
  `test_reseal_rejects_foreign_file_as_codegen_provenance` (`cmd_seal` returned 0, laundered),
  `test_reseal_rejects_edit_to_codegen_produced_file`, and `test_generate_emits_generation_manifest`
  (no manifest emitted). Restored clean via `git checkout`.
- **Phase 1/2 GREEN** — `test_seal_step9.py` 13 passed; `test_package_trust.py` 4 passed
  (attack a, skew ×2, control). Both re-run first-hand.

### Spec conformance

- **Attack (a) — unconditional-success verifier rejected before exec:** MET.
  `_load_authenticated_verifier` (`teax package_load.py:56-81`) reads `verify.py` once, hashes
  against `TRUSTED_VERIFIER_SHA256`, and on match execs *those exact bytes*
  (`exec(compile(source, str(verify_path), "exec"), module.__dict__)`). The stub-verifier test
  asserts both `SealVerificationError` **and** the `_pwned_marker` (written by the stub's module
  body) is absent — so no package code ran before authentication (INV-A). Verified RED→GREEN.
- **Attack (b) — foreign-file laundering refused:** MET. `check_reseal_provenance`
  (`manifest.py:60-118`) classifies each covered file: in the enumerated `codegen_produced` set
  → hash must equal prior seal (frozen); under a non-codegen glob → admitted; otherwise →
  `ProvenanceError` hard-fail. A `modules/evil.py` in a non-glob location hard-fails and is
  never recorded. Verified RED→GREEN. Sibling INV-F (edit to a generated file → hard-fail) also
  met.
- **Version skew fails closed both directions with a naming diagnostic:** MET.
  `ACCEPTED_RUNTIME_CONTRACT_VERSIONS = frozenset({"1.0.0"})`; the loader rejects any
  `recorded_version not in` the set (both newer and older), naming "accepted runtime-contract
  versions" (`package_load.py:113-119`). The bare `RUNTIME_CONTRACT_VERSION = "1.0.0"` literal
  is deleted — grep finds only docstring mentions, zero code survivors.
- **Item 6 guarantees stay green:** MET. `test_verify_package.py` (38) +
  `test_fingerprint_stability.py` (4) + `test_contract_models.py` (17) = **59 passed**,
  unchanged, no fixture regen. `test_seal_step9.py` symlink/verbatim tests green.
- **One authority, no bypass:** MET. Acceptance lives only in the loader; `verify_package` is
  passed the seal's own version, making its symmetric-`==` a satisfied no-op. The bare literal
  and the symmetric-`==` authority are deleted. `seal_package` and both walkers untouched.
- **Generation manifest records provenance, re-seal consults it:** MET. `GenerationManifest`
  (`models.py:92-114`) carries `codegen_produced` / `handwritten_globs` / `runtime_globs`, no
  `runtime_contract_version` (seal owns it), emitted before the seal so it is itself covered.

Non-goals respected: no second catalog authority, no reopened Item-6 matrix, `runtime_globs`
deliberately empty, `GENERATOR_MISMATCH` not revived, seal signing explicitly out of scope.

### Design conformance — the four Majors (verified independently, no second review round)

1. **TOCTOU (Major 1):** CLOSED. The loader execs the exact bytes it hashed — one
   `read_bytes()`, then `exec(compile(source, ...))`. No `exec_module`, no `spec_from_file_location`,
   no second read; `importlib.util` import removed. A swap between hash and exec is impossible
   because there is no second read. Verified in `package_load.py:56-81`.
2. **Version policy (Major 3):** single-image `frozenset({"1.0.0"})`; both skew directions fail
   closed with the named diagnostic (reproduced RED for both 2.0.0 and 0.9.0); the bare literal
   has zero code survivors. The version check reads seal JSON only and runs *before* verifier
   authentication — safe ordering.
3. **Manifest honesty (Major 2):** the unforgeable-consumer-anchor vs defense-in-depth-producer-gate
   distinction is stated in design Core Concept (`design.md:88-97`) and in the
   `check_reseal_provenance` docstring; the same-privilege / seal-signing Non-Goal is present
   (`design.md:254-258`). `codegen_produced` = tree-minus-`handwritten/**`-minus-runtime-globs
   is *actually* implemented that way (`manifest.py:39-50`), and the completeness test — drop a
   foreign file in a non-glob location → hard fail — passes (and reproduced RED).
4. **Churn (Major 4 / Minor):** codegen commit touched **no** `baseline_outputs` (10 files, all
   Item-7 contract/CLI + docs); codegen has no committed sealed-tree fixture, so the manifest
   adds none. TEAx diff is exactly the enumerated re-seals + loader + test: 7 files =
   `package_load.py` + `test_package_trust.py` + 2× `verify.py` + 2× `package_contract.json` +
   1× `GENERATION.md`. `test_fingerprint_stability` needed no regen (all assertions relative).

**D3 re-seal correctness:** both fixtures now carry canonical `ad0a855…` verify.py bytes; each
seal's recorded `contracts/verify.py` hash equals it; `runtime_contract_version` stays `1.0.0`
(correction to the single 1.0.0 image, not a bump). No files added — covered sets unchanged.
A repo-wide search found only these two sealed fixtures, so the re-seal set is complete.

### Code integrity

No slop or failure-honesty issues. Specifics checked:

- The version check `except (OSError, json.JSONDecodeError)` and the verifier
  `except OSError` are narrow and re-raise as `SealVerificationError` — fail-closed, not
  swallowed. The provenance gate raises `ProvenanceError` on every unaccounted path (foreign,
  edited-codegen, tampered manifest, missing-codegen); no silent default.
- `check_reseal_provenance` reuses `_glob_to_regex` / `_is_covered` from `seal.py` — it adds no
  walker and edits neither `seal.py` nor `verify.py` (INV-D honored).
- The manifest's self-reference is handled by construction (`codegen.add(MANIFEST_REL_PATH)`)
  rather than a special-case at the gate — no circularity (its anchor is the *prior* seal's
  recorded hash).
- The `handwritten/**` admit-and-execute residual is on record as an accepted Non-Goal, not a
  silent gap.

---

## Certification

Checked and reproduced first-hand:
- Both attacks RED against pre-fix (loader reverted to `98a6d07^`; codegen src reverted to
  `280a2bd^`), GREEN at HEAD. Working trees restored clean afterward.
- TOCTOU closed (compile+exec of read bytes, no `exec_module`); single-version policy, both
  skew directions named, bare literal zero survivors.
- Manifest = tree-minus-globs; foreign-file-in-non-glob → hard fail; honesty prose + Non-Goal
  present in code and design.
- D3 fixtures at canonical `ad0a855`, version unchanged, nothing else moved.
- Full suites: codegen **3068 passed, 44 skipped, 17 deselected, 0 license skips**; teax
  **281 passed**; certified Item-6 surface **59 passed**; mypy **72** (base 73, Item 7 adds 0);
  ruff clean on all Item-7 files.
- Scope: codegen touched only Item-7 contract/CLI files; teax touched only the loader + test +
  re-sealed fixtures — Items 1–6 acceptance surfaces (extraction/analysis/graph/generation)
  untouched.

**Findings requiring no code change but noted:**
- **Evidence hygiene (minor, non-blocking).** `evidence.md:165-166` and `CURRENT_WORK.md:27`
  still carry `<CANDIDATE_REV_CODEGEN>` / `<CANDIDATE_REV_TEAX>` placeholders; the commits are
  now known (`280a2bd` / `98a6d07`). Does not affect the delivered code; fill before Item 13.

**Not checked:**
- The full `python -O` suite count (evidence claims 2 failures). I ran only the flagged file
  (`test_expression_compiler.py`) under `-O` and confirmed the failures are assert-strip
  artifacts in assertion-raising tests; Item 7 touches none of that code, so they are
  pre-existing by construction. The exact whole-suite `-O` tally was not independently re-run.
- The agentic-mbse repo was not diffed. The design claims Item 7 has no agentic-mbse change;
  scope (fix lives in codegen loader/contracts + teax loader) is consistent with that, but I
  did not independently confirm the absence of an agentic-mbse diff.
- The actual PR push (Item 13's job); the commits are correctly unpushed.
- Same-privilege / collusive re-seal adversary — explicitly out of scope (seal signing
  Non-Goal); not a gap this item claims to close.
