# Spec: D3 Hygiene Tail (four benign silent sites)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-07
**Complexity:** MEDIUM
**Branch:** truth-debt-epic
**Epic:** TRUTH-DEBT — Item 6

---

## Problem

PIPELINE-TRUTH's silent-failure hunt (discovery §D3) found four benign-leaning sites where
the code takes a fallback instead of surfacing a gap. Each is low blast-radius on the covered
corpus, so Item 5 hardened the high-value families and filed these four as one consolidated
tail (`[D3-HYGIENE-TAIL]`). They are still silent today: on a shape they can't handle, they
fall back quietly instead of firing a diagnostic. That contradicts the project's own
noise-discipline contract — nothing dropped silently; a diagnostic fires on the shape it
claims, and stays silent on clean input (R1, and the V11 precedent in RN-7).

The four sites, re-verified at HEAD during this spec pass:

1. **Loader `.get` defaults on load-bearing fields** — `snapshot/loader.py`.
   The snapshot loader reads fields with `d.get(field, default)`. Most defaults are benign
   (empty list, `False`, `""` on metadata). A load-bearing subset masks a corrupt or
   missing field instead of surfacing it: `python_type=d.get("python_type", "Any")`
   (`loader.py:273` — feeds site 3), `qualified_name=d.get("qualified_name", "")`
   (`:327/:343` — a keying field), the `binding_type` falsy-guard that silently becomes
   `UNBOUND` (`:269`, dropping a binding), and the scoping fields `parent_part_path` /
   `owning_part_def_qn` (`:326/:329`). A malformed snapshot loads clean and mis-wires
   offline.

2. **Naive substring `.replace()` in aggregation compile** — `graph_builder.py:1532-1536`.
   The aggregation expression is compiled by substituting each symbolic ref with its
   `inputs.X` form: `compiled = compiled.replace(ref, ref_to_inputs[ref])`, in a
   `sorted(ref_to_inputs, key=len, reverse=True)` loop. The length-sort already guards the
   "one ref is a prefix of another ref" case. The residual silent shape is a ref that is a
   substring of a *larger token* in the expression text or of an already-substituted
   `inputs.Y` — e.g. a ref `x` matching inside `max(...)`, corrupting the compiled
   expression with no diagnostic. Confirmed live at HEAD: this function calls
   `resolve_input(AGG_STRATEGIES)` (`:1498`), so it is the post-Item-1-cutover path — the
   `.replace` survived the cutover, it did not move or die.

3. **`type_map` "Any" exit-point skip** — `generation/registry.py:44-56`
   (`_collect_exit_point_primitive_types`). Each single-output (`field_name="root"`) exit
   point maps its `python_type` to a primitive wrapper: `wrapper = type_map.get(...)` then
   `if wrapper: types.add(wrapper)`. An exit point whose `python_type` is outside
   `{float,int,str,bool}` — notably `"Any"`, the exact loader default from site 1 — is
   silently skipped: no wrapper registered, no diagnostic. **Coupled to site 1**: site 1
   mints the `"Any"` that site 3 then drops.

4. **Registry alias-rewrite no-not-found branch** — `output_registry_builder.py:353-367`
   (Phase 4, transitive design-attribute aliases). A design attribute whose default is a
   dotted-path reference to another channel (`is_transitive_default`, e.g.
   `cost_model.total_cost`) is an alias intent. Phase 4 tries three lookups
   (`instance_attr_to_channel` → `scoped_lookup` → `alias_lookup`) and, on success,
   `register_alias`. There is **no `else`** — an unresolved transitive default silently
   loses its alias. Sibling Phases 2 (`:258`) and 3 (`:282`) both `logger.warning` on the
   identical not-found shape, so this is a clean family gap: the diagnostic already exists
   two phases over.

## Success Criteria

- [ ] Each of the four sites either **fires a diagnostic on its silent shape** (verified by
  a fires-on-shape test with an independently-anchored expectation) **or is reclassified**
  with a reason (R4: a site that does not reproduce is not fixed).
- [ ] Each new diagnostic has a **silent-on-clean** sibling test proving it does not fire on
  clean input (R1 pair).
- [ ] **INV-6 preserved**: the clean corpora still generate with zero WARNINGs.
- [ ] Baselines byte-identical (no covered model changes output); suite green; ruff/mypy not
  worse than current.

## Known Requirements

- **[HARD]** Every new or changed diagnostic lands with (a) a fires-on-shape test whose
  expectation is independently anchored (never computed by the code under test) and (b) a
  silent-on-clean test (R1 addition, carried from PIPELINE-TRUTH).
- **[HARD]** INV-6: clean fixtures generate with zero WARNINGs. A new diagnostic that fires
  on a clean corpus fixture is a regression, not a fix.
- **[HARD]** R4 verify-then-fix per site, in order: check doc/REQ intent first; reproduce
  the silent shape with a probe or test against real fixtures (never mocks) BEFORE
  hardening; a non-reproducing site is reclassified in the register, not fixed; close the
  loop in the reference docs and matrix rows in the same change.
- **[HARD]** Baseline/snapshot regeneration only through `scripts/capture_*.py` with reviewed
  diffs (R3). This item expects byte-identical baselines — a new diagnostic surfaces a gap,
  it does not change wiring on covered models.
