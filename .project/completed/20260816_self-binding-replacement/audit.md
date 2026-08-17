# Audit: Self-Binding Replacement

**Verdict:** Needs Work
**Audited:** 2026-08-16
**Branch:** codegen `main`; agentic-mbse `self-binding-replacement`; fusion-tea
`self-binding-replacement`
**Commit:** codegen `26e19f9` + worktree; agentic-mbse `8b105b3` + worktree;
fusion-tea `7703ba1e` + worktree
**Owner disposition:** Accepted risk; close directed 2026-08-16

---

## The Point

A calculation binding such as `in R = R` resolves the right-hand reference to the calculation's
own input. It does not carry the intended outer model value into the calculation. The exact route
must refuse that dead end before generation. Authors and agents need the right positive form for
each situation, affected models must use it without changing their physics, and a public
off-default mutation must reach every and only the consumers bound to that source.

## Summary

The functional delivery now meets all ten spec criteria. The previously open Fusion proof is
injective and its collision falsifier fails closed; qualified definition-owned lineage misses now
refuse without descendant search; the focused cross-repository evidence is green.

The item still needs work. Both migration-tool CLI modes accept a pre-existing dangling target
symlink and write through it to the symlink's referent, contradicting Phase 2's checked safety
claims. The final repair set is also uncommitted in all three changed repositories, and two design
passages still describe the removed fallback as live.

## Product Judgment

This is the right bounded piece of work. It restores the customer model, teaches the situational
rule, refuses the wrong form, and stays out of the remaining ELABORATE-FIRST Item 8 work.

The append-only Product-Lens ledger gate is **CLEAR** at
`.project/active/self-binding-replacement/product-lens.md:606`. Its new audit block explicitly
resolves `audit-F1`: each Fusion logical-path map proves injectivity before insertion, then the
retained gate compares exact key sets and bytes. **Smell 1** still fires because the customer keeps
two model trees, but the injective equality gate disposes it. **Smell 6** no longer fires. Smells
3, 4, and 5 remain clear, and no unresolved owner/`[HARD]` contradiction exists.

The Needs Work verdict comes from code integrity and incomplete delivery, not from the product
gate.

## Findings

### Plan completion

Phases 1, 3, and 4 are verified. Phase 2 is partial because both advertised pre-existing-target
guards miss dangling symlinks. Phase 5 is partial because the final repair state is not captured by
the checked local commits.

1. **The checked path-safety work is incomplete.** Positional mode resolves an operand before it
   checks whether the original path is a symlink
   (`scripts/make_d5_variant.py:300-309,612-645`). Customer mode does the same to `--scratch`
   (`scripts/make_d5_variant.py:510-565`). In fresh temporary trees, a pre-created
   `target_link -> future` returned exit 0 and created `future/model.sysml` in both modes. Keep
   the lexical operand long enough to reject any pre-existing symlink before resolution, handle
   symlink loops as exit-1 refusals, and retain no-mutation falsifiers for both CLI modes.

2. **The checked delivery commits do not contain the final repairs.**
   `.project/active/self-binding-replacement/plan.md:660-672` records only earlier hashes.
   Codegen's final path/lineage implementation, agentic-mbse's final guide and validation comments,
   and Fusion's injectivity helper/test are still worktree changes. Review and commit the final
   phase-owned paths with updated hashes while preserving unrelated worktree changes.

Fresh audit evidence:

- codegen D5 suite: **39 passed**;
- codegen final semantic battery: **114 passed**;
- codegen guidance/cycle battery delegated independently: **37 passed**;
- agentic behavioral checks: **30 passed**; a fresh wheel then built successfully and its packaged
  `plant-idiom.md` bytes matched the source;
- Fusion public spine: **10 passed**;
- changed-file Ruff and `git diff --check`: clean in all three repositories.

### Spec conformance

All ten functional success criteria are verified:

- **SC1 — verified.** Complete `(group, key)` sources and `(module, formal)` consumers drive two
  off-default mutations; the gain constraint formal is checked structurally
  (`fusion-tea/tests/models/test_self_binding_replacement.py:146-211,312-375`). The cross-tree
  helper rejects normalized-key collisions before insertion and the retained
  `library/x.sysml`/`x.sysml` falsifier passes
  (`fusion-tea/tests/models/test_self_binding_replacement.py:126-143,378-412`).
- **SC2 — verified.** D-5/D-7 behavior, exact usage-owner anchoring, local definition-owned
  lineage mapping, bare references, and explicit paths remain green. The 52-test owner-reference
  battery and the wider 114-test semantic battery passed.
- **SC3 — verified.** A qualified definition-owned leaf maps only through the consumer lineage and
  refuses a miss before descendant search
  (`src/sysml_codegen/elaboration/elaborate.py:2319-2451`); one-above, two-above, and sibling
  fixtures pin `SI_OCCURRENCE_MISSING`
  (`tests/conformance/test_definition_owned_reference_positions.py:48-86`).
