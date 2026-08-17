# Probe: authored bare-reference discriminator authorability

**Date:** 2026-08-15
**Status:** **Affected shape found.** Nine legal authored topologies discriminate. The original
u6-style candidate stays falsified.
**Environment:** SysIDE 0.8.4 through the repository's licensed `uv` environment.

---

## Summary of Findings

A legal authored SysML model **does** exist in which a bare (one-segment, unqualified) reference to
a `PartUsage`-owned leaf makes consumer-lineage selection and exact-owner selection land on
different occurrences. Nine of the fourteen candidates swept do it, across four consumer lanes.

The mechanism is one sentence. A `FeatureSlotId` is the **root of the redefinition family**
(`src/sysml_codegen/elaboration/occurrence.py:70-73`), so `comp_a::length` and `comp_b::length` share
one slot. `_resolve_leaf` throws the exact leaf's owner away and re-finds that shared slot by walking
up the *consumer's* occurrence lineage (`src/sysml_codegen/elaboration/elaborate.py:2299-2347`). So
any legal way to make a bare name inside `comp_b` resolve to a leaf owned by `comp_a` discriminates.

Two independent families of legal SysML do exactly that:

- **`alias`** — `alias a_len for comp_a::length;` anywhere visible to the consumer, then bare `a_len`
  in the consumer. Works from parent scope, package scope, and inside the consumer's own body.
- **`import`** — `private import comp_a::length;` (or `comp_a::*`) inside the consumer, then a
  literally bare `length`. This one needs no alias name at all; the written text is one segment.

The discrimination is a wrong number, not just a wrong ID. In `c01`, `comp_a.length = 3.0` and
`comp_b.length = 7.0`; the shipped resolver wires the consumer to the `7.0` node, so `doubled`
computes `14.0` where the model says `6.0`.

**What this means for the upstream work.** Spec criterion SC8 (`spec.md:128-130`) is authorable as
written, so design bet B3 is **confirmed** and D10 route 1 is available on evidence. Choosing the
route remains the owner's call; this document does not make it.

**Recommended fixture if route 1 is taken:** `c01-alias-parent-scope`. It is the smallest shape, it
loads with zero errors and zero warnings, it keeps the u6 `comp_a`/`comp_b` naming the rest of the
item already uses, and its wrong edge is legible as `14.0` versus `6.0`. `c10` (calc actual) and
`c11` (constraint predicate) extend the same alias to the other two consumer lanes if the Phase-2
combined fixture wants them.

**Bound worth carrying:** the truly-bare `import` shapes (`c04`, `c05`) only discriminate when the
consumer does **not** redefine the name locally. Add `:>> length = 7.0;` back and SysIDE resolves the
bare name to the consumer's own redefinition (`c14`), and the shape stops discriminating. The
`alias` shapes have no such fragility — they discriminate with the local redefinition present.

---

## Question

Does a legal authored SysML model exist in which a **bare** (one-segment, unqualified) reference to a
`PartUsage`-owned leaf makes consumer-lineage selection and exact-owner selection land on **different**
occurrences?

The first probe below asked the narrower question posed by
`.project/research/20260815-142743_bare-expression-side-measurement.md:251-256`, and falsified it.
The sweep that follows is the bounded search over legal scoping and redefinition shapes.

---

## Part 1 — the original two-candidate probe (retained)

### Result

The inside-sibling model loads. SysIDE resolves bare `length` to the redefining feature owned by the
same sibling as the consumer:

```text
inside-sibling loaded= True resolved= [('BareInsideSibling::Plant::comp_b::length', 'BareInsideSibling::Plant::comp_b')]
```

Both positional and owner-aware routes therefore select `comp_b`; the shape does not discriminate.

The parent-scope variant does not load. Bare `length` is not visible from the parent:

```text
error (reference-error): No Feature named 'length' found.
parent-scope loaded= False resolved= [("'<placeholder Feature>'", 'None')]
```

### Disposition

This probe falsifies the one candidate topology named by the measurement report. It does **not**
prove that no legal authored discriminating topology exists. Part 2 finds nine that do.

### Reproduction

```bash
set -a; source ../agentic-mbse/.env; set +a
uv run python \
  .project/completed/20260816_qualified-reference-occurrence-anchoring/spike/\
bare-discriminator-authorability/probe.py
```

---

## Part 2 — bounded sweep over legal scoping and redefinition shapes

### Method

`sweep.py` beside this file loads every candidate directory through the licensed environment and
reports, per candidate:

1. whether the model loads, and any load warnings;
2. for each `FeatureReferenceExpression`: the written text, whether the extractor classifies it as a
   bare reference (`written_qualifier(expr) is None`, i.e. `SourceForm.BARE_REFERENCE`,
   `src/sysml_codegen/extraction/binding_evidence.py:109-129`), the **exact referent element ID**,
   and the referent's **live owner element ID and metatype**;
