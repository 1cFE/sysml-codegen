# Design: Return-Style & Bare-Parameter Extraction (SC-2)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-05
**Branch:** upstream-findings-epic
**Commit:** 9afb797
**Epic Item:** UPSTREAM-FINDINGS Item 3
**Complexity:** MEDIUM (1-day)

---

## Overview

Relax the calc-def member filter so the extractor keeps direction-carrying
`ReferenceUsage` members (named `return`, bare `in`), not just `AttributeUsage`.
One anonymous form (`return : Real = expr;`) stays unsupported but now gets its
own diagnostic (V8) instead of the generic zero-output error.

## Related Artifacts

- **Spec (contract):** `.project/active/return-style-extraction/spec.md`
- **Spec review:** `.project/active/return-style-extraction/spec-review.md`
- **Epic:** `.project/backlog/epic_upstream_findings.md` (Item 3; R1/R2/R3)
- **Required Reading:**
  - `.project/research/20260705_upstream-findings-deep-research.md` (SC-2 — authoritative)
  - `docs/architecture/modeling-assumptions.md` (§ Validation Rules, V7 from Item 1)
  - `docs/architecture/reference/01-extraction.md` (canonical example to reconcile)
  - `~/1cfe/fusion-tea/.project/reports/2026-07-05-upstream-findings-register.md` (A-2)
- **Code:** `src/sysml_codegen/extraction/extractor.py`

## Research Findings

**The bug is one filter, applied twice.** `_extract_calculation_definition`
gates both member passes on `is_instance(member, "AttributeUsage")` and
`continue`s past everything else — `extractor.py:204` (primary pass) and `:242`
(second `member_expressions` pass). syside represents three legal SysML forms as
`ReferenceUsage`, so they never enter the loop body.

**Everything downstream of the filter already works.** Confirmed against HEAD:

- `_get_direction` (`extractor.py:296-306`) reads `member.direction` via `str()`
  and matches the `"In"` / `"Out"` substrings. A `ReferenceUsage` carries
  `.direction` just like an `AttributeUsage`, so this works unchanged on the new
  members. (Note: there is **no** `FeatureDirectionKind.Return` — a `return`
  result has direction `Out`. The `"Return"` substring check is harmless dead
  code; leave it.)
- The AST-capture block (`extractor.py:223-228`) keys off `is_output` +
  `member.feature_value_expression`. A `return y : Real = expr;` ReferenceUsage
  carries the expression, so auto-impl falls out for free once the filter admits
  it — no new code.
- `_extract_attribute` (`extractor.py:405-437`) is member-type-agnostic; it reads
  `name`, `heritage`, `feature_value_expression`. It returns `None` for a
  nameless member (`:407-409`) — the mechanism that makes an anonymous return
  invisible to `output_attributes`.

**syside type model (confirmed via syside-expert against the metamodel docs):**
`AttributeUsage` and `ReferenceUsage` are **siblings** — both specialize `Usage`
directly, neither is an ancestor of the other. So `is_instance(m, "ReferenceUsage")`
is **False** for an `AttributeUsage`. The two-branch predicate below is therefore
unambiguous: attributes match the first branch, reference usages the second.

**Baseline safety.** No committed fixture calc def declares a `return`-style or
bare-`in` member (grepped every `.sysml`; spec-review L3-3 confirms). The
relaxation adds zero members for existing models, so their snapshots and the 4
pipeline baselines stay byte-identical. The byte-identical re-run is the *proof*;
the source grep is only the hypothesis (treat any baseline diff as a real signal).

## Core Concept

Today the extractor asks "is this member an `AttributeUsage`?" That question is
wrong — it is a proxy for the real one, "is this member a calc-def **parameter**?"
The two diverged the moment SysML let you write `return y` and bare `in x`, which
syside models as `ReferenceUsage`. The fix replaces the proxy with the real
question, expressed as one predicate used at both filter sites:

> A member is a parameter if it is an `AttributeUsage`, **or** a `ReferenceUsage`
> that carries a direction (In / Out).

