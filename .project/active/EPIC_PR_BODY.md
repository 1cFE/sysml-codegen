## Summary

The UPSTREAM-FINDINGS epic runs the full SysML → codegen → teax pipeline against models **outside** our fixture corpus (fusion-tea's IFE/MFE set) for the first time, fixes the 11 de-risk findings that surfaced (SC-1–SC-11), and adds staged support for the plant idiom that gates fusion-tea's MFE epic. Twelve items, each carried spec → review → design → review → plan → implement → audit(PASS), one commit per stage.

**Three headlines:**

- **fusion-tea's `gamma → lcoe` edge now wires from generated output.** The cross-part binding that fusion-tea faked with a two-pass gamma-feedback workaround is present in the ComputationGraph from generated wiring alone: `hif_plant__lcoe_calc.driver_cost_constant` is fed by the real Meier channel `hif_plant_pkg__hif_plant__driver__meier_cost__gamma`, not a JSON param (Item 10, SC-5 stage 2).
- **V11 params-coverage — importable no longer means runnable.** A pipeline that would `KeyError` at load on an uncovered input now fails loudly and precisely at the generation boundary instead of shipping a latently-broken YAML. The committed catf_mfe fixture that shipped a dangling input is fixed (Item 7, SC-8; wired by Item 10).
- **Snapshot generation decouples the license.** `generate --from-snapshot` produces output matching live generation without a syside seat — the mitigation for the single-seat license that **expires 2026-08-06** with no grace period (Item 2, SC-9/SC-10).

The fixture corpus previously exercised none of the failing shapes, which is why 1,500+ conformance tests caught none of this. Every newly supported (or explicitly rejected) shape now lands with a real SysML fixture + snapshot, and its agentic-mbse guidance in lockstep.

## Quality gate (at HEAD)

- **pytest:** 1989 passed / 4 skipped / 5 xfailed
- **ruff src/:** 21 findings — the epic's starting baseline, pre-existing, none introduced
- **mypy src/:** 109 findings — same baseline, pre-existing, none introduced

## The 12 items

| # | Item | SC | What it does | Audit |
|---|------|-----|--------------|-------|
| 1 | Baseline Repair & Silent-Failure Diagnostics | SC-1/2/7 | Suite green at source (sort at graph construction); constraint-drop, EXPOSE_PURE name-drop, and zero-output calc all become loud diagnostics; dead constraint code removed | PASS¹ |
| 2 | Snapshot-Driven Generation | SC-9/10 | `--from-snapshot` + snapshot-capture CLI, versioned format with `compilation_results`; generation runs with no live license | PASS¹ |
| 3 | Return-Style & Bare-Parameter Extraction | SC-2 | Legal return-style / bare-`in` calc defs extract; anonymous return rejected (new V8) | PASS |
| 4 | Part-Usage Type Indexing | SC-3 | Retyped part usages instantiate their subtype's template calcs (FeatureTyping target over list position) | PASS |
| 5 | Identifier Sanitization | SC-4, SC-11 | Quoted SysML names produce valid, consistent Python everywhere — sanitized once at the `::`→`__` derivation boundary; SC-11 closed intended/documented/tested | PASS |
| 6 | Expression Reconstruction Fidelity | SC-6 | Literals render as values, branch ordering + KerML-precedence parens preserved; display-only invariant, zero valid-model churn | PASS¹ |
| 7 | Resolution Matcher Fixes & Warning Reconciliation | SC-8 | Two matcher bugs (quoted-owner QN, def-owned attr) fixed; **V11** params-coverage check fails loud on an uncovered wired input; benign per-binding noise demoted to DEBUG | PASS¹ |
| 8 | Plant-Idiom Conformance Fixtures | — | Closes the corpus blind spot: `wi014_toy` (byte-verbatim vs fusion-tea), `ife_plant` (six shapes), `self_named_binding_trap` | PASS¹ |
| 9 | Plant-Idiom Literal Pre-Fill | SC-5 (stage 1) | Plain-usage `:>>` overrides captured; entry points pre-fill from design literals | PASS¹ |
| 10 | Cross-Part Channel Wiring | SC-5 (stage 2) | Wires four cross-part shapes end to end — multi-hop EXPOSE, part-def scoped aliases, specialized-def `:>>` chain (single- and two-level), sibling disambiguation. **The `gamma → lcoe` edge.** | PASS¹ |
| 11 | Derived-Attribute Alias Surfacing | SC-7 | The modeler's EXPOSE_PURE name reaches generated output: new `ComputationGraph.output_aliases` field + output-filename override, both shapes; Item 1's warning retired for the resolvable case | PASS |
| 12 | agentic-mbse Sync — Guidance & Validation | R2 | Executes the accumulated agentic-mbse impact list (guidance + validation checks); the A-2 stencil fix; cross-repo acceptance verified | PASS¹ |

¹ CONDITIONAL → PASS: audit raised a condition, the condition was cleared, and the clear was re-verified before the item closed.

## Behavioral changes — downstream coordination

Three items change observable output. Distilled from the per-item release notes (`.project/active/{warning-reconciliation,cross-part-wiring,alias-surfacing}/release-notes.md`).

**Channel wiring (Item 10).** Cross-part channels that previously dropped or aborted now wire:
- `catf_mfe`: `cryo_load.magnet_volume` wires to `CATFMFERadialBuild__catf_radial_build__tf_coil__volume_calc__volume` (was a dangling entry point); catf pipeline baseline regenerated.
- fusion-tea `gamma → lcoe`: `hif_plant__lcoe_calc.driver_cost_constant` moves from an unwired library-default to the `module_output` channel `hif_plant_pkg__hif_plant__driver__meier_cost__gamma`. **A consumer feeding that input from a JSON param must stop** — it is now produced upstream.

**Output filename moves (Item 11).** Aliased channels' output files move from `{channel}.json` to `{instance_path}__{alias_name}.json`. **A harness reading generated output by the old `{channel}.json` path sees the move.** Four exit filenames move in existing committed YAML (`attr_expr_probe` ×3, `solar_battery` ×1); one new committed YAML (`wi014_toy`) carries the alias filename from the start. At the graph level, five committed fixtures now carry populated `output_aliases`.

**Warning reconciliation (Item 7).** "Registry unresolved" warnings now mean something. Benign per-binding / per-collision lines are DEBUG; one WARNING count-summary per class. A genuinely uncovered pipeline input fails at V11 rather than generating a pipeline that `KeyError`s at load.

**fusion-tea workaround retirement.** The `gamma → lcoe` edge those workarounds stood in for is now wired, but the whole-model fusion-tea YAML does **not** yet emit (see caveats), so the `hif_driver_instance` scaffold and the two-pass gamma feedback in `run_anchors.py` are **not yet deletable**. Retirement is gated on the remaining 10 cross-part bindings resolving — tracked as BACKLOG P1.

## Honest caveats

- **SC-2 is met at the graph level, not as a rendered YAML.** On `generate --models ~/1cfe/fusion-tea/models`, the `gamma → lcoe` edge is present in the ComputationGraph from generated wiring alone (V11 offender count 11 → 10), confirmed by direct graph inspection. The full fusion-tea YAML does **not** yet emit.
- **10 remaining fusion-tea cross-part bindings → BACKLOG P1.** Generation still aborts at V11 on 10 other unresolved cross-part inputs on `lcoe_calc`/`recirc_calc` (`driver.efficiency`, `driver.energy`, `driver.lifetime_shots`, `chamber.blanket_energy_multiple`, `chamber.yield_cost_constant`, `target_factory.cost_per_target`, plus the separate `hif_driver_instance` driver). Pre-existing plant-wiring gaps beyond Item 10's SC-2 scope; untouched by this change (INV-A additive). These must resolve before the generated pipeline can replace the hand-plumbing.
- **The Run-C anchor** ($270.12/MWh lcoe, γ=$68.247/J) stays **recorded, not reproduced** in-repo: it is a fusion-tea-harness computation, never an in-repo gate. The in-repo SC-2 gate is the graph edge plus the `spec_chain_twolevel` pin flip.
- **Deferred drift chore.** SC-1 full constraint execution, supertype-chain template inheritance, EXPOSE_COMPUTED / redefinition name-surfacing, and non-uniform arrays remain out of scope (see the epic's Deferred section). Item 1 removed the silence; demand should be re-weighed after the MFE epic.

## Companion PR — agentic-mbse

Item 12's implementation (the accumulated guidance + validation changes and the A-2 stencil fix) lands in a companion branch, `upstream-findings-sync`, in `~/1cfe/agentic-mbse`. The orchestrator opens that PR separately. The two repos are designed to move in lockstep (R2): sysml-codegen defines the executable subset, agentic-mbse teaches and audits it.

## Audit trail

- Epic doc: `.project/backlog/epic_upstream_findings.md` (Status: Complete)
- Per-item artifacts: `.project/active/*/` (spec, design, plan, audit for each item)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
