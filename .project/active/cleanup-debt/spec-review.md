# Spec Review: Dead Code & Cleanup Debt (PIPELINE-TRUTH Item 8)

**Spec:** `.project/active/cleanup-debt/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/cleanup-debt/spec-review.md`
**Date:** 2026-07-06

---

## Reality Check

**Sound.** I re-ran the load-bearing greps for every B-row function, both templates, the
skipif guards, and the Row D dispatch code. The spec's zero-caller evidence holds: the
enumerations are accurate (two trivial omissions noted in L1-1), the deleted symbols are
genuinely dead, the aggregation bug is real and reproduces the code the spec describes,
and the epic's seven Item-8 scope points are all covered with no unsanctioned additions.
This is a well-built deletion catalog. The defects are not "wrong targets" — they are
**loop-closing gaps**: dispositions that stop one step short of the "nothing left filed
in a plan file" bar the item sets for itself. Verdict is Revise, not Rework.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim (minor): two caller enumerations miss a doc/comment site each —
the exact kind of stale-doc this item exists to kill.**
- `map_sysml_type_to_rootmodel_wrapper`: the spec lists callers as "its own def, the
  `__all__` entry (`:81`), and one conformance test." It misses
  `type_mapping.py:9` — the module docstring bullet
  `- map_sysml_type_to_rootmodel_wrapper(): SysML type -> RootModel wrapper`. Deleting the
  function leaves that docstring describing a symbol that no longer exists.
