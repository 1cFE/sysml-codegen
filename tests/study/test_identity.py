"""The identity recipe, its canonical text, and the gate that recomputes it.

Moved from fusion-tea ``tests/study/test_identity.py`` at ``b06585709`` and re-pointed at the
neutral station fixture, read in place as its own project. The tests pin the designed bytes of
``effective-executable-fingerprint/v1``: one ``adapter <path> <sha256>`` line per declared
source. Each refusal is one ``identity``'s module docstring documents.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

import jsonschema
import pytest

from sysml_codegen.study import common, identity
from sysml_codegen.study import manifest as manifest_mod
from tests.study.conftest import STATION_PACKAGE

SEALED = "ab" * 32
MOD = [("inputs/x.json", "11" * 32)]
SRC = [("a/route_adapter.py", "22" * 32)]

#: An effective identity over the station: two package files a route may modify, and one
#: project file it declares as a source.
GLUE_FILES = ["inputs/station_params.json", "pipelines/pipeline.yaml"]
ADAPTER_SOURCE = "studies/oracle_entry.py"


def test_the_recipe_canonical_text_is_exactly_this() -> None:
    assert identity.canonical_text(SEALED, MOD, SRC) == (
        "effective-executable-fingerprint/v1\n"
        "sealed " + "ab" * 32 + "\n"
        "modified inputs/x.json " + "11" * 32 + "\n"
        "adapter a/route_adapter.py " + "22" * 32 + "\n"
    )


def test_the_digest_is_sha256_of_that_text() -> None:
    text = identity.canonical_text(SEALED, MOD, SRC)
    assert identity.effective_digest(SEALED, MOD, SRC) == (
        hashlib.sha256(text.encode("utf-8")).hexdigest()
    )


def test_the_canonical_text_sorts_by_path_not_by_argument_order() -> None:
    """Two agents listing the same files in different orders must agree."""
    a = [("z/b.py", "33" * 32), ("a/a.py", "44" * 32)]
    assert identity.canonical_text(SEALED, MOD, a) == identity.canonical_text(
        SEALED, MOD, list(reversed(a))
    )


def test_adapter_source_digest_is_over_the_sorted_adapter_lines_alone() -> None:
    """A record snapshot takes one sha256 while a route declares several sources."""
    sources = [("z/b.py", "33" * 32), ("a/a.py", "44" * 32)]
    expected = hashlib.sha256(
        ("adapter a/a.py " + "44" * 32 + "\nadapter z/b.py " + "33" * 32 + "\n").encode("utf-8")
    ).hexdigest()
    assert identity.adapter_source_digest(sources) == expected
    assert identity.adapter_source_digest(list(reversed(sources))) == expected


def test_touching_any_of_the_three_inputs_changes_the_digest() -> None:
    base = identity.effective_digest(SEALED, MOD, SRC)
    assert identity.effective_digest("cd" * 32, MOD, SRC) != base
    assert identity.effective_digest(SEALED, [("inputs/x.json", "99" * 32)], SRC) != base
    assert identity.effective_digest(SEALED, MOD, [("a/route_adapter.py", "99" * 32)]) != base


# ------------------------------------------------------------------ the document


def test_the_sealed_kind_reduces_to_the_sealed_fingerprint(station_project: Path) -> None:
    doc = identity.build_sealed(package_name="ignored", package_root=STATION_PACKAGE)
    sealed = manifest_mod.read_executable_fingerprint(STATION_PACKAGE)
    assert doc["identity"]["kind"] == "sealed"
    assert doc["identity"]["digest"] == sealed
    assert doc["identity"]["allowed_modified_files"] == []
    assert doc["identity"]["adapter_sources"] == []
    # The sealed case is the degenerate member of the same gate, not a special case.
    assert identity.recompute(doc, STATION_PACKAGE) == sealed


def test_an_effective_identity_that_bypasses_nothing_is_refused() -> None:
    """An empty allowed-modified set is the sealed case wearing the wrong label."""
    with pytest.raises(identity.IdentityError) as exc:
        identity.build_effective(
            package_name="p", package_root=".", sealed_fingerprint=SEALED,
            allowed_modified=[], adapter_sources=SRC, glue_ledger=[],
        )
    assert "sealed" in str(exc.value)


def test_the_documents_validate_against_the_committed_schema(
    station_project: Path, load_schema: Callable[[str], dict[str, Any]]
) -> None:
    schema = load_schema("package_identity.v1")
    jsonschema.validate(
        identity.build_sealed(package_name="p", package_root=STATION_PACKAGE), schema
    )
    jsonschema.validate(
        identity.build_effective(
            package_name="p", package_root=STATION_PACKAGE, sealed_fingerprint=SEALED,
            allowed_modified=MOD, adapter_sources=SRC,
            glue_ledger=[{"rung": "g3", "keys": ["k"], "supplies": "a value",
                          "independently_verified": False, "note": "n"}],
        ),
        schema,
    )


def test_the_document_is_deterministic_across_working_directories(
    station_project: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Paths come from the project root, never from the caller's working directory."""
    first = identity.build_sealed(package_name="p", package_root=STATION_PACKAGE)
    monkeypatch.chdir(tmp_path)
    assert identity.build_sealed(package_name="p", package_root=STATION_PACKAGE) == first
    assert first["package"]["path"] == "pkg/station_study"


# ---------------------------------------------------------------------- the gate


def _effective_doc(
    package_root: Path, modified_rel: list[str], source_rel: list[str]
) -> dict[str, Any]:
    document: dict[str, Any] = identity.build_effective(
        package_name=manifest_mod.read_package_name(package_root),
        package_root=package_root,
        sealed_fingerprint=manifest_mod.read_executable_fingerprint(package_root),
        allowed_modified=[(r, manifest_mod.sha256_file(package_root / r)) for r in modified_rel],
        adapter_sources=[
            (r, manifest_mod.sha256_file(manifest_mod.repo_root() / r)) for r in source_rel
        ],
        glue_ledger=[],
    )
    return document