3. the edge the **shipped** resolver actually produces for the consumer, as the target `AttrNode`'s
   exact `declaration_id`;
4. the edge **exact-owner selection** would produce, derived by matching occurrence records on
   `effective_usage_id == <live owner ID>` and taking the leaf's slot at that occurrence.

A candidate discriminates when (3) and (4) disagree. **Every comparison is on element IDs.**
Qualified names appear only as human-readable labels; no step matches on a name string.

Reference expressions with only one segment are the whole population here: a
`FeatureReferenceExpression` always yields exactly one segment
(`src/sysml_codegen/extraction/binding_evidence.py:198-220`), which satisfies the plan's
`len(fact.segment_element_ids) == 1` stencil assertion by construction.

### Reproduction

```bash
set -a; source ../agentic-mbse/.env; set +a
uv run python \
  .project/completed/20260816_qualified-reference-occurrence-anchoring/spike/\
bare-discriminator-authorability/sweep.py
```

Exits 0. Writes no generated package and no production file.

### Candidate table

Owner metatype is the live metatype of the referent's `owning_type`. "Shipped" and "owner-anchored"
are the two selections compared; they are `AttrNode.declaration_id` values, abbreviated to their
first eight hex digits, with the display path for readability.

| # | Candidate | Loads | Bare | Owner metatype | Shipped edge | Owner-anchored edge | Conclusion |
|---|---|---|---|---|---|---|---|
| c01 | `alias` at parent (`Plant`) scope, computed attribute in `comp_b` | yes, clean | yes | `PartUsage` | `comp_b.length` `68aac994` (7.0) | `comp_a.length` `c301fa9c` (3.0) | **affected shape found** |
| c02 | `alias` declared inside the consumer `comp_b` | yes, clean | yes | `PartUsage` | `comp_b.length` `a943e0f4` (7.0) | `comp_a.length` `53194239` (3.0) | **affected shape found** |
| c03 | `alias` at package scope | yes, clean | yes | `PartUsage` | `comp_b.length` `9e596725` (7.0) | `comp_a.length` `fb1aaaeb` (3.0) | **affected shape found** |
| c04 | `private import comp_a::*;` in `comp_b`, literally bare `length` | yes, clean | yes | `PartUsage` | `comp_b.length` `66cb7da5` (1.0) | `comp_a.length` `e01dc440` (3.0) | **affected shape found** |
| c05 | `private import comp_a::length;` in `comp_b`, literally bare `length` | yes, clean | yes | `PartUsage` | `comp_b.length` `73d3c377` (1.0) | `comp_a.length` `388d1c56` (3.0) | **affected shape found** |
| c06 | `alias` to the **definition**-owned `Component::length` | yes, clean | yes | `PartDefinition` | `comp_b.length` `4cb49e56` (7.0) | n/a — owner is not a `PartUsage` | candidate falsified (useful control) |
| c07 | `attribute borrowed : Real :> comp_a::length;` then bare `borrowed` | yes, 1 warning | yes | `PartUsage` (`comp_b`) | `comp_b.borrowed` `59a87457` | `comp_b.borrowed` `59a87457` | candidate falsified |
| c08 | `part comp_b : Component :> comp_a`, bare `length` | yes, clean | yes | `PartDefinition` | `comp_b.length` `9c84f30b` (1.0) | n/a — owner is not a `PartUsage` | candidate falsified |
| c09 | `alias` at parent scope, consumer nested two levels down (`bay.comp_b`) | yes, clean | yes | `PartUsage` | `bay.comp_b.length` `731caa3d` (7.0) | `comp_a.length` `42311e36` (3.0) | **affected shape found** |
| c10 | `alias` used as a **calc usage actual** (`in w = a_len`) | yes, clean | yes | `PartUsage` | `comp_b.length` `26e8b0b9` (7.0) | `comp_a.length` `84390938` (3.0) | **affected shape found** |
| c11 | `alias` used inside an **asserted constraint predicate** | yes, clean | yes | `PartUsage` | `comp_b.length` `7b0072a8` (7.0) | `comp_a.length` `0249f92e` (3.0) | **affected shape found** |
| c12 | `alias` where the owner usage is arrayed `comp_a : Component[2]` | yes, clean | yes | `PartUsage` | `comp_b.length` `4f9ecede` (7.0) | **two** occurrences: `comp_a[0]`, `comp_a[1]`, both `0520afdc` | **affected shape found** (see note) |
| c13 | `alias`, consumer `comp_b` has **no** local `:>> length` | yes, clean | yes | `PartUsage` | `comp_b.length` `7ae6d7a4` (1.0) | `comp_a.length` `3ad148be` (3.0) | **affected shape found** |
| c14 | `private import comp_a::length;` **plus** a local `:>> length = 7.0` | yes, clean | yes | `PartUsage` (`comp_b`) | `comp_b.length` `01eff1cc` (7.0) | `comp_b.length` `01eff1cc` (7.0) | candidate falsified (bounds c04/c05) |
| — | `inside-sibling` (Part 1) | yes | yes | `PartUsage` (`comp_b`) | `comp_b.length` `3dc8d4ee` | `comp_b.length` `3dc8d4ee` | candidate falsified |
| — | `parent-scope` (Part 1) | **no** | n/a | n/a | n/a | n/a | candidate falsified — does not load |

