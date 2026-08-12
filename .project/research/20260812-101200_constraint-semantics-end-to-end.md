---
date: 2026-08-12T10:12:00-07:00
researcher: Claude
topic: "Constraint semantics end-to-end: plain vs assert forms, pipeline treatment, and the product rule for design-search physics gates"
tags: [research, constraints, executable-profile, elaboration, catalog, design-search, catf, fusion-tea]
status: complete
last_updated: 2026-08-12
---

# Research: Constraint Semantics End-to-End

**Date**: 2026-08-12 (PDT)
**Researcher**: Claude
**Research Type**: Domain + Codebase + Architecture
**Trigger**: Owner direction in `/tmp/handoff-20260812-095207.md` — subjects 1 and 2 first, together:

> **[OWNER-VERBATIM, 2026-08-12]** "We need to get to the bottom of 'how do constraints work',
> checking against our most rich model to make sure we have defined, clear expectations and that
> that is what our code does."

Owner-stated product frame, given in session on 2026-08-12: constraints are how the models
enforce things like physics, so that the overall **design search** stays viable. That frame is
used throughout: a constraint story is judged by whether a design-space search over these models
can trust its feasibility evidence.

All measurements below were taken this session at codegen `2ebf638` / agentic-mbse `3fbda2f`
(worktrees `sysml-codegen-item7-rebuild` / `agentic-mbse-item7-rebuild`), with imports verified to
resolve into the rebuild worktrees. No repo file was modified; probes ran on disposable copies in
the session scratchpad.

## Research Question

What do modeled constraints mean (plain `constraint` vs `assert constraint` vs
`require`/`satisfy`)? How does the pipeline treat each form (extraction → profile classification →
catalog disposition → generated module → TEAx report)? And what should the product rule be, given
constraints exist to enforce physics feasibility for design-space search? Pressure-tested against
`catf_mfe_d5` (nine instance-reaching plain constraints, all excluded) and `fusion_tea` (the
executable customer route).

## Summary

- **The language settles question 1.** SysML v2 says a plain `constraint` usage is a computed
  Boolean with **no truth claim**; only the `assert` family (`assert constraint`,
  `assert not`, `satisfy requirement`) asserts its predicate (SysML v2 Part 1 §8.4.16.3). The
  shipped profile — only assert inline/definition-typed forms execute — is standard-conformant
  and matches the owner-ratified contract. The modeling-assumptions doc's claim that a bare
  `constraint` gives an enforced gate is wrong and uncorroborated by any owner decision.
- **CATF's constraints are physics guards authored in the non-asserted form.** All 65 are bare
  `constraint`; their doc comments say "must be positive", "should be physical". The 9
  instance-reaching (part-usage-owned) ones catalog as excluded/unassessed. Adding `assert` is
  **not** sufficient: measured on a disposable copy, 1 of 9 admits (`ViabilityCheck`), 8 block
  (6 in-predicate feature chains, 2 real equalities without tolerance) — and any block hard-halts
  generation of the whole model.
- **51 of CATF's 65 constraints are structurally unreachable regardless of form.** The elaborator's
  `_scopes_for_owner` has no `CalculationDefinition` branch (`elaborate.py:522-539`), so a
  constraint inside a `calc def` body never reaches an instance — even though those calc defs
  produce most of the 42 generated modules. These 51 (plus 5 part-def-owned with zero typed
  occurrences) also have **no catalog carrier**: the exact route's catalog shows only the 9,
  leaving 56 swept usages invisible.
- **The design-search consequence is the sharpest problem.** TEAx policy maps a package with no
  constraint headline to `unconstrained`. CATF today generates no aggregator, so a search over it
  treats every candidate as feasible with zero physics gating and zero signal that 65 gating
  constraints were authored. Even after the excluded-only fix, the report schema
  (`assessed_count`, `headline`, `results` only) cannot distinguish "all physics gates passed"
  from "the two easy gates passed and seven were excluded."
- **fusion_tea shows the one blessed authoring pattern that works end to end:** a
  `constraint def` with formals + `assert constraint x : Def { in formal = child.attr; }` +
  inequality predicates. Cross-part navigation lives in the usage bindings, not the predicate;
  the operator is `>=`, not `==`. That exact shape admits, lowers, generates a constraint module
  and report aggregator, and drives study dispositions.

## Detailed Findings

### 1. What the language says (per-form semantics)

