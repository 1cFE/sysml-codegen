"""The shipped catalog carries the whole domain, and the join is gated before anything is written.

The catalog is what ships. A package whose catalog lost a carrier would claim coverage it
does not have, and nothing downstream would notice — so the join is re-asserted at the
fail-before-mutate boundary, by ``declaration_id`` and never by qualified name.

The mutations below act on the **graph**, not on snapshot bytes: a snapshot with a record
removed fails the document fingerprint long before any gate runs, so mutating bytes would
prove the fingerprint works rather than that the gate does.
"""

from __future__ import annotations

import dataclasses
import logging
from pathlib import Path

import pytest

from sysml_codegen.cli import GenerationConfig, _generate_package_from_graph
from sysml_codegen.elaboration import project
from sysml_codegen.elaboration.project import ProjectionError
from sysml_codegen.orchestration.elaborated_pipeline import (
    build_elaborated_pipeline,
    elaborate_model_paths,
)
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "constraint_domain_detached_owner"
# Every constraint here is owned by a `calc def`, so the graph has zero constraint nodes
# and a full domain — the combination that used to produce no catalog at all.
CALC_DEF_ONLY = FIXTURES_DIR / "constraint_domain_satisfy_calc_def"


def _config(tmp_path: Path) -> GenerationConfig:
    return GenerationConfig(
        output_path=tmp_path / "generated",
        models_path=FIXTURE,
        package_name="totality_probe",
        overwrite=True,
    )


def test_the_catalog_carries_every_domain_member():
    graph = elaborate_model_paths([FIXTURE])
    catalog = project(graph).constraint_catalog
    assert {row.declaration_id for row in catalog.usage_records} == {
        key.to_wire() for key in graph.constraint_usages
    }


def test_catf_mfe_d5_ships_all_sixty_five_rows():
    catalog = build_elaborated_pipeline([FIXTURES_DIR / "catf_mfe_d5"]).constraint_catalog
    assert len(catalog.usage_records) == 65
    assert sum(1 for row in catalog.usage_records if row.disposition_kind == "eligible") == 0
    assert sum(1 for row in catalog.usage_records if row.occurrence_count > 0) == 9


def test_rows_are_keyed_by_declaration_id_not_by_a_qualified_name_pair():
    catalog = build_elaborated_pipeline([FIXTURE]).constraint_catalog
    ids = [row.declaration_id for row in catalog.usage_records]
    assert len(ids) == len(set(ids))
    assert all(row.declaration_id for row in catalog.usage_records)


def test_a_calc_def_only_model_still_gets_a_catalog():
    """The `None` return keys on the DOMAIN being empty, never on expansion."""
    graph = elaborate_model_paths([CALC_DEF_ONLY])
    assert not graph.constraints
    catalog = project(graph).constraint_catalog
    assert catalog is not None
    assert catalog.usage_records
    assert not catalog.concrete_entries


def test_a_usage_only_catalog_fingerprints_deterministically():
    """A combination that had never existed: usage rows populated, everything else empty."""
    first = project(elaborate_model_paths([CALC_DEF_ONLY])).constraint_catalog
    second = project(elaborate_model_paths([CALC_DEF_ONLY])).constraint_catalog
    assert first.fingerprint == second.fingerprint
    assert not first.source_records
    assert not first.concrete_entries


def test_the_disposition_travels_onto_every_catalog_row():
    catalog = build_elaborated_pipeline([FIXTURE]).constraint_catalog
    by_name = {row.usage_qualified_name: row for row in catalog.usage_records}
    vacuous = by_name["constraint_domain_detached_owner::Detached::vacuous_gate"]
    assert (vacuous.disposition_kind, vacuous.disposition_reason) == (
        "non_reaching",
        "owner_has_no_occurrences",
    )
    assert vacuous.disposition_severity == "warning"
    assert vacuous.occurrence_count == 0


