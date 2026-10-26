# Spec: Repeated computed attributes register one class per definition

**Status:** Implementation complete (2026-10-26), awaiting audit
**Owner:** Reid Westwood
**Created:** 2026-10-25
**Complexity:** MEDIUM
**Branch:** `repeated-rollup-collision` (spec written at `af981956`)

---

## Problem

A part definition whose own value is computed cannot be used more than once in a model. `part def Sub { part leaf : Leaf[3]; :>> capital_cost = sum(leaf.capital_cost); }` used as `part sub : Sub[2];` fails `check` with `REGISTRY_CLASS_NAME_COLLISION ... 'Sub_capital_costModule' <- ['p.sub.capital_costModule', 'p.sub.capital_costModule']`. That is the ordinary costing shape (several identical racks, each summing its servers), so consumer project dc3 cannot use the toolkit's costing pattern.

[OWNER-VERBATIM] 2026-10-25: "yes file it and orchestrate a fix in sysml-codegen". The owner authorized this change to what the generator builds without waiting on the RG-1 gate.

### Root cause

The occurrence index is not lost. Each copy already gets its own module name, its own input keys and (for a rollup) its own file. What is shared is the class identity, and that sharing is by design. Only the registry fails to follow it.

- **The class identity (`module_type`) is per definition feature, on purpose.** A computed attribute's `calc_def_qualified_name` is the definition that owns it (`P::Sub`), not the occurrence (`src/sysml_codegen/elaboration/elaborate.py:1111-1113`). The module type is built from that (`src/sysml_codegen/elaboration/project.py:877-881`, `:915`). So `sub[0].capital_cost` and `sub[1].capital_cost` both get `p.sub.capital_costModule`. This matches calc defs: a calc def used three times is one `p.TwiceModule` class with three pipeline entries.
- **The registry emits one entry per occurrence for computed modules.** Calc-def modules are deduplicated (`src/sysml_codegen/generation/registry.py:169-178`, `:295-306`). Formula and rollup (aggregation) modules are not: one entry and one import per occurrence (`registry.py:180-184`, `:311-337`). Two entries carry the same class name, so the aliaser renames both.
- **The alias cannot separate identical module types.** The alias takes the parent segment of `module_type` (`registry.py:131-139`). Identical module types give identical aliases, so the residual check refuses (`registry.py:142-152`, called from `src/sysml_codegen/cli/prepare.py:439-458`). The error calls this a "grandparent collision", but it is really the same class registered twice.
- **Formula and rollup modules differ in where their file goes.** A formula module's file is per definition (`prepare.py:312-313`), so every copy writes the same file. A rollup module's file is per occurrence, from the module name (`prepare.py:314-315`), for example `modules/p/top/sub_0/capital_cost.py` and `modules/p/top/sub_1/capital_cost.py`, both defining `capital_costModule` for the one type `p.sub.capital_costModule`.

What I ran (graphs dumped through `exact_pipeline_context`). The brief's reproducers are `repro/one`, `repro/two` and `repro/twoplain`. I added variants beside them: `repro/named`, `repro/twotops`, `repro/nested`, `repro/named_total`, `repro/leafformula` and `repro/arity`.

- Every computed attribute on a definition with more than one occurrence fails, not only rollups. These all fail the same way: `Sub[2]`; two named parts `a : Sub; b : Sub`; `Sub` under two different parent definitions; the three-level nested case; the named-total variant (`'Sub_sub_totalModule'`); and a plain formula on a repeated leaf (`Leaf[3]` with `capital_cost = a * 5.0`, giving `'Leaf_capital_costModule'` three times).
- One copy builds. Two copies with a literal value build, because a literal is an input, not a module. That is why `Leaf[3]` in the reproducers never collides.
- A committed fixture already hits this defect. `tests/fixtures/unresolvable_attr_probe` has two occurrences of `'Derived Component'` (one through `Grandchild`). Their formulas `inherited_product` and `mixed_product` collide on identical module types. `tests/conformance/test_public_authority_switch.py:516` and `tests/expectations/public_package_oracle/baseline.json` currently pin that refusal. So the statement in `docs/architecture/reference/20-module-registry-generation.md` that "no committed model hits the grandparent case" is not true.
- Copies of one definition feature can need different shapes. With `part a : Sub; part b : Sub { part :>> leaf[2]; }`, both rollups get `p.sub.capital_costModule`, but `a` sums three inputs and `b` sums two. One shared class cannot serve both.

