# Probe: deep-literal-override affected-shape authorability (D11)

**Date:** 2026-08-15
**Status:** No affected shape found. `deep override affected-shape coverage unproven` — dated
coverage gap recorded below, per the owner disposition in the brief.
**Environment:** SysIDE 0.8.4 through the repository's licensed `uv` environment.
**Repo state:** branch `main`, commit `c537981`.

## Question

Can a legal authored SysML model make the deep-literal-override lane produce a **one-segment,
`PartUsage`-owned** reference — the only input shape that would reach the branch this item
repairs (`src/sysml_codegen/elaboration/elaborate.py:2062-2076`)?

The lane is `_apply_deep_literal_redefinitions` (`elaborate.py:1032-1078`). It fires on an
anonymous feature that carries a feature-value expression and owns a redefinition whose target is
a **chained** feature. It builds its reference from `redefined.chaining_features` via
`_reference_from_elements` (`elaborate.py:1082`), which keeps only chain links that
`resolved_target_fact` can identify — links with a qualified name. Segment count is therefore the
count of *identifiable* chain links, not the authored dot count.

An affected shape needs both:

1. exactly one surviving segment fact, and
2. that leaf's live semantic owner being a `PartUsage`.

## Result

**Zero one-segment sites, over 51 live lane sites.** Every site that fired produced two segments;
one produced three. No candidate, and no tracked fixture, reached the one-segment branch.

### Search surface actually covered

**A. 15 authored candidates** kept beside this file, each loaded through the licensed extractor.
Element IDs below are the exact live SysIDE IDs; full per-link owner IDs and metatypes are in
`probe-output.txt`.

| # | Candidate | Authored redefinition | Load | Lane sites | Segments | Conclusion |
|---|---|---|---|---|---|---|
| c1 | `c1_dot_chain_baseline` | `:>> comp_a.length = 43.0;` | loads, 0 diagnostics | 1 | 2 | candidate falsified |
| c2 | `c2_plain_redef` | `:>> length = 43.0;` nested in a redefining part | loads | **0** | — | candidate falsified (never enters the lane) |
| c3 | `c3_pkg_qualified` | `:>> Pkg::'Component'::length = 43.0;` | loads, 1 warning | **0** | — | candidate falsified (no chain; override does not apply) |
| c4 | `c4_usage_qualified` | `:>> comp_a::length = 43.0;` | loads, 1 warning | **0** | — | candidate falsified (no chain; override does not apply) |
| c5 | `c5_anon_leaf` | `:>> comp_a.length = 43.0;` where `comp_a` already redefines `length` | loads | 1 | 2 | candidate falsified |
| c6 | `c6_anon_root` | chain authored inside `:>> plant { … }` | loads | 1 | 2 | candidate falsified |
| c7 | `c7_three_segment` | `:>> asm.comp_a.length = 43.0;` | loads | 1 | 3 | candidate falsified |
| c8 | `c8_unresolved_leaf` | `:>> comp_a.no_such_member = 43.0;` | **fails** (reference-error) | — | — | candidate falsified (not a legal model) |
| c9 | `c9_arrayed_child` | `:>> comp_a.length = 43.0;`, `comp_a : 'Component'[2]` | loads | 1 | 2 | candidate falsified |
| c10 | `c10_attr_root` | `:>> dims.length = 43.0;`, attribute-def root | loads | 1 | 2 | candidate falsified |
| c11 | `c11_inline_def` | `:>> comp_a.length = 43.0;`, `length` owned by usage `comp_a` | loads | 1 | 2 | candidate falsified (owner is a `PartUsage`, but two segments) |
| c12 | `c12_named_chain_alias` | `attribute alias_length :>> comp_a.length;` then `:>> alias_length = 43.0;` | **fails** (reference-error) | — | — | candidate falsified (not a legal model) |
| c13 | `c13_self_chain` | `:>> self.length = 43.0;` inside a redefining part | **fails** (reference-error) | — | — | candidate falsified |
| c14 | `c14_self_chain_usage_owned` | same, with a usage-owned `length` | **fails** (reference-error) | — | — | candidate falsified |
| c15 | `c15_self_direct_member` | `:>> self.length = 43.0;` on a direct member | **fails** (reference-error) | — | — | candidate falsified |

**B. Tracked-corpus census.** Every fixture root under `tests/fixtures/` whose text contains a
chained redefinition (regex `:>>\s*[\w']+(\s*\.\s*[\w']+)+`) — 13 roots, 44 live lane sites:
`agg_literal_probe`, `alias_agg_d5`, `alias_agg_probe`, `constraint_def_owned_redefining`,
`constraint_occurrence_demand`, `costed_cart_d5`, `d38_caret`, `issue22_model`,
`nested_occurrence_override_probe`, `plant_values`, `solar_battery_d5`, `solar_battery_model`,
`source_identity_mixed_consumers`. All 44 are two-segment.

### What the negative result rests on

Two observations explain every falsification, and both are empirical, not assumed:

- **The lane only fires on a chain, and a chain has at least two links.** The writer is anonymous
  precisely *because* its redefinition target is a chain construct — an unnamed `Feature`. A
  one-name redefinition (`:>> length = 43.0;`, c2) gives the writer the redefined feature's name,
  so the lane's `qualified_name is None` guard skips it and the value is applied elsewhere. The
  `::`-qualified spellings (c3, c4) produce no chain at all: SysIDE accepts them with a
  `subsetting-featuring-types` warning and the literal never lands (both attributes stay at
  `1.0`, `value_site=definition_default`).
- **Every chain link that resolves has a qualified name, so none is dropped.** Segment collapse
  would need a link with `qualified_name is None`. In all 51 live sites, every link carried a
  qualified name. The links are name-resolved by construction, and the two things that lack
  qualified names — anonymous redefinition writers and the chain construct itself — are not
  reachable by name. The only way observed to drop a link is to make it unresolvable (c8), which
  makes the model illegal.

This is an explanation of the bounded search, **not a proof of impossibility.** A SysML shape
outside the 15 candidates and 13 census roots could still produce the fact.

### The `plural=True` call, judged against the scalar policy (D4)

The lane calls `_resolve_semantic_reference(..., plural=True)` (`elaborate.py:1051`), and the
probe exercises that call for real by running `elaborate()` on every loading candidate.

The call is genuinely plural-sensitive: `c9_arrayed_child` (`comp_a : 'Component'[2]`) returns two
`NodeRef` edges and writes `43.0` into both occurrences of
`declaration=719996f2-5beb-502a-b8e3-0c06db3a8268`.

But that plural behavior lives entirely in the **multi-segment** path.
`_resolve_semantic_reference` returns from the one-segment branch (`elaborate.py:2062-2068`)
before `plural` is read at all. So D4's scalar policy for one-segment owner anchoring is
consistent with this lane by construction, and no shape found here can test it.

### Closest near-miss, and why it is not the shape

`c11_inline_def` produces a leaf whose live owner **is** a `PartUsage`:

- leaf `length` — element ID `46ebd45e-5dcd-500a-b41c-bee27be031c2`,
  QN `DeepOverrideInlineDef::Plant::comp_a::length`
- live owner `comp_a` — element ID `6b7b5fb3-3bbd-5be2-b562-6e79cc8d20eb`, metatype `PartUsage`,
  `owner_is_definition=False`

The owner condition holds; the segment condition does not (2 segments), so the reference takes the
multi-segment route and the repaired branch is never entered. `c5_anon_leaf` is the same story
with a `ReferenceUsage` leaf owned by `PartUsage comp_a`
(`3589537c-b4cc-57c1-92bd-1313e54660cb`).

## Conclusion

**authorability unproven** for the D11 affected shape, over the surface recorded above.

No candidate is retained for Phase-2 promotion, because none is an affected shape. `c1` and `c11`
are the useful non-affected controls if a later phase wants to pin that a usage-owned *deep* target
keeps its current multi-segment behavior.

## Coverage gap record

> **`deep override affected-shape coverage unproven` — 2026-08-15.**
> A bounded authorability search found no legal authored SysML model producing a one-segment,
> `PartUsage`-owned deep-literal-redefinition target. Surface searched: 15 authored candidates
> (dot chain, plain redefinition, package-qualified and usage-qualified `::` forms, pre-redefined
> leaf, anonymous root, three-segment, unresolvable leaf, arrayed child, attribute-def root,
> inline-def usage-owned leaf, named chain alias, three `self.`-rooted forms) plus a census of all
> 13 tracked fixture roots containing a chained redefinition — 51 live lane sites in total, every
> one of them two or three segments. The search is bounded; absence here is not proof of
> impossibility. The deep-override lane therefore ships with no affected-shape regression fixture,
> and the close disposition stays with the owner.

Per the brief, this is a recorded gap, not a pipeline halt. `spec.md` and `design.md` are
unedited.

## Incidental observation (not part of this question)

`c10_attr_root` (`:>> dims.length = 43.0;` where `dims` is an `AttributeUsage` typed by an
attribute definition) loads cleanly but elaborates to `OVERRIDE_TARGET_MISSING`, leaving
`value=None`, `value_site=none`. This is pre-existing behavior in the multi-segment path, unrelated
to owner anchoring. Recorded so a later reader does not mistake it for fallout of this item.

## Reproduction

From the repository root, with the SysIDE license loaded:

```bash
set -a; source ../agentic-mbse/.env; set +a
uv run python .project/active/qualified-reference-occurrence-anchoring/spike/\
deep-override-authorability/probe.py            # both sections
```

`probe.py candidates` and `probe.py census` run either section alone. The captured run is
`probe-output.txt` beside this file; the candidate models are the `c*/model.sysml` files.

Note when comparing runs: the anonymous *writer* element IDs are fresh UUID4s per load and differ
between runs. Every chain link, leaf, and owner ID is derivation-stable and reproduces exactly.

Checks at the time of writing: `git diff -- src/ tests/` empty; `ruff check` clean on `probe.py`.