Two shapes were tried and dropped as **not legal SysML v2**, so they are not candidates:

- `private import comp_a::length as a_len;` — `import … as` is not SysML v2 syntax.
  SysIDE: `parsing-error: Unexpected ';'` at the `as`. The retained `c06` reuses that directory for
  the definition-owned control instead.
- A consumer typed by the same definition that contains it (`part comp_b : Component { part inner :
  Component { … } }`) loads, but elaboration refuses it with `SI_CONTAINMENT_RECURSIVE`. `c09` gets
  its second nesting level from an untyped `part bay { … }` instead.

### Notes on individual results

**c04 / c05 are the strongest form of the criterion.** The written reference text is literally
`length` — one segment, no alias name, no qualifier. SysIDE resolves it to `comp_a::length` because
the explicit import beats the inherited feature. This is what SC8 most plainly describes.

**c12 changes the failure mode rather than the target.** With an arrayed owner, exact-owner
selection in scalar mode has two candidate occurrences and must raise
`SI_OCCURRENCE_AMBIGUOUS`, where the shipped resolver silently returns `comp_b.length`. That is
still a disagreement, and it is a useful negative case for the Phase-3 "no hidden positional
recovery" risk — but it is not a clean single-target discriminator, so it is not the fixture to
promote.

**c13 shows the defect does not need a redefining consumer.** `comp_b` has no `:>> length`, so its
node carries the definition default `1.0`; the shipped edge still lands there instead of on
`comp_a`'s `3.0`.

**c07's warning is real and expected.** SysIDE reports
`subsetting-featuring-types: Subsetted feature must be accessible from the subsetting feature`.
The candidate is falsified on its own terms anyway — `borrowed` is owned by `comp_b`, so both routes
agree — and the shape is not recommended for a fixture.

### Raw driver output

The exact run backing the table:

```text
## c01-alias-parent-scope
loaded: True
  ref written='a_len' bare=True
    referent id=c301fa9c-5227-5578-bb3d-877d5d91b6ab (BareAliasParentScope::Plant::comp_a::length)
    owner    id=5c33d1dc-653f-5906-b9f4-412646528ca8 (BareAliasParentScope::Plant::comp_a) metatype=PartUsage
  edge calc BareAliasParentScope__plant__comp_b__doubled.length ->
    attr[BareAliasParentScope__plant__comp_b__length] declaration=68aac994-506a-5ae6-8a7b-8232f46e9e8d value=7.0
  owner-anchored target for 'a_len': 1 owner occurrence(s) ->
    ['attr[BareAliasParentScope__plant__comp_a__length] declaration=c301fa9c-5227-5578-bb3d-877d5d91b6ab value=3.0']
```

Re-run `sweep.py` for all fourteen. Element IDs are reload-stable UUIDv5 values, so a re-run
reproduces the IDs above exactly.

### Model source text

Every candidate's source is retained beside this file at `<candidate>/model.sysml`. The
recommended fixture, `c01-alias-parent-scope/model.sysml`, in full:

```sysml
package BareAliasParentScope {
    private import ScalarValues::*;

    part def 'Component' {
        attribute length : Real default 1.0;
    }

    part def 'Plant' {
        part comp_a : 'Component' { :>> length = 3.0; }

        alias a_len for comp_a::length;

        part comp_b : 'Component' {
            :>> length = 7.0;
            attribute doubled : Real = a_len * 2.0;
        }
    }

    part plant : 'Plant';
}
```

---

## Owner decision still reserved

`[OWNER, 2026-08-15]` D10 is the owner's to settle. This document supplies the evidence route 1
asked for and nothing more. It does not amend `spec.md`, does not amend `design.md`'s bet or
decision status, does not select a route, and does not open or close a gap record.

## Open questions / follow-ups

- **Not searched:** shapes reached through `connect`/binding connectors, `variant`/variation
  points, `port` conjugation, or `#metadata`-driven resolution. The sweep covered aliasing,
  importing, subsetting, specialization, nesting, arraying, and redefinition presence/absence. A
  discriminator was found, so widening further has no remaining question to answer.
- **Not settled here:** whether SysIDE's precedence of an explicit `import` over an inherited
  feature (c04/c05 versus c14) is specified behavior or tool behavior. The `alias` shapes do not
  depend on it, which is the second reason `c01` is the recommended fixture.
- **D11** (deep literal override authorability) is a separate probe and is untouched by this work.