## Success Criteria

Value checks run the package through its registry, in the real-TEAx execution lane (`tests/execution/real_teax.py:execute_sealed_package`, run with `pytest -m execution` and `TEAX_SIMKIT_PATH` set, on a machine where `simkit` is importable). `simkit` is not importable on this machine, so the structural registry criterion below is the check that runs in the default suite everywhere. The in-repo runner (`tests/runtime/pipeline_runner.py:113`) maps `module_type` straight to a file path. It cannot find a rollup module even in the single-copy reproducer `one/` (`No module named 'generated_code.modules.p.sub'`), so it does not prove the registry. Leaf values are 10.0 unless stated.

- [ ] `repro/two/` (`Sub[2]`, three leaves each) passes `check` and `generate`. `Top.capital_cost` = 60.0, and each `sub[k].capital_cost` = 30.0.
- [ ] Each copy's inputs stay separate. In `repro/two/`, setting `P__top__sub[1]__leaf[0]__capital_cost` to 20.0 gives `sub[1]` = 40.0, `sub[0]` = 30.0 and `Top` = 70.0.
- [ ] Two named parts `a : Sub; b : Sub` with `Top.capital_cost = a.capital_cost + b.capital_cost` build, and the total is 60.0.
- [ ] Three levels, each repeated (`Hall { row : Row[2] }`, `Row { rack : Rack[2] }`, `Rack { leaf : Leaf[3] }`, each summing its children) builds. `Hall.capital_cost` = 120.0, and changing one leaf under `row[1].rack[0]` changes only that rack, that row and the hall.
- [ ] The named-total variant (`attribute sub_total : Real = sum(leaf.capital_cost); :>> capital_cost = sub_total;` in `Sub`, used as `Sub[2]`) builds, and the total is 60.0.
- [ ] A plain formula on a repeated part (`Leaf[3]` with `capital_cost = a * 5.0`, `a = 2.0`) builds, and the parent's sum is 30.0.
- [ ] Copies that share a definition feature but differ in shape (`a : Sub; b : Sub { part :>> leaf[2]; }`) either build with total 50.0, or are refused with an error that names the copies and the cause. A refusal needs a recorded reason in the design and a filed backlog row for the limit. They never build a package in which a pipeline entry runs a class whose inputs differ from the entry's inputs.
- [ ] (Default suite, no `simkit` needed.) In every built package, each `module_type` named in `pipelines/*.yaml` is registered exactly once in `__init__.py`, and the registered class's input fields equal the input names of every pipeline entry that uses it.
- [ ] A real collision still fails fast: `tests/fixtures/refusal_cases/output-naming__registry_class_collision` (two different formulas `a::Site::t` and `b::Site::t`, whose aliases are the same) is still refused with `REGISTRY_CLASS_NAME_COLLISION` before anything is written. `tests/unit/test_sc11_recheck.py` still passes.
- [ ] The full default test run passes. The tests that pinned `unresolvable_attr_probe` as refused are updated to its built result, and the refuse-before-writing check at `test_public_authority_switch.py:516` uses a model that still truly collides.

## Known Requirements

