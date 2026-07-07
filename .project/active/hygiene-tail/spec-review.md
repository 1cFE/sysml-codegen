# Spec Review: D3 Hygiene Tail (four benign silent sites)

**Spec:** `.project/active/hygiene-tail/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/hygiene-tail/spec-review.md`
**Date:** 2026-07-07

---

## Reality Check

**Sound.** Every code-facing pin verifies at HEAD, the coupling claims are real, and the
Required-Reading correction is correct. The four sites match the authoritative BACKLOG filing
(`[D3-HYGIENE-TAIL]`, `BACKLOG.md:531`), not just the looser discovery-register triage. This is
the right work item, framed correctly. The findings below are refinements, not a redirect — the
verdict is **Revise**.

Pin-by-pin verification (all accurate at HEAD):

- Site 1 — `loader.py`: `python_type=…"Any"` (`:273`), `binding_type` falsy→`UNBOUND`
  (`:268-270`), `parent_part_path` (`:326`), `qualified_name` (`:327`, `:343`),
  `owning_part_def_qn` (`:329`). All confirmed.
- Site 2 — `graph_builder.py`: the `sorted(…, key=len, reverse=True)` + `.replace` loop at
  `:1534-1535`; the same function calls `resolve_input(…AGG_STRATEGIES)` at `:1498`. Confirmed
  post-cutover.
- Site 3 — `registry.py:44-56`: `type_map.get(out.python_type)` then `if wrapper:`. Confirmed —
  `"Any"` returns `None`, silently skipped.
- Site 4 — `orchestration/output_registry_builder.py:353-367`: Phase 4 three-lookup ladder with
  no `else`; siblings Phase 2 (`:258-263`) and Phase 3 (`:282-289`) both `logger.warning`.
  Confirmed.
- Doc correction: `reference/12-usage-extraction.md` does not exist; `12-virtual-binding-rewrite.md`,
  `01-extraction.md`, `10-output-registry.md` do. Confirmed.
- No pin moved under Item 2's parallel commits — Item 2 touches `usage_extractor` /
  `dependency_backtracker`, none of the four site files.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** The site-1↔site-3 coupling is overstated, and it makes the parked
collapse option (b) a likely trap. The spec says "site 1 mints the `"Any"` that site 3 drops"
(line 50) and Open Question (b) proposes fixing site 1 so "site 3's skip shape becomes
unreachable and site 3 keeps only a defensive assert" (lines 118-122). But `"Any"` is minted on
the **live** path independently of the snapshot loader: `extractor.py:492` initializes
`python_type = "Any"` and only overrides it when a type name resolves through
`_map_sysml_to_python_type` (`:500`); the `AttributeInfo` field itself defaults to `"Any"`
(`data_models.py:70`). So a single-output exit point can carry `python_type="Any"` from a
genuinely-unresolved sysml_type with no snapshot involved — site 3's skip shape is reachable
live, not only via site 1. The spec's reproduce-first hedge ("Reproduce-first decides whether
the site-3 shape is still reachable after a site-1 fix") technically saves it, but the framing
should be corrected: site 3 has an independent (arguably primary) live source of `"Any"`, so
"fix site 1 → site 3 becomes a defensive assert" is probably wrong. Site 3 most likely needs its
own diagnostic regardless. Recommend rewording the coupling so it reads "site 1 is *one* source
of the `"Any"`, and site 3 also fires on live-extracted `"Any"`," and reframing option (b) as
"does a site-1 fix remove *any* of site 3's reachable shapes" rather than "all."

**L1-2 · Question to the user:** The discovery register's §D3 hygiene-tail note (lines 108-112)
describes "~20 sites" and names seven patterns, one of which — **`str(expr)` fallbacks feeding
channel names** — is not among the spec's four, not `_check_semantic_match` (dispositioned to
Item 8), and not one of the three parked residues in Non-Goals (`[SANITIZER-MERGE]`,
`[SC11-IMPORT-REWRITE]`, `[DOTTED-LEAF-PART-BLIND]`). The BACKLOG filing (`:531`) already
narrowed the tail to the spec's four, so the spec is faithful *to its contract*. But the
narrowing dropped the `str(expr)`-channel-name pattern with no recorded disposition — in an epic
whose entire discipline is "nothing dropped silently, re-file with a named count," a
register-named site vanishing from the ledger is exactly the anti-pattern. **Where did the
`str(expr)`-fallback-into-channel-name pattern go — folded into an Item-5 family fix, absorbed by
one of the three parked residues, or genuinely dropped?** The spec should account for it in one
line (Non-Goals pointer or a note), not leave the register and the spec disagreeing on the tail's
membership.

### Lens 2 — Problem & Approach

**L2-1 · Direct claim:** The site-2 characterization overstates what the length-sort buys, and it
leads the reproduce pass toward the *less* reproducible shape. The spec says "The length-sort
already guards the 'one ref is a prefix of another ref' case" and frames the residual as the
exotic "ref `x` matching inside `max(...)`" (lines 38-42). But the length-sort only fixes
ordering in the **original** text; the `inputs.` substitution reintroduces the prefix collision.
Concretely, with refs `{cost, cost_total}` and `ref_to_inputs = {cost: inputs.cost, cost_total:
inputs.cost_total}`:

- length-sort processes `cost_total` first → `"… inputs.cost_total …"`,
- then processes `cost` → `.replace("cost", "inputs.cost")` matches the `cost` **inside**
  `inputs.cost_total` → `"… inputs.inputs.cost_total …"`. Corruption, with no diagnostic.