Assertion in SysML v2/KerML is library subsetting, not a flag: every constraint usage subsets
`Constraints::constraintChecks` (a Boolean evaluation with no committed value); only Invariants
additionally subset `Performances::trueEvaluations`/`falseEvaluations`, whose result is bound to
`true`/`false` (KerML 8.4.4.8.2; SysML Part 1 8.4.16.3).

| Form | Standard verdict | Key citation (SysML v2 Part 1 unless noted) |
|---|---|---|
| `constraint c { ... }` (bare, any owner) | **NOT asserted** — "may be true at some times and false at other times" | §8.4.16.2–3, §7.20.1 |
| `constraint c : Def { ... }` (typed, no `assert`) | **NOT asserted** — typing supplies the predicate, not an assertion | §8.4.16.2 |
| `assert constraint c [: Def] { ... }` | **Asserted true, always** — `AssertConstraintUsage` is a KerML `Invariant` | §8.3.20.2, §8.4.16.3 |
| `assert not constraint ...` | **Asserted false, always** | §8.4.16.3 |
| `require constraint` / `assume constraint` | **Not asserted standalone** — a conjunct in the owning requirement's implication (assumptions ⇒ constraints) | §8.4.16.2, §9.2.14.2.8 |
| `satisfy requirement ... by f` | **Asserted** — asserts the requirement's result for the bound subject | §8.4.17.3 |

Constraints nested in a `calc def` get no special clause: a calc def is a Behavior, the nested
constraint is an enclosed Boolean-valued performance, its result computed and nowhere bound. The
spec's "may effectively constrain the values of those features" (§7.20.1) is about expression
scoping, not a grant of invariant status.

The spec neither authorizes nor forbids tools evaluating non-asserted constraints. What a tool may
not claim on the standard's authority is that a failed plain constraint makes the model
inconsistent — that verdict is reserved for the assert family. So "admit plain forms" is a
permitted tool choice, but it erases the modeler's only way to write a descriptive,
deliberately-unasserted constraint, and it contradicts the ratified contract (below).

### 2. What the code does (taxonomy, profile, lifecycle)

**Form classification** — `agentic_mbse/sysml/constraint_extraction.py:703-723` (`_classify`):
membership `RequirementConstraintMembership` → `requirement_constraint`; `AssertConstraintUsage`
→ `named_usage_reference` (assert-by-reference) / `definition_typed` (no own
`result_expression`) / `inline` (owns predicate); `SatisfyRequirementUsage` → `satisfy`;
fall-through → `plain_usage`. The single syntactic feature separating `plain_usage` from `inline`
is the `assert` keyword. A bare typed usage (`constraint c : Def;`) is also `plain_usage`.
`_effective_predicate_source` (`:726-735`) returns `None` for `plain_usage` — an authored bare
body is never read as a predicate.

**Profile gate** — `agentic_mbse/sysml/executable_profile.py:949-950`: `satisfy`,
`requirement_constraint`, `plain_usage` → UNASSESSED **before predicate inspection**; an
UNASSESSED decision carries no predicate and no polarity by construction (`UsageDecision`
invariant, `:156-165`). `named_usage_reference` → `block_assert_by_reference`. Only `inline` and
`definition_typed` get their predicate walked; the walk blocks on invocation, in-predicate feature
chains (`_walk_value`, `:535-537`), `xor`/`implies`, real/quantity `==`/`!=` without tolerance
(`classify_equality`, `:305-308`), and unit incompatibilities.

**Instance reach** — `sysml_codegen/elaboration/elaborate.py:522-539` (`_scopes_for_owner`,
verified directly this session): branches for `PartDefinition` (occurrences of the type),
`PartUsage` (occurrences of the declaration), `Package`; **no `CalculationDefinition` branch** —
fall-through returns `()`, so `_build_constraint_nodes` (`elaborate.py:997-1004`) creates zero
nodes for calc-def-owned constraints regardless of form or how often the calc def is used.

**Catalog** — excluded records carry `kind="unassessed_form"`, `reasons=["eligibility_unassessed"]`
(`sysml_codegen/elaboration/project.py:1093-1105`). Only constraints that produced instance-graph
nodes get carriers; usages with zero scopes appear nowhere (see finding 4).

