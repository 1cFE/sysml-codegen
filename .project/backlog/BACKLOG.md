# Product Backlog

**Updated:** 2026-10-19

Current work and independently justified follow-ons. Owner-originated rulings retain their source authority; agent proposals remain challengeable. Historical closed work is available through Git and durable registers.

## Active Work

No active implementation items. ELABORATE-FIRST and PR-readiness cleanup are closed; their bounded certification and historical authority are recorded in [CURRENT_WORK](../CURRENT_WORK.md).

## Capabilities and Diagnostics

### [INDEXED-ELEMENT-EXPRESSION-SUPPORT] Valid indexed element references — unscheduled `[AGENT]`

SysIDE preserves an authored index; codegen currently refuses before graph construction with `SI_INDEXED_SOURCE_UNSUPPORTED`. Adding execution semantics needs a separate scoped capability. Earlier agent filings proposed P1 and P3; they are consolidated here without assigning an owner priority. Sources: parser Phase-4 design D5/D7/D8 (Git history), `tests/fixtures/indexed_expression_source/model.sysml`, and `tests/conformance/test_expression_evidence_integrity.py`.

### [OUTPUT-ALIAS-DUPLICATE-SOURCE-SILENCE] Multiple aliases for one source — unscheduled `[AGENT]`

Aliases survive in `graph.output_aliases`; generation currently selects the first alias for the single file per exit channel. Decide whether to emit additional files or diagnose the second alias in its own item. Earlier P1/P3 filings are consolidated without assigning an owner priority. Evidence: `elaboration/project.py`, `generation/pipeline.py`, and `tests/unit/test_exit_point_aliases.py`. The earlier extraction-loss premise is superseded.

### [POSITIONAL-FORMAL-REDEFINITION] Improve skipped-formal diagnostics — P1, unowned `[AGENT]`

Current elaboration follows parser redefinition identity. The August 21 filing's name-matching/positional-codegen premise is superseded; it does not establish a binding defect. A clearer refusal should identify the skipped formal and corrective declaration order. Customer examples and the original four sites remain in the August 21 backlog revision and `models/stellarator_migration_ledger.md` in fusion-tea; `tests/fixtures/modeled_default_fidelity/PROVENANCE.md` records parser positional behavior.

- **[SCALAR-FUNCTION-VOCABULARY] Add scalar invocation functions as a separately owned capability — P2 `[OWNER, 2026-08-18]`.** Supporting `min`, `max`, or other scalar functions is not part of the stop-parser remediation; its declaration/compilation semantics remain separately owned. Today every invocation except the exact standard-library `NumericalFunctions::sum` declaration refuses before graph construction with `SI_EXPRESSION_SOURCE_UNSUPPORTED`, naming the authored expression and its source location. A future capability must define and test each admitted function explicitly. **Motivating case (filed 2026-08-21, fusion-tea stellarator-model-migration):** the stellarator model authored six invocations -- `RealFunctions::sqrt` in `'DT Fusion Power'` (`mfe_plasma_scaling.sysml`, the Bosch-Hale peak reactivity) and `RealFunctions::max` ×3, `min`, `floor` in `'Levelized Replacement Cost'` (`mfe_account_costs.sysml`, jnp.clip and ceil written as identities). Both calcs were made opaque manual interfaces so the pinned route generates (fusion-tea `models/stellarator_migration_ledger.md`, Class B rows, Appendix A/B hold the verbatim bodies); fusion-tea carries a revert row to restore them when this capability lands. The wanted vocabulary for that model is exactly `sqrt`, `max`, `min`, `floor`.

- **[DEEP-QUALIFIED-OUTPUT-WIRING] Wire a deep qualified reference to its concrete calculation output — P2 `[AGENT]`.** The authored shape is `measurement_system::station::array::sensor::core::metric_value` in `tests/fixtures/deep_cross_scope_probe/design.sysml`. The current contract is `SI_OCCURRENCE_MISSING` because no producer exists in the consumer domain, with no captured snapshot. Transition A2 owns that refusal. Implement exact producer wiring as a separate capability; do not restore the removed globally-sole substitution.

### [CALC-USAGE-BINDING-LOST-WITH-RESULT-EXPRESSION] A calc usage with its own result expression also loses its input binding — unscheduled, owner Reid Westwood `[AGENT]` (filed 2026-10-19, EXEC-SUBSET-CONTRACT Item 2a P5)

Found in Item 2a P4. In `calc m : Twice { in v = x; v * 3.0 }` the generator ignores the usage's result expression (RG1-3, a candidate refusal for the owner) and also drops the `in v = x` binding: `v` becomes a `library_default` entry point with a null default, and `x` gets no entry point. The same usage without the result expression binds `v` to `x`. Pinned by case `calc-usage-result__bare_result__other_expression_site` (agentic-mbse package; stored answer `tests/expectations/subset_profile/cases/`), whose `contract_parameter` and `entry_point` seams record today's output, so a fix fails that case visibly and its answer is re-captured; control `calc-usage-result__no_bare_result__other_expression_site`. Suspected cause, not confirmed: `_collect_bound_members` (`src/sysml_codegen/elaboration/elaborate.py`) iterates `getattr(usage, "owned_members", None) or ()`, and on this usage that iteration yields the operator expression twice and never the `in v` member, while `.collect()` yields both; the `or ()` truth test may consume SysIDE's lazy iterator. Recorded rather than fixed in Item 2a because the fix changes generated output, which is outside that item's scope. If the owner accepts RG1-3's refusal, this shape stops generating, and the defect remains for any other path that reads `owned_members` the same way. Source: `c381fb00:.project/active/subset-profile-conformance/rg1-recommendations.md` RG1-3.

### [CALC-DEF-KEYWORD-MEMBER-STUB] A calc def member named with a Python keyword becomes a manual stub — unscheduled, owner Reid Westwood `[AGENT]` (filed 2026-10-19, EXEC-SUBSET-CONTRACT Item 2a P5)

RG1-8. In `calc def C { in v : Real; attribute 'if' : Real = 2.0 * v; return r : Real = 'if' + 1.0; }`, `r` compiles to a `MANUAL_REQUIRED` stub with cause `compile_reference_unresolved`. The extractor registers the member through `core.qualified_names.sanitize_name`, which suffixes reserved words (`if_`), while the renderer resolves the reference through `expression_compiler._sanitize_name`, which does not (`if`), so the lookup misses. A leading digit (`'1x'`) behaves the same. Pinned by codegen-home case `calc-def-output-stub__python_keyword_member` (stored stub cause and a `calc_compilability` seam reading `manual_required`), so a fix shows as a changed stub list and seam; control `calc-def-output-stub__compiled_control`. This is the divergence [SANITIZER-MERGE] records as deliberate, and it shows that the two sanitizers do not match by construction for calc def members with reserved-word names. The stub fails safe, so acceptance does not change; Item 2a recorded it as a defect rather than fixing it because a fix changes generated output. It also shadows the renderer's not-Python check (`render_calc_expression`), which no model reaches while this mismatch stands (`tests/expectations/subset_profile/mutations.json`, unwitnessed). Source: `c381fb00:.project/active/subset-profile-conformance/rg1-recommendations.md` RG1-8.

