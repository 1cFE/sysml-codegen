# Spec: GAP-CLOSE Item 5 — Packaging, Docs, and Hygiene Closeout + Wave Gates

**Status:** Local Scope Certified — Ready for Explicitly Partial Pre-PR
**Owner:** Reid W
**Created:** 2026-07-18
**Complexity:** MEDIUM
**Branch:** constraint-exec-epic
**Epic:** GAP-CLOSE — Item 5

---

## Problem

The coordinated constraint-execution branches now contain the Item 1–4 code changes, but the
installable package contract, durable documentation, and several local hygiene surfaces still
describe or assume the pre-v3 system. Both companion generations identify as `0.1.0`, and codegen's
declared `agentic-mbse>=0.1.0` dependency permits metadata-only resolution against a companion that
lacks the v3 profile behavior. Editable sibling installs hide that mismatch. The three shipped or
durable docs still teach three outcomes, obsolete equality and connective behavior, or the false
claim that snapshot generation has no companion lockstep surface.

The remaining hygiene defects make the final wave harder to use and verify outside this checkout:
two catalog field types have ambiguous public visibility, the catalog fingerprint docstring omits
excluded records, the loader cites a stale source line, codegen warnings discard actionable
diagnostic messages, and the execution test lane hard-codes one machine's TEAx path. The proposed
branch ranges also contain trailing whitespace. These are closeout defects at package, docs, and
local test boundaries. They do not require a product or architecture change.

Items 1–4 are implemented locally, but GAP-CLOSE F1 is not complete end to end. Sysml-codegen
propagates exceptional arithmetic correctly; external `[GAP-CLOSE-F1-TEAX-NORMALIZATION]` still
owns evaluator normalization and constraint-module identity. A green Item 5 therefore cannot by
itself justify claiming F1 or the epic complete.

## Success Criteria

- [x] `agentic-mbse` reports one real compatible patch release consistently from its built package
      metadata and `agentic_mbse.__version__`; sysml-codegen's built metadata requires at least that
      release. A metadata-only probe proves that the declared codegen requirement rejects companion
      `0.1.0` and accepts the new release without relying on the editable sibling override, imports,
      or the runtime profile pin.
- [x] Companion `docs/patterns/constraints.md` teaches all four v3 outcomes and their consequences:
      `ADMIT`, `BLOCK`, `NON_NUMERICAL`, and `UNASSESSED`. It states that `==` and `!=` never enter
      numerical execution; Boolean, string, and enumeration equality are non-numerical warnings,
      while integer, real, and quantity equality block for the documented float-path or missing-
      tolerance reasons. It states that valid binary `xor` and `implies` are classified by
      numerical containment, while malformed arity default-denies.
- [x] Codegen `docs/architecture/reference/28-constraint-lowering-and-catalog.md` uses the same
      four-outcome vocabulary and documents `excluded_records`, including its validated exclusion
      payload and inclusion in the catalog fingerprint.
- [x] Codegen `docs/architecture/reference/27-snapshot-generation.md` replaces the false “no
      lockstep surface” / no-companion-impact claim with the actual coordinated boundary: snapshot
      re-lowering consumes the companion fact/IR schemas and executable-profile v3 behavior, and
      the package floor plus runtime/schema guards protect different parts of that boundary.
- [x] `ConstraintExclusion` and `ConstraintCatalogExcludedRecord` have an explicit, internally
      consistent API status. If public, both are exported from the defining module; if private,
      their names and consumers make that status clear. Tests and documentation use the selected
      status consistently.
- [x] The `ConstraintCatalog` docstring states that its fingerprint covers `source_records`,
      `concrete_entries`, and `excluded_records`. The snapshot-loader skew-guard comment points to
      the current profile guard without retaining an obsolete line citation.
- [x] Every codegen warning for a `NON_NUMERICAL` decision includes the statement identity,
      rendered source location, and each actionable diagnostic message in profile walk order. The
      warning may retain reason codes, but reason codes alone do not satisfy D5. Live and snapshot
      routes produce the same warning value.
