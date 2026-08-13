"""Live, in-place snapshot, and relocated snapshot mint the same domain.

The document fingerprint proves the snapshot bytes are internally coherent. It says
nothing about whether the live route, re-elaborating the same model, produces the same
domain — a different claim, and the one that can drift. This repo has been bitten by that
class before, where a multi-hop EXPOSE resolved live and mis-wired from a snapshot with
every seal passing. So the comparison here is field for field and record for record, not
digest against digest.

``source_file`` is the one deliberately route-dependent field: the live route records the
caller's checkout path and the capture route records the portable referent. It is masked
here for the same reason it is masked in ``test_snapshot_v6_routes``, and its portability
is asserted separately below.
"""

from __future__ import annotations

import dataclasses
import shutil
from pathlib import Path

import pytest

from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths
from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot
from sysml_codegen.snapshot.envelope import load_instance_graph_snapshot
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

# Chosen because it carries both a reaching gate and a vacuous one, so the parity claim
# covers a record whose disposition came from the profile and one whose disposition came
# from the attachment cause.
FIXTURE = FIXTURES_DIR / "constraint_domain_detached_owner"


def _comparable(domain: dict) -> dict:
    return {
        key: dataclasses.replace(record, source_file="<masked>")
        for key, record in domain.items()
    }


@pytest.fixture(scope="module")
def routes(tmp_path_factory) -> tuple[dict, dict, dict]:
    tmp_path = tmp_path_factory.mktemp("parity")
    live = elaborate_model_paths([FIXTURE])
    captured = capture_instance_graph_snapshot([FIXTURE], tmp_path / "case.json")
    in_place = load_instance_graph_snapshot(captured)
    relocated_path = tmp_path / "moved" / "case.json"
    relocated_path.parent.mkdir()
    shutil.copyfile(captured, relocated_path)
    relocated = load_instance_graph_snapshot(relocated_path)
    return (
        live.constraint_usages,
        in_place.constraint_usages,
        relocated.constraint_usages,
    )


def test_all_three_routes_agree_field_for_field(routes):
    live, in_place, relocated = routes
    assert _comparable(live) == _comparable(in_place) == _comparable(relocated)


def test_the_domain_is_not_empty_so_the_comparison_means_something(routes):
    live, _, _ = routes
    assert len(live) == 2
    assert {record.disposition.reason for record in live.values()} == {
        "admitted",
        "owner_has_no_occurrences",
    }


def test_the_sealed_routes_carry_a_portable_source_referent(routes):
    """The capture route rewrites the usage tier's path, as it does every other tier."""
    _, in_place, relocated = routes
    for domain in (in_place, relocated):
        for record in domain.values():
            assert record.source_file.startswith("root-")
            assert not Path(record.source_file).is_absolute()