**Generated runtime** — `templates/report_aggregator.py.jinja2`: headline = violation >
indeterminate > `all_satisfied` (any non-empty result set) > `not_assessed`. It never consults
excluded records. `ConstraintReport` = `catalog_fingerprint`, `assessed_count`, `headline`,
`results` — no total population, no excluded count/reasons, no coverage state. The projector's
`_build_constraint_modules` returns early when there are no executable constraints
(`project.py:895`), and scheduling adds the aggregator only when constraint outputs exist — so an
excluded-only model gets **no aggregator at all**, though the template itself supports the
zero-input `not_assessed` shape and contract invariant 32 requires it.

**Study consumption** — `teax/packages/teax-simkit/simkit/study/policy.py:32-37, 76-80`:
`violated → reject`, `indeterminate → keep-for-boundary`, `not_assessed → keep-for-boundary`,
`satisfied → feed-strategy` (or `penalize` past a threshold). A package with **no headline**
(no aggregator) → disposition `unconstrained` (`policy.py:65-68, 112-116`), the deliberate
contract-46a state for constraint-free models.

### 3. The rich-model measurement (CATF)

`catf_mfe_d5` is confirmed as the right richness witness (65 constraint usages spanning all three
owner kinds, 42-module calc graph); `fusion_tea` complements it as the executable customer route.
Catalog at HEAD reproduces the prior session exactly: `source_records=0, usage_records=0,
concrete_entries=0, excluded_records=9`; fingerprint
`69164c0c23d874e121c24dbba6bf9aae1564b3e3c193b68abafae0d5a8554e60`; 42 modules, all CALCULATION.

Owner-type census of the 65 swept usages:

| owner type | count | reaches instances? | why |
|---|---|---|---|
| `PartUsage` (in `designs/`) | 9 | yes — the 9 excluded records | `_scopes_for_owner` PartUsage branch |
| `PartDefinition` (in `library/components/`) | 5 | no | branch exists, but every design part is untyped (`part catf_vacuum_vessel { ... }`, never `part x : 'Vacuum Vessel'`) → zero occurrences |
| `CalculationDefinition` (in `library/physics/`, `library/analyses/`) | 51 | no | **no branch at all** — structurally unreachable even though these calc defs generate most of the 42 modules |

The nine instance-reaching constraints, with intent read from their source doc comments — every
one is a physics/consistency check, none reads as deliberately descriptive:

| # | usage (QN tail) | file:line | predicate (abridged) | intent per doc comment | assert-probe outcome |
|---|---|---|---|---|---|
| 1 | `catf_physics::PowerBalanceConsistency` | `designs/catf_mfe/physics.sysml:125` | `alpha_neutron_split.p_alpha + ... > p_fusion * 0.999 and ... < p_fusion * 1.001` | energy-conservation band | BLOCK: `block_feature_chain` ×2 |
| 2 | `catf_physics::ViabilityCheck` | `physics.sysml:134` | `p_electric_net_out > 0` | net-power viability gate | **ADMIT** |
| 3 | `catf_physics::ReasonableParasiticTotal` | `physics.sysml:142` | `net_electric.p_parasitic_total > gross_electric.p_electric_gross * 0.10 and ... < ... * 0.90` | parasitic-fraction plausibility | BLOCK: `block_feature_chain` ×2 |
| 4 | `catf_shield::CompositionConsistency` | `designs/catf_mfe/shield.sysml:171` | `neutron_shield.fraction_volume + gamma_shield.fraction_volume == 1.0` | volume-fraction closure | BLOCK: `block_feature_chain` (equality also present, masked) |
| 5 | `catf_vacuum_vessel::ThicknessConsistency` | `designs/catf_mfe/vacuum.sysml:87` | `outer_radius == inner_radius + wall_thickness` | geometry consistency | BLOCK: `block_real_equality_requires_tolerance` |
| 6 | `catf_vacuum_pumping::PumpingSpeedConsistency` | `vacuum.sysml:169` | `pumping_speed_total == n_pumps * pump_capacity_each` | pump sizing consistency | BLOCK: `block_real_equality_requires_tolerance` |
| 7 | `catf_radial_build::TotalRadiusConsistency` | `designs/catf_mfe/radial_build.sysml:605` | `bioshield.outer_radius == 8.55 [m]` | envelope pin | BLOCK: `block_feature_chain`; also trips the independent `[m]` defect (finding 6) |
| 8 | `catf_radial_build::LayerContinuity` | `radial_build.sysml:612` | 13-term `and` of `layerN.inner_radius == layerN-1.outer_radius` | radial-build continuity | BLOCK: `block_feature_chain` ×13 |
| 9 | `catf_radial_build::RadiusThicknessConsistency` | `radial_build.sysml:630` | 14-term `and` of `layer.outer == layer.inner + layer.thickness` | per-layer geometry | BLOCK: `block_feature_chain` ×14 |

