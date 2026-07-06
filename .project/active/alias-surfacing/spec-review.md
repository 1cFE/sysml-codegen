# Spec Review: Derived-Attribute Alias Surfacing (SC-7)

**Spec:** `.project/active/alias-surfacing/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/alias-surfacing/spec-review.md`
**Date:** 2026-07-06

---

## Reality Check

**Sound, with one load-bearing correction.** The spec is about the right work item: take
the name→channel mapping Item 10 already computes and surface the modeler's name into the
graph and YAML, then retire Item 1's interim warning for the now-resolvable case. The
Problem section is accurate, the scope boundaries (EXPOSE_PURE only; no new resolution;
snapshots carry no graph) are correct, and the baseline enumeration checks out exactly (7
graph baselines, verified against `tests/fixtures/baseline_outputs/` at HEAD — the Item-10
`spec_chain_*` / `sibling` / `self_named` fixtures carry **no** committed
`computation_graph.json`, so nothing is missing).

The one thing that isn't sound as written: the spec targets the **wrong warning site** for
shape A, and that error propagates into the warning-retirement success criterion and the
"machinery exists, just render it" framing (L1-1, L1-3). This is fixable with spec edits
plus one scope acknowledgment — the work item itself is right — so this is a **Revise**, not
a Rework.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim (highest stakes):** The spec names `graph_builder.py:809` as the
shape-A "name is dropped" warning to retire. That branch is **not the one that fires for
shape A.** For a part-def EXPOSE (wi014's `total_cost = cost_calc.cost`), `_resolve_expose_pure`
cannot separate the instance ref from the output ref — on a part def the calc-usage instance
names are absent from `calc_usage_names` — so it hits the **malformed-refs** warning at
`graph_builder.py:796` ("could not identify instance/output from refs") and returns *before*
reaching the name-drop branch at `:809`. This is documented, not speculative:
`tests/conformance/test_wi014_toy.py:28-32` pins exactly that behavior as the current
baseline, and the caller at `graph_builder.py:865` routes **all** EXPOSE_PURE CAs (no
part-def guard) through `_resolve_expose_pure`. Item 10 did not touch that function.

Consequence: retiring `:809` is a **no-op for shape A**. After this item surfaces
`total_cost` via `_scoped_alias` (a different code path), `_build_attribute_resolution_map`
still calls the old `_resolve_expose_pure` for the same CA and still logs the malformed-refs
warning — so SC-7's stated outcome ("a resolvable EXPOSE no longer warns and instead emits
its name") is **violated for shape A** unless the spec also addresses `:796`. The spec must
re-anchor at HEAD and name the warning that actually fires for each shape.

**L1-2 · Direct claim:** The spec repeatedly says each surfaced entry carries "the modeler's
name" / "the name the modeler chose" (Problem para 1; SC line 43; Known Requirements). What
the registries actually carry is `_sanitize_name(attr_name)` — `ChannelAlias.alias_name =
python_name` (`computed_attribute_extractor.py:318`) and the `_scoped_alias` key's second
element is `ca.python_name` (`pipeline_builder.py:505`), and `python_name =
_sanitize_name(attr_name)` (`computed_attribute_extractor.py:274`). For `total_cost` the two
are identical, so the demo is unaffected. But for a quoted name (`attribute 'total cost'`)
the surfaced token is the sanitized `total_cost`, not the literal SysML name. Per Item 5's
naming contract ("identifiers are derived once at extraction, looked up downstream",
REQ-NC-06) emitting the sanitized form is the **right** call — but the spec should say so
explicitly, and reconcile it with modeling-assumptions §3's promise that "consumers bind to
`subsystem.exposed_name`": the consumer binds to the *sanitized* exposed name. This is a
precision fix, not a redirection.

**L1-3 · If-then tradeoff:** The "the machinery exists; this item renders it" framing (Problem
para 3; Non-Goal "New resolution machinery") is honest for **shape B** and for shape-A
*consumer* resolution (Item 10's `_scoped_alias` + `scoped_alias_lookup`). It is **not**
honest for the shape-A graph-builder path that emits the residual warning (L1-1). Item 10
made shape A resolve for *cross-part consumers*; it did **not** reroute
`_build_attribute_resolution_map`'s own EXPOSE_PURE handling, which still fails and warns.
Making shape A go silent therefore needs *either* a reroute of that map through
`_scoped_alias` *or* a suppression of `:796` for the resolvable case — and a reroute is
arguably the "new resolution machinery" the spec lists as a Non-Goal. **If** the intent is
that shape-A surfacing reads `_scoped_alias` and the malformed-refs warning is separately
silenced/retired, say that and carve it out of the Non-Goal. **If** the intent is a genuine
reroute, then the Non-Goal is overclaimed and should be softened. Either way the spec can't
leave this implicit.

### Lens 2 — Problem & Approach

**L2-1 · Direct claim:** The "Code touch-points" list and Known Requirements point surfacing
at "the flat `_alias` / `expose_pure` `ChannelAlias` entries" for shape B. The flat `_alias`
registry **cannot** be filtered by source: it is populated from CHAIN aliases
(`output_registry_builder.py:241`), design overrides, *and* expose_pure
(`output_registry_builder.py:264`) as bare `key → channel` pairs — the `source`
discriminator is gone by the time it lands there. To honor the [HARD] "EXPOSE_PURE only"
invariant, surfacing must read the **`ChannelAlias` objects** (which retain
`.source == "expose_pure"`) plus **`_scoped_alias`** (which is populated *exclusively* for
part-def EXPOSE_PURE — verified at `pipeline_builder.py:484-506`, guarded on
`classification == EXPOSE_PURE and is_on_part_definition`). Neither source is `_alias`. The
spec's own "ChannelAlias source discrimination" note is the right instinct; the `_alias`
mention contradicts it and should be dropped so design doesn't try to filter a
source-erased dict.

### Lens 3 — Pipeline Risk

**L3-1 · Question to the user:** The spec defers the *shape* of an `output_aliases` entry to
design (correct), but it does not pin the **invariants** that keep the field trustworthy and
the baselines stable. Two are missing:

- **Reference validity.** Should `output_aliases` be validated so every entry's canonical
  channel actually exists as a declared output channel in the graph — the same guard
  `_validate_channel_references` (`graph_builder.py:627`) already applies to
  `module_output` producer channels? The registry mapping came from a real channel, but
  baselines are regenerated and modules can drop; a cheap existence check matches the R1
  "typed registries + validation" discipline. Pin it or consciously skip it.
- **Deterministic ordering.** `_scoped_alias` and the `ChannelAlias` list are
  dict/list-ordered; `find_instance_paths_for_partdef` returns instances in some order.
  Item 1 exists *because* a nondeterministic ordering diff reddened the solar_battery YAML
  baseline. A graph field that serializes in registry-iteration order will do the same. The
  spec should pin deterministic ordering (sorted by alias key, or similar) as an invariant,
  not leave it to design to rediscover.

(The empty-field serialization question *is* handled well — it's in Open Questions with the
baseline-churn consequence and the `fallback_entry_points` `exclude=True` contrast stated.)

**L3-2 · Question to the user:** SC line 46 requires "two instances that expose the same name
produce distinct output-capture keys — no duplicate YAML keys," and the spec names
ife_plant's shape-7 siblings as the motivating collision. But **no committed baseline
exercises that case.** The two end-to-end YAML demos are wi014 (a single `demo_plant`
instance) and attr_expr_probe (one part usage exposing three *distinct* names —
`scale_result` / `half_vol` / `quarter_vol`). ife_plant has no committed YAML baseline
(`baseline_yaml/` holds only attr_expr_probe, chain_spike, sample_model, solar_battery). So
the collision guarantee would rest on a unit test at best, not a reviewed baseline diff.
Where is "same name, two instances" demonstrated? Either name the fixture/unit test that
covers it, or accept that the collision guard is graph-level-only and say so.

**L3-3 · Direct claim:** `test_wi014_toy.py:34-40` explicitly hands a deferred assertion — the
"reworded name-drop-warning test" — forward to "Items 10/11," and states that once the
shape-A path lands, "the deferred assertion can be upgraded there." Item 10 discharged the
*resolution* half (the `_scoped_alias` tests); the *warning* half is Item 11's to close. The
spec doesn't mention this handoff. Given L1-1 (the warning that fires is malformed-refs, not
name-drop), closing this deferral correctly is entangled with getting the warning inventory
right. The spec should name this test as an artifact it must update.

### Lens 4 — Hygiene

None material. The spec is well-structured and the Baseline Regeneration section is exactly
the kind of up-front churn accounting R1 asks for.

### Lens 5 — Reader Comprehension

None material. The Problem section builds the mental model cleanly (name chosen → value flows
on canonical channel → name appears nowhere → this item renders it), and the shape-A/shape-B
distinction is carried consistently. The one comprehension risk is downstream of L1-1: a
reader trusts "retire the `:809` warning" as precise when it isn't — but that's a
correctness finding, already raised.

---

## Engagement Summary

**Overall take:** The work item is right and the spec is unusually well-grounded on baselines
and scope — but it misidentifies the shape-A warning site, and that single error cascades
into the warning-retirement success criterion and the "just render it" framing. Fix the
warning inventory (which warning fires for which shape, at HEAD) and decide whether silencing
shape A is in-scope rendering or out-of-scope machinery, and this is ready.

**Here's what I need you to weigh in on:**

1. **[L1-1, L1-3, L3-3]** Shape A's residual warning is the **malformed-refs** branch at
   `graph_builder.py:796`, not the name-drop at `:809` — confirmed by `test_wi014_toy.py:28-32`
   and the unguarded caller at `graph_builder.py:865`. Retiring `:809` won't silence shape A.
   Decide: does this item also fix/retire `:796` for the resolvable shape-A case (and is that
   "new machinery" per your Non-Goal, or in-scope), and does it close the deferred
   name-drop-warning assertion that `test_wi014_toy.py` hands to "Items 10/11"?
2. **[L3-1]** Pin the two ComputationGraph invariants the spec currently omits: (a) an
   existence validation for alias channels (precedent `_validate_channel_references`), and
   (b) deterministic ordering of `output_aliases` — the exact class of bug Item 1 was created
   to kill. Or consciously decide to skip each.
3. **[L2-1]** Shape-B surfacing must read the `ChannelAlias` objects (they keep
   `.source="expose_pure"`) plus `_scoped_alias` for shape A — **not** the flat `_alias`
   registry, which erases source. Drop the `_alias` mention from the touch-points.
4. **[L3-2]** The same-name-two-instances collision (the SC's third bullet, motivated by
   ife_plant siblings) isn't demonstrated in any committed baseline. Decide whether a unit
   test suffices or a fixture/baseline should cover it.
5. **[L1-2]** What surfaces is the sanitized `python_name`, not the literal modeler name.
   That's correct per Item 5's contract — but say so, and reconcile with modeling-assumptions
   §3's `subsystem.exposed_name` promise (the consumer binds the sanitized form).

---

## Resolutions

*(Incorporated into spec.md 2026-07-06; rulings from the orchestrator.)*

- **L1-1 / L1-3 / L3-3 — IN SCOPE, reframed.** Shape A's resolution map
  (`_build_attribute_resolution_map`, `graph_builder.py:865`) reroutes through Item
  10's `_scoped_alias` registrations instead of the naive `_resolve_expose_pure`
  refs-parsing — CONNECTING landed machinery to its consumer, not new resolution
  logic; the Non-Goal now reads "genuinely new resolution logic" and carves this out.
  The `:796` malformed-refs warning (not just `:809`) retires for resolvable shape A.
  Warning case-matrix added to Success Criteria: resolvable+surfaced = silent;
  unresolvable refs = `:796` stays; EXPOSE_COMPUTED = rejected per §3. `test_wi014_toy`
  deferral (`:28-40`) named as an artifact that flips to asserting resolution +
  surfaced alias.
- **L3-1 — both invariants pinned HARD.** Channel-existence validation (precedent
  `_validate_channel_references`, `:627`) and deterministic stable-sorted ordering of
  `output_aliases` (Item 1's ordering-diff failure class) added as a HARD requirement
  and two Success Criteria.
- **L2-1 — sources corrected.** Surfacing reads the `expose_pure` `ChannelAlias`
  objects + `_scoped_alias`; the flat `_alias` mention is dropped (source-erased) from
  the HARD requirement and touch-points.
- **L3-2 — collision coverage required.** `sibling_channel_ambiguity` (two `Chamber`
  siblings each exposing `power`) named as the shape; spec requires the case covered
  (unit test on the two distinct keys, or a new baseline), design picks the artifact.
- **L1-2 — sanitized name stated.** Spec now says the surfaced token is the derived
  `python_name` (Item 5 / REQ-NC-06) and reconciles with modeling-assumptions §3
  (`subsystem.exposed_name` in its sanitized form).

---

**Verdict:** Revise
**Next Steps:** Record resolutions above, then re-run `/_my_spec` (or return to the
spec-agent session) and point it at this review to incorporate. The reviewer does not edit
the spec. The highest-leverage edit is the shape-A warning inventory (L1-1): re-anchor
`_resolve_expose_pure`'s two warning branches at HEAD and rewrite the retirement SC and case
matrix around the warning that actually fires.
