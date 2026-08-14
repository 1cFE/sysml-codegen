"""Smart regeneration proved as behavior through the public route.

Replacement coverage for four rows whose tests retired with ``test_gen_stencils.py``
(ledger L-150) and had no recorded heir (narrow-correction step 4, rev-2 brief).
The retired tests were static source inspections; these are their behavioral
re-derivations, run through ``run_codegen`` end to end:

- REQ-SR-01 — an existing implementation whose interface still matches the graph
  is preserved; a type-level change (return annotation) and a field-level change
  (the ``inputs.*`` reference set) each regenerate it, with the old file backed up.
- REQ-SR-02 — reference order alone never regenerates: permuting the body's
  ``inputs.*`` references while keeping the same set preserves the file.
- REQ-SR-06 — every stencil-bearing module kind (calculation, formula,
  aggregation) rides the same preservation path: a marker planted in every
  generated implementation of ``solar_battery_d5`` survives a smart rerun.
- REQ-SR-07 — ``preserve_handwritten`` without ``smart_regen`` is a blanket
  skip: even a file whose signature no longer matches anything is left
  byte-identical, with no backup and no comparison.

Everything runs license-free from committed v6 snapshots. Regeneration runs pass
``smart_regen=True, preserve_handwritten=True`` — the flag pair the clear step
requires, since only ``preserve_handwritten`` exempts ``handwritten/`` from the
overwrite clear (`cli/__init__.py`, ``_clear_output_directory``).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.cli import GenerationConfig, run_codegen
from sysml_codegen.orchestration.exact_pipeline_context import (
    build_exact_pipeline_context_from_snapshot,
)
from tests.conftest import FIXTURES_DIR

FUSION_SNAPSHOT = FIXTURES_DIR / "fusion_tea" / "instance_graph_snapshot.json"
SOLAR_SNAPSHOT = FIXTURES_DIR / "solar_battery_d5" / "instance_graph_snapshot.json"
MARKER = "# HANDWRITTEN-BY-A-HUMAN sentinel for smart-regen proof"


def _generate(snapshot: Path, output: Path, **flags) -> None:
    assert run_codegen(
        GenerationConfig(
            output_path=output,
            from_snapshot=snapshot,
            package_name=output.name,
            overwrite=True,
            **flags,
        )
    ), f"generation from {snapshot} must succeed"


def _smart_rerun(snapshot: Path, output: Path) -> None:
    _generate(snapshot, output, smart_regen=True, preserve_handwritten=True)


@pytest.fixture()
def fusion_package(tmp_path) -> Path:
    output = tmp_path / "fusion_regen"
    _generate(FUSION_SNAPSHOT, output)
    return output


def _impl(package: Path, stem: str) -> Path:
    matches = sorted(package.rglob(f"{stem}_impl.py"))
    assert len(matches) == 1, f"expected exactly one {stem}_impl.py, found {matches}"
    return matches[0]


def test_matching_interface_is_preserved_with_edits_intact(fusion_package: Path) -> None:
    """REQ-SR-01, match path: no interface change means the human's file wins."""
    impl = _impl(fusion_package, "recirculating_power_fraction")
    edited = impl.read_text() + f"\n{MARKER}\n"
    impl.write_text(edited)

    _smart_rerun(FUSION_SNAPSHOT, fusion_package)

    assert impl.read_text() == edited, "signature-matched impl must be preserved verbatim"
    assert not (fusion_package / "handwritten" / "backup").exists(), (
        "a preserved impl must not be backed up"
    )


def test_return_type_change_regenerates_and_backs_up(fusion_package: Path) -> None:
    """REQ-SR-01, type level: the return annotation is part of the interface."""
    impl = _impl(fusion_package, "meier_reactor_cost")
    mutated = impl.read_text().replace("-> float", "-> int")
    assert "-> int" in mutated, "the fixture impl lost its float return; re-anchor"
    mutated += f"\n{MARKER}\n"
    impl.write_text(mutated)

    _smart_rerun(FUSION_SNAPSHOT, fusion_package)

    regenerated = impl.read_text()
    assert MARKER not in regenerated, "a type-mismatched impl must be regenerated"
    assert "-> float" in regenerated, "regeneration must restore the graph's interface"
    backups = list((fusion_package / "handwritten" / "backup").rglob("*.py"))
    assert any(MARKER in b.read_text() for b in backups), (
        "the human's mismatched impl must survive in backup/"
    )