Direction-None `ReferenceUsage` members stay excluded. That single exclusion is
what prevents double-ingestion of the `return attribute y; ... y = expr;` form:
its body-assignment target is a direction-None `ReferenceUsage` sharing the
output's name, so it must not become a second `y`. Everything else — direction
splitting, expression capture, auto-impl — already keys off this membership
decision and needs no change.

One form has no real question to answer: anonymous `return : Real = expr;` has no
name, so there is no PQN channel to build. It cannot be supported; it gets a
specific diagnostic (V8) that names the fix, fired before the generic
zero-output error (V7) so the modeler sees the precise cause.

## Key Bets

- **B1.** syside exposes `.direction` on `ReferenceUsage` members with the same
  semantics as on `AttributeUsage` (In for bare `in`, Out for `return`), and the
  return expression lives on the ReferenceUsage's `feature_value_expression`.
  *If false → auto-impl for named return silently breaks; bare-in inputs land in
  the wrong list.* (Mitigated: confirmed by the research SC-2 probe and
  syside-expert; the live fixture test re-confirms at implementation.)
- **B2.** The body-assignment target of `return attribute y;` is a direction-None
  `ReferenceUsage` (not an `AttributeUsage`). *If false → the predicate would
  admit it as a second `y` and double-ingest.* (Mitigated: probe + syside-expert
  confirm direction-None; the no-double-ingestion test pins it.)
- **B3.** No committed fixture uses a direction-carrying `ReferenceUsage` member.
  *If false → existing snapshots/baselines shift and the "byte-identical"
  criterion fails.* (Mitigated: source grep negative; byte-identical re-run is
  the real check.)
