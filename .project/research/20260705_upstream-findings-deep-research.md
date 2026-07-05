# Deep Research: fusion-tea Upstream Findings SC-1 – SC-11

**Date**: 2026-07-05
**Source register**: `~/1cfe/fusion-tea/.project/reports/2026-07-05-upstream-findings-register.md`
**Verified against**: HEAD of `cost-pattern-refactor-squashed` (d6c725f)
**Method**: six parallel research agents, each verifying register claims against current code (several with live syside runs and purpose-built probe models), checking design docs / backlog for intent, and assessing alternatives, lift, and risk. Lift scale: S = hours, M = days, L = week+.

---

## Summary table

| Finding | Register verdict | Research verdict | Recommended action | Lift |
|---|---|---|---|---|
| SC-1 constraints dropped | blocks-pipeline, "Phase 6 stub" | Confirmed, but **never scheduled here** — "Phase 6" is fusion-tea folklore. Dead code handles the wrong constraint shape | Warn + document now; scoped epic later (annotate-don't-halt) | S now / L later |
| SC-2 `return` crash | blocks-pipeline | Confirmed and **broader**: bare `in` params also invisible; repo's own docs teach the crashing pattern | Support named `return` + bare `in`; reject anonymous `return`; zero-output fail-fast | S (M with auto-impl capture) |
| SC-3 first-type indexing | blocks-pipeline | Confirmed, **in two places** (usage_extractor + hierarchy_resolver); zero fixture coverage | Support: index by owned FeatureTyping target + all user PartDef types | S–M |
| SC-4 quoted names | blocks-pipeline | Confirmed, reproduced with in-repo fixture; register's fix aimed one layer too high | Sanitize at identifier derivation (or extraction source) + file-path collision guard | S |
| SC-5 cross-part wiring | blocks-pipeline, "biggest gap" | Confirmed; decomposes into **4 mechanisms** (2 extraction holes + 1 missing lookup + 1 real feature); deliberately deferred on now-invalid fixture evidence; MFE gating confirmed | Staged support: literal pre-fill first, then channel wiring; new plant-idiom fixture mandatory | M (staged) |
| SC-6 expression reconstruction | friction | Confirmed; register's root cause **corrected** (branch ordering alone, not node-type naming) | Fix in place before PUSH-DOWN move; precedence-aware parens | S (+baseline regen) |
| SC-7 EXPOSE alias drop | friction | Confirmed and **worse**: name dropped in both shapes; part-usage shape drops *silently*. EXPOSE is officially supported — this is a bug in promised functionality | Warning upgrade now (30 min); alias surfacing later | 30 min / 0.5–2 d |
| SC-8 warning noise | friction | Reframed: noise is a symptom of **two real matcher bugs**, and the same warning text provably masks a real dangling-input failure in the committed catf_mfe fixture | Fix matchers, then summary + params-coverage check. Do NOT blanket-demote | 0.5 d + 1 d |
| SC-9 no snapshot CLI | enhancement | Confirmed; refactor already built every ingredient; live license outage makes value immediate | `--from-snapshot` + capture subcommand + format versioning | M (with SC-10) |
| SC-10 compilation_results | enhancement | Confirmed, **narrower**: only CalcUsage auto-impl is lost; FORMULA and aggregation already survive snapshots | Serialize `compilation_results` (plain dataclasses), never syside ASTs (impossible) | +0.5 d on SC-9 |
| SC-11 class-name aliasing | informational | **Closable**: designed, documented (REQ-REG-03/04/07), conformance-tested | Close; optional micro-follow-up on 2 residual gaps | — |

---

## Cross-cutting conclusions

### 1. Which findings are bugs vs. scope decisions

Against the project philosophy (deliberate SysML subset, agentic-mbse audits compatibility), the findings split cleanly:

- **Bugs in already-promised functionality** — the supported-subset contract (`docs/architecture/modeling-assumptions.md`) or requirement IDs already cover these; "reject the pattern" is not on the table:
  - SC-4 (quoted names: REQ-NC-06 mandates sanitization, fixtures use quoted names pervasively)
  - SC-7 (EXPOSE pattern is contract §3)
  - SC-8 (the misses are matcher defects on supported binding shapes)
  - SC-6 (plain display defect)
- **Support-vs-reject trade-offs, decided in favor of support**:
  - SC-2 — the repo's own `01-extraction.md:25-28` canonical example uses `return`-style, and the direction logic already anticipates `"Return"`; rejecting would require reconciling more artifacts than fixing.
  - SC-3 — retyping (`part :>> x : Subtype`) is the natural extension of the Costed Component idiom the COST-PATTERN epic just spent ~12 days supporting, and the MFE epic's reuse pattern depends on it.
- **Genuine scope expansions** requiring a deliberate decision:
  - SC-5 — the plant idiom (def-declared attributes valued by `:>>`, nested retyped parts) was never in the contract and was deferred on "0 found across all models" fixture evidence. That evidence base is now invalid: fusion-tea's WI-010/WI-012 design docs are explicitly built on this idiom.
  - SC-1 — constraint execution was never scheduled in this repo (see below).
- **Tooling** (SC-9/SC-10) and **closable** (SC-11).

### 2. The register is accurate on symptoms, sometimes wrong on mechanics

Every register claim about *behavior* verified. Three suggested fixes are mis-aimed:

- SC-1: "wire `extract_all_constraints` in" — that extractor handles the *inline* constraint shape (predicate in the usage body, the catf_mfe fixture style), not the def-typed `assert constraint` shape fusion-tea needs. Plan a rewrite, not a wire-in.
- SC-4: "apply sanitize_name in template contexts" — one layer too high. The defect is in the ADR-003 derivation layer (`core/identifier_types.py:104-108, 140-143`), which every template context consumes.
- SC-6: "literal branch matches node-type names SysIDE doesn't use" — false; the literal branch works if reached (probed live: `is_instance(node, "LiteralRational")` is True). The bug is branch *ordering* alone (every SysIDE node carries a derived `.function`, so literals hit the invocation catch-all at `expression_utils.py:57` first) plus missing parenthesization.

### 3. One shared root-cause family

SC-4, SC-7, and SC-8's matcher bugs are all the same defect class: **name-form mismatches** between raw syside qualified names (quotes, spaces, `::`), sanitized EQNs, and simple names. Three concrete instances:

- `sysml_to_python_qualified_name` (`core/qualified_names.py:103-105`) is a bare `::`→`__` replace, no per-segment sanitize → SC-8's REFERENCE-path misses and SC-4's FORMULA latent leak.
- `_resolve_expose_pure` (`resolution/graph_builder.py:665-669`) matches simple names against EQNs → SC-7's part-def warning.
- `identifier_types.py` derivations consume raw QNs → SC-4.

One sanitized-QN matching helper, applied at these sites (or better: sanitize once at extraction, per the "compute once, look up thereafter" principle), retires the family.

### 4. The meta-cause: fixture blind spot

None of the 10 snapshot models exercises: return-style outputs, retyped part usages, quoted calc defs in a *baseline* (quoted fixtures exist but never flow through registry/module generation tests), the plant idiom, or def-typed assert constraints. Every SC finding survived 1500+ conformance tests because the conformance net is exactly as good as its fixtures. **Recommendation**: import fusion-tea's WI-014 toy (`exploration/construct_validation/`) and add an ife_plant-shaped fixture as new conformance baselines before or with any of these fixes.

### 5. New defects discovered during this research (not in the register)

1. **Bare `in x : Real;` parameters are invisible** to extraction (same ReferenceUsage mechanism as SC-2) — a calc def written fully bare extracts as an empty shell.
2. **`hierarchy_resolver.py:526-533` has the same first-type bug as SC-3** — retyped usages resolve redefinition defaults against the wrong PartDef.
3. **Shared mutable `BindingInfo`**: `_create_virtual_calc_usage` does `bindings=list(template.bindings)` (`usage_extractor.py:259`) — all virtual instances share the same objects. Must be fixed (deep copy) before any per-instance rewriting (SC-5 stage 2) lands, or corruption will be silent.
4. **Committed catf_mfe fixture has a real dangling input**: `pipeline.yaml:402` references `...cryo_load__magnet_volume` which is absent from `magnets_params.json` — a runtime failure hiding behind the same "Registry unresolved" text as the benign cases. Proof that SC-8 must not be fixed by demotion.
5. **File-path collision hole**: two names sanitizing to the same lowercased filename silently overwrite (`cli/__init__.py:214` has no duplicate check) — add a fail-fast alongside SC-4.
6. **Doc contradictions**: `01-extraction.md:25-28` teaches the SC-2 crashing pattern; `16-computed-attributes.md:184-200` example contradicts its own REQ-CA-03; `08-generation.md:198` lists a constraint template that nothing uses.

---

## Per-finding detail

### SC-1 — Constraint predicates silently dropped

**Verification.** Confirmed in every particular, two refinements: the stub is on the *part-def* path (`extractor.py:106-107`; `PartDefinitionData.constraints` exists but is always empty; `CalculationDefinitionData` has no field), and the dead code survived Phase 7 dead-code removal (`generation/constraint_comments.py` was removed; `constraint_extractor.py`, `constraints.py`, and the TODO-body template were kept). Nothing on the live path looks at constraints; no warning exists.

**Intent.** "Phase 6" comes from fusion-tea's own epic doc ("codegen Phase 6 (constraint predicate generation) is in flight" — `work/backlog/epic-pipeline-derisk-demo.md:21,47`). No such phase exists in any sysml-codegen planning artifact; the repo's Phase 6 is the unrelated refactor generation-validation phase. **Constraint execution was never decided or scheduled here**, and `modeling-assumptions.md` never mentions constraints — the silent drop is also a contract-documentation gap. The downstream consumer already adapted (harness-side ηG > 10 in `sweep_ife.py`).

**Two constraint shapes exist in the wild**: inline (predicate in the usage body — catf_mfe fixtures; the dead extractor handles this shape) and def-typed assert (predicate in the def, usage holds `in` bindings — fusion-tea; the dead extractor cannot handle this). Conflating them is the main design trap. They also mean different things: inline = input validation, part-level assert = viability gate.

**Rationale.** The capability at stake: viability gates evaluated *by the generated pipeline* so thresholds live in the model, not duplicated in sweep scripts (where they drift silently). Alternatives: (a) harness-side checks — status quo, proven, drifts; (b) model the gate as a calc def with boolean output — works today, zero codegen change, but loses `assert constraint` semantics and traceability; (c) agentic-mbse validation WARN (register A-1) — right layer for this project's philosophy, converts silent drop into informed decision, gives no execution.

**Recommendation.** Three cheap things now (S total): extraction-time warning when constraint usages are found (summary WARN + per-item INFO — catf_mfe has dozens of inline constraints, per-item WARN would be noisy), a "constraints are not executable" section in `modeling-assumptions.md`, and endorse A-1 in agentic-mbse. Backlog full execution as its own scoped epic: **part-level `assert constraint` typed by constraint defs only**, compiled into ordinary boolean-output pipeline modules that **annotate rather than halt** (TEA sweeps need violations to flow through so infeasible points can be classified — make this an ADR). No teax changes needed (`ModuleBase` is generic Pydantic-in/out; a bool channel is ordinary). When the epic starts: rewrite, don't wire in, `constraint_extractor.py`; delete `constraints.py` and `constraint_validator.py.jinja2` as dead code either way.

**Lift.** Warning + docs: S. Full execution: L — dominated not by mechanism but by refactor-machinery churn (ComputationGraph schema rev, field-set conformance tests, 4 baselines + 10 snapshots, reference docs).

**Risks.** ComputationGraph is the freshly-frozen generation boundary — amend it as a deliberate schema rev. syside nuance from WI-014: evaluating an assert usage returns the element, not the boolean — extraction must compile the def's predicate itself. Unsupported predicate expressions need an UNRESOLVABLE-style fallback, not a crash.

---

### SC-2 — `return`-style outputs invisible; crash on legal SysML

**Verification.** Confirmed by live syside probe, and broader than registered. The member-type filter (`extractor.py:151-153`, again at :189-191) skips everything that isn't an AttributeUsage. Probe results:

| Form | syside representation | Current behavior |
|---|---|---|
| `return y : Real = expr;` | ReferenceUsage, direction Out | Invisible → zero outputs → jinja crash at `teax_module.py.jinja2:118` |
| `in x : Real;` (bare) | ReferenceUsage, direction In | **Invisible → input lost** (new finding) |
| `return attribute y : Real;` + body `y = x * 2;` | AttributeUsage(Out) + expression on a separate direction-None ReferenceUsage | Output seen, **expression lost** → silent downgrade to manual stencil |
| `out attribute y : Real = expr;` | AttributeUsage | Fully handled |

The direction logic (`_get_direction`, extractor.py:231-241) already handles `"Return"` — only the member-type filter blocks it. Nothing guards zero outputs before the template.

**Intent is incoherent across artifacts**: `01-extraction.md:25-28`'s canonical example is return-style (and false as documented); the sysml-conventions skill stencil (`references/stencils.md:39-41`) teaches the expression-losing form (register A-2 confirmed); every fixture uses `out attribute`; `modeling-assumptions.md` is silent.

**Recommendation.** Support the named forms: relax the filter to accept direction-carrying ReferenceUsage members (`_extract_attribute` is already member-type-agnostic — probe confirms ReferenceUsages carry name/typing/expression). This fixes bare `return` AND bare `in` in one change and makes the existing docs true. Independently: (a) add a zero-output fail-fast diagnostic regardless — crashing inside jinja is the actual bug whatever patterns are legal; (b) reject anonymous `return : Real = expr` with a diagnostic (no name → nothing to build the PQN channel from; don't synthesize); (c) decide separately whether to capture body-assignment expressions to restore auto-impl for the skill-stencil form.

**Lift.** Filter + named-return + bare-in + fixture/snapshot/tests: S. Body-assignment expression capture: M.

**Risks.** Must not double-ingest the `return attribute` form (two members named `y`; direction-None ReferenceUsages must stay excluded — the existing is_output/is_input structure already handles this, but the second-pass `member_expressions` loop needs the same care). Baselines safe (all fixtures are AttributeUsage-based).

---

### SC-3 — First-type part-usage indexing drops redefinition subtypes

**Verification.** Confirmed by live probe, unfixed by the refactor, and present in **two places**: `usage_extractor.py:163` (`next(iter(usage.types))` → template instantiation) and `hierarchy_resolver.py:526-533` (identical pattern → `usage_type_map` → literal-value-propagation resolves defaults against the wrong PartDef). Probe: for `part :>> driver : 'HIF Driver'`, `usage.types` = `['IFE Driver', Part, …, 'HIF Driver']` — declared type **last**. For plain usages the declared type is first and user supertypes are **absent** — an important fact for the fix design. The refactor deliberately skips type-only redefinitions for *value* extraction (25-hierarchy-resolver.md:74-76, correct) but never followed the consequence into the index. Zero fixtures use retyping; the only unit test mocks single-type lists.

**Intent.** The documented convention (§5 template instantiation) lists LITERAL/CHAIN/deep-path redefinitions — retyping is *silent*, not forbidden. But it is the natural next step of the Costed Component specialize-and-redefine idiom, and the MFE epic's generic-plant → specialized-instantiation structure is exactly this shape. The `hif_driver_instance` workaround abandons the slot — the variant no longer conforms to the base facility structure, defeating the reuse the epic is built around.

**Recommendation.** Support. Mechanism is already proven in-repo: `_get_calc_def_name` (extractor.py:251-259) picks the owned FeatureTyping target from heritage. "Most-specific declared type" should mean **owned FeatureTyping target**, never a position in `usage.types`. But declared-type-*only* is wrong too: today the retyped usage accidentally serves supertype-owned templates; the right shape is **index under every user-model PartDefinition in `usage.types` plus the owned FeatureTyping target** (`{'IFE Driver', 'HIF Driver'}`), filtered to user packages. Fix `usage_type_map` the same way (prefer FeatureTyping target). Add a most-specific-owner tiebreak (or at least a warning) for virtual-QN collisions when supertype and subtype both own a same-named template calc.

**Lift.** S–M (a day; mostly the retyping fixture + snapshot + conformance tests).

**Risks.** Double-instantiation when supertype and subtype own *differently*-named template calcs (both instantiate — can double-count if the subtype's was meant to replace) — bounded, warn on it. Baselines safe: plain usages' `types` lack user supertypes and 'Costed Component' owns no template calcs, so all-types indexing adds no consequential keys for existing models. Separate gap noted for the MFE epic: templates on a supertype never reach a *plain* subtype-typed usage (needs a supertype-chain walk) — out of scope here.

---

### SC-4 — Quoted names leak into Python identifiers

**Verification.** Confirmed and reproduced at HEAD using the existing `tests/fixtures/alias_agg_probe/` fixture (quoted calc defs): `'margin calc'.py` filenames, `class 'Margin Calc'Input`, registry importing a sanitized class name the module file doesn't declare. Root cause is a split at extraction: `name` is sanitized (`extractor.py:133`) but `qualified_name` is stored raw (`extractor.py:212`), and the ADR-003 derivation layer (`ModuleType.from_sysml`, `PythonModulePath.from_sysml` — `identifier_types.py:104-108, 140-143`) is pure string transforms with no sanitize. Channel names (PQN) are clean — built per-segment-sanitized. The refactor *formalized* the unsanitized derivation (REQ-REG-05 doc excerpt reproduces it verbatim) and even compensates ad hoc at `graph_builder.py:267-275`. Latent second leak: FORMULA `module_eqn` goes through `sysml_to_python_qualified_name` (bare `::`→`__`), so a FORMULA attribute on a quoted-named owner would leak into module/channel names.

**Intent is unambiguous**: quoted names are supported — `sanitize_name`'s docstring anticipates them, REQ-NC-06 mandates the transform, it's unit-tested, and fixtures use quoted names pervasively (`'Fusion Power Plant'`, `'Racking & Mounting'` — the `&` is only expressible quoted). Banning them (agentic-mbse route) would invalidate half the fixture corpus for a purely internal defect. The gap survived because no *baseline* model has a quoted calc def — the quoted fixtures only feed hierarchy/backtracker tests.

**Recommendation.** Sanitize at the source (`extractor.py:212` + producer of `owning_part_qualified_name`) — cleaner, makes the graph_builder ad-hoc normalization a no-op, consistent with `name` already being sanitized; verified that all consumers of `calc_def_qualified_name` are name-derivation, not syside lookups (one QN comparison at `dependency_backtracker.py:663` to check). Alternative: sanitize inside `identifier_types.py` (~10 lines) — must then also fix the FORMULA path. Add a **fail-fast duplicate-file-path check** (`cli/__init__.py:214` silently overwrites today); registry-level class collisions are already handled (SC-11). Add a conformance test generating registry/modules from `alias_agg_probe` and asserting `ast.parse` + import-name consistency.

**Lift.** S (half-day to a day including the collision guard).

**Risks.** Low: channel names and all baselines unchanged (verified — no baseline has a quoted calc def); today's output for quoted models is unimportable anyway. fusion-tea's `sanitize_names.py` post-processor should be retired in lockstep (its rules may differ subtly from `sanitize_name` — one-time name migration downstream). Source-sanitizing requires regenerating extraction snapshots.

---

### SC-5 — Cross-part references drop to unresolved entry points

**Verification.** Fully reproduced at HEAD (27 "Registry unresolved" warnings; missing gamma edge; fresh `ife_plant_params.json` has 2/16 keys, `hif_driver_params.json` is `{}` — the checked-in fusion-tea inputs are hand-filled, including run-A's computed gamma pasted as a constant). The register's "cross-part" framing needs one refinement: cross-part refs to *plain literal attributes on part usages* and to *EXPOSE'd outputs of top-level parts* already work (catf_mfe proves both, and is why its 42-module pipeline wires). The failure is specifically the **def/specialization idiom**: attributes declared on part defs, valued by `:>>`, parts nested and retyped.

**It is four mechanisms, not one bug:**

- **(A)** Def-declared attributes valued by `:>>` on a specialized PartDef (`driver.efficiency` ← `:>> efficiency = 0.35`) — design-attribute extraction skips all `:>>` AttributeUsages entirely, so the dotted match has nothing to hit; classification then tries `float("driver.efficiency")` → bare entry point, no pre-fill.
- **(B)** Cross-part calc chains through specialized nested parts (`driver.cost_per_joule` ← `meier_cost.gamma`) — three stacked failures: retype not honored in the usage index (= SC-3), the one CHAIN alias keys to the workaround instance, and the backtracker has **no consumer-scoped alias lookup** (Step 2 is unscoped only, `dependency_backtracker.py:584`) so the correct key could never be constructed.
- **(C)** `:>>` overrides on *plain* part usages are never extracted — `extract_design_overrides` guards on `owned_redefinitions` (`hierarchy_resolver.py:182`), which only `part redefines` usages have. This is why "0 bindings rewritten" and why even the workaround instance's own literals drop.
- **(D)** Rider: self-named bindings (`in availability = availability`) resolve to the calc's own parameter — only the rewrite path (C) can rescue them; a conventions check belongs in agentic-mbse (register A-1 already proposes it).

**Intent.** Deliberately deferred — `.project/backlog/epic_attribute_expression_capture.md:89,432`: "Cross-part references: 0 found across all models. Phase 3 concern." The fixture evidence that justified deferral simply doesn't contain the idiom. Meanwhile fusion-tea's WI-009 design doc describes WI-010 as "exactly the `ife_plant.sysml` idiom, one level richer" — **the gating claim is confirmed in the client's own design docs.**

**Alternatives judged.** Flattening models to the catf_mfe idiom is a proven bridge but the wrong endpoint — it forfeits exactly the generic-def/specialized-instance structure the MFE epic is built on. Permanent harness wiring is semantically wrong under sweeps: gamma depends on driver parameters, so fixed-value feedback silently decouples them the moment a sweep varies those parameters.

**Recommendation.** Full support, staged:

- **Stage 1 (S pieces, ships literal pre-fill):** (1) capture `:>>` on plain part usages (one guard, `hierarchy_resolver.py:182`); (2) propagate `RedefinitionData` literals to CalcUsage entry-point defaults (mirror of REQ-LVP, which exists for aggregations only).
- **Stage 2 (channel wiring):** (3) consumer-scoped alias lookup step in CHAIN dispatch (additive, `dependency_backtracker.py:565-588`); (4) retype-honoring usage index (= SC-3 fix); (5) per-instance binding rewrite through the specialization chain with redefinition precedence — the genuinely hard part (M), and **blocked on fixing the shared-BindingInfo mutation bug** (`usage_extractor.py:259`); (6) PartDef-level EXPOSE with instance-scoped alias keys (overlaps SC-7).
- **Precondition:** an ife_plant-shaped conformance fixture as the fifth baseline — the "0 hits" blind spot must not repeat.

**Lift.** M overall (roughly one refactor phase), meaningfully easier post-refactor: single resolution dispatch site, typed registries with a defined collision policy, the Phase-2 instance-path-alias precedent, and the conformance net.

**Risks.** Component 4 changes indexing for all models (baselines are the net, run per component). Keep all new registry keys consumer-scope-prefixed (unique by construction, FR-6). Correct wiring **moves the gamma channel name** — fusion-tea harness/sweeps must re-anchor and the `hif_driver_instance` workaround part should be deleted upstream. Aggregation-scoping interaction when new virtual instances appear. Enum-valued CHAIN redefs currently filtered by a `"." in source_path` check could become junk aliases if filters are loosened carelessly.

---

### SC-6 — Expression reconstruction corrupts literals, loses parens

**Verification.** Reproduced live: docstring shows `capacity * rate / LiteralRationalEvaluation() * LiteralRationalEvaluation()` next to a correct executable body. **Register's root cause corrected**: the literal branch would work if reached (`is_instance(node, "LiteralRational")` is True on live nodes); the bug is that every SysIDE expression node carries a derived KerML `.function`, so literals hit the invocation catch-all first (`expression_utils.py:57` before :64-77). Second, independent defect: `reconstruct_operator_expression` never emits parens.

**Fix.** In place, two parts: move literal branches (plus LiteralBoolean/LiteralString/NullExpression) above the catch-all, preferably via `is_instance` dispatch; add precedence-aware parenthesization (~30 lines — minimal text churn vs. always-paren which rewrites every `expression_text` in baselines). The compiler path (`build_expression_ast`) is faithful but not a drop-in replacement — it's Python-flavored and deliberately narrower (no FCE/chains/booleans), and `reconstruct_expression` also serves constraint text and the aggregation fallback.

**PUSH-DOWN interaction**: `expression_utils.py` moves wholesale to agentic-mbse in the P1 backlog item (design ready, not implemented). Fix here first so the pushed-down code is born correct and baseline churn is reviewed once.

**Lift.** S: ~40 lines + regenerating baselines — 173 occurrences of `LiteralRationalEvaluation` across 12 committed fixture files, all regen-scripted. Add a regression test against a real parsed AST (mocks masked this bug — mock nodes lack the derived `.function`).

---

### SC-7 — EXPOSE_PURE derived-attribute name drop

**Verification.** Confirmed and worse than registered. Both shapes lose the name:

- **Shape A (attr + calcs on a part def, instantiated separately — the toy):** warns and drops. Two layers: REQ-CA-03 deliberately skips ChannelAlias production for part defs (no instance scope at extraction — sound rationale), and `_resolve_expose_pure` matches simple names against EQNs (`graph_builder.py:665-669`: refs are `'cost_calc'`, backtracker instance names are `'toy_plant__demo_plant__cost_calc'`) → the register's exact warning.
- **Shape B (attr + calcs on a part usage — catf_mfe shape):** **silently** drops. The alias IS produced and registered (`plant.total_cost` → canonical channel) but lives only in the in-memory OutputRegistry for resolving *other references* — nothing emits the name into YAML/schemas/JSON.

Since EXPOSE is officially supported (modeling-assumptions §3 promises "consumers bind to `subsystem.exposed_name`"), this is a bug in promised functionality, though the *name-surfacing* half was arguably never promised. Doc bug found: 16-computed-attributes.md's own example contradicts REQ-CA-03.

**Recommendation.** Warning upgrade now (~30 min, risk-free): state plainly that the name is dropped and where the value went (the canonical channel). Alias surfacing later as a deliberate feature: a graph-level `output_aliases` field rendered as named exit-point captures — 0.5–1 day for shape B (registry already holds the mapping), 1–2 days for shape A (needs per-instance alias expansion + REQ-CA-03 revision; same instantiation problem the hierarchy resolver solves — and it's component 6 of SC-5 stage 2, so bundle them).

**Risks.** Alias captures need instance qualification to avoid collisions; baseline/YAML churn on surfacing.

---

### SC-8 — Warning noise that looks like failure

**Verification and reframe.** Confirmed benign *in outcome* for the reported cases — but the register's "triage or silence" framing is the wrong menu. Three verified facts change the fix:

1. The benign "Registry unresolved" warnings are first-pass misses caused by **two real matcher bugs**: `sysml_to_python_qualified_name` does no per-segment sanitization (quoted-QN REFERENCE paths never match, `qualified_names.py:103-105`), and design attributes owned by part *defs* extract with `parent_part=''` while bindings carry the part *usage* name (`dependency_backtracker.py:650`).
2. The downstream repair (`graph_builder.py:534-544` merges values the classifier missed) is lossy: entry points are misclassified (USAGE_LITERAL instead of DESIGN_ATTRIBUTE, wrong ADR-001 metadata) and Step-3's dedup is lost (two calcs reading one design attribute mint two JSON keys).
3. **The same warning text provably masks a real failure**: in the committed catf_mfe fixture, `pipeline.yaml:402` references a params key absent from `magnets_params.json` (dangling `magnet_volume` input, downstream of a FORMULA compile failure) — a runtime crash. Blanket demotion would hide it.

**Recommendation.** (1) Fix the two matchers (~0.5 day) — this is a **behavioral** change (classification + dedup churn in baselines and params-JSON key sets), not a logging patch; flag the key-collapse in release notes. (2) Then demote per-binding Step-4 lines to DEBUG and add a post-assembly reconciliation summary + **params-coverage check**: any module input referencing `*_params.X` with no matching key in any parameter group is a hard error (precedent: `_validate_channel_references`). That check would have caught the catf_mfe dangling input precisely. Adjacent noise worth the same treatment: 25 of catf_mfe's 29 warnings are repetitive alias-collision lines.

---

### SC-9 / SC-10 — Snapshot-driven generation

**Verification.** Confirmed (register's "6 snapshots" is now 10). The refactor already built and battle-tested every ingredient: loader/serializer round-trip, snapshot-to-graph assembly used by 900+ conformance tests, and the REQ-ORCH-06 boundary (generation consumes only ComputationGraph — the fusion-tea harness exploits it, passing `extractor=None`). SC-10 is narrower than registered: of the three auto-impl paths, FORMULA (`compiled_expression` string) and aggregation (`transformed_expression` string) already survive snapshots; only **CalcUsage** auto-impl is lost, because `compilation_results` is rebuilt from live syside ASTs that the snapshot nullifies. The "byte-identical solar_battery" result has a clean explanation: no baseline model has calc defs with inline output expressions — the loss only bites expression-bearing models like the IFE set, **silently** (well-formed output, stencils regress to NotImplementedError, `compilability` stays UNKNOWN, smart-regen's stub-upgrade never fires).

**Recommendation.** Ship SC-9 + SC-10 as **one change** so the snapshot format version bumps once:

1. Promote loader/serializer out of `tests/helpers/` (clean move — no syside runtime imports); parameterize the fixtures dir.
2. `build_pipeline_context_from_snapshot()` in `orchestration/` (the proven conformance-helper body).
3. `--from-snapshot PATH` on `generate`, mutually exclusive with `--models`; reject `--design-path-filter` with it (filter is baked at capture).
4. A `sysml-codegen snapshot` capture subcommand (else users can't produce snapshots through supported surface).
5. **`snapshot_format_version`** (currently absent) with a hard error on mismatch, plus a source-hash freshness check — `source_hash`/`source_file`/`captured_at` are already in the snapshot, so warn (or `--strict`-fail) on drift.
6. SC-10: serialize `compilation_results` — plain dataclasses of already-lowered, validated Python expression strings; the generic serializer handles them with near-zero new code. Never attempt syside AST serialization (live bridge objects, impossible — that's why `_AST_FIELDS` exists). Old snapshots degrade to today's behavior with a warning.

**Lift.** M for both together (SC-10 adds ~half a day). A minimal library-API-plus-flag version is S, at the cost of carrying the versioning risk.

**Risks.** The snapshot format becomes a public contract over just-refactored dataclasses, and the re-capture escape hatch requires the (currently precarious) license — versioning is therefore not optional. This is also the license-exposure mitigation the register's infrastructure note asks for (license expires 2026-08-06).

---

### SC-11 — Class-name collision aliasing

**Verdict: closable as "confirmed intended, documented, tested."** `_resolve_class_name_collisions` (`generation/registry.py:60-129`) is a first-class design decision with rationale in 20-module-registry-generation.md:29-34, requirement IDs REQ-REG-03/04/07 (PASS in the verification matrix), direct conformance tests (`test_gen_registry.py:354-452, 595-643` — uniqueness, aliased imports, pre-render warning, plus a no-collision negative test), and a checked-in aliased baseline validated as parseable Python.

Two residual gaps, neither affecting disposition, optionally one small follow-up: the alias scheme uses only the parent segment and doesn't re-check uniqueness after aliasing (two `pump` scopes under different grandparents collide); the import rewrite is substring-based with first-match break.

---

## Suggested sequencing (sysml-codegen work only)

1. **Now, cheap, stops silent wrongness:** SC-1 warning + modeling-assumptions entry; SC-7 warning upgrade; SC-2 zero-output fail-fast. (All S; none change generated output for valid models.)
2. **Small bug fixes in promised functionality:** SC-2 named-return/bare-in support; SC-4 sanitization + path-collision guard; SC-3 index fix (both sites); SC-6 reconstruction fix (before PUSH-DOWN); SC-8 matcher fixes. Import the WI-014 toy + a retyping fixture as conformance baselines alongside.
3. **SC-8 reconciliation summary + params-coverage check** — makes the remaining SC-5-class failures loud and precise before SC-5 work starts.
4. **SC-5 staged** (stage 1 literal pre-fill → stage 2 wiring incl. the SC-3/SC-7 components and the BindingInfo deep-copy fix), with the ife_plant fixture landing first.
5. **SC-9+SC-10 as one change** — timed against the 2026-08-06 license expiry, since it's also the mitigation.
6. **SC-1 full execution** as a scoped epic, only if in-pipeline gates earn their keep after the MFE epic clarifies demand.
7. **SC-11**: close.