So the prefix case is *not* fully guarded, and the more-reproducible shape on a real fixture is
**one attribute name being a substring of another** (`cost` / `cost_total`, `p` / `power`), not a
single character inside a function token. This matters because it changes both the fix and the
reproduce target: pointing the R4 reproduce pass only at the `x`-in-`max` example risks it
finding nothing and wrongly reclassifying site 2 as non-reproducing, when a nested-name shape may
be sitting in a real aggregation expression. Recommend the spec (a) drop or qualify the
"length-sort already guards the prefix case" claim, and (b) name the nested-attribute-name shape
as the primary reproduce candidate.

### Lens 3 — Pipeline Risk

**L3-1 · Question to the user:** INV-6 is asserted as an *outcome* but the method that actually
protects it is not required. The spec makes "clean corpora generate with zero WARNINGs" a success
criterion (line 70) and a `[HARD]` requirement (line 79), and defers WARN-vs-raise disposition to
design "informed by the R4 reproduce" (lines 115-117). But the R4 reproduce is about the *silent
shape* — it does not scan the clean corpora for a *false fire*. The epic's own established
discipline is a corpus scan before committing a disposition (memory note: Item-4 D5 diagnostic
was made "INV-6-safe by corpus scan"). Whether a diagnostic can be a WARN at all depends on
whether any clean fixture trips it. **Should the spec require, per site, a scan of every clean
corpus fixture proving the candidate diagnostic does not fire — as the gate for choosing its
disposition — rather than only asserting the zero-WARNINGs outcome and catching a violation at
the end?** As written, a design agent could pick WARN, discover at INV-6-test time that a clean
fixture trips it, and have to re-open the disposition. Requiring the scan up front is the
cheaper, honest ordering.

**L3-2 · Rewrite request:** The R4 reproduce-first requirement is stated once for all four sites
(`[HARD]`, lines 81-84) but is not per-site concrete. Two of the four have genuine "does it even
reproduce" doubt — site 2 (does any real fixture have the nested-name / token-boundary shape) and
site 3 (is its skip shape reachable at all after an eventual site-1 fix; see L1-1). The spec
should ask design to name, per site, the concrete reproduce artifact (which fixture or probe, what
shape) and its independently-anchored expectation, so the reproduce-or-reclassify verdict is
auditable per site rather than a blanket promise. This is a per-site deliverable ask, not a
mechanism lock — the mechanism stays deferred.

**L3-3 · Note:** The Item-2 semantic-adjacency flag on site 4 (lines 136-142) is well-judged.
Worth noting for design that the same file already runs a multi-hop confirm pass (Phase 3b,
`output_registry_builder.py:302-334`, `_resolve_reference_chain`) that reverts unresolved
tentatives to FORMULA — so site 4's Phase-4 gap and Item 2's chain resolution live one screen
apart. Re-checking site 4's reproduce fixture against Item 2's landed state (as the spec already
asks) is the right call.

### Lens 4 — Hygiene

None material. The spec is well-structured and the tags are honest (`[HARD]` items are genuinely
forced; `[INFERRED]` items are labeled and traceable to outcome-based criteria).

### Lens 5 — Reader Comprehension

**L5-1 · Note:** The site-2 residual-shape sentence (lines 38-42) packs the mechanism, the
length-sort caveat, and two residual shapes into one dense run. If L2-1 is taken, the rewrite that
leads with the nested-name example and states the corruption in one concrete before/after line
will also fix the readability. No separate action needed.

---

## Engagement Summary

**Overall take:** The spec is accurate and points at the right work — all four pins verify at
HEAD and the coupling and doc-correction claims hold. But two of its technical characterizations
are optimistic in a way that could mislead the reproduce pass (site 2's length-sort, site 1↔3's
coupling), and the INV-6 protection is asserted as an outcome without requiring the corpus-scan
gate the epic already uses. These are Revise-level edits, not a rework.

**Here's what I need you to weigh in on:**

1. **[L2-1]** Site 2: the length-sort does *not* fully guard the prefix case — the `inputs.`
   substitution reintroduces it (`cost` corrupts inside `inputs.cost_total`). Correct the claim
   and name the nested-attribute-name shape as the primary reproduce target, so the R4 pass
   doesn't hunt the wrong (exotic) shape and wrongly reclassify site 2 as non-reproducing.
2. **[L3-1]** INV-6: require a per-site scan of the clean corpora proving the candidate
   diagnostic does not fire, as the *gate* for choosing WARN-vs-raise — not just the end-state
   zero-WARNINGs assertion. This is the epic's own Item-4 D5 discipline.
3. **[L1-1]** Site 1↔3: `"Any"` is minted live (`extractor.py:492`, `data_models.py:70`), not
   only by the snapshot loader. Reframe the coupling and the collapse option (b): site 3 likely
   needs its own diagnostic because its skip shape is reachable without site 1.
4. **[L3-2]** Make R4 reproduce-first per-site concrete: each site names its reproduce artifact
   and independently-anchored expectation, since sites 2 and 3 have real "does it reproduce"
   doubt.
5. **[L1-2]** The discovery register named a `str(expr)`-fallback-into-channel-name pattern that
   isn't in the four, isn't `_check_semantic_match`, and isn't a parked residue. Account for it in
   one line, or the register and the spec disagree on the tail's membership.

---

## Resolutions

*Filled in during Stage 5, keyed by finding ID.*

---

**Verdict:** Revise
**Next Steps:** Once resolutions are recorded here, re-run `/_my_spec` (or return to the
spec-agent session) and point it at this review to incorporate. The reviewer does not edit the
spec.
