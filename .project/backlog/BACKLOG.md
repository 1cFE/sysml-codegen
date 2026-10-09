# Product Backlog

**Updated:** 2026-10-09

Current work and independently justified follow-ons. Owner-originated rulings retain their source authority; agent proposals remain challengeable. Historical closed work is available through Git and durable registers.

## Active Work

| Item | Status | Authority and next boundary |
|------|--------|-----------------------------|
| [ELABORATE-FIRST Item 8](epic_elaborate_first_architecture.md) | Bounded cleanup closed; Item 8 remains open | One completion authority; source-identity evidence bounds and Item 8 audit/close remain. |
| [GAP-CLOSE](epic_gap_close.md) | Local scope certified; F1 runtime leg closed 2026-07-20 | The old full-suite PR-wave evidence gap remains historical and is not retroactively proved by today's tests. |

## Capabilities and Diagnostics

### [INDEXED-ELEMENT-EXPRESSION-SUPPORT] Valid indexed element references — unscheduled `[AGENT]`

SysIDE preserves an authored index; codegen currently refuses before graph construction with `SI_INDEXED_SOURCE_UNSUPPORTED`. Adding execution semantics needs a separate scoped capability. Earlier agent filings proposed P1 and P3; they are consolidated here without assigning an owner priority. Sources: parser Phase-4 design D5/D7/D8 (Git history), `tests/fixtures/indexed_expression_source/model.sysml`, and `tests/conformance/test_expression_evidence_integrity.py`.

### [OUTPUT-ALIAS-DUPLICATE-SOURCE-SILENCE] Multiple aliases for one source — unscheduled `[AGENT]`

Aliases survive in `graph.output_aliases`; generation currently selects the first alias for the single file per exit channel. Decide whether to emit additional files or diagnose the second alias in its own item. Earlier P1/P3 filings are consolidated without assigning an owner priority. Evidence: `elaboration/project.py`, `generation/pipeline.py`, and `tests/unit/test_exit_point_aliases.py`. The earlier extraction-loss premise is superseded.

### [POSITIONAL-FORMAL-REDEFINITION] Improve skipped-formal diagnostics — P1, unowned `[AGENT]`

Current elaboration follows parser redefinition identity. The August 21 filing's name-matching/positional-codegen premise is superseded; it does not establish a binding defect. A clearer refusal should identify the skipped formal and corrective declaration order. Customer examples and the original four sites remain in the August 21 backlog revision and `models/stellarator_migration_ledger.md` in fusion-tea; `tests/fixtures/modeled_default_fidelity/PROVENANCE.md` records parser positional behavior.

- **[SCALAR-FUNCTION-VOCABULARY] Add scalar invocation functions as a separately owned capability — P2 `[OWNER, 2026-08-18]`.** Supporting `min`, `max`, or other scalar functions is not part of the stop-parser remediation; its declaration/compilation semantics remain separately owned. Today every invocation except the exact standard-library `NumericalFunctions::sum` declaration refuses before graph construction with `SI_EXPRESSION_SOURCE_UNSUPPORTED`, naming the authored expression and its source location. A future capability must define and test each admitted function explicitly. **Motivating case (filed 2026-08-21, fusion-tea stellarator-model-migration):** the stellarator model authored six invocations -- `RealFunctions::sqrt` in `'DT Fusion Power'` (`mfe_plasma_scaling.sysml`, the Bosch-Hale peak reactivity) and `RealFunctions::max` ×3, `min`, `floor` in `'Levelized Replacement Cost'` (`mfe_account_costs.sysml`, jnp.clip and ceil written as identities). Both calcs were made opaque manual interfaces so the pinned route generates (fusion-tea `models/stellarator_migration_ledger.md`, Class B rows, Appendix A/B hold the verbatim bodies); fusion-tea carries a revert row to restore them when this capability lands. The wanted vocabulary for that model is exactly `sqrt`, `max`, `min`, `floor`.

