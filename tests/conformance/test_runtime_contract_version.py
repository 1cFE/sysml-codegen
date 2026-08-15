"""Item 3: RUNTIME_CONTRACT_VERSION is a deliberately-bumped pin with a re-vendor obligation.

Mirrors `test_catalog_schema_version.py`. Cross-repo agreement rests on this constant plus
manual re-vendoring — B3 forbids TEAx importing this repo, so no automated cross-repo check
is possible from here. The TEAx side owns `ACCEPTED_RUNTIME_CONTRACT_VERSIONS`.

**The obligation this pin carries.** Moving the token means the report shape a runtime reads
changed in a breaking way, and TEAx's vendored accepted set must be *replaced* — not extended
— in the same landing, so a package built against the old shape fails at seal verification
before any report is read.
"""

from __future__ import annotations

from sysml_codegen.contracts.versions import (
    CATALOG_SCHEMA_VERSION,
    RUNTIME_CONTRACT_VERSION,
)


def test_runtime_contract_version_is_the_reviewed_pin():
    # 2.0.0 renamed `assessed_count` to `assessed_entry_count`, added the required `coverage`
    # block, and replaced the headline vocabulary (`all_satisfied` -> `full_satisfaction`,
    # plus `partial_coverage`). Any of the three alone is breaking for a reader.
    assert RUNTIME_CONTRACT_VERSION == "2.0.0"


def test_the_catalog_schema_version_did_not_move_with_it():
    """The two versions are independent, and only one moved in this item.

    Item 3 adds no catalog field and re-keys nothing, so a consumer's catalog reader is
    unaffected. Bumping both together would tell TEAx to re-vendor a set that did not change
    and would move `model_contract_fingerprint` for every constraint-bearing package.
    """
    assert CATALOG_SCHEMA_VERSION == "3.0.0"


def test_the_version_rides_the_package_seal(tmp_path):
    """A seal records the generator that produced the package, not what is on the loader.

    This is the field TEAx's `package_load` reads and refuses on, which is why the bump makes
    every pre-Item-3 package fail closed before any report is read.
    """
    from sysml_codegen.contracts.seal import seal_package

    (tmp_path / "modules").mkdir()
    (tmp_path / "modules" / "thing.py").write_text("x = 1\n")
    contract = seal_package(tmp_path, "probe_pkg")
    assert contract.runtime_contract_version == RUNTIME_CONTRACT_VERSION
