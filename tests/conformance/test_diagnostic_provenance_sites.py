"""Named refusal codes carry the authored site they were measured at.

The re-audit's R2: three refusal shapes reached the user with no reference and no
location, and three more codes shared the gap. The rule these proofs enforce is
the same one the catch-all now obeys — a diagnostic field is either measured or
absent — read from the other end: where an authored site *is* in hand, the raise
site must attach it rather than leave the user to guess.

The AST guard is the enumerating half. It keys on the code, not on a list of
scenarios, so a new raise site for a guarded code is covered the day it is
written.
"""

from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace
from uuid import NAMESPACE_URL, uuid5

import pytest

from sysml_codegen.elaboration import ElaborationCode, ElaborationDiagnosticError
from sysml_codegen.elaboration.identity import (
    DeclarationId,
    FeatureSlotId,
    NodeId,
    NodeKind,
    PackageScopeId,
)
from sysml_codegen.elaboration.occurrence import (
    FeatureSlotIndex,
    InvalidRedefinitionFamilyError,
)
from sysml_codegen.elaboration.project import ProjectionError, _Projection
from sysml_codegen.orchestration import elaborated_pipeline
from tests.conftest import requires_license

ROOT = Path(__file__).resolve().parents[2]

#: The codes the re-audit named as reaching the user without provenance. A raise
#: site for one of these must pass both ``reference`` and ``location``.
GUARDED_CODES = frozenset(
    {
        "SI_REDEFINITION_INVALID",
        "SI_CONSTRAINT_UNATTACHED",
        "SI_RENDERING_COLLISION",
        "SI_CONTAINMENT_RECURSIVE",
    }
)

#: Error classes that fix their code at construction rather than taking it.
CODE_BY_CLASS = {
    "InvalidRedefinitionFamilyError": "SI_REDEFINITION_INVALID",
    "RecursiveContainmentError": "SI_CONTAINMENT_RECURSIVE",
}

GUARDED_FILES = (
    "src/sysml_codegen/elaboration/occurrence.py",
    "src/sysml_codegen/elaboration/elaborate.py",
    "src/sysml_codegen/elaboration/project.py",
)


def _guarded_code(call: ast.Call) -> str | None:
    """The guarded code one refusal-constructing call carries, if it carries one."""
    name = call.func.id if isinstance(call.func, ast.Name) else None
    if name in CODE_BY_CLASS:
        return CODE_BY_CLASS[name]
    for argument in call.args:
        if (
            isinstance(argument, ast.Attribute)
            and isinstance(argument.value, ast.Name)
            and argument.value.id == "ElaborationCode"
            and argument.attr in GUARDED_CODES
        ):
            return argument.attr
    return None


def _sites_missing_provenance() -> list[str]:
    missing: list[str] = []
    for relative in GUARDED_FILES:
        tree = ast.parse((ROOT / relative).read_text())
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            code = _guarded_code(node)
            if code is None:
                continue
            keywords = {keyword.arg for keyword in node.keywords}
            if not {"reference", "location"} <= keywords:
                missing.append(f"{relative}:{node.lineno} ({code})")
    return missing


def test_every_guarded_refusal_site_attaches_reference_and_location() -> None:
    assert _sites_missing_provenance() == []


def test_the_guard_fails_when_a_site_drops_its_provenance() -> None:
    """The guard's own kill proof: a stripped site is detected, not tolerated."""
    stripped = ast.parse(
        "raise InvalidRedefinitionFamilyError('redefinition family contains a cycle')\n"
    )
    [call] = [node for node in ast.walk(stripped) if isinstance(node, ast.Call)]
    assert _guarded_code(call) == "SI_REDEFINITION_INVALID"
    assert not {"reference", "location"} <= {keyword.arg for keyword in call.keywords}


def _declaration(name: str) -> DeclarationId:
    return DeclarationId(uuid5(NAMESPACE_URL, f"provenance-probe/{name}"))