### [REGISTRY-CALC-DEF-SIMPLE-NAME-DEDUP] Two calc defs with one simple name may register one class — unconfirmed, unscheduled, owner Reid Westwood `[AGENT]` (filed 2026-10-19, EXEC-SUBSET-CONTRACT Item 2a P7)

Unconfirmed: read from the code in Item 2a P6, not reproduced. `_registry_class_entries` (`src/sysml_codegen/generation/registry.py:155`) keeps one registry entry per `calc_def_name`, the calc def's simple name (`seen_names`), so two calc defs named `Twice` in different packages may both generate a module while the registry lists one `TwiceModule` class. If so, the second calc def's module is silently unreachable through the registry, a silent loss with no refusal. Probing it was not in Item 2a's scope (the orchestrator's ruling on Phase 6, 2026-10-19), so no case pins it. The first step is a two-package model and a read of the generated `__init__.py`. Source: `c381fb00:.project/active/subset-profile-conformance/plan.md` § Phase 6 Completion, "Other findings".

### [SI-TYPE-INVALID-MESSAGE-PRINTS-QN-OBJECT] The usage-typing refusal prints a SysIDE object, not the usage name — unscheduled, owner Reid Westwood `[AGENT]` (filed 2026-10-19, EXEC-SUBSET-CONTRACT Item 2a P7)

`_typed_definition` (`src/sysml_codegen/elaboration/elaborate.py:1720`) formats `usage.qualified_name` with `!r`, so the `SI_TYPE_INVALID` message reads `syside.core.QualifiedName([...]) has 0 exact CalculationDefinition typings` where a modeller expects the dotted name. Item 2a P6 converted this site from a plain `ValueError` to `SI_TYPE_INVALID` (O8) and kept the message body, which predates it. Not fixed in Item 2a, by the orchestrator's ruling on Phase 6 (2026-10-19). Cases that reach it: `calc-usage-typing__untyped`, `calc-usage-typing__subsetting_only` (stored answers in `tests/expectations/subset_profile/cases/`; they store code and reason, not message text, so a fix changes no stored answer). Fixing it changes message text only.

### [ITEM-OWNED-PART-REFUSED] A part usage owned by an item refuses the whole model — suspected defect, unscheduled, owner Reid Westwood `[AGENT]` (filed 2026-10-19, EXEC-SUBSET-CONTRACT Item 2a final-audit fixes)

RG1-12. `item it : Thing { part rk : Rack; }` inside `part def Site` is refused `SI_EDGE_DANGLING` "root occurrence has no package display metadata" (reason `graph_root_occurrence_package_missing`), a check in `InstanceGraph._validate_occurrences` (`src/sysml_codegen/elaboration/graph.py:616`) meant to catch inconsistent records. The cause, read from the code and not yet confirmed by a fix: `build_occurrence_index` makes every part usage not owned by a part def or part usage a root occurrence (`elaboration/occurrence.py:935-942`), but gives package metadata only to a root owned by a package (`occurrence.py:1021-1031`), so a part owned by an item usage or item def becomes a root with none. Probed (models in `c381fb00:.project/active/subset-profile-conformance/evidence/experiments/audit-fixes/probes/`): the same refusal when nothing reads the part, when the part is in an item def a part usage types, and when the item def is never used at all. The screen reports these models clear. Pinned by codegen-home case `candidate-es-002__part_inside_item_usage__attribute_value` (stored code and reason, a `rg1_pending` disagreement), which shows a fix as a changed answer. A fix changes what is accepted, so it waits on the owner's RG-1 call. Source: `c381fb00:.project/active/subset-profile-conformance/rg1-recommendations.md` RG1-12.

### [DIAGNOSTIC-PROVENANCE-BY-CONSTRUCTION] Internal-defect diagnostic totality — separate follow-up

The parser predecessor closed by owner direction with its historical `Needs Work` audit preserved. Model-caused reference/location fixes shipped; independently complete internal-defect provenance remains separate. Source: parser-close/shipment Git records, product-lens final dispositions, and `.project/adr/0004-derive-occurrences-from-exact-evidence-or-refuse.md`.

## Retained Model and Assurance Work

### [GAP-CLOSE] Historical PR-wave evidence — unscheduled reconciliation

[INHERITED: historical GAP-CLOSE epic and independent audit, Git references below] Local scope is certified and F1 runtime normalization was verified closed in merged TEAx `fa0e06a` on 2026-07-20. The July full-suite PR-wave evidence gap remains unreconciled. The epic (`a082db22a120f5fa420312f96881a59b71166cd5:.project/backlog/epic_gap_close.md`) retains the July evidence record: the normalized-runtime behavior is closed, while pre-fix regression evidence and the full-suite wave gate remain unreconciled. The July audit also refuted the pushed companion whitespace claim; the independent audit (`a082db22a120f5fa420312f96881a59b71166cd5:.project/backlog/epic_gap_close_audit_independent.md`) describes its July 18 candidate. Today's passing tests do not retroactively certify that wave.

### [SOURCE-IDENTITY-LIFECYCLE-ASSURANCE] Complete 35-coordinate evidence — unscheduled `[AGENT]`

The [source-identity reconciliation](../reference/source-identity-reconciliation.md) records the surviving requirement grades and per-coordinate bounds. All 29 cell keys have controls, but full 35-coordinate lifecycle evidence and LC-SI-23 remain PARTIAL. Separately scope any further assurance work against those recorded gaps, preserving the owner's descoped joined-study/lineage obligations. ELABORATE-FIRST closed for independently certified bounded delivery on 2026-10-10; this entry does not reopen its implementation.

### [SNAPSHOT-CODEC-AND-DUP-CONSOLIDATION] Digest-sensitive consolidations deferred from REPO-CLEANUP Move C — P3, unowned (filed 2026-08-25)

Move C deleted the dead lanes; three *duplication* findings from the same inventory (`aa35f06fb6b3bacfd42c7763a07a4ee4fdaafa57:.project/research/20260820-201945_line-count-anatomy-and-salvageability.md` §5) are consolidations whose cost is a digest or byte change, so they were filed rather than done:

- The hand-written snapshot codec (`snapshot/instance_graph.py`, ~550 collapsible lines in the August inventory) — the original proposal was dataclass→Pydantic with union discriminators and a graph-version bump. Current snapshots are v6; re-derive migration scope and the tracked fixture set before scheduling.
- The two ExpressionIR→Python numeric compilers (`calc_compat_renderer.py`, `predicate_compiler.py`) differ mainly in spacing — consolidating changes emitted bytes, so it rides with a deliberate baseline re-capture, not a cleanup pass.
- The canonical-JSON encoder copies (three byte-identical of six) sit on sealed-digest paths (contracts, snapshot, catalog); consolidate only with the byte-identity gate run per encoder.

Judged no-change, recorded here so it is not re-proposed: the error-subclass constructors (`extraction/errors.py`, `elaboration/occurrence.py` and friends) and the `_collect_unbound_{constraint,calculation}_formals` pair look like boilerplate but carry different payloads per site; collapsing them means a dispatch shim, and the owner ruling is qualitative simplicity — deletion over shims.

### [CATF-CRYO-HEAT-LEAK-COEFFICIENT] Magnet static heat-leak coefficient ~3–6 orders high; authored CATF design point is gate-infeasible — P1, unowned (filed at owner direction, 2026-08-13)

**The defect (measured, Item 5 finding 6-D; figures corrected 2026-08-13 — see below):** `heat_leak = magnet_volume * 0.05 // MW` (`library/analyses/thermal_loads.sysml:59`) puts **116.72 MW** of static heat leak into a **20 K** system — `magnet_volume = 2334.47 m³ × 0.05`. That is **69.5%** of the **167.92 MW** cryogenic-temperature load, which the refrigeration term then amplifies by **`300/(20 × 0.3)` = 50×** into `cooling_power = 8396.054399837172 MW`, **5.43× the plant's gross electric output of 1546.723690193402 MW**. Net electric power is therefore negative at the authored inputs. Real cryostats see kilowatt-scale static leak, so the coefficient reads as W/m³ or kW/m³ written as MW/m³.

> **Correction, recorded.** This entry was filed carrying "~38 MW into a 4.5 K system, ~×220
> amplification". Those figures came from a hand estimate in Item 5's STOP report that assumed
> a 4.5 K magnet system. The model says `operating_temp = 20 [K]`
> (`designs/catf_mfe/magnets.sysml:66`). The corrected figures above are **re-derived from
> model source and shown to reproduce the executed value bit-exactly** by
> `.project/completed/20260813_catf-constraint-policy-acceptance/cryo_derivation.py`, which is runnable and
> self-checking. The conclusion is unchanged and the headline numbers (8396 MW vs 1547 MW,
> 5.43×) were always right; only the internal breakdown moved.

The identical number reproduces on untouched `catf_mfe_d5` — it was always true and always invisible, because d5 executes zero gates. The first execution of the derivative's asserted gates (CONSTRAINT-SEMANTICS Item 5) caught it: the epic's founding failure mode, demonstrated and closed by the same item.

**Why P1, not P3 — the prioritization insight [AGENT] (ratified by owner, 2026-08-13):** a design search run against the uncorrected cryo model rejects essentially everything near the authored regime. The corrected coefficient is a **prerequisite for design search being useful**, not merely honest — so this should be scheduled soon after the CONSTRAINT-SEMANTICS epic lands, ahead of any real CATF study campaign.

**Scope of the fix (separately authorized per the 6-D ruling; NOT inside Item 5):**
- First decision is the fix's **home**, made in daylight with its own provenance: the derivative's copy of the library (frozen twins untouched; physics diverges deliberately; PROVENANCE records it) vs the upstream shared library (frozen-twin territory; needs its own ruling).
- A physically defensible replacement coefficient is a **modeling decision** — owner or domain-source signed, never agent-invented (same rule as tolerances).
- Re-run Item 5 Phase 6 acceptance under the corrected model; derive feasibility headlines and SC-5 candidate labeling from the resulting model arithmetic.

**Evidence home:** Item 5's verification record, source-derived arithmetic, and the 6-D ruling are retained at `62a07e5c870158672eb100f1cba73adfe4c9df28:.project/completed/20260813_catf-constraint-policy-acceptance/`. The acceptance record states the authored point is gate-infeasible under the model as authored. [AGENT] The same derivation includes about 51.20 MW of nuclear heating at cryogenic temperature; at 50× refrigeration power, removing static heat leak alone still leaves about 2,560 MW of cooling demand. A corrected coefficient therefore requires fresh feasibility assessment rather than assuming the headline becomes feasible.

---

### [CALCDEF-GATE-IMPLEMENTATION] Implement calculation-definition constraint gates — P1, unowned, awaiting owner authorization (filed at owner direction, 2026-08-13)

**What it is:** the production implementation of the capability CONSTRAINT-SEMANTICS Item 6 designed. One asserted constraint owned by a calculation definition expands into one concrete check per calculation occurrence, with usage-level coverage and occurrence-level results joined through exact graph identity. Today the usage is classified `non_reaching / owner_kind_unattachable` with error severity; an asserted gate halts generation with `SI_CONSTRAINT_UNATTACHED`. Evidence: `tests/unit/test_constraint_usage_record_mint.py::test_asserted_gate_owned_by_a_calc_def_halts_naming_the_missing_attachment` and `src/sysml_codegen/elaboration/graph.py`.

**Authorization status `[OWNER 2026-08-13]`:** **not authorized in the CONSTRAINT-SEMANTICS epic.** The owner ruled at Item 6's close that this is a separate, later decision. It is unowned and unscheduled. It competes for the next slot with `[CATF-CRYO-HEAT-LEAK-COEFFICIENT]` (P1). **No agent may start it without a new owner ruling.**

**Historical estimate `[AGENT]`:** 7–9 working days, cross-repository (codegen + TEAx); re-estimate against the delivered architecture before scheduling.

**Historical design:** `be8d3dd:.project/completed/20260813_calcdef-constraint-gate-design/implementation-item.md` — file-level scope, dependency pins, phase order, and customer-shaped acceptance tests, revised against three rounds of independent design review (F1–F8). Its companions are `spec.md`, `design.md`, `design-review.md`, and `probes/findings.md` in the same archived folder. The spec's production-acceptance boxes are deliberately still open: they are this item's, not Item 6's. [AGENT] Reconcile the proposed graph-v4/catalog-4 migration against today's v6 snapshots and catalog 3.0.0 before implementation.

