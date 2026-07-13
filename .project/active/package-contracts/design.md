# Design: Contracts and Sealing — `ModelContract` / `PackageContract`

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-13
**Branch:** constraint-exec-epic
**Base commit:** 46cb5a5
**Epic:** CONSTRAINT-EXEC — Item 9

---

## Overview

Turn a generated package from a loose directory of files into one verifiable unit. Two
graph/artifact contracts do it: a **`ModelContract`** (graph-only semantic identity — parameter
IDs, output IDs, constraint catalog, evaluation semantics, a semantic fingerprint) and a
**`PackageContract`** (a content-hash seal over the final artifact bytes plus generator/runtime
versions, verified on load). The S4 spike proved the shape; this item productionizes it and
closes S4's three named gaps (declared coverage set, missing-file detection, environment check).

## Related Artifacts

- **Spec:** `.project/active/package-contracts/spec.md`
- **Epic:** `.project/backlog/epic_constraint_execution.md` (Item 9)
- **Concept (Required Reading):** `.project/concepts/constraint-execution-and-design-space-studies-claude.md`
  — "Contracts and the Evaluator" (line 108-110), Architectural Bet "graph owns the catalog…
  packaging seals them" (line 74), no-circularity (line 96).
- **Upstream (landed):** Item 7 catalog + fingerprint (`generation/constraint_catalog.py:56,103`,
  `resolution/models.py:357-407`). S4 test-only seal:
  `.project/active/spike-vertical-slice-constraint-execution/s4_lib.py:903-975`.
- **Coordinated (in flight):** Item 8 snapshot v3 (`.project/active/snapshot-v3/design.md`) —
  byte-identical live/snapshot artifacts; the contingency the fingerprint-parity criterion rests on.
- **Downstream seam:** Item 0 mismatch 8 (teax `simkit/evaluation/` loader — outside this
  sandbox); Item 10 loader hardening; Item 14 integration sweep.

## Research Findings

- **Generation flow** — `cli/__init__.py:846` `run_codegen()` converges live and from-snapshot
  onto one `PipelineContext`, then writes artifacts in Steps 3–8 (`:902-934`). No sealing step
  exists. The seal is a natural **Step 9** after `_generate_tests` (`:934`), over the final
  on-disk state.
- **The graph fields ModelContract reads** — `resolution/models.py`: `ComputationGraph`
  (`:372-407`) with `entry_point_groups[].parameters` (`qualified_name`, `python_type`,
  `default_value`, `entry_type`), `modules[].outputs` (`channel_name`, `python_type`,
  `field_name`), and `constraint_catalog: ConstraintCatalog | None` (`:407`, `exclude=True`,
  `None` on a constraint-free corpus). `ConstraintCatalog` (`:357`) = `source_records` +
  `concrete_entries` + `fingerprint`.
- **Canonicalization already pinned** — `generation/constraint_catalog.py:56`
  `_canonical_json = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)`;
  Item 7's catalog fingerprint is sha256 of it (`:103`). S4 used the identical form
  (`s4_lib.py:860`). Reuse it for every fingerprint payload here.
- **S4's seal + its gaps** — `s4_lib.py`: `seal_package` (`:943`) rglobs and hashes (implicit
  coverage), `verify_seal` (`:962`) checks recorded hashes + extras but **never checks a recorded
  file is still present** (missing-file gap), **never declares coverage explicitly** (rglob), and
  **never checks versions** (env-compat gap). `write_contracts` (`:903`) already splits
  ModelContract (graph fields) from the seal.
- **Stencil preservation** — `cli/__init__.py:402-486` `_generate_stencils`: with
  `--preserve-handwritten` (`:467`) an existing `handwritten/*_impl.py` is kept as-is; otherwise a
  stub (`raise NotImplementedError`) is written. So the final artifact set at generation time may
  hold either stubs or filled-in human code — the seal must cover whatever is on disk *now*.
- **Versions available at generation** — `sysml_codegen.__version__ = "0.1.0"`
  (`src/sysml_codegen/__init__.py:9`); `package_name` from `GenerationConfig.package_name`
  (`cli/__init__.py:69`). No teax/runtime version is importable here (teax is a separate install,
  out of sandbox — confirmed: the `simkit/evaluation/` loader is unreadable this session).
- **Snapshot layering** — snapshot v3 (`snapshot-v3/design.md:332`) explicitly excludes sealing:
  "Parity here is graph/catalog identity, an input to the fingerprint." Contracts are generation
  *outputs*, downstream of the extraction snapshot — never persisted into it.

