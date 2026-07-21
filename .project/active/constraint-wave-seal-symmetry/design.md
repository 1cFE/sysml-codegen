# Design: Seal and Verify Symlink Symmetry

**Status:** Draft — revised after design review
**Owner:** Reid W
**Created:** 2026-07-18 19:55 PDT
**Revised:** 2026-07-18
**Branch:** constraint-exec-epic
**Base commit:** 512786c
**Epic:** CONSTRAINT-WAVE-REMEDIATION — Item 6 (R-10)

---

## Overview

Make any symlink at the package root or beneath it invalid before an integrity route follows,
opens, resolves, or writes through that link. One root-aware, non-following tree inspection runs at
the start of direct seal, verification, CLI generation output mutation, Step 9, and re-seal. A
link fails deterministically as `INVALID_PATH`; only an inspected link-free tree reaches seal
loading, coverage, hashing, contract writes, or other target-following operations.

## Related Artifacts

- **Spec:** `.project/active/constraint-wave-seal-symmetry/spec.md`
- **Design review:** `.project/active/constraint-wave-seal-symmetry/design-review.md`
- **Epic:** `.project/backlog/epic_constraint_pr_wave_remediation.md`, Item 6
- **Primary R-10 research:**
  `.project/research/20260718-192048_constraint-exec-pr-wave-code-review.md`
- **GAP-CLOSE F9:** `.project/active/gap-boundary-guards/{spec,plan,evidence}.md`
- **Package contract:** `docs/architecture/reference/29-contracts-and-sealing.md` and
  `.project/completed/20260713_package-contracts/{spec,design,audit}.md`

## Research Findings

- Direct seal currently starts with `package_dir.rglob("*")`, then calls target-following
  `is_file()` and `read_bytes()` (`src/sysml_codegen/contracts/seal.py:57`). It hashes file-link
  targets and skips directory or dangling links.
- Verification currently opens and parses `contracts/package_contract.json` before it walks the
  package (`src/sysml_codegen/contracts/verify.py:185`). Its recorded-artifact pass resolves and
  hashes before its later directory-link-only check (`src/sysml_codegen/contracts/verify.py:204`,
  `src/sysml_codegen/contracts/verify.py:263`).
- A real-root Python 3.12 `Path.rglob("*")` exposes descendant file, directory, and dangling links
  without descending through directory links. It does not inspect the root itself; `rglob` on a
  symlink root can traverse the target. The project requires Python 3.12+
  (`pyproject.toml:10`). A separate non-following root check is therefore mandatory.
- Step 9 creates `contracts/`, writes the model contract, and copies the verifier before calling
  direct seal (`src/sysml_codegen/cli/__init__.py:610`). Re-seal calls target-following
  `model_contract_path.is_file()` before direct seal (`src/sysml_codegen/cli/__init__.py:704`).
  Route-level safety requires an earlier guard, not only a guard inside `seal_package`.
- The existing isolation pattern deliberately duplicates the glob matcher in seal and verifier,
  AST-compares its body, imports only stdlib in the verifier, and copies canonical verifier bytes
  verbatim (`tests/unit/test_contract_models.py:161`, `tests/unit/test_verify_package.py:346`,
  `tests/conformance/test_seal_step9.py:47`). The link inspector should follow this pattern.
- The reviewed canonical verifier SHA-256 is
  `24eb3565b0a7a682cf8a2510c871d7af9baa938fdaac6b5e826f88045a400276`. The verifier must change;
  Step 9 covers its emitted bytes (`src/sysml_codegen/cli/__init__.py:630`,
  `tests/conformance/test_seal_step9.py:72`). A newly generated package must therefore receive a
  different verifier artifact hash and a different executable fingerprint.

## Core Concept

The symlink rule is a prerequisite to package I/O, not a coverage-policy rule. The inspector first
checks the package root itself with a non-following symlink predicate. For a real root, it fully
materializes the standard-library non-following descendant walk, sorts entries by canonical
package-relative POSIX path, and checks each entry itself with `is_symlink()` before any caller
uses the paths. The result is either one forbidden-link path or a reusable sorted link-free entry
list. Seal and verifier duplicate this small stdlib algorithm and AST-pin it; CLI routes reuse the
seal-side guard before their own output-tree reads or writes. This single boundary catches a
symlink root, `contracts/`, the seal file, excluded paths, file/directory links, and dangling links
without consulting targets.

