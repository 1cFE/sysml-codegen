# agentic-mbse Impact Note — Item 2 (Resolved Multi-Hop Chain Bindings)

**R2 disposition:** No agentic-mbse code change required. Record only.

**Why (in one line):** the change is entirely in sysml-codegen's resolution layer; it
consumes the SysML shape agentic-mbse already produces, and adds no new authoring rule.

## What changed (sysml-codegen side)

A calc-usage parameter bound to a **3+-segment feature chain**
(`station.array.derived_calc.derived_value`) now resolves to its upstream channel
instead of hard-rejecting to an unbound entry point. Two mechanisms:

- Extraction emits a full-path `CHAIN` binding for the deep chain (was a loud reject).
- The backtracker resolves it via `scoped_lookup` plus an **ancestor-scope climb** — no
  new SysML construct, no new authoring convention.

## Why agentic-mbse needs nothing

- **No new modeling construct.** The 3+-segment feature chain is already valid SysML that
  agentic-mbse parses and hands over via `extract_feature_chain_segments`
  (`extraction/expression_utils.py:279`). Item 5 of the prior epic already used that helper;
  this item just stops discarding its output. The parser/adapter surface is unchanged.
- **No new authoring rule to document in the MODELING_GUIDE.** Before this change a deep
  chain was silently degraded to a hand-filled entry point; now it wires. That is a
  capability the modeler gains for free — it does not constrain how they write the model.
  There is no "do X / avoid Y" guidance to add.

## The one thing worth recording for a future guide edit

If a MODELING_GUIDE section ever enumerates *what binding shapes resolve*, it can now list
the 3+-segment cross-scope calc-usage chain as **resolved** (previously "rejected, surfaces
as an entry point"). Precise limit to state if so: resolution is by scope-climbing a single
registry lookup, and it **refuses** (loud diagnostic + entry point, never a silent pick)
when two ancestor scopes carry the same full path to different channels. The subtler
first-segment-shadowing shape (an inner scope declares only the chain's first segment while
an outer scope supplies the rest) is a documented, filed non-goal — no corpus model
exercises it.

## Pointers

- Design: `.project/active/multihop-chain/design.md` (D1–D5, Key Bets B1–B3)
- Reference doc updated in-repo: `docs/architecture/reference/24-dual-resolution-architecture.md`
  (CHAIN dispatch — Step CLIMB + the Step-4 multi-hop WARN)
- agentic-mbse repo (sandbox-blocked this session): `/home/reid/1cfe/agentic-mbse`
