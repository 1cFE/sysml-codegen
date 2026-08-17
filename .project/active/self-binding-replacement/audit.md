# Audit: Self-Binding Replacement

**Verdict:** Needs Work
**Audited:** 2026-08-16
**Branch:** codegen `main`; agentic-mbse `self-binding-replacement`; fusion-tea
`self-binding-replacement`
**Commit:** codegen `f25afc0`; agentic-mbse `3e9734b`; fusion-tea `9e1ff87b`

---

## The Point

A calculation binding such as `in R = R` resolves the right-hand reference to the calculation's
own input. It does not carry the intended outer model value into the calculation. The exact route
must refuse that dead-end before generation. Authors need one situational rule that points them to
the intended source, and the affected customer model must use that rule without changing its
physics. A public mutation then has to reach every and only the consumers bound to that source.

## Summary

The migration itself is bounded and both current fusion-tea trees generate. The measured guidance,
codegen refusal, corrected examples, agent surfaces, and stellarator triage are solid. Seven of ten
functional success criteria are verified.

The work is not ready to certify. The public mutation oracle loses source and consumer identity,
the silently sideways F-4 candidate has no named disposition, customer mode accepts destructive
source/scratch relationships, and agentic validation can silently abstain. The retained fusion-tea
proof can also pass after its two maintained model trees diverge.

## Product Judgment

This is the right piece of work: it closes the blocked customer model, the teaching gap, and the
future-detection gap without expanding into the rest of ELABORATE-FIRST Item 8. The Product-Lens
ledger gate is **DISPOSED (audit-F1)**. Its current-state checks confirm that the two fusion-tea
trees are byte-identical and both generate.

Certification still fails the implementation-level product check. Product-drift smells 1 and 6
fire in `fusion-tea/tests/models/test_self_binding_replacement.py:30,96,121-140,164-169,235-288`.
Two live representations require manual synchronization, the deciding mutation spine silently
selects the default `models/` copy, and its helpers collapse source and consumer identities. The
ledger permits proceeding because today's bytes agree, but the smells remain in the kept test. The
proof must preserve complete group/key and module/port identities and fail on cross-tree divergence.

Every earlier Product-Lens `BLOCK` in the item ledger has a later resolution by citation. The
ledger names the parent epic, but that epic has no live Product-Lens gate to inspect. No unresolved
epic `BLOCK` was found.

One premise conflict remains surfaced rather than silently resolved. Earlier design/Product-Lens
reasoning treats F-4 as a supported positional form when the sibling is intended. Rev-6 SC3 still
requires a named owner and vehicle for any candidate found to resolve silently and wrongly, and the
guide states that the route cannot establish that intent. The spec is the audit contract, so SC3
stays open pending a durable disposition or an explicit spec correction.

## Findings

### Plan completion

The phase-owned commits, artifacts, and local delivery boundaries exist, but the plan is only
partially verified. Phase 2's customer tool lacks destructive-path guards. Phase 4's exact-source,
consumer, and constraint-formal oracles are weaker than the plan requires. Phase 1's agentic repair
works on the retained fixtures but remains inside a broad exception that can silently skip a usage.
The affected plan checkboxes are reopened.

The audit independently reran the focused final-state proof: codegen 117 passed, agentic-mbse 23
passed, and fusion-tea 8 passed. Focused Ruff checks were clean in all three repositories. Current
bytes for all six fusion-tea logical model pairs are equal. Those results establish the current
happy path; they do not close the false-green and destructive-path findings below.

### Spec conformance

- **SC1 — not verified.** The mutations exist, but `_entry_values()` overwrites duplicate keys,
  `_consumers_of()` matches only a source suffix and overwrites ports by module, the constraint
  formal is inferred from predicate text, and the spine runs only against the default tree
  (`fusion-tea/tests/models/test_self_binding_replacement.py:96-140,235-288`). The oracle does not
  yet prove exactly one runtime source reaching every and only complete consumer identities.