## Key Bets

- **B1.** The package tree is quiescent during an operation, as the existing physical seal already
  assumes. *If false → a path can change after inspection and before use; this item does not add
  filesystem snapshots or locking.*
- **B2.** For a root proven not to be a symlink, Python 3.12's default `Path.rglob("*")` enumerates
  descendant symlink entries without descending through directory links. *If false → target
  traversal or an unseen link breaks the all-links-forbidden boundary.*
- **B3.** Generation code creates only regular files/directories after its initial output-tree
  inspection. *If false → a generator step could introduce and use a link before the Step 9
  recheck; tests must pin that production writers do not create links.*

## Key Decisions

- **D1. Inspect root, then descendants, before route-specific package I/O.** Root inspection uses
  `is_symlink()` before `rglob`; the root-link path is the canonical token `"."`. For a real root,
  descendant paths use `relative_to(package_dir).as_posix()`. *Rejected: descendant-only `rglob`
  (misses and can traverse a symlink root). Rejected: inspect after seal load or contract-path
  checks (those operations can already follow `contracts/` or a contract-file link).*
- **D2. The duplicated inspector returns `(forbidden_path, entries)`.** On a link it returns its
  path and no usable entries; on success it returns `None` plus the complete sorted link-free entry
  list. Seal hashes from that list, and verification uses it for the extra-artifact phase, so no
  second walk introduces another ordering or walker-error point. *Rejected: `str | None` followed
  by a second walk (leaves walker precedence and race behavior ambiguous). Rejected: a shared
  project import or third emitted module (breaks or expands the standalone boundary).*
- **D3. Materialize the whole descendant walk before classifying descendants.** An `OSError` from
  the root inspection or walk means classification is incomplete and wins over any descendant link
  that may have been yielded earlier. A successfully classified root link still wins because it
  precedes the walk. *Rejected: classify a lazy stream until the first link (the observed result can
  depend on filesystem enumeration order before canonical sorting, and later walker failure becomes
  ambiguous).*
- **D4. Seal uses `PackageSealError(ValueError)` only for policy failures.** It carries
  `kind="INVALID_PATH"`, canonical `path`, and exact
  `message="symlinks are forbidden beneath the package root"`; string form is
  `INVALID_PATH(<path>): <message>`. Direct seal propagates walk/hash `OSError` unchanged. *Rejected:
  a result union or `PackageContract` change (expands every success caller and the schema). Rejected:
  bare `ValueError` (cannot distinguish policy failure from other validation errors).*
- **D5. Verification preflight precedes `_load_seal` and returns immediately on preflight
  failure.** A link becomes one fatal `INVALID_PATH`. A walk `OSError` becomes one fatal
  `ARTIFACT_UNREADABLE`, `path=None`, with message
  `package artifact preflight failed: <error>`. Neither case opens the seal or hashes a file.
  *Rejected: append and continue (can duplicate a link as `MISSING`, `TAMPER`, or another
  `INVALID_PATH` and can use its target).*
- **D6. CLI routes guard before their first output-tree access and recheck at the final integrity
  boundary.** `run_codegen` inspects an existing output tree before clear/setup/writes and Step 9
  reinspects before creating/writing `contracts/`; `cmd_seal` inspects before
  `model_contract_path.is_file()`. *Rejected: direct-seal-only protection (does not protect CLI
  operations that precede direct seal).*
- **D7. Fingerprint stability is scoped to unchanged bytes, not historical generated packages.**
  The regular-file hash algorithm and all non-verifier artifact hashes remain unchanged. New
  generation intentionally changes the covered verifier hash and consequently the executable
  fingerprint. *Rejected: promise the old full-package fingerprint (incompatible with changing the
  covered verifier). Rejected: exclude the verifier from coverage (weakens the physical seal and
  violates the package-contract referent).*

## Architecture and Route Order

The duplicated inspector has this conceptual interface:

```python
def _inspect_package_tree(root: Path) -> tuple[str | None, list[tuple[str, Path]]]:
    """Return forbidden path or a sorted, link-free descendant list; may raise OSError."""
```

It performs only:

1. non-following `root.is_symlink()`; if true, return `(".", [])`;
2. fully materialize `root.rglob("*")`; any `OSError` escapes;
3. sort by entry-relative POSIX path;
4. scan `entry.is_symlink()` only; return the first path and no entries, or the clean list.