**Historical unit-lane prerequisite — SATISFIED:** constraint-formal and computed-attribute unit metadata landed at **`62a07e5c870158672eb100f1cba73adfe4c9df28`**. Evidence bundle: `62a07e5c870158672eb100f1cba73adfe4c9df28:.project/completed/20260813_unit-lane-port-metadata/verification.md`. Owner authorization remains required; the historical dependency pins need refresh against the current repositories.

**Carried guards and consequences:**

- **SC8 — re-derive, never reuse.** A future snapshot migration must derive its own then-current tracked path set from Git and prove equality against that. Item 8's 23 paths and the older 15-path subset are dated evidence, not durable scope.
- **TEAx re-vendor.** The archived design proposes **catalog 4.0.0** and coordinated TEAx consumer changes. Its `5b70ae9` baseline is historical; the October cleanup execution used TEAx `8d877460ac4f6f264561d916e40c1708adb13397`. Refresh producer/consumer compatibility and immutable dependency pins when shaping this capability.
- **R5 joint delivery is declined.** Folding Item 8's unit-lane work into this implementation was ruled out and executed as ruled — Item 8 shipped standalone. The option text survives in `design.md` as a decision record only; **reviving it requires a new owner ruling**, not an agent reading the recorded option.

---

### [ANCHORING-ARRAYED-DIAGNOSTIC] Arrayed-owner aggregation: reconcile the two spellings — P3, unowned (filed at owner direction, 2026-08-16)

For an arrayed owner `comp_a : Component[2]`, `sum(comp_a::length)` refuses with `SI_OCCURRENCE_AMBIGUOUS` while `sum(comp_a.length)` resolves to one input per occurrence. Direct one-segment references are deliberately scalar (design D4 of `qualified-reference-occurrence-anchoring`): a direct reference names one owner, so fanning it out would invent a cardinality the model never authored. **[OWNER 2026-08-16]** accepted that policy for the delivering item and filed this instead of reversing it.

Nothing that worked was lost — pre-repair, `sum(comp_a::length)` silently summed the *sibling's* value, so this is the same fix rather than a new break. What remains is author-facing: the diagnostic names neither the candidate occurrences nor the index syntax that would resolve it.

**Scope the diagnostic message first** — that may be the whole fix. Reversing D4 would reopen a ratified design decision and its review, and risks the cardinality drift that item's risk register was written to prevent. Bound recorded at [0002](../product/0002-exact-owner-anchoring.md).

### [CATF-DIVERTOR-GATE] Divertor addition + HeatLoadBalance gating, CATF derivative — P3, unowned (filed at owner direction, 2026-08-13)

`FusionComponents::Divertor::HeatLoadBalance` is a genuine one-sided power-exhaust gate with no divertor part anywhere in the CATF design, so Item 5's ruled disposition table leaves it `inapplicable` (owner-disposition.md B1/O5, **[OWNER 2026-08-13]**). Gating divertor physics means adding a divertor to the model — a modeling-scope decision to make in daylight. This entry records the option; priority is the owner's-later.

### [CATF-SHIELD-MODEL-DEBT] d5 shield closure/thickness inconsistencies carried into the derivative as recorded debt — P3, unowned (filed per O3 ruling, 2026-08-13)

Two pre-existing d5 modeling-debt items, ruled "record, don't bake silently" (Item 5 owner-disposition.md O3, **[OWNER 2026-08-13]**): the shield volume-fraction closure covers 2 of 4 layers (`thermal_shield`/`biological_shield` have no `fraction_volume`), and `'Shield Assembly'::TotalThicknessConsistency` sums four layer thicknesses while the design's `thickness_total` is `0.4 [m]` ("HT shield + structure layers") — not the same set; the guard would fail if attached. Named model-debt entries live in the derivative's PROVENANCE; this is the one backlog note the ruling requires.

### [ACAUSAL-RELATIONS-CAPABILITY] Relation-style parametrics with study-selectable causality — P3, unowned capability bet (filed at owner direction, 2026-08-13)

"Don't force independent vs dependent": acausal constraint relations whose solve direction is study-selectable are a capability this toolchain cannot currently express — Item 5's derive rulings (owner-disposition.md, ruling item 5, **[OWNER 2026-08-13]**) choose visible in-model bases precisely because the alternative hides causality in study harness config. Recorded so the bet doesn't quietly die.

[AGENT proposal, unimplemented] The relational/DM-decomposition alternative is retained at `aa35f06fb6b3bacfd42c7763a07a4ee4fdaafa57:.project/research/02-arch-relational-solve-dm-decomposition-v1.0.md`; it supplies background for the acausal capability.

### [MATRIX-EPIC-SURFACE-ROWS] Add verification-matrix rows for the three uncovered lifecycle surfaces — P3 `[OWNER]` (ticketed 2026-07-24)

Owner directed filing this as a ticket at the docs-lifecycle-sync wrap. The lifecycle epic added tested behaviors with no matrix rows; docs-lifecycle-sync Phase 4 added only the required portability pair (REQ-SNAP-21/22) and registered these three as candidates (`.project/completed/20260724_docs-lifecycle-sync/inventory.md`, MG1–MG3):

