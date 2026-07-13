"""Throwaway S3 probe for calc-independent concrete constraint expansion.

The strict snapshot and ID functions are deliberately local to this script. They test the
design assumption without adding a production schema or choosing a production ID encoding.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import syside

from sysml_codegen.core.qualified_names import build_element_qualified_name
from sysml_codegen.extraction.hierarchy_resolver import extract_hierarchy_data
from sysml_codegen.extraction.usage_extractor import (
    _build_part_usage_index,
    _find_instantiation_paths,
    _supertype_closure,
    user_partdef_lookup,
)
from sysml_codegen.orchestration.pipeline_builder import find_instance_paths_for_partdef
from sysml_codegen.snapshot import SnapshotFormatError, load_extraction_snapshot

PROBE_SNAPSHOT_VERSION = 3
OWNER_QN = "InstanceIndexProbe__ConstrainedLeaf"
SOURCE_QN = "InstanceIndexProbe::ConstrainedLeaf::nonnegative"
EXPECTED_CONCRETE_PATHS = {
    "InstanceIndexProbe__root__bank__member[0]",
    "InstanceIndexProbe__root__bank__member[1]",
    "InstanceIndexProbe__root__bank__member[2]",
    "InstanceIndexProbe__root__direct_a",
    "InstanceIndexProbe__root__direct_b",
    "InstanceIndexProbe__root__container_a__leaf",
    "InstanceIndexProbe__root__plain_subtype",
    "InstanceIndexProbe__root__container_b__leaf",
    "InstanceIndexProbe__root__specialized__leaf",
}


class ProbeSnapshotError(ValueError):
    """Strict test-only snapshot rejection."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode()


def execution_id(owner_instance: str) -> str:
    """Return a deterministic test-only ID over the concept's identity inputs."""
    identity = {
        "membership_kind": "assert",
        "owner_instance": owner_instance,
        "polarity": "positive",
        "source_identity": SOURCE_QN,
    }
    return "cx_" + hashlib.sha256(canonical_bytes(identity)).hexdigest()[:24]


def fixed_multiplicity_paths(raw_paths: list[str], hierarchy: Any) -> list[str]:
    """Expand only unambiguous fixed literal multiplicities exposed by extraction."""
    counts_by_leaf: dict[str, int] = {}
    for multiplicity in hierarchy.multiplicities:
        if multiplicity.count is None:
            continue
        name = multiplicity.part_usage_name
        if name in counts_by_leaf:
            raise AssertionError(f"fixture has ambiguous multiplicity leaf name: {name}")
        counts_by_leaf[name] = multiplicity.count

    expanded: list[str] = []
    for path in raw_paths:
        count = counts_by_leaf.get(path.rsplit("__", 1)[-1])
        if count is None:
            expanded.append(path)
        else:
            expanded.extend(f"{path}[{index}]" for index in range(count))
    return sorted(expanded)


def paths_including_plain_subtypes(
    owner_qn: str, index: dict[str, list[Any]], model: Any
) -> list[str]:
    """Prototype the missing subtype-closure projection, with stable deduplication."""
    definitions = user_partdef_lookup(model)
    applicable_types = sorted(
        candidate_qn
        for candidate_qn in definitions
        if candidate_qn == owner_qn
        or owner_qn in _supertype_closure(candidate_qn, definitions)
    )
    return sorted(
        {
            path
            for applicable_type in applicable_types
            for path in _find_instantiation_paths(applicable_type, index)
        }
    )


def source_constraint(model: Any) -> Any:
    matches = [
        item
        for item in model.elements(syside.AssertConstraintUsage, include_subtypes=True)
        if str(getattr(item, "qualified_name", "")) == SOURCE_QN
    ]
    assert len(matches) == 1, [str(getattr(item, "qualified_name", "")) for item in matches]
    return matches[0]


def load_live(model_path: Path) -> dict[str, Any]:
    model, diagnostics = syside.try_load_model([str(model_path)])
    assert not diagnostics.contains_errors(warnings_as_errors=False), str(diagnostics)
    assert list(model.elements(syside.CalculationUsage, include_subtypes=True)) == []

    constraint = source_constraint(model)
    owner = getattr(constraint, "owner", None)
    assert build_element_qualified_name(owner) == OWNER_QN
    assert getattr(constraint, "is_negated", None) is False

    index = _build_part_usage_index(model)
    current_raw_paths = sorted(_find_instantiation_paths(OWNER_QN, index))
    complete_raw_paths = paths_including_plain_subtypes(OWNER_QN, index, model)
    hierarchy = extract_hierarchy_data(model)
    current_concrete_paths = fixed_multiplicity_paths(current_raw_paths, hierarchy)
    complete_concrete_paths = fixed_multiplicity_paths(complete_raw_paths, hierarchy)

    catalog = sorted(
        (
            {
                "constraint_id": execution_id(owner_path),
                "membership_kind": "assert",
                "owner_instance": owner_path,
                "polarity": "positive",
                "source_identity": SOURCE_QN,
            }
            for owner_path in complete_concrete_paths
        ),
        key=lambda row: row["constraint_id"],
    )
    return {
        "source": {
            "membership_kind": "assert",
            "owner_part_definition": OWNER_QN,
            "polarity": "positive",
            "source_identity": SOURCE_QN,
        },
        "complete_concrete_paths": complete_concrete_paths,
        "complete_raw_paths": complete_raw_paths,
        "current_concrete_paths": current_concrete_paths,
        "current_raw_paths": current_raw_paths,
        "catalog": catalog,
        "multiplicities": [
            {
                "count": item.count,
                "count_attribute_name": item.count_attribute_name,
                "owner_part_definition": item.owning_part_def_qn,
                "part_usage_name": item.part_usage_name,
            }
            for item in hierarchy.multiplicities
        ],
    }


