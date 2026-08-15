# Where the `::` qualified-binding defect actually lives

**Date:** 2026-08-15
**Author:** Claude (orchestrated run of `.project/active/self-binding-replacement/`)
**Measured at:** codegen `3458659`, licensed, on the shipped CLI
**Question asked by:** Reid W — *"is this KerML/SysIDE being correct, is it a SysIDE bug, or is it our
code?"*

---

## Headline

### The three options, as posed

| # | Option | Verdict |
|---|---|---|
| 1 | **SysIDE parses `::` correctly per KerML.** Trying to "correct" our interpretation would be wrong — it would re-legitimize the bad pattern the epic exists to delete. | **SPLIT: premise TRUE, conclusion FALSE** |
| 2 | **`::` should work; SysIDE has a bug.** Any fix of ours would be a hacked patch around a vendor defect. | **RULED OUT** by measurement |
| 3 | **`::` should work and *does* in SysIDE — our code breaks it.** | **CONFIRMED** |

### Conclusion

**It is our code.** SysIDE resolves `comp_a::length` and `comp_b::length` to two distinct elements,
exactly as KerML §7.3.4.5 requires. Our extraction preserves that distinction. Our elaborator then
normalizes both to the same `FeatureSlotId` at `elaborate.py:2315` and selects an occurrence
positionally from there, which can silently pick a different part than the author named.

Two precisions, both corrections to this report's first revision:

- **The defect is not the normalization.** Slot normalization is intentional and correct — it is what
  makes a redefinition and the feature it redefines one slot. The defect is *normalizing before using
  the exact leaf's owning usage to select an occurrence*. `elaborate.py:2315` is the first harmful
  collapse on this route, not a wrong line in itself.
- **The owner information is not "unrecoverable"**, as this report first said. `_resolve_leaf` still
  holds the exact `DeclarationId`, and the elaborator retains the corresponding live element. The
  information is present and simply unused. That is precisely why the repair is cheap.

Two things follow that matter for how you weigh this:

- **Correcting it re-legitimizes nothing.** `in R = R` fails on a *scoping collision inside the
  calculation* — the name matches the calc's own parameter. This defect is a *correctly-resolved
  cross-part reference that we normalize away afterward*. Different mechanism, no overlap. Honoring
  an explicit `comp_a::length` does not make an unqualified self-reference any more valid.
- **The fix is contained**, and it does not touch slot semantics or the wire format.

### Recommendation, in steps

1. **Run a corpus scan first** (~1 hour, no code change). **A count is not enough.** For every
   `usage::feature` binding, record: the exact referent owner, the consumer's position relative to
   it, the current edge or diagnostic, the expected edge after repair, and the affected snapshots or
   baselines. That schema — not a total — is what tells you whether the repair is a silent behavior
   change anywhere currently green. Do not authorize a code change before it exists.
2. **Write the guidance now, but know which half is stable.** The **stable** half is the advice
   itself: rename a local calculation input, use a dot path for a value on another part. That is
   correct today and after any repair. The **unstable** half is any sentence explaining that `::`
   "does not select which part" — that describes the current defect and **will need revision once
   step 4 lands**. Write it so the explanation can be revised without touching the advice.
3. **Migrate fusion-tea on the rename form (D-5) as already planned.** Unaffected by this report.
4. **Then fix it at the shared elaboration boundary** (option (a) in *Repair* below): when a
   one-segment leaf is owned by a real `PartUsage`, contextualize that owner's occurrence and resolve
   the slot inside it; definition-owned leaves keep today's route. Scope it as its own bounded change
   with the step-1 evidence attached, and re-run the affected baselines. **Not** at extraction —
   see why below.

**Why I recommend fixing rather than only documenting.** If we do not fix it, the guidance has to
tell authors that our tool ignores a qualifier the standard says is meaningful. That is documenting a
defect as if it were the design, in the exact document whose purpose is to stop authors writing
silently-wrong models. The fix is small; the documentation debt is permanent.

**What I am not recommending.** Fixing it *inside* the self-binding-replacement item as currently
scoped. That item is documentation plus model migration; this is a resolver behavior change needing
its own fixtures and baseline re-verification. Adjacent and sequenced, not folded in.

---

