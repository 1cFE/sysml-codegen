# Design Review: Identifier Sanitization (SC-4 + SC-11 riders)

**Design:** `.project/active/identifier-sanitization/design.md`
**Spec:** `.project/active/identifier-sanitization/spec.md`
**Review File:** `.project/active/identifier-sanitization/design-review.md`
**Date:** 2026-07-05
**Reviewed against:** committed HEAD `35e54cb` (Item 4's working-tree churn in `usage_extractor.py` / `hierarchy_resolver.py` ignored except where noted)

---

## Fundamental Assessment

**Sound.** The approach is right and minimal: one new pure helper (`sanitize_qualified_name`),
dropped in at the FORMULA module_eqn sites, plus an inline per-segment sanitize in the two
`from_sysml` methods. No new module, no new data model, no new abstraction. It reuses the existing
`sanitize_name` primitive, the existing fail-fast precedent (SC-2 zero-output,
`_validate_channel_references`), and the existing collision-resolution code. A senior engineer would
not ask "why is this so heavy" — if anything the surface is admirably small for the blast radius.

The derivation-layer-vs-source call is correctly framed as item-boundary discipline (defer the
both-sides key flip to Item 7), and every code link in that argument checks out against HEAD
(`:130` raw key, `:595` raw lookup, `:663` not the deciding site).

Proceeding to the detailed review. The findings below are **refinements, not a rework** — the two
that matter (M1, M2) are precision gaps that could let a broken wire pass the very fixture meant to
catch it.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Every HARD spec requirement has a design element: derivation-layer sanitize (helper + `from_sysml`),
three-key-space fail-fast, `alias_agg_probe` full-generation test, new FORMULA fixture, SC-11
gated re-check, Item 7 lockstep handoff, docs/agentic-mbse carry-through. The match sites and `:130`
are correctly held raw (INV-3).

Two compliance gaps, both about the FORMULA fixture that SC #2 leans on:

- The fixture's job is to prove "the wire resolves, produced == consumed under the identical name."
  As specced the assertion is name-equality of the two channel derivations. But the design does not
  pin the fixture's **resolution topology** (M2) — and with the wrong topology the fixture either
  exercises Item 7's raw-QN path or proves less than it claims.
- The design's B2 rationale (M1) mis-describes where `python_name` comes from, which undercuts the
  "produced == consumed" reasoning the fixture is built on.

### 2. Pattern Consistency
**Assessment:** Pass

`sanitize_qualified_name` joins `sanitize_name`'s family in `core/qualified_names.py` — the right
home, exported in `__all__` alongside `sysml_to_python_qualified_name`. The fail-fast pre-pass
mirrors existing generation-time guards. The SC-11 re-check extends
`_resolve_class_name_collisions` (`registry.py:60-129`) rather than inventing a parallel mechanism.
The `graph_builder.py:271-275` EXPOSE_PURE ad-hoc is **character-for-character** the helper body
(verified) — collapsing it (D3) is correct and removes a real drift seam.

### 3. Abstraction Quality
**Assessment:** Pass

The helper earns its existence: it is the single point where `::`→`__` becomes per-segment-sanitizing,
and it is the exact function Item 7 reuses at the REFERENCE path. D4 (route the `__`-joining helper at
the FORMULA sites, but sanitize inline in `from_sysml`) is justified — `from_sysml` joins with `.`/`/`,
lowercases, and appends `Module`, so it genuinely cannot use a `__`-joining helper; both paths still
bottom out on the same `sanitize_name` primitive (scrutiny 3). The residual "duplication" is a
one-line split-and-map loop, not worth a shared per-segment primitive.

One real drift seam lives elsewhere — see M1 (two different `_sanitize_name` implementations).

### 4. Duplication Avoidance
**Assessment:** Concerns

The `::`-split duplication (scrutiny 3) is benign. The duplication that bites is the **two
sanitizers**: `core.qualified_names.sanitize_name` (what the helper uses) and
`extraction.expression_compiler._sanitize_name` (what produces `ca.python_name`,
`computed_attribute_extractor.py:226`). They are copy-pasted and differ in one branch —
reserved-word suffixing (expression_compiler.py:174-175 explicitly drops it). The design treats
`python_name` as if it were `sanitize_name(name)`; it is not. This is the drift the fixture should
be guarding, and the design doesn't name it (M1).

### 5. Data Structure Clarity
**Assessment:** Concerns

The raw `::` QN riding on `qualified_name` / `owning_part_qualified_name` to the derivation layer is
explicit and traceable. One data-availability question for the error text (m3): the fail-fast must
name **both raw source names**, but after sanitize the colliding modules share an identifier — the
distinguishing raw spelling has to come from `PipelineModule.calc_def_qualified_name` (raw, verified
present at `resolution/models.py:185`). Confirm it is populated for **FORMULA** modules too, which
may carry `calc_def_name = None`.

### 6. Route Safety
**Assessment:** Concerns

The fail-fast is the right shape — fail before any write. But the placement ("after `:707`, before
`_generate_schemas`") runs it **after** `_clear_output_directory` (`cli/__init__.py:709-711`, gated
on `config.overwrite`). On a collision the user's existing output is already wiped before the error
fires. Move the pre-pass ahead of `_clear_output_directory`, not just ahead of `_generate_schemas`
(m2). Otherwise routing is explicit; no wildcard/fallback hazards.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

B1/B3/B4 are honest bets with real "if false" consequences. The decisions (D1–D5) each name the
rejected alternative. Two integrity issues:

- **Hidden bet behind B2.** B2 is stated as "coincide iff `sanitize_name(ca.name) == ca.python_name`,"
  which reads as near-tautological. The load-bearing, *unstated* belief is that the two distinct
  sanitizer implementations agree on `ca.name`. They agree for every name that does **not** sanitize
  to a Python keyword, and disagree for `class/def/import/from/return/yield` (M1). That is the real
  bet, and it is currently invisible.
- **INV-1 overclaims (M3).** As written ("every segment matching `[A-Za-z0-9_]+`") the invariant is
  false: `value_`, `_x`, `a__b`, and `class` all match the regex yet `sanitize_name` changes them.
  The claim survives on the corpus only because no snapshot segment has a leading/trailing or doubled
  underscore or a reserved word (verified across all 11 snapshots). State it as an empirical,
  corpus-scoped fact, not a mathematical identity.

### 8. Reader Comprehension
**Assessment:** Pass

Dense but navigable. Core Concept states the idea (sanitize at emission, no-op on unquoted) before
the mechanism. The site-by-site before/after appendix is a genuine aid — a reader can see the leak
and the fix in one table. INV-1..INV-5 give the reader the checkable claims up front. No coined label
hides complexity. The one comprehension cost is that INV-1 and B2, as worded, will mislead the
implementer about *why* they hold (M1/M3) — a precision problem, fixed by restating them.

---

## Issues by Severity

### Critical
- None. The direction is sound; do not rework.

### Major
- **M1 — B2/INV-5 rests on an undisclosed two-sanitizer agreement; the fix can turn a working wire
  into a broken one.** `ca.python_name` is produced by `expression_compiler._sanitize_name`
  (`computed_attribute_extractor.py:226`), **not** `core.sanitize_name`. The two are copy-paste twins
  that differ only in reserved-word suffixing (`expression_compiler.py:174-175` drops it).
  - Producer channel (`output_registry_builder.py:124-126`) builds the module_eqn leaf from
    `ca.python_name`.
  - Consumer channel (`graph_builder.py:745`), as the design specs it, becomes
    `sanitize_qualified_name(f"{owner}::{ca.name}")` — leaf = `core.sanitize_name(ca.name)`.
  - They coincide iff `core.sanitize_name(name) == expression_compiler._sanitize_name(name)`, which
    **fails** when `name` sanitizes to `class/def/import/from/return/yield`. For such a name the wire
    matches *today* (both sides land on the un-suffixed form) and would **mismatch after the fix**
    (consumer gets `class_`, producer keeps `class`).
  - **Recommendation:** at `graph_builder.py:745` build the leaf from the already-computed
    `ca.python_name`, i.e. `sanitize_qualified_name(owner) + "__" + ca.python_name`, rather than
    re-sanitizing `ca.name` through the helper. That makes producer == consumer **structural** (both
    use `python_name`), removes the keyword edge, and eliminates the coincidence dependency entirely.
    Then B2 becomes a fact, not a bet, and the fixture's job narrows to "no site was missed." Also
    correct the design's prose to stop equating `python_name` with `sanitize_name(name)`.

- **M2 — the FORMULA fixture's resolution topology is unspecified; wrong topology defeats its
  purpose.** "A quoted part def owning a FORMULA attribute wired to a consumer" is ambiguous.
  - A **same-part** FORMULA consumer resolves through the in-memory `resolution_map`
    (`graph_builder.py:739-749`, consumed at `:823`) / the `ScopedKey` `key_f`
    (`output_registry_builder.py:137`, per-segment clean via `python_name`). This path is
    Item-7-independent and is the one the design's argument relies on.
  - A **cross-part REFERENCE** consumer resolves through the raw `SysMLQN` key at `:130` / lookup at
    `:595` — Item 7's territory. On a quoted owner that raw-to-raw match is fragile (both sides must
    spell the quoted name identically), and it is exactly the path Item 5 must not depend on.
  - **Recommendation:** pin the fixture to a **same-part** FORMULA→consumer topology, and have the
    conformance test assert the resolved input channel **equals the registered canonical channel**
    (proving the `resolution_map`/`ScopedKey` path was taken), not merely that the file `ast.parse`s
    or that two derivations are string-equal. As scrutiny 5 put it: assert the path, not just the
    outcome.