- **[NEED]** The ordinary repeated sub-assembly builds instead of being refused (owner quote above).
- **[HARD]** Each copy keeps its own inputs, output channel and pipeline entry. Values are never merged across copies (ADR 0011; `docs/architecture/modeling-assumptions.md` § 6, "Each occurrence is its own parameter").
- **[HARD]** A residual class-name collision between different module types still refuses before output is written (REQ-REG-08 in `20-module-registry-generation.md`).
- **[INFERRED]** Copies with the same shape share one class and one registry entry, and differ only in their pipeline entries, as calc defs already do. Class identity stays per definition feature, so `module_type` keeps its current derivation for every same-shape group. If differing copies get a second class identity, it is created once, at projection, and the registry only looks it up; the registry never creates or renames an identity while deduplicating (ADR 0009).
- **[INFERRED]** A shared class is defined in exactly one file. The registry never picks one of several identical class definitions (product-lens spec-F3). Design may argue otherwise only by showing how per-copy files cannot drift apart.
- **[INFERRED]** A model with one occurrence of each definition generates byte-identical output. The public-route baselines (`tests/conformance/test_public_route_baselines.py`) pass unchanged, apart from the `unresolvable_attr_probe` refusal turning into a build.
- **[INFERRED]** Formula modules on repeated parts are in scope. They have the same cause at the same place in the code, and the committed fixture that hits this defect uses formulas.

## Non-Goals

- `[REGISTRY-CALC-DEF-SIMPLE-NAME-DEDUP]` is a different cause in the next pass over: calc-def entries are deduplicated by the calc def's simple name instead of by module type (`registry.py:169-178`, `:295-306`). This item leaves that pass alone. A design that chooses "one registry entry per distinct module type" for every module kind would also fix that row. If design goes that way, it stops and asks the orchestrator first.
- Other backlog rows.
- Changing how the alias is derived for genuinely different module types.

## Open Questions / Deferred to design

- **Shape divergence: build or refuse.** [AGENT] Building is preferred, because § 6 says non-uniform arrays are a normal shape. It needs a second class name for the differing copy. Design decides between building and a precise refusal, and records why. A refusal also needs a filed backlog row.
- **Where a shared rollup class lives.** Today a rollup's file is per occurrence. With one shared class, design picks one of two ways. One file at a single path; the single-copy case must keep its current path `modules/p/top/sub/capital_cost.py`. Or one file per copy, registered once. Known Requirements now asks for one file. The open part is which path the shared file gets when there are several copies. The single-copy path must not change.
- **Handwritten stencils** follow the same choice. Rollup and formula stencils are auto-implemented (`AUTO_IMPLEMENTED = True`), so this matters less.
- **Docs:** `20-module-registry-generation.md` (the "no committed model hits" claim and the class-identity rule) needs updating. In agentic-mbse, the wrong-way example `fails="REGISTRY_CLASS_NAME_COLLISION"` in `docs/patterns/adr002-calculations.md` § "Repeated sub-assemblies" turns red and needs rewriting. That is the orchestrator's follow-up.

Not checked: whether the real-TEAx execution lane runs on this machine (`simkit` is not importable in this repo's venv or in agentic-mbse's), and whether the stored refusal-case corpus has other cases that flip. I searched it for `REGISTRY_CLASS_NAME_COLLISION` and found only the genuine case.

---

## Related Artifacts

- **Backlog:** `.project/backlog/BACKLOG.md` `[REPEATED-ROLLUP-REGISTRY-COLLISION]`
- **Brief:** `.project/active/repeated-rollup-collision/briefs/spec.md`
- **Reproducers:** `.project/active/repeated-rollup-collision/repro/` (`one`, `two`, `twoplain` from the brief; `named`, `twotops`, `nested`, `named_total`, `leafformula`, `arity` added at spec)
- **Evidence upstream:** agentic-mbse `.project/active/rollup-guidance/audit.md`
- **Product lens:** `.project/active/repeated-rollup-collision/product-lens.md` (gate DISPOSED: F1-F4 applied above)
- **Design:** `.project/active/repeated-rollup-collision/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`.