## How to verify this report independently

Everything below was produced by these commands from the repo root at `3458659`.

```bash
# license (there is no .env in this repo; it lives in the companion checkout)
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a

# the identity probe — the core evidence for the conclusion
uv run python .project/active/self-binding-replacement/spike/probe_referent_identity.py

# the six behavioral rows the conclusion explains
uv run python .project/active/self-binding-replacement/spike/run_addendum.py
```

Fixtures and probe scripts **are tracked**, under
`.project/active/self-binding-replacement/spike/`, so this report is reproducible from a clean
checkout. The decisive fixtures are `u7_both_spellings/` (both spellings authored as real bindings
from a symmetric position) and `u6_usage_qual_crossnamed/` (the failing behavior). Generated probe
output under `spike/out/` is **not** tracked and is regenerated by the commands above.

*(This report's first revision described the fixtures as untracked. They had in fact been committed —
along with 250 files of generated output, since removed from the index. Corrected after the
independent assessment caught it.)*

**Without the license the licensed paths skip rather than fail** — a green run with no key is not a
run. The probe prints `license key loaded (len 37)` on success; if it does not, stop.

Full evidence chain, including the two earlier passes and their corrections:
`.project/active/self-binding-replacement/spike/findings.md` (F-1 … F-7).

---

## The failing behavior

```sysml
part def 'Plant' {
    part comp_a : 'Component' { :>> length = 3.0; }

    part comp_b : 'Component' {
        :>> length = 7.0;

        calc area_calc : AreaCalculation {
            in length_in = comp_a::length;   // author named comp_a. Means 3.0.
        }
    }
}
```

**Observed:** exit 0, no diagnostic, package seals, and the delivered entry point is
`U6UsageQualCrossnamed__plant__comp_b__length = 7.0`. The author's explicit `comp_a` is discarded.

Corroboration that this is not a matter of reading author intent: write the *same* explicit name from
*outside* both usages and the route raises `SI_OCCURRENCE_AMBIGUOUS` (row u5). It can only be
ambiguous if the qualifier's occurrence information was discarded — the author named one.

---

## The measurement that attributes the layer

`u7_both_spellings` authors both spellings in one model from a symmetric position. Identity compared
at three layers:

```
                        comp_a::length                          comp_b::length
SysIDE element_id       936d7879-82e1-5bcf-92b8-773d6f67b37d    d7d38390-79be-56a3-876f-3c1a7f4d41e7
our DeclarationId       936d7879-82e1-5bcf-92b8-773d6f67b37d    d7d38390-79be-56a3-876f-3c1a7f4d41e7
our FeatureSlotId       6093ae42-e366-5c66-b26a-5b4194b42f8a    6093ae42-e366-5c66-b26a-5b4194b42f8a
                                                                ^^^^^ identical — loss happens here
```

Both referents carry `owned_redefinitions -> U7BothSpellings::Component::length (6093ae42-…)`, and
their `owner` fields are `…::Plant::comp_a` and `…::Plant::comp_b` respectively.

`6093ae42` is `Component::length` — the root of the redefinition chain. The normalization is
`elaborate.py:2315` (`slot = self._slots.slot_of(declaration_id)`) → `occurrence.py:73` → `_root_of`
(`occurrence.py:116-133`).

**Reading:** distinct at SysIDE → distinct in our extraction → collapsed in our elaboration. Option 3.

### Why option 1 is ruled out (the standard, not opinion)

- KerML §7.3.4.5 (`full_document.md:1681`): where a type owns a redefining feature, the redefined
  feature is *"not inherited and [is], instead, replaced by the redefining feature."*
- §7.3.4.5 (`:1689`): an unnamed redefining feature *"is implicitly given the same name … used in
  name resolution, just as explicitly declared names would be."*
- §8.2.3.5.1 step 3 (`:3095`): a qualified name resolves its last segment against the namespace the
  qualification part identifies.

Since `comp_a` writes `:>> length = 3.0` in its own body, `comp_a`'s namespace contains *its own*
`length`. So `comp_a::length` normatively denotes comp_a's feature. Our expectation was correct.