def test_a_redefinition_family_cycle_names_the_declaration_it_re_entered() -> None:
    first, second = _declaration("first"), _declaration("second")
    index = FeatureSlotIndex(
        {first, second},
        {first: frozenset({second}), second: frozenset({first})},
        {
            first: ("Probe::first", ("root-0/model.sysml", 11)),
            second: ("Probe::second", ("root-0/model.sysml", 14)),
        },
    )

    with pytest.raises(InvalidRedefinitionFamilyError) as caught:
        index.slot_of(first)

    assert caught.value.code is ElaborationCode.SI_REDEFINITION_INVALID
    assert caught.value.reference == "Probe::first"
    assert caught.value.location == ("root-0/model.sysml", 11)
    assert "Probe::first" in caught.value.detail


RECURSIVE_CONTAINMENT_MODEL = """package recursive_containment_probe {
    private import ScalarValues::*;

    part def Node {
        attribute mass : Real = 1.0;
        part child : Node;
    }

    part root : Node;
}
"""


@requires_license
def test_recursive_containment_names_the_definition_and_the_usage(tmp_path: Path) -> None:
    """SI_CONTAINMENT_RECURSIVE reported a bare UUID and nothing else."""
    model = tmp_path / "model"
    model.mkdir()
    (model / "model.sysml").write_text(RECURSIVE_CONTAINMENT_MODEL)

    with pytest.raises(ElaborationDiagnosticError) as caught:
        elaborated_pipeline.elaborate_model_paths([model])

    [diagnostic] = caught.value.diagnostics
    assert diagnostic.code is ElaborationCode.SI_CONTAINMENT_RECURSIVE
    assert diagnostic.reference == "recursive_containment_probe::Node::child"
    assert diagnostic.source_file == "root-0/model.sysml"
    assert diagnostic.source_line > 0
    assert "recursive_containment_probe::Node" in diagnostic.detail


def _calc_node_id(name: str) -> NodeId:
    return NodeId(
        NodeKind.CALCULATION,
        PackageScopeId(_declaration(f"{name}-scope")),
        FeatureSlotId(_declaration(f"{name}-slot")),
    )


def test_a_rendering_collision_names_both_authored_sides_and_cites_one() -> None:
    holder, arriving = _calc_node_id("holder"), _calc_node_id("arriving")
    projection = _Projection.__new__(_Projection)
    projection.graph = SimpleNamespace(
        calcs={
            holder: SimpleNamespace(
                display_path="Probe::Held",
                source_file="root-0/model.sysml",
                source_line=7,
            ),
            arriving: SimpleNamespace(
                display_path="Probe::Arriving",
                source_file="root-0/model.sysml",
                source_line=19,
            ),
        },
        constraints={},
        attrs={},
    )
    projection.public_module_names = {"probe_module": holder}

    with pytest.raises(ProjectionError) as caught:
        projection._claim_module("probe_module", arriving)

    [diagnostic] = caught.value.diagnostics
    assert diagnostic.code is ElaborationCode.SI_RENDERING_COLLISION
    assert "'Probe::Held'" in diagnostic.detail
    assert "'Probe::Arriving'" in diagnostic.detail
    assert diagnostic.reference == "Probe::Held"
    assert (diagnostic.source_file, diagnostic.source_line) == ("root-0/model.sysml", 7)


def test_a_node_with_no_measured_source_cites_no_location() -> None:
    """The other half of the rule: an unmeasured node contributes no citation."""
    holder, arriving = _calc_node_id("holder"), _calc_node_id("arriving")
    projection = _Projection.__new__(_Projection)
    projection.graph = SimpleNamespace(
        calcs={
            holder: SimpleNamespace(
                display_path="Probe::Held", source_file="unknown", source_line=0
            ),
            arriving: SimpleNamespace(
                display_path="Probe::Arriving", source_file="unknown", source_line=0
            ),
        },
        constraints={},
        attrs={},
    )
    projection.public_module_names = {"probe_module": holder}

    with pytest.raises(ProjectionError) as caught:
        projection._claim_module("probe_module", arriving)

    [diagnostic] = caught.value.diagnostics
    assert diagnostic.reference == "Probe::Held"
    assert diagnostic.source_file is None
    assert diagnostic.source_line is None


