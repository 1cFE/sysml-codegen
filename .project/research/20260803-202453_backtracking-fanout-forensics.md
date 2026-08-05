---
date: 2026-08-03
researcher: Codex
topic: Forensic analysis of shared-source fan-out splitting into per-consumer entry points
tags: [backtracking, source-identity, entry-points, virtual-bindings, testing, audit, process]
status: complete
last_updated: 2026-08-03
---

# How a central backtracking bug survived the refactors and reviews

## Research question

**[OWNER-VERBATIM]**: “How the flying fuck could this happen?”

**[OWNER-VERBATIM]**: “What does that say about this library? Is this total AI slop and garbage?”

The handoff sharpens the first question: the owner had personally shepherded two large
backtracking/source-resolution refactors, yet the generated public input surface still turns one
shared SysML attribute into several independently mutable fields
(`/tmp/handoff-20260803-200817.md:5-11`).

This is a forensic report, not a fix. It answers:

1. What the code does.
2. Whether the behavior regressed or never worked.
3. Which specifications, reviews, tests, and audits should have caught it.
4. What confidence remains justified in the library.

## Executive verdict

### The short answer

**[AGENT] This exact feature composition never worked. It is not a regression from a correct
implementation.**

The failing composition is:

- an attribute declared on a `PartDef`;
- a literal supplied at a concrete occurrence;
- two or more self-named calculation bindings such as `in R = R`; and
- a generated input surface that is supposed to preserve the one source attribute as one public
  parameter.

The current pipeline copies the occurrence literal into each calculation binding and turns each
binding into a consumer-local `LITERAL` before backtracking. It also clears the binding's
`source_path`. The backtracker therefore never gets a chance to converge those bindings on the
source attribute. It mints `usage_qn__param` once per consumer instead
(`src/sysml_codegen/orchestration/pipeline_builder.py:336-369`,
`src/sysml_codegen/analysis/dependency_backtracker.py:439-463`).

The July source-qualified-name work fixed adjacent shapes. It did not fix this shape. The later
shared-producer work explicitly certified only an attribute declared directly on a concrete
`PartUsage`, and explicitly excluded occurrence-indexed `PartDef` owners
(`.project/completed/20260720_constraint-lifecycle-shared-resolution/spec.md:175-191,274-278`,
`.project/completed/20260720_epic_constraint_execution_lifecycle_remediation.md:476-499`).

### How it survived

The failure was not hidden from the repository. The workflow saw it repeatedly:

1. A July extraction fixture recorded that a self-named binding resolves to the calculation's own
   formal instead of the outer attribute.
2. The real Fusion Tea fixture contained the full multi-consumer defect.
3. A runtime acceptance test explicitly documented `gain` as per-consumer and perturbed only the
   LCOE copy.
4. The implementation plan reclassified the contradiction as a distinction between “plant design
   attribute” and “cross-part fan-out.”
5. The audit certified that narrowed interpretation.
6. Nine days before the customer report, downstream research found the exact `R`/`a`/`kappa`
   fan-out and proposed a consumer workaround instead of escalating an upstream contract failure.

The central failure is therefore **wrong-oracle institutionalization**. The project did not merely
omit a test. It had the customer-shaped fixture and taught its tests, plan, audit, and later
research to call the broken topology correct.

### Is the library total AI slop?

**[AGENT] No. The whole library is not garbage. Its certification story for source identity and
off-design mutation is currently untrustworthy.**

There is real engineering here: generated modules execute; arithmetic anchors are independently
checked; several reviews caught genuine defects; fail-fast behavior exists; and the direct
usage-owned shared-producer case now converges correctly. Pinned design-point results remain valid
because all duplicated fields start with the same captured value
(`/tmp/handoff-20260803-200817.md:29-33`).

But this is not a harmless edge case either. Shared-source identity is central to parameter studies.
At that seam, the project produced a slop-like result: huge artifact volume, contradictory passing
requirements, tests that preserve representation instead of semantics, and audits that certify a
fixture-specific story after the implementation contradicts the written requirement.

