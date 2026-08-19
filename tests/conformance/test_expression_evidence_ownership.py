"""Codegen's raw-selector ownership manifest and its evasion gate.

This is Phase 1's seed of closure leg 1 (acquisition) from
`.project/active/stop-reinventing-the-parser/design.md#checked-consumer-and-ownership-manifests`.

The gate reads production source with the Python `ast` module.  It discovers four
things and nothing else, exactly as the design specifies: a direct attribute read of
one of the reviewed selector names, a literal `getattr` for one of those names, a
simple local or imported alias of either form, and a non-literal `getattr` in the
raw-SysIDE module set (which is rejected outright, because its selector cannot be
reviewed).

`REVIEWED_ROWS` is the complete production-package manifest for the four reviewed selector
names.  It contains Codegen's four
contextual parser reads, collision-aware rows for neutral IR and the serialized
``SourceFile.referent`` key, and mechanically excluded off-route legacy reads.  An
unannotated receiver never qualifies as a collision, which is why the adapter-free mutant
below remains an unowned read and kills equality.
"""

from __future__ import annotations

import ast
import importlib
import inspect
import textwrap
from dataclasses import dataclass
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2] / "src" / "sysml_codegen"

#: The expression selectors Agentic owns after this item lands.
REVIEWED_SELECTORS = frozenset({"operands", "referent", "target_feature", "chaining_features"})

#: How Codegen reaches SysIDE.  No production module imports `syside` directly — that is
#: deliberate and stated at `extraction/extractor.py:14` — so importing this adapter is what
#: identifies a module that handles raw parser nodes in this repository.
RAW_SYSIDE_ADAPTER = "agentic_mbse.sysml.syside_adapter"

#: The measured raw-SysIDE module set: a module qualifies if it imports the adapter above or
#: reads one of the reviewed selectors.  Recorded here so the rule's effect is reviewable
#: rather than implicit, and pinned by `test_the_raw_syside_module_set_is_the_recorded_one`
#: so a module cannot drift in or out unnoticed.
RAW_SYSIDE_MODULES = (
    "elaboration/elaborate.py",
    "elaboration/expression_evidence.py",
    "elaboration/graph.py",
    "elaboration/identity.py",
    "elaboration/occurrence.py",
    "elaboration/project.py",
    "extraction/binding_source.py",
    "extraction/calc_compat_renderer.py",
    "extraction/expression_utils.py",
    "extraction/extractor.py",
    "extraction/feature_metadata.py",
    "extraction/hierarchy_resolver.py",
    "extraction/modeled_defaults.py",
    "extraction/source_manifest.py",
    "extraction/usage_extractor.py",
    "generation/constraint_name_safety.py",
    "generation/predicate_compiler.py",
    "orchestration/elaborated_pipeline.py",
)


@dataclass(frozen=True, order=True)
class SelectorRead:
    """One reviewable raw read of a semantic selector in production source."""

    module: str
    function: str
    selector: str
    form: str
    receiver: str


@dataclass(frozen=True)
class ReviewedRow:
    """A manifest row: who reads what, on which route, and what proves it closed."""

    module: str
    function: str
    selector: str
    form: str
    semantic_owner: str
    route_state: str
    closure_proof: str
    receiver: str = ""

    @property
    def read(self) -> SelectorRead:
        return SelectorRead(
            self.module,
            self.function,
            self.selector,
            self.form,
            self.receiver,
        )


# Proof artifacts shared by row classes.  Every string resolves to a kept test below.
COLLISION_PROOF = (
    "tests/conformance/test_expression_evidence_ownership.py"
    "::test_collision_rows_have_provable_receiver_contracts"
)
OFF_ROUTE_PROOF = (
    "tests/conformance/test_expression_evidence_ownership.py"
    "::test_public_raw_source_arms_do_not_reach_off_route_modules"
)