- **[DEEP-QUALIFIED-OUTPUT-WIRING] Wire a deep qualified reference to its concrete calculation output — P2 `[AGENT]`.** The authored shape is `measurement_system::station::array::sensor::core::metric_value` in `tests/fixtures/deep_cross_scope_probe/design.sysml`. The current contract is `SI_OCCURRENCE_MISSING` because no producer exists in the consumer domain, with no captured snapshot. Transition A2 owns that refusal. Implement exact producer wiring as a separate capability; do not restore the removed globally-sole substitution.

### [DIAGNOSTIC-PROVENANCE-BY-CONSTRUCTION] Internal-defect diagnostic totality — separate follow-up

The parser predecessor closed by owner direction with its historical `Needs Work` audit preserved. Model-caused reference/location fixes shipped; independently complete internal-defect provenance remains separate. Source: parser-close/shipment Git records, product-lens final dispositions, and `.project/adr/0004-derive-occurrences-from-exact-evidence-or-refuse.md`.

## Retained Model and Assurance Work

### [SNAPSHOT-CODEC-AND-DUP-CONSOLIDATION] Digest-sensitive consolidations deferred from REPO-CLEANUP Move C — P3, unowned (filed 2026-08-25)

Move C deleted the dead lanes; three *duplication* findings from the same inventory (`.project/research/20260820-201945_line-count-anatomy-and-salvageability.md` §5) are consolidations whose cost is a digest or byte change, so they were filed rather than done:

- The hand-written snapshot codec (`snapshot/instance_graph.py`, ~550 collapsible lines of field-copying) — needs dataclass→Pydantic, discriminators on three untagged unions, an `instance-graph/v4` schema bump, and 22 licensed fixture re-captures.
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
- Re-run of the Item 5 Phase 6 acceptance under the corrected model (coverage unaffected; headline flips back; the SC-5 candidate labeling reverts to the natural direction).

**Evidence home:** Item 5's verification record and the 6-D ruling (`.project/completed/20260813_catf-constraint-policy-acceptance/`); acceptance record states the authored point is gate-infeasible under the model as authored.

---

### [CALCDEF-GATE-IMPLEMENTATION] Implement calculation-definition constraint gates (graph v4 + catalog 4.0.0) — P1, unowned, awaiting owner authorization (filed at owner direction, 2026-08-13)

**What it is:** the production implementation of the capability CONSTRAINT-SEMANTICS Item 6 designed. One asserted constraint owned by a calculation definition expands into one concrete check per calculation occurrence, with usage-level coverage and occurrence-level results joined through exact graph identity. Today such a usage ends as `non_reaching / owner_kind_unattachable`; nothing executes.

**Authorization status `[OWNER 2026-08-13]`:** **not authorized in the CONSTRAINT-SEMANTICS epic.** The owner ruled at Item 6's close that this is a separate, later decision. It is unowned and unscheduled. It competes for the next slot with `[CATF-CRYO-HEAT-LEAK-COEFFICIENT]` (P1) and the paused ELABORATE-FIRST Item 7 resumption. **No agent may start it without a new owner ruling.**

**Estimate:** 7–9 working days, cross-repository (codegen + TEAx).

**Plan of record:** `.project/completed/20260813_calcdef-constraint-gate-design/implementation-item.md` — file-level scope, dependency pins, phase order, and customer-shaped acceptance tests, revised against three rounds of independent design review (F1–F8). Its companions are `spec.md`, `design.md`, `design-review.md`, and `probes/findings.md` in the same archived folder. The spec's production-acceptance boxes are deliberately still open: they are this item's, not Item 6's.

**Start gate — SATISFIED, and here is why it mattered:** no lawful start SHA existed until Item 8's unit-lane characterizations landed, because the constraint-formal and computed-attribute unit lanes carried `unit=None` by construction and would have refused valid models. They landed at **`62a07e5c870158672eb100f1cba73adfe4c9df28`**. The gate dissolves; the only remaining block is owner authorization. Evidence bundle: `.project/completed/20260813_unit-lane-port-metadata/verification.md`.

**Carried guards and consequences:**

- **SC8 — re-derive, never reuse.** The future graph-v4 snapshot record must derive its own then-current tracked path set from Git and prove equality against that. It may **not** reuse Item 8's 23 paths or the older 15-path subset; those are dated evidence, not durable scope.
- **TEAx re-vendor.** This work ships **catalog 4.0.0**, so TEAx must be re-vendored against a catalog-4 producer candidate. TEAx stays on `constraint-semantics-item3` @ `5b70ae9` until one exists.
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