- **SC2 — verified.** D-5, D-7, definition-owned D-6, and usage-owned exact-owner behavior are
  retained in the conformance suites; the independent codegen battery passed 117 tests.
- **SC3 — not verified.** F-4 still resolves a definition-owned qualifier sideways into a sibling
  occurrence (`verification/post-repair-spike-recheck.md:17-23`; `tests/conformance/test_definition_owned_reference_positions.py:79-91`).
  The guide warns that the route cannot establish the author's intent, but no durable name, owner,
  and vehicle disposition covers this silent candidate. The arrayed-owner filing covers a loud refusal,
  not F-4.
- **SC4 — verified.** The guidance is organized by where the value lives and distinguishes the two
  D-6 owner classes (`agentic-mbse/docs/patterns/plant-idiom.md:53-180`).
- **SC5 — partially verified.** Codegen uses resolved referent identity and emits
  `SI_SELF_BINDING` before generation (`src/sysml_codegen/extraction/source_evidence.py:130-138,227-239`).
  Agentic-mbse uses the same identity rule, but its whole per-usage check is under
  `except Exception: continue`, so the path can silently return no finding instead of refusing
  (`agentic-mbse/src/agentic_mbse/validation/level2_structure.py:309-385`).
- **SC6 — verified.** The guidance contract finds no unmarked refused example across the four
  instruction trees (`tests/conformance/test_self_binding_guidance_contract.py:146-264`).
- **SC7 — verified.** The same contract pins one authoritative copy, the reviewed qualified
  inventory, and all three short rule-and-pointer surfaces.
- **SC8 — verified.** Both fusion-tea model roots generate with zero readiness findings; the live
  route seals and reproduces the v6 snapshot bytes (`fusion-tea/tests/models/test_self_binding_replacement.py:164-190`).
- **SC9 — verified.** The migration logs prove suffix-only rewrites, and this audit rechecked all
  six cross-tree pairs byte for byte. The customer commit changes binding referents without changing
  arithmetic or physical values.
- **SC10 — verified.** The one stellarator run refused with exactly 114 `SI_SELF_BINDING` findings,
  wrote no output, left the repository byte-identical, and filed the follow-up
  (`stellarator-triage.md:8-54`).

Tagged requirements:

- **[NEED] right patterns, documentation, migration, and detection — partial.** The guidance,
  customer commit, and exact-route refusal are delivered; SC1, SC3, and agentic failure honesty
  remain open.
- **[NEED] situational agent understanding — met.** The authoritative guide and three agent-facing
  pointer surfaces carry the situation split.
- **[NEED] stellarator triage only — met.** Exactly one read-only run was recorded; no fix was made.
- **[INHERITED] one runtime source and public mutation — not verified.** The public oracle collapses
  input-group and consumer-port identity and does not protect the second model tree.
- **[INHERITED] D-4 through D-7 — met.** D-4 refusal is unchanged, D-5 performs the migration,
  D-7 is taught for another part, and D-6 is documented against measured owner-class behavior.
- **[HARD] pre-generation self-binding refusal — met.** Codegen returns `SI_SELF_BINDING` and no
  output for the refused family.
- **[HARD] redefinition semantics — met.** The guide cites KerML §7.3.4.5 and §8.2.3.5.1 and does
  not teach `:>>` as access to the enclosing attribute (`plant-idiom.md:155-180`).
- **[HARD] usage-owned exact anchoring — met.** The landed anchoring suite remains in the 117-test
  battery and the guidance states the exact-owner rule.
- **[HARD] definition-owned fallback — met.** Three retained fixtures pin its distinct positional
  behavior beside the usage-owned suite.
- **[HARD] arrayed-owner scalar boundary — met.** The guide records the refusal boundary and points
  to `[ANCHORING-ARRAYED-DIAGNOSTIC]` without inventing a workaround (`plant-idiom.md:104-107`).
- **[HARD] no false SysML Part 1 §7.17.2 authority — met.** The drift contract rejects that citation
  as a shadowing rule; the published guide does not use it.
