"""The two decision registers and the register-facing docs keep their conventions.

Split out of test_stop_parser_documentation_contract.py (REPO-CLEANUP Move C, 2026-08-25):
the manifest-bound legs retired with verification/, and these register-contract legs — the
only mechanical guard on the owner-verbatim 0003/0004 quotes and the register conventions —
stay, license-free, on an ordinary checkout.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRODUCT = ROOT / ".project/product"
ADR = ROOT / ".project/adr"
DIAGNOSTICS = {
    "SI_EVIDENCE_INCOMPLETE",
    "SI_TYPE_INVALID",
    "SI_INDEXED_SOURCE_UNSUPPORTED",
    "EXIT_POINT_TYPE_UNSUPPORTED",
}


def _read(relative: str) -> str:
    return (ROOT / relative).read_text()


def _frontmatter_value(text: str, field: str) -> str:
    match = re.search(rf"^{re.escape(field)}: (?P<value>.+)$", text, re.MULTILINE)
    assert match is not None, f"missing frontmatter field: {field}"
    return match.group("value")


def _product_ids_in(index: str) -> tuple[str, ...]:
    ids: list[str] = []
    for line in index.splitlines():
        match = re.match(r"^- (?P<id>[0-9]{4}) · ", line)
        if match is not None:
            ids.append(match.group("id"))
    assert ids, "product index contains no promise rows"
    assert len(ids) == len(set(ids)), "product index contains duplicate promise ids"
    return tuple(ids)


def _regenerate_product_index(tmp_path: Path) -> str:
    product = tmp_path / ".project/product"
    shutil.copytree(PRODUCT, product)
    subprocess.run(
        [str(ROOT / ".project/scripts/product.sh"), "index"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    return (product / "INDEX.md").read_text()


def test_every_indexed_promise_resolves_to_exactly_one_entry() -> None:
    for entry_id in _product_ids_in(_read(".project/product/INDEX.md")):
        assert len(list(PRODUCT.glob(f"{entry_id}-*.md"))) == 1


def test_product_index_is_a_faithful_regeneration(tmp_path: Path) -> None:
    assert _read(".project/product/INDEX.md") == _regenerate_product_index(tmp_path)


def test_no_document_claims_a_single_adr_home() -> None:
    convention_docs = (
        "CLAUDE.md",
        ".project/product/README.md",
    )
    for relative in convention_docs:
        text = _read(relative)
        assert "docs/architecture/modeling-assumptions.md" in text
        assert ".project/adr/" in text
        assert "two decision registers" in text.lower()

    # Pins the one single-home sentence that existed before the two-register ruling;
    # the positive assertions above are the guard on the convention itself.
    for relative in (*convention_docs, ".project/product/INDEX.md"):
        assert "there is no `docs/adr/` directory" not in _read(relative).lower()


def test_decision_register_boundary_is_discoverable() -> None:
    entries = list(ADR.glob("0001-*.md"))
    assert len(entries) == 1
    entry = entries[0].read_text()
    normalized_entry = " ".join(entry.split())
    assert 'provenance: "[OWNER]"' in entry
    assert "Who is bound by this decision" in normalized_entry
    assert "person writing the system's inputs" in normalized_entry
    assert "person changing the system itself" in normalized_entry
    assert "- 0001 · Route decisions by who they bind" in _read(
        ".project/adr/INDEX.md"
    )


def test_load_bearing_register_conventions_are_filed() -> None:
    entries = {
        _frontmatter_value(path.read_text(), "title"): path.read_text()
        for path in ADR.glob("[0-9][0-9][0-9][0-9]-*.md")
    }

    resolution = entries["Resolve generated index ids by sibling filename"]
    assert "exactly one" in resolution
    assert "<id>-*.md" in resolution
    assert "generated index" in resolution

    citations = entries["Cite decisions by register path"]
    assert "bare number" in citations
    assert "docs/architecture/modeling-assumptions.md ADR-009" in citations
    assert ".project/adr/" in citations


def test_every_product_promise_has_a_script_managed_check_stamp() -> None:
    for entry_id in _product_ids_in(_read(".project/product/INDEX.md")):
        entries = list(PRODUCT.glob(f"{entry_id}-*.md"))
        assert len(entries) == 1
        checked = _frontmatter_value(entries[0].read_text(), "checked")
        assert re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2} @ [0-9a-f]{7,40}", checked)


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


def test_dead_computed_attribute_classifier_and_its_golden_are_absent() -> None:
    retired = (
        "src/sysml_codegen/extraction/computed_attribute_extractor.py",
        "tests/conformance/test_computed_attribute_golden.py",
        "tests/conformance/test_silent_failure_d316.py",
        "tests/fixtures/golden/computed_attribute_golden.json",
    )
    # The expected-transitions record that narrated this retirement left with
    # verification/ (REPO-CLEANUP Move C); the absence pins above are the contract.
    assert all(not (ROOT / relative).exists() for relative in retired)


def test_backlog_and_product_records_preserve_force_and_current_status() -> None:
    backlog = _read(".project/backlog/BACKLOG.md")
    product = _read(".project/product/0003-no-workarounds-for-bad-models.md")
    product_identity = _read(".project/product/0004-product-identity-parse-walk-emit.md")
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
    assert "- 0003 · No workarounds to accept bad models" in index
    assert len(list(PRODUCT.glob("0003-*.md"))) == 1
    assert "Use a SysMLv2 parser to interpret the models" in product_identity
    assert "Walk the AST to reconstruct the math" in product_identity
    assert "Write the math into python using TEAx" in product_identity
    assert "- 0004 · What this product is: parse the models" in index
    assert len(list(PRODUCT.glob("0004-*.md"))) == 1


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

