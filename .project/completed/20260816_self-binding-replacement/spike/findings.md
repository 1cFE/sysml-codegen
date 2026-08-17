# Spike: binding-shape behavior on the shipped exact route

> **One headline below is superseded.** The 2026-08-15 addendum measures the *usage*-qualified
> spelling and finds a form that **does** resolve silently and wrongly (F-6). The summary sentence
> "No shape measured here resolves silently and wrongly" is true only of the shapes in the original
> table. Every original row stands as measured. Jump to
> [Addendum — 2026-08-15](#addendum--2026-08-15-the-usage-qualified-spelling).
>
> **F-6's repair sizing is superseded by F-7.** Addendum 2 measures *which layer* loses the
> occurrence — SysIDE and our `DeclarationId` keep the two references distinct, our `FeatureSlotId`
> collapses them — and the repair is **contained**, not "not contained" as F-6 estimated. See
> [Addendum 2 — F-7](#addendum-2--2026-08-15-which-layer-loses-the-occurrence-f-7).

**Date**: 2026-08-15 · **Branch**: `main` @ `6e3c18d` (codegen) / `1decd95` (agentic-mbse)
**Fixtures**: `.project/active/self-binding-replacement/spike/fixtures/` (throwaway, untracked)
**Driver**: `.project/active/self-binding-replacement/spike/run_probe.sh`
**Raw logs**: `.project/active/self-binding-replacement/spike/out/*.log`
**License**: `SYSIDE_LICENSE_KEY` loaded from `/home/reid/1cfe/agentic-mbse/.env` (len 37) before every
run; the driver aborts if it is absent. Every result below is a licensed live load.

---

## Summary of Findings

Three of the four expected behaviors reproduce exactly. The fourth — the `[HARD]`
`SI_OCCURRENCE_AMBIGUOUS` row — reproduces **only for one of the two authoring positions**, and its
current wording is falsified for the position the brief asked me to cover.

1. **Self-named (`in availability = availability`) is refused, and nothing is written.** Codegen
   fails pre-generation with `SI_SELF_BINDING` and leaves the output directory empty. The
   agentic-mbse level-2 validator independently returns an `ERROR`
   (`L2_SELF_NAMED_BINDING`, `success=False`) on the same model. Both paths refuse it. **Confirmed.**
2. **D-5 (names differ) lands on the outer attribute and the value arrives.** The generated pipeline
   wires the calc formal directly to an entry point keyed by the *supplying attribute*, and mutating
   the modelled value 0.85 → 0.42 moves the shipped default. **Confirmed, with the value proved.**
3. **D-7 (path-named) lands on that occurrence's feature.** `in driver_cost = driver.cost` produces
   entry point `…__plant__driver__cost = 12.5`. **Confirmed.**
4. **D-6 (owner-qualified) is position-dependent, and the `[HARD]` row is wrong as written.**
   See the contradiction section below. The row says the reference is refused when the consumer's
   context contains more than one leaf occurrence *of the qualifying definition*. Measured: what
   matters is whether the consumer sits **inside** an occurrence of that definition (resolves
   correctly, per occurrence, no diagnostic) or **outside/above** it (refused when more than one
   occurrence is reachable below the consumer's anchor). Two `'Plant'` occurrences with the binding
   authored inside `part def 'Plant'` generate cleanly and correctly, with each occurrence getting
   its own value.

**No shape measured here resolves silently and wrongly.** Every failure mode I could construct fails
loudly. Two of those loud failures are, however, badly reported — one escapes as an unhandled Python
traceback — and one *cross-path disagreement* is a real false positive that will block the migration
if D-6 is used. Details in "Findings called out separately."

---

## Question / Goal

For each authoring shape, on the shipped exact route at codegen HEAD: which feature does the
authored reference land on, and what concrete value or named diagnostic follows?

Confirmation means an observed entry-point value or a named diagnostic from the real CLI
(`sysml-codegen generate --models …`), not a successful exit code.

---

## The measurement table

| # | shape | authored spelling | feature the reference lands on | observed value / diagnostic | fixture |
|---|---|---|---|---|---|
| 1 | self-named | `in availability = availability` | the calc usage's **own `in` formal** | **refused pre-generation**: `SI_SELF_BINDING: S1SelfNamed__Plant__revenue_calc.availability`; exit 1; output directory **empty** | `s1_self_named` |
| 1b | self-named, agentic-mbse validator | same model | (name-based check) | `ERROR` `L2_SELF_NAMED_BINDING` on `S1SelfNamed::Plant::revenue_calc`, `success=False` | `s1_self_named` |
| 2 | D-5, names differ | `in availability_in = availability` | the **outer part attribute** `Plant::availability` | generates; entry point `S2NamesDiffer__plant__availability = 0.85`, `entry_type: design_attribute`; pipeline wires `availability_in: float s2_names_differ_params.S2NamesDiffer__plant__availability` | `s2_names_differ` |
| 2m | D-5, mutation proof | same, model value changed to `0.42` | same | entry point default moves to **0.42** — the referent is the attribute, not the formal | `s2m_names_differ_mutated` |
| 3 | D-7, path-named | `in driver_cost = driver.cost` | the `driver` occurrence's `cost` | generates; entry point `S3PathNamed__plant__driver__cost = 12.5` | `s3_path_named` |
| 4a | D-6, **inside** part def, 1 occurrence | `in availability = 'Plant'::availability` | the enclosing occurrence's `availability` | generates; `S4AQualOneOcc__plant__availability = 0.85` | `s4a_qual_one_occ` |
| 4b | D-6, **inside** part def, **2 occurrences** of the qualifying def | same spelling | **each occurrence's own** `availability` | generates, **2 modules**; `…plant_a__availability = 0.11` and `…plant_b__availability = 0.99`, each feeding its own calc node. **No diagnostic.** | `s4b_qual_two_occ` |
| 4c | D-6, inside part def, qualifying a **child** def with 2 leaf occurrences | `in unit_cost = 'Unit'::cost` | — | **refused**: `SI_OCCURRENCE_AMBIGUOUS: S4CQualMultiLeaf__plant__cost_calc: consumer context contains 2 leaf occurrences` | `s4c_qual_multi_leaf` |
| 4d | D-6, **outside** the part def, 2 occurrences below the consumer | `in availability = 'Plant'::availability` in an enclosing `part def 'Fleet'` | — | **refused**: `SI_OCCURRENCE_AMBIGUOUS: S8QualOutsideTwo__fleet__revenue_calc: consumer context contains 2 leaf occurrences` | `s8_qual_outside_two` |
| 4e | D-6, outside the part def, 1 occurrence | same | the single `plant_a` occurrence's `availability` | generates; `S9QualOutsideOne__fleet__plant_a__availability = 0.11` | `s9_qual_outside_one` |
| 5 | D-5 rename colliding with the calc def's own **out** parameter | `in availability_in = availability` where `Revenue` also declares `out attribute availability` | the calc's **own out formal** (producer cycle) | **unhandled traceback**: `GraphValidationError: SI_EDGE_DANGLING: typed producer dependency cycle`; no file/line, no binding named | `s5_sibling_formal` |
| 6 | D-6 reaching sideways | `in unit_cost = 'Unit'::cost` from a part with no local `'Unit'`, one `'Unit'` under a **sibling** subtree | the sibling's `the_unit.cost` | generates; `S6QualSiblingScope__plant__bop__the_unit__cost = 7.0` — resolves across a containment boundary the author never named | `s6_qual_sibling_scope` |
| 7 | D-5 rename colliding with the calc def's own **second in** parameter | `in availability_in = availability` where `Revenue` also declares `in attribute availability` | the calc's **own second in formal** | **refused**, but opaquely: `SI_OCCURRENCE_MISSING: … consumer context has no occurrence of leaf slot FeatureSlotId(root_declaration=DeclarationId(value=UUID('a784b41c-…')))` | `s7_sibling_in_formal` |

Exact command for every row (fixture name substituted):

```bash
cd /home/reid/1cfe/sysml-codegen
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
uv run sysml-codegen generate \
  --models .project/active/self-binding-replacement/spike/fixtures/<fixture> \
  --output .project/active/self-binding-replacement/spike/out/<fixture> \
  --package-name spike_pkg --overwrite
```

Row 1b was produced with `agentic_mbse.validation.level2_structure.validate_structure(<fixture dir>)`
under the same license (see `probe_validation.py` reproduction below).

---

## Findings called out separately

### F-1 — CONTRADICTS the spec's `[HARD]` `SI_OCCURRENCE_AMBIGUOUS` row (spec.md:125-129)

The row states: *"An owner-qualified reference is refused with `SI_OCCURRENCE_AMBIGUOUS` when the
consumer's context contains more than one leaf occurrence of the qualifying definition."*

**Row 4b falsifies that as written.** `part def 'Plant'` has two occurrences (`plant_a`, `plant_b`),
the binding `in availability = 'Plant'::availability` is authored inside `part def 'Plant'`, and the
route generates cleanly: two modules, two entry points, each occurrence reading its own value
(0.11 and 0.99). This is the authoring position the brief asked me to cover, and it is the position
the row's second sentence speculates about.

The measured rule, read off `elaborate.py:2299-2348` (`_resolve_leaf`) and confirmed by rows
4a–4e:

1. Walk the consumer's own scope lineage outward. If any scope in that lineage **owns the slot**,
   that occurrence wins — one target, no ambiguity, regardless of how many other occurrences of the
   definition exist elsewhere in the model. This is rows 4a and 4b.
2. Only if the lineage misses, search **descendants** of each lineage anchor, innermost first. If
   exactly one descendant occurrence carries the slot, it is selected silently (rows 4e and 6). If
   more than one does, `SI_OCCURRENCE_AMBIGUOUS` fires (rows 4c and 4d).

So the discriminator is the consumer's **position relative to the occurrences**, not the occurrence
count of the qualifying definition. A corrected row would read: *refused with
`SI_OCCURRENCE_AMBIGUOUS` when the consumer sits above more than one reachable leaf occurrence of the
qualifying definition and is not itself inside one of them.* "It never guesses" survives intact — no
row showed a guess.

Dependent conclusion parked: the spec's D-6 characterisation ("works only while the consumer's
context contains one applicable occurrence", spec.md:53-56) is *narrower than the truth* for the
inside-the-part-def position. Whether that changes the guidance's recommendation is a design call,
not mine.

### F-2 — the agentic-mbse validator FALSE-POSITIVES on the D-6 owner-qualified form

`s4a_qual_one_occ` — `in availability = 'Plant'::availability`, which codegen generates correctly —
is reported by `validate_structure()` as:

> `ERROR: Input 'availability' in calc 'S4AQualOneOcc::Plant::revenue_calc' binds to a same-named
> reference that resolves to the calc's own parameter, so the binding dead-ends.`

That is false. The two paths disagree: codegen's check is identity-based
(`source_evidence.py:130-138` compares referent `element_id` to the bound formal's), while
agentic-mbse's is name-based (`level2_structure.py:350`, `binding.source_path != binding.param_name`).
The qualifier never reaches `source_path`: `binding.py::_extract_reference_name` returns the
referent's bare `name`, so `'Plant'::availability` and `availability` are indistinguishable to it.

Measured directly:

```
== s4a_qual_one_occ   param= availability type= BindingType.REFERENCE source_path= 'availability'
== s1_self_named      param= availability type= BindingType.REFERENCE source_path= 'availability'
```

**Why this matters now:** the spec's success criterion requires the agentic-mbse path to refuse the
self-named form. It does — but it also refuses a form D-6 supports. If the guidance teaches owner
qualification at all, an author who follows it gets a spurious blocking ERROR from the validator.

**Repair size, honestly:** small and contained, in agentic-mbse only. Mirror codegen's identity
comparison inside `check_self_named_bindings` — compare the referent element of the member's
`feature_value_expression` against the member itself, instead of comparing names. That is roughly
one helper plus the changed condition in `level2_structure.py`, optionally exposing the referent on
`BindingInfo` in `binding.py`, plus a test per direction (self-named still flagged, qualified no
longer flagged). No codegen change. **Orchestrator's call** — the spec's disposition rule for this
class is `[AGENT]` grade.

### F-3 — an unhandled traceback where a diagnostic belongs (`s5_sibling_formal`)

A D-5 rename whose bare right-hand side collides with the calc def's own **out** parameter exits
with a raw Python traceback: `GraphValidationError: SI_EDGE_DANGLING: typed producer dependency
cycle`, thrown out of `graph.py:448` through `run_codegen`. It is loud, so nothing ships wrong, but
the message names no file, no line, and no binding. An author hitting this during migration has
nothing to act on.

`s7_sibling_in_formal` is the same family with the collision on a second **in** parameter. It is
caught properly as `SI_OCCURRENCE_MISSING`, but the detail is a bare
`FeatureSlotId(root_declaration=DeclarationId(value=UUID(...)))` — no name, no location.

Both matter for the migration: the collision they describe is exactly the residual risk the spec
notes for D-5 ("residual risk only if a rename collides with another calc member"). The prior probe
table never covered it. **Neither is silently wrong; both are reporting-quality defects.** I have
not fixed either.

### F-4 — the sideways reach (`s6_qual_sibling_scope`) — characterised, not called a defect

`'Unit'::cost` written inside `part def 'Power Block'`, which contains no `'Unit'`, resolves to
`plant.bop.the_unit.cost` (7.0) in a sibling subtree. Silent, and it crosses a containment boundary
the author never wrote. I am **not** calling this silently wrong: it is the only occurrence in the
model, it is what step 2 of the measured rule specifies, and adding a second `'Unit'` anywhere under
`plant` converts it into a loud `SI_OCCURRENCE_AMBIGUOUS`. It is worth a sentence in the guidance —
owner qualification does not mean "mine."

### F-5 — observation, low blast radius: agentic-mbse chain source paths are garbage

`extract_bindings` on `in driver_cost = driver.cost` returns a `source_path` of ~60 KerML library
segments (`'cost.result.self.involvedObjects.performers.…'`) rather than `driver.cost`.
`_build_chain_source_path` walks `expr.memberships` and collects every inherited membership name.
The only in-tree consumer of `BindingInfo.source_path` is `level2_structure.py:350`, which filters
`BindingType.CHAIN` out first — so nothing is currently broken by it. Recorded so it is not
rediscovered.

---

## Log

1. Read `spec.md`, the 2026-08-05 probe table, and the resolution code
   (`extraction/source_evidence.py`, `elaboration/elaborate.py:1990-2350`) to predict what each
   shape should do. Predictions were written before measurement; row 4b's outcome matched the
   prediction read off `_resolve_leaf`, row 5's did not (I expected a diagnostic, got a traceback).
2. Loaded the license and confirmed it (`KEY_LEN=37`, and `os.environ` sees it under `uv run`).
3. Authored the minimal fixtures under `spike/fixtures/`, one package per shape.
4. First run of `s4b`/`s4c` failed at load with
   `error (feature-value-overriding): Cannot override a binding feature value` — the part-def
   attribute used `= 0.85` (a binding) where `:>>` in the occurrence needs `default 0.85`. Fixed in
   the fixtures; this is a fixture-authoring fact, not a route finding.
5. Ran every fixture through the shipped CLI, recorded exit code, diagnostic, `inputs/*.json`,
   `contracts/model_contract.json`, and `pipelines/pipeline.yaml`.
6. Added `s5`/`s7` (formal-collision variants) and `s6`/`s8`/`s9` (D-6 position variants) after the
   first pass, to separate "how many occurrences" from "where the consumer sits" and to probe the
   D-5 residual risk the spec names.
7. Ran the agentic-mbse level-2 validator over the same fixture directories, then dropped to
   `extract_bindings` to explain the s4a false positive.

## Reproduction

```bash
cd /home/reid/1cfe/sysml-codegen

# All codegen rows (writes spike/out/<fixture>/ and spike/out/<fixture>.log):
.project/active/self-binding-replacement/spike/run_probe.sh            # all fixtures
.project/active/self-binding-replacement/spike/run_probe.sh s4b_qual_two_occ   # one fixture

# Entry-point values for a generated fixture:
cat .project/active/self-binding-replacement/spike/out/<fixture>/inputs/*.json
cat .project/active/self-binding-replacement/spike/out/<fixture>/pipelines/pipeline.yaml

# Rows 1b and F-2 (agentic-mbse validation path):
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
uv run python .project/active/self-binding-replacement/spike/probe_validation.py
```

`run_probe.sh` sources the license itself and aborts if `SYSIDE_LICENSE_KEY` is unset, so a green run
without a key is not possible here.

## Open Questions / Follow-ups

- **The `[HARD]` row needs rewording** (F-1). I did not edit `spec.md` — see the loop-closure note.
- **F-2 is a decision, not a finding I closed.** Small contained repair in agentic-mbse, or file it.
- **F-3's two reporting defects have no owner.** Neither is in this item's scope as written.
- **Not measured:** actual TEAx execution of a generated package. The D-5 value proof here is
  referent-identity plus mutation tracking through the sealed contract and pipeline wiring, which
  settles "which feature does it land on." End-to-end numeric execution belongs to the spec's spine
  criterion, not to this spike.
- **Not measured:** D-7 with a multiplicity-`[2]` child part; constraint-side consumers of these
  same forms.

## Loop closure — NOT done, deliberately

`/_my_spike` requires a back-reference in the triggering artifact. The triggering artifact is
`.project/active/self-binding-replacement/spec.md`, which is **tracked**, and this spike's brief sets
a hard bound: *"Change no tracked source, fixture, model, or document."* I did not edit it. The
orchestrator should insert, under the spec's Related Artifacts:

> - **Spike (measured):** `.project/active/self-binding-replacement/spike/findings.md` — re-establishes
>   the D-5/D-6/D-7 and self-named behavior by measurement on the shipped exact route. It confirms
>   `SI_SELF_BINDING` on both paths and the D-5/D-7 referents, and **falsifies the `[HARD]`
>   `SI_OCCURRENCE_AMBIGUOUS` row as written**: refusal depends on the consumer's position relative to
>   the occurrences, not on the occurrence count of the qualifying definition.

Everything this spike wrote lives under `.project/active/self-binding-replacement/spike/` and is
untracked. No tracked file in any repository was modified.

---

# Addendum — 2026-08-15: the usage-qualified spelling

**Date**: 2026-08-15 · **Branch**: `main` @ `991ae1e` (codegen) / `1decd95` (agentic-mbse)
**Fixtures**: `spike/fixtures/u1…u6` (throwaway, untracked)
**Driver**: `spike/run_addendum.py` — loads the license from `/home/reid/1cfe/agentic-mbse/.env`
itself and aborts if it is absent
**Provenance of the numbers**: the sandbox withdrew execution permission from this session partway
through the addendum. Every u1–u6 result below was produced by the **orchestrator running
`run_addendum.py`** against the fixtures authored here, on the shipped CLI at HEAD, with
`license key loaded (len 37)` confirmed in the run output. No number in this addendum was predicted,
inferred, or carried over from the reverted branches. Where I could not measure, I say so.

The original table is unchanged. This addendum adds rows; it corrects one headline, at the top of
the file.

---

## F-6 — SILENTLY WRONG: a usage qualifier does not select an occurrence, and it can name one thing while the route delivers another

**This is the highest-value finding in either pass, and it reverses the first pass's headline.**

Authored (`u6_usage_qual_crossnamed`), consumer inside `comp_b`:

```sysml
part def 'Plant' {
    part comp_a : 'Component' { :>> length = 3.0; }

    part comp_b : 'Component' {
        :>> length = 7.0;

        calc area_calc : AreaCalculation {
            in length_in = comp_a::length;      // the author means comp_a's 3.0
        }
    }
}
```

| | |
|---|---|
| value the author named | `comp_a::length` = **3.0** |
| value delivered | `U6UsageQualCrossnamed__plant__comp_b__length` = **7.0** |
| diagnostic | **none** — `exit=0`, 1 module, package generated and sealed |
| wiring | `length_in: float u6…_params.U6UsageQualCrossnamed__plant__comp_b__length` |

The written qualifier names `comp_a` unambiguously. The route discards that and resolves off the
consumer's own scope lineage, which hits `comp_b` first. The generated package is well-formed,
contract-sealed, and wrong.

**Corroborated independently by u5**, which needs no reading of intent: the author names `comp_a`
just as explicitly, but from *outside* both usages, and the route reports
`SI_OCCURRENCE_AMBIGUOUS: consumer context contains 2 leaf occurrences`. If the qualifier selected
the occurrence there would be nothing ambiguous — the author named one. u5 proves the qualifier's
occurrence information is discarded; u6 shows what that costs when a competing occurrence wins.

### Blast radius

Every `::`-qualified calc binding in the published agentic-mbse guidance is **usage**-qualified.
Seven sites, found by searching the vendored `agentic_mbse_data` tree (line-aligned with the copy
the design review cites):

| file | line(s) | binding |
|---|---|---|
| `docs/patterns/expose-pattern.md` | 19-20 | `in length = geometry::input_length;` |
| `docs/patterns/expose-pattern.md` | 66-67 | `in input_a = producer_part::param_a;` |
| `docs/patterns/expose-pattern.md` | 118-119 | `in length = geometry_module::input_length;` |
| `docs/patterns/cross-file-binding.md` | 60-61 | `in length = geometry_module::input_length;` |
| `docs/patterns/syntax-reference.md` | 93 | `in input_param = my_component::my_input;` |
| `docs/patterns/adr002-calculations.md` | 106-107 | `in length = component::length;` |
| `project_templates/MODELING_PROCESS.md.template` | 349-350 | `in volume = my_component::volume;` |

There are **zero** definition-qualified examples in the authored guidance. The
`'IFE Power Plant'::availability` spelling — the one the first pass measured, and the one ten sites
of the reverted migration used — appears in this tree only inside
`reverted/fusion-tea-model-migration.patch`.

### Are the published examples correct?

**All seven share u1's topology, not u6's**: in every one, the calc usage is authored *inside the
very usage the qualifier names*, binding to a sibling attribute in that same body. So the qualifier
and the consumer's lineage point at the same occurrence, and all seven resolve to the value the
reader expects. `u1_usage_qual_self` reproduces that topology verbatim and generates correctly —
`U1UsageQualSelf__component__length = 3.0`, wired straight into the formal.

**They are correct, but for the wrong reason.** The qualifier is doing one job in those examples and
not the other:

- **It does bypass shadowing** (name resolution). In `in length = component::length` the formal is
  also called `length`; a bare `length` there is the self-binding shape that `s1_self_named` shows
  is refused as `SI_SELF_BINDING`. The qualifier is genuinely load-bearing for *which declaration*
  the name reaches. This is real, and the guidance is right about it.
- **It does not select the occurrence.** Which *instance* supplies the value is decided entirely by
  the consumer's position (u2, u3, u3b, u5, u6). In the published examples the qualifier happens to
  agree with the position, so the distinction is invisible.

That invisibility is the hazard. The examples teach a shape whose natural generalization — "name the
part you want the value from" — is false, and fails silently the first time an author names a usage
other than their own enclosing one. Nothing in the published text marks the boundary.

### Repair sizing — honest, and NOT contained

The obvious check is: *when the authored reference carries a qualifier, verify the resolved
referent's owner is the occurrence the qualifier names, and refuse when it is not.* Measured against
what the code actually has, that reaches into resolver semantics. Three reasons, in increasing order
of cost:

1. **The qualifier's kind is not recorded.** A check must distinguish a *usage* qualifier
   (`comp_a::length` — names one instance, so disagreement is a defect) from a *definition*
   qualifier (`'Plant'::availability` — names no instance at all). For the definition spelling, s4b
   and s9 show the route legitimately selects an occurrence the author never named, and that is
   correct behavior this item must not break. So the check needs a new qualifier-kind field on
   `SourceReferenceEvidence` (`extraction/source_evidence.py`), populated at extraction.
2. **Mapping the named usage to its occurrence is the resolver's own job.** Given a usage-kind
   qualifier, deciding which occurrence(s) of that usage are in play under the consumer's scope is
   exactly what `_select_occurrences` (`elaboration/elaborate.py:2158`) does. A check cannot sit
   beside that; it re-enters it.
3. **The multiplicity case is a policy question, not a mechanical one.** When the named usage itself
   has several occurrences (u3's `component[2]`), what "the occurrence the qualifier names" even
   means is undefined. Someone has to decide.

The structural reason none of this is cheap: `_resolve_leaf` (`elaboration/elaborate.py:2299`) takes
a `DeclarationId` and a consumer scope. **The written qualifier is not one of its arguments.** It
cannot influence the answer because it never arrives. *(Internals cited to explain the measured
behavior only; the finding rests on u5 and u6 at the shipped surface.)*

A genuinely smaller option exists, and it is a support-policy change rather than a bug fix: **permit
only the u1 topology** — refuse any usage-qualified reference whose qualifier does not name the
consumer's own enclosing occurrence. That matches all seven published sites, needs only item 1 plus
a scope comparison, and turns u6 into a loud refusal. But it narrows D-6, and `spec.md` Non-Goals
put "changing D-4 through D-7 support policy" out of this item.

**Not implemented, not chosen.** Both options are recorded so the owner can price them. The
disposition is the owner's.

### Surfaced, not resolved

F-6 contradicts the epic's `[OWNER]`-grade critical success factor — *an unsupported authored form
fails loudly before generation*. Here a form resolves quietly and produces a sealed package carrying
a value the model never asked for. It is also the direct negation of the spec's spine criterion and
of `P-001`: mutating `comp_a.length` moves nothing downstream, while `comp_b.length` drives a
calculation that never named it. **Dependent conclusions are parked.** The orchestrator reports this
is already surfaced to the owner. This spike does not resolve it in either direction.

---

## Measurement table — usage-qualified spelling (u1–u6)

| # | position | authored spelling | feature the reference lands on | observed value / diagnostic | fixture |
|---|---|---|---|---|---|
| u1 | consumer **inside** the qualifying usage, 1 occurrence (the published topology) | `in length = component::length` | the enclosing `component` occurrence's `length` | generates; `U1UsageQualSelf__component__length = 3.0` (+ `__width = 4.0`), wired `length: float …__component__length` | `u1_usage_qual_self` |
| u2 | consumer inside it, **2 occurrences** of the enclosing definition | `in length = component::length` inside `part def 'Plant'`, two Plants | **each occurrence's own** `component.length` | generates, **2 modules**; `…plant_a__component__length = 11.0`, `…plant_b__component__length = 99.0`. No diagnostic. | `u2_usage_qual_two_owner_occ` |
| u3 | consumer **beside** a qualifying usage of multiplicity 2 | `in length = component::length`, `part component : 'Component'[2]` | — | **refused**: `SI_OCCURRENCE_AMBIGUOUS: U3UsageQualMultiOcc__plant__area_calc: consumer context contains 2 leaf occurrences` | `u3_usage_qual_multi_occ` |
| u3b | multiplicity-1 control for u3 | same, `[1]` | the single occurrence | generates; `U3BUsageQualSingleOcc__plant__component[0]__length = 3.0`, wired `…component_0__length` — the ADR-001 arrayed-child key form | `u3b_usage_qual_single_occ` |
| u4 | qualifier names a **package-level** usage, consumer inside another part def | `in length = shared_component::length` | — | **refused**: `SI_OCCURRENCE_MISSING: U4UsageQualPkgSibling__plant__area_calc: consumer context has no occurrence of leaf slot FeatureSlotId(…)` | `u4_usage_qual_pkg_sibling` |
| u5 | consumer **above** two sibling occurrences, one named explicitly | `in length_in = comp_a::length`, `comp_a`/`comp_b` beside it | — | **refused**: `SI_OCCURRENCE_AMBIGUOUS: U5UsageQualNamedSibling__plant__area_calc: consumer context contains 2 leaf occurrences` — the explicit name does not disambiguate | `u5_usage_qual_named_sibling` |
| u6 | consumer **inside** `comp_b`, naming `comp_a` | `in length_in = comp_a::length` | **`comp_b`'s** `length` — the consumer's own enclosing occurrence | **generates, exit 0, no diagnostic**; `U6UsageQualCrossnamed__plant__comp_b__length = 7.0`. Author meant 3.0. **See F-6.** | `u6_usage_qual_crossnamed` |

Command for every row:

```bash
cd /home/reid/1cfe/sysml-codegen
uv run python .project/active/self-binding-replacement/spike/run_addendum.py          # all u* fixtures
uv run python .project/active/self-binding-replacement/spike/run_addendum.py u6_usage_qual_crossnamed
```

---

## Does the F-1 position rule hold for both spellings?

**Yes — identically, message for message.** Every position measured for the definition-qualified
spelling has a usage-qualified twin with the same outcome and the same diagnostic text:

| position | definition-qualified | usage-qualified | outcome |
|---|---|---|---|
| consumer inside, 1 occurrence | s4a → 0.85 | u1 → 3.0 | resolves to the enclosing occurrence |
| consumer inside, 2 occurrences of the owner | s4b → 0.11 / 0.99, 2 modules | u2 → 11.0 / 99.0, 2 modules | resolves per occurrence, **no diagnostic** |
| consumer above 2 reachable leaf occurrences | s4c, s8 → `SI_OCCURRENCE_AMBIGUOUS: … contains 2 leaf occurrences` | u3, u5 → same code, same wording | refused |
| consumer above 1 reachable occurrence | s9 → 0.11 | u3b → 3.0 | resolves, silently, to the one found |
| no reachable occurrence of the leaf | s7 → `SI_OCCURRENCE_MISSING: … no occurrence of leaf slot FeatureSlotId(…)` | u4 → same code, same detail shape | refused |

The F-1 rule stated in the first pass holds unchanged for both:

1. Walk the consumer's own scope lineage outward; the first scope that owns the slot wins outright.
2. Only on a lineage miss, search descendants of each lineage anchor innermost-first — one candidate
   resolves silently, more than one raises `SI_OCCURRENCE_AMBIGUOUS`.

u6 adds the sting the first pass could not see: **step 1 can win over an explicitly named
occurrence.** That is not a new rule. It is the same rule, measured against a spelling that carries
information the rule ignores.

## Distinct shape, or same shape with a different qualifier?

**Same shape, different qualifier.** One authoring shape — a qualified bare reference — with two
spellings that differ only in what the qualifier is written against.

The grounds are the position table above: ten measurements across five positions, and the two
spellings agree on every one, including the exact diagnostic wording. Nothing downstream of name
resolution distinguishes them.

The qualifier has exactly one measured effect and one measured non-effect, and this is what the
guidance has to teach:

- **Effect — it chooses the declaration.** It bypasses shadowing. Without it, `in length = length`
  is `SI_SELF_BINDING` (s1). This is the whole reason the published examples need it.
- **Non-effect — it does not choose the instance.** Occurrence selection is positional in every
  measured case, for both spellings (u2, u3, u3b, u5, u6; s4b, s9).

*(Explanation only, from internals: both spellings arrive as a `FeatureReferenceExpression` resolving
to a single leaf declaration, so `_resolve_semantic_reference` takes its `len(segment_ids) == 1`
branch into `_resolve_leaf`, which never sees the written qualifier. The claim above rests on the
shipped-surface rows, not on this paragraph.)*

**Consequence for the guidance:** teach one rule, not two, and state the non-effect explicitly. The
docs must not describe a qualifier as naming where the value comes from. It names *which
declaration* you mean; *which instance* you get is decided by where the calculation sits.

## What u4 and u5 mean for the guidance

These two bound the hazard, and they are why F-6 is narrow rather than everywhere.

- **u4 — a qualifier naming a package-level sibling misses entirely.** `shared_component::length`
  from inside another part definition is refused with `SI_OCCURRENCE_MISSING`. Naming a shared
  component does not reach it; there must be a common *occurrence* ancestor. Contrast `s6`, where
  the sibling sat under a shared `plant` occurrence and did resolve (7.0, silently, across a
  containment boundary). So "reference it by name from anywhere" is not a supported idiom, and the
  guidance should not imply it.
- **u5 — naming a sibling from outside is loud, not silent.** Two candidate occurrences below the
  consumer produce `SI_OCCURRENCE_AMBIGUOUS`. The author gets told.

**Therefore the silence in u6 has a precise trigger: the consumer sits inside a competing
occurrence.** The lineage hit at step 1 short-circuits before the descendant search that would have
raised the ambiguity in u5. Same model shape, same two candidate occurrences — move the calc from
`'Plant'`'s body into `comp_b`'s body and a loud refusal becomes a wrong number.

The guidance sentence that follows: *a qualifier does not select an occurrence. If your calculation
sits inside one occurrence and you qualify by another, you silently get your own.*

## Addendum log

1. Searched the published agentic-mbse guidance for `::`-qualified calc bindings. Found seven, all
   usage-qualified, all sharing one topology; found zero definition-qualified examples. This is what
   made the addendum necessary: the first pass measured the spelling nobody publishes.
2. Authored u1–u6 to cover the four requested positions plus two constructions aimed at the
   silent-wrong question — u5 (explicit name, consumer outside) and u6 (explicit name, consumer
   inside a competitor). u6 was designed specifically to test whether the qualifier is load-bearing
   for occurrence selection.
3. Execution permission was withdrawn from this session mid-addendum. Stopped rather than write
   predicted numbers; the orchestrator ran `run_addendum.py` and returned the output transcribed
   above.
4. Read the results back against the fixture sources before writing, and against the first pass's
   position table to build the twin comparison.

## Addendum open questions

- **F-6's disposition is unowned.** Two options are priced above; neither is implemented.
- **Not measured: the multiplicity case for a *named* qualifier.** u3 shows `component[2]` is
  ambiguous when the qualifier names the multiplicity-2 usage itself. What a qualifier naming one
  occurrence of an arrayed usage should mean is undefined, and is item 3 of the repair sizing.
- **Not measured: whether u6's shape occurs in fusion-tea or stellarator.** The corpus scan that
  would answer it is a prevalence question, not a behavior question, and this spike did not run it.
  It matters for how urgent F-6 is.
- **Not measured: constraint-side consumers** of the usage-qualified spelling. Still out of scope,
  as in the first pass.
- **Loop closure remains open**, for the same reason as the first pass: `spec.md` is tracked and the
  brief forbids editing tracked documents. The back-reference text at the end of the original
  findings should now also name F-6 — the usage-qualified spelling is the one the guidance publishes,
  and it resolves silently and wrongly when the consumer sits inside a competing occurrence.

---

# Addendum 2 — 2026-08-15: which layer loses the occurrence (F-7)

**Answer, one line: DISTINCT at SysIDE and still distinct at our `DeclarationId`; COLLAPSED at our
`FeatureSlotId`. The information reaches us intact and our own code discards it, two layers in.
This is our defect — not a SysIDE bug and not a KerML mismatch.**

**Date**: 2026-08-15 · **Branch**: `main` @ `991ae1e`
**Probe**: `spike/probe_referent_identity.py` (internals by design) · **Fixture**:
`spike/fixtures/u7_both_spellings` (authors both `::` spellings and both `.` spellings in one model),
plus `s3_path_named` for the chain contrast
**Provenance**: execution permission was again unavailable to this session; the orchestrator ran the
probe and returned the output transcribed below. Spec citations are read directly from
`agentic_mbse_data/docs/sysmlv2/SysML_KerMLSpec/full_document.md` and cited by line.

## The measurement

```
  pair_calc.a_len vs pair_calc.b_len       (comp_a::length vs comp_b::length)
      same python object     = False
      same SysIDE elem id    = False
      same OUR DeclarationId = False
      same OUR FeatureSlotId = True    <-- the single point of loss

  usage comp_a, owned member 'length'   ReferenceUsage
      element_id     = 936d7879-82e1-5bcf-92b8-773d6f67b37d
      qualified_name = U7BothSpellings::Plant::comp_a::length
      owner          = U7BothSpellings::Plant::comp_a
      owned_redefinitions -> Component::length (6093ae42-…)
      OUR DeclarationId = 936d7879-…      OUR FeatureSlotId = 6093ae42-…

  usage comp_b, owned member 'length'
      element_id     = d7d38390-79be-56a3-876f-3c1a7f4d41e7
      qualified_name = U7BothSpellings::Plant::comp_b::length
      owner          = U7BothSpellings::Plant::comp_b
      owned_redefinitions -> Component::length (6093ae42-…)
      OUR DeclarationId = d7d38390-…      OUR FeatureSlotId = 6093ae42-…
```

Both usage-owned redefinitions normalize to `6093ae42` — `Component::length`, the root of the
redefinition chain — at `elaborate.py:2315` (`slot = self._slots.slot_of(declaration_id)`) via
`occurrence.py:73` → `_root_of` (`occurrence.py:116-133`). After that line the qualifier is
unrecoverable and positional search over the slot is the only thing left.

**The standard agrees with SysIDE.** KerML §7.3.4.5 (`full_document.md:1681`): when a type owns a
redefining feature, the redefined feature is "not inherited and [is], instead, replaced by the
redefining feature"; (`:1689`) an unnamed redefining feature "is implicitly given the same name …
used in name resolution, just as explicitly declared names would be." §8.2.3.5.1 step 3 (`:3095`)
then resolves the last segment against that namespace. So `comp_a::length` *must* denote comp_a's
own feature, and the measurement shows SysIDE does exactly that. The prediction recorded before the
run held.

## Correction to F-6 — the layer is now attributed, and one of my two candidate sites is acquitted

F-6 named two places the distinction could die and said the repair was **not contained**. The
measurement corrects both claims:

- **`binding_evidence.py:211-221` is NOT where it dies.** The one-segment fact preserves element
  identity — our `DeclarationId` is still distinct for the two spellings. What remains true is
  narrower and matters for the repair: because `reference_evidence` builds `root = segments = leaf`,
  there is no *root segment* to anchor on, so the occurrence information arrives not as a path but
  as the leaf declaration's **owner** (`…::Plant::comp_a`). It is present; it is just somewhere the
  resolver never looks.
- **`elaborate.py:2315` is the single point of loss**, as predicted.
- **"Not contained" was wrong**, and it was wrong because it rested on the belief that the qualifier
  never reached us. See the re-derived sizing below.

## Why the dot path lands correctly, when its leaf collapses too

The probe shows the dot pair collapses at `FeatureSlotId` as well
(`dot_calc.a_len vs dot_calc.b_len: same FeatureSlotId = True`). So the slot collapse is not by
itself the bug. The difference is what happens *before* the leaf lookup.

For `driver.cost` the probe shows a **two**-segment fact:

```
      expression metatype = FeatureChainExpression
      OUR semantic_reference.segments = 2 segment(s)
          segment[0] = S3PathNamed::Plant::driver     (the root usage)
          segment[1] = S3PathNamed::Driver::cost
      expr.operands: ['FeatureReferenceExpression'] -> S3PathNamed::Plant::driver
```

Two segments means `_resolve_semantic_reference` skips its one-segment shortcut
(`elaborate.py:2070`) and calls `_contextualize_root` (`:2119`), which enumerates the **occurrences
of the root usage** and selects one, then `_transition` (`:2278`) steps from that occurrence to the
leaf. The leaf lookup is therefore scoped to an occurrence that is already fixed, and inside one
occurrence a slot is unique by construction — collapsing it costs nothing.

For `comp_a::length` there is no root segment, so `_resolve_leaf` has to *find* a scope, and the
only thing it has to find it with is the collapsed slot. **The slot is being asked to do occurrence
selection, which is precisely what the collapse destroyed.**

Stated once: *the slot collapse is harmless when an occurrence is already fixed, and fatal when the
slot is the only thing left to pick an occurrence with.* The dot form fixes the occurrence
structurally; the `::` form, as we record it, has nothing to fix it with.

This also matches the standard's own account of the two notations, which is why the difference is
structural rather than incidental. A qualified name "does not appear in the corresponding abstract
syntax — instead, the abstract syntax representation contains an actual reference to the identified
Element" (§8.2.3.4, `:3065`). A feature chain keeps every segment as a real chaining feature
(§7.3.4.6, `:1703`) and the chain *expression* evaluates the referent "in the context of each of the
result values of the primary expression" (§7.4.9.3, `:2437`). The `::` path is gone by design in any
conforming tool; what survives is only *which element was picked* — and that element, measured
above, carries its owning usage.

## Repair sizing — re-derived from the measured layer: CONTAINED

F-6's sizing assumed a check would have to reconstruct occurrence semantics for `::` from a written
string. It does not. The resolved leaf already carries its owning usage, so the repair is a
recognition step, not an invention.

**What it compares.** The resolved leaf declaration's owner. When that owner is a *part usage*
(`…::Plant::comp_a`) rather than a part definition, the leaf is a usage-owned redefinition and its
owning usage **is** the occurrence anchor. Measured as available: `owner` and
`owned_redefinitions -> Component::length` are both on the referent at extraction time.

**Two candidate sites.**

- **(a) `_resolve_leaf` (`elaborate.py:2299`)** — one branch ahead of the lineage loop: resolve the
  owning usage's occurrence, then `_target_for_slot` against *that* occurrence instead of searching.
- **(b) `reference_evidence` (`binding_evidence.py:197-231`)** — emit a two-segment fact when the
  referent's owner is a usage, so `comp_a::length` takes the same route `comp_a.length` already
  takes. This reuses `_contextualize_root`/`_select_occurrences` wholesale, adds no new selection
  logic, and is principled rather than expedient: §7.3.4.5 and §7.3.4.6 make the two spellings
  denote the same feature here, so routing them the same way is what the standard implies.

**The normalisation stays.** The slot collapse is not gratuitous — it is what makes a redefinition
and the feature it redefines one slot, which `effective_declaration` (`occurrence.py:75-100`)
depends on and which occurrence identity itself is built from (`OccurrenceStep.containment_slot`).
Neither option changes slot semantics.

**Blast radius.**

- `OccurrenceId.to_wire()` (`identity.py:108-113`) encodes `containment_slot.root_declaration`, so
  slot roots are baked into every serialized occurrence id and every snapshot fixture. **Neither
  option touches that**, which is the strongest argument for (b) over anything that would re-scope
  slots: no wire-format break, no snapshot re-capture beyond fixtures whose wiring legitimately
  changes.
- Still slot-based and unaffected: `_target_for_slot`, `_transition`, the `_resolve_leaf` lineage
  loop, and the redefinition-family invariant.

**Does the definition-qualified case survive? Yes, untouched.** `'Plant'::availability` (s4b, s9)
resolves to a leaf owned by a *part def*, so the new branch never fires and the positional search
still runs — which is correct there, because a definition qualifier names no occurrence and the
route legitimately picks one the author never named. **This retires F-6's item 1:** no new
"qualifier kind" field is needed. The owner metatype of the resolved leaf already discriminates the
two spellings. F-6's item 2 was right that the fix re-enters `_select_occurrences`, but under (b)
that is reuse, not reinvention.

**Does the arrayed case survive? Same answer as today, and F-6's item 3 was overstated.** Under (b),
u3's `component::length` would anchor on segment 0 = `component`, whose two occurrences produce
`SI_OCCURRENCE_AMBIGUOUS` through the existing selector — the same refusal u3 gets now, reached by
the same code path the dot form would use. No new policy has to be invented. **Caveat, stated
because it is unmeasured:** I probed referent identity only for u7. In u3 the usage has no body, so
its referent is most likely the inherited `Component::length` (owner = part def) and the branch
would not fire at all; either way the outcome is today's refusal, but which of the two paths it
takes is not measured.

**Honest residuals.**

- The count of tracked fixtures and baselines whose wiring would legitimately change is
  **unmeasured**. It needs a corpus scan for `usage::feature` bindings where the consumer sits
  outside the named usage. This spike did not run one.
- Whether the u1 published topology is bit-for-bit unchanged under (b) is **unmeasured**. It should
  be — segment 0 would be the consumer's own enclosing usage — but "should be" is not a measurement.
- F-2 (the agentic-mbse validator false positive) is independent of F-7 and unaffected.

**Not implemented, and no patch proposed.** The disposition is the owner's.

## Does this change the guidance? No — and it strengthens the `.` recommendation

The owner's settled choice to teach `.` for the cross-part case is **orthogonal to F-7 and survives
it intact**, for three reasons:

1. `.` is correct on the shipped route today. `::` would need a code change the owner has not
   dispositioned, and that change is outside this item's scope.
2. `.` carries occurrence intent structurally and portably — §8.2.3.4 (`:3065`) says the `::`
   qualification part is absent from the abstract syntax in any conforming tool, so `.` is the
   spelling whose meaning does not depend on our resolver's behavior.
3. If the repair later lands, `.` stays correct. Guidance authored now needs no rewrite after.

**What F-7 does change is the reason the guidance should give.** Do not write that `::` "doesn't
work" — it does, in the u1 topology all seven published examples use, and the standard says it
denotes exactly what the author means. The accurate statement is that the *shipped route* mis-handles
the general case: a usage qualifier names an occurrence, and our resolver currently ignores it. So
teach `.` because it names the occurrence, and mark `::` as safe only when the qualifier names your
own enclosing usage — which is the boundary F-6 already established and which no published example
crosses.

## Addendum 2 log

1. Read KerML §7.3.4.5, §7.3.4.6, §8.2.3.4 and §8.2.3.5 directly and recorded the predicted answer
   (distinct) **before** the probe ran, so the measurement could falsify it.
2. Traced the code path by reading: `reference_evidence` → one-segment fact → `_resolve_semantic_
   reference` shortcut → `_resolve_leaf` → `slot_of` → `_root_of`. Named two candidate loss sites.
3. Authored `u7_both_spellings` so both spellings and both dot forms are real authored bindings in
   one model, from a symmetric position, and wrote `probe_referent_identity.py` to compare identity
   at three layers.
4. Execution was unavailable; the orchestrator ran the probe. The result confirmed the prediction
   and **acquitted one of the two candidate sites**, which in turn falsified the "not contained"
   sizing recorded in F-6.

## Addendum 2 open questions

- **Disposition of F-6/F-7 is the owner's.** Two contained options are priced; neither implemented.
- **Unmeasured:** the corpus count of affected `usage::feature` bindings; whether u1's output is
  unchanged under option (b); u3's actual referent owner.
- **Unmeasured:** whether any tracked fixture depends on today's positional behavior for a
  usage-qualified reference — i.e. whether the repair would be a silent behavior change somewhere
  that is currently green.
- **Loop closure still open**, same reason as both earlier passes: `spec.md` is tracked and the
  briefs forbid editing tracked documents. The back-reference should now read that the spike
  measured the defect to our own slot normalisation at `elaborate.py:2315`, with SysIDE and KerML
  both exonerated.