# The complete reviewed manifest.  Production-package-wide discovery remains load-bearing: rows
# are added because their receiver is proved, never because the scan was narrowed.
REVIEWED_ROWS: tuple[ReviewedRow, ...] = (
    ReviewedRow(
        module="extraction/binding_source.py",
        function="_relationship_segments",
        selector="chaining_features",
        form="getattr",
        semantic_owner="codegen: total deep-relationship-path factory",
        route_state="live",
        closure_proof=(
            "tests/unit/test_expression_evidence_boundary.py"
            "::test_deep_override_mapped_index_refuses_at_the_path_factory"
        ),
        receiver="redefined_feature",
    ),
    ReviewedRow(
        module="elaboration/elaborate.py",
        function="_ExactElaborator._enumeration_literal",
        selector="referent",
        form="getattr",
        semantic_owner="codegen: enumeration discrimination",
        route_state="live",
        closure_proof=(
            "tests/unit/test_expression_evidence_boundary.py"
            "::test_enumeration_literal_requires_an_exact_referent"
        ),
        receiver="expression",
    ),
    ReviewedRow(
        module="elaboration/occurrence.py",
        function="_modeled_integer_bound",
        selector="referent",
        form="getattr",
        semantic_owner="codegen: multiplicity contextualization",
        route_state="live",
        closure_proof=(
            "tests/unit/test_elaboration_occurrence.py"
            "::test_multiplicity_cannot_borrow_an_unrelated_package_writer"
        ),
        receiver="bound",
    ),
    ReviewedRow(
        module="elaboration/occurrence.py",
        function="build_feature_slot_index",
        selector="chaining_features",
        form="getattr",
        semantic_owner="codegen: redefinition endpoints",
        route_state="live",
        closure_proof=(
            "tests/conformance/test_occurrence_domain_derivation.py"
            "::test_real_fixture_has_one_redefinition_slot_and_effective_specialized_usage"
        ),
        receiver="redefined",
    ),
    # Neutral ExpressionIR reads.  The field name collides with SysIDE's raw selector,
    # but the receiving parameter is annotated at every read site and the kept proof
    # below pins that annotation.
    ReviewedRow(
        "elaboration/graph.py",
        "InstanceGraph._expression_reference_count",
        "operands",
        "direct",
        "agentic-mbse ExpressionIR.OperatorNode.operands",
        "live",
        COLLISION_PROOF,
        "expression",
    ),
    ReviewedRow(
        "elaboration/graph.py",
        "InstanceGraph._validate_expression_tags",
        "operands",
        "direct",
        "agentic-mbse ExpressionIR.OperatorNode.operands",
        "live",
        COLLISION_PROOF,
        "expression",
    ),
    ReviewedRow(
        "elaboration/project.py",
        "_Projection._compile_computed_expression.render",
        "operands",
        "direct",
        "agentic-mbse ExpressionIR.OperatorNode.operands",
        "live",
        COLLISION_PROOF,
        "expression",
    ),
    ReviewedRow(
        "extraction/calc_compat_renderer.py",
        "_render_operator",
        "operands",
        "direct",
        "agentic-mbse ExpressionIR.OperatorNode.operands",
        "live",
        COLLISION_PROOF,
        "node",
    ),
    ReviewedRow(
        "extraction/calc_compat_renderer.py",
        "collect_calc_refs._walk",
        "operands",
        "direct",
        "agentic-mbse ExpressionIR.OperatorNode.operands",
        "live",
        COLLISION_PROOF,
        "node",
    ),
    ReviewedRow(
        "extraction/modeled_defaults.py",
        "_resolve_default_node",
        "operands",
        "direct",
        "agentic-mbse ExpressionIR.OperatorNode.operands",
        "live",
        COLLISION_PROOF,
        "node",
    ),
    ReviewedRow(
        "generation/constraint_name_safety.py",
        "predicate_bindings.visit",
        "operands",
        "direct",
        "agentic-mbse ExpressionIR.OperatorNode.operands",
        "live",
        COLLISION_PROOF,
        "node",
    ),
    ReviewedRow(
        "generation/predicate_compiler.py",
        "_compile_numeric_operator",
        "operands",
        "direct",
        "agentic-mbse ExpressionIR.OperatorNode.operands",
        "live",
        COLLISION_PROOF,
        "n",
    ),
    ReviewedRow(
        "generation/predicate_compiler.py",
        "_compile_boolean",
        "operands",
        "direct",
        "agentic-mbse ExpressionIR.OperatorNode.operands",
        "live",
        COLLISION_PROOF,
        "n",
    ),
    ReviewedRow(
        "generation/predicate_compiler.py",
        "_leaf_ref_names",
        "operands",
        "direct",
        "agentic-mbse ExpressionIR.OperatorNode.operands",
        "live",
        COLLISION_PROOF,
        "n",
    ),
    ReviewedRow(
        "generation/predicate_compiler.py",
        "margin_expression",
        "operands",
        "direct",
        "agentic-mbse ExpressionIR.OperatorNode.operands",
        "live",
        COLLISION_PROOF,
        "n",
    ),
    # SourceFile.referent supplies the value stored under the explicitly sealed
    # ``"referent"`` key.  The field name itself does not choose that serialized key; the
    # collision proof guards the typed code/schema linkage at each read site.
    ReviewedRow(
        "extraction/source_manifest.py",
        "SourceAdmission._verify_staged_files",
        "referent",
        "direct",
        "codegen SourceFile.referent serialized key",
        "live",
        COLLISION_PROOF,
        "item",
    ),
    ReviewedRow(
        "extraction/source_manifest.py",
        "SourceAdmission.staged_to_referent",
        "referent",
        "direct",
        "codegen SourceFile.referent serialized key",
        "live",
        COLLISION_PROOF,
        "item",
    ),
    ReviewedRow(
        "extraction/source_manifest.py",
        "SourceFile.envelope_data",
        "referent",
        "direct",
        "codegen SourceFile.referent serialized key",
        "live",
        COLLISION_PROOF,
        "self",
    ),
    ReviewedRow(
        "extraction/source_manifest.py",
        "_admitted_membership",
        "referent",
        "direct",
        "codegen SourceFile.referent serialized key",
        "live",
        COLLISION_PROOF,
        "item",
    ),
    ReviewedRow(
        "orchestration/elaborated_pipeline.py",
        "_elaborate_admitted_sources",
        "referent",
        "direct",
        "codegen SourceFile.referent serialized key",
        "live",
        COLLISION_PROOF,
        "item",
    ),
    # The remaining four discovered rows are mechanically excluded from both public raw
    # source roots.  They stay visible in repository-wide discovery and cannot satisfy a
    # live row.
    ReviewedRow(
        "extraction/hierarchy_resolver.py",
        "_render_neutral_aggregation_node",
        "operands",
        "direct",
        "agentic-mbse neutral aggregation IR",
        "off-route",
        OFF_ROUTE_PROOF,
        "node",
    ),
    ReviewedRow(
        "extraction/usage_extractor.py",
        "_parse_chain_expression",
        "operands",
        "direct",
        "off-route legacy raw SysIDE reader",
        "off-route",
        OFF_ROUTE_PROOF,
        "expr",
    ),
    ReviewedRow(
        "extraction/usage_extractor.py",
        "_parse_chain_expression",
        "target_feature",
        "direct",
        "off-route legacy raw SysIDE reader",
        "off-route",
        OFF_ROUTE_PROOF,
        "expr",
    ),
    ReviewedRow(
        "extraction/usage_extractor.py",
        "_parse_reference_expression",
        "referent",
        "direct",
        "off-route legacy raw SysIDE reader",
        "off-route",
        OFF_ROUTE_PROOF,
        "expr",
    ),
)


