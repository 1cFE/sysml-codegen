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
   `sorted(ref_to_inputs, key=len, reverse=True)` loop. The length-sort does **not** close
   the prefix-collision case — it only orders the passes over the *original* text; the
   `inputs.` substitution reintroduces the collision. Concrete silent shape, refs
   `{cost, cost_total}`: the loop substitutes `cost_total` first →
   `"… inputs.cost_total …"`, then `.replace("cost", "inputs.cost")` matches the `cost`
   **inside** the already-substituted `inputs.cost_total` → `"… inputs.inputs.cost_total …"`,
   a corrupt expression with no diagnostic. The **primary reproduce target is one attribute
   name being a substring of another** in a real aggregation expression (`cost`/`cost_total`,
   `p`/`power`) — not the exotic single-char-inside-a-function-token shape. Confirmed live at
   HEAD: this function calls `resolve_input(AGG_STRATEGIES)` (`:1498`), so it is the
   post-Item-1-cutover path — the `.replace` survived the cutover, it did not move or die.

3. **`type_map` "Any" exit-point skip** — `generation/registry.py:44-56`
   (`_collect_exit_point_primitive_types`). Each single-output (`field_name="root"`) exit
   point maps its `python_type` to a primitive wrapper: `wrapper = type_map.get(...)` then
   `if wrapper: types.add(wrapper)`. An exit point whose `python_type` is outside
   `{float,int,str,bool}` — notably `"Any"` — is silently skipped: no wrapper registered,
   no diagnostic. **Coupled to site 1, but site 1 is only *one* source of the `"Any"`.**
   `"Any"` is also minted on the **live** path, independent of any snapshot: `extractor.py`
   initializes `python_type = "Any"` (`:492`) and overrides it only when a FeatureTyping
   resolves through `_map_sysml_to_python_type` (`:500`); the `AttributeInfo` field itself
   defaults to `"Any"` (`data_models.py:70`). So an exit point can carry `python_type="Any"`
   from a genuinely-unresolved sysml_type with no loader involved — site 3's skip shape is
   reachable live, not only via site 1.

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

- [x] Each of the four sites either **fires a diagnostic on its silent shape** (verified by
  a fires-on-shape test with an independently-anchored expectation) **or is reclassified**
  with a reason (R4: a site that does not reproduce is not fixed). (Audit note: Site 4's
  "reclassify" label is a stretch of R4's non-reproducing definition — it reproduces on 5/15
  fixtures but the safe fix is design-level, out of scope — see `audit.md`; advisory only.)
- [x] Each new diagnostic has a **silent-on-clean** sibling test proving it does not fire on
  clean input (R1 pair).
- [x] **INV-6 preserved**: the clean corpora still generate with zero WARNINGs.
- [x] Baselines byte-identical (no covered model changes output); suite green; ruff/mypy not
  worse than current.

## Known Requirements

- **[HARD]** Every new or changed diagnostic lands with (a) a fires-on-shape test whose
  expectation is independently anchored (never computed by the code under test) and (b) a
  silent-on-clean test (R1 addition, carried from PIPELINE-TRUTH).
- **[HARD]** INV-6: clean fixtures generate with zero WARNINGs. A new diagnostic that fires
  on a clean corpus fixture is a regression, not a fix.