def _package_copy(tmp_path: Path) -> Path:
    copy = tmp_path / "pkg"
    shutil.copytree(STATION_PACKAGE, copy, ignore=shutil.ignore_patterns("__pycache__"))
    return copy


def test_the_gate_passes_on_the_station_package(station_project: Path) -> None:
    doc = _effective_doc(STATION_PACKAGE, GLUE_FILES, [ADAPTER_SOURCE])
    assert identity.assert_matches(doc, STATION_PACKAGE) == doc["identity"]["digest"]


def test_a_recompute_mismatch_fails_naming_both_values(station_project: Path) -> None:
    doc = _effective_doc(STATION_PACKAGE, GLUE_FILES, [ADAPTER_SOURCE])
    declared = doc["identity"]["digest"]
    doc["identity"]["digest"] = "0" * 64
    with pytest.raises(identity.IdentityError) as exc:
        identity.assert_matches(doc, STATION_PACKAGE)
    assert "0" * 64 in str(exc.value) and declared in str(exc.value)


def test_a_missing_declared_file_fails_naming_it(station_project: Path) -> None:
    """A file that has moved or vanished is a failure naming it (``identity.recompute``)."""
    doc = _effective_doc(STATION_PACKAGE, GLUE_FILES, [ADAPTER_SOURCE])
    doc["identity"]["adapter_sources"].append({"path": "no/such/file.py", "sha256": "0" * 64})
    with pytest.raises(identity.IdentityError) as exc:
        identity.recompute(doc, STATION_PACKAGE)
    assert "no/such/file.py" in str(exc.value)


def test_the_gate_recomputes_and_does_not_trust(station_project: Path, tmp_path: Path) -> None:
    """A route could assert any digest. The gate reads the bytes instead."""
    copy = _package_copy(tmp_path)
    doc = _effective_doc(copy, GLUE_FILES, [ADAPTER_SOURCE])
    identity.assert_matches(doc, copy)
    target = copy / "inputs" / "station_params.json"  # an allowed-modified file
    target.write_text(target.read_text().replace("}", ', "x": 1}', 1))
    with pytest.raises(identity.IdentityError) as exc:
        identity.assert_matches(doc, copy)
    assert "digest mismatch" in str(exc.value)


def test_a_sealed_artifact_outside_the_allowed_set_fails_naming_the_file(
    station_project: Path, tmp_path: Path
) -> None:
    """The exception may not widen: every sealed artifact outside the allowed set must
    still match (``identity.assert_seal_outside_allowed_set``)."""
    copy = _package_copy(tmp_path)
    doc = _effective_doc(copy, GLUE_FILES, [ADAPTER_SOURCE])
    target = copy / "contracts" / "model_contract.json"  # sealed, NOT in the allowed set
    target.write_text(target.read_text().replace("}", ', "x": 1}', 1))
    with pytest.raises(identity.IdentityError) as exc:
        identity.assert_seal_outside_allowed_set(doc, copy)
    assert "contracts/model_contract.json" in str(exc.value)


def test_an_allowed_modified_file_that_is_not_a_sealed_artifact_is_refused(
    station_project: Path,
) -> None:
    doc = _effective_doc(STATION_PACKAGE, GLUE_FILES, [ADAPTER_SOURCE])
    doc["identity"]["allowed_modified_files"].append(
        {"path": "not/sealed.json", "sha256": "0" * 64}
    )
    with pytest.raises(identity.IdentityError) as exc:
        identity.assert_seal_outside_allowed_set(doc, STATION_PACKAGE)
    assert "not/sealed.json" in str(exc.value)


# ------------------------------------------------------------------- load/write


def test_load_refuses_a_wrong_schema_version(station_project: Path, tmp_path: Path) -> None:
    doc = identity.build_sealed(package_name="p", package_root=STATION_PACKAGE)
    doc["schema_version"] = "study-package-identity/v2"
    path = common.write_document(doc, tmp_path / "package_identity.json")
    with pytest.raises(identity.IdentityError) as exc:
        identity.load(path)
    assert "v2" in str(exc.value)


@pytest.mark.parametrize(
    "mutate,needle",
    [
        (lambda d: d["identity"].pop("digest"), "digest"),
        (lambda d: d["identity"].update(kind="other"), "kind"),
        (lambda d: d["identity"].update(recipe="nope/v1"), "recipe"),
        (lambda d: d["identity"].update(allowed_modified_files={}), "allowed_modified_files"),
        (lambda d: d.update(glue_ledger={}), "glue_ledger"),
    ],
)
def test_load_refuses_a_malformed_document(
    mutate: Callable[[dict[str, Any]], object], needle: str, station_project: Path,
    tmp_path: Path,
) -> None:
    doc = identity.build_sealed(package_name="p", package_root=STATION_PACKAGE)
    mutate(doc)
    path = common.write_document(doc, tmp_path / "package_identity.json")
    with pytest.raises(identity.IdentityError) as exc:
        identity.load(path)
    assert needle in str(exc.value)


def test_a_written_document_round_trips_and_its_digest_is_stable(
    station_project: Path, tmp_path: Path
) -> None:
    doc = identity.build_sealed(package_name="p", package_root=STATION_PACKAGE)
    path = common.write_document(doc, tmp_path / "results" / "package_identity.json")
    assert identity.load(path) == doc
    assert json.loads(path.read_text()) == doc
    assert common.digest_of_document(doc) == hashlib.sha256(path.read_bytes()).hexdigest()
