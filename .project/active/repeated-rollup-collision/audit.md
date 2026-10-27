# Audit: Repeated computed attributes register one class per definition

**Verdict:** Certify (no must-fix; two should-fix items, one of which needs an owner decision before dc3 relies on per-copy overrides)
**Audited:** 2026-10-26
**Branch:** `repeated-rollup-collision`
**Commit:** `35969d1f` (implementation `44d4ed5e`..`7063db16`, base `e6c20bca`)

---

## The Point

A part definition whose own value is computed (a formula or a rollup) could not be used more than once: `part def Sub { part leaf : Leaf[3]; :>> capital_cost = sum(leaf.capital_cost); }` used as `part sub : Sub[2]` was refused with `REGISTRY_CLASS_NAME_COLLISION`, because the registry registered the one shared class once per copy. That is the ordinary costing shape (several identical racks, each summing its servers), so dc3 could not use it. [OWNER-VERBATIM] 2026-10-25: "yes file it and orchestrate a fix in sysml-codegen". The fix must make the shape check, generate and compute the right numbers; each copy keeps its own inputs, output and pipeline entry, and values are never merged across copies (`[HARD]`, ADR 0011); a genuine collision between two different classes still refuses before anything is written (`[HARD]`, REQ-REG-08).

## Summary

The change does what the owner asked. Copies with the same shape share one class, written once and registered once; copies that differ in shape get one class each. I tried to make two copies share a class while computing different things and could not: every probe below gave each copy its own correct number in real TEAx, or was refused by name. The default suite, the whole-corpus byte identity and the genuine-collision refusal all hold when re-run. The one real concern is not in this code: a known upstream defect (`[NESTED-OVERRIDE-LEAKS-TO-SIBLING]`) used to be hidden behind the refusal for the rollup shape, and now produces a wrong number for it.

## Product Judgment

This is the right piece of work. It removes a refusal of a well-formed, common model without adding a workaround, keeps identity decided once at projection (ADR 0009), and keeps every copy's values separate. The product-lens ledger has no open `BLOCK`; spec-F1 to F4 and design_review-F1/F2 are disposed and still true in the code (spec-F3: one file per shared class, verified in the generated trees). No structural smell fired in a way that hides a wrong result. I did not run a fresh product-lens subagent (see Not checked).

## Must-fix

None.

## Should-fix

1. **The rollup form of the known sibling-override leak now builds with a wrong number instead of being refused (owner decision).** Model `Top { part a : Sub; part b : Sub { part :>> leaf[3] { :>> capital_cost = 20.0; } } }`, with `Sub` summing its three leaves and `Leaf` defaulting to 10.0. On `e6c20bca` this is refused (`REGISTRY_CLASS_NAME_COLLISION`). On the branch it generates and real TEAx gives `a` = 60.0 (should be 30.0), `b` = 60.0, total 120.0 (should be 90.0). The same happens when the override lives in a specializing definition (`part def Sub20 :> Sub { part :>> leaf[3] { :>> capital_cost = 20.0; } }`, `b : Sub20`): branch 120.0, base refused. The wrong values are already in `inputs/m_params.json` (`P__top__a__leaf[0..2]__capital_cost` = 20.0), so the cause is upstream and not this change; base gives the same wrong 120.0 for the non-rollup version of the specializing-definition case. Impact: a dc3 model with one rack variant set by a nested value override would now cost silently wrong, where before it could not be built at all. What should change: either fix `[NESTED-OVERRIDE-LEAKS-TO-SIBLING]` before dc3 uses per-copy overrides, or say plainly in agentic-mbse's rollup guidance not to use them yet. Also widen that backlog row: it is reachable through a specializing part definition, not only a nested usage override, and it is now reachable in the rollup shape this item opened. Models: `/tmp/claude-1000/rrc-audit/models/leak_rollup`, `leak_array`, `leak_array_norollup`.