- [x] The execution conftest discovers TEAx SimKit from a validated explicit environment path or a
      checkout-relative sibling path. It contains no user-specific absolute path, inserts only an
      existing directory with the expected SimKit package, and fails early with an actionable
      diagnostic that names the accepted discovery routes when neither candidate is valid.
- [x] Trailing whitespace is removed from every file in both proposed PR branch ranges. The final
      branch-range and worktree checks for both repositories are clean; Markdown hard-break style
      is not accepted as an exception to this literal gate.
- [x] Final paired validation records the exact codegen and companion revisions and import roots.
      It includes the licensed full codegen suite, the licensed companion full suite, focused docs
      and hygiene checks, static checks with no new debt, the metadata-only pairing probe, fixture
      manifests and diffs, generated live/snapshot byte comparison where already required by the
      wave, and reviewed justification for every permitted byte change. No fixture recapture or
      generated-artifact churn occurs unless the plan identifies and justifies it first.
- [ ] After implementation, an independent GAP-CLOSE epic audit and the project pre-PR checks
      certify the final paired candidate before any cross-repository commit, push, or PR comment.
      The two PR comments report exact commits, suites, metadata and diff evidence, justified
      artifact changes, the still-open external F1 dependency, and the load-bearing merge order:
      agentic-mbse PR #11 before sysml-codegen PR #9.
- [x] Item 5 and its audit do not mark F1 or the GAP-CLOSE epic complete while
      `[GAP-CLOSE-F1-TEAX-NORMALIZATION]` remains open. They distinguish completed codegen
      propagation from missing evaluator-level normalization and module identity.

## Known Requirements

- **[NEED]** Bump agentic-mbse from `0.1.0` to a real compatible patch release in both
  `pyproject.toml` and `src/agentic_mbse/__init__.py`, then raise codegen's dependency floor so
  metadata alone rejects a pre-v3 companion. Owner-stated in the Item 5 stage input.
- **[INFERRED]** Use `0.1.1` for the companion release and `agentic-mbse>=0.1.1` for codegen. It is
  the smallest unused patch increment visible from the two repositories and expresses the stated
  compatibility intent without changing either package's major/minor line. The metadata probe must
  inspect built distribution metadata, not infer success from source text alone.
- **[HARD]** `pyproject.toml` is the built distribution's version and dependency source, while
  `agentic_mbse.__version__` is a separate runtime version surface. Both currently say `0.1.0`, so
  changing only one leaves contradictory observable metadata. Existing package interfaces:
  `../agentic-mbse/pyproject.toml`, `../agentic-mbse/src/agentic_mbse/__init__.py`, and
  `pyproject.toml`.
- **[NEED]** Update exactly the three durable documentation surfaces named by the epic: companion
  `docs/patterns/constraints.md`, codegen reference doc 28, and codegen reference doc 27.
  Owner-stated in the Item 5 stage input and `.project/backlog/epic_gap_close.md`, Item 5.
- **[INHERITED]** The v3 documentation truth is four outcomes; no equality or inequality is
  admitted; Boolean/string/enumeration equality is `NON_NUMERICAL`; integer/real/quantity equality
  is `BLOCK`; and `xor`/`implies` recurse to classify numerical containment. Sources:
  `.project/active/numerical-constraint-profile/spec.md`, requirements 2–4, and
  `.project/active/numerical-constraint-profile/design.md`, D1–D2 and I1–I4.
- **[INHERITED]** Malformed `xor`/`implies` arity and contradictory serialized ratio facts now
  default-deny within `executable-profile/v3`; promoted containment diagnostics carry blocking
  reason, force, and repair text. Source:
  `../agentic-mbse/.project/active/gap-profile-totalization/{spec,plan}.md`.
- **[NEED]** Resolve export visibility, the catalog fingerprint docstring, the stale loader cite,
  D5 warning messages, portable validated TEAx discovery, and trailing whitespace. Owner-stated in
  the Item 5 stage input.
