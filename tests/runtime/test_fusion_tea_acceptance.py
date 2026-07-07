"""PIPELINE-TRUTH Item 3, SC-B: fusion-tea's real plant executes to run-C's lcoe.

License-free acceptance proof. The vendored canonical fusion-tea models (committed v2
snapshot, true-zero V11 offenders) generate a package that:

  * executes to the epic's headline lcoe (``270.1211779380445/MWh``) through the
    ``run_pipeline`` runner — anchor C, the full pipeline (``test_run_c_reproduces``);
  * genuinely *consumes* its emitted entry-point JSON — moving one key changes the output
    to an independently hand-computed target (``test_gain_perturbation_is_consumed``).
    This closes the "consumed vs baked-default" hole: every run-C value equals a baked
    schema default, so a JSON-ignoring executor would reproduce anchor C by accident; only
    a moved input proves the JSON is read.

Anchors A/B are module-level checks — each calc's own arithmetic, run in isolation. They
replace WI-015's historical dollar anchors ($252.30 / $68.69), which predate wiring the
Meier gamma edge into ``driver_cost_constant`` (with that edge wired, the calc's cost
constant is an upstream channel, not a fed entry point — so A/B assert the modules' own
semantics instead). Every expected value below is hand-derived from the SysML arithmetic,
never read back from the executor (epic R1 anti-pattern ban).
"""

from __future__ import annotations

import importlib
import sys

import pytest

from sysml_codegen.cli import GenerationConfig, run_codegen
from tests.conftest import snapshot_fixture
from tests.runtime.pipeline_runner import (
    _install_simkit_stub,
    _module_import_path,
    run_pipeline,
)

_LCOE_CHANNEL = "hif_plant_pkg__hif_plant__lcoe_calc__lcoe"
_RUN_C_LCOE = 270.1211779380445

# gain is emitted per-consumer (it is a plant DESIGN_ATTRIBUTE bound into each calc usage,
# NOT a cross-part fan-out that collapses by source QN). So lcoe_calc reads its own key,
# distinct from recirc_calc's. Perturbing only lcoe_calc's key moves lcoe alone.
_GAIN_EP_KEY = "hif_plant_pkg__hif_plant__lcoe_calc__gain"
_GAIN_PERTURBED = 100.0

# Hand-computed from ife_lcoe.sysml:53-125 with gain=100 and the emitted inputs, and the
# driver_cost_constant channel = Meier gamma = 68.247088 (hif_economics.sysml; unaffected
# by gain). Independent of the executor. Full transcription:
#   driver_efficiency=0.35, driver_energy=14286000.0, frequency=3.5, availability=0.9,
#   blanket_energy_multiple=1.15, thermal_efficiency=0.43, discount_rate=0.08,
#   driver_lifetime_shots=6.0e9, om_cost_constant=65.0, plant_cost_constant=2000.0,
#   target_cost_constant=10.0, yield_cost_constant=5.0e6, construction_years=5.0,
#   operational_years=40.0, driver_cost_constant=68.247088, gain=100.0
#   energy_on_target       = 0.35*14286000.0                       = 5_000_100.0
#   fusion_energy_per_shot = 100.0*energy_on_target
#   net_electric_power     = 14286000.0*3.5*(0.43*1.15*100.0*0.35 - 2.0)
#   net_electric_kw        = net_electric_power/1000.0
#   shots_per_year         = 31557600.0*3.5*0.9
#   driver_lifetime_years  = 6.0e9/shots_per_year
#   annual_capital_cost    = (2000.0*net_electric_kw + 5.0e6*fusion_energy_per_shot/1.0e9
#                              + 68.247088*14286000.0)/5.0
#   annual_operating_cost  = 10.0*shots_per_year + 65.0*net_electric_kw
#                              + 68.247088*14286000.0/driver_lifetime_years
#   annual_energy          = 8760.0*net_electric_kw*0.9/1000.0
#   discount_factor_con    = 1.08**5.0 ; pvf_construction = (1 - 1/dfc)/0.08
#   discount_factor_op     = 1.08**40.0; pvf_operation    = (1/dfc)*(1 - 1/dfo)/0.08
#   lcoe = (annual_capital_cost*pvf_construction + annual_operating_cost*pvf_operation)
#          / (annual_energy*pvf_operation)
_HAND_LCOE_AT_GAIN_100 = 216.55528392479388

