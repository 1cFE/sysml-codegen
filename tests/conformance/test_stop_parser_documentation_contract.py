"""Public docs and project records describe the exact semantic route that shipped."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from verification import capture_baseline

ROOT = Path(__file__).resolve().parents[2]
TRANSITIONS = {
    "A1",
    "A2",
    "A3",
    "A4",
    "A5",
    "A5a",
    "A5b",
    "A6",
    "B1-B5",
    "B6/B7",
    "B8",
    "B9",
    "B10",
}
DIAGNOSTICS = {
    "SI_EVIDENCE_INCOMPLETE",
    "SI_TYPE_INVALID",
    "SI_INDEXED_SOURCE_UNSUPPORTED",
    "EXIT_POINT_TYPE_UNSUPPORTED",
}


def _read(relative: str) -> str:
    return (ROOT / relative).read_text()


def test_architecture_docs_name_one_owner_walk_and_exact_evidence_boundary() -> None:
    overview = _read("docs/architecture/overview.md")
    pipeline = _read("docs/architecture/reference/00-pipeline-overview.md")
    extraction = _read("docs/architecture/reference/01-extraction.md")
    dispatch = _read("docs/architecture/reference/19-ast-dispatch-invariant.md")

    for text in (overview, pipeline):
        assert "ContainmentAddress" in text
        assert "OccurrenceIndex" in text
        assert "calculation-output producer index" in text
        assert "tests/conformance/test_occurrence_domain_derivation.py" in text
        assert "tests/conformance/test_occurrence_calc_domain_derivation.py" in text
    assert "elaborate_loaded_extractor" in extraction
    assert "SemanticEvidenceError" in extraction
    assert "SI_EVIDENCE_INCOMPLETE" in extraction
    assert "tests/conformance/test_expression_evidence_integrity.py" in extraction
    assert "mapped metatype" in dispatch
    assert "class-name dispatch" in dispatch
    assert "SI_INDEXED_SOURCE_UNSUPPORTED" in dispatch


def test_exit_point_contract_is_refuse_before_mutate_everywhere() -> None:
    registry = _read("docs/architecture/reference/20-module-registry-generation.md")
    matrix = _read("docs/architecture/verification-matrix.md")

    req_row = next(line for line in registry.splitlines() if "REQ-REG-09" in line)
    assert "EXIT_POINT_TYPE_UNSUPPORTED" in req_row
    assert "before output mutation" in req_row
    assert all(
        field in req_row
        for field in ("type token", "module", "output", "file:line", "status 1")
    )
    matrix_row = next(line for line in matrix.splitlines() if "REQ-REG-09" in line)
    assert "tests/conformance/test_generation_exit_type_preflight.py" in matrix_row
    assert "PASS" in matrix_row
    assert "warn" not in matrix_row.lower()


def test_diagnostic_reference_assigns_owner_and_refusal_stage() -> None:
    reference = _read("docs/architecture/reference/30-diagnostic-severity.md")
    for diagnostic in DIAGNOSTICS:
        row = next(line for line in reference.splitlines() if f"`{diagnostic}`" in line)
        assert "owner" in row.lower()
        assert "stage" in row.lower()


def test_transition_record_is_total_and_hashed() -> None:
    transitions = _read("verification/expected-transitions.md")
    rows = {
        match.group("id"): match.groupdict()
        for match in re.finditer(
            r"^\| (?P<id>A5[ab]|A[1-6]|B1-B5|B6/B7|B8|B9|B10) "
            r"\| `(?P<old>[0-9a-f]{64})` \| `(?P<new>[0-9a-f]{64})` "
            r"\| (?P<difference>[^|]+) \| `(?P<test>[^`]+)` "
            r"\| `(?P<commit>[0-9a-f]{40})` \|$",
            transitions,
            re.MULTILINE,
        )
    }
    assert set(rows) == TRANSITIONS
    for row in rows.values():
        old_behavior, new_behavior = row["difference"].strip().split(" -> ", maxsplit=1)
        assert hashlib.sha256(old_behavior.encode()).hexdigest() == row["old"]
        assert hashlib.sha256(new_behavior.encode()).hexdigest() == row["new"]
    assert "Maintained-output result: byte-identical" in transitions
    assert "pre-change-baseline.json" in transitions


def test_every_transition_test_citation_resolves_to_a_retained_file() -> None:
    from verification.artifact_sources import agentic_source_root

    transitions = _read("verification/expected-transitions.md")
    citations = re.findall(
        r"^\| (?:A5[ab]|A[1-6]|B1-B5|B6/B7|B8|B9|B10) .*?\| `([^`]+)` \| `[0-9a-f]{40}` \|$",
        transitions,
        re.MULTILINE,
    )
    assert len(citations) == len(TRANSITIONS)
    agentic_root: Path | None = None
    for cell in citations:
        for citation in cell.split("; "):
            file_name = citation.split("::", 1)[0]
            if file_name.startswith("agentic-mbse/"):
                if agentic_root is None:
                    agentic_root = agentic_source_root(ROOT)
                path = agentic_root / file_name.removeprefix("agentic-mbse/")
            else:
                path = ROOT / file_name
            assert path.is_file(), citation


def test_probe_inventory_and_transitioned_batch_are_separate_contracts() -> None:
    manifest = json.loads(_read("verification/fixture-manifest.json"))

    capture_baseline.validate_manifest(manifest)
    transitioned = capture_baseline.validate_current_batch()

    assert transitioned == {
        "path": "tests/fixtures/v6_recapture_batch/batch.json",
        "frozen_p_seed": "52a03cd2d0a9fdd340b60b16cea79a5b72234b08",
        "frozen_sha256": "bd7bf245e3ca3923b9b5d41db97861c9fcdf64435e768d48a2d7027eb52d9288",
        "current_sha256": "7f9269781a8938308715229c5be00855490e82b7e54f9cb90939195e3aeefa40",
        "captured": 14,
        "refused": 23,
    }


def test_post_change_output_diff_has_only_named_metadata_and_a_b_rows() -> None:
    assert capture_baseline.validate_output_transitions() == {
        "metadata_only_snapshots": 23,
        "golden_rows": [
            "deep_cross_scope_probe::DeepCrossScopeProducer::'Monitoring Station'::station_output",
            "ife_plant::IfePlantSubsystems::radial_build::magnet_volume_total",
        ],
        "batch_record_transitions": ["deep_cross_scope_probe", "plant_value_shapes"],
        "maintained_current_snapshots": 22,
    }


def test_dead_computed_attribute_classifier_and_its_golden_are_absent() -> None:
    retired = (
        "src/sysml_codegen/extraction/computed_attribute_extractor.py",
        "tests/conformance/test_computed_attribute_golden.py",
        "tests/conformance/test_silent_failure_d316.py",
        "tests/fixtures/golden/computed_attribute_golden.json",
    )
    assert all(not (ROOT / relative).exists() for relative in retired)
    assert "classifier and its golden were retired" in _read(
        "verification/expected-transitions.md"
    )


def test_backlog_and_product_records_preserve_force_and_current_status() -> None:
    backlog = _read(".project/backlog/BACKLOG.md")
    product = _read(".project/product/P-003-no-workarounds-for-bad-models.md")
    product_identity = _read(".project/product/P-004-product-identity-parse-walk-emit.md")
    index = _read(".project/product/INDEX.md")
    owner_quote = (
        "> we do NOT create workarounds to accept bad models -- we follow what KerML, SysMLv2 and "
        "SysIDE\n> support"
    )

    assert "[INDEXED-ELEMENT-EXPRESSION-SUPPORT]" in backlog
    assert "[OUTPUT-ALIAS-DUPLICATE-SOURCE-SILENCE]" in backlog
    lines = backlog.splitlines()
    for tag in (
        "[INDEXED-ELEMENT-EXPRESSION-SUPPORT]",
        "[OUTPUT-ALIAS-DUPLICATE-SOURCE-SILENCE]",
    ):
        # The close rewrapped the bold headings, so the provenance grade sits on a
        # continuation line; grade and settledness are judged on the whole entry block.
        start = next(index for index, line in enumerate(lines) if tag in line)
        block_lines = [lines[start]]
        for line in lines[start + 1 :]:
            if not line.strip() or line.startswith("- **["):
                break
            block_lines.append(line)
        block = "\n".join(block_lines)
        assert "AGENT" in block
        assert "settled" not in block.lower()
    assert owner_quote in product
    assert "every definition-owned lineage miss" in product
    assert "P-003-no-workarounds-for-bad-models.md" in index
    assert "Use a SysMLv2 parser to interpret the models" in product_identity
    assert "Walk the AST to reconstruct the math" in product_identity
    assert "Write the math into python using TEAx" in product_identity
    assert "P-004-product-identity-parse-walk-emit.md" in index


def test_status_records_owner_close_and_satisfied_downstream_dependency() -> None:
    current = _read(".project/CURRENT_WORK.md")
    epic = _read(".project/backlog/epic_elaborate_first_architecture.md")
    assert "stop-reinventing-the-parser CLOSED by owner direction" in current
    assert ".project/completed/20260819_stop-reinventing-the-parser/" in current
    assert "Bounded predecessor closed 2026-08-19 by owner direction" in epic
    assert "predecessor dependency is satisfied" in epic
    assert "8a758e9240707b58fe32a509c3b509941ca4fa01" in epic
    assert "924eadfd12f39401a6ea8e578b405d4ba8833b51" in epic
    for text in (current, epic):
        # The record keeps the audit history honest: rev-3 said Needs Work, and the
        # diagnostic follow-up was transferred, not shipped here.
        assert "Needs Work" in text
        assert "[DIAGNOSTIC-PROVENANCE-BY-CONSTRUCTION]" in text


def test_final_ledger_path_stays_reserved_for_the_evidence_commit() -> None:
    assert not (ROOT / "verification/reconciliation-ledger.md").exists()