## Core Concept

A generated package carries two contracts in a `contracts/` subdirectory beside its code.

The **`ModelContract`** is the package's *semantic identity*: a pure function of the
`ComputationGraph` — parameter IDs, output IDs, the constraint catalog, the evaluation-semantics
tag, and a **semantic fingerprint** (sha256 over the canonical contract payload). It touches no
filesystem and no templates; a study layer reads it to know what it may vary, what it may observe,
and which constraints exist, without ever parsing YAML or module filenames.

The **`PackageContract`** is the package's *physical seal*: content hashes over the final
artifact bytes — generated **and** preserved-handwritten — plus generator and runtime versions.
It is **self-describing**: it records its own coverage policy (the explicit include/exclude
ruleset) and the full enumerated coverage set (`{relative_path: sha256}`), so any consumer can
re-verify with no out-of-band knowledge. From those hashes it derives the **executable
fingerprint** — the stable identity the study binds runs to.

The key insight is that **sealing is a pure function of a directory plus a declared coverage
policy**, independent of the generation pipeline that produced it. That single fact resolves the
stencil tension: the seal runs as the *last* step over final on-disk state (stubs or filled-in
alike), and re-sealing after a human edits a stencil is the *same function* run again — a modified
stencil correctly invalidates the seal until re-sealed. Verification is the mirror of that same
function: recompute hashes, compare to the recorded set both ways (nothing changed, nothing
missing, nothing extra), and check versions.

Fingerprints layer without circularity (concept line 96): IDs live in the graph → artifacts carry
the IDs → the semantic fingerprint hashes the semantic payload → artifact bytes (which contain the
IDs *and* the semantic fingerprint) → the executable fingerprint hashes those bytes. Each layer's
fingerprint is an input to the next layer's *bytes*, never to its own IDs.

Existing pieces this composes with, each keeping its concern:
- **Item 7 catalog + `_canonical_json`** (`generation/constraint_catalog.py`) — the catalog and its
  fingerprint are read, embedded, and reused for canonicalization; never rebuilt.
- **`ComputationGraph`** (`resolution/models.py`) — the sole input to `ModelContract`.
- **`run_codegen` artifact writers** (`cli/__init__.py`) — the seal joins their end as Step 9.
- **Item 8 byte-identity** — the contingency that makes both fingerprints stable across
  live/snapshot; this item inherits it, does not re-prove it.

## Key Bets

- **B1. The only live-model / pipeline dependency of a fingerprint is the artifact bytes and the
  graph — both of which Item 8 makes byte-identical across live and snapshot.** *If false → the
  executable or semantic fingerprint diverges live-vs-snapshot and the study's lineage binding
  (SC "fingerprint stability") breaks.*
