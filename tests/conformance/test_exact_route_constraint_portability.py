"""Gate 4C, row L-118: constraint portability, live versus replay — and one defect.

The responsibility this row carries is that a constraint-bearing model's lowered
catalog, its model contract, and the generated constraint report are the same
whether the package was generated live or replayed from a snapshot, the same
across two checkout roots, and free of any checkout path. The retired specimen
proved it on the legacy route with a **v5** snapshot of ``catf_mfe_model``,
corpus row 5, which the exact route refuses.

**On the exact route it does not hold, and this module says so rather than
asserting around it.** A constraint the catalog *excludes* records its source
``location`` as an absolute path — the checkout path in a live run, and the
capture-time staging directory (``/tmp/sysml-codegen-sources-XXXXXXXX/root-0/…``)
in a replay. That location is inside the catalog fingerprint, which is inside the
model contract's semantic fingerprint, so one model produces four different
semantic fingerprints across two checkout roots x two routes. Measured, at the
values one run produced:

    live-a    ebbeda695a59   ///tmp/cp2/checkout-a/models/model.sysml:13
    live-b    5bef4ec1fb5c   ///tmp/cp2/checkout-b/models/model.sysml:13
    replay-a  97a9518d6776   ///tmp/sysml-codegen-sources-btsdvdfx/root-0/model.sysml:13
    replay-b  b0a802944d37   ///tmp/sysml-codegen-sources-xz63d9p_/root-0/model.sysml:13

So this module does two jobs. It proves the parts that *are* portable — the
constraint report module, the predicate module, and the pipeline YAML are
identical across all four routes — and it pins the leak, so the defect is a
recorded measurement rather than an absence of coverage. Row L-118 stays
**pending** in ``ledger-4a.json`` until the leak is closed: the property the row
exists to protect is the one that fails, and Gate 4B may not delete the legacy
owners while it does.

The fixture is ``constraint_non_numerical``, corpus row 10, which the exact route
accepts and which carries both a numerically executable constraint and a
cataloged-as-excluded string comparison — the excluded record being exactly what
the leak rides on.
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


def test_exactly_three_files_move_with_the_checkout_root(routes) -> None:
    """The blast radius of the leak, named file by file.

    Everything else in the package — the module wrappers, the predicates, the
    pipeline, the inputs, the schemas — is identical across both checkout roots
    and both routes. The three that are not all trace to one field: the model
    contract carries the leaked location, the constraint report embeds the
    catalog fingerprint derived from it, and the package contract hashes both.
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
    assert differing == [
        "contracts/model_contract.json",
        "contracts/package_contract.json",
        REPORT_MODULE,
    ]


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


def test_the_excluded_record_leaks_an_absolute_source_path(routes) -> None:
    """The surfaced defect, measured. Closing it must delete this test, not edit it.

    Live records the checkout path; a replay records the capture-time staging
    directory. Both are absolute, and neither is the portable ``root-0/``
    referent every generated file uses.
    """
    root = routes["_root"].as_posix()

    for name in ("a", "b"):
        live_location = _excluded_location(routes[f"live-{name}"])
        assert live_location == f"//{root}/checkout-{name}/models/model.sysml:13"

        replay_location = _excluded_location(routes[f"replay-{name}"])
        assert _STAGING_DIR.search(replay_location), replay_location
        assert replay_location.endswith("root-0/model.sysml:13")


def test_the_leak_reaches_the_catalog_and_semantic_fingerprints(routes) -> None:
    """Why the leak matters: one model, four fingerprints.

    A fingerprint that moves with the directory a package was built in cannot
    authenticate anything, which is what row L-118 exists to protect.
    """
    semantic = {name: _model_contract(routes[name])["semantic_fingerprint"] for name in ROUTE_NAMES}
    catalog = {
        name: _model_contract(routes[name])["constraint_catalog"]["fingerprint"]
        for name in ROUTE_NAMES
    }
    assert len(set(semantic.values())) == 4, semantic
    assert len(set(catalog.values())) == 4, catalog


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
