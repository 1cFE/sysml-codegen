# Design Review: Repeated computed attributes register one class per definition

**Design:** `.project/active/repeated-rollup-collision/design.md` (commit `71214b28`)
**Spec:** `.project/active/repeated-rollup-collision/spec.md`
**Review File:** `.project/active/repeated-rollup-collision/design-review.md`
**Date:** 2026-10-25
**Reviewer:** fresh subagent, did not write the spec or design. Probes are in `/tmp/claude-1000/-home-reid-src-agentic-mbse/9366fe1c-453c-484d-b30e-782bbdd1390c/scratchpad/review/`. They reuse the design's own prototype (`../plug/proto_plugin.py`, `../gen_proto2.py`) and run packages in real TEAx through dc3's venv.

---

## The Point

[OWNER-VERBATIM] 2026-10-25: "yes file it and orchestrate a fix in sysml-codegen". Several identical sub-assemblies, each summing its own children, must pass `check`, generate, and compute the right numbers. Each copy keeps its own inputs, output channel and pipeline entry, and values are never merged across copies (`[HARD]`, ADR 0011, modeling-assumptions §6). A genuine collision between two different classes still refuses before anything is written (`[HARD]`, REQ-REG-08). Product rule 0003 (owner): a well-formed model is not refused to make the generator's life easier.

## Fundamental Assessment

**Sound, with one must-fix.** The rule is one clear rule: projection decides which copies share a class, and the registry registers each module type once. The design keeps identity at projection (ADR 0009), adds no special case for rollups in the registry, and leaves calc defs alone as the spec requires. I checked the riskiest part, whether two copies that should differ could be merged into one class and give a wrong number, and found no way for that to happen (details under Dimension 3). The prototype builds and computes every spec case. I re-ran several of those cases and three new shapes, and all gave the right numbers.

The must-fix is the fallback for copies that differ in shape (D3). It gives *every* copy in the group its own class. As soon as such a group sits inside a repeated parent, the copies' aliases collide and the model is refused. That is not the narrow "same parent name under different grandparents" limit the design describes. It refuses the item's own shape: identical rows, each with one half-filled rack. A small change (one class per distinct shape, not one per copy) builds it. I prototyped that change and it computes correctly.

Product lens (run inline, see note at the end): CLEAR after dispositions. Neither design smell fired.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

- Every success criterion has a design element and a test in the plan. The prototype results match the spec's numbers. I re-ran `mult1` (40.0) and `trio` (80.0, copies 30/30/20) in real TEAx.
- Spec known requirements are met: identity stays per definition feature for same-shape groups; a second identity is created once, at projection (D3, D4); one file per shared class (D2); calc-def dedup is untouched (D1).
- The shape-divergence criterion is met for the flat case only. Owner intent is "several identical sub-assemblies". `review/nestdiv` (`Top { row : Row[2] }`, `Row { a : Sub; b : Sub { part :>> leaf[2]; } }`) is refused with `REGISTRY_CLASS_NAME_COLLISION ... 'A_capital_costModule' <- ['p.top.row_0.a.capital_costModule', 'p.top.row_1.a.capital_costModule']`. The two rows are identical. See must-fix M1.
- Byte identity (I3) is proven for the 22 fixtures in the public package oracle and for `solar_battery_d5` in the route baselines. The other generating fixtures (`fixture_classes.json` has 178 entries) are only checked to still generate, not to produce the same bytes. See S1.

### 2. Pattern Consistency
**Assessment:** Pass

- "One registry entry per module type" matches what calc defs already do. Re-typing with `model_copy` on `modules_by_semantic` follows the projector's existing style.
- The new refusal reuses `REGISTRY_CLASS_NAME_COLLISION` and its existing preflight site, so no new code or site-account rows.

### 3. Abstraction Quality
**Assessment:** Concerns

The shape comparison (`class_signature`, D5) is right, and it is built the safe way round:

- It *removes* a short list of fields (`name`, `execution_order`, `module_type`, each input's `source`, each output's `channel_name`) and compares everything else. A field added to `PipelineModule` later counts by default, so the comparison can only grow stricter. The plan should state that this must stay a removal list, not a list of fields to keep (S4).
- I checked that none of the removed fields reach the class body. `generate_teax_module` (`generation/modules.py:414-531`) and the stencil context (`generation/stencils.py:127-175`) read `name` only to build the file path for a rollup (`_get_module_sysml_qn`, `modules.py:55-56`). One shared file means one path. They never read `source` or `channel_name`. Everything the templates render (`param_name`, `python_type`, `description`, `compiled_expression`, `auto_impl_context`, `doc_comment`, `calc_expressions`, `source_file`/`source_line`, output `field_name`/`unit`) stays in the signature.
- Things that should *not* split copies do not. In `review/valdiff`, one copy overrides its leaves' values; both copies still share `p.sub.capital_costModule`, because the value lives in the input file, not the class.
- Things that should split copies do. A different leaf count splits (`mult1`, `arity`), and so would a different module kind, because `module_kind` stays in the signature. That only works if settlement groups formula and rollup modules *together* by module type, as the prototype does (`settle` in `proto_plugin.py`). The design text says "groups formula and rollup modules by module type"; the plan should make that explicit.

The concern is the D3 fallback (M1), plus the same path being worked out in three places (S2).

### 4. Duplication Avoidance
**Assessment:** Concerns

- **The file path is worked out in three places:** `cli/prepare.py:299-322` (`_get_python_path`), `generation/modules.py:42-66` (`_get_module_sysml_qn`) and the four import passes in `generation/registry.py:294-354`. D6 adds `import_module` to each entry, but derives it "exactly as today", which keeps the third copy. The prototype already derives it from `_get_python_path`. Doing that in the real change makes I5 ("every class file written is imported, every import names a written file") hold by construction. It also puts the optional per-copy formula path (Implementation Notes) in one place instead of three. See S2.
- After this change the registry has two dedup rules next to each other: calc defs by simple name, formula and rollup by module type. That is forced by the spec's non-goal (`[REGISTRY-CALC-DEF-SIMPLE-NAME-DEDUP]`). Name the two passes plainly in code so the next reader doesn't merge them by accident.

### 5. Data Structure Clarity
**Assessment:** Pass

- `class_signature` lives next to `PipelineModule` and returns a comparable value. Registry entries stay untyped dicts. Adding `import_module` is in keeping with today's code. A small typed entry would be clearer, but it isn't needed.

### 6. Route Safety
**Assessment:** Pass

- D4 is correct. `select()` reads `modules_by_semantic` (`elaboration/project.py:288-321`), so selecting only some targets gives the same module types as the full build. The plan has a test for this.
- The snapshot route goes through the same projection, so it gets the same identities.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

- B1 and B2 are real bets with evidence. I confirmed B2 independently. In `nestdiv` built with one class per shape, changing `row[1].a.leaf[0]` to 20 moved `row[1].a` 30→40, `row[1]` 50→60, total 100→110. Nothing else changed.
- **B3 is the weak bet, and the design doesn't follow its own "if false" branch.** "Differing copies are rare and flat" fails as soon as the repeated parent is the whole point of the model (rows of racks). The decision to make every copy its own class turns any nesting into a refusal. The design's description of the limit ("`top.x.a` and `top.y.a`") understates it. It fires for any differing group under any array.
- **D2 and D3 contradict each other.** D2 puts the shared file at "the first copy's path". D3 rejects naming by one copy because "no copy is privileged". One class per shape, named from that shape's first copy, makes both decisions use the same rule.
- D6 (the import fix the orchestrator pulled in) is sound and contained. I reproduced the defect on the stock generator with `review/onenamed`. The alias goes onto `p.top.capital_cost`'s import line, because `p.top` is a substring of it, and `p.top.a.capital_cost`'s line is left bare. The registry body then names `Sub_capital_costModule`, which is never imported. The fix only needs registry.py, because the entry already knows its module. It removes the first-match search instead of patching it, so it does close `[SC11-IMPORT-REWRITE]`. The backlog called it "cross-module AST rework". That turns out not to be needed, because the generator writes these import lines itself.
- D7 re-checks at generation what projection already guarantees (I1). It is harmless as a backstop. See N1.

