"""A D-5 variant differs from its original by the rename and by nothing else.

The variants exist because the exact route refuses a binding that resolves to its own formal,
and the ratified migration for a real model is renaming. The risk in authoring one by hand is
not the rename — it is everything else that can ride along in a large diff: a reformat, a
dropped comment, a nudged literal. A reviewer reading two thousand lines will not catch it.

So the proof is mechanical and reversible: strip the ``_in`` suffix from the renamed formals
and the variant must reproduce its original **byte for byte, file for file**. That holds only
if the rename was the sole edit.

License-free by construction — it is a text comparison of committed fixtures.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import make_d5_variant as d5  # noqa: E402

#: Every variant, with the original it was derived from.
VARIANTS = [("catf_mfe_model", "catf_mfe_d5"), ("solar_battery_model", "solar_battery_d5")]


@pytest.mark.parametrize(("original", "variant"), VARIANTS)
def test_stripping_the_rename_reproduces_the_original_byte_for_byte(
    original: str, variant: str
) -> None:
    assert d5.strip_check(original, variant, d5.refused_formals(original)) == []


@pytest.mark.parametrize(("original", "variant"), VARIANTS)
def test_the_variant_renames_every_formal_the_route_refused(
    original: str, variant: str
) -> None:
    """No partial migration: a formal left un-renamed would still refuse, silently."""
    text = "".join(
        path.read_text() for path in sorted((d5.FIXTURES / variant).rglob("*.sysml"))
    )
    for formal in d5.refused_formals(original):
        assert f"{formal}_in" in text, f"{variant}: {formal} was not renamed"


@pytest.mark.parametrize(("original", "variant"), VARIANTS)
def test_a_variant_carries_no_snapshot_of_its_own(original: str, variant: str) -> None:
    """A variant is not a corpus fixture and must not come to look like one."""
    for name in d5.NOT_INHERITED:
        assert not (d5.FIXTURES / variant / name).exists()


@pytest.mark.parametrize(("original", "variant"), VARIANTS)
def test_the_original_is_untouched_by_its_variant(original: str, variant: str) -> None:
    """The corpus guarantee: the refused original still carries the refused shape."""
    text = "".join(
        path.read_text() for path in sorted((d5.FIXTURES / original).rglob("*.sysml"))
    )
    for formal in d5.refused_formals(original):
        assert f"{formal}_in" not in text, f"{original} was edited in place"
    assert (d5.FIXTURES / original / "extraction_snapshot.json").is_file()


def test_a_refusal_code_outside_the_rename_recipe_stops_rather_than_guesses() -> None:
    """The recipe addresses SI_SELF_BINDING. Anything else is a finding, not a variant."""
    import json

    manifest = json.loads(d5.BATCH_MANIFEST.read_text())
    for original, _variant in VARIANTS:
        codes = set(manifest["records"][original]["codes"])
        assert codes == {"SI_SELF_BINDING"}, (
            f"{original} carries {sorted(codes - {'SI_SELF_BINDING'})}, which the D-5 "
            "recipe does not address — make_d5_variant.py must stop rather than emit"
        )
