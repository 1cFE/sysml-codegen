"""Slice 3D: the customer model executes in real TEAx, live and relocated.

The route under test, end to end and through public APIs only:

    load/extract -> elaborate -> project -> generate -> seal
      -> ``ProvisionalPackageLoader`` (verifier authentication + seal check + import)
      -> ``create_<package>_registry`` (backed by ``simkit.core.registry_builder``)
      -> ``simkit.core.pipeline.execute_pipeline``

Two packages take that route: one generated live from the model tree, one
generated from a v6 instance-graph snapshot copied to a different directory
with the model tree deleted. Both are compared against
``fusion_tea_arithmetic``, a hand transcription of the SysML equations that
never reads a generated artifact.

**No skips.** A missing licence or a missing ``simkit`` fails these tests rather
than skipping them. The recovery plan requires the real-TEAx evidence to run in
the acceptance command and forbids a gate that can go green without executing,
so the prerequisites are asserted, not tolerated.

**No stub.** ``tests/runtime/pipeline_runner.py`` installs a fake ``simkit``
(``_install_simkit_stub``) and takes an ``inputs=`` override the real
``execute_pipeline`` has no counterpart for. It is absent from this lane, and
``test_the_lane_runs_the_real_simkit`` asserts that.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

from sysml_codegen.orchestration.exact_pipeline_context import (
    build_exact_pipeline_context,
    build_exact_pipeline_context_from_snapshot,
)
from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot
from tests.execution import fusion_tea_arithmetic as hand
from tests.execution.real_teax import (
    FUSION_TEA,
    LCOE_CHANNEL,
    execute_sealed_package,
    generate_package_from_models,
    generate_package_from_snapshot,
)

pytestmark = pytest.mark.execution

REL = 1e-12

#: Every channel the pipeline publishes. Pinned as a set so a module that stops
#: producing an output, or starts producing an extra one, fails here.
EXPECTED_CHANNELS = {
    "constraint_report",
    "hif_driver__hif_driver_instance__meier_cost__cost_billions",
    "hif_driver__hif_driver_instance__meier_cost__gamma",
    "hif_plant_pkg__hif_plant__driver__meier_cost__cost_billions",
    "hif_plant_pkg__hif_plant__driver__meier_cost__gamma",
    "hif_plant_pkg__hif_plant__lcoe_calc__lcoe",
    "hif_plant_pkg__hif_plant__meier_capital_calc__total_capital_billions",
    "hif_plant_pkg__hif_plant__meier_coe_calc__coe_cents_kwh",
    "hif_plant_pkg__hif_plant__meier_reactor_cost_calc__reactor_cost_billions",
    "hif_plant_pkg__hif_plant__recirc_calc__f_recirc",
    "hif_plant_pkg__hif_plant__viability__81ddf10fb1d1749b__evaluation",
}

VIABILITY_ID = "hif_plant_pkg__hif_plant__viability__81ddf10fb1d1749b"


def _numeric_outputs(result) -> dict[str, float]:
    """Every numeric channel, unwrapped.

    Single-output modules publish a ``RootModel[float]``; a multi-output
    module's fields arrive as plain floats. Both are numeric channels, and the
    every-and-only comparisons below need all of them.
    """
    numeric: dict[str, float] = {}
    for name, value in result.outputs.items():
        if hasattr(value, "root"):
            numeric[name] = float(value.root)
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            numeric[name] = float(value)
    return numeric


@pytest.fixture(scope="module")
def environment() -> dict[str, str]:
    """The resolved environment this evidence was produced in.

    Asserted rather than reported: the recovery plan requires the acceptance run
    to resolve ``simkit`` from the pinned TEAx checkout and both project packages
    from the rebuild worktrees, and a run that silently resolved elsewhere would
    be measuring a different tree.
    """
    import agentic_mbse
    import simkit

    import sysml_codegen

    resolved = {
        "python": sys.executable,
        "simkit": str(Path(simkit.__file__).resolve()),
        "sysml_codegen": str(Path(sysml_codegen.__file__).resolve()),
        "agentic_mbse": str(Path(agentic_mbse.__file__).resolve()),
    }
    assert "/teax/packages/teax-simkit/" in resolved["simkit"], resolved
    assert "-item7-rebuild/" in resolved["sysml_codegen"], resolved
    assert "-item7-rebuild/" in resolved["agentic_mbse"], resolved
    return resolved


@pytest.fixture(scope="module")
def live_package(tmp_path_factory, environment) -> dict[str, object]:
    """Generate, seal, load, and execute the live-route package."""
    root = tmp_path_factory.mktemp("ft-live")
    name = "fusion_tea_live"
    package = generate_package_from_models(FUSION_TEA, root / name, name)
    return execute_sealed_package(package, name, root)


@pytest.fixture(scope="module")
def relocated_package(tmp_path_factory, environment) -> dict[str, object]:
    """Capture a v6 snapshot, move it, delete the model tree, then generate.

    "Relocated" here is literal: the snapshot is read from a directory that is
    neither where it was captured nor anywhere near the model, and the model
    tree no longer exists when generation runs.
    """
    root = tmp_path_factory.mktemp("ft-relocated")
    model_copy = root / "model-tree" / "fusion_tea"
    shutil.copytree(FUSION_TEA, model_copy)
    captured = capture_instance_graph_snapshot([model_copy], root / "capture" / "ft.json")

    moved = root / "elsewhere" / "ft.json"
    moved.parent.mkdir(parents=True)
    shutil.copyfile(captured, moved)
    shutil.rmtree(root / "model-tree")
    assert not model_copy.exists()

    name = "fusion_tea_relocated"
    package = generate_package_from_snapshot(moved, root / name, name)
    return execute_sealed_package(package, name, root)


# ---------------------------------------------------------------------------
# The lane itself
# ---------------------------------------------------------------------------


def test_the_lane_runs_the_real_simkit(environment) -> None:
    """The fake ``simkit`` never entered this process."""
    assert "sysml-codegen" not in environment["simkit"]
    stub_owner = sys.modules.get("tests.runtime.pipeline_runner")
    assert stub_owner is None, (
        "the in-repo stub runner was imported on the real-TEAx lane; its fake simkit "
        "would shadow the installed one"
    )
    import simkit.core.pipeline

    assert Path(simkit.core.pipeline.__file__).is_file()


def test_the_generated_registry_is_the_public_simkit_builder(live_package) -> None:
    """Registry discovery goes through ``simkit.core.registry_builder.create_registry``."""
    assert live_package["registry_backing"] is live_package["public_create_registry"]
    registry = live_package["registry"]
    assert type(registry).__module__ == "simkit.core.pipeline_registry"
    assert registry.has("ife_lcoe.IFE_LCOEModule")


# ---------------------------------------------------------------------------
# Live route
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("route", ["live", "relocated"])
def test_the_package_publishes_exactly_eleven_channels(
    route, live_package, relocated_package
) -> None:
    result = (live_package if route == "live" else relocated_package)["result"]
    assert set(result.outputs) == EXPECTED_CHANNELS
    assert len(result.outputs) == 11


@pytest.mark.parametrize("route", ["live", "relocated"])
def test_real_teax_reproduces_the_hand_computed_arithmetic(
    route, live_package, relocated_package
) -> None:
    """Every numeric channel, against the transcription — not against each other."""
    result = (live_package if route == "live" else relocated_package)["result"]
    outputs = _numeric_outputs(result)

    assert outputs[LCOE_CHANNEL] == pytest.approx(hand.lcoe(), rel=REL)
    assert hand.lcoe() == hand.RUN_C_LCOE
    assert outputs[LCOE_CHANNEL] == pytest.approx(hand.RUN_C_LCOE, rel=1e-6)

    assert outputs[
        "hif_plant_pkg__hif_plant__meier_coe_calc__coe_cents_kwh"
    ] == pytest.approx(hand.meier_coe_cents_kwh(), rel=REL)
    assert outputs[
        "hif_plant_pkg__hif_plant__meier_capital_calc__total_capital_billions"
    ] == pytest.approx(hand.total_capital_billions(), rel=REL)
    assert outputs[
        "hif_plant_pkg__hif_plant__meier_reactor_cost_calc__reactor_cost_billions"
    ] == pytest.approx(hand.reactor_cost_billions(), rel=REL)
    assert outputs["hif_plant_pkg__hif_plant__recirc_calc__f_recirc"] == pytest.approx(
        hand.recirculating_fraction(), rel=REL
    )
    for prefix in (
        "hif_driver__hif_driver_instance__meier_cost",
        "hif_plant_pkg__hif_plant__driver__meier_cost",
    ):
        assert outputs[f"{prefix}__gamma"] == pytest.approx(hand.driver_gamma(), rel=REL)
        assert outputs[f"{prefix}__cost_billions"] == pytest.approx(
            hand.driver_cost_billions(), rel=REL
        )


@pytest.mark.parametrize("route", ["live", "relocated"])
def test_the_constraint_report_carries_the_modeled_verdict(
    route, live_package, relocated_package
) -> None:
    """C19 at the constraint consumer: the plant's 80.0 gain reaches the predicate.

    ``eta * gain_in >= threshold`` with the modelled 0.35, 80.0, and 10.0 is
    satisfied with margin 18.0 — arithmetic done here, not read back.

    Compared as a whole dump rather than field by field, so a field the report
    starts carrying has to be accounted for here before this passes. The one
    exception is ``catalog_fingerprint``, which is a digest of the catalog rather
    than a modelled value: there is nothing to derive it from by hand, so it is
    popped and checked for shape.
    """
    result = (live_package if route == "live" else relocated_package)["result"]
    dump = result.outputs["constraint_report"].model_dump(mode="json")

    fingerprint = dump.pop("catalog_fingerprint")
    assert isinstance(fingerprint, str)
    assert len(fingerprint) == 64 and set(fingerprint) <= set("0123456789abcdef")

    assert dump == {
        "headline": "all_satisfied",
        "assessed_count": 1,
        "results": [
            {
                "constraint_id": VIABILITY_ID,
                "status": "satisfied",
                "actual_value": True,
                "margin": hand.DRIVER_EFFICIENCY * hand.GAIN - hand.VIABILITY_THRESHOLD,
                "observed": {
                    "eta": hand.DRIVER_EFFICIENCY,
                    "gain_in": hand.GAIN,
                    "threshold": hand.VIABILITY_THRESHOLD,
                },
            }
        ],
    }


def test_c19_the_one_modeled_gain_reaches_the_calculation_and_the_constraint(
    live_package,
) -> None:
    """The same 80.0 on both consumer paths, read off the executed package.

    Calculation path: the emitted entry-point JSON carries 80.0, and moving it
    is what ``tests/runtime/test_fusion_tea_acceptance.py`` proves changes lcoe.
    Constraint path: the predicate's ``observed`` map carries the same 80.0.
    """
    package: Path = live_package["package"]
    inputs = json.loads((package / "inputs" / "hif_plant_params.json").read_text())
    assert inputs["hif_plant_pkg__hif_plant__gain"] == hand.GAIN

    source = (FUSION_TEA / "designs" / "hif_ife" / "hif_plant.sysml").read_text()
    assert ":>> gain = 80.0 {" in source

    report = live_package["result"].outputs["constraint_report"]
    (evaluation,) = report.results
    assert evaluation.observed["gain_in"] == hand.GAIN


# ---------------------------------------------------------------------------
# Live vs relocated
# ---------------------------------------------------------------------------


def test_live_and_relocated_packages_execute_to_equal_outputs(
    live_package, relocated_package
) -> None:
    """Byte-equal numeric outputs and an identical constraint report."""
    live = _numeric_outputs(live_package["result"])
    relocated = _numeric_outputs(relocated_package["result"])

    assert set(live) == set(relocated)
    assert live == relocated

    live_report = live_package["result"].outputs["constraint_report"]
    relocated_report = relocated_package["result"].outputs["constraint_report"]
    assert live_report.model_dump(mode="json") == relocated_report.model_dump(mode="json")


def test_the_two_packages_carry_the_same_model_and_differ_only_in_provenance(
    live_package, relocated_package
) -> None:
    """Same model contract; different bytes, and only where provenance lives.

    The ``executable_fingerprint`` is a hash of the whole covered tree, so it is
    *not* equal: relocation changes each module's ``SysML Source:`` comment (the
    live route knows the checkout path, a relocated snapshot knows only its
    portable referent). That residual is the one carried to Slice 3E. What must
    be equal is the semantic surface, which is what ``model_contract.json``'s
    ``semantic_fingerprint`` covers.
    """
    live_dir: Path = live_package["package"]
    relocated_dir: Path = relocated_package["package"]

    def contract(package: Path) -> dict:
        return json.loads((package / "contracts" / "model_contract.json").read_text())

    assert (
        contract(live_dir)["semantic_fingerprint"]
        == contract(relocated_dir)["semantic_fingerprint"]
    )
    assert live_package["fingerprint"] != relocated_package["fingerprint"]

    def tree(root: Path, package_name: str) -> dict[str, str]:
        # Every file, not a suffix subset: the JSON contracts and the emitted
        # entry-point payloads are exactly where a real divergence would hide.
        # The two packages must carry distinct import names to coexist in one
        # interpreter, and that name is written into the generated text. Neutralise
        # it so the comparison is about the model, not about the name.
        return {
            str(path.relative_to(root)): path.read_text().replace(package_name, "<pkg>")
            for path in sorted(root.rglob("*"))
            if path.is_file() and "__pycache__" not in path.parts
        }

    live_tree = tree(live_dir, str(live_package["name"]))
    relocated_tree = tree(relocated_dir, str(relocated_package["name"]))
    assert set(live_tree) == set(relocated_tree)

    # The seal is a hash manifest over the tree, so it restates every difference
    # below as a changed digest and can carry no independent information. Excused
    # by name, and only this one file: anything else differing must be a
    # provenance comment.
    seal = "contracts/package_contract.json"
    assert seal in live_tree
    assert live_tree[seal] != relocated_tree[seal]

    differing = {
        name
        for name in live_tree
        if name != seal and live_tree[name] != relocated_tree[name]
    }
    assert differing
    for name in differing:
        live_lines = set(live_tree[name].splitlines())
        relocated_lines = set(relocated_tree[name].splitlines())
        # Both directions: a line the relocated package has and the live one does
        # not is just as much a divergence, and a one-sided check would let it
        # through whenever a provenance line also differed.
        only_one_side = (live_lines - relocated_lines) | (relocated_lines - live_lines)
        assert only_one_side
        assert all("SysML Source:" in line for line in only_one_side), (
            f"{name} differs somewhere other than its provenance comment: "
            f"{sorted(only_one_side)[:3]}"
        )


def test_the_relocated_package_was_built_without_the_model_tree(
    relocated_package,
) -> None:
    """The relocated route's own precondition, asserted rather than assumed."""
    package: Path = relocated_package["package"]
    assert package.is_dir()
    # The fixture deleted the copied model tree before generating; it stays gone.
    assert not (package.parent / "model-tree").exists()
    assert (package / "contracts" / "package_contract.json").is_file()