2. **The remaining alias limit is reached by an ordinary specialization, and the docs say a rename fixes it in a form that does not work there.** `Mid { part sub : Sub[2]; capital_cost = sum(sub.capital_cost) }`, `Mid2 :> Mid { part :>> sub : Sub2[2]; }` with `Sub2 :> Sub { part :>> leaf : Leaf[2]; }`, used as `a : Mid; b : Mid2`, is refused: `'Sub0_capital_costModule' <- ['p.top.a.sub_0.capital_costModule', 'p.top.b.sub_0.capital_costModule']`. Renaming `a` or `b` does not help, because the alias uses the parent segment `sub_0`. Giving the redefinition a new name (`part racks2 :>> sub : Sub2[2]`) does build, and computes 100.0 (a 60, b 40) correctly. Impact: design bet B3 ("rarely") is weaker than stated: a row subtype with a different rack type is a natural dc3 shape. What should change: add this case and its workaround to `[REPEATED-ROLLUP-SHAPE-ALIAS-LIMIT]` (`.project/backlog/BACKLOG.md:67`) and to the "Remaining limit" bullet in `docs/architecture/reference/20-module-registry-generation.md`, which now says only "Renaming one of the two parts builds it". Model: `/tmp/claude-1000/rrc-audit/models/deep_mult`, `deep_mult_renamed`.

3. **The stencil writer still works out the file path on its own.** `src/sysml_codegen/generation/stencils.py:37` `_get_module_sysml_qn` is a fourth copy of the path rule that design D6 said every caller would share. It gives the same path today (verified in the `nestdiv` tree: the stencil imports `modules.p.top.row_0.a.capital_cost`, which is the written class file), and the doc names the copy honestly. Impact: if someone changes the rollup path rule in `generation/module_paths.py`, generated classes would import a stencil at the old path and nothing in the default suite would catch it (`test_registry_class_coverage.py` checks the registry imports, not the stencil imports). What should change: point `stencils.py` at `module_python_path`, as was done for `generation/modules.py`.

## Notes

- **"First copy" is stated twice.** Projection picks the first copy by sorting on module name (`src/sysml_codegen/elaboration/project.py:1464`), and `class_owners` picks it by taking the smallest name (`src/sysml_codegen/generation/registry.py:158`). They agree today, and they must: the split module type comes from one and the class file path from the other. A one-line shared helper would remove the need to keep them in step.
- **The signature drops `channel_name`, but the template reads its last segment** for single-output class field names (`generation/modules.py` `_output_attr_name`). Copies under one module type always share that segment (the attribute name), so this is safe, but the docstring of `class_signature` (`resolution/models.py:243`) should say so.
- **The coverage test skips any snapshot that refuses** (`tests/conformance/test_registry_class_coverage.py:147`), not just the two refused by design. A snapshot that starts refusing would skip here; the public oracle would still catch it.
- **Intermediate commits fail tests** (phase 1 to 4: fixture classing; phase 2 to 4: `site_account.csv`). The notes say so. It only matters if someone bisects inside this branch; squashing on merge removes it.
- **`PROJECTOR_SEMANTICS` not bumped** (`elaboration/project.py:89`). I agree: every model that built before projects and generates byte-identically (corpus check below); only models that used to be refused get new types.
- **Registry entry fields** (`import_path`, `imported_name`, `import_group` instead of one `import_module`) are a reasonable deviation: the path is package-relative, so the residual-collision check needs no package name. Import order and text are unchanged for every existing package (corpus check).

## Findings Detail

### Plan completion

All five phases verified complete. No placeholders or TODOs in the diff. The phase notes match the code.

### Spec conformance

Values below are from real TEAx (dc3 venv, `simkit` from `/home/reid/src/teax`), re-run by me.

- `repro/two`: verified, 60.0, each copy 30.0.
- Per-copy inputs (`sub[1].leaf[0]` = 20.0): verified, 40 / 30 / 70 (execution test, 13 of 13 passed when I ran it with `--noconftest -m execution`).
- Named `a : Sub; b : Sub`: verified, 60.0.
- Three levels: verified, 120.0, and the `row[1].rack[0]` mutation moves only that rack, row and hall.
- Named total: verified, 60.0.
- Formula on a repeated leaf: verified, 30.0.
- Different shapes: builds, 50.0 (a 30, b 20), one class per shape.
- Default-suite structural check (I2): verified, `tests/conformance/test_registry_class_coverage.py` over 12 live models and 22 snapshots.
- Genuine collision still refuses: verified. `generate` on `refusal_cases/output-naming__registry_class_collision` exits 1 with `REGISTRY_CLASS_NAME_COLLISION ... 'Site_tModule'`, and a sentinel file in the output folder was the only thing there afterwards.
- Full default run: verified, 9 failed, 8583 passed, 11 skipped. The 9 are the known `test_check_ledger_4a.py` ×8 and one `test_study_cli.py`.
- `[HARD]` per-copy separation: met by this change. (The leak in should-fix 1 is upstream.) `[HARD]` REQ-REG-08: met. `[INFERRED]` one file per shared class: met. `[INFERRED]` single-occurrence byte identity: met. Non-goal `[REGISTRY-CALC-DEF-SIMPLE-NAME-DEDUP]`: the calc-def pass is untouched.