1. **Producer resolution / completeness** — the unified ladder (`resolution/producer_resolution.py`, `resolve_producer`, KEY_FORMS, TerminalPolicy) and `producer_completeness.py`. Reference doc exists (`04-producer-resolution.md`); pinning tests exist (Item 2's suite, e.g. `test_producer_completeness_acceptance.py`) — verify which tests pin which claim before citing (no aspirational citations).
2. **Catalog schema 2.0.0** — `CATALOG_SCHEMA_VERSION` (`contracts/versions.py:18`) and the catalog contract (`test_catalog_schema_version.py`, `test_catalog_definition_join.py`).
3. **Trust manifest / bootstrap** — `contracts/manifest.py` and the trust-anchor behavior (Item 7's tests).

Discipline: matrix recount per memory `verification-matrix-drift-modes` (index totals + per-family counts, not just the summary block). The **288 rows / 156 PASS / 34 families** count belongs to 2026-08-14; the current matrix summary lists 313 requirements and 35 families. [AGENT] Reconcile the three candidate surfaces against current matrix rows and retired mechanisms before scheduling; the old producer-resolution modules and catalog 2.0.0 are historical scope.

*The previous line here read "276 rows / 275 PASS / 32 families." The row and family counts were right for their date; **"275 PASS" was never true** — the matrix's own summary read 133 at the time and its tables read 134. Corrected by recount, not by adopting either number (`.project/completed/20260814_constraint-docs-agent-sync/verification.md`).*

### [DM08-MODEL-FIELD-TYPING] NewType-annotate the resolution-model name fields — P3

**Filed by TRUTH-DEBT Item 3 (Route A ruling), 2026-07-07.** REQ-DM-08's original text claimed the *model fields* use NewType wrappers; at HEAD they are deliberately bare `str` (`resolution/models.py`: `EntryPoint.qualified_name`, `InputSource.qualified_name` / `producer_channel`, `ModuleOutput.channel_name`), and `09-data-models.md` documents the field↔format table with this deferral. Item 3 pinned the *enforced surface* (OutputRegistry dicts + `make_*` constructors, `test_dm08_enforced_surface.py`) and reframed the REQ text to match (INV-B). **Scope**: annotate the documented model fields with their NewTypes (field↔format table in doc 09 is the target list), update the DM-08 row + doc 09 note, and extend the AST-scan test to cover the widened surface. Pure typing churn — zero runtime change (NewType is erased), but touches many models; mypy must not regress.

### [ITEM7-MATRIX-SWEEP-RESIDUE] Deep-read sweep findings — P3, test-coverage / matrix-honesty

**Absorbed into TRUTH-DEBT (`epic_truth_debt.md`) Item 5, 2026-07-06.**

**Filed by PIPELINE-TRUTH Item 7, 2026-07-06.** The leashed ~175-row deep-read sweep (Phase 8) ran to substantial completion via delegated per-family readers (~167 qualifying strong-word PASS rows examined). Every finding is a **PASS-but-pins-narrower** row — the cited test passes and the behavior is real, but the test pins less than the full requirement text (INV-B). **None is a correctness lie**; none is feature work. Three were reframed in-matrix already (SR-03 6-case, EXT-07, EXT-14). The rest are filed here rather than reframed/strengthened in-item (matrix-truth budget; test-authoring, not reconciliation). Each carries its disposition; fix per row when the owning component is next touched.

**Reframe REQ text to what the test checks (cheap, byte-safe):**
- **REQ-CA-01** — test uses the 6-member enum set (incl. transient `EXPOSE_CHAIN_TENTATIVE`); INV-F/no-tentative-survives is REQ-CA-10's job, not pinned here. Reframe: "assign each attr exactly one enum member."
- **REQ-CA-06** — LITERAL assignment path never exercised (only FORMULA/EXPOSE_ALIAS). Reframe to those two, note LITERAL is design-attr/entry-point path.
- **REQ-AST-03** — cited test pins only the FCE<OE<FRE ordering clause, not literal-before-catch-all (that's REQ-AST-08). Reframe to the ordering clause.
- **REQ-DM-03** — compares field-NAME sets only (not type/optionality). Reframe "field name lists," or strengthen.
- **REQ-DM-04** — checks source file only, not parent class. Reframe "importable from documented source file," or strengthen.
- **REQ-OSR-03** — template-fidelity only (both sides from same graph), not SysML-source match. Reframe or add the output-registry PQN test to the citation.
- **REQ-SR-06** — grep-only static, no behavioral regen. Reframe to "all module types route through the single `_generate_stencils()`."
- **REQ-SNAP-18** — vacuous grep: `generation_timestamp` token exists nowhere in repo; the template-var premise is stale (var removed). Reframe to a regression guard.
- **REQ-PMM-04** — asserts valid non-empty Python, not byte-identity vs pre-migration baseline (the doc's `diff -r` gate ran once at cutover). Reframe to the testable property.
- **REQ-PMM-05** — phased-sequence (add/create/deprecate/remove) is process, not a testable module property; test pins coexistence only. Reframe to importable-variants + unchanged-fields.
- **REQ-AS-02** — Strategy-1-before-2 short-circuit shown only via a disjoint fixture (no dual-match partdef); precedence inferred. Reframe or add a dual-match case.

**Strengthen test (needs a new/expanded assertion; risks touching baselines — do under byte-identity gate):**
- **REQ-EC-04** — tests call `python_ast.parse` themselves on the compiler's output; the compiler's internal parse-and-raise gate (`expression_compiler.py:217-223`) is unpinned (delete it and every EC-04 test still passes). Add a case that forces invalid emitted Python and asserts `CompilationError`.
- **REQ-AS-06** — resolve-before-register gate wrapped in `if result is not None:` + `resolved_count>0` floor; 40 of 41 aliases could be unresolvable and pass. Assert every registered redefinition alias resolves.
- **REQ-EPC-07** — purity test deep-compares only 2 of 5 inputs. Deep-compare all five against fresh copies.
- **REQ-ORCH-05** — `len(scoped)>=len(expr)` aggregate count; one over-producing expr masks another scoping to zero. Assert every expression id appears in the scoped output.
- **REQ-ORCH-02** — source call-order only; the in-place binding_type mutation-visible-to-backtracker half is unpinned. Assert a virtual binding's `binding_type` is actually mutated.
- **REQ-ORCH-06** — source-order proof only; the "computation_graph is SSOT / generation boundary" half is really pinned under REQ-PIPE-07's `TestGenerationBoundary`. Re-cite or assert `ctx.computation_graph` identity.
- **REQ-OR-02** — despite its name (`test_no_single_resolve_method`) never asserts `not hasattr(registry, "resolve")`; omits the 4th lookup `scoped_alias_lookup`. Add the negative assertion.
- **REQ-OR-03** — wraps `caplog.at_level(WARNING)` but never asserts a warning record for the first-wins alias collision. Assert the record.
- **REQ-PGD-03** — "one group per file" pinned only as `>=` lower bound; over-grouping passes. Assert `== distinct source-file count`.
- **REQ-REG-06** — circular expected-set: derives expected types from the SUT helper `_collect_exit_point_primitive_types`. Derive the expected set independently from the graph.
- **REQ-CA-07** — self-reference exclusion vacuous (no self-referencing fixture; checks a downstream string). Add an `x = x + 1` fixture and assert on `input_names` directly.
- **REQ-CA-11** — pins only the registered→silent case, not unregistered→warns-naming-real-cause. Add the unregistered shape-A case.
- **REQ-EPC-05** — "exactly one ParameterGroup" — no cross-group uniqueness check. Add it.
- **REQ-BASE-04** — parametrizes 4 models but 10 baseline dirs have `computation_graph.json`. Glob all.
- **REQ-DM-09** — pins the 4 field names, not serialization-non-exclusion / INV-5 sort / INV-3 validation. Strengthen; also its `test_graph_assembly.py` citation has no REQ-DM-09-marked method (docstring only).
- **REQ-SR-05** — backup mechanism tested in isolation, not the "before every regen/upgrade" ordering. Drive the regen path.
- **REQ-PMM-02** — pins ModuleInput desc/default + ModuleOutput desc/unit, but not `ModuleOutput.default_value` (a real field). Add it.

**Fix citation only (traceability — behavior IS pinned, under a different REQ/test):**
- **REQ-BASE-01** — the real full-JSON baseline compare lives in `test_graph_assembly.py::TestBaselineComparison` (marked REQ-GA-01); the cited `test_baselines.py` only checks 3 keys exist. Re-cite/mark.
- **REQ-NC-08** — FORMULA module_eqn/channel leg pinned by `test_formula_quoted_owner.py` (not cited). Add it.
- **REQ-VBR-10** — the "else leave it as-is" clause is pinned by `test_self_named_binding_trap.py::test_self_named_binding_resolves_to_own_param` (not cited). Add it.
- **REQ-HR-08** — the "`part redefines` keeps all RHS types" leg is pinned by `test_virtual_binding_rewrite.py::TestChainOverrideFixtureCoverage` (marked REQ-VBR-04). Add a `# REQ-HR-08` marker there.
- **REQ-PY-08 / REQ-DM-09** — cited methods carry the REQ only in a docstring, no `@pytest.mark.req`; matrix tooling may not bind them.

**Residue (register discipline — NOT swept, named with count):** the sweep examined ~167 of the ~213 qualifying strong-word/diagnostic/count rows. ~46 qualifying rows were not independently deep-read this pass (primarily the EPC diagnostics, LVP literal-propagation, and GA topo-sort internals judged adequate on their family reader's spot-check but not line-by-line). These are **not** asserted swept — a future pass completes them. No silent truncation.

### [ITEM5-SWEEP-RESIDUE-OVERFLOW] D7 sweep completion — 21 rows read-spot-checked, not line-by-line deep-read — P3, test-coverage / matrix-honesty

**Filed by TRUTH-DEBT Item 5 (matrix-sweep-residue), 2026-07-08.**

Step 5.0's D7 qualifier grep (`SHALL|ALL|every|never|exactly|warn|fire|count`, case-insensitive) across all 259 current matrix rows returns 232 qualifying rows. Subtracting the ~167 the Item-7 register already swept and the 33 rows this item dispositioned in Phases 1-4 (17 strengthen + 11 reframe + 5 cite) leaves **32 rows** as the concrete residue (the spec's ~46 estimate included rows this item's own Phase 2 work re-verified/absorbed).

Of those 32, the 23 in the three named families (EPC 8, GA 8, LVP 9, minus REQ-EPC-05/07 already strengthened in Phase 2 = 21 unread here) were spot-checked (not individually line-by-line deep-read): REQ-GA-04's `TestNoSelfDependency` and REQ-LVP-04's LocalTerm-fallback assertions both read as real, non-vacuous checks matching their row text on inspection. No correctness lie or feature gap was found in the spot-check, consistent with the Item-7 register's finding that every prior deep-read row was PASS-pins-narrower, never a lie.

**Stopping rule invoked:** the D7 stopping rule (0 new findings in 40 consecutive rows after the first 60) was not reached on row-count grounds — this pass stopped short of it, at the item's remaining implementation budget, having read 2 of 21 representative rows in the named families (GA-04, LVP-04) plus the row-text/citation check for all 21 during Step 5.0's grep pass. This is an **honest budget-bound stop**, not a claim the D7 heuristic's row-count threshold was hit -- named separately per the plan's risk-management section (an unread residual vs. a read-but-too-big-to-fix residual are both named, separately).

**Residue, named exactly:**
- **21 rows** in EPC/GA/LVP families not individually deep-read beyond the spot-check above: REQ-EPC-01, -02, -03, -04, -06, -08; REQ-GA-01, -02, -03, -05, -06, -07, -08; REQ-LVP-01, -02, -03, -05, -06, -07, -08, -09.
- **11 rows** elsewhere in the qualifying set (the "~21 spread across other families" the spec named) not enumerated by REQ id in this filing -- reconstructing the exact list requires re-running the Step 5.0 grep minus the 167+33+21 already accounted for; left as a precise follow-on rather than guessed here.

**Scope for the follow-on:** re-run the Step 5.0 grep, subtract this item's full disposition (33 dispositioned + 21 spot-checked here), deep-read the remainder under a fresh D7 budget, land cheap dispositions (reframe/cite) inline, re-file only genuine budget-exceeding strengthens.

### [SANITIZER-MERGE] Two-sanitizer consolidation (D1-F2) — P3, load-bearing divergence

**Filed by PIPELINE-TRUTH Item 8 (D1-F2), 2026-07-06.** `core.sanitize_name` (`core/qualified_names.py:13`) vs `expression_compiler._sanitize_name` (`extraction/expression_compiler.py:167`) diverge deliberately: the compiler drops the reserved-word suffix `core.sanitize_name` applies, and the FORMULA REFERENCE wire matches *by construction* on that difference. **Assessed → FILE (not merged):** a naive shared core risks breaking the FORMULA REFERENCE match, and the byte-identity discipline makes a speculative merge high-risk for near-zero gain. Implement a shared core only if it falls out safely with the byte-identity gate green. Not forced in a cleanup pass.

### [SC11-IMPORT-REWRITE] AST-based import rewrite (D1-F1 / SC-11) — P3, not small

**Filed by PIPELINE-TRUTH Item 8 (§G), 2026-07-06.** `identifier-sanitization/close-out.md:31` claimed the AST-based import rewrite (substring, first-match) was a "filed follow-up" — it was filed **nowhere**; the false claim is now corrected in that close-out. **Assessed → FILE:** the size judgment is *not small*. Compared against the registry alias-rewrite's no-not-found branch (a D3 hygiene site, a 1–2-site local change), a correct substring/first-match import rewrite is a cross-module AST rework. Build it as its own scoped change, not opportunistically. This entry is the SC-11 assessment-verdict artifact.

- **[ANON-ELIGIBLE-KEY] Verify multiple anonymous executable assertions — P3 `[AGENT]`.** The July defect described a shared `"<anonymous>"` key in retired lowering. The exact route now derives predicate source keys from definition metadata, inline predicate identity, or exact usage identity (`src/sysml_codegen/elaboration/elaborate.py`, `elaboration/project.py`, `generation/constraint_catalog.py`). Confirm which anonymous executable forms are supported, then establish independent compilation/evaluation for distinct anonymous bodies. The old report does not prove a current key collision; this remains a support/evidence question.

- **[CATALOG-FINGERPRINT-ROUTE-PORTABILITY] The constraint catalog fingerprint is not portable across the live and snapshot routes — P3 `[AGENT]`, unowned, pre-existing.** `ConstraintCatalog.recomputed_fingerprint` (`src/sysml_codegen/resolution/models.py:597-622`) hashes the full model dump of `usage_records`, and those rows carry `source_file`. The live route records paths relative to the invocation root (`tests/fixtures/catf_mfe_gated/…`); the snapshot route records `root-0/…`. Same sealed graph, same semantics, different paths, **different fingerprint** — and the generated aggregator bakes it in as `CATALOG_FINGERPRINT`, a runtime coherence check, so two packages generated from one graph via different routes ship different values. It also propagates into the model contract's `semantic_fingerprint`. **Measured** (CONSTRAINT-SEMANTICS Item 5 Phase 6). On `catf_mfe_gated`, live `4edaf85e8c6737e5fb55a7c07cf2beabf8a3112ec5539d1267a3648bda7c022c` versus snapshot `65083fb7e1350f6862974428c7bf1f6b960bc6b76011583b42d62c7848f33b25`; normalising the source-root prefix in every provenance comment leaves this as the **only** substantive difference between the two packages. **Reproduces on the untouched frozen twin `catf_mfe_d5`** (live `39d02855…027f`, snapshot `beaaa339…c91ca`), so it is pre-existing and not caused by Item 5. It does **not** reproduce on `constraint_domain_satisfy_calc_def`, whose model is a single flat `model.sysml` — both routes agree there (`9b93a157…5254`). That is why no existing fixture caught it: the split needs a nested source layout. In-place and relocated snapshot reads agree with each other exactly, so only the live-versus-snapshot pair diverges. Fix direction: make the hashed identity route-independent (relative-to-model-root paths, or exclude `source_file` from the fingerprint and pin it elsewhere).

---

- **[PROFILE-COMPILER-PARITY] Characterize current profile → compiler → generated-runtime agreement — P1 `[AGENT]`.** The old v2 defect premise is superseded: the current compiler accepts numeric quantity references/arithmetic and explicitly rejects equality (`src/sysml_codegen/generation/predicate_compiler.py`; `tests/unit/test_predicate_compiler.py`). Re-derive the admitted/blocked category matrix against current immutable companion/codegen/runtime artifacts before changing implementation. The retained scope is complete admission/compilation/execution agreement; the old research does not establish a current mismatch.

- **[EXIT-PIN-SEAM] Decide the exit-selection seam — P3.** `src/sysml_codegen/generation/pipeline.py:257` carries `selected_channels`/`pin_report_channels` used only by `tests/unit/test_exit_pin.py` (production always no-op; disclosed in design-review and docstring). Either real exit selection owns this API or the test proves capture-everything behavior without dormant production branches.

- **[INLINE-PREDICATE-MARKER-DROP] `@inapplicable:` markers on inline-predicate constraints never reach the domain — P3 `[AGENT]`, unowned.** SysIDE drops a `doc` comment inside an inline-predicate constraint body (`constraint X { doc /* … */ <predicate> }`), so an `@inapplicable:` marker written on that shape is silently discarded. Measured in CONSTRAINT-SEMANTICS Item 5 Phase 1 on the CATF derivative's five part-definition guards: **5 markers written in source, 0 carried on the domain**, with the markers in the exact form and first-line placement the Item 2 fixtures pin. Every Item 2 fixture that carries a working marker is bindings-form, so the gap was never exercised. Already named as rule 3 of `tests/conformance/test_constraint_population_oracle.py`, which fails loudly when it happens — this entry is for closing the gap, not for detecting it. Until it closes, an inapplicability disposition on an inline-predicate usage has to be recorded in PROVENANCE instead of in source. **Closing this defect is what fires the B1–B5 marker migration** — move the five `@inapplicable:` markers out of `tests/fixtures/catf_mfe_gated/PROVENANCE.md` §3b and into source, and retire the workaround. Epic Item 9 ran on 2026-08-13 with that criterion recorded as a conditional that did not fire, precisely because this entry is still open; it is not Item 9 that retires the workaround.

- **[CATF-ACCEPTANCE-LANE-MANUAL] The CATF feasibility-rejection lane is recorded evidence without a committed regression gate — P3 `[AGENT]`, unowned.** Item 5 coverage is gated by `tests/unit/test_coverage_ledger_agreement.py`. Its generate → seal → load → execute → policy → durable-record rejection was a recorded manual acceptance run; its archived harness names historical artifact roots. The former unmerged-TEAx explanation is obsolete. Decide whether to keep this lane explicitly manual or add a committed artifact-bound runtime regression for the current model.

## Study Layer (WRAP-SPLIT Item 3 follow-ups)

Filed by the audit fix pass of WRAP-SPLIT Item 3 (study-layer-to-codegen, branch `study-layer-to-codegen`), 2026-10-12, on the orchestrator's brief, because the item folder is deleted at close (audit F2). The audit is `01990a5:.project/active/study-layer-to-codegen/audit.md`; `evidence/` paths below are in that commit's item folder.

### [STUDY-RECORD-RESUME] A resume path for a study record stopped at § 17 — unscheduled `[AGENT]`

The shipped runbook (`src/sysml_codegen/assets/skills/run-study/runbook.md`) has a § 17 stop rule but does not say how a stopped record resumes. Item 3's dry run hit it: the agent obeyed record immutability and started a new study id, which is defensible but costly (dry-run finding F-DR1, `evidence/dry-run/run-20261012/RESULT.md:36`). The text came over unchanged from fusion-tea's runbook, and changing the record lifecycle was outside Item 3's closed list. Source: audit F2 and its F-DR1 disposition.

### [STUDY-ROUTE-POINT-RUNNER] The route contract leaves the point runner open — unscheduled, the owner's or orchestrator's call `[AGENT]`

The shipped contract for a package's route names `execute_baseline` and then "whatever runs the study's points" (`runbook.md:261`). A route that fixes its grid in code therefore satisfies the contract and still defeats step 7's rule that the window is chosen after the oracle scan (`runbook.md:83`). Requiring the point runner to take step 7's window would change study semantics, so the decision is not an implementer's. This restates dry-run finding F-DR2, whose recorded cause was wrong: the neutral fixture's route already has a points entry, `run_points` (`tests/fixtures/study_station/studies/study_route.py:44`); the dry run fixed its grid because its brief named only `execute_baseline` and `run_grid` (`evidence/dry-run/brief.md:29`). Source: audit F4.

### [INTEGRATE-CALLER-ERROR-AS-SEAM-FAULT] `integrate` reports two caller mistakes as `seam-internal-error` — unscheduled `[AGENT]`, inherited

Both paths fail closed, but each says "the seam broke" for a caller's error:

- A `--census-file` that is valid JSON of the wrong shape, or lacks `derived_against_semantic_fingerprint`, raises `KeyError` or `TypeError` in gate 4 (`src/sysml_codegen/study/integrate.py:1206-1221`). The catch-all at `:1621` returns `seam-internal-error`, exit 2.
- A baseline result without `executed_under.store_id` raises `KeyError` at `:1298`, which escapes the `ToolError`-only handler at `:1350`, also exit 2.

Both are byte-faithful to fusion-tea `b06585709`, so the fix is a behaviour change and was kept out of the move. The audit's proposed mapping: gate 4 `input-invalid` for the census, gate 7 `could_not_run` for the baseline result. The `index` mypy override on `integrate` is what hides them (see the next item). Source: audit F5.

### [VERIFY-MISSING-STORE-TRACEBACK] `verify` crashes on a missing store instead of refusing — unscheduled `[AGENT]`, inherited

Given a `--store` path that does not exist, `verify` lets teax's store open raise an uncaught `sqlite3.OperationalError` rather than refusing with a `ToolError` that names the path. It still fails closed (non-zero exit, no summary written), but the message is a traceback. Found by the Item 3 rehearsal's step 8b (fusion-tea record `20260929-magnet-material-comparison`, whose stores are not committed). Byte-faithful to fusion-tea `b06585709`, so the fix is a behaviour change kept out of the move: check the store path exists before opening it, and refuse naming it.

### [READ-COVERAGE-STALE-BYTECODE] Gate 7 refuses a route whose bytecode cache is stale — unscheduled `[AGENT]`, inherited

When a route module's `__pycache__/*.pyc` is older than its source, the observed run recompiles it, and `read_coverage` refuses with `dependency changed after read: …/__pycache__/study_route.cpython-312.pyc`. The next run passes, because the cache is then fresh. fusion-tea's adoption hit this on the first gate-7 run after step 5 rewrote the route imports. fusion-tea's original observer refuses the same way after `touch study_route.py` (agentic-mbse `.project/completed/20261012_study-layer-to-codegen/evidence/adoption-20261012.md`). It fails closed, but the message points at a cache rather than the route. A fix could treat a rewritten `.pyc` of an observed source as that source's read, or run the route with `PYTHONDONTWRITEBYTECODE`. Either is a behaviour change.

### [STUDY-PORTED-MYPY-OVERRIDES] Typing debt in the eight ported study modules — P3 `[AGENT]`

`pyproject.toml`'s `[[tool.mypy.overrides]]` blocks relax checking for the eight modules ported byte-faithfully from fusion-tea (`common`, `identity`, `indicators`, `integrate`, `manifest`, `preflight`, `read_coverage`, `verify`). The audit's strict probe (`--check-untyped-defs --disallow-untyped-defs`, 53 errors in 6 files) found what each hides:

- `disallow_untyped_defs = false` (all eight): 29 untyped defs (read_coverage 12, verify 12, preflight 3, integrate 2). Looseness only; checking their bodies found nothing beyond the codes below.
- `identity` `attr-defined`: `.get` on `object` at `:262`, unreachable because the contract is validated first.
- `indicators` `arg-type`, `no-any-return`: `arg-type` at `:617` (a `None` key, guarded at `:618`) and `:903`; `no-any-return` at `:134`. Looseness.
- `integrate` `index`, `no-any-return`: `:1210-1221` and `:1298` hide the two real misreports in [INTEGRATE-CALLER-ERROR-AS-SEAM-FAULT]; `:1169` and `:1388-1389` are looseness over validated documents.
- `manifest` `no-any-return`: `:402`, over a schema-validated manifest.
- `preflight` `arg-type`, `assignment`, `attr-defined`: seven guarded `arg-type` sites at `:383-417`, `assignment` at `:313`, and `attr-defined` at `:126` and `:136`. The last two are real but cosmetic: a non-object `model_contract.json` gives an `AttributeError` traceback, still exit 1 with no document.
- `verify` `index`: `:507`, after the contract is asserted at `:500`.
- `ignore_missing_imports` for `simkit` and `yaml`: no stubs.

Typing the modules is a byte change, so it belongs after fusion-tea adopts the moved layer. The `no-any-return` sites were not re-probed by the audit; their list rests on Item 3's Phase 1 mypy run. Source: audit § Code integrity, "The mypy overrides, named".

### [STUDY-CHECK-RECORD] Ship the record checker as `sysml-codegen study check-record` — unscheduled `[AGENT]`

Item 3 shipped no record checker (design DD12). The installed runbook's steps 14 and 15 carry **Check:** lines the executor runs, and the dry run's evidence script `evidence/dry-run/check_record.py` ran five checks over the committed record and agreed with them. Shipping that script as a `study` subcommand gives a target one command for the same checks. Rejected at design time: shipping it inside Item 3, and an installed pytest template. Source: design DD12, review S6.

### [STUDY-PORTED-SMELLS] Smells kept in the ported study modules — unscheduled `[AGENT]`, inherited

Design DD19 removed the `if __package__` path inserts and kept these, each byte-faithful to fusion-tea `b06585709`:

- argparse `prog="<tool>.py"` in `indicators.py:927`, `preflight.py:472`, `verify.py:585` and `integrate.py:408`, so usage lines name a file the target never runs instead of `sysml-codegen study <tool>`;
- `indicators.write_atomically` (`indicators.py:907`), a local atomic-write helper;
- `integrate.py`'s size (1,663 lines);
- gate 4's fixed `*.snapshot.json` glob beside the models root (`integrate.py:1132`). The follow-up is an explicit `--snapshot` flag.

`read_coverage.py`'s untyped style is [STUDY-PORTED-MYPY-OVERRIDES]. Each fix is a byte change, so it belongs after fusion-tea adopts the moved layer. Source: design DD19, review S7.

### [STUDY-GLUE-LEDGER-SEMANTICS] Is a non-empty glue ledger a model-development finding? — the owner's call `[AGENT]`

The shipped runbook treats a non-empty glue ledger as a scoped disclosure (`runbook.md:94`; `record-template.md:126-128`). It treats an axis the model does not resist as a model-development finding (`runbook.md:56`). The owner's concept says glue is temporary and "studies will not need glue" (run-study concept, amended 2026-08-18), and P-004 calls a harness-injected value "a massive, disgusting smell". Not a regression: the text came over unchanged (read-through RB-14). Making it a finding changes study semantics, so the owner decides. Source: Item 3 product-lens audit-F6.

## Historical Scope Question

### [HIERARCHICAL-OUTPUT] Recover original scope — unscheduled

The original item folder is absent and its scope is not independently recovered. This remains an unresolved historical-scope question.

Closed and superseded backlog entries are archived at `a082db22a120f5fa420312f96881a59b71166cd5:.project/backlog/BACKLOG.md`. Current completion summaries are in [CURRENT_WORK](../CURRENT_WORK.md).
