"""Canonical logical source-referent shape at the v6 owner."""

from __future__ import annotations

import pytest

from sysml_codegen.snapshot.source_manifest import validate_source_referent


def test_canonical_v6_referent_is_accepted() -> None:
    assert (
        validate_source_referent("root-0/space%20here/caf%C3%A9.sysml")
        == "root-0/space%20here/caf%C3%A9.sysml"
    )


@pytest.mark.parametrize(
    "referent",
    [
        "/home/someone/checkout/library/geometry.sysml",
        "library/geometry.sysml",
        "root-00/model.sysml",
        "root-0/%2e%2e/model.sysml",
        "root-0/UPPER.SYSML",
    ],
)
def test_noncanonical_referent_is_rejected(referent: str) -> None:
    with pytest.raises(ValueError, match="canonical source referent"):
        validate_source_referent(referent)