- **B2. A content-hash seal over a self-describing coverage set is sufficient integrity for this
  epic — tamper, extra, and missing files are exactly the failure modes a study must catch.**
  *If false → an undetected package mutation lets a study record evidence against artifacts that no
  longer match what was generated (the spec's core "no integrity check" problem persists).*
- **B3. The verification algorithm is generic — it depends only on the seal's self-description, not
  on the specific model — so one small stdlib-only verifier serves every generated package and can
  be shipped inside it.** *If false → verification needs model-specific logic or a sysml-codegen
  import at load time, and a teax env without sysml-codegen cannot verify a package it loaded.*
- **B4. Human stencil edits change artifact bytes but never graph fields, so re-sealing must
  recompute the `PackageContract` and must NOT rebuild the `ModelContract`.** *If false → re-seal
  either misses the semantic contract (stale) or needs the graph (license/pipeline) at re-seal time,
  defeating the cheap license-free re-seal workflow.*

## Key Decisions

- **D1. Seal as Step 9 of `run_codegen`, over final on-disk state; a separate `seal` subcommand
  re-seals in place.** The seal runs after all artifact writers, covering stubs or preserved
  handwritten code as they exist. `sysml-codegen seal <package>` recomputes the executable seal
  over an edited package. *Rejected: seal at generation over stub-state only (a filled-in stencil
  then permanently mismatches — the exact stencil tension). Rejected: a fully separate `package`
  command distinct from `generate` (two commands to keep in sync for the common case where nobody
  edits a stencil; the Step-9 default already produces a valid seal, and `seal` is the opt-in
  re-seal).*
- **D2. Re-seal recomputes the `PackageContract` only; it does not rebuild the `ModelContract`.**
  The semantic contract is graph-derived and stencil-independent (B4), so re-seal is graph-free,
  license-free, fast. It validates that `contracts/model_contract.json` is present and covered.
  *Rejected: rebuild both on re-seal (needs the graph — reintroduces the license/pipeline
  dependency the snapshot path exists to remove).*
- **D3. The seal is self-describing: it records its coverage policy and the full enumerated
  coverage set.** `coverage_policy` = an explicit include/exclude ruleset (exclude the seal file
  itself, `**/__pycache__/**`, and a declared runtime-output location); `artifact_hashes` = the
  resolved `{rel_path: sha256}` enumeration. Verification applies the *recorded* policy, so
  producer and consumer never disagree on scope. *Rejected: S4's implicit `rglob` (coverage
  "declared" only by whatever happened to be on disk — the epic's coverage-set gap). Rejected: a
  hard-coded exclusion list in the verifier (a policy change silently desyncs old seals from new
  verifiers).*
- **D4. Verification is bidirectional and integrity failures are always fatal.** For each recorded
  path: it must exist and its hash must match (**tamper** + **missing** — closes S4's missing-file
  gap). Then walk the dir under the recorded policy: any surviving path not in the coverage set is
  an **extra/stale** file. All three raise a named diagnostic. *Rejected: S4's extras-only check
  (misses a deleted covered file). Rejected: returning advisory diagnostics for integrity (a hash
  mismatch is unambiguous corruption — never soft).*
- **D5. Environment compatibility is advisory-by-default, strict-promotable; integrity stays
  fatal.** The seal records `generator_version` (`sysml_codegen.__version__`, pinned constant) and
  `runtime_contract_version` (a pinned generator constant naming the runtime API the emitted code
  targets). Verify takes the loading environment's runtime marker as a parameter; a mismatch emits
  a named diagnostic — advisory (`ok` stays true) unless `strict=True`. *Rejected: fatal-by-default
  env-compat (a semver-compatible runtime patch bump would brick every package; the executable
  fingerprint already guarantees byte-identity, so versions are explanatory metadata a strict
  consumer may harden on). Rejected: reading the runtime version from the environment at generation
  (couples generation to an installed teax and breaks license-free snapshot determinism).*
- **D6. `ModelContract` embeds the constraint catalog by value; `constraint_catalog is None` →
  an explicit `null` field.** The study reads one semantic file with everything: parameter IDs,
  output IDs, the catalog (`source_records` + `concrete_entries` + Item-7 `fingerprint`), and the
  evaluation-semantics tag. A `None` catalog serializes as `constraint_catalog: null` — well-formed,
  and the semantic fingerprint over it is still stable (zero-constraint packages seal). *Rejected:
  fingerprint-only reference + a separate `constraint_catalog.json` (S4's split — two files the
  study must correlate; more seams). Rejected: minting a synthetic empty catalog for the None case
  (dishonest — `null` says "zero assertions" plainly).*
- **D7. Ship a stdlib-only verifier inside the package, copied verbatim from the canonical
  in-repo module.** `sysml_codegen/contracts/verify.py` (no sysml-codegen-internal imports —
  `hashlib`, `json`, `pathlib` only) is the one source of truth, tested in-repo against generated
  packages, and emitted verbatim as `contracts/verify.py`. A drift test asserts emitted ==
  source. *Rejected: teax vendors its own copy (drift with no in-repo guard). Rejected: teax
  imports `sysml_codegen.contracts` at load time (a teax env need not have sysml-codegen installed —
  B3). Either placement satisfies the [HARD] "shipped with / callable from within sysml-codegen"; a
  self-verifying package is the concept's intent and the more robust choice.*
- **D8. Contracts are always recomputed at generation (Step 9), never persisted into the extraction
  snapshot.** Both live and from-snapshot paths seal identically because Item 8 makes their
  artifacts byte-identical. *Rejected: carry contracts in the snapshot (they are generation outputs
  downstream of the extraction boundary; a snapshot-carried seal would be stale against re-generated
  bytes — and snapshot-v3 explicitly scopes sealing out, `snapshot-v3/design.md:332`).*

## Architecture

**Contract files** (in `<package>/contracts/`, JSON beside the package):

```
contracts/model_contract.json      # graph-only semantic contract (covered by the seal)
contracts/verify.py                # stdlib-only verifier, verbatim copy (covered)
contracts/package_contract.json    # the executable seal (EXCLUDED from its own coverage)
```

**Two serialization policies, both deterministic:**
- *Fingerprint payload* — `_canonical_json` (compact, `sort_keys`, reused from
  `constraint_catalog.py:56`). The semantic and executable fingerprints hash this form.
- *On-disk file bytes* — pretty deterministic (`json.dumps(..., indent=2, sort_keys=True,
  ensure_ascii=True)` + trailing newline). Human-readable **and** byte-stable, so
  `model_contract.json`'s own bytes hash reproducibly inside the seal.

**Seal data flow (Step 9 in `run_codegen`, `_seal_package`):**
1. `model_contract = build_model_contract(ctx.computation_graph)` — pure, graph-only.
2. Compute `semantic_fingerprint = sha256(_canonical_json(payload-without-the-fingerprint-field))`;
   embed it; write `contracts/model_contract.json` (deterministic bytes).
3. Copy the canonical verifier source verbatim to `contracts/verify.py`.
4. `package_contract = seal_package(output_path, package_name, coverage_policy)` — walk under the
   policy, hash every covered file (now including `model_contract.json` + `verify.py`), enumerate
   `artifact_hashes`, compute `executable_fingerprint = sha256` over `"\n".join(sorted "path:hash")`.
5. Write `contracts/package_contract.json` **last** (excluded from coverage — it holds the hashes).

Ordering is the invariant that keeps the seal well-formed: everything the seal covers is on disk
and final before the seal is computed; the seal file is the only thing written after.

**Verification (the `verify_package` seam — the contract Item 10 wires to):**

```python
def verify_package(
    package_dir: Path,
    package_name: str,                    # declared name; load-by-declared-name (mismatch 8)
    runtime_version: str | None = None,   # loading env's runtime marker; None → skip env-compat
    strict: bool = False,                 # promote env-compat advisory → fatal
) -> VerificationResult:                  # ok: bool; diagnostics: list[Diagnostic (kind, path?, msg)]
```

- Reads `contracts/package_contract.json`, applies its **recorded** `coverage_policy`.
- Integrity (always fatal → `ok=False`): each recorded path exists + hash matches (tamper/missing);
  no policy-scoped on-disk file is outside the coverage set (extra).
- Env-compat: `generator_version` / `runtime_contract_version` vs the loading environment; mismatch
  → diagnostic, `ok=False` only under `strict`.
- `package_name` mismatch (seal's recorded name ≠ requested) → its own diagnostic.
- A thin `verify_package_or_raise` wrapper raises on `not ok` for the ergonomic in-repo path;
  tests assert on `diagnostics`.

**The teax seam (stated, not built here):** Item 9 fixes the `verify_package` signature and the
self-describing seal. Item 10 makes teax's `simkit/evaluation/` loader call it — resolving the
package by *declared name*, injecting teax's installed runtime marker as `runtime_version`, and
choosing `strict`. That wiring is mechanical because the seal carries its own coverage policy and
versions; it lands with Item 14's integration sweep (or a follow-on), not this item. The exact
runtime marker teax exposes is confirmed during that wiring — recorded here as the injection point,
not assumed.

## Required Invariants

- **INV-1. `build_model_contract` is pure over the graph.** No filesystem, no template read on the
  ModelContract path (test-enforced — SC "ModelContract is graph-only").
- **INV-2. No circularity.** No ID (constraint/parameter/output) depends on any fingerprint;
  fingerprints only ever hash bytes/payloads that already contain the IDs.
- **INV-3. Seal ordering.** Every covered artifact is final on disk before the seal is computed;
  `package_contract.json` is written last and is never in its own coverage set.
- **INV-4. Bidirectional coverage.** Verification fails on a covered file that is tampered, a
  covered file that is missing, and a policy-scoped file that is extra.
- **INV-5. Byte-stable fingerprints.** Both fingerprints reproduce byte-exactly across independent
  live loads, from-snapshot generation, and separate sessions (contingent on Item 8 parity).
- **INV-6. Deterministic on-disk contract bytes.** `model_contract.json`'s bytes are a
  deterministic function of the graph, so its hash inside the seal is stable.
- **INV-7. Zero-constraint well-formedness.** `constraint_catalog is None` yields a well-formed
  `ModelContract` (`null` catalog) and a valid seal — the contract path never assumes a catalog.
- **INV-8. Emitted verifier == canonical source.** `contracts/verify.py` is byte-identical to the
  in-repo `sysml_codegen/contracts/verify.py` (drift guard).

## Component Overview

- **`ModelContract` / `PackageContract`** (`sysml_codegen/contracts/models.py`) — pydantic
  BaseModels matching the `resolution/models.py` style. ModelContract: `parameters`, `outputs`,
  `constraint_catalog: ConstraintCatalog | None`, `evaluation_semantics`, `semantic_fingerprint`.
  PackageContract: `package_name`, `coverage_policy`, `artifact_hashes`, `executable_fingerprint`,
  `generator_version`, `runtime_contract_version`.
- **`build_model_contract(graph) -> ModelContract`** (`sysml_codegen/contracts/model_contract.py`)
  — pure graph projection + semantic fingerprint. Imports no I/O (INV-1).
- **`seal_package(dir, name, policy) -> PackageContract`** (`sysml_codegen/contracts/seal.py`) —
  walk-hash-enumerate-fingerprint. The re-seal entry point too.
- **`verify.py`** (`sysml_codegen/contracts/verify.py`) — stdlib-only verifier; `verify_package`,
  `verify_package_or_raise`, `VerificationResult`, `Diagnostic`. Emitted verbatim into packages.
- **`_seal_package(ctx, config)`** (`cli/__init__.py`) — Step 9 orchestration; writes the three
  files in order.
- **`seal` subcommand** (`cli/__init__.py`) — in-place re-seal (D2): recompute the
  `PackageContract` over an existing package dir.
- **Version constants** (`sysml_codegen/contracts/versions.py`) — `RUNTIME_CONTRACT_VERSION`
  pinned token; `generator_version` reads `sysml_codegen.__version__`.

## Non-Goals

- **Study-side consumption** (Items 10–11): teax loader wiring, `ModelEvidence` projection, study
  fingerprint binding. This item ships the seal + `verify_package`; the runtime consumes them.
- **The teax-side wiring change itself** — Item 10 / Item 14. This item fixes the seam, not the
  caller.
- **Signing / cryptographic attestation** beyond content hashes.
- **Changing the constraint catalog or its fingerprint** — Item 7 owns it; Item 9 reads it.
- **Persisting contracts into the extraction snapshot** — contracts are generation outputs (D8).
- **Detecting a stale-but-consistent snapshot** — snapshot-v3's accepted boundary
  (`snapshot-v3/design.md:388`); the executable-fingerprint seal is *where* that staleness becomes
  a hard boundary at the study layer, but flagging an un-recaptured source edit is the loader's
  freshness warning, not this seal.

## Implementation Notes

- **Reuse `_canonical_json` verbatim** (`generation/constraint_catalog.py:56`) for every
  fingerprint payload — do not hand-roll a second canonicalizer. Consider lifting it to a shared
  helper if the import direction is awkward, but keep one definition.
- **Semantic fingerprint excludes itself.** Compute over the ModelContract payload with the
  `semantic_fingerprint` field absent (or emptied), then insert — mirroring S4 (`s4_lib.py:937`).
- **Runtime-output exclusion is by location, not extension.** Generated `.json` (schemas, input
  templates) must stay covered; only a declared runtime location (e.g. a reserved report/study
  path) is excluded. Record the exact patterns in `coverage_policy` so verify applies them
  identically. Where teax writes runtime outputs relative to the package is confirmed at Item 10
  wiring; default the policy to exclude the seal file + `__pycache__` and document the runtime-output
  slot as policy-extensible.
- **`verify.py` must import nothing from sysml-codegen.** Enforce with the drift test (INV-8) and a
  simple import-scan test. This is what lets a teax env verify without sysml-codegen installed.
- **Load by declared name (mismatch 8).** `verify_package` takes `package_name` and the seal
  records it; a name mismatch is a diagnostic. In-repo tests pass dir + name directly; teax resolves
  the installed package by name to its dir.
- **Re-seal preserves `model_contract.json`.** D2 recomputes only the seal; a re-seal over a package
  whose `model_contract.json` was deleted/edited fails integrity on the next verify (the semantic
  contract is covered) — which is correct.

## Potential Risks

- **Runtime-output location unknown until Item 10.** If teax writes outputs inside the package under
  a path the coverage policy doesn't exclude, on-load verify raises spurious "extra file". Mitigation:
  the policy is self-describing and extensible; the default excludes seal + `__pycache__`; the
  runtime-output slot is finalized at Item 10 wiring against the real loader. Stated as a seam, not
  assumed away.
- **Fingerprint parity is only as stable as Item 8.** If Item 8's byte-identity regresses, both
  fingerprints diverge live-vs-snapshot. Mitigation: inherit Item 8's parity gate; add a
  fingerprint-parity test that fails loudly if it regresses (the canary).
- **Emitted-verifier drift.** A change to the canonical verifier that isn't re-emitted leaves old
  packages with a stale `verify.py`. Mitigation: INV-8 drift test; the emitted copy is covered by
  the seal, so a hand-edit is caught on verify.
- **Over-strict env-compat.** A too-eager `strict` default would brick semver-compatible runtimes.
  Mitigation: D5 advisory-default; strict is the caller's opt-in.

## Integration Strategy

Single additive change on top of the landed Item 7 catalog and the in-flight Item 8 snapshot path:

1. **New `sysml_codegen/contracts/` package** — models, `build_model_contract`, `seal`, stdlib-only
   `verify`, version constants. No change to existing generation.
2. **Wire Step 9** into `run_codegen` (`cli/__init__.py:936`, before `return True`) and the `seal`
   subcommand. Both paths (live + from-snapshot) get the seal for free (D8).
3. **Tests** (see below) — in-repo, license-free, over a small generated fixture package.

Nothing existing changes shape; the seal is a strictly additive final step. The teax loader wiring
is a separate, later, mechanical change (Item 10 / 14).

## Validation Approach

- **Tamper (SC-1):** generate a fixture package, seal, mutate one covered file → `verify_package`
  returns `ok=False` with a tamper diagnostic naming the file.
- **Missing (SC-2, S4 gap):** delete a covered file → missing diagnostic. **Extra (SC-2):** add an
  unhashed policy-scoped file → extra diagnostic.
- **Env-compat (SC-3):** verify with a mismatched `runtime_version` → advisory diagnostic, `ok=True`;
  same under `strict=True` → `ok=False`.
- **Fingerprint stability (SC-4):** the same fixture sealed twice (independent sessions / live vs
  from-snapshot once Item 8 lands) yields byte-identical semantic and executable fingerprints.
- **Graph-only (SC-5):** `build_model_contract` runs against a graph with filesystem access patched
  to raise; asserts no I/O; a module-import scan confirms no template/Path dependency.
- **Zero-constraint (SC-6):** a constraint-free graph (`constraint_catalog is None`) yields a
  well-formed ModelContract (`null` catalog) and a valid seal.
- **Re-seal workflow:** seal → edit a stencil (seal now invalid) → `sysml-codegen seal <pkg>` →
  verify passes; ModelContract bytes unchanged.
- **Drift (INV-8):** emitted `contracts/verify.py` is byte-identical to the canonical source; the
  verifier imports nothing from sysml-codegen.
- **Suite:** `uv run pytest tests/` green; `ruff check src/` clean; no new mypy errors.

## Next-Stage Handoff

**Fixed:** the three-file `contracts/` layout and two-policy serialization (D3, Architecture); seal
as Step 9 + `seal` re-seal recomputing only the PackageContract (D1, D2); bidirectional
integrity-always-fatal verification (D4); env-compat advisory-default/strict-promotable with pinned
generator + runtime-contract versions (D5); ModelContract embeds catalog by value, `null` on None
(D6); stdlib-only verifier shipped verbatim (D7); contracts recomputed at generation, never in the
snapshot (D8); the `verify_package` signature (the Item 10 seam).

**Open for the plan:** the exact `coverage_policy` schema and its default runtime-output exclusion
patterns (finalized against the real teax loader at Item 10 — default to seal + `__pycache__`);
whether `_canonical_json` is lifted to a shared helper or imported from `generation`; the precise
`Diagnostic` kinds enum; the `RUNTIME_CONTRACT_VERSION` token's initial value and bump policy.

**De-risk first:** the fingerprint-parity test on the smallest constraint-bearing fixture, run
live vs from-snapshot the moment Item 8 certifies — that is the one criterion (SC-4) whose
stability this item cannot prove alone. If it diverges, the divergence is an Item 8 artifact-parity
regression, surfaced by this canary rather than discovered later at the study layer.

---

**Next Step:** After approval → `/_my_plan` (or `/_my_design_review` only if a contested call
surfaces in review). This is a well-trodden shape (S4 proved it); keep the plan proportional.
