"""Exact staged source-admission policy and failure vocabulary."""

from __future__ import annotations

import os
import unicodedata
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

import sysml_codegen.extraction.source_manifest as source_manifest
from sysml_codegen.extraction.source_manifest import (
    PINNED_STANDARD_LIBRARY_COUNT,
    PINNED_STANDARD_LIBRARY_SHA256,
    PINNED_SYSIDE_VERSION,
    SourceAdmissionCode,
    SourceAdmissionError,
    SysideStandardLibraryDigestAdapter,
    admit_sources,
    validate_source_referent,
)


class _Model:
    def __init__(self, uris: list[str]) -> None:
        self._uris = uris

    def uris(self, _kind) -> list[str]:
        return self._uris


def _source(path: Path, text: str = "package admitted;") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def _parsed(admission) -> _Model:
    return _Model([str(path.resolve()) for path in admission.staged_files])


def test_roots_are_nonempty_ordered_path_values(tmp_path: Path) -> None:
    with pytest.raises(SourceAdmissionError) as empty:
        admit_sources([])
    assert empty.value.code is SourceAdmissionCode.SOURCE_ROOT_INVALID
    with pytest.raises(TypeError):
        admit_sources("not-a-sequence-of-paths")  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        admit_sources(["not-a-path"])  # type: ignore[list-item]
    with pytest.raises(SourceAdmissionError) as missing:
        admit_sources([tmp_path / "missing"])
    assert missing.value.code is SourceAdmissionCode.SOURCE_ROOT_INVALID


def test_exact_file_wins_then_deepest_directory_then_earliest_duplicate(
    tmp_path: Path,
) -> None:
    broad = tmp_path / "models"
    narrow = broad / "nested"
    source = _source(narrow / "model.sysml")

    with admit_sources([broad, narrow, source]) as admission:
        assert [root.ordinal for root in admission.roots] == [0, 1, 2]
        assert [root.kind for root in admission.roots] == ["directory", "directory", "file"]
        assert [row.referent for row in admission.files] == ["root-2/model.sysml"]

    with admit_sources([narrow, narrow]) as admission:
        assert [row.referent for row in admission.files] == ["root-0/model.sysml"]

    with admit_sources([broad, narrow]) as admission:
        assert [row.referent for row in admission.files] == ["root-1/model.sysml"]