# The neutral collision rows must be provable from a receiver annotation in the exact
# function that performs the read.  Values are ``(receiver parameter, required type)``.
NEUTRAL_RECEIVER_CONTRACTS = {
    SelectorRead(
        "elaboration/graph.py",
        "InstanceGraph._expression_reference_count",
        "operands",
        "direct",
        "expression",
    ): ("expression", "ExpressionIR"),
    SelectorRead(
        "elaboration/graph.py",
        "InstanceGraph._validate_expression_tags",
        "operands",
        "direct",
        "expression",
    ): ("expression", "ExpressionIR"),
    SelectorRead(
        "elaboration/project.py",
        "_Projection._compile_computed_expression.render",
        "operands",
        "direct",
        "expression",
    ): ("expression", "ExpressionIR"),
    SelectorRead(
        "extraction/calc_compat_renderer.py",
        "_render_operator",
        "operands",
        "direct",
        "node",
    ): (
        "node",
        "OperatorNode",
    ),
    SelectorRead(
        "extraction/calc_compat_renderer.py",
        "collect_calc_refs._walk",
        "operands",
        "direct",
        "node",
    ): ("node", "ExpressionIR"),
    SelectorRead(
        "extraction/modeled_defaults.py",
        "_resolve_default_node",
        "operands",
        "direct",
        "node",
    ): (
        "node",
        "ExpressionIR",
    ),
    SelectorRead(
        "generation/constraint_name_safety.py",
        "predicate_bindings.visit",
        "operands",
        "direct",
        "node",
    ): ("node", "ExpressionIR"),
    SelectorRead(
        "generation/predicate_compiler.py",
        "_compile_numeric_operator",
        "operands",
        "direct",
        "n",
    ): ("n", "OperatorNode"),
    SelectorRead(
        "generation/predicate_compiler.py",
        "_compile_boolean",
        "operands",
        "direct",
        "n",
    ): (
        "n",
        "ExpressionIR",
    ),
    SelectorRead(
        "generation/predicate_compiler.py",
        "_leaf_ref_names",
        "operands",
        "direct",
        "n",
    ): (
        "n",
        "ExpressionIR",
    ),
    SelectorRead(
        "generation/predicate_compiler.py",
        "margin_expression",
        "operands",
        "direct",
        "n",
    ): (
        "n",
        "ExpressionIR",
    ),
}

