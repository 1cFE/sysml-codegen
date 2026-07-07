# Companion Audit (PIPELINE-TRUTH Item 9, Phase 4)

The two agentic-mbse primitives that sysml-codegen's extraction bottoms out in. Each gets a
written verdict — covered / gap-found-and-fixed / gap-found-and-filed — not a silent pass
(spec SC-6 / NEED). A gap in either is a silent-drop root: a shape codegen relies on that the
primitive quietly loses.

**Environment:** agentic-mbse `/home/reid/1cfe/agentic-mbse` @ `pipeline-truth-item4`, syside
**0.8.4**, license via `.env`. Probe model: `/tmp/c7probe/audit_model.sysml` (a plant-shaped
model with a multi-segment chain, a one-hop cross-part ref, and a self-named `in x = x`
binding). Probe script: `/tmp/c7probe/audit_probe.py`.

Probe command:

```bash
cd /home/reid/1cfe/agentic-mbse && uv run --env-file .env python /tmp/c7probe/audit_probe.py
```

---

## A1 — `extract_feature_refs` traversal coverage

`agentic_mbse.sysml.expression.extract_feature_refs` (`sysml/expression.py:119`) is the
primitive sysml-codegen's binding extraction bottoms out in. It walks an expression tree and
returns an `ExpressionRef` for every `FeatureReferenceExpression` / `FeatureChainExpression`
node. The audit question: does it traverse every reference shape codegen relies on, or does it
silently drop one?

**Probe output:**

```
=== A1: extract_feature_refs traversal coverage ===
  multi-segment chain (sensor.metric.derived)  expr=CollectExpression          n_refs=2 names=['metric', 'sensor'] qns=['AuditProbe::Sensor::metric', 'AuditProbe::Array::sensor']
  cross-part ref (arr.rollup)                  expr=FeatureChainExpression     n_refs=2 names=['rollup', 'arr'] qns=['AuditProbe::Array::rollup', 'AuditProbe::Array::rollup::arr']
  self-named binding (in gain = gain)          expr=FeatureReferenceExpression n_refs=1 names=['gain']
```

**Verdict: COVERED.** All three reference shapes traverse to a **non-empty** ref set — none is
silently dropped:
- Multi-segment chain → the walk reaches the chain's segment features (returns the container
  features, `n_refs=2`), not an empty set.
- One-hop cross-part ref → traversed (`rollup` + its container `arr`).
- Self-named `in gain = gain` binding → the RHS `FeatureReferenceExpression` yields the ref
  `gain`, not dropped.

**Nuance (not a gap).** For a multi-hop chain, `extract_feature_refs` returns the walked
segment features — it does not *truncate* to a single leaf. The `source_path` truncation
documented as D3 (`hierarchy_resolver` keeps only the first segment) lives on the **codegen**
side (`extract_feature_chain_name`), not in this primitive. `extract_feature_refs` itself is
traversal-complete, so it is not the silent-drop root; the D3 guidance ("keep chains one hop")
already covers the codegen-side choice. No fix, nothing to file.

---

## A2 — `str(direction)` repr stability

sysml-codegen keys parameter direction (in/out) off the **stringified** `member.direction`:
`extractor.py:381` `_get_direction` and `usage_extractor.py:891` `_is_input_parameter` both do
`direction_str = str(member.direction)` and then substring-match: `"In" in direction_str`,
`"Out" in direction_str or "Return" in direction_str`. The audit question: is that repr stable,
or is there `<Direction.IN: …>`-vs-`in` drift that would break the substring keys?

**Probe output:**

```
=== A2: str(direction) repr stability ===
  syside version: 0.8.4
  Metric.base                  repr=FeatureDirectionKind.In    str='FeatureDirectionKind.In'
  Metric.None                  repr=FeatureDirectionKind.Out   str='FeatureDirectionKind.Out'
  SelfCalc.gain                repr=FeatureDirectionKind.In    str='FeatureDirectionKind.In'
  SelfCalc.scaled              repr=FeatureDirectionKind.Out   str='FeatureDirectionKind.Out'
```

**Verdict: STABLE.** `str(direction)` is a clean enum string — `FeatureDirectionKind.In` /
`FeatureDirectionKind.Out` — not an angle-bracket value repr. Codegen's substring keys resolve
it correctly: `"In" in "FeatureDirectionKind.In"` → input; `"Out" in "FeatureDirectionKind.Out"`
→ output. The class-name prefix `FeatureDirectionKind` contains none of `In`/`Out`/`Return`, so
it does not spuriously match.

**Why the substring approach is the thing that de-risks this.** The keys are *resilient to the
exact drift A2 worried about*: even if a future syside changed the repr to `<FeatureDirectionKind.In: N>`,
`"In" in …` still holds. The keying would only break if syside dropped the `In`/`Out`/`Return`
tokens from the direction string entirely — a change that would also break the validators'
identical `"Out" not in direction` checks, so a regression would surface loudly in both repos'
suites, not silently. No drift found on 0.8.4; no fix, nothing to file.

---

## Summary

| Primitive | Shapes probed | Verdict | Fix / file |
|---|---|---|---|
| A1 `extract_feature_refs` | multi-segment chain, cross-part ref, self-named binding | **COVERED** | none |
| A2 `str(direction)` | in / out across calc-def + calc-usage members (syside 0.8.4) | **STABLE** | none |

Both primitives cover the shapes codegen relies on. No gap fixed, no gap filed — each is
covered with evidence, none assumed.
