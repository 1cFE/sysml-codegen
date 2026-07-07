Companion PR for the **PIPELINE-TRUTH** epic — the agentic-mbse side of Items 4 and 9. sysml-codegen changed what SysML it accepts, wires, and executes across the epic (most of all the whole-plant value idiom, which now resolves end-to-end with zero bridges). This PR moves agentic-mbse's adapter, validators, and teaching surfaces in lockstep so the validated-subset contract is enforceable again: a model the auditor passes is a model codegen accepts.

**Branch:** `pipeline-truth-item4` (7 commits over base `7f77510`).

## PR base (B1 — base-then-retarget)

The prior epic's companion PR ([#7](https://github.com/1cFE/agentic-mbse/pull/7), `upstream-findings-sync`) is still **open**, and this branch is stacked on it. So:

- **While #7 is open:** open this PR against **`upstream-findings-sync`**, so the diff shows only the epic's work (Items 4 + 9), not #7's commits.
- **Once #7 merges:** retarget this PR to **`main`**.
- If #7 is already merged at PR-creation time, base against **`main`** directly.

One branch, one PR for the epic's whole agentic-mbse story (mirrors the prior epic's single companion PR).

## Item 4 — subtype-aware enumeration (the coordinated pair, 4 commits)

`elements_of_type` matched a type name exactly and never its subtypes, while `is_instance` was hierarchy-aware — an asymmetry that silently blinded every model-wide enumeration to the subtypes of the type it queried.

- **`64a097e`** — adapter: `elements_of_type(model, name, *, include_subtypes=False, exclude=())`; both methods raise `ValueError` on an unmapped type name (D6/INV-F, no silent no-op); `EXCLUDED_CONSTRAINT_TYPES` + `is_droppable_constraint` single-source droppability; `InvocationExpression` mapped.
- **`cc64b1d`** — validators: L3 import sweep now queries `Import` with subtypes (was matching zero → dep graph always `{}` → circular check structurally always passed) and re-keys the graph by importing-package QN; L4/L6 constraint sweeps include subtypes so `assert` (`AssertConstraintUsage`) is counted; the L6 `except: constraints = []` swallow removed (D7 — an extraction failure must be loud, not mask the fix).
- **`bc24ae3`** — adapter: map `OwningMembership` / `Subclassification` / `NullExpression` (D6 name-inventory).
- **`bc196df`** — docs: the 8-row subtype-enumeration decision table (`docs/subtype-enumeration-decision-table.md`) — every call site's include-subtypes decision, recorded so each is deliberate.

## Item 9 — sync: the one missing check, the teaching surface, the dispositions (3 commits)

- **`fa3b706`** — **C7** (the one unbuilt check): WARN an `attribute :>> attr = <expression>` redefinition. That form parses as an `AttributeUsage`, but codegen's redefinition scan reads only `ReferenceUsage`, so the override is silently dropped at extraction. `check_attr_redef_expression_dropped` (L6, WARNING) fires on an AttributeUsage `:>>` with a non-literal RHS and stays silent on the supported bare `:>>` forms (ReferenceUsage) and the `attribute :>>`-literal form (taught, not warned). A live syside probe confirmed the trigger boundary is cleanly distinguishable before the check landed. Test-first: `tests/fixtures/item9/attr_redef_expr` fires exactly once; `attr_redef_literal` stays silent. Discharges the filed `ITEM-SYNC-C7`. Plus **D1**: `docs/patterns/plant-idiom.md` gains the whole-plant value idiom — the four value mechanisms, precedence, QN-keying, and the LITERAL-only propagation rule.
- **`1fab4d6`** — teaching-surface sync: **D2** secondary shapes with observed CORRECT/DEGRADED labels; **I5** Item-5 diagnostics folded in (non-float entry points diagnosed; aggregation `^` maps to `**`, was a silent XOR); **D3** keep cross-part chains one hop (multi-hop truncates `source_path`); **D4** `constraints.md` note that `assert` constraints are now visible to the drop report and L4/L6, pointing at the decision table.
- **`9cc7ab4`** — backlog dispositions: `ITEM-SYNC-C7` discharged (built), `ITEM-SYNC-C8` two-names-one-identifier WARN **keep-filed** (codegen SC-4 sanitizer-injectivity is the backstop; the pre-warn needs a shared sanitizer to avoid drift), `ITEM-SYNC-F1` syside vendor note **declined** (evaluation-time recursion, extraction is finite/degenerate — Item-8 probe exit 0).

## Companion audit (Item 9)

The two agentic-mbse primitives sysml-codegen's extraction bottoms out in were audited (evidence: sysml-codegen `.project/active/pipeline-truth-sync/companion-audit.md`):

- **`extract_feature_refs`** — COVERED: multi-segment chains, cross-part refs, and self-named bindings all traverse to a non-empty ref set; the D3 `source_path` truncation is codegen-side, not in this primitive.
- **`str(direction)`** — STABLE: syside 0.8.4 yields a clean enum string (`FeatureDirectionKind.In/.Out`); codegen's substring keys resolve it and are resilient even to a `<…>` repr.

No gap fixed, no gap filed.

## Acceptance

- agentic-mbse suite: **1240 passed / 1 skipped / 33 deselected** (baseline 1238 + 2 new C7 tests). ruff clean; 0 new mypy errors.
- Cross-repo: `validate_architecture` over sysml-codegen's `plant_values` / `plant_value_shapes` / `spec_chain_twolevel` — C7 silent (count 0); stash-verified no L6-error regression (10 / 18 / 9 with and without C7).
- Traceability: every impact recorded across the epic is implemented, verified, or filed — the 18-row table is in sysml-codegen `.project/active/pipeline-truth-sync/close-out.md`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
