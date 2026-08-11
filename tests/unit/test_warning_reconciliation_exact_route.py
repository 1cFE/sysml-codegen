"""Gate 4C, rows L-251 and L-249: the params-coverage boundary on the exact route.

Two rows meet here, because they are two halves of one mechanism —
``cli._reconcile_params_coverage``, which partitions the fell-through, valueless
entry points into an unwired remainder (one WARNING summary) and a wired half
(the V11 hard error).

**L-251, warning reconciliation.** The kept half of the responsibility is that a
clean model generates with no WARNING at all. That is asserted below across
every accepted-fixture shape the exact route has: plain formulas, aggregation,
constraints, quoted names, a costed hierarchy, and a v6 snapshot replay.

The row's other half — the ``OutputRegistry`` alias-collision count-summary —
**has no exact-route counterpart.** That summary is emitted by
``orchestration/output_registry_builder.py:385``, and the exact route never
builds an ``OutputRegistry``: nothing in ``run_codegen``'s closure imports that
module. The behaviour did not move, it retired with the mechanism that had it.
Recorded as a Gate 4C surfacing rather than replaced with a lookalike.

**L-249, the V11 seeded abort.** It cannot be reached through public generation
on the exact route, and the test below proves why rather than asserting it.
``elaboration/project.py`` constructs every ``ComputationGraph`` with
``fallback_entry_points=set()`` — both in ``run`` and in ``select`` — and both
collectors filter on membership in that set. So the guard still runs on every
generation and can never fire. That is a finding about the guard, not a gap in
this module's coverage: the collectors themselves stay pinned by the nine
graph-level nodes in ``tests/unit/test_uncovered_params.py``, which build their
graphs directly and are route-neutral.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from sysml_codegen.cli import GenerationConfig, run_codegen
from tests.conftest import FIXTURES_DIR, requires_license

V6_SNAPSHOT = FIXTURES_DIR / "fusion_tea" / "instance_graph_snapshot.json"

# One accepted fixture per shape the exact route can produce a package from.
CLEAN_FIXTURES = [
    "attr_expr_probe",          # formulas and EXPOSE attributes
    "wi014_toy",                # a constraint and its report
    "source_identity_mixed_consumers",  # every module kind but aggregation
    "costed_cart_d5",           # a costed hierarchy with aggregations
    "alias_agg_d5",             # quoted names and a chain alias
]

# ``costed_cart_d5`` names the same rolled attribute in three assemblies, so the
# registry legitimately reports a module-class collision and aliases the imports.
# That is a different category, owned by REQ-REG-04, and silencing it here would
# be scoping the sweep to whatever currently passes. It is named instead.
SILENT_FIXTURES = [name for name in CLEAN_FIXTURES if name != "costed_cart_d5"]


def _warnings(caplog) -> list[str]:
    return [record.message for record in caplog.records if record.levelno >= logging.WARNING]


@requires_license
@pytest.mark.parametrize("fixture", SILENT_FIXTURES)
def test_a_clean_model_generates_with_no_warning(fixture: str, tmp_path: Path, caplog) -> None:
    with caplog.at_level(logging.WARNING):
        assert run_codegen(
            GenerationConfig(
                models_path=FIXTURES_DIR / fixture,
                output_path=tmp_path / "out",
                package_name="wr",
                overwrite=True,
            )
        ), f"{fixture} should generate cleanly"
    assert _warnings(caplog) == [], f"{fixture} emitted WARNING lines"


@requires_license
def test_the_costed_hierarchy_warns_only_about_its_module_class_collision(
    tmp_path: Path, caplog
) -> None:
    """The one fixture that warns, and the whole of what it says."""
    with caplog.at_level(logging.WARNING):
        assert run_codegen(
            GenerationConfig(
                models_path=FIXTURES_DIR / "costed_cart_d5",
                output_path=tmp_path / "out",
                package_name="wr",
                overwrite=True,
            )
        )
    messages = _warnings(caplog)
    assert len(messages) == 1, messages
    assert messages[0].startswith("Module class name collisions detected:")
    assert "Generating aliased imports" in messages[0]


def test_a_snapshot_replay_generates_with_no_warning(tmp_path: Path, caplog) -> None:
    with caplog.at_level(logging.WARNING):
        assert run_codegen(
            GenerationConfig(
                from_snapshot=V6_SNAPSHOT,
                output_path=tmp_path / "out",
                package_name="fusion_tea",
                overwrite=True,
            )
        )
    assert _warnings(caplog) == []


@requires_license
@pytest.mark.parametrize("fixture", CLEAN_FIXTURES)
def test_no_reconciliation_summary_is_emitted(fixture: str, tmp_path: Path, caplog) -> None:
    """The category the row names, checked by its message rather than by silence."""
    with caplog.at_level(logging.WARNING):
        assert run_codegen(
            GenerationConfig(
                models_path=FIXTURES_DIR / fixture,
                output_path=tmp_path / "out",
                package_name="wr",
                overwrite=True,
            )
        )
    assert not any("Unresolved after assembly" in message for message in _warnings(caplog))


@requires_license
@pytest.mark.parametrize("fixture", CLEAN_FIXTURES)
def test_the_exact_route_projects_no_fall_through_entry_points(fixture: str) -> None:
    """Why no summary is emitted, and why L-249 cannot be reached from here.

    The reconciliation summary and the V11 abort both key on
    ``graph.fallback_entry_points``. The exact route's projection constructs
    every graph with that set empty, so both collectors are structurally empty
    on the shipped route. Asserting the cause, not just the effect, is what
    makes the L-249 surfacing checkable.
    """
    from sysml_codegen.orchestration.exact_pipeline_context import (
        build_exact_pipeline_context,
    )
    from sysml_codegen.resolution.uncovered_params import (
        collect_uncovered_params,
        collect_unwired_fallthrough,
    )

    graph = build_exact_pipeline_context([FIXTURES_DIR / fixture]).computation_graph
    assert graph.fallback_entry_points == set()
    assert collect_uncovered_params(graph) == []
    assert collect_unwired_fallthrough(graph) == []


def test_the_projection_hard_codes_an_empty_fall_through_set() -> None:
    """The surfacing, pinned at its source so it cannot be closed silently.

    ``elaboration/project.py`` builds a ``ComputationGraph`` in two places, and
    both pass ``fallback_entry_points=set()`` as a literal. While that is true,
    ``cli._reconcile_params_coverage`` is dead code on the shipped route. If the
    projection starts populating the set, this test fails and row L-249 becomes
    authorable — which is the point.
    """
    import importlib

    # The package re-exports a ``project`` *function* of the same name, so the
    # module has to be fetched explicitly rather than by attribute access.
    projection_module = importlib.import_module("sysml_codegen.elaboration.project")
    source = Path(projection_module.__file__).read_text()
    assert source.count("fallback_entry_points=set()") == 2
    assert "fallback_entry_points=" not in source.replace("fallback_entry_points=set()", "")


@requires_license
@pytest.mark.parametrize("fixture", CLEAN_FIXTURES)
def test_no_output_registry_alias_summary_is_ever_emitted(
    fixture: str, tmp_path: Path, caplog
) -> None:
    """The other surfacing: the alias-collision summary has no exact-route home.

    The count-summary L-251 names is emitted while building an
    ``OutputRegistry`` (``orchestration/output_registry_builder.py:385``). The
    exact route builds none, so the message cannot appear — including on
    ``costed_cart_d5``, whose four same-named module classes are the closest
    thing the exact route has to the collisions that summary counted.

    The module is still *importable* from ``sysml_codegen.orchestration``'s
    re-exports; what matters is that nothing constructs one, which is the 3E
    construction-closure pin. This asserts the consequence, at the log.
    """
    with caplog.at_level(logging.DEBUG):
        assert run_codegen(
            GenerationConfig(
                models_path=FIXTURES_DIR / fixture,
                output_path=tmp_path / "out",
                package_name="wr",
                overwrite=True,
            )
        )
    messages = [record.message for record in caplog.records]
    assert not any("OutputRegistry" in message for message in messages)
    assert not any("alias collision" in message for message in messages)