### 8. Reader Comprehension
**Assessment:** Pass

- The Core Concept states the rule plainly before the mechanism. The Research Findings are concrete and checkable; I checked several.
- One fix: the D3 "Known limit" sentence is wrong about scope (M1), and that is the sentence a future reader would plan around.

---

## Issues by Severity

### Must-fix (Critical)

- **M1. The D3 fallback refuses differing copies inside any repeated parent, including identical rows.** *(Spec Compliance, Bets)*
  - *Evidence:* `review/nestdiv` (rows `Row[2]`, each with `a : Sub` and `b : Sub { leaf[2] }`) is refused, naming `row_0.a`/`row_1.a` and `row_0.b`/`row_1.b`. The error then says "rename one scope". That advice is impossible here, because the copies are elements of one array.
  - *Fix:* group the copies of a module type by signature. Give each distinct signature one module type, taken from the occurrence path of its first copy by module name, the same "first copy" rule as D2. Copies in the same-signature group keep the definition's type, as now.
  - *Prototype:* `review/gen_persig.py`, a 3-line change to the design's own prototype. `nestdiv` builds: total 100.0, rows 50, a 30, b 20; the mutation above stays separate. In flat cases nothing changes except that same-shape copies share a class (`trio`: `s_0` and `s_1` share `p.top.s_0.capital_costModule`, `b` gets its own).
  - *What's left:* the limit becomes narrow. Two *different* shapes whose first copies have the same parent name under different grandparents still collide. File that, described accurately.
  - *If the design keeps "every copy gets its own class":* it must restate the limit as "any differing group inside an array or under same-named parents is refused", give the reason, and file that wider row. I recommend against that, because it refuses the owner's shape.

### Should-fix (Major)

- **S1. Prove byte identity beyond 22 fixtures.** *(Spec Compliance)* Add a one-off receipt to phase 2: generate every generating fixture on `main` and on the branch, and diff the trees. Expected differences: `unresolvable_attr_probe` and `elab_native_plural_scope` only. The oracle covers 22 snapshots, and `test_fixture_classes_live.py` only checks generate versus refuse.
- **S2. Derive `import_module` from the same function the writers use.** *(Duplication)* Move `_get_python_path` into `generation/`, so registry.py doesn't import from `cli/`, and use it for all four import groups. Then I5 holds by construction, and the per-copy formula path (if it is built) is one edit, not three.
- **S3. File a separate pre-existing defect: a nested override in one part changes the same values in its sibling.** *(Bets, outside this design)*
  - *Evidence:* `review/leak` runs the stock generator with no computed `Sub`, so this item plays no part. `Top { part a : Sub; part b : Sub { part :>> leaf[3] { :>> capital_cost = 20.0; } } }` writes 20.0 for `a`'s leaves too (`inputs/m_params.json`). The model means 10.0.
  - *Why it matters here:* it breaks the spec's `[HARD]` "values never merged across copies" upstream of the registry. This item's tests use the same values in every copy, so they cannot see it.
  - *Ask:* the orchestrator files a backlog row. Don't add a per-copy value-override case to this item's fixtures, because it would fail for this other reason. Not checked: what native SysIDE says, and the cause.
- **S4. Guard the signature against a later change dropping a field that matters.** *(Abstraction)*
  - I2 compares input *names* only. Two classes with the same input names and a different expression would pass it.
  - Add a unit test on `class_signature`: modules that differ only in `compiled_expression`, `auto_impl_context`, `python_type` or `module_kind` must differ in signature; modules that differ only in the five removed fields must not.
  - Say in the docstring that it is a removal list.
  - Also run the I2 structural check over every package the oracle already builds, not only the new fixtures.
- **S5. Check all the values of the two fixtures that flip.** *(Spec Compliance)*
  - I confirmed the design's numbers from the models. `unresolvable_attr_probe`: `derived_instance.inherited_product` 10×2 = 20, `mixed_product` 10×3 = 30. `elab_native_plural_scope`: `selected.total` 2×7 = 14, `shadow.total` 2×2 = 4.
  - The plan should also check the rest. In `unresolvable_attr_probe`: `grandchild_instance` (`inherited_product` 20, `mixed_product` 30, `grandchild_product` 20) and the `design_derived_instance` values. In `elab_native_plural_scope`: `fleet_total` and `dashboard.observed_total` (both 14).