Until this is fixed and the source-to-entry-point routes are audited, trust the library only for the
exact fixed-point and authoring shapes its tests exercise. Do not trust its broad claims about
backtracking, shared input identity, or parameter sweeps.

## The customer failure

The model declares `R`, `a`, and `kappa` once on the plant definition and binds each into both the
geometry and radial-build calculations:

- source declarations and geometry bindings:
  `/home/reid/1cfe/fusion-tea-stellarator-mbse-demo/models/designs/generic_mfe/mfe_plant.sysml:108-121`
- radial-build bindings:
  `/home/reid/1cfe/fusion-tea-stellarator-mbse-demo/models/designs/generic_mfe/mfe_plant.sysml:138-156`

The generated pipeline exposes two independent fields for each source:

- `...__geom__R`, `...__geom__a`, `...__geom__kappa`
- `...__rb__R`, `...__rb__a`, `...__rb__kappa`

The emitted evidence is at
`/home/reid/1cfe/fusion-tea-stellarator-mbse-demo/exploration/stellarator_e2e/generated/pipelines/mfe_stellarator.yaml:20-39`.

The behavior exists at both the demo's sysml-codegen pin `06d95f8` and current `fa9e0d0`; it is not
stale-pin drift (`/tmp/handoff-20260803-200817.md:13-27`).

The failure is silent at a design point. Both generated copies receive the same captured default.
It becomes wrong when a caller changes one public field and reasonably expects all consumers of the
one SysML source attribute to observe the change.

## Exact failure mechanism

### 1. Extraction does not establish the outer source identity reliably

For the self-named form `in availability = availability`, SysIDE can resolve the right-hand side to
the calculation's own input formal. The repository measured and pinned this exact behavior:

- the test states that the binding resolves to the calc's own parameter, not the outer part
  attribute (`tests/conformance/test_self_named_binding_trap.py:10-24,57-69`);
- the fixture is a `PartDef` literal plus a self-named calculation binding
  (`tests/fixtures/self_named_binding_trap/library.sysml:19-35`).

Current extraction also carries the written reference for later resolution. That was enough to fix
one direct `PartUsage`-owned shape. It does not by itself fix occurrence-overridden `PartDef`
attributes.

### 2. Virtual-binding rewrite changes the semantic route before backtracking

The virtual-binding rewrite extracts the leaf from each resolved source path and matches it to the
occurrence override. For a literal match it performs three mutations:

```text
binding_type = LITERAL
literal_value = occurrence override value
source_path = None
```

That is current production behavior
(`src/sysml_codegen/orchestration/pipeline_builder.py:342-369`). It is also an explicit architecture
requirement, REQ-VBR-03, and the rewrite is required to run before all downstream processing
(`docs/architecture/reference/12-virtual-binding-rewrite.md:19-30,92-121`).

The object may still contain written-form evidence, but the downstream literal route does not use it.
Operationally, shared-source identity has been removed from resolution before resolution begins.

### 3. The source-QN materializer cannot see the rewritten bindings

The supplied-value materializer runs later, at pipeline Step 5.65, while virtual binding rewrite runs
at Step 3.5
(`src/sysml_codegen/orchestration/pipeline_builder.py:900-917,986-1002`).

Its calculation-origin sweep skips every binding without `source_path`
(`src/sysml_codegen/resolution/supplied_values.py:494-513`). The VBR literal bindings therefore never
enter the source-qualified-name collapse mechanism.

Even without the eager literal rewrite, the self-named referent may still point to the calculation
formal. A correct repair must preserve or reconstruct the outer source identity; simply deleting the
three VBR mutations is not a demonstrated fix.

### 4. The backtracker does exactly what its literal contract says

For every literal binding, the backtracker mints:

```text
{consumer_usage_qualified_name}__{formal_parameter_name}
```