No `resolve()`, `open`, `read_*`, `is_file()`, `is_dir()`, coverage check, or contract write occurs
inside or before this boundary for an existing package tree.

| Route | Required order |
|---|---|
| direct `seal_package` | inspect → reject or hash covered regular files from inspected entries → build contract |
| `verify_package` / emitted verifier | inspect → link/walk failure return or load seal → existing integrity checks using inspected entries |
| generation | build graph (no output-tree I/O) → inspect existing output → clear/setup and Steps 3–8 → Step 9 reinspect → write model/verifier → seal from a fresh inspected list → write package contract last |
| re-seal | inspect → model-contract regular-file check → `seal_package` reinspect/hash → write replacement package contract |

The second inspection at mutation boundaries retains the existing quiescent-tree assumption but
narrows the check/use window. It does not claim race-free filesystem atomicity.

## Deterministic Failure Precedence

Verification and seal use this order:

1. **Root link:** `INVALID_PATH`, path `"."`; no traversal.
2. **Root-inspection or descendant-walk `OSError`:** verifier returns sole
   `ARTIFACT_UNREADABLE`; direct seal propagates the `OSError`; no partial contract. Because the
   walk must complete before sorting, this wins over any descendant link not yet fully classified.
3. **Descendant link:** `INVALID_PATH` at the lexically first relative POSIX path. Thus `contracts`
   beats `contracts/package_contract.json` because a linked directory is not descended; an actual
   linked seal file is reported only when `contracts/` is real.
4. **Seal load:** existing `SEAL_MISSING`, `SEAL_UNREADABLE`, or `SEAL_MALFORMED`, only after a
   link-free inspection.
5. **Valid-seal integrity:** seal fingerprint/name checks retain their current phase positions;
   recorded artifacts are evaluated in sorted path order. Missing, tamper, and per-file unreadable
   findings appear in that order by path, not by kind.
6. **Extras:** policy-covered extras from the inspected entry list appear after all recorded-path
   findings, in lexical relative-path order.
7. **Runtime advisory:** remains last.

Therefore a link always wins over missing/extra/seal-malformed outcomes when inspection completes;
walker failure wins when the tree cannot be completely classified; and mixed missing-plus-extra
results are deterministic: all sorted recorded findings precede all sorted extras.

## Required Invariants

- **INV-1 — Complete location policy.** `"."`, `contracts`,
  `contracts/package_contract.json`, excluded/runtime-output paths, and every other descendant are
  subject to the same all-links-forbidden policy. This design retains the spec's `[INFERRED]`
  force for excluded paths; it does not present that inference as owner-settled.
- **INV-2 — No target use before classification.** Root/entry `is_symlink()` and the documented
  non-following real-root walk are the only permitted preflight filesystem operations.
- **INV-3 — No target-dependent result.** Internal, escaping, and dangling file or directory links
  produce the same kind/message; targets are never resolved, opened, traversed, or hashed.
- **INV-4 — Canonical deterministic path.** Root is `"."`; descendants are relative POSIX paths;
  the lexical first link is the sole link result.
- **INV-5 — No partial contract.** Direct seal returns a complete `PackageContract` or raises.
  Generation and re-seal write no replacement package contract after policy, walker, or hash I/O
  failure; an existing contract remains byte-identical.
- **INV-6 — Shared public classification.** Seal error and verifier diagnostic share
  `INVALID_PATH`, path, and exact message.
- **INV-7 — Honest fingerprint stability.** For identical link-free input bytes, direct seal and
  re-seal remain deterministic. New generation preserves every non-verifier artifact hash but
  intentionally changes the verifier hash and executable fingerprint.
- **INV-8 — Isolation and drift.** Canonical `verify.py` remains stdlib-only; inspector and glob
  matcher bodies are AST-identical across seal/verifier; emitted verifier bytes equal canonical.

## Fingerprint Consequences

- **Reviewed verifier:**
  `sha256(src/sysml_codegen/contracts/verify.py) = 24eb3565b0a7a682cf8a2510c871d7af9baa938fdaac6b5e826f88045a400276`.
