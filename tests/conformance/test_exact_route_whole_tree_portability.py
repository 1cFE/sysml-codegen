"""Gate 4C, row L-188: whole-tree checkout-root portability, exact route.

The responsibility this replaces is
``tests/conformance/test_whole_tree_portability.py::test_catf_mfe_whole_tree_two_root_portable``:
the same snapshot bytes replayed at two distinct absolute checkout roots produce
byte-identical output trees, and no checkout-absolute path reaches any generated
file. Its specimen was a **v5** snapshot of ``catf_mfe_model``, corpus row 5,
which the exact route refuses.

This is a completeness gate rather than a field-by-field check: it does not
enumerate the fields that could leak a root, it asserts that nothing did. Any
checkout byte reaching output shows up either as a two-root diff or as an
absolute ``.sysml`` path in the scan.
"""

from __future__ import annotations

import re
from pathlib import Path

from sysml_codegen.cli import GenerationConfig, run_codegen
from tests.conftest import FIXTURES_DIR

V6_SNAPSHOT = FIXTURES_DIR / "fusion_tea" / "instance_graph_snapshot.json"
PACKAGE = "fusion_tea"

# An absolute filesystem path ending in ``.sysml``. The leading ``/`` must not be
# preceded by a word character or dash, so the portable ``root-0/library/x.sysml``
# referent never matches while ``/home/reid/.../x.sysml`` does.
_ABSOLUTE_SYSML = re.compile(rb"(?<![\w-])/(?:[\w.-]+/)+[\w.-]+\.sysml")


def _tree_bytes(tree: Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(tree)): path.read_bytes()
        for path in sorted(tree.rglob("*"))
        if path.is_file()
    }


def _generate(snapshot: Path, output: Path) -> Path:
    assert run_codegen(
        GenerationConfig(
            output_path=output,
            from_snapshot=snapshot,
            package_name=PACKAGE,
            schema_class_name="Params",
            pipeline_name="pipeline",
            overwrite=True,
        )
    )
    return output


def test_the_same_snapshot_at_two_checkout_roots_writes_one_tree(tmp_path: Path) -> None:
    snapshot_bytes = V6_SNAPSHOT.read_bytes()
    roots = [tmp_path / "checkout-a", tmp_path / "checkout-b"]
    outputs = []
    for index, root in enumerate(roots):
        root.mkdir()
        snapshot = root / "instance_graph_snapshot.json"
        snapshot.write_bytes(snapshot_bytes)
        outputs.append(_generate(snapshot, tmp_path / f"out-{index}"))

    first, second = (_tree_bytes(output) for output in outputs)
    differing = sorted(
        key for key in set(first) | set(second) if first.get(key) != second.get(key)
    )
    assert differing == [], f"the two checkout roots produced different trees: {differing}"


def test_no_checkout_absolute_path_reaches_a_generated_file(tmp_path: Path) -> None:
    root = tmp_path / "checkout"
    root.mkdir()
    snapshot = root / "instance_graph_snapshot.json"
    snapshot.write_bytes(V6_SNAPSHOT.read_bytes())
    output = _generate(snapshot, tmp_path / "out")

    needle = root.as_posix().encode()
    hits = [
        relative
        for relative, data in _tree_bytes(output).items()
        if needle in data or _ABSOLUTE_SYSML.search(data)
    ]
    assert hits == [], f"generated files carry a checkout-absolute path: {hits}"


def test_the_scan_would_catch_a_leak(tmp_path: Path) -> None:
    """The completeness gate is only worth its name if the detector actually fires."""
    assert _ABSOLUTE_SYSML.search(b"SysML Source: /home/x/models/library.sysml:4")
    assert not _ABSOLUTE_SYSML.search(b"SysML Source: root-0/library/analyses/ife_lcoe.sysml:4")