- **[NEED]** Harden at the cleanest choke point within each site's local family, not
  site-by-site where a family choke exists (e.g. the loader's ~40 `.get` calls share one
  choke; Phase 4 shares Phases 2/3's warn pattern). There is **no single cross-site choke** —
  the four sites live in four different modules (`snapshot/`, `resolution/`, `generation/`,
  `orchestration/`), so "family-style" means one choke *per site*, not one for all four.
- **[INFERRED]** Site 1's "load-bearing" subset is defined by outcome: a field whose default
  masks a missing/corrupt value that changes wiring, keying, or type. The benign majority
  (`is_input`, `is_output`, `description`, `unit`, `source_line`, `is_optional`, list
  fields) keeps its default untouched. The exact field list is settled at the R4 reproduce
  pass (see Open Questions).
- **[INFERRED]** House diagnostic style is a WARNING that leaves output importable-but-flagged
  (the Item-5 family style, RN-7 / V11 precedent), not a hard raise — unless the R4 pass
  shows a shape where a raise is the honest disposition (e.g. a corrupt snapshot at site 1).

## Non-Goals

- The already-dispositioned residue stays filed, not touched: `[SANITIZER-MERGE]`,
  `[SC11-IMPORT-REWRITE]`, `[DOTTED-LEAF-PART-BLIND]`.
- Dead `_check_semantic_match` — cross-referenced to Item 8's dead-code sweep, not this item.
- Any change to how a covered model wires or generates. A diagnostic that would move a
  baseline means the shape is not benign and is out of this item's "benign tail" scope —
  file it, don't force it.
- Behavior fixes surfaced *by* a new diagnostic (e.g. actually resolving a Phase-4 transitive
  alias that currently drops). This item makes the gap loud; resolving it is separate work.

## Open Questions / Deferred to design

- **Per-site diagnostic disposition** (WARNING vs raise vs skip-with-log). Default to
  WARNING per house style; the loader load-bearing case (site 1) may warrant a raise on a
  genuinely corrupt snapshot. Decide per site at design, informed by the R4 reproduce.
- **Site 1 ↔ site 3 collapse.** These are one coupled pair: site 1 mints the `"Any"` that
  site 3 skips. Two shapes for design to choose between: (a) harden both independently, or
  (b) fix at site 1 (don't default `python_type` silently) so site 3's skip shape becomes
  unreachable and site 3 keeps only a defensive assert. Reproduce-first decides whether the
  site-3 shape is still reachable after a site-1 fix.
- **Site 2 mitigation form.** The length-sort already closes the prefix case; the reproduce
  pass decides whether the residual token-boundary shape reproduces on a real fixture and,
  if so, whether the fix is a token-boundary replace (word-level / `\b`), a placeholder pass,
  or a diagnostic-only tripwire. Defer the mechanism to design.
- **Site 1 exact load-bearing field list.** Captured by criterion above; the concrete list is
  the R4 reproduce pass's output.

## Coupling Notes (R4 context)

- **Item 1 (F4 cutover, landed):** re-verified site 2 at HEAD. The `.replace` is at
  `graph_builder.py:1534-1535`, inside the post-cutover aggregation module builder (same
  function calls `resolve_input(AGG_STRATEGIES)`). It did not move or die in the cutover.
- **Item 2 (multi-hop chains, in flight, parallel):** touches `usage_extractor`,
  `dependency_backtracker`, `expression_utils` (chain-follow). **No direct file overlap** with
  the four sites (`loader.py`, `graph_builder.py` agg builder, `registry.py`,
  `output_registry_builder.py`). One **semantic** adjacency to flag for design: site 4 is
  transitive-alias resolution and Item 2 is multi-hop chain resolution — if Item 2 makes a
  previously-unresolvable dotted path resolvable, it could change whether site 4's new
  diagnostic fires. Re-check site 4's reproduce fixture against Item 2's landed state at
  design if Item 2 has merged by then.
- **PUSH-DOWN:** this item is scheduled before PUSH-DOWN because it edits extraction/
  resolution surfaces PUSH-DOWN moves (`expression_utils`, `hierarchy_resolver` neighborhood).
  Harden here so the moved code is born correct.

## Required-Reading Correction

The epic's Item 6 Required Reading cites `docs/architecture/reference/12-usage-extraction.md`.
That file does not exist. The actual `reference/12-*` is `12-virtual-binding-rewrite.md` (the
alias-rewrite semantics relevant to site 4). Usage extraction is documented in
`reference/01-extraction.md`. Design should read `10-output-registry.md` (Phase 4 semantics,
site 4), `12-virtual-binding-rewrite.md`, and `01-extraction.md`.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_truth_debt.md` (Item 6; R1–R4)
- **Required Reading:** `.project/backlog/BACKLOG.md` `[D3-HYGIENE-TAIL]`;
  `.project/research/20260706_pipeline-truth-discovery.md` §D3 (finding table + hygiene-tail
  list); `docs/architecture/reference/01-extraction.md`, `reference/10-output-registry.md`,
  `reference/12-virtual-binding-rewrite.md` (see Required-Reading Correction);
  `.project/active/warning-reconciliation/release-notes.md` (RN-7 — the V11
  fires-on-shape/silent-on-clean noise-discipline precedent)
- **Prior-item template:** `.project/active/silent-failure-hardening/{spec,design,plan}.md`
  (Item-5 family-style hardening — the pattern this item follows)
- **Research:** `.project/research/20260706_pipeline-truth-discovery.md`
- **Design:** `.project/active/hygiene-tail/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`.