- **[HARD]** Corpus-scan-before-disposition gate (the epic's Item-4 D5 discipline). Before
  choosing a candidate diagnostic's disposition (WARN vs raise), scan **every clean corpus
  fixture** to prove the candidate does not fire on any of them. INV-6 is the *outcome*; this
  scan is the *gate* that earns it. Do not choose WARN, ship, and discover a false fire at
  INV-6-test time — that re-opens the disposition. The scan is a per-site deliverable, run up
  front, not the end-state assertion.
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
- **`str(expr)` fallbacks feeding channel names** (a fifth pattern the discovery register's
  §D3 hygiene-tail note listed, which the BACKLOG `[D3-HYGIENE-TAIL]` filing dropped from the
  four): **OUT.** The `str(expr_node)` fallbacks live in `expression_utils.py` and feed
  rendered/raw expression *text*, not channel keys — codegen channel names derive from
  `attribute_name` via `get_channel_name`, not raw `str(expr)`. The register's own `str(expr)`
  / `str(direction)` repr-stability concern was routed to Item 9 (agentic-mbse companion
  audit, §D3 cross-repo pointer). If design finds an in-repo `str(expr)`→channel-name path,
  re-file it with a named pointer rather than folding it in silently.
- Any change to how a covered model wires or generates. A diagnostic that would move a
  baseline means the shape is not benign and is out of this item's "benign tail" scope —
  file it, don't force it.
- Behavior fixes surfaced *by* a new diagnostic (e.g. actually resolving a Phase-4 transitive
  alias that currently drops). This item makes the gap loud; resolving it is separate work.

## Open Questions / Deferred to design

- **Per-site diagnostic disposition** (WARNING vs raise vs skip-with-log). Default to
  WARNING per house style; the loader load-bearing case (site 1) may warrant a raise on a
  genuinely corrupt snapshot. Decide per site at design, informed by the R4 reproduce.
- **Site 1 ↔ site 3 collapse.** Site 1 is one source of the `"Any"` site 3 skips, but not
  the only one — the live extractor mints `"Any"` too (`extractor.py:492`), so a site-1 fix
  cannot make site 3's skip shape unreachable. **Site 3 most likely needs its own
  diagnostic regardless.** The design question is narrower than "collapse the pair": does a
  site-1 fix (don't default `python_type` silently on the loader) remove *any* of site 3's
  reachable shapes, or just the snapshot-sourced one? Reproduce-first (below) answers it per
  path. Do not park option (b) as "fix site 1 → site 3 becomes a defensive assert" — that is
  the trap.
- **Site 2 mitigation form.** The length-sort already closes the prefix case; the reproduce
  pass decides whether the residual token-boundary shape reproduces on a real fixture and,
  if so, whether the fix is a token-boundary replace (word-level / `\b`), a placeholder pass,
  or a diagnostic-only tripwire. Defer the mechanism to design.
- **Site 1 exact load-bearing field list.** Captured by criterion above; the concrete list is
  the R4 reproduce pass's output.

## R4 Reproduce-First — per-site deliverable

The R4 `[HARD]` requirement above is one rule; design must discharge it **per site** by
naming the concrete reproduce artifact (which fixture or probe, what shape) and its
independently-anchored expectation, so the reproduce-or-reclassify verdict is auditable site
by site. Reclassification is a **legitimate outcome** — a site whose silent shape does not
reproduce on real fixtures is re-filed, not fixed (R4). Starting targets:

- **Site 1 (loader `.get`):** a probe that loads a snapshot with a load-bearing field
  removed (e.g. drop `python_type`, `qualified_name`, or `binding_type`) and asserts the
  fallback fires the new diagnostic instead of silently mis-typing/mis-keying. Reproduces by
  construction (the loader path is exercised by every `--from-snapshot` run). Independent
  anchor: the hand-authored malformed snapshot, not the loader's own default.
- **Site 2 (`.replace`):** an aggregation fixture with **two attribute names where one is a
  substring of the other** (`cost`/`cost_total`), asserting the compiled expression is
  corrupted (or the new diagnostic fires) — the nested-name shape from L2-1, **not** the
  `x`-in-`max` shape. **Real reclassification doubt:** if no supported aggregation model has
  nested attribute names and none can be added within the covered corpus, site 2 reclassifies
  to a defensive tripwire with a synthetic-fixture pin, or is re-filed. Say which at design.
- **Site 3 (`type_map` "Any" skip):** two reproduce paths, since `"Any"` has two sources —
  (a) a snapshot exit point carrying `python_type="Any"`, and (b) a **live** exit point whose
  sysml_type does not resolve (`extractor.py:492`). Assert the new diagnostic fires on an
  exit point with an unmapped `python_type`. **Real reclassification doubt:** confirm a
  single-output (`field_name="root"`) exit point can actually carry a non-`{float,int,str,bool}`
  type on a real model — if every exit point is always `float` in practice, site 3 is a
  latent-only tripwire, and design says so.
- **Site 4 (Phase-4 no-`else`):** a fixture with a transitive design-attribute default
  (dotted path, `is_transitive_default`) that fails all three lookups, asserting the new
  warning fires — mirroring the sibling Phase-2/3 warn tests as the independent anchor.
  Reproduces cleanly; the sibling phases already have the shape.

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