### [MATRIX-EPIC-SURFACE-ROWS] Add verification-matrix rows for the three uncovered lifecycle surfaces — P3 `[OWNER]` (ticketed 2026-07-24)

Owner directed filing this as a ticket at the docs-lifecycle-sync wrap. The lifecycle epic added tested behaviors with no matrix rows; docs-lifecycle-sync Phase 4 added only the required portability pair (REQ-SNAP-21/22) and registered these three as candidates (`.project/completed/20260724_docs-lifecycle-sync/inventory.md`, MG1–MG3):

1. **Producer resolution / completeness** — the unified ladder (`resolution/producer_resolution.py`, `resolve_producer`, KEY_FORMS, TerminalPolicy) and `producer_completeness.py`. Reference doc exists (`04-producer-resolution.md`); pinning tests exist (Item 2's suite, e.g. `test_producer_completeness_acceptance.py`) — verify which tests pin which claim before citing (no aspirational citations).
2. **Catalog schema 2.0.0** — `CATALOG_SCHEMA_VERSION` (`contracts/versions.py:18`) and the catalog contract (`test_catalog_schema_version.py`, `test_catalog_definition_join.py`).
3. **Trust manifest / bootstrap** — `contracts/manifest.py` and the trust-anchor behavior (Item 7's tests).

Discipline: matrix recount per memory `verification-matrix-drift-modes` (index totals + per-family counts, not just the summary block); current baseline **288 rows / 156 PASS / 34 families** after the ELABORATE-FIRST step-4 pass closed all UNTESTED rows and filed the REQ-CS family (2026-08-14).

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

- **[ANON-ELIGIBLE-KEY] Anonymous executable assertions share one catalog compile key — P3 `[AGENT]` (filed 2026-07-18, GAP-CLOSE Item 2 non-goal).** Eligible anonymous assertions all get `"<anonymous>"` as their `predicate_definition_key`, so compile-once grouping cannot distinguish them (pre-existing; distinct from the F5 exclusion-path collision GAP-CLOSE fixes). Needs an owner ruling first: are anonymous *executable* assertions a supported authoring form? (Gap review Open Question 2.) Evidence: `.project/research/20260718-123558_constraint-expression-final-gap-review.md` (F5) and the verification record's F5 sub-question (c).

- **[CATALOG-FINGERPRINT-ROUTE-PORTABILITY] The constraint catalog fingerprint is not portable across the live and snapshot routes — P3 `[AGENT]`, unowned, pre-existing.** `ConstraintCatalog.recomputed_fingerprint` (`src/sysml_codegen/resolution/models.py:597-622`) hashes the full model dump of `usage_records`, and those rows carry `source_file`. The live route records paths relative to the invocation root (`tests/fixtures/catf_mfe_gated/…`); the snapshot route records `root-0/…`. Same sealed graph, same semantics, different paths, **different fingerprint** — and the generated aggregator bakes it in as `CATALOG_FINGERPRINT`, a runtime coherence check, so two packages generated from one graph via different routes ship different values. It also propagates into the model contract's `semantic_fingerprint`. **Measured** (CONSTRAINT-SEMANTICS Item 5 Phase 6). On `catf_mfe_gated`, live `4edaf85e8c6737e5fb55a7c07cf2beabf8a3112ec5539d1267a3648bda7c022c` versus snapshot `65083fb7e1350f6862974428c7bf1f6b960bc6b76011583b42d62c7848f33b25`; normalising the source-root prefix in every provenance comment leaves this as the **only** substantive difference between the two packages. **Reproduces on the untouched frozen twin `catf_mfe_d5`** (live `39d02855…027f`, snapshot `beaaa339…c91ca`), so it is pre-existing and not caused by Item 5. It does **not** reproduce on `constraint_domain_satisfy_calc_def`, whose model is a single flat `model.sysml` — both routes agree there (`9b93a157…5254`). That is why no existing fixture caught it: the split needs a nested source layout. In-place and relocated snapshot reads agree with each other exactly, so only the live-versus-snapshot pair diverges. Fix direction: make the hashed identity route-independent (relative-to-model-root paths, or exclude `source_file` from the fingerprint and pin it elsewhere).

---

- **[PROFILE-COMPILER-PARITY] Make executable-profile admission total for predicate compilation — P1 `[AGENT]`.** The partial cure handles unary plus and literal Boolean/string/integer/synthetic- enum equality, but exact companion profile v2 still admits quantity-reference ordering and arithmetic that `predicate_compiler.py` rejects. The generated path also remains float-only, so non-real feature inputs, defaults, observations, and production enum constants cannot preserve their admitted semantics. Resolve the contract conflict between expanded profile admission and the completed float-shaped generation design, reconcile every admitted operator/category pair, and add a matrix-driven profile-`ADMIT` → compile → generated-execution gate. Include blocked parity so the compiler cannot accept profile-blocked derivations such as integer exponentiation equality.

- **[EXIT-PIN-SEAM] Decide the exit-selection seam — P3.** `generation/pipeline.py:233-288` carries `selected_channels`/`pin_report_channels` used only by `test_exit_pin.py` (production always no-op; disclosed in design-review and docstring). Either real exit selection owns this API or the test proves capture-everything behavior without dormant production branches.

- **[INLINE-PREDICATE-MARKER-DROP] `@inapplicable:` markers on inline-predicate constraints never reach the domain — P3 `[AGENT]`, unowned.** SysIDE drops a `doc` comment inside an inline-predicate constraint body (`constraint X { doc /* … */ <predicate> }`), so an `@inapplicable:` marker written on that shape is silently discarded. Measured in CONSTRAINT-SEMANTICS Item 5 Phase 1 on the CATF derivative's five part-definition guards: **5 markers written in source, 0 carried on the domain**, with the markers in the exact form and first-line placement the Item 2 fixtures pin. Every Item 2 fixture that carries a working marker is bindings-form, so the gap was never exercised. Already named as rule 3 of `tests/conformance/test_constraint_population_oracle.py`, which fails loudly when it happens — this entry is for closing the gap, not for detecting it. Until it closes, an inapplicability disposition on an inline-predicate usage has to be recorded in PROVENANCE instead of in source. **Closing this defect is what fires the B1–B5 marker migration** — move the five `@inapplicable:` markers out of `tests/fixtures/catf_mfe_gated/PROVENANCE.md` §3b and into source, and retire the workaround. Epic Item 9 ran on 2026-08-13 with that criterion recorded as a conditional that did not fire, precisely because this entry is still open; it is not Item 9 that retires the workaround.

- **[CATF-ACCEPTANCE-LANE-MANUAL] The CATF end-to-end feasibility-rejection lane is a reproduced run, not a committed test — P3 `[AGENT]`, unowned.** Item 5's SC-5 has two halves. The coverage half is durably gated (population oracle by scan; `tests/unit/data/expected-coverage.md` drives `tests/unit/test_coverage_ledger_agreement.py`). The feasibility half — the authored CATF design point reaching `reject` through generate → seal → load → execute → policy → durable record — is recorded evidence reproducible from `probes/acceptance_run.py` in the archived item home, and nothing fails if it regresses. Deliberate at the time (the lane needs the TEAx checkout on `constraint-semantics-item3`, which is unmerged). Fix direction: mark the lane as intentionally manual in a named place, or file it as a licensed/marked test once the TEAx branch lands.

## Disposition References

These entries preserve reference targets; they are completion/retirement records, not active implementation requests.

- **[UNIT-SCRAPE-BYTE-OFFSET]** Resolved by owner-directed deletion of all three unit guessers, with parser-native value units retained. Authority: cleanup spec-review Resolution L2-2, 2026-10-08; public live/snapshot unit tests.
- **[SERIALIZE-NAN-SEAL]** Strict contract/input encoders and public non-finite refusal checks implemented. The public route already refused upstream; this encoder repair is additional defense, not proof an invalid public package previously shipped.
- **[EMIT-STEP-REGRESSION-GATE]** Implemented by the durable all-22 public package oracle and template/rendering mutation checks; candidate evidence is retained at `540826abd4cb55759fd80a731a65376e25ee8afa:.project/active/pr-readiness-cleanup/evidence.md`.
- **[CONSTRAINT-GATES-UNTAGGED]** Discharged at ELABORATE-FIRST cutover step 4 on 2026-08-14. REQ-CS records the retained gates; the Item-5 minting disposition is unchanged.
- **[ARTIFACT-MANIFEST-TESTS-HARD-FAIL]** Closed by owner-authorized verification-tool retirement in REPO-CLEANUP Move C, 2026-08-25.
- **[V11-DEAD-GATE-DOCS]** Closed by deletion of the dead gate and correction of its live references.
- **[NESTED-OCCURRENCE-OVERRIDE]** The old resolver mechanism is retired. Surviving occurrence behavior and diagnostic bounds are tracked by source-identity evidence and [ANCHORING-ARRAYED-DIAGNOSTIC].
- **[TRUTH-DEBT-INHERITED-FORMULA-COMPILE]** The legacy inherited-formula compiler is retired; current computed-attribute evidence uses exact elaboration.
- **[STALE-BASELINE-CLASS]** V5 extraction baseline mechanism retired; actual v6 snapshot freshness is checked in this cleanup.
- **[TRUTH-DEBT-IFE-PLANT-CHAIN-STALE]** The v5 classifier/snapshot mechanism is retired.
- **[GB-PARAMGROUPS-TYPING]** The old graph-builder surface is retired; current generation typing is repaired without relaxing mypy.
- **[DOTTED-LEAF-PART-BLIND]** The name-fallback alias mechanism is retired; exact source identity owns current resolution.
- **[ITEM7-F4-CUTOVER]** Discharged by later cutover/retirement; no old aggregation resolver remains to wire.
- **[ITEM7-MATRIX-TEST-GAPS]** Current source-identity/matrix evidence replaces the retired-row proof gap; any surviving partial evidence remains in the matrix.
- **[CONSTRAINT-FORM-PER-DIMENSION-COST]** Superseded by owner-directed unit-guesser removal; declaration comment labels no longer force duplicated dimension-specific forms.
- **[CONSTRAINT-ARCH-UNIFY]** The legacy resolver/lowering stack is retired; the original cross-stack unification proposal no longer describes current work. Codec/compiler follow-ons remain separately scoped above.
- **[GAP-CLOSE-F1-TEAX-NORMALIZATION]** Verified closed in merged TEAx `fa0e06a`, 2026-07-20; no new F1 implementation is pending.
- **[REPO-CLEANUP]** Complete and merged in PR #15. Historical rulings and replacement evidence remain in registers/ledger and Git.
- **generation-boundary** Delivered at `6523521`; it is not a February active feature.
- **new-pipeline-explainer** Built then purged at `507e838`; it is not current active work.
- **hierarchical-output** Its folder is absent and original scope is not independently recovered. This is an unscheduled historical-scope question, not a completed feature claim.

- **[CONSTRAINT-MODEL-INVARIANTS]** The old mutable lowered-record shape is retired; current catalog/receipt totality and assignment validators retain the live invariant. New defects need a current reproducer, not the old removed-model premise.
- **[CONTRACT-VERIFY-BOUNDARY]** Digest syntax, fingerprint derivation, hostile artifact paths, and symlink containment are covered by `tests/unit/test_verify_package.py`; the older missing-validation claim is superseded.
- **[INLINE-CONSTRAINT-WIRING]** The old fixture collides with a generated binding and is correctly refused publicly before mutation. Evidence: `tests/execution/test_constraint_verdicts_exact_route.py::test_a_binding_that_collides_with_a_generated_name_is_refused_at_generation`; it is not an unimplemented valid binding shape.
- **[V2-HTML-BUILD]** The explainer was added at `5be8276`, shipped at `385e163`, and purged at `507e838`; this is a historical delivered artifact, not active implementation.
- **[GOLDEN-BYPASSES-RUN-CODEGEN]** The new all-22 public package oracle covers the shipped route; the older zero-entry private-helper test retains its narrower component scope.
