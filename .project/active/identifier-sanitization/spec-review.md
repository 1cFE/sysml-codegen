# Spec Review: Identifier Sanitization (SC-4, + SC-11 riders)

**Spec:** `.project/active/identifier-sanitization/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/identifier-sanitization/spec-review.md`
**Date:** 2026-07-05

---

## Reality Check

**Sound, with material gaps.** The central reversal holds up against HEAD. I verified every link
in the evidence chain:

- **(a)** `dependency_backtracker.py:660-663` compares `attr.qualified_name` — which is
  per-segment sanitized at `parameter_groups.py:141` via `build_element_qualified_name` — against
  a raw-replaced `source_path`. It does **not** consume `owning_part_qualified_name` or
  `calc_def_qualified_name`. So source-sanitizing those fields would not touch this site. The
  spec's claim that "663 is not the deciding one" is correct.
- **(b)** `output_registry_builder.py:130` registers the FORMULA output under a **raw** key
  (`SysMLQN(f"{ca.owning_part_qualified_name}::{ca.name}")`); the REFERENCE lookup at
  `dependency_backtracker.py:595` queries with a **raw** `SysMLQN(source_path)`. Raw-to-raw match
  confirmed. Source-sanitizing the registration side alone would break it.
- **(c)** The derivation layer touches no extraction data, so the committed snapshots stay
  byte-identical. Confirmed — the fix lives in `identifier_types.py` and the channel-derivation
  sites, none of which run at capture.

The direction is right. But the spec (1) claims a FORMULA-path fixture repro that the named fixture
cannot produce, (2) mis-scopes the duplicate-path fail-fast to one of three overwrite sites, and
(3) frames the source-vs-derivation call as "derivation wins" when the honest framing is "defer the
complete fix to Item 7." These are fixable with targeted edits — hence **Revise**, not Rework.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** The Success Criteria and Non-Goals say "all **10** extraction snapshots."
There are **11** committed (`git ls-files | grep extraction_snapshot.json`):
alias_agg_probe, attr_expr_probe, catf_mfe_model, chain_override_probe, chain_spike_model,
expression_binding_probe, issue22_model, return_styles, sample_model, solar_battery_model,
unresolvable_attr_probe. `alias_agg_probe` is the 11th, and under the derivation-layer choice it
too stays byte-identical (its snapshot holds raw quoted QNs that the fix never re-captures). The
count should read 11, and the spec should state plainly that the probe's own snapshot is included
in the byte-identical set — that fact is load-bearing evidence for the reversal, not a footnote.

