"""A site reason set at a raise reaches the harness's refusal observation (Item 2a D8).

Every later mutation test judges a site by the reason the harness observes. If a rebuild
between the raise and ``run_codegen``'s log call dropped the reason, a neutralized site
would look like a survivor rather than a lost field. So the field is proved here first: one
witness per carrier type and per converter branch of
``orchestration/elaborated_pipeline.py:_build_from_extractor``, each run through
``run_codegen`` exactly as a user runs it.

Each witness is a packaged conformance case where one carries the branch's reason (read
through agentic-mbse's package, design D14), a committed fixture, or, where neither exists, a
model written here.

Two branches have no model that reaches them:

- ``ExpressionInventoryError``: every raise in ``elaboration/expression_evidence.py`` is a
  consistency check over the inventory the same call built (a duplicate site, a conflicting
  role, a site or declaration the inventory does not hold). The one authored form the
  inventory refuses, an index, leaves through ``_indexed_refusal`` as a
  ``SemanticEvidenceError``; the indexed-reference witness below takes that path.
- ``except Exception``: it exists for failures nothing classified, so no model is known to
  reach it.

Each is witnessed instead by a raise patched in at the inventory call, which proves the
converter carries the reason when the branch is reached.
"""

from __future__ import annotations

import textwrap
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pytest
from agentic_mbse.sysml.conformance_case import packaged_case_dir

from sysml_codegen.cli.refusal import RefusalKind
from sysml_codegen.elaboration.diagnostics import SiteReason
from sysml_codegen.elaboration.expression_evidence import ExpressionInventoryError
from sysml_codegen.orchestration import elaborated_pipeline
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.subset_profile import observe

pytestmark = requires_license

_GENERATING_MODEL = """
package fx {
    private import ScalarValues::*;
    calc def Twice { in v : Real; return r : Real = 2.0 * v; }
    part def Site { attribute x : Real = 1.0; calc t : Twice { in v = x; } }
    part site : Site;
}
"""


def _inline(source: str) -> Callable[[Path], Path]:
    def write(tmp_path: Path) -> Path:
        model = tmp_path / "model" / "model.sysml"
        model.parent.mkdir()
        model.write_text(textwrap.dedent(source))
        return model.parent

    return write


def _fixture(name: str) -> Callable[[Path], Path]:
    return lambda _tmp_path: FIXTURES_DIR / name


def _packaged(case_id: str) -> Callable[[Path], Path]:
    return lambda _tmp_path: packaged_case_dir(case_id)


@dataclass(frozen=True)
class Witness:
    #: The carrier type and converter branch the reason travels through.
    branch: str
    reason: SiteReason
    kind: RefusalKind
    model_root: Callable[[Path], Path]


REACH_WITNESSES = (
    Witness(
        "ReadinessFinding__readiness_with_referent",
        SiteReason.BINDING_SOURCE_FORM_UNSUPPORTED,
        RefusalKind.READINESS,
        _packaged("binding-source__expression_source__owner_instantiated"),
    ),
    Witness(
        "Diagnostic__GraphValidationError__diagnostic_with_referent",
        SiteReason.CONSTRAINT_PROFILE_BLOCKED,
        RefusalKind.DIAGNOSTIC,
        _packaged("constraint-predicate__blocked_predicate__owner_instantiated"),
    ),
    Witness(
        "ElaborationInvariantError__diagnostic_with_referent",
        SiteReason.OCCURRENCE_MULTIPLICITY_ORDERED,
        RefusalKind.DIAGNOSTIC,
        _packaged("part-multiplicity__ordered__expanded_part_usage"),
    ),
    Witness(
        "SemanticEvidenceError__semantic_evidence_diagnostic",
        SiteReason.EVIDENCE_INDEXED_REFERENCE_UNSUPPORTED,
        RefusalKind.DIAGNOSTIC,
        _packaged("indexed-reference__indexed_reference__attribute_value"),
    ),
    Witness(
        "ExactTypeError__diagnostic_with_referent",
        SiteReason.EXTRACTION_TYPING_TARGET_UNSUPPORTED,
        RefusalKind.DIAGNOSTIC,
        _fixture("plant_value_shapes"),
    ),
    Witness(
        "CodeGenerationError__reraised_during_construction",
        SiteReason.ELABORATION_NO_EXECUTABLE_CONTENT,
        RefusalKind.GENERATION,
        _inline(
            """
            package fx {
                private import ScalarValues::*;
                part def Site { attribute x : Real = 1.0; }
                part site : Site;
            }
            """
        ),
    ),
    Witness(
        "CodeGenerationError__generation_stage",
        SiteReason.GENERATION_CONSTRAINT_NAME_UNSAFE,
        RefusalKind.GENERATION,
        _fixture("constraint_inline"),
    ),
)


@pytest.mark.parametrize("witness", REACH_WITNESSES, ids=lambda w: w.branch)
def test_reason_set_at_site_reaches_harness(witness, tmp_path):
    obs = observe.generator_half(witness.model_root(tmp_path))
    assert not obs.generated
    assert obs.refusal is not None
    assert obs.refusal.kind is witness.kind
    assert witness.reason in {item.reason for item in obs.refusals}


def _raise_inventory_error(_model: object) -> None:
    raise ExpressionInventoryError(
        "patched consistency failure", reason=SiteReason.INTERNAL_FAILURE_UNCLASSIFIED
    )


def _raise_unclassified(_model: object) -> None:
    raise RuntimeError("patched unclassified failure")


@pytest.mark.parametrize(
    "raise_at_inventory",
    [_raise_inventory_error, _raise_unclassified],
    ids=[
        "ExpressionInventoryError__diagnostic_with_referent",
        "Exception__unexpected_public_failure",
    ],
)
def test_reason_reaches_harness_from_branch_no_model_reaches(
    raise_at_inventory, tmp_path, monkeypatch
):
    monkeypatch.setattr(
        elaborated_pipeline, "build_expression_evidence_inventory", raise_at_inventory
    )
    obs = observe.generator_half(_inline(_GENERATING_MODEL)(tmp_path))
    assert not obs.generated
    assert obs.refusal is not None
    assert obs.refusal.kind is RefusalKind.DIAGNOSTIC
    assert [item.reason for item in obs.refusals] == [SiteReason.INTERNAL_FAILURE_UNCLASSIFIED]


def test_generating_model_logs_no_refusal(tmp_path):
    obs = observe.generator_half(_inline(_GENERATING_MODEL)(tmp_path))
    assert obs.generated
    assert obs.refusal is None
    assert obs.graph is not None
    assert obs.contract is not None
