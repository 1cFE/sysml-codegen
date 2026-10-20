"""agentic-mbse's occurrence port gives codegen's own answer (Item 2a D6, ADR 0001 invariant 6).

The screen decides instantiation-dependent rules from ``extract_occurrence_structure``, a port
of codegen's occurrence logic. This test holds the port to codegen live, on the same loaded
model: the 34-model parity seed (``tests/fixtures/subset_profile_occurrence_seed/``), the
37 corpus fixtures that ``tests/fixtures/v6_recapture_batch/batch.json`` lists, and every
conformance case in either home. A case with no instantiation compares two empty summaries,
which is cheap and keeps the set total. A missing input fails by name rather than shrinking
the set.

The companion test drops one occurrence index inside codegen's ``_multiplicity_indices`` and
requires the comparison to see it, so a normalizer that renders both sides alike regardless of
input cannot pass.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from agentic_mbse.sysml.occurrence_extraction import extract_occurrence_structure
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.elaboration import occurrence as cg_occurrence
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.subset_profile import cases
from tests.helpers.subset_profile.occurrence_parity import (
    differences,
    normalize_agentic,
    normalize_codegen,
)

pytestmark = requires_license

SEED_DIR = FIXTURES_DIR / "subset_profile_occurrence_seed"
SEED = sorted(d.name for d in SEED_DIR.iterdir() if d.is_dir())
CORPUS = json.loads((FIXTURES_DIR / "v6_recapture_batch" / "batch.json").read_text())["fixtures"]
#: A seed case whose model expands one usage to two occurrences.
MUTATION_CASE = "es004_admitted_exact_redefinition"


def _roots() -> list[tuple[str, Path]]:
    return (
        [(f"seed/{name}", SEED_DIR / name) for name in SEED]
        + [(f"corpus/{name}", FIXTURES_DIR / name) for name in CORPUS]
        + [(f"case/{a.case_id}", cases.model_root(a)) for a in cases.all_answers()]
    )


def _load(root: Path):
    if not root.is_dir():
        pytest.fail(f"parity input {root} is missing")
    paths = sorted(root.glob("*.sysml")) if root.parent == SEED_DIR else [root]
    # Validation errors do not stop the comparison: some seed models are invalid on purpose
    # (f1_invalid_redefinition_family), and both sides answer for whatever loads.
    model, _diagnostics = SysideAdapter.load_model(paths)
    return model


def test_the_seed_is_the_planned_set():
    """Item 1's 11 F1 edge fixtures, 22 prototype fixtures and P-6's effective-declaration case."""
    assert len(SEED) == 34
    assert sum(name.startswith("f1_") for name in SEED) == 12
    assert "f1_effective_declaration_slot" in SEED
    assert len(CORPUS) == 37


@pytest.mark.parametrize(("label", "root"), _roots(), ids=[label for label, _ in _roots()])
def test_agentic_summary_equals_codegen_index(label, root):
    model = _load(root)
    codegen = normalize_codegen(model)
    agentic = normalize_agentic(extract_occurrence_structure(model))
    assert codegen == agentic, "\n".join(differences(codegen, agentic))


def test_a_dropped_occurrence_index_is_seen(monkeypatch):
    model = _load(SEED_DIR / MUTATION_CASE)
    agentic = normalize_agentic(extract_occurrence_structure(model))
    assert normalize_codegen(model) == agentic
    multiplicity_indices = cg_occurrence._multiplicity_indices

    def drop_last_index(usage, **kwargs):
        indices = multiplicity_indices(usage, **kwargs)
        return indices[:-1] if len(indices) > 1 else indices

    monkeypatch.setattr(cg_occurrence, "_multiplicity_indices", drop_last_index)
    assert differences(normalize_codegen(model), agentic)
