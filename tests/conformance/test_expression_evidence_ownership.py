"""Codegen's raw-selector ownership manifest and its evasion gate.

This is Phase 1's seed of closure leg 1 (acquisition) from
`.project/active/stop-reinventing-the-parser/design.md#checked-consumer-and-ownership-manifests`.

The gate reads production source with the Python `ast` module.  It discovers four
things and nothing else, exactly as the design specifies: a direct attribute read of
one of the reviewed selector names, a literal `getattr` for one of those names, a
simple local or imported alias of either form, and a non-literal `getattr` in the
raw-SysIDE module set (which is rejected outright, because its selector cannot be
reviewed).

`REVIEWED_ROWS` is the *target* manifest, not an inventory of `C_base`.  Codegen owns
only the reviewed contextual exceptions — redefinition endpoints, multiplicity
contextualization, enumeration discrimination, and the total deep-relationship-path
factory.  Every other raw read belongs to Agentic after this item lands.  At `C_base`
the discovered set is much larger, so `test_discovered_raw_selectors_equal_the_reviewed_manifest`
is a recorded red that names each unowned read.  It goes green when Phase 3 removes
Codegen's weaker representations and raw walks.
"""

from __future__ import annotations

import ast
import textwrap
from dataclasses import dataclass
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2] / "src" / "sysml_codegen"

#: The expression selectors Agentic owns after this item lands.
REVIEWED_SELECTORS = frozenset(
    {"operands", "referent", "target_feature", "chaining_features"}
)


@dataclass(frozen=True, order=True)
class SelectorRead:
    """One reviewable raw read of a semantic selector in production source."""

    module: str
    function: str
    selector: str
    form: str


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

    @property
    def read(self) -> SelectorRead:
        return SelectorRead(self.module, self.function, self.selector, self.form)


# The four contextual exceptions the design leaves in Codegen.  Everything else is
# Agentic's after D5/D7.  See design.md#checked-consumer-and-ownership-manifests.
REVIEWED_ROWS: tuple[ReviewedRow, ...] = (
    ReviewedRow(
        module="elaboration/elaborate.py",
        function="_ExactElaborator._apply_deep_literal_redefinitions",
        selector="chaining_features",
        form="getattr",
        semantic_owner="codegen: total deep-relationship-path factory",
        route_state="live",
        closure_proof=(
            "tests/conformance/test_expression_evidence_integrity.py"
            "::test_deep_override_mapped_index_refuses_at_the_path_factory"
        ),
    ),
    ReviewedRow(
        module="elaboration/elaborate.py",
        function="_ExactElaborator._enumeration_literal",
        selector="referent",
        form="getattr",
        semantic_owner="codegen: enumeration discrimination",
        route_state="live",
        closure_proof=(
            "tests/conformance/test_feature_typing_integrity.py"
            "::test_enumeration_literal_requires_an_exact_referent"
        ),
    ),
    ReviewedRow(
        module="elaboration/occurrence.py",
        function="_modeled_integer_bound",
        selector="referent",
        form="getattr",
        semantic_owner="codegen: multiplicity contextualization",
        route_state="live",
        closure_proof=(
            "tests/conformance/test_occurrence_multiplicity_authority.py"
            "::test_modeled_bound_requires_an_exact_referent"
        ),
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
            "::test_redefined_usage_shares_one_canonical_slot"
        ),
    ),
)

#: Modules audited as off the public raw-source route.  A live import of one of these
#: fails `test_public_raw_source_arms_do_not_reach_off_route_modules`; their raw reads
#: can never satisfy a live manifest row.
OFF_ROUTE_MODULES = (
    "extraction/usage_extractor.py",
    "extraction/computed_attribute_extractor.py",
    "extraction/hierarchy_resolver.py",
)

#: The two public raw-source arms.  B1 says this set is finite; these are its members.
PUBLIC_RAW_SOURCE_ARMS = (
    "orchestration/elaborated_pipeline.py",
    "snapshot/capture.py",
)

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

    def _record(self, selector: str, form: str) -> None:
        self.reads.add(SelectorRead(self.module, self._qualified(), selector, form))

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
            self._record(node.attr, "direct")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "getattr" and len(node.args) >= 2:
            selector = node.args[1]
            if isinstance(selector, ast.Constant):
                if selector.value in REVIEWED_SELECTORS:
                    self._record(str(selector.value), "getattr")
            elif isinstance(selector, ast.Name) and selector.id in self._aliases:
                self._record(self._aliases[selector.id], "alias-getattr")
            else:
                self._record("<unreviewable>", "dynamic-getattr")
        self.generic_visit(node)


def scan_module(source: str, module: str) -> set[SelectorRead]:
    """Discover every reviewable selector read in one module's source text."""
    scanner = _SelectorScanner(module)
    scanner.visit(ast.parse(source))
    return scanner.reads


def _production_modules() -> list[Path]:
    return sorted(PACKAGE_ROOT.rglob("*.py"))


def discovered_reads() -> set[SelectorRead]:
    """The full raw-selector inventory of the production package."""
    found: set[SelectorRead] = set()
    for path in _production_modules():
        module = path.relative_to(PACKAGE_ROOT).as_posix()
        found |= scan_module(path.read_text(), module)
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


def test_no_dynamic_getattr_survives_in_production() -> None:
    """A non-literal `getattr` selector cannot be reviewed, so it cannot be owned."""
    dynamic = sorted(read for read in discovered_reads() if read.form == "dynamic-getattr")
    assert not dynamic, f"unreviewable dynamic getattr selectors: {dynamic}"


# ---------------------------------------------------------------------------
# The five AST evasion mutations — every one must kill the gate
# ---------------------------------------------------------------------------

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
    "dynamic-getattr": (
        "def consume(node, chosen):\n    return getattr(node, chosen)\n"
    ),
}


@pytest.mark.parametrize("evasion", sorted(_EVASIONS))
def test_every_ast_evasion_mutation_is_discovered(evasion: str) -> None:
    """Introduce one evasion form and require the scanner to surface it."""
    found = scan_module(textwrap.dedent(_EVASIONS[evasion]), "mutant.py")
    assert found, f"evasion form went undiscovered: {evasion}"
    assert all(read.function == "consume" for read in found), found


def test_a_clean_module_produces_no_selector_reads() -> None:
    """Anti-vacuity: the scanner is not simply flagging everything."""
    assert scan_module("def consume(node):\n    return node.name\n", "clean.py") == set()


# ---------------------------------------------------------------------------
# Off-route reachability and deleted-symbol inventory
# ---------------------------------------------------------------------------


def test_public_raw_source_arms_do_not_reach_off_route_modules() -> None:
    """An off-route module may never be imported by a public raw-source arm."""
    off_route_names = {
        Path(module).with_suffix("").as_posix().replace("/", ".")
        for module in OFF_ROUTE_MODULES
    }
    offenders: list[str] = []
    for arm in PUBLIC_RAW_SOURCE_ARMS:
        imported = _imports_of(PACKAGE_ROOT / arm)
        for name in off_route_names:
            if any(entry.endswith(name) for entry in imported):
                offenders.append(f"{arm} imports {name}")
    assert not offenders, offenders


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
