"""Main SysML data extractor for code generation.

Transforms SysML v2 models into structured data for Python code generation.
Uses SysideAdapter for all syside interactions (centralizes syside dependency).
"""

import hashlib
import logging
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any
from uuid import UUID

# CRITICAL: Import syside adapter from agentic-mbse, NOT direct syside import
from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.core.qualified_names import sanitize_name
from sysml_codegen.extraction.data_models import (
    AttributeInfo,
    CalculationDefinitionData,
    ConstraintInfo,
    PartDefinitionData,
)
from sysml_codegen.extraction.expression_utils import reconstruct_expression

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
        self.model = None
        self.diagnostics = None

    def load_models(self) -> bool:
        """Load SysML models using SysIDE via adapter.

        Returns:
            bool: True if loaded successfully (even with warnings)
        """
        self.model, self.diagnostics = self.adapter.load_model(self.model_paths)

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

    def _extract_part_definition(self, elem) -> PartDefinitionData | None:
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
        constraints = []

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
        self, elem
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

    def _get_direction(self, member) -> tuple[bool, bool]:
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

    def _get_source_location(self, elem) -> tuple[Path | None, int]:
        """Get source file path and line number from element."""
        result = self.adapter.get_source_location(elem)
        if result:
            file_path, line = result
            return Path(file_path), line
        return None, 0

    def _get_calc_def_name(self, elem) -> str | None:
        """Get calculation definition name from a calculation usage element."""
        if not hasattr(elem, 'heritage'):
            return None

        for relationship, target in elem.heritage:
            if self.adapter.is_instance(relationship, "FeatureTyping"):
                if hasattr(target, 'name') and target.name:
                    return sanitize_name(target.name)

        return None

    def _extract_binding_source(self, param_elem) -> str | None:
        """Extract binding source from a parameter element."""
        if not hasattr(param_elem, 'feature_value_expression'):
            return None

        expr = param_elem.feature_value_expression
        if not expr:
            return None

        return self._parse_expression_to_path(expr)

    def _parse_expression_to_path(self, expr) -> str | None:
        """Parse SysML expression to extract binding path."""
        if self.adapter.is_instance(expr, "FeatureChainExpression"):
            path_parts = []
            operands = list(expr.operands)
            if operands:
                operand_expr = operands[0]
                instance_name = self._extract_simple_reference(operand_expr)
                if instance_name:
                    path_parts.append(instance_name)

            if hasattr(expr, 'target_feature') and expr.target_feature:
                target = expr.target_feature
                if hasattr(target, 'name') and target.name:
                    path_parts.append(target.name)

            if len(path_parts) >= 2:
                return ".".join(path_parts)
            elif len(path_parts) == 1:
                return path_parts[0]

        elif self.adapter.is_instance(expr, "FeatureReferenceExpression"):
            return self._extract_simple_reference(expr)

        return None

    def _extract_simple_reference(self, expr) -> str | None:
        """Extract simple reference from FeatureReferenceExpression."""
        if not self.adapter.is_instance(expr, "FeatureReferenceExpression"):
            return None

        for membership in expr.memberships:
            if type(membership).__name__ == "Membership":
                if hasattr(membership, "member_element"):
                    elem = membership.member_element
                    if elem and hasattr(elem, "name") and elem.name:
                        path = self._build_reference_path(elem)
                        return path

        return None

    def _build_reference_path(self, elem) -> str:
        """Build full reference path for an element."""
        parts = []

        if hasattr(elem, 'name') and elem.name:
            parts.append(elem.name)

        current = elem
        while hasattr(current, 'owner') and current.owner:
            owner = current.owner
            if self.adapter.is_instance(owner, "OwningMembership"):
                if hasattr(owner, 'owning_related_element'):
                    owning_elem = owner.owning_related_element
                    if owning_elem and hasattr(owning_elem, 'name') and owning_elem.name:
                        if (self.adapter.is_instance(owning_elem, "PartUsage") or
                            self.adapter.is_instance(owning_elem, "CalculationUsage") or
                            self.adapter.is_instance(owning_elem, "AttributeUsage")):
                            parts.insert(0, owning_elem.name)
                            current = owning_elem
                            continue
                break
            current = owner

        return ".".join(parts) if parts else elem.name if hasattr(elem, 'name') else ""

    def _extract_attribute(
        self, attr_elem: Any, *, capture_element_id: bool = False
    ) -> AttributeInfo | None:
        """Extract attribute information from attribute usage element."""
        name = sanitize_name(attr_elem.name)
        if not name:
            return None

        sysml_type = "Any"
        python_type = "Any"

        if attr_elem.heritage:
            for relationship, target in attr_elem.heritage:
                if self.adapter.is_instance(relationship, "FeatureTyping"):
                    type_name = target.name if hasattr(target, "name") else None
                    if type_name:
                        sysml_type = type_name
                        python_type = self._map_sysml_to_python_type(type_name)
                        break

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

    def _extract_default_value(self, feature) -> str | None:
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

    def _extract_literal_value(self, expr) -> Any | None:
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

    def _extract_calc_documentation(self, calc_def) -> str:
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

    def _extract_attribute_documentation(self, attr) -> str:
        """Extract attribute-level documentation from Comment elements."""
        if not hasattr(attr, 'documentation'):
            return ""

        docs = attr.documentation
        if not docs:
            return ""

        for doc in docs:
            if hasattr(doc, 'body') and doc.body:
                return doc.body.strip()

        return ""

    def _extract_unit(self, attr_elem, sysml_type: str, description: str) -> str | None:
        """Extract unit annotation from attribute using multiple sources."""
        unit = self._extract_unit_from_type(attr_elem, sysml_type)
        if unit:
            return unit

        unit = self._extract_unit_from_cst(attr_elem)
        if unit:
            return unit

        unit = self._extract_unit_from_description(description)
        if unit:
            return unit

        return None

    def _extract_unit_from_type(self, attr_elem, sysml_type: str) -> str | None:
        """Extract unit from ISQ/SI type heritage."""
        isq_to_unit = {
            "Length": "m", "Mass": "kg", "Time": "s", "ElectricCurrent": "A",
            "ThermodynamicTemperature": "K", "AmountOfSubstance": "mol",
            "LuminousIntensity": "cd", "Power": "W", "Energy": "J", "Force": "N",
            "Pressure": "Pa", "Frequency": "Hz", "Voltage": "V",
            "ElectricResistance": "Ω", "MagneticFluxDensity": "T", "Area": "m²",
            "Volume": "m³", "Velocity": "m/s", "Acceleration": "m/s²",
            "Density": "kg/m³", "HeatFlux": "W/m²",
        }

        si_to_unit = {
            "Metre": "m", "Kilogram": "kg", "Second": "s", "Ampere": "A",
            "Kelvin": "K", "Mole": "mol", "Candela": "cd", "Watt": "W",
            "Joule": "J", "Newton": "N", "Pascal": "Pa", "Hertz": "Hz",
            "Volt": "V", "Ohm": "Ω", "Tesla": "T",
        }

        if sysml_type in isq_to_unit:
            return isq_to_unit[sysml_type]
        if sysml_type in si_to_unit:
            return si_to_unit[sysml_type]

        if hasattr(attr_elem, 'heritage') and attr_elem.heritage:
            for relationship, target in attr_elem.heritage:
                if self.adapter.is_instance(relationship, "FeatureTyping"):
                    if hasattr(target, 'qualified_name'):
                        qname = target.qualified_name
                        if qname and '::' in qname:
                            parts = qname.split('::')
                            if len(parts) >= 2:
                                namespace = parts[-2]
                                type_name = parts[-1]
                                if namespace == "ISQ" and type_name in isq_to_unit:
                                    return isq_to_unit[type_name]
                                if namespace == "SI" and type_name in si_to_unit:
                                    return si_to_unit[type_name]

        return None

    def _extract_unit_from_cst(self, attr_elem) -> str | None:
        """Extract unit from inline comment in original source."""
        if not hasattr(attr_elem, 'cst_node') or not attr_elem.cst_node:
            return None

        cst_node = attr_elem.cst_node
        if not hasattr(cst_node, 'start_byte'):
            return None

        start_byte = cst_node.start_byte
        source_file = self._get_source_file_for_element(attr_elem)
        if not source_file or not source_file.exists():
            return None

        try:
            source_content = source_file.read_text(encoding='utf-8')
        except Exception:
            return None

        lines = source_content.split('\n')
        cumulative = 0
        source_line = None
        for line in lines:
            if cumulative <= start_byte < cumulative + len(line) + 1:
                source_line = line
                break
            cumulative += len(line) + 1

        if not source_line:
            return None

        match = re.search(r'//\s*(\[?[A-Za-z°Ω²³/·⋅\-]+\]?)\s*(?:-|$|\s)', source_line)
        if match:
            unit = match.group(1).strip('[]')
            non_units = {
                "the",
                "this",
                "that",
                "todo",
                "note",
                "fixme",
                "energy",
                "power",
            }
            if unit.lower() not in non_units:
                return unit

        return None

    def _get_source_file_for_element(self, elem) -> Path | None:
        """Get the source file Path for an element."""
        current = elem
        while current:
            if hasattr(current, 'document'):
                doc = current.document
                if doc and hasattr(doc, 'url'):
                    url = doc.url
                    if hasattr(url, 'path'):
                        return Path(url.path)
                    url_str = str(url)
                    if url_str.startswith('file:'):
                        return Path(url_str[5:])
                    return Path(url_str)
            if hasattr(current, 'source_file'):
                return Path(current.source_file) if current.source_file else None
            if hasattr(current, 'owning_document'):
                doc = current.owning_document
                if doc and hasattr(doc, 'uri'):
                    return Path(doc.uri) if doc.uri else None
            if hasattr(current, 'owner'):
                current = current.owner
            else:
                break

        if hasattr(self, 'model_paths') and self.model_paths:
            files = []
            for path in self.model_paths:
                if path.is_file():
                    files.append(path)
                elif path.is_dir():
                    files.extend(path.glob('**/*.sysml'))
            if len(files) == 1:
                return files[0]

        return None

    def _extract_unit_from_description(self, description: str) -> str | None:
        """Extract unit from description/doc comment."""
        if not description:
            return None

        match = re.search(r'\[([A-Za-z°Ω²³/·⋅\-]+)\]', description)
        if match:
            return match.group(1)

        match = re.match(r'^([A-Za-z°Ω²³/·⋅]+)\s*[-–—]', description)
        if match:
            unit = match.group(1)
            if unit.lower() not in ['the', 'this', 'that', 'total', 'maximum', 'minimum']:
                return unit

        match = re.search(r'\(([A-Za-z°Ω²³/·⋅\-]+)\)', description)
        if match:
            unit = match.group(1)
            if len(unit) <= 10 and not unit.lower().startswith(('e.g', 'i.e', 'typ', 'def')):
                return unit

        return None

    def _map_sysml_to_python_type(self, sysml_type: str) -> str:
        """Map SysML type to Python type."""
        type_map = {
            "Real": "float",
            "Integer": "int",
            "String": "str",
            "Boolean": "bool",
        }
        return type_map.get(sysml_type, sysml_type)

    def _extract_documentation(self, elem) -> str:
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

    def _report_diagnostics(self, diagnostics: Iterable) -> None:
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
