"""Compatibility tests for the permanent qualified-name shim."""

from agentic_mbse.sysml import qualified_names as shared

import sysml_codegen.core as core
from sysml_codegen.core import qualified_names as shim


def test_moved_helpers_are_shared_objects() -> None:
    assert shim.sanitize_name is shared.sanitize_name
    assert shim.build_element_qualified_name is shared.build_element_qualified_name
    assert shim.sysml_to_python_qualified_name is shared.sysml_to_python_qualified_name
    assert shim.sanitize_qualified_name is shared.sanitize_qualified_name
    assert shim.python_to_sysml_qualified_name is shared.python_to_sysml_qualified_name
    assert shim.extract_simple_name is shared.extract_simple_name


def test_codegen_builders_remain_local_to_sysml_codegen() -> None:
    assert shim.build_parameter_qualified_name("A__b", "x") == "A__b__x"
    assert shim.get_module_name("A__B") == "a__b"
    assert shim.get_channel_name("A__b", "out") == "A__b__out"
    assert shim.owning_part_leaf("A::B__c") == "B__c"

    assert not hasattr(shared, "build_parameter_qualified_name")
    assert not hasattr(shared, "get_module_name")
    assert not hasattr(shared, "get_channel_name")
    assert not hasattr(shared, "owning_part_leaf")


def test_core_package_exports_existing_qualified_name_surface() -> None:
    assert core.sanitize_name is shared.sanitize_name
    assert core.build_element_qualified_name is shared.build_element_qualified_name
    assert core.sysml_to_python_qualified_name is shared.sysml_to_python_qualified_name
    assert core.python_to_sysml_qualified_name is shared.python_to_sysml_qualified_name
    assert core.extract_simple_name is shared.extract_simple_name

    assert not hasattr(core, "sanitize_qualified_name")