It then skips producer resolution
(`src/sysml_codegen/analysis/dependency_backtracker.py:439-467`). Two consumers necessarily become
two public entry points.

Reference bindings take a different path. They call the shared producer resolver and can reach the
occurrence-materialized source-qualified-name rule
(`src/sysml_codegen/analysis/dependency_backtracker.py:571-631`,
`src/sysml_codegen/resolution/producer_resolution.py:416-449`). That explains the observed split:
direct constraint references can converge on the source attribute while calc-usage rebindings become
per-consumer literals.

### 5. The initial suspect was a red herring

The handoff pointed to the D3/Step-4 comment in `usage_extractor.py`. That comment concerns diagnostic
handling for three-or-more-segment feature chains, not self-named literal fan-out
(`src/sysml_codegen/extraction/usage_extractor.py:790-809`). The defect is the interaction between
self-named extraction, virtual-binding rewrite, supplied-value materialization, and the literal arm
of backtracking.

## Regression or never-built?

**[AGENT] Never-built, with the failure becoming better masked over time.**

| Date | Change | Effect on this shape |
|---|---|---|
| 2025-12-31 | Initial backtracker, `36bd2c2` | Literals and terminal misses already minted consumer-local entry points. No shared-source proof existed. |
| 2026-02-10 | Hierarchy pipeline and VBR, `f49005c` | Introduced per-virtual-usage literal propagation. The first implementation matched a narrower bare-name form. |
| 2026-02-14 | VBR full-QN leaf matching, precursor commit `d9b23c4`, later squashed into `d6c725f` | Made resolved self-named paths match occurrence overrides, then cleared `source_path`. The current deterministic failure path was established. |
| 2026-02-15–22 | OutputRegistry and typed-dispatch refactors | Their gates emphasized old/new parity and byte-identical baselines. They preserved the existing public topology rather than proving source semantics. |
| 2026-07-05 | `self_named_binding_trap`, `84ae948` | Recorded the exact extraction defect but kept the fixture extraction-only, outside generated-package acceptance (`tests/conformance/test_self_named_binding_trap.py:23-24`). |
| 2026-07-06 | Supplied-value materializer, `df35289` | Added source-QN collapse for retained reference paths such as `driver.efficiency`; rewritten literals remained invisible. |
| 2026-07-06 | Fusion Tea acceptance, `36d3394`; audit, `e8840a8` | The real fixture exposed duplicate `gain` inputs. The test, plan, and audit declared the split intentional. |
| 2026-07-19 | Shared resolver and written-reference work, `46a9b15`, `7430aba` | Fixed convergence for a direct concrete `PartUsage`-owned attribute. The occurrence-indexed `PartDef` class remained explicitly unclaimed. |
| 2026-07-25 | Stellarator study research | Found exact `R`/`a`/`kappa` fan-out and proposed caller-side expansion rather than escalating the upstream contract conflict. |
| 2026-08-03 | First customer use of the study surface | Customer identifies the duplicate fields as a central semantic bug. |

No inspected revision could correctly collapse the exact composition. Before the current VBR route,
the self-reference still fell toward a consumer-local terminal entry point. After the rewrite, the
correct captured value made the incorrect identity harder to notice.

## How the review pipeline failed

### Failure 1: the design partitioned one semantic invariant into incompatible mechanisms

The July whole-plant design knew that VBR-03 produces per-consumer entry points and that the new
materializer produces source-QN entry points. It called them distinct siblings
(`.project/active/whole-plant-resolution/design.md:78-109,191-207`).

That taxonomy became an excuse not to ask the product-level question: **does one authored source
attribute produce one public parameter for every supported binding route?**

The resulting documentation presents both behaviors as valid:

- VBR requires literal rewrite and source-path clearing
  (`docs/architecture/reference/12-virtual-binding-rewrite.md:21-30`).
- SVM says differently named consumers collapse by source QN
  (`docs/architecture/verification-matrix.md:560-569`).