- **Candidate verifier:** its exact hash is determined by the final reviewed source bytes. The
  required relation is
  `artifact_hashes["contracts/verify.py"] == sha256(canonical_candidate_verify_bytes)` and
  `emitted_verify_bytes == canonical_candidate_verify_bytes`; that candidate hash must differ from
  the reviewed hash above because policy code changes.
- **Other artifacts:** for the same symlink-free generated model and environment, every
  `artifact_hashes` entry other than `contracts/verify.py` remains byte-identical. The seal file is
  excluded from its own artifact set.
- **Executable fingerprint:** it remains SHA-256 of sorted `path:hash` lines. Replacing the verifier
  line necessarily produces the candidate generation's new expected executable fingerprint. The
  design does not hardcode a candidate hex value before candidate source bytes exist; implementation
  evidence must record both exact candidate hashes and prove the verifier line is the only changed
  input.
- **Re-seal:** re-seal does not refresh emitted `verify.py`. An unchanged existing package therefore
  retains its current artifact hashes/fingerprint; a newly generated package carries the new
  verifier hash from creation onward.

## Component Overview and File-Level Changes

- **`src/sysml_codegen/contracts/seal.py`** — add the root-aware inspector,
  `PackageSealError`, and a seal-side guard callable for CLI use. Hash only from the returned clean
  entries; keep coverage and fingerprint formulas unchanged.
- **`src/sysml_codegen/contracts/verify.py`** — add the AST-identical inspector; call it before
  `_load_seal`; normalize walk failure; pass clean entries into extra-artifact checking; remove the
  later directory-target-specific link check. Keep imports stdlib-only and signatures unchanged.
- **`src/sysml_codegen/contracts/__init__.py`** — export the seal error and CLI guard.
- **`src/sysml_codegen/cli/__init__.py`** — guard generation before output mutation and again before
  Step 9 contract writes; guard re-seal before model-contract inspection; translate
  `PackageSealError`/`OSError` into existing false/nonzero command outcomes without writing a seal.
- **`tests/unit/test_contract_models.py`** — pin inspector AST parity and direct-seal matrix; pin the
  reviewed tiny regular-tree hash/fingerprint controls.
- **`tests/unit/test_verify_package.py`** — canonical root/ancestor/file/excluded/target matrix,
  no-follow probes, walker failure, mixed-error precedence, and exact messages.
- **`tests/conformance/test_seal_step9.py`** — emitted matrix, byte identity, generation pre-write
  guards, Step 9 failure, and failed re-seal preservation.
- **`tests/conformance/test_fingerprint_stability.py`** — retain current within-version independent
  generation and live/snapshot parity. Add source-isolated reviewed-to-candidate comparison of
  non-verifier artifact equality, the exact canonical/emitted verifier hash relation, and the
  expected executable-fingerprint change across the policy update.

No contract model, serializer, coverage schema, snapshot, fixture layout, archive, or loader change.

## Failure Behavior

| Route | Link outcome | Walk/hash I/O outcome | Package-contract write |
|---|---|---|---|
| direct seal | raises `PackageSealError` | propagates `OSError` | returns no contract |
| canonical/emitted verify | sole fatal `INVALID_PATH` | sole fatal preflight `ARTIFACT_UNREADABLE`; later per-file errors keep existing diagnostics | none |
| generation / Step 9 | logs `Package sealing failed: <error>`; returns `False` | same command outcome | no new/replacement seal; prior bytes preserved |
| `cmd_seal` | same log; returns `1` | same command outcome | prior seal bytes preserved |

Generation may have written ordinary Steps 3–8 artifacts before the Step 9 recheck fails. “No
partial contract” means no returned or replacement `PackageContract`; this item does not make the
whole generation directory transactional.

## RED/GREEN Validation Matrix

| Case | Reviewed state | Candidate result |
|---|---|---|
| regular file / real directory | control green | unchanged seal algorithm; no link finding |
| package root symlink | target may be traversed | `INVALID_PATH`, path `"."`, no traversal |
| `contracts/` symlink | verifier/CLI may follow or write target | `INVALID_PATH`, path `contracts` |
| seal-file symlink under real `contracts/` | verifier opens target | `INVALID_PATH`, full seal path |
| file link × internal/escaping/dangling | hashes, fails late, or skips | common early `INVALID_PATH` |
| directory link × internal/escaping/dangling | seal skips; verifier partial | common early `INVALID_PATH`, no descent |
| link under excluded/runtime-output path | skipped | common early `INVALID_PATH` |
| multiple links | undefined across routes | sole lexical first path |
| root link + missing/malformed seal | seal outcome may win/follow | root link wins |
| descendant link + missing/extra artifact | route-dependent | link wins after complete walk |
| walk `OSError` + possible descendant link | unspecified | walk error wins; no link claim |
| missing recorded + extra file | phase-dependent but unpinned | sorted recorded findings, then sorted extras |