def test_distinct_roots_and_supported_suffixes_have_sorted_portable_referents(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    _source(first / "space here" / "café#.sysml")
    _source(second / "types.kerml")
    _source(second / "ignored.SYSML")
    with admit_sources([first, second]) as admission:
        assert [row.referent for row in admission.files] == [
            "root-0/space%20here/caf%C3%A9%23.sysml",
            "root-1/types.kerml",
        ]


def test_file_root_requires_lower_case_supported_suffix(tmp_path: Path) -> None:
    source = _source(tmp_path / "model.SYSML")
    with pytest.raises(SourceAdmissionError) as caught:
        admit_sources([source])
    assert caught.value.code is SourceAdmissionCode.SOURCE_ROOT_INVALID


def test_utf8_failure_has_closed_read_code(tmp_path: Path) -> None:
    source = tmp_path / "model.sysml"
    source.write_bytes(b"\xff")
    with pytest.raises(SourceAdmissionError) as caught:
        admit_sources([source])
    assert caught.value.code is SourceAdmissionCode.SOURCE_READ_ERROR


def test_root_symlink_is_supported_and_descendant_links_are_not_followed(
    tmp_path: Path,
) -> None:
    real = tmp_path / "real"
    _source(real / "model.sysml")
    root_link = tmp_path / "visible-root"
    root_link.symlink_to(real, target_is_directory=True)
    with admit_sources([root_link]) as admission:
        assert admission.roots[0].display_path == root_link.absolute()
        assert admission.files[0].referent == "root-0/model.sysml"

    outside = _source(tmp_path / "outside.sysml")
    (real / "linked.sysml").symlink_to(outside)
    with pytest.raises(SourceAdmissionError) as caught:
        admit_sources([real])
    assert caught.value.code is SourceAdmissionCode.SOURCE_SYMLINK_ESCAPE

    (real / "linked.sysml").unlink()
    external_dir = tmp_path / "external"
    _source(external_dir / "hidden.sysml")
    (real / "linked-dir").symlink_to(external_dir, target_is_directory=True)
    with admit_sources([real]) as admission:
        assert [row.referent for row in admission.files] == ["root-0/model.sysml"]


def test_nfc_collisions_refuse_and_case_collisions_follow_platform_policy(
    tmp_path: Path,
) -> None:
    root = tmp_path / "models"
    composed = "café.sysml"
    decomposed = unicodedata.normalize("NFD", composed)
    if composed == decomposed:
        pytest.skip("filesystem test requires distinct NFC/NFD spellings")
    _source(root / composed)
    _source(root / decomposed)
    with pytest.raises(SourceAdmissionError) as caught:
        admit_sources([root])
    assert caught.value.code is SourceAdmissionCode.SOURCE_ALIAS_COLLISION

    for path in root.iterdir():
        path.unlink()
    _source(root / "Model.sysml")
    _source(root / "model.sysml")
    if os.path.normcase("Model.sysml") == os.path.normcase("model.sysml"):
        with pytest.raises(SourceAdmissionError) as case_caught:
            admit_sources([root])
        assert case_caught.value.code is SourceAdmissionCode.SOURCE_ALIAS_COLLISION
    else:
        with admit_sources([root]) as admission:
            assert len(admission.files) == 2


@pytest.mark.parametrize("mutation", ["add", "remove", "change"])
def test_membership_and_byte_changes_after_admission_are_source_races(
    tmp_path: Path, mutation: str
) -> None:
    root = tmp_path / "models"
    source = _source(root / "model.sysml")
    with admit_sources([root]) as admission:
        model = _parsed(admission)
        if mutation == "add":
            _source(root / "added.sysml")
        elif mutation == "remove":
            source.unlink()
        else:
            source.write_text("package changed;")
        with pytest.raises(SourceAdmissionError) as caught:
            admission.verify_after_parse(model)
        assert caught.value.code is SourceAdmissionCode.SOURCE_RACE


def test_identity_change_between_enumeration_and_read_is_a_source_race(
    tmp_path: Path, monkeypatch
) -> None:
    source = _source(tmp_path / "model.sysml")
    real_read = source_manifest._read_stable_file

    def replace_before_read(path: Path):
        replacement = path.with_suffix(".replacement")
        replacement.write_text(path.read_text())
        replacement.replace(path)
        return real_read(path)

    monkeypatch.setattr(source_manifest, "_read_stable_file", replace_before_read)
    with pytest.raises(SourceAdmissionError) as caught:
        admit_sources([source])
    assert caught.value.code is SourceAdmissionCode.SOURCE_RACE


def test_staged_mutation_and_uri_skew_have_distinct_codes(tmp_path: Path) -> None:
    source = _source(tmp_path / "model.sysml")
    with admit_sources([source]) as admission:
        staged = admission.staged_files[0]
        staged.chmod(0o600)
        staged.write_text("package changed;")
        with pytest.raises(SourceAdmissionError) as changed:
            admission.verify_after_parse(_parsed(admission))
        assert changed.value.code is SourceAdmissionCode.SOURCE_STAGE_MUTATED

    with admit_sources([source]) as admission:
        expected = [str(path.resolve()) for path in admission.staged_files]
        for uris in ([], expected + expected, expected + [str(tmp_path / "extra.sysml")]):
            with pytest.raises(SourceAdmissionError) as mismatch:
                admission.verify_after_parse(_Model(uris))
            assert mismatch.value.code is SourceAdmissionCode.SOURCE_ADMISSION_MISMATCH


def test_post_parse_failure_order_is_stage_then_uri_then_original(tmp_path: Path) -> None:
    root = tmp_path / "models"
    source = _source(root / "model.sysml")
    with admit_sources([root]) as admission:
        staged = admission.staged_files[0]
        staged.chmod(0o600)
        staged.write_text("package changed;")
        source.write_text("package original_changed;")
        with pytest.raises(SourceAdmissionError) as stage_first:
            admission.verify_after_parse(_Model([]))
        assert stage_first.value.code is SourceAdmissionCode.SOURCE_STAGE_MUTATED

    source.write_text("package admitted;")
    with admit_sources([root]) as admission:
        source.write_text("package original_changed;")
        with pytest.raises(SourceAdmissionError) as uri_second:
            admission.verify_after_parse(_Model([]))
        assert uri_second.value.code is SourceAdmissionCode.SOURCE_ADMISSION_MISMATCH

    source.write_text("package admitted;")
    with admit_sources([root]) as admission:
        source.write_text("package original_changed;")
        with pytest.raises(SourceAdmissionError) as original_third:
            admission.verify_after_parse(_parsed(admission))
        assert original_third.value.code is SourceAdmissionCode.SOURCE_RACE


def test_admission_records_are_immutable(tmp_path: Path) -> None:
    source = _source(tmp_path / "model.sysml")
    with admit_sources([source]) as admission:
        with pytest.raises(FrozenInstanceError):
            admission.files[0].referent = "changed"  # type: ignore[misc]


def test_standard_library_digest_matches_the_pinned_environment_twice() -> None:
    first = SysideStandardLibraryDigestAdapter.read()
    second = SysideStandardLibraryDigestAdapter.read()
    assert (first.document_count, first.sha256) == (
        PINNED_STANDARD_LIBRARY_COUNT,
        PINNED_STANDARD_LIBRARY_SHA256,
    )
    assert second == first


def test_unavailable_standard_library_has_a_closed_code(monkeypatch) -> None:
    import syside

    class _UnavailableEnvironment:
        @staticmethod
        def get_default():
            raise RuntimeError("unavailable")

    monkeypatch.setattr(syside, "Environment", _UnavailableEnvironment)
    with pytest.raises(SourceAdmissionError) as caught:
        SysideStandardLibraryDigestAdapter.read()
    assert caught.value.code is SourceAdmissionCode.SOURCE_STANDARD_LIBRARY_UNAVAILABLE


def test_failure_code_vocabulary_is_closed() -> None:
    assert {code.value for code in SourceAdmissionCode} == {
        "SOURCE_ROOT_INVALID",
        "SOURCE_ALIAS_COLLISION",
        "SOURCE_SYMLINK_ESCAPE",
        "SOURCE_READ_ERROR",
        "SOURCE_RACE",
        "SOURCE_STAGE_MUTATED",
        "SOURCE_ADMISSION_MISMATCH",
        "SOURCE_STANDARD_LIBRARY_UNAVAILABLE",
    }


def test_pinned_syside_version_matches_the_running_environment() -> None:
    import syside

    assert syside.__version__ == PINNED_SYSIDE_VERSION


@pytest.mark.parametrize(
    "referent",
    [
        "root-0/model.sysml",
        "root-12/nested/deep/types.kerml",
        "root-0/space%20here/caf%C3%A9%23.sysml",
    ],
)
def test_canonical_referents_round_trip(referent: str) -> None:
    assert validate_source_referent(referent) == referent


@pytest.mark.parametrize(
    "referent",
    [
        "model.sysml",
        "/absolute/model.sysml",
        "root-00/model.sysml",
        "root-0/model.SYSML",
        "root-0/model.txt",
        "root-0//model.sysml",
        "root-0/../model.sysml",
        "root-0/space here/model.sysml",
        "root-0/",
        "root-x/model.sysml",
    ],
)
def test_non_canonical_referents_are_refused(referent: str) -> None:
    with pytest.raises(ValueError, match="referent"):
        validate_source_referent(referent)