def strict_snapshot(facts: dict[str, Any]) -> dict[str, Any]:
    return {
        "constraint_facts": facts,
        "snapshot_format_version": PROBE_SNAPSHOT_VERSION,
    }


def load_strict_snapshot(payload: bytes) -> dict[str, Any]:
    raw = json.loads(payload)
    version = raw.get("snapshot_format_version")
    if version != PROBE_SNAPSHOT_VERSION:
        raise ProbeSnapshotError(
            f"snapshot format {version!r}; expected {PROBE_SNAPSHOT_VERSION}; recapture"
        )
    if "constraint_facts" not in raw:
        raise ProbeSnapshotError("snapshot missing constraint_facts; recapture")
    return raw["constraint_facts"]


def production_snapshot_behavior(repo_root: Path) -> dict[str, Any]:
    old_rejected = False
    old_message = ""
    with tempfile.TemporaryDirectory() as directory:
        old = Path(directory) / "old.json"
        old.write_text(json.dumps({"snapshot_format_version": 1, "model_name": "old"}))
        try:
            load_extraction_snapshot(old)
        except SnapshotFormatError as error:
            old_rejected = True
            old_message = str(error)

    current_path = repo_root / "tests/fixtures/wi014_toy/extraction_snapshot.json"
    current_raw = json.loads(current_path.read_text())
    assert "constraint_facts" not in current_raw
    loaded = load_extraction_snapshot(current_path)
    return {
        "current_missing_constraint_facts_accepted": loaded is not None,
        "old_version_rejected": old_rejected,
        "old_version_message": old_message,
    }


def rejected_by_strict(payload: dict[str, Any]) -> str:
    try:
        load_strict_snapshot(canonical_bytes(payload))
    except ProbeSnapshotError as error:
        return str(error)
    raise AssertionError(f"strict loader unexpectedly accepted {payload}")


def main() -> int:
    home = Path(__file__).resolve().parent
    repo_root = home.parents[2]
    model_path = home / "model.sysml"

    live_a = load_live(model_path)
    live_b = load_live(model_path)
    live_bytes_a = canonical_bytes(live_a)
    live_bytes_b = canonical_bytes(live_b)
    assert live_bytes_a == live_bytes_b

    current_observed = set(live_a["current_concrete_paths"])
    current_missing = sorted(EXPECTED_CONCRETE_PATHS - current_observed)
    current_unexpected = sorted(current_observed - EXPECTED_CONCRETE_PATHS)
    assert current_missing == ["InstanceIndexProbe__root__plain_subtype"], current_missing
    assert current_unexpected == [], current_unexpected

    prototype_observed = set(live_a["complete_concrete_paths"])
    prototype_missing = sorted(EXPECTED_CONCRETE_PATHS - prototype_observed)
    prototype_unexpected = sorted(prototype_observed - EXPECTED_CONCRETE_PATHS)
    assert prototype_missing == [], prototype_missing
    assert prototype_unexpected == [], prototype_unexpected

    # The public downstream helper has no path source when there are no virtual calcs.
    assert find_instance_paths_for_partdef(OWNER_QN, [], {}) == []

    strict_payload = strict_snapshot(live_a)
    strict_bytes = canonical_bytes(strict_payload)
    replayed = load_strict_snapshot(strict_bytes)
    replayed_bytes = canonical_bytes(replayed)
    assert replayed_bytes == live_bytes_a
    assert [row["constraint_id"] for row in replayed["catalog"]] == [
        row["constraint_id"] for row in live_a["catalog"]
    ]

    production = production_snapshot_behavior(repo_root)
    assert production["old_version_rejected"] is True
    assert production["current_missing_constraint_facts_accepted"] is True

    result = {
        "calculation_usage_count": 0,
        "catalog_count": len(live_a["catalog"]),
        "expected_semantic_instance_count": len(EXPECTED_CONCRETE_PATHS),
        "instance_index": {
            "current": {
                "missing": current_missing,
                "observed_after_fixed_multiplicity": live_a["current_concrete_paths"],
                "raw_paths": live_a["current_raw_paths"],
                "unexpected": current_unexpected,
            },
            "subtype_closure_prototype": {
                "missing": prototype_missing,
                "observed_after_fixed_multiplicity": live_a["complete_concrete_paths"],
                "raw_paths": live_a["complete_raw_paths"],
                "unexpected": prototype_unexpected,
            },
        },
        "live_repeated_bytes_identical": live_bytes_a == live_bytes_b,
        "multiplicities": live_a["multiplicities"],
        "production_snapshot": production,
        "strict_prototype": {
            "catalog_ids": [row["constraint_id"] for row in replayed["catalog"]],
            "current_missing_facts_rejected": rejected_by_strict(
                {"snapshot_format_version": PROBE_SNAPSHOT_VERSION}
            ),
            "old_version_rejected": rejected_by_strict(
                {
                    "constraint_facts": live_a,
                    "snapshot_format_version": PROBE_SNAPSHOT_VERSION - 1,
                }
            ),
            "snapshot_replay_bytes_identical": replayed_bytes == live_bytes_a,
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