**L1-2 · Question to the user (highest stakes):** Success Criterion #2 — "The FORMULA
channel/module_eqn path produces sanitized identifiers for a quoted-named owner (latent second leak
closed)" — has **no triggering fixture**. `alias_agg_probe` has `"computed_attributes": []`; no
committed snapshot anywhere carries a `FORMULA` classification on a quoted owner (`grep -l FORMULA
tests/fixtures/*/extraction_snapshot.json` returns nothing). The research report itself only calls
this leak *latent* — inferred from code (`sysml_to_python_qualified_name` on
`owning_part_qualified_name`), never reproduced. So as written, Item 5 ships the FORMULA
sanitization with the fix applied in code but exercised by no test — which violates R1 ("no new
behavior without a real fixture"). **Decision needed:** either add a FORMULA computed-attribute on
a quoted-named part (to `alias_agg_probe` or a new fixture) — which requires a *live extraction
re-capture*, colliding with both the "no re-capture / byte-identical" benefit the spec leans on and
the 2026-08-06 license window (R3) — or downgrade SC #2 to a code-level assertion and file the
fixture as a follow-up. You can't have both "byte-identical, no re-capture" and "FORMULA leak
proven dead by a fixture" without paying a live capture. Which one gives?

**L1-3 · Direct claim:** The spec calls the five FORMULA sites a "pure name-derivation change with
zero resolution behavior change." One of them is not pure derivation. `pipeline_builder.py:70`
builds `formula_qns` from `sysml_to_python_qualified_name(owner)` and then **uses it as a match
set** at line 81 (`a.qualified_name not in formula_qns`) to strip FORMULA attributes'
design-attribute twins. `a.qualified_name` is per-segment sanitized; the set is raw-replaced — so
for a quoted owner they mismatch today and the twin is *not* removed (a latent false entry point).
Sanitizing line 70 fixes that mismatch, which is a real behavioral change for quoted FORMULA
owners. It's a no-op on every non-quoted baseline, so the byte-identical claim survives — but "zero
resolution behavior change" is imprecise. State it as: no change on existing (unquoted) models; a
latent correctness fix for quoted FORMULA owners.

### Lens 2 — Problem & Approach

**L2-1 · The central question (if-then / reframe):** The prompt asks why "sanitize BOTH sides of
the registry key" (source-sanitization done completely) is worse than the derivation layer. After
tracing it: **it isn't worse — it's the same direction, and it's what Item 7 will do anyway.**
Sanitizing both sides means flipping the registration key (`output_registry_builder.py:130`) *and*
the lookups (`dependency_backtracker.py:595`, and the `:660` / `parameter_groups.py:439` matching
sites) from raw to sanitized together. Those lookups are exactly the matching sites the spec
(correctly) reserves for Item 7. So the real reason to prefer the derivation layer *now* is
**item-boundary discipline**, not permanent superiority: Item 5 does the minimal name-derivation
slice; the "complete" key-pair sanitization is **deferred to Item 7**, which owns the behavioral
matching work. The snapshot-re-capture argument is a genuine but *secondary* benefit — and, as the
prompt notes, Item 2 made re-capture cheap, so it can't be load-bearing. Recommend the spec reframe
the decision this way: not "derivation beats source," but "do the derivation slice now; defer the
both-sides key sanitization to Item 7." This is more honest and it sets Item 7's expectations
correctly (see L2-2).

**L2-2 · Direct claim (Item 7 handoff):** The spec presents `output_registry_builder.py:130`
staying raw as an *invariant* ("leaving the line-130 registration key raw → the raw-to-raw
REFERENCE match is preserved"). It's a *temporary state*. When Item 7 sanitizes the REFERENCE
lookup at `:595` (its stated job — reuse Item 5's helper on the REFERENCE path), it MUST flip the
`:130` registration to sanitized in lockstep, or the FORMULA REFERENCE match breaks (sanitized
lookup vs. raw key). The spec's Item 7 handoff (the "shared sanitized-QN matching helper" it
leaves) gives Item 7 the helper *function*, which is the right shape — but it does not flag that
Item 7 inherits an obligation to change `:130` too. Add that to the Item 7 dependency note so it
isn't discovered mid-implementation.

**L2-3 · Confirm (helper shape leaves Item 7 what it needs):** The helper as specced —
`sanitize_qualified_name(qn)` = split `::`, `sanitize_name` each segment, join `__`, applied only
at derivation sites, `sysml_to_python_qualified_name` left unchanged — is exactly what Item 7 needs
at the REFERENCE matching path (research SC-8: "per-segment-sanitizing QN conversion (REFERENCE
path — reuse Item 5's helper)"). This part is sound. The only gap is L2-2's registration-side
coupling, which is Item 7's to own but Item 5's to flag.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim (duplicate-path is under-scoped):** The fail-fast is specced at
`cli/__init__.py:214` (the module write). The silent-overwrite class actually spans **three** write
paths in **different key spaces**:
- **Modules** — `modules_dir / python_path.full_path`, write at `:223`. Keyed by the usage EQN's
  lowercased element name.
- **Stencils** — `{python_path.filename}_impl.py`, writes at `:271` / `:285` / `:299`. Same
  filename key as modules (a module collision implies a stencil collision).
- **Schemas** — `schemas_dir / f"{module.calc_def_name.lower()}_output.py"`, write at `:185`.
  **Keyed by `calc_def_name`, a different collision space.** Two calc defs whose names sanitize to
  one lowercased name (`'Margin Calc'` and `'margin calc'`) collide on `margin_calc_output.py`
  *even if their module paths differ*.

The spec's Open Question proposes "a pre-generation pass over all derived `full_path`s" — that only
covers module paths and would miss a schema-name collision entirely. Either widen the pre-pass to
cover the schema (`calc_def_name.lower()`) and stencil key spaces, or explicitly scope the check to
modules and record the schema/stencil residual as a known gap. As written, SC #4 ("never a silent
overwrite") is stronger than the mechanism the spec points at.

**L3-2 · Direct claim (conformance test doesn't lock the FORMULA wire):** The test asserts (1)
every file `ast.parse`s and (2) each registry-imported class name is declared by its module. That
locks the CalcUsage class-name / module-path leak (`ModuleType.from_sysml` /
`PythonModulePath.from_sysml`, verified: both use raw `sqn.element_name`). It does **not** assert
that a FORMULA channel *produced* by one module is *consumed* under the identical name downstream.
This matters because the channel is derived two different ways:
`output_registry_builder.py:124-126` builds `module_eqn` from `ca.python_name`, while
`graph_builder.py:745` builds it from raw `ca.name`. They coincide only when
`sanitize(name) == python_name` — which the per-segment helper guarantees *if applied consistently
to all five sites*, but a missed site would produce a "sanitized-but-mismatched" wire that
`ast.parse` + import-name checks would not catch. Combined with L1-2, this is the argument for a
*consumed* FORMULA-on-quoted-owner fixture and a "the wire resolves" assertion.

**L3-3 · Question (SC-11 fail-fast could break a baseline):** The recommended in-scope rider turns
the post-alias grandparent collision (`registry.py:103-108, 115` — alias uses only the parent
segment) into a hard fail-fast. Confirm no committed fixture/baseline hits the
two-`pump`-under-different-grandparents case. If one does, adding the fail-fast converts a
currently-generating model into a hard error — which would break the "all baselines byte-identical"
criterion (it becomes an error, not a diff). Research confirms the aliased baseline is parseable
but does not confirm it avoids the grandparent case.

### Lens 4 — Hygiene

**L4-1 · Rewrite request (minor):** `output_registry_builder.py` is cited without its path; it's in
`orchestration/`, not `resolution/`. The "Code touchpoints" cites `:124` (the channel derivation)
while the source-vs-derivation section's deciding site is `:130` (the registration key) — both are
real and distinct, but a reader skimming the touchpoints list won't connect them. Worth one line
tying `:124` (leak value) and `:130` (match key, left raw) together. Low value; fold into any edit
pass.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request (tied to L2-1):** "The source-vs-derivation decision" section leads with
"The flagged site (663) is not the deciding one" and then pivots through three line numbers
(663 → 130 → 595) and their raw/sanitized states before the reader learns the actual conclusion. A
tired reader has to hold all three to follow it. If the reframe in L2-1 is accepted, lead the
section with the conclusion — "Item 5 does the name-derivation slice; the complete both-sides key
sanitization is Item 7's, deferred not rejected" — then give the three-line-number mechanism as
support. Same facts, but the point arrives first.

---

## Engagement Summary

**Overall take:** The reversal is correct and every code link checks out against HEAD — the
derivation layer is the right place for Item 5. But the spec oversells it in three ways: it claims a
FORMULA-leak fixture that the named fixture can't produce, it scopes the "never overwrite silently"
guarantee to one of three overwrite sites, and it frames the source-vs-derivation call as a
permanent win when it's really a deferral of the complete fix to Item 7. All fixable; the work item
is sound.

**Here's what I need you to weigh in on:**

1. **[L1-2, L3-2]** The FORMULA path (SC #2) has no triggering fixture — `alias_agg_probe` has
   zero computed attributes, and the leak was only ever code-inferred. Do you add a
   FORMULA-on-quoted-owner fixture (needs a live re-capture, against the license window and the
   "byte-identical / no re-capture" benefit), or downgrade SC #2 to a code assertion + follow-up
   fixture? You can't keep both "no re-capture" and "leak proven dead by a test."
2. **[L2-1, L2-2]** Reframe the central decision: "sanitize both sides of the registry key" isn't
   worse than the derivation layer — it's the same direction, deferred to Item 7 (which owns the
   matching sites). Accept the reframe, and add the note that Item 7 must flip
   `output_registry_builder.py:130` in lockstep with the `:595` lookup or the FORMULA REFERENCE
   match breaks.
3. **[L3-1]** The duplicate-path fail-fast is specced at the module write only. The overwrite
   hazard also lives at the stencil writes and — in a *different* key space — the schema write
   (`calc_def_name.lower()`). Widen the check to all three, or scope it to modules and record the
   residual. SC #4 currently promises more than the mechanism delivers.
4. **[L1-1, L1-3]** Two precision fixes: the snapshot count is 11 not 10 (and `alias_agg_probe`'s
   snapshot is in the byte-identical set); and `pipeline_builder.py:70` is a match site, not pure
   derivation, so "zero resolution behavior change" should read "no change on unquoted models; a
   latent fix for quoted FORMULA owners."
5. **[L3-3]** Confirm no committed baseline hits the SC-11 grandparent-collision case before making
   it a fail-fast, or that rider breaks the byte-identical criterion.

Numbering and coordination notes check out: REQ-NC-08/09 and REQ-REG-08 are free (doc 15 stops at
NC-07, doc 20 at REG-07); V-rules stop at V8 in modeling-assumptions, so V11 is unclaimed (though
the spec rightly notes the duplicate-path guard is more naturally a generation invariant than a
V-rule). The agentic-mbse impact list and the fusion-tea `sanitize_names.py` retirement note are
both present.

---

## Resolutions

*Filled in during Stage 5, keyed by finding ID.*

---

**Verdict:** Revise

**Next Steps:** Record resolutions above, then re-run `/_my_spec` (or return to the spec-agent
session) and point it at this review to incorporate. The reviewer does not edit the spec. The
highest-stakes items are the FORMULA-fixture decision (L1-2/L3-2) and the duplicate-path scope
(L3-1); the L2-1 reframe is presentation but it also fixes the Item 7 handoff (L2-2).