SOURCE_FILE_COLLISION_READS = {
    row.read
    for row in REVIEWED_ROWS
    if row.semantic_owner.startswith("codegen SourceFile.referent")
}

#: Modules audited as off the public raw-source route.  A live import of one of these
#: fails `test_public_raw_source_arms_do_not_reach_off_route_modules`; their raw reads
#: can never satisfy a live manifest row.
OFF_ROUTE_MODULES = (
    "extraction/usage_extractor.py",
    "extraction/hierarchy_resolver.py",
)

#: The installed command surface is the mechanically checked root.  Both the live
#: elaboration arm and snapshot-capture arm are reachable from this module; a companion
#: assertion below pins that relationship instead of declaring those arms only in prose.
PUBLIC_RAW_SOURCE_ROOTS = ("cli/__init__.py",)

#: Weak identifiers that must not survive the item.  Present at `C_base`, so
#: `test_deleted_symbols_are_absent` is a recorded red until Phases 2-3 remove them.
DELETED_SYMBOLS = (
    "_extract_binding_source",
    "_parse_expression_to_path",
    "_extract_simple_reference",
    "_build_reference_path",
    "has_index_segment",
    "SourceReferenceEvidence",
)


class _SelectorScanner(ast.NodeVisitor):
    """Collect every reviewable selector read in one parsed module."""

    def __init__(self, module: str) -> None:
        self.module = module
        self.reads: set[SelectorRead] = set()
        self._scope: list[str] = []
        self._aliases: dict[str, str] = {}

    def _qualified(self) -> str:
        return ".".join(self._scope) or "<module>"

    def _record(self, selector: str, form: str, receiver: ast.AST) -> None:
        self.reads.add(
            SelectorRead(
                self.module,
                self._qualified(),
                selector,
                form,
                ast.unparse(receiver),
            )
        )

    def _visit_scope(self, node: ast.AST) -> None:
        self._scope.append(getattr(node, "name", "<anonymous>"))
        self.generic_visit(node)
        self._scope.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        self._visit_scope(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
        self._visit_scope(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        self._visit_scope(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for name in node.names:
            if name.name in REVIEWED_SELECTORS and name.asname:
                self._aliases[name.asname] = name.name
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        # A simple local alias: `chain = node.chaining_features` or
        # `pull = operator.attrgetter("operands")`-style literal rebinding.
        if isinstance(node.value, ast.Constant) and node.value.value in REVIEWED_SELECTORS:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self._aliases[target.id] = str(node.value.value)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr in REVIEWED_SELECTORS:
            self._record(node.attr, "direct", node.value)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "getattr" and len(node.args) >= 2:
            selector = node.args[1]
            if isinstance(selector, ast.Constant):
                if selector.value in REVIEWED_SELECTORS:
                    self._record(str(selector.value), "getattr", node.args[0])
            elif isinstance(selector, ast.Name) and selector.id in self._aliases:
                self._record(self._aliases[selector.id], "alias-getattr", node.args[0])
            else:
                self._record("<unreviewable>", "dynamic-getattr", node.args[0])
        elif (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "__getattribute__"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value in REVIEWED_SELECTORS
        ):
            self._record(str(node.args[0].value), "dunder-getattribute", node.func.value)
        elif (
            isinstance(node.func, ast.Call)
            and isinstance(node.func.func, ast.Attribute)
            and node.func.func.attr == "attrgetter"
            and node.func.args
            and isinstance(node.func.args[0], ast.Constant)
            and node.func.args[0].value in REVIEWED_SELECTORS
            and node.args
        ):
            self._record(str(node.func.args[0].value), "attrgetter", node.args[0])
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:  # noqa: N802
        if (
            isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "vars"
            and node.value.args
            and isinstance(node.slice, ast.Constant)
            and node.slice.value in REVIEWED_SELECTORS
        ):
            self._record(str(node.slice.value), "vars-subscript", node.value.args[0])
        self.generic_visit(node)


def scan_module(source: str, module: str) -> set[SelectorRead]:
    """Discover every reviewable selector read in one module's source text."""
    scanner = _SelectorScanner(module)
    scanner.visit(ast.parse(source))
    return scanner.reads


def is_raw_syside_module(source: str) -> bool:
    """Does this module handle raw SysIDE nodes?

    Two clauses, either sufficient: it imports the SysIDE adapter, or it reads one of the
    reviewed selectors.  This is the scope the design's ownership manifest means by "the
    raw-SysIDE module set", and it is what bounds the dynamic-`getattr` rejection below.
    """
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module == RAW_SYSIDE_ADAPTER or node.module.startswith(
                f"{RAW_SYSIDE_ADAPTER}."
            ):
                return True
        elif isinstance(node, ast.Import):
            if any(
                alias.name == RAW_SYSIDE_ADAPTER or alias.name.startswith(f"{RAW_SYSIDE_ADAPTER}.")
                for alias in node.names
            ):
                return True
        elif isinstance(node, ast.Attribute) and node.attr in REVIEWED_SELECTORS:
            return True
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "getattr"
            and len(node.args) >= 2
            and isinstance(node.args[1], ast.Constant)
            and node.args[1].value in REVIEWED_SELECTORS
        ):
            return True
    if any(read.form != "dynamic-getattr" for read in scan_module(source, "<probe>")):
        return True
    return False


def _production_modules() -> list[Path]:
    return sorted(PACKAGE_ROOT.rglob("*.py"))


def raw_syside_modules() -> tuple[str, ...]:
    """Every production module that handles raw SysIDE nodes, by the rule above."""
    return tuple(
        path.relative_to(PACKAGE_ROOT).as_posix()
        for path in _production_modules()
        if is_raw_syside_module(path.read_text())
    )


def discovered_reads() -> set[SelectorRead]:
    """The raw-selector inventory of the production package.

    Selector reads are collected throughout ``src/sysml_codegen`` — a read of `.operands`
    is a selector read wherever it sits in that package.  Scripts and probes are outside this
    shipping-code gate.  The unreviewable dynamic-`getattr` form is collected only inside the
    raw-SysIDE module set, because that is the scope in which a hidden selector is the
    hazard.  Outside it, a `getattr` over a module's own field names is ordinary Python.
    """
    found: set[SelectorRead] = set()
    for path in _production_modules():
        module = path.relative_to(PACKAGE_ROOT).as_posix()
        source = path.read_text()
        reads = scan_module(source, module)
        if not is_raw_syside_module(source):
            reads = {read for read in reads if read.form != "dynamic-getattr"}
        found |= reads
    return found


def _imports_of(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
            for name in node.names:
                modules.add(f"{node.module}.{name.name}")
        elif isinstance(node, ast.Import):
            modules |= {name.name for name in node.names}
    return modules


def _qualified_scopes(path: Path) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    scopes: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}

    class Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.stack: list[str] = []

        def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        def _function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
            self.stack.append(node.name)
            scopes[".".join(self.stack)] = node
            self.generic_visit(node)
            self.stack.pop()

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
            self._function(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
            self._function(node)

    Visitor().visit(ast.parse(path.read_text()))
    return scopes


def _parameter_annotation_node(module: str, function: str, parameter: str) -> ast.expr:
    scope = _qualified_scopes(PACKAGE_ROOT / module)[function]
    arguments = [*scope.args.posonlyargs, *scope.args.args, *scope.args.kwonlyargs]
    [argument] = [item for item in arguments if item.arg == parameter]
    assert argument.annotation is not None, f"{module}::{function} leaves {parameter} unannotated"
    return argument.annotation


def _class_annotation_node(module: str, class_name: str, field_name: str) -> ast.expr:
    tree = ast.parse((PACKAGE_ROOT / module).read_text())
    [class_node] = [
        node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == class_name
    ]
    [field] = [
        node
        for node in class_node.body
        if isinstance(node, ast.AnnAssign)
        and isinstance(node.target, ast.Name)
        and node.target.id == field_name
    ]
    return field.annotation


def _annotation_origins(module: str, annotation: ast.expr) -> set[str]:
    """Resolve annotation names to their declared import or module origin."""
    path = PACKAGE_ROOT / module
    imports: dict[str, str] = {}
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.ImportFrom) and node.module:
            for name in node.names:
                imports[name.asname or name.name] = f"{node.module}.{name.name}"
        elif isinstance(node, ast.Import):
            for name in node.names:
                imports[name.asname or name.name.split(".")[0]] = name.name

    local_module = "sysml_codegen." + Path(module).with_suffix("").as_posix().replace("/", ".")
    local_classes = {
        node.name
        for node in ast.parse(path.read_text()).body
        if isinstance(node, ast.ClassDef)
    }
    origins: set[str] = set()
    for node in ast.walk(annotation):
        if isinstance(node, ast.Name):
            if node.id in imports:
                origins.add(imports[node.id])
            elif node.id in local_classes:
                origins.add(f"{local_module}.{node.id}")
            else:
                origins.add(node.id)
    return origins


def _receiver_iterables(module: str, function: str, receiver: str) -> set[str]:
    """The exact iterables that bind a local receiver used at a selector read."""
    scope = _qualified_scopes(PACKAGE_ROOT / module)[function]
    result: set[str] = set()
    for node in ast.walk(scope):
        if isinstance(node, (ast.For, ast.comprehension)):
            target = node.target
            if isinstance(target, ast.Name) and target.id == receiver:
                result.add(ast.unparse(node.iter))
    return result


def _named_proof_exists(proof: str) -> bool:
    module_path, separator, function = proof.partition("::")
    if not separator:
        return False
    module_name = Path(module_path).with_suffix("").as_posix().replace("/", ".")
    candidate = getattr(importlib.import_module(module_name), function, None)
    return (
        inspect.isfunction(candidate)
        and function.startswith("test_")
        and getattr(candidate, "__test__", True) is not False
    )


def _production_module_map() -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in _production_modules():
        relative = path.relative_to(PACKAGE_ROOT)
        parts = list(relative.with_suffix("").parts)
        if parts[-1] == "__init__":
            parts.pop()
        name = ".".join(("sysml_codegen", *parts))
        result[name] = path
    return result


def _local_imports(module_name: str, path: Path, known: set[str]) -> set[str]:
    package = module_name if path.name == "__init__.py" else module_name.rpartition(".")[0]
    result: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names if alias.name in known)
            continue
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.level:
            package_parts = package.split(".")
            anchor = package_parts[: len(package_parts) - node.level + 1]
            if node.module:
                anchor.extend(node.module.split("."))
            base = ".".join(anchor)
        else:
            base = node.module or ""
        if base in known:
            result.add(base)
        result.update(
            candidate for alias in node.names if (candidate := f"{base}.{alias.name}") in known
        )
    return result


def _transitively_reachable_modules() -> set[str]:
    modules = _production_module_map()
    starts = {
        module_name
        for module_name, path in modules.items()
        if path.relative_to(PACKAGE_ROOT).as_posix() in PUBLIC_RAW_SOURCE_ROOTS
    }
    assert len(starts) == len(PUBLIC_RAW_SOURCE_ROOTS)
    reached: set[str] = set()
    pending = list(starts)
    while pending:
        current = pending.pop()
        if current in reached:
            continue
        reached.add(current)
        pending.extend(_local_imports(current, modules[current], set(modules)) - reached)
    return reached


# ---------------------------------------------------------------------------
# Leg 1 — acquisition
# ---------------------------------------------------------------------------


def test_discovered_raw_selectors_equal_the_reviewed_manifest() -> None:
    """Recorded red at `C_base`: Codegen still owns raw reads the manifest does not.

    The failure lists every unowned read.  Phase 3 removes them; this row goes green
    when Codegen holds only the four reviewed contextual exceptions.
    """
    reviewed = {row.read for row in REVIEWED_ROWS}
    discovered = discovered_reads()

    unowned = sorted(discovered - reviewed)
    stale = sorted(reviewed - discovered)
    assert not unowned, f"raw selector reads with no reviewed manifest row: {unowned}"
    assert not stale, f"reviewed manifest rows no longer present in production: {stale}"


def test_every_reviewed_row_names_a_closure_proof() -> None:
    """A manifest row without a proof is a claim, not closure."""
    unproved = [row for row in REVIEWED_ROWS if not row.closure_proof.strip()]
    assert not unproved, f"reviewed rows with no closure proof: {unproved}"
    assert {row.route_state for row in REVIEWED_ROWS} <= {"live", "off-route"}
    unresolved = [row for row in REVIEWED_ROWS if not _named_proof_exists(row.closure_proof)]
    assert not unresolved, f"reviewed rows name tests that do not exist: {unresolved}"


def test_collision_rows_have_provable_receiver_contracts() -> None:
    """Every collision is typed at its read site; a docstring cannot qualify it."""
    collision_reads = {
        row.read
        for row in REVIEWED_ROWS
        if "ExpressionIR" in row.semantic_owner or "SourceFile.referent" in row.semantic_owner
    }
    assert collision_reads == set(NEUTRAL_RECEIVER_CONTRACTS) | SOURCE_FILE_COLLISION_READS

    for read, (parameter, owner_type) in NEUTRAL_RECEIVER_CONTRACTS.items():
        expected_origin = f"agentic_mbse.sysml.expression_ir.{owner_type}"
        origins = _annotation_origins(
            read.module,
            _parameter_annotation_node(read.module, read.function, parameter),
        )
        assert read.receiver == parameter
        assert expected_origin in origins, (
            f"{read.module}::{read.function} does not prove {parameter} comes from "
            f"{expected_origin}: {sorted(origins)}"
        )

    source_module = "extraction/source_manifest.py"
    assert _annotation_origins(
        source_module,
        _class_annotation_node(source_module, "SourceFile", "referent"),
    ) == {"str"}
    source_file_origin = "sysml_codegen.extraction.source_manifest.SourceFile"
    source_admission_origin = "sysml_codegen.extraction.source_manifest.SourceAdmission"
    assert source_file_origin in _annotation_origins(
        source_module,
        _class_annotation_node(source_module, "SourceAdmission", "files"),
    )
    assert source_file_origin in _annotation_origins(
        source_module,
        _parameter_annotation_node(source_module, "_admitted_membership", "files"),
    )
    assert source_admission_origin in _annotation_origins(
        "orchestration/elaborated_pipeline.py",
        _parameter_annotation_node(
            "orchestration/elaborated_pipeline.py",
            "elaborate_admitted_sources",
            "admission",
        ),
    )

    # Each local ``item.referent`` receiver is tied to the annotated collection above.
    assert _receiver_iterables(
        source_module, "SourceAdmission._verify_staged_files", "item"
    ) == {"self.files"}
    assert _receiver_iterables(
        source_module, "SourceAdmission.staged_to_referent", "item"
    ) == {"self.files"}
    assert _receiver_iterables(source_module, "_admitted_membership", "item") == {"files"}
    assert _receiver_iterables(
        "orchestration/elaborated_pipeline.py", "_elaborate_admitted_sources", "item"
    ) == {"admission.files"}


def test_the_raw_syside_module_set_is_the_recorded_one() -> None:
    """Pin the rule's measured effect, so the gate's scope cannot drift unreviewed."""
    assert raw_syside_modules() == RAW_SYSIDE_MODULES


def test_no_production_module_imports_syside_directly() -> None:
    """The premise behind keying the rule on the adapter rather than on `syside` itself.

    Codegen reaches SysIDE only through `agentic_mbse.sysml.syside_adapter`; a direct
    `import syside` would make the adapter-import clause miss that module.
    """
    offenders = [
        path.relative_to(PACKAGE_ROOT).as_posix()
        for path in _production_modules()
        for node in ast.walk(ast.parse(path.read_text()))
        if (
            isinstance(node, ast.Import)
            and any(a.name == "syside" or a.name.startswith("syside.") for a in node.names)
        )
        or (
            isinstance(node, ast.ImportFrom)
            and node.module is not None
            and (node.module == "syside" or node.module.startswith("syside."))
        )
    ]
    assert not offenders, f"direct syside imports bypass the adapter boundary: {offenders}"


def test_no_dynamic_getattr_survives_in_the_raw_syside_module_set() -> None:
    """A non-literal `getattr` inside a raw-SysIDE module hides an unreviewable selector.

    Scoped to that module set on purpose. Outside it, a `getattr` over a module's own
    declared field names reads no parser node and is ordinary, reviewable Python.
    """
    dynamic = sorted(read for read in discovered_reads() if read.form == "dynamic-getattr")
    assert not dynamic, f"unreviewable dynamic getattr selectors: {dynamic}"


# ---------------------------------------------------------------------------
# The five AST evasion mutations — every one must kill the gate
# ---------------------------------------------------------------------------

#: Every mutant imports the SysIDE adapter, so each one is a raw-SysIDE module by the rule
#: above.  That matters for the dynamic-`getattr` mutation in particular: scoping the gate
#: would be worthless if the mutation that scoping could hide were tested outside the scope.
_ADAPTER_IMPORT = f"from {RAW_SYSIDE_ADAPTER} import SysideAdapter\n\n\n"

_EVASIONS = {
    "direct-read": "def consume(node):\n    return node.operands\n",
    "literal-getattr": 'def consume(node):\n    return getattr(node, "operands")\n',
    "local-alias": (
        'SELECTOR = "operands"\n\n\ndef consume(node):\n    return getattr(node, SELECTOR)\n'
    ),
    "imported-alias": (
        "from somewhere import operands as SELECTOR\n\n\n"
        "def consume(node):\n    return getattr(node, SELECTOR)\n"
    ),
    "dynamic-getattr": ("def consume(node, chosen):\n    return getattr(node, chosen)\n"),
    "attrgetter": (
        "import operator\n\n\n"
        'def consume(node):\n    return operator.attrgetter("operands")(node)\n'
    ),
    "dunder-getattribute": (
        'def consume(node):\n    return node.__getattribute__("referent")\n'
    ),
    "vars-subscript": 'def consume(node):\n    return vars(node)["referent"]\n',
}

_EVASION_RESULTS = {
    "direct-read": ("operands", "direct"),
    "literal-getattr": ("operands", "getattr"),
    "local-alias": ("operands", "alias-getattr"),
    "imported-alias": ("operands", "alias-getattr"),
    "dynamic-getattr": ("<unreviewable>", "dynamic-getattr"),
    "attrgetter": ("operands", "attrgetter"),
    "dunder-getattribute": ("referent", "dunder-getattribute"),
    "vars-subscript": ("referent", "vars-subscript"),
}


@pytest.mark.parametrize("evasion", sorted(_EVASIONS))
def test_every_ast_evasion_mutation_is_discovered(evasion: str) -> None:
    """Introduce one evasion form into a raw-SysIDE module and require the gate to kill it."""
    source = _ADAPTER_IMPORT + textwrap.dedent(_EVASIONS[evasion])

    assert is_raw_syside_module(source), "mutant fell outside the scoped gate"
    found = scan_module(source, "mutant.py")
    selector, form = _EVASION_RESULTS[evasion]
    assert found == {SelectorRead("mutant.py", "consume", selector, form, "node")}


def test_adapter_free_unannotated_receiver_fails_manifest_equality() -> None:
    """Ruling 3's own escape: discovery is not enough; equality must reject the row."""
    source = "def consume(node):\n    return node.referent\n"
    assert RAW_SYSIDE_ADAPTER not in source
    found = scan_module(source, "mutant.py")
    expected = {SelectorRead("mutant.py", "consume", "referent", "direct", "node")}
    assert found == expected
    reviewed = {row.read for row in REVIEWED_ROWS}
    assert found - reviewed == expected


def test_a_clean_module_produces_no_selector_reads() -> None:
    """Anti-vacuity: the scanner is not simply flagging everything."""
    assert scan_module("def consume(node):\n    return node.name\n", "clean.py") == set()


def test_a_clean_module_is_not_in_the_raw_syside_set() -> None:
    """Anti-vacuity for the scope rule: it does not admit everything."""
    assert not is_raw_syside_module("def consume(node):\n    return getattr(node, node.name)\n")


def test_adapter_free_dynamic_getattr_remains_outside_the_declared_scope() -> None:
    """Record the residual: no finite selector manifest can classify a dynamic name."""
    source = "def consume(node, chosen):\n    return getattr(node, chosen)\n"
    assert scan_module(source, "residual.py") == {
        SelectorRead(
            "residual.py",
            "consume",
            "<unreviewable>",
            "dynamic-getattr",
            "node",
        )
    }
    assert not is_raw_syside_module(source)


def test_second_receiver_inside_a_reviewed_function_fails_manifest_equality() -> None:
    """A row proves one receiver; another receiver in that function needs its own row."""
    source = "def consume(node, untyped):\n    return node.operands, untyped.operands\n"
    found = scan_module(source, "mutant.py")
    reviewed = {
        SelectorRead("mutant.py", "consume", "operands", "direct", "node")
    }

    assert found - reviewed == {
        SelectorRead("mutant.py", "consume", "operands", "direct", "untyped")
    }


# ---------------------------------------------------------------------------
# Off-route reachability and deleted-symbol inventory
# ---------------------------------------------------------------------------


def test_public_raw_source_arms_do_not_reach_off_route_modules() -> None:
    """An off-route module may never be reached transitively from a public raw-source arm."""
    off_route_names = {
        "sysml_codegen." + Path(module).with_suffix("").as_posix().replace("/", ".")
        for module in OFF_ROUTE_MODULES
    }
    reached = _transitively_reachable_modules()
    assert not off_route_names & reached, sorted(off_route_names & reached)


def test_cli_root_reaches_both_public_raw_source_arms() -> None:
    """The reachability root covers live conversion and sealed snapshot capture."""
    reached = _transitively_reachable_modules()
    assert {
        "sysml_codegen.orchestration.elaborated_pipeline",
        "sysml_codegen.snapshot.capture",
    } <= reached


def test_off_route_modules_are_inventoried_and_present() -> None:
    """The exclusion is only meaningful while the modules it names still exist."""
    missing = [module for module in OFF_ROUTE_MODULES if not (PACKAGE_ROOT / module).is_file()]
    assert not missing, f"off-route inventory names an absent module: {missing}"


def test_deleted_symbols_are_absent() -> None:
    """Recorded red at `C_base`: the weak identifiers are still defined.

    Phases 2-3 delete them.  The check is on definitions, not mentions, so a comment
    or a test naming the old symbol does not keep this red alive.
    """
    surviving: list[str] = []
    for path in _production_modules():
        tree = ast.parse(path.read_text())
        module = path.relative_to(PACKAGE_ROOT).as_posix()
        for node in ast.walk(tree):
            name = getattr(node, "name", None)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if name in DELETED_SYMBOLS:
                    surviving.append(f"{module}::{name}")
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                if node.target.id in DELETED_SYMBOLS:
                    surviving.append(f"{module}::{node.target.id}")
    assert not surviving, f"symbols that must not survive the item: {sorted(surviving)}"