- the shared resolution matrix says the same reference resolves to the same producer across
  consumers (`docs/architecture/verification-matrix.md:328-336`).

All are marked PASS. The matrix proves selected routes, not the stated semantic invariant.

### Failure 2: component tests covered the axes separately, not their composition

The green tests are individually real:

- `shared_producer` proves one concrete `PartUsage`-owned attribute shared by one calculation and one
  constraint (`tests/fixtures/shared_producer/model.sysml:38-52`,
  `tests/conformance/test_shared_producer_convergence.py:36-65`).
- supplied-value unit tests prove two retained dotted references such as `driver.efficiency` dedupe
  to one synthetic source attribute (`tests/unit/test_supplied_values.py:96-125`).
- the Fusion Tea conformance test proves the same dotted source feeds differently named inputs
  (`tests/conformance/test_fusion_tea_snapshot.py:48-62`).
- VBR tests require every matched override to become a literal and lose `source_path`
  (`tests/conformance/test_virtual_binding_rewrite.py:338-400`).

The missing semantic cell was:

```text
PartDef attribute
+ concrete occurrence literal override
+ two self-named calculation consumers
+ one public input
+ off-default mutation observed by both consumers
```

The exact syntax existed in the real Fusion Tea fixture. What was missing was the correct oracle.

### Failure 3: the real acceptance test blessed the bug

The runtime test says:

> gain is emitted per-consumer ... NOT a cross-part fan-out that collapses by source QN

It selects `lcoe_calc__gain`, changes only that copy, and proves only LCOE moves
(`tests/runtime/test_fusion_tea_acceptance.py:37-43,113-125`).

This is not neutral coverage. It turns the defect into required behavior. The corpus-QN test also
requires Fusion Tea to contain a non-empty population of per-consumer entry points
(`tests/unit/test_producer_qn_rule.py:87-106`).

Five focused tests were run during this research:

- shared-producer convergence;
- dotted Fusion Tea fan-out collapse;
- one-copy Fusion Tea gain perturbation;
- VBR literal/source-path clearing;
- per-consumer mint reproduction across the Fusion Tea corpus.

All five passed together in 0.27 seconds. The suite simultaneously proves the intended invariant and
the opposite behavior because each claim is scoped to a different implementation route.

### Failure 4: implementation silently changed the meaning of the acceptance requirement

The acceptance spec said:

- source-QN keying collapses fan-out to one JSON key
  (`.project/active/fusiontea-acceptance/spec.md:39-48`);
- the perturbed key must survive that collapse (`:125-137,202-205`);
- a mechanism gap found during acceptance must be escalated to Item 2, not patched locally
  (`:175-184`).

The implementation plan then recorded the discovered duplicate keys and concluded that a plant
`DESIGN_ATTRIBUTE` was “not cross-part fan-out.” It perturbed only the LCOE key and left recirculation
untouched (`.project/active/fusiontea-acceptance/plan.md:311-323`).

That is a premise conflict resolved silently in favor of the implementation. The source was shared;
the code path was per-consumer. The plan changed the semantic category to preserve a green result.
This is exactly the failure mode the project's current Surfacing rule is meant to prevent.

### Failure 5: audit checked arithmetic and completion, not the contradicted topology

The audit certified SC-B because changing `lcoe_calc__gain` changed LCOE to the independently computed
number (`.project/active/fusiontea-acceptance/audit.md:42-60`). That proves the selected duplicate is
consumed. It does not prove that the one model source remains one parameter.

The audit repeats that no resolution code changed and declares “No slop or failure-honesty issues”
(`.project/active/fusiontea-acceptance/audit.md:75-84,100-107`). It never reconciles the plan's
per-consumer finding with the spec's source-QN contract or the requirement to escalate a mechanism
gap.

The independent arithmetic was good. The audit question was wrong.

### Failure 6: parity and baselines preserved the defect