### Required route tests

- Run root, `contracts/`, seal-file, six target/type cells, excluded-path, and multiple-link cases
  through direct seal plus canonical and emitted verification.
- Patch target `resolve`, file/directory predicates, reads, and descendant access to fail; link
  classification must still succeed without invoking them.
- Inject preflight walk `OSError`; verify exact sole diagnostic, direct exception, command outcome,
  and byte-identical prior seal.
- Test mixed precedence exactly as the table above, including a recorded regular file replaced by a
  link producing no `MISSING`, `TAMPER`, or containment duplicate.
- For generation, place a root/descendant link before output mutation and another before Step 9;
  assert the appropriate guard fails before the next write. For re-seal, assert the model-contract
  check never follows a linked `contracts/` or model-contract path.
- Pin the reviewed verifier hash, candidate canonical/emitted equality, non-verifier artifact-hash
  equality, changed verifier artifact hash, and the consequent changed executable fingerprint.
- Retain glob matcher parity, inspector parity, stdlib import scan, and emitted byte identity.

Historical RED uses exact reviewed commit `512786c`. F9 cases already green remain controls, not
newly claimed RED.

## Implementation Notes

- Do not call `resolve()`, `is_file()`, `is_dir()`, `open`, `read_*`, `mkdir`, `copy`, or clear the
  output tree before the applicable route guard.
- The root spelling `"."` is a diagnostic token only; never join it back to resolve a target.
- Sort recorded hashes explicitly rather than relying on JSON insertion order.
- Reuse the successful preflight entry list for the seal hash pass and verifier extra pass.
- Successful re-seal continues to recompute only `package_contract.json`; it does not refresh the
  emitted verifier.
- Ancestors above the caller-supplied package root and concurrent mutation after inspection remain
  outside this item. Do not add locks, snapshots, or platform-specific APIs.

## Potential Risks

- **Route guard drift.** A future write may be inserted before inspection. Mitigation: tests patch
  the first prohibited operation and assert it is never reached for root or contract-path links.
- **Walker behavior changes.** Mitigation: kept target-descendant tests on every supported Python
  version prove directory links are not descended.
- **Classifier copies drift.** Mitigation: AST body equality plus the shared matrix and emitted-byte
  guard.
- **Fingerprint tests encode the old contradiction.** Mitigation: compare all non-verifier entries,
  assert exact verifier derivation/equality, and require the executable fingerprint to change.

## Integration Strategy

Land the inspector and error contract first, then place guards before verifier seal loading and CLI
output-tree access, then route existing hashing/extra checks through the inspected entry list. No
contract version bump or migration is needed: JSON shape and hash formula stay fixed. The only
intentional valid-package byte change is the covered emitted verifier and the seal values derived
from it.

## Non-Goals

- Supporting, copying, dereferencing, hashing, or recording any symlink or its metadata.
- Changing contract schemas, coverage globs, package layout, snapshots, archives, runtime outputs,
  package installation, or loader behavior.
- Making the entire generation output transactional or race-free.
- Normalizing unrelated non-walker I/O diagnostics or closing external GAP-CLOSE F1.

## Next-Stage Handoff

**Fixed by this design:** root token `"."`; root-first/full-walk/lexical-link precedence; route
guards before seal loading, model-contract checks, clear/setup, and Step 9 writes;
`PackageSealError`; verifier `INVALID_PATH`/`ARTIFACT_UNREADABLE` behavior; no partial package
contract; honest verifier-hash and executable-fingerprint consequences; stdlib-only and emitted
byte identity.

**Inherited/inferred, still challengeable:** every descendant link is forbidden even under an
excluded path. The current stage request requires accounting and tests for that boundary, but the
design preserves its provenance rather than marking it owner-settled.

**Open:** no technical design question remains. The implementation evidence must record the exact
candidate verifier artifact hash and generated executable fingerprint once candidate source bytes
exist.

---

Next Step: After approval → `my-plan`
