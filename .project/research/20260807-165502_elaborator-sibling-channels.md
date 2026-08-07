# Learning Test: Sibling same-name channels through the elaborator (Item 5 Phase 2, leg 2)

**Date**: 2026-08-07 · **Branch**: `source-identity-epic` @ `550aaf1` · **Author**: leg-2 session
**Upstream**: `.project/active/elaborator-breadth/plan.md` (Phase 2, second leg)

## Summary of Findings

**The SC-3 sibling-channel disambiguation holds by construction — no leg
implementation was needed.** Two same-type sibling chambers each expand to their own
producer calc node, each def-declared expose (`power = power_calc.power`) resolves
per occurrence to its OWN producer (leg-1 alias mechanics), and the consumer's
`chamber_b.power` chain anchors at chamber_b's occurrence and follows its alias to
chamber_b's channel exactly. The flat-name collision the legacy pipeline needed
instance-scoped channel machinery for cannot occur: node identity IS the occurrence
path (design D1), so there is no flat namespace to collide in.

Second finding: the fixture itself authors the degenerate `in fuel = fuel` idiom on
the shared `Chamber` producer — a real SRC-01, screened at the *declaration* (one
finding, not one per occurrence). Strict elaboration rejects the fixture; lenient
records the finding once and skips only that binding. Same family as catf_mfe's
(`vacuum.sysml:176`) and fusion_tea's; the Phase-3 grind ledger will carry a
"fixture authors SRC-01" class with at least these three members.

## Question / Goal

Whether same-type sibling occurrences exposing same-named channels (the SC-3
collision that Item 10's legacy channel machinery disambiguates) survive the
elaborator with distinct identities, and what the consumer's cross-part binding
resolves to.

## Log

- Probe (scratchpad `probe_leg2.py`, licensed): strict elaboration raises
  `SI_SELF_BINDING: SiblingLib__Chamber__power_calc.fuel`. Lenient graph: 3 calc
  nodes (two `power_calc` occurrences + `total_calc`), per-sibling `power` attrs
  with distinct `ProducerRef` aliases, and
  `total_calc.chamber_power = ProducerRef(...chamber_b__power_calc, power)`.
  One diagnostic total — the declaration-level self-binding.
- No elaborator change was required; the leg pins existing behavior.

## Tests Written

`tests/conformance/test_elaboration_sibling_channels.py` — 5 kept licensed tests:
strict rejection of the fixture's own self-binding; lenient single
declaration-level finding + skip; sibling producers distinct; per-sibling expose
aliases; consumer reaches exactly chamber_b.

## Reproduction

```bash
set -a && source /home/reid/1cfe/agentic-mbse/.env && set +a
uv run pytest tests/conformance/test_elaboration_sibling_channels.py -q
```

## Open Questions / Follow-ups

- The lenient skip leaves `fuel` unbound on both producer occurrences; at
  projection those become entry-point candidates. Whether the dual-run diff
  classifies that as expected-collapse or needs-review is a Phase-3 ledger row.
