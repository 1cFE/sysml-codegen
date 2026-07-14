# B1/B2 Probe Evidence — Live Multiplicity Surface (orchestrator, 2026-07-12)

Design Bet B1 asked whether the live SysIDE 0.8.4 multiplicity surface positively
identifies a single fixed literal count and distinguishes it from range, unbounded,
parameterized, and ordered/nonunique shapes. **Confirmed — the surface is sufficient.**
Probe: `probe_b1_multiplicity.py` (this directory), run via the licensed sibling env:

```bash
UV_CACHE_DIR=/tmp/agentic-mbse-uv-cache \
uv run --directory /home/reid/1cfe/agentic-mbse python \
  .project/active/part-instance-index/probe_b1_multiplicity.py
```

## Observed, per shape (usage on `MultProbe::Owner`, all `MultiplicityRange`)

| shape | `cached_lower/upper` | `lower_bound` node | `upper_bound` node | usage markers |
|---|---|---|---|---|
| `fixed3 : Leaf[3]` | 3 / 4 (exclusive) | `None` | `LiteralInteger(3)` | ordered=F nonunique=F |
| `unbounded_many : Leaf[*]` | 0 / **None** | `None` | `LiteralInfinity` | — |
| `range05 : Leaf[0..5]` | 0 / 6 | `LiteralInteger(0)` | `LiteralInteger(5)` | — |
| `range33 : Leaf[3..3]` | 3 / 4 | `LiteralInteger(3)` | `LiteralInteger(3)` | — |
| `ordered3 : Leaf[3] ordered` | 3 / 4 | `None` | `LiteralInteger(3)` | **is_ordered=True** |
| `nonunique3 : Leaf[3] nonunique` | 3 / 4 | `None` | `LiteralInteger(3)` | **is_nonunique=True**, is_unique=False |
| `param_n : Leaf[n]` (attr `n=4`) | 4 / **5 — non-None!** | `None` | `FeatureReferenceExpression` → referent `AttributeUsage(n)` | — |
| `singleton : Leaf` | usage.multiplicity is `None` | | | |

## Consequences for the design

1. **B1 holds.** Positive fixed-literal identification: `upper_bound` node is
   `LiteralInteger` (not `LiteralInfinity`, not `FeatureReferenceExpression`), and when
   `lower_bound` is present it must be an equal `LiteralInteger`. The ordered/nonunique
   markers live on the **usage** (`is_ordered`, `is_nonunique`), not the multiplicity node —
   the gate must read both.
2. **B2 holds, stronger than feared.** A parameterized `[n]` resolves its default into
   `cached_upper_bound` (non-None 5 here). Any gate keyed on cached counts or
   `MultiplicityData` presence silently expands parameterized shapes with the *default*
   value — exactly the no-silent-drop violation. Node-type dispatch on `upper_bound` is
   mandatory, as the design chose.
3. **New edge for design to pin:** `[3..3]` presents as equal literal bounds — decide
   admit-as-fixed-3 or block, and record it (recommend admit with a test, since it is
   semantically identical to `[3]`; but either decision recorded is acceptable).
4. Note: a `nonunique` subsetting of a unique feature emits a load **error** diagnostic
   (`subsetting-uniqueness-conformance`) — models carrying it may fail load before the gate
   ever sees it; the gate still must not rely on that.
