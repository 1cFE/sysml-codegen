---
date: 2026-08-15T13:46:15-07:00
researcher: Codex
topic: "Assessment of qualified-binding defect attribution and recommendations"
tags: [research, elaboration, source-identity, qualified-reference]
status: complete
last_updated: 2026-08-15
---

# Research: Qualified-binding defect attribution

**Date:** 2026-08-15
**Researcher:** Codex
**Research Type:** Codebase / architecture / defect assessment

## Research Question

`[OWNER-VERBATIM]` “I need you to read and assess
`.project/reports/20260815-1338_qualified-binding-defect-attribution.md`. Do you agree with the
findings? Research the code. Do you agree with the recommendations?”

## Summary

- `[AGENT]` **Agree with the central attribution.** In the measured local-redefinition case,
  SysIDE resolves `comp_a::length` and `comp_b::length` to distinct usage-owned elements. Codegen
  preserves those declaration IDs, then its one-segment resolver reduces both to one feature slot
  before choosing an occurrence. That lets consumer position override the usage the author named.
- `[AGENT]` **Qualify “one line.”** `elaborate.py:2315` is the first harmful identity collapse on
  this route. Slot normalization is intentional elsewhere. The defect is the combination of the
  one-segment shortcut and positional leaf resolution before the usage owner is contextualized.
- `[AGENT]` **Reject repair option (b) as the preferred implementation.** Synthesizing a
  two-segment path in `binding_evidence.reference_evidence` rewrites extraction evidence and fixes
  only calculation-input bindings. Aliases, computed attributes, and constraint expressions build
  their own one-segment facts and would retain the defect.
- `[AGENT]` **Prefer a shared elaboration-layer repair.** Use the exact leaf's owner ID when that
  owner is a `PartUsage`, contextualize that occurrence, then resolve the slot inside it. Preserve
  today's definition-owned path. Prove redefined containment, multiplicity, bare usage-owned
  references, and snapshot effects before accepting the change.
- `[AGENT]` **Agree with sequencing, with two corrections.** Run a semantic corpus assessment first,
  publish the rename/dot guidance, keep the fusion-tea D-5 migration, and fix this in a separate
  bounded item. A raw count is not enough to decide blast radius, and the current-defect warning in
  the proposed guidance will need removal or revision after the fix.

## Detailed Findings

### 1. The measured defect is in codegen, not SysIDE

The live licensed identity probe reproduced the report's decisive result on current `main`:

- `comp_a::length` resolves to `936d7879-82e1-5bcf-92b8-773d6f67b37d`, owned by `comp_a`.
- `comp_b::length` resolves to `d7d38390-79be-56a3-876f-3c1a7f4d41e7`, owned by `comp_b`.
- Codegen's `DeclarationId` values remain distinct.
- Both declarations map to slot root `6093ae42-e366-5c66-b26a-5b4194b42f8a`, the redefined
  `Component::length` family.

The fixture authors the two local redefinitions and both spellings at
`.project/active/self-binding-replacement/spike/fixtures/u7_both_spellings/model.sysml:21-33`.
The probe follows SysIDE identity into codegen at
`.project/active/self-binding-replacement/spike/probe_referent_identity.py:55-90` and compares the
layers at `:112-160`.

This matches the code:

- `DeclarationId` wraps the exact stable SysIDE UUID at
  `src/sysml_codegen/elaboration/identity.py:66-82`.
- The companion extraction fact retains leaf ID, owner ID, owner classification, and redefinition
  endpoints at `../agentic-mbse/src/agentic_mbse/sysml/data_models.py:55-74` and
  `../agentic-mbse/src/agentic_mbse/sysml/expression.py:639-678`.
- `reference_evidence` keeps that referent as a one-segment semantic reference at
  `src/sysml_codegen/extraction/binding_evidence.py:197-231`.
- `_exact_reference` still carries the exact declaration at
  `src/sysml_codegen/elaboration/elaborate.py:2050-2060`.

KerML supports the report's reading of this local-redefinition shape. A redefining feature replaces
the inherited feature, an unnamed redefining feature gets the redefined feature's name for name
resolution, and the final segment of a qualified name resolves in the qualifier's namespace
(`full_document.md:1681`, `:1689`, `:3093-3097`). SysIDE's two exact referents are consistent with
those rules.

### 2. The silent wrong result also reproduces

A clean licensed CLI generation of `u6_usage_qual_crossnamed` completed and sealed with no
diagnostic. The model writes `comp_a::length`, where `comp_a.length = 3.0`, from inside `comp_b`,
where `comp_b.length = 7.0`
(`.project/active/self-binding-replacement/spike/fixtures/u6_usage_qual_crossnamed/model.sysml:18-27`).
The generated input and pipeline select `U6UsageQualCrossnamed__plant__comp_b__length = 7.0`
(`.project/active/self-binding-replacement/spike/out/u6_usage_qual_crossnamed/inputs/u6_usage_qual_crossnamed_params.json:1-3`,
`.project/active/self-binding-replacement/spike/out/u6_usage_qual_crossnamed/pipelines/pipeline.yaml:18-24`).