- `binding_to_entry_point`: the spec's HEAD site list (62/81/177/218/304/373/405/421/440)
  omits `dependency_backtracker.py:179`, the comment
  `# Unified binding resolutions (replaces _binding_to_entry_point)`, which names the dict
  being deleted.
  Both are covered *in principle* by SC-G/R1 ("every touched component's docstring
  updated"), but the row-level enumerations are the item's contract for "what to cut," and
  a deletion-heavy spec should not leave a doc-line naming a deleted symbol out of its own
  grep list. Add both sites to the respective rows.

**L1-2 · Verified — not a finding (recording so it isn't re-raised).** The Row D "known
deviation from REQ-AST-03" citation is *correct*. doc-19 line 36 defines REQ-AST-03 to
cover "all literal/null branches SHALL dispatch **before** the invocation catch-all," and
BACKLOG:196 confirms it as "a known deviation from revised REQ-AST-03." I checked this
because a doc-truth item mis-citing a REQ would be self-defeating; it does not.

### Lens 2 — Problem & Approach

**L2-1 · Direct claim: the framing and sizing are right.** One reviewed pass that either
clears or files each row is the correct shape for scattered low-risk debt, and bundling
the aggregation bug (the one executable-path item) with a byte-identity gate is defensible
— it is the only row that needs the gate, and isolating it into its own item would be
overhead. No sizing finding. The bet ("clear it now, before PUSH-DOWN moves these
surfaces") is stated and sound (Problem §Sequencing).

### Lens 3 — Pipeline Risk

**L3-1 · Question to the user: the REQ-PGD-06 handoff is recorded only on *this* end —
Item 7 does not exist yet to receive it.** `.project/active/matrix-truth/` (Item 7) is an
**empty directory**; it has no spec. The spec hands the REQ-PGD-06 re-frame to Item 7 via
a coordination note *in Item 8's own spec.md* (§Coordination recorded). That is precisely
the "filed only in a plan file" anti-pattern the item's own [NEED] rails against — if
Item 8 lands and someone spec's Item 7 next week, nothing in Item 7's required reading
points back here. **For the fork-B "delete" outcome, the handoff needs a durable home
Item 7 will actually read — a BACKLOG entry or a register line, carrying the
conditionality ("only if `get_default_value` was deleted").** (By contrast, the Item-4
`_deserialize_constraint_info` handoff *is* solid: Item 4 is fully spec'd/designed/planned
and its artifacts already name the symbol — that one is recorded on both ends.)

**L3-2 · Direct claim: deleting `get_default_value` strands doc-17 and matrix:379
immediately, but the spec assigns the fix to an item that runs later.** REQ-PGD-06 is not
just a matrix row. It lives in three places:
- `reference/17-parameter-group-deriver.md:26` — the REQ table row naming
  `get_default_value()`.
- `reference/17-parameter-group-deriver.md:143` — prose describing the live method.
- `verification-matrix.md:379` — PASS, verified by `test_parameter_group_deriver.py` (the
  very tests the spec deletes).
  The spec's row B says "hand the REQ-PGD-06 re-frame to Item 7," and the [INFERRED] req
  scopes "any matrix re-frame" to Item 7. But R4 step 4 / R1 make **this** item responsible
  for the reference-doc it renders stale. Deleting the method while leaving doc-17:26/143
  describing it is the doc-lie the epic exists to kill. And matrix:379 will read PASS via a
  deleted test until Item 7 runs — a silent "PASS row pins less than its text" gap.
  **Decide and state the split:** does Item 8 update doc-17 here (per R1) and hand *only*
  the matrix PASS-row re-frame to Item 7, and does it leave a visible breadcrumb on
  matrix:379 so the transient gap isn't silent? "Hand it all to Item 7" is not consistent
  with the item's own R1 discipline.

**L3-3 · Rewrite request: the spec has no stated test-deletion rule, and SC-G doesn't tell
the count-change story.** The item deletes tests (map-function dedicated cases,
`get_default_value` tests, the `test_data_models.py:361` field-name assertion). Item 6's
epic rule is "no test deleted without a replacement" — that is *Item 6's* rule, and this
item is explicitly different, but the spec never says what *its* rule is. SC-G ("full suite
green") is satisfiable by silently deleting a failing/orphaned test, which is exactly the
move that needs a guardrail here. State the rule plainly: **delete a test only when its
sole purpose was pinning the now-deleted dead symbol (no live behavior loses coverage),
and expect a net test-count decrease** — then have SC-G name the expected decrease and why
it is not a coverage loss, so "green" is auditable rather than assumed.

**L3-4 · Direct claim: the fixed `_walk_aggregation_ast` has no clean REQ to be
verified-by, and the doc close-out step names the wrong ones.** doc-19's Known-deviation
note puts `_walk_aggregation_ast` **explicitly out of scope** of the ordering REQs ("out of
the display-only scope of REQ-AST-08/-09"). REQ-AST-03/-08 are scoped to
`reconstruct_expression` by their own text (doc-19:36,38); REQ-AST-05 governs
`_walk_aggregation_ast` but only for "classify FCE nodes as SingletonTerm" — nothing to do
with literals. So the spec's docs step ("reconcile REQ-AST-03/-05 verified-by") is muddy:
neither REQ, as written, will verify the fixed literal ordering in this function. **Name
concretely what happens to the requirement surface:** does REQ-AST-03 get re-scoped to
cover `_walk_aggregation_ast` too, or does a new/extended REQ pick it up — and is that a
matrix change that must coordinate with Item 7? Right now the fix moves code from
"documented-as-deviation" to "documented-as-conforming" without saying which REQ it now
conforms to.

**L3-5 · Direct claim: the aggregation BACKLOG entry is tagged "Absorbed," not closed —
and the spec's row-D disposition never lists closing it.** `BACKLOG.md:185-197` is the real
filed home of this bug, already annotated "*→ Absorbed into PIPELINE-TRUTH Item 8*." Row D
lists retiring the doc-19 note and reconciling REQs, but never "retire/close BACKLOG:185
on completion." For an item whose thesis is register discipline, the BACKLOG entry that
tracks this exact bug must be closed when the fix lands — add it to row D's disposition.

**L3-6 · If-then tradeoff: SC-11 (row G) can be satisfied by declaring "not small → file"
without recording the assessment.** The disposition is forced either way (implement, or
file a P3 BACKLOG entry + correct the false close-out claim), which is good — implement
*cannot* silently skip. But "implement if small; else file" leaves "small" undefined and
the assessment output unspecified. If the intent is a real assess-then-decide, **require
the assessment verdict itself to be recorded** (what the registry alias-rewrite
no-not-found branch comparison showed, and the size judgment), so "file" is a reasoned
outcome and not the path of least resistance. If the intent is "default to file, implement
only if it's a one-liner," say that — either is fine, but the spec is currently ambiguous
about which.

**L3-7 · Rewrite request (minor): the byte-identity gate is not version-explicit.** SC-2
and Row D's Gate say "all existing corpora stay byte-identical" without naming v1 vs v2.
The [HARD] sequencing req (spec:211-216) resolves the ambiguity well — before-Item-4
(judge against v1) or after (judge against v2), never interleaved — but the gate sentence
itself should point at that req, so an implementer reading SC-2 alone knows which baseline
set the identity is judged against. One cross-reference closes it.

### Lens 4 — Hygiene

**L4-1 · Rewrite request (minor): the two templates are filed under "generation/ symbols"
but live one directory up.** The coordination note (spec:250) calls the two `.jinja2`
files "`generation/` symbols" and flags `templates/` to the generation-boundary owner. They
actually live in `src/sysml_codegen/templates/` (a sibling of `generation/`, confirmed by
`find`). The deletion path is fine; only the "generation/ symbols" label is loose. Not
worth more than a word.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request: the two "F" numbering series collide and will confuse a tired
reader.** The spec runs two independent finding namespaces with near-identical labels:
- **DOCS-SCRUB-F1 / F3** (row A/B header, row C header) — BACKLOG findings from the
  docs-scrub pass.
- **D1-F1 … F5** ("every D1 finding (F1–F5)"; row F writes them "F-2, F-3, F-4, F-5"; row G
  is "D1-F1") — discovery-register findings.
  So "F-2" (D1 sanitizer consolidation) sits in the same document as "DOCS-SCRUB-F2" (the
  `resolve_input` cutover, a *different item's* concern), and the hyphenation flips (F1 vs
  F-2) between the SC list and row F. A reader can't tell at a glance whether "F-2" and "F2"
  are the same thing. Disambiguate: always qualify the discovery series as `D1-F1…D1-F5`
  and keep the docs-scrub series as `DOCS-SCRUB-Fn`, consistently, everywhere.

---

## Engagement Summary

**Overall take:** The catalog is accurate and the work item is right — I re-ran the greps
and the deletions are genuinely dead, the aggregation bug is real, and every epic scope
point is covered. What's missing is loop-closure: three of the dispositions stop one step
short of the "nothing left filed in a plan file" bar the item sets for itself, and one
handoff has no receiver yet. Revise.

**Here's what I need you to weigh in on:**

1. **[L3-1]** The REQ-PGD-06 → Item 7 handoff is recorded only inside this spec, and Item 7
   (`matrix-truth/`) is an empty directory. Give it a durable home (BACKLOG/register) with
   the "only if deleted" condition, or Item 7 will never see it.
2. **[L3-2]** Deleting `get_default_value` strands doc-17:26/143 and matrix:379
   *immediately*, but Item 7 runs later. Decide the split — this item updates the reference
   doc (per R1) and breadcrumbs the matrix row; Item 7 owns only the PASS-row re-frame.
3. **[L3-3]** State Item 8's own test-deletion rule (delete only tests that solely pin a
   now-dead symbol; net count decreases) and make SC-G tell that count story, so "suite
   green" isn't achievable by dropping an orphaned test silently.
4. **[L3-4]** Name which REQ verifies the *fixed* `_walk_aggregation_ast` — today it's
   explicitly out of scope of REQ-AST-08/-09, and REQ-AST-05 is about SingletonTerm, not
   literals. "Reconcile REQ-AST-03/-05" is too loose, and it may be an Item-7 matrix change.
5. **[L3-5]** Add "close BACKLOG:185 (the aggregation-literal entry)" to row D's
   disposition — it's tagged "Absorbed," not done.
6. **[L3-6]** Decide whether row G is "assess-then-decide" (then require the assessment
   verdict be recorded) or "default-file, implement only if trivial" (then say so). As
   written, "if small" is an undefined off-ramp.
7. **[L5-1]** Disambiguate the D1-F1…F5 vs DOCS-SCRUB-F1/F3 numbering — they collide in the
   same document.

---

## Resolutions

*(To be filled in during Stage 5 as the reviewer resolves each finding, keyed by ID.)*

---

**Verdict:** Revise

**Next Steps:** Once resolutions are recorded here, re-run `/_my_spec` (or return to the
spec-agent session) and point it at this review to incorporate. The reviewer does not edit
the spec. The load-bearing evidence checks passed — the revisions are disposition/handoff
tightening, not a re-verification of the deletion targets.