- **[INFERRED] parser-validated examples — partial.** Pinned blocks are compared with retained
  fixtures; the two `@measured` blocks are label-checked but have no kept route check.
- **[INFERRED] contained repair or filed silent candidate — not met.** F-4's silently sideways
  definition-owned case has no named owner and vehicle.

The non-goals were respected. There is no stellarator model edit, ADR-010, arrayed-expression
expansion, customer physics change, or implementation of the broader Item 8 regeneration work.

### Design conformance

The core architecture is present: one authoritative teaching copy with drift gates, identity-based
validators, named F-3 diagnostics, dual-tree customer migration, mutation tests, and triage-only
stellarator handling. D1-D3, D6, D8-D11, and D13 conform for the delivered paths.

D4/D5's safe customer-tool intent is not met for path aliasing or package-qualified duplicate
definition names. D7 works on retained fixtures but is not failure-honest. D12 was proved at the
migration commit but is not retained as a cross-tree regression invariant. Phase 4 also deviates
from `plan.md:440-443`: it searches for a formal name inside serialized `predicate_ir` instead of
asserting a structured constraint `formal_identity`.

### Code integrity

1. **The public mutation oracle can false-green.**
   `fusion-tea/tests/models/test_self_binding_replacement.py:121-140` merges input groups with
   `dict.update()`, matches pipeline sources only by `endswith()`, and reduces consumer ports to a
   `{module: formal}` dictionary. Duplicate keys, a same-suffix source in another group, or two
   bound ports in one module can disappear from the comparison. Preserve the complete
   `(group, key)` source and `(module, formal)` consumer identities and assert uniqueness.

2. **The retained proof selects one of two maintained customer trees and does not assert the
   planned structured constraint identity.**
   `fusion-tea/tests/models/test_self_binding_replacement.py:30,96,164-169,235-288` runs only the
   weaker generation check for `exploration/ife_e2e/models`; the snapshot and both mutations use
   `_copy_set()`'s default `models/`. At `:254-264`, the constraint check searches for a qualified
   name inside `predicate_ir` even though the plan requires `formal_identity`; the structured field
   is excluded from public serialization at `src/sysml_codegen/resolution/models.py:175-180`. Add a
   retained equality or both-root spine gate and expose/assert a structured public relationship.

3. **Customer mode can delete its source or another unsafe target before migration.**
   `scripts/make_d5_variant.py:247-255,408-412,452-459,463-496,530-539` calls
   `shutil.rmtree(target_dir)` for an existing `--scratch`, but validates only that the argument was
   supplied. Equal or overlapping source/scratch paths can destroy the input or recurse. Its D5(c)
   definition lookup also reduces package-qualified names to one simple-name key, so one definition
   can overwrite another. Reject unsafe or pre-existing targets before any deletion, retain
   no-mutation tests, and preserve qualified definition identity.

4. **The delivered agentic validator hides unexpected failures.**
   `agentic-mbse/src/agentic_mbse/validation/level2_structure.py:339-385` wraps the whole
   self-binding inspection in `except Exception: continue`. A SysIDE or adapter regression can skip
   a calculation usage and return a clean issue list. Catch only a named, recoverable model-access
   failure or surface a validation failure; unexpected errors must not be reported as success.

5. **The silently sideways F-4 result has no required durable disposition.**
   `spec.md:74-76` requires a name, owner, and vehicle for a silently wrong candidate when it is not
   repaired. F-4 is retained at `tests/conformance/test_definition_owned_reference_positions.py:79-91`
   and disclosed at `agentic-mbse/docs/patterns/plant-idiom.md:141-144`, but documentation alone is
   explicitly insufficient. Record the required disposition or repair the behavior.

No new placeholder code, TODO implementation, compatibility shim, parameter-sprawl problem, or
auto-memory `feedback_*` constraint was found in the audited paths.

---

## Certification

Seven functional success criteria were verified and may be marked complete in `spec.md`. SC1, SC3,
and SC5 remain open. The affected Phase 2 and Phase 4 plan checkboxes are reopened. The verdict is
**Needs Work** until the five findings are closed and reverified.

