"""INV-6 on the exact route: a ``0.0`` default stays ``0.0``, never ``None``.

Gate 4C part 7 authored this so ``tests/unit/test_graph_builder_zero_default.py``
(ledger L-224) can retire with the legacy graph builder without losing its subject.

The bug it guards is a truthiness test where an identity test belongs. Legacy
``_classify_entry_points`` filled the default with ``if attr.default_value:``, which
drops ``"0.0"`` and ``""`` to ``None``. A Step-3-resolved entry point is not in the
fell-through set, so the V11 collector never inspects it — the ``null`` reaches the
generated JSON and fails at load. The exact route cannot reproduce that particular
code path, but it can reproduce the *mistake*, which is why the pins below are on the
projection's own default seam rather than on the legacy classification step.

License-free: both nodes read the committed v6 snapshot.
"""

from __future__ import annotations

from pathlib import Path

from tests.conftest import exact_graph_from_fixture

# `solar_battery_d5/design.sysml:61-62` declares two genuinely zero-valued design
# attributes — "No fuel for solar" — so the fixture carries the case by modelling
# intent rather than by a value planted for this test.
ZERO_VALUED_ATTRS = ("fuel_unit_cost", "fuel_consumption")


def test_a_zero_valued_design_attribute_projects_as_zero_not_null() -> None:
    """The end-to-end property, read off a real model.

    Stronger than the legacy node it replaces: that one hand-built a
    ``DesignAttributeData`` and called the classifier, where this projects the real
    fixture and looks at what a caller would actually receive.
    """
    graph = exact_graph_from_fixture("solar_battery_d5")
    defaults = {
        parameter.simple_name: parameter.default_value
        for group in graph.entry_point_groups
        for parameter in group.parameters
    }
    for name in ZERO_VALUED_ATTRS:
        assert name in defaults, f"{name} is not an entry point at all"
        assert defaults[name] == 0.0, f"{name} projected as {defaults[name]!r}"
        assert defaults[name] is not None


def test_the_projection_tests_identity_not_truthiness() -> None:
    """The rot pin, at the source, so the mistake cannot come back quietly.

    ``_float_default`` is the projection's only path to a ``None`` default. If that
    branch ever becomes a truthiness test again, every zero-valued attribute in every
    model silently becomes ``null`` — and only this assertion is positioned to say so
    before a generated package fails at load.
    """
    import importlib

    # The package re-exports a ``project`` *function* of the same name, so the module
    # has to be fetched explicitly rather than by attribute access.
    projection_module = importlib.import_module("sysml_codegen.elaboration.project")
    source = Path(projection_module.__file__).read_text()
    assert "if value is None:" in source
    assert "if not value:" not in source


def test_the_default_seam_maps_every_falsy_number_to_itself() -> None:
    """The seam directly, for the cases no committed fixture happens to carry."""
    from sysml_codegen.elaboration.project import _float_default

    assert _float_default(0.0) == 0.0
    assert _float_default(0) == 0.0
    assert _float_default(False) == 0.0
    assert _float_default(None) is None
