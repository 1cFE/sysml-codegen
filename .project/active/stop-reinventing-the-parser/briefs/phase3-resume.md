# Phase 3 resume — your stop was ruled on; continue from b4e97dd

Your halt was correct and every question you raised has been ruled. The contracts changed while
you were stopped — re-read before touching anything:

1. **plan.md is now Revision 4.** Your phase is rewritten: a "Starting state" block resumes you
   from `b4e97dd` (no rollback — the owner ruled your landed work stands), and the checklist
   items below replace what you stopped on.
2. **design.md is now Revision 8** (targeted amendment + review closed + one Phase 2b factual
   correction). The sections that answer your questions:
   `#one-total-inspection-operation` (opaque unit operand, the shared primitive, the arity
   ruling) and the new Codegen-gate subsection under the manifests section.
3. **Phase 2b landed and is audit-confirmed:** your upstream is now `stop-parser-evidence-r2` at
   **`3f8bd58`** (commits `efc235a` + `3f8bd58` on top of `68bca37`; unchanged `0.1.3` /
   `semantic-evidence/v2` contract; `unit_annotation_value` exported). The Agentic tree is
   **read-only again** for you. The compound-unit blocker is gone — measured: all 144
   unit-annotated attributes in `catf_mfe_model` elaborate with zero refusals.
4. `run-records/phase2-audit.md` has a "Phase 2b addendum" section; plan rev 4's Phase 2b
   completion section records the landing.

## How your five questions were ruled [OWNER, 2026-08-18 — encoded in design rev 8 / plan rev 4]

1. **Compound units:** fixed upstream (Phase 2b). The unit operand is opaque; this boundary
   validates no unit grammar.
2. **Raw-selector manifest:** your proposed adapter-import scoping was **rejected** — the
   Phase-2 m2 hole must never become load-bearing. Repository-wide discovery stays. Collision-
   aware reviewed rows for neutral `ExpressionIR.operands` and `SourceFile.referent` (each with
   the design-defined proof artifact — an annotation/declaring-type-pinning kept test; an
   unannotated receiver never qualifies), an adapter-free evasion mutant that must fail the
   manifest equality gate, and the genuine raw reads (e.g. `usage_extractor`) stay red until
   migrated or mechanically excluded. The 20-row measurement is the closure target.
3. **`annotated_ast_value`:** responsibility ratified, implementation superseded — rebuild
   `expression_evidence.unit_annotated_value` as value-site **policy only**, delegating all
   structural interpretation (metatype, operator, arity, operand shape) to Agentic's
   `unit_annotation_value`.
4. **`test_source_identity_extraction.py`:** blanket deletion **rejected**. Build the 14-row
   disposition table plan rev 4 enumerates (replacement test ID or precise retirement reason
   per row, against `ledger-4a.md:628`'s responsibilities); replacements land in the same
   commit that deletes the file.
5. **Tests-after:** accepted conditionally — no history rewrite; the missing
   constructor/inventory/deep-path/manifest kept tests must be written before phase close;
   mutation-test the important boundaries. The closing audit will attack six weak variants
   (skipped inventory, indexed-to-exact conversion, shortened deep paths, adapter-free selector
   reads, malformed unit arity, missing diagnostic provenance) — and it does not substitute for
   missing kept tests.

## Execute plan rev 4's Phase 3 checklist from where you stand

Including (not exhaustive — the plan is the contract): pin the dependency to the `3f8bd58`
landing per the design's pin contract; re-base the value-site helper on the shared primitive;
the six-part ownership closure; the disposition table; the missing kept tests + mutations; the
carried Phase-1 Minors 6/7/8 and Informational 12; compound-unit elaboration proof over the
`catf_mfe_*` fixtures in your validation; occurrence.py byte-identity; extraction-lane full
suite; D1-D4 rerun. All prior hard constraints stand (worktree discipline, license handling,
PDF exclusion, no compatibility surfaces, baselines not called green).

Deliverables unchanged from your original brief: commits in reviewable units, every validation
box executed and recorded, plan.md "Phase 3 completion" filled and committed in the docs
checkout, final message ending `ARTIFACT: .project/active/stop-reinventing-the-parser/plan.md`.
Stop rules unchanged — a new conflict halts, stated plainly at the top.