Assert-conversion probe (disposable copy, bodies unchanged, all nine `constraint` →
`assert constraint`, reclassified `inline`): **1 ADMIT / 8 BLOCK / 0 NON_NUMERICAL**. Building the
converted model raises `ElaborationDiagnosticError` at `elaborate.py:488` with one
`SI_CONSTRAINT_BLOCKED` per block — generation of the *whole model* halts (by design: contract
"named model halt"); there is no partial-generation path. A second copy asserting only
`ViabilityCheck` builds cleanly: 44 modules (constraint module + `constraint_report_aggregator`
added), `concrete_entries=1`, `excluded_records=8`, well-formed IR. So part-usage ownership works;
the CATF blockers are entirely predicate shape.

### 4. The catalog totality gap (56 of 65 usages have no carrier)

The license-free manifest sweep sees 65 usages; the exact route's catalog carries 9. The 51
calc-def-owned and 5 part-def-owned usages produce zero instance-graph nodes, therefore zero
concrete records, therefore no excluded record either. Contract invariant 1 ("after generation,
every other usage has executable concrete representation or a visible exclusion") and invariant 28
("one visible disposition per usage") are not met by the exact route for these 56; REQ-CL-04
(verification matrix, PARTIAL) is exactly this obligation and REQ-EXT-09's old evidence test
(`test_constraint_migration_mapping.py`) no longer exists. This is the concrete instance behind
the step-4 brief's "a silently dropped third usage must fail."

### 5. fusion_tea — the working exemplar and the exact pattern difference

`fusion_tea` has exactly one constraint: `assert constraint viability : 'Viability Threshold'
{ in eta = driver.efficiency; in gain_in = gain; }` (`designs/generic_ife/ife_plant.sysml:155`,
part-def owner). Predicate from the `constraint def` (`library/analyses/fusion_cycle.sysml:29`):
`eta * gain_in >= threshold` with `threshold` defaulting to 10.0. Catalog: `source_records=1,
usage_records=1, concrete_entries=1, excluded_records=0`; graph has 7 calculation modules + 1
constraint module + the aggregator; the execution suite drives satisfied/violated/indeterminate,
margins, persistence, and study dispositions through it.

The whole executable/excluded gap between fusion_tea and CATF reduces to three authoring choices:

| dimension | fusion_tea (admits) | CATF (blocks/unassessed) |
|---|---|---|
| assertion | `assert constraint` | bare `constraint` |
| navigation | in usage **bindings** (`in eta = driver.efficiency`) — predicate written over formals | dotted chains **inside the predicate** (`net_electric.p_parasitic_total`) |
| comparison | inequality (`>=`) | 6 of 9 use real `==` with no tolerance band |

### 6. New defects and quality findings (beyond the semantics question)

- **[m]-literal elaborator failure (new, independent).** `bioshield.outer_radius == 8.55 [m]`
  asserted alone produces `SI_OCCURRENCE_MISSING: leaf declaration 146016c8-… has no feature
  slot` on top of the profile block; dropping `[m]` removes it. Any admitted predicate carrying a
  unit-annotated literal will hit this. Reproduced and isolated this session.
- **Chain-block diagnostic is a tautology.** The message is literally
  `feature_chain: block_feature_chain` — no reference, no segment; `LayerContinuity` emits 13
  identical copies. The equality block's message, by contrast, is actionable. Modelers cannot
  debug from the chain message.
- **Owner-kind duality.** `ConstraintNode.owner_kind = "partusage"` while agentic-mbse's
  `OwningDefinitionFact.kind = "package"` for the same usage (the fact walk skips part usages).
  Any join on owner kind across the two layers mismatches.
- **Stale PROVENANCE.** `tests/fixtures/catf_mfe_d5/PROVENANCE.md` still says the exact route
  refuses the model (152× `SI_OCCURRENCE_MISSING`); it now builds 42 modules. Needs amending when
  the fixture's disposition is decided.
- **Doc-promise evidence hole.** `modeling-assumptions.md:482-487` and
  `reference/01-extraction.md:20` pin the totality promise on a test file that was retired.

### 7. Documentation contradiction register (subject 2 worklist)

Authority side (agree with code + standard): ratified concept
`constraint-execution-and-design-space-studies.md:83` ("Plain, require, assume, and satisfy forms
remain cataloged but unassessed", under the 2026-07-19 **[OWNER-VERBATIM]** "Ratified."), contract
invariant 12 (inline + definition-typed assertions, ratification-target grade), completed
executable-profile spec (`20260713_executable-profile/spec.md:126-134`), agentic
`docs/patterns/constraints.md:25-41` (correct four-outcome story).

Contradicting/defective statements to fix (all agent-authored, none owner-corroborated):

| # | location | defect |
|---|---|---|
| D1 | codegen `docs/architecture/modeling-assumptions.md:489-491` | says bare `constraint`/`require constraint` gives an enforced gate — false; the exact form that silently does nothing |
| D2 | codegen `modeling-assumptions.md:466-469` | unassessed set enumerated as requirement-side + bad owner only; omits `plain_usage`/`require`/`assume` |
| D3 | agentic `docs/subtype-enumeration-decision-table.md:24` | "require/plain are executable constraint usages (lowered under the profile)" — false |
| D4 | agentic `docs/patterns/constraints.md:192-199` | calls bare `constraint` wrong for a false reason ("parser does not create proper AST node" — it produces a `ConstraintUsage`, classified `plain_usage`) |
| D5 | agentic `claude/agents/sysml-expert.md:124`, `docs/patterns/semantic-operators.md:505-545` | teach `require constraint` as an equal alternative for checks — steers modelers into an unassessed form |
| D6 | codegen `docs/architecture/reference/28-constraint-lowering-and-catalog.md:42-48` | attributes unassessed to owner kind only; code decides by source form (contract: the axes are independent) |
| D7 | codegen `modeling-assumptions.md:482-487`, `reference/01-extraction.md:20` | cite retired `test_constraint_migration_mapping.py` as the living evidence |

## Architecture Insights

- The three-job mental model (model states meaning / package evaluates / study decides) is sound
  and the fusion_tea route proves it end to end. The failures are all at the edges: authoring
  guidance that misstates the model's side, an elaborator reach gap for calc-def owners, catalog
  totality at the exact route, and a report that under-communicates coverage to the study.
- The profile's form gate is where language semantics enter the product. Because assertion is the
  standard's own executable/descriptive discriminator, keeping the gate aligned with the standard
  preserves both meanings: modelers can still write descriptive constraints, and `assert` is the
  single, spec-defined opt-in to enforcement.
- BLOCK-halts-the-model is the right default for asserted-but-unsupported predicates (fail closed,
  never silently skip a physics gate), but it makes model migration atomic: CATF cannot be
  converted incrementally in place — each converted constraint must admit or the model stops
  generating.

## Proposed product rule (critiqueable expectation set — all [AGENT], for owner ratification)

**P1 — Meaning follows the standard (confirm the ratified rule).** A bare `constraint` is a
visible, cataloged, never-executed description. `assert constraint` (inline or
definition-typed) is the one enforcement opt-in; `assert not` is its negation;
`require`/`assume`/`satisfy` stay requirement-side and unassessed. This is what the code does and
what the owner ratified on 2026-07-19; it should be re-stated once, plainly, as the product rule.

**P2 — One blessed authoring recipe for a physics gate**, documented identically everywhere:
`constraint def` with formals (+ modeled defaults where sensible) → `assert constraint g : Def {
in formal = <real value in scope>; }` → inequalities only; equality intent becomes an explicit
two-inequality tolerance band with a modeler-chosen tolerance. fusion_tea's `viability` is the
canonical example. Fix D1–D7 accordingly (delete-over-shim: D1's wrong clause is deleted, not
annotated).

**P3 — Every swept usage has a visible carrier (close the 56-usage gap).** The exact route's
catalog must carry a disposition for every manifest-swept usage — eligible, excluded-with-reason,
or named justified exclusion — including calc-def- and part-def-owned usages that reach no
instance. "Reaches no instance" should itself be a visible exclusion reason, not an absence.

**P4 — Coverage must be legible to the design search (feeds subjects 3/4; contract before code).**
A search must be able to distinguish: all gates passed / some gates passed and N excluded (with
reasons) / nothing ran / no constraints exist. Whether that lives in `ConstraintReport` fields, a
headline value like `partially_assessed`, or a verifiable catalog join is the subject-3/4 design
decision — but the expectation should be fixed now: **silent partial coverage is never
representable as full feasibility.** The excluded-only zero-input aggregator (invariant 32) is one
instance of this, to be patched only as part of the agreed contract.

**P5 — Asserted-but-unreachable is an error.** Once P3 exists: an `assert constraint` whose owner
gives it zero concrete scopes (e.g. inside a calc def today) should be a loud diagnostic, not a
silent no-op — an asserted invariant the pipeline cannot check is exactly the silent-gap class the
design search cannot tolerate.

## Material choices for the owner

1. **Ratify P1 or change it.** The alternative — profile admits plain forms — is standard-divergent,
   contradicts the ratified concept, and erases descriptive constraints. Not recommended.
2. **CATF constraint intent, per constraint.** All nine read as intended physics checks. Which
   should become enforced gates (`assert` + P2 rewrite), and which stay descriptive? The six
   equality predicates each need a modeler-chosen tolerance (code must not invent one — e.g.
   `CompositionConsistency`'s `== 1.0`, `TotalRadiusConsistency`'s `== 8.55 [m]`).
3. **The 51 calc-def guards.** Options: (a) declare calc-def-owned constraints out of executable
   scope permanently and surface them per P3 as visible non-reaching records; (b) add elaborator
   scope so asserted calc-def constraints expand per calculation occurrence (new capability,
   real design work); (c) migrate the guard intent up to part level in the models. This is the
   dominant share of CATF's authored physics checking — it deserves an explicit ruling, not a
   default.
4. **Fixture strategy.** `catf_mfe_d5` is strip-reversal-pinned to `catf_mfe_model`
   (`test_d5_variants.py:29`), whose ratified corpus row pins its *refused* shape. A constraint
   migration therefore needs an explicit artifact decision: migrate both twins coherently
   (redefining the D-5 relationship), build a new enriched derivative fixture and keep the twins
   frozen, or leave CATF as the unassessed witness and author gates in a new model. Blocked on
   choice 2/3.
5. **Defect filing.** The `[m]`-literal `SI_OCCURRENCE_MISSING` failure and the tautological
   chain-block diagnostic: fix inside the constraint-semantics work, or file to backlog?

## Code References

- `agentic-mbse: src/agentic_mbse/sysml/constraint_extraction.py:703-723` — form classifier (`_classify`)
- `agentic-mbse: src/agentic_mbse/sysml/executable_profile.py:949-950` — plain/require/satisfy → UNASSESSED gate
- `agentic-mbse: src/agentic_mbse/sysml/executable_profile.py:535-537, 305-308` — chain and equality blocks
- `src/sysml_codegen/elaboration/elaborate.py:522-539` — `_scopes_for_owner`; no CalculationDefinition branch
- `src/sysml_codegen/elaboration/elaborate.py:488` — `ElaborationDiagnosticError` hard halt on BLOCK
- `src/sysml_codegen/elaboration/project.py:895, 1093-1105` — excluded-only early return; exclusion record shape
- `src/sysml_codegen/templates/report_aggregator.py.jinja2` — headline logic; excluded records unconsulted
- `teax: packages/teax-simkit/simkit/study/policy.py:32-37, 65-68, 76-80, 112-116` — headline → disposition; `unconstrained`
- `tests/fixtures/catf_mfe_d5/designs/catf_mfe/{physics,shield,vacuum,radial_build}.sysml` — the nine (lines in table)
- `tests/fixtures/fusion_tea/designs/generic_ife/ife_plant.sysml:155`, `library/analyses/fusion_cycle.sysml:29` — exemplar
- `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:126-247` — invariants (1, 8, 12, 16, 28, 32, 46a)
- Probe scripts and disposable copies: session scratchpad (`task_a.py`, `task_b.py`, `catf_copy/`, `catf_one/`)

## Open Questions

Carried from the owner handoff and sharpened by measurement — the five Material Choices above,
plus for subjects 3/4 (deferred until 1/2 are settled): what population runtime coverage counts
(usage vs occurrence), whether `ConstraintReport` embeds exclusions or joins to the catalog,
whether `all_satisfied` may coexist with exclusions under a separate coverage state, and how
`NON_NUMERICAL`/`UNASSESSED`/`BLOCK` surface to generation users, package consumers, and TEAx
studies. The narrow excluded-only projector patch stays parked until that contract is defined.
