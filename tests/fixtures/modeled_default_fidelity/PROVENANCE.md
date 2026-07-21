# Provenance

Authored fixture for CONSTRAINT-LIFECYCLE-REMEDIATION Item 4 (spec DD-R20, DD-R21,
DD-R25; design Phase 3). Acceptance surface for DD-A11 and DD-A12.

## What it pins

Three modeled-default IR shapes on constraint definition formals:

| Formal | Modeled default | IR shape | Expected |
|---|---|---|---|
| `Drift Bound::drift` | `default -0.1` | `OperatorNode` (unary `-`) over a literal | value `-0.1` |
| `Power Floor::rated_power` | `default 40.0 [W]` | `UnitAnnotationNode` over a literal | value `40.0`, `unit_text` `"W"` |
| `Derived Bound::limit` | `default 2.0 + 3.0` | binary `OperatorNode` | explicitly unresolved, `unresolved_default_kind = "operator"` |

Before Item 4 the default lane understood only a bare `LiteralNode`, so the first two
resolved to `None` and the generated JSON omitted their keys entirely — a value the
model states became one the user had to re-supply, with no diagnostic anywhere. The
third pins the other half of the contract: an unsupported default IR must stay
explicitly unresolved and diagnosed by QN and node kind, never invented and never
silently omitted (DD-R21).

The unit is **carried, never converted** (DD-R25). `[W]` is used rather than `[MW]`
because the value is what this fixture is about; unit conversion is an explicit
non-goal.

## Authoring note — formal order is load-bearing

A constraint actual written `in <formal> = <value>` binds **positionally**. Each
definition here therefore lists its bound formal first and its defaulted formal
second. Writing the defaulted formal first makes the actual bind to it, and the
intended formal then fails with "has no actual and no explicit modeled default".

## Routes

Live extraction only, for now. DD-A11's snapshot route needs a captured snapshot and
therefore the SysIDE licence; it is declared as a Phase 5 dependency in the design
(there are zero `unit` IR nodes across all 34 currently committed snapshots, which is
why this fixture had to be authored rather than found).