# Anchor A — Meier_HIF_Driver_Cost (hif_economics.sysml), in isolation:
#   cost_billions = (0.32 + 0.088*5.0)*(1.25 + 0.05*1.0)*(1.0 + 0.0088*(3.5 - 5.0))
#                 = 0.76 * 1.30 * 0.9868                            = 0.9749584
#   bank_energy_joules = 5.0*1.0e6/0.35 ; gamma = cost_billions*1.0e9/bank_energy_joules
#                                                                     = 68.247088
_ANCHOR_A_COST_BILLIONS = 0.9749584
_ANCHOR_A_GAMMA = 68.247088

# Anchor B — Recirculating_Power_Fraction (fusion_cycle.sysml), in isolation:
#   f_recirc = 1.0 / (eta*gain*blanket_multiplier*thermal_efficiency)
#            = 1.0 / (0.35*80.0*1.15*0.43)                          = 0.07222302470027446
_ANCHOR_B_F_RECIRC = 0.07222302470027446


def _gen(tmp_path):
    """Generate the fusion-tea package from the committed v2 snapshot (license-free).

    The package name is unique per test (derived from pytest's per-test tmp_path). The
    runner imports the package by its directory name; a shared name across tests would
    collide in ``sys.modules`` (a stale import wins), so each test gets its own.
    """
    pkg_name = "ftacc_" + tmp_path.name.replace("-", "_").lower()
    cfg = GenerationConfig(
        output_path=tmp_path / pkg_name,
        from_snapshot=snapshot_fixture("fusion_tea"),
        package_name=pkg_name,
        overwrite=True,
    )
    assert run_codegen(cfg) is True
    return tmp_path / pkg_name


def _module_class(pkg, module_type):
    """Import a generated module class by its pipeline-YAML module_type (for A/B)."""
    _install_simkit_stub()
    parent = str(pkg.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    import_path, class_name = _module_import_path(pkg.name, module_type)
    return getattr(importlib.import_module(import_path), class_name)


def test_run_c_reproduces(tmp_path):
    """Anchor C: the full generated pipeline executes to run-C's lcoe (270.12)."""
    out = run_pipeline(_gen(tmp_path))
    assert out[_LCOE_CHANNEL] == pytest.approx(_RUN_C_LCOE, rel=1e-6)


def test_gain_perturbation_is_consumed(tmp_path):
    """SC-B rider: moving the emitted gain key moves lcoe to the hand-computed target.

    Proves the entry-point JSON is genuinely consumed (not shadowed by a baked default).
    """
    out = run_pipeline(_gen(tmp_path), inputs={_GAIN_EP_KEY: _GAIN_PERTURBED})
    assert out[_LCOE_CHANNEL] == pytest.approx(_HAND_LCOE_AT_GAIN_100, rel=1e-6)


def test_meier_driver_cost_module(tmp_path):
    """Anchor A (module-level): the Meier driver-cost calc's own arithmetic."""
    cls = _module_class(_gen(tmp_path), "hif_economics.Meier_HIF_Driver_CostModule")
    data = cls().run(
        beam_energy_mj=5.0, driver_efficiency=0.35, num_chambers=1.0, rep_rate=3.5
    ).data
    assert data.gamma == pytest.approx(_ANCHOR_A_GAMMA, rel=1e-6)
    assert data.cost_billions == pytest.approx(_ANCHOR_A_COST_BILLIONS, rel=1e-6)


def test_recirc_fraction_module(tmp_path):
    """Anchor B (module-level): the recirculating-power-fraction calc's own arithmetic."""
    cls = _module_class(_gen(tmp_path), "fusion_cycle.Recirculating_Power_FractionModule")
    data = cls().run(
        eta=0.35, gain=80.0, blanket_multiplier=1.15, thermal_efficiency=0.43
    ).data
    assert data.root == pytest.approx(_ANCHOR_B_F_RECIRC, rel=1e-6)
