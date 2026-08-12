"""The exact-ID front end cannot depend on legacy or string identity machinery."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]

BOUNDARY_FILES = {
    "identity.py": ROOT / "src/sysml_codegen/elaboration/identity.py",
    "occurrence.py": ROOT / "src/sysml_codegen/elaboration/occurrence.py",
    "elaborate.py": ROOT / "src/sysml_codegen/elaboration/elaborate.py",
    "graph.py": ROOT / "src/sysml_codegen/elaboration/graph.py",
    "instance_graph.py": ROOT / "src/sysml_codegen/snapshot/instance_graph.py",
    "project.py": ROOT / "src/sysml_codegen/elaboration/project.py",
}

LEGACY_MODULES = {
    "sysml_codegen.analysis.part_instance_index",
    "sysml_codegen.analysis.dependency_backtracker",
    "sysml_codegen.resolution.output_registry",
    "sysml_codegen.resolution.producer_resolution",
    "sysml_codegen.resolution.supplied_values",
}
LEGACY_SYMBOLS = {"PartInstanceIndex", "InstanceOccurrence", "PathStep"}
PRESENTATION_FIELDS = {
    "name",
    "qualified_name",
    "display_name",
    "display_path",
    "instance_path",
    "producer_channel",
}
STRING_SELECTOR_METHODS = {"split", "rsplit", "startswith", "endswith"}
IR_STRING_PARSERS = {"deserialize_expression", "expression_from_json", "loads", "parse"}

STRING_SELECTOR_VIOLATION = "prefix/suffix or rendered-path string selector"
IR_PARSING_VIOLATION = "IR string parsing for identity"

# Every function in every boundary file is guarded. These narrow exceptions name the exact
# syntactic rule used for wire decoding or public rendering; a new function is never exempt.
FUNCTION_EXEMPTIONS = {
    ("identity.py", "OccurrenceId.from_wire"): frozenset({IR_PARSING_VIOLATION}),
    ("identity.py", "NodeId.from_wire"): frozenset({IR_PARSING_VIOLATION}),
    ("elaborate.py", "_ExactElaborator._direction"): frozenset(
        {STRING_SELECTOR_VIOLATION}
    ),
    ("project.py", "_group_identity"): frozenset({STRING_SELECTOR_VIOLATION}),
    ("project.py", "_Projection._constraint_module_type"): frozenset(
        {STRING_SELECTOR_VIOLATION}
    ),
}


def _attribute_names(node: ast.AST) -> set[str]:
    return {item.attr for item in ast.walk(node) if isinstance(item, ast.Attribute)}


def _called_name(call: ast.Call) -> str | None:
    if isinstance(call.func, ast.Name):
        return call.func.id
    if isinstance(call.func, ast.Attribute):
        return call.func.attr
    return None


FunctionNode = ast.FunctionDef | ast.AsyncFunctionDef


def _boundary_functions(module: ast.Module) -> list[tuple[str, FunctionNode]]:
    functions: list[tuple[str, FunctionNode]] = []

    class Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.scope: list[str] = []

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            self.scope.append(node.name)
            self.generic_visit(node)
            self.scope.pop()

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self._visit_function(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self._visit_function(node)

        def _visit_function(self, node: FunctionNode) -> None:
            qualified_name = ".".join((*self.scope, node.name))
            functions.append((qualified_name, node))
            self.scope.append(node.name)
            self.generic_visit(node)
            self.scope.pop()

    Visitor().visit(module)
    return functions


def _function_nodes(function: FunctionNode) -> list[ast.AST]:
    """Return one function body without folding nested helper bodies into its policy."""

    nodes: list[ast.AST] = []

    class Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            if node is function:
                for statement in node.body:
                    self.visit(statement)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            if node is function:
                for statement in node.body:
                    self.visit(statement)

        def generic_visit(self, node: ast.AST) -> None:
            nodes.append(node)
            super().generic_visit(node)

    Visitor().visit(function)
    return nodes


def _function_violations(
    filename: str, qualified_name: str, function: FunctionNode
) -> set[str]:
    violations: set[str] = set()
    function_nodes = _function_nodes(function)
    for node in function_nodes:
        if isinstance(node, ast.Call):
            called_name = _called_name(node)
            if called_name in STRING_SELECTOR_METHODS:
                violations.add(STRING_SELECTOR_VIOLATION)
            if called_name == "next":
                violations.add("first-match selection")
            if filename != "instance_graph.py" and called_name in IR_STRING_PARSERS:
                violations.add(IR_PARSING_VIOLATION)
            if (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "get"
                and node.args
                and _attribute_names(node.args[0]) & PRESENTATION_FIELDS
            ):
                violations.add("name/QN/rendered-path keyed association")
        elif isinstance(node, ast.Subscript):
            if _attribute_names(node.slice) & PRESENTATION_FIELDS:
                violations.add("name/QN/rendered-path keyed association")
        elif isinstance(node, ast.Compare):
            operands = [node.left, *node.comparators]
            fields = set().union(*(_attribute_names(operand) for operand in operands))
            if fields & PRESENTATION_FIELDS:
                violations.add("name/QN/rendered-path comparison")
        elif isinstance(node, ast.DictComp):
            if _attribute_names(node.key) & PRESENTATION_FIELDS:
                violations.add("name/QN/rendered-path keyed association")

    if qualified_name.rsplit(".", 1)[-1] == "_typed_module_order" and any(
        isinstance(node, ast.Attribute) and node.attr == "producer_channel"
        for node in function_nodes
    ):
        violations.add("channel-to-producer reverse lookup")
    return violations


def _boundary_violations(sources: dict[str, str]) -> set[str]:
    violations: set[str] = set()
    for filename, source in sources.items():
        module = ast.parse(source)
        for node in ast.walk(module):
            if isinstance(node, ast.ImportFrom):
                if node.module in LEGACY_MODULES:
                    violations.add("legacy occurrence/resolution import")
                if {alias.name for alias in node.names} & LEGACY_SYMBOLS:
                    violations.add("legacy occurrence/resolution import")
            elif isinstance(node, ast.Name) and node.id in LEGACY_SYMBOLS:
                violations.add("legacy occurrence/resolution symbol")

        for qualified_name, function in _boundary_functions(module):
            raw = _function_violations(filename, qualified_name, function)
            exemptions = FUNCTION_EXEMPTIONS.get((filename, qualified_name), frozenset())
            violations.update(raw - exemptions)
    return violations


def test_guard_exemptions_are_narrow_and_exercised() -> None:
    for filename, path in BOUNDARY_FILES.items():
        module = ast.parse(path.read_text())
        raw_by_function = {
            qualified_name: _function_violations(filename, qualified_name, function)
            for qualified_name, function in _boundary_functions(module)
        }
        for (exempt_filename, qualified_name), exemptions in FUNCTION_EXEMPTIONS.items():
            if exempt_filename != filename:
                continue
            assert qualified_name in raw_by_function
            assert exemptions <= raw_by_function[qualified_name]


def test_exact_semantic_boundary_has_no_string_or_legacy_identity_route() -> None:
    sources = {name: path.read_text() for name, path in BOUNDARY_FILES.items()}
    assert _boundary_violations(sources) == set()


def test_new_boundary_function_is_guarded_by_default() -> None:
    sources = (
        "def newly_added_selector(node, by_name): return by_name[node.name]\n",
        "async def newly_added_selector(node, by_name): return by_name[node.name]\n",
        "def newly_added_selector(node, by_name): "
        "return (lambda item: by_name[item.name])(node)\n",
    )
    for source in sources:
        assert "name/QN/rendered-path keyed association" in _boundary_violations(
            {"project.py": source}
        )


@pytest.mark.parametrize(
    ("filename", "source", "expected"),
    (
        (
            "elaborate.py",
            "from sysml_codegen.analysis.part_instance_index import PathStep\n"
            "def _resolve_leaf(): return PathStep\n",
            "legacy occurrence/resolution import",
        ),
        (
            "elaborate.py",
            "def _resolve_leaf(node, by_name): return by_name[node.name]\n",
            "name/QN/rendered-path keyed association",
        ),
        (
            "elaborate.py",
            "def _index_calculation_payloads(calc_def, payloads):\n"
            "    return payloads.get(calc_def.qualified_name)\n",
            "name/QN/rendered-path keyed association",
        ),
        (
            "elaborate.py",
            "def _resolve_semantic_reference(node, by_path): return by_path[node.display_path]\n",
            "name/QN/rendered-path keyed association",
        ),
        (
            "elaborate.py",
            "def _select_occurrences(candidate, prefix): return candidate.startswith(prefix)\n",
            "prefix/suffix or rendered-path string selector",
        ),
        (
            "project.py",
            "def _topological_modules(modules, name):\n"
            "    return next(module for module in modules if module.name == name)\n",
            "first-match selection",
        ),
        (
            "project.py",
            "def _computed_inputs(node): return expression_from_json(node.expression_ir)\n",
            "IR string parsing for identity",
        ),
        (
            "project.py",
            "def _typed_module_order(input_, by_channel):\n"
            "    return by_channel[input_.source.producer_channel]\n",
            "channel-to-producer reverse lookup",
        ),
    ),
)
def test_boundary_guard_rejects_each_banned_family(
    filename: str, source: str, expected: str
) -> None:
    assert expected in _boundary_violations({filename: source})


def test_display_rendering_is_an_explicit_metadata_only_boundary() -> None:
    source = (ROOT / "src/sysml_codegen/elaboration/display.py").read_text()
    assert "sanitize_name" in source
    assert "sanitize_qualified_name" in source
    assert "identity" not in source
    assert "NodeId" not in source


def test_the_shipped_cli_is_on_the_exact_route_and_the_legacy_owners_are_unreachable() -> None:
    """Slice 3E switched this pin, and the old expectation is recorded here.

    Until the authority switch this test read
    ``test_shipped_cli_and_capture_remain_on_the_legacy_black_box_route`` and
    required the CLI to name ``build_pipeline_context`` and
    ``build_pipeline_context_from_snapshot``. That was the correct expectation
    while the legacy builder was the shipped authority; it is the opposite of
    the expectation now, so the assertions are inverted rather than deleted.

    The v5 ``capture_snapshot`` was the one place still calling the legacy builder
    after the switch. It retired with the v5 family (retirement step 2), so the
    capture module is now checked for the *absence* of that name, not its presence.
    """
    cli_source = (ROOT / "src/sysml_codegen/cli/__init__.py").read_text()
    capture_source = (ROOT / "src/sysml_codegen/snapshot/capture.py").read_text()
    public_orchestration = (ROOT / "src/sysml_codegen/orchestration/__init__.py").read_text()

    assert "build_exact_pipeline_context" in cli_source
    assert "build_exact_pipeline_context_from_snapshot" in cli_source
    assert "build_pipeline_context" not in cli_source
    assert "build_pipeline_context_from_snapshot" not in cli_source

    # The v6 capture is the only capture left, and it does not name the legacy builder.
    assert "capture_instance_graph_snapshot" in capture_source
    assert "build_pipeline_context" not in capture_source

    # Unchanged by the switch and kept deliberately (restored after the 3E audit,
    # F4, which caught it being dropped without a disposition): the exact route's
    # elaborator entry stays out of the public orchestration API. The legacy builder
    # it used to sit beside is gone, so this pin is now the whole rule — the package
    # exports the two error classes and nothing that constructs a pipeline.
    assert "build_elaborated_pipeline" not in public_orchestration
    assert "build_pipeline_context" not in public_orchestration


def test_internal_exact_route_cannot_mix_in_the_legacy_builder_or_snapshot_rebuild() -> None:
    source = (ROOT / "src/sysml_codegen/orchestration/elaborated_pipeline.py").read_text()
    forbidden = {
        "pipeline_builder",
        "snapshot_context",
        "graph_rebuild",
        "build_pipeline_context",
        "build_full_graph_from_snapshot",
    }
    assert {token for token in forbidden if token in source} == set()