# --- Two layers, two subjects --------------------------------------------------------
#
# `graph.validate()` owns the DOMAIN: it runs on the live route, both decode paths, and
# the sealed context, so a graph-level break is refused before projection ever finishes.
# The preflight owns the CATALOG, which is the thing that actually ships and the only
# artifact a consumer reads. They are not redundant: a projection defect produces a broken
# catalog from a perfectly valid graph, and only the preflight is downstream of it.


def _graph_mutation_is_refused(mutate, expected: str) -> None:
    graph = elaborate_model_paths([FIXTURE])
    mutate(graph)
    with pytest.raises(ProjectionError, match=expected):
        project(graph)


def test_a_removed_disposition_is_refused_at_the_graph():
    def mutate(graph):
        key = next(iter(graph.constraint_usages))
        record = graph.constraint_usages[key]
        graph.constraint_usages[key] = dataclasses.replace(
            record,
            disposition=dataclasses.replace(record.disposition, reason="invented_later"),
        )

    _graph_mutation_is_refused(mutate, "reason 'invented_later' is outside kind")


def test_a_misjoined_occurrence_count_is_refused_at_the_graph():
    def mutate(graph):
        key = next(
            item
            for item, record in graph.constraint_usages.items()
            if record.occurrence_count > 0
        )
        graph.constraint_usages[key] = dataclasses.replace(
            graph.constraint_usages[key], occurrence_count=99
        )

    _graph_mutation_is_refused(mutate, "occurrence_count 99 disagrees with 1 nodes")


def test_an_orphaned_occurrence_node_is_refused_at_the_graph():
    def mutate(graph):
        node = next(iter(graph.constraints.values()))
        del graph.constraint_usages[node.declaration_id]

    _graph_mutation_is_refused(mutate, "occurrence node joins no usage record")


# --- The preflight: mutate the projected catalog, then generate ------------------------


def _catalog_mutation_is_refused(
    tmp_path: Path, caplog: pytest.LogCaptureFixture, mutate, expected: str
) -> None:
    """Generation refuses, says why, and leaves the output tree untouched.

    ``_generate_package_from_graph`` reports a refusal by logging it and returning False —
    that is its contract with the CLI, so the assertion is on the return value and the
    message, not on an escaping exception.
    """
    graph = build_elaborated_pipeline([FIXTURE])
    mutate(graph.constraint_catalog)
    output = tmp_path / "generated"

    with caplog.at_level(logging.ERROR):
        assert _generate_package_from_graph(graph, _config(tmp_path)) is False

    assert "constraint usage domain incomplete" in caplog.text
    assert expected in caplog.text
    assert not output.exists() or not any(output.iterdir())


def test_generation_refuses_a_catalog_row_with_no_disposition(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
):
    def mutate(catalog):
        catalog.usage_records[0].disposition_reason = "invented_later"

    _catalog_mutation_is_refused(tmp_path, caplog, mutate, "no disposition for")


def test_generation_refuses_a_duplicated_catalog_row(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
):
    def mutate(catalog):
        catalog.usage_records.append(catalog.usage_records[0].model_copy())

    _catalog_mutation_is_refused(tmp_path, caplog, mutate, "duplicate usage record")


def test_generation_refuses_an_occurrence_row_that_joins_no_domain_member(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
):
    def mutate(catalog):
        for row in catalog.usage_records:
            row.declaration_id = f"orphaned-{row.declaration_id}"

    _catalog_mutation_is_refused(tmp_path, caplog, mutate, "joins no domain member")


def test_generation_refuses_a_catalog_whose_counts_disagree(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
):
    def mutate(catalog):
        catalog.usage_records[0].occurrence_count = 99

    _catalog_mutation_is_refused(tmp_path, caplog, mutate, "occurrence_count 99 disagrees")


def test_the_refusal_names_the_usage_not_just_a_count(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
):
    graph = build_elaborated_pipeline([FIXTURE])
    row = graph.constraint_catalog.usage_records[0]
    row.occurrence_count = 99

    with caplog.at_level(logging.ERROR):
        assert _generate_package_from_graph(graph, _config(tmp_path)) is False

    assert row.usage_qualified_name in caplog.text
    assert row.declaration_id in caplog.text
