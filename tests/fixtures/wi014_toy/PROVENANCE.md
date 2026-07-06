# wi014_toy — Provenance

Imported verbatim (Item 8, UPSTREAM-FINDINGS) from the fusion-tea WI-014
construct-validation toy.

- **Source repo:** `~/1cfe/fusion-tea`
- **Source path:** `exploration/construct_validation/`
- **Source files:** `toy_library.sysml`, `toy_plant.sysml`
- **Repo HEAD at import:** `964d3ae477154d4451e3c4e041f330db09e6e98d` (2026-07-05)
- **Last-touched commit for the toy files:** `dae3942a` (2026-07-05 08:36:35 -0700)

## Import adaptation

Files copied byte-for-byte. **No path/import adaptation was needed** — both files
use self-contained package imports (`ScalarValues::*`, `toy_library::*`) that
resolve within the fixture directory. **No modeling shape was altered** (Non-Goal:
import adapts paths/imports only, never the shapes under test — EXPOSE_PURE,
REFERENCE bindings).

## Shapes under test

- **Part-def EXPOSE_PURE (shape A):** `attribute total_cost : Real = cost_calc.cost`
  on `part def 'Toy Plant'` — a derived attribute on a part def reading a calc
  output. This is the fixture that funds the deferred REQ-CA-09 test (Item 1).
- **Usage-level calc chaining:** `cost_calc.in area` bound to `area_calc.area`.
- **Part-level asserted constraint** fed by a calc output.

`part demo_plant : 'Toy Plant'` is the separate instantiation the research names
(`toy_plant__demo_plant__cost_calc`).