- **M3 — INV-1's stated precondition is false; the byte-identical guarantee is corpus-scoped, not
  algebraic.** Segments matching `[A-Za-z0-9_]+` can still change under `sanitize_name` (leading /
  trailing / doubled underscore, or a reserved word). Verified this does **not** bite any of the 11
  committed snapshots (all segments use single internal underscores only), so INV-4 holds — but the
  reasoning as written is wrong and would mislead a future contributor.
  - **Recommendation:** restate INV-1 precisely ("no segment has a leading/trailing underscore, an
    internal `__` run, or is a Python keyword — verified across the committed corpus"), and add a
    constraint that the **new FORMULA fixture's owner QN** avoid such segments (or the no-op / B2
    claims break on the very fixture being added).

### Minor
- **m1 — line anchor `usage_extractor.py:573` is wrong even at HEAD.** The `calc_def_name =
  sanitize_name(get_calc_def_name(elem))` sanitize is at **`:399`** on committed HEAD (verified; the
  claim itself is true). Item 4 is editing this file now, so the anchor will move again — re-anchor
  at implement, don't trust `:573`.
- **m2 — run the duplicate-path pre-pass before `_clear_output_directory`** (`cli/__init__.py:709`),
  not just before `_generate_schemas`, so a collision error doesn't first wipe the user's existing
  output (see Route Safety).
