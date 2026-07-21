"""Lifecycle Item 5 — whole-tree snapshot portability (Axis 1).

Two real checkout roots, same semantic input -> byte-identical output tree and no
checkout-absolute path anywhere in it. This is the completeness gate: it does not
depend on enumerating every leaking field by hand. Any checkout-root byte that reaches
output shows up as a two-root diff or as an absolute source path in the scan.

The license-free leg (`test_catf_mfe_whole_tree_two_root_portable`) is the primary gate
and fails RED before the referent generalization lands. The licensed leg completes Item 1's
deferred relocated anonymous-admitted leg (`OccurrenceDemandAnonymous__Admitted`).
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from sysml_codegen.cli import GenerationConfig, run_codegen
from sysml_codegen.snapshot import build_full_graph_from_snapshot, capture_snapshot
from tests.conftest import FIXTURES_DIR, requires_license

# An absolute filesystem path ending in ``.sysml`` — i.e. a checkout-absolute source
# leak. The leading ``/`` must not be preceded by a word char or dash, so the portable
# ``root-0/library/x.sysml`` referent (its inner ``/`` sits after ``0``/``y``) never
# matches, while ``/home/reid/.../x.sysml`` does. Requires at least one intermediate dir.
_ABSOLUTE_SYSML = re.compile(rb"(?<![\w-])/(?:[\w.-]+/)+[\w.-]+\.sysml")


def _generate_tree(snapshot: Path, output: Path, package: str) -> None:
    assert run_codegen(
        GenerationConfig(
            output_path=output,
            from_snapshot=snapshot,
            package_name=package,
            schema_class_name="Params",
            pipeline_name="pipeline",
            overwrite=True,
        )
    )


def _tree_bytes(tree: Path) -> dict[str, bytes]:
    """Map every generated file to its bytes, keyed by path relative to the tree root."""
    return {
        str(path.relative_to(tree)): path.read_bytes()
        for path in sorted(tree.rglob("*"))
        if path.is_file()
    }


def _diff_paths(first: dict[str, bytes], second: dict[str, bytes]) -> list[str]:
    """Relative paths that differ (present on one side only, or differing bytes)."""
    keys = sorted(set(first) | set(second))
    return [key for key in keys if first.get(key) != second.get(key)]


def _absolute_hits(tree: Path, needles: list[str]) -> list[str]:
    """Files whose bytes contain any literal needle or any absolute ``.sysml`` path."""
    hits: list[str] = []
    encoded = [needle.encode() for needle in needles]
    for rel, data in _tree_bytes(tree).items():
        if any(needle in data for needle in encoded) or _ABSOLUTE_SYSML.search(data):
            hits.append(rel)
    return sorted(hits)


def _place_snapshot(root: Path, snapshot_bytes: bytes) -> Path:
    root.mkdir(parents=True)
    snapshot = root / "extraction_snapshot.json"
    snapshot.write_bytes(snapshot_bytes)
    return snapshot


def test_catf_mfe_whole_tree_two_root_portable(tmp_path: Path) -> None:
    """Same snapshot bytes at two distinct absolute roots -> identical output tree.

    The only thing that can differ between the two output trees is a field derived
    from the snapshot's absolute on-disk location — exactly the re-absolutized
    source_file. RED today: the docstring renderers embed the checkout-absolute path.
    """
    snapshot_bytes = (FIXTURES_DIR / "catf_mfe_model/extraction_snapshot.json").read_bytes()
    root_a = tmp_path / "checkout-a"
    root_b = tmp_path / "checkout-b"
    snapshot_a = _place_snapshot(root_a, snapshot_bytes)
    snapshot_b = _place_snapshot(root_b, snapshot_bytes)
    out_a = tmp_path / "out-a"
    out_b = tmp_path / "out-b"
    _generate_tree(snapshot_a, out_a, "catf_mfe")
    _generate_tree(snapshot_b, out_b, "catf_mfe")

    assert _diff_paths(_tree_bytes(out_a), _tree_bytes(out_b)) == []
    assert _absolute_hits(out_a, [root_a.as_posix()]) == []
    assert _absolute_hits(out_b, [root_b.as_posix()]) == []


def _admitted_default(graph) -> float:
    target = "OccurrenceDemandAnonymous__design__admitted__admitted_value"
    for group in graph.entry_point_groups:
        for parameter in group.parameters:
            if parameter.qualified_name == target:
                return parameter.default_value
    raise AssertionError(f"admitted entry point {target} not found")


@requires_license
def test_anonymous_admitted_relocated_graph_portable(tmp_path: Path) -> None:
    """Item 1's deferred leg: anonymous-admitted-with-actual, relocated replay.

    Item 1 certified only same-checkout replay for ``OccurrenceDemandAnonymous``.
    Here the snapshot is captured at two distinct checkout roots and at a relocated
    copy; the rebuilt graph and catalog must be identical across all three, the
    admitted anonymous actual (3.0) must survive, and the serialized graph must carry
    no checkout-absolute path. The anonymous fixture trips an unrelated constraint
    name-safety preflight in full code generation, so the proof is at the graph/
    catalog altitude — exactly where Item 1's replay evidence lives.
    """
    fixture = FIXTURES_DIR / "constraint_occurrence_demand/anonymous"
    model_text = (fixture / "model.sysml").read_text()
    # Two real checkout roots share the leaf directory ("proj") and differ only in
    # the absolute prefix — a genuine second checkout, not two differently-named
    # dirs. model_name (= the leaf) must therefore match across roots.
    roots = [tmp_path / "root-a" / "proj", tmp_path / "root-b" / "proj"]
    snapshots: list[Path] = []
    for root in roots:
        root.mkdir(parents=True)
        (root / "model.sysml").write_text(model_text)
        snapshots.append(capture_snapshot([root], root / "extraction_snapshot.json"))

    # Relocated leg: move a captured snapshot to an unrelated directory (same leaf).
    moved = tmp_path / "relocated" / "proj"
    moved.mkdir(parents=True)
    shutil.copy2(roots[0] / "model.sysml", moved / "model.sysml")
    shutil.copy2(snapshots[0], moved / "extraction_snapshot.json")
    replay_snapshots = [snapshots[0], snapshots[1], moved / "extraction_snapshot.json"]

    needles = [root.as_posix() for root in roots] + [moved.as_posix()]
    dumps: list[dict] = []
    for snapshot in replay_snapshots:
        graph, _inputs = build_full_graph_from_snapshot(snapshot)
        assert _admitted_default(graph) == 3.0
        assert graph.constraint_catalog is not None
        payload = json.dumps(graph.model_dump(mode="json")).encode()
        assert not any(needle.encode() in payload for needle in needles)
        assert not _ABSOLUTE_SYSML.search(payload)
        dumps.append(graph.model_dump(mode="json"))

    assert dumps[0] == dumps[1]
    assert dumps[0] == dumps[2]
