---
date: 2026-07-19 10:34 PDT
researcher: Codex
topic: "Independent assessment of fusion-tea Gate B constraint-extension/V11 collision"
tags: [research, constraint-wave, v11, fusion-tea, snapshot, integration]
status: complete
last_updated: 2026-07-19
---

# Independent assessment: fusion-tea Gate B

## Question

Assess the fusion-tea report
`/home/reid/1cfe/fusion-tea-stellarator-mbse-demo/.project/research/20260719-082509_gate-b-root-cause-constraint-lowering-vs-v11-bridge.md`:

1. Is the issue legitimate?
2. Is it already covered by the constraint PR-wave remediation epic?
3. What is the correct repair?
4. When should it enter the wave?

This document decides nothing. Recommendations are `[AGENT]`.

## Verdict

- **Legitimate issue: yes.** Adding any concrete constraint conditionally runs a whole-graph V11
  check during graph extension. That rejects unrelated pre-existing coverage violations before the
  normal generation boundary and before fusion-tea's late-fill bridge can act.
- **Already addressed: no.** Completed Items 1, 2, 4, and 6 do not change the collector, the two
  extension call sites, or the extension-time raise. Items 3, 5, and 8 overlap with the affected
  surfaces or evidence, but none owns this behavior.
- **Correct repair: amend extension ownership.** Constraint extension should introduce no new V11
  violations. Final generation should still require zero whole-graph V11 violations. Keep strict
  constraint-actual resolution and whole-graph channel-reference validation unchanged.
- **Timing: capture it in the epic now as a distinct item.** It should be implemented before Item 5
  and verified again in Item 8. `[AGENT]` Default sequence: Item 3, Gate B, Item 5, Item 7, Item 8.
  If fusion-tea needs to unblock before Item 3 completes, Gate B has no technical dependency on
  Item 3 and can be implemented first.

## Evidence

### The current tree reproduces the collision

`extend_graph_with_constraints` copies the base modules, appends constraint/report modules, copies
the base fallback set, and then calls `collect_uncovered_params` across the complete extended graph.
It raises on any result (`constraint_lowering.py:1265-1438`). The live path invokes this only when
`concrete_constraints` is non-empty (`pipeline_builder.py:996-1004`). Snapshot rebuild invokes the
same function before a consumer can modify the rebuilt graph (`graph_rebuild.py:213-225`).

The collector classifies a module input as uncovered when it consumes an entry point whose QN is in
the fallback set and whose default is `None` (`graph_builder.py:800-845`). Its own docstring says
only the generation boundary raises V11 (`graph_builder.py:803-804`). The architecture contract also
places the strict raise at generation (`docs/architecture/reference/07-graph-assembly.md:25,280-299`).

The fusion bridge fills exactly three such entry points after rebuilding the context, then runs the
normal coverage collector/gate (`bridge_v11_generate.py:73-111`). The two-pass runner replaces those
placeholders with calculated rollups before its canonical second pass (`run_stellaris.py:178-215`).

Three current-tree checks were run:

- The report's license-free minimal graph reports one offender before placeholder fill and zero
  afterward.
- Calling `extend_graph_with_constraints` on that same current-tree graph with an unrelated safe
  constraint raises at current `constraint_lowering.py:1438` on the pre-existing LCOE input.
- An independent agent also reran the licensed fusion snapshot capture against the current dirty
  tree. It failed at the same line with the report's exact three rollup offenders.

### Existing epic work does not fix it

The current diff does not modify `graph_builder.py`, `pipeline_builder.py`, or `graph_rebuild.py`.
Item 1 modifies earlier lowering/profile behavior in `constraint_lowering.py`, but leaves the V11
tail unchanged. The current epic scopes:

- Item 3 to occurrence expansion and demand identity (`epic_constraint_pr_wave_remediation.md:242-273`),
- Item 5 to diagnostic and modeled-default fidelity (`:330-359`), and
- Item 8 to final compatibility/release evidence (`:456-487`).

None specifies coverage-gate timing or ownership. A final evidence item cannot substitute for a
behavioral-fix owner.

## Corrections to the fusion report

### INV-6 is not already narrow

The report says scoping the check to constraint-added inputs matches INV-6's existing intent. The
second sentence of INV-6 discusses constraint consumers and minted entry points, but the first
sentence literally requires the extended graph to have zero V11 uncovered parameters
(`completed/20260713_constraint-lowering/design.md:294-295`). The implementation also documents a
whole-extended-graph recheck (`constraint_lowering.py:1286-1288`).

Therefore this repair must be recorded as an intentional contract correction, not described as an
unambiguous restoration of the old wording. `[AGENT]` Replacement invariant:

> Constraint extension introduces no new V11 uncovered inputs. Final generation requires zero
> whole-graph V11 uncovered inputs.

Whole-graph `_validate_channel_references` remains required during extension.

### The fusion bridge is not a supported upstream seam

The bridge labels itself `LOCAL BRIDGE — NOT A FIX` and imports private CLI functions
(`bridge_v11_generate.py:1,51-67`). It is a legitimate consumer workaround, but normal
`run_codegen` has no callback between context construction and the final V11 gate. The report's
claim that codegen explicitly sanctions this bridge pattern is too strong.

