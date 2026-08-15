# Learning Test: Specialization + usage-level retypes through the elaborator (Item 5 Phase 2, leg 3)

**Date**: 2026-08-07 · **Branch**: `source-identity-epic` (after `e92934d`) · **Author**: leg-3 session
**Upstream**: `.project/active/elaborator-breadth/plan.md` (Phase 2, third leg)

## Summary of Findings

**The two-level retype itself is free; the missing piece was redefinition-borne
EXPOSE, plus a latent hole in the remap rule.** Three findings, all landed:

1. **Usage-level retypes hold by construction.** `part hif_plant : 'IFE Power
   Plant' { part :>> driver : 'HIF Driver'; }` — the occurrence index already
   types the driver occurrence most-specifically (Item-10 C3 machinery), so the
   specialized def's attributes, its inherited base attributes, and the base-def
   template calc all materialize at `hif_plant__driver` with no elaborator change.
   The legacy WI-015 failure (def-keyed type map missing usage-level retypes) has
   no analog here.
2. **Chain-valued `:>>` redefinitions are EXPOSE aliases** (new:
   `_collect_redefinition_aliases`). `:>> cost_per_joule = meier_cost.gamma` on
   the specialized def re-sources the inherited attribute; without an alias the
   consumer degraded to a dead node (the WI-015 unwired pin, reproduced first).
   The sweep walks redefining members with pure-chain values on user part defs
   AND part usages, enqueues alias facts in tier order (def-borne, then
   usage-borne; occurrence-literal overrides outrank both at resolution; a
   resolved alias supersedes a definition-default value). `RedefinitionData`
   couldn't feed this: it carries `source_path` as a flat string and
   `expression_ast=None` for CHAIN — the elaborator reads the members off the
   AST, which is D2's stance anyway.
3. **The remap rule missed whole-path definition keys.** `_expand_def_context`
   checked only *proper* prefixes, so a `:>>` owned directly by a def
   (`TwoLevelLib__HIF_Driver`) never anchored — latent for literal def-level
   `:>>` (tier 2) as well, unexercised by any earlier fixture. Fixed: the cut
   scan now includes the full path.

Verified against the real customer shape: fusion_tea (lenient — it carries 15
SRC-01 self-bindings) wires `lcoe_calc.driver_cost_constant` to
`ProducerRef(hif_plant__driver__meier_cost, gamma)` end to end.

Also: `spec_chain_twolevel` is the FOURTH corpus fixture authoring the degenerate
`in R = R` idiom (`meier_cost.drive_power`), after fusion_tea, catf_mfe, and
sibling_channel_ambiguity. The Phase-3 ledger's "fixture authors SRC-01" class
keeps growing — the lenient mode added in leg 1 is carrying every leg since.

## Question / Goal

Whether two-level specialization (usage-level retype of an inherited part usage)
and specialized-def value redefinitions survive elaboration with correct identity:
does the inherited consumer (`lcoe_calc` on the base def) reach the specialized
producer channel (`meier_cost.gamma`)?

## Log

- Probe (`probe_leg3.py`, licensed): retype + placement already correct
  (driver attrs + meier_cost at `hif_plant__driver`); `cost_per_joule` dead
  (no value, no alias); `RedefinitionData` for the CHAIN `:>>` has
  `expression_ast=None`. Strict raises the fixture's own SI_SELF_BINDING.
- Implemented the redefinition-alias sweep; first run produced
  `OVERRIDE_TARGET_MISSING` at the def-relative path — exposed the
  proper-prefix-only hole in `_expand_def_context`; fixed; edge wires.
- Probe (`probe_leg3b.py`): fusion_tea lenient — 7 calcs, 52 attrs, the
  driver edge exact; 15 SI_SELF_BINDING + 3 OVERRIDE_TARGET_MISSING +
  3 SI_OCCURRENCE_MISSING diagnostics (Phase-3 ledger material, not leg scope).

## Tests Written

`tests/conformance/test_elaboration_specialization_retypes.py` — 7 kept licensed
tests: strict rejection pin; retyped occurrence carries the specialized def;
chain redefinition → alias at the occurrence; the WI-015 lcoe→gamma edge; plain
cross-part attribute stays a NodeRef; SC-2 fan-out collapse; fusion_tea's real
driver edge end to end.

## Reproduction

```bash
set -a && source /home/reid/1cfe/agentic-mbse/.env && set +a
uv run pytest tests/conformance/test_elaboration_specialization_retypes.py -q
```

## Open Questions / Follow-ups

- Multi-level def-tier LITERAL shadowing (a literal `:>>` on both a def and its
  subtype hitting one node) still has no ordering guarantee — no corpus fixture
  authors it; now that whole-path def keys anchor, both would apply in
  `hier.redefinitions` iteration order. Surfaces in Phase 3 if any fixture
  trips it; otherwise author the missing fixture in the shadowing leg.
- fusion_tea's 3 OVERRIDE_TARGET_MISSING + 3 SI_OCCURRENCE_MISSING lenient
  diagnostics are unclassified — Phase-3 grind rows.
