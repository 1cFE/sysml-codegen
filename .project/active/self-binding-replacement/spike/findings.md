# Spike: binding-shape behavior on the shipped exact route

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