The sibling-position control produces `SI_OCCURRENCE_AMBIGUOUS` even though the author explicitly
names `comp_a`
(`.project/active/self-binding-replacement/spike/out/u5_usage_qual_named_sibling.log:1-5`). Together,
these results show that the current route selects by consumer position after it discards the
usage-owned declaration distinction.

### 3. The report names the right site but overstates what is lost

The one-segment shortcut sends the leaf directly to `_resolve_leaf`
(`src/sysml_codegen/elaboration/elaborate.py:2062-2076`). `_resolve_leaf` calls `slot_of` at `:2315`,
then searches the consumer lineage and descendants using that slot at `:2321-2347`. Redefinition
families intentionally share a root slot (`src/sysml_codegen/elaboration/occurrence.py:58-73`,
`:116-133`).

`[AGENT]` The precise diagnosis is:

> The exact leaf survives extraction. The one-segment leaf resolver reduces it to a redefinition
> slot before occurrence selection and does not use the leaf's usage owner.

Two phrases in the report should be narrowed:

- “It is our code, at one line” is useful shorthand, but slot normalization is not itself the bug.
  Value nodes and occurrence identities deliberately use slots
  (`src/sysml_codegen/elaboration/identity.py:85-113`,
  `src/sysml_codegen/elaboration/elaborate.py:756-807`).
- The qualifier is not literally “unrecoverable” after line 2315. `_resolve_leaf` still has the
  exact `declaration_id`, and the elaborator still has the live declaration in `_elements`
  (`src/sysml_codegen/elaboration/elaborate.py:636-653`). The current path simply stops consulting
  its owner.

The dot route explains the difference. A two-segment chain contextualizes its exact root occurrence
before transitioning to the leaf (`src/sysml_codegen/elaboration/elaborate.py:2077-2084`,
`:2119-2156`, `:2278-2297`). The later slot normalization is then safe because the occurrence is
already fixed.

### 4. Repair option (b) is incomplete at the proposed boundary

`[AGENT]` Do not approve the report's preferred option (b) without redesign.

First, it conflicts with the stated evidence boundary. The extraction layer says it captures frozen
SysIDE facts and does not resolve, rewrite, or interpret them
(`src/sysml_codegen/extraction/binding_evidence.py:1-10`;
`src/sysml_codegen/extraction/source_evidence.py:1-13`). KerML also says the `::` qualification does
not survive into abstract syntax; the abstract syntax contains the resolved element reference
(`full_document.md:3063-3065`). Adding the owner as a synthetic feature-chain segment turns
resolution policy into purported extraction evidence.

Second, the proposed site is not shared. Calculation-input bindings consume `reference_evidence`
through `_resolve_bindings` (`src/sysml_codegen/elaboration/elaborate.py:2575-2602`). Aliases,
computed attributes, and constraints independently create one-segment facts for direct feature
references in `_expression_references` at `:2524-2554`, then use the same resolver through
`_resolve_aliases` and `_resolve_computed_expressions` at `:2370-2394` and `:2435-2519`. A
`binding_evidence`-only patch leaves those paths unchanged.

Third, leaf owner kind does not recover every written qualifier. For a usage-qualified inherited
feature such as `component::length`, SysIDE may resolve the leaf to definition-owned
`Component::length`; the report already leaves this unmeasured for u3. The qualifier legitimately
disappears during name resolution, so a repair must not reconstruct semantic identity from the
stored qualifier string. The bounded, directly supported repair is the usage-owned local-
redefinition case measured by u5/u6/u7.

### 5. A shared elaboration repair fits the existing architecture better

The elaborator design already requires usage-owned features to select occurrences produced by their
exact owning usage and feature chains to contextualize the root once
(`.project/active/elaborator-design/design.md:345-355`). It also separates declaration, occurrence,
and node identity (`:105-122`) while keeping redefinition-family slots (`:163-178`).

`[AGENT]` Preferred direction:

1. At the shared one-segment resolution boundary, inspect the exact leaf declaration's semantic
   owner.
2. If the owner is a real `PartUsage`, contextualize that owner occurrence through the existing
   occurrence selector, then transition to the leaf within that fixed occurrence.
3. If the owner is a definition, preserve the current definition-owned positional path.
4. If an owner-anchored leaf is missing, fail loudly. Do not fall back to the positional search.

This is the report's option (a) in spirit, or an elaboration-boundary normalization immediately
before `_resolve_leaf`. It covers every caller and leaves slots and wire identity unchanged.

The risk is broader than u6. Bare references can also resolve to usage-owned leaves
(`tests/conformance/test_source_identity_extraction.py:151-193`). Redefined containment usages and
multiplicity exercise the occurrence selector's slot-family behavior
(`src/sysml_codegen/elaboration/occurrence.py:223-231`). Those are reasons for a semantic corpus
assessment and tests, not reasons to keep the wrong edge.

### 6. Assessment of the report's recommendations

#### Recommendation 1: corpus scan first

`[AGENT]` **Agree with the order; disagree that one count decides the blast radius.** A textual
pre-scan finds hundreds of qualified input bindings across tracked fixtures, with duplicated corpus
variants. The needed result is a semantic inventory, not a regex count. For each direct reference,
record:

- exact referent ID and owner kind/ID;
- authored form;
- consumer position relative to owner occurrences;
- current edge or diagnostic;
- expected edge or diagnostic under owner-aware resolution;
- affected live baseline, instance-graph snapshot, and generated package.

Committed snapshots store final graph edges. They do not rerun live reference resolution, so an old
snapshot with a wrong edge will preserve that edge on replay. There is no wire-format break, but
affected snapshots and baselines need legitimate recapture.

#### Recommendation 2: write guidance now

`[AGENT]` **Agree with the stable advice; qualify the defect warning.** Teaching a renamed input for
a local owning-part attribute and a dot path for a value on another part is correct now and after a
fix. Do not teach the current resolver defect as language semantics.

The proposed sentence that the shipped route “does not select which part a value comes from” is a
version-specific warning. It becomes false for the repaired usage-owned case. Publish it as a known
current limitation with a removal condition, or omit the implementation detail and state the
project's preferred authoring form. The report's claim that this exact guidance needs no rewrite
after the fix is therefore too strong.

#### Recommendation 3: keep fusion-tea on D-5

`[AGENT]` **Agree.** The fusion-tea migration repairs self-named local bindings by giving the formal
and owning attribute different names. That defect is separate from a correctly resolved
cross-part usage-owned reference. Nothing in this investigation reopens the migration form
(`.project/active/self-binding-replacement/spec.md:38-56`).

#### Recommendation 4: fix separately after the scan

`[AGENT]` **Agree with fixing it and with a separate bounded item. Disagree with approving option
(b).** This changes resolver behavior and needs kept fixtures, semantic before/after evidence, and
baseline review. It should not be folded into the current documentation/model-migration item. The
repair should live at the shared elaboration boundary or explicitly declare that non-binding direct
references remain an owned follow-up.

## Validation Performed

- Licensed live run of
  `.project/active/self-binding-replacement/spike/probe_referent_identity.py`: reproduced distinct
  SysIDE and `DeclarationId` values, identical slot roots, and two-segment dot facts.
- Licensed shipped-CLI generation of `u6_usage_qual_crossnamed` to a temporary directory: exit 0,
  sealed package, input and wiring selected `comp_b = 7.0`.
- Focused conformance tests:
  - three source-identity extraction tests passed;
  - two definition-qualified ambiguity/fail-closed tests passed.
- Read-only source and corpus inventory across codegen and companion/customer checkouts.

## Required Regression Coverage for a Repair

- Keep u1/u2 correct for an enclosing named usage.
- Keep u3/u3b characterized for usage-qualified inherited definition-owned leaves.
- Characterize package-level u4 explicitly.
- Change u5 from false ambiguity to `comp_a`; change u6 from silent `comp_b` to `comp_a`.
- Prove u7's `::` and `.` spellings reach the same occurrence-specific values.
- Keep definition-qualified s4/s8/s9 behavior unchanged.
- Add bare usage-owned, redefined-containment, multiplicity, alias, computed-attribute, and
  constraint-side cases.
- Compare occurrence IDs byte-for-byte, graph input edges semantically, and live versus recaptured
  snapshot/package output.

## Corrections to the Report

- `.project/reports/20260815-1338_qualified-binding-defect-attribution.md:78-80` calls the spike
  fixtures “throwaway and untracked.” They are tracked at current `main` and were added by the
  measured commit.
- The option table's option 1 is a composite statement. “SysIDE parses `::` correctly” is supported;
  the claimed consequence that codegen should preserve the current positional behavior is what is
  ruled out for the measured usage-owned redefinition.
- “One line” and “unrecoverable” should be replaced with the narrower diagnosis in Finding 3.

## Open Questions

- Which tracked qualified references actually resolve to usage-owned leaves outside their owner
  occurrence, and which committed snapshots preserve those edges?
- Should the repair enforce the general architecture rule for every usage-owned one-segment leaf,
  including bare references, or ship the qualified-binding case first with a named follow-up?
- What behavior does the project want for usage-qualified inherited, definition-owned leaves, where
  KerML resolution leaves no qualifier occurrence in the abstract syntax?

## Code References

- `src/sysml_codegen/extraction/binding_evidence.py:197-231` — one-segment binding fact.
- `src/sysml_codegen/elaboration/elaborate.py:2050-2084` — one-segment shortcut versus chain route.
- `src/sysml_codegen/elaboration/elaborate.py:2119-2219` — root occurrence selection.
- `src/sysml_codegen/elaboration/elaborate.py:2278-2348` — transition and positional leaf resolver.
- `src/sysml_codegen/elaboration/elaborate.py:2524-2602` — independent expression and binding paths.
- `src/sysml_codegen/elaboration/occurrence.py:58-133,223-231` — slot families and occurrence lookup.
- `src/sysml_codegen/elaboration/identity.py:66-113` — declaration, slot, and occurrence wire identity.
- `tests/conformance/test_source_identity_extraction.py:103-193` — kept extraction evidence controls.
- `tests/conformance/test_elaboration_fail_closed.py:70-92` — kept definition ambiguity controls.