Trying to break the shape comparison (each in real TEAx; expected value worked by hand first):

| Probe | What differs between copies | Result |
|---|---|---|
| `redef_expr` | `b` redefines the rollup as `sum(...) * 2.0` | a 30, b 60, total 90: correct |
| `redef_plus` | `b` redefines it as `sum(...) + 5.0` | 30 / 35 / 65: correct |
| `redef_literal` | `b` redefines it as a literal 7.0 | 30 / 7 / 37: correct |
| `agg_feature` | `b` sums a different leaf feature | 30 / 3 / 33: correct |
| `formula_redef` | `b` redefines a formula `rate * 4.0` | 6 / 12 / 18: correct |
| `formula_sources` | inputs from different values, and one from a computed source | 6 / 10 / 8, total 24: correct |
| `defaults` | `b` overrides an input's default | 6 / 10 / 16: correct |
| `leaf_subtype_formula` | `b`'s leaves retyped to a formula subtype | 30 / 60 / 90: correct |
| `deep_mult` | different multiplicity one level deeper, via a subtype | refused by name (should-fix 2); renamed variant 100: correct |
| `units` | leaves in kg vs g | not reachable: the exact route refuses `MassValue` before projection |
| `leak_rollup`, `leak_array` | nested value override in one copy | wrong number, upstream (should-fix 1) |

A redefined expression gets its own module type from elaboration (the usage path, for example `p.top.b.capital_costModule`), so the split is not even needed there. Where copies do share a type, their inputs are bound per pipeline entry.

### Design conformance

Implementation follows the design (D1 to D8, I1 to I5). Deviations, all listed by the implementer: the stencil path copy (should-fix 3), the registry entry fields and `PROJECTOR_SEMANTICS` (notes), and the D8 refusal as a plain `AssertionError`, which matches projection's existing internal-invariant style.

Whole-corpus byte identity, re-run in full rather than spot-checked: I ran `evidence/corpus.py` on a worktree of `e6c20bca` and on the branch. 165 roots generate on both and are byte-identical (`diff -rq`); the only differences are the two expected flips (`unresolvable_attr_probe`, `elab_native_plural_scope`, refused on base) and the ten new `repeated_rollup` fixtures that exist only on the branch. This confirms `evidence/corpus-receipt.md`.

### Code integrity

One clear rule in the right places: identity is settled once at the end of `_build_calculation_modules` (`elaboration/project.py:938`), the registry and writers only look it up through `class_owners`, and generation re-checks the rule as an internal defect (`registry.py:167`). The import rewrite now renders each line from its own entry, which removes the substring search and the real one-copy import failure (`onenamed` computes 35.0). `ruff check src/` and `mypy src/` are clean, and the changed test files pass `ruff check`. `ruff format --check` flags three changed files, but the flagged lines are untouched by this branch.

---

## Certification

Checked: the source diff in full; every spec success criterion and tagged requirement; the full default suite; the execution test for this item; the whole corpus against `e6c20bca`; the genuine-collision refusal with a sentinel; 13 adversarial models in real TEAx; docs and backlog against the code. I did not tick checkboxes in the spec or plan, or update `CURRENT_WORK.md`, because this run was limited to writing `audit.md`.

**Not checked:** the full provenance execution lane (`lane.sh`), which I did not re-run; I ran only `tests/execution/test_repeated_rollup_teax.py` directly. A fresh product-lens subagent (I read the existing ledger instead). Constraint and report-aggregator modules on repeated parts (out of scope in the design). Unit-bearing quantities, which the exact route refuses before projection. Preserved-handwritten and smart-regen runs, where a stale per-copy stencil from an old generation could remain. Native SysIDE agreement with the leak values. The agentic-mbse follow-up (the `adr002-calculations.md` wrong-way example that now generates).

ARTIFACT: /home/reid/src/sysml-codegen/.project/active/repeated-rollup-collision/audit.md