### Notes (Minor)

- **N1.** D7: run the signature backstop over *all* formula and rollup modules, not over the reduced list of class owners, or it can never fire. Consider making it an internal-defect assertion. A user-facing collision message for "projection broke its own invariant" will mislead whoever reads it.
- **N2.** D6: sort import lines on the text *before* the alias is added, as today. I checked that adding " as X" cannot reorder lines (a space sorts below every identifier character), but say it so phase 2 doesn't chase a false difference.
- **N3.** The divergent-formula branch: I could not reach it. I tried a doc comment on a redefined input (`review/fdiv`), an `Integer` redefinition (`fdiv2`) and a usage overriding a `default` formula (`fdiv3`, which already gets its own owner, `p.top.y`). An explicit internal-defect refusal with a test is cheaper than a path branch. Record the choice, as the design asks.
- **N4.** `IMPLEMENTATION_BACKLOG.md` counts auto-implemented modules per copy ("4 aggregation module(s)" in `trio`, which writes 4 files; after M1 it would write 3). This is cosmetic, and single-copy output is unaffected.
- **N5.** The execution lane can run, with work.
  - *What works:* direct runs (`PYTHONPATH=src:/home/reid/src/teax/packages/teax-simkit /home/reid/src/dc3/.venv/bin/python`) work; I used them for every number above. The lane's TEAx pin `8d877460` is TEAx HEAD.
  - *What doesn't yet:* `pytest -m execution` refuses without `CODEGEN_EXECUTION_PROVENANCE`; I confirmed that error. `lane.sh` hardcodes `CG=/home/reid/src/subset-conformance/sysml-codegen` and `/tmp/subset-2b/tools/lane_manifest.py`, which does not exist. It also archives a *commit*, so the new execution test must be committed before phase 5 runs it.
- **N6.** D2: the shared file lives under the first copy's folder. Renaming or removing that copy moves the class file and its stencil. That's acceptable because these stencils are auto-implemented. A short line in the 20-module-registry doc would save someone a puzzle.

---

## Recommendations

1. Change D3 to one class per distinct shape, named from that shape's first copy (M1). Add `nestdiv` to the fixtures and execution test: total 100.0, plus the `row[1].a.leaf[0]` mutation. File the remaining narrow limit with an accurate description.
2. Add the whole-corpus before/after diff to phase 2 (S1). Derive import paths from the writers' path function (S2).
3. Add the signature unit test and widen the I2 check (S4). Check every value of the two flipped fixtures (S5).
4. Orchestrator files the sibling-override leak as its own backlog row (S3).

---

## Product lens (inline)

Run by the reviewer, not a separate subagent. It is not appended to `product-lens.md` because this run was told to write only the review file. The orchestrator can copy this block there.

`design_review — 2026-10-25 — rev 71214b28`. Point: a well-formed model with repeated sub-assemblies builds and computes per-copy values; refusal only for a genuine identity conflict [owner-verbatim 2026-10-25; product 0003 (owner); ADR 0011 / modeling-assumptions §6 (INHERITED)]. Falsifier: identical repeated parents containing differing copies are refused.

- `design_review-F1` [DO] Refuses identical rows that each contain differing copies (M1). Source: owner-verbatim intent plus §6, owner/INHERITED. Disposition: design adopts one class per shape (recommended), or files the wider limit with its reason.
- `design_review-F2` [DON'T-risk] D7 re-checks at generation what projection guarantees (smell 2, consumer compensating for the producer, mild). Not fired as a structural smell, because it refuses rather than compensates. Disposition: N1.
- Smell 7 (ownership changed without saying so): not fired. Class identity stays with projection, and the design says so.

Gate: DISPOSE-and-proceed (F1 must be disposed in the design before implementation).

---

## Resolutions

(Empty. To be filled with the owner's or orchestrator's calls.)

---

**Overall:** Revise
**Next Steps:** Record resolutions here, then return to the design agent with this review. The reviewer does not edit the design.