- **B4. An anonymous `return : Real = expr;` surfaces as a member with direction
  Out and an empty/missing name after `sanitize_name`.** This is the one node
  shape the research SC-2 probe never covered — the probe tested named forms, not
  the anonymous result. *If false → V8 detection never fires (the anonymous
  return either falls through to V7's generic message, or, if syside synthesizes
  a name, is admitted by the predicate and reaches `output_attributes` as a
  garbage-named output).* **This bet is unproven and gates V8's detection rule —
  it MUST be probed live before V8 is written (de-risk task #1).** *Fallback: if
  the probe shows syside synthesizes a name or reports direction None, V8 keys off
  whatever the probe shows distinguishes the result member — e.g. its
  result-parameter membership or heritage (`ReturnParameterMembership`) — and this
  design's "direction-Out + empty name" rule is replaced with the probe-evidenced
  one before implementation.*

## Key Decisions

- **D1. One shared predicate `_is_parameter_member(member)`, used at both `:204`
  and `:242`.** *Rejected: inlining the two-branch check at each site (the two
  copies drift; the HARD "both passes agree" requirement forbids it).* This is a
  predicate extraction, not a new abstraction.
- **D2. V8 detection is a dedicated raw-member pre-scan placed immediately before
  the V7 guard.** *Rejected: setting a flag inside the relaxed primary loop
  (couples V8 correctness to the filter's admission logic; a standalone scan over
  `elem.owned_members` is self-evidently correct and independent of the
  predicate).* The scan is ~4 lines: any member with direction Out whose
  `sanitize_name` is empty raises V8. **The detection key is confirmed by de-risk
  task #1 (B4) before V8 is written** — the "direction-Out + empty name" rule
  holds only if the live probe confirms that node shape; otherwise it is replaced
  by the probe-evidenced key (see B4 fallback).
- **D3. The new fixture is a full-pipeline model (design part + calc usages), not
  extraction-only.** *Rejected: extraction-only like `zero_output_calc` (would
  not prove the return/bare-in forms flow through backtracker → graph →
  generation without downstream breakage).* Binding a bare `in x` in a usage is
  just `in x = <literal>` — not awkward, so the spec's fallback isn't needed.
- **D4. Auto-impl presence (style B) vs absence (style D) is asserted offline on
  the snapshot's `compilation_results` block, with the live extractor test kept
  for end-to-end stencil generation.** The snapshot nullifies raw
  `output_expression_asts` (REQ-SNAP-05), so AST *nodes* are invisible offline —
  but the full-pipeline capture threads `compilation_results` into the snapshot
  (`capture_extraction_snapshots.py:111`, built at `pipeline_builder.py:545-567`,
  keyed by `calc_def.name`, populated only when `output_expression_asts` is
  non-empty and try/excepted so style D skips rather than crashes). The loader
  exposes it as `snapshot["compilation_results"]` (`loader.py:115`). So the
  committed `return_styles` snapshot *pins* the compilation behavior: style B's
  def name is a key, style D's is absent. *Rejected: "the snapshot can't see
  auto-impl, so only a live test can" (true for raw ASTs, false for
  `compilation_results` in the Item-2 world — the offline assertion is stronger
  because it's committed and license-free).* The live test still earns its place:
  it verifies the return form generates a real stencil body end-to-end, which the
  compilation block alone doesn't prove.
- **D5. REQ numbering:** REQ-EXT-10 (direction-carrying ReferenceUsage extracted
  + inline-return auto-impl), REQ-EXT-11 (anonymous-return V8, before V7),
  REQ-EXT-12 (no double-ingestion of the body-assignment form). *Rejected:
  folding no-double-ingestion into REQ-EXT-10 (it is a distinct testable property
  and deserves its own row).*
- **D6. The IFE six-def confirmation is opportunistic, not a close gate.** The
  four-styles fixture covers the same inline-return shape and the spec-review
  already established (from the fusion-tea conversion diff) that all six were
  inline `return`. *Rejected: gating Item 3 close on a live IFE re-run (adds a
  license-dependent step for evidence already gathered; the fixture proves the
  mechanism).*

## Architecture

Two touch points, both inside `_extract_calculation_definition`
(`extractor.py:181-294`), plus one new private helper. Nothing else in the
extractor or downstream changes.

```
elem.owned_members
     │
     ├─ pass 1 (:203)  filter → _is_parameter_member  ← was is_instance(AttributeUsage)
     │     _extract_attribute → input/output split (unchanged)
     │     AST capture :223-228 (unchanged) → output_expression_asts
     │
     ├─ pass 2 (:241)  filter → _is_parameter_member  ← was is_instance(AttributeUsage)
     │     member_expressions for intermediates (unchanged)
     │
     ├─ V8 pre-scan (NEW, before :271)  raw members → nameless direction-Out? → raise
     └─ V7 guard (:271) zero output_attributes → raise (message revised)
```

**Data-flow invariance for existing models:** every existing fixture member is an
`AttributeUsage`, which matches branch 1 of the predicate exactly as
`is_instance(AttributeUsage)` did. `all_member_names`, `input_attributes`,
`output_attributes`, `output_expression_asts`, `member_expressions` are all
computed identically → byte-identical snapshots.

**The four forms after the change:**

| Form | syside node | Predicate | Result |
|------|-------------|-----------|--------|
| `out attribute y : Real = expr;` | AttributeUsage(Out) | branch 1 | output `y` + AST (unchanged control) |
| `return y : Real = expr;` | ReferenceUsage(Out) | branch 2 | output `y` + AST (**auto-impl**) |
| `in x : Real;` | ReferenceUsage(In) | branch 2 | input `x` |
| `return attribute y; ... y = expr;` | AttributeUsage(Out) + ReferenceUsage(None) | branch 1 admits `y`; None-ref excluded | output `y`, **no AST** (degraded, deferred) |
| `return : Real = expr;` | ReferenceUsage(Out), nameless | pre-scan → V8 | raises actionable diagnostic |

## Required Invariants

- **I1.** Every existing extraction snapshot and all 4 pipeline baselines are
  byte-identical after the change.
- **I2.** For the `return attribute y; ... y = expr;` form, `y` appears **once**
  in `output_attributes`, and the direction-None body ReferenceUsage appears in
  neither the attribute lists nor `member_expressions` (no phantom member).
- **I3.** V8 fires before V7 for an anonymous return: the modeler sees the
  name-the-result message, never the generic zero-output message. V8 fires on the
  anonymous member **whenever one is present, regardless of any other named
  outputs** — the anonymous return is itself the defect, so it is not masked by a
  sibling `out attribute`. (SysML likely forbids a second result alongside a
  `return` anyway; de-risk task #1 records whether the combination even parses —
  cover it there if cheap.)
- **I4.** Both member passes use the identical `_is_parameter_member` predicate.
- **I5.** Named inline `return y : Real = expr;` produces a non-empty
  `output_expression_asts["y"]` (auto-impl, not a stencil).

## Component Overview

- **`_is_parameter_member(member) -> bool`** — new private method on
  `SysMLDataExtractor` (`extractor.py`). Two-branch predicate (see Core Concept).
  Replaces the `is_instance(AttributeUsage)` gate at `:204` and `:242`.
- **V8 pre-scan** — a short loop over `elem.owned_members` inserted just before
  the REQ-EXT-08 guard (`:271`). Raises `ValueError` on the first member with
  direction Out and empty `sanitize_name`. Message wording below.
- **V7 message + modeling-assumptions row** — revised text (below); no longer
  cites "not yet extracted (Item 3)".
- **Fixture `tests/fixtures/return_styles/`** — 4 calc defs (one per style) +
  a design part with 4 calc usages binding all inputs. Full-pipeline capture.
- **Fixture `tests/fixtures/anonymous_return/`** — one calc def with an anonymous
  return. Live-only V8 test; no snapshot (extraction raises), mirrors
  `zero_output_calc`.
- **Conformance tests** — offline snapshot assertions (I/O, no double-ingestion)
  + live extractor tests (auto-impl AST presence, V8, revised V7).
- **A-2 stencil fix** — in `~/1cfe/agentic-mbse` sysml-conventions
  `references/stencils.md` (implementer verifies live line range; content below).

## Non-Goals

- **Body-assignment expression capture** (restore auto-impl for
  `return attribute y; ... y = expr;`). Deferred — backlog note. Style D extracts
  a correct *output*, just a manual stencil; nothing crashes.
- **Multi-output `return`** — not legal SysML.
- **Constraint execution, alias surfacing, type indexing, sanitization** — other
  epic items.

## Implementation Notes

**Predicate (interface, not implementation):**

```python
def _is_parameter_member(self, member) -> bool:
    if self.adapter.is_instance(member, "AttributeUsage"):
        return True
    if self.adapter.is_instance(member, "ReferenceUsage"):
        is_in, is_out = self._get_direction(member)
        return is_in or is_out
    return False
```

Because attributes never match branch 2 and reference usages never match branch
1, ordering is not fragile — but keep branch 1 first for clarity.

**V8 wording** (V1-style, names the fix):

> "Calc def '{name}' has an anonymous `return` (a result with no name), so no
> output channel can be built. Give the result a name, e.g.
> `return result : Real = <expr>`."

**Revised V7 wording — two live strings, edited separately.** They differ today,
so each is quoted exactly and gets its own replacement.

*`extractor.py:272-278` (current, exact):*

> "Calc def '{name}' extracted with zero output attributes. A pipeline module
> needs at least one output channel. Likely cause: return-style ('return y : Real
> = expr') or bare 'in' parameters, which are not yet extracted (Item 3);
> anonymous 'return' is unsupported. Declare an 'out attribute'."

*→ replace with:*

> "Calc def '{name}' extracted with zero output attributes. A pipeline module
> needs at least one output channel. Likely cause: the calc def declares no
> result — add one, e.g. 'out attribute y : Real = <expr>' or 'return y : Real =
> <expr>'. (An anonymous 'return' is reported separately.)"

*`modeling-assumptions.md:350` V7 row (current, exact):*

> "Calc def '{name}' extracted with zero output attributes. A pipeline module
> needs at least one output channel. Likely cause: return-style or bare `in`
> parameters (not yet extracted, Item 3); anonymous `return` is unsupported.
> Declare an `out attribute`."

*→ replace with:*

> "Calc def '{name}' extracted with zero output attributes. A pipeline module
> needs at least one output channel. Likely cause: the calc def declares no result
> — add one, e.g. `out attribute y : Real = <expr>` or `return y : Real = <expr>`.
> (An anonymous `return` is reported separately.)"

(The two keep their existing quoting styles — plain quotes in the code string,
backticks in the doc table.)

**Second-pass predicate detail:** switching `:242`'s gate to
`_is_parameter_member` is safe — intermediate locals (`attribute tmp : Real =
x*2;`) are direction-None `AttributeUsage`, so they still match branch 1 and are
still captured into `member_expressions` (they are neither input nor output). The
body-assignment ReferenceUsage is excluded by both the predicate (direction-None
ref) and the existing `member_name in output_names → continue` — belt and braces.

**A-2 stencil fix** (`references/stencils.md`, ~lines 39-41 per research — verify
live). Replace the expression-losing body-assignment stencil with the inline
return form:

```sysml
calc def <Name> {
    in <param> : Real;
    return <result> : Real = <expr>;   // inline expression → auto-implemented
}
```

Do **not** teach `return attribute <result> : Real;` + a separate `<result> =
<expr>;` — that form loses its expression.

## Potential Risks

- **Style D breaks `build_pipeline_context`.** If the degraded (no-AST) form
  raises during generation rather than falling to a `NotImplementedError`
  stencil, the full-pipeline capture fails. *Mitigation:* the compilation step is
  already safe — `pipeline_builder.py:547` guards on `if
  calc_def.output_expression_asts:`, so style D (empty ASTs) is skipped, never
  compiled, and the `:561` try/except catches any surprise. A stencil with
  `NotImplementedError` is the normal manual-impl artifact and should generate
  fine (it fails only at runtime execution, not codegen). If it does break
  capture, fall back: drop style D's design usage and assert style D via a
  live extraction-only test instead. Verify at implementation.
- **`return attribute y; ... y = expr;` may be hard to express parseably** in a
  fixture. *Mitigation:* the implementer confirms syside parses the chosen syntax
  before capturing; the expected extracted shape (output `y`, empty AST) is the
  assertion target regardless of exact body syntax.
- **`feature_value_expression` not populated on the return ReferenceUsage.**
  Would silently drop auto-impl. *Mitigation:* I5 live test catches it; research
  probe already confirms presence.
- **Item 2 snapshot format sequencing.** Item 2 (concurrent) may land a versioned
  snapshot format and promote the serializer into `src/sysml_codegen/snapshot/`.
  Capture the new fixture's snapshot with whatever capture surface is current at
  implementation time — do not pin a format. If Item 2 has landed, capture
  through the promoted `snapshot/` package so the format matches and Item 2's
  version-mismatch guard accepts it.

## Integration Strategy

The change is additive at the filter and diagnostic layer; it complements Item 1
(REQ-EXT-08/V7 zero-output guard) by narrowing V7's remaining scope and adding
V8. It makes the existing `01-extraction.md` canonical example (which already
teaches `return total_cost : Real = capacity * unit_cost;`) true as documented —
no example change needed, only requirement/matrix rows.

**Docs touched (R1 lockstep):**
- `docs/architecture/reference/01-extraction.md` — add REQ-EXT-10/11/12 rows to
  the Requirements table.
- `docs/architecture/modeling-assumptions.md` — revise V7 row; add V8 row.
- `docs/architecture/verification-matrix.md` — add REQ-EXT-10/11/12 rows (EXT
  section, after `:204`).
- Backlog: file the body-assignment-capture follow-up note.

## Validation Approach

- **Baseline invariance (I1):** re-run the capture surface; `git diff` on all
  existing snapshots + 4 pipeline baselines must be empty. A diff is a signal to
  investigate, not to re-baseline.
- **Offline snapshot tests** on `return_styles` (committed, license-free):
  - I/O — each of the 4 calc defs has the expected `input_attributes` /
    `output_attributes` (names + counts); style D's `y` appears exactly once (I2).
  - Auto-impl (I5) — assert on `snapshot["compilation_results"]` **keys**: style
    B's def name **is** a key (its inline `return` expression compiled), style D's
    def name is **absent** (EXPECTED degraded — comment points at the
    body-assignment-capture backlog note). Assert on key presence/absence, *not*
    on "the snapshot carries no compilation data" — that phrasing would break when
    Item 2 lands its snapshot-carried `compilation_results`. This assertion is
    format-stable across Item 2.
- **Live extractor tests** (skip without license, via `_load_live_extractor`):
  - I5 (end-to-end) — `return_styles` style B def has non-empty
    `output_expression_asts["y"]` at the raw extractor (the AST the offline
    `compilation_results` key was built from); style D def has empty
    `output_expression_asts`. This confirms the return form generates a real
    stencil body end-to-end — it complements, not replaces, the offline
    `compilation_results` assertion.
  - I3 — `anonymous_return` raises `ValueError` matching the V8 message, and the
    message is V8's (name-the-result), not V7's zero-output text.
  - Revised V7 — `zero_output_calc` still raises; match still holds on "zero
    output attributes" (the stable substring); assert the message no longer
    contains "not yet extracted".
- **Full-pipeline capture** of `return_styles` proves the new forms flow through
  backtracker → graph → generation without downstream break.

## Next-Stage Handoff

- **Fixed:** the two-branch predicate and its two sites; V8 as a raw-member
  pre-scan before V7; REQ-EXT-10/11/12 numbering; full-pipeline fixture shape;
  auto-impl asserted live; V7/modeling-assumptions rewording; A-2 stencil content.
- **Open (implementer's call at the file):** exact fixture SysML syntax for style
  D's body assignment (must parse); the live `references/stencils.md` line range;
  whether to also add a 5th pipeline baseline (not required — extraction snapshot
  + live auto-impl test suffice).
- **De-risk first, in order:**
  1. **Probe the anonymous-return node shape (B4).** Parse an anonymous `return :
     Real = expr;` live and record what syside produces: the member's
     `.direction`, its `.name` / `sanitize_name`, and whether it carries a
     result-parameter membership/heritage (`ReturnParameterMembership`). This is
     the one shape the research probe never covered, and it fixes V8's detection
     key. If direction is not Out or a name is synthesized, adopt the B4 fallback
     key **before** writing V8. Do this first — V8's rule depends on it.
  2. Confirm `return y : Real = expr;` populates `feature_value_expression` on the
     ReferenceUsage (auto-impl, B1/I5).
  3. Confirm style D generates a stencil without breaking `build_pipeline_context`
     (Risk 1) — decides whether style D keeps its design usage.

## Review Resolutions (design-review.md)

Verdict was **Revise**. Applied in place:

- **M1 (major) — V8 detection premise unprobed.** Promoted to Key Bet **B4** with
  an explicit "unproven, gates V8" flag and a named fallback (key off
  result-parameter membership/heritage if the probe shows a synthesized name or
  direction None). Added as **de-risk task #1** — probe the anonymous-return node
  shape live *before* writing V8. D2 and the V8 component now note the detection
  key is probe-confirmed.
- **M2 (major) — compilation_results in the Item-2 snapshot.** Verified live:
  `compilation_results` is threaded at capture (`capture_extraction_snapshots.py:111`,
  built `pipeline_builder.py:545-567`, try/excepted so style D skips not crashes)
  and exposed by the loader (`loader.py:115`). (a) Rewrote **D4**: the committed
  `return_styles` snapshot now *pins* compilation behavior (style B key present,
  style D absent). (b) Kept the live auto-impl test but corrected its rationale —
  it verifies end-to-end stencil generation, not "the only way to see auto-impl."
  (c) Validation Approach offline assertions now key off
  `snapshot["compilation_results"]` presence/absence — phrased to survive Item 2's
  landing (not "snapshots carry no compilation data"). Risk 1 mitigation cites the
  `:547` guard + `:561` try/except confirming style D skips rather than crashes.
- **Minor 1 — mixed anonymous + named outputs.** **I3** now rules V8 fires on the
  anonymous member regardless of other named outputs; notes SysML likely forbids
  the combination and defers the parse check to de-risk task #1.
- **Minor 2 — V7 wording against both live strings.** Implementation Notes now
  quote `extractor.py:272-278` and `modeling-assumptions.md:350` V7 *exactly*
  (they differ) and give each its own replacement, preserving each file's quoting
  style.

---
Next Step: After approval → `/_my_plan` (or `/_my_implement` for direct build).