- **m3 — confirm raw-name provenance for the error text on FORMULA modules.**
  `PipelineModule.calc_def_qualified_name` (raw) exists (`resolution/models.py:185`) and carries the
  distinguishing quoted spelling for calc-usage modules; verify it is populated for FORMULA computed-
  attribute modules (which may have `calc_def_name = None`) so "names both sources" is achievable in
  every collision case.
- **m4 — stencil write-line anchors drift.** Design cites the stencil write at `:299`; actual writes
  are at `:271/:285/:298`. Cosmetic, but re-anchor with the others. (The substantive claim — stencil
  shares the module filename key, so the module check covers it — holds.)
- **m5 — re-verify V/REQ numbering at implement.** Item 4 lands V9/V10 concurrently; the design's
  "V9/V10 reserved by Item 4, V11 next" and REQ-NC-08/09, REQ-REG-08 assignments should be
  re-confirmed against docs 15/20 at implement time, same churn risk as the line anchors.

---

## What checks out (do not relitigate)

- **INV-2 is sound.** `sanitize_name` collapses `_+`→`_` (`qualified_names.py:31`) and strips
  leading/trailing `_` (`:33`), so applying the helper to an already-`__`-joined string would eat the
  separator — the design correctly applies it exactly once at the `::` boundary. Empty-sanitizing
  segments (e.g. `'&'`) fall back to `"unnamed"` (`:33`), so the join never produces `____` or a
  dangling separator. No segment value breaks the chosen order; collisions from `"unnamed"` are the
  duplicate-path check's job, and it compares final paths, so it catches them.
- **Site mapping is accurate.** `:124` (channel value, uses `python_name`), `:130` (raw SysMLQN key),
  `graph_builder.py:745/789/818` (module_eqn / part_eqn), `:791` (`derive_module_type` →
  `ModuleType.from_sysml`) all verified. Both `from_sysml` methods use the **raw** `sqn.element_name`
  today (`identifier_types.py:107,143`) — the leak is real.
- **D3 collapse is safe** — `graph_builder.py:271-275` is byte-identical to the helper body.
- **The derivation-vs-source decision holds** — `:130` raw key and `:595` raw lookup confirmed;
  same-part FORMULA resolution goes through `resolution_map`, not the `:130`/`:595` QN path, so the
  fixture can be Item-7-independent (contingent on M2's topology pin).
- **SC-11 mechanics** — the alias uses only the parent segment (`registry.py:104-116`), so two
  same-named scopes under different grandparents with the same parent still collide; the post-alias
  re-group re-check detects exactly that. Gating it on the static scan (B4/D5) is the right call.

---

## Recommendations

1. **M1:** derive the consumer FORMULA module_eqn leaf from `ca.python_name` at `graph_builder.py:745`
   so producer == consumer is structural; drop the prose that equates `python_name` with
   `sanitize_name(name)`; note the `expression_compiler._sanitize_name` vs `core.sanitize_name`
   divergence explicitly (and, if in scope for the plan, flag the two sanitizers for eventual
   consolidation).
2. **M2:** pin the new fixture to a same-part FORMULA→consumer topology and assert the resolved
   channel equals the registered canonical channel (path, not just outcome).
3. **M3:** restate INV-1 as a corpus-verified fact with the precise segment exclusions, and constrain
   the fixture's owner QN to avoid leading/trailing/doubled-underscore and keyword segments.
4. **m1–m5:** re-anchor `usage_extractor.py:573`→`:399` (and expect Item 4 churn); move the pre-pass
   ahead of `_clear_output_directory`; confirm FORMULA-module raw-name for the error text; fix the
   stencil write anchors; re-verify V/REQ numbering at implement.

---

## Resolutions

*Filled in during Stage 4 with the user. One entry per resolved issue — this is what the design agent
reads to incorporate the review.*

---

**Overall:** Revise
**Next Steps:** Record resolutions above, then re-run `/_my_design` (or return to the design-agent
session) and point it at this review to incorporate. The reviewer does not edit the design. Highest
stakes are M1 (structural produced==consumed) and M2 (fixture topology) — both concern whether the
FORMULA fixture actually proves the wire it claims to; M3 is a precision fix to keep the byte-identical
reasoning honest.