- **[INHERITED]** D5 requires warning and halt rendering to carry actionable diagnostic messages;
  live and snapshot paths share the rendering contract. Source:
  `.project/active/numerical-constraint-profile/design.md`, D5 and I5.
- **[NEED]** Run final licensed codegen and companion suites plus fixture, diff, static, and
  metadata probes. Cross-repository commits, pushes, and PR comments occur only after the
  independent epic audit and pre-PR stage. Owner-stated in the Item 5 stage input.
- **[INFERRED]** The final evidence must prove which companion source code the codegen process
  imported. The local editable override otherwise can make a green suite say nothing about built
  metadata or the intended paired revision. This control follows the verified F3 failure mode in
  both gap research documents.
- **[NEED]** Preserve Item 1's external `[GAP-CLOSE-F1-TEAX-NORMALIZATION]` truth. Do not claim
  complete F1 or a complete epic while it remains open. Owner-stated in the Item 5 stage input.
- **[NEED]** Agentic-mbse PR #11 must merge before sysml-codegen PR #9. Owner-stated in the Item 5
  stage input; the epic records this coordinated-pair order as load-bearing.

## Non-Goals

- Implementing TEAx evaluator normalization or closing `[GAP-CLOSE-F1-TEAX-NORMALIZATION]`.
- Changing executable-profile v3 decisions, schema versions, generated predicate behavior, or the
  completed Item 1–4 behavioral fixes.
- Adding CI infrastructure, a lockfile, an exact companion pin, or a new profile semantic version.
- Refactoring C901 complexity or taking on `[CONSTRAINT-ARCH-UNIFY]` architecture work.
- Expanding the documentation refresh beyond the three durable surfaces named by Item 5.
- Capturing new licensed fixtures or accepting unrelated generated-byte churn as closeout cleanup.
- Committing, pushing, or updating PR comments during specification, planning, implementation, or
  audit. Those externalizing actions follow successful independent audit and pre-PR checks.

## Open Questions / Deferred to design

- None. The epic, research, current implementation, and stage input enumerate the required
  mechanisms closely enough for a file-level plan. Exact test names, the TEAx environment-variable
  name, and whether the two catalog types are public exports or explicitly private are local plan
  decisions whose results remain constrained by the success criteria above.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_gap_close.md`, Item 5
- **Required Reading:**
  - `.project/research/20260718-123558_constraint-expression-final-gap-review.md`, F3, F10, and
    hygiene 2/4–8
  - `.project/research/20260718_gap-review-verification.md`, F3 correction, F10, OQ3 evidence, and
    hygiene 2/4–8
- **Completed dependency artifacts:**
  - `.project/active/gap-runtime-contract/{spec,spec-review,design,design-review,plan,evidence}.md`
  - `.project/active/gap-lowering-integrity/{spec,spec-review,design,design-review,plan,evidence}.md`
  - `.project/active/gap-boundary-guards/{spec,plan,evidence}.md`
  - `../agentic-mbse/.project/active/gap-profile-totalization/{spec,plan}.md`
- **External dependency:** `[GAP-CLOSE-F1-TEAX-NORMALIZATION]` in
  `.project/backlog/BACKLOG.md`
- **Current cross-repo context:** `.project/CURRENT_WORK.md` and
  `../agentic-mbse/.project/CURRENT_WORK.md`
- **Stage disposition:** Product design, technical design, spec review, and design review are
  deliberately skipped. This is docs/metadata/local hygiene with mechanisms already enumerated and
  no unresolved product interaction or architecture choice.

---

**Next Steps:** The final focused re-audit certifies all local and in-scope work. Run `my-pre-pr` as
an explicitly partial wave. Only after that gate succeeds may the paired branches be committed,
pushed, and their PR comments updated. Any closeout record must keep F1 and the epic open while
`[GAP-CLOSE-F1-TEAX-NORMALIZATION]` is open.