- **SC4 — verified.** The authoritative guide is organized by D-5, D-7, usage-owned D-6, and
  definition-owned D-6 situations, with the self-binding refusal explained
  (`agentic-mbse/docs/patterns/plant-idiom.md:40-168`).
- **SC5 — verified.** Codegen compares referent identity and refuses `SI_SELF_BINDING`
  (`src/sysml_codegen/extraction/source_evidence.py:130-138,227-238`). Agentic-mbse mirrors that
  identity check and turns unexpected inspection failures into
  `L2_CHECK_UNVERIFIABLE` errors
  (`agentic-mbse/src/agentic_mbse/validation/level2_structure.py:309-403`).
- **SC6 — verified.** The drift contract finds no unmarked refused example and keeps every pinned
  block tied to its fixture
  (`tests/conformance/test_self_binding_guidance_contract.py:146-239`).
- **SC7 — verified.** Exactly one authoritative copy exists; the three summary surfaces point to
  it, and the tracked `.claude/` zero-surface inventory is pinned
  (`tests/conformance/test_self_binding_guidance_contract.py:146-154,242-264`). The built wheel
  carries byte-identical guidance.
- **SC8 — verified.** Both Fusion model sets generate; live and v6-snapshot packages are
  byte-identical (`fusion-tea/tests/models/test_self_binding_replacement.py:234-260`).
- **SC9 — verified.** The migration's source/variant strip check remains byte-exact and the
  customer diff is suffix-only
  (`scripts/make_d5_variant.py:312-351`,
  `tests/conformance/test_d5_variants.py:425-489`). The dangling-symlink finding is a tool-safety
  failure; it does not falsify the already delivered customer migration's meaning.
- **SC10 — verified from the permitted single run.** Stellarator refused with exactly 114
  `SI_SELF_BINDING` findings, no traceback or output, and unchanged repository state; the
  follow-up is filed
  (`.project/active/self-binding-replacement/stellarator-triage.md:8-54`).

The tagged requirements follow the same result. The owner-stated situational-rule, documentation,
model-migration, detection, agent-understanding, and stellarator-triage needs are met. The inherited
every-and-only public-mutation obligation is now proved. D-4 through D-7 retain their recorded
semantics. The self-binding, redefinition, exact-owner, definition-lineage, arrayed-owner, and
normative-citation hard constraints are respected. Examples are route-checked, and the unsupported
definition-owned fallback received the owner-directed contained repair.

The non-goals remain respected: no stellarator migration, broader Item 8 regeneration, arrayed
cardinality work, ADR-010, model-physics change, or merged validator implementation was added.

### Design conformance

The implementation follows the design's architecture: one authoritative teaching copy with drift
and wheel gates; identity-based validators; named cycle diagnostics; a guarded, mechanized
migration; dual-tree public mutations; and triage-only stellarator handling.

The design artifact itself has two stale contradictions:

1. `.project/active/self-binding-replacement/design.md:263-264` says the definition-owned
   lineage repair has not been made, although rev 6 and the implementation contain it. Amend the
   sentence to describe the implemented refusal.
2. `.project/active/self-binding-replacement/design.md:699-701` still says the sibling fallback
   resolves and leaves intent with the reader. That behavior was removed. Replace it with the
   lineage-miss refusal and D-7 guidance already used by the authoritative document.

### Code integrity

The dangling-symlink write-through at
`scripts/make_d5_variant.py:300-309,510-531,612-645` is a failure-honesty and path-safety defect:
an operand that already exists as a symlink is reported as a successful fresh target after its
referent is created. It must refuse before writing.

No new god function, unrelated implicit mode, parameter-sprawl problem, broad swallowed exception,
compatibility shim, or placeholder was found in the changed implementation. Agentic-mbse's broad
inspection catch is failure-honest because it emits an ERROR; it does not return a clean default.
No auto-memory `feedback_*` entries exist for this project.

Product-drift smells: smell 1 fires but is disposed by the injective equality guard; smells 3, 4,
5, and 6 do not fire.

---

## Certification

SC1 is newly verified and may be checked; all ten spec criteria now pass. The audit reopens the
Phase 2 customer/positional safety work, its hazard validation, and the Phase 5 final-diff/commit
delivery boxes. The parent epic remains open because this bounded child is not certified.

**[OWNER-VERBATIM 2026-08-16]** “mark it as testing edge case only and accepted risk”. The owner
classified the dangling-symlink behavior as a testing/developer-tooling edge case, accepted the
risk, and directed closure without another remediation/audit cycle. This disposition does not
erase the technical finding; it removes it as a closure gate. No runtime elaboration, generation,
model-migration meaning, or public mutation failure was found.

**Not checked:** This pass did not rerun the full three-repository suites or reconstruct their
recorded pre-existing failure baselines. It did not rerun stellarator because the requirement
permits exactly one triage run. It did not execute TEAx, inspect remote push/PR state, reopen the
cited KerML/SysML normative texts, or verify the unrelated dirty-worktree changes.
