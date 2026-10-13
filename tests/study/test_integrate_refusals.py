"""The executed store resolves from the baseline result, or the seam raises.

The two store-resolution tests of fusion-tea ``tests/study/test_integrate_refusals.py`` at
``b06585709``. They are package-agnostic, so they moved unchanged apart from the import. The
station's gate refusals are in ``test_integrate_declared.py`` and
``tests/execution/test_study_integrate.py``.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sysml_codegen.study import integrate
from sysml_codegen.study import manifest as manifest_mod


def test_the_baseline_store_resolves_from_the_baseline_result(tmp_path: Path) -> None:
    """The route deposits two documents and names the store in one of them; it returns
    neither the store nor its path, so both spellings of ``store_id`` are resolved."""
    out = tmp_path / "out"
    work = out / "_work"
    work.mkdir(parents=True)
    (work / "some-study.db").write_bytes(b"")
    document = out / "baseline_result.json"

    document.write_text(json.dumps({"executed_under": {"store_id": "some-study.db"}}))
    assert integrate.resolve_store(document, out) == work / "some-study.db"

    inside = manifest_mod.repo_relative_posix(work / "some-study.db")
    document.write_text(json.dumps({"executed_under": {"store_id": inside}}))
    assert integrate.resolve_store(document, out) == work / "some-study.db"


def test_a_store_that_resolves_to_nothing_raises_rather_than_being_guessed(
    tmp_path: Path,
) -> None:
    out = tmp_path / "out"
    out.mkdir()
    document = out / "baseline_result.json"
    document.write_text(json.dumps({"executed_under": {"store_id": "no-such-store.db"}}))
    with pytest.raises(Exception, match="resolves to no file"):
        integrate.resolve_store(document, out)