def test_changed_input_field_set_regenerates(fusion_package: Path) -> None:
    """REQ-SR-01, field level: the ``inputs.*`` reference set is compared."""
    impl = _impl(fusion_package, "meier_total_capital_cost")
    source = impl.read_text()
    lines = source.splitlines()
    returns = [i for i, line in enumerate(lines) if line.strip().startswith("return ")]
    assert returns, "fixture impl has no return statement; re-anchor"
    lines.insert(returns[-1], "    _ = inputs.phantom_field_never_modeled")
    impl.write_text("\n".join(lines) + f"\n{MARKER}\n")

    _smart_rerun(FUSION_SNAPSHOT, fusion_package)

    regenerated = impl.read_text()
    assert MARKER not in regenerated, (
        "an impl whose input reference set differs from the graph must regenerate"
    )
    assert "phantom_field_never_modeled" not in regenerated


def test_reference_order_alone_never_regenerates(fusion_package: Path) -> None:
    """REQ-SR-02: same reference set, different order — preserved."""
    impl = _impl(fusion_package, "ife_lcoe")
    source = impl.read_text()
    head, sep, tail = source.partition("    return ")
    assert sep, "fixture impl has no return statement; re-anchor"
    body_lines = head.splitlines()
    assigns = [i for i, line in enumerate(body_lines) if "inputs." in line]
    assert len(assigns) >= 2, "need two input-referencing lines to permute; re-anchor"
    first, last = assigns[0], assigns[-1]
    body_lines[first], body_lines[last] = body_lines[last], body_lines[first]
    permuted = "\n".join(body_lines) + "\n" + sep + tail + f"\n{MARKER}\n"
    impl.write_text(permuted)

    _smart_rerun(FUSION_SNAPSHOT, fusion_package)

    assert impl.read_text() == permuted, (
        "permuting input references must not count as an interface change"
    )


def test_preserve_handwritten_is_a_blanket_skip_without_comparison(
    fusion_package: Path,
) -> None:
    """REQ-SR-07: preserve means preserve — even a wrong interface stays."""
    impl = _impl(fusion_package, "meier_coe")
    garbled = f"{MARKER}\ndef run_something_else(unrelated):\n    return None\n"
    impl.write_text(garbled)

    _generate(FUSION_SNAPSHOT, fusion_package, preserve_handwritten=True)

    assert impl.read_text() == garbled, (
        "preserve_handwritten must skip existing impls without signature comparison"
    )
    assert not (fusion_package / "handwritten" / "backup").exists()


def test_every_stencil_bearing_module_kind_is_preserved(tmp_path) -> None:
    """REQ-SR-06: calculation, formula, and aggregation stencils all ride
    the same preservation path — proved by marking every generated impl."""
    graph = build_exact_pipeline_context_from_snapshot(SOLAR_SNAPSHOT).computation_graph
    kinds = {m.module_kind.value for m in graph.modules}
    assert {"calculation", "formula", "aggregation"} <= kinds, (
        f"solar_battery_d5 no longer carries all three stencil kinds ({kinds}); re-anchor"
    )

    output = tmp_path / "solar_regen"
    _generate(SOLAR_SNAPSHOT, output)
    impls = sorted((output / "handwritten").rglob("*_impl.py"))
    assert impls, "the package generated no implementation stencils; re-anchor"
    for impl in impls:
        impl.write_text(impl.read_text() + f"\n{MARKER}\n")

    _smart_rerun(SOLAR_SNAPSHOT, output)

    lost = [
        str(impl.relative_to(output))
        for impl in impls
        if MARKER not in impl.read_text()
    ]
    assert lost == [], (
        "these implementations were rewritten despite unchanged interfaces "
        f"(a module kind is bypassing smart-regen preservation): {lost}"
    )
