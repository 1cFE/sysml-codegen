# fusion-tea IFE sweep — orchestrator-verified facts for Item 14 (2026-07-13)

<!-- REFERENCE. Canonical harness: ~/1cfe/fusion-tea/exploration/ife_e2e/ (path-blocked for
sessions rooted in sysml-codegen; the orchestrator or a fusion-tea-rooted session applies
the changes there). -->

- **The harness**: `exploration/ife_e2e/sweep_ife.py` — "WI-015 viability sweep: grid over
  (eta, G, f) using the GENERATED modules."
- **The hand-coded rule the epic retires** (`sweep_ife.py:82`): `viable = eta_g > ETA_G_MIN`
  with `ETA_G_MIN = 10` (docstring line 9: "viable: eta * G > 10 (DI-001, fusion_cycle.sysml)").
  Note the STRICT `>` here vs the modeled `>=` in fusion_cycle.sysml (`eta * gain >= threshold`,
  threshold default 10.0) — the acceptance comparison must check whether any grid point sits
  exactly on the boundary (eta*G == 10) where > and >= diverge; if one exists, that is a REAL
  semantic difference to surface, not paper over.
- **Downstream overlay** (`:84`): `attractive = viable and power_positive and lcoe <= 100` —
  the LCOE overlay is NOT the modeled constraint and stays hand-coded (it is policy, exactly
  what the concept says studies own).
- **Classification outputs**: rows carry `viable`/`attractive` booleans; summary prints
  percentages. The grid results live in `exploration/ife_e2e/outputs/` — the acceptance
  comparison replays the same grid through the study layer and compares every row's `viable`
  classification.
- Sibling: `plot_sweep.py` (visualization, out of scope), `run_anchors.py`, `pkg/` (generated
  package), `models/` (the SysML sources fusion-tea generates from).