*Caveat carried forward:* visible resolution requires `visibility = public` (§8.2.3.5.3), and the
2026-08-05 probe table already noted the spec states no explicit "features default public" rule.
Not load-bearing for this conclusion — the measurement shows resolution succeeding.

### Why option 2 is ruled out

SysIDE returned two distinct elements with correct owners and correct `owned_redefinitions`. It
implements §7.3.4.5 as written. There is nothing to patch around.

---

## Why the dot path is different in kind

The dot pair **also** collapses at `FeatureSlotId`, so the collapse is not by itself the bug. The
difference is what happens *before* the leaf lookup.

`driver.cost` produces a **two-segment** reference:

```
expression metatype = FeatureChainExpression
segments = 2:  [0] S3PathNamed::Plant::driver   (the root usage)
               [1] S3PathNamed::Driver::cost
expr.operands: ['FeatureReferenceExpression'] -> S3PathNamed::Plant::driver
```

Two segments means `_resolve_semantic_reference` skips its one-segment shortcut
(`elaborate.py:2070`) and calls `_contextualize_root` (`:2119`), which fixes an occurrence of the
root usage, then `_transition` (`:2278`) steps to the leaf. The leaf lookup is scoped to an
occurrence that is *already fixed*, and within one occurrence a slot is unique by construction.

`comp_a::length` has no root segment, so `_resolve_leaf` must *find* a scope, and the collapsed slot
is the only thing it has to find one with.

> **The slot collapse is harmless when an occurrence is already fixed, and fatal when the slot is the
> only thing left to pick an occurrence with.**

This is structural, not incidental to our implementation. §8.2.3.4 (`:3065`): a qualified name
*"does not appear in the corresponding abstract syntax — instead, the abstract syntax representation
contains an actual reference to the identified Element."* A feature chain keeps each segment as a
real chaining feature (§7.3.4.6, `:1703`) and evaluates in the context of the primary expression's
results (§7.4.9.3, `:2437`). **So `.` carries occurrence context by construction in any conforming
tool, and `::` never does — only the resolved element survives.** That element does carry its owning
usage, which is why the repair is possible at all.

---

## Repair

**What it compares:** the resolved leaf declaration's **owner**. Owner is a part *usage* → the leaf
is a usage-owned redefinition and that usage is the occurrence anchor. Owner is a part *def* → today's
positional search, unchanged. Both fields are present at extraction time (measured above).

**Option (a), PREFERRED — repair at the shared elaboration boundary.** When a one-segment leaf is
owned by a real `PartUsage`, contextualize that owner's occurrence and resolve the slot inside it;
definition-owned leaves keep their existing route. Covers every caller, preserves slot and wire
identity, and adds no synthetic evidence.

**Option (b), REJECTED — emit a two-segment fact in `reference_evidence`**
(`binding_evidence.py:197-231`). *This was the preferred option in the first revision of this report
and it was wrong.* Two reasons, the first decisive:

1. **It repairs one of four callers.** `_expression_references` (`elaborate.py:2543-2552`) builds a
   one-segment `ResolvedSemanticReferenceFact(root=target, segments=(target,), leaf=target)` for any
   `FeatureReferenceExpression`, independently of extraction. Verified callers of
   `_resolve_semantic_reference`: `:2587` (calc-input bindings — the only one fed by
   `binding_evidence`), `:2384` (alias expressions), `:2458` (aggregation and constraint terms),
   `:1051` (redefinition chaining features). Option (b) fixes `:2587` only and leaves the identical
   silent defect in aliases, constraints, and computed attributes — while *appearing* fixed, since
   the natural regression fixtures for it are calc-binding fixtures.
2. **It turns resolution policy into synthetic extraction evidence.** Extraction would fabricate a
   path the author did not write, to steer a downstream policy decision.

*(Attribution: both points are from the independent assessment,
`.project/research/20260815-134615_qualified-binding-defect-assessment.md`. Point 1 was verified
against the source before acceptance.)*

**The normalization stays.** It is what makes a redefinition and the feature it redefines one slot,
which `effective_declaration` (`occurrence.py:75-100`) depends on and which occurrence identity is
built from (`OccurrenceStep.containment_slot`). Neither option changes slot semantics.