ITEM_DEF_OWNER_MODEL = """package item_def_owner_probe {
    private import ScalarValues::*;

    item def Payload {
        attribute mass : Real = 2.0;

        assert constraint mass_positive {
            mass > 0.0
        }
    }

    part def Rig {
        attribute load : Real = 4.0;
        calc def Sizer {
            in attribute demand : Real;
            out attribute size : Real = demand * 2.0;
        }
        calc sizer : Sizer {
            in demand = load;
        }
    }

    part the_rig : Rig;
}
"""


@requires_license
def test_an_item_def_constraint_owner_is_named_and_located(tmp_path: Path) -> None:
    """The `item def` arm of SI_CONSTRAINT_UNATTACHED, which rev 1 never repaired."""
    model = tmp_path / "model"
    model.mkdir()
    (model / "model.sysml").write_text(ITEM_DEF_OWNER_MODEL)

    with pytest.raises(ElaborationDiagnosticError) as caught:
        elaborated_pipeline.elaborate_model_paths([model])

    [diagnostic] = caught.value.diagnostics
    assert diagnostic.code is ElaborationCode.SI_CONSTRAINT_UNATTACHED
    assert diagnostic.reference == "item_def_owner_probe::Payload"
    assert diagnostic.source_file == "root-0/model.sysml"
    assert diagnostic.source_line == 4
    assert "QualifiedName" not in diagnostic.detail


BROKEN_MODEL = "package CaptureProbe;\n" + "".join(
    f"// filler line {index}\n" for index in range(2, 17)
) + "part def Broken { attribute\n"


@requires_license
def test_a_capture_refusal_never_names_the_private_staging_directory(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Capture parses private copies; the user is told about the file they wrote."""
    from sysml_codegen.core.errors import SysMLParsingError
    from sysml_codegen.snapshot.capture import capture_instance_graph_snapshot

    model = tmp_path / "model"
    model.mkdir()
    (model / "model.sysml").write_text(BROKEN_MODEL)

    with pytest.raises(SysMLParsingError) as caught:
        capture_instance_graph_snapshot([model], tmp_path / "snapshot.json")

    reported = str(caught.value) + capsys.readouterr().out
    assert "sysml-codegen-sources-" not in reported
    assert "root-0/model.sysml:17" in reported


def test_a_generation_preflight_refusal_carries_its_code_token_and_source() -> None:
    """The preflight family speaks in stable tokens and cites what it measured."""
    from sysml_codegen.cli import _check_duplicate_output_paths
    from sysml_codegen.core.errors import CodeGenerationError
    from sysml_codegen.resolution.models import ModuleKind, ModuleOutput, PipelineModule

    def module(qualified_name: str, name: str, line: int | None) -> PipelineModule:
        return PipelineModule(
            name=name.lower(),
            module_type=f"{name}Module",
            inputs=[],
            outputs=[ModuleOutput(field_name="o0", python_type="float", channel_name="c0")],
            execution_order=0,
            module_kind=ModuleKind.CALCULATION,
            calc_def_name=name,
            calc_def_qualified_name=qualified_name,
            source_file="root-0/model.sysml" if line is not None else None,
            source_line=line,
        )

    with pytest.raises(CodeGenerationError) as caught:
        _check_duplicate_output_paths(
            [
                module("Probe::'Margin Calc'", "Margin_Calc", 11),
                module("Probe::'margin calc'", "margin_calc", 27),
            ]
        )

    assert str(caught.value).startswith("DUPLICATE_OUTPUT_PATH: ")
    assert "source='root-0/model.sysml:27'" in str(caught.value)

    # A module the graph never measured a source for cites none.
    with pytest.raises(CodeGenerationError) as unlocated:
        _check_duplicate_output_paths(
            [
                module("Probe::'Margin Calc'", "Margin_Calc", None),
                module("Probe::'margin calc'", "margin_calc", None),
            ]
        )

    assert "source=" not in str(unlocated.value)