The current remediation tree has also made the script stale: `_generate_modules` now requires a
prebuilt `ConstraintGenerationPlan` (`cli/__init__.py:349-354,980-1001`), while the bridge still
passes three arguments (`bridge_v11_generate.py:117`). The bridge also bypasses current preflight,
prewrite planning, and sealing steps. Gate B repair restores context construction; it does not by
itself make this private script compatible with the final wave.

### The proposed negative regression needs a precise shape

Extension copies `fallback_entry_points` unchanged (`constraint_lowering.py:1428-1433`). A freshly
minted constraint entry point is therefore not a new fallback key and cannot independently satisfy
the collector's V11 predicate. The useful negative case is:

1. The base graph contains a valueless fallback entry point that is currently unwired.
2. A new constraint module reuses that entry point as a design-attribute input.
3. Extension must reject the newly introduced consumer.

## Repair assessment

### `[AGENT]` Preferred semantic rule: reject only new violations

The smallest coherent behavior is:

1. Collect baseline V11 violations from the input graph.
2. Build the extended graph.
3. Validate channel references across the whole extended graph.
4. Collect extended V11 violations.
5. Raise only for violations introduced by the extension.
6. Leave `_reconcile_params_coverage` unchanged as the final whole-graph generation gate.

A before/after **multiset** difference states the semantic rule directly and does not rely on module
names. The extension is append-only today, so checking only the appended module slice is equivalent
and cheaper. A module-name filter is less safe because names are not the ownership boundary and can
collide. Design should choose multiset differential or an object/module-slice collector, and pin the
identity used by the difference.

Removing the early coverage check entirely is defensible under REQ-GA-08, but loses the earlier
constraint-specific failure when a new constraint consumes a previously unwired bad key. Deferred
input annotations and a capture hook add schema/API surface without being needed for this defect.

Strict actual resolution (INV-2) is independent and must not change. This repair must never
synthesize a constraint actual, textual default, or fallback entry point.

## Required regressions

- Pre-existing wired V11 violation plus unrelated safe constraint: extension succeeds.
- Pre-existing unwired fallback entry point newly consumed by a constraint: extension fails.
- Mixed baseline and new violations: the extension error names only the new violation.
- Final generation gate: still fails before late fill and passes afterward.
- Strict unresolved constraint actual: still fails through the existing INV-2 path.
- Live and snapshot reconstruction: identical graph/catalog/generated bytes after late fill.
- Fusion integration: update the private bridge for `ConstraintGenerationPlan`, current preflights,
  and sealing, or replace it with an explicitly designed public seam in a separate item.

## Epic placement and timing

This finding postdates the R-1 through R-12 source review and is not already registered. `[AGENT]`
Add a distinct item such as **Item 3B: Constraint-Extension V11 Coverage Ownership (Gate B)**. A
separate item gives the invariant amendment, RED/GREEN evidence, and consumer caveat an auditable
home. It does not imply a separate commit or PR; the owner's one-landing-unit decision remains
unchanged.

Recommended default sequence:

```text
Item 3 occurrence/demand
  -> Item 3B Gate B coverage ownership
  -> Item 5 lowering/default fidelity
  -> Item 7 tail
  -> Item 8 release evidence + fusion bridge compatibility
```

Gate B has no correctness dependency on Item 3. If the fusion demo is the immediate blocker, move
Item 3B ahead of Item 3, then rerun its parity regression after Item 3. Do not add model placeholder
defaults merely to avoid edit overlap; all work is already one landing unit. The placeholder model
workaround is reasonable only for an independent fusion delivery deadline that precedes the wave.

## Limits

- No production fix was implemented in this review.
- The full fusion capture was independently reproduced, but the post-fix end-to-end bridge could
  not be tested because no fix exists and the bridge is currently incompatible with the dirty
  generation API.
- The exact public/private status of a future late-fill seam is a product/API design decision. It
  is separate from correcting extension-time V11 ownership.

## Primary references

- Fusion report: `/home/reid/1cfe/fusion-tea-stellarator-mbse-demo/.project/research/20260719-082509_gate-b-root-cause-constraint-lowering-vs-v11-bridge.md`
- Current extension: `src/sysml_codegen/analysis/constraint_lowering.py:1265-1438`
- Collector: `src/sysml_codegen/resolution/graph_builder.py:800-845`
- Live/snapshot calls: `src/sysml_codegen/orchestration/pipeline_builder.py:996-1004`;
  `src/sysml_codegen/snapshot/graph_rebuild.py:213-225`
- Final gate: `src/sysml_codegen/cli/__init__.py:244-290`
- V11 architecture: `docs/architecture/reference/07-graph-assembly.md:25,280-299`
- Old INV-6: `.project/completed/20260713_constraint-lowering/design.md:294-295`
- Epic: `.project/backlog/epic_constraint_pr_wave_remediation.md`
- Fusion bridge/runner:
  `/home/reid/1cfe/fusion-tea-stellarator-mbse-demo/exploration/stellarator_e2e/bridge_v11_generate.py`;
  `/home/reid/1cfe/fusion-tea-stellarator-mbse-demo/exploration/stellarator_e2e/run_stellaris.py`