**Blast radius.** `OccurrenceId.to_wire()` (`identity.py:108-113`) encodes
`containment_slot.root_declaration`, so slot roots are baked into every serialized occurrence id and
every snapshot fixture. **Neither option touches that** — no wire-format break, no snapshot
re-capture beyond fixtures whose wiring legitimately changes. Unaffected and still slot-based:
`_target_for_slot`, `_transition`, the `_resolve_leaf` lineage loop, the redefinition-family
invariant.

**Definition-qualified case survives untouched.** `'Plant'::availability` resolves to a leaf owned by
a part *def*, so the branch never fires and the positional search still runs — correct there, since a
definition qualifier names no occurrence. **No "qualifier kind" field is needed**; the owner metatype
already discriminates.

---

## Guidance

**Unchanged by this report, and better justified.** Teach `.` for a value on another part; teach the
rename (`in availability_in = availability`) for an attribute on the owning part. Both are correct on
the shipped route today, both stay correct if the repair lands, so guidance written now needs no
rewrite after.

**Do not write that `::` "doesn't work."** It works in the topology all seven published examples use
— the calc sits inside the very usage the qualifier names, so qualifier and lineage agree — and the
standard says it denotes exactly what the author means. The accurate line:

> A `::` qualifier is safe when it names your own enclosing usage. It does not select which part a
> value comes from: the shipped route resolves the feature and then picks an occurrence by position,
> so naming a *sibling* part can silently deliver a different part's value. To take a value from a
> specific part, use a dot path (`driver.cost`).

---

## What is measured, and what is not

**Measured** (reproducible by the commands above): the three-layer identity comparison; the six
behavioral rows u1–u6; the two-segment structure of the dot path; the ten-row agreement between the
definition-qualified and usage-qualified spellings; the KerML citations, read directly.

**Not measured — treat as open:**

- **The corpus count** of tracked models/fixtures/baselines with a `usage::feature` binding whose
  consumer sits outside the named usage. This is recommendation step 1 and gates the code change.
- **Whether any currently-green tracked fixture depends on today's positional behavior** for a
  usage-qualified reference — i.e. whether the repair is a silent behavior change somewhere.
- Whether the u1 published topology is bit-identical under option (b). It should be; "should be" is
  not a measurement.
- `u3`'s actual referent owner (its usage has no body, so the referent is probably the inherited
  definition-level feature and the branch would not fire — outcome is today's refusal either way,
  but which path it takes is unverified).

## Corrections this report supersedes

Recorded because earlier statements of mine are in the commit trail and should not be trusted:

1. **"The repair is not contained / reaches resolver semantics."** Wrong. It rested on the belief
   that the written qualifier never reached our code. The measurement falsified that.
2. **`binding_evidence.py:211-221` named as a site of loss.** Acquitted — identity survives it
   intact. Single point of loss, not two.
3. **The spike's first-pass headline "nothing resolves silently and wrongly."** Falsified by u6.
4. **"`::` doesn't work."** Imprecise to the point of being false; see *Guidance*.

Corrections from the independent assessment
(`.project/research/20260815-134615_qualified-binding-defect-assessment.md`), all accepted, the
first two verified against source before acceptance:

5. **Option (b) was the preferred repair.** Wrong — it covers one of four callers of
   `_resolve_semantic_reference`. Repair belongs at the shared elaboration boundary.
6. **"The fixtures are untracked."** False; they were tracked, with 250 generated artifacts.
7. **"The qualifier is unrecoverable" after `:2315`.** False — `_resolve_leaf` holds the exact
   `DeclarationId`. Present but unused.
8. **Option 1 ruled out wholesale.** Its premise (SysIDE is correct) is true; only its conclusion
   (therefore keep our positional behavior) is false.
9. **"Guidance written now needs no rewrite after."** Too strong. The advice is stable; the sentence
   explaining `::` describes current behavior and will need revision after the repair.

## Related

- Evidence chain: `.project/active/self-binding-replacement/spike/findings.md` (F-1 … F-7)
- Item spec: `.project/active/self-binding-replacement/spec.md`
- Epic: `.project/backlog/epic_elaborate_first_architecture.md` — the `[OWNER]` critical success
  factor this defect contradicts (*an unsupported authored form fails loudly before generation*)
- Product promise negated by the defect: `.project/product/P-001`