The parent epic was not marked complete. This work item is a bounded child of ELABORATE-FIRST Item
8, has no discrete epic item heading or done-state checkbox, and does not complete Item 8's broader
success criteria.

**Not checked:** The audit did not rerun the full three-repository suites; it relied on the plan's
recorded full-suite results and independently reran the focused 148-test proof. It did not rerun
stellarator because the requirement permits exactly one triage run. It did not reconstruct the
deleted temporary raw stellarator log, reopen the cited KerML normative sections, inspect remote
push/PR state, or inspect a live epic Product-Lens gate because the epic contains none.

---

## Remediation — 2026-08-16 (implementing session; for re-audit)

All five findings were repaired the same day. Per finding:

1. **Mutation oracle false-green (F1).** `_entry_sources` replaces the merged dict: every input
   value keyed by its complete `(group, key)` identity with uniqueness asserted in both
   directions; `_consumers_of` matches the exact serialized source token (`"<type> <group>.<key>"`,
   full-string, entry-point module excluded) and returns the complete `(module, formal)` port
   set. The expected consumer constants became identity sets. **The tightened oracle immediately
   falsified one of the session's own constants** — the beam source's group is
   `hif_plant_params`, not `hif_driver_params` — which is the class of error the finding named.
2. **One-tree selection and constraint identity (F2).** New retained
   `test_the_two_maintained_model_trees_cannot_diverge`: every `.sysml` under both sets must pair
   up under the layout mapping (`library/`-prefix difference) and match byte for byte, so the
   `models/`-rooted spine stays honest for the second tree. The viability check now parses
   `predicate_ir` as JSON and asserts exactly one structural `feature_ref` targeting
   `fusion_cycle::'Viability Threshold'::gain_in` (kind `AttributeUsage`, `source_name`
   `gain_in`). **Judgment call recorded:** the typed `formal_identity` field is deliberately not
   added to public serialization — exposing it would churn every generated baseline the
   byte-identity gates depend on; the parsed-IR relationship is the structured public equivalent.
3. **Destructive customer-mode paths and definition-name collapse (F3).**
   `_run_customer_mode` resolves both paths and refuses, before any deletion: a non-directory
   root, `scratch == root`, either path nested in the other, and any pre-existing scratch
   (`--check` instead requires the scratch to exist). D5(c)'s definition lookup is a
   non-collapsing multimap over the new `_definition_entries` walk and refuses when any
   same-named candidate lacks the formal. The rename/strip paths use the same entries walk (a
   same-file same-named pair no longer loses a span); the closed-loop byte-identity test pins
   the happy path unchanged. Six new refusal tests, each proving exit 1 with the tree digest
   byte-identical.
4. **Silent agentic abstention (F4).** The blanket `except Exception: continue` now surfaces an
   `L2_CHECK_UNVERIFIABLE` ERROR naming the usage and the error (new `ValidationCode` member), so
   an inspection failure reads as a failed check, never a clean list; `_safe_display_name` keeps
   the reporting path itself from re-raising. A forced-failure test (monkeypatched
   `SysideAdapter.element_id`) pins it.
5. **F-4 durable disposition (F5).** `[DEF-OWNED-SIDEWAYS-REACH]` filed in
   `.project/backlog/BACKLOG.md` (P2, needs an owner ruling: loud refusal vs supported
   positional fallback, then the bounded implementation), cross-linked from
   `tests/fixtures/def_qual_sibling_scope/PROVENANCE.md`. Documentation is no longer the only
   disposition.

**Reverification:** agentic item12 22 passed and full suite **1835 passed / 1 skipped** (+1 new
test, zero failures); codegen `test_d5_variants.py` **35 passed** (+6) and the full licensed
suite result is recorded in the plan's remediation notes; fusion spine **9 passed** (+1). Ruff
clean on every changed file. The reopened plan checkboxes carry dated remediation notes.
Verdict left as **Needs Work** for the re-audit to overturn on its own evidence.
