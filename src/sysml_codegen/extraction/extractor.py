"""Main SysML data extractor for code generation.

Transforms SysML v2 models into structured data for Python code generation.
Uses SysideAdapter for all syside interactions (centralizes syside dependency).
"""

import hashlib
import logging
from collections.abc import Iterable
from pathlib import Path
from typing import Any
from uuid import UUID

# CRITICAL: Import syside adapter from agentic-mbse, NOT direct syside import
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.core.qualified_names import sanitize_name
from sysml_codegen.core.type_mapping import SYSML_TO_PYTHON
from sysml_codegen.extraction.data_models import (
    AttributeInfo,
    CalculationDefinitionData,
    ConstraintInfo,
    PartDefinitionData,
)
from sysml_codegen.extraction.errors import ExactTypeError
from sysml_codegen.extraction.expression_utils import reconstruct_expression
from sysml_codegen.extraction.feature_metadata import extract_feature_unit

# Setup logging
logger = logging.getLogger(__name__)

__all__ = [
    "SysMLDataExtractor",
    "AttributeInfo",
    "ConstraintInfo",
    "PartDefinitionData",
    "CalculationDefinitionData",
]


class SysMLDataExtractor:
    """Extract structured data from SysML models using SysIDE API.

    Uses SysideAdapter for all syside interactions (centralizes syside dependency).
    """

    def __init__(self, model_paths: list[Path]):
        """Initialize with SysML model file paths."""
        self.model_paths = model_paths
        self.adapter = SysideAdapter()
        self.model: Any | None = None
        self.diagnostics: Any | None = None

    def load_models(self) -> bool:
        """Load SysML models using SysIDE via adapter.

        Returns:
            bool: True if loaded successfully (even with warnings)
        """
        self.model, self.diagnostics = self.adapter.load_model(self.model_paths)
        if self.diagnostics is None:
            raise RuntimeError("SysIDE returned no diagnostic collection")

        # Check for errors (warnings OK)
        if self.diagnostics.contains_errors():
            self._report_diagnostics(list(self.diagnostics.errors))
            return False

        return True

    def extract_part_definitions(self) -> list[PartDefinitionData]:
        """Extract all part definitions from loaded model."""
        if not self.model:
            return []

        part_defs = []
        for elem in self.adapter.elements_of_type(self.model, "PartDefinition"):
            part_data = self._extract_part_definition(elem)
            if part_data:
                part_defs.append(part_data)

        return part_defs

    def extract_calculation_definitions(self) -> list[CalculationDefinitionData]:
        """Extract all calculation definitions from loaded model."""
        if not self.model:
            return []

        calc_defs = []
        for elem in self.adapter.elements_of_type(self.model, "CalculationDefinition"):
            calc_data = self._extract_calculation_definition(elem)
            if calc_data:
                calc_defs.append(calc_data)

        return calc_defs

    def _extract_part_definition(self, elem: Any) -> PartDefinitionData | None:
        """Extract data from single part definition element."""
        name = sanitize_name(elem.name)
        if not name:
            return None

        # Extract attributes
        attributes = []
        for member in elem.owned_members:
            if self.adapter.is_instance(member, "AttributeUsage"):
                attr_info = self._extract_attribute(member)
                if attr_info:
                    attributes.append(attr_info)

        # Extract constraints (stub for now)
        constraints: list[ConstraintInfo] = []

        # Get documentation
        doc_comment = self._extract_documentation(elem)

        # Get source location
        source_file = self.model_paths[0] if self.model_paths else Path("unknown")
        source_hash = self._compute_file_hash(source_file) if source_file != Path("unknown") else ""
        source_line = 0
        qualified_name = name

        return PartDefinitionData(
            name=name,
            qualified_name=qualified_name,
            doc_comment=doc_comment,
            attributes=attributes,
            constraints=constraints,
            source_file=source_file,
            source_line=source_line,
            source_hash=source_hash,
        )

    def _extract_calculation_definition(
        self, elem: Any
    ) -> CalculationDefinitionData | None:
        """Extract data from calculation definition element."""
        name = sanitize_name(elem.name)
        if not name:
            return None

        # Extract documentation
        doc_comment = self._extract_calc_documentation(elem)

        # Extract attributes - separate into input and output based on direction
        # Also capture AST data for expression compilation
        input_attributes = []
        output_attributes = []
        input_ids: set[UUID] = set()
        output_ids: set[UUID] = set()
        output_expression_asts_by_id: dict[UUID, Any] = {}
        all_member_ids: set[UUID] = set()
        member_expressions_by_id: dict[UUID, Any] = {}
        member_names_by_id: dict[UUID, str] = {}
        calc_expressions: list[str] = []

        calc_definition_id = self._stable_declaration_id(elem)

        for member in elem.owned_members:
            if not self._is_parameter_member(member):
                continue

            attr_info = self._extract_attribute(member, capture_element_id=True)
            member_name = sanitize_name(member.name)
            member_id = self._stable_declaration_id(member)
            if member_name:
                if member_id is not None:
                    all_member_ids.add(member_id)
                    member_names_by_id[member_id] = member_name

            is_input, is_output = self._get_direction(member)

            if attr_info:
                if is_output:
                    output_attributes.append(attr_info)
                    if member_id is not None:
                        output_ids.add(member_id)
                elif is_input:
                    input_attributes.append(attr_info)
                    if member_id is not None:
                        input_ids.add(member_id)

            # Capture ASTs and expression text
            if hasattr(member, "feature_value_expression") and member.feature_value_expression:
                expr = member.feature_value_expression

                # Store raw AST for output attributes
                if is_output and member_name:
                    if member_id is not None:
                        output_expression_asts_by_id[member_id] = expr

                # Reconstruct expression text for calc_expressions
                expr_text = reconstruct_expression(expr)
                if expr_text and not expr_text.startswith("<"):
                    calc_expressions.append(f"{member_name} = {expr_text}")
                elif expr_text and expr_text.startswith("<"):
                    logger.debug(
                        "Filtered repr-like expression for %s.%s: %s",
                        name, member_name, expr_text[:80],
                    )

        # Second pass: capture member_expressions for non-input/non-output members
        for member in elem.owned_members:
            if not self._is_parameter_member(member):
                continue
            member_name = sanitize_name(member.name)
            member_id = self._stable_declaration_id(member)
            if (
                not member_name
                or member_id is None
                or member_id in input_ids
                or member_id in output_ids
            ):
                continue
            if hasattr(member, "feature_value_expression") and member.feature_value_expression:
                member_expressions_by_id[member_id] = member.feature_value_expression

        # Always append doc comment as additional context
        if doc_comment:
            if calc_expressions:
                calc_expressions.append(f"\nDocumentation:\n{doc_comment}")
            else:
                calc_expressions.append(f"See documentation:\n{doc_comment}")

        # Extract source location
        source_file, source_line = self._get_source_location(elem)
        if source_file is None:
            source_file = self.model_paths[0] if self.model_paths else Path("unknown")
            source_line = 0

        source_hash = self._compute_file_hash(source_file) if source_file.exists() else ""
        qualified_name = str(getattr(elem, 'qualified_name', None) or name)
        references: list[str] = []

        # REQ-EXT-11 (V8): an anonymous `return` (a result parameter the modeler
        # left unnamed) has no name to build a PQN output channel from. syside
        # synthesizes the name 'result' (from the redefined base
        # Calculation::result), so the relaxed filter would otherwise admit it as
        # a garbage-named output; the raw member carries an empty declared_name.
        # Scan the raw members for a ReturnParameterMembership whose declared_name
        # is empty and raise before the generic V7 zero-output guard, so the
        # modeler sees the precise fix (name the result) rather than V7's message
        # (I3; detection key probe-confirmed in Phase 0).
        for member in elem.owned_members:
            owning_membership = getattr(member, "owning_membership", None)
            if type(owning_membership).__name__ != "ReturnParameterMembership":
                continue
            # Detect anonymity on the RAW declared_name — sanitize_name no longer
            # returns "" for empty input (SC-4 A2 always yields a legal identifier),
            # so emptiness must be checked before sanitizing.
            if not (getattr(member, "declared_name", None) or "").strip():
                raise ValueError(
                    f"Calc def '{name}' has an anonymous `return` (a result with "
                    "no name), so no output channel can be built. Give the result "
                    "a name, e.g. `return result : Real = <expr>`."
                )

        # REQ-EXT-08 (V7): fail fast on a calc def with no output channel. Zero
        # outputs slip past extraction and crash deep in the Jinja module
        # template (teax_module.py.jinja2 indexes output_attributes[0]); raise
        # here with an actionable message instead.
        if not output_attributes:
            raise ValueError(
                f"Calc def '{name}' extracted with zero output attributes. "
                "A pipeline module needs at least one output channel. Likely cause: "
                "the calc def declares no result — add one, e.g. "
                "'out attribute y : Real = <expr>' or 'return y : Real = <expr>'. "
                "(An anonymous 'return' is reported separately.)"
            )

        return CalculationDefinitionData(
            name=name,
            qualified_name=qualified_name,
            doc_comment=doc_comment,
            calc_expressions=calc_expressions,
            input_attributes=input_attributes,
            output_attributes=output_attributes,
            references=references,
            source_file=source_file,
            source_line=source_line,
            source_hash=source_hash,
            element_id=calc_definition_id,
            output_expression_asts_by_id=output_expression_asts_by_id,
            all_member_ids=all_member_ids,
            member_expressions_by_id=member_expressions_by_id,
            member_names_by_id=member_names_by_id,
        )

    def _is_parameter_member(self, member: Any) -> bool:
        """Is this calc-def member a parameter (input/output channel)?

        The real question the member filter must ask. An `AttributeUsage` is
        always a parameter. A `ReferenceUsage` is a parameter only when it
        carries a direction — named `return` (Out) and bare `in` (In) do; the
        direction-None body-assignment target of the `return attribute y; y =
        expr;` form does not, so it stays out of the attribute lists and does
        not double-ingest as a second `y` (I2). Attributes and reference usages
        are syside siblings, so the two branches never overlap.
        """
        if self.adapter.is_instance(member, "AttributeUsage"):
            return True
        if self.adapter.is_instance(member, "ReferenceUsage"):
            is_input, is_output = self._get_direction(member)
            return is_input or is_output
        return False

    def _get_direction(self, member: Any) -> tuple[bool, bool]:
        """Get input/output direction from member."""
        is_input = False
        is_output = False
        if hasattr(member, "direction"):
            direction_str = str(member.direction)
            if "In" in direction_str:
                is_input = True
            if "Out" in direction_str or "Return" in direction_str:
                is_output = True
        return is_input, is_output

    def _get_source_location(self, elem: Any) -> tuple[Path | None, int]:
        """Get source file path and line number from element."""
        result = self.adapter.get_source_location(elem)
        if result:
            file_path, line = result
            return Path(file_path), line
        return None, 0

    def _get_calc_def_name(self, elem: Any) -> str | None:
        """Get calculation definition name from a calculation usage element."""
        if not hasattr(elem, 'heritage'):
            return None

        for relationship, target in elem.heritage:
            if self.adapter.is_instance(relationship, "FeatureTyping"):
                if hasattr(target, 'name') and target.name:
                    return sanitize_name(target.name)

        return None

    def _extract_attribute(
        self, attr_elem: Any, *, capture_element_id: bool = False
    ) -> AttributeInfo | None:
        """Extract attribute information from attribute usage element."""
        name = sanitize_name(attr_elem.name)
        if not name:
            return None

        typing_targets = [
            target
            for relationship, target in (getattr(attr_elem, "heritage", None) or ())
            if self.adapter.is_instance(relationship, "FeatureTyping") and target is not None
        ]
        reference = str(getattr(attr_elem, "qualified_name", None) or attr_elem.name)
        location = self.adapter.get_source_location(attr_elem)
        if len(typing_targets) != 1:
            raise ExactTypeError(
                f"feature has {len(typing_targets)} typings; expected exactly one qualified typing",
                reference=reference,
                location=location,
            )
        (typing_target,) = typing_targets
        qualified_type = getattr(typing_target, "qualified_name", None)
        python_type = (
            SYSML_TO_PYTHON.get(str(qualified_type)) if qualified_type is not None else None
        )
        if python_type is None:
            rendered_type = str(qualified_type or "<unqualified>")
            raise ExactTypeError(
                f"typing target {rendered_type!r} is unsupported; expected one of "
                "ScalarValues::Boolean, ScalarValues::Integer, ScalarValues::Real, "
                "or ScalarValues::String",
                reference=reference,
                location=location,
            )
        sysml_type = str(getattr(typing_target, "name", None) or qualified_type)

        description = self._extract_attribute_documentation(attr_elem)
        default_value = self._extract_default_value(attr_elem)
        is_optional = default_value is not None
        unit = self._extract_unit(attr_elem, sysml_type, description)
        element_id = (
            self._stable_declaration_id(attr_elem)
            if capture_element_id
            else None
        )

        return AttributeInfo(
            name=name,
            sysml_type=sysml_type,
            python_type=python_type,
            description=description,
            default_value=default_value,
            is_optional=is_optional,
            source_line=0,
            unit=unit,
            element_id=element_id,
        )

    def _stable_declaration_id(self, element: Any) -> UUID | None:
        """Capture a stable UUID sidecar without narrowing shared extraction."""
        qualified_name = getattr(element, "qualified_name", None)
        if qualified_name is None:
            return None
        element_id = self.adapter.element_id(element)
        if element_id.version != 5:
            return None
        return element_id

    def _extract_default_value(self, feature: Any) -> str | None:
        """Extract default value from AttributeUsage if present."""
        if hasattr(feature, 'feature_value_expression') and feature.feature_value_expression:
            expr = feature.feature_value_expression
            value = self._extract_literal_value(expr)
            if value is not None:
                return str(value)

        if not hasattr(feature, 'owned_memberships'):
            return None

        for membership in feature.owned_memberships:
            if not hasattr(membership, 'is_default') or not membership.is_default:
                continue
            if not hasattr(membership, 'value'):
                continue
            value_expr = membership.value
            value = self._extract_literal_value(value_expr)
            if value is not None:
                return str(value)

        return None

    def _extract_literal_value(self, expr: Any) -> Any | None:
        """Extract Python value from a literal expression."""
        if expr is None:
            return None

        if self.adapter.is_instance(expr, "LiteralRational"):
            return expr.value
        elif self.adapter.is_instance(expr, "LiteralInteger"):
            return expr.value
        elif self.adapter.is_instance(expr, "LiteralBoolean"):
            return expr.value
        elif self.adapter.is_instance(expr, "LiteralString"):
            return expr.value
        else:
            return None

    def _extract_calc_documentation(self, calc_def: Any) -> str:
        """Extract calculation-level documentation from Comment elements."""
        if hasattr(calc_def, 'documentation'):
            docs = list(calc_def.documentation)
            if docs:
                doc_texts = []
                for doc in docs:
                    if hasattr(doc, 'body') and doc.body:
                        doc_texts.append(doc.body.strip())
                if doc_texts:
                    return "\n\n".join(doc_texts)

        if hasattr(calc_def, 'owner') and calc_def.owner:
            owner = calc_def.owner
            if hasattr(owner, 'owned_members'):
                members = list(owner.owned_members)
                for i, member in enumerate(members):
                    if member == calc_def and i > 0:
                        prev_member = members[i - 1]
                        if self.adapter.is_instance(prev_member, "Comment"):
                            if hasattr(prev_member, 'body') and prev_member.body:
                                body = prev_member.body.strip()
                                lines = []
                                for line in body.split('\n'):
                                    line = line.strip()
                                    if line.startswith('*'):
                                        line = line[1:].strip()
                                    lines.append(line)
                                return '\n'.join(lines)
                        break

        return ""

    def _extract_attribute_documentation(self, attr: Any) -> str:
        """Extract attribute-level documentation from Comment elements."""
        if not hasattr(attr, 'documentation'):
            return ""

        docs = attr.documentation
        if not docs:
            return ""

        for doc in docs:
            if hasattr(doc, 'body') and doc.body:
                return str(doc.body).strip()

        return ""

    def _extract_unit(
        self, attr_elem: Any, sysml_type: str, description: str
    ) -> str | None:
        """Delegate exact unit extraction to the declaration-owned helper."""
        return extract_feature_unit(attr_elem)

    def _extract_documentation(self, elem: Any) -> str:
        """Extract documentation string from element."""
        docs = []
        if hasattr(elem, "owned_members"):
            for member in elem.owned_members:
                if self.adapter.is_instance(member, "Comment"):
                    if hasattr(member, "body") and member.body:
                        body = member.body.strip().strip("*").strip()
                        if body:
                            docs.append(body)

        return "\n".join(docs) if docs else ""

    def _report_diagnostics(self, diagnostics: Iterable[Any]) -> None:
        """Report diagnostics to console."""
        for diag in diagnostics:
            print(f"[ERROR] {diag}")

    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of file contents."""
        if not file_path.exists() or file_path.is_dir():
            return ""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
