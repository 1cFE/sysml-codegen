"""The station's model-family-spine gate: the tracked census matches the committed package.

Written for study-layer-to-codegen. ``integrate`` runs this file as gate 5, because the
station's ``pyproject.toml`` declares it under
``[tool.sysml-codegen.integrate.gates.model-family-spine]``. It re-derives the entry-point
census through the helper ``integrate`` itself uses, so the gate and the seam cannot disagree
about what a census is.
"""

import json
from pathlib import Path

from sysml_codegen.study import census

PROJECT = Path(__file__).resolve().parents[1]
PACKAGE = PROJECT / "pkg" / "station_study"


def test_the_tracked_census_is_the_committed_packages():
    tracked = json.loads((PROJECT / "census.json").read_text())
    contract = json.loads((PACKAGE / "contracts" / "model_contract.json").read_text())
    assert tracked["derived_against_semantic_fingerprint"] == contract["semantic_fingerprint"], (
        "model meaning moved, so census.json must be re-derived (PROVENANCE.md)"
    )
    assert tracked["entry_points"] == len(contract["parameters"])
    by_type = census.by_entry_type(PACKAGE)
    assert tracked["by_entry_type"] == {key: sorted(value) for key, value in by_type.items()}
