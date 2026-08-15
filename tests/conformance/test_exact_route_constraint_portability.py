"""Gate 4C, row L-118: constraint portability, live versus replay, exact route.

The responsibility this row carries is that a constraint-bearing model's lowered
catalog, its model contract, and the generated constraint report are the same
whether the package was generated live or replayed from a snapshot, and the same
across two checkout roots. The retired specimen proved it on the legacy route
with a **v5** snapshot of ``catf_mfe_model``, corpus row 5, which the exact route
refuses.

**This module is the red-to-green record of the S1 fix.** When it was first
authored, the exact route failed the property: a constraint the catalog
*excludes* recorded its source ``location`` as an absolute path — the checkout
path in a live run, the private staging directory in a replay — and that field
is inside the catalog fingerprint, which is inside the model contract's semantic
fingerprint. One model at two checkout roots on two routes minted four different
semantic fingerprints, and three files moved with the build directory.

The fix normalizes that location to the same portable ``root-N/<relpath>``
referent the sealed source manifest already uses
(``orchestration/elaborated_pipeline.py``, ``_rewrite_exclusion_locations``),
with each route supplying the mapping it can prove: the live route maps the raw
parser path against its model roots, and the capture route re-renders from the
referent it has already written onto ``source_file``. A snapshot captured before
the fix is refused at load rather than replayed, because replaying it would mint
a fingerprint that varies by capture machine.

So the assertions below are the property, not the defect: four routes, one
package, byte for byte.

The fixture is ``constraint_non_numerical``, corpus row 10, which the exact route
accepts and which carries both a numerically executable constraint and a
cataloged-as-excluded string comparison — the excluded record being exactly what
the leak rode on.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from sysml_codegen.cli import GenerationConfig, run_codegen
from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "constraint_non_numerical"
PACKAGE = "constraint_portability"
REPORT_MODULE = "modules/constraints/constraintreportaggregatormodule.py"
PREDICATES_MODULE = "modules/constraints/predicates.py"

_STAGING_DIR = re.compile(r"/tmp/sysml-codegen-sources-\w+/root-0/")

# An absolute filesystem path ending in ``.sysml``. The leading ``/`` must not be
# preceded by a word character or dash, so the portable ``root-0/model.sysml``
# referent never matches while ``/home/reid/.../model.sysml`` does.
_ABSOLUTE_SYSML = re.compile(r"(?<![\w-])/(?:[\w.-]+/)+[\w.-]+\.sysml")


def _portable_model_text() -> str:
    """The fixture with its ``value`` attribute renamed, copied to each checkout.

    ``constraint_non_numerical`` names an attribute ``value``, which collides
    with the generated predicate binding of the same name and trips the
    constraint name-safety preflight before any package is written. That refusal
    is its own subject with its own tests; renaming here is the same transform
    the retired specimen applied, and it leaves the two constraint shapes — one
    numerical, one excluded string comparison — untouched.
    """
    text = (FIXTURE / "model.sysml").read_text()
    text = text.replace("attribute value", "attribute safe_value")
    return text.replace("value > 0.0", "safe_value > 0.0")


def _generate_live(models: Path, output: Path) -> Path:
    assert run_codegen(
        GenerationConfig(
            models_path=models,
            output_path=output,
            package_name=PACKAGE,
            schema_class_name="Params",
            pipeline_name="pipeline",
            overwrite=True,
        )
    )
    return output


def _generate_replay(snapshot: Path, output: Path) -> Path:
    assert run_codegen(
        GenerationConfig(
            from_snapshot=snapshot,
            output_path=output,
            package_name=PACKAGE,
            schema_class_name="Params",
            pipeline_name="pipeline",
            overwrite=True,
        )
    )
    return output


def _model_contract(package: Path) -> dict:
    return json.loads((package / "contracts" / "model_contract.json").read_text())


def _excluded_location(package: Path) -> str:
    records = _model_contract(package)["constraint_catalog"]["excluded_records"]
    assert len(records) == 1, f"expected one excluded record, got {len(records)}"
    return records[0]["exclusion"]["location"]


@pytest.fixture(scope="module")
def routes(tmp_path_factory) -> dict[str, Path]:
    """One model, two checkout roots, generated live and replayed from each."""
    root = tmp_path_factory.mktemp("constraint-portability")
    model_text = _portable_model_text()

    packages: dict[str, Path] = {"_root": root}
    for name in ("a", "b"):
        checkout = root / f"checkout-{name}" / "models"
        checkout.mkdir(parents=True)
        (checkout / "model.sysml").write_text(model_text)
        packages[f"live-{name}"] = _generate_live(checkout, root / f"live-{name}")
        snapshot = capture_instance_graph_snapshot([checkout], checkout / "snapshot.json")
        packages[f"replay-{name}"] = _generate_replay(snapshot, root / f"replay-{name}")
    return packages


ROUTE_NAMES = ["live-a", "live-b", "replay-a", "replay-b"]


def test_the_whole_package_is_identical_on_every_route(routes) -> None:
    """The property, at its widest: four routes, one package, byte for byte.

    Before the S1 fix this listed three files that moved with the build
    directory — the model contract carrying the leaked location, the constraint
    report embedding the catalog fingerprint derived from it, and the package
    contract hashing both. The set is asserted empty rather than dropped, so a
    *new* route-dependent byte fails here.
    """
    trees = {
        name: {
            str(path.relative_to(routes[name])): path.read_bytes()
            for path in sorted(routes[name].rglob("*"))
            if path.is_file()
        }
        for name in ROUTE_NAMES
    }
    every_path = set(trees["live-a"])
    for name in ROUTE_NAMES:
        assert set(trees[name]) == every_path, f"{name} has a different file set"

    differing = sorted(
        path for path in every_path if len({trees[name][path] for name in ROUTE_NAMES}) > 1
    )
    assert differing == []


def test_the_predicate_module_and_pipeline_are_identical_on_every_route(routes) -> None:
    for relative in (PREDICATES_MODULE, "pipelines/pipeline.yaml"):
        texts = {name: (routes[name] / relative).read_text() for name in ROUTE_NAMES}
        reference = texts["live-a"]
        for name, text in texts.items():
            assert text == reference, f"{name}'s {relative} diverges from live-a"


def test_the_catalog_admits_the_numerical_constraint_and_excludes_the_string_one(
    routes,
) -> None:
    """The fixture is only a portability specimen if the catalog has both kinds."""
    catalog = _model_contract(routes["live-a"])["constraint_catalog"]
    assert len(catalog["excluded_records"]) == 1
    exclusion = catalog["excluded_records"][0]["exclusion"]
    assert exclusion["kind"] == "non_numerical"
    assert exclusion["reasons"] == ["warn_non_numerical_equality"]
    report = (routes["live-a"] / REPORT_MODULE).read_text()
    assert "positive_value" in report, "the numerical constraint must still execute"


def test_the_excluded_location_is_the_portable_referent_on_every_route(routes) -> None:
    """The fix, at the field it fixed.

    ``root-0/model.sysml:13`` is the same shape the sealed source manifest names
    the file by, so it says nothing about where the package was built. Asserted
    literally, not by absence of the old paths: a location that became empty or
    ``<unknown>`` would pass a mere no-absolute-path check.
    """
    root = routes["_root"].as_posix()
    for name in ROUTE_NAMES:
        location = _excluded_location(routes[name])
        assert location == "root-0/model.sysml:13", f"{name}: {location}"
        assert root not in location
        assert not _STAGING_DIR.search(location)


def test_no_contract_field_carries_an_absolute_source_path(routes) -> None:
    """Enumerated, not assumed: the whole contract is scanned, not one field.

    S1's ruling asked whether any *other* catalog or contract field stored an
    absolute path. This is the check that answers it on every run rather than
    once, so a newly added field that leaks one fails here.
    """
    for name in ROUTE_NAMES:
        for contract in ("model_contract.json", "package_contract.json"):
            text = (routes[name] / "contracts" / contract).read_text()
            hits = sorted(set(_ABSOLUTE_SYSML.findall(text)))
            assert hits == [], f"{name}/{contract} carries {hits}"


def test_the_catalog_and_semantic_fingerprints_are_route_and_root_invariant(routes) -> None:
    """One model, one fingerprint. This is what the row exists to protect."""
    semantic = {
        name: _model_contract(routes[name])["semantic_fingerprint"] for name in ROUTE_NAMES
    }
    catalog = {
        name: _model_contract(routes[name])["constraint_catalog"]["fingerprint"]
        for name in ROUTE_NAMES
    }
    assert len(set(semantic.values())) == 1, semantic
    assert len(set(catalog.values())) == 1, catalog


def test_replaying_one_snapshot_twice_is_deterministic(routes, tmp_path: Path) -> None:
    """The leak is a capture-time record, not a generation-time one.

    Stated because it bounds the defect: the same snapshot always replays to the
    same bytes, so the failure is portability across captures, not per-run
    nondeterminism.
    """
    snapshot = routes["_root"] / "checkout-a" / "models" / "snapshot.json"
    first = _generate_replay(snapshot, tmp_path / "first")
    second = _generate_replay(snapshot, tmp_path / "second")
    assert _model_contract(first) == _model_contract(second)


def test_a_snapshot_carrying_a_pre_fix_location_is_refused_at_load(
    routes, tmp_path: Path
) -> None:
    """The fix cannot be undone by an old artifact: a stale snapshot is refused.

    A snapshot captured before ``exclusion_location`` was normalized stores the
    capture machine's staging path there. Replaying it would mint a fingerprint
    that varies by capture machine — exactly the defect — so the envelope refuses
    the load instead of quietly reproducing it.
    """
    from sysml_codegen.snapshot.envelope import (
        SnapshotIntegrityError,
        _outer_digest,
        load_instance_graph_snapshot,
    )

    sealed = routes["_root"] / "checkout-a" / "models" / "snapshot.json"
    document = json.loads(sealed.read_text())
    rows = document["instance_graph"]["graph"]["constraints"]
    stale = [row for row in rows if row.get("exclusion_location") is not None]
    assert len(stale) == 1, "the fixture must seal exactly one excluded constraint"
    stale[0]["exclusion_location"] = "/tmp/sysml-codegen-sources-deadbeef/root-0/model.sysml:13"

    # The digest is unkeyed and the envelope docstring says so: a writer that
    # sealed this location recomputed the digest over it. Recomputing here is
    # what makes the document a pre-fix snapshot rather than a corrupt one, so
    # the refusal under test is the location check and not the digest check.
    document["integrity"]["digest"] = _outer_digest(document)
    tampered = tmp_path / "stale.json"
    tampered.write_text(json.dumps(document))

    with pytest.raises(SnapshotIntegrityError) as refusal:
        load_instance_graph_snapshot(tampered)
    assert "exclusion_location" in str(refusal.value)
    assert "re-capture" in str(refusal.value)