The February registry work intentionally ran old and new resolution in parallel and required zero
divergence. Later refactors emphasized byte identity outside named forced changes. Those are useful
regression controls, but they answer “did output change?” rather than “is the output faithful to
SysML source identity?”

The project's own July discovery had already found that many tests could not fail and that matrix
PASS claims diverged from reality
(`.project/reports/20260706_pipeline-truth-epic-report.md:19-29`). Yet the epic close-out again made
strong general claims from route-specific tests: it said source-QN keying makes one attribute feeding
two inputs become one JSON key (`:79-100`) and said all items passed independent audit (`:31-41`).

The compatibility gates preserved a stable wrong interface.

### Failure 7: a later line of defense saw the customer bug and normalized it again

The 2026-07-25 Stellarator research explicitly says one SysML attribute fans out to `geom__R` and
`rb__R`, and that changing one copy creates an inconsistent point
(`/home/reid/1cfe/fusion-tea-stellarator-mbse-demo/.project/research/20260725-110828_study-failure-classes-and-mechanisms.md:21-27,37-47`).

It then classifies source-level axis expansion across entry-key sets as feasible with no upstream
change (`:125-137`). The research treated generated output as ground truth even though the upstream
architecture claimed source-QN convergence.

The customer was not the first observer. The customer was the first observer who refused the coping
strategy.

## What the massive refactors actually proved

They proved less than their summaries implied.

### What they did prove

- Old and new registry paths agreed on the selected corpus.
- Generated files stayed byte-identical except for named changes.
- Dotted cross-part references can share a source-QN entry point.
- A direct concrete `PartUsage`-owned attribute can be shared by a calculation and a constraint.
- Generated modules execute and reproduce fixed-point numerical anchors.
- Perturbing a selected emitted field changes the calculation that consumes that field.

### What they did not prove

- Every supported spelling and ownership form for one source attribute maps to one semantic producer.
- `PartDef` attributes remain identifiable through virtual instance expansion and occurrence
  overrides.
- A public parameter mutation reaches every consumer of the authored SysML source.
- A fixed-point numerical result implies correct off-design behavior.
- Old/new parity or captured-byte parity implies semantic correctness.

The reviews frequently certified a local theorem and the documentation promoted it to a universal
claim.

## What this says about library quality

### Confidence that remains justified

| Surface | Current confidence | Basis |
|---|---|---|
| Generated module arithmetic at pinned points | Moderate to high for tested modules | Independent hand calculations and executable acceptance tests exist. |
| Fixed-point package generation for committed fixtures | High for exact captured shapes | Large regression corpus and byte comparisons. |
| Dotted cross-part source-QN fan-out | Moderate for the tested routes | Unit, conformance, and real-fixture coverage agree. |
| Direct concrete `PartUsage` shared producer | Moderate for the exact fixture | Live and snapshot convergence tests exist. |

### Confidence that is not justified

| Surface | Current confidence | Reason |
|---|---|---|
| Public input identity across all supported SysML forms | Low | Known contradictory routes are both marked PASS. |
| `PartDef` + occurrence override + self-named calc binding | Failed | Customer case and Fusion Tea fixture reproduce the split. |
| Parameter sweeps and off-design studies | Unsafe until audited | One source can be changed for only a subset of consumers. |
| Verification-matrix breadth claims | Low | Rows name semantic invariants but tests certify selected syntax/mechanisms. |
| Audit/certification as evidence of completeness | Low at this seam | A direct spec contradiction was rationalized and certified. |

### The “AI slop” judgment

Calling the entire repository AI slop would erase evidence of working, carefully checked code. It
would also make the diagnosis less useful.

Calling this a small missed edge case would be false.

The accurate judgment is:

> The implementation is mixed-quality engineering with real working cores. The semantic-assurance
> process around backtracking and public input identity produced an AI-slop failure mode: artifacts
> multiplied faster than understanding, narrow examples were promoted to broad guarantees, and an
> observed contradiction was rewritten into the expected result.

The number of documents, commits, agents, tests, or reviewed lines is not evidence against that
judgment. In this case, volume increased confidence without increasing coverage of the governing
invariant.

## Blast radius

### Known safe result class

Pinned-point results stand because every duplicate begins with the same captured value. The stellarator
handshake and other fixed design-point anchors are not made numerically wrong by this defect
(`/tmp/handoff-20260803-200817.md:29-33`).

### Known unsafe result class

Any caller that mutates one emitted copy while assuming it represents the one SysML attribute can
create an internally inconsistent design point. This includes sweeps, optimization, sensitivity
analysis, and manual input edits.

The July IFE acceptance study swept source-level `gain` and efficiency fields used by the constraint,
while LCOE and recirculation calculations kept their consumer-local captured defaults. The verdict
agreement remains meaningful, but cost outputs on those rows are frozen-design-point outputs. It is
not yet known whether anything downstream consumed those costs
(`/tmp/handoff-20260803-200817.md:29-33,49-53`).

### Unknown class

The repository has not yet enumerated every ownership, specialization, override, and reference-form
combination that can route one semantic source to a public entry point. The safe boundary is therefore
the exact exercised fixtures, not the architecture's broad prose.

## Recommendations

These are **[AGENT]** recommendations. They are not owner-settled decisions.

1. **Treat this as a release-blocking semantic defect for studies.** Keep the stellarator study item
   gated. Do not hide the split behind consumer-side fan-out expansion.
2. **Correct the certification record before claiming a fix.** Mark the broad REQ-IR-07 and
   REQ-SVM-02 claims as partial or failed for occurrence-overridden self-named bindings. Amend the
   Pipeline Truth and Fusion Tea acceptance conclusions that imply universal one-source/one-key
   behavior.
3. **Make the customer shape the acceptance contract.** One `PartDef` source attribute, one concrete
   literal override, two self-named calculations, one generated public input. Changing that one input
   must change both consumer outputs. The test must inspect topology and execution.
4. **Fix provenance, not just emitted duplication.** Preserve or reconstruct source identity before
   VBR changes the binding route. A downstream key-dedup patch could merge unrelated literals and
   would leave the semantic model broken.
5. **Audit the whole emitted corpus by semantic source.** Find every case where one modeled source
   becomes multiple entry-point QNs, then classify each by ownership and binding route. Do not assume
   the customer case is the only one.
6. **Change review evidence from route examples to invariants.** For source identity, use a matrix of
   owner kind, declaration site, occurrence override, written reference form, consumer type, consumer
   count, and mutation result. Each supported cell needs a semantic test; unsupported cells need an
   explicit diagnostic or scope statement.
7. **Check the July IFE study outputs once.** Determine whether any downstream decision used LCOE or
   other cost values from swept rows. If so, correct the record: those costs were fixed-point values
   attached to swept constraint inputs.

More review stages are not the answer. The existing stages already encountered the evidence. The
answer is to stop the pipeline when evidence contradicts the semantic contract.

## Open questions

1. Did any downstream artifact or decision consume cost outputs from the July IFE swept rows?
2. Which other occurrence-indexed `PartDef` and qualified-reference combinations split source
   identity today?
3. Is written-reference plus occurrence-owner data sufficient to recover identity before VBR for all
   supported cases, or must extraction expose an explicit semantic source ID?
4. Which current verification-matrix rows depend on universal source identity and must be downgraded
   until the corpus audit completes?
5. Should the historical Fusion Tea acceptance artifact be amended in place or superseded by a
   correction report? The current artifact is materially misleading.

## Research method and evidence scope

This report used:

- the supplied handoff, read in full;
- current architecture and verification documentation;
- active and completed specs, designs, design reviews, plans, run reports, and audits;
- git history from the initial backtracker through current `fa9e0d0`;
- current production code and committed snapshots;
- the external Stellarator demo model, generated pipeline, and prior research;
- focused executable checks of the mutually inconsistent green tests.

No production code or fixtures were changed. The only new repository artifact is this report.
